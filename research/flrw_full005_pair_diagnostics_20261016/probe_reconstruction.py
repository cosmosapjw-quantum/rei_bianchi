#!/usr/bin/env python3
"""R7 synthetic-only PL probe; independent of the forthcoming production code.

Run from any directory with Python 3. Installed Matplotlib is used only to draw
the synthetic counterexample. No saved physical history is read or solver run.
The exact oracle integrates global linear polynomials using antiderivatives and
splits at their exact zero. It does not use the proposed endpoint formulas.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import platform
import resource
import sys
import time
from fractions import Fraction as F
from pathlib import Path


HERE = Path(__file__).resolve().parent
SUPPORT = HERE.parent / "flrw_full005_postprocess_20261015/vendor/reconstruction_support.py"


def interpolate(points, x):
    for (a, u), (b, v) in zip(points, points[1:]):
        if a <= x <= b:
            return u + (v - u) * (x - a) / (b - a)
    raise ValueError("query outside supplied common domain")


def polynomial_oracle(reference, candidate):
    """Exact rational polynomial antiderivatives; independent integral method."""
    knots = sorted({x for x, _ in reference} | {x for x, _ in candidate})
    l1 = F(0)
    squared = F(0)
    maximum = F(0)
    for a, b in zip(knots, knots[1:]):
        p = interpolate(candidate, a) - interpolate(reference, a)
        q = interpolate(candidate, b) - interpolate(reference, b)
        maximum = max(maximum, abs(p), abs(q))
        slope = (q - p) / (b - a)
        intercept = p - slope * a

        def primitive(x):
            return slope * x * x / 2 + intercept * x

        def square_primitive(x):
            return (slope * slope * x**3 / 3
                    + slope * intercept * x*x + intercept*intercept*x)

        split = [a, b]
        if slope:
            zero = -intercept / slope
            if a < zero < b:
                split.insert(1, zero)
        l1 += sum(abs(primitive(v) - primitive(u))
                  for u, v in zip(split, split[1:]))
        squared += square_primitive(b) - square_primitive(a)
    return {"sup": maximum, "l1": l1, "squared_integral": squared,
            "domain_length": knots[-1] - knots[0], "merged_knots": len(knots)}


def endpoint_formula(reference, candidate):
    """Prescribed endpoint formulas, using either Fraction or float inputs."""
    knots = sorted({x for x, _ in reference} | {x for x, _ in candidate})
    one = []
    two = []
    maximum = 0
    for a, b in zip(knots, knots[1:]):
        p = interpolate(candidate, a) - interpolate(reference, a)
        q = interpolate(candidate, b) - interpolate(reference, b)
        h = b - a
        maximum = max(maximum, abs(p), abs(q))
        two.append(h * (p*p + p*q + q*q) / 3)
        if p*q >= 0:
            one.append(h * (abs(p) + abs(q)) / 2)
        else:
            one.append(h * (p*p + q*q) / (2 * (abs(p) + abs(q))))
    exact = isinstance(knots[0], F)
    total_one = sum(one, F(0)) if exact else math.fsum(one)
    total_two = sum(two, F(0)) if exact else math.fsum(two)
    length = knots[-1] - knots[0]
    return {"sup": maximum, "l1": total_one, "squared_integral": total_two,
            "domain_length": length, "merged_knots": len(knots),
            "l2": math.sqrt(float(total_two)),
            "rms": math.sqrt(float(total_two / length))}


def fractions(knots, values):
    return [(F(str(x)), F(str(y))) for x, y in zip(knots, values)]


def summary(metrics):
    out = {}
    for key, value in metrics.items():
        out[key] = str(value) if isinstance(value, F) else value
    return out


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    sys.dont_write_bytecode = True  # Keep the reused read-only vendor path untouched.
    out = HERE / "probe"
    out.mkdir(exist_ok=True)
    spec = importlib.util.spec_from_file_location("existing_reconstruction_support", SUPPORT)
    support = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(support)
    fixtures = [
        ("identically_zero", fractions([0, 1], [0, 0]), fractions([0, 1], [0, 0])),
        ("same_sign", fractions([0, 1], [0, 0]), fractions([0, 1], [2, 4])),
        ("opposite_sign", fractions([0, 1], [0, 0]), fractions([0, 1], [-2, 1])),
        ("left_endpoint_zero", fractions([0, 1], [0, 0]), fractions([0, 1], [0, -3])),
        ("right_endpoint_zero", fractions([0, 1], [0, 0]), fractions([0, 1], [3, 0])),
        ("unequal_adaptive_grids", fractions([0, "0.2", "0.7", 1], [1, -1, 2, 0]),
         fractions([0, "0.1", "0.65", "0.9", 1], [-1, 2, -2, 1, 2])),
        ("identical_affine_unequal_grids", fractions([0, "0.3", 1], [-1, "-0.1", 2]),
         fractions([0, "0.2", "0.6", 1], [-1, "-0.4", "0.8", 2])),
        ("narrow_spike", fractions([0, 1], [0, 0]),
         fractions([0, "0.50025", "0.5005", "0.50075", 1], [0, 0, 1, 0, 0])),
    ]
    results = []
    for name, reference, candidate in fixtures:
        oracle = polynomial_oracle(reference, candidate)
        proposed = endpoint_formula(reference, candidate)
        for key in ("sup", "l1", "squared_integral", "domain_length", "merged_knots"):
            assert proposed[key] == oracle[key], (name, key, proposed[key], oracle[key])
        vendor = support.reconstruction_norm(reference, candidate, "LN_A")
        assert vendor["sup_absolute_difference"] == oracle["sup"], name
        # Preserve stored-binary64 interpretation separately from ideal decimal
        # fixture coordinates. Lift those exact float values for the oracle.
        float_reference = [(float(x), float(y)) for x, y in reference]
        float_candidate = [(float(x), float(y)) for x, y in candidate]
        lifted_reference = [(F.from_float(x), F.from_float(y)) for x, y in float_reference]
        lifted_candidate = [(F.from_float(x), F.from_float(y)) for x, y in float_candidate]
        dyadic_oracle = polynomial_oracle(lifted_reference, lifted_candidate)
        float_metrics = endpoint_formula(float_reference, float_candidate)
        dyadic_vendor = support.reconstruction_norm(float_reference, float_candidate, "LN_A")
        assert dyadic_vendor["sup_absolute_difference"] == dyadic_oracle["sup"], name
        numeric_truth = {key: float(dyadic_oracle[key])
                         for key in ("sup", "l1", "squared_integral")}
        numeric_truth["l2"] = math.sqrt(float(dyadic_oracle["squared_integral"]))
        numeric_truth["rms"] = math.sqrt(float(dyadic_oracle["squared_integral"] /
                                               dyadic_oracle["domain_length"]))
        residuals = {key: abs(float_metrics[key] - value) for key, value in numeric_truth.items()}
        record = {"name": name,
                  "reference_rational": [[str(x), str(y)] for x, y in reference],
                  "candidate_rational": [[str(x), str(y)] for x, y in candidate],
                  "rational_oracle": summary(oracle), "rational_endpoint_formula": summary(proposed),
                  "exact_antiderivative_formula_equal": True,
                  "existing_vendor_sup_equal_rational_and_dyadic": True,
                  "stored_binary64_oracle": summary(dyadic_oracle),
                  "binary64_endpoint_formula": float_metrics,
                  "binary64_absolute_residuals_against_dyadic_oracle": residuals}
        results.append(record)
        print(f"{name}: exact_integrals_equal; vendor_sup_equal; "
              f"sup={oracle['sup']} L1={oracle['l1']} I2={oracle['squared_integral']}; "
              f"binary64_residuals={json.dumps(residuals, sort_keys=True)}")

    _, reference, candidate = fixtures[-1]
    spike = results[-1]
    assert spike["rational_oracle"]["sup"] == "1"
    assert spike["rational_oracle"]["l1"] == "1/4000"
    assert spike["rational_oracle"]["squared_integral"] == "1/6000"
    sample_x = [j / 1000 for j in range(1001)]
    float_candidate = [(float(x), float(y)) for x, y in candidate]
    sample_y = [interpolate(float_candidate, x) for x in sample_x]
    rational_sample_y = [interpolate(candidate, F(j, 1000)) for j in range(1001)]
    assert max(map(abs, sample_y)) == 0
    assert max(map(abs, rational_sample_y)) == 0
    spike["uniform_samples"] = {"count": 1001, "coordinates": "j/1000, j=0,...,1000",
                                "binary64_max_absolute": max(map(abs, sample_y)),
                                "rational_max_absolute": str(max(map(abs, rational_sample_y))),
                                "all_samples_zero": True}

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
    ax.plot([float(x) for x, _ in candidate], [float(y) for _, y in candidate],
            color="#185f9c", linewidth=2.3, marker="o", markersize=5,
            label="Candidate PL difference; reference = 0")
    visible = [(x, y) for x, y in zip(sample_x, sample_y) if 0.4998 <= x <= 0.5012]
    ax.scatter([x for x, _ in visible], [y for _, y in visible], color="#c64d27",
               marker="x", s=90, linewidths=2.2, zorder=5,
               label="Uniform j/1000 samples (1001 in full domain)")
    ax.set(xlim=(0.4998, 0.5012), ylim=(-0.12, 1.25),
           xlabel="L (dimensionless synthetic coordinate)",
           ylabel="Reconstructed difference (dimensionless)",
           title="SYNTHETIC COUNTEREXAMPLE\nA narrow PL spike between uniform sample coordinates")
    ax.ticklabel_format(axis="x", style="plain", useOffset=False)
    ax.grid(alpha=0.2)
    ax.annotate("PL sup = 1 at L = 0.5005", xy=(0.5005, 1), xytext=(0.50065, 1.12),
                arrowprops={"arrowstyle": "->", "color": "#333333"}, fontsize=10)
    ax.text(0.02, 0.93, "All 1001 uniform samples = 0\nL1 = 1/4000; integral of difference² = 1/6000",
            transform=ax.transAxes, va="top", fontsize=10)
    ax.legend(loc="lower center", fontsize=8)
    image = out / "synthetic_sampling_gap.png"
    fig.savefig(image, dpi=160)
    plt.close(fig)

    max_residual = max(max(x["binary64_absolute_residuals_against_dyadic_oracle"].values())
                       for x in results)
    result = {"schema_version": 1, "workflow_version": "1.0.0",
              "unit_id": "flrw_full005_pair_diagnostics_20261016",
              "scope": "R7 synthetic mathematical probe only; no physical history reads or solver runs",
              "coordinate": "dimensionless synthetic L; integration measure dL",
              "command": "python3 research/flrw_full005_pair_diagnostics_20261016/probe_reconstruction.py",
              "execution_status": "completed", "exit_code_on_success": 0,
              "checks": {"fixture_count": len(results), "exact_integrals_and_vendor_sup": "pass_scoped",
                         "narrow_spike_uniform_sampling_gap": "pass_scoped",
                         "binary64_comparison": "measured residuals; no new production acceptance threshold",
                         "maximum_binary64_absolute_residual": max_residual},
              "oracle_method": "Exact Fraction global slope/intercept polynomial antiderivatives; split integral of absolute value at exact interior zero",
              "formula_method": "Prescribed merged-interval endpoint L1/I2 formulas; square roots for L2/RMS",
              "dependencies": {"python": platform.python_version(), "matplotlib": matplotlib.__version__,
                               "probe_sha256": sha(Path(__file__)), "vendor_sup_sha256": sha(SUPPORT)},
              "fixtures": results,
              "resources": {"native_solver_runs": 0, "physical_history_reads": 0,
                            "wall_seconds": time.perf_counter() - started_wall,
                            "cpu_seconds": time.process_time() - started_cpu,
                            "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},
              "artifacts": ["probe_reconstruction.py", "probe/RESULT.json", "probe/stdout.log",
                            "probe/synthetic_sampling_gap.png"]}
    (out / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("SYNTHETIC ONLY: all 1001 spike samples are zero; PL sup=1, L1=1/4000, I2=1/6000")
    print(f"RESULT {out / 'RESULT.json'}")
    print("RESOURCES " + json.dumps(result["resources"], sort_keys=True))


if __name__ == "__main__":
    main()
