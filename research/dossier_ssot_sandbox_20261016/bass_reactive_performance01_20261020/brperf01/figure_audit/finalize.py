#!/usr/bin/env python3
"""Record export/source integrity and hash the finished figure payload only.

No simulation, scientific test, Rust build, or benchmark is launched. Run after
figures/render.py and completion of the visual audit/captions.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIGURES = ROOT / "figures"


def digest(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def write_json(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n")


def main():
    index = json.loads((FIGURES / "SOURCE_INDEX.json").read_text())
    mismatches = [name for name, record in index["sources"].items()
                  if digest(ROOT / name) != record]
    if mismatches:
        raise RuntimeError(f"Source evidence changed since rendering: {mismatches}")
    audit_sources = [
        "../project_sources/07-Figure-Residual-Error-Pass.txt",
        "../project_sources/08-Figure-Hostile-Audit.txt",
        "rates/REPORT_RATES_KO.md", "rates/examples/measure_rates.rs",
        "integration/README.md", "runtime_evidence/RUNTIME_IDENTITY.json",
        "rates/evidence/LEGACY_BASELINE.json",
    ]
    write_json("AUDIT_SOURCE_INDEX.json", {
        "path_base": "BRPERF01 root; ../ refers to its parent workspace",
        "sources": {name: digest(ROOT / name) for name in audit_sources},
    })
    exports = {}
    for path in sorted(FIGURES.glob("*.png")) + sorted(HERE.glob("*_90mm_preview.png")):
        with Image.open(path) as im:
            exports[str(path.relative_to(ROOT))] = {
                "pixels": im.size, "dpi": im.info.get("dpi"),
                "width_mm_from_metadata": 25.4 * im.width / im.info["dpi"][0],
            }
    for path in sorted(FIGURES.glob("*.pdf")):
        boxes = re.findall(rb"/MediaBox\s*\[([^\]]+)\]", path.read_bytes())
        exports[str(path.relative_to(ROOT))] = {
            "media_boxes_points": [value.decode() for value in boxes],
        }
    write_json("EXPORT_DIMENSIONS.json", exports)
    layout = json.loads((HERE / "LAYOUT_CHECKS.json").read_text())
    outside = {name: len(value["text_boxes_outside_canvas"]) for name, value in layout.items()}
    if any(outside.values()):
        raise RuntimeError(f"Clipped final figure text: {outside}")
    write_json("FINAL_STATUS.json", {
        "status": "PASS_SCOPED_FIGURES_AND_CAPTIONS",
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "figure_count": 3, "png_count": 3, "vector_pdf_count": 3,
        "half_width_preview_count": 3,
        "readback_verified_source_files": len(index["sources"]),
        "source_hash_mismatches": mismatches,
        "final_text_boxes_outside_canvas": outside,
        "visually_reviewed_widths_mm": [180, 90],
        "physical_printer_proof": False,
        "minimum_standard_font_pt_at180mm": 14,
        "minimum_standard_font_pt_at90mm": 7,
        "font_note": "Math superscripts/subscripts are smaller than their surrounding standard text.",
        "new_benchmarks": 0, "new_scientific_test_suites": 0,
        "new_rust_builds": 0, "new_physical_simulations": 0,
        "publication_scope_issue": "SIMD_TARGET_SCOPE_ISSUE.md: advertised host AVX/AVX512 capability differs from compiled target features; frozen report unchanged",
        "non_claims": ["combined end-to-end gain", "incremental SIMD gain", "global coefficient error bound", "universal second-order radiation-gas convergence", "admitted longspan solution"],
        "source_changes": "No edits to original evidence or frozen implementation/report files",
    })
    excluded_names = {"FIGURE_DELIVERABLE_MANIFEST.json", "SHA256SUMS"}
    payload = {}
    for directory in [FIGURES, HERE]:
        for path in sorted(directory.rglob("*")):
            if not path.is_file() or path.name in excluded_names:
                continue
            if any(part in {"mpl_cache", "__pycache__"} for part in path.relative_to(directory).parts):
                continue
            payload[str(path.relative_to(ROOT))] = digest(path)
    manifest = {
        "path_base": "BRPERF01 root",
        "status": "FROZEN_FIGURE_PAYLOAD_READY_FOR_ROOT_PUBLICATION",
        "payload_files": len(payload),
        "payload_bytes": sum(record["bytes"] for record in payload.values()),
        "exclusions": ["figure_audit/mpl_cache", "__pycache__", "manifest and SHA256SUMS self-reference"],
        "files": payload,
    }
    write_json("FIGURE_DELIVERABLE_MANIFEST.json", manifest)
    sums = [f"{record['sha256']}  {name}" for name, record in sorted(payload.items())]
    manifest_path = HERE / "FIGURE_DELIVERABLE_MANIFEST.json"
    sums.append(f"{digest(manifest_path)['sha256']}  figure_audit/FIGURE_DELIVERABLE_MANIFEST.json")
    (HERE / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    print(json.dumps({"payload_files": len(payload), "payload_bytes": manifest["payload_bytes"], "manifest": digest(manifest_path), "source_readbacks": len(index["sources"]), "outside_text": outside}, indent=2))


if __name__ == "__main__":
    main()
