#!/usr/bin/env python3
"""Render the successor-preflight state figure deterministically."""

from __future__ import annotations

import argparse
import csv
from html import escape
from pathlib import Path


HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "PREFLIGHT_STATE.csv"
SVG_PATH = HERE / "PREFLIGHT_STATE.svg"


def render() -> str:
    with CSV_PATH.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    width = 1400
    height = 100 + 42 * len(rows)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="white"/>',
        '<text x="40" y="38" font-family="sans-serif" font-size="24" font-weight="bold">REI successor Section-0 preflight state</text>',
        '<text x="40" y="64" font-family="sans-serif" font-size="14">Per-node deliverable state; not solver or science maturity.</text>',
    ]
    for index, row in enumerate(rows):
        y = 82 + 42 * index
        completion = int(row["completion_percent"])
        bar_width = 500 * completion // 100
        fill = "#333333" if completion else "#dddddd"
        lines.extend(
            [
                f'<text x="40" y="{y + 18}" font-family="monospace" font-size="14">{escape(row["node"])}</text>',
                f'<rect x="500" y="{y}" width="500" height="24" fill="none" stroke="#555555" stroke-width="1"/>',
                f'<rect x="500" y="{y}" width="{bar_width}" height="24" fill="{fill}"/>',
                f'<text x="1015" y="{y + 18}" font-family="monospace" font-size="14">{completion:3d}%</text>',
                f'<text x="1080" y="{y + 18}" font-family="monospace" font-size="13">{escape(row["state"])}</text>',
            ]
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    options = parser.parse_args()
    expected = render()
    if options.verify:
        if not SVG_PATH.is_file() or SVG_PATH.read_text(encoding="utf-8") != expected:
            raise SystemExit("PREFLIGHT_STATE_SVG_MISMATCH")
        print("PREFLIGHT_STATE_SVG_PASS")
        return 0
    SVG_PATH.write_text(expected, encoding="utf-8")
    print(SVG_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
