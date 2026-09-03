#!/usr/bin/env python3
"""READ_ONLY_PREFLIGHT for a successor-host REI Section-0 receipt.

This module verifies and records every pre-lease input.  It can create a new
successor-host Section-0 receipt, but it cannot reserve the global attempt,
create a local attempt lease, or invoke the native runtime.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
from typing import Any, Callable, Mapping, Sequence
import urllib.error
import urllib.parse
import urllib.request


PACKAGE = Path(__file__).resolve().parent
CONTRACT_PATH = PACKAGE / "CONTRACT.json"
PACKAGE_INDEX_PATH = PACKAGE / "PACKAGE_INDEX.json"


class PreflightError(RuntimeError):
    """Typed fail-closed preflight error."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def write_o_excl(path: Path, value: Mapping[str, Any]) -> None:
    encoded = canonical_bytes(dict(value)) + b"\n"
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise PreflightError("CREATE_ONLY_RECEIPT_ALREADY_EXISTS") from exc
    except OSError as exc:
        raise PreflightError("CREATE_ONLY_RECEIPT_UNAVAILABLE") from exc
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(encoded)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PreflightError("PREFLIGHT_CONTRACT_UNREADABLE") from exc
    required = {
        "schema",
        "classification",
        "repository",
        "executable_release",
        "successor_section0",
        "attempt_state",
        "execution_context",
        "required_operations",
        "forbidden_operations",
        "success_status",
        "failure_status",
        "claim_ceiling",
        "next_node_after_success",
    }
    if (
        not isinstance(value, dict)
        or set(value) != required
        or value.get("schema")
        != "rei-runtime-successor-section0-readonly-preflight/v1"
        or value.get("repository") != "cosmosapjw-quantum/rei_bianchi"
        or value.get("success_status")
        != "PASS_READ_ONLY_SUCCESSOR_SECTION0_PREFLIGHT"
    ):
        raise PreflightError("PREFLIGHT_CONTRACT_SCHEMA_INVALID")
    attempt = value["attempt_state"]
    if (
        attempt.get("global_observation_method") != "READ_ONLY_GET_ONLY"
        or attempt.get("absence_is_authorization") is not False
        or attempt.get("remaining_before_reservation") != 1
        or attempt.get("global_lease_acquisition")
        != "FORBIDDEN_IN_THIS_NODE"
        or attempt.get("local_lease_creation") != "FORBIDDEN_IN_THIS_NODE"
        or attempt.get("native_dispatch") != "FORBIDDEN_IN_THIS_NODE"
    ):
        raise PreflightError("PREFLIGHT_ATTEMPT_POLICY_INVALID")
    return value


def verify_package_index(
    root: Path = PACKAGE,
    index_path: Path = PACKAGE_INDEX_PATH,
) -> None:
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PreflightError("PREFLIGHT_PACKAGE_INDEX_UNREADABLE") from exc
    if (
        not isinstance(index, dict)
        or set(index) != {"schema", "git_object_format", "entries"}
        or index.get("schema")
        != "rei-runtime-successor-section0-preflight-package-index/v1"
        or index.get("git_object_format") != "sha1"
        or not isinstance(index.get("entries"), list)
    ):
        raise PreflightError("PREFLIGHT_PACKAGE_INDEX_INVALID")
    expected: dict[Path, str] = {}
    for row in index["entries"]:
        if not isinstance(row, dict) or set(row) != {"path", "blob_sha", "role"}:
            raise PreflightError("PREFLIGHT_PACKAGE_INDEX_INVALID")
        raw = row.get("path")
        blob = row.get("blob_sha")
        pure = PurePosixPath(raw) if isinstance(raw, str) else None
        if (
            pure is None
            or pure.is_absolute()
            or ".." in pure.parts
            or str(pure) != raw
            or not isinstance(blob, str)
            or len(blob) != 40
            or any(character not in "0123456789abcdef" for character in blob)
        ):
            raise PreflightError("PREFLIGHT_PACKAGE_INDEX_INVALID")
        relative = Path(raw)
        if relative in expected:
            raise PreflightError("PREFLIGHT_PACKAGE_INDEX_INVALID")
        expected[relative] = blob

    package_root = root.resolve(strict=True)
    index_resolved = index_path.resolve(strict=True)
    actual: set[Path] = set()
    for candidate in package_root.rglob("*"):
        if candidate.is_symlink():
            raise PreflightError("PREFLIGHT_PACKAGE_SCOPE_MISMATCH")
        if candidate.is_file() and candidate.resolve(strict=True) != index_resolved:
            actual.add(candidate.relative_to(package_root))
    if set(expected) != actual:
        raise PreflightError("PREFLIGHT_PACKAGE_SCOPE_MISMATCH")
    for relative, blob in expected.items():
        path = package_root / relative
        if not path.is_file() or git_blob_sha1(path) != blob:
            raise PreflightError(
                f"PREFLIGHT_PACKAGE_BLOB_MISMATCH:{relative.as_posix()}"
            )


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def inspect_attempt_state(root: Path) -> list[str]:
    candidate = Path(root).resolve(strict=True)
    return sorted(path.relative_to(candidate).as_posix() for path in candidate.rglob("*"))


def validate_attempt_state_root(path: Path, *, repo: Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise PreflightError("ATTEMPT_STATE_ROOT_UNAVAILABLE")
    resolved = candidate.resolve(strict=False)
    tmp = Path("/tmp").resolve(strict=True)
    repository = Path(repo).resolve(strict=True)
    if _is_under(resolved, tmp) or _is_under(resolved, repository):
        raise PreflightError("ATTEMPT_STATE_ROOT_FORBIDDEN")
    if not resolved.is_dir() or resolved.is_symlink():
        raise PreflightError("ATTEMPT_STATE_ROOT_UNAVAILABLE")
    existing = inspect_attempt_state(resolved)
    if existing:
        raise PreflightError("ATTEMPT_STATE_ALREADY_PRESENT:" + ",".join(existing))
    return resolved


def validate_output_root(path: Path, *, repo: Path, state_root: Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise PreflightError("PREFLIGHT_OUTPUT_ROOT_INVALID")
    resolved = candidate.resolve(strict=False)
    tmp = Path("/tmp").resolve(strict=True)
    repository = Path(repo).resolve(strict=True)
    state = Path(state_root).resolve(strict=True)
    if (
        _is_under(resolved, tmp)
        or _is_under(resolved, repository)
        or _is_under(resolved, state)
        or _is_under(state, resolved)
    ):
        raise PreflightError("PREFLIGHT_OUTPUT_ROOT_FORBIDDEN")
    if resolved.exists() or resolved.is_symlink():
        raise PreflightError("PREFLIGHT_OUTPUT_ROOT_PREEXISTS")
    try:
        resolved.mkdir(mode=0o700, parents=False)
    except OSError as exc:
        raise PreflightError("PREFLIGHT_OUTPUT_ROOT_UNAVAILABLE") from exc
    return resolved.resolve(strict=True)


def observe_global_ref_read_only(
    *,
    ref: str,
    expected_target: str,
    token: str = "",
    api_base: str = "https://api.github.com",
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> dict[str, Any]:
    if not ref.startswith("refs/"):
        raise PreflightError("GLOBAL_REF_INVALID")
    relative = urllib.parse.quote(ref.removeprefix("refs/"), safe="/")
    endpoint = (
        api_base.rstrip("/")
        + "/repos/cosmosapjw-quantum/rei_bianchi/git/ref/"
        + relative
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "rei-runtime-successor-section0-readonly-preflight/v1",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(endpoint, method="GET", headers=headers)
    try:
        with opener(request, 30) as response:
            status = response.status
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {
                "status": "GLOBAL_ATTEMPT_REF_ABSENT_OBSERVED",
                "http_status": 404,
                "ref": ref,
                "expected_target": expected_target,
                "authorization_effect": "NONE",
                "global_lease_acquired": False,
            }
        raise PreflightError(
            f"GLOBAL_REF_READ_ONLY_OBSERVATION_FAILED:HTTP_{exc.code}"
        ) from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PreflightError("GLOBAL_REF_READ_ONLY_OBSERVATION_FAILED") from exc
    if status != 200 or not isinstance(payload, dict):
        raise PreflightError("GLOBAL_REF_READ_ONLY_OBSERVATION_FAILED")
    observed_ref = payload.get("ref")
    observed_target = payload.get("object", {}).get("sha")
    raise PreflightError(
        "STOP_ATTEMPT_ALREADY_RESERVED:"
        f"ref={observed_ref!r}:target={observed_target!r}"
    )


def validate_successor_receipt_mapping(
    receipt: Mapping[str, Any],
    rule: Mapping[str, Any],
) -> dict[str, Any]:
    value = dict(receipt)
    if value.get("status") != rule["required_status"]:
        raise PreflightError("SUCCESSOR_SECTION0_STATUS_MISMATCH")
    if value.get("schema") != rule["required_schema"]:
        raise PreflightError("SUCCESSOR_SECTION0_SCHEMA_MISMATCH")
    if (
        value.get("semantic_toolchain_lock_sha256")
        != rule["semantic_toolchain_lock_sha256"]
    ):
        raise PreflightError("SUCCESSOR_SECTION0_LOCK_MISMATCH")
    expected_toolchain = rule.get("semantic_toolchain_lock")
    if expected_toolchain is not None and value.get("observed_toolchain") != expected_toolchain:
        raise PreflightError("SUCCESSOR_SECTION0_FIELD_MISMATCH")
    return value


def build_preflight_receipt(
    *,
    release_head: str,
    release_tree: str,
    successor_receipt_sha256: str,
    first_ref_observation: Mapping[str, Any],
    second_ref_observation: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": "rei-runtime-successor-section0-readonly-preflight-receipt/v1",
        "status": "PASS_READ_ONLY_SUCCESSOR_SECTION0_PREFLIGHT",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "executable_release": {"commit": release_head, "tree": release_tree},
        "successor_section0_receipt_sha256": successor_receipt_sha256,
        "global_ref_observations": [
            dict(first_ref_observation),
            dict(second_ref_observation),
        ],
        "attempt_state": {
            "global_lease_acquired": False,
            "local_lease_created": False,
            "remaining_attempts": 1,
            "absence_is_authorization": False,
        },
        "native_runtime": "NOT_RUN",
        "claim_ceiling": {
            "runtime_bridge": "STOP_INVALID_UNTIL_FRESH_RESULT_AUDIT",
            "first_interval": "NO_PASS_FIRST_CANONICAL_INTERVAL",
            "provider_export": "NOT_AUTHORIZED",
            "scientific_pass": "NOT_CLAIMED",
        },
        "next_node": (
            "REI-RUNTIME-BRIDGE-03B_"
            "ATOMIC_GLOBAL_LEASE_AND_ONE_NATIVE_DISPATCH"
        ),
    }


def _load_module(path: Path, name: str) -> Any:
    if path.is_symlink() or not path.is_file():
        raise PreflightError(f"PINNED_MODULE_UNAVAILABLE:{path.name}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise PreflightError(f"PINNED_MODULE_IMPORT_SPEC_MISSING:{path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _git_text(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C"},
    )
    if completed.returncode != 0:
        raise PreflightError(f"READ_ONLY_GIT_COMMAND_FAILED:{arguments[0]}")
    return completed.stdout.strip()


def _verify_blob(repo: Path, release: Mapping[str, Any], path_key: str, blob_key: str) -> Path:
    relative = release[path_key]
    observed = _git_text(repo, "rev-parse", f"HEAD:{relative}")
    if observed != release[blob_key]:
        raise PreflightError(f"EXECUTABLE_RELEASE_BLOB_MISMATCH:{relative}")
    candidate = repo / relative
    if candidate.is_symlink() or not candidate.is_file():
        raise PreflightError(f"EXECUTABLE_RELEASE_FILE_UNAVAILABLE:{relative}")
    return candidate.resolve(strict=True)


def verify_exact_release_and_inputs(
    repo: Path,
    contract: Mapping[str, Any],
) -> tuple[Any, dict[str, Any], Any, Any]:
    root = Path(repo)
    if root.is_symlink():
        raise PreflightError("EXECUTABLE_RELEASE_STANDALONE_CLONE_REQUIRED")
    root = root.resolve(strict=True)
    release = contract["executable_release"]
    if _git_text(root, "rev-parse", "HEAD") != release["commit"]:
        raise PreflightError("EXECUTABLE_RELEASE_HEAD_MISMATCH")
    if _git_text(root, "rev-parse", "HEAD^{tree}") != release["tree"]:
        raise PreflightError("EXECUTABLE_RELEASE_TREE_MISMATCH")
    runner_path = _verify_blob(root, release, "runner_path", "runner_blob_sha1")
    runtime_contract_path = _verify_blob(
        root, release, "contract_path", "contract_blob_sha1"
    )
    section = contract["successor_section0"]
    _verify_blob(root, section, "policy_path", "policy_blob_sha1")
    _verify_blob(root, section, "emitter_path", "emitter_blob_sha1")

    runner = _load_module(runner_path, "rei_successor_runtime_release_readonly")
    runtime_package = runner_path.parent
    runner.verify_package_index(
        root=runtime_package,
        index_path=runtime_package / "PACKAGE_INDEX.json",
    )
    runtime_contract = runner.load_contract(runtime_contract_path)
    runner.verify_source_inputs(root, runtime_contract)
    base = runner._load_base_runner(root, runtime_contract)
    bridge = base.load_bridge(
        root, runtime_contract["source_handoff"]["production_bridge_path"]
    )
    standalone_roots = base.verify_standalone_repository_context(bridge, root)
    pinned = lambda *args: base.git_checked(bridge, root, *args).strip()
    runner.verify_exact_release_identity(
        root,
        release["commit"],
        release["tree"],
        git_text=pinned,
    )
    predecessor = runtime_contract["immutable_governance_predecessor"]
    if pinned("merge-base", "HEAD", predecessor["commit"]) != predecessor["commit"]:
        raise PreflightError("GOVERNANCE_PREDECESSOR_NOT_ANCESTOR")
    if pinned("rev-parse", f'{predecessor["commit"]}^{{tree}}') != predecessor["tree"]:
        raise PreflightError("GOVERNANCE_PREDECESSOR_TREE_MISMATCH")
    pinned("fsck", "--full")
    pinned("diff", "--check")
    if pinned("status", "--porcelain=v1", "--untracked-files=all"):
        raise PreflightError("EXECUTABLE_RELEASE_WORKTREE_NOT_CLEAN")
    return runner, runtime_contract, base, bridge


def run_successor_emitter(
    *,
    repo: Path,
    contract: Mapping[str, Any],
    rustc: Path,
    python: Path,
    mpfr: Path,
    gmp: Path,
    cc: Path,
    ld: Path,
    output: Path,
) -> str:
    record = contract["successor_section0"]
    emitter = repo / record["emitter_path"]
    policy = repo / record["policy_path"]
    command = [
        str(python),
        "-I",
        "-S",
        "-B",
        str(emitter),
        "--policy",
        str(policy),
        "--rustc",
        str(rustc),
        "--python",
        str(python),
        "--mpfr",
        str(mpfr),
        "--gmp",
        str(gmp),
        "--cc",
        str(cc),
        "--ld",
        str(ld),
        "--output",
        str(output),
    ]
    completed = subprocess.run(
        command,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C"},
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip()
        raise PreflightError("SUCCESSOR_SECTION0_REATTESTATION_FAILED:" + message)
    return completed.stdout.strip()


def run_read_only_preflight(
    *,
    repo: Path,
    rustc: Path,
    python: Path,
    mpfr: Path,
    gmp: Path,
    cc: Path,
    ld: Path,
    attempt_state_root: Path,
    output_root: Path,
    token: str = "",
    api_base: str = "https://api.github.com",
) -> tuple[dict[str, Any], Path]:
    verify_package_index()
    contract = load_contract()
    root = Path(repo).resolve(strict=True)
    state = validate_attempt_state_root(attempt_state_root, repo=root)
    output = validate_output_root(output_root, repo=root, state_root=state)
    runner, runtime_contract, _, _ = verify_exact_release_and_inputs(root, contract)

    attempt = contract["attempt_state"]
    release = contract["executable_release"]
    first = observe_global_ref_read_only(
        ref=attempt["global_ref"],
        expected_target=release["commit"],
        token=token,
        api_base=api_base,
    )
    section0_path = output / "successor-section0.json"
    emitter_stdout = run_successor_emitter(
        repo=root,
        contract=contract,
        rustc=rustc,
        python=python,
        mpfr=mpfr,
        gmp=gmp,
        cc=cc,
        ld=ld,
        output=section0_path,
    )
    try:
        section0 = json.loads(section0_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PreflightError("SUCCESSOR_SECTION0_UNREADABLE_AFTER_EMISSION") from exc
    validate_successor_receipt_mapping(
        section0,
        runtime_contract["successor_section0"],
    )
    if sha256_file(section0_path) == contract["successor_section0"]["historical_receipt_sha256"]:
        raise PreflightError("HISTORICAL_SECTION0_RECEIPT_REUSE_FORBIDDEN")
    runner.load_successor_section0_receipt(section0_path, runtime_contract)

    second = observe_global_ref_read_only(
        ref=attempt["global_ref"],
        expected_target=release["commit"],
        token=token,
        api_base=api_base,
    )
    validate_attempt_state_root(state, repo=root)
    receipt = build_preflight_receipt(
        release_head=release["commit"],
        release_tree=release["tree"],
        successor_receipt_sha256=sha256_file(section0_path),
        first_ref_observation=first,
        second_ref_observation=second,
    )
    receipt["successor_section0"] = {
        "status": section0["status"],
        "schema": section0["schema"],
        "semantic_toolchain_lock_sha256": section0[
            "semantic_toolchain_lock_sha256"
        ],
        "host_epoch_fingerprint": section0["host_epoch_fingerprint"],
        "emitter_stdout": emitter_stdout,
    }
    receipt["attempt_state_root"] = str(state)
    receipt["output_root"] = str(output)
    receipt_path = output / "read-only-preflight-receipt.json"
    write_o_excl(receipt_path, receipt)
    return receipt, receipt_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--rustc", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--mpfr", type=Path, required=True)
    parser.add_argument("--gmp", type=Path, required=True)
    parser.add_argument("--cc", type=Path, required=True)
    parser.add_argument("--ld", type=Path, required=True)
    parser.add_argument("--attempt-state-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--api-base", default="https://api.github.com")
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    options = parser.parse_args(argv)
    try:
        receipt, path = run_read_only_preflight(
            repo=options.repo,
            rustc=options.rustc,
            python=options.python,
            mpfr=options.mpfr,
            gmp=options.gmp,
            cc=options.cc,
            ld=options.ld,
            attempt_state_root=options.attempt_state_root,
            output_root=options.output_root,
            token=os.environ.get(options.token_env, ""),
            api_base=options.api_base,
        )
    except PreflightError as exc:
        print(f"STOP_INVALID: {exc}", file=sys.stderr)
        return 65
    except Exception as exc:
        print(
            "STOP_INVALID: UNEXPECTED_PREFLIGHT_EXCEPTION:"
            f"{type(exc).__name__}:{exc}",
            file=sys.stderr,
        )
        return 65
    print(json.dumps({"status": receipt["status"], "receipt": str(path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
