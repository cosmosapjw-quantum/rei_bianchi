"""Independent manufactured-file tests; zero HH numerical/scientific work."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import warnings
import zipfile


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("phys73_return_capsule_review", HERE / "return_capsule.py")
capsule = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capsule)


class ReturnCapsuleChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="phys73_return_capsule_fixture_")
        self.root = Path(self.temporary.name)
        self.repo = self.root / "manufactured_repo"
        self.out = self.root / "manufactured_output"
        self.invocation = "FIXTURE_NO_SCIENCE_001"
        self.source_bytes = {
            "src/kernel.py": b"manufactured_fixture = True\n",
            "inputs/frozen.txt": b"synthetic source bytes; no atomic data\n",
        }
        for relative, value in self.source_bytes.items():
            path = self.repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
        self.identity = {
            "source_head": "FIXTURE_NOT_A_GIT_HEAD",
            "parent": "FIXTURE_NOT_A_GIT_PARENT",
            "files_sha256": {name: hashlib.sha256(value).hexdigest()
                             for name, value in self.source_bytes.items()},
            "HH_R10": "OFF",
        }
        self.result = self.out / "invocations" / (self.invocation + "_RESULT.json")
        self.result.parent.mkdir(parents=True)
        self.result.write_text(json.dumps({
            "schema": "PHYS73_NCP_BATCH_RESULT_V1",
            "status": "MANUFACTURED_FIXTURE_ZERO_SCIENCE",
            "scientific_integrations": 0,
            "source_binding": self.identity,
        }) + "\n")
        (self.out / "IDENTITY.json").write_text(json.dumps(self.identity) + "\n")
        self.result_bytes = {
            "work/value.bin": b"manufactured binary\x00payload\xff",
            "jobs/tiny/attempt/stdout.txt": b"fixture stdout\n",
            "jobs/tiny/attempt/stderr.txt": b"",
            "jobs/tiny/SUCCESS.json": b'{"fixture_only": true}\n',
        }
        for relative, value in self.result_bytes.items():
            path = self.out / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
        for relative in ("work/held.lock", "work/current.tmp", "work/__pycache__/ignored.pyc"):
            path = self.out / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"transient fixture excluded from capsule")
        archives = self.out / "archives"
        archives.mkdir()
        (archives / "OLDER.zip").write_bytes(b"old capsule must not be recursively archived")
        self.target = archives / ("PHYS73_NCP_RETURN_" + self.invocation + ".zip")
        self.ack = archives / (self.target.stem + "_ACK.json")

    def tearDown(self):
        self.temporary.cleanup()

    def pack(self, out=None):
        return capsule.pack_return(self.out if out is None else out, self.repo,
                                   self.identity, self.invocation, self.result)

    def test_complete_membership_hashes_and_local_only_ack(self):
        receipt = self.pack()
        manifest = capsule.verify_capsule(self.target)
        expected = {"source/" + name: value for name, value in self.source_bytes.items()}
        expected.update({"results/" + name: value for name, value in self.result_bytes.items()})
        expected["results/IDENTITY.json"] = (self.out / "IDENTITY.json").read_bytes()
        expected["results/" + str(self.result.relative_to(self.out))] = self.result.read_bytes()
        self.assertEqual(manifest["files_sha256"],
                         {name: hashlib.sha256(value).hexdigest() for name, value in expected.items()})
        with zipfile.ZipFile(self.target) as archive:
            self.assertEqual(set(archive.namelist()), set(expected) | {"MANIFEST.json"})
            for name, value in expected.items():
                self.assertEqual(archive.read(name), value)
        self.assertEqual(set(manifest["excluded_transient_files"]),
                         {"work/held.lock", "work/current.tmp", "work/__pycache__/ignored.pyc"})
        self.assertEqual(receipt["status"], "LOCAL_ARCHIVED_VERIFIED")
        self.assertFalse(receipt["external_upload_performed"])
        self.assertFalse(receipt["full_git_clone"])
        self.assertEqual(receipt["sha256"], capsule.sha(self.target))
        self.assertEqual(receipt["bytes"], self.target.stat().st_size)
        self.assertEqual(receipt["result_sha256"], capsule.sha(self.result))
        self.assertEqual(receipt["manifest_payloads"], len(expected))
        self.assertEqual(json.loads(self.ack.read_text()), receipt)

    def test_missing_extra_changed_and_duplicate_zip_members_are_rejected(self):
        self.pack()
        with zipfile.ZipFile(self.target) as archive:
            original = {name: archive.read(name) for name in archive.namelist()}
        key = "results/work/value.bin"
        for case in ("missing", "extra", "changed", "duplicate"):
            with self.subTest(case=case):
                candidate = self.root / ("corrupted_" + case + ".zip")
                contents = dict(original)
                if case == "missing":
                    del contents[key]
                elif case == "extra":
                    contents["unmanifested.txt"] = b"extra"
                elif case == "changed":
                    contents[key] = b"different bytes"
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    with zipfile.ZipFile(candidate, "x") as archive:
                        for name, value in contents.items():
                            archive.writestr(name, value)
                        if case == "duplicate":
                            archive.writestr(key, original[key])
                with self.assertRaises(ValueError):
                    capsule.verify_capsule(candidate)

    def test_source_mutation_is_rejected_before_new_archive(self):
        (self.repo / "src/kernel.py").write_bytes(b"changed source")
        with self.assertRaisesRegex(ValueError, "bound source changed"):
            self.pack()
        self.assertFalse(self.target.exists())
        self.assertFalse(self.ack.exists())

    def test_duplicate_existing_archive_is_not_overwritten(self):
        self.pack()
        archive_bytes, ack_bytes = self.target.read_bytes(), self.ack.read_bytes()
        with self.assertRaises(FileExistsError):
            self.pack()
        self.assertEqual(self.target.read_bytes(), archive_bytes)
        self.assertEqual(self.ack.read_bytes(), ack_bytes)
        self.assertEqual(list(self.target.parent.glob(".*.tmp")), [])

    def test_source_symlink_is_refused(self):
        original = self.repo / "src/kernel.py"
        target = self.repo / "src/ordinary_copy.py"
        target.write_bytes(original.read_bytes())
        original.unlink()
        original.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "bound source changed"):
            self.pack()
        self.assertFalse(self.target.exists())

    def test_result_file_symlink_is_refused(self):
        target = self.root / "external.bin"
        target.write_bytes(b"not an owned result")
        (self.out / "work/alias.bin").symlink_to(target)
        with self.assertRaisesRegex(ValueError, "result symlink"):
            self.pack()
        self.assertFalse(self.target.exists())

    def test_result_directory_symlink_is_refused(self):
        source = self.out / "work"
        target = self.root / "moved_work"
        source.rename(target)
        source.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "result directory symlink"):
            self.pack()
        self.assertFalse(self.target.exists())

    def test_archive_directory_symlink_is_refused_without_external_write(self):
        archives = self.out / "archives"
        shutil.rmtree(archives)
        outside = self.root / "outside_archive"
        outside.mkdir()
        archives.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "archive directory symlink"):
            self.pack()
        self.assertEqual(list(outside.iterdir()), [])

    def test_output_directory_symlink_is_refused(self):
        alias = self.root / "output_alias"
        alias.symlink_to(self.out, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "capsule output symlink"):
            self.pack(alias)
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
