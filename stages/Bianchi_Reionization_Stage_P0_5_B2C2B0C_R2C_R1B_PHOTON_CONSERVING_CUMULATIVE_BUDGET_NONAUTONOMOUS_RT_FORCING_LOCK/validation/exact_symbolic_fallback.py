#!/usr/bin/env python3
"""Independent exact/high-precision fallback for the R2C-R1B proof gates."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

import mpmath as mp
import sympy as sp


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    u, r, n_hi, n_hii = sp.symbols("u r n_hi n_hii", nonnegative=True)
    A = sp.Matrix([[-u, r], [u, -r]])
    s = sp.symbols("s", real=True)
    g = s * (1 - s) * (s - sp.Rational(1, 2))
    f = s * (1 - s)

    K = 8
    temporal_matrix = sp.zeros(3, K)
    temporal_matrix[0, 0] = 1
    temporal_matrix[1, K - 1] = 1
    for q in range(K):
        temporal_matrix[2, q] = sp.Rational(1, 2) if q in (0, K - 1) else 1

    N, KK = 3, 4
    spatial_rows = []
    for i in range(N):
        row0 = [0] * (N * KK)
        row1 = [0] * (N * KK)
        row0[i * KK] = 1
        row1[i * KK + KK - 1] = 1
        spatial_rows.extend([row0, row1])
    for q in range(KK):
        row = [0] * (N * KK)
        for i in range(N):
            row[i * KK + q] = 1
        spatial_rows.append(row)
    spatial_matrix = sp.Matrix(spatial_rows)

    mp.mp.dps = 100
    u0, r0, tau = mp.mpf("0.37"), mp.mpf("0.19"), mp.mpf("3.7")
    A_mp = mp.matrix([[-u0, r0], [u0, -r0]])
    semigroup = mp.expm(A_mp * tau)
    col_resid = max(abs(semigroup[0, j] + semigroup[1, j] - 1) for j in range(2))
    min_semigroup = min(semigroup[i, j] for i in range(2) for j in range(2))

    plugin_ratio = mp.mpf(
        "2.7011780329190638961347262305571454866594701712624220962721031504178895348425808"
    )
    fallback_ratio = mp.gamma(4) * mp.zeta(4) / (mp.gamma(3) * mp.zeta(3))

    result = {
        "classification": "R2C_R1B_EXACT_SYMBOLIC_AND_100_DPS_FALLBACK",
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "symbolic": {
            "column_sums": [str(v) for v in (sp.ones(1, 2) * A)],
            "boundary_HI_derivative": str((A * sp.Matrix([0, n_hii]))[0]),
            "boundary_HII_derivative": str((A * sp.Matrix([n_hi, 0]))[1]),
            "temporal_null_endpoints_and_integral": [
                str(g.subs(s, 0)),
                str(g.subs(s, 1)),
                str(sp.integrate(g, (s, 0, 1))),
            ],
            "spatial_partition_endpoints_and_integral": [
                str(f.subs(s, 0)),
                str(f.subs(s, 1)),
                str(sp.integrate(f, (s, 0, 1))),
            ],
            "temporal_K8_rank": int(temporal_matrix.rank()),
            "temporal_K8_nullity": K - int(temporal_matrix.rank()),
            "spatial_N3_K4_rank": int(spatial_matrix.rank()),
            "spatial_N3_K4_nullity": N * KK - int(spatial_matrix.rank()),
        },
        "high_precision": {
            "dps": mp.mp.dps,
            "semigroup_min_entry": mp.nstr(min_semigroup, 90),
            "semigroup_column_sum_residual_max": mp.nstr(col_resid, 90),
            "blackbody_mean_energy_ratio_fallback": mp.nstr(fallback_ratio, 90),
            "blackbody_mean_energy_ratio_plugin": mp.nstr(plugin_ratio, 90),
            "blackbody_ratio_relative_residual": mp.nstr(
                abs(fallback_ratio - plugin_ratio) / abs(fallback_ratio), 90
            ),
        },
        "pass": bool(
            temporal_matrix.rank() == 3
            and spatial_matrix.rank() == 8
            and min_semigroup >= 0
            and col_resid < mp.mpf("1e-90")
            and abs(fallback_ratio - plugin_ratio) / abs(fallback_ratio) < mp.mpf("1e-79")
        ),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
