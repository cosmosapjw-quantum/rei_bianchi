"""Independent NCP parallel source moment/edge convergence study."""
import csv,json,math,os,time
from concurrent.futures import ProcessPoolExecutor
from md14_edge_flux import audit,independent_reference

MS=(4,8,16,32,64,128,256,512,1024)
HS=(0.,math.log(21/20.998),1.e-3,1.e-2,math.log(21/20.))
def one(item):
    m,h=item
    z=audit(m,h)
    ref=independent_reference(h)
    z["reference_fraction"]=ref
    z["fraction_error"]=z["physical_below13p6_fraction"]-ref
    return z
def main():
    jobs=[(m,h) for h in HS for m in MS]
    workers=min(16,len(jobs))
    ts=time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows=list(pool.map(one,jobs))
    wall=time.perf_counter()-ts
    with open("results/SOURCE_EDGE_45_CASES.csv","w",newline="") as f:
        keys=("m","h","physical_below13p6_fraction","native_first_node_ghost_fraction",
              "reference_fraction","fraction_error","N_residual","U_residual_eV")
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
        for row in rows:writer.writerow({k:row[k] for k in keys})
    hn=HS[1]
    ref=independent_reference(hn)
    near=[r for r in rows if r["h"]==hn]
    report={"schema":"bass_he.he19.source_edge_study.v1",
        "scope":"SOURCE_ONLY_CONDITIONAL_SIMPSON32_NO_NATIVE_RUST",
        "rows":len(rows),"parallel_processes":workers,"wall_s":wall,
        "h_native_C8":hn,"reference_native_C8_physical_flux_fraction":ref,
        "native_C8_ghost_first_node_fraction_by_m":
          {str(r["m"]):r["native_first_node_ghost_fraction"] for r in near},
        "physical_flux_fraction_by_m":
          {str(r["m"]):r["physical_below13p6_fraction"] for r in near},
        "largest_reference_absolute_error":max(abs(r["fraction_error"]) for r in rows),
        "largest_normalized_number_defect":max(abs(r["N_residual"])/r["emitted_n"] for r in rows),
        "largest_normalized_energy_defect":max(abs(r["U_residual_eV"])/r["emitted_u_eV"] for r in rows)}
    with open("results/RESULT_STATUS.json","w") as f:
        json.dump(report,f,indent=2,sort_keys=True)
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":main()
