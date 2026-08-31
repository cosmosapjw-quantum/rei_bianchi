from __future__ import annotations

import hashlib
import importlib.util
import io
import os
import tarfile
import tempfile
import threading
import time
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "extract_bundle.py"
SPEC = importlib.util.spec_from_file_location("rei_safe_bundle_extractor", MODULE_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import machinery guard
    raise RuntimeError(f"cannot load extractor: {MODULE_PATH}")
EXTRACTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXTRACTOR)

ROOT = "REI_SEALED_NATIVE_BUILD_AUTHORITY_20260831"


def _directory(name: str, mode: int = 0o755) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.type = tarfile.DIRTYPE
    info.mode = mode
    return info


def _file(name: str, data: bytes, mode: int = 0o644) -> tuple[tarfile.TarInfo, bytes]:
    info = tarfile.TarInfo(name)
    info.type = tarfile.REGTYPE
    info.mode = mode
    info.size = len(data)
    return info, data


def _symlink(name: str, target: str) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.type = tarfile.SYMTYPE
    info.linkname = target
    info.mode = 0o777
    return info


def _special(name: str, kind: bytes) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.type = kind
    info.mode = 0o600
    if kind == tarfile.LNKTYPE:
        info.linkname = f"{ROOT}/rootfs/payload"
    return info


def _base_members() -> list[tarfile.TarInfo | tuple[tarfile.TarInfo, bytes]]:
    return [
        _directory(ROOT),
        _file(f"{ROOT}/AUTHORITY_MANIFEST.json", b"{}\n"),
        _directory(f"{ROOT}/rootfs"),
    ]


def _write_archive(
    path: Path,
    members: list[tarfile.TarInfo | tuple[tarfile.TarInfo, bytes]],
) -> str:
    with tarfile.open(path, "w:xz", format=tarfile.PAX_FORMAT) as archive:
        for value in members:
            if isinstance(value, tuple):
                info, data = value
                archive.addfile(info, io.BytesIO(data))
            else:
                archive.addfile(value)
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SafeBundleExtractorTests(unittest.TestCase):
    def test_extracts_only_valid_bundle_without_executing_members(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            archive = base / "authority.tar.xz"
            marker = base / "must-not-exist"
            payload = f"#!/bin/sh\ntouch {marker}\n".encode()
            expected = _write_archive(
                archive,
                _base_members()
                + [
                    _directory(f"{ROOT}/rootfs/usr"),
                    _directory(f"{ROOT}/rootfs/usr/bin"),
                    _file(f"{ROOT}/rootfs/usr/bin/tool", payload, 0o755),
                    _symlink(f"{ROOT}/rootfs/usr/bin/tool-link", "tool"),
                ],
            )

            destination = base / "extracted"
            receipt = EXTRACTOR.extract_bundle(archive, destination, expected)

            bundle = destination / ROOT
            self.assertEqual((bundle / "AUTHORITY_MANIFEST.json").read_bytes(), b"{}\n")
            self.assertEqual((bundle / "rootfs/usr/bin/tool").read_bytes(), payload)
            self.assertEqual(os.readlink(bundle / "rootfs/usr/bin/tool-link"), "tool")
            self.assertFalse(marker.exists())
            self.assertEqual(receipt["archive_sha256"], expected)
            self.assertEqual(receipt["archive_root"], ROOT)
            self.assertEqual(receipt["member_count"], 7)

    def test_accepts_empty_existing_destination_and_logical_absolute_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            archive = base / "authority.tar.xz"
            expected = _write_archive(
                archive,
                _base_members()
                + [
                    _directory(f"{ROOT}/rootfs/etc"),
                    _file(f"{ROOT}/rootfs/etc/terminal", b"terminal"),
                    _directory(f"{ROOT}/rootfs/usr"),
                    _symlink(f"{ROOT}/rootfs/usr/absolute-link", "/etc/terminal"),
                ],
            )
            destination = base / "existing-empty"
            destination.mkdir()

            EXTRACTOR.extract_bundle(archive, destination, expected)

            link = destination / ROOT / "rootfs/usr/absolute-link"
            self.assertEqual(os.readlink(link), "/etc/terminal")

    def test_rejects_wrong_or_malformed_external_archive_digest_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            archive = base / "authority.tar.xz"
            _write_archive(archive, _base_members())
            for digest in ("0" * 64, "A" * 64, "not-a-digest"):
                destination = base / f"out-{len(list(base.iterdir()))}"
                with self.subTest(digest=digest), self.assertRaises(
                    EXTRACTOR.BundleExtractionError
                ):
                    EXTRACTOR.extract_bundle(archive, destination, digest)
                self.assertFalse(destination.exists())

    def test_rejects_archive_mutated_after_initial_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            archive = base / "authority.tar.xz"
            payload = bytes(range(251)) * 65536
            expected = _write_archive(
                archive,
                _base_members() + [_file(f"{ROOT}/rootfs/payload", payload)],
            )
            destination = base / "out"
            mutation_errors: list[BaseException] = []

            def mutate_after_destination_creation() -> None:
                deadline = time.monotonic() + 10
                while not destination.exists():
                    if time.monotonic() >= deadline:
                        mutation_errors.append(TimeoutError("extractor never created destination"))
                        return
                    time.sleep(0.0001)
                try:
                    with archive.open("ab", buffering=0) as stream:
                        stream.write(b"ARCHIVE_MUTATED_DURING_EXTRACTION")
                        os.fsync(stream.fileno())
                except BaseException as exc:  # pragma: no cover - diagnostic transport
                    mutation_errors.append(exc)

            mutator = threading.Thread(target=mutate_after_destination_creation)
            mutator.start()
            try:
                with self.assertRaisesRegex(
                    EXTRACTOR.BundleExtractionError,
                    "ARCHIVE_CHANGED_DURING_EXTRACTION",
                ):
                    EXTRACTOR.extract_bundle(archive, destination, expected)
            finally:
                mutator.join(timeout=10)

            self.assertFalse(mutator.is_alive())
            self.assertEqual(mutation_errors, [])

    def test_rejects_nonempty_file_or_symlink_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            archive = base / "authority.tar.xz"
            expected = _write_archive(archive, _base_members())
            nonempty = base / "nonempty"
            nonempty.mkdir()
            (nonempty / "sentinel").write_text("preserve", encoding="utf-8")
            regular = base / "regular"
            regular.write_text("preserve", encoding="utf-8")
            target = base / "target"
            target.mkdir()
            symlink = base / "symlink"
            symlink.symlink_to(target, target_is_directory=True)

            for destination in (nonempty, regular, symlink):
                with self.subTest(destination=destination), self.assertRaises(
                    EXTRACTOR.BundleExtractionError
                ):
                    EXTRACTOR.extract_bundle(archive, destination, expected)

            self.assertEqual((nonempty / "sentinel").read_text(encoding="utf-8"), "preserve")
            self.assertEqual(regular.read_text(encoding="utf-8"), "preserve")
            self.assertTrue(symlink.is_symlink())

    def test_rejects_absolute_dotdot_duplicate_and_extra_root_members_preflight(self) -> None:
        cases = {
            "absolute": _base_members() + [_file("/etc/passwd", b"bad")],
            "dotdot": _base_members() + [_file(f"{ROOT}/../escape", b"bad")],
            "duplicate": _base_members()
            + [
                _file(f"{ROOT}/rootfs/payload", b"one"),
                _file(f"{ROOT}/rootfs/payload", b"two"),
            ],
            "extra-root": _base_members() + [_file("SECOND_ROOT/payload", b"bad")],
            "extra-bundle-top-level": _base_members()
            + [_file(f"{ROOT}/README", b"not permitted")],
        }
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for name, members in cases.items():
                archive = base / f"{name}.tar.xz"
                expected = _write_archive(archive, members)
                destination = base / f"{name}-out"
                with self.subTest(name=name), self.assertRaises(
                    EXTRACTOR.BundleExtractionError
                ):
                    EXTRACTOR.extract_bundle(archive, destination, expected)
                self.assertFalse(destination.exists())

    def test_rejects_hard_links_devices_fifos_and_unknown_types_preflight(self) -> None:
        special_types = {
            "hard-link": tarfile.LNKTYPE,
            "character-device": tarfile.CHRTYPE,
            "block-device": tarfile.BLKTYPE,
            "fifo": tarfile.FIFOTYPE,
            "socket-or-unknown": b"S",
        }
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for name, kind in special_types.items():
                archive = base / f"{name}.tar.xz"
                expected = _write_archive(
                    archive,
                    _base_members() + [_special(f"{ROOT}/rootfs/special", kind)],
                )
                destination = base / f"{name}-out"
                with self.subTest(name=name), self.assertRaises(
                    EXTRACTOR.BundleExtractionError
                ):
                    EXTRACTOR.extract_bundle(archive, destination, expected)
                self.assertFalse(destination.exists())

    def test_rejects_members_beneath_symlink_ancestors_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            archive = base / "authority.tar.xz"
            expected = _write_archive(
                archive,
                _base_members()
                + [
                    _directory(f"{ROOT}/rootfs/terminal"),
                    _symlink(f"{ROOT}/rootfs/link", "/terminal"),
                    _file(f"{ROOT}/rootfs/link/payload", b"must not escape"),
                ],
            )
            destination = base / "out"

            with self.assertRaises(EXTRACTOR.BundleExtractionError):
                EXTRACTOR.extract_bundle(archive, destination, expected)

            self.assertFalse(destination.exists())

    def test_rejects_escaping_missing_and_cyclic_symlink_targets_preflight(self) -> None:
        cases = {
            "escape": _base_members()
            + [_symlink(f"{ROOT}/rootfs/link", "../../host")],
            "missing": _base_members()
            + [_symlink(f"{ROOT}/rootfs/link", "/not-declared")],
            "cycle": _base_members()
            + [
                _symlink(f"{ROOT}/rootfs/a", "b"),
                _symlink(f"{ROOT}/rootfs/b", "a"),
            ],
        }
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for name, members in cases.items():
                archive = base / f"{name}.tar.xz"
                expected = _write_archive(archive, members)
                destination = base / f"{name}-out"
                with self.subTest(name=name), self.assertRaises(
                    EXTRACTOR.BundleExtractionError
                ):
                    EXTRACTOR.extract_bundle(archive, destination, expected)
                self.assertFalse(destination.exists())

    def test_rejects_missing_manifest_or_rootfs_preflight(self) -> None:
        cases = {
            "manifest": [_directory(ROOT), _directory(f"{ROOT}/rootfs")],
            "rootfs": [
                _directory(ROOT),
                _file(f"{ROOT}/AUTHORITY_MANIFEST.json", b"{}\n"),
            ],
        }
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for name, members in cases.items():
                archive = base / f"missing-{name}.tar.xz"
                expected = _write_archive(archive, members)
                destination = base / f"missing-{name}-out"
                with self.subTest(name=name), self.assertRaises(
                    EXTRACTOR.BundleExtractionError
                ):
                    EXTRACTOR.extract_bundle(archive, destination, expected)
                self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
