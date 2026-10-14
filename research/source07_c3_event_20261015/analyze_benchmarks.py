"""Three independent local release benchmark invocations, same physics and order."""
import json,statistics,csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
root=Path(__file__).parent
rows={}
for i in (1,2,3):
    for line in (root/f"evidence/BENCH_REP_{i}.csv").read_text().splitlines():
        fields=line.split(',')
        if fields[0] not in ("BENCH","ENERGY"):continue
        if fields[0]=="BENCH":
            label=fields[1];threads=int(fields[2]);count=int(fields[3]);seconds=float(fields[4])
            signature=fields[5:7];bytes_=int(fields[7])
            assert count==24576 and bytes_==96
            key=f"{label}_{threads}"
        else:
            label=fields[1];count=int(fields[2]);seconds=float(fields[3])
            signature=[fields[4]];bytes_=int(fields[5])
            assert count==24576 and bytes_==589824
            key=f"ENERGY_{label}"
        d=rows.setdefault(key,{"times":[],"signature":signature})
        assert d["signature"]==signature,(key,signature,d["signature"])
        d["times"].append(seconds)
for d in rows.values():
    d["median_seconds"]=statistics.median(d["times"])
    d["range_seconds"]=[min(d["times"]),max(d["times"])]
speed={label:{
    "speedup_2":rows[f"{label}_1"]["median_seconds"]/rows[f"{label}_2"]["median_seconds"],
    "speedup_4":rows[f"{label}_1"]["median_seconds"]/rows[f"{label}_4"]["median_seconds"]
} for label in ("FLRW","AXISYM")}
speed["ENERGY_SOA_VS_AOS"]={
    "repeat_batch_speedup":rows["ENERGY_AOS"]["median_seconds"]/rows["ENERGY_SOA"]["median_seconds"],
    "soa_allocated_bytes":589824
}
mem={"single_packet_bytes":32,"single_result_bytes":96,
    "source_cohort_packet_count":384,"sample_packet_count":24576,
    "hypothetical_200000_emission_step_source_packet_bytes":384*200000*32,
    "hypothetical_200000_emission_step_packets_gib":384*200000*32/2**30,
    "full_result_bytes_per_24576_packet_batch":24576*96}
payload={"kind":"matched-source readout runtime, NOT cosmological speedup",
         "method":"Rust --release; per-run inner 3 measured reps median; outer 3 run medians",
         "runs":rows,"speedups":speed,"memory":mem,
         "source":"actual AxbiSource discrete 48x8 emitted packet replicated 64 times, frozen artificial constant-H and neutral-gas instance",
         "science":"no coupled gas feedback, no whole-EoR admission, no SIMD instruction certification"}
(root/"evidence/BENCHMARK_ANALYSIS.json").write_text(json.dumps(payload,indent=2))
fig,ax=plt.subplots(figsize=(7.6,4.4))
for label in ("FLRW","AXISYM"):
    ax.plot([1,2,4],[1000*rows[f"{label}_{t}"]["median_seconds"] for t in (1,2,4)],marker="o",label=label)
ax.set_xscale("log",base=2)
ax.set_xticks([1,2,4]);ax.set_xticklabels(["1","2","4"])
ax.set_xlabel("Worker threads");ax.set_ylabel("Median batch time (ms)")
ax.set_title("Event-aware frozen-gas propagation, 24,576 packets")
ax.legend();ax.grid(alpha=.25)
fig.tight_layout();fig.savefig(root/"evidence/PARALLEL_SCALING.png",dpi=155);plt.close(fig)
print(json.dumps({"speedup":speed,"memory":mem,"timings_ms":{k:round(v['median_seconds']*1000,3) for k,v in rows.items()}},indent=2))
