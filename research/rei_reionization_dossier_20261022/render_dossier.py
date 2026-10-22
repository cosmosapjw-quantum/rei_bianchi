"""Render fixed-axis nuclear and ionic trajectories from immutable NPZ histories.

The frozen PLOT_CONTRACT.json selects all cases. This script only reads saved
backgrounds and the separately admitted conditional nuclear T/n histories.
"""
from __future__ import annotations

import csv
import html
import json
import math
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
import numpy as np

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
OLD = RESEARCH/"rei_isotope_quotient_pilot_20261022"/"pilot"/"results"
NETWORK = RESEARCH/"rei_tritium_production_audit_20261022"/"NUCLEAR_NETWORK_HISTORIES.npz"
CONTRACT = HERE/"PHYSICS_PLOT_CONTRACT.json"
SPECIES = ("n", "H1", "D", "T", "He3", "He4", "Li6", "Li7")
IONS = {"H1": 2, "D": 2, "He3": 3, "He4": 3, "Li6": 4, "Li7": 4}
CONDITIONAL = ("H I", "H II", "He I", "He II", "He III",
               "Li I", "Li II", "Li III", "Li IV")
COLORS = plt.get_cmap("tab10").colors
STYLES = ("-", "--", ":", "-.")
YEAR_S = 365.25*86400
DISPLAY = json.loads((HERE/"DISPLAY_CONTRACT.json").read_text())
_CURRENT_REFERENCE = None
_CURRENT_REFERENCE_ID = None


def set_display_reference(case: dict) -> None:
    global _CURRENT_REFERENCE, _CURRENT_REFERENCE_ID
    _CURRENT_REFERENCE, _CURRENT_REFERENCE_ID = case, case["case"]
    z = case["z"]
    t = case["elapsed_s"]/(YEAR_S*1e6)
    if (not np.isfinite(z).all() or not np.isfinite(t).all()
            or not np.all(np.diff(z) < 0) or not np.all(np.diff(t) > 0)):
        raise ValueError("reference clock is not finite and strictly monotonic")
    # Endpoints and an interior saved knot exercise both interpolation directions.
    for index in (0, len(z)//2, len(z)-1):
        mapped = np.interp(z[index], z[::-1], t[::-1])
        reverse = np.interp(t[index], t, z)
        if abs(mapped-t[index]) > 1e-9 or abs(reverse-z[index]) > 1e-12:
            raise ValueError("reference-clock knot mapping")


def _abundance_axis(ax, ionic=False):
    # Curves already contain log10(Y): a second logarithmic transform would
    # destroy the extremely small but representable nuclear inventories.
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: rf"$10^{{{value:g}}}$"))
    ax.set_ylabel("Y_Aq = n_Aq/n_B (log scale)" if ionic else
                  "Y = n_species/n_B (log scale)")


def _signed_axis(ax, values, fraction=False):
    finite = np.concatenate([np.asarray(v)[np.isfinite(v)].ravel() for v in values])
    magnitude = float(np.max(abs(finite))) if finite.size else 0.
    threshold = (DISPLAY["y_axes"]["signed"]["fraction_difference_linthresh"]
                 if fraction else 10.**(math.floor(math.log10(magnitude))-2)
                 if magnitude else 1e-12)
    ax.set_yscale("symlog", base=10, linthresh=threshold)
    ax.text(.98,.04, f"linear |y| ≤ {threshold:.2e}", ha="right", va="bottom",
            transform=ax.transAxes, fontsize=7.2,
            bbox={"facecolor":"white","alpha":.75,"edgecolor":"none"})
    if magnitude == 0:
        ax.set_ylim(-2*threshold,2*threshold)
        ax.text(.04,.52,"exact zero in saved model",transform=ax.transAxes,fontsize=8)


def _positive_axis(ax, values, zero_label="Exact zero omitted on log axis"):
    finite=np.concatenate([np.asarray(v)[np.isfinite(v)].ravel() for v in values])
    positive=finite[finite>0]
    if positive.size:
        ax.set_yscale("log", base=10)
        if np.any(finite == 0):
            ax.text(.03,.07,zero_label,transform=ax.transAxes,fontsize=7.2,
                    bbox={"facecolor":"white","alpha":.8,"edgecolor":"none"})
    else:
        ax.text(.04,.5,"Exact zero in saved model",transform=ax.transAxes,fontsize=8)


def _load_atomic(case: str) -> dict:
    path = OLD/(case+".npz")
    if not path.exists():
        path = HERE/"results"/(case+".npz")
    meta = json.loads(path.with_suffix(".json").read_text())
    with np.load(path, allow_pickle=False) as d:
        cn = d["census_names"].tolist()
        dn = d["diagnostic_names"].tolist()
        return {"case": case, "model": meta["model"], "initial_axes": meta["initial_axes"],
                "x": d["x"].copy(), "z": d["z"].copy(),
                "Y": d["census"].copy(), "names": cn,
                "f": d["conditional"].copy(),
                "time_Gyr": d["diagnostics"][:, dn.index("elapsed_s")].copy()/(YEAR_S*1e9),
                "elapsed_s": d["diagnostics"][:, dn.index("elapsed_s")].copy(),
                "T_K": d["diagnostics"][:, dn.index("T_K")].copy(),
                "signed_Sigma": d["diagnostics"][:, dn.index("signed_Sigma")].copy(),
                "Sigma_F": d["diagnostics"][:, dn.index("Sigma_F")].copy(),
                "P_m": d["diagnostics"][:, dn.index("P_m")].copy(),
                "P_r": d["diagnostics"][:, dn.index("P_r")].copy(),
                "P_gamma": d["diagnostics"][:, dn.index("P_gamma")].copy(),
                "P_nu": d["diagnostics"][:, dn.index("P_nu")].copy(),
                "H_per_s": d["diagnostics"][:, dn.index("H_per_s")].copy(),
                "Pi_m": d["diagnostics"][:, dn.index("Pi_m")].copy(),
                "Pi_r": d["diagnostics"][:, dn.index("Pi_r")].copy(),
                "Pi_total": d["diagnostics"][:, dn.index("Pi_total")].copy(),
                "source": "new_case" if path.parent == HERE/"results" else "saved_82"}


def _nuclear_lookup() -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    with np.load(NETWORK, allow_pickle=False) as d:
        names = d["case_names"].tolist()
        logs = d["log_T_n"].copy()
        times = d["elapsed_s"].copy()
    if len(names) != 82 or len(set(names)) != 82:
        raise ValueError("conditional nuclear case registry mismatch")
    out = {name: logs[j] for j, name in enumerate(names)}
    timeline = {name: times[j] for j, name in enumerate(names)}
    extra_path = HERE/"NEW_CASE_NUCLEAR_HISTORIES.npz"
    if extra_path.exists():
        with np.load(extra_path, allow_pickle=False) as d:
            extra_names = d["case_names"].tolist()
            extra_logs = d["log_T_n"].copy()
            extra_times = d["elapsed_s"].copy()
        if extra_logs.shape != (len(extra_names), 257, 2):
            raise ValueError("new-case nuclear history shape")
        for j, name in enumerate(extra_names):
            if name in out:
                raise ValueError("duplicate old/new nuclear case name")
            out[name] = extra_logs[j]
            timeline[name] = extra_times[j]
    return out, timeline


def _axis(case: dict, which: str) -> np.ndarray:
    return case["z"] if which == "redshift" else case["elapsed_s"]/(YEAR_S*1e6)


def _format_axis(ax, which: str):
    if which == "redshift":
        ax.invert_xaxis()
        ax.set_xlabel("Redshift z")
    else:
        ax.set_xlabel("Proper elapsed time since z=20 (Myr)")
    ax.grid(alpha=.18)
    if _CURRENT_REFERENCE is None:
        return
    subplot = ax.get_subplotspec()
    if subplot is None or subplot.rowspan.start != 0:
        return
    z=_CURRENT_REFERENCE["z"]
    t=_CURRENT_REFERENCE["elapsed_s"]/(YEAR_S*1e6)
    if which == "redshift":
        # Space physical positions on the drawn z axis, then read the saved
        # reference clock. Equal time ticks bunch near z=2 and overlap.
        positions=np.linspace(float(z[0]),float(z[-1]),5)
        values=np.interp(positions,z[::-1],t[::-1])
        valid=(positions>=min(z)) & (positions<=max(z))
        labels=[f"{v:.0f}" for v in values[valid]]
        title="Reference elapsed time (Myr)"
    else:
        # Space physical positions on the time axis; interpolate the saved
        # reference z at each time and never extend past the reference support.
        positions=np.linspace(float(t[0]),float(t[-1]),5)
        values=np.interp(positions,t,z)
        valid=(positions>=t[0]) & (positions<=t[-1])
        labels=[f"{v:.1f}" for v in values[valid]]
        title="Reference redshift z"
    top=ax.twiny()
    top.set_xlim(ax.get_xlim())
    top.set_xticks(positions[valid],labels)
    top.set_xlabel(title,fontsize=8,labelpad=3)
    top.tick_params(axis="x",labelsize=7,pad=1)
    ax.set_title(ax.get_title(),pad=39)


def _save(fig, stem: str) -> list[str]:
    if _CURRENT_REFERENCE_ID is not None and fig._suptitle is not None:
        title=fig._suptitle.get_text()
        fig._suptitle.set_text(title+"\nAuxiliary axis uses reference clock: "
                               +_CURRENT_REFERENCE_ID+"; other cases have different z(t).")
        fig._suptitle.set_fontsize(10.2)
    output = []
    for ext in ("png", "pdf"):
        name = stem+"."+ext
        fig.savefig(HERE/name, dpi=155)
        if (HERE/name).stat().st_size < 1000:
            raise IOError(f"incomplete rendered figure {name}")
        output.append(name)
    plt.close(fig)
    return output


def plot_totals(cases: list[dict], nuclear: dict, label: str, which: str) -> list[str]:
    fig, axs = plt.subplots(4, 2, figsize=(12.4, 13.5), layout="constrained")
    for k, species in enumerate(SPECIES):
        ax = axs.flat[k]
        finite_logs = []
        for j, case in enumerate(cases):
            if species in ("T", "n"):
                log_y = nuclear[case["case"]][:, 0 if species == "T" else 1]/math.log(10)
                source = "conditional nuclear total"
            else:
                cols = [i for i, name in enumerate(case["names"])
                        if name.startswith(species+"_")]
                y = case["Y"][:, cols].sum(axis=1)
                log_y = np.full(y.shape, np.nan)
                positive = y > 0
                log_y[positive] = np.log10(y[positive])
                source = "inherited atomic isotope total"
            good = np.isfinite(log_y)
            finite_logs.extend(log_y[good].tolist())
            ax.plot(_axis(case, which)[good], log_y[good], color=COLORS[j], lw=1.6)
        ax.set_title(f"{species} — {source}", fontsize=10)
        if species in ("T", "n"):
            ax.text(.03, .08, "Initial total = 0; omitted from log axis",
                    transform=ax.transAxes, fontsize=8,
                    bbox={"facecolor": "white", "alpha": .85, "edgecolor": "none"})
        elif finite_logs and max(finite_logs)-min(finite_logs) < 1e-4:
            # Atomic isotope totals are passive reservoirs here. Avoid a floating
            # offset that magnifies roundoff into an apparent physical variation.
            center = float(np.median(finite_logs))
            ax.set_ylim(center-.02, center+.02)
            ax.ticklabel_format(axis="y", style="plain", useOffset=False)
            ax.text(.03, .08, "Inherited passive isotope total",
                    transform=ax.transAxes, fontsize=8,
                    bbox={"facecolor": "white", "alpha": .85, "edgecolor": "none"})
        _format_axis(ax, which)
        _abundance_axis(ax)
    handles = [Line2D([0], [0], color=COLORS[j], lw=2, label=c["legend"])
               for j, c in enumerate(cases)]
    fig.legend(handles=handles, loc="outside lower center", ncol=2, fontsize=8)
    fig.suptitle(f"{label}: isotope totals versus {which}\n"
                 "T/n: all-bare, instant-thermalization passive nuclear totals; "
                 "no charge projection", fontsize=13)
    return _save(fig, f"{label}_nuclei_{which}")


def plot_ions(cases: list[dict], nuclear: dict, label: str, which: str) -> list[str]:
    fig, axs = plt.subplots(4, 2, figsize=(12.4, 13.5), layout="constrained")
    for k, species in enumerate(SPECIES):
        ax = axs.flat[k]
        if species in ("T", "n"):
            for j, case in enumerate(cases):
                vals = nuclear[case["case"]][:, 0 if species == "T" else 1]/math.log(10)
                good = np.isfinite(vals)
                ax.plot(_axis(case, which)[good], vals[good], color=COLORS[j], lw=1.6)
            ax.set_title(f"{species}: nuclear total only", fontsize=10)
            ax.text(.03, .08, ("Initial T=0; T charge states unresolved; "
                                "old T₀/T₁ hard-zero" if species == "T" else
                                "Initial n=0; old n₀ hard-zero"),
                    transform=ax.transAxes, fontsize=8,
                    bbox={"facecolor": "white", "alpha": .85, "edgecolor": "none"})
        else:
            exact_zero = []
            for charge in range(IONS[species]):
                column = cases[0]["names"].index(f"{species}_{charge}")
                if all(np.all(case["Y"][:, column] == 0) for case in cases):
                    exact_zero.append(charge)
                    continue
                for j, case in enumerate(cases):
                    y = case["Y"][:, column]
                    good = y > 0
                    ax.plot(_axis(case, which)[good], np.log10(y[good]),
                            color=COLORS[j], ls=STYLES[charge], lw=1.3)
            ax.set_title(f"{species}: saved ionic census Y_q", fontsize=10)
            if exact_zero:
                ax.text(.03, .08, "Saved-model exact zero: charge "
                        + ", ".join(map(str, exact_zero)),
                        transform=ax.transAxes, fontsize=8,
                        bbox={"facecolor": "white", "alpha": .85,
                              "edgecolor": "none"})
        _format_axis(ax, which)
        _abundance_axis(ax, ionic=species not in ("n","T"))
    case_handles = [Line2D([0], [0], color=COLORS[j], lw=2, label=c["legend"])
                    for j, c in enumerate(cases)]
    state_handles = [Line2D([0], [0], color="black", ls=STYLES[q],
                            label=f"ionic charge {q}") for q in range(4)]
    fig.legend(handles=case_handles+state_handles, loc="outside lower center",
               ncol=3, fontsize=8)
    fig.suptitle(f"{label}: ionic census and conditional T/n versus {which}\n"
                 "Inherited atomic ions; T/n all-bare instant-thermalized passive totals, "
                 "no T charge projection", fontsize=13)
    return _save(fig, f"{label}_ions_{which}")


def plot_fraction_differences(cases: list[dict], baseline: dict,
                              label: str, which: str,
                              control_reference: float | None = None) -> list[str]:
    """Actual signed change in conditional ionic fractions, never rescaled."""
    fig, axs = plt.subplots(3, 3, figsize=(13, 11), layout="constrained")
    for k, name in enumerate(CONDITIONAL):
        ax = axs.flat[k]
        ax.axhline(0., color="#777777", lw=.7)
        if control_reference is not None:
            for sign in (-1, 1):
                ax.axhline(sign*control_reference, color="#777777", ls=":", lw=.8)
        extrema = []
        displayed=[]
        for j, case in enumerate(cases):
            delta = case["f"][:, k]-baseline["f"][:, k]
            ax.plot(_axis(case, which), delta, color=COLORS[j], lw=1.5)
            extrema.append(float(np.max(abs(delta))))
            displayed.append(delta)
        extent = max(extrema)
        if extent or control_reference:
            display = max(extent, control_reference or 0.)
            ax.set_ylim(-1.12*display, 1.12*display)
            ax.text(.02, .96, f"max |Δ|={extent:.2e}", transform=ax.transAxes,
                    va="top", fontsize=8)
        _signed_axis(ax,displayed,fraction=True)
        ax.set_title(name)
        _format_axis(ax, which)
        ax.set_ylabel("Δ conditional fraction")
    handles = [Line2D([0], [0], color=COLORS[j], lw=2, label=c["legend"])
               for j, c in enumerate(cases)]
    fig.legend(handles=handles, loc="outside lower center", ncol=2, fontsize=8)
    note = (f"Dotted ±{control_reference:.2e}: observed angular-control scale, not error bound; "
            "matter response unresolved" if control_reference is not None else
            "Signed absolute differences; panel scales stated individually")
    fig.suptitle(f"{label}: ionic-fraction change from saved zero-axis reference\n"
                 + note, fontsize=13)
    return _save(fig, f"{label}_ionic_difference_{which}")


def plot_stress(cases: list[dict], baseline: dict, label: str) -> list[str]:
    fields = (("signed_Sigma", "signed Σ"), ("P_m", "signed Pₘ"),
              ("P_r", "signed Pᵣ"))
    fig, axs = plt.subplots(3, 2, figsize=(12.8, 10), layout="constrained")
    for k, (key, name) in enumerate(fields):
        ax = axs.flat[k]
        ax.axhline(0., color="#777777", lw=.7)
        values=[]
        for j, case in enumerate(cases):
            ax.plot(case["z"], case[key], color=COLORS[j], lw=1.5)
            values.append(case[key])
        _signed_axis(ax,values)
        ax.set_ylabel(name)
        _format_axis(ax, "redshift")
    photons = axs.flat[3]
    photon_values=[]
    for j, case in enumerate(cases):
        photons.plot(case["z"], case["P_gamma"], color=COLORS[j], lw=1.3)
        photons.plot(case["z"], case["P_nu"], color=COLORS[j], ls="--", lw=1.3)
        photon_values.extend((case["P_gamma"],case["P_nu"]))
    _signed_axis(photons,photon_values)
    photons.set_ylabel("Pγ solid; Pν dashed")
    _format_axis(photons, "redshift")
    hubble = axs.flat[4]
    h_values=[]
    for j, case in enumerate(cases):
        value=case["H_per_s"]/baseline["H_per_s"]-1
        hubble.plot(case["z"], value,
                    color=COLORS[j], lw=1.5)
        h_values.append(value)
    hubble.axhline(0., color="#777777", lw=.7)
    _signed_axis(hubble,h_values)
    hubble.set_ylabel("H/H_baseline − 1")
    _format_axis(hubble, "redshift")
    elapsed = axs.flat[5]
    time_values=[]
    for j, case in enumerate(cases):
        value=case["elapsed_s"]/(YEAR_S*1e6)
        elapsed.plot(case["z"],np.where(value>0,value,np.nan), color=COLORS[j], lw=1.5)
        time_values.append(value)
    _positive_axis(elapsed,time_values)
    elapsed.set_ylabel("Proper elapsed time (Myr; log scale)")
    _format_axis(elapsed, "redshift")
    handles = [Line2D([0], [0], color=COLORS[j], lw=2, label=c["legend"])
               for j, c in enumerate(cases)]
    fig.legend(handles=handles, loc="outside lower center", ncol=2, fontsize=8)
    fig.suptitle(f"{label}: signed stress and geometry versus redshift\n"
                 "Fixed other parameters refer to initial values, not entire histories", fontsize=13)
    return _save(fig, f"{label}_stress_redshift")


def _case_row(c: dict) -> dict:
    start = lambda k: float(c[k][0])
    return {"case": c["case"], "source": c["source"],
            "signed_Sigma0": start("signed_Sigma"), "Sigma_F0": start("Sigma_F"),
            "P_m0": start("P_m"), "Pi_m0": start("Pi_m"),
            "P_gamma0": start("P_gamma"), "P_nu0": start("P_nu"),
            "P_r0": start("P_r"), "Pi_r0": start("Pi_r"),
            "Pi_total0": start("Pi_total"),
            "elapsed_time_end_Gyr": float(c["time_Gyr"][-1]),
            "metadata_Sigma_F0": float(c["model"]["Sigma_F0"]),
            "metadata_A_m": float(c["model"]["A_m"]),
            "metadata_A_r": float(c["model"]["A_r"])}


def _validate(contract: dict, cases: dict, nuclear: dict,
              timeline: dict) -> list[dict]:
    if contract["status"] != "FROZEN_FOR_IMPLEMENTATION":
        raise ValueError("plot contract is not frozen")
    rows = []
    reference = cases[contract["baseline_case"]]
    x = reference["x"]
    z = reference["z"]
    tol = contract["acceptance"]["initial_fixed_axis_absolute_tolerance"]
    expected_names = contract["observables"]["census_names"]
    for name, c in cases.items():
        if (len(c["x"]) != 257 or c["f"].shape != (257, 9)
                or c["Y"].shape != (257, 21) or c["names"] != expected_names
                or not np.array_equal(c["x"], x) or not np.array_equal(c["z"], z)):
            raise ValueError(f"atomic grid/census alignment {name}")
        if name not in nuclear or name not in timeline:
            raise ValueError(f"missing exact-name nuclear join {name}")
        if not np.array_equal(c["time_Gyr"]*YEAR_S*1e9, timeline[name]):
            # Unit conversion can lose a few low bits at cosmological times.
            if not np.allclose(c["time_Gyr"]*YEAR_S*1e9, timeline[name],
                               rtol=3e-15, atol=1e-8):
                raise ValueError(f"nuclear proper-time mismatch {name}")
        logs = nuclear[name]
        if logs.shape != (257, 2) or np.isnan(logs).any() or np.isposinf(logs).any():
            raise ValueError(f"invalid nuclear log stock {name}")
        if np.any(c["Y"] < -1e-13) or not np.isfinite(c["Y"]).all():
            raise ValueError(f"negative/nonfinite saved ionic census {name}")
        if not np.isfinite(c["f"]).all():
            raise ValueError(f"nonfinite conditional fraction {name}")
        if abs(c["time_Gyr"][0]) > 1e-12 or np.any(np.diff(c["time_Gyr"]) <= 0):
            raise ValueError(f"proper-time grid invalid {name}")
        for species in IONS:
            cols = [c["names"].index(f"{species}_{q}") for q in range(IONS[species])]
            total = c["Y"][:, cols].sum(axis=1)
            if abs(total[-1]-total[0]) > 1e-8*max(total[0], 1e-30):
                raise ValueError(f"inherited isotope number drift {name}/{species}")
        def initial_label(value):
            return "≈0" if abs(value) < tol else f"{value:+.2e}"
        c["legend"] = (f"Σ₀={initial_label(c['signed_Sigma'][0])}, "
                       f"Pₘ₀={initial_label(c['P_m'][0])}, "
                       f"Pᵣ₀={initial_label(c['P_r'][0])}")
        rows.append(_case_row(c))
    for group in contract["slices"]:
        values = []
        for name in group["cases"]:
            c = cases[name]
            for key, target in group["fixed_initial"].items():
                if abs(c[key][0]-target) > tol:
                    raise ValueError(f"fixed initial axis failed {group['id']}/{name}/{key}")
            values.append(float(c[group["varied"]][0]))
        if not (abs(values[0]) < tol and np.all(np.diff(values) > 0)):
            raise ValueError(f"positive varied-norm ordering failed {group['id']}")
    return rows


def _write_gallery(records: list[dict]) -> None:
    cards = []
    for row in records:
        src, pdf = (html.escape(x, quote=True) for x in row["files"])
        title = html.escape(f"{row['group']}: {row['kind']}")
        cards.append(f'<article><h2>{title}</h2><a href="{src}"><img src="{src}" '
                     f'alt="{title}"></a><p><a href="{pdf}">PDF</a> · '
                     f'{html.escape(", ".join(row["cases"]))}</p></article>')
    page = ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Reionization nucleus and ion dossier</title>'
            '<style>body{font:16px system-ui;margin:2rem auto;max-width:1400px;'
            'background:#f7f7f4;color:#222}h1,p{margin-left:1rem}section{display:grid;'
            'grid-template-columns:repeat(auto-fit,minmax(390px,1fr));gap:1rem}'
            'article{background:white;padding:1rem;border:1px solid #ddd}'
            'img{width:100%;height:auto}article p{font-size:12px;overflow-wrap:anywhere}'
            '</style><h1>Fixed-initial-axis nucleus and ion dossier</h1>'
            '<p>Plots use saved trajectories. T/neutron totals are conditional all-bare '
            'instant-thermalization nuclear sensitivities; T ionic partition is unresolved. '
            'See CASE_TABLE.csv and FIGURE_MANIFEST.json for exact case identity.</p>'
            '<section>'+''.join(cards)+'</section></html>')
    (HERE/"GALLERY.html").write_text(page)


def _group_metrics(groups: list[dict], cases: dict, baseline: dict,
                   nuclear: dict, contract: dict) -> dict:
    output = {}
    for group in groups:
        biggest = (-1., None, None, None)
        by_channel = {}
        for k, channel in enumerate(CONDITIONAL):
            contenders = []
            for name in group["cases"]:
                residual = cases[name]["f"][:, k]-baseline["f"][:, k]
                i = int(np.argmax(abs(residual)))
                contenders.append((float(abs(residual[i])), name,
                                   float(cases[name]["z"][i]), float(residual[i])))
            selected = max(contenders, key=lambda q: q[0])
            by_channel[channel] = {"max_abs_delta_f": selected[0],
                                   "case": selected[1], "z": selected[2],
                                   "signed_delta_f": selected[3]}
            if selected[0] > biggest[0]:
                biggest = (selected[0], channel, selected[1], selected[2])
        endpoint = {name: {"T_log10": float(nuclear[name][-1, 0]/math.log(10)),
                           "n_log10": float(nuclear[name][-1, 1]/math.log(10)),
                           "elapsed_end_Gyr": float(cases[name]["time_Gyr"][-1])}
                    for name in group["cases"]}
        control = contract["numerical_interpretation"][
            "existing_control_max_abs_conditional_discrepancy"]
        output[group["id"]] = {"cases": group["cases"],
                                "max_abs_delta_f": biggest[0],
                                "max_delta_channel": biggest[1],
                                "max_delta_case": biggest[2],
                                "max_delta_z": biggest[3],
                                "channels": by_channel,
                                "endpoint_conditional_nuclear": endpoint,
                                "matter_response_unresolved_relative_to_observed_control":
                                bool(group["id"] == "pi_m" and biggest[0] < control)}
    return output


def main():
    wall0, cpu0 = time.perf_counter(), time.process_time()
    contract = json.loads(CONTRACT.read_text())
    groups = contract["slices"]+contract["interesting_groups"]
    selected = list(dict.fromkeys(name for group in groups for name in group["cases"]))
    if len(selected) != len(set(selected)):
        raise AssertionError("case registry duplicated")
    cases = {name: _load_atomic(name) for name in selected}
    nuclear, timeline = _nuclear_lookup()
    table = _validate(contract, cases, nuclear, timeline)
    baseline = cases[contract["baseline_case"]]
    records = []
    for group in groups:
        group_cases = [cases[name] for name in group["cases"]]
        label = group["id"]
        set_display_reference(cases[DISPLAY["reference_cases"][label]])
        requested = contract["figures"]["per_primary_slice" if group in contract["slices"]
                                        else "per_interesting_group"]
        for kind in requested:
            if kind.startswith("totals_"):
                files = plot_totals(group_cases, nuclear, label, kind.split("_", 1)[1])
            elif kind.startswith("ions_"):
                files = plot_ions(group_cases, nuclear, label, kind.split("_", 1)[1])
            elif kind == "ionic_difference_redshift":
                reference = (contract["numerical_interpretation"]
                             ["existing_control_max_abs_conditional_discrepancy"]
                             if label == "pi_m" else None)
                files = plot_fraction_differences(group_cases, baseline, label,
                                                  "redshift", reference)
            elif kind == "stress_redshift":
                files = plot_stress(group_cases, baseline, label)
            else:
                raise ValueError(f"unknown figure kind {kind}")
            records.append({"group": label, "kind": kind, "files": files,
                            "cases": group["cases"], "source": "saved NPZ + admitted nuclear logs"})
    expected = contract["figures"]["total_figure_count"]
    if len(records) != expected or any(not (HERE/f).exists()
                                       for row in records for f in row["files"]):
        raise AssertionError("figure manifest incomplete")
    with (HERE/"CASE_TABLE.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)
    metrics = _group_metrics(groups, cases, baseline, nuclear, contract)
    (HERE/"GROUP_METRICS.json").write_text(json.dumps(metrics, indent=2)+"\n")
    manifest = {"contract": CONTRACT.name, "figure_count": len(records),
                "visual_file_count": sum(len(r["files"]) for r in records),
                "selected_case_count": len(selected), "figures": records,
                "field_provenance": {"atomic": "census, conditional, diagnostics",
                                     "nuclear": "log_T_n[:,0]=T; [:,1]=n",
                                     "time": "individual elapsed_s, Julian Gyr"},
                "checks": {"fixed_initial_axes": "pass",
                           "exact_case_join": "pass", "common_x_z": "pass",
                           "original_82_background_ivps_rerun": 0},
                "resources": {"wall_s": time.perf_counter()-wall0,
                              "cpu_s": time.process_time()-cpu0}}
    (HERE/"FIGURE_MANIFEST.json").write_text(json.dumps(manifest, indent=2)+"\n")
    _write_gallery(records)
    print(json.dumps({k: v for k, v in manifest.items() if k != "figures"}, indent=2))


if __name__ == "__main__":
    main()
