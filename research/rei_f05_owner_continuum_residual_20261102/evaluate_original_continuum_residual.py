#!/usr/bin/env python3
"""Actual source F05 26-event continuous RHS sampled on V2 t160→161→162.
Original photon/OTS/thermal/forcing unchanged. Numerical samples, NOT an LTE proof.
"""
import argparse,csv,gzip,hashlib,importlib.util,io,json,math,subprocess,sys
from pathlib import Path
import numpy as np
N=46080; TICKS=131072; KB=1.380649e-16; EV=1.602176634e-12
CHI_H=13.598434599702;CHI_HEI=24.587389011;CHI_HEII=54.41776
OWNER="645437697d915da45147071e266bc47937e76f6c"
SRC="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
KERN="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
POLICY="c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9"
T160="74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6"
T161="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823"
T162="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b"
SITES=(0,.25,.5,.75,1.)
WEIGHTS=(1/12,4/12,2/12,4/12,1/12)
COORDS=("x_HI","x_HeI","r_HeIII","logT")
COLS=["interval_a","interval_b","site","proper_time_s","cell","N_H","N_He",
      *[f"y_{x}" for x in COORDS],*[f"f_{x}" for x in COORDS],
      *[f"slope_{x}" for x in COORDS],*[f"res_{x}" for x in COORDS],
      "N_e","B_erg","U_gas_erg","dNe_dt_s_inv","Bdot_erg_s","Udot_erg_s","v_source"]
def need(ok,what):
    if not ok: raise ValueError("REI_ORIGINAL_CONTINUUM_FAIL_CLOSED_"+what)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for z in iter(lambda:f.read(4<<20),b""):h.update(z)
    return h.hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    need(spec is not None and spec.loader is not None,"MODULE")
    obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj)
    return obj
def total(a):return math.fsum(np.asarray(a,dtype=np.float64).ravel().tolist())
def source_point(p0,p1,l0,l1,nH,nHe,edge):
    p=edge.element_conserving_parent_candidate(p0,p1,nH,nHe)
    logt=(np.asarray(l0)+np.asarray(l1))/2
    need(p.shape==(N,5) and logt.shape==(N,),"POINT_SHAPE")
    need(np.all(np.isfinite(p)) and np.all(np.isfinite(logt)),"POINT_FINITE")
    need(np.max(np.abs((p[:,0]+p[:,1]-nH)/nH))<1e-14,"H_NUCLEI")
    need(np.max(np.abs((p[:,2]+p[:,3]+p[:,4]-nHe)/nHe))<1e-14,"HE_NUCLEI")
    xhi=p[:,0]/nH;xhei=p[:,2]/nHe;r=p[:,4]/(p[:,3]+p[:,4])
    y=np.ascontiguousarray(np.vstack((xhi,xhei,r,logt)))
    need(np.all((y[:3]>0)&(y[:3]<1)) and np.all(np.exp(logt)<1e5),"SOURCE_PHYSICAL_CONE")
    return y
def physics(y,f,nH,nHe):
    a,b,r,l=y;fa,fb,fr,fl=f
    h2=nH*(1-a);he2=nHe*(1-b)*(1-r);he3=nHe*(1-b)*r
    ne=h2+he2+2*he3
    dh2=-nH*fa
    dhe2=-nHe*((1-r)*fb+(1-b)*fr)
    dhe3=nHe*(-r*fb+(1-b)*fr)
    dne=dh2+dhe2+2*dhe3
    B=EV*(CHI_H*h2+CHI_HEI*(he2+he3)+CHI_HEII*he3)
    bdot=EV*(CHI_H*dh2+CHI_HEI*(dhe2+dhe3)+CHI_HEII*dhe3)
    U=1.5*KB*(nH+nHe+ne)*np.exp(l)
    udot=U*(fl+dne/(nH+nHe+ne))
    return ne,B,U,dne,bdot,udot
def main(a):
    repo=Path(a.repo).resolve()
    need(subprocess.check_output(["git","-C",str(repo),"rev-parse","HEAD"],text=True).strip()==a.code_head,"GIT_HEAD")
    need(subprocess.run(["git","-C",str(repo),"merge-base","--is-ancestor",OWNER,"HEAD"],check=False).returncode==0,"SOURCE_OWNER_ANCESTRY")
    need(not subprocess.check_output(["git","-C",str(repo),"status","--porcelain","--untracked-files=no"],text=True).strip(),"DIRTY_ORIGINAL")
    stage=next(repo.glob("stages/*UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY"))
    kernel=next(repo.glob("stages/*CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK/analysis/interval_discrete_map.py"))
    need(sha(stage/"local_results/first_interval_r2_blocked_minimum_step.tar.gz")==SRC,"ARCHIVE_SOURCE_SHA")
    need(sha(stage/"analysis/adaptive_policy.py")==POLICY and sha(kernel)==KERN,"KERNEL_POLICY_SHA")
    need(sha(a.accepted160)==T160 and sha(a.v2161)==T161 and sha(a.v2162)==T162,"PR369_REAL_SOURCE_STATES")
    worker=module("rei_continuum_original_worker",stage/"analysis/attempt_worker.py")
    edge=module("rei_continuum_original_edge",repo/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
    worker.jax_guard.install_if_missing()
    m=worker._kernel()
    base,_,_,nH,nHe=worker._context(m,"LOCAL_NEUTRAL_HAZARD_PRIMARY")
    model=m.rim.ReducedIntervalModel.from_repo(repo)
    accepted=worker.state_io.read_state(Path(a.accepted160),expected_sha256=T160)
    with np.load(a.v2161,allow_pickle=False) as z161,np.load(a.v2162,allow_pickle=False) as z162:
        for old,new in (("source_parent_population_lower","population_lower"),
                        ("source_parent_population_upper","population_upper"),
                        ("source_parent_logT_lower","log_temperature_lower"),
                        ("source_parent_logT_upper","log_temperature_upper")):
            need(np.array_equal(z161[old],getattr(accepted,new)),"SOURCE_ACCEPTED_PARENT_"+old)
        def endpoint(z):
            return source_point(z["population_lower"],z["population_upper"],
                z["log_temperature_lower"],z["log_temperature_upper"],nH,nHe,edge)
        ys=(source_point(accepted.population_lower,accepted.population_upper,
                accepted.log_temperature_lower,accepted.log_temperature_upper,nH,nHe,edge),
            endpoint(z161),endpoint(z162))
    dt=float(base.forcing.duration_seconds(0))/TICKS
    need(abs(dt/4871848749.16828-1)<2e-15,"ORIGINAL_TICK_PROPER_TIME")
    raw=Path(a.raw);out=Path(a.summary)
    need(not raw.exists() and not out.exists(),"NO_OVERWRITE")
    raw.parent.mkdir(parents=True,exist_ok=True);out.parent.mkdir(parents=True,exist_ok=True)
    result={"schema":"REI_F05_ORIGINAL_26EVENT_10SITE_CONTINUUM_RESIDUAL_V1",
      "immutable_parent_pr":369,"immutable_parent_head":OWNER,"run_code_head":a.code_head,
      "original_source_tar_sha256":SRC,"original_kernel_sha256":KERN,
      "original_V1_policy_sha256":POLICY,"original_accepted_tick160_sha256":T160,
      "research_V2_tick161_npz_sha256":T161,"research_V2_tick162_npz_sha256":T162,
      "source_cells":N,"original_proper_tick_seconds":dt,
      "physical_realizations":1,"s_samples":list(SITES),"simpson_weights":list(WEIGHTS),
      "sampled_path_type":"NUCLEI_CONSERVING_SOURCE_ENDPOINT_LINEAR_REDUCED_COORDS",
      "source_rhs_operator":"UNCHANGED_ORIGINAL_26EVENT_F05_NONAUTONOMOUS_FLOAT_REFERENCE",
      "path_residual_status":"NUMERICALLY_EVALUATED_SAMPLES_NOT_CONTINUUM_SUP_ENCLOSURE",
      "epochs":[],"official_tick161":False,"official_tick162":False,
      "DAG":{"central":"28/88","working":"33/88_NONADDITIVE","physical_fast":"4/7","delta":0},
      "production":"HOLD"}
    with raw.open("xb") as f0:
      with gzip.GzipFile(fileobj=f0,mode="wb",filename="",mtime=0,compresslevel=6) as g:
       with io.TextIOWrapper(g,encoding="ascii",newline="",write_through=True) as stream:
        writer=csv.writer(stream,lineterminator="\n");writer.writerow(COLS)
        for i,(ta,tb) in enumerate(((160,161),(161,162))):
            left,right=ys[i:i+2]
            slope=(right-left)/dt
            integ=np.zeros((4,N),dtype=np.float64)
            info={"original_tick_interval":[ta,tb],"source_samples":[]}
            for s,w in zip(SITES,WEIGHTS):
                y=(1-s)*left+s*right;t=(ta+s)*dt
                v=model.source_v_point(y[3])
                F=model.floating_reference_rhs(coordinates=y,time_s=t,v=v,f=0.1)
                need(F.shape==(4,N) and np.isfinite(F).all(),"ORIGINAL_RHS_FINITE")
                residual=slope-F
                integ+=w*dt*residual
                ne,B,U,dne,bdot,udot=physics(y,F,nH,nHe)
                vals={"site":s,"source_proper_time_s":t,"original_tick_float":ta+s,
                  "global_S_HI":total(nH*y[0]),
                  "global_S_HeI":total(nHe*y[1]),
                  "global_S_HeII":total(nHe*(1-y[1])*(1-y[2])),
                  "global_N_e":total(ne),"global_B_erg":total(B),
                  "global_U_gas_erg":total(U),"global_dNe_dt_s_inv":total(dne),
                  "global_original_Bdot_erg_s":total(bdot),"global_original_Udot_erg_s":total(udot),
                  "v_source_minmax":[float(v.min()),float(v.max())],
                  "h_times_sample_max_abs_residual":[float(dt*np.max(np.abs(x))) for x in residual],
                  "h_times_sample_rms_residual":[float(dt*np.sqrt(np.mean(x*x))) for x in residual]}
                info["source_samples"].append(vals)
                for j in range(N):
                    values=(nH,nHe,*y,*F,*slope,*residual,ne,B,U,dne,bdot,udot,v)
                    writer.writerow([ta,tb,format(s,".17e"),format(t,".17e"),j,
                                     *[format(float(x[j]),".17e") for x in values]])
                print(json.dumps({"interval":[ta,tb],"site":s,"Bdot":vals["global_original_Bdot_erg_s"],
                    "Udot":vals["global_original_Udot_erg_s"],"h_times_r_max":vals["h_times_sample_max_abs_residual"]}),flush=True)
            info["sampled_simpson_signed_residual_sum"]=[total(q) for q in integ]
            info["sampled_simpson_max_abs_residual_by_coord"]=[float(np.max(np.abs(q))) for q in integ]
            info["sampled_simpson_rms_residual_by_coord"]=[float(np.sqrt(np.mean(q*q))) for q in integ]
            info["sampled_simpson_not_rigorous_integration"]=True
            result["epochs"].append(info)
    result["original_source_point_evaluations"]=2*len(SITES)
    result["actual_source_cell_site_rows"]=2*N*len(SITES)
    result["private_raw_csv_gzip_sha256"]=sha(raw)
    result["private_raw_csv_gzip_bytes"]=raw.stat().st_size
    result["V1_old_tick161_error"]="2.1245050576368385e-4 > 2e-4_HISTORICAL_FAIL"
    result["V2_discrete_defect"]="5.387144148931529e-6_UNPROVEN_CONTINUUM"
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"original_RHS_points":result["original_source_point_evaluations"],
        "source_records":result["actual_source_cell_site_rows"],"source_sha":sha(raw),
        "public_sha":sha(out),"simpson_max":[max(x["sampled_simpson_max_abs_residual_by_coord"]) for x in result["epochs"]],
        "DAG":"28/88"}),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for k in ("repo","code-head","accepted160","v2161","v2162","raw","summary"):
        p.add_argument("--"+k,required=True)
    main(p.parse_args())
