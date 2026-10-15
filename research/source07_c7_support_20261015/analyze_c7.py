"""C7 scientific comparison and timing of pooled vs two age-lane fixed-q grids."""
import csv,json,statistics,math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent
oracle=json.loads((p/"evidence/INDEPENDENT_TWO_AGE.json").read_text())
native=list(csv.DictReader((p/"evidence/TWO_AGE_NATIVE.csv").open()))
native_key={(float(r["q_ref"]),int(r["nE"])):r for r in native}
speed={}
for i in (1,2,3):
    for row in csv.DictReader((p/f"evidence/TWO_AGE_REP_{i}.csv").open()):
        key=(float(row["q_ref"]),int(row["nE"]))
        speed.setdefault(key,{"pooled_ms":[],"support_ms":[],"two_lane_ms":[]})
        speed[key]["pooled_ms"].append(float(row["old_rep_ms"]))
        speed[key]["support_ms"].append(float(row["support_rep_ms"]))
        speed[key]["two_lane_ms"].append(float(row["two_age_ms"]))
        for k in ["old_rep_HI","support_rep_HI","two_age_HI","two_age_heat"]:
            a=float(row[k]);b=float(native_key[key][k])
            assert abs(a-b) <= 5e-13 * abs(b), (i,key,k,a,b)
for r in oracle["comparison"]:
    key=(float(r["q"]),r["energy_bins"])
    native_row=native_key[key]
    truth=oracle["source_geometry"][r["q"]]
    for label,field,ref in [("HI","HI","frozen_HI_absorbed_photons_per_H"),
                            ("HeI","HeI","frozen_HeI_absorbed_photons_per_H"),
                            ("heat","heat","frozen_photoheat_eV_per_H")]:
        actual=float(native_row[f"two_age_{field}"])
        r[f"two_age_{label}_relative_error"]=actual/truth[ref]-1
    r["two_age_buffer_bytes"]=int(native_row["two_age_payload_bytes"])
    r["one_buffer_bytes"]=int(native_row["reference_state_bytes"])
    r["median_pooled_ms"]=statistics.median(speed[key]["pooled_ms"])
    r["median_support_ms"]=statistics.median(speed[key]["support_ms"])
    r["median_two_age_ms"]=statistics.median(speed[key]["two_lane_ms"])
assert len(oracle["comparison"])==12
errors=[r for r in oracle["comparison"] if r["energy_bins"]==256]
assert all(abs(r["two_age_HI_relative_error"])<1e-8 for r in errors)
assert all(abs(r["legacy_HI_relative_error"])>2e-3 for r in errors)
assert all(r["two_age_buffer_bytes"]==2*r["one_buffer_bytes"] for r in oracle["comparison"])
assert all(abs(r["two_age_heat_relative_error"])<2e-8 for r in errors)
result={"scientific_scope":"two impulse equal-photons source age z20 and z4, physical redshift and proper frozen neutral gas at z4; not evolving coupled H/He",
        "source_model":"PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1",
        "comparison":oracle["comparison"],
        "invariants":{"physical_reference_support_always_overlaps":True,
          "rigorous_support_ratio_bound":(21/5)**1.02,
          "emission_band_ratio":100/13.6,
          "source_bound_max_lower_ref_eV":13.6*(21/5)**1.02,
          "elapsed_proper_photon_source_count_per_age":oracle["old_and_late_source_photons_per_H"],
          "physical_gas_fixed_at_final_epoch":oracle["gas_proper_cm3"]},
        "risk":"One compressed 2-moment mixture bias in HI; two independent age lanes close manufactured two-impulse case, does NOT allow unbounded age accumulation.",
        "performance":"Rust --release; 3 exterior runs, same threads=4 for all representations after final tuning; extra 2x q-grid resident state."}
(p/"evidence/C7_COMPARISON.json").write_text(json.dumps(result,indent=2))
plt.figure(figsize=(8,4.6))
for q in [-.01,0.,.01]:
    tab=sorted((r for r in result["comparison"] if float(r["q"])==q),key=lambda x:x["energy_bins"])
    color=None
    plt.plot([r["energy_bins"] for r in tab],[abs(r["legacy_HI_relative_error"]) for r in tab],
             "o-",label=f"pooled q={q:+.2f}")
    plt.plot([r["energy_bins"] for r in tab],[abs(r["two_age_HI_relative_error"]) for r in tab],
             "s--",label=f"2 ages q={q:+.2f}")
plt.xscale("log",base=2);plt.yscale("log");plt.xlabel("Fixed-q energy bins (32 angular)")
plt.ylabel("Absolute relative error, H I photoabsorption")
plt.title("C7 two source ages: one pooled N/U vs two fixed spectral lanes")
plt.xticks([64,128,256,512],["64","128","256","512"])
plt.grid(alpha=.25);plt.legend(ncol=2,fontsize=8);plt.tight_layout()
plt.savefig(p/"evidence/C7_TWO_AGE_HI.png",dpi=160);plt.close()
plt.figure(figsize=(7.2,4.1))
t=next(r for r in result["comparison"] if float(r["q"])==0. and r["energy_bins"]==256)
plt.bar(["Pooled 4T","Support 4T","Two ages 4T"],
        [t["median_pooled_ms"],t["median_support_ms"],t["median_two_age_ms"]])
plt.ylabel("Measured median reaction time (ms)");plt.title("C7 nE256, nmu32, same frozen gas")
plt.tight_layout();plt.savefig(p/"evidence/C7_TIME_COMPARISON.png",dpi=160);plt.close()
print(json.dumps({"n256":errors,"q0_n256":t,"support_overlap_bound":result["invariants"]["source_bound_max_lower_ref_eV"]},indent=2)[:8500])
