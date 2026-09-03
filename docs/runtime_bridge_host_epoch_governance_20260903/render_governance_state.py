#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path
import sys


def render(csv_path: Path) -> str:
    with csv_path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    width = 960
    height = 90 + 54 * len(rows)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="30" y="38" font-family="sans-serif" font-size="24" font-weight="bold">REI runtime governance state</text>',
        '<text x="30" y="66" font-family="sans-serif" font-size="14">Per-node deliverables; not solver or science maturity</text>',
    ]
    for index, row in enumerate(rows):
        y = 94 + 54 * index
        value = int(row["completion_percent"])
        bar = 4 * value
        lines.extend([
            f'<text x="30" y="{y + 20}" font-family="sans-serif" font-size="15">{row["node"]}</text>',
            f'<rect x="390" y="{y}" width="400" height="24" fill="none" stroke="black"/>',
            f'<rect x="390" y="{y}" width="{bar}" height="24" fill="black"/>',
            f'<text x="805" y="{y + 18}" font-family="sans-serif" font-size="14">{value}%  {row["state"]}</text>',
        ])
    lines.append('</svg>')
    return "\n".join(lines) + "\n"


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: render_governance_state.py INPUT.csv OUTPUT.svg")
    output = Path(sys.argv[2])
    output.write_text(render(Path(sys.argv[1])), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
