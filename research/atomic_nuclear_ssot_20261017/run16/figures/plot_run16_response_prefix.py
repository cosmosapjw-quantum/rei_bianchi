#!/usr/bin/env python3
"""Plot frozen RUN16 JSON values only. No native calls or numerical solves."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import tempfile

sys.dont_write_bytecode = True
RESPONSE_SHA = "f48c0ee0949590dfa5e1c82d355542521ca2d3df3e08c0fc6fdbcf429a2ed6fe"
PREFIX_SHA = "69cd9e459991fa7f0bf1ed6fed12bedbadffc1b5451ad0b8a380235e8f8813eb"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identify(path):
    path = Path(path)
    return {"path": str(path.resolve()), "bytes": path.stat().st_size,
            "sha256": digest(path)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--response-json", required=True, type=Path)
    ap.add_argument("--prefix-json", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    if digest(args.response_json) != RESPONSE_SHA or digest(args.prefix_json) != PREFIX_SHA:
        raise ValueError("frozen scientific input SHA mismatch")
    response = json.loads(args.response_json.read_text())
    prefix = json.loads(args.prefix_json.read_text())
    selected = [run for run in response["runs"]
                if run["energy_order"] == 16 and run["time_order"] == 32]
    if len(selected) != 1:
        raise ValueError("unique frozen E16/T32 response required")
    run = selected[0]
    breaks = [0.0, 0.6479966231660246, 0.7609039888237062, 1.0]
    groups = [[] for _ in range(3)]
    for index, item in enumerate(run["time_sensitivity"]):
        belonging = [j for j in range(3)
                     if breaks[j] <= item["left_z"] < item["right_z"] <= breaks[j+1]]
        if len(belonging) != 1 or item["fraction_of_total_sensitivity"] < 0:
            raise ValueError("frozen sensitivity row crosses a requested boundary or is negative")
        groups[belonging[0]].append((index, item))
    bars = []
    for j, group in enumerate(groups):
        if not group:
            raise ValueError("missing requested sensitivity interval")
        if group[0][1]["left_z"] != breaks[j] or group[-1][1]["right_z"] != breaks[j+1]:
            raise ValueError("sensitivity group does not fill requested interval")
        for (_, left), (_, right) in zip(group[:-1], group[1:]):
            if left["right_z"] != right["left_z"]:
                raise ValueError("gap in frozen interval rows")
        fraction = math.fsum(item["fraction_of_total_sensitivity"] for _, item in group)
        bars.append({"left_code_z": breaks[j], "right_code_z": breaks[j+1],
            "input_row_indices": [index for index, _ in group],
            "sensitivity_fraction": fraction, "sensitivity_percent": 100*fraction,
            "integrated_minus_dS_d_relative_density_com3": math.fsum(
                item["minus_dS_d_relative_density_com3"] for _, item in group)})
    total = math.fsum(bar["sensitivity_fraction"] for bar in bars)
    if abs(total-1) > 1e-12:
        raise ValueError("sensitivity partition does not sum to one within recorded rounding")
    first_gap_percent = math.fsum(bar["sensitivity_percent"] for bar in bars[:2])
    z_end = prefix["source_free_domain_z"][1]
    if prefix["source_free_domain_z"][0] != 0 or z_end != 0.004989333151072248:
        raise ValueError("incorrect source-free prefix endpoint")
    points = [{"code_z": item["z"], "prefix_fraction": item["z"]/z_end,
        "pchip_minus_native_HI_relative": item["pchip_minus_halfstep_HI_relative"],
        "pchip_minus_native_HI_ppm": 1e6*item["pchip_minus_halfstep_HI_relative"],
        "pchip_minus_native_T_K": item["pchip_minus_halfstep_T_K"]}
        for item in prefix["comparisons"]]
    if len(points) != 5 or any(abs(p["prefix_fraction"]-j/4) > 1e-14 for j,p in enumerate(points)):
        raise ValueError("exactly five evaluated quarter-prefix points required")
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    png = out/"RUN16_GAS_PATH_RESPONSE_AND_PREFIX.png"
    svg = out/"RUN16_GAS_PATH_RESPONSE_AND_PREFIX.svg"
    receipt = out/"PLOTTED_VALUES_AND_PROVENANCE.json"
    if any(path.exists() for path in (png,svg,receipt)):
        raise FileExistsError("plot artifacts already exist; use a new output directory")

    with tempfile.TemporaryDirectory(prefix="rei_run16_plot_config_") as config:
        os.environ["MPLCONFIGDIR"] = config
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.ticker import MultipleLocator, FuncFormatter
        matplotlib.rcParams.update({
            "font.family":"DejaVu Sans", "font.size":11,
            "axes.labelcolor":"#263746", "text.color":"#263746",
            "xtick.color":"#445766", "ytick.color":"#445766",
            "axes.spines.top":False, "axes.spines.right":False,
            "axes.edgecolor":"#BCC7CE", "axes.linewidth":0.8,
            "svg.fonttype":"none", "svg.hashsalt":"rei-run16-response-prefix-v1",
        })
        fig = plt.figure(figsize=(14.8,7.0),facecolor="white")
        fig.text(.055,.935,"RUN16 | Gas-path response and pre-birth interpolation bias",
                 fontsize=19,fontweight="bold",va="top")
        fig.text(.055,.872,r"Code $z=(X-0.7)/0.0004$ is the integration coordinate.",
                 fontsize=11.8,color="#526572")
        ax_a = fig.add_axes([.170,.29,.335,.425])
        ax_b = fig.add_axes([.635,.29,.320,.425])
        ax_a.set_title("A   Fixed-core survivor sensitivity",loc="left",
                       fontweight="bold",fontsize=14,pad=37)
        ax_a.text(0,1.07,"Integrated response to relative neutral-gas density",
                  transform=ax_a.transAxes,fontsize=10.6,color="#526572")
        ax_a.axhspan(.60,2.45,color="#EFF6F7",zorder=0)
        colors=["#087F91","#63B0BD","#9EABB7"]
        ys=[2,1,0]
        for y,bar,color in zip(ys,bars,colors):
            ax_a.barh(y,bar["sensitivity_percent"],height=.50,color=color,zorder=3)
            ax_a.text(bar["sensitivity_percent"]+1.0,y,
                      f'{bar["sensitivity_percent"]:.2f}%',va="center",fontsize=11.5,
                      fontweight="bold",color="#263746")
        ax_a.text(0,2.66,f"First tight checkpoint gap: {first_gap_percent:.3f}%",
                  fontsize=10.8,fontweight="bold",color="#087F91",va="center")
        ax_a.set_yticks(ys,["0 to 0.647997", "0.647997 to 0.760904", "0.760904 to 1"])
        ax_a.tick_params(axis="y",length=0,pad=8,labelsize=10.2)
        ax_a.set_ylim(-.65,2.96)
        ax_a.set_xlim(0,80)
        ax_a.set_xticks([0,20,40,60,80])
        ax_a.xaxis.grid(True,color="#E4E9ED",linewidth=.7,zorder=0)
        ax_a.set_axisbelow(True)
        ax_a.spines["left"].set_visible(False)
        ax_a.set_xlabel("Fraction of integrated sensitivity [%]",labelpad=9)
        ax_a.text(-.005,-.24,"Intervals in code z; displayed boundaries rounded.\n"
                  "Fixed gas path and core support, E16/T32; 160 fixed births / GL8.",
                  transform=ax_a.transAxes,fontsize=9.2,color="#526572",ha="left",va="top")

        ax_b.set_title("B   Source-free gas prefix bias",loc="left",
                       fontweight="bold",fontsize=14,pad=37)
        ax_b.text(0,1.07,"Five actually evaluated native states (prefix C)",
                  transform=ax_b.transAxes,fontsize=10.6,color="#526572")
        ax_b.axhline(0,color="#C9D2D8",linewidth=1.0,zorder=1)
        ax_b.scatter([p["prefix_fraction"] for p in points],
                     [p["pchip_minus_native_HI_ppm"] for p in points],
                     s=58,color="#AE5317",edgecolors="white",linewidths=.7,zorder=3)
        ax_b.set_xlim(-.055,1.12)
        ax_b.set_ylim(-1.88,.15)
        ax_b.set_xticks([0,.25,.5,.75,1],["0","1/4","1/2","3/4","1"])
        ax_b.set_yticks([0,-.4,-.8,-1.2,-1.6])
        ax_b.xaxis.grid(True,color="#E4E9ED",linewidth=.7,zorder=0)
        ax_b.yaxis.grid(True,color="#E4E9ED",linewidth=.7,zorder=0)
        ax_b.set_axisbelow(True)
        ax_b.set_xlabel(r"Fraction of source-free prefix, $z/z_b$",labelpad=9)
        ax_b.set_ylabel("PCHIP − native HI relative difference [ppm]",labelpad=10,fontsize=10.6)
        ax_b.text(.98,.95,f'At first birth\nΔT = +{points[-1]["pchip_minus_native_T_K"]:.7f} K',
                  transform=ax_b.transAxes,ha="right",va="top",fontsize=10.5,color="#8C4214",
                  bbox={"boxstyle":"round,pad=.45","facecolor":"#FBF3EB","edgecolor":"none"})
        ax_b.annotate(f'{points[-1]["pchip_minus_native_HI_ppm"]:.6f} ppm',
                      xy=(1,points[-1]["pchip_minus_native_HI_ppm"]),
                      xytext=(.48,-1.77),fontsize=10.4,fontweight="bold",color="#8C4214",
                      arrowprops={"arrowstyle":"-","color":"#B4784E","lw":.8})
        ax_b.text(0,-.24,r"Prefix ends at $z_b=0.004989333151$, immediately before first birth."+"\n"
                  "Points only; no continuous path is inferred from this plot.",
                  transform=ax_b.transAxes,fontsize=9.2,color="#526572",ha="left",va="top")
        fig.text(.055,.075,"Sensitivity fractions are conditional fixed-path diagnostics, not a coupled error bound.",
                 fontsize=10.3,color="#526572")
        fig.text(.055,.040,"No direct survivor error is inferred from the source-free prefix.",
                 fontsize=10.3,color="#263746",fontweight="bold")
        fig.savefig(png,dpi=200,facecolor="white",metadata={"Software":"RUN16 frozen-JSON matplotlib plot"})
        fig.savefig(svg,facecolor="white",metadata={"Date":None,
                    "Title":"RUN16 gas-path response and source-free prefix bias",
                    "Description":"Frozen JSON numerical diagnostics; no new RHS calls or IVP solves."})
        plt.close(fig)
        mpl_version=matplotlib.__version__
    if digest(args.response_json) != RESPONSE_SHA or digest(args.prefix_json) != PREFIX_SHA:
        raise AssertionError("scientific input changed during plotting")
    result={"schema":"rei.run16.figure-values.v1","status":"PLOTTED_FROM_FROZEN_JSON_ONLY",
        "figure_title":"RUN16 gas-path response and pre-birth interpolation bias",
        "inputs":{"fixed_response":identify(args.response_json),"prefix_C":identify(args.prefix_json)},
        "selected_response":{"energy_order":16,"time_order":32,"scope":response["scope"]},
        "code_coordinate":"z=(X-0.7)/0.0004; integration coordinate",
        "panel_A":{"values":bars,"fraction_sum_unrenormalized":total,
                    "first_tight_gap_percent":first_gap_percent,
                    "display_rounding":"individual bars2decimalpercent; first gap3decimalpercent; interval limits6decimal"},
        "panel_B":{"points":points,"source_free_domain_z":prefix["source_free_domain_z"],
                    "point_count":5,"line_interpolation_drawn":False,
                    "right_endpoint_convention":prefix["right_endpoint_convention"]},
        "scope_limits":["fixed-path sensitivity is not a coupled error bound",
                        "no direct survivor error is inferred from the source-free prefix",
                        "no point defect or interpolated trajectory envelope inferred from this figure"],
        "new_rhs_calls":0,"new_ivp_solves":0,
        "code":identify(__file__),"command_argv":[sys.executable,"-B",*sys.argv],
        "environment":{"python":sys.version,"matplotlib":mpl_version,"platform":platform.platform()},
        "artifacts":[identify(png),identify(svg)],"input_hashes_unchanged_after_plot":True}
    with receipt.open("x") as stream:
        json.dump(result,stream,indent=2,allow_nan=False);stream.write("\n")
    print(json.dumps({"status":result["status"],"panel_A_percent":[bar["sensitivity_percent"] for bar in bars],
        "first_tight_gap_percent":first_gap_percent,"panel_B_ppm":[p["pchip_minus_native_HI_ppm"] for p in points],
        "files":[identify(png),identify(svg),identify(receipt)]},allow_nan=False))


if __name__ == "__main__":
    main()
