"""One SVG postprocess from saved exact residuals; never imports the compiler."""
import argparse
from fractions import Fraction
import hashlib
from html import escape
import json
import math
from pathlib import Path
import resource
import signal
import time


def ratio(value):
    if value is None:
        return None
    return Fraction(value["numerator"], value["denominator"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    raw, target = Path(args.raw), Path(args.output)
    receipt_path = raw / "postprocessing_receipt.json"
    if receipt_path.exists() or target.exists():
        raise SystemExit("ALREADY_POSTPROCESSED")
    prior = json.loads((raw / "resource_receipt.json").read_text())
    remaining_cpu = 30 - prior["child_cpu_seconds"]
    remaining_wall = 120 - prior["wall_seconds"]
    if remaining_cpu <= 0 or remaining_wall <= 0:
        raise SystemExit("CUMULATIVE_BUDGET_EXHAUSTED")
    start_usage = resource.getrusage(resource.RUSAGE_SELF)
    started = time.monotonic()
    current_cpu = start_usage.ru_utime + start_usage.ru_stime
    resource.setrlimit(resource.RLIMIT_CPU, (max(1, math.ceil(current_cpu + remaining_cpu)), max(1, math.ceil(current_cpu + remaining_cpu))))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    signal.setitimer(signal.ITIMER_REAL, remaining_wall)
    result_bytes = (raw / "results.json").read_bytes()
    results = json.loads(result_bytes)
    rows = [row for row in results["rows"]
            if row["category"] in ("positive_chemistry", "algebraic_nuclear") and row["residuals"] is not None
            or row["intended_rejection"] and row["residuals"] is not None]
    values = []
    for row in rows:
        residuals = row["residuals"]
        isotopes = [abs(ratio(value)) for value in residuals.get("isotope_count", {}).values()]
        values.append([max(isotopes, default=Fraction(0)), ratio(residuals.get("charge")), ratio(residuals.get("energy"))])
    width, row_height, left, panel = 1160, 34, 425, 230
    height = 210 + row_height * len(rows)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="#fbfcfe"/>',
           '<style>text{font-family:Arial,sans-serif;fill:#142338}.small{font-size:12px}.label{font-size:13px}.title{font-size:23px;font-weight:bold}</style>',
           '<text x="24" y="35" class="title">Exact finite event ledger: saved residuals</text>',
           '<text x="24" y="60" class="label">Synthetic algebra only. Zero means exact rational cancellation; no physical rates or cosmological readiness.</text>',
           '<text x="24" y="84" class="small">Blue: accepted chemistry | Amber: typed nuclear algebra (isotope change allowed) | Red: intended rejected control | Gray: unqualified</text>']
    labels = ["Max |isotope-count residual|", "Signed charge residual", "Energy residual (eV/event)"]
    for p, label in enumerate(labels):
        x = left + p * panel
        max_value = max([abs(v[p]) for v in values if v[p] is not None] + [Fraction(1)])
        svg.append(f'<text x="{x + panel/2}" y="118" text-anchor="middle" class="label">{escape(label)}</text>')
        for frac in (-1, 0, 1):
            tick = x + panel / 2 + frac * (panel / 2 - 25)
            svg.append(f'<line x1="{tick}" y1="145" x2="{tick}" y2="{160 + row_height * len(rows)}" stroke="#dbe2ec"/>')
            svg.append(f'<text x="{tick}" y="138" text-anchor="middle" class="small">{escape(str(max_value * frac))}</text>')
        for i, (row, row_values) in enumerate(zip(rows, values)):
            y = 164 + i * row_height
            value = row_values[p]
            color = "#c83e4d" if row["intended_rejection"] else "#ad7000" if row["category"] == "algebraic_nuclear" else "#2563a8"
            if value is None:
                svg.append(f'<text x="{x + panel/2}" y="{y + 4}" text-anchor="middle" fill="#6b7280" class="small">UNQUALIFIED</text>')
            else:
                point = x + panel / 2 + float(value / max_value) * (panel / 2 - 25)
                svg.append(f'<circle cx="{point}" cy="{y}" r="5" fill="{color}"/>')
                if value:
                    svg.append(f'<text x="{point + 8}" y="{y + 4}" class="small">{escape(str(value))}</text>')
    for i, row in enumerate(rows):
        y = 164 + i * row_height
        tag = "[expected rejection]" if row["intended_rejection"] else "[nuclear algebra]" if row["category"] == "algebraic_nuclear" else "[accepted]"
        svg.append(f'<text x="24" y="{y + 4}" class="label">{escape(row["name"] + " " + tag)}</text>')
    svg.append(f'<text x="24" y="{height - 22}" class="small">Source: raw/results.json. Panels retain separate conservation quantities. No fixture was recomputed.</text>')
    svg.append('</svg>')
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x") as handle:
        handle.write("\n".join(svg) + "\n")
    elapsed = time.monotonic() - started
    ending = resource.getrusage(resource.RUSAGE_SELF)
    user = ending.ru_utime - start_usage.ru_utime
    system = ending.ru_stime - start_usage.ru_stime
    receipt = {"schema": "REI_CHEM_LEDGER_POSTPROCESS_RECEIPT_V1", "source_results_sha256": hashlib.sha256(result_bytes).hexdigest(),
               "source_row_names": [r["name"] for r in rows], "fixture_recomputation": False,
               "user_seconds": user, "system_seconds": system, "cpu_seconds": user + system, "wall_seconds": elapsed,
               "cumulative_unit_cpu_seconds": prior["child_cpu_seconds"] + user + system,
               "cumulative_unit_wall_seconds": prior["wall_seconds"] + elapsed, "peak_rss_kib": ending.ru_maxrss,
               "within_cumulative_cap": prior["child_cpu_seconds"] + user + system <= 30 and prior["wall_seconds"] + elapsed <= 120,
               "svg_path": str(target), "independent_rendered_inspection": "PENDING"}
    with receipt_path.open("x") as handle:
        json.dump(receipt, handle, indent=2)
        handle.write("\n")
    signal.setitimer(signal.ITIMER_REAL, 0)
    print(json.dumps(receipt))
    return 0 if receipt["within_cumulative_cap"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
