#!/usr/bin/env python3
"""Seven frozen H1B1 DEB-member cases. Synthetic archives, no installation.

Run next to the unmodified PR #68 test_signed_archive_chain.py and its source.
This is newly materialized from the prior conversational draft, not a claimed
byte-identical recovery. The report never turns expected RED into process success.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tarfile
import unittest

from test_signed_archive_chain import SignedChainTests, PACKAGE, VERSION, FILENAME

HERE = Path(__file__).resolve().parent
TARGET = HERE / "deb_member_census.py"
MEMBER = "usr/bin/rei-member-fixture"
CONTENT = b"REI synthetic regular member; never executed\n"
MISSING = "MISSING_H1B1_DEB_MEMBER_CENSUS"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tar_gz(entries: list[tuple[str, bytes | str, bool]]) -> bytes:
    """Build inert tar fixtures in memory; never extract them."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.USTAR_FORMAT) as archive:
        for name, value, symlink in entries:
            item = tarfile.TarInfo(name)
            item.uid = item.gid = item.mtime = 0
            item.mode = 0o644
            if symlink:
                item.type = tarfile.SYMTYPE
                item.linkname = str(value)
                archive.addfile(item)
            else:
                if not isinstance(value, bytes):
                    raise TypeError("Regular fixture content must be bytes")
                item.size = len(value)
                archive.addfile(item, io.BytesIO(value))
    return gzip.compress(buffer.getvalue(), mtime=0)


def ar_member(name: str, payload: bytes) -> bytes:
    if len(name) > 15:
        raise ValueError("Fixture ar member name is too long")
    header = (
        f"{name + '/':<16}{0:<12}{0:<6}{0:<6}"
        f"{'100644':<8}{len(payload):<10}`\n"
    ).encode("ascii")
    if len(header) != 60:
        raise ValueError("Invalid fixture ar header")
    return header + payload + (b"\n" if len(payload) % 2 else b"")


def make_deb(
    *,
    control_version: str = VERSION,
    entries: list[tuple[str, bytes | str, bool]] | None = None,
) -> bytes:
    control = (
        f"Package: {PACKAGE}\n"
        f"Version: {control_version}\n"
        "Architecture: amd64\n"
        "Maintainer: Fixture <fixture@example.invalid>\n"
        "Description: Inert REI member-binding fixture\n"
    ).encode()
    if entries is None:
        entries = [("./" + MEMBER, CONTENT, False)]
    return b"!<arch>\n" + b"".join(
        (
            ar_member("debian-binary", b"2.0\n"),
            ar_member("control.tar.gz", tar_gz([("./control", control, False)])),
            ar_member("data.tar.gz", tar_gz(entries)),
        )
    )


class MemberCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = None
        cls.fixture_started = False
        if not TARGET.is_file():
            return
        spec = importlib.util.spec_from_file_location("rei_h1b1_member_census_tested", TARGET)
        if spec is None or spec.loader is None:
            raise RuntimeError("Cannot load member-census implementation")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        cls.mod = module
        SignedChainTests.setUpClass()
        cls.fixture_started = True
        cls.fixture = SignedChainTests()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.fixture_started:
            SignedChainTests.tearDownClass()

    def setUp(self) -> None:
        self.assertIsNotNone(self.mod, MISSING)

    def inputs(self, payload: bytes) -> dict:
        stanza = (
            f"Package: {PACKAGE}\nVersion: {VERSION}\n"
            f"Architecture: amd64\nFilename: {FILENAME}\n"
            f"Size: {len(payload)}\nSHA256: {sha256(payload)}\n"
            "Description: Inert signed DEB fixture\n\n"
        ).encode()
        signed, packed = self.fixture.bundle(plain=stanza)
        return {
            "inrelease": signed,
            "index_bytes": packed,
            "debs": {FILENAME: payload},
            "keyring": self.fixture.keyring,
            "policy": self.fixture.policy(),
            "gpgv": Path(shutil.which("gpgv")),
        }

    def audit(self, payload: bytes, **overrides):
        values = self.inputs(payload)
        values.update(overrides)
        return self.mod.verify_member_census(
            **values,
            required_members=((FILENAME, MEMBER, sha256(CONTENT)),),
        )

    def test_valid_signed_deb_and_regular_member(self) -> None:
        report = self.audit(make_deb())
        self.assertEqual(report["status"], "PASS_H1B1_AUTHENTICATED_DEB_MEMBERS")
        self.assertEqual(report["signed_chain"]["status"], "PASS_H1B1_SIGNED_ARCHIVE_CHAIN_COMPONENT")
        self.assertEqual(len(report["verified_members"]), 1)
        member = report["verified_members"][0]
        self.assertEqual(member["archive_filename"], FILENAME)
        self.assertEqual(member["member_path"], MEMBER)
        self.assertEqual(member["sha256"], sha256(CONTENT))
        self.assertEqual(report["authority_effect"], "NONE")
        self.assertFalse(report["installed_files_verified"])
        self.assertFalse(report["full_census_complete"])

    def test_authenticated_non_deb_payload_is_rejected(self) -> None:
        payload = b"Signed opaque bytes are not a DEB archive\n"
        values = self.inputs(payload)
        old = self.fixture.mod.verify_chain(**values)
        self.assertEqual(old["status"], "PASS_H1B1_SIGNED_ARCHIVE_CHAIN_COMPONENT")
        with self.assertRaisesRegex(ValueError, "DEB_FORMAT"):
            self.audit(payload)

    def test_control_identity_must_match_signed_index(self) -> None:
        payload = make_deb(control_version=VERSION + ".1")
        with self.assertRaisesRegex(ValueError, "CONTROL_IDENTITY"):
            self.audit(payload)

    def test_member_hash_is_checked_after_package_authentication(self) -> None:
        payload = make_deb(entries=[("./" + MEMBER, b"Different member bytes\n", False)])
        with self.assertRaisesRegex(ValueError, "MEMBER_HASH"):
            self.audit(payload)

    def test_symlink_is_not_a_regular_file_witness(self) -> None:
        payload = make_deb(entries=[("./" + MEMBER, "other-member", True)])
        with self.assertRaisesRegex(ValueError, "MEMBER_NOT_REGULAR"):
            self.audit(payload)

    def test_normalized_duplicate_member_is_rejected(self) -> None:
        payload = make_deb(entries=[("./" + MEMBER, CONTENT, False), (MEMBER, CONTENT, False)])
        with self.assertRaisesRegex(ValueError, "DUPLICATE_MEMBER"):
            self.audit(payload)

    def test_consumer_cannot_bypass_signature_verification(self) -> None:
        payload = make_deb()
        values = self.inputs(payload)
        bad = values["inrelease"].replace(b"Origin: Ubuntu", b"Origin: Ubuntx", 1)
        self.assertNotEqual(bad, values["inrelease"])
        with self.assertRaisesRegex(ValueError, "SIGNATURE"):
            self.audit(payload, inrelease=bad)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    # Select only this class: never recount the imported 18-test parent fixture.
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(MemberCensusTests)
    ids = [test.id() for test in suite]
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    expected_red = (result.testsRun == 7 and len(result.failures) == 7
                    and not result.errors and not result.skipped
                    and all(MISSING in text for _, text in result.failures))
    if args.report:
        payload = {
            "schema": "rei-h1b1-member-test-report/v1",
            "test_ids": ids, "tests": result.testsRun,
            "failures": len(result.failures), "errors": len(result.errors),
            "skipped": len(result.skipped), "successful": result.wasSuccessful(),
            "expected_missing_implementation_red": expected_red,
            "fixture": "SYNTHETIC_DEB_NOT_REAL_UBUNTU",
            "native_runtime": "NOT_RUN", "authority_effect": "NONE",
        }
        # Evidence is create-only, including RED. Existing output is never overwritten.
        with args.report.open("x", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
    raise SystemExit(0 if result.wasSuccessful() else 1)
