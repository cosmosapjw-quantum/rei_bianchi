#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path
import sys
from xml.sax.saxutils import escape

source = Path(sys.argv[1])
target = Path(sys.argv[2])
rows = list(csv.DictReader(source.open(encoding="utf-8", newline="")))
width = 980
left = 330
top = 52
row_h = 42
height = top + row_h * len(rows) + 40
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
    '<rect width="100%" height="100%" fill="white"/>',
    '<text x="20" y="28" font-family="sans-serif" font-size="18">REI successor-host executable handoff state</text>',
]
for index, row in enumerate(rows):
    y = top + index * row_h
    value = float(row["completion_percent"])
    bar_w = 5.8 * value
    parts.append(
        f'<text x="20" y="{y + 21}" font-family="sans-serif" font-size="13">{escape(row["node"])}</text>'
    )
    parts.append(
        f'<rect x="{left}" y="{y + 7}" width="580" height="18" fill="none" stroke="black" stroke-width="1"/>'
    )
    parts.append(
        f'<rect x="{left}" y="{y + 7}" width="{bar_w:.1f}" height="18" fill="black"/>'
    )
    parts.append(
        f'<text x="925" y="{y + 21}" font-family="sans-serif" font-size="12">{value:.0f}%</text>'
    )
parts.append("</svg>")
target.write_text("\n".join(parts) + "\n", encoding="utf-8")
