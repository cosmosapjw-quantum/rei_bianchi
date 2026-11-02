#!/usr/bin/env python3
"""Evaluate ORIGINAL REI F05 full 26-event interval RHS over continuous test-curve time slabs.

This is an original-source project-binary64 pathwise enclosure CONDITIONAL
on the interval implementation; no verified IVP tube or continuous error claim.
"""
import argparse,hashlib,importlib.util,json,math,subprocess,sys
from pathlib import Path
import numpy as np

N=46080
O_SOURCE="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
O_KERNEL="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
O_POLICY="c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9"
S160="74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6"
S161="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823"
S162="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b"
PARENT="7c083fffe105cae8bea634f4302dafc9a70cb577"
COORDS=["x_HI","x_HeI","r_HeIII","lnT"]
def need(b,msg):
 if not b:raise RuntimeError("REI_SOURCE_INTERVAL_FAIL_CLOSED_"+msg)
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for x in iter(lambda:f.read(4<<20),b""):h.update(x)
 return h.hexdigest()
def load(n,p):
 spec=importlib.util.spec_from_file_location(n,p)
 need(spec is not None and spec.loader is not None,"MODULE_"+n)
 mod=importlib.util.module_from_spec(spec);sys.modules[n]=mod;spec.loader.exec_module(mod);return mod
def main(a):
 root=Path(a.repo).resolve()
 need(subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()==a.code_sha,"GIT_SOURCE_SHA")
 need(subprocess.run(["git","-C",str(root),"merge-base","--is-ancestor",PARENT,"HEAD"],check=False).returncode==0,"PARENT")
 need(not subprocess.check_output(["git","-C",str(root),"status","--porcelain","--untracked-files=no"],text=True).strip(),"GIT_TRACKED_DIRTY")
 stage=next(root.glob("stages/*UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY"))
 kern=next(root.glob("stages/*CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK/analysis/interval_discrete_map.py"))
 need(sha(stage/"local_results/first_interval_r2_blocked_minimum_step.tar.gz")==O_SOURCE,"ORIGINAL_SOURCE")
 need(sha(stage/"analysis/adaptive_policy.py")==O_POLICY and sha(kern)==O_KERNEL,"ORIGINAL_KERNEL_POLICY")
 need(sha(a.t160)==S160 and sha(a.t161)==S161 and sha(a.t162)==S162,"ORIGINAL_STATE_SHA")
 old=load("interval_source_previous",root/"research/rei_f05_owner_continuum_residual_20261102/evaluate_original_continuum_residual.py")
 worker=load("interval_source_worker",stage/"analysis/attempt_worker.py")
 edge=load("interval_source_edge",root/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
 worker.jax_guard.install_if_missing()
 kernel=worker._kernel()
 base,_,_,nH,nHe=worker._context(kernel,"LOCAL_NEUTRAL_HAZARD_PRIMARY")
 model=kernel.rim.ReducedIntervalModel.from_repo(root)
 interval=kernel.rim.iv
 accepted=worker.state_io.read_state(Path(a.t160),expected_sha256=S160)
 y0=old.source_point(accepted.population_lower,accepted.population_upper,accepted.log_temperature_lower,accepted.log_temperature_upper,nH,nHe,edge)
 with np.load(a.t161,allow_pickle=False) as z161,np.load(a.t162,allow_pickle=False) as z162:
  for key,field in (("source_parent_population_lower","population_lower"),("source_parent_population_upper","population_upper"),("source_parent_logT_lower","log_temperature_lower"),("source_parent_logT_upper","log_temperature_upper")):
   need(np.array_equal(z161[key],getattr(accepted,field)),"V2_RESEARCH_PARENT_"+key)
  def to_y(z):
   return old.source_point(z["population_lower"],z["population_upper"],z["log_temperature_lower"],z["log_temperature_upper"],nH,nHe,edge)
  y1=to_y(z161);y2=to_y(z162)
 dt=float(base.forcing.duration_seconds(0))/131072
 need(abs(dt/4871848749.16828-1.)<2e-15,"ORIGINAL_CLOCK")
 p=Path(a.private);pub=Path(a.public)
 need(not p.exists() and not pub.exists(),"NO_OVERWRITE")
 p.parent.mkdir(parents=True,exist_ok=True);pub.parent.mkdir(parents=True,exist_ok=True)
 records={};output=[]
 for i,(ta,tb) in enumerate(((160,161),(161,162))):
  left,right=([y0,y1,y2][i:i+2])
  slope=(right-left)/dt
  signed_lo=np.zeros_like(slope)
  signed_hi=np.zeros_like(slope)
  slab_records=[]
  for k in range(a.subslabs):
   sa=k/a.subslabs;sb=(k+1)/a.subslabs
   ya=(1-sa)*left+sa*right;yb=(1-sb)*left+sb*right
   lo=np.minimum(ya,yb);hi=np.maximum(ya,yb)
   lo=np.nextafter(lo,-np.inf);hi=np.nextafter(hi,np.inf)
   need(np.all(np.isfinite(lo)) and np.all(np.isfinite(hi)),"SOURCE_BOX_FINITE")
   need(np.all((lo[:3]>0)&(hi[:3]<1)),"ORIGINAL_POSITIVE_CONE")
   Z=interval.Interval(lo,hi)
   v=model.source_v_interval(Z)
   tlo=(ta+sa)*dt;thi=(ta+sb)*dt
   F=model.rhs_interval(coordinates=Z,time_lower_s=tlo,time_upper_s=thi,
                        v_interval=v,f_interval=interval.Interval(0.1))
   need(F.lo.shape==(4,N) and np.all(np.isfinite(F.lo)) and np.all(np.isfinite(F.hi)),"SOURCE_INTERVAL_FINITE")
   residual_lo=np.nextafter(slope-F.hi,-np.inf)
   residual_hi=np.nextafter(slope-F.lo,np.inf)
   signed_lo+=np.nextafter(dt*(sb-sa)*residual_lo,-np.inf)
   signed_hi+=np.nextafter(dt*(sb-sa)*residual_hi,np.inf)
   # For validation only: independently evaluate actual full source point RHS
   # at slab endpoints and midpoint, not a substitute for interval coverage.
   max_violation=0.;outside=0;source_probe=[]
   for ss in (sa,(sa+sb)*.5,sb):
    y=(1-ss)*left+ss*right
    vv=model.source_v_point(y[3])
    f=model.floating_reference_rhs(coordinates=y,time_s=(ta+ss)*dt,v=vv,f=0.1)
    violate=np.maximum(np.maximum(F.lo-f,f-F.hi),0)
    max_violation=max(max_violation,float(np.max(violate)))
    outside+=int(np.count_nonzero((f<F.lo)|(f>F.hi)))
    source_probe.append({"frac":ss,"point_rhs_hi_max":float(np.max(np.abs(f))),
       "max_violation":float(np.max(violate))})
   if outside>0:
    raise RuntimeError(f"ORIGINAL_SOURCE_POINT_NOT_CONTAINED {ta} {tb} slab{k} count={outside} max={max_violation}")
   source_halfwidth=.5*(F.hi-F.lo)
   hRmax=np.maximum(np.abs(dt*residual_lo),np.abs(dt*residual_hi))
   summary={"slab":k,"fraction":[sa,sb],"proper_time_seconds":[tlo,thi],
     "original_f_bounds_max_abs_by_coord":[float(np.max(np.maximum(np.abs(F.lo[c]),np.abs(F.hi[c])))) for c in range(4)],
     "h_times_residual_sup_candidate_by_coord":[float(np.max(hRmax[c])) for c in range(4)],
     "h_times_interval_rhs_halfwidth_max":[float(dt*np.max(source_halfwidth[c])) for c in range(4)],
     "source_v_exact_one_interval_count":int(np.count_nonzero((v.lo<=0)&(v.hi>=1))),
     "source_v_range":[float(v.lo.min()),float(v.hi.max())],
     "source_point_probe_count":len(source_probe),"source_point_coverage_violations":outside,
     "original_source_probes":source_probe}
   slab_records.append(summary)
   records[f"{ta}_{tb}_slab_{k}_lo"]=np.asarray(dt*(sb-sa)*residual_lo,dtype="<f8")
   records[f"{ta}_{tb}_slab_{k}_hi"]=np.asarray(dt*(sb-sa)*residual_hi,dtype="<f8")
   print(json.dumps({"source_interval":[ta,tb],"slab":k,
      "h_sup_logT":summary["h_times_residual_sup_candidate_by_coord"][3],
      "v_boundary_cells":summary["source_v_exact_one_interval_count"],
      "inclusion":"PASS"}),flush=True)
  need(np.all(signed_lo<=signed_hi),"SUM_ENCLOSURE")
  signed_bounds=[[float(np.min(signed_lo[c])),float(np.max(signed_hi[c]))] for c in range(4)]
  max_abs=[float(np.max(np.maximum(np.abs(signed_lo[c]),np.abs(signed_hi[c])))) for c in range(4)]
  records[f"{ta}_{tb}_total_lo"]=signed_lo.astype("<f8")
  records[f"{ta}_{tb}_total_hi"]=signed_hi.astype("<f8")
  output.append({"ticks":[ta,tb],"original_subslabs":a.subslabs,
    "full_time_source_interval_expression":"PROJECT_BINARY64_CONDITIONAL_NOT_MPFR",
    "residual_integral_outer_max_abs_by_coord":max_abs,
    "global_minlo_maxhi_by_coord":signed_bounds,
    "native_source_sample_inclusion_checks":3*a.subslabs,
    "slab_details":slab_records})
 np.savez_compressed(p,**records)
 result={"schema":"REI_F05_ORIGINAL_26EVENT_PATH_INTERVAL_RHS_V1",
   "source_owner_pr":371,"source_owner_sha":PARENT,
   "actual_original_three_state_sha256":[S160,S161,S162],
   "original_source_tar_sha256":O_SOURCE,"original_26event_kernel_sha256":O_KERNEL,
   "original_policy_sha256":O_POLICY,"evaluated_source_code_commit":a.code_sha,
   "actual_cells":N,"actual_physical_realizations":1,
   "nonautonomous_original_source_full_interval_rhs_calls":a.subslabs*2,
   "native_source_point_probes":a.subslabs*2*3,
   "source_interval_confidence":"PROJECT_BINARY64_INTERVAL_ARITHMETIC_CONDITIONAL",
   "not_verified_real_mpfr":True,
   "not_validated_unknown_ode_solution_tube":True,
   "not_certified_continuum_ode_error":True,
   "segments":output,
   "private_interval_fields_npz_sha256":sha(p),
   "private_interval_fields_npz_bytes":p.stat().st_size,
   "original_V1_logT_failure":"2.1245050576368385e-4 > 2e-4",
   "source_V2_discrete_logT":"5.387144148931529e-6 SCOPED_ONLY",
   "official_tick161":False,"official_tick162":False,
   "DAG":{"central":"28/88","working":"33/88_NONADDITIVE","physical_fast":"4/7","delta":0},
   "production":"HOLD"}
 pub.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
 print(json.dumps({"SOURCE_INTERVAL_FULL_TIME_PATH":"EXECUTED",
     "interval_calls":a.subslabs*2,"original_source_probes":a.subslabs*2*3,
     "private_npz_sha256":sha(p),"science_sha256":sha(pub),
     "outer_residual":[seg["residual_integral_outer_max_abs_by_coord"] for seg in output],
     "DAG":"28/88"}),flush=True)
if __name__=="__main__":
 args=argparse.ArgumentParser()
 for v in ("repo","code_sha","t160","t161","t162","private","public"):
  args.add_argument("--"+v.replace("_","-"),dest=v,required=True)
 args.add_argument("--subslabs",type=int,default=4)
 main(args.parse_args())
