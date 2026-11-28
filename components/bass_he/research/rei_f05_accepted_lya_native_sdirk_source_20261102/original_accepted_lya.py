#!/usr/bin/env python3
"""Original accepted F05 [0,64,128,160] HeII Ly-alpha OTS line escape.
Actual SOURCE-ORIGINAL full/half/half 26-event map. Does not create or mutate
a REI state/history and does not claim post-cell causal photon propagation.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,math,subprocess,sys,zipfile
from pathlib import Path
import numpy as np

N=46080
SOURCE_REI_HEAD="70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00"
SOURCE_KERNEL_SHA="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
SOURCE_TAR_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
SOURCE_ARRAY_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
REC195_ZIP_SHA="ed08c131cb61b8cb5c5a52a8dadeb4fc7350945eefc5c2e1c1bf12c1a2052657"
LANE="LOCAL_NEUTRAL_HAZARD_PRIMARY"
STATE={
 64:("private/first64_original_source.state","aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425"),
 128:("private/replayed128_pinned.state","bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6"),
 160:("private/replayed160_pinned.state","74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6")}
INTERVALS=((0,64),(64,128),(128,160))
LOCAL_GATE=2e-4;WIDTH_GATE=2e-3

def digest(data):return hashlib.sha256(data).hexdigest()
def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
 return h.hexdigest()
def req(cond,msg):
 if not cond:raise ValueError("SOURCE_ORIGINAL_F05_LYA_"+msg)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,str(path))
 req(spec is not None and spec.loader is not None,"SOURCE_LOADER_MISSING")
 mod=importlib.util.module_from_spec(spec)
 sys.modules[name]=mod;spec.loader.exec_module(mod)
 return mod
def mids(x):return 0.5*np.asarray(x.lo)+0.5*np.asarray(x.hi)
def global_sum(a):return float(np.sum(a,dtype=np.longdouble))
def iv_pair(a):return [global_sum(a.lo),global_sum(a.hi)]
def zero(a):return bool(np.all(np.asarray(a.lo)<=0) and np.all(np.asarray(a.hi)>=0))
def write_gz(path,rows):
 with Path(path).open("wb") as fout,gzip.GzipFile(filename="",fileobj=fout,mode="wb",compresslevel=6,mtime=0) as gz:
  with io.TextIOWrapper(gz,encoding="utf-8",newline="") as stream:
   writer=csv.writer(stream,lineterminator="\n")
   writer.writerow(("tick_left","tick_right","cell","escaped_photon_lo","escaped_photon_hi",
                    "escaped_energy_lo_erg","escaped_energy_hi_erg","fullstep_energy_hi_erg",
                    "twohalf_vs_full_center_energy_erg"))
   writer.writerows(rows)
 return sha(path)

def accepted_ledger(m,model,step,pop,t0,t1,nh,nhe):
 """Same 14 original-source invariants/limits as protected REC195 owner."""
 gamma=m.sdirk.GAMMA
 z=m.iv.sum_interval
 ledgers={
 "H_nuclei":(float(np.min(pop.lo[:,0]+pop.lo[:,1]-nh)),
             float(np.max(pop.hi[:,0]+pop.hi[:,1]-nh))),
 "He_nuclei":(float(np.min(np.sum(pop.lo[:,2:5],axis=1)-nhe)),
              float(np.max(np.sum(pop.hi[:,2:5],axis=1)-nhe)))}
 for label,event,box,ts in (
  ("stage",step.stage_event,pop,t0+gamma*(t1-t0)),
  ("final",step.final_event,pop,t1)):
  ledgers[label+"_photon_identity"]=(float(np.min(event.photon_identity.lo)),
                                    float(np.max(event.photon_identity.hi)))
  e=event.resolved_heat+event.unresolved_energy+event.escaped_energy+event.chemical_energy
  ledgers[label+"_total_energy"]=(float(np.min(e.lo)),float(np.max(e.hi)))
  for gi,x in enumerate(m.group_photon_residuals(model,box,ts)):
   ledgers[f"{label}_group_{gi}_photon"]=(float(np.asarray(x.lo)),float(np.asarray(x.hi)))
 req(len(ledgers)==14,"ORIGINAL_14_LEDGER_COUNT")
 audit=m.primitive.audit_set_ledgers(ledgers)
 req(bool(audit.all_include_zero),"ORIGINAL_14_LEDGER_NOT_ZERO")
 req(not any(x.any_event for x in step.table_events),"ORIGINAL_TABLE_EVENT")
 return ledgers

def original_physical_error(m,full,two,nh,nhe):
 def physical(step):
  p=step.population; l=step.log_temperature
  return {"x_HII":m._I(p.lo[:,1]/nh,p.hi[:,1]/nh),
          "x_HeII":m._I(p.lo[:,3]/nhe,p.hi[:,3]/nhe),
          "x_HeIII":m._I(p.lo[:,4]/nhe,p.hi[:,4]/nhe),
          "log_T":l}
 f=physical(full);h=physical(two)
 err={k:float(np.max(np.maximum(abs(h[k].lo-f[k].hi),
             abs(h[k].hi-f[k].lo)))) for k in f}
 width={k:float(np.max(h[k].hi-h[k].lo)) for k in h}
 req(max(err.values())<LOCAL_GATE,"ORIGINAL_LOCAL_DEFECT_GATE")
 req(max(width.values())<WIDTH_GATE,"ORIGINAL_PUBLIC_WIDTH_GATE")
 return err,width

def integral(m,step,h):
 g=float(m.sdirk.GAMMA)
 req(0<g<1 and h>0,"ORIGINAL_TIME_OR_GAMMA")
 req(step.certified,"ORIGINAL_STAGE_NOT_CERTIFIED")
 return h*((1-g)*step.stage_event.escaped_energy+g*step.final_event.escaped_energy)

def run(rei,rec_zip,out):
 rei=Path(rei).resolve();rec_zip=Path(rec_zip).resolve();out=Path(out).resolve()
 req(subprocess.check_output(["git","-C",str(rei),"rev-parse","HEAD"],text=True).strip()==SOURCE_REI_HEAD,"REI_HEAD_DRIFT")
 req(sha(rec_zip)==REC195_ZIP_SHA,"REC195_SOURCE_ZIP_SHA_DRIFT")
 edge=load("he151_original_edge",rei/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
 worker=load("he151_original_worker",rei/edge.REL_STAGE/"analysis/attempt_worker.py")
 worker.jax_guard.install_if_missing()
 req(sha(worker.KERNEL_PATH)==SOURCE_KERNEL_SHA,"ORIGINAL_26EVENT_KERNEL_DRIFT")
 m=worker._kernel()
 base,y,logt,nh,nhe=worker._context(m,LANE)
 req(y.shape==(N,5),"ORIGINAL_STATE_GRAIN")
 model=m.rim.ReducedIntervalModel.from_repo(rei)
 accept160,src=edge.source_state(rei/edge.REL_STAGE,LANE,worker.state_io)
 req(src["archive_sha256"]==SOURCE_TAR_SHA and src["accepted_array_sha256"]==SOURCE_ARRAY_SHA,"ORIGINAL_ACCEPTED160_DRIFT")
 E_eV=float(m.rim.HEII_LYA_EV);EV=float(m.rim.EV_ERG)
 req(abs(E_eV-40.81332)<1e-12,"SOURCE_HEII_LYA_ENERGY_CHANGED")
 E_erg=E_eV*EV
 req(float(m.rim.CHI_H_EV)<E_eV and float(m.rim.CHI_HEI_EV)<E_eV and E_eV<float(m.rim.CHI_HEII_EV),"PHOTO_THRESHOLD_ORDER_CHANGED")
 time_total=float(base.forcing.duration_seconds(0))
 source_states={0:(m._I(y,y),m._I(logt,logt))}
 with zipfile.ZipFile(rec_zip) as z:
  req(z.testzip() is None,"REC195_ZIP_CRC")
  for tick,(path,want) in STATE.items():
   raw=z.read(path)
   req(digest(raw)==want,"ACCEPTED_STATE_SHA_"+str(tick))
   v=worker.state_io.decode_state(raw)
   req(v.metadata.get("endpoint_tick")==tick,"ACCEPTED_STATE_METADATA_"+str(tick))
   source_states[tick]=(m._I(v.population_lower,v.population_upper),
                        m._I(v.log_temperature_lower,v.log_temperature_upper))
 req(np.array_equal(source_states[160][0].lo,accept160.population_lower),
     "REC195_FINAL_SOURCE_REI_ORIGINAL_ARRAY_NOT_IDENTICAL")
 out.mkdir(parents=True,exist_ok=True)
 gamma=float(m.sdirk.GAMMA)
 reports=[];rows=[]
 total_upper=0.;total_lower=0.;total_full_hi=0.
 for a,b in INTERVALS:
  X,LT=source_states[a]
  t0=time_total*a/131072.;t1=time_total*b/131072.;tm=t0+(t1-t0)*0.5
  sourcekw={"model":model,"base":base,"parent_pop":X,
            "parent_logt":LT,"total_h":nh,"total_he":nhe}
  full=m.run_step(**sourcekw,t0=t0,t1=t1)
  first=m.run_step(**sourcekw,t0=t0,t1=tm)
  req(first.certified,"ORIGINAL_FIRST_HALF_NOT_CERTIFIED")
  second=m.run_step(model,base,parent_pop=first.population,
      parent_logt=first.log_temperature,t0=tm,t1=t1,total_h=nh,total_he=nhe)
  req(all(st.certified for st in (full,first,second)),"ORIGINAL_THREE_MAPS_NOT_CERTIFIED")
  Y,Z=source_states[b]
  req(all((np.array_equal(second.population.lo,Y.lo),
           np.array_equal(second.population.hi,Y.hi),
           np.array_equal(second.log_temperature.lo,Z.lo),
           np.array_equal(second.log_temperature.hi,Z.hi))),
      "ORIGINAL_ACCEPTED_ENDPOINT_BYTE_ARRAY_MISMATCH_"+str(b))
  source_ledgers=accepted_ledger(m,model,second,second.population,tm,t1,nh,nhe)
  err,width=original_physical_error(m,full,second,nh,nhe)
  ef=integral(m,full,t1-t0)
  e1=integral(m,first,tm-t0)
  e2=integral(m,second,t1-tm)
  en=e1+e2
  req(np.isfinite(en.lo).all() and np.isfinite(en.hi).all() and
      np.isfinite(ef.lo).all() and np.isfinite(ef.hi).all(),"NONFINITE_LYA_ENERGY")
  req(np.all(en.lo<=en.hi) and np.all(ef.lo<=ef.hi),"INVALID_LYA_INTERVAL")
  req(np.all(en.hi>=0),"NEGATIVE_ESCAPING_LYA_UPPER")
  # Negative lower intervals at the subnormal scale arise from original outward rounding.
  observed_lower_min=float(np.min(en.lo))
  lower=np.maximum(en.lo,0.)
  upper=np.maximum(en.hi,0.)
  full_upper=np.maximum(ef.hi,0.)
  diag=mids(ef)-mids(en)
  nlo=lower/E_erg;nhi=upper/E_erg
  for j in range(N):
   rows.append((a,b,j,format(nlo[j],".17g"),format(nhi[j],".17g"),
        format(lower[j],".17g"),format(upper[j],".17g"),
        format(full_upper[j],".17g"),format(diag[j],".17g")))
  report={
      "ticks":[a,b],"proper_t0_s":t0,"proper_t1_s":t1,
      "source_duration_s":t1-t0,"source_gamma":gamma,
      "accepted_endpoint_private_sha256":STATE[b][1],
      "source_three_maps_certified":True,
      "14_original_ledgers_include_zero":True,"original_zero_table_events":True,
      "source_local_defect_by_field":err,"source_width_by_field":width,
      "integrated_escaped_line_energy_twohalf_erg":
          [global_sum(lower),global_sum(upper)],
      "integrated_escaped_line_photons_twohalf":[global_sum(nlo),global_sum(nhi)],
      "integrated_escaped_line_energy_full_erg":
          [global_sum(np.maximum(ef.lo,0.)),global_sum(full_upper)],
      "full_vs_twohalf_midpoint_energy_erg":global_sum(diag),
      "original_interval_min_lower_erg_cell":observed_lower_min,
      "escaped_source_lower_can_be_zero_due_f_one":True,
      "native_14_ledger_count":len(source_ledgers)}
  reports.append(report)
  total_lower+=report["integrated_escaped_line_energy_twohalf_erg"][0]
  total_upper+=report["integrated_escaped_line_energy_twohalf_erg"][1]
  total_full_hi+=report["integrated_escaped_line_energy_full_erg"][1]
  print(json.dumps({"phase":[a,b],"upper_energy_erg":report["integrated_escaped_line_energy_twohalf_erg"][1],
      "upper_photons":report["integrated_escaped_line_photons_twohalf"][1],
      "state_sha":STATE[b][1],"source_maps":"3_OF_3_CERTIFIED",
      "original_14_ledgers":"PASS",
      "DAG":"28/88_REPORTED"},sort_keys=True),flush=True)
 csv_path=out/"ORIGINAL_REI_F05_ACCEPTED_0_64_128_160_LYA_ESCAPE_138240.csv.gz"
 csvsha=write_gz(csv_path,rows)
 science={"schema":"BASS_HE_REI_F05_ORIGINAL_ACCEPTED_LYA_SDIRK_3_INTERVALS_V1",
   "original_REI_source_head":SOURCE_REI_HEAD,
   "original_source_tar_sha256":SOURCE_TAR_SHA,
   "original_accepted160_array_sha256":SOURCE_ARRAY_SHA,
   "original_26event_kernel_sha256":SOURCE_KERNEL_SHA,
   "input_REC195_source_zip_sha256":REC195_ZIP_SHA,
   "state_SHA256_by_tick":{str(x):STATE[x][1] for x in STATE},
   "original_accepted_source_ticks":[0,64,128,160],
   "one_original_material_history_not_four_simulations":True,
   "line_energy_eV":E_eV,"line_energy_erg":E_erg,
   "source_branch_f_range":[0.1,1.0],
   "source_gamma":gamma,
   "original_source_accepted_intervals":reports,
   "integrated_three_interval_escaped_energy_erg":[total_lower,total_upper],
   "integrated_three_interval_escaped_photons":[total_lower/E_erg,total_upper/E_erg],
   "original_fullstep_upper_energy_sum_erg":total_full_hi,
   "source_genuine_physics_rows":len(rows),"original_nodes":N,
   "derived_CSV":csv_path.name,"derived_CSV_SHA256":csvsha,
   "original_spectrum_and_causal_transport":"NOT_ADMITTED",
   "original_tick161":"NOT_ACCEPTED",
   "native_subagent":"NOT_RUN","independent_different_author":"NOT_RUN",
   "REI_canonical_DAG":"28/88_REPORTED","REI_working_DAG":"33/88_REPORTED",
   "REI_physical_fast":"4/7_REPORTED","BASS_HE_physical":"14/18_REPORTED",
   "canonical_delta":0,"production":"HOLD"}
 p=out/"SCIENCE_RESULT.json"
 p.write_text(json.dumps(science,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"status":"SOURCE_NATIVE_ACCEPTED_LYA_TIME_QUADRATURE_COMPLETED",
      "interval_count":len(reports),"source_rows":len(rows),
      "esc_total_erg_interval":[total_lower,total_upper],
      "esc_total_photon_interval":[total_lower/E_erg,total_upper/E_erg],
      "csv_sha256":csvsha,"json_sha256":sha(p),
      "canonical_delta":0},sort_keys=True),flush=True)
 return science
if __name__=="__main__":
 arg=argparse.ArgumentParser()
 arg.add_argument("--rei-repo",required=True,type=Path)
 arg.add_argument("--rec195-zip",required=True,type=Path)
 arg.add_argument("--out",required=True,type=Path)
 a=arg.parse_args()
 run(a.rei_repo,a.rec195_zip,a.out)
