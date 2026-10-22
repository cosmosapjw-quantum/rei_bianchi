"""Package the frozen tritium audit with its existing atomic-pilot context.

Run only after the scientific reviewer freezes the current unit. The archive
contains source and saved raw evidence, not a new scientific computation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / "research/rei_isotope_quotient_pilot_20261022"
NEW = ROOT / "research/rei_tritium_production_audit_20261022"
SOURCE_INTAKE = (ROOT / "research/rei_full_nuclear_source_intake_20261022"
                 / "PROVIDER_CODE_INTAKE.md")
DUPLICATE_FAILED_RAW = {
    "NUCLEAR_NETWORK_DUPLICATE_TRAPEZOID_EXECUTION_STDOUT.json",
    "NUCLEAR_NETWORK_DUPLICATE_TRAPEZOID_HISTORIES.npz",
    "NUCLEAR_NETWORK_DUPLICATE_TRAPEZOID_REPORT.json",
    "NUCLEAR_NETWORK_REAPPEARED_HISTORIES.npz",
    "NUCLEAR_NETWORK_REAPPEARED_REPORT.json",
}


def members(output: Path) -> list[Path]:
    paths = [ROOT / "AGENTS.md", SOURCE_INTAKE]
    for unit in (OLD, NEW):
        paths.extend(p for p in unit.rglob("*") if p.is_file()
                     and "__pycache__" not in p.parts
                     and p.suffix not in (".pyc", ".zip")
                     and p.name not in DUPLICATE_FAILED_RAW
                     and p.resolve() != output.resolve())
    paths.sort(key=lambda p: p.relative_to(ROOT).as_posix())
    for p in paths:
        rel = p.relative_to(ROOT).as_posix().lower()
        if "private_ncp" in rel or "ncp_raw" in rel:
            raise RuntimeError(f"Private NCP raw path encountered: {p}")
        if p.suffix.lower() in (".html", ".htm") or (
            p.suffix.lower() == ".pdf"
            and not any(part.startswith("figures") for part in p.parts)
        ):
            raise RuntimeError(f"Review redistribution of source-cache document: {p}")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path, help="Absolute destination ZIP path")
    args = parser.parse_args()
    out = args.output.resolve()
    if not out.is_absolute() or not OLD.is_dir() or not NEW.is_dir():
        parser.error("Absolute output and both source units are required")
    files = members(out)
    if len(files) < 300:
        raise RuntimeError("Expected standalone old atomic pilot plus new audit")
    out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(out, "w", compression=ZIP_DEFLATED, compresslevel=6) as z:
        for p in files:
            info = ZipInfo(p.relative_to(ROOT).as_posix(), (2026, 10, 21, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=6)
    with ZipFile(out) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError(f"ZIP CRC failure: {bad}")
        assert len(z.namelist()) == len(files)
    print(json.dumps({"output": str(out), "members": len(files),
                      "bytes": out.stat().st_size,
                      "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
                      "local_zip_crc": "PASS"}, indent=2))


if __name__ == "__main__":
    main()
