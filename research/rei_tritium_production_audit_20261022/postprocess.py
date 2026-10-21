"""Conditional DD bare-ion tracer on immutable isotope-quotient NPZ histories.

Only reads the old result corpus. New outputs are confined to this directory.
The constant-S Maxwellian continuation is a declared model, not an empirical
low-temperature rate evaluation or a coupled nuclear/atomic calculation.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy import constants as C
from scipy.integrate import quad
from scipy.special import logsumexp

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "rei_isotope_quotient_pilot_20261022" / "pilot"
RESULTS = OLD / "results"
LOG_ZERO = -math.inf
SP = 50.8
SN = 51.0
MU = C.physical_constants["deuteron mass"][0] / 2
ALPHA = C.physical_constants["fine-structure constant"][0]
EG = 2 * MU * C.c**2 * (math.pi * ALPHA)**2
S_UNIT = 1e3 * C.electron_volt * 1e-28  # keV barn -> J m^2
LOG_SP = math.log(SP * S_UNIT)
LOG_SN = math.log(SN * S_UNIT)


def temperature(x):
    z = 21 * np.exp(-np.asarray(x)) - 1
    return 100 + 9900 * (1 + np.tanh((7.5 - z) / 1.25)) / 2


def log_maxwell_kernel(T, epsrel=2e-10):
    """Log <sigma v> per unit SI S; the Gamow exponential never underflows."""
    kt = C.k * float(T)
    e0 = (EG * kt**2 / 4) ** (1 / 3)
    a = e0 / kt

    def shifted(u):
        if u == 0:
            return 0.0
        return math.exp(-a * (u + 2 / math.sqrt(u) - 3))

    pieces = [quad(shifted, lo, hi, epsabs=0, epsrel=epsrel, limit=200)
              for lo, hi in ((0, 1), (1, 4), (4, np.inf))]
    if any(not np.isfinite(v) or not np.isfinite(err) for v, err in pieces):
        raise ArithmeticError("nonfinite Maxwell quadrature")
    integ = sum(v for v, _ in pieces)
    if not integ > 0:
        raise ArithmeticError("zero shifted Maxwell quadrature")
    return (.5 * math.log(8 / (math.pi * MU)) - 1.5 * math.log(kt)
            + math.log(e0) - 3 * a + math.log(integ)), e0 / C.electron_volt


def log_source(logk, nB, Y):
    """Event count per baryon per second; zero inventory has log -inf."""
    nB = np.asarray(nB)
    Y = np.asarray(Y)
    if np.any(nB <= 0) or np.any(Y < 0):
        raise ValueError("nonpositive baryon density or negative reactant")
    return np.where(Y > 0, math.log(.5) + np.log(nB)
                    + 2 * np.log(np.maximum(Y, np.finfo(float).tiny)) + logk,
                    LOG_ZERO)


def convolution(t, logs, lam):
    """Exact endpoint recurrence for piecewise-linear *source* in proper time.

    Returns log cumulative births and log surviving population. The source's
    endpoint logs are exponentiated only through logsumexp, so subnormal rates
    are never interpreted as zero. Source interpolation is in linear units.
    """
    if lam <= 0 or not np.all(np.diff(t) > 0):
        raise ValueError("decay rate/time ordering")
    births = np.full(len(t), LOG_ZERO)
    survive = np.full(len(t), LOG_ZERO)
    for i in range(1, len(t)):
        dt = float(t[i] - t[i-1])
        q = lam * dt
        e = math.exp(-q)
        if q < 1e-4:
            # lambda*A = q/2-q^2/3+q^3/8...,
            # lambda*B = q/2-q^2/6+q^3/24...
            ca = q * (.5 - q / 3 + q*q / 8 - q**3 / 30 + q**4 / 144)
            cb = q * (.5 - q / 6 + q*q / 24 - q**3 / 120 + q**4 / 720)
        else:
            f = -math.expm1(-q) / q
            ca, cb = f - e, 1 - f
        if ca < 0 or cb < 0:
            raise ArithmeticError("negative convolution coefficient")
        part = logsumexp([logs[i-1], logs[i]]) + math.log(dt / 2)
        births[i] = np.logaddexp(births[i-1], part)
        survive[i] = logsumexp((survive[i-1] - q,
                                 logs[i-1] + math.log(ca / lam),
                                 logs[i] + math.log(cb / lam)))
    return births, survive


def linear_log(v):
    """Explicit underflow annotation; never call the result a physical zero."""
    return {"log10": float(v / math.log(10)) if np.isfinite(v) else None,
            "linear": float(math.exp(v)) if v > math.log(np.nextafter(0., 1.)) else None,
            "linear_underflow": bool(np.isfinite(v) and
                                     v <= math.log(np.nextafter(0., 1.)))}


def read_case(path):
    with np.load(path, allow_pickle=False) as d:
        required = {"x", "z", "conditional", "census", "census_names",
                    "diagnostics", "diagnostic_names"}
        if not required.issubset(d.files):
            raise ValueError("missing raw fields " + path.name)
        x = d["x"].copy()
        f = d["conditional"].copy()
        census = d["census"].copy()
        diagnostics = d["diagnostics"].copy()
        cn = d["census_names"].tolist()
        dn = d["diagnostic_names"].tolist()
        if x.shape != (257,) or f.shape != (257, 9) or census.shape != (257, 21) \
                or diagnostics.shape != (257, 37):
            raise ValueError("unexpected background shape " + path.name)
        ix = {name: cn.index(name) for name in ("D_0", "D_1", "T_0", "T_1")}
        jx = {name: dn.index(name) for name in
              ("H_per_s", "nB_m3", "T_K", "elapsed_s", "ne_cm3")}
        v = {k: census[:, ix[k]] for k in ix}
        v.update({k: diagnostics[:, jx[k]] for k in jx})
        v["x"] = x
        v["f_DII"] = f[:, 1]
        if not all(np.isfinite(a).all() for a in v.values()):
            raise ValueError("nonfinite background " + path.name)
        if np.any(np.diff(x) <= 0) or np.any(np.diff(v["elapsed_s"]) <= 0):
            raise ValueError("nonmonotone grid " + path.name)
        if np.any(v["H_per_s"] <= 0) or np.any(v["T_K"] <= 0) or np.any(v["nB_m3"] <= 0):
            raise ValueError("nonpositive background " + path.name)
        if np.any(v["D_0"] < 0) or np.any(v["D_1"] < 0):
            raise ValueError("negative D population " + path.name)
        if np.any(v["T_0"] != 0) or np.any(v["T_1"] != 0):
            raise ValueError("old T hard-zero premise failed " + path.name)
        yd = v["D_0"] + v["D_1"]
        if not np.allclose(v["D_1"], yd * v["f_DII"], rtol=1e-10, atol=1e-15):
            raise ValueError("DII census/conditional mismatch " + path.name)
        if np.max(np.abs(yd - yd[0])) > 1e-10 * yd[0]:
            raise ValueError("nonconstant inherited D inventory " + path.name)
        v["Y_D"] = yd[0]
        return v


def refinements(v, factor):
    if factor == 1:
        return v
    x = np.linspace(v["x"][0], v["x"][-1], factor * (len(v["x"])-1) + 1)
    w = {k: np.interp(x, v["x"], v[k]) for k in
         ("elapsed_s", "nB_m3", "H_per_s", "f_DII")}
    w.update(x=x, T_K=temperature(x), Y_D=v["Y_D"])
    w["D_1"] = w["Y_D"] * w["f_DII"]
    return w


def rate_grid(x, T):
    logs, e0 = zip(*(log_maxwell_kernel(float(temp)) for temp in T))
    return np.asarray(logs), np.asarray(e0)


def evaluate(v, log_kernel, lambda_t, lambda_n):
    nb = v["nB_m3"]
    k_p = log_kernel + LOG_SP
    k_n = log_kernel + LOG_SN
    p = log_source(k_p, nb, v["D_1"])
    n = log_source(k_n, nb, v["D_1"])
    pa = log_source(k_p, nb, np.full(len(nb), v["Y_D"]))
    na = log_source(k_n, nb, np.full(len(nb), v["Y_D"]))
    cp, yt = convolution(v["elapsed_s"], p, lambda_t)
    cn, yn = convolution(v["elapsed_s"], n, lambda_n)
    cpa, _ = convolution(v["elapsed_s"], pa, lambda_t)
    cna, _ = convolution(v["elapsed_s"], na, lambda_n)
    return dict(log_kp=k_p, log_kn=k_n, log_sp=p, log_sn=n,
                log_Cp=cp, log_Cn=cn, log_YT=yt, log_Yn=yn,
                log_Cp_allD=cpa, log_Cn_allD=cna,
                log_YT_qss=p-math.log(lambda_t))


def controls(lambda_t):
    evidence = {}
    for temp in (100., 1000., 10000.):
        a, e0 = log_maxwell_kernel(temp, 1e-9)
        b, _ = log_maxwell_kernel(temp, 1e-12)
        if abs(a-b) > 1e-7:
            raise AssertionError("quadrature tightening")
        evidence[str(int(temp))] = {"log_rate_difference": abs(a-b), "E0_eV": e0}
    t = np.array([0., .001/lambda_t, .01/lambda_t, .1/lambda_t,
                  1/lambda_t, 10/lambda_t, 100/lambda_t])
    s = 1e-30
    c, y = convolution(t, np.full(len(t), math.log(s)), lambda_t)
    exact = s / lambda_t * -np.expm1(-lambda_t * t[1:])
    err = np.max(abs(np.exp(y[1:]) - exact) / exact)
    if err > 1e-10:
        raise AssertionError("constant-source decay convolution")
    if not np.all(y[1:] <= c[1:] + 1e-10):
        raise AssertionError("survivors exceed births")
    z = log_source(np.array([-1000., -1000.]), np.ones(2), np.array([0., 1e-5]))
    if not np.isneginf(z[0]) or not np.isfinite(z[1]):
        raise AssertionError("zero versus underflow source")
    # D+D -> T+p and D+D -> He3+n each conserve A and nuclear Z.
    if not (2*2 == 3+1 == 3+1 and 2*1 == 1+1 == 2+0):
        raise AssertionError("DD stoichiometry")
    if abs((math.exp(LOG_SN-LOG_SP)/(SN/SP))-1) > 1e-12:
        raise AssertionError("channel S ratio")
    return dict(quadrature=evidence, constant_source_relative_error=float(err),
                zero_source_structural=True, finite_underflow_log_source=True,
                identical_reactant_factor=.5, stoichiometric_A_Z=True,
                SI_S_unit_J_m2=S_UNIT, rate_ratio=SN/SP)


def load_decay():
    p = HERE / "EVALUATED_DECAY_INPUTS.json"
    if not p.exists():
        raise FileNotFoundError("evaluated decay input required before execution: " + str(p))
    d = json.loads(p.read_text())
    # Contractual values are read from the evaluated-input file, never guessed.
    half = float(d["tritium_half_life_years"])
    year = float(d["year_days"]) * float(d["seconds_per_day"])
    neutron = float(d["neutron_mean_lifetime_s"])
    if not (half > 0 and year > 0 and neutron > 0 and d.get("sources")):
        raise ValueError("incomplete evaluated decay input")
    return d, math.log(2) / (half * year), 1 / neutron


def run():
    if (HERE / "TRACER_HISTORIES.npz").exists() or (HERE / "TRACER_REPORT.json").exists():
        raise FileExistsError("one-shot sweep outputs already present")
    decay, lt, ln = load_decay()
    contract = json.loads((HERE / "PHYSICS_CONTRACT.json").read_text())
    paths = sorted(RESULTS.glob("quotient_*.npz"))
    if len(paths) != contract["background_count"]:
        raise ValueError("expected 82 quotient trajectories")
    backgrounds = [read_case(p) for p in paths]
    x = backgrounds[0]["x"]
    if any(not np.array_equal(v["x"], x) for v in backgrounds):
        raise ValueError("nonmatching sample grids")
    if not any(np.any(v["D_1"] > 0) for v in backgrounds):
        raise ValueError("no ionized D")
    logk, e0 = rate_grid(x, backgrounds[0]["T_K"])
    record = [evaluate(v, logk, lt, ln) for v in backgrounds]
    keys = tuple(record[0])
    arrays = {key: np.stack([r[key] for r in record]) for key in keys}
    for i, r in enumerate(record):
        positive = backgrounds[i]["D_1"] > 0
        if not (np.isfinite(r["log_sp"][positive]).all()
                and np.isfinite(r["log_sn"][positive]).all()):
            raise AssertionError("positive source represented as zero")
        if not np.all(r["log_YT"][1:] <= r["log_Cp"][1:] + 1e-10):
            raise AssertionError("T survival larger than births")
        if not np.all(r["log_Yn"][1:] <= r["log_Cn"][1:] + 1e-10):
            raise AssertionError("n survival larger than births")
        if np.any(r["log_Cp"] > r["log_Cp_allD"]+1e-10):
            raise AssertionError("all-D source comparator")
    # One source-grid refinement sweep. 4x is only authorized if the 2x
    # reconstructed cumulative birth differs by more than 0.02 dex.
    sample = refinements(backgrounds[0], 2)
    logk2, e02 = rate_grid(sample["x"], sample["T_K"])
    refined = [evaluate(refinements(v, 2), logk2, lt, ln) for v in backgrounds]
    d2 = np.array([max(abs((r["log_Cp"][-1]-q["log_Cp"][-1])/math.log(10)),
                       abs((r["log_Cn"][-1]-q["log_Cn"][-1])/math.log(10)))
                   for r, q in zip(record, refined)])
    extra = None
    if np.max(d2) > contract["checks"]["grid_sensitivity_dex_max"]:
        sample4 = refinements(backgrounds[0], 4)
        logk4, e04 = rate_grid(sample4["x"], sample4["T_K"])
        refined4 = [evaluate(refinements(v, 4), logk4, lt, ln) for v in backgrounds]
        d4 = np.array([max(abs((r["log_Cp"][-1]-q["log_Cp"][-1])/math.log(10)),
                           abs((r["log_Cn"][-1]-q["log_Cn"][-1])/math.log(10)))
                       for r, q in zip(refined, refined4)])
        extra = dict(max_2x_to_4x_dex=float(np.max(d4)),
                     e0_eV_range=[float(np.min(e04)), float(np.max(e04))])
    birthsum = np.logaddexp(arrays["log_Cp"][:,-1], arrays["log_Cn"][:,-1])
    depletion = 2*np.exp(birthsum)/np.array([v["Y_D"] for v in backgrounds])
    checks = controls(lt)
    checks.update(max_passive_depletion=float(np.max(depletion)),
                  max_1x_to_2x_cumulative_birth_dex=float(np.max(d2)),
                  refinement_4x=extra)
    status = ("PASS_CONDITIONAL_TRACER" if
              np.max(depletion) <= contract["checks"]["passive_depletion_fraction_max"]
              else "HOLD_PASSIVE_DEPLETION")
    strongest = int(np.argmax(arrays["log_Cp"][:,-1]))
    report = dict(status=status, scope=contract["scope"], base_head=contract["base_head"],
                  old_quotient_count=len(paths), new_background_ivps=0,
                  old_T_zero_structural=True, old_T_census_exact_zero=True,
                  S_keV_barn=dict(DDp=SP, DDn=SN), decay_inputs=decay,
                  E_G_eV=EG/C.electron_volt,
                  E0_eV_range=[float(np.min(e0)), float(np.max(e0))],
                  checks=checks, strongest_case=paths[strongest].stem,
                  strongest_endpoint={k:linear_log(arrays[k][strongest,-1]) for k in
                                      ("log_Cp", "log_Cn", "log_YT", "log_Yn", "log_YT_qss")},
                  endpoint_ranges={k:{"min_log10":float(np.min(arrays[k][:,-1])/math.log(10)),
                                      "max_log10":float(np.max(arrays[k][:,-1])/math.log(10))}
                                   for k in ("log_Cp", "log_Cn", "log_YT", "log_Yn")},
                  caveats=["Bare-ion, Maxwellian, constant-zero-energy-S conditional model; no measured 100–10000 K rate.",
                           "Primary total T only; no energetic-product stopping or ionic state prediction.",
                           "DDn secondary T count no-decay first-generation envelope <= Cn; recycling excluded.",
                           "Coarse/refined comparison tests reconstructed history, not unknown subgrid physics.",
                           "No 99% statement, full 19-channel completeness, or production-default change."])
    if status != "PASS_CONDITIONAL_TRACER":
        # Preserve bounded diagnostic outcomes; admission remains with reviewer.
        report["stop_reason"] = "depletion exceeds passive-tracer threshold"
    np.savez_compressed(HERE / "TRACER_HISTORIES.npz",
                        case_names=np.array([p.stem for p in paths]), x=x,
                        z=21*np.exp(-x)-1, T_K=backgrounds[0]["T_K"],
                        E0_eV=e0, nB_m3=np.stack([v["nB_m3"] for v in backgrounds]),
                        DII=np.stack([v["D_1"] for v in backgrounds]),
                        elapsed_s=np.stack([v["elapsed_s"] for v in backgrounds]),
                        **arrays)
    (HERE / "TRACER_REPORT.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="one bounded saved-history sweep")
    args = parser.parse_args()
    if args.run:
        print(json.dumps(run(), indent=2))
    else:
        parser.print_help()
