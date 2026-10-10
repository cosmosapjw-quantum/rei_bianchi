#!/usr/bin/env python3
"""Independent PHYS21 second-order checks; stdlib only, no gas/native IVP.

Exact Fraction coefficient expansion uses a degree-four spherical cubature.
Decimal finite-amplitude evaluation uses the same bounded analytic diagnostics,
with composite Boole time integration and a fourth-order central extrapolation.
The epsilon^2 coefficient, not the second derivative, is reported throughout.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import platform
import time

getcontext().prec = 80
D = Decimal


def fracstr(q):
    q = F(q)
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def dec(q):
    q = F(q)
    return D(q.numerator) / D(q.denominator)


def padd(a, b):
    return tuple((a[i] if i < len(a) else F(0)) +
                 (b[i] if i < len(b) else F(0))
                 for i in range(max(len(a), len(b))))


def pscale(a, c):
    return tuple(F(c) * x for x in a)


def pmul(a, b):
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x * y
    return tuple(out)


def pint(a):
    return sum((x / (i+1) for i, x in enumerate(a)), F(0))


def peval(a, x):
    val = x * 0
    for q in reversed(a):
        val = val * x + (dec(q) if isinstance(x, Decimal) else q)
    return val


def dot(a, b):
    return sum((x*y for x, y in zip(a,b)), a[0]*0)


def tr2(a):
    return dot(a,a)


# Four squared-direction classes represent 6 axial rays (each weight 1/15)
# and 8 cube-vertex rays (each weight 3/40). Fixed diagonal tensors depend
# only on direction squares, so the signs can be exactly grouped.
CUBATURE = [
    ((F(1), F(0), F(0)), F(2,15)),
    ((F(0), F(1), F(0)), F(2,15)),
    ((F(0), F(0), F(1)), F(2,15)),
    ((F(1,3), F(1,3), F(1,3)), F(3,5)),
]


def angular_average(fn):
    return sum((w * fn(n2) for n2,w in CUBATURE), F(0))


S = (F(1), F(-1), F(0))
T = (F(1,3), F(1,6), F(-1,2))
BC = (F(2,5), F(-1,3), F(-1,15))


def shape(slope, curve=(F(0),)*3):
    return tuple((F(0),s,c) for s,c in zip(slope,curve))


CASES = [
    {"name":"inverse_cube_absorption_tau_quarter", "A":shape(S),
     "kappa":(F(1,4),), "p":F(-3), "terminal":[(F(1,4),F(-3))]},
    {"name":"inverse_cube_absorption_tau_eight", "A":shape(S),
     "kappa":(F(8),), "p":F(-3), "terminal":[(F(8),F(-3))]},
    {"name":"inverse_cube_heating_eta_half_tau_quarter", "A":shape(S),
     "kappa":(F(1,4),), "p":F(-3),
     "terminal":[(F(1,4),F(-2)),(F(-1,8),F(-3))]},
    {"name":"inverse_cube_heating_eta_half_tau_four", "A":shape(S),
     "kappa":(F(4),), "p":F(-3),
     "terminal":[(F(4),F(-2)),(F(-2),F(-3))]},
    {"name":"changing_diagonal_shape_and_time_varying_opacity", "A":shape(S,T),
     "kappa":(F(1,5),F(1,10)), "p":F(2),
     "terminal":[(F(7,5),F(-1)),(F(2,7),F(3))]},
]


def terminal_derivatives(case):
    return tuple(sum((c * r**k for c,r in case["terminal"]), F(0)) for k in range(3))


def exact_directional_coefficient(case, n2):
    A,kap,p = case["A"],case["kappa"],case["p"]
    a = (F(0),)
    y = (F(0),)
    for weight,ai in zip(n2,A):
        a = padd(a,pscale(ai,weight))
        y = padd(y,pscale(pmul(ai,ai),weight))
    theta1 = -p * pint(pmul(kap,a))
    theta2 = pint(pmul(kap,padd(pscale(y,p),pscale(pmul(a,a),p*(p-2)/2))))
    at,yt = peval(a,F(1)),peval(y,F(1))
    l0,lD,lDD=terminal_derivatives(case)
    l1=-lD*at
    l2=lD*yt+(lDD-2*lD)*at*at/2
    return l2-l1*theta1+l0*(theta1*theta1/2-theta2)


def tensor_coefficient(case):
    A,kap,p = case["A"],case["kappa"],case["p"]
    At = tuple(peval(ai,F(1)) for ai in A)
    M = tuple(p*pint(pmul(kap,ai)) for ai in A)
    V = p*(p+3)*sum((pint(pmul(kap,pmul(ai,ai))) for ai in A),F(0))
    l0,lD,lDD = terminal_derivatives(case)
    return ((lDD+3*lD)*tr2(At)-2*lD*dot(At,M)+l0*tr2(M)-l0*V)/15


def boole_integrate(fn, blocks):
    h=D(1)/D(4*blocks)
    weights=(D(7),D(32),D(12),D(32),D(7))
    total=D(0)
    for block in range(blocks):
        start=4*block
        total += sum((w*fn(D(start+j)*h) for j,w in enumerate(weights)),D(0))
    return total*D(2)*h/D(45)


def numeric_scalar(case, epsilon, blocks, representation):
    A,kap,p=case["A"],case["kappa"],int(case["p"])
    scalar=D(0)
    for n2,weight in CUBATURE:
        squares=tuple(dec(x) for x in n2)
        if representation=="physical_birth":
            denominator=D(1)
            source_j=D(1)
        elif representation=="fixed_q_with_Jb":
            denominator=sum((wi*(-D(2)*epsilon*dec(ci)).exp()
                             for wi,ci in zip(squares,BC)),D(0))
            source_j=D(1)/(denominator*denominator.sqrt())
        else:
            raise ValueError(representation)

        def ratio(x):
            coeff=tuple(peval(ai,x) for ai in A)
            if representation=="fixed_q_with_Jb":
                coeff=tuple(ai+dec(ci) for ai,ci in zip(coeff,BC))
            numerator=sum((wi*(-D(2)*epsilon*ai).exp()
                           for wi,ai in zip(squares,coeff)),D(0))
            return (numerator/denominator).sqrt()

        theta=boole_integrate(lambda x: peval(kap,x)*ratio(x)**p,blocks)
        rt=ratio(D(1))
        terminal=sum((dec(c)*rt**int(r) for c,r in case["terminal"]),D(0))
        scalar += dec(weight)*source_j*(-theta).exp()*terminal
    return scalar


def numeric_normalized_coefficient(case, epsilon, blocks, representation):
    l0=terminal_derivatives(case)[0]
    k0=(-dec(pint(case["kappa"]))).exp()*dec(l0)
    plus=numeric_scalar(case,epsilon,blocks,representation)
    minus=numeric_scalar(case,-epsilon,blocks,representation)
    return (plus+minus-D(2)*k0)/(D(2)*epsilon*epsilon*k0)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    start=time.perf_counter()
    checks=[]

    def check(name,condition,**details):
        checks.append({"name":name,"status":"PASS" if condition else "FAIL",**details})

    check("cubature_total_weight",sum((w for _,w in CUBATURE),F(0))==1)
    for i in range(3):
        q2=angular_average(lambda n:n[i])
        check(f"new_second_order_moment_Q2_{i}",q2==F(1,3),value=fracstr(q2))
        for j in range(i,3):
            q4=angular_average(lambda n:n[i]*n[j])
            target=F(1,5) if i==j else F(1,15)
            check(f"new_second_order_moment_Q4_{i}_{j}",q4==target,value=fracstr(q4))

    exact_results=[]
    for case in CASES:
        directional=angular_average(lambda n:exact_directional_coefficient(case,n))
        tensor=tensor_coefficient(case)
        l0,lD,lDD=terminal_derivatives(case)
        relative=tensor/l0
        check(f"tensor_vs_polynomial_{case['name']}",directional==tensor,
              tensor_P0_factored=fracstr(tensor),direct_P0_factored=fracstr(directional),
              normalized_epsilon2_coefficient=fracstr(relative))
        # Fixed-q second-order covariance and Jacobian terms must cancel
        # after exact Q2/Q4 integration. X is traceless.
        At=tuple(peval(ai,F(1)) for ai in case["A"])
        M=tuple(case["p"]*pint(pmul(case["kappa"],ai)) for ai in case["A"])
        X=tuple(lD*aa-l0*mm for aa,mm in zip(At,M))
        coordinate_difference=angular_average(lambda n:
            4*sum((n[i]*BC[i]*X[i] for i in range(3)),F(0))
            -10*dot(n,BC)*dot(n,X)
            +l0*(15*dot(n,BC)**2-6*sum((n[i]*BC[i]**2 for i in range(3)),F(0))))
        check(f"fixed_q_Jb_covariance_cancellation_{case['name']}",coordinate_difference==0,
              averaged_second_derivative_difference_P0_factored=fracstr(coordinate_difference))
        exact_results.append({"case":case["name"],"baseline_optical_depth":fracstr(pint(case["kappa"])),
                              "normalized_epsilon2_coefficient":fracstr(relative),
                              "normalized_second_derivative":fracstr(2*relative)})

    numerical=[]
    tolerance=D("1e-12")
    eps=D("1e-4")
    for case in CASES:
        target=dec(tensor_coefficient(case)/terminal_derivatives(case)[0])
        for representation in ("physical_birth","fixed_q_with_Jb"):
            coarse=numeric_normalized_coefficient(case,eps,8,representation)
            fine=numeric_normalized_coefficient(case,eps/2,8,representation)
            extrapolated=(D(4)*fine-coarse)/D(3)
            cross=numeric_normalized_coefficient(case,eps/2,16,representation)
            error=abs(extrapolated-target)
            integration_difference=abs(cross-fine)
            check(f"finite_amplitude_second_order_{case['name']}_{representation}",error<tolerance,
                  absolute_error=str(error),tolerance=str(tolerance))
            check(f"boole_resolution_{case['name']}_{representation}",integration_difference<tolerance,
                  normalized_coefficient_difference=str(integration_difference),tolerance=str(tolerance))
            numerical.append({"case":case["name"],"representation":representation,
                              "epsilon":str(eps),"epsilon_half":str(eps/2),
                              "time_boole_blocks":8,"cross_blocks":16,
                              "coefficient_epsilon":str(coarse),"coefficient_epsilon_half":str(fine),
                              "richardson_epsilon2_coefficient":str(extrapolated),
                              "analytic_coefficient":str(target),"absolute_error":str(error),
                              "integration_difference":str(integration_difference)})

    expected={
        "inverse_cube_absorption_tau_quarter":F(-9,32),
        "inverse_cube_absorption_tau_eight":F(48,5),
        "inverse_cube_heating_eta_half_tau_quarter":F(-59,96),
        "inverse_cube_heating_eta_half_tau_four":F(8,3),
    }
    for case in CASES:
        if case["name"] in expected:
            computed=tensor_coefficient(case)/terminal_derivatives(case)[0]
            check(f"analytic_sign_case_{case['name']}",computed==expected[case["name"]],
                  coefficient=fracstr(computed))

    result={
        "schema":"rei.phys21.independent_second_order_checks.v1",
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "evidence_status":["derived","numerically checked"],
        "scope":"Fixed gas analytic diagnostics. No FT03 evolving-gas/native history or physical admission.",
        "coordinate_convention":"Isotropic physical birth directions. beta=epsilon B; fixed principal axes.",
        "normalization":"All reported coefficients multiply epsilon^2; the second derivative is twice the coefficient.",
        "units":"Dimensionless x=(s-b)/T; kappa=T*lambda0. E0 is one energy unit; heating chi/E0=1/2.",
        "method":"Exact Fraction polynomial integration and degree-four spherical cubature; Decimal80 finite-amplitude kernels, composite Boole, centered Richardson extrapolation.",
        "limitations":["Four direction-square classes group a 14-ray cubature; exact Q2/Q4 does not imply exact finite-amplitude angular integration.",
                       "Boole resolution comparison is numerical evidence, not a rigorous quadrature enclosure.",
                       "The H=0, power-law opacity cases are analytic diagnostics, not self-consistent Einstein or production FT03 runs.",
                       "Native midpoint source/defaults were not modified."],
        "python":platform.python_version(),"decimal_precision":getcontext().prec,
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "exact_results":exact_results,"numerical_results":numerical,"checks":checks,
        "summary":{"passed":sum(c["status"]=="PASS" for c in checks),"total":len(checks),
                   "failed":sum(c["status"]=="FAIL" for c in checks),
                   "max_finite_amplitude_error":str(max(D(r["absolute_error"]) for r in numerical)),
                   "max_boole_resolution_difference":str(max(D(r["integration_difference"]) for r in numerical)),
                   "wall_seconds":time.perf_counter()-start},
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result["summary"],ensure_ascii=False))
    raise SystemExit(1 if result["summary"]["failed"] else 0)


if __name__=="__main__":
    main()
