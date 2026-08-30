#!/usr/bin/env python3
"""Behavioral tests for the prompt-only REI-LOCAL-01 locator bootstrap."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import textwrap
import unittest


TERMINAL_COMMIT = "04a353339c0fe517ac5209a78bc57b49b8006f77"
TERMINAL_TREE = "6cde78286be28f1c4077e389f3b8bab8373c5a9d"
PAYLOAD_COMMIT = "4d6bf6a356f8e944d20fd1e2423d8db55f5961b7"
PAYLOAD_TREE = "7c01b545b6f30b9b43c290ad0757f9a564972c97"
BASE_COMMIT = "1893f12d14b212eb4b6bd637332824f692e6f4b3"
BASE_TREE = "773fcdc4d1ab115fa0542d26ba67af5c086f450b"
PR14_SOURCE_COMMIT = "053b97c56e089e28a83f37d79a4128ed3cdae9f4"
PR14_SOURCE_TREE = "46a96c789a691d671644685893a552cd9486788d"
TRANSPORT_REF = (
    "refs/heads/agent/handoff/rei-local-01-bootstrap-spec-20260830-r1"
)
LOCATOR_PATH = (
    "handoff/rei_local_01_source_bound_paired_map_20260830/"
    "FETCH_AND_VALIDATE.py"
)
LOCATOR_BLOB = "0f43968815b8fa8da3a7d426c07af294e46fcc6a"
LOCATOR_SHA256 = (
    "241f5f5722b9eda0f9fbbd8600da80907e3056fca3d04dc4c52ba48927c6579c"
)

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PROMPT = PACKAGE_ROOT / "LOCAL_EXECUTION_PROMPT_V2.md"
SOURCE_LOCATOR = REPOSITORY_ROOT / LOCATOR_PATH

BEGIN = "<!-- BEGIN EXECUTABLE_BOOTSTRAP_V2 -->\n```bash\n"
END = "\n```\n<!-- END EXECUTABLE_BOOTSTRAP_V2 -->"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def executable_block() -> tuple[str, str]:
    prompt = PROMPT.read_text(encoding="utf-8")
    if prompt.count(BEGIN) != 1 or prompt.count(END) != 1:
        raise AssertionError("prompt must contain exactly one executable bootstrap block")
    return prompt.split(BEGIN, 1)[1].split(END, 1)[0], prompt


def tree_snapshot(root: Path) -> tuple[tuple[str, int, str], ...]:
    snapshot = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        mode = stat.S_IMODE(path.lstat().st_mode)
        digest = sha256(path.read_bytes()) if path.is_file() else "DIRECTORY"
        snapshot.append((relative, mode, digest))
    return tuple(snapshot)


FAKE_GIT = r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import signal
import sys

TERMINAL_COMMIT = "04a353339c0fe517ac5209a78bc57b49b8006f77"
TERMINAL_TREE = "6cde78286be28f1c4077e389f3b8bab8373c5a9d"
PAYLOAD_COMMIT = "4d6bf6a356f8e944d20fd1e2423d8db55f5961b7"
PAYLOAD_TREE = "7c01b545b6f30b9b43c290ad0757f9a564972c97"
BASE_COMMIT = "1893f12d14b212eb4b6bd637332824f692e6f4b3"
BASE_TREE = "773fcdc4d1ab115fa0542d26ba67af5c086f450b"
PR14_SOURCE_COMMIT = "053b97c56e089e28a83f37d79a4128ed3cdae9f4"
PR14_SOURCE_TREE = "46a96c789a691d671644685893a552cd9486788d"
TRANSPORT_REF = "refs/heads/agent/handoff/rei-local-01-bootstrap-spec-20260830-r1"
LOCATOR_PATH = "handoff/rei_local_01_source_bound_paired_map_20260830/FETCH_AND_VALIDATE.py"
LOCATOR_BLOB = "0f43968815b8fa8da3a7d426c07af294e46fcc6a"

for forbidden in (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
):
    if forbidden in os.environ:
        print(f"unscrubbed environment: {forbidden}", file=sys.stderr)
        raise SystemExit(96)
if any(name.startswith("GIT_CONFIG") for name in os.environ):
    print("unscrubbed GIT_CONFIG environment", file=sys.stderr)
    raise SystemExit(96)
if os.environ.get("GIT_NO_LAZY_FETCH") != "1":
    print("GIT_NO_LAZY_FETCH is not set", file=sys.stderr)
    raise SystemExit(96)

raw = sys.argv[1:]
with Path(os.environ["FAKE_GIT_LOG"]).open("a", encoding="utf-8") as stream:
    stream.write(json.dumps(raw) + "\n")

args = list(raw)
if args[:1] == ["--no-replace-objects"]:
    args.pop(0)
if args[:1] != ["-C"] or len(args) < 3:
    raise SystemExit(97)
repo = args[1]
args = args[2:]
if repo != os.environ["REI_REPO"]:
    raise SystemExit(97)

fetch_marker = Path(os.environ["FAKE_FETCH_MARKER"])
lazy_marker = Path(os.environ["FAKE_LAZY_MARKER"])
count_marker = Path(os.environ["FAKE_COUNT_MARKER"])

def require_explicit_fetch():
    if not fetch_marker.exists():
        lazy_marker.write_text("implicit lazy fetch would have occurred\n")
        raise SystemExit(95)

if args == ["rev-parse", "--is-bare-repository"]:
    print("false")
elif args == ["rev-parse", "--is-shallow-repository"]:
    print("false")
elif args == ["rev-parse", "--show-object-format"]:
    print("sha1")
elif args == ["rev-parse", "--show-toplevel"]:
    print(repo)
elif args == ["rev-parse", "--path-format=absolute", "--git-dir"]:
    print(f"{repo}/.git")
elif args == ["rev-parse", "--path-format=absolute", "--git-common-dir"]:
    print(f"{repo}/.git")
elif args == ["worktree", "list", "--porcelain", "-z"]:
    sys.stdout.buffer.write(f"worktree {repo}\0".encode())
    if os.environ.get("FAKE_GIT_MODE") == "pin-root-other-worktree":
        sys.stdout.buffer.write(
            f"worktree {os.environ['FAKE_OTHER_WORKTREE']}\0".encode()
        )
elif args[0:1] == ["fetch"]:
    if os.environ.get("FAKE_GIT_MODE") == "reject-exact" and args[-1] == TERMINAL_COMMIT:
        raise SystemExit(1)
    if args[-1] not in (TERMINAL_COMMIT, TRANSPORT_REF):
        raise SystemExit(97)
    fetch_marker.write_text("explicit full-closure fetch completed\n")
elif args == ["count-objects", "-v"]:
    require_explicit_fetch()
    seen = count_marker.exists()
    count_marker.write_text("counted\n")
    in_pack = 43 if seen and os.environ.get("FAKE_GIT_MODE") == "object-growth" else 42
    print(f"count: 0\nsize: 0\nin-pack: {in_pack}\npacks: 1\nsize-pack: 1")
elif args == ["rev-parse", "--verify", f"{TERMINAL_COMMIT}^{{commit}}"]:
    require_explicit_fetch()
    print(TERMINAL_COMMIT)
elif args == ["rev-parse", "--verify", f"{TERMINAL_COMMIT}^{{tree}}"]:
    require_explicit_fetch()
    print("0" * 40 if os.environ.get("FAKE_GIT_MODE") == "bad-terminal-tree" else TERMINAL_TREE)
elif args == ["rev-list", "--parents", "-n", "1", TERMINAL_COMMIT]:
    require_explicit_fetch()
    print(f"{TERMINAL_COMMIT} {PAYLOAD_COMMIT}")
elif args == ["rev-parse", "--verify", f"{PAYLOAD_COMMIT}^{{tree}}"]:
    require_explicit_fetch()
    print(PAYLOAD_TREE)
elif args == ["rev-list", "--parents", "-n", "1", PAYLOAD_COMMIT]:
    require_explicit_fetch()
    print(f"{PAYLOAD_COMMIT} {BASE_COMMIT}")
elif args == ["rev-parse", "--verify", f"{BASE_COMMIT}^{{tree}}"]:
    require_explicit_fetch()
    print("0" * 40 if os.environ.get("FAKE_GIT_MODE") == "bad-base-tree" else BASE_TREE)
elif args == ["rev-parse", "--verify", f"{PR14_SOURCE_COMMIT}^{{commit}}"]:
    require_explicit_fetch()
    print(PR14_SOURCE_COMMIT)
elif args == ["rev-parse", "--verify", f"{PR14_SOURCE_COMMIT}^{{tree}}"]:
    require_explicit_fetch()
    print("0" * 40 if os.environ.get("FAKE_GIT_MODE") == "bad-pr14-tree" else PR14_SOURCE_TREE)
elif args == ["rev-parse", "--verify", f"{TERMINAL_COMMIT}:{LOCATOR_PATH}"]:
    require_explicit_fetch()
    print("0" * 40 if os.environ.get("FAKE_GIT_MODE") == "bad-locator-blob" else LOCATOR_BLOB)
elif args == ["cat-file", "-t", LOCATOR_BLOB]:
    require_explicit_fetch()
    print("blob")
elif args == ["cat-file", "blob", LOCATOR_BLOB]:
    require_explicit_fetch()
    if os.environ.get("FAKE_GIT_MODE") == "signal-parent":
        os.kill(os.getppid(), signal.SIGTERM)
        raise SystemExit(1)
    sys.stdout.buffer.write(Path(os.environ["FAKE_LOCATOR_SOURCE"]).read_bytes())
else:
    print(f"unexpected fake Git call: {args!r}", file=sys.stderr)
    raise SystemExit(97)
'''


class PromptOnlyBootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.block, self.prompt = executable_block()
        self.locator = SOURCE_LOCATOR.read_bytes()
        self.assertEqual(sha256(self.locator), LOCATOR_SHA256)

    def run_block(
        self,
        temporary: Path,
        *,
        locator: bytes | None = None,
        mode: str = "success",
    ) -> tuple[subprocess.CompletedProcess[str], Path, Path, Path]:
        repo = temporary / "repo"
        pin_root = temporary / "pins"
        fake_bin = temporary / "bin"
        repo.mkdir(exist_ok=True)
        pin_root.mkdir(exist_ok=True)
        pin_root.chmod(0o700)
        fake_bin.mkdir(exist_ok=True)
        (repo / "dirty-untracked.txt").write_text("preserve me\n", encoding="utf-8")

        locator_source = temporary / "locator-source.py"
        locator_source.write_bytes(self.locator if locator is None else locator)
        fake_log = temporary / "git.jsonl"
        fake = fake_bin / "git"
        fake.write_text(textwrap.dedent(FAKE_GIT), encoding="utf-8")
        fake.chmod(0o700)

        environment = dict(os.environ)
        environment.update(
            {
                "PATH": f"{fake_bin}:/usr/bin:/bin",
                "REI_REPO": str(repo),
                "REI_PIN_ROOT": str(pin_root),
                "FAKE_GIT_LOG": str(fake_log),
                "FAKE_GIT_MODE": mode,
                "FAKE_LOCATOR_SOURCE": str(locator_source),
                "FAKE_FETCH_MARKER": str(temporary / "explicit-fetch.marker"),
                "FAKE_LAZY_MARKER": str(temporary / "implicit-lazy-fetch.marker"),
                "FAKE_COUNT_MARKER": str(temporary / "count-objects.marker"),
                "FAKE_OTHER_WORKTREE": str(temporary),
                "GIT_DIR": "/hostile/git-dir",
                "GIT_WORK_TREE": "/hostile/work-tree",
                "GIT_INDEX_FILE": "/hostile/index",
                "GIT_OBJECT_DIRECTORY": "/hostile/objects",
                "GIT_ALTERNATE_OBJECT_DIRECTORIES": "/hostile/alternates",
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "core.hooksPath",
                "GIT_CONFIG_VALUE_0": "/hostile/hooks",
            }
        )
        process = subprocess.run(
            ["/bin/bash", "--noprofile", "--norc", "-c", self.block],
            cwd=temporary,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=False,
        )
        return process, repo, pin_root, fake_log

    def test_materializes_exact_locator_without_touching_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            temporary = Path(name)
            process, repo, pin_root, fake_log = self.run_block(temporary)
            before = (("dirty-untracked.txt", 0o644, sha256(b"preserve me\n")),)

            self.assertEqual(process.returncode, 0, process.stderr)
            target = pin_root / "FETCH_AND_VALIDATE.py"
            self.assertEqual(target.read_bytes(), self.locator)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o500)
            self.assertEqual(tree_snapshot(repo), before)
            self.assertEqual(list(pin_root.glob(".FETCH_AND_VALIDATE.py.*")), [])
            self.assertIn(f"LOCATOR_READY={target}", process.stdout)
            self.assertFalse((temporary / "implicit-lazy-fetch.marker").exists())

            calls = [json.loads(line) for line in fake_log.read_text().splitlines()]
            flattened = [argument for call in calls for argument in call]
            self.assertNotIn("--no-lazy-fetch", flattened)
            fetch = next(call for call in calls if "fetch" in call)
            for flag in (
                "--no-tags",
                "--no-write-fetch-head",
                "--no-recurse-submodules",
                "--no-auto-maintenance",
                "--no-write-commit-graph",
                "--no-filter",
                "--refetch",
                "--refmap=",
            ):
                self.assertIn(flag, fetch)

    def test_rejects_locator_byte_mutation_before_publish(self) -> None:
        mutation = bytearray(self.locator)
        mutation[len(mutation) // 2] ^= 1
        with tempfile.TemporaryDirectory() as name:
            temporary = Path(name)
            process, repo, pin_root, _ = self.run_block(
                temporary, locator=bytes(mutation)
            )

            self.assertNotEqual(process.returncode, 0)
            self.assertIn("LOCATOR_SHA256_MISMATCH", process.stderr)
            self.assertFalse((pin_root / "FETCH_AND_VALIDATE.py").exists())
            self.assertEqual(list(pin_root.glob(".FETCH_AND_VALIDATE.py.*")), [])
            self.assertEqual(
                tree_snapshot(repo),
                (("dirty-untracked.txt", 0o644, sha256(b"preserve me\n")),),
            )

    def test_existing_target_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            temporary = Path(name)
            first, _, pin_root, _ = self.run_block(temporary)
            self.assertEqual(first.returncode, 0, first.stderr)
            target = pin_root / "FETCH_AND_VALIDATE.py"
            initial = (target.read_bytes(), target.stat().st_mtime_ns)

            second, _, _, _ = self.run_block(temporary)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("TARGET_ALREADY_EXISTS", second.stderr)
            self.assertEqual((target.read_bytes(), target.stat().st_mtime_ns), initial)

    def test_transport_ref_is_only_a_no_ref_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            process, _, _, fake_log = self.run_block(
                Path(name), mode="reject-exact"
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            calls = [json.loads(line) for line in fake_log.read_text().splitlines()]
            fetches = [call for call in calls if "fetch" in call]
            self.assertEqual(fetches[0][-1], TERMINAL_COMMIT)
            self.assertEqual(fetches[1][-1], TRANSPORT_REF)
            self.assertIn("--refmap=", fetches[1])

    def test_rejects_object_growth_during_authenticated_reads(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            process, _, pin_root, _ = self.run_block(
                Path(name), mode="object-growth"
            )
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("UNEXPECTED_OBJECT_STORE_MUTATION", process.stderr)
            self.assertFalse((pin_root / "FETCH_AND_VALIDATE.py").exists())
            self.assertEqual(list(pin_root.glob(".FETCH_AND_VALIDATE.py.*")), [])

    def test_rejects_pinned_identity_mismatches(self) -> None:
        for mode in (
            "bad-terminal-tree",
            "bad-base-tree",
            "bad-pr14-tree",
            "bad-locator-blob",
        ):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as name:
                process, _, pin_root, _ = self.run_block(Path(name), mode=mode)
                self.assertNotEqual(process.returncode, 0)
                self.assertIn("OBJECT_MISMATCH", process.stderr)
                self.assertFalse((pin_root / "FETCH_AND_VALIDATE.py").exists())

    def test_signal_aborts_and_cleans_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            process, _, pin_root, _ = self.run_block(
                Path(name), mode="signal-parent"
            )
            self.assertNotEqual(process.returncode, 0)
            self.assertFalse((pin_root / "FETCH_AND_VALIDATE.py").exists())
            self.assertEqual(list(pin_root.glob(".FETCH_AND_VALIDATE.py.*")), [])

    def test_rejects_pin_root_inside_another_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            process, _, pin_root, _ = self.run_block(
                Path(name), mode="pin-root-other-worktree"
            )
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("PIN_ROOT_POLICY", process.stderr)
            self.assertFalse((pin_root / "FETCH_AND_VALIDATE.py").exists())

    def test_v2_contains_no_unbound_publication_placeholders(self) -> None:
        self.assertNotIn("<exact 40-hex SHA from the publishing response>", self.prompt)
        self.assertNotIn("<exact GitHub PR URL from the publishing response>", self.prompt)
        for value in (
            TERMINAL_COMMIT,
            TERMINAL_TREE,
            BASE_COMMIT,
            BASE_TREE,
            PR14_SOURCE_COMMIT,
            PR14_SOURCE_TREE,
            LOCATOR_PATH,
            LOCATOR_BLOB,
            LOCATOR_SHA256,
            "https://github.com/cosmosapjw-quantum/rei_bianchi/pull/19",
            "https://github.com/cosmosapjw-quantum/rei_bianchi.git",
        ):
            self.assertIn(value, self.prompt)


if __name__ == "__main__":
    unittest.main()
