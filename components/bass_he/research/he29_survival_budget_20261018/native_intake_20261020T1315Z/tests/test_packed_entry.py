"""Only new entry wiring is exercised; all targets/watchdogs are fake modules.

No old scientific module, compiler, subprocess worker or solver is executed.
Published watchdog behavior and the original a5 scientific gates are reused.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ENTRY = Path(__file__).resolve().parents[1] / "ncp/packed_entry.py"
SPEC = importlib.util.spec_from_file_location("packed_entry_under_test", ENTRY)
entry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(entry)

FAKE_EXECUTION = '''
import hashlib, json
from pathlib import Path
PROVIDER = "original-execution-evidence-provider"
def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as out:
        json.dump(data, out)
'''

FAKE_WATCHDOG = '''
from pathlib import Path
def run_process_group(argv, destination, timeout_s, *, execution):
    dst = Path(destination)
    dst.mkdir(parents=True, exist_ok=False)
    execution.atomic_json(dst / "FORWARDED_PROCESS.json", {
        "argv": argv, "timeout_s": timeout_s,
        "execution_provider": execution.PROVIDER,
    })
    return {"returncode": 0, "timed_out": False, "wall_s": 0.0}
'''

FAKE_TARGET = '''
import json, sys
from pathlib import Path
def run_process(*args, **kwargs):
    raise AssertionError("old watchdog binding was not replaced")
def main():
    argv = list(sys.argv)
    mode = argv[1] if argv[1] in ("preflight", "canary") else "build"
    def value(flag):
        return argv[argv.index(flag) + 1]
    out = Path(value("--out"))
    if mode != "build":
        source = Path(value("--baseline-campaign"))
        if (source / "REFUSED").exists():
            raise ValueError((source / "REFUSED").read_text())
    out.mkdir(parents=True, exist_ok=False)
    (out / "FORWARDED_ARGV.json").write_text(json.dumps(argv))
    if mode != "build" and (source / "FAIL_AFTER_OUTPUT").exists():
        (out / "PREFIX.json").write_text('{"kept":true}')
        raise RuntimeError("manufactured target failure after a saved prefix")
    if mode == "preflight":
        return
    worker = ["sentinel-python", str(Path(__file__).resolve()), "_worker",
              "--out", str(out / "case"), "--source-revision", value("--source-revision")]
    timeout = float(value("--wall-s")) if "--wall-s" in argv else 900.0
    receipt = run_process(worker, out / "process", timeout)
    (out / "SUMMARY.json").write_text(json.dumps(receipt))
'''


class PackedEntryWiringTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.packed = self.root / "packed"
        self.controller = self.root / "controller"
        self.packed.mkdir()
        self.controller.mkdir()
        self.refs = self.root / "references"
        self.refs.mkdir()
        self.hashes = {}
        for mode, relative in entry.TARGET_PATHS.items():
            self.write_source(self.packed / relative, FAKE_TARGET)
            self.hashes[mode] = entry.digest(self.packed / relative)
        self.write_source(self.packed / entry.EXECUTION_PATH, FAKE_EXECUTION)
        self.write_source(self.controller / entry.CONTROLLER_PATH, FAKE_WATCHDOG)
        self.hashes["execution"] = entry.digest(self.packed / entry.EXECUTION_PATH)
        self.hashes["controller"] = entry.digest(self.controller / entry.CONTROLLER_PATH)
        self.heads = {self.packed: entry.PACKED_REVISION,
                      self.controller: entry.CONTROLLER_REVISION}
        self.dirty = set()
        self.query_patch = patch.object(entry, "query", side_effect=self.fake_git)
        self.hash_patch = patch.object(entry, "SOURCE_SHA256", self.hashes)
        self.query_patch.start()
        self.hash_patch.start()
        self.addCleanup(self.query_patch.stop)
        self.addCleanup(self.hash_patch.stop)

    def write_source(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data)

    def fake_git(self, root, *args):
        root = Path(root)
        if args == ("rev-parse", "--show-toplevel"):
            return str(root)
        if args == ("rev-parse", "HEAD"):
            return self.heads[root]
        if args == ("rev-parse", "HEAD^{tree}"):
            return "1" * 40
        if args == ("status", "--porcelain=v1", "--untracked-files=no"):
            return " M tracked.py" if root in self.dirty else ""
        raise AssertionError(args)

    def arguments(self, mode="canary", label="one"):
        boundary = self.root / (label + "_boundary")
        out = self.root / (label + "_target")
        target = ["--out", str(out), "--source-revision", entry.PACKED_REVISION]
        if mode != "build":
            target += ["--baseline-campaign", str(self.refs), "--binary", "/unused/native",
                       "--owner-receipt", "/unused/owner.json", "--library", "/unused/bridge.so",
                       "--bridge-receipt", "/unused/build.json", "--wall-s", "900"]
        outer = [mode, "--packed-root", str(self.packed), "--controller-root", str(self.controller),
                 "--boundary-out", str(boundary)]
        return outer + ["--"] + target, boundary, out, target

    def test_canary_uses_corrected_binding_and_preserves_target_and_worker_arguments(self):
        argv, boundary, out, target = self.arguments()
        self.assertEqual(entry.main(argv), 0)
        target_path = str(self.packed / entry.TARGET_PATHS["canary"])
        self.assertEqual(json.loads((out / "FORWARDED_ARGV.json").read_text()),
                         [target_path, "canary"] + target)
        process = json.loads((out / "process/FORWARDED_PROCESS.json").read_text())
        self.assertEqual(process["argv"], ["sentinel-python", target_path, "_worker", "--out",
                                         str(out / "case"), "--source-revision", entry.PACKED_REVISION])
        self.assertEqual(process["timeout_s"], 900)
        self.assertEqual(process["execution_provider"], "original-execution-evidence-provider")
        source = json.loads((boundary / "SOURCE_IDENTITY.json").read_text())
        self.assertEqual(source["target_argv"], [target_path, "canary"] + target)
        self.assertFalse(source["original_source_files_modified"])

    def test_build_preserves_flags_without_adding_a_target_mode(self):
        argv, boundary, out, target = self.arguments("build")
        extra = ["--offline", "--cargo", "/tool chain/cargo", "--rustc", "/tool chain/rustc"]
        self.assertEqual(entry.main(argv + extra), 0)
        self.assertEqual(json.loads((out / "FORWARDED_ARGV.json").read_text()),
                         [str(self.packed / entry.TARGET_PATHS["build"])] + target + extra)
        self.assertEqual(json.loads((boundary / "RECEIPT.json").read_text())["mode"], "build")

    def test_existing_reference_rejection_propagates_without_dispatch(self):
        for message in ("HE29_VIGILODE_REQUIRES_FOUR_COMPLETED_BASELINE_PAIRS",
                        "HE29_OPT_BASELINE_RUNTIME: m8_r4_table512: scipy"):
            with self.subTest(message=message):
                (self.refs / "REFUSED").write_text(message)
                argv, boundary, out, _ = self.arguments("preflight", message.split(":")[0])
                with self.assertRaisesRegex(ValueError, message.split(":")[0]):
                    entry.main(argv)
                self.assertFalse(out.exists())
                self.assertIn(message, json.loads((boundary / "FAILURE.json").read_text())["error"])

    def test_direct_worker_and_extra_case_options_are_rejected_before_loading(self):
        argv, boundary, out, _ = self.arguments()
        invalid = [["_worker"] + argv[1:], argv + ["--strips", "8"],
                   argv + ["--table-nodes", "1024"]]
        with patch.object(entry, "load_module") as load, contextlib.redirect_stderr(io.StringIO()):
            for item in invalid:
                with self.subTest(argv=item), self.assertRaises(SystemExit) as error:
                    entry.main(item)
                self.assertEqual(error.exception.code, 2)
            load.assert_not_called()
        self.assertFalse(boundary.exists())
        self.assertFalse(out.exists())

    def test_wrong_source_argument_git_revision_and_tracked_changes_are_rejected(self):
        argv, _, _, _ = self.arguments(label="argument")
        argv[argv.index("--source-revision") + 1] = "0" * 40
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            entry.main(argv)
        self.heads[self.packed] = "0" * 40
        argv, boundary, out, _ = self.arguments(label="git")
        with self.assertRaisesRegex(ValueError, "GIT_REVISION"):
            entry.main(argv)
        self.assertTrue((boundary / "FAILURE.json").is_file())
        self.assertFalse(out.exists())
        self.heads[self.packed] = entry.PACKED_REVISION
        self.dirty.add(self.controller)
        argv, boundary, out, _ = self.arguments(label="dirty")
        with self.assertRaisesRegex(ValueError, "TRACKED_DIRTY"):
            entry.main(argv)
        self.assertTrue((boundary / "FAILURE.json").is_file())
        self.assertFalse(out.exists())

    def test_target_controller_and_legacy_hash_mismatches_stop_before_import(self):
        paths = [self.packed / entry.TARGET_PATHS["canary"],
                 self.controller / entry.CONTROLLER_PATH, self.packed / entry.EXECUTION_PATH]
        for index, path in enumerate(paths):
            with self.subTest(path=path):
                saved = path.read_bytes()
                path.write_bytes(saved + b"\n# unapproved change\n")
                argv, boundary, out, _ = self.arguments(label="hash" + str(index))
                with patch.object(entry, "load_module") as load:
                    with self.assertRaisesRegex(ValueError, "SOURCE_IDENTITY"):
                        entry.main(argv)
                    load.assert_not_called()
                self.assertTrue((boundary / "FAILURE.json").exists())
                self.assertFalse(out.exists())
                path.write_bytes(saved)

    def test_create_only_outputs_preserve_occupied_target_and_boundary(self):
        argv, boundary, out, _ = self.arguments(label="target_exists")
        out.mkdir()
        marker = out / "RESULT.json"
        marker.write_bytes(b"existing return bytes")
        with self.assertRaises(FileExistsError):
            entry.main(argv)
        self.assertEqual(marker.read_bytes(), b"existing return bytes")
        self.assertTrue((boundary / "FAILURE.json").is_file())
        argv, boundary, out, _ = self.arguments(label="boundary_exists")
        boundary.mkdir()
        marker = boundary / "RECEIPT.json"
        marker.write_bytes(b"existing boundary receipt")
        with self.assertRaises(FileExistsError):
            entry.main(argv)
        self.assertEqual(marker.read_bytes(), b"existing boundary receipt")
        self.assertFalse(out.exists())

    def test_target_failure_preserves_prefix_and_restores_python_call_context(self):
        (self.refs / "FAIL_AFTER_OUTPUT").touch()
        argv, boundary, out, _ = self.arguments()
        old_argv, old_path = sys.argv[:], sys.path[:]
        with self.assertRaisesRegex(RuntimeError, "manufactured target failure"):
            entry.main(argv)
        self.assertEqual(json.loads((out / "PREFIX.json").read_text()), {"kept": True})
        self.assertTrue((boundary / "FAILURE.json").is_file())
        self.assertFalse((boundary / "RECEIPT.json").exists())
        self.assertEqual(sys.argv, old_argv)
        self.assertEqual(sys.path, old_path)

    def test_output_paths_inside_checkouts_or_overlapping_are_rejected(self):
        for label, location in (("packed", self.packed / "new-output"),
                                ("controller", self.controller / "new-output")):
            argv, boundary, out, _ = self.arguments(label=label)
            argv[argv.index("--out") + 1] = str(location)
            with self.assertRaisesRegex(ValueError, "OUTSIDE_CHECKOUTS"):
                entry.main(argv)
            self.assertFalse(location.exists())
            self.assertFalse(boundary.exists())
        argv, boundary, _, _ = self.arguments(label="overlap")
        argv[argv.index("--out") + 1] = str(boundary / "target")
        with self.assertRaisesRegex(ValueError, "OUTSIDE_CHECKOUTS"):
            entry.main(argv)
        self.assertFalse(boundary.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
