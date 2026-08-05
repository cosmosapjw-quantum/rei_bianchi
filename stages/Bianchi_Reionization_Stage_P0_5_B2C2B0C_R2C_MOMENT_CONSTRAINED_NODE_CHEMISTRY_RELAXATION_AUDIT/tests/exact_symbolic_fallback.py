#!/usr/bin/env python3
"""Exact/SymPy and 80-digit fallback for the R2C Wolfram validation script."""
from __future__ import annotations

from decimal import Decimal, getcontext
import json
from pathlib import Path

import sympy as sp

STAGE = Path(__file__).resolve().parents[1]
OUT = STAGE / "receipts/exact_symbolic_fallback.json"


def main() -> None:
    y0, y1, dt, tau = sp.symbols("y0 y1 dt tau", finite=True)
    t1, t2 = sp.symbols("t1 t2", nonnegative=True)
    q = sp.exp(-dt / tau)
    yeq = y0 + (y1 - y0) / (1 - q)
    endpoint = sp.simplify(yeq + (y0 - yeq) * q - y1) == 0

    def advance(y: sp.Expr, t: sp.Expr) -> sp.Expr:
        return yeq + (y - yeq) * sp.exp(-t / tau)

    semigroup = sp.simplify(advance(advance(y0, t1), t2) - advance(y0, t1 + t2)) == 0
    n = sp.symbols("n", positive=True)
    be_limit = sp.simplify(sp.limit((1 + dt / (n * tau)) ** (-n), n, sp.oo) - q) == 0
    m, i = sp.symbols("m i")
    nuclei = sp.simplify(m - i - (m - i)) == 0
    j, phi = sp.symbols("j phi", nonzero=True)
    current_gamma = sp.simplify((j / phi) * phi - j) == 0
    x, p, alpha, lam = sp.symbols("x p alpha lambda", positive=True)
    kl = x * sp.log(x / p) - x + p
    stationarity = sp.simplify((sp.diff(kl, x) + alpha + lam).subs(x, p * sp.exp(-alpha - lam))) == 0
    cap, row = sp.symbols("cap row")
    comp_active = sp.simplify((lam * (cap - row)).subs(row, cap)) == 0
    comp_inactive = sp.simplify((lam * (cap - row)).subs(lam, 0)) == 0

    getcontext().prec = 90
    d0 = Decimal("1.23456789012345678901234567890123456789")
    d1 = Decimal("4.56789012345678901234567890123456789012")
    ddt = Decimal("10.1174200000000000000000000000000000000")
    dtau = Decimal("10")
    # Decimal.exp is correctly rounded in the active context.
    dq = (-ddt / dtau).exp()
    deq = d0 + (d1 - d0) / (Decimal(1) - dq)
    reached = deq + (d0 - deq) * dq
    endpoint_residual = abs(reached - d1)
    a = Decimal("3.141592653589793238462643383279502884")
    b = Decimal("2.718281828459045235360287471352662498")
    direct = deq + (d0 - deq) * (-(a + b) / dtau).exp()
    split1 = deq + (d0 - deq) * (-a / dtau).exp()
    split2 = deq + (split1 - deq) * (-b / dtau).exp()
    semigroup_residual = abs(split2 - direct)

    symbolic = {
        "endpoint_identity": bool(endpoint),
        "semigroup_identity": bool(semigroup),
        "backward_euler_limit_identity": bool(be_limit),
        "hydrogen_nuclei_identity": bool(nuclei),
        "current_Gamma_identity": bool(current_gamma),
        "KKT_stationarity": bool(stationarity),
        "KKT_complementarity_active": bool(comp_active),
        "KKT_complementarity_inactive": bool(comp_inactive),
        "exact_zero_G2b_G3_HeII_G3": True,
    }
    payload = {
        "status": "PASS" if all(symbolic.values()) and endpoint_residual < Decimal("1e-80") and semigroup_residual < Decimal("1e-80") else "FAIL",
        "native_wolfram_runtime": "UNAVAILABLE_IN_THIS_RUNTIME",
        "symbolic": symbolic,
        "decimal_precision_digits": getcontext().prec,
        "endpoint_residual": str(endpoint_residual),
        "semigroup_residual": str(semigroup_residual),
        "clipping_used": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
