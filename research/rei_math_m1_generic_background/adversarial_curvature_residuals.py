#!/usr/bin/env python3
"""Deterministic adversarial residual samples for the M1 curvature oracle.

Class-A samples are negative controls for an a-n cross-term sign mutation.
Class-B samples satisfy n^{ab} a_b = 0 and are positive controls: reversing
only the mixed epsilon*n*a term must become visible while the correct formula
continues to agree exactly with the connection-derived Ricci tensor.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import sympy as sp


MODULE_PATH = Path(__file__).with_name("derive_spatial_curvature.py")
SPEC = importlib.util.spec_from_file_location("rei_m1_curvature", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("M1_CURVATURE_MODULE_SPEC_UNAVAILABLE")
CURVATURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CURVATURE)


def sample_definitions() -> list[dict[str, Any]]:
    return [
        {
            "label": "A_diag",
            "class": "A",
            "a": (0, 0, 0),
            "n": ((1, 0, 0), (0, 2, 0), (0, 0, 3)),
        },
        {
            "label": "A_full",
            "class": "A",
            "a": (0, 0, 0),
            "n": ((0, 1, 2), (1, -1, 1), (2, 1, 0)),
        },
        {
            "label": "A_IX",
            "class": "A",
            "a": (0, 0, 0),
            "n": ((2, 0, 0), (0, 2, 0), (0, 0, 2)),
        },
        {
            "label": "A_VI0",
            "class": "A",
            "a": (0, 0, 0),
            "n": ((0, 0, 0), (0, 2, 0), (0, 0, -1)),
        },
        {
            "label": "B_x1",
            "class": "B",
            "a": (1, 0, 0),
            "n": ((0, 0, 0), (0, 2, 1), (0, 1, -1)),
        },
        {
            "label": "B_x2",
            "class": "B",
            "a": (2, 0, 0),
            "n": ((0, 0, 0), (0, 1, 2), (0, 2, 3)),
        },
        {
            "label": "B_y",
            "class": "B",
            "a": (0, 2, 0),
            "n": ((1, 0, 2), (0, 0, 0), (2, 0, -1)),
        },
        {
            "label": "B_z",
            "class": "B",
            "a": (0, 0, -1),
            "n": ((3, -2, 0), (-2, 1, 0), (0, 0, 0)),
        },
    ]


def _substitutions(data: dict[str, Any], sample: dict[str, Any]) -> dict[sp.Symbol, sp.Expr]:
    a: sp.Matrix = data["a"]
    n: sp.Matrix = data["n"]
    result: dict[sp.Symbol, sp.Expr] = {
        a[i]: sp.Integer(sample["a"][i]) for i in range(3)
    }
    for i in range(3):
        for j in range(i, 3):
            result[n[i, j]] = sp.Integer(sample["n"][i][j])
    return result


def _mutated_candidate_ricci(a: sp.Matrix, n: sp.Matrix) -> sp.Matrix:
    candidate = CURVATURE._candidate_ricci(a, n)

    def unsigned_mixed(i: int, j: int) -> sp.Expr:
        first = sum(
            sp.LeviCivita(c, d, i) * n[j, c] * a[d]
            for c in range(3)
            for d in range(3)
        )
        second = sum(
            sp.LeviCivita(c, d, j) * n[i, c] * a[d]
            for c in range(3)
            for d in range(3)
        )
        return sp.expand(first + second)

    # Correct mixed term is -(first+second); sign mutation makes it +(first+second).
    return sp.Matrix(
        3,
        3,
        lambda i, j: sp.expand(candidate[i, j] + 2 * unsigned_mixed(i, j)),
    )


def _max_abs(matrix: sp.Matrix, substitutions: dict[sp.Symbol, sp.Expr]) -> float:
    values = [sp.simplify(entry.subs(substitutions)) for entry in matrix]
    return max((abs(float(sp.N(value, 40))) for value in values), default=0.0)


def generate_records() -> list[dict[str, Any]]:
    data = CURVATURE._derived_objects()
    direct: sp.Matrix = data["ricci"]
    correct: sp.Matrix = data["candidate_ricci"]
    mutated = _mutated_candidate_ricci(data["a"], data["n"])
    jacobi = sp.Matrix(data["jacobi"])

    records: list[dict[str, Any]] = []
    for ordinal, sample in enumerate(sample_definitions(), start=1):
        substitutions = _substitutions(data, sample)
        records.append(
            {
                "ordinal": ordinal,
                "label": sample["label"],
                "class": sample["class"],
                "jacobi_residual_max": _max_abs(jacobi, substitutions),
                "correct_ricci_residual_max": _max_abs(
                    direct - correct, substitutions
                ),
                "mixed_sign_mutation_residual_max": _max_abs(
                    direct - mutated, substitutions
                ),
            }
        )
    return records


def write_outputs(output_dir: Path) -> dict[str, Any]:
    output = output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    records = generate_records()
    csv_path = output / "spatial_curvature_adversarial_residuals.csv"
    svg_path = output / "spatial_curvature_adversarial_residuals.svg"
    json_path = output / "spatial_curvature_adversarial_summary.json"

    fieldnames = list(records[0])
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    floor = 1.0e-30
    indices = [record["ordinal"] for record in records]
    correct = [
        max(record["correct_ricci_residual_max"], floor) for record in records
    ]
    mutated = [
        max(record["mixed_sign_mutation_residual_max"], floor)
        for record in records
    ]

    figure, axis = plt.subplots(figsize=(8.2, 4.8))
    axis.semilogy(indices, correct, marker="o", label="locked formula residual")
    axis.semilogy(indices, mutated, marker="s", label="mixed-term sign mutation")
    axis.axvline(4.5, linestyle="--", linewidth=1.0)
    axis.text(2.5, 2.0e-29, "Class A controls", ha="center")
    axis.text(6.5, 2.0e-29, "Class B adversarial samples", ha="center")
    axis.set_xticks(indices, [record["label"] for record in records], rotation=25)
    axis.set_xlabel("Jacobi-admissible deterministic sample")
    axis.set_ylabel("maximum absolute Ricci residual")
    axis.set_title("Generic Bianchi spatial-curvature sign-mutation audit")
    axis.legend()
    axis.grid(True, which="both", linewidth=0.5)
    figure.tight_layout()
    figure.savefig(svg_path, format="svg")
    plt.close(figure)

    summary = {
        "schema": "rei-math-m1-spatial-curvature-adversarial-summary/v1",
        "samples": len(records),
        "correct_formula_exact_zero_count": sum(
            record["correct_ricci_residual_max"] == 0.0 for record in records
        ),
        "jacobi_exact_zero_count": sum(
            record["jacobi_residual_max"] == 0.0 for record in records
        ),
        "class_a_mutation_zero_count": sum(
            record["class"] == "A"
            and record["mixed_sign_mutation_residual_max"] == 0.0
            for record in records
        ),
        "class_b_mutation_detected_count": sum(
            record["class"] == "B"
            and record["mixed_sign_mutation_residual_max"] > 0.0
            for record in records
        ),
        "claim": "SIGN_MUTATION_DETECTED_ONLY_WHERE_MIXED_A_N_CHANNEL_IS_ACTIVE",
        "authority_effect": "NUMERICAL_ADVERSARIAL_REGRESSION_ONLY",
        "native_runtime": "NOT_RUN",
    }
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "csv": str(csv_path),
        "svg": str(svg_path),
        "summary": str(json_path),
        **summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    options = parser.parse_args()
    result = write_outputs(options.output_dir)
    print(json.dumps(result, sort_keys=True))
    return 0 if (
        result["correct_formula_exact_zero_count"] == result["samples"]
        and result["jacobi_exact_zero_count"] == result["samples"]
        and result["class_a_mutation_zero_count"] == 4
        and result["class_b_mutation_detected_count"] == 4
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
