#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "HANDOFF_STATE.csv"
SVG_PATH = ROOT / "HANDOFF_STATE.svg"
WIDTH = 960
HEIGHT = 420
TOP = 66
ROW_HEIGHT = 54
BAR_X = 430
BAR_WIDTH = 400


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    expected = {"node", "state", "completion_percent"}
    if not rows or set(rows[0]) != expected:
        raise SystemExit("HANDOFF_STATE_SCHEMA_INVALID")
    for row in rows:
        percent = int(row["completion_percent"])
        if not 0 <= percent <= 100:
            raise SystemExit("HANDOFF_STATE_PERCENT_INVALID")
    return rows


def render(rows: list[dict[str, str]]) -> str:
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '  <rect width="100%" height="100%" fill="white"/>',
        '  <style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#111}.title{font-size:22px;font-weight:700}.node{font-size:14px}.state{font-size:13px}.pct{font-size:13px;font-weight:700}.bg{fill:#e6e6e6}.bar{fill:#555}.axis{stroke:#222;stroke-width:1}</style>',
        '  <text class="title" x="20" y="32">REI runtime recovery DAG — handoff rebind state</text>',
        f'  <line class="axis" x1="{BAR_X}" y1="48" x2="{BAR_X}" y2="382"/>',
        f'  <line class="axis" x1="{BAR_X + BAR_WIDTH}" y1="48" x2="{BAR_X + BAR_WIDTH}" y2="382"/>',
        f'  <text class="state" x="{BAR_X - 5}" y="46" text-anchor="end">0%</text>',
        f'  <text class="state" x="{BAR_X + BAR_WIDTH + 5}" y="46">100%</text>',
    ]
    for index, row in enumerate(rows):
        y = TOP + index * ROW_HEIGHT
        percent = int(row["completion_percent"])
        fill_width = BAR_WIDTH * percent / 100
        lines.extend(
            [
                f'  <text class="node" x="20" y="{y + 18}">{escape(row["node"])}</text>',
                f'  <text class="state" x="300" y="{y + 18}">{escape(row["state"])}</text>',
                f'  <rect class="bg" x="{BAR_X}" y="{y + 3}" width="{BAR_WIDTH}" height="22"/>',
            ]
        )
        if fill_width:
            lines.append(
                f'  <rect class="bar" x="{BAR_X}" y="{y + 3}" width="{fill_width:g}" height="22"/>'
            )
        lines.append(
            f'  <text class="pct" x="850" y="{y + 19}">{percent}%</text>'
        )
    lines.extend(
        [
            '  <text class="state" x="20" y="405">Status counts are DAG deliverables, not physics or solver maturity.</text>',
            '</svg>',
            '',
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", action="store_true")
    options = parser.parse_args()
    expected = render(read_rows())
    if options.write:
        SVG_PATH.write_text(expected, encoding="utf-8")
        return 0
    if not SVG_PATH.is_file() or SVG_PATH.read_text(encoding="utf-8") != expected:
        raise SystemExit("HANDOFF_STATE_SVG_MISMATCH")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
