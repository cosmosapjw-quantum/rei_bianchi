#!/usr/bin/env python3
"""Independent scalar/age checks for positive exponential-fitted birth panels.

No rei_bianchi Rust/Python implementation is imported.  Analytic scalar
references use Python Decimal at 90 decimal digits; candidate arithmetic is
ordinary binary64.  This is a frozen-opacity source-integral study, not a
thermochemical native evolution.
"""
from __future__ import annotations

import csv
from decimal import Decimal, localcontext
import json
import math
from pathlib import Path


def phi_decimal(tau: float) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = 90
        t = Decimal(str(tau))
        if not t:
            return Decimal(1)
        return +(Decimal(1) - (-t).exp()) / t


def age_moment_decimal(tau: float, order: int) -> Decimal:
    """Integral_0^1 x^order exp(-tau*x) dx / Phi(tau)."""
    with localcontext() as ctx:
        ctx.prec = 90
        t = Decimal(str(tau))
        if not t:
            return Decimal(1) / (order + 1)
        if t < 1:
            term = Decimal(1)
            integral = term / Decimal(order + 1)
            for k in range(1, 2000):
                term *= -t / Decimal(k)
                add = term / Decimal(order + k + 1)
                integral += add
                if abs(add) < Decimal("1e-86") * abs(integral):
                    break
            else:
                raise RuntimeError("reference series did not converge")
            return +(integral / phi_decimal(tau))
        ex = (-t).exp()
        p, partial = Decimal(1), Decimal(1)
        for k in range(1, order + 1):
            p *= t / Decimal(k)
            partial += p
        integral = Decimal(math.factorial(order)) * (1 - ex * partial) / t**(order + 1)
        return +(integral / phi_decimal(tau))


def acosh_sinhc(z: float) -> float:
    if z == 0.0:
        return 0.0
    if z < 0.125:
        # sinh(z)/z - 1, evaluated independently of exp-fit Rust code.
        zz = z*z
        term = zz/6.0
        delta = term
        for n in range(2, 15):
            term *= zz / ((2*n)*(2*n + 1))
            delta += term
        return math.log1p(delta + math.sqrt(delta*(delta + 2.0)))
    if z < 20.0:
        return math.acosh(math.sinh(z)/z)
    log_s = z + math.log1p(-math.exp(-2*z)) - math.log(2*z)
    return log_s + math.log1p(math.sqrt(-math.expm1(-2*log_s)))


def rule(tau: float, refinement: int) -> list[tuple[float, float]]:
    """Return (physical age / dt, emission fraction), preserving all nodes."""
    if not math.isfinite(tau) or tau < 0 or refinement < 1:
        raise ValueError("invalid rule input")
    if tau == 0:
        h = 1.0/refinement
        d = 0.5*h/math.sqrt(3)
        return [(h*(i+0.5)+sign*d, 0.5*h)
                for i in range(refinement) for sign in (-1,1)]
    eta = 1.0/refinement
    lo = 0.0
    out: list[tuple[float,float]] = []
    while lo < tau:
        hi = min(tau, lo + eta*min(tau,1.0+lo))
        if hi <= lo:
            raise ArithmeticError("geometric panel stalled")
        width = hi-lo
        z = 0.5*width
        q = acosh_sinhc(z)
        # Optical-age offsets, rather than a global last-time subtraction.
        young = lo + (z-q)
        old = hi - (z-q)
        out.extend([(young/tau, width/(2*tau)), (old/tau, width/(2*tau))])
        lo = hi
    return out


def gl(n: int) -> list[tuple[float,float]]:
    if n == 2:
        return [(0.5*(1-1/math.sqrt(3)),0.5),(0.5*(1+1/math.sqrt(3)),0.5)]
    nodes = [0.3399810435848562648, 0.8611363115940525752]
    weights = [0.6521451548625461426,0.3478548451374538574]
    return sorted([(0.5*(1+sign*x), 0.5*w) for x,w in zip(nodes,weights) for sign in (-1,1)])


def evaluate(tau: float, pairs: list[tuple[float,float]]) -> dict:
    exact = float(phi_decimal(tau))
    surv = [w*math.exp(-tau*a) for a,w in pairs]
    total = math.fsum(surv)
    absorbed = math.fsum(w*(-math.expm1(-tau*a)) for a,w in pairs)
    emission = math.fsum(w for _,w in pairs)
    mean_emission = math.fsum(a*w for a,w in pairs)
    means = [math.fsum((a**p)*s for (a,_),s in zip(pairs,surv))/total for p in range(1,5)] if total>0 else []
    refs = [float(age_moment_decimal(tau,p)) for p in range(1,5)]
    rels = [(got-ref)/ref for got,ref in zip(means,refs)]
    kolmogorov = 0.0
    cum = 0.0
    if total>0:
        for (age,_), weight in sorted(zip(pairs,surv)):
            cdf = age if tau == 0 else -math.expm1(-tau*age)/(-math.expm1(-tau))
            kolmogorov = max(kolmogorov,abs(cum-cdf),abs(cum+weight/total-cdf))
            cum += weight/total
    rates = [0.71,0.19,0.097,0.003]
    species = [absorbed*k for k in rates]
    # A single constant-energy source with physical binding owners represented
    # only by their thresholds.  This algebra check does not import atomic rates.
    energy_ev = 100.0
    thresholds_ev = [13.598434599702,24.5873888,54.417765,13.602134599702]
    chemical = math.fsum(a*c for a,c in zip(species,thresholds_ev))
    thermal = math.fsum(a*(energy_ev-c) for a,c in zip(species,thresholds_ev))
    return {
        "tau":tau,"cohorts":len(pairs),"phi":total,"phi_exact":exact,
        "phi_relative_error":(total-exact)/exact,
        "emission_error":emission-1.0,"emission_mean_error":mean_emission-0.5,
        "photon_ledger":emission-total-math.fsum(species),
        "energy_ledger_ev":energy_ev*emission-energy_ev*total-chemical-thermal,
        "age_moment_relative_errors":rels if total>0 else [None]*4,
        "age_mean_scaled_abs_error":tau*abs(means[0]-refs[0]) if total>0 else None,
        "age_cdf_sup_error":kolmogorov if total>0 else None,
        "survival_status":"RESOLVED" if total>0 else "FLOAT_UNDERFLOW_LEGACY_GL",
        "minimum_weight":min(w for _,w in pairs),
        "minimum_age":min(a for a,_ in pairs),"maximum_age":max(a for a,_ in pairs),
        "species_nonnegative":all(a>=0 for a in species),
    }


def main() -> None:
    here=Path(__file__).resolve().parent
    taus=[0.,1e-12,1e-8,1e-4,.1,1.,10.,30.,93.,100.,1e3,1e6,1e12]
    rows=[]
    for tau in taus:
        for refinement in [1,2,4,8,16]:
            ans=evaluate(tau,rule(tau,refinement))
            ans["method"]="positive_symmetric_exp_fit"
            ans["refinement"]=refinement
            ans["eta"]=1./refinement
            assert ans["minimum_weight"]>0
            assert 0.<=ans["minimum_age"]<=ans["maximum_age"]<=1.
            assert abs(ans["phi_relative_error"])<2e-13
            assert abs(ans["emission_error"])<4e-15
            assert abs(ans["emission_mean_error"])<4e-15
            assert ans["age_mean_scaled_abs_error"]<=2./refinement+1e-14
            assert ans["species_nonnegative"]
            assert abs(ans["photon_ledger"])<3e-15
            assert abs(ans["energy_ledger_ev"])<3e-13
            rows.append(ans)
        for n in [2,4]:
            ans=evaluate(tau,gl(n))
            ans["method"]="legacy_gl";ans["refinement"]=n;ans["eta"]=None
            rows.append(ans)
    failures=[]
    for bad in [float("nan"),float("inf"),-1.]:
        try:
            rule(bad,1)
        except ValueError:
            failures.append({"input":repr(bad),"classification":"INPUT_REJECTED"})
        else:
            raise AssertionError("invalid input admitted")
    # At τ=0 the r uniform panels each use GL2: moments 0..3 are exact, while
    # the fourth moment is refined with the physical source age mesh.
    summary={
        "status":"PASS_SCOPED",
        "runtime":"PYTHON_PASS",
        "reference":"analytic integrals evaluated with Decimal precision=90",
        "scope":"constant nonnegative opacity and source; age quadrature and scalar ledgers only",
        "rows":len(rows),
        "positive_rule_rows":sum(r["method"]=="positive_symmetric_exp_fit" for r in rows),
        "max_abs_phi_relative_error":max(abs(r["phi_relative_error"]) for r in rows if r["method"]=="positive_symmetric_exp_fit"),
        "max_abs_source_mean_error":max(abs(r["emission_mean_error"]) for r in rows if r["method"]=="positive_symmetric_exp_fit"),
        "max_abs_number_ledger":max(abs(r["photon_ledger"]) for r in rows if r["method"]=="positive_symmetric_exp_fit"),
        "max_abs_energy_ledger_ev":max(abs(r["energy_ledger_ev"]) for r in rows if r["method"]=="positive_symmetric_exp_fit"),
        "rejections":failures,
        "tau93":[r for r in rows if r["tau"]==93.],
        "tau1e12":[r for r in rows if r["tau"]==1e12],
        "limits":[
            "No native thermochemistry, BASS geometry, or production provider is imported.",
            "Emission mean is exact; source higher moments need refinement or macrostep convergence.",
            "The physical panel cap Δx≤1/r resolves transparent source age distributions independently of κ.",
            "Finite cohort age CDF is atomic; moment convergence does not imply exact age distribution.",
        ],
    }
    with (here/"SCALAR_AND_AGE_RESULTS.json").open("w") as f:
        json.dump(summary,f,indent=2,allow_nan=False)
    fields=["tau","method","refinement","cohorts","phi_relative_error","emission_error","emission_mean_error","photon_ledger","energy_ledger_ev","age_mean_scaled_abs_error","age_cdf_sup_error"]
    with (here/"SCALAR_AND_AGE_GRID.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(fields+[f"age_moment_{p}_relative_error" for p in range(1,5)])
        for r in rows:
            w.writerow([r[k] for k in fields]+r["age_moment_relative_errors"])
    print(json.dumps({k:summary[k] for k in ["status","rows","positive_rule_rows","max_abs_phi_relative_error","max_abs_source_mean_error","max_abs_number_ledger","max_abs_energy_ledger_ev"]},indent=2))
    for r in summary["tau93"]:
        print(r["method"],r["refinement"],r["cohorts"],r["phi_relative_error"],r["age_moment_relative_errors"],r["age_cdf_sup_error"])


if __name__=="__main__":
    main()
