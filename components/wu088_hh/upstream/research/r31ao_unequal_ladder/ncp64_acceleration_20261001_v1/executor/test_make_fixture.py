"""Manifest bridge tests only: fake receipt bytes, never native execution."""
import json
from pathlib import Path
import tempfile
import unittest

from core import ContractError, file_identity, load_manifest, verify_files
from make_fixture import create_native_fixture


def receipt_fixture(folder):
    root = Path(folder)
    lib = root / "lib"
    lib.mkdir()
    def recorded(path, data):
        path.write_bytes(data)
        item = file_identity(path)
        return {"path": item["path"], "size": item["bytes"], "sha256": item["sha256"]}
    binary = recorded(root / "native_cache_synthetic", b"SYNTHETIC_METADATA_FIXTURE_NOT_ELF\n")
    Path(binary["path"]).chmod(0o700)
    libraries = {name: recorded(lib / ("lib" + name + ".so.1"), name.encode())
                 for name in ("flint", "gmp", "mpfr")}
    source = recorded(root / "source.cpp", b"// source metadata fixture\n")
    record = recorded(root / "provenance.json", b'{"metadata_test_only":true}\n')
    compiler = recorded(root / "compiler", b"NOT_A_COMPILER\n")
    version = recorded(root / "compiler.txt", b"metadata fixture version\n")
    link = recorded(root / "linked_libraries.txt", b"synthetic metadata fixture\n")
    doc = {"scope": "SYNTHETIC_ONLY", "native_executed": False,
           "native_equality_verified": False, "actual_HH_runs": 0, "scientific_promotion": False,
           "binary": binary, "sources": [source], "backend_record": record,
           "native_compiler": compiler, "native_compiler_version_output": version,
           "link_report": link, "native_flags": ["-std=c++17", "-O3", "-fno-fast-math", "-ffp-contract=off"],
           "backend_byte_chain": {"status": "BYTE_CHAIN_VERIFIED", "libraries": {
               name: {"binary": item, "source": source} for name, item in libraries.items()}},
           "linkage": {"status": "LINKED_BACKEND_PATHS_VERIFIED", "libraries": libraries,
                       "system_libraries": []}}
    receipt = root / "BUILD_READY.json"
    receipt.write_text(json.dumps(doc) + "\n")
    return receipt, lib, doc


class NativeManifestTests(unittest.TestCase):
    def test_native_receipt_binds_loader_env_and_all_byte_identities(self):
        with tempfile.TemporaryDirectory() as d:
            receipt, lib, evidence = receipt_fixture(d)
            path = Path(d) / "tasks.json"
            create_native_fixture(path, Path(d) / "run", None, ["point107"],
                                  build_ready=receipt, backend_library_path=lib)
            task = load_manifest(path)["tasks"][0]
            self.assertEqual(task["env"], {"LD_LIBRARY_PATH": str(lib)})
            self.assertEqual(len(task["library_pins"]), 3)
            self.assertIn(file_identity(receipt), task["inputs"])
            self.assertIn(file_identity(Path(evidence["sources"][0]["path"])), task["inputs"])
            self.assertEqual(task["argv"][2], "OUTPUT_PATH")
            verify_files(task)  # Hash and permissions only; does not execute fake binary.

    def test_native_requires_receipt_explicit_loader_dir_and_three_library_pins(self):
        with tempfile.TemporaryDirectory() as d:
            receipt, lib, doc = receipt_fixture(d)
            for kind in ("no_receipt", "no_directory", "missing_library", "wrong_directory"):
                current = json.loads(json.dumps(doc))
                if kind == "missing_library":
                    del current["linkage"]["libraries"]["mpfr"]
                receipt.write_text(json.dumps(current))
                with self.subTest(kind=kind), self.assertRaises(ContractError):
                    create_native_fixture(Path(d) / (kind + ".json"), Path(d) / (kind + "_run"),
                        doc["binary"]["path"], ["point107"],
                        build_ready=None if kind == "no_receipt" else receipt,
                        backend_library_path=None if kind == "no_directory" else (Path(d) if kind == "wrong_directory" else lib))

    def test_native_changed_binary_library_or_receipt_identity_refused(self):
        for field in ("binary", "library", "source", "chain_binary", "backend_argument"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                receipt, lib, doc = receipt_fixture(d)
                backend = None
                if field == "chain_binary":
                    doc["backend_byte_chain"]["libraries"]["flint"]["binary"] = dict(doc["binary"])
                    receipt.write_text(json.dumps(doc))
                elif field == "backend_argument":
                    backend = doc["native_compiler"]["path"]
                else:
                    item = doc["binary"] if field == "binary" else (doc["sources"][0] if field == "source" else doc["linkage"]["libraries"]["flint"])
                    Path(item["path"]).write_bytes(b"changed")
                with self.assertRaises(ContractError):
                    create_native_fixture(Path(d) / "tasks.json", Path(d) / "run", backend,
                        ["complex_box107"], build_ready=receipt, backend_library_path=lib)

    def test_native_scope_and_case_limits_refused(self):
        with tempfile.TemporaryDirectory() as d:
            receipt, lib, doc = receipt_fixture(d)
            for index, (cases, precision, repeat) in enumerate([
                    (["HH"], 128, 1), (["errors"], 128, 2), (["point107"], 16, 1)]):
                with self.assertRaises(ContractError):
                    create_native_fixture(Path(d) / f"m{index}.json", Path(d) / f"r{index}", None,
                        cases, precision, repeat, build_ready=receipt, backend_library_path=lib)
            doc["actual_HH_runs"] = 1
            receipt.write_text(json.dumps(doc))
            with self.assertRaises(ContractError):
                create_native_fixture(Path(d) / "bad.json", Path(d) / "bad_run", None,
                    ["point107"], build_ready=receipt, backend_library_path=lib)


if __name__ == "__main__":
    unittest.main()
