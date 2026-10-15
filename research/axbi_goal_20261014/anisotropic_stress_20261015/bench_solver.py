#!/usr/bin/env python3
"""Benchmark matched-accuracy actual new coupled Einstein ODE pilot.

No legacy H/He source running; source free radiation, optional viscous thermal.
Differentiate overhead of native-radiation moment microkernel vs whole coupled
background ODE, tests identical eigengeometry stress physics for 4 cases.
"""
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import statistics
import time
import numpy as np
from coupled_pi import Solver,PhysicalScenario,sigma_init_from_legacy_signed_ratio
HERE=Path(__file__).resolve().parent
def specs():
    a=sigma_init_from_legacy_signed_ratio(.005)[0]
    b=sigma_init_from_legacy_signed_ratio(.01)[0]
    return [(a,1,1.,0.),(a,-1,1.,.02),(b,1,1.,.02),(b,-1,1.,.02)]
def run_one(spec,method):
    m=PhysicalScenario(*spec)
    solver=Solver(m,moment_method=method)
    solution,infos,_=solver.solve(n=201,rtol=5e-11,atol=3e-13)
    return np.asarray(solution.y,dtype=float),solution.nfev,solver.moments.evals
def batch(method,parallel=False):
    S=specs()
    if not parallel:
        return [run_one(z,method) for z in S]
    with ThreadPoolExecutor(max_workers=2) as pool:
        return list(pool.map(lambda z:run_one(z,method),S))
def profile():
    timings={z:[] for z in ("series_serial","gl128_serial","series_thread2")}
    outputs={}
    for x in range(7):
        for key,mode,parallel in (
          ("series_serial","taylor14",False),
          ("gl128_serial","gl128",False),
          ("series_thread2","taylor14",True)):
            t=time.perf_counter()
            outputs[key]=batch(mode,parallel)
            timings[key].append(time.perf_counter()-t)
        for a,b in zip(outputs["series_serial"],outputs["gl128_serial"]):
            if np.max(abs(a[0]-b[0]))>1e-10:
                raise RuntimeError("CROSS_QUADRATURE_EVOLUTION_NOT_MATCHED")
        for a,b in zip(outputs["series_serial"],outputs["series_thread2"]):
            if not np.array_equal(a[0],b[0]):
                raise RuntimeError("THREAD2_IS_NOT_DETERMINISTIC")
    centers={key:statistics.median(values) for key,values in timings.items()}
    errors=[]
    for a,b in zip(outputs["series_serial"],outputs["gl128_serial"]):
        errors.append({"max_abs_b":float(np.max(abs(a[0][0]-b[0][0]))),
           "max_abs_signed_s_scaled":float(np.max(abs(a[0][1]-b[0][1]))),
           "max_abs_thermal_energy_density_scaled":float(np.max(abs(a[0][2]-b[0][2]))),
           "max_abs_elapsed_t_times_Href":float(np.max(abs(a[0][3]-b[0][3]))),
           "nfev_taylor":a[1],"nfev_gl128":b[1]})
    result={
        "schema":"rei.axbi.sourcefree_sigma_pi_coupled_ode_perf.v1",
        "status":"MATCHED_COUPLED_EINSTEIN_BACKGROUND_TAYLOR14_GL128_PASS",
        "scoped_model":"source-free collisionless radiation and optional phenomenological viscous matter heat, NOT original HHe RT chemistry",
        "scenarios":specs(),"trial_repetitions":7,
        "timing_seconds":timings,"median_seconds":centers,
        "series_over_gl128_speedup":centers["gl128_serial"]/centers["series_serial"],
        "parallel_over_serial_speedup":centers["series_serial"]/centers["series_thread2"],
        "recommended":"taylor14_two_threads" if centers["series_thread2"]<centers["series_serial"] else "taylor14_serial",
        "max_equivalent_evolution_errors":errors,
        "scoped_speedup":"4-case toy coupled-background ODE wall, not original native ionization photon solver",
        "scientific_admission":"NOT_ISSUED"
    }
    (HERE/"results/bench_solver.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ("status","median_seconds",
         "series_over_gl128_speedup","parallel_over_serial_speedup",
         "recommended","max_equivalent_evolution_errors")},indent=2))
if __name__=="__main__":profile()
