#!/usr/bin/env python3
"""Produce source-bound exact angular certificates and bounded diagnostics."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/"src"))
from wu088_hh.phys67_angular_certificate import (
    exact_gauss_error_bound, json_safe, make_angular_certificate,
)


def independent_physical_checks() -> dict:
    """High-precision direct angular integral versus a different GL path.

    These finite numerical witnesses test the formula and normalization.
    The proof, rather than numerical self-agreement, certifies the bound.
    """
    import mpmath as mp
    import numpy as np
    import sympy as sp
    from wu088_hh.phys63_scaled_riccati import AngularScreen

    rows = []
    x = sp.Symbol("x")
    with mp.workdps(90):
        nodes, weights = mp.gauss_quadrature(12,"legendre")
        epsilon = exact_gauss_error_bound(4,12)
        eps_mp = mp.mpf(epsilon.numerator)/epsilon.denominator
        for radius in (27,39):
            r = mp.mpf(radius)
            sep = mp.mpf(7)/10
            screen = lambda z: 2*(1+1/mp.sqrt(r*r+sep*sep-2*r*sep*z))*mp.exp(
                -2*mp.sqrt(r*r+sep*sep-2*r*sep*z))
            for m in (0,1,4):
                ells = tuple(range(m,5))
                basis = []
                for ell in ells:
                    poly = sp.Poly(sp.diff(sp.legendre(ell,x),x,m),x)
                    coeffs = [mp.mpf(int(c.p))/int(c.q) for c in poly.all_coeffs()]
                    norm = (-1)**m*mp.sqrt(mp.mpf(2*ell+1)/2
                           *mp.factorial(ell-m)/mp.factorial(ell+m))
                    def fn(z, coeffs=coeffs, norm=norm, m=m):
                        return norm*(1-z*z)**(mp.mpf(m)/2)*mp.polyval(coeffs,z)
                    basis.append(fn)
                n = len(ells)
                error = mp.matrix(n)
                gram = mp.matrix(n)
                for i in range(n):
                    for j in range(i,n):
                        f = lambda z: basis[i](z)*basis[j](z)*screen(z)
                        direct = mp.quad(f,[-1,0,1])
                        gauss = mp.fsum(weights[q]*f(nodes[q]) for q in range(12))
                        err = gauss-direct
                        error[i,j] = error[j,i] = err
                        gram[i,j] = gram[j,i] = mp.fsum(
                            weights[q]*basis[i](nodes[q])*basis[j](nodes[q])
                            for q in range(12))-int(i==j)
                residual = max(abs(t) for t in mp.eigsy(error,eigvals_only=True))
                gram_residual = max(abs(t) for t in mp.eigsy(gram,eigvals_only=True))
                bound = eps_mp*mp.exp(-2*(r-27))
                if not residual < bound:
                    raise ArithmeticError("independent finite angular witness exceeds analytic bound")
                rows.append({
                    "r_atomic":radius,"L":4,"m":m,"equivalent_signed_m":[-m,m] if m else [0],
                    "Q":12,"dps":90,
                    "direct_integral_vs_GL_operator_norm":mp.nstr(residual,35),
                    "analytic_quadrature_bound":mp.nstr(bound,35),
                    "residual_over_bound":mp.nstr(residual/bound,25),
                    "highprecision_discrete_Gram_defect":mp.nstr(gram_residual,25),
                    "bound_comparison":True,
                    "numerical_witness_is_not_interval_certification":True,
                })
    floating = []
    for m in (0,1,32,64):
        a = AngularScreen(tuple(range(m,65)),m,128)
        gram = (a.basis*a.weights[None,:])@a.basis.T
        floating.append({
            "L":64,"m":m,"Q":128,
            "actual_f64_Gram_defect_2norm":float(np.linalg.norm(gram-np.eye(65-m),2)),
            "meaning":"diagnostic effect of floating nodes/weights/basis; separate from ideal Gauss truncation",
            "roundoff_bound_certified":False,
        })
    return {"physical_highprecision_rows":rows,"floating_AngularScreen_rows":floating,
            "actual_radial_solver_runs":0,"actual_NCP_runs":0}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--independent-checks",action="store_true")
    args = parser.parse_args()
    t = perf_counter()
    table = [make_angular_certificate(args.source,L,Q)
             for L,Q in [(64,65),(64,80),(64,96),(64,128),(28,128),(64,192),(64,256),(64,512)]]
    files = [
        "src/wu088_hh/phys58_screen_multipoles.py",
        "src/wu088_hh/phys63_scaled_riccati.py",
        "src/wu088_hh/phys66_order_tail.py",
        "src/wu088_hh/phys67_angular_certificate.py",
        "tests/test_phys67_angular_certificate.py",
        "research/hh_phys67_20261019/angular/produce.py",
    ]
    out = {
        "schema":"PHYS67_ANGULAR_EXECUTED_RESULTS_V1",
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "python":platform.python_version(),
        "source_sha256":table[0]["source_sha256"],
        "file_sha256":{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
        "certificates":table,
        "independent_checks":independent_physical_checks() if args.independent_checks else None,
        "seconds":perf_counter()-t,
        "scientific_scope":"ideal angular quadrature for finite L, all signed m, every r>=27",
        "total_numerical_error_certified":False,
        "HH_R10":"OFF",
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(json_safe(out),indent=2)+"\n")
    print(json.dumps({
        "output":str(args.output),"source_sha256":out["source_sha256"],
        "L64_Q128_error_upper":table[3]["chebyshev_operator_error_decimal_upper"],
        "physical_witnesses":len(out["independent_checks"]["physical_highprecision_rows"]) if out["independent_checks"] else 0,
        "seconds":out["seconds"],"HH_R10":"OFF",
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
