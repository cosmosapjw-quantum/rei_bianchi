"""HE20: source-pinned native Rust MD14 spectral-threshold run and audit."""
import argparse, csv, hashlib, json, math, os, pathlib, subprocess, time
from concurrent.futures import ProcessPoolExecutor
FIELDS=("q","m","steps","born_n","born_u","final_u","redshift_work",
        "below_hi_n","below_hei_n","below_heii_n",
        "below_hi_u","below_hei_u","below_heii_u",
        "parent_n_residual","parent_u_residual","support_violations")
QS=(-0.005,0.,0.005)
MS=(4,8,16,32,64,128)
STEPS=(1,8,32,128)

def run_one(item):
    exe,q,m,step=item
    p=subprocess.run([str(exe),str(q),str(m),str(step)],
                     capture_output=True,text=True,timeout=90)
    if p.returncode: raise RuntimeError(f"q={q},m={m},step={step}: {p.stderr}")
    cols=p.stdout.strip().split(",")
    if len(cols)!=len(FIELDS): raise RuntimeError(f"bad row {cols}")
    d=dict(zip(FIELDS,cols))
    for key in FIELDS:d[key]=int(d[key]) if key in ("m","steps","support_violations") else float(d[key])
    return d

def suite(exe,workers):
    jobs=[(exe,q,m,st) for q in QS for m in MS for st in STEPS]
    start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows=list(pool.map(run_one,jobs))
    rows.sort(key=lambda r:(r["q"],r["m"],r["steps"]))
    return rows,time.perf_counter()-start

def original_c8(path):
    with open(path,newline="") as f:
        return {(int(r["cells_per_segment"]),int(r["substeps"])):r for r in csv.DictReader(f)}

def scientific_gate(rows,fixture):
    checked=0;max_num=max_en=max_parent=0.
    cases=[]
    for r in rows:
        n,u=r["born_n"],r["born_u"]
        if not(n>0 and u>0):raise AssertionError("nonpositive source")
        nerr=abs(r["parent_n_residual"])/n
        uerr=abs(r["parent_u_residual"])/u
        werr=abs(u-r["final_u"]-r["redshift_work"])/u
        max_num=max(max_num,nerr);max_en=max(max_en,werr);max_parent=max(max_parent,uerr)
        if max(nerr,uerr,werr)>5e-12:raise AssertionError(f"source ledger: {r}")
        if r["support_violations"]:raise AssertionError(f"threshold-straddling child: {r}")
        if not(0<=r["below_hi_n"]<=r["below_hei_n"]<=r["below_heii_n"]<=n*(1+1e-11)):
            raise AssertionError("negative or unordered species partition")
        if r["q"]==0 and (r["m"],r["steps"]) in fixture:
            old=fixture[(r["m"],r["steps"])]
            previous=float(old["source_n_per_H"])
            if abs(n-previous)>3e-10*previous:
                raise AssertionError(f"native source mismatch m{r['m']} t{r['steps']}")
            old_lost=float(old["boundary_n_fraction"])
            physical=r["below_hi_n"]/n
            cases.append(dict(m=r["m"],steps=r["steps"],old_boundary_fraction=old_lost,
                              actual_continuum_subthreshold_fraction=physical,
                              old_boundary_over_physical=old_lost/physical if physical else None))
            checked+=1
    return dict(signed_q_values=list(QS),energy_resolutions=list(MS),steps=list(STEPS),
                cases=len(rows),q0_native_original_source_comparisons=checked,
                max_number_parent_relative_defect=max_num,
                max_energy_parent_relative_defect=max_parent,
                max_energy_work_relative_defect=max_en,
                comparisons=cases)

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--binary",required=True)
    ap.add_argument("--fixture",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--workers",type=int,default=16)
    ap.add_argument("--repeat",type=int,default=2)
    args=ap.parse_args()
    out=pathlib.Path(args.out);out.mkdir(parents=True,exist_ok=True)
    fx=original_c8(args.fixture)
    durations={"serial":[],"parallel":[]}
    baseline=None
    for rep in range(args.repeat):
        for tag,w in (("serial",1),("parallel",args.workers)):
            rows,wall=suite(args.binary,w);durations[tag].append(wall)
            if baseline is not None and rows!=baseline:
                raise AssertionError(f"serial/parallel scientific result mismatch {tag} rep{rep}")
            baseline=rows
    report=scientific_gate(baseline,fx)
    report.update(schema="bass_he.he20.native_source_threshold.v1",
                  source_scope="ACTUAL_REI_MICROPHYSICS_RUST_MD14_AND_BIANCHI_KILLING_NO_CHEM",
                  input_original_c8_sha256=sha(args.fixture),
                  binary_sha256=sha(args.binary),
                  executions=args.repeat*2*len(baseline),
                  process_workers=args.workers,
                  wall_seconds=durations,
                  serial_parallel_numeric_identity=True)
    keys=tuple(FIELDS)
    with open(out/"HE20_NATIVE_72_CASES.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(baseline)
    with open(out/"RESULT_STATUS.json","w") as f:json.dump(report,f,indent=2,sort_keys=True)
    print(json.dumps({k:v for k,v in report.items() if k!="comparisons"},indent=2,sort_keys=True))
    chosen=[x for x in report["comparisons"] if x["m"]==16 and x["steps"]==128]
    print("CASE_M16_N128",chosen[0] if chosen else "not found")

if __name__=="__main__":main()
