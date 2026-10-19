#!/usr/bin/env python3
"""Read-only BR04 figure consistency and adversarial checks.

The original plot functions are imported, their finish hook is replaced by an
in-memory capture, and intentionally corrupted inputs live in TemporaryDirectory.
Original plots, input data, and plotting source are never changed. This harness
does not replace human view_image inspection or grant journal-print qualification.
"""
from __future__ import annotations

import argparse
import copy
import csv
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import tempfile

import numpy as np


def read_csv(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def identity(path):
    return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size}


def figure_extent_audit(plot, fig):
    """Inspect text actually drawn, excluding dormant out-of-range log ticks."""
    drawn = {}
    original_draw = plot.matplotlib.text.Text.draw

    def draw(text, renderer):
        if text.get_visible() and text.get_text().strip():
            drawn[id(text)] = text
        return original_draw(text, renderer)

    plot.matplotlib.text.Text.draw = draw
    try:
        fig.canvas.draw()
    finally:
        plot.matplotlib.text.Text.draw = original_draw
    renderer = fig.canvas.get_renderer()
    width, height = fig.get_size_inches()
    fw, fh = fig.canvas.get_width_height()
    clipped = []
    for text in drawn.values():
        box = text.get_window_extent(renderer)
        if box.x0 < -1 or box.y0 < -1 or box.x1 > fw + 1 or box.y1 > fh + 1:
            clipped.append({"text": text.get_text(), "bbox": list(map(float, box.extents))})
    fonts = [text.get_fontsize() for text in drawn.values()]
    axes = []
    for index, ax in enumerate(fig.axes):
        low, high = sorted(ax.get_ylim())
        violations = []
        for i, line in enumerate(ax.lines):
            if not line.get_visible():
                continue
            values = np.asarray(line.get_ydata(), dtype=float)
            values = values[np.isfinite(values)]
            if np.any(values < low - 1e-12) or np.any(values > high + 1e-12):
                violations.append({"line": i, "min": float(values.min()), "max": float(values.max())})
        for i, patch in enumerate(ax.patches):
            if hasattr(patch, "get_height"):
                bottom, top = patch.get_y(), patch.get_y() + patch.get_height()
                if min(bottom, top) < low - 1e-12 or max(bottom, top) > high + 1e-12:
                    violations.append({"bar": i, "range": [bottom, top]})
        axes.append({"axis": index, "ylim": [low, high], "outside_y_range": violations})
    return {
        "width_mm": float(width * 25.4), "height_mm": float(height * 25.4),
        "drawn_texts": len(drawn), "clipped_drawn_texts": clipped,
        "min_font_pt": min(fonts),
        "font_at_90mm_pt": min(fonts) * 90 / (width * 25.4),
        "font_at_182mm_pt": min(fonts) * 182 / (width * 25.4),
        "axis_ranges": axes,
        "digital_bounds_pass": not clipped and all(not a["outside_y_range"] for a in axes),
    }


def optical_w1_parts(rows):
    """Decimal75 direct CDF primitive, independent of Rust positive psi/chi."""
    with localcontext() as context:
        context.prec = 75
        d = Decimal
        denominator = 1 - (-d(93)).exp()
        nodes = sorted((d(row["age"]) * 93, d(row["emitted_weight"])) for row in rows)
        weights = [weight * (-age).exp() for age, weight in nodes]
        total = sum(weights)

        def interval(lower, upper, plateau):
            if upper <= lower:
                return d(0)
            crossing = d(0) if plateau == 0 else d(93) if plateau == 1 else -(1 - plateau * denominator).ln()

            def primitive(x):
                return (x + (-x).exp()) / denominator - plateau * x

            if upper <= crossing:
                return primitive(lower) - primitive(upper)
            if lower >= crossing:
                return primitive(upper) - primitive(lower)
            return primitive(lower) + primitive(upper) - 2 * primitive(crossing)

        previous, prefix, full, visible = d(0), d(0), d(0), d(0)
        for (age, _), weight in zip(nodes, weights):
            full += interval(previous, age, prefix / total)
            if previous < 6:
                visible += interval(previous, min(age, d(6)), prefix / total)
            prefix += weight
            previous = age
        full += interval(previous, d(93), d(1))
        if previous < 6:
            visible += interval(previous, d(6), d(1))
        return full, visible, (full - visible) / full


def resolve_native_csv(unit, original):
    path = Path(original)
    if path.exists():
        return path
    restored = unit / "reused_br03/evidence/native" / path.name
    if restored.exists():
        return restored
    raise FileNotFoundError(original)


def run(unit):
    report = {"execution_utc": datetime.now(timezone.utc).isoformat(),
              "checks": [], "mutations": [], "figures": {}, "source_identities": {}}

    def check(name, condition, **details):
        report["checks"].append({"id": name, "pass": bool(condition), **details})

    def mutation(name, caught, **details):
        report["mutations"].append({"id": name, "caught": bool(caught), **details})

    for relative in ["scripts/plot_br04.py", "evidence/figures/PLOT_PROVENANCE.json",
                     "evidence/age_study/AGE_CERTIFICATES.csv", "evidence/age_study/AGE_ACTUAL_NODES.csv",
                     "evidence/age_study/AGE_SOURCE_CERTIFICATES.csv", "evidence/age_study/AGE_SOURCE_MIXTURE_BOUNDS.csv",
                     "evidence/native_audit/crossed/TIME_AGE_ANALYSIS.json", "evidence/figures/NATIVE_PLOT_POINTS.csv"]:
        report["source_identities"][relative] = identity(unit / relative)
    for path in sorted((unit / "evidence/figures").glob("*.png")) + sorted((unit / "evidence/figures").glob("*.pdf")):
        report["source_identities"][str(path.relative_to(unit))] = identity(path)
    provenance = json.loads((unit / "evidence/figures/PLOT_PROVENANCE.json").read_text())
    check("render_provenance_hashes",
          provenance["script_sha256"] == report["source_identities"]["scripts/plot_br04.py"]["sha256"]
          and all(f["png_sha256"] == report["source_identities"][f"evidence/figures/{f['name']}.png"]["sha256"]
                  for f in provenance["figures"]))

    spec = importlib.util.spec_from_file_location("br04_plot_readonly_audit", unit / "scripts/plot_br04.py")
    plot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plot)
    plot.plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False,
                             "axes.spines.right": False, "font.size": 10})
    captured = {}
    plot.finish = lambda fig, out, name, paths, figures: captured.__setitem__(name, fig)
    with tempfile.TemporaryDirectory(prefix="rei_br04_plot_audit_") as temporary:
        out = Path(temporary)
        plot.shape_figure(unit, out, [])
        plot.native_figure(unit, out, [])
        plot.source_figure(unit, out, [])
        for name, fig in captured.items():
            result = figure_extent_audit(plot, fig)
            report["figures"][name] = result
            check(name + "_digital_bounds", result["digital_bounds_pass"])

        all_bounds = read_csv(unit / "evidence/age_study/AGE_SOURCE_MIXTURE_BOUNDS.csv")
        ap = sorted([r for r in all_bounds if r["family"] == "AP" and r["measure"] == "survivor"],
                    key=lambda r: int(r["resolution"]))
        actual = np.asarray(captured["BR04_SOURCE_AGE_BOUNDS"].axes[2].lines[0].get_ydata(), dtype=float)
        expected = np.array([float(r["duration_s"]) * float(r["mixture_w1_upper_bound"]) for r in ap])
        actual_mean = np.asarray(captured["BR04_SOURCE_AGE_BOUNDS"].axes[2].lines[1].get_ydata(), dtype=float)
        expected_mean = np.array([float(r["duration_s"]) * abs(float(r["mixture_mean_defect"])) for r in ap])
        check("source_physical_units_actual_artists", np.array_equal(actual, expected)
              and np.array_equal(actual_mean, expected_mean),
              W1_seconds=list(actual), mean_error_seconds=list(actual_mean))
        omitted = np.array([float(r["mixture_w1_upper_bound"]) for r in ap])
        mutation("omit_T_from_physical_W1", not np.allclose(actual, omitted, rtol=1e-12, atol=0),
                 detector="actual artist versus T*W1_x", missing_factor=8e12,
                 max_relative_mismatch=float(np.max(abs((actual - omitted) / actual))))

        certrows = read_csv(unit / "evidence/age_study/AGE_CERTIFICATES.csv")
        for name, rows in [("duplicate_case", certrows + [certrows[0]]),
                           ("negative_w1", copy.deepcopy(certrows)),
                           ("nonfinite_cdf", copy.deepcopy(certrows))]:
            if name == "negative_w1":
                rows[0]["w1"] = "-0.01"
            if name == "nonfinite_cdf":
                rows[0]["cdf_sup"] = "nan"
            path = out / (name + ".csv")
            write_csv(path, rows)
            try:
                plot.load_certificates(path)
                caught = False
            except ValueError:
                caught = True
            mutation("renderer_" + name, caught, detector="plot.load_certificates")

        for name, ratio in [("hidden_high_bar", 2.0), ("hidden_negative_bar", -0.1)]:
            rows = copy.deepcopy(all_bounds)
            row = next(r for r in rows if r["family"] == "AP" and r["resolution"] == "8" and r["measure"] == "survivor")
            row["discrete_mass_com3"] = str(float(row["exact_mass_com3"]) * ratio)
            write_csv(out / name / "evidence/age_study/AGE_SOURCE_MIXTURE_BOUNDS.csv", rows)
            plot.source_figure(out / name, out, [])
            fig = captured["BR04_SOURCE_AGE_BOUNDS"]
            ax = fig.axes[0]
            low, high = ax.get_ylim()
            caught = any(min(p.get_y(), p.get_y() + p.get_height()) < low
                         or max(p.get_y(), p.get_y() + p.get_height()) > high for p in ax.patches)
            mutation(name, caught, detector="independent artist extent audit",
                     renderer_rejected=False, injected_ratio=ratio)
            plot.plt.close(fig)

        native = json.loads((unit / "evidence/native_audit/crossed/TIME_AGE_ANALYSIS.json").read_text())
        for name, value in [("lost_negative_sign", "1e-12"), ("hidden_zero_log_point", "0")]:
            data = copy.deepcopy(native)
            data["fixed_r_time_slices"]["2"]["fields"]["photons_com3"]["changes"][0]["absolute"] = value
            target = out / name / "evidence/native_audit/crossed/TIME_AGE_ANALYSIS.json"
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(data))
            try:
                plot.native_figure(out / name, out, [])
                caught = False
            except ValueError:
                caught = True
            mutation(name, caught, detector="native signed-caption guard")
        data = copy.deepcopy(native)
        data["rectangles"]["N32_64_r2_4"]["final"]["q2"]["D_tr_over_time_difference_at_2r"] = "-10"
        target = out / "native_crop/evidence/native_audit/crossed/TIME_AGE_ANALYSIS.json"
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps(data))
        plot.native_figure(out / "native_crop", out, [])
        ax = captured["BR04_NATIVE_TIME_AGE"].axes[3]
        mutation("hidden_native_ratio", any(min(p.get_y(), p.get_y() + p.get_height()) < ax.get_ylim()[0]
                                              for p in ax.patches),
                 detector="independent artist extent audit", renderer_rejected=False, injected_value=-10)
    plot.plt.close("all")

    certs = {(r["family"], float(r["tau"]), int(r["nsteps"]), int(r["resolution"]), r["measure"]): r for r in certrows}
    node_rows = read_csv(unit / "evidence/age_study/AGE_ACTUAL_NODES.csv")
    for refinement in [1, 4, 16]:
        rows = [r for r in node_rows if r["family"] == "AP" and float(r["tau"]) == 93
                and int(r["nsteps"]) == 1 and int(r["resolution"]) == refinement]
        atoms = np.array(sorted((float(r["age"]), float(r["emitted_weight"])) for r in rows))
        optical_age = 93 * atoms[:, 0]
        weight = atoms[:, 1] * np.exp(-optical_age)
        cumulative = np.r_[0, np.cumsum(weight / weight.sum())]
        target = -np.expm1(-optical_age) / -np.expm1(-93.)
        ks = float(max(np.max(abs(cumulative[:-1] - target)), np.max(abs(cumulative[1:] - target))))
        visible = optical_age[optical_age <= 6]
        grid = np.linspace(0, 6, 3000)
        complete = np.unique(np.r_[grid, visible, np.nextafter(visible, -np.inf)])
        residual = cumulative[np.searchsorted(optical_age, complete, side="right")] + np.expm1(-complete) / -np.expm1(-93.)
        coarse = cumulative[np.searchsorted(optical_age, grid, side="right")] + np.expm1(-grid) / -np.expm1(-93.)
        tail = optical_age > 6
        tail_ks = float(max(np.max(abs(cumulative[:-1][tail] - target[tail])),
                            np.max(abs(cumulative[1:][tail] - target[tail])),
                            abs(cumulative[np.searchsorted(optical_age, 6, side="right")]
                                + math.expm1(-6) / -math.expm1(-93))))
        full, crop, tail_fraction = optical_w1_parts(rows)
        certificate = certs[("AP", 93., 1, refinement, "survivor")]
        error = abs(full - Decimal(certificate["w1"]) * 93)
        check("cdf_jumps_crop_r" + str(refinement), abs(ks - float(certificate["cdf_sup"])) < 1e-14
              and abs(ks - float(np.max(abs(residual)))) < 1e-14 and tail_ks < ks and error < Decimal("1e-13"),
              r=refinement, full_KS=ks, visible_KS=float(np.max(abs(residual))),
              tail_KS_after_y6=tail_ks, full_optical_W1=str(full), displayed_optical_W1=str(crop),
              tail_W1_fraction=str(tail_fraction), Decimal75_W1_minus_certificate_abs=str(error))
        mutation("omit_jump_side_samples_r" + str(refinement), float(np.max(abs(coarse))) < ks - 1e-7,
                 detector="node before/after supremum recomputation", underestimate=ks - float(np.max(abs(coarse))))
        wrong = np.r_[0, np.cumsum(atoms[:, 1] / atoms[:, 1].sum())]
        wrong_ks = float(max(np.max(abs(wrong[:-1] - target)), np.max(abs(wrong[1:] - target))))
        mutation("use_emitted_as_survivor_weights_r" + str(refinement), abs(wrong_ks - ks) > 0.1,
                 detector="survivor normalization and CDF check", wrong_KS=wrong_ks)

    with localcontext() as context:
        context.prec = 80
        d = Decimal
        final = {}
        for case in native["cases"]:
            ident = next(i for i in case["identity"] if i["path"].endswith(".csv"))
            path = resolve_native_csv(unit, ident["path"])
            check("native_csv_identity_" + case["name"], identity(path)["sha256"] == ident["sha256"])
            row = read_csv(path)[-1]
            final[(case["N_t"], case["r"])] = {
                "photons_com3": d(row["photons_com3"]),
                "mean_age_s": d(row["survivor_age_com_s"]) / d(row["photons_com3"]),
                "q2": d(row["q2"]),
            }
        expected, max_relative = [], d(0)
        for refinement in [2, 4]:
            series = native["fixed_r_time_slices"][str(refinement)]
            ns = series["N_t"]
            for field in ["photons_com3", "mean_age_s", "q2"]:
                for (low, high), change in zip(zip(ns, ns[1:]), series["fields"][field]["changes"]):
                    actual = final[(high, refinement)][field] - final[(low, refinement)][field]
                    max_relative = max(max_relative, abs((actual - d(change["absolute"])) / actual))
                    expected.append((field, refinement, low, high, float(actual)))
        points = read_csv(unit / "evidence/figures/NATIVE_PLOT_POINTS.csv")
        got = {(r["field"], int(r["r"]), int(r["N_coarse"]), int(r["N_fine"])):
               float(r["signed_time_difference"]) for r in points}
        check("native_plotted_differences_from_raw_rows", len(expected) == 15 and max_relative < d("1e-45")
              and all(got[r[:4]] == r[4] for r in expected), points=len(expected),
              max_decimal_relative_difference=str(max_relative), all_signed_negative=all(r[-1] < 0 for r in expected))
        ratios = []
        for n in [16, 32]:
            for field in ["mean_age_s", "q2"]:
                dt4 = final[(2 * n, 4)][field] - final[(n, 4)][field]
                dt2 = final[(2 * n, 2)][field] - final[(n, 2)][field]
                interaction = dt4 - dt2
                ratio = interaction / dt4
                stored = d(native["rectangles"][f"N{n}_{2*n}_r2_4"]["final"][field]["D_tr_over_time_difference_at_2r"])
                ratios.append({"N": n, "field": field, "D_tr": str(interaction),
                               "delta_t_r4": str(dt4), "ratio": str(ratio),
                               "relative_diff": str(abs((ratio - stored) / ratio))})
        check("native_mixed_ratio_units_and_sign", all(d(r["relative_diff"]) < d("1e-44") for r in ratios), ratios=ratios)
        mutation("native_sign_erasure_in_raw_point_file", any(abs(v) != v for v in got.values()),
                 detector="direct signed finite-difference reconstruction")
        wrong = final[(32, 2)]["photons_com3"] - d("1.00111686436201655e-8")
        correct = final[(32, 2)]["photons_com3"] - final[(16, 2)]["photons_com3"]
        mutation("misuse_frozen_reference_as_native_error", wrong != correct, detector="raw-grid difference definition",
                 wrong_reference_difference=str(wrong), correct_time_difference=str(correct))

    source_rows = read_csv(unit / "evidence/age_study/AGE_SOURCE_CERTIFICATES.csv")
    reconstructed = []
    for row in all_bounds:
        if row["measure"] != "survivor":
            continue
        selected = [r for r in source_rows if r["family"] == row["family"]
                    and r["resolution"] == row["resolution"] and r["measure"] == "survivor"]
        exact = math.fsum(float(r["exact_mass_com3"]) for r in selected)
        discrete = math.fsum(float(r["discrete_mass_com3"]) for r in selected)
        p = np.array([float(r["exact_mass_com3"]) / exact for r in selected])
        q = np.array([float(r["discrete_mass_com3"]) / discrete for r in selected])
        tv = 0.5 * math.fsum(abs(p - q))
        ks = math.fsum(p * np.array([float(r["cdf_sup"]) for r in selected]))
        w1 = math.fsum(p * np.array([float(r["w1"]) for r in selected]))
        mean = (math.fsum(q * np.array([float(r["discrete_mean"]) for r in selected]))
                - math.fsum(p * np.array([float(r["exact_mean"]) for r in selected])))
        unweighted = math.fsum(float(r["w1"]) for r in selected) / len(selected)
        errors = [abs(ks + tv - float(row["mixture_cdf_upper_bound"])),
                  abs(w1 + tv - float(row["mixture_w1_upper_bound"])),
                  abs(mean - float(row["mixture_mean_defect"]))]
        reconstructed.append({"family": row["family"], "r": int(row["resolution"]), "labels": len(selected),
                              "cdf_bound": ks + tv, "w1_bound": w1 + tv, "mean_defect": mean,
                              "max_abs_reconstruction_error": max(errors), "unweighted_w1": unweighted})
        if row["family"] == "AP":
            mutation("equal_label_weights_AP" + row["resolution"], abs(unweighted - w1) > 1e-7,
                     detector="exact label mass weighting reconstruction", wrong_w1=unweighted, correct_w1=w1)
    check("source_bounds_rebuilt_from_384_labels", all(r["labels"] == 384
          and r["max_abs_reconstruction_error"] < 1e-14 for r in reconstructed), rows=reconstructed)
    gl2 = next(r for r in all_bounds if r["family"] == "GL" and r["resolution"] == "2" and r["measure"] == "survivor")
    check("source_bound_not_exact_mixture_distance",
          all(float(r["mixture_cdf_upper_bound"]) >= float(r["exact_weighted_cdf_sup"]) for r in all_bounds),
          GL2_raw_bound=float(gl2["mixture_cdf_upper_bound"]), plotted_shape_families=["AP"])
    report["technical_checks_pass"] = all(r["pass"] for r in report["checks"])
    report["all_mutations_caught"] = all(r["caught"] for r in report["mutations"])
    report["mutation_count"] = len(report["mutations"])
    report["print_scope"] = {"182mm": "MINOR_REVISE", "90mm": "NOT_QUALIFIED",
                             "reason": "Reduced font sizes are recorded; no journal-print claim is made."}
    report["harness_identity"] = identity(Path(__file__))
    report["completed_utc"] = datetime.now(timezone.utc).isoformat()
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run(args.root.resolve())
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end="")
    if not (report["technical_checks_pass"] and report["all_mutations_caught"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
