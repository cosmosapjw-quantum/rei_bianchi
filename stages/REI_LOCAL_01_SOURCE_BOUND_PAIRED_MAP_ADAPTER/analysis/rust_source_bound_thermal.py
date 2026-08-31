"""Capability-bound bridge to the Rust/MPFR interval certificate kernel.

The numerical implementation is exclusively the pinned Rust ABI.  Python owns
authority validation, deterministic build orchestration, closed records, and
native replay.  Public load-bearing entrypoints automatically observe Python
opens, imports, process launches, and native loads.  The capability blocks
ordinary API-level fabrication.
Python private state is not a hostile same-process boundary and cannot authenticate
its own pre-start process image; those residual limitations are typed blockers below.
"""

from __future__ import annotations

import builtins
import ctypes
import contextvars
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
from typing import Any, Callable, Mapping, Sequence

from rei_bianchi.joint_implicit_remainder import (
    CERTIFICATE_SCHEMA,
    LinearRequest,
    MixedRhsRequest,
    MixedVfRequest,
    PRECISION_BITS,
    ROUNDING_POLICY,
    TangentCertificate,
    TangentRequest,
    validate_mixed_vf_certificate,
    validate_tangent_certificate,
)


DEFAULT_RUSTC = Path(
    "/workspace/scratch/6f83d977af18/toolchains/rust-1.94.1-prefix/bin/rustc"
)
LINKER = Path("/usr/bin/x86_64-linux-gnu-gcc")
GIT = Path("/usr/bin/git")
LDD = Path("/usr/bin/ldd")
READELF = Path("/usr/bin/readelf")
NATIVE_LIBRARY_DIRECTORY = Path("/usr/lib/x86_64-linux-gnu")
MPFR = NATIVE_LIBRARY_DIRECTORY / "libmpfr.so.6.2.1"
GMP = NATIVE_LIBRARY_DIRECTORY / "libgmp.so.10.5.0"

RUSTC_COMMIT = "e408947bfd200af42db322daf0fadfe7e26d3bd1"
RUSTC_HOST = "x86_64-unknown-linux-gnu"
RUSTC_RELEASE = "1.94.1"
MPFR_SHA256 = "2156351fa3dedd04a7381c6ac7a8a26efa2d6fb08b80f8a2d644ccdd653710ae"
MPFR_VERSION = "4.2.1"
GMP_SHA256 = "0ccdfb6d6f5c039465f6d002cf7e4c072d48ac6a2cffc8dd6c748dec31592804"
GMP_VERSION = "6.3.0"
ABI_VERSION = 4

_FIXED_EXECUTABLE_SHA256 = {
    GIT.resolve(): "2a8c18fbf43da9f692d75474c72bea9dfd796c260b0f3dfe456376abc3bbd668",
    LDD.resolve(): "429938a30ba5d51f4cdba476e8f8f8b1595d51b14a665ab6edf642454ff662ea",
    READELF.resolve(): "6d54602a1ee13f1214973086bd60efe2dae4363f8f5ab7516eaaf3e259dca90e",
    LINKER.resolve(): "6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234",
}
_RUNTIME_ELF_ALLOWLIST = {
    "ELF_INTERPRETER": "6222a16be7f2d458d6870efe6e715fc0c8d45766fb79cf7dcc3125538d703e28",
    "libc.so.6": "511f825ee075610ac9c0f7f91e2c13de2000d0f7b859f6461137e809a0a009d0",
    "libgcc_s.so.1": "d93224d2b0dab4247598be683adca02f5cf00586f99c187579cd7e92058fb7cb",
    "libgmp.so.10": GMP_SHA256,
    "libmpfr.so.6": MPFR_SHA256,
}
_RUNTIME_ELF_PATHS = {
    "ELF_INTERPRETER": Path(
        "/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2"
    ).resolve(),
    "libc.so.6": Path("/usr/lib/x86_64-linux-gnu/libc.so.6").resolve(),
    "libgcc_s.so.1": Path("/usr/lib/x86_64-linux-gnu/libgcc_s.so.1").resolve(),
    "libgmp.so.10": GMP.resolve(),
    "libmpfr.so.6": MPFR.resolve(),
}

BUILD_CONTRACT = (
    "--edition=2021",
    "--crate-type=cdylib",
    "--crate-name=rei_source_bound_thermal",
    "-Copt-level=3",
    "-Ccodegen-units=1",
    "-Cstrip=symbols",
    "-Cembed-bitcode=no",
    "-Cmetadata={SOURCE_SHA256}",
    "-Clinker={AUTHENTICATED_LINKER}",
    "--remap-path-prefix={REPOSITORY}=/rei_bianchi",
    "-Lnative={NATIVE_LIBRARY_DIRECTORY}",
    "-Clink-arg=-Wl,--build-id=none",
    "-Clink-arg=-Wl,--disable-new-dtags",
    "-Clink-arg=-Wl,-rpath,{NATIVE_LIBRARY_DIRECTORY}",
    "-Clink-arg=-Wl,-l:libmpfr.so.6",
    "-Clink-arg=-Wl,-l:libgmp.so.10",
    "{SOURCE}",
    "-o{OUTPUT}",
)

PROCESS_BOUNDARY_BLOCKER = "RUST_BACKEND_CAPABILITY_PROCESS_BOUNDARY_MISSING"
PRESTART_RUNTIME_BLOCKER = (
    "BLOCKED_PRESTART_ELF_INTERPRETER_IDENTITY_NOT_ESTABLISHED"
)


class RustBackendError(RuntimeError):
    """Authenticated backend build, use, or admission failure."""


class RuntimeClosureError(RustBackendError):
    """Invocation-scoped input or Git closure validation failed."""

    def __init__(self, classification: str, detail: str = "") -> None:
        self.classification = classification
        super().__init__(f"{classification}: {detail}" if detail else classification)


_STATUS = {
    1: "INVALID_DIMENSION",
    2: "NULL_POINTER",
    3: "INVALID_INTERVAL",
    4: "ZERO_DIVISOR_INTERVAL",
    5: "SINGULAR_MIDPOINT",
    6: "NO_STRICT_SELF_INCLUSION",
    7: "NONFINITE_OUTPUT",
    8: "MISSING_DELTA_A",
    9: "MISSING_MIXED_TERM",
    10: "LENGTH_MISMATCH",
    11: "NATIVE_PANIC",
    12: "ALIASED_OUTPUT",
}

_RUNTIME_CLOSURE_KEYS = {
    "schema",
    "enforcement_scope",
    "declared_paths",
    "declared_import_roots",
    "forbidden_import_roots",
    "path_policy",
    "git_config_policy",
}
_DECLARED_PATH_KEYS = {"path", "sha256", "role"}
_DECLARED_PATH_ROLES = {
    "RUST_NUMERICAL_SOURCE",
    "PYTHON_CAPABILITY_BRIDGE",
    "IMPLICIT_CERTIFICATE_MODEL",
    "CERTIFICATE_GRAPH",
    "FOUR_SITE_OPERATOR_SEAM",
    "BASS_CUSTODY_SUBSTRATE",
    "RUST_IMPLEMENTATION_AMENDMENT",
    "RUST_BUILD_RECEIPT",
    "REIAFF1_CODEC",
    "TEST_AUTHORITY",
    "NONCODE_BLOCKER_LEDGER",
    "NONCODE_DERIVATION",
    "NONCODE_LITERATURE_CROSSCHECK",
    "NONCODE_SOURCE_MANIFEST",
    "NONCODE_WOLFRAM_RECEIPT",
    "NONCODE_WOLFRAM_SCRIPT",
    "NONCODE_INTAKE",
    "NONCODE_PACKAGE_MANIFEST",
}
_PATH_POLICY = {
    "resolve_symlinks": True,
    "reject_undeclared": True,
    "require_regular_file": True,
    "verify_sha256": True,
}
_GIT_CONFIG_POLICY = {
    "inspect_repo_local": True,
    "inspect_common": True,
    "inspect_worktree_when_enabled": True,
    "reject_extensions_partial_clone": True,
    "reject_promisor_remotes": True,
    "system_and_global_out_of_scope": True,
}


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("ascii")


def _canonical_digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_closed(mapping: Mapping[str, Any], keys: set[str], classification: str) -> None:
    if set(mapping) != keys:
        raise RuntimeClosureError(classification, ",".join(sorted(set(mapping) ^ keys)))


def _sanitized_environment() -> dict[str, str]:
    return {
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
        "SOURCE_DATE_EPOCH": "0",
        "TZ": "UTC",
    }


def _preauthenticate_file(
    path: Path,
    expected_sha256: str,
    *,
    classification: str,
) -> Path:
    try:
        resolved = Path(path).resolve(strict=True)
    except (FileNotFoundError, RuntimeError) as exc:
        raise RustBackendError(f"{classification}: {path}") from exc
    if not resolved.is_file() or _sha256(resolved) != expected_sha256:
        raise RustBackendError(f"{classification}: {resolved}")
    return resolved


def _run(
    arguments: Sequence[str],
    *,
    cwd: Path | None = None,
    expected_executable_sha256: str | None = None,
) -> str:
    if not arguments:
        raise RustBackendError("PREAUTH_EXECUTION_IDENTITY_NOT_ESTABLISHED: empty argv")
    executable = Path(arguments[0])
    if not executable.is_absolute():
        raise RustBackendError(
            f"PREAUTH_EXECUTION_IDENTITY_NOT_ESTABLISHED: {arguments[0]}"
        )
    try:
        resolved_executable = executable.resolve(strict=True)
    except (FileNotFoundError, RuntimeError) as exc:
        raise RustBackendError(
            f"PREAUTH_EXECUTION_IDENTITY_NOT_ESTABLISHED: {executable}"
        ) from exc
    expected = expected_executable_sha256 or _FIXED_EXECUTABLE_SHA256.get(
        resolved_executable
    )
    if expected is None:
        raise RustBackendError(
            f"PREAUTH_EXECUTION_IDENTITY_NOT_ESTABLISHED: {resolved_executable}"
        )
    _preauthenticate_file(
        resolved_executable,
        expected,
        classification="PREAUTH_EXECUTION_IDENTITY_NOT_ESTABLISHED",
    )
    command = (str(executable), *(str(argument) for argument in arguments[1:]))
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=_sanitized_environment(),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RustBackendError(f"COMMAND_FAILED: {' '.join(arguments)}\n{detail}")
    return completed.stdout


def _git_config_records(arguments: Sequence[str], repo: Path) -> list[tuple[str, str]]:
    output = _run((str(GIT), "-C", str(repo), *arguments, "--null", "--list"))
    records: list[tuple[str, str]] = []
    for record in output.split("\0"):
        if not record:
            continue
        if "\n" in record:
            key, value = record.split("\n", 1)
        elif "=" in record:
            key, value = record.split("=", 1)
        else:
            key, value = record, ""
        records.append((key.strip().lower(), value.strip().lower()))
    return records


def _validate_git_closure(repo: Path) -> tuple[str, ...]:
    observations: list[tuple[str, str]] = []
    observations.extend(_git_config_records(("config", "--local"), repo))

    common_dir_text = _run(
        (str(GIT), "-C", str(repo), "rev-parse", "--git-common-dir")
    ).strip()
    common_dir = Path(common_dir_text)
    if not common_dir.is_absolute():
        common_dir = (repo / common_dir).resolve(strict=True)
    common_config = common_dir / "config"
    if common_config.is_file():
        observations.extend(
            _git_config_records(("config", "--file", str(common_config)), repo)
        )

    worktree_config_enabled = any(
        key == "extensions.worktreeconfig" and value in {"true", "yes", "on", "1"}
        for key, value in observations
    )
    if worktree_config_enabled:
        observations.extend(_git_config_records(("config", "--worktree"), repo))

    for key, value in observations:
        if key == "extensions.partialclone" and value:
            raise RuntimeClosureError("GIT_PARTIAL_CLONE", f"{key}={value}")
        if key.startswith("remote.") and key.endswith(".promisor") and value in {
            "true",
            "yes",
            "on",
            "1",
        }:
            raise RuntimeClosureError("GIT_PROMISOR", key)
        if key.startswith("remote.") and key.endswith(".partialclonefilter") and value:
            raise RuntimeClosureError("GIT_PARTIAL_CLONE", key)
    return tuple(sorted({f"{key}={value}" for key, value in observations}))


def _repo_relative_path(raw: Any) -> str:
    if not isinstance(raw, str) or not raw:
        raise RuntimeClosureError("INVALID_DECLARED_PATH", repr(raw))
    pure = PurePosixPath(raw)
    if pure.is_absolute() or ".." in pure.parts or str(pure) != raw:
        raise RuntimeClosureError("INVALID_DECLARED_PATH", raw)
    return raw


def _valid_digest(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and value == value.lower()
        and all(character in "0123456789abcdef" for character in value)
    )


@dataclass(frozen=True)
class _RuntimeAuthority:
    schema: str
    enforcement_scope: str
    input_lock_sha256: str
    declared_path_count: int
    allowed_paths: frozenset[Path]
    allowed_import_roots: frozenset[str]
    forbidden_import_roots: frozenset[str]
    git_record_count: int


_RUNTIME_CAPABILITY_TOKEN = object()
_ACTIVE_RUNTIME_CAPABILITY: contextvars.ContextVar[
    RuntimeClosureCapability | None
] = contextvars.ContextVar("rei_active_runtime_closure_capability", default=None)
_AUDIT_HOOK_INSTALLED = False


class RuntimeClosureCapability:
    """Factory-only observer for one active Python invocation.

    The capability is deliberately invocation scoped.  It records and rejects
    Python ``open``/``import`` events and process/native-load entrypoints while
    the callback is running; it is not represented as caller-provided evidence.
    """

    __slots__ = (
        "_authority",
        "_active",
        "_observed_paths",
        "_observed_imports",
        "_violation",
        "_seal",
    )

    def __init__(
        self,
        authority: _RuntimeAuthority,
        *,
        _seal: object | None = None,
    ) -> None:
        if _seal is not _RUNTIME_CAPABILITY_TOKEN:
            raise RuntimeClosureError("RUNTIME_OBSERVATION_CAPABILITY_FACTORY_REQUIRED")
        self._authority = authority
        self._active = False
        self._observed_paths: set[Path] = set()
        self._observed_imports: set[str] = set()
        self._violation: RuntimeClosureError | None = None
        self._seal = _seal

    def _require_active(self) -> None:
        if not self._active or self._seal is not _RUNTIME_CAPABILITY_TOKEN:
            raise RuntimeClosureError("RUNTIME_OBSERVATION_CAPABILITY_INACTIVE")

    def _reject(self, classification: str, detail: str) -> None:
        violation = RuntimeClosureError(classification, detail)
        if self._violation is None:
            self._violation = violation
        raise violation

    def _observe_path(self, raw_path: Any) -> None:
        self._require_active()
        if raw_path is None or isinstance(raw_path, int):
            return
        try:
            decoded = os.fsdecode(raw_path)
        except TypeError as exc:
            self._reject("UNDECLARED_PATH", repr(raw_path))
            raise AssertionError("unreachable") from exc
        resolved = Path(decoded).resolve(strict=False)
        if resolved not in self._authority.allowed_paths:
            self._reject("UNDECLARED_PATH", decoded)
        self._observed_paths.add(resolved)

    def _observe_import(self, imported: Any) -> None:
        self._require_active()
        if not isinstance(imported, str) or not imported:
            self._reject("UNDECLARED_IMPORT", repr(imported))
        root_name = imported.split(".", 1)[0]
        if root_name in self._authority.forbidden_import_roots:
            self._reject("FORBIDDEN_IMPORT", imported)
        if root_name not in self._authority.allowed_import_roots:
            self._reject("UNDECLARED_IMPORT", imported)
        self._observed_imports.add(root_name)


def _runtime_audit_hook(event: str, arguments: tuple[Any, ...]) -> None:
    capability = _ACTIVE_RUNTIME_CAPABILITY.get()
    if capability is None:
        return
    if event == "open" and arguments:
        capability._observe_path(arguments[0])
    elif event == "import" and arguments:
        capability._observe_import(arguments[0])
    elif event == "ctypes.dlopen" and arguments:
        capability._observe_path(arguments[0])
    elif event == "subprocess.Popen" and arguments:
        capability._observe_path(arguments[0])
    elif event in {"_thread.start_new_thread", "os.fork", "os.forkpty"}:
        capability._reject("UNOBSERVED_EXECUTION_CONTEXT", event)


def _install_runtime_audit_hook() -> None:
    global _AUDIT_HOOK_INSTALLED
    if not _AUDIT_HOOK_INSTALLED:
        sys.addaudithook(_runtime_audit_hook)
        _AUDIT_HOOK_INSTALLED = True


def _prepare_runtime_authority(
    *,
    repo: Path,
    stage_dir: Path,
    input_lock_path: Path | None,
    additional_allowed_paths: Sequence[Path] = (),
) -> _RuntimeAuthority:
    root = Path(repo).resolve(strict=True)
    stage = Path(stage_dir).resolve(strict=True)
    lock_path = (
        Path(input_lock_path).resolve(strict=True)
        if input_lock_path is not None
        else (stage / "INPUT_LOCK.json").resolve(strict=True)
    )
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if not isinstance(lock, dict) or not isinstance(lock.get("runtime_closure"), dict):
        raise RuntimeClosureError("RUNTIME_CLOSURE_MISSING")
    closure = lock["runtime_closure"]
    _require_closed(closure, _RUNTIME_CLOSURE_KEYS, "RUNTIME_CLOSURE_SCHEMA_NOT_CLOSED")
    if closure["schema"] != "rei-runtime-input-closure/v2":
        raise RuntimeClosureError("RUNTIME_CLOSURE_SCHEMA_MISMATCH")
    if closure["enforcement_scope"] != "INVOCATION_SCOPED_NOT_GLOBAL_INTERCEPTION":
        raise RuntimeClosureError("RUNTIME_CLOSURE_SCOPE_MISMATCH")
    if closure["path_policy"] != _PATH_POLICY:
        raise RuntimeClosureError("PATH_POLICY_MISMATCH")
    if closure["git_config_policy"] != _GIT_CONFIG_POLICY:
        raise RuntimeClosureError("GIT_CONFIG_POLICY_MISMATCH")
    if closure["forbidden_import_roots"] != ["jax", "jaxlib"]:
        raise RuntimeClosureError("FORBIDDEN_IMPORT_POLICY_MISMATCH")

    import_roots = closure["declared_import_roots"]
    if (
        not isinstance(import_roots, list)
        or not all(isinstance(root_name, str) and root_name for root_name in import_roots)
        or import_roots != sorted(set(import_roots))
    ):
        raise RuntimeClosureError("DECLARED_IMPORTS_NOT_CLOSED")

    declared_records = closure["declared_paths"]
    if not isinstance(declared_records, list):
        raise RuntimeClosureError("DECLARED_PATHS_NOT_CLOSED")
    declared: dict[Path, Mapping[str, Any]] = {}
    for record in declared_records:
        if not isinstance(record, dict):
            raise RuntimeClosureError("DECLARED_PATHS_NOT_CLOSED")
        _require_closed(record, _DECLARED_PATH_KEYS, "DECLARED_PATH_SCHEMA_NOT_CLOSED")
        relative = _repo_relative_path(record["path"])
        role = record["role"]
        if role not in _DECLARED_PATH_ROLES:
            raise RuntimeClosureError("DECLARED_PATH_ROLE_INVALID", str(role))
        if not _valid_digest(record["sha256"]):
            raise RuntimeClosureError("INVALID_SHA256", relative)
        resolved = (root / relative).resolve(strict=False)
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise RuntimeClosureError("UNDECLARED_PATH", relative) from exc
        if not resolved.is_file():
            raise RuntimeClosureError("DECLARED_PATH_NOT_REGULAR", relative)
        observed_digest = _sha256(resolved)
        if observed_digest != record["sha256"]:
            raise RuntimeClosureError("HASH_MISMATCH", relative)
        if resolved in declared:
            raise RuntimeClosureError("DECLARED_PATH_DUPLICATE", relative)
        declared[resolved] = record

    allowed_paths = set(declared)
    allowed_paths.add(lock_path)
    for external in additional_allowed_paths:
        allowed_paths.add(Path(external).resolve(strict=False))
    git_records = _validate_git_closure(root)
    return _RuntimeAuthority(
        schema=closure["schema"],
        enforcement_scope=closure["enforcement_scope"],
        input_lock_sha256=_sha256(lock_path),
        declared_path_count=len(declared),
        allowed_paths=frozenset(allowed_paths),
        allowed_import_roots=frozenset(import_roots),
        forbidden_import_roots=frozenset(closure["forbidden_import_roots"]),
        git_record_count=len(git_records),
    )


def _observe_runtime_invocation(
    authority: _RuntimeAuthority,
    invocation: Callable[[RuntimeClosureCapability], Any],
) -> tuple[Any, RuntimeClosureCapability]:
    if not callable(invocation):
        raise RuntimeClosureError("RUNTIME_OBSERVATION_CAPABILITY_REQUIRED")
    if _ACTIVE_RUNTIME_CAPABILITY.get() is not None:
        raise RuntimeClosureError("RUNTIME_OBSERVATION_NESTING_FORBIDDEN")
    _install_runtime_audit_hook()
    capability = RuntimeClosureCapability(authority, _seal=_RUNTIME_CAPABILITY_TOKEN)
    capability._active = True
    token = _ACTIVE_RUNTIME_CAPABILITY.set(capability)
    original_import = builtins.__import__

    def observed_import(name: str, *args: Any, **kwargs: Any) -> Any:
        active = _ACTIVE_RUNTIME_CAPABILITY.get()
        if active is capability:
            capability._observe_import(name)
        return original_import(name, *args, **kwargs)

    builtins.__import__ = observed_import
    failure: BaseException | None = None
    result: Any = None
    try:
        result = invocation(capability)
    except BaseException as exc:
        failure = exc
    finally:
        builtins.__import__ = original_import
        _ACTIVE_RUNTIME_CAPABILITY.reset(token)
        capability._active = False
    if capability._violation is not None:
        if failure is capability._violation or failure is None:
            raise capability._violation
        raise capability._violation from failure
    if failure is not None:
        raise failure
    return result, capability


def validate_runtime_closure(
    *,
    repo: Path,
    stage_dir: Path,
    input_lock_path: Path | None = None,
    observed_paths: Sequence[Path] = (),
    observed_imports: Sequence[str] = (),
    invocation: Callable[[RuntimeClosureCapability], Any] | None = None,
) -> dict[str, Any]:
    """Run and attest one automatically observed Python invocation.

    ``observed_paths`` and ``observed_imports`` remain in the signature solely
    so legacy self-reported evidence fails with a typed classification.
    """

    if observed_paths or observed_imports:
        raise RuntimeClosureError("SELF_REPORTED_OBSERVATION_FORBIDDEN")
    if invocation is None:
        raise RuntimeClosureError("RUNTIME_OBSERVATION_CAPABILITY_REQUIRED")
    authority = _prepare_runtime_authority(
        repo=repo,
        stage_dir=stage_dir,
        input_lock_path=input_lock_path,
    )
    _, capability = _observe_runtime_invocation(authority, invocation)
    return {
        "status": "PASS",
        "schema": authority.schema,
        "enforcement_scope": authority.enforcement_scope,
        "input_lock_sha256": authority.input_lock_sha256,
        "declared_path_count": authority.declared_path_count,
        "observed_path_count": len(capability._observed_paths),
        "observed_import_count": len(capability._observed_imports),
        "git_record_count": authority.git_record_count,
    }


def resolve_rustc_locator() -> Path:
    """Resolve a compiler locator without treating its path as identity."""

    explicit = os.environ.get("REI_RUSTC_1_94_1")
    prefix = os.environ.get("RUST_1_94_1_PREFIX")
    locator = Path(explicit) if explicit else Path(prefix) / "bin/rustc" if prefix else DEFAULT_RUSTC
    if not locator.is_file() or not os.access(locator, os.X_OK):
        raise RustBackendError("RUSTC_LOCATOR_UNAVAILABLE")
    return locator.resolve(strict=True)


def _ldd_records(path: Path) -> dict[str, Path]:
    report = _run((str(LDD), str(Path(path).resolve(strict=True))))
    records: dict[str, Path] = {}
    for raw_line in report.splitlines():
        line = raw_line.strip()
        if "=>" in line:
            soname, remainder = line.split("=>", 1)
            target_text = remainder.split(" (", 1)[0].strip()
            if target_text == "not found":
                raise RustBackendError(f"DEPENDENCY_NOT_FOUND: {soname.strip()}")
            records[soname.strip()] = Path(target_text).resolve(strict=True)
        elif line.startswith("/"):
            target_text = line.split(" (", 1)[0].strip()
            records["ELF_INTERPRETER"] = Path(target_text).resolve(strict=True)
    return records


def _verify_dynamic_library_closure(
    target: Path,
    required_names: set[str],
) -> tuple[tuple[str, str], ...]:
    """Hash the fixed dependency set before ``ldd`` or ``ctypes`` can load it."""

    for name in sorted(required_names):
        _preauthenticate_file(
            _RUNTIME_ELF_PATHS[name],
            _RUNTIME_ELF_ALLOWLIST[name],
            classification=(
                "PREAUTH_DYNAMIC_LIBRARY_DEPENDENCY_IDENTITY_NOT_ESTABLISHED"
            ),
        )
    records = _ldd_records(target)
    if set(records) != required_names:
        raise RustBackendError(
            "PREAUTH_DYNAMIC_LIBRARY_DEPENDENCY_IDENTITY_NOT_ESTABLISHED: "
            f"{target}"
        )
    result: list[tuple[str, str]] = []
    for name in sorted(required_names):
        if records[name] != _RUNTIME_ELF_PATHS[name]:
            raise RustBackendError(
                "PREAUTH_DYNAMIC_LIBRARY_DEPENDENCY_IDENTITY_NOT_ESTABLISHED: "
                f"{name}"
            )
        result.append((name, _RUNTIME_ELF_ALLOWLIST[name]))
    return tuple(result)


def _rustc_closure_digest(rustc: Path) -> str:
    records = _ldd_records(rustc.resolve(strict=True))
    owned = [
        {"soname": soname, "sha256": _sha256(target)}
        for soname, target in sorted(records.items())
        if soname.startswith("librustc_driver-") or soname.startswith("libLLVM.so")
    ]
    if len(owned) < 2:
        raise RustBackendError("RUSTC_CLOSURE_INCOMPLETE")
    return _canonical_digest({"owned_dynamic_libraries": owned})


def _runtime_versions(mpfr_path: Path, gmp_path: Path) -> tuple[str, str]:
    admitted_mpfr = _preauthenticate_file(
        mpfr_path,
        MPFR_SHA256,
        classification="PREAUTH_DYNAMIC_LIBRARY_IDENTITY_NOT_ESTABLISHED",
    )
    admitted_gmp = _preauthenticate_file(
        gmp_path,
        GMP_SHA256,
        classification="PREAUTH_DYNAMIC_LIBRARY_IDENTITY_NOT_ESTABLISHED",
    )
    mpfr = ctypes.CDLL(str(admitted_mpfr), mode=ctypes.RTLD_GLOBAL)
    mpfr.mpfr_get_version.argtypes = []
    mpfr.mpfr_get_version.restype = ctypes.c_char_p
    mpfr_value = mpfr.mpfr_get_version()
    if not mpfr_value:
        raise RustBackendError("MPFR_VERSION_UNAVAILABLE")
    gmp = ctypes.CDLL(str(admitted_gmp), mode=ctypes.RTLD_GLOBAL)
    try:
        gmp_value = ctypes.c_char_p.in_dll(gmp, "__gmp_version").value
    except ValueError as exc:
        raise RustBackendError("GMP_VERSION_UNAVAILABLE") from exc
    if not gmp_value:
        raise RustBackendError("GMP_VERSION_UNAVAILABLE")
    return mpfr_value.decode("ascii"), gmp_value.decode("ascii")


class _MpfrRawLayout(ctypes.Structure):
    _fields_ = (
        ("precision", ctypes.c_long),
        ("sign", ctypes.c_int),
        ("exponent", ctypes.c_long),
        ("limbs", ctypes.POINTER(ctypes.c_ulong)),
    )


def _local_layout() -> dict[str, int]:
    return {
        "pointer_width_bits": ctypes.sizeof(ctypes.c_void_p) * 8,
        "mpfr_raw_size": ctypes.sizeof(_MpfrRawLayout),
        "mpfr_raw_align": ctypes.alignment(_MpfrRawLayout),
        "limb_bits": ctypes.sizeof(ctypes.c_ulong) * 8,
    }


def _parse_rustc_report(report: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in report.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            parsed[key.strip()] = value.strip()
    required = {"release", "commit-hash", "host"}
    if not required.issubset(parsed):
        raise RustBackendError("RUSTC_VERBOSE_REPORT_INCOMPLETE")
    return parsed


def _build_contract_sha256() -> str:
    return _canonical_digest({"rustc_arguments": list(BUILD_CONTRACT)})


_AMENDMENT_KEYS = {
    "schema",
    "backend_source",
    "backend_source_sha256",
    "abi_version",
    "precision_bits",
    "rounding_policy",
    "load_bearing_boundary",
    "claim_ceiling",
    "expected_artifact_sha256",
    "deterministic_build_contract_sha256",
    "rustc",
    "linker",
    "mpfr",
    "gmp",
    "native_layout",
}


def _authenticate_runtime_observed(*, stage_dir: Path) -> dict[str, Any]:
    """Return an amendment-checked identity inside an active observer."""

    stage = Path(stage_dir).resolve(strict=True)
    source = stage / "rust/source_bound_thermal.rs"
    amendment = json.loads(
        (stage / "RUST_IMPLEMENTATION_AMENDMENT.json").read_text(encoding="utf-8")
    )
    if not isinstance(amendment, dict) or set(amendment) != _AMENDMENT_KEYS:
        raise RustBackendError("AMENDMENT_SCHEMA_NOT_CLOSED")
    nested_keys = {
        "rustc": {"sha256", "commit", "host", "release", "verbose_report_sha256", "closure_sha256"},
        "linker": {"sha256", "report_sha256"},
        "mpfr": {"soname", "sha256", "version"},
        "gmp": {"soname", "sha256", "version"},
        "native_layout": {"pointer_width_bits", "mpfr_raw_size", "mpfr_raw_align", "limb_bits"},
    }
    if any(
        not isinstance(amendment[name], dict) or set(amendment[name]) != expected
        for name, expected in nested_keys.items()
    ):
        raise RustBackendError("AMENDMENT_SCHEMA_NOT_CLOSED")
    if amendment["schema"] != "rei-rust-implementation-amendment/v2":
        raise RustBackendError("AMENDMENT_SCHEMA_MISMATCH")
    if amendment["backend_source"] != "rust/source_bound_thermal.rs":
        raise RustBackendError("AMENDMENT_SOURCE_LOCATOR_MISMATCH")
    if amendment["claim_ceiling"] != "NO_PASS_FIRST_CANONICAL_INTERVAL":
        raise RustBackendError("AMENDMENT_CLAIM_CEILING_MISMATCH")
    if not isinstance(amendment["load_bearing_boundary"], str) or not amendment[
        "load_bearing_boundary"
    ]:
        raise RustBackendError("AMENDMENT_LOAD_BOUNDARY_MISMATCH")

    source_sha256 = _sha256(source)
    if source_sha256 != amendment["backend_source_sha256"]:
        raise RustBackendError("RUNTIME_IDENTITY_MISMATCH: source_sha256")
    rustc = resolve_rustc_locator()
    rustc_sha256 = _sha256(rustc)
    if rustc_sha256 != amendment["rustc"]["sha256"]:
        raise RustBackendError(
            "PREAUTH_EXECUTION_IDENTITY_NOT_ESTABLISHED: rustc"
        )
    linker = _preauthenticate_file(
        LINKER,
        amendment["linker"]["sha256"],
        classification="PREAUTH_EXECUTION_IDENTITY_NOT_ESTABLISHED",
    )
    mpfr_path = _preauthenticate_file(
        MPFR,
        amendment["mpfr"]["sha256"],
        classification="PREAUTH_DYNAMIC_LIBRARY_IDENTITY_NOT_ESTABLISHED",
    )
    gmp_path = _preauthenticate_file(
        GMP,
        amendment["gmp"]["sha256"],
        classification="PREAUTH_DYNAMIC_LIBRARY_IDENTITY_NOT_ESTABLISHED",
    )
    _verify_dynamic_library_closure(
        mpfr_path,
        {"ELF_INTERPRETER", "libc.so.6", "libgmp.so.10"},
    )
    _verify_dynamic_library_closure(
        gmp_path,
        {"ELF_INTERPRETER", "libc.so.6"},
    )

    rustc_report = _run(
        (str(rustc), "-Vv"),
        expected_executable_sha256=amendment["rustc"]["sha256"],
    )
    rustc_fields = _parse_rustc_report(rustc_report)
    linker_report = _run((str(LINKER), "--version"))
    mpfr_version, gmp_version = _runtime_versions(mpfr_path, gmp_path)
    identity: dict[str, Any] = {
        "abi_version": ABI_VERSION,
        "precision_bits": PRECISION_BITS,
        "rounding_policy": ROUNDING_POLICY,
        "source_sha256": source_sha256,
        "rustc_sha256": rustc_sha256,
        "rustc_commit": rustc_fields["commit-hash"],
        "rustc_host": rustc_fields["host"],
        "rustc_release": rustc_fields["release"],
        "rustc_verbose_report_sha256": hashlib.sha256(
            rustc_report.encode("utf-8")
        ).hexdigest(),
        "rustc_closure_sha256": _rustc_closure_digest(rustc),
        "linker_sha256": _sha256(linker),
        "linker_report_sha256": hashlib.sha256(
            linker_report.encode("utf-8")
        ).hexdigest(),
        "mpfr_soname": "libmpfr.so.6",
        "mpfr_sha256": _sha256(mpfr_path),
        "mpfr_version": mpfr_version,
        "gmp_soname": "libgmp.so.10",
        "gmp_sha256": _sha256(gmp_path),
        "gmp_version": gmp_version,
        "deterministic_build_contract_sha256": _build_contract_sha256(),
        **_local_layout(),
    }
    expected = {
        "abi_version": amendment["abi_version"],
        "precision_bits": amendment["precision_bits"],
        "rounding_policy": amendment["rounding_policy"],
        "source_sha256": amendment["backend_source_sha256"],
        "rustc_sha256": amendment["rustc"]["sha256"],
        "rustc_commit": amendment["rustc"]["commit"],
        "rustc_host": amendment["rustc"]["host"],
        "rustc_release": amendment["rustc"]["release"],
        "rustc_verbose_report_sha256": amendment["rustc"]["verbose_report_sha256"],
        "rustc_closure_sha256": amendment["rustc"]["closure_sha256"],
        "linker_sha256": amendment["linker"]["sha256"],
        "linker_report_sha256": amendment["linker"]["report_sha256"],
        "mpfr_soname": amendment["mpfr"]["soname"],
        "mpfr_sha256": amendment["mpfr"]["sha256"],
        "mpfr_version": amendment["mpfr"]["version"],
        "gmp_soname": amendment["gmp"]["soname"],
        "gmp_sha256": amendment["gmp"]["sha256"],
        "gmp_version": amendment["gmp"]["version"],
        "deterministic_build_contract_sha256": amendment[
            "deterministic_build_contract_sha256"
        ],
        **amendment["native_layout"],
    }
    if identity != expected:
        mismatches = sorted(key for key in identity if identity[key] != expected.get(key))
        raise RustBackendError(f"RUNTIME_IDENTITY_MISMATCH: {','.join(mismatches)}")
    return identity


@dataclass(frozen=True)
class BackendReceipt:
    schema: str
    artifact_sha256: str
    expected_artifact_sha256: str
    runtime_identity_sha256: str
    source_sha256: str
    rustc_sha256: str
    rustc_commit: str
    rustc_host: str
    rustc_closure_sha256: str
    linker_sha256: str
    mpfr_soname: str
    mpfr_sha256: str
    mpfr_version: str
    gmp_soname: str
    gmp_sha256: str
    gmp_version: str
    ondisk_runtime_elf_closure_sha256: str
    abi_version: int
    precision_bits: int
    rounding_policy: str
    pointer_width_bits: int
    mpfr_raw_size: int
    mpfr_raw_align: int
    limb_bits: int
    deterministic_build_contract_sha256: str

    def to_mapping(self) -> dict[str, Any]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.to_mapping())

    def identity_sha256(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


_CAPABILITY_TOKEN = object()


class AuthenticatedBackend:
    """Factory-minted type-state for one currently authenticated artifact."""

    __slots__ = (
        "_artifact_path",
        "_receipt",
        "_receipt_digest",
        "_runtime_authority",
        "_seal",
    )

    def __init__(
        self,
        artifact_path: Path,
        receipt: BackendReceipt,
        runtime_authority: _RuntimeAuthority | None = None,
        *,
        _seal: object | None = None,
    ) -> None:
        if _seal is not _CAPABILITY_TOKEN:
            raise RustBackendError("BACKEND_CAPABILITY_FACTORY_REQUIRED")
        if type(runtime_authority) is not _RuntimeAuthority:
            raise RuntimeClosureError("RUNTIME_OBSERVATION_CAPABILITY_REQUIRED")
        self._artifact_path = Path(artifact_path).resolve(strict=True)
        self._receipt = receipt
        self._receipt_digest = receipt.identity_sha256()
        self._runtime_authority = runtime_authority
        self._seal = _seal

    @property
    def artifact_path(self) -> Path:
        return self._artifact_path

    @property
    def receipt(self) -> BackendReceipt:
        return self._receipt

    def __copy__(self) -> None:
        raise RustBackendError("BACKEND_CAPABILITY_NONCOPYABLE")

    def __deepcopy__(self, memo: Any) -> None:
        del memo
        raise RustBackendError("BACKEND_CAPABILITY_NONCOPYABLE")

    def __reduce__(self) -> None:
        raise RustBackendError("BACKEND_CAPABILITY_NONTRANSFERABLE")


def _worktree_roots(repo: Path) -> tuple[Path, ...]:
    report = _run((str(GIT), "worktree", "list", "--porcelain"), cwd=repo)
    roots = tuple(
        Path(line.removeprefix("worktree ")).resolve(strict=True)
        for line in report.splitlines()
        if line.startswith("worktree ")
    )
    if not roots:
        raise RustBackendError("WORKTREE_ENUMERATION_EMPTY")
    return roots


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _artifact_dependencies(artifact: Path) -> tuple[tuple[str, str], ...]:
    for soname, expected_sha256 in sorted(_RUNTIME_ELF_ALLOWLIST.items()):
        dependency = _RUNTIME_ELF_PATHS[soname]
        if not dependency.is_file() or _sha256(dependency) != expected_sha256:
            raise RustBackendError(f"BACKEND_DEPENDENCY_HASH_MISMATCH: {soname}")
    records = _ldd_records(artifact)
    observed_names = set(records)
    required_names = set(_RUNTIME_ELF_ALLOWLIST)
    if observed_names != required_names:
        missing = ",".join(sorted(required_names - observed_names))
        unexpected = ",".join(sorted(observed_names - required_names))
        raise RustBackendError(
            f"BACKEND_DEPENDENCY_CLOSURE_MISMATCH: missing={missing};unexpected={unexpected}"
        )
    result: list[tuple[str, str]] = []
    for soname, expected_sha256 in _RUNTIME_ELF_ALLOWLIST.items():
        target = records[soname]
        if target != _RUNTIME_ELF_PATHS[soname]:
            raise RustBackendError(f"BACKEND_DEPENDENCY_PATH_MISMATCH: {soname}")
        observed = _sha256(target)
        if observed != expected_sha256:
            raise RustBackendError(f"BACKEND_DEPENDENCY_HASH_MISMATCH: {soname}")
        result.append((soname, observed))
    if any(soname.lower().startswith("libpython") for soname in records):
        raise RustBackendError("BACKEND_PYTHON_DEPENDENCY_FORBIDDEN")
    dynamic = _run((str(READELF), "-d", str(artifact.resolve(strict=True))))
    expected_rpath = str(NATIVE_LIBRARY_DIRECTORY)
    if "(RPATH)" not in dynamic or expected_rpath not in dynamic:
        raise RustBackendError("BACKEND_FIXED_RPATH_MISSING")
    return tuple(sorted(result))


def _configure_library(library: ctypes.CDLL) -> None:
    for name in (
        "rei_mpfr_precision_bits",
        "rei_source_bound_abi_version",
        "rei_pointer_width_bits",
        "rei_limb_bits",
    ):
        function = getattr(library, name)
        function.argtypes = []
        function.restype = ctypes.c_uint32
    for name in ("rei_mpfr_raw_size", "rei_mpfr_raw_align"):
        function = getattr(library, name)
        function.argtypes = []
        function.restype = ctypes.c_size_t

    double_pointer = ctypes.POINTER(ctypes.c_double)
    unsigned_pointer = ctypes.POINTER(ctypes.c_uint32)
    size = ctypes.c_size_t
    library.rei_validate_lengths_mpfr256.argtypes = [size, size, size]
    library.rei_validate_lengths_mpfr256.restype = ctypes.c_int
    library.rei_interval_divide_mpfr256.argtypes = [
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        double_pointer,
        double_pointer,
    ]
    library.rei_interval_divide_mpfr256.restype = ctypes.c_int
    library.rei_certify_linear_mpfr256.argtypes = (
        [size, size, size]
        + [double_pointer] * 6
        + [double_pointer] * 11
        + [unsigned_pointer]
    )
    library.rei_certify_linear_mpfr256.restype = ctypes.c_int
    library.rei_certify_tangent_mpfr256.argtypes = (
        [size, size, size]
        + [double_pointer] * 10
        + [double_pointer] * 11
        + [unsigned_pointer]
    )
    library.rei_certify_tangent_mpfr256.restype = ctypes.c_int
    library.rei_certify_mixed_vf_mpfr256.argtypes = (
        [size, size, size] + [double_pointer] * 29 + [unsigned_pointer]
    )
    library.rei_certify_mixed_vf_mpfr256.restype = ctypes.c_int
    library.rei_diagnostic_mixed_rhs_mpfr256.argtypes = (
        [size, size, size] + [double_pointer] * 16
    )
    library.rei_diagnostic_mixed_rhs_mpfr256.restype = ctypes.c_int


def _load_library(
    artifact: Path,
    dependencies: tuple[tuple[str, str], ...] | None = None,
) -> ctypes.CDLL:
    verified = _artifact_dependencies(artifact)
    if dependencies is not None and verified != dependencies:
        raise RustBackendError("BACKEND_DEPENDENCY_CLOSURE_MISMATCH")
    if dict(verified) != _RUNTIME_ELF_ALLOWLIST:
        raise RustBackendError("BACKEND_DEPENDENCY_CLOSURE_MISMATCH")
    mpfr_path = _RUNTIME_ELF_PATHS["libmpfr.so.6"]
    gmp_path = _RUNTIME_ELF_PATHS["libgmp.so.10"]
    if _runtime_versions(mpfr_path, gmp_path) != (MPFR_VERSION, GMP_VERSION):
        raise RustBackendError("BACKEND_DEPENDENCY_VERSION_MISMATCH")
    admitted_artifact = artifact.resolve(strict=True)
    library = ctypes.CDLL(str(admitted_artifact))
    _configure_library(library)
    return library


def _native_facts(library: ctypes.CDLL) -> dict[str, int]:
    return {
        "abi_version": int(library.rei_source_bound_abi_version()),
        "precision_bits": int(library.rei_mpfr_precision_bits()),
        "pointer_width_bits": int(library.rei_pointer_width_bits()),
        "mpfr_raw_size": int(library.rei_mpfr_raw_size()),
        "mpfr_raw_align": int(library.rei_mpfr_raw_align()),
        "limb_bits": int(library.rei_limb_bits()),
    }


def _expected_native_facts(receipt: BackendReceipt) -> dict[str, int]:
    return {
        "abi_version": receipt.abi_version,
        "precision_bits": receipt.precision_bits,
        "pointer_width_bits": receipt.pointer_width_bits,
        "mpfr_raw_size": receipt.mpfr_raw_size,
        "mpfr_raw_align": receipt.mpfr_raw_align,
        "limb_bits": receipt.limb_bits,
    }


def _require_backend(backend: AuthenticatedBackend) -> AuthenticatedBackend:
    if (
        type(backend) is not AuthenticatedBackend
        or backend._seal is not _CAPABILITY_TOKEN
        or type(backend._runtime_authority) is not _RuntimeAuthority
    ):
        raise RustBackendError("BACKEND_CAPABILITY_REQUIRED")
    return backend


def _validate_backend_observed(backend: AuthenticatedBackend) -> ctypes.CDLL:
    authenticated = _require_backend(backend)
    receipt = authenticated.receipt
    artifact = authenticated.artifact_path
    if receipt.identity_sha256() != authenticated._receipt_digest:
        raise RustBackendError("BACKEND_RECEIPT_MUTATED")
    observed_artifact = _sha256(artifact)
    if observed_artifact != receipt.artifact_sha256:
        raise RustBackendError("BACKEND_ARTIFACT_HASH_MISMATCH")
    if receipt.artifact_sha256 != receipt.expected_artifact_sha256:
        raise RustBackendError("BACKEND_ARTIFACT_NOT_PINNED")
    dependencies = _artifact_dependencies(artifact)
    expected_dependencies = tuple(sorted(_RUNTIME_ELF_ALLOWLIST.items()))
    if dependencies != expected_dependencies or _canonical_digest(
        {"runtime_elf_closure": list(dependencies)}
    ) != receipt.ondisk_runtime_elf_closure_sha256:
        raise RustBackendError("BACKEND_DEPENDENCY_CLOSURE_MISMATCH")
    library = _load_library(artifact, dependencies)
    if _native_facts(library) != _expected_native_facts(receipt):
        raise RustBackendError("BACKEND_NATIVE_FACT_MISMATCH")
    return library


def _validate_backend(backend: AuthenticatedBackend) -> ctypes.CDLL:
    authenticated = _require_backend(backend)
    library, _ = _observe_runtime_invocation(
        authenticated._runtime_authority,
        lambda _capability: _validate_backend_observed(authenticated),
    )
    return library


def _postvalidate_backend(backend: AuthenticatedBackend) -> None:
    _validate_backend(backend)


def _runtime_observation_paths(
    stage: Path,
    artifact: Path | None = None,
) -> tuple[Path, ...]:
    """Resolve the closed external runtime set before observation starts.

    The compiler is hash-admitted before ``ldd`` can inspect it.  The returned
    paths are not an authority by themselves: the amendment, Rust closure
    digest, fixed tool digests, and ELF allowlist are rechecked while the
    observed invocation runs.
    """

    amendment = json.loads(
        (stage / "RUST_IMPLEMENTATION_AMENDMENT.json").read_text(encoding="utf-8")
    )
    if not isinstance(amendment, dict) or not isinstance(amendment.get("rustc"), dict):
        raise RustBackendError("AMENDMENT_SCHEMA_NOT_CLOSED")
    rustc = resolve_rustc_locator()
    _preauthenticate_file(
        rustc,
        amendment["rustc"].get("sha256", ""),
        classification="PREAUTH_EXECUTION_IDENTITY_NOT_ESTABLISHED",
    )
    rustc_dependencies = _ldd_records(rustc)
    paths = {
        GIT.resolve(),
        LDD.resolve(),
        READELF.resolve(),
        LINKER.resolve(),
        rustc,
        MPFR.resolve(),
        GMP.resolve(),
        *_RUNTIME_ELF_PATHS.values(),
        *rustc_dependencies.values(),
    }
    if artifact is not None:
        paths.add(artifact.resolve(strict=False))
    return tuple(paths)


def _base_runtime_observation_paths(
    artifact: Path | None = None,
) -> tuple[Path, ...]:
    """Paths fixed independently of amendment contents for phase-one intake."""

    paths = {
        GIT.resolve(),
        LDD.resolve(),
        READELF.resolve(),
        LINKER.resolve(),
        resolve_rustc_locator(),
        MPFR.resolve(),
        GMP.resolve(),
        *_RUNTIME_ELF_PATHS.values(),
    }
    if artifact is not None:
        paths.add(artifact.resolve(strict=False))
    return tuple(paths)


def authenticate_runtime(*, stage_dir: Path) -> dict[str, Any]:
    """Return a path-free identity from an automatically observed invocation."""

    stage = Path(stage_dir).resolve(strict=True)
    repo = stage.parents[1]
    intake_authority = _prepare_runtime_authority(
        repo=repo,
        stage_dir=stage,
        input_lock_path=stage / "INPUT_LOCK.json",
        additional_allowed_paths=_base_runtime_observation_paths(),
    )
    external_paths, _ = _observe_runtime_invocation(
        intake_authority,
        lambda _capability: _runtime_observation_paths(stage),
    )
    authority = _prepare_runtime_authority(
        repo=repo,
        stage_dir=stage,
        input_lock_path=stage / "INPUT_LOCK.json",
        additional_allowed_paths=external_paths,
    )
    identity, _ = _observe_runtime_invocation(
        authority,
        lambda _capability: _authenticate_runtime_observed(stage_dir=stage),
    )
    return identity


def _build_authenticated_backend_observed(
    *,
    stage_dir: Path,
    output_dir: Path,
    runtime_authority: _RuntimeAuthority,
) -> AuthenticatedBackend:
    stage = Path(stage_dir).resolve(strict=True)
    repo = stage.parents[1]
    raw_output = Path(output_dir)
    if raw_output.is_symlink():
        raise RustBackendError("BUILD_OUTPUT_DIRECTORY_SYMLINK")
    output = raw_output.resolve(strict=False)
    if any(_is_within(output, root) for root in _worktree_roots(repo)):
        raise RustBackendError("BUILD_OUTPUT_INSIDE_GIT_WORKTREE")

    identity = _authenticate_runtime_observed(stage_dir=stage)
    rustc = resolve_rustc_locator()
    source = stage / "rust/source_bound_thermal.rs"
    output.mkdir(parents=True, exist_ok=True)
    artifact = output / "librei_source_bound_thermal.so"
    if artifact.exists():
        raise RustBackendError("BUILD_ARTIFACT_PREEXISTS")
    command = (
        str(rustc),
        "--edition=2021",
        "--crate-type=cdylib",
        "--crate-name=rei_source_bound_thermal",
        "-C",
        "opt-level=3",
        "-C",
        "codegen-units=1",
        "-C",
        "strip=symbols",
        "-C",
        "embed-bitcode=no",
        "-C",
        f"metadata={identity['source_sha256']}",
        "-C",
        f"linker={LINKER}",
        "--remap-path-prefix",
        f"{repo}=/rei_bianchi",
        "-L",
        f"native={NATIVE_LIBRARY_DIRECTORY}",
        "-C",
        "link-arg=-Wl,--build-id=none",
        "-C",
        "link-arg=-Wl,--disable-new-dtags",
        "-C",
        f"link-arg=-Wl,-rpath,{NATIVE_LIBRARY_DIRECTORY}",
        "-C",
        "link-arg=-Wl,-l:libmpfr.so.6",
        "-C",
        "link-arg=-Wl,-l:libgmp.so.10",
        str(source),
        "-o",
        str(artifact),
    )
    _run(
        command,
        cwd=repo,
        expected_executable_sha256=identity["rustc_sha256"],
    )
    if _authenticate_runtime_observed(stage_dir=stage) != identity:
        raise RustBackendError("BUILD_IDENTITY_CHANGED_DURING_COMPILE")

    artifact_sha256 = _sha256(artifact)
    amendment = json.loads(
        (stage / "RUST_IMPLEMENTATION_AMENDMENT.json").read_text(encoding="utf-8")
    )
    expected_artifact_sha256 = amendment["expected_artifact_sha256"]
    if artifact_sha256 != expected_artifact_sha256:
        raise RustBackendError("BACKEND_ARTIFACT_PIN_MISMATCH")
    dependencies = _artifact_dependencies(artifact)
    library = _load_library(artifact, dependencies)
    native_facts = _native_facts(library)
    expected_native = {
        "abi_version": identity["abi_version"],
        "precision_bits": identity["precision_bits"],
        "pointer_width_bits": identity["pointer_width_bits"],
        "mpfr_raw_size": identity["mpfr_raw_size"],
        "mpfr_raw_align": identity["mpfr_raw_align"],
        "limb_bits": identity["limb_bits"],
    }
    if native_facts != expected_native:
        raise RustBackendError("BACKEND_NATIVE_FACT_MISMATCH")

    receipt = BackendReceipt(
        schema="rei-authenticated-backend-receipt/v1",
        artifact_sha256=artifact_sha256,
        expected_artifact_sha256=expected_artifact_sha256,
        runtime_identity_sha256=_canonical_digest(identity),
        source_sha256=identity["source_sha256"],
        rustc_sha256=identity["rustc_sha256"],
        rustc_commit=identity["rustc_commit"],
        rustc_host=identity["rustc_host"],
        rustc_closure_sha256=identity["rustc_closure_sha256"],
        linker_sha256=identity["linker_sha256"],
        mpfr_soname=identity["mpfr_soname"],
        mpfr_sha256=identity["mpfr_sha256"],
        mpfr_version=identity["mpfr_version"],
        gmp_soname=identity["gmp_soname"],
        gmp_sha256=identity["gmp_sha256"],
        gmp_version=identity["gmp_version"],
        ondisk_runtime_elf_closure_sha256=_canonical_digest(
            {"runtime_elf_closure": list(dependencies)}
        ),
        abi_version=identity["abi_version"],
        precision_bits=identity["precision_bits"],
        rounding_policy=identity["rounding_policy"],
        pointer_width_bits=identity["pointer_width_bits"],
        mpfr_raw_size=identity["mpfr_raw_size"],
        mpfr_raw_align=identity["mpfr_raw_align"],
        limb_bits=identity["limb_bits"],
        deterministic_build_contract_sha256=identity[
            "deterministic_build_contract_sha256"
        ],
    )
    return AuthenticatedBackend(
        artifact,
        receipt,
        runtime_authority,
        _seal=_CAPABILITY_TOKEN,
    )


def build_authenticated_backend(*, stage_dir: Path, output_dir: Path) -> AuthenticatedBackend:
    """Build only inside a factory-minted automatic runtime observer."""

    stage = Path(stage_dir).resolve(strict=True)
    repo = stage.parents[1]
    raw_output = Path(output_dir)
    if raw_output.is_symlink():
        raise RustBackendError("BUILD_OUTPUT_DIRECTORY_SYMLINK")
    output = raw_output.resolve(strict=False)
    if any(_is_within(output, root) for root in _worktree_roots(repo)):
        raise RustBackendError("BUILD_OUTPUT_INSIDE_GIT_WORKTREE")
    artifact = output / "librei_source_bound_thermal.so"
    intake_authority = _prepare_runtime_authority(
        repo=repo,
        stage_dir=stage,
        input_lock_path=stage / "INPUT_LOCK.json",
        additional_allowed_paths=_base_runtime_observation_paths(artifact),
    )
    external_paths, _ = _observe_runtime_invocation(
        intake_authority,
        lambda _capability: _runtime_observation_paths(stage, artifact),
    )
    authority = _prepare_runtime_authority(
        repo=repo,
        stage_dir=stage,
        input_lock_path=stage / "INPUT_LOCK.json",
        additional_allowed_paths=external_paths,
    )
    backend, _ = _observe_runtime_invocation(
        authority,
        lambda _capability: _build_authenticated_backend_observed(
            stage_dir=stage,
            output_dir=output_dir,
            runtime_authority=authority,
        ),
    )
    return backend


def _array(values: Sequence[float]) -> Any:
    array_type = ctypes.c_double * len(values)
    return array_type(*values)


def _null_double_pointer() -> Any:
    return ctypes.POINTER(ctypes.c_double)()


def _candidate_arrays(
    lower: Sequence[float] | None,
    upper: Sequence[float] | None,
) -> tuple[Any, Any]:
    if lower is None and upper is None:
        return _null_double_pointer(), _null_double_pointer()
    if lower is None or upper is None:
        raise RustBackendError("INCOMPLETE_CANDIDATE")
    return _array(lower), _array(upper)


def _check_status(status: int) -> None:
    if status:
        raise RustBackendError(_STATUS.get(status, f"UNKNOWN_NATIVE_STATUS_{status}"))


def _certificate_outputs(dimension: int) -> dict[str, Any]:
    # ABI v4 calls these slots ``residual`` for wire compatibility.  They carry
    # the implicit RHS, as exposed by TangentCertificate.implicit_rhs_*.
    return {
        "solution_lower": _array([0.0] * dimension),
        "solution_upper": _array([0.0] * dimension),
        "krawczyk_lower": _array([0.0] * dimension),
        "krawczyk_upper": _array([0.0] * dimension),
        "center": _array([0.0] * dimension),
        "residual_lower": _array([0.0] * dimension),
        "residual_upper": _array([0.0] * dimension),
        "preconditioner": _array([0.0] * (dimension * dimension)),
        "rho_upper": ctypes.c_double(),
        "lower_margins": _array([0.0] * dimension),
        "upper_margins": _array([0.0] * dimension),
        "iterations": ctypes.c_uint32(),
    }


def _certificate(
    request: LinearRequest | TangentRequest | MixedVfRequest,
    outputs: Mapping[str, Any],
    backend: AuthenticatedBackend,
) -> TangentCertificate:
    n = request.dimension
    return TangentCertificate(
        request_sha256=request.sha256(),
        precision_bits=PRECISION_BITS,
        rounding_policy=ROUNDING_POLICY,
        backend_schema=CERTIFICATE_SCHEMA,
        solution_lower=tuple(outputs["solution_lower"][:n]),
        solution_upper=tuple(outputs["solution_upper"][:n]),
        krawczyk_lower=tuple(outputs["krawczyk_lower"][:n]),
        krawczyk_upper=tuple(outputs["krawczyk_upper"][:n]),
        center=tuple(outputs["center"][:n]),
        residual_lower=tuple(outputs["residual_lower"][:n]),
        residual_upper=tuple(outputs["residual_upper"][:n]),
        preconditioner=tuple(outputs["preconditioner"][: n * n]),
        rho_upper=float(outputs["rho_upper"].value),
        lower_margins=tuple(outputs["lower_margins"][:n]),
        upper_margins=tuple(outputs["upper_margins"][:n]),
        iterations=int(outputs["iterations"].value),
        strict_self_inclusion=True,
        backend_identity_sha256=backend.receipt.identity_sha256(),
    )


def _finish_certificate_call(
    *,
    status: int,
    request: LinearRequest | TangentRequest | MixedVfRequest,
    outputs: Mapping[str, Any],
    backend: AuthenticatedBackend,
) -> TangentCertificate:
    _check_status(status)
    _postvalidate_backend(backend)
    return _certificate(request, outputs, backend)


def certify_linear(
    request: LinearRequest,
    *,
    backend: AuthenticatedBackend,
) -> TangentCertificate:
    native = _validate_backend(backend)
    n = request.dimension
    candidate_lower, candidate_upper = _candidate_arrays(
        request.candidate_lower, request.candidate_upper
    )
    outputs = _certificate_outputs(n)
    status = native.rei_certify_linear_mpfr256(
        n,
        n * n,
        n,
        _array(request.a_lower),
        _array(request.a_upper),
        _array(request.b_lower),
        _array(request.b_upper),
        candidate_lower,
        candidate_upper,
        outputs["solution_lower"],
        outputs["solution_upper"],
        outputs["krawczyk_lower"],
        outputs["krawczyk_upper"],
        outputs["center"],
        outputs["residual_lower"],
        outputs["residual_upper"],
        outputs["preconditioner"],
        ctypes.byref(outputs["rho_upper"]),
        outputs["lower_margins"],
        outputs["upper_margins"],
        ctypes.byref(outputs["iterations"]),
    )
    return _finish_certificate_call(
        status=status, request=request, outputs=outputs, backend=backend
    )


def certify_tangent(
    request: TangentRequest,
    *,
    backend: AuthenticatedBackend,
) -> TangentCertificate:
    native = _validate_backend(backend)
    n = request.dimension
    candidate_lower, candidate_upper = _candidate_arrays(
        request.candidate_lower, request.candidate_upper
    )
    outputs = _certificate_outputs(n)
    status = native.rei_certify_tangent_mpfr256(
        n,
        n * n,
        n,
        _array(request.a_lower),
        _array(request.a_upper),
        _array(request.z_lower),
        _array(request.z_upper),
        _array(request.delta_a_lower),
        _array(request.delta_a_upper),
        _array(request.delta_b_lower),
        _array(request.delta_b_upper),
        candidate_lower,
        candidate_upper,
        outputs["solution_lower"],
        outputs["solution_upper"],
        outputs["krawczyk_lower"],
        outputs["krawczyk_upper"],
        outputs["center"],
        outputs["residual_lower"],
        outputs["residual_upper"],
        outputs["preconditioner"],
        ctypes.byref(outputs["rho_upper"]),
        outputs["lower_margins"],
        outputs["upper_margins"],
        ctypes.byref(outputs["iterations"]),
    )
    return _finish_certificate_call(
        status=status, request=request, outputs=outputs, backend=backend
    )


def certify_mixed_vf(
    request: MixedVfRequest,
    *,
    backend: AuthenticatedBackend,
) -> TangentCertificate:
    native = _validate_backend(backend)
    n = request.dimension
    candidate_lower, candidate_upper = _candidate_arrays(
        request.candidate_lower, request.candidate_upper
    )
    outputs = _certificate_outputs(n)
    status = native.rei_certify_mixed_vf_mpfr256(
        n,
        n * n,
        n,
        _array(request.a_lower),
        _array(request.a_upper),
        _array(request.b_vf_lower),
        _array(request.b_vf_upper),
        _array(request.a_vf_lower),
        _array(request.a_vf_upper),
        _array(request.z_lower),
        _array(request.z_upper),
        _array(request.a_v_lower),
        _array(request.a_v_upper),
        _array(request.z_f_lower),
        _array(request.z_f_upper),
        _array(request.a_f_lower),
        _array(request.a_f_upper),
        _array(request.z_v_lower),
        _array(request.z_v_upper),
        candidate_lower,
        candidate_upper,
        outputs["solution_lower"],
        outputs["solution_upper"],
        outputs["krawczyk_lower"],
        outputs["krawczyk_upper"],
        outputs["center"],
        outputs["residual_lower"],
        outputs["residual_upper"],
        outputs["preconditioner"],
        ctypes.byref(outputs["rho_upper"]),
        outputs["lower_margins"],
        outputs["upper_margins"],
        ctypes.byref(outputs["iterations"]),
    )
    return _finish_certificate_call(
        status=status, request=request, outputs=outputs, backend=backend
    )


def _require_certificate_backend_identity(
    certificate: TangentCertificate,
    backend: AuthenticatedBackend,
) -> None:
    authenticated = _require_backend(backend)
    if certificate.backend_identity_sha256 != authenticated.receipt.identity_sha256():
        raise RustBackendError("BACKEND_IDENTITY_MISMATCH")


def _admit_recomputed(
    certificate: TangentCertificate,
    replay: TangentCertificate,
    backend: AuthenticatedBackend,
) -> None:
    del backend
    if certificate.canonical_bytes() != replay.canonical_bytes():
        raise RustBackendError("CERTIFICATE_SEMANTIC_REPLAY_MISMATCH")


def admit_tangent_certificate(
    request: TangentRequest,
    certificate: TangentCertificate,
    *,
    backend: AuthenticatedBackend,
) -> None:
    """Admit only after structure, backend identity, and exact Rust replay."""

    validate_tangent_certificate(request, certificate)
    _require_certificate_backend_identity(certificate, backend)
    replay = certify_tangent(request, backend=backend)
    _admit_recomputed(certificate, replay, backend)


def admit_mixed_vf_certificate(
    request: MixedVfRequest,
    certificate: TangentCertificate,
    *,
    backend: AuthenticatedBackend,
) -> None:
    """Admit an atomic mixed certificate under one bound request digest."""

    validate_mixed_vf_certificate(request, certificate)
    _require_certificate_backend_identity(certificate, backend)
    replay = certify_mixed_vf(request, backend=backend)
    _admit_recomputed(certificate, replay, backend)


def diagnostic_mixed_rhs(
    request: MixedRhsRequest | MixedVfRequest,
    *,
    backend: AuthenticatedBackend,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Return the complete mixed RHS; it is never an admission result."""

    native = _validate_backend(backend)
    n = request.dimension
    lower = _array([0.0] * n)
    upper = _array([0.0] * n)
    status = native.rei_diagnostic_mixed_rhs_mpfr256(
        n,
        n * n,
        n,
        _array(request.b_vf_lower),
        _array(request.b_vf_upper),
        _array(request.a_vf_lower),
        _array(request.a_vf_upper),
        _array(request.z_lower),
        _array(request.z_upper),
        _array(request.a_v_lower),
        _array(request.a_v_upper),
        _array(request.z_f_lower),
        _array(request.z_f_upper),
        _array(request.a_f_lower),
        _array(request.a_f_upper),
        _array(request.z_v_lower),
        _array(request.z_v_upper),
        lower,
        upper,
    )
    _check_status(status)
    _postvalidate_backend(backend)
    return tuple(lower[:n]), tuple(upper[:n])


def interval_divide(
    numerator: tuple[float, float],
    denominator: tuple[float, float],
    *,
    backend: AuthenticatedBackend,
) -> tuple[float, float]:
    native = _validate_backend(backend)
    lower = ctypes.c_double()
    upper = ctypes.c_double()
    status = native.rei_interval_divide_mpfr256(
        numerator[0],
        numerator[1],
        denominator[0],
        denominator[1],
        ctypes.byref(lower),
        ctypes.byref(upper),
    )
    _check_status(status)
    _postvalidate_backend(backend)
    return lower.value, upper.value


__all__ = (
    "AuthenticatedBackend",
    "BackendReceipt",
    "PRESTART_RUNTIME_BLOCKER",
    "PROCESS_BOUNDARY_BLOCKER",
    "RuntimeClosureCapability",
    "RuntimeClosureError",
    "RustBackendError",
    "admit_mixed_vf_certificate",
    "admit_tangent_certificate",
    "authenticate_runtime",
    "build_authenticated_backend",
    "certify_linear",
    "certify_mixed_vf",
    "certify_tangent",
    "diagnostic_mixed_rhs",
    "interval_divide",
    "resolve_rustc_locator",
    "validate_runtime_closure",
)
