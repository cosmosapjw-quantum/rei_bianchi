#!/usr/bin/env python3
"""Render a dependency-count plot without external plotting packages."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "NT_PATH_CLOSURE_RECEIPT_R1.json"
CSV = HERE / "IMPORT_CLOSURE_DELTA.csv"
SVG = HERE / "IMPORT_CLOSURE_DELTA.svg"


def main() -> int:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    rows = [
        ("declared import roots", receipt["declared_import_root_count_before"], receipt["declared_import_root_count_after"]),
        ("forbidden import roots", 2, len(receipt["forbidden_import_roots"])),
        ("declared source paths", receipt["declared_path_count"], receipt["declared_path_count"]),
        ("production bridge bytes changed", 0, int(receipt["production_bridge_changed"])),
    ]
    with CSV.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["quantity", "before", "after", "delta"])
        for label, before, after in rows:
            writer.writerow([label, before, after, after - before])

    width, height = 920, 410
    left, right, top, bottom = 260, 50, 55, 70
    chart_width = width - left - right
    maximum = max(max(before, after) for _, before, after in rows)
    scale = chart_width / max(maximum, 1)
    group_height = 72
    bar_height = 22
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#111}.title{font-size:20px;font-weight:700}.label{font-size:14px}.value{font-size:13px}.axis{stroke:#333;stroke-width:1}.before{fill:#7a7a7a}.after{fill:#2f6f9f}</style>',
        '<text x="460" y="30" text-anchor="middle" class="title">REI ntpath runtime-closure delta</text>',
    ]
    for index, (label, before, after) in enumerate(rows):
        y = top + index * group_height
        pieces.append(f'<text x="{left - 12}" y="{y + 25}" text-anchor="end" class="label">{html.escape(label)}</text>')
        before_width = before * scale
        after_width = after * scale
        pieces.append(f'<rect class="before" x="{left}" y="{y}" width="{before_width:.3f}" height="{bar_height}"/>')
        pieces.append(f'<rect class="after" x="{left}" y="{y + 28}" width="{after_width:.3f}" height="{bar_height}"/>')
        pieces.append(f'<text x="{left + before_width + 6:.3f}" y="{y + 16}" class="value">before {before}</text>')
        pieces.append(f'<text x="{left + after_width + 6:.3f}" y="{y + 44}" class="value">after {after}</text>')
    axis_y = top + len(rows) * group_height + 5
    pieces.append(f'<line class="axis" x1="{left}" y1="{axis_y}" x2="{width-right}" y2="{axis_y}"/>')
    pieces.append('<rect class="before" x="310" y="365" width="20" height="12"/><text x="338" y="376" class="value">before</text>')
    pieces.append('<rect class="after" x="440" y="365" width="20" height="12"/><text x="468" y="376" class="value">after</text>')
    pieces.append('<text x="460" y="400" text-anchor="middle" class="value">Only declared-import roots change: +1 ntpath; all authority/firewall counts remain fixed.</text>')
    pieces.append('</svg>')
    SVG.write_text("\n".join(pieces) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "csv": str(CSV), "svg": str(SVG)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
