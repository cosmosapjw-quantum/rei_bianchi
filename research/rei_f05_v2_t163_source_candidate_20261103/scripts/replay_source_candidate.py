#!/usr/bin/env python3
"""Source-native REI F05 162->163 research candidate only.
Runs the original 26-event full/half/half maps in three frozen shape lanes.
It does not accept a history tick, install production control, or certify a
continuum ODE error. Original V1 and existing research transactions are read-only.
"""
import argparse,hashlib,importlib.util,json,math,subprocess,sys
from pathlib import Path
import numpy as np
LANES={"LOCAL_NEUTRAL_HAZARD_PRIMARY":"primary","RECOMBINATION_WEIGHTED_AUDITOR":"recomb","SCRIPT_SELF_SHIELDING_AUDITOR":"shield"}
SRC="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
KERN="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
V1POL="c648c0ae1e10bced3b159e96f92bdc5f2bd3c1031b9a13e6b947dbf102557aa9"
P162="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b"
RUNTIME="97b00826f518aa7a2c258dae15d1e92918b44a04b6f928e2014241bbba2f0075"
LIMIT=2e-4;WIDTH=2e-3;N=46080;FIELDS=("x_HII","x_HeII","x_HeIII","log_T")
def fail(x,s):
 if not x:raise ValueError("V2_RESEARCH_T163_"+s)
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(4<<20),b""):h.update(b)
 return h.hexdigest()
def module(s,path):
 spec=importlib.util.spec_from_file_location(s,path)
 x=importlib.util.module_from_spec(spec);sys.modules[s]=x;spec.loader.exec_module(x);return x
def run(a):
 repo=Path(a.repo);target=Path(a.output)
 fail(not target.exists(),"NO_OVERWRITE")
 stage=next(repo.glob("stages/*UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY"))
 fail(sha(stage/"local_results/first_interval_r2_blocked_minimum_step.tar.gz")==SRC,"ORIGINAL_ARCHIVE")
 fail(sha(stage/"analysis/adaptive_policy.py")==V1POL,"OLD_POLICY")
 owner=module("v2new_owner",repo/"research/rei_f05_owner_v2_shadow_20261101/owner_v2_shadow.py")
 mm=module("v2new_residual",repo/"research/rei_f05_mmatrix_residual_20261101/residual_certificate.py")
 worker=module("v2new_worker",stage/"analysis/attempt_worker.py")
 head=subprocess.run(["git","rev-parse","HEAD"],cwd=repo,text=True,capture_output=True,check=False)
 fail(head.returncode==0 and head.stdout.strip()=="a2a3ff5d77e6f3b96275b8787f3b4b109c7bbd78","EXACT_SOURCE_GIT_HEAD")
 runtime=worker.runtime_contract.verify(RUNTIME,repo,stage)
 fail(runtime["sha256"]==RUNTIME,"EXACT_FULL_RUNTIME_CONTRACT")
 fail(sha(worker.KERNEL_PATH)==KERN,"ORIGINAL_KERNEL")
 fail(sha(a.source162)==P162,"ORIGINAL_T162_SOURCE")
 chk=json.loads((Path(a.txrun)/"CONTROL.json").read_text())
 fail(chk["versioned_branch_accepted_tick"]==162 and chk["official_original_production_advance"] is False,"PR372_CONTROL")
 worker.jax_guard.install_if_missing()
 m=worker._kernel()
 inc=mm.load_original()
 target.mkdir(parents=True)
 with np.load(a.source162,allow_pickle=False) as z:
  for key in ("population_lower","population_upper","log_temperature_lower","log_temperature_upper"):
   fail(key in z.files,"SOURCE162_FIELD")
  P=m._I(z["population_lower"],z["population_upper"])
  Z=m._I(z["log_temperature_lower"],z["log_temperature_upper"])
 receipts={};bodies=set();npzs=set()
 for lane,slug in LANES.items():
  base,_,_,nh,nhe=worker._context(m,lane)
  model=m.rim.ReducedIntervalModel.from_repo(repo)
  duration=float(base.forcing.duration_seconds(0))
  t0=duration*(162/131072);t1=duration*(163/131072);tm=t0+.5*(t1-t0)
  maps={};incs={};details={}
  old_inc=inc.krawczyk_increment
  def common_parent(mod,parent,flux,den,dt,hyd,helium):
   return mm.structural_residual_increment(mod,parent,flux,den,dt,hyd,helium,inc)
  inc.krawczyk_increment=common_parent
  try:
   for name,pp,zz,begin,end in (("full",P,Z,t0,t1),("half1",P,Z,t0,tm),("half2",None,None,tm,t1)):
    if name=="half2":pp=maps["half1"].population;zz=maps["half1"].log_temperature
    state,delta,meta=inc.original_map(m,model,base,name,pp,zz,begin,end,nh,nhe)
    fail(state.certified and delta is not None and meta["original_table_event_count"]==0,"ORIGINAL_MAP_"+slug+"_"+name)
    maps[name]=state;incs[name]=delta;details[name]=meta
  finally: inc.krawczyk_increment=old_inc
  state=maps["half2"];full=maps["full"];pop=state.population
  ledgers=owner.source_ledgers(m,model,state,t0,tm,t1,nh,nhe)
  fail(len(ledgers)==14 and set(ledgers)==set(worker.policy.EXPECTED_LEDGER_KEYS),"NATIVE_LEDGER_KEYS_"+slug)
  fail(all(math.isfinite(x) and math.isfinite(y) and x<=0<=y for x,y in ledgers.values()),"LEDGER_ZERO_"+slug)
  events=worker.summarize_events(full.table_events+maps["half1"].table_events+state.table_events)
  fail(not events["any_event"] and events["node_count"]==0,"ORIGINAL_EVENTS_"+slug)
  widths={"x_HII":float(np.max((pop.hi[:,1]-pop.lo[:,1])/nh)),"x_HeII":float(np.max((pop.hi[:,3]-pop.lo[:,3])/nhe)),"x_HeIII":float(np.max((pop.hi[:,4]-pop.lo[:,4])/nhe)),"log_T":float(np.max(state.log_temperature.hi-state.log_temperature.lo))}
  defect={}
  for key in FIELDS:
   q=incs["full"][key]-(incs["half1"][key]+incs["half2"][key])
   v=inc.interval_upper(q)
   fail(v.shape==(N,) and np.isfinite(v).all(),"DEFECT_SOURCE_"+slug+"_"+key)
   defect[key]=float(np.max(v))
  fail(max(defect.values())<LIMIT and max(widths.values())<WIDTH,"FIXED_GATES_"+slug)
  worker.policy._validate_post_map_metrics({"public_widths":widths,"set_ledgers":ledgers,"diagnostics":{"map_enclosed":True,"validated_local_error_bounds":defect,"maximum_validated_local_error":max(defect.values())}},"PASS",lane)
  xdir=target/slug;xdir.mkdir()
  npz=xdir/"NEW_SOURCE_TICK163.npz"
  with npz.open("xb") as f:
   np.savez_compressed(f,population_lower=pop.lo,population_upper=pop.hi,log_temperature_lower=state.log_temperature.lo,log_temperature_upper=state.log_temperature.hi)
  arrs=(pop.lo,pop.hi,state.log_temperature.lo,state.log_temperature.hi)
  body=b"".join(np.ascontiguousarray(np.asarray(x,dtype="<f8")).tobytes() for x in arrs)
  bh=hashlib.sha256(body).hexdigest()
  bodies.add(bh);npzs.add(sha(npz))
  receipt={"schema":"REI_F05_V2_NEXT163_NATIVE_ORIGINAL_SOURCE_V1","lane":lane,"parent162_original_npz_sha256":P162,"source_tar_sha256":SRC,"source_kernel_sha256":KERN,"source_proper_times_hex":[t0.hex(),tm.hex(),t1.hex()],"full_sevenpin_runtime_sha256":RUNTIME,"native_map_receipts":details,"original_14_ledgers":ledgers,"original_table_event_count":0,"source_correlated_discrete_defect":defect,"original_public_widths":widths,"old_V1_failure_kept":True,"new162to163_source_state_sha256":sha(npz),"physical_body_sha256":bh,"official_original_V1_tick":160,"acceptance":"V2_POLICY_CANDIDATE_NOT_YET_CONTROL","continuous_ode_error_certified":False}
  (xdir/"NATIVE_RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
  receipts[lane]={"native_receipt_sha256":sha(xdir/"NATIVE_RECEIPT.json"),"source_new_state_sha256":sha(npz),"physical_body_sha256":bh,"local_estimator":defect,"public_width":widths}
  print(json.dumps({"lane":slug,"new_source_tick":163,"native_original_maps":3,"max_defect":max(defect.values()),"max_width":max(widths.values()),"body":bh}),flush=True)
 fail(len(bodies)==1 and len(npzs)==1,"LANES_NOT_ONE_PHYSICAL_REALIZATION")
 output={"schema":"REI_F05_V2_NEW_T163_ORIGINAL_PHYSICS_V1","source_original_tar_sha256":SRC,"source_original_26event_kernel_sha256":KERN,"source_research_tick162_npz_sha256":P162,"full_runtime_sha256":RUNTIME,"native_maps":9,"lanes":receipts,"physical_realizations":1,"new_source_tick163_npz_sha256":next(iter(npzs)),"new_physical_body_sha256":next(iter(bodies)),"old_V1_accepted_tick":160,"candidate_V2_next_tick":163,"original_14_ledgers":"ALL_LANES_PASS","source_discrete_estimator":"PASS_NEW_V2_ONLY","continuum_ode_error_certified":False,"official_V1_tick163":False,"production_control":"NOT_YET_INSTALLED"}
 (target/"PUBLIC_NEXT163.json").write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"SOURCE_MAP_162_TO_163":"PASS","original_native_maps":9,"sha256":next(iter(npzs)),"current_V1_tick":160}),flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for k in ("repo","txrun","source162","output"):p.add_argument("--"+k,required=True)
 a=p.parse_args();run(a)
