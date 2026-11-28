#!/usr/bin/env python3
"""Immutable D3 consumer. Hash-bound arrays only; no science solver imports.

The compact output is a plot/analysis product, not an ODE restart checkpoint.
Original full states, failed serialization receipts and source stay in D3.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "he30_mpl_cache"))
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_SHA = "7f3856bceea80f25e1f32d69f61cb40841a8461f66e1257bbd7eb79e01184498"
KERNEL = "3b85dedce84d37b3e165da00685a8a984950aafe"
G, C = 6.67430e-11, 299792458.0
SIGMAS = [0., 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1]
MATTER = [-3e-4, -1e-4, 0., 1e-4, 3e-4]
RADIATION = [-1e-3, -3e-4, 0., 3e-4, 1e-3]
FIELDS = ("Sigma_F", "P_m", "P_r", "P_total", "Pi_m", "Pi_r", "Pi_total",
          "H", "s", "b", "elapsed_proper_s", "p_m_J_m3", "p_r_J_m3",
          "gamma_N0", "nu_N0", "minimum_brightness_gamma", "minimum_brightness_nu",
          "Hamiltonian_construction_residual", "normalized_cross", "cancellation_fraction")

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def atomic_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix="." + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(name, path)
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
    finally:
        if os.path.exists(name): os.unlink(name)

def write_json(path, obj):
    atomic_bytes(path, (json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n").encode())

def axes(config):
    # The 35 shared zero-matter cases retain the original radiation-only schema.
    return (config["Sigma_F_i"], config.get("P_m_i", 0.),
            config.get("P_r_i", config["Pi_F_signed_i"]))

def extract(source, out):
    source, out = Path(source), Path(out)
    rows, arrays, common, null_metadata = [], [], None, 0
    source_digests = None
    checks = {"all_raw_sha256": True, "all_tail_sha256": True,
              "all_prefix_hashes": True, "exact_prefix_and_tail": True}
    for result_path in sorted((source / "z2_extension/results/cases").glob("*/RESULT.json")):
        result = json.loads(result_path.read_text())
        inp = json.loads((result_path.parent / "INPUT.json").read_text())
        config, ident = result["config"], result["id"]
        assert ident == result_path.parent.name == inp["id"]
        assert config == inp["config"] and config["source_commit"] == KERNEL
        assert result["status"] == "COMPLETED" and result["exit"] == 0
        if source_digests is None:
            source_digests = {name: sha(source / "vendor" / name) for name in config["source_sha256"]}
        assert source_digests == config["source_sha256"]
        raw_path, tail_path = result_path.parent / "raw.npz", result_path.parent / "tail.npz"
        assert sha(raw_path) == result["raw_sha256"]
        assert sha(tail_path) == result["tail_raw_sha256"]
        prefix = result["prefix_provenance"]
        pre_dir = (source / prefix["prefix_relative"]).resolve()
        assert pre_dir.is_relative_to(source.resolve())
        for name in ("raw", "input", "result"):
            filename = "raw.npz" if name == "raw" else name.upper() + ".json"
            assert sha(pre_dir / filename) == prefix["prefix_" + name + "_sha256"]
        with np.load(raw_path, allow_pickle=False) as raw, np.load(tail_path, allow_pickle=False) as tail, np.load(pre_dir / "raw.npz", allow_pickle=False) as pre:
            assert raw["x"].shape == (153,) and tail["x"].shape == (33,)
            assert pre["x"].shape == (121,)
            assert np.array_equal(raw["x"][:121], pre["x"])
            assert np.array_equal(raw["raw_y"][:, :121], pre["raw_y"])
            assert np.array_equal(raw["raw_y"][:, 120:], tail["raw_y"])
            assert np.array_equal(raw["x"][120:], tail["x"])
            assert np.array_equal(tail["raw_y"][:, 0], pre["raw_y"][:, -1])
            assert raw["raw_y"].shape == (56 if config["guard"] else 40, 153)
            assert np.all(np.isfinite(raw["raw_y"]))
            grid = {k: raw[k].copy() for k in ("x", "a")}
            if common is None: common = grid
            else:
                assert all(np.array_equal(common[k], grid[k]) for k in common)
            data = {key: raw[key].copy() for key in FIELDS}
        assert all(v.shape == (153,) and np.all(np.isfinite(v)) for v in data.values())
        assert np.all(data["H"] > 0)
        si, pm, pr = axes(config)
        assert max(abs(data["Sigma_F"][0] - si), abs(data["P_m"][0] - pm),
                   abs(data["P_r"][0] - pr)) < 5e-12
        is_joint = not config["guard"] and pm in MATTER and pr in RADIATION
        rows.append({"case_id": ident, "source_raw_sha256": result["raw_sha256"],
                     "source_input_sha256": sha(result_path.parent / "INPUT.json"),
                     "source_result_sha256": sha(result_path),
                     "prefix_raw_sha256": prefix["prefix_raw_sha256"],
                     "tail_raw_sha256": result["tail_raw_sha256"],
                     "Sigma_i": si, "P_m_i": pm, "P_r_i": pr,
                     "guard": config["guard"], "joint_grid": is_joint,
                     "radiation_baseline": not config["guard"] and "P_m_i" not in config,
                     "metadata_recovered_without_nfev": result.get("nfev") is None})
        null_metadata += result.get("nfev") is None
        arrays.append(data)
    assert len(rows) == 237 and len({r["case_id"] for r in rows}) == 237
    assert sum(r["joint_grid"] for r in rows) == 175
    assert sum(r["radiation_baseline"] for r in rows) == 91
    assert sum(r["guard"] for r in rows) == 6
    observed_joint = {axes_: 0 for axes_ in [(r["Sigma_i"],r["P_m_i"],r["P_r_i"]) for r in rows if r["joint_grid"]]}
    assert set(observed_joint) == {(s,m,r) for s in SIGMAS for m in MATTER for r in RADIATION}
    stacked = {k: np.stack([a[k] for a in arrays]) for k in FIELDS}
    stacked["S_signed"] = np.sqrt(6.) * stacked["s"] / stacked["H"]
    kappa = 8 * np.pi * G / C**2
    residuals = {
        "Sigma_F": float(np.max(abs(abs(stacked["S_signed"]) - stacked["Sigma_F"]))),
        "P_m_from_SI": float(np.max(abs(kappa*np.sqrt(6)*stacked["p_m_J_m3"]/stacked["H"]**2-stacked["P_m"]))),
        "P_r_from_SI": float(np.max(abs(kappa*np.sqrt(6)*stacked["p_r_J_m3"]/stacked["H"]**2-stacked["P_r"]))),
        "signed_sum": float(np.max(abs(stacked["P_m"]+stacked["P_r"]-stacked["P_total"]))),
        "total_magnitude": float(np.max(abs(abs(stacked["P_total"])-stacked["Pi_total"]))),
        "cross": float(np.max(abs(stacked["P_m"]*stacked["P_r"]-stacked["normalized_cross"])))
    }
    assert max(residuals.values()) < 5e-12
    z = 1/common["a"] - 1
    assert np.all(np.diff(z) < 0) and abs(z[0]-20) < 1e-12 and abs(z[-1]-2) < 1e-12
    assert abs(z[120]-4) < 1e-12
    check = json.loads((source / "z2_extension/results/CHECK.json").read_text())
    refinements = []
    index = {r["case_id"]: i for i,r in enumerate(rows)}
    for pair in check["refinement_controls"]:
        g,n = index[pair["id"]],index[pair["nominal_id"]]
        assert rows[g]["guard"] and not rows[n]["guard"]
        assert all(rows[g][k] == rows[n][k] for k in ("Sigma_i","P_m_i","P_r_i"))
        endpoint = {k: float(abs(stacked[k][g,-1]-stacked[k][n,-1])) for k in ("Sigma_F","P_m","P_r","b")}
        endpoint["H_relative"] = float(abs(stacked["H"][g,-1]/stacked["H"][n,-1]-1))
        assert endpoint == pair["absolute_endpoint_differences"]
        full = {k: float(np.max(abs(stacked[k][g]-stacked[k][n]))) for k in ("Sigma_F","P_m","P_r","b")}
        full["H_relative"] = float(np.max(abs(stacked["H"][g]/stacked["H"][n]-1)))
        refinements.append({"guard_id": pair["id"],"nominal_id":pair["nominal_id"],"endpoint":endpoint,"full_history":full})
    buffer = io.BytesIO()
    np.savez_compressed(buffer, **stacked, **common, z_mean=z,
                        case_id=np.array([r["case_id"] for r in rows], dtype="U64"))
    atomic_bytes(out / "histories.npz", buffer.getvalue())
    for i,row in enumerate(rows):
        for k in ("Sigma_F","P_m","P_r","Pi_m","Pi_r","Pi_total","S_signed","b","H"):
            row[k+"_z2"] = float(stacked[k][i,-1])
        row["elapsed_Gyr_z2"] = float(stacked["elapsed_proper_s"][i,-1]/(365.25*86400*1e9))
    catalog = {"schema":"HE30_SAVED_D3_V1", "source_archive_sha256":ARCHIVE_SHA,
               "source_kernel_commit":KERNEL, "histories_sha256":sha(out / "histories.npz"),
               "science_runs_this_consumer":0, "cases":rows}
    write_json(out / "CATALOG.json", catalog)
    table = io.StringIO(newline="")
    writer=csv.DictWriter(table,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    atomic_bytes(out / "endpoints.csv", table.getvalue().encode())
    nominal = np.array([not r["guard"] for r in rows])
    joint = np.array([r["joint_grid"] for r in rows])
    sig = stacked["S_signed"]
    eps=1e-12
    reversals = []
    for i,r in enumerate(rows):
        active=sig[i][abs(sig[i])>eps]
        if r["joint_grid"] and len(active)>1 and np.any(active[1:]*active[:-1]<0): reversals.append(r["case_id"])
    summary = {"schema":"HE30_D3_ANALYSIS_V1", "source_archive_sha256":ARCHIVE_SHA,
        "cases":237,"nominal":231,"refinement_guards":6,"joint_grid":175,
        "radiation_baseline":91,"overlap":35,"epochs":153,"prefix_epochs":121,
        "tail_epochs_including_join":33,"source_science_new_ivps":237,"science_runs_this_turn":0,
        "recovered_null_execution_metadata_cases":null_metadata,
        "z_initial":float(z[0]),"z_join":float(z[120]),"z_final":float(z[-1]),
        "array_identity_checks":checks,"maximum_identity_residuals":residuals,
        "histories_sha256":catalog["histories_sha256"],
        "minimum_sampled_brightness":float(min(stacked[k].min() for k in ("minimum_brightness_gamma","minimum_brightness_nu"))),
        "maximum_N0_error":float(max(abs(stacked[k]-1).max() for k in ("gamma_N0","nu_N0"))),
        "max_Hamiltonian_construction_residual":float(abs(stacked["Hamiltonian_construction_residual"]).max()),
        "joint_shear_sign_reversals_above_1e_12":len(reversals),"reversal_case_ids":reversals,
        "endpoint_ranges_nominal":{k:[float(stacked[k][nominal,-1].min()),float(stacked[k][nominal,-1].max())] for k in ("Sigma_F","P_m","P_r","Pi_total")},
        "endpoint_ranges_joint":{k:[float(stacked[k][joint,-1].min()),float(stacked[k][joint,-1].max())] for k in ("Sigma_F","P_m","P_r","Pi_total")},
        "refinement_controls":refinements,
        "refinement_scope":"Six saved nominal/guard pairs; no uniform grid-wide or continuum error certificate",
        "compact_data_scope":"observables only; recover D3 full raw_y for any future continuation",
        "mean_redshift_definition":"z_mean=1/a-1; elapsed time is measured from z_mean=20"}
    write_json(out / "ANALYSIS_SUMMARY.json",summary)
    return catalog,stacked,z,summary

def plot(catalog,data,z,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"axes.spines.top":False,
                        "axes.spines.right":False,"axes.titlesize":12,"figure.facecolor":"white",
                        "axes.titleweight":"medium","svg.fonttype":"none","savefig.facecolor":"white"})
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=catalog["cases"]
    lookup={(r["Sigma_i"],r["P_m_i"],r["P_r_i"]):i for i,r in enumerate(rows) if r["joint_grid"]}
    colors=["#59616e","#007f86","#376bc4","#8159a7","#b85b91","#d47f21","#b74231"]
    provenance={"source_archive_sha256":ARCHIVE_SHA,"histories_sha256":catalog["histories_sha256"],
                "interpolation":"None for sweep; lines join stored time samples only",
                "z_definition":"mean redshift 1/a-1","figures":{}}
    def save(fig,name,ids,note):
        fig.savefig(out/(name+".png"),dpi=170,bbox_inches="tight")
        fig.savefig(out/(name+".svg"),bbox_inches="tight")
        plt.close(fig)
        provenance["figures"][name]={"case_ids":ids,"note":note,"png_sha256":sha(out/(name+".png")),"svg_sha256":sha(out/(name+".svg"))}
    # All independently varied joint-grid endpoints, no interpolated surface.
    fig,axs=plt.subplots(1,2,figsize=(13,5.3),layout="constrained")
    for s,color in zip(SIGMAS,colors):
        ix=[i for i,r in enumerate(rows) if r["joint_grid"] and r["Sigma_i"]==s]
        for ax,key in zip(axs,["Pi_m","Pi_r"]):
            ax.scatter(data[key][ix,-1],data["Sigma_F"][ix,-1],s=34,color=color,alpha=.88,edgecolor="white",linewidth=.35,label=fr"$\Sigma_i={s:g}$")
    for ax,label in zip(axs,[r"Matter $\Pi_m(\bar z=2)$",r"Radiation $\Pi_r(\bar z=2)$"]):
        ax.set_xscale("symlog",linthresh=1e-8);ax.set_yscale("symlog",linthresh=1e-8)
        ax.set_xlabel(label);ax.set_ylabel(r"$\Sigma_F(\bar z=2)$");ax.grid(alpha=.2,which="major")
    axs[1].legend(loc="center left",bbox_to_anchor=(1, .5),frameon=False,title="Initial shear at z = 20")
    fig.suptitle("LRS Bianchi I | independent matter and radiation stress",fontsize=17)
    fig.supxlabel("175 joint-grid endpoints · 7 shear planes × 5 matter × 5 radiation values · symmetric-log axes retain zero",fontsize=10)
    save(fig,"parameter_sweep_z2",[r["case_id"] for r in rows if r["joint_grid"]],"Two component planes; same 175 endpoints. Colors are initial shear; points can overlap.")
    # Exact categorical grid, with actual nonuniform axis values displayed.
    fig,axs=plt.subplots(2,4,figsize=(15,7.6),layout="constrained")
    norm=LogNorm(1e-7,1e-2)
    for ax,s in zip(axs.flat,SIGMAS):
        matrix=np.array([[data["Sigma_F"][lookup[(s,m,r)],-1] for m in MATTER] for r in RADIATION])
        display=np.ma.masked_less(matrix,1e-7)
        im=ax.imshow(display,origin="lower",norm=norm,cmap="viridis",interpolation="none")
        for iy,ix in zip(*np.where(matrix<1e-7)):
            ax.text(ix,iy,"0*",ha="center",va="center",fontsize=8,color="#444")
        ax.set_title(fr"$\Sigma_i={s:g}$")
        ax.set_xticks(range(5),["−3","−1","0","1","3"])
        ax.set_yticks(range(5),["−1","−0.3","0","0.3","1"])
        ax.set_xlabel(r"$P_{m,i}$ [$10^{-4}$]");ax.set_ylabel(r"$P_{r,i}$ [$10^{-3}$]")
    axs[1,3].axis("off")
    fig.colorbar(im,ax=list(axs[:,3]),label=r"$\Sigma_F(\bar z=2)$",shrink=.75)
    axs[1,3].text(.03,.87,"Exact 5 × 5 cells per plane\n\nSigned initial component axes\nCategorical, nonuniform values\nNo surface interpolation\n\n0*: residual below 10⁻⁷\n     retained in source arrays",transform=axs[1,3].transAxes,fontsize=10,va="top")
    fig.suptitle("Shear response at z = 2 across all seven initial-shear planes",fontsize=17)
    save(fig,"sweep_all_shear_planes",[r["case_id"] for r in rows if r["joint_grid"]],"Cell centers enumerate exact input values. Below-color-range cell marked 0*; raw residual retained.")
    patterns=[(3e-4,0.,"matter seed"),(0.,3e-4,"radiation seed"),(3e-4,3e-4,"same sign"),(3e-4,-3e-4,"initial cancellation"),(0.,0.,"zero initial stress")]
    style_colors=["#1a7f8e","#bd6540","#7856a1","#2b66ba","#62676f"]
    fig,axs=plt.subplots(2,2,figsize=(13,8),layout="constrained")
    ids=[]
    for (m,r,label),color in zip(patterns,style_colors):
        i=lookup[(.003,m,r)];ids.append(rows[i]["case_id"])
        for ax,key in zip(axs.flat,["Sigma_F","Pi_m","Pi_r","Pi_total"]):
            ax.plot(z,data[key][i],color=color,lw=2,label=label)
    for ax,label in zip(axs.flat,[r"Shear $\Sigma_F$",r"Matter $\Pi_m=|P_m|$",r"Radiation $\Pi_r=|P_r|$",r"Total $\Pi_{tot}=|P_m+P_r|$"]):
        ax.set_xlim(20,2);ax.set_yscale("symlog",linthresh=1e-8);ax.grid(alpha=.2)
        ax.set_ylim(bottom=0)
        ax.axvline(4,color="#777",lw=1,ls=":");ax.set_title(label);ax.set_xlabel(r"Mean redshift $\bar z$")
        ax.set_xticks([20,15,10,6,4,2])
    axs[0,0].legend(frameon=False,fontsize=9)
    fig.suptitle(r"Time evolution | $\Sigma_i=0.003$ and independent stress seeds",fontsize=17)
    fig.supxlabel(r"Nonzero seeds have magnitude $3\times10^{-4}$ · dotted line: exact saved-state join at z = 4 · 153 stored epochs",fontsize=10)
    save(fig,"time_evolution_z20_to_z2",ids,"Five representative tracks at initial shear .003. Absolute norms use symlog near zero; full signed histories preserved.")
    fig,axs=plt.subplots(2,2,figsize=(13,8),layout="constrained")
    selections=[(3e-4,-3e-4,"Pm + / Pr −","#2864ad"),(-3e-4,3e-4,"Pm − / Pr +","#c36338"),(0.,0.,"isotropic control","#66696f")]
    ids=[]
    for m,r,label,color in selections:
        i=lookup[(0.,m,r)];ids.append(rows[i]["case_id"])
        for ax,key in zip(axs.flat,["P_m","P_r","P_total","S_signed"]):
            ax.plot(z,data[key][i]*1e4,lw=2,color=color,label=label)
    for ax,label in zip(axs.flat,[r"Signed matter $P_m$",r"Signed radiation $P_r$",r"Signed total $P_m+P_r$",r"Signed shear $S=\sqrt{6}s/H$"]):
        ax.axhline(0,color="#babdc3",lw=.7);ax.axvline(4,color="#777",lw=1,ls=":")
        ax.set_xlim(20,2);ax.set_xticks([20,15,10,6,4,2]);ax.set_title(label)
        ax.set_xlabel(r"Mean redshift $\bar z$");ax.set_ylabel(r"value / $10^{-4}$");ax.grid(alpha=.15)
    axs[0,0].legend(frameon=False,fontsize=9)
    fig.suptitle("Initial stress cancellation does not persist during expansion",fontsize=17)
    fig.supxlabel(r"$\Sigma_i=0$, $P_{m,i}=-P_{r,i}=\pm3\times10^{-4}$ · all curves from saved D3 data · no new integration",fontsize=10)
    save(fig,"signed_cancellation_evolution",ids,"Signed components and shear. Zero initial total stress with anisotropic components is distinct from true isotropy.")
    # A small portable table contains every point drawn in representative time plots.
    selected=sorted(set(cid for name,v in provenance["figures"].items() if "evolution" in name for cid in v["case_ids"]))
    stream=io.StringIO(newline=""); keys=["case_id","z_mean","Sigma_F","S_signed","P_m","P_r","P_total","Pi_m","Pi_r","Pi_total"]
    writer=csv.DictWriter(stream,fieldnames=keys);writer.writeheader()
    for cid in selected:
        i=next(i for i,r in enumerate(rows) if r["case_id"]==cid)
        for j,zz in enumerate(z):
            writer.writerow({"case_id":cid,"z_mean":float(zz),**{k:float(data[k][i,j]) for k in keys[2:]}})
    atomic_bytes(out.parent/"results/selected_histories.csv",stream.getvalue().encode())
    write_json(out/"FIGURE_MANIFEST.json",provenance)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--source-root",type=Path)
    mode.add_argument("--plot-saved",action="store_true",help="Replot the hash-bound compact product without original ODE checkpoints")
    p.add_argument("--out",type=Path,default=ROOT/"results")
    p.add_argument("--plots",type=Path,default=ROOT/"plots")
    args=p.parse_args()
    if args.plot_saved:
        catalog=json.loads((args.out/"CATALOG.json").read_text())
        assert sha(args.out/"histories.npz")==catalog["histories_sha256"]
        with np.load(args.out/"histories.npz",allow_pickle=False) as f:
            data={k:f[k].copy() for k in (*FIELDS,"S_signed")}; z=f["z_mean"].copy()
            assert list(f["case_id"])==[r["case_id"] for r in catalog["cases"]]
        summary=json.loads((args.out/"ANALYSIS_SUMMARY.json").read_text())
    else:
        catalog,data,z,summary=extract(args.source_root,args.out)
    plot(catalog,data,z,args.plots)
    print(json.dumps({k:summary[k] for k in ("cases","nominal","joint_grid","epochs","science_runs_this_turn","maximum_identity_residuals","joint_shear_sign_reversals_above_1e_12")},indent=2))

if __name__=="__main__": main()
