"""Scientific C6 metrics from pinned Rust release cohorts + independent SciPy."""
from pathlib import Path
import csv,json,statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
root=Path(__file__).parent
r=json.loads((root/"evidence/INDEPENDENT_C6.json").read_text())
truth=r["absorbers"]["owner_initial"]
hi_ref,hei_ref,_=truth["continuous_absorbed_per_H"]
heat_ref=truth["continuous_heat_eV_per_H"]
runs={}
for rep in [1,2,3]:
    for row in csv.DictReader((root/f"evidence/C6_REP_{rep}.csv").open()):
        ne=int(row["N_E"])
        record=runs.setdefault(ne,{"serial":[],"parallel":[]})
        record["serial"].append(float(row["serial_ms"]))
        record["parallel"].append(float(row["parallel_4_ms"]))
        if "native" not in record:record["native"]=row
        else:
            for field in ["centroid_HeI","reconstructed_HeI","centroid_heat","reconstructed_heat",
                          "reconstructed_HI","n_photons_per_H","n_state_bytes"]:
                if field=="n_state_bytes": assert record["native"][field]==row[field]
                else:assert abs(float(record["native"][field])-float(row[field]))<3e-13*abs(float(row[field]))
results={}
for n,v in runs.items():
    raw=v["native"]
    results[n]={
        "centroid_HeI_rel_error":float(raw["centroid_HeI"])/hei_ref-1,
        "positive_HeI_rel_error":float(raw["reconstructed_HeI"])/hei_ref-1,
        "centroid_heat_rel_error":float(raw["centroid_heat"])/heat_ref-1,
        "positive_heat_rel_error":float(raw["reconstructed_heat"])/heat_ref-1,
        "positive_HI_rel_error":float(raw["reconstructed_HI"])/hi_ref-1,
        "buffer_bytes":int(raw["n_state_bytes"]),
        "serial_median_ms":statistics.median(v["serial"]),
        "parallel4_median_ms":statistics.median(v["parallel"]),
        "speedup4":statistics.median(v["serial"])/statistics.median(v["parallel"]),
        "photon_number_residual_per_H":float(raw["number_residual_per_H"]),
        "photon_energy_residual_eV_per_H":float(raw["energy_residual_eV_per_H"])
    }
assert len(results)==4
assert abs(results[256]["positive_HeI_rel_error"])<1e-5
assert abs(results[256]["positive_heat_rel_error"])<1e-6
assert abs(results[512]["positive_HeI_rel_error"])<1e-6
assert all(abs(v["photon_energy_residual_eV_per_H"])<1e-18 for v in results.values())
payload={"stage":"C6 implementation verification","model":"selected original MD14 50k source, frozen zbar20 gas",
"baseline":"original C5 centroid opacity","positive_closure":"exponential number/mean matched positive within-bin threshold split",
"per_resolution":results,
"manufactured_HeII":{"reference_per_H":2.5555213060184666e-13,
                       "native_per_H":2.55552184876903757e-13,
                       "relative_error":2.12383504560875735e-7},
"boundaries":{"scientific_admission":"SCOPED_ONLY",
"independent_absolute_error_bound":"NOT_CERTIFIED",
"full_coupled_EoR":"NOT_RUN",
"arbitrary_spectral_support_identifiability":"IMPOSSIBLE_FROM_N_AND_U_ALONE; must preserve extra support data or certified bounds"}}
(root/"evidence/C6_ANALYSIS.json").write_text(json.dumps(payload,indent=2))
fig,ax=plt.subplots(figsize=(8,4.5))
grid=sorted(results)
for key,style,label in [("centroid_HeI_rel_error","o--","Centroid: HeI"),
                        ("positive_HeI_rel_error","o-","Positive reconstruction: HeI"),
                        ("centroid_heat_rel_error","s--","Centroid: heat"),
                        ("positive_heat_rel_error","s-","Positive reconstruction: heat")]:
    ax.plot(grid,[100*results[n][key] for n in grid],style,label=label)
ax.axhline(0,color="gray",linewidth=1,linestyle=":")
ax.set_xscale("log",base=2)
ax.set_xticks(grid);ax.set_xticklabels(grid)
ax.set_xlabel("Reference q energy bins (n_mu=32)")
ax.set_ylabel("Relative error (%) vs independent continuum")
ax.set_title("C6 HeI and photoheat frozen-gas source closure")
ax.grid(alpha=0.25);ax.legend()
fig.tight_layout();fig.savefig(root/"evidence/C6_SPECIES_CONVERGENCE.png",dpi=155);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.5,4.3))
ax.plot(grid,[results[n]["serial_median_ms"] for n in grid],"o-",label="1 thread")
ax.plot(grid,[results[n]["parallel4_median_ms"] for n in grid],"s-",label="4 threads")
ax.set_xscale("log",base=2);ax.set_xticks(grid);ax.set_xticklabels(grid)
ax.set_xlabel("Energy bins (n_mu=32)");ax.set_ylabel("Mean operator time per invocation (ms)")
ax.set_title("C6 positive reconstructed absorption, Rust --release")
ax.grid(alpha=0.25);ax.legend()
fig.tight_layout();fig.savefig(root/"evidence/C6_THREADS.png",dpi=155);plt.close(fig)
print(json.dumps({"n256":results[256],"n512":results[512],"HeII":payload["manufactured_HeII"]},indent=2))
