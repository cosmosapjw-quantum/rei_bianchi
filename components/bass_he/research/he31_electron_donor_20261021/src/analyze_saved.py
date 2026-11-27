"""Saved HE31 results to tables/figures; follows cross-directory reuse receipts."""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import tempfile
import textwrap

# Resolve a writable cache before matplotlib is imported on a shared host.
_mpl_config = Path(os.environ.get("MPLCONFIGDIR",
                    str(Path(tempfile.gettempdir())/f"he31_matplotlib_{os.getuid()}")))
try:
    _mpl_config.mkdir(parents=True, exist_ok=True)
    if not os.access(_mpl_config, os.W_OK | os.X_OK):
        raise PermissionError(str(_mpl_config))
except OSError:
    _mpl_config = Path(tempfile.mkdtemp(prefix="he31_matplotlib_"))
os.environ["MPLCONFIGDIR"] = str(_mpl_config)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from receiver import completed_result
from bindings import load_runner

SECONDS_PER_GYR = 365.25 * 86400. * 1e9


def donor_description(result):
    """Use the saved donor provenance, including future non-R15 sources."""
    provenance = result["donor"]["provenance"]
    closure = provenance["closure"]
    label = (provenance.get("label") or provenance.get("name")
             or provenance.get("model") or closure.split(";")[0].strip())
    return str(label), str(closure), provenance


def history_arrays(result):
    return {key:np.asarray([row[key] for row in result["history"]], dtype=float)
            for key in result["history"][0]}


def collect(campaign_path, results_dir):
    campaign = json.loads(Path(campaign_path).read_text())
    results_dir = Path(results_dir)
    report_path = results_dir/"RUNNER_REPORT.json"
    statuses = json.loads(report_path.read_text())["statuses"] if report_path.exists() else {}
    cases = []
    for config in campaign["cases"]:
        status = statuses.get(config["case_id"], {})
        path = Path(status.get("path", results_dir/(config["case_id"]+".json")))
        if not completed_result(config, path):
            raise ValueError("missing or changed physical case: " + config["case_id"])
        cases.append((config, json.loads(path.read_text()), str(path)))
    return cases


def save(fig, out, name):
    if not fig.get_constrained_layout():
        fig.tight_layout()
    files = []
    for ext in ("png", "svg"):
        path = out/(name+"."+ext)
        fig.savefig(path, dpi=160)
        files.append(path.name)
    plt.close(fig)
    return files


def endpoint_projection(cases, out):
    """Plot completed donor-on sweep endpoints only; never synthesize cases."""
    on = [(c,r) for c,r,p in cases if c["opacity"] == "on"]
    if len(on) < 2:
        return []
    final = {key:np.asarray([r["history"][-1][key] for c,r in on])
             for key in ("Sigma_F", "Pi_m", "Pi_r")}
    initial_pr = np.asarray([c["P_r"] for c,r in on])
    extent = float(np.max(abs(initial_pr)))
    fig, axes = plt.subplots(1,3,figsize=(13,4.4),layout="constrained")
    projections = (("Sigma_F", "Pi_m", r"$\Sigma_F$", r"$\Pi_m$"),
                   ("Sigma_F", "Pi_r", r"$\Sigma_F$", r"$\Pi_r$"),
                   ("Pi_m", "Pi_r", r"$\Pi_m$", r"$\Pi_r$"))
    for ax,(x,y,xlabel,ylabel) in zip(axes,projections):
        color = dict(c=initial_pr,cmap="coolwarm",vmin=-extent,vmax=extent) if extent else dict(color="#236B8E")
        points = ax.scatter(final[x],final[y],s=29,alpha=.8,edgecolors="none",**color)
        ax.set(xlabel="endpoint "+xlabel,ylabel="endpoint "+ylabel)
        ax.ticklabel_format(style="sci",axis="both",scilimits=(-3,3),useOffset=False)
        ax.grid(alpha=.22)
    if extent:
        fig.colorbar(points,ax=axes,label=r"signed initial $P_r$ at z=20",shrink=.83)
    end_z = sorted({float(c["z_end"]) for c,r in on})
    endpoint = f"z={end_z[0]:g}" if len(end_z) == 1 else "each declared endpoint z"
    color_note = "signed initial radiation stress sets color" if extent else "initial P_r = 0 for every point"
    fig.suptitle(f"Completed donor-on sweep: {len(on)} cases at {endpoint}\n"
                 f"Endpoint magnitudes; {color_note}",fontsize=11)
    return save(fig,out,"endpoint_projections")


def analyze(campaign, results, out):
    cases = collect(campaign, results)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size":10, "svg.fonttype":"none"})
    paths = []
    selected_on = next(((c,r,p) for c,r,p in cases if c["opacity"] == "on"), None)
    if selected_on is None:
        raise ValueError("a donor-on case is required for these sensitivity figures")
    c0, r0, _ = selected_on
    off = next((r for c,r,p in cases if c["opacity"] == "off" and all(c[k] == c0[k]
                for k in ("Sigma_F", "P_m", "P_r", "z_end", "backend"))
                and c.get("numerics") == c0.get("numerics")), None)
    data = history_arrays(r0)
    ref = None if off is None else history_arrays(off)
    if ref is not None and not np.array_equal(data["z"],ref["z"]):
        raise ValueError("paired differences require the same saved redshift grid")
    donor_label, donor_closure, provenance = donor_description(r0)
    z = data["z"]
    zi = float(z[0])
    zf = c0["z_end"]
    initial_zero = bool(data["ne_cm3"][0] == 0.)
    fig, axes = plt.subplots(1,2,figsize=(11,4.5),layout="constrained")
    positive = data["ne_cm3"] > 0
    axes[0].plot(z,np.where(positive,data["ne_cm3"],np.nan),color="#236B8E")
    axes[0].set(yscale="log", ylabel=r"proper $n_e$ [cm$^{-3}$]",xlabel="mean-volume redshift z")
    if initial_zero:
        axes[0].text(.03,.08,"Initial sample: ne = 0 (omitted on log axis)",
                     transform=axes[0].transAxes,fontsize=9)
    axes[1].plot(z,data["tau_T"],color="#A04263")
    axes[1].set(ylabel=rf"$\tau_T$ since z={zi:g} (target clock)",xlabel="mean-volume redshift z")
    for ax in axes:
        ax.set_xlim(zi,zf)
        ax.grid(alpha=.25)
    fig.suptitle(textwrap.fill("Prescribed donor: "+donor_label,100)
                 +f"\nz={zi:g} to {zf:g}; photon-only unpolarized Thomson receiver",fontsize=11)
    paths += save(fig,out,"donor_optical_depth")
    fig, axes = plt.subplots(2,3,figsize=(14,7),layout="constrained")
    keys = ("Sigma_F","Pi_m","Pi_r","P_gamma","P_nu","P_r")
    labels = (r"$\Sigma_F$",r"$\Pi_m$",r"$\Pi_r$",r"signed $P_\gamma$",r"signed $P_\nu$",r"signed $P_r=P_\gamma+P_\nu$")
    for ax,key,label in zip(axes.flat,keys,labels):
        ax.plot(z,data[key],label="Thomson on",color="#A04263",lw=1.7)
        if ref is not None:
            ax.plot(ref["z"],ref[key],label="Thomson off",color="#236B8E",ls="--",lw=1.2)
        ax.set(xlabel="mean-volume redshift z",ylabel=label,xlim=(zi,zf))
        ax.grid(alpha=.25)
    axes[0,0].legend(fontsize=9)
    fig.suptitle(f"Full40 LRS receiver, prescribed donor | initial Sigma={c0['Sigma_F']:g}, Pm={c0['P_m']:g}, Pr={c0['P_r']:g}\nMassive nonbaryonic matter and neutrinos receive no direct Thomson collision term",fontsize=11)
    paths += save(fig,out,"species_evolution")

    # Each trajectory uses its own stored target-clock elapsed time.
    elapsed_gyr = (data["elapsed_s"]-data["elapsed_s"][0])/SECONDS_PER_GYR
    ref_elapsed_gyr = None if ref is None else (ref["elapsed_s"]-ref["elapsed_s"][0])/SECONDS_PER_GYR
    fig, axes = plt.subplots(1,3,figsize=(13,4.3),layout="constrained")
    for ax,key,label in zip(axes,("Sigma_F","Pi_m","Pi_r"),labels[:3]):
        ax.plot(elapsed_gyr,data[key],label="Thomson on",color="#A04263",lw=1.7)
        if ref is not None:
            ax.plot(ref_elapsed_gyr,ref[key],label="Thomson off",color="#236B8E",ls="--",lw=1.2)
        ax.set(xlabel=f"elapsed time since z={zi:g} [Gyr]",ylabel=label)
        ax.ticklabel_format(style="sci",axis="y",scilimits=(-3,3),useOffset=False)
        ax.grid(alpha=.25)
    axes[0].legend(fontsize=9)
    fig.suptitle(f"Full40 evolution in stored receiver proper time: z={zi:g} to {zf:g}\n"
                 "Each trajectory uses its own target clock; elapsed time is not cosmic age",fontsize=11)
    paths += save(fig,out,"time_evolution")

    delta_keys = ("Sigma_F","signed_Sigma","P_m","P_gamma","P_nu","P_r")
    if ref is not None:
        fig, axes = plt.subplots(2,3,figsize=(14,7),layout="constrained")
        delta_labels = (r"$\Delta\Sigma_F$",r"$\Delta(\mathrm{signed}\ \Sigma)$",r"$\Delta P_m$",
                        r"$\Delta P_\gamma$",r"$\Delta P_\nu$",r"$\Delta P_r$")
        for ax,key,label in zip(axes.flat,delta_keys,delta_labels):
            ax.axhline(0,color=".55",lw=.7)
            ax.plot(z,data[key]-ref[key],color="#8B4D85",lw=1.7)
            ax.set(xlabel="mean-volume redshift z",ylabel=label,xlim=(zi,zf))
            ax.ticklabel_format(style="sci",axis="y",scilimits=(-3,3),useOffset=False)
            ax.grid(alpha=.25)
        fig.suptitle(f"Paired Thomson on minus off at matched saved redshift: z={zi:g} to {zf:g}\n"
                     "P_m, P_gamma, P_nu and P_r are signed; Sigma_F is the shear magnitude",fontsize=11)
        paths += save(fig,out,"paired_difference")

    paths += endpoint_projection(cases,out)
    endpoints = [dict(case_id=c["case_id"],opacity=c["opacity"],initial_Sigma=c["Sigma_F"],
                     initial_P_m=c["P_m"],initial_P_r=c["P_r"],**r["history"][-1]) for c,r,p in cases]
    with (out/"endpoints.csv").open("w",newline="") as stream:
        writer = csv.DictWriter(stream,fieldnames=list(endpoints[0]))
        writer.writeheader();writer.writerows(endpoints)
    summary = dict(status="SAVED_RESULT_ANALYSIS_COMPLETE",cases=len(cases),new_ode_calls=0,
        selected_case=c0["case_id"],selected_tau=float(data["tau_T"][-1]),
        selected_final={k:float(data[k][-1]) for k in ("Sigma_F","P_m","P_gamma","P_nu","P_r")},
        paired_final_difference=None if ref is None else {k:float(data[k][-1]-ref[k][-1]) for k in delta_keys},
        donor_identity=r0["donor"]["identity_sha256"],
        donor_label=donor_label,donor_closure=donor_closure,donor_provenance=provenance,
        initial_ne_exact_zero=initial_zero,
        selected_elapsed_gyr=float(elapsed_gyr[-1]),
        off_elapsed_gyr=None if ref is None else float(ref_elapsed_gyr[-1]),
        elapsed_time_convention=dict(origin=f"saved receiver time at z={zi:g}",
                                     seconds_per_gyr=SECONDS_PER_GYR,cosmic_age=False),
        paired_difference_grid="exact shared saved redshift; no interpolation" if ref is not None else None,
        endpoint_projection_cases=sum(c["opacity"] == "on" for c,r,p in cases),
        endpoint_projection_status="rendered" if sum(c["opacity"] == "on" for c,r,p in cases)>1 else "not rendered: only one completed donor-on case",
        campaign_path=str(Path(campaign).resolve()),results_report_path=str((Path(results)/"RUNNER_REPORT.json").resolve()),
        source_result_paths=[p for c,r,p in cases],figures=paths,
        physical_scope="one-way prescribed "+provenance["kind"]+" donor: "+donor_closure+"; existing scalar unpolarized Thomson",
        z_start=zi,z_end=zf)
    load_runner().atomic_json(out/"ANALYSIS_SUMMARY.json",summary)
    return summary


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign",type=Path,required=True)
    parser.add_argument("--results",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(analyze(args.campaign,args.results,args.out),indent=2))
