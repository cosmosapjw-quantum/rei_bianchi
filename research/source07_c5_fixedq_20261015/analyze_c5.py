"""Analyze C5 same-source finite q grid actual native runtime and continuum oracle."""
from pathlib import Path
import csv,json,statistics,math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
root=Path(__file__).parent
data=list(csv.DictReader((root/"evidence/PILOT.csv").open()))
oracle=json.loads((root/"evidence/INDEPENDENT_SPECTRUM.json").read_text())
cent=json.loads((root/"evidence/CENTROID_DIAGNOSIS.json").read_text())
bench={}
for rep in (1,2,3):
    for row in csv.DictReader((root/f"evidence/BENCH_REP_{rep}.csv").open()):
        key=(row["kind"],int(row["N_E"]),int(row["threads"]))
        rec=bench.setdefault(key,{"times":[],"checksum":row["checksum"],"state_bytes":int(row["state_bytes"])})
        assert rec["checksum"]==row["checksum"],(rep,key)
        rec["times"].append(float(row["median_ms"]))
assert len(bench)==4*3*3
tbl=[]
for ne in (64,128,256,512):
    item={"cells":ne*32,"energy_bins":ne,"buffers_bytes":bench[("SOURCE",ne,1)]["state_bytes"]}
    for mode in ("SOURCE","ABSORB","ADVANCE"):
        serial=statistics.median(bench[(mode,ne,1)]["times"])
        parallel=statistics.median(bench[(mode,ne,4)]["times"])
        item[f"{mode}_serial_ms"]=serial
        item[f"{mode}_parallel_4_ms"]=parallel
        item[f"{mode}_speedup_4"]=serial/parallel
    tbl.append(item)
rows=[]
for row in data:
    ne=int(row["n_energy"]);q=float(row["q_ref"])
    if q!=0:continue
    absval=float(row["one_source_abs_per_H"])
    heatval=float(row["one_source_heat_eV_per_H"])
    expected=oracle["continuous_source_only"]
    rows.append({"n_energy":ne,"q_ref":q,"source_number":float(row["created_per_H"]),
       "source_mean_energy_ev":float(row["emit_mean_eV"]),
       "absorption_rel_err":absval/expected["absorbed_per_H"]-1,
       "heating_rel_err":heatval/expected["heating_eV_per_H"]-1,
       "short_two_source_number_residual_per_H":float(row["total_two_source_number_residual_per_H"]),
       "short_two_source_energy_residual_eV_per_H":float(row["total_two_source_energy_residual_eV_per_H"])})
assert len(rows)==4
assert max(abs(r["source_mean_energy_ev"]-oracle["source_emission_mean_ev"]) for r in rows)<1e-8
assert max(abs(r["source_number"]/oracle["reference_source_number_per_H"]-1) for r in rows)<2e-11
assert max(abs(r["short_two_source_number_residual_per_H"]) for r in rows)<1e-18
assert max(abs(r["short_two_source_energy_residual_eV_per_H"]) for r in rows)<1e-16
payload={"stage":"C5", "scientific_scope":"MD14 source + fixed q N/U + frozen H/He photo-absorption + 2-step fixed-gas optical/geometry surrogate",
    "bench_bounded":tbl,"source_relative_continuum":rows,
    "continuous_source_ref":oracle["continuous_source_only"],
    "source_energy_convergence_not_monotone":True,
    "centroid_high_grid_refinement":cent["centroid_refinement"],
    "memory_boundary":"working_arrays_bytes counts vector capacities for n/u/edges/source integrals, excludes scratch and gas/solver/checkpoint",
    "performance_boundary":"Release 3 external runs x4 measured internal samples, unchanged N_E/n_mu and gas within each 1 vs4 thread comparison, no full cosmological solver speed claims"}
(root/"evidence/C5_ANALYSIS.json").write_text(json.dumps(payload,indent=2))
fig,ax=plt.subplots(figsize=(7.5,4.5))
for mode in ("SOURCE","ABSORB","ADVANCE"):
    ax.plot([d["energy_bins"] for d in tbl],[d[f"{mode}_speedup_4"] for d in tbl],
            "o-",label=mode.lower())
ax.axhline(1,linestyle=":",color="gray",linewidth=1)
ax.set_xscale("log",base=2);ax.set_xticks([64,128,256,512]);ax.set_xticklabels(["64","128","256","512"])
ax.set_xlabel("Reference-energy cells, n_mu=32");ax.set_ylabel("Serial / 4-thread measured time")
ax.set_title("C5 fixed-q numerical reference batch speedups")
ax.grid(alpha=.25);ax.legend();fig.tight_layout()
fig.savefig(root/"evidence/C5_THREAD_SPEEDUP.png",dpi=150);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.5,4.5))
diag=cent["centroid_refinement"]
ax.plot([d["N"] for d in diag],[100*d["absorption_rel_err"] for d in diag],
        "o-",label="HI+HeI absorption")
ax.plot([d["N"] for d in diag],[100*d["heating_rel_err"] for d in diag],
        "s-",label="photoelectron heat")
ax.axhline(0,linestyle=":",color="gray",linewidth=1)
ax.set_xscale("log",base=2);ax.set_xticks([64,128,256,512,1024,2048,4096])
ax.set_xticklabels([64,128,256,512,1024,2048,4096])
ax.set_xlabel("Fixed q reference-energy cells (FLRW source-only)");ax.set_ylabel("Relative difference from continuum (%)")
ax.set_title("Threshold-alignment sensitivity of mean-energy opacity closure")
ax.grid(alpha=.25);ax.legend();fig.tight_layout()
fig.savefig(root/"evidence/C5_CENTROID_CONVERGENCE.png",dpi=150);plt.close(fig)
print(json.dumps({"speedups_256":tbl[2],"short_source_errors":rows,"continuous":oracle["continuous_source_only"]},indent=2)[:6500])
