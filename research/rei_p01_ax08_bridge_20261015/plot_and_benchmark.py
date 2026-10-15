#!/usr/bin/env python3
"""Plot scoped tau provenance and benchmark serial vs data-parallel reductions."""
import json
from concurrent.futures import ThreadPoolExecutor
import math
from pathlib import Path
import statistics
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import ax08_early_tau as cold

HERE=Path(__file__).resolve().parent
OUT=HERE/"results"
owner=Path.home()/"Dropbox/bianchi/rei_bianchi"
cold_data=json.loads((OUT/"ax08_cold_vs_p01_warm.json").read_text())
warm_data=json.loads((OUT/"certified_poisson.json").read_text())
vis_data=json.loads((OUT/"warm_P01_finite_visibility.json").read_text())
times=np.array([row["proper_elapsed_s"] for row in cold_data["rows"]],dtype=float)/1e11
warm_tau=np.array([float(row["source_tau_lower"]) for row in warm_data["cells"]])
cold_tau=np.array(cold_data["cases"]["ZERO"]["tau_cumulative_16"])
plus_tau=np.array(cold_data["cases"]["SHEAR_PLUS"]["tau_cumulative_16"])
minus_tau=np.array(cold_data["cases"]["SHEAR_MINUS"]["tau_cumulative_16"])
three=np.array([float(row["prob_three_plus_upper"]) for row in warm_data["cells"]])
twice=np.array([float(row["prob_twice_upper"]) for row in warm_data["cells"]])
once=np.array([float(row["prob_once_upper"]) for row in warm_data["cells"]])
last=np.array([float(row["source_window_last_scatter_mid"])
               for row in vis_data["result"]])

fig,(ax0,ax1)=plt.subplots(2,1,figsize=(10,8),constrained_layout=True)
ax0.plot(times,warm_tau,marker=".",label="BASS_HE warm P01: stored 16-cell source-scoped tau")
ax0.plot(times,cold_tau,marker="o",ms=2.5,label="rei_bianchi AX08 cold ZERO: original electron history")
ax0.plot(times,plus_tau,linestyle=":",label="AX08 cold +0.01 (near ZERO here)")
ax0.plot(times,minus_tau,linestyle="--",label="AX08 cold -0.01 (near ZERO here)")
ax0.set_yscale("log")
ax0.set_ylabel("Cumulative Thomson optical depth")
ax0.legend(loc="best",fontsize=8)
ax0.grid(alpha=.25)
ax0.set_title("Equal elapsed proper time; different physical source / IC / clock epochs")
ax1.plot(times,once,marker=".",label="BASS warm P(N=1)")
ax1.plot(times,twice,marker=".",label="BASS warm P(N=2)")
ax1.plot(times,three,marker=".",label="BASS warm P(N>=3), stable positive series")
ax1.set_yscale("log")
ax1.set_xlabel("Elapsed proper time / 1e11 seconds (each model's own origin)")
ax1.set_ylabel("Cumulative event-count probability")
ax1.legend(fontsize=8)
ax1.grid(alpha=.25)
fig.suptitle("Source-scoped opacity and independent actual AX08 cold control, NOT model-matched EoR",fontsize=11)
fig.savefig(OUT/"warm_p01_vs_cold_ax08_tau.png",dpi=175)
plt.close(fig)

fig,ax=plt.subplots(figsize=(9,4.8),constrained_layout=True)
ax.plot(times,last,marker="o",label="P01 probability of last scattering in cell")
ax.set_xlabel("Cell end, elapsed proper time / 1e11 s")
ax.set_ylabel("Finite-window last-scatter cell probability")
ax.grid(alpha=.25)
ax.legend()
ax.set_title("Archived warm P01 only; not observer CMB visibility")
fig.savefig(OUT/"warm_p01_last_scatter_cells.png",dpi=175)
plt.close(fig)

# Matched numerical result over exactly the same five actual saved arrays.
loaded=[cold.load_case(owner,key) for key in cold.CASE_REL]
arrays=[d["arrays"] for d in loaded]
def serial():
    return [cold.optical_history(a["t"],a["ne"],cold.BOUNDARIES) for a in arrays]
def parallel(pool):
    return list(pool.map(lambda a:cold.optical_history(a["t"],a["ne"],cold.BOUNDARIES),arrays))
serial()
timings={"serial_5case_s":[],"thread2_5case_s":[]}
with ThreadPoolExecutor(max_workers=2) as workers:
    for i in range(24):
        begin=time.perf_counter(); ref=serial()
        timings["serial_5case_s"].append(time.perf_counter()-begin)
        begin=time.perf_counter(); actual=parallel(workers)
        timings["thread2_5case_s"].append(time.perf_counter()-begin)
        for a,b in zip(ref,actual):
            if not np.array_equal(a,b):raise RuntimeError("UNSAFE_PARALLEL_REDUCTION")
med={k:statistics.median(v) for k,v in timings.items()}
speed=med["serial_5case_s"]/med["thread2_5case_s"]
bench={
 "schema":"rei.axbi.p01_bridge_kernel_benchmark.v1",
 "status":"MATCHED_NUMERICAL_PARITY_24_REPEAT",
 "workers":2,"data_sharing":"read only per-case numpy arrays, independent q cases",
 "cpu_note":"Remote commands ran under taskset -c 2,3, science owner PID1099975 uses CPU0",
 "kernel":"five-case postprocessing optical-history integration, 16 sample windows",
 "median_s":med,"serial_over_parallel_speedup":speed,
 "faster_choice":"threads_2" if speed>1 else "serial_due_to_thread_overhead",
 "one_case_mean_stored_prefix_rows":statistics.mean([d["prefix_rows"] for d in loaded]),
 "scoped_time_bound_s":1e11,
 "original_case_accepted_rows":200001,
 "not_ode_solver_speedup":True,
 "trials":timings
}
(OUT/"bench_matched.json").write_text(json.dumps(bench,indent=2)+"\n")
print(json.dumps({k:bench[k] for k in
    ("status","median_s","serial_over_parallel_speedup","faster_choice",
     "one_case_mean_stored_prefix_rows")},indent=2))
