"""Seven matched-family figure pairs from saved semi-relativistic histories.

Only plotting and finite comparisons live here. The producer owns integrations;
this renderer never calls a background IVP or a nuclear solver.
"""
from __future__ import annotations

import csv
import json
import math
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
DOSSIER = HERE.parent
sys.path.insert(0, str(DOSSIER))
import render_dossier as draw

CONTRACT = DOSSIER / "STRONG_PI_M_CONTRACT.json"
TITLE = "New matched semi-relativistic family: fₘ=0.3, m/Tref=3"
YEAR_S = 365.25 * 86400


def _context_save(fig, stem):
    heading = fig._suptitle
    if heading is not None:
        heading.set_text(heading.get_text().replace("strong_pi_m:", TITLE + ":"))
        heading.set_fontsize(11.5)
    return draw._save_original(fig, stem)


def _load(case):
    path = HERE / "results" / (case + ".npz")
    meta = json.loads(path.with_suffix(".json").read_text())
    with np.load(path, allow_pickle=False) as data:
        names = data["diagnostic_names"].tolist()
        cols = {key: data["diagnostics"][:, names.index(key)].copy()
                for key in ("elapsed_s", "T_K", "signed_Sigma", "Sigma_F", "P_m",
                            "P_r", "P_gamma", "P_nu", "H_per_s", "Pi_m", "Pi_r",
                            "Pi_total", "tau_T", "nB_m3", "ne_m3",
                            "matter_number_comoving")}
        output = {"case": case, "model": meta["model"], "initial_axes": meta["initial_axes"],
                  "x": data["x"].copy(), "z": data["z"].copy(),
                  "Y": data["census"].copy(), "names": data["census_names"].tolist(),
                  "f": data["conditional"].copy(), "source": "new matched hot family",
                  "massive_rho": data["massive_rho"].copy(),
                  "massive_pbar": data["massive_pbar"].copy(),
                  **cols}
    output["time_Gyr"] = output["elapsed_s"] / (YEAR_S * 1e9)
    p = output["Pi_m"][0]
    output["legend"] = f"hot Πₘ₀={p:.3g} (L{output['model']['ellmax']})"
    return output, meta


def _load_nuclear(names, cases):
    path = HERE / "STRONG_PI_M_NUCLEAR_HISTORIES.npz"
    with np.load(path, allow_pickle=False) as data:
        keys = data["case_names"].tolist()
        logs, elapsed = data["log_T_n"].copy(), data["elapsed_s"].copy()
    if set(keys) != set(names) or logs.shape != (4, 257, 2):
        raise ValueError("four exact-name nominal nuclear histories required")
    nuclear = {}
    for j, name in enumerate(keys):
        if not np.allclose(cases[name]["elapsed_s"], elapsed[j], rtol=3e-15, atol=1e-8):
            raise ValueError("nuclear elapsed time join failed " + name)
        if np.isnan(logs[j]).any() or np.isposinf(logs[j]).any():
            raise ValueError("invalid log T/n")
        nuclear[name] = logs[j]
    return nuclear


def _validate(contract, names, cases, meta):
    anchor = cases[names[0]]
    tolerance = contract["acceptance"]["initial_fixed_zero_axes_absolute"]
    x, z = anchor["x"], anchor["z"]
    for entry in contract["cases"]:
        name = entry["case"]
        case = cases[name]
        if len(case["x"]) != 257 or not np.array_equal(case["x"], x) or not np.array_equal(case["z"], z):
            raise ValueError("common x,z failed " + name)
        if case["Y"].shape != (257, 21) or case["f"].shape != (257, 9):
            raise ValueError("census/fraction dimensions " + name)
        if case["names"] != draw._load_atomic("quotient_L16_S0_Am0_Ar0")["names"]:
            raise ValueError("ionic census mapping " + name)
        if not np.isfinite(case["Y"]).all() or not np.isfinite(case["f"]).all():
            raise ValueError("nonfinite saved census " + name)
        if (case["massive_rho"].shape != (257,) or case["massive_pbar"].shape != (257,)
                or not np.isfinite(case["massive_rho"]).all()
                or not np.isfinite(case["massive_pbar"]).all()):
            raise ValueError("massive stress context shape/finite " + name)
        if any(abs(case[k][0]) > tolerance for k in ("signed_Sigma", "Pi_r", "P_r")):
            raise ValueError("initial other axes not fixed " + name)
        target = entry["Pi_m0"]
        if abs(case["Pi_m"][0] - target) > contract["acceptance"]["actual_Pi_target_absolute"]:
            raise ValueError("initial physical Pi_m target " + name)
        if np.any(np.diff(case["time_Gyr"]) <= 0) or abs(case["time_Gyr"][0]) > 1e-12:
            raise ValueError("elapsed time order " + name)
        model = case["model"]
        if abs(model["mass_fraction"]-.3)>1e-14 or abs(model["mass_over_Tref"]-3)>1e-14:
            raise ValueError("strong-family identity " + name)
    nominal = [cases[name] for name in names]
    if np.any(np.diff([c["Pi_m"][0] for c in nominal]) <= 0):
        raise ValueError("positive Pi_m ordering")
    relative = contract["acceptance"]["nominal_family_rho_pbar_number_relative"]
    for c in nominal:
        for key in ("massive_rho", "massive_pbar", "matter_number_comoving"):
            if abs(c[key][0]/anchor[key][0]-1) > relative:
                raise ValueError("unmatched initial massive isotropic moment " + c["case"] + "/" + key)
        for key in ("H_per_s", "nB_m3", "T_K"):
            if abs(c[key][0]/anchor[key][0]-1) > relative:
                raise ValueError("unmatched initial background " + c["case"] + "/" + key)
        if not np.allclose(c["Y"][0], anchor["Y"][0], rtol=relative, atol=1e-16):
            raise ValueError("unmatched initial ionic fractions " + c["case"])
    fine = cases[contract["cases"][4]["case"]]
    fine_relative = contract["acceptance"]["quadrature_pressure_relative_nominal_control_max"]
    if (abs(fine["massive_pbar"][0]/nominal[-1]["massive_pbar"][0]-1) > fine_relative
            or abs(fine["massive_rho"][0]/nominal[-1]["massive_rho"][0]-1) > fine_relative):
        raise ValueError("L24 control initial isotropic moment differs beyond tolerance")
    return {"common_x_z": "pass", "physical_initial_Pi_m_targets": "pass",
            "initial_Sigma_Pi_r": "pass", "strong_family_identity": "pass",
            "matched_initial_isotropic_moments_and_gas": "pass",
            "fine_control_initial_isotropic_moments": "pass",
            "old_82_background_ivps_rerun": 0}


def _max_delta(case, baseline):
    difference = case["f"] - baseline["f"]
    k, q = np.unravel_index(int(np.argmax(np.abs(difference))), difference.shape)
    return {"max_abs_delta_f": float(abs(difference[k, q])),
            "channel": draw.CONDITIONAL[q], "z": float(case["z"][k]),
            "signed_delta_f": float(difference[k, q]), "index": int(k)}


def _control_plot(nominal, fine, baseline, discrepancy):
    fig, axs = plt.subplots(3, 3, figsize=(13, 11), layout="constrained")
    for j, channel in enumerate(draw.CONDITIONAL):
        ax = axs.flat[j]
        difference = nominal["f"][:, j] - fine["f"][:, j]
        ax.plot(nominal["z"], difference, color="#b02c56", lw=1.5,
                label="L16 − L24 control")
        ax.axhline(0., color="gray", lw=.7)
        peak = np.max(abs(difference))
        draw._signed_axis(ax,[difference])
        ax.text(.03,.95,f"max |Δcontrol|={peak:.2e}",transform=ax.transAxes,
                fontsize=8,va="top")
        ax.set_title(channel)
        ax.set_ylabel("signed numerical-control difference")
        draw._format_axis(ax,"redshift")
    response = _max_delta(nominal, baseline)
    fig.suptitle(TITLE+" — strongest case L16 vs tighter L24 control\n"
                 f"Matched-hot-anchor peak response {response['max_abs_delta_f']:.3e}; "
                 f"maximum observed control discrepancy {discrepancy:.3e}; "
                 "control scale is not a certified error bound", fontsize=12)
    return draw._save_original(fig,"strong_pi_m_control_comparison")


def _stress_plot(cases, baseline):
    fig, axs = plt.subplots(4, 2, figsize=(12.8, 12.4), layout="constrained")
    specifications = (
        ("signed_Sigma", "signed Σ"), ("P_m", "signed Pₘ"),
        ("Pi_m", "Πₘ stress norm (nonnegative)"), ("P_r", "signed Pᵣ"),
    )
    for k,(key,label) in enumerate(specifications):
        ax=axs.flat[k]
        ax.axhline(0,color="gray",lw=.7)
        values=[]
        for j,c in enumerate(cases):
            value=c[key]
            if key=="Pi_m":
                ax.plot(c["z"],np.where(value>0,value,np.nan),color=draw.COLORS[j],lw=1.5)
            else:
                ax.plot(c["z"],value,color=draw.COLORS[j],lw=1.5)
            values.append(value)
        if key=="Pi_m":draw._positive_axis(ax,values)
        else:draw._signed_axis(ax,values)
        ax.set_ylabel(label);draw._format_axis(ax,"redshift")
    ax=axs.flat[4]
    photon_values=[]
    for j,c in enumerate(cases):
        ax.plot(c["z"],c["P_gamma"],color=draw.COLORS[j],lw=1.4)
        ax.plot(c["z"],c["P_nu"],color=draw.COLORS[j],ls="--",lw=1.4)
        photon_values.extend((c["P_gamma"],c["P_nu"]))
    draw._signed_axis(ax,photon_values)
    ax.set_ylabel("Pγ solid; Pν dashed");draw._format_axis(ax,"redshift")
    ax=axs.flat[5]
    hubble_values=[]
    for j,c in enumerate(cases):
        value=c["H_per_s"]/baseline["H_per_s"]-1
        ax.plot(c["z"],value,
                color=draw.COLORS[j],lw=1.5)
        hubble_values.append(value)
    ax.axhline(0,color="gray",lw=.7)
    draw._signed_axis(ax,hubble_values)
    ax.set_ylabel("H/H_hot_zero − 1");draw._format_axis(ax,"redshift")
    ax=axs.flat[6]
    time_values=[]
    for j,c in enumerate(cases):
        value=c["elapsed_s"]/(YEAR_S*1e6)
        ax.plot(c["z"],np.where(value>0,value,np.nan),color=draw.COLORS[j],lw=1.5)
        time_values.append(value)
    draw._positive_axis(ax,time_values)
    ax.set_ylabel("Elapsed proper time (Myr; log scale)");draw._format_axis(ax,"redshift")
    ax=axs.flat[7]
    massive_values=[]
    for j,c in enumerate(cases):
        ax.plot(c["z"],c["massive_rho"],color=draw.COLORS[j],lw=1.4)
        ax.plot(c["z"],c["massive_pbar"],color=draw.COLORS[j],ls="--",lw=1.4)
        massive_values.extend((c["massive_rho"],c["massive_pbar"]))
    draw._positive_axis(ax,massive_values)
    ax.set_ylabel("massive ρ solid; p̄ dashed\nsolver normalized units (log scale)")
    draw._format_axis(ax,"redshift")
    handles=[plt.Line2D([0],[0],color=draw.COLORS[j],lw=2,label=c["legend"])
             for j,c in enumerate(cases)]
    fig.legend(handles=handles,loc="outside lower center",ncol=2,fontsize=8)
    fig.suptitle(TITLE+" — signed stresses, stress norm, geometry, and massive moments\n"
                 "Other axes and isotropic massive moments fixed initially; histories may differ", fontsize=12)
    return draw._save_original(fig,"strong_pi_m_stress_redshift")


def main():
    wall0, cpu0 = time.perf_counter(), time.process_time()
    contract = json.loads(CONTRACT.read_text())
    if contract["status"] != "FROZEN_FOR_IMPLEMENTATION":
        raise ValueError("strong contract not frozen")
    names = [entry["case"] for entry in contract["cases"][:4]]
    control_name = contract["cases"][4]["case"]
    cases, meta = {}, {}
    for name in names + [control_name]:
        cases[name], meta[name] = _load(name)
    checks = _validate(contract, names, cases, meta)
    nuclear = _load_nuclear(names, cases)
    baseline = cases[names[0]]
    nominal = [cases[name] for name in names]
    draw.set_display_reference(baseline)
    draw._save_original = draw._save
    draw._save = _context_save
    draw.HERE = HERE
    records = []
    for kind in contract["figures"]["required"]:
        if kind.startswith("strong_pi_m_totals_"):
            files = draw.plot_totals(nominal,nuclear,"strong_pi_m",kind.removeprefix("strong_pi_m_totals_"))
            # Shared plot utility calls isotope totals "nuclei"; the frozen
            # strong-family contract names this required design "totals".
            renamed=[]
            for filename in files:
                target=filename.replace("strong_pi_m_nuclei_", "strong_pi_m_totals_",1)
                (HERE/filename).replace(HERE/target)
                renamed.append(target)
            files=renamed
        elif kind.startswith("strong_pi_m_ions_"):
            files = draw.plot_ions(nominal,nuclear,"strong_pi_m",kind.removeprefix("strong_pi_m_ions_"))
        elif kind == "strong_pi_m_ionic_difference_redshift":
            files = draw.plot_fraction_differences(nominal,baseline,"strong_pi_m","redshift")
        elif kind == "strong_pi_m_stress_redshift":
            files = _stress_plot(nominal,baseline)
        elif kind == "strong_pi_m_control_comparison":
            fine = cases[control_name]
            discrepancy = float(np.max(abs(nominal[-1]["f"]-fine["f"])))
            files = _control_plot(nominal[-1],fine,baseline,discrepancy)
        else:
            raise ValueError("unknown required figure " + kind)
        records.append({"group":"new matched semi-relativistic family", "kind":kind,
                        "files":files,"cases":names + ([control_name] if "control" in kind else []),
                        "matched_hot_baseline":names[0]})
    if len(records) != 7 or any(not (HERE/f).is_file() for r in records for f in r["files"]):
        raise AssertionError("seven figure pairs incomplete")
    control_error = np.abs(nominal[-1]["f"]-cases[control_name]["f"])
    e_control = float(np.max(control_error))
    inherited_ref = 3.3929270504273745e-9
    ref = max(e_control, inherited_ref)
    metrics = {}
    for c in nominal:
        peak = _max_delta(c,baseline)
        ratio = peak["max_abs_delta_f"]/ref
        classification = ("matched zero anchor" if c is baseline else
                          "separated from observed discrepancy" if ratio >= 10 else
                          "unresolved at observed accuracy" if ratio < 1 else "numerically marginal")
        by_channel={}
        for j,channel in enumerate(draw.CONDITIONAL):
            difference=c["f"][:,j]-baseline["f"][:,j]
            at=int(np.argmax(np.abs(difference)))
            by_channel[channel]={"max_abs_delta_f":float(abs(difference[at])),
                                 "signed_delta_f":float(difference[at]),
                                 "z":float(c["z"][at]),
                                 "endpoint_signed_delta_f":float(difference[-1])}
        metrics[c["case"]] = {**peak,"amplitude_over_observed_reference":ratio,
                              "classification":classification,
                              "per_channel":by_channel,
                              "endpoint_tau_shift":float(c["tau_T"][-1]-baseline["tau_T"][-1]),
                              "endpoint_electron_per_baryon_shift":float(c["ne_m3"][-1]/c["nB_m3"][-1] - baseline["ne_m3"][-1]/baseline["nB_m3"][-1])}
    f_peak = metrics[names[-1]]
    ch = draw.CONDITIONAL.index(f_peak["channel"])
    at = f_peak["index"]
    nominal_peak = float(nominal[-1]["f"][at,ch]-baseline["f"][at,ch])
    control_peak = float(cases[control_name]["f"][at,ch]-baseline["f"][at,ch])
    metrics["numerical_control"] = {"max_abs_conditional_difference":e_control,
        "inherited_cold_family_observed_reference":inherited_ref,
        "combined_observed_reference":ref,
        "reference_is_not_certified_error_bound":True,
        "peak_response_L16":nominal_peak,"peak_response_L24":control_peak,
        "leading_sign_agreement":bool(np.sign(nominal_peak)==np.sign(control_peak)),
        "peak_profile_difference":abs(nominal_peak-control_peak),
        "per_channel_max_abs_difference":{label:float(np.max(control_error[:,j])) for j,label in enumerate(draw.CONDITIONAL)}}
    (HERE/"GROUP_METRICS.json").write_text(json.dumps(metrics,indent=2)+"\n")
    with (HERE/"CASE_TABLE.csv").open("w",newline="") as f:
        rows=[]
        for j,c in enumerate(cases.values()):
            rows.append({"case":c["case"],"role":contract["cases"][j]["role"],
                "mass_fraction":c["model"]["mass_fraction"],
                "mass_over_Tref":c["model"]["mass_over_Tref"],
                "A_m":c["model"]["A_m"],
                "Sigma0":float(c["signed_Sigma"][0]),
                "Pi_m0":float(c["Pi_m"][0]),"Pi_r0":float(c["Pi_r"][0]),
                "massive_rho0":float(c["massive_rho"][0]),
                "massive_pbar0":float(c["massive_pbar"][0]),
                "H0_per_s":float(c["H_per_s"][0]),
                "elapsed_end_Gyr":float(c["time_Gyr"][-1])})
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    manifest={"contract":"../STRONG_PI_M_CONTRACT.json", "family":TITLE,
              "figure_count":len(records),"visual_file_count":14,
              "matched_zero_anchor":names[0],"nominal_cases":names,
              "control_case":control_name,"figures":records,"checks":checks,
              "resources":{"wall_s":time.perf_counter()-wall0,"cpu_s":time.process_time()-cpu0}}
    (HERE/"FIGURE_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    draw._write_gallery(records)
    gallery = HERE/"GALLERY.html"
    content=gallery.read_text().replace("Fixed-initial-axis nucleus and ion dossier",
        "New matched semi-relativistic matter-stress family: f_m=0.3, m/Tref=3")
    content=content.replace("See CASE_TABLE.csv and FIGURE_MANIFEST.json for exact case identity.",
        "All response differences use this family's hot Pi_m=0 anchor, never the old cold-family anchor. "
        "See CASE_TABLE.csv and FIGURE_MANIFEST.json for exact case identity.")
    gallery.write_text(content)
    print(json.dumps({k:v for k,v in manifest.items() if k!="figures"},indent=2))


if __name__ == "__main__":
    main()
