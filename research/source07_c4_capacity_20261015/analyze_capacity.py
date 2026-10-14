#!/usr/bin/env python3
"""Summarize actual local source-bound Rust cap pilot without solver replay."""
import json,csv,statistics,math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parent
base=json.loads((root/"evidence/DESIGN_CAPACITY.json").read_text())
rows=list(csv.DictReader((root/"evidence/CAPACITY_PILOT.csv").open()))
assert len(rows)==3
per_q={}
for row in rows:
    q=row["q_ref"]
    assert int(row["n_before"])==384 and int(row["n_after"])==256 and int(row["merges"])==128
    assert int(row["tagged_payload_bytes_before"])==15360 and int(row["tagged_payload_bytes_after"])==10240
    n0,n1=(float(row[k]) for k in ("original_photons_per_H","new_photons_per_H"))
    e0,e1=(float(row[k]) for k in ("original_energy_eV_per_H","new_energy_eV_per_H"))
    assert abs(n0-n1) <= 2e-14*n0
    assert abs(e0-e1) <= 2e-14*e0
    def delta(key,reference):
        ref=float(row[reference]);dv=float(row[key])
        return {"baseline":ref,"absolute_difference":dv,"relative_change_percent":100*dv/ref if ref else None}
    per_q[q]={"hi":delta("event_HI_delta","baseline_HI_events_per_H"),
        "hei":delta("event_HeI_delta","baseline_HeI_events_per_H"),
        "heii":delta("event_HeII_delta","baseline_HeII_events_per_H"),
        "heat":delta("heat_delta_eV_per_H","baseline_heat_eV_per_H"),
        "memory_saved_bytes":15360-10240}
times={}
for i in (1,2,3):
    for row in csv.DictReader((root/f"evidence/CAPACITY_RUN_{i}.csv").open()):
        times.setdefault(row["q_ref"],[]).append(float(row["elapsed_ms"]))
median={q:statistics.median(t) for q,t in times.items()}
assert len(times)==3 and all(len(t)==3 for t in times.values())
report={"stage":"C4", "physics":"same source and proper gas during one z20 1e8-second local pilot",
        "source_sha":base["source_sha256"],"decision":"FIXED_Q_ENERGY_ANGLE_GRID_FIRST; direction-only small cohort cap oracle",
        "three_run_median_ms":median,"reaction_readout":per_q,
        "cross_epoch_true_bianchi_energy_defect":base["actual_bianchi_source_geometry_cross_epoch_energy_gap"],
        "memory_candidate_mib":base["fixed_q_candidates"],
        "caveats":["local fixed-gas exponential readout, no coupled error bound",
                   "all-epoch q-grid source R*J not implemented in this C4 stage",
                   "TaggedPhoton payload-only measurement; total Vec/solver memory not included",
                   "same local source mu across emission times is generally not same covariant-q direction"]}
(root/"evidence/CAPACITY_SUMMARY.json").write_text(json.dumps(report,indent=2))
fig,ax=plt.subplots(figsize=(8,4.5))
case=base["actual_bianchi_source_geometry_cross_epoch_energy_gap"]
qs=[v["q_ref"] for v in case]
defects=[1e6*v["relative_energy_deficit"] for v in case]
ax.plot(qs,defects,"o-",label="two-epoch energy deficit")
ax.set_xlabel("Signed q_ref")
ax.set_ylabel("Naive one-ray merged energy deficit (ppm)")
ax.set_title("Same local emission direction, two emission epochs in actual Bianchi I")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(root/"evidence/Q_DIRECTION_DEFICIT.png",dpi=160);plt.close(fig)
print(json.dumps({"cap_median_ms":median,
                  "reaction_delta":per_q["0"],
                  "q_direction_energy_ppm":dict(zip(qs,defects))},indent=2))
