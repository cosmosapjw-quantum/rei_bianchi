#!/usr/bin/env python3
"""New RR competition and frozen-energy absorption responses on saved P01 data.

PR113 RCT rates and its trapezoid exposure are retained as inputs. This script
performs no history ODE, photon transport, native build or RCT-ON evolution.
FT03 and Verner functions are explicit SHA-pinned Python transcriptions; they
are not a Rust parity claim. The original HE scalar provider is actually called
once for KF96 and once for the expected out-of-domain GM25 response.
"""
from __future__ import annotations
import argparse
import csv
from decimal import Decimal as D, localcontext
import hashlib
import json
import math
from pathlib import Path
import platform
import resource
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
C_CM_S = 29979245800.0
EV_ERG, KB_ERG_K = 1.602176634e-12, 1.380649e-16
CHI_EV = (13.598434599702, 24.587389011, 54.41776)
ENERGIES_EV = (20.0, 30.0, 40.819325400298, 54.42, 60.0, 100.0)
SPECIES = ("HI", "HeI", "HeII")
VERNER = (
    ("13.60", "0.4298", "5.475e4", "32.88", "2.963", "0", "0", "0"),
    ("24.59", "13.61", "949.2", "1.469", "3.188", "2.039", "0.4434", "2.136"),
    ("54.42", "1.720", "1.369e4", "32.88", "2.963", "0", "0", "0"),
)
PINS = {
    "inputs/extended_dataset.npz": "3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be",
    "inputs/extended.json": "f1ef5e09495df872e705656ff8d1252376c230e860ccbb882e3527b17e41a24b",
    "inputs/CONTRACT.json": "2f5f118b856a47fa339a510a58e7221e7d7ab3ea3a38625d2c61e9b93380ed6d",
    "inputs/ft03_rates.rs": "1a97cd7a3555deeb4d8700376cd84580c5102127773bc3a235a29c33b0c1542f",
    "inputs/atomic_provider.rs": "b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3",
    "inputs/hhe_events.rs": "c100b08e034089c2d67b2102769ccdd51f1d29a2f388d6bb2dfe7984af93b290",
    "inputs/bass_he_atomic_export/_kf96.py": "0e7c8a846112e14ec8d761fe7b9d978e65b4c30456e0d31829c52724e91a4ff6",
    "inputs/bass_he_atomic_export/_rate.py": "529ae325622718b48292c3b748a7850ccb315733b28bff930388f00915f2d217",
    "inputs/prior_PR113/per_epoch.json": "079f31c7574d6eebd05ca207ff5fcd75e8e1a78a58e0733c1ff901c6124d6b36",
    "inputs/prior_PR113/VALIDATION.json": "03143655066edf7c92c3ae250dcb33d8ac4624f45b3fc368a716e9feb63e26b9",
}


def alpha3_case_a(t):
    """Exact algebra/guard of ft03_rates.rs, a=2, not raw Grackle K6."""
    if not math.isfinite(t) or not 30000.0 <= t <= 110000.0:
        raise ValueError("FT03_TEMPERATURE_DOMAIN")
    lam = 1263030.0 / t
    u = (lam / 0.522) ** 0.470
    return 2.0 * 1.269e-13 * lam**1.503 / (1.0 + u)**1.923


def sigma_verner(energy, species_index):
    """atomic_provider.rs::cross_section, cm^2, threshold and <=50keV guard."""
    if not math.isfinite(energy) or energy < 0.0 or energy > 50000.0:
        raise ValueError("VERNER_ENERGY_DOMAIN")
    eth, e0, sigma0, ya, power, yw, y0, y1 = map(float, VERNER[species_index])
    if energy < eth:
        return 0.0
    x = energy / e0 - y0
    y = math.sqrt(x*x + y1*y1)
    return sigma0 * ((x-1.0)**2 + yw*yw) * y**(power/2.0-5.5) * (
        1.0 + math.sqrt(y/ya))**(-power) * 1e-18


def absorption_fractions(x):
    """Impulse and uniform-birth absorption probabilities; stable as x -> 0."""
    if not math.isfinite(x) or x < 0.0:
        raise ValueError("OPTICAL_DEPTH_DOMAIN")
    if x == 0.0:
        return 0.0, 0.0
    impulse = -math.expm1(-x)
    if x < 0.05:
        term = x / 2.0
        terms = [term]
        for n in range(2, 19):
            term *= -x / (n+1)
            terms.append(term)
        uniform = math.fsum(terms)
    else:
        uniform = 1.0 - impulse / x
    return impulse, uniform


def decimal_alpha3(t):
    lam = D("1263030") / D(str(t))
    u = (D("0.470") * (lam/D("0.522")).ln()).exp()
    return D("2.538e-13") * (
        D("1.503")*lam.ln() - D("1.923")*(1+u).ln()).exp()


def decimal_sigma(energy, index):
    eth, e0, sigma0, ya, power, yw, y0, y1 = map(D, VERNER[index])
    energy = D(str(energy))
    if energy < eth:
        return D(0)
    x = energy/e0-y0
    y = (x*x+y1*y1).sqrt()
    log_factor = (power/2-D("5.5"))*y.ln() - power*(1+(y/ya).sqrt()).ln()
    return sigma0*((x-1)**2+yw*yw)*log_factor.exp()*D("1e-18")


def relative(a, b):
    return abs(float(a)-float(b))/abs(float(b)) if b else abs(float(a))


def dump_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+"\n")


def dump_csv(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT/"results")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    started = time.perf_counter()
    args.output.mkdir(parents=True, exist_ok=False)
    checks, identity = {}, []
    for name, sha in PINS.items():
        b = (ROOT/name).read_bytes()
        actual = hashlib.sha256(b).hexdigest()
        if actual != sha:
            raise ValueError("SOURCE_HASH_MISMATCH:"+name)
        identity.append({"path":name, "sha256":actual, "bytes":len(b)})
    checks["selected_inputs_and_source_sha256"] = True

    sys.path.insert(0, str(ROOT/"inputs"))
    import bass_he_atomic_export
    from bass_he_atomic_export import _kf96, _rate
    bass_he_atomic_export.verify_runtime_bindings()
    contract = json.loads((ROOT/"inputs/CONTRACT.json").read_text())
    assert contract["closure"]["id"] == "HOMOGENEOUS_PRIMARY_ONLY_CASE_A_ESCAPE"
    assert contract["closure"]["optional_CR_RCT_HH"] == "OFF"
    prior = json.loads((ROOT/"inputs/prior_PR113/per_epoch.json").read_text())
    prior_validation = json.loads((ROOT/"inputs/prior_PR113/VALIDATION.json").read_text())
    reference = json.loads((ROOT/"inputs/extended.json").read_text())["history"]
    with np.load(ROOT/"inputs/extended_dataset.npz", allow_pickle=False) as data:
        times, states = data["times_s"].copy(), data["states"].copy()
        q = data["q_eV"].copy()
    assert states.shape == (2913,17) and len(prior) == 17 and len(reference) == 17
    assert np.array_equal(times, np.linspace(0,1e11,17))
    assert np.array_equal(states[:3].T, [[r["xHII"],r["xHeII"],r["xHeIII"]] for r in prior])
    scalar_keys = ("time_s","T_K","nH_cm3","xHII","xHeII","xHeIII")
    assert all(r[k] == s[k] for r,s in zip(prior,reference) for k in scalar_keys)
    checks["prior_PR113_gas_points_exactly_match_selected_extended_reference"] = True
    checks["selected_wide_band_2904_nodes_17_epochs"] = True
    assert all(np.min(np.abs(q-energy)) > 0 for energy in ENERGIES_EV)
    checks["probe_energies_distinct_from_retained_P03A_quadrature_nodes"] = True

    common = {"distribution":"MAXWELL_COMMON_T_ZERO_DRIFT",
              "acknowledge_source_conflict":True, "unit":"cm3 s-1"}
    kf = _kf96.rate(prior[0]["T_K"], source_id=_kf96.SOURCE_ID, **common)
    try:
        _rate.rate(prior[0]["T_K"], source_id=_rate.SOURCE_ID, **common)
    except _rate.ContractError as exc:
        gm25_error = str(exc)
    else:
        raise AssertionError("GM25_WARM_TEMPERATURE_SHOULD_REJECT")
    checks["GM25_50000K_domain_rejected"] = gm25_error == "OUTSIDE_REPORTED_FIT_DOMAIN_NO_EXTRAPOLATION"
    k = kf["rate_binary64"]

    rate_rows = []
    max_alpha_error = max_rct_arithmetic_error = max_rho_error = max_eos_error = 0.0
    for i, row in enumerate(prior):
        t, nh, nh0, nhe = row["T_K"], row["nH_cm3"], prior[0]["nH_cm3"], row["nHe_m3"]/1e6
        ne = nh*row["xHII"]+nhe*(row["xHeII"]+2*row["xHeIII"])
        nhi, nheiii = row["nHI_m3"]/1e6, row["nHeIII_m3"]/1e6
        rct = row["rate_m3_s"]/1e6
        alpha = alpha3_case_a(t)
        rr = alpha*ne*nheiii
        rho = rct/rr
        eos_t = 2*states[3,i]*nh*EV_ERG/(3*KB_ERG_K*(nh+nhe+ne))
        max_eos_error = max(max_eos_error, relative(eos_t,t))
        with localcontext() as ctx:
            ctx.prec = 80
            da = decimal_alpha3(t)
            drct = D(str(k))*D(str(nhi))*D(str(nheiii))
            drr = da*D(str(ne))*D(str(nheiii))
            max_alpha_error = max(max_alpha_error, relative(alpha,da))
            max_rct_arithmetic_error = max(max_rct_arithmetic_error, relative(rct,drct))
            max_rho_error = max(max_rho_error, relative(rho,drct/drr))
        rate_rows.append({
            "epoch":i,"time_s":row["time_s"],"temperature_K":t,
            "nHI_cm3":nhi,"nHeIII_cm3":nheiii,"ne_cm3":ne,
            "RCT_rate_cm3_s_retained":rct,
            "HeIII_CaseA_RR_alpha_cm3_s_new":alpha,
            "HeIII_CaseA_RR_rate_cm3_s_new":rr,"RCT_over_HeIII_RR_new":rho,
            "RCT_per_H_s_retained":row["fraction_rates_s"][0],
            "HeIII_RR_per_H_s_new":rr/nh,
        })
    checks["FT03_alpha3_vs_Decimal80"] = max_alpha_error < 3e-14
    checks["retained_RCT_rate_unit_arithmetic_vs_Decimal80"] = max_rct_arithmetic_error < 3e-14
    checks["new_RCT_RR_ratio_vs_Decimal80"] = max_rho_error < 3e-14
    checks["saved_EOS_compatibility"] = max_eos_error < 3e-14

    first = prior[0]
    nh, nhe = first["nH_cm3"], first["nHe_m3"]/1e6
    lower = (nh*(1-first["xHII"]),
             nhe*(1-first["xHeII"]-first["xHeIII"]), nhe*first["xHeII"])
    dt = float(times[-1]-times[0])
    kernel_rows = []
    sigma_error = fraction_error = ledger_error = 0.0
    for energy in ENERGIES_EV:
        sigmas = [sigma_verner(energy,s) for s in range(3)]
        lambdas = [C_CM_S*n*s for n,s in zip(lower,sigmas)]
        total = math.fsum(lambdas)
        branches = [v/total for v in lambdas] if total else [0.0]*3
        impulse, uniform = absorption_fractions(total*dt)
        entry = {"energy_eV":energy,"dt_s":dt,"total_lambda_s":total,
                 "optical_depth":total*dt,
                 "impulse_absorption_fraction":impulse,
                 "uniform_birth_absorption_fraction":uniform,
                 "uniform_over_impulse":uniform/impulse if impulse else 0.0}
        for j,species in enumerate(SPECIES):
            entry["sigma_"+species+"_cm2"] = sigmas[j]
            entry["lambda_"+species+"_s"] = lambdas[j]
            entry["branch_"+species] = branches[j]
            entry["impulse_absorbed_"+species+"_per_incident"] = impulse*branches[j]
            entry["uniform_absorbed_"+species+"_per_born"] = uniform*branches[j]
        mean_binding = math.fsum(v*c for v,c in zip(branches,CHI_EV))
        mean_heat = math.fsum(v*(energy-c) for v,c in zip(branches,CHI_EV))
        for label,p in (("impulse",impulse),("uniform",uniform)):
            entry[label+"_binding_eV_per_photon"] = p*mean_binding
            entry[label+"_heat_eV_per_photon"] = p*mean_heat
            entry[label+"_surviving_energy_eV_per_photon"] = (1-p)*energy
            ledger_error = max(ledger_error, abs(
                p*mean_binding+p*mean_heat+(1-p)*energy-energy)/energy)
        with localcontext() as ctx:
            ctx.prec = 80
            for j in range(3):
                sigma_error = max(sigma_error, relative(sigmas[j],decimal_sigma(energy,j)))
            dx = D(str(total))*D(str(dt))
            di = 1-(-dx).exp()
            du = 1-di/dx
            fraction_error = max(fraction_error,relative(impulse,di),relative(uniform,du))
        kernel_rows.append(entry)
    checks["Verner_transcription_vs_Decimal80"] = sigma_error < 3e-14
    checks["impulse_uniform_response_vs_Decimal80"] = fraction_error < 3e-14
    checks["species_absorption_sum_and_positive"] = all(
        math.isclose(sum(r["branch_"+s] for s in SPECIES),1,rel_tol=3e-15)
        and 0 <= r["uniform_birth_absorption_fraction"] <= r["impulse_absorption_fraction"] <= 1
        for r in kernel_rows)
    checks["binding_heat_surviving_energy_identity"] = ledger_error < 3e-15
    checks["fit_cutoffs_distinct_from_native_binding_thresholds"] = all(
        float(VERNER[i][0]) != CHI_EV[i] for i in range(3))
    checks["RCT_Q_reference_below_HeII_fit_cutoff"] = (
        ENERGIES_EV[2] == CHI_EV[2]-CHI_EV[0]
        and sigma_verner(ENERGIES_EV[2],2) == 0)
    limit_checks = []
    with localcontext() as ctx:
        ctx.prec = 80
        for x in (0.0,1e-12,1e-8,0.01,0.049,0.05,1.0,100.0):
            pi,pu = absorption_fractions(x)
            if x:
                dx=D(str(x));di=1-(-dx).exp();du=1-di/dx
                limit_checks.append({"x":x,"impulse_relative":relative(pi,di),"uniform_relative":relative(pu,du)})
            else:
                assert (pi,pu)==(0.0,0.0)
    checks["zero_thin_intermediate_thick_response_limits"] = max(
        max(v["impulse_relative"],v["uniform_relative"]) for v in limit_checks) < 3e-14
    ratios=[r["RCT_over_HeIII_RR_new"] for r in rate_rows]
    result = {
        "task":"BASS_HE_RUX03_WARM_SAVED_RR_AND_FROZEN_ABSORPTION",
        "status":"NUMERICALLY_CHECKED_CANDIDATE" if all(checks.values()) else "FAIL",
        "independent_decision":"PENDING_PARENT_REVIEW",
        "selected_input":{
            "path":"inputs/extended_dataset.npz","sha256":PINS["inputs/extended_dataset.npz"],
            "original_path":"recovery_drive/physical_v2/research/physical_provider_20261010/evidence/extended_dataset.npz",
            "nodes":2904,"epochs":17,"time_s":[0,dt],"initial_xHeIII":first["xHeIII"],
            "input_selection_correction":"base_dataset.npz is historical 10-200eV/1984-node input; selected extended dataset is 10-50000eV/2904-node P01 input. No narrow-band calculation performed."},
        "retained_PR113":{
            "commit":"efb63623c4ed0f6c270a677fab3eb0a81ce80e34",
            "path":"research/rct_rate_only_p01_20261011",
            "event_rates":"per_epoch.json retained; converted from m^-3 s^-1 to cm^-3 s^-1",
            "saved_grid_piecewise_linear_rate_exposure":prior_validation["saved_grid_piecewise_linear_rate_exposure"],
            "old_provider_campaign_reexecuted":False},
        "new_work":{"HeIII_RR_point_evaluations":17,"frozen_absorption_energy_points":6,
                    "ODE_runs":0,"transport_runs":0,"native_builds":0,
                    "actual_KF96_scalar_provider_calls":1,"actual_GM25_domain_probe_calls":1},
        "coefficient_evaluation":{
            "KF96":"Original Python provider function called at 50000K; retained rate table consumed",
            "HeIII_RR":"Source-pinned FT03 CaseA a=2 transcription of inputs/ft03_rates.rs, not raw Grackle K6",
            "Verner":"Source-pinned transcription of inputs/atomic_provider.rs::cross_section",
            "new_native_parity":"NOT_RUN"},
        "summary":{"RCT_over_HeIII_RR_min":min(ratios),"RCT_over_HeIII_RR_max":max(ratios),
                   "initial_HeIII_RR_alpha_cm3_s":rate_rows[0]["HeIII_CaseA_RR_alpha_cm3_s_new"],
                   "initial_HeIII_RR_rate_cm3_s":rate_rows[0]["HeIII_CaseA_RR_rate_cm3_s_new"],
                   "initial_RCT_rate_cm3_s_retained":rate_rows[0]["RCT_rate_cm3_s_retained"],
                   "GM25_50000K_expected_error":gm25_error,
                   "RCT_direct_free_electron_per_event":0},
        "frozen_absorption_assumptions":{
            "densities_cm3":dict(zip(SPECIES,lower)), "clock":"proper elapsed seconds",
            "photon_energy":"Fixed local gas-frame energy at each named probe; no redshift or evolved opacity",
            "birth_models":["all photons born at t=0","constant birth rate from0 to dt, normalized per total born"],
            "angular_dependence":"none for frozen isotropic ground-state absorption at fixed gas-frame E",
            "energy_points_are_a_spectrum":False,
            "Q_reference_eV":CHI_EV[2]-CHI_EV[0],
            "cross_section_cutoffs_eV":dict(zip(SPECIES,[float(v[0]) for v in VERNER])),
            "native_binding_energies_eV":dict(zip(SPECIES,CHI_EV)),
            "c_cm_s":C_CM_S, "eV_erg":EV_ERG,"kB_erg_K":KB_ERG_K,
            "relation_to_P03A":"Retained P03A uses time-varying 17-epoch opacity and existing2904 nodes; not rerun. Current constant-initial-state six monoenergy responses add uniform-birth integration."},
        "numerical_validation":{
            "checks":checks,"max_alpha3_relative_Decimal80":max_alpha_error,
            "max_retained_RCT_arithmetic_relative_Decimal80":max_rct_arithmetic_error,
            "max_rho_relative_Decimal80":max_rho_error,"max_Verner_relative_Decimal80":sigma_error,
            "max_absorption_fraction_relative_Decimal80":fraction_error,
            "max_energy_ledger_relative":ledger_error,
            "max_saved_EOS_relative":max_eos_error,"limit_checks":limit_checks},
        "limits":[
            "Sampled OFF-trajectory competition, not an RCT-ON history or feedback/error bound.",
            "Retained trapezoid exposure has no estimated interpolation error or uniform continuous-time bound.",
            "Frozen absorption is an exact constant-coefficient response under the named assumptions, not evolving Bianchi transport.",
            "No RCT photon spectrum, mean photon energy, atomic uncertainty, heat moment or physical escaping/reabsorption closure is supplied.",
            "One small local ratio does not establish global EoR or other initial-state materiality."],
        "input_identity":identity,"source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "runtime":{"python":platform.python_version(),"numpy":np.__version__,
                   "wall_seconds":time.perf_counter()-started,
                   "maxrss_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},
    }
    dump_csv(args.output/"RCT_RR_COMPETITION.csv",rate_rows)
    dump_csv(args.output/"FROZEN_ABSORPTION_KERNEL.csv",kernel_rows)
    dump_json(args.output/"SCREENING_RESULT.json",result)
    if args.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
        fig,(ax,ab)=plt.subplots(1,2,figsize=(11.4,4.4),gridspec_kw={"width_ratios":[1.15,1]},layout="constrained")
        labels=["20","30","40.8193\n(Q reference)","54.42","60","100"]
        x=np.arange(6)
        ax.bar(x-.18,[r["impulse_absorption_fraction"] for r in kernel_rows],.36,label="Born at interval start",color="#176b87")
        ax.bar(x+.18,[r["uniform_birth_absorption_fraction"] for r in kernel_rows],.36,label="Uniform births",color="#ef9f42")
        ax.set_yscale("log");ax.set_xticks(x,labels);ax.set_xlabel("Probe energy [eV]")
        ax.set_ylabel("Absorbed fraction");ax.set_title("Frozen initial state, duration $10^{11}$ s")
        ax.legend(frameon=False,fontsize=9);ax.grid(axis="y",alpha=.18)
        bottom=np.zeros(6)
        for species,color in zip(SPECIES,["#176b87","#ef9f42","#894c9b"]):
            value=np.array([r["branch_"+species] for r in kernel_rows])
            ab.bar(x,value,bottom=bottom,label=species,color=color);bottom+=value
        ab.set_xticks(x,labels);ab.set_ylim(0,1.04);ab.set_xlabel("Probe energy [eV]")
        ab.set_ylabel("Share of absorption events");ab.set_title("Species branching for either birth model")
        ab.legend(frameon=False,fontsize=9)
        fig.suptitle("Conditional monoenergy response on saved warm P01 gas",fontsize=13)
        fig.savefig(args.output/"FROZEN_ABSORPTION_RESPONSE.png",dpi=190)
        fig.savefig(args.output/"FROZEN_ABSORPTION_RESPONSE.pdf")
        plt.close(fig)
    print(json.dumps({"status":result["status"],"summary":result["summary"],
                      "checks":checks,"runtime":result["runtime"]},indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
