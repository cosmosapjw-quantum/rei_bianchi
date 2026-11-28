#!/usr/bin/env python3
"""Actual ORIGINAL REI 26-event V2 [160,161],[161,162] HeII Ly-alpha
source escaping time quadrature. Research-only versioned native source: no
original REI state, history, main, worker, IVP or runtime modification.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,math,subprocess,sys
from pathlib import Path
import numpy as np

N=46080
TICKS=131072
SOURCE_TAR="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
KERNEL="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
SOURCE_REI_PR369_HEAD="645437697d915da45147071e266bc47937e76f6c"
PR151_SCIENCE="545f363740a8533f643d1f26b9dd6fd0c30d42078800fc6dce0d3c604156a993"
REC195_ARCHIVE="ed08c131cb61b8cb5c5a52a8dadeb4fc7350945eefc5c2e1c1bf12c1a2052657"
ACCEPTED_T160_ARRAY_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
V2_T161_SHA="c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823"
V2_T162_SHA="35b1969ccd2bf16be94e1b9bcc7df9189c647b60c0aa2b00cb479a0d504a0e7b"
HEII_LYA_E=40.813320
EV=1.602176634e-12
KB=1.380649e-16
CHI=np.array([13.598434599702,24.587389011,54.417760],dtype=np.float64)
TOLERANCE=2e-4
WIDTH=2e-3
LANE="LOCAL_NEUTRAL_HAZARD_PRIMARY"
SOURCE_INTERVALS=((160,161),(161,162))
ORIGINAL_CANDIDATE={
 "recomb":"recomb_source_t161_pinned/SHADOW_V2_NONAUTHORITATIVE_TICK161.npz",
 "shield":"shield_source_t161_pinned/SHADOW_V2_NONAUTHORITATIVE_TICK161.npz"}
RESEARCH_162={
 "primary":"primary_tick161_parent_to_tick162/REI_TICK162_V2_RESEARCH_NONPRODUCTION.npz",
 "recomb":"recomb_tick161_parent_to_tick162/REI_TICK162_V2_RESEARCH_NONPRODUCTION.npz",
 "shield":"shield_tick161_parent_to_tick162/REI_TICK162_V2_RESEARCH_NONPRODUCTION.npz"}
FIELD_NAMES=("population_lower","population_upper","log_temperature_lower","log_temperature_upper")
COLUMNS=("left_tick","right_tick","node","escaped_llya_energy_lo_erg",
 "escaped_llya_energy_hi_erg","escaped_llya_photons_lo",
 "escaped_llya_photons_hi","stage1_escaped_rate_lo_erg_s",
 "stage1_escaped_rate_hi_erg_s","final1_escaped_rate_lo_erg_s",
 "final1_escaped_rate_hi_erg_s","stage2_escaped_rate_lo_erg_s",
 "stage2_escaped_rate_hi_erg_s","final2_escaped_rate_lo_erg_s",
 "final2_escaped_rate_hi_erg_s","full_escaped_energy_upper_erg",
 "source_delta_B_cell_mid_erg","source_delta_U_cell_mid_erg")
def require(c,msg):
 if not c:raise ValueError("BASS_HE_REI_F05_V2_NATIVE_LYA_"+msg)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for z in iter(lambda:f.read(1<<20),b""):h.update(z)
 return h.hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,str(p))
 require(s is not None and s.loader is not None,"SOURCE_MODULE_UNAVAILABLE_"+name)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def total(v):
 return float(np.sum(np.asarray(v),dtype=np.longdouble))
def mid(v):
 return np.asarray(v.lo)*0.5+np.asarray(v.hi)*0.5
def twohalf(m,step,h):
 gamma=float(m.sdirk.GAMMA)
 require(0<gamma<1 and h>0,"SDIRK_GAMMA_OR_DT")
 return h*((1-gamma)*step.stage_event.escaped_energy+gamma*step.final_event.escaped_energy)
def report_ledger(owner,m,model,steps,t0,tm,t1,nh,nhe):
 raw=owner.source_ledgers(m,model,steps["half2"],t0,tm,t1,nh,nhe)
 require(len(raw)==14 and set(raw)=={"H_nuclei","He_nuclei",
       "stage_photon_identity","stage_total_energy","final_photon_identity",
       "final_total_energy",*[f"stage_group_{i}_photon" for i in range(4)],
       *[f"final_group_{i}_photon" for i in range(4)]},"NATIVE_14_LEDGER_KEYS")
 require(all(np.isfinite(lo) and np.isfinite(hi) and lo<=0<=hi for lo,hi in raw.values()),
         "NATIVE_14_LEDGER_ZERO_INCLUSION")
 test=m.primitive.audit_set_ledgers({k:tuple(v) for k,v in raw.items()})
 require(bool(test.all_include_zero),"NATIVE_14_LEDGER_AUDIT")
 return raw
def energy_boxes(pop,logt,nh,nhe):
 p=pop
 ne_lo=p.lo[:,1]+p.lo[:,3]+2*p.lo[:,4]
 ne_hi=p.hi[:,1]+p.hi[:,3]+2*p.hi[:,4]
 Blo=EV*(CHI[0]*p.lo[:,1]+CHI[1]*(p.lo[:,3]+p.lo[:,4])+CHI[2]*p.lo[:,4])
 Bhi=EV*(CHI[0]*p.hi[:,1]+CHI[1]*(p.hi[:,3]+p.hi[:,4])+CHI[2]*p.hi[:,4])
 Ulo=1.5*KB*(nh+nhe+ne_lo)*np.exp(logt.lo)
 Uhi=1.5*KB*(nh+nhe+ne_hi)*np.exp(logt.hi)
 return {"B":(Blo,Bhi),"U":(Ulo,Uhi)}
def write_gzip(path,rows):
 with Path(path).open("wb") as raw,gzip.GzipFile(filename="",fileobj=raw,mode="wb",mtime=0,compresslevel=6) as gz:
  with io.TextIOWrapper(gz,encoding="utf-8",newline="") as f:
   w=csv.writer(f,lineterminator="\n")
   w.writerow(COLUMNS);w.writerows(rows)
 return sha(path)
def load_box_arrays(m,z,prefix=""):
 if prefix:
  return m._I(z[prefix+"population_lower"],z[prefix+"population_upper"]), m._I(z[prefix+"logT_lower"],z[prefix+"logT_upper"])
 return m._I(z["population_lower"],z["population_upper"]),m._I(z["log_temperature_lower"],z["log_temperature_upper"])
def execute(repo,private,primary161,he151source,out):
 repo=Path(repo).resolve();private=Path(private).resolve()
 primary161=Path(primary161).resolve();he151source=Path(he151source).resolve()
 out=Path(out).resolve()
 require(subprocess.check_output(["git","-C",str(repo),"rev-parse","HEAD"],text=True).strip()==SOURCE_REI_PR369_HEAD,
   "REI369_SOURCE_HEAD_CHANGED")
 require(sha(he151source/"results/SCIENCE_RESULT.json")==PR151_SCIENCE,"ORIGINAL_ACCEPTED_LYA_SOURCE_CHANGED")
 t161={k:private/x for k,x in ORIGINAL_CANDIDATE.items()}
 t161["primary"]=primary161
 t162={k:private/x for k,x in RESEARCH_162.items()}
 for k,p in t161.items():require(sha(p)==V2_T161_SHA,"V2_T161_"+k+"_SHA_CHANGED")
 for k,p in t162.items():require(sha(p)==V2_T162_SHA,"V2_T162_"+k+"_SHA_CHANGED")
 mm=load("hei153_original_mm",repo/"research/rei_f05_mmatrix_residual_20261101/residual_certificate.py")
 inc=mm.load_original()
 owner=load("hei153_original_v2_owner",repo/"research/rei_f05_owner_v2_shadow_20261101/owner_v2_shadow.py")
 edge=load("hei153_original_edge",repo/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
 stage=repo/edge.REL_STAGE
 worker=load("hei153_original_worker",stage/"analysis/attempt_worker.py")
 worker.jax_guard.install_if_missing()
 require(sha(worker.KERNEL_PATH)==KERNEL,"NATIVE_ORIGINAL_KERNEL_CHANGED")
 require(sha(stage/"local_results"/edge.ARCHIVE_NAME)==SOURCE_TAR,"SOURCE_TAR_CHANGED")
 m=worker._kernel(); model=m.rim.ReducedIntervalModel.from_repo(repo)
 require(abs(float(m.rim.HEII_LYA_EV)-HEII_LYA_E)<1e-12,"NATIVE_HEII_LYA_ENERGY_CHANGED")
 base,_,_,nh,nhe=worker._context(m,LANE)
 decoded,receipt=edge.source_state(stage,LANE,worker.state_io)
 require(receipt["accepted_array_sha256"]==ACCEPTED_T160_ARRAY_SHA,"ORIGINAL_ACCEPTED_SOURCE_ARRAY")
 require(len(nh)==N and len(nhe)==N,"SOURCE_NODE_COUNT")
 with np.load(t161["primary"],allow_pickle=False) as a:
  p160,lt160=load_box_arrays(m,a,prefix="source_parent_")
  p161,lt161=load_box_arrays(m,a)
 # First parent from 161 research source must equal original accepted tick160 input exactly
 for actual,expected in ((p160.lo,decoded.population_lower),(p160.hi,decoded.population_upper),
  (lt160.lo,decoded.log_temperature_lower),(lt160.hi,decoded.log_temperature_upper)):
  require(np.array_equal(actual,expected),"REI369_SOURCE_PARENT_NOT_REAL_ACCEPTED160")
 target_boxes={161:(p161,lt161)}
 with np.load(t162["primary"],allow_pickle=False) as z:target_boxes[162]=load_box_arrays(m,z)
 for path in list(t161.values())+list(t162.values()):
  require(path.exists(),"SOURCE_V2_PRIVATE_MISSING")
 duration=float(base.forcing.duration_seconds(0));dt=duration/TICKS
 old=inc.krawczyk_increment
 def v2_increment(mod,parent,flux,den,time,th,the):
  return mm.structural_residual_increment(mod,parent,flux,den,time,th,the,inc)
 rows=[];summaries=[];rates=[]
 try:
  inc.krawczyk_increment=v2_increment
  for a,b in SOURCE_INTERVALS:
   p,lt=(p160,lt160) if a==160 else (p161,lt161)
   t0=dt*a;t1=dt*b;tm=t0+0.5*(t1-t0)
   steps={};deltas={}
   for name,pp,zz,lft,rgt in (("full",p,lt,t0,t1),("half1",p,lt,t0,tm),
                              ("half2",None,None,tm,t1)):
    if name=="half2":pp=steps["half1"].population;zz=steps["half1"].log_temperature
    step,delta,details=inc.original_map(m,model,base,name,pp,zz,lft,rgt,nh,nhe)
    require(bool(step.certified) and delta is not None,"NATIVE_V2_MAP_"+name+"_"+str(a))
    require(details["original_table_event_count"]==0,"NATIVE_SOURCE_TABLE_"+name+"_"+str(a))
    steps[name]=step;deltas[name]=delta
   target,tl=target_boxes[b];pout=steps["half2"].population;lout=steps["half2"].log_temperature
   exact=[np.array_equal(x,y) for x,y in (
     (pout.lo,target.lo),(pout.hi,target.hi),
     (lout.lo,tl.lo),(lout.hi,tl.hi))]
   require(all(exact),"ORIGINAL_RESEARCH_V2_"+str(b)+"_ENDPOINT_NOT_EXACT")
   raw=report_ledger(owner,m,model,steps,t0,tm,t1,nh,nhe)
   newdefect={}
   for name in ("x_HII","x_HeII","x_HeIII","log_T"):
    dd=deltas["full"][name]-(deltas["half1"][name]+deltas["half2"][name])
    newdefect[name]=float(np.max(inc.interval_upper(dd)))
   widths={
     "x_HII":float(np.max((pout.hi[:,1]-pout.lo[:,1])/nh)),
     "x_HeII":float(np.max((pout.hi[:,3]-pout.lo[:,3])/nhe)),
     "x_HeIII":float(np.max((pout.hi[:,4]-pout.lo[:,4])/nhe)),
     "log_T":float(np.max(lout.hi-lout.lo))}
   require(max(newdefect.values())<TOLERANCE and max(widths.values())<WIDTH,
           "V2_ORIGINAL_FROZEN_GATE")
   radiation_full=twohalf(m,steps["full"],t1-t0)
   radiation_h1=twohalf(m,steps["half1"],tm-t0)
   radiation_h2=twohalf(m,steps["half2"],t1-tm)
   radiation=radiation_h1+radiation_h2
   require(np.all(np.isfinite(radiation.lo)) and np.all(np.isfinite(radiation.hi))
         and np.all(radiation.lo<=radiation.hi) and np.all(radiation.hi>=0),
         "NATIVE_ESCAPED_LINE_NOT_PHYSICAL_INTERVAL")
   lower=np.maximum(radiation.lo,0.0);upper=np.maximum(radiation.hi,0.0)
   fullhi=np.maximum(radiation_full.hi,0.0)
   ergang=HEII_LYA_E*EV
   photlo=lower/ergang;phothi=upper/ergang
   Emat_init=energy_boxes(p,lt,nh,nhe)
   Emat_final=energy_boxes(pout,lout,nh,nhe)
   deltaBm=0.5*(Emat_final["B"][0]+Emat_final["B"][1]) - 0.5*(Emat_init["B"][0]+Emat_init["B"][1])
   deltaUm=0.5*(Emat_final["U"][0]+Emat_final["U"][1]) - 0.5*(Emat_init["U"][0]+Emat_init["U"][1])
   for i in range(N):
    vals=(lower[i],upper[i],photlo[i],phothi[i],
      steps["half1"].stage_event.escaped_energy.lo[i],
      steps["half1"].stage_event.escaped_energy.hi[i],
      steps["half1"].final_event.escaped_energy.lo[i],
      steps["half1"].final_event.escaped_energy.hi[i],
      steps["half2"].stage_event.escaped_energy.lo[i],
      steps["half2"].stage_event.escaped_energy.hi[i],
      steps["half2"].final_event.escaped_energy.lo[i],
      steps["half2"].final_event.escaped_energy.hi[i],
      fullhi[i],deltaBm[i],deltaUm[i])
    rows.append([a,b,i]+[format(float(x),".17g") for x in vals])
   g_em=[total(lower),total(upper)]
   g_ph=[total(photlo),total(phothi)]
   delB=[total(Emat_final["B"][0]-Emat_init["B"][1]),
         total(Emat_final["B"][1]-Emat_init["B"][0])]
   delU=[total(Emat_final["U"][0]-Emat_init["U"][1]),
         total(Emat_final["U"][1]-Emat_init["U"][0])]
   ratio=g_em[1]/(-delB[1]) if delB[1]<0 else None
   interval={
      "ticks":[a,b],"duration_s":t1-t0,
      "source_SDIRK_gamma":float(m.sdirk.GAMMA),
      "original_source_map_three_steps":True,
      "exact_research_V2_endpoint_array_identity":True,
      "original_native_14_ledger_zero_included":True,
      "original_source_14_ledgers":raw,
      "source_original_public_widths":widths,"source_V2_common_parent_defects":newdefect,
      "esc_local_Lya_energy_erg":[*g_em],"esc_local_Lya_photons":[*g_ph],
      "native_full_step_line_upper_energy_erg":total(fullhi),
      "native_twohalf_vs_full_upper_erg":g_em[1]-total(fullhi),
      "original_V2_research_delta_B_outer_interval_erg":delB,
      "original_V2_research_delta_U_outer_interval_erg":delU,
      "original_V2_source_Bmid_erg":total(deltaBm),
      "original_V2_source_Umid_erg":total(deltaUm),
      "radiation_upper_to_abs_B_outer_near_zero_scale":ratio,
      "native_source_line_lower_can_be_zero_due_f_one":True
   }
   summaries.append(interval)
   print(json.dumps({"phase":f"{a}->{b}",
     "upper_Lya_erg":g_em[1],"upper_Lya_photons":g_ph[1],
     "delta_B_erg":delB,"delta_U_erg":delU,
     "source_map":"3/3_PASS","native_14_ledgers":"14/14_PASS",
     "canonical":"28/88_REPORTED"},sort_keys=True),flush=True)
 finally:
  inc.krawczyk_increment=old
 out.mkdir(parents=True,exist_ok=True)
 csv_path=out/"ORIGINAL_REI_F05_V2_T160_T162_LYA_92160.csv.gz"
 csv_hash=write_gzip(csv_path,rows)
 radiation_upper=sum(q["esc_local_Lya_energy_erg"][1] for q in summaries)
 radiation_num=sum(q["esc_local_Lya_photons"][1] for q in summaries)
 data={
    "schema":"BASS_HE_ORIGINAL_F05_RESEARCH_V2_T160_162_LYA_TWOHALF_NATIVE_SOURCE_V1",
    "original_REI369_git_head":SOURCE_REI_PR369_HEAD,
    "original_F05_source_tar_sha256":SOURCE_TAR,
    "original_original_26event_kernel_sha256":KERNEL,
    "original_accepted160_array_sha256":ACCEPTED_T160_ARRAY_SHA,
    "original_V2_tick161_research_SHA256":V2_T161_SHA,
    "original_V2_tick162_research_SHA256":V2_T162_SHA,
    "three_source_lane_candidates_byte_identical":True,
    "source_accepted160_official":True,"source_ticks161_162_official":False,
    "source_original_predecessor_all_3_lane_physical_realizations":1,
    "source_original_method":"ORIGINAL_26EVENT_TWOHALF_MAP_IN_PROCESS_V2_STRUCTURAL_M_MATRIX_CORRELATED_INCREMENT",
    "native_original_source_4_groups_not_modified":True,
    "source_HeII_Lya_E_eV":HEII_LYA_E,
    "source_HeII_Lya_E_erg":ergang,
    "source_escape_branch_f_interval":[0.1,1.0],
    "two_research_source_intervals":summaries,
    "source_interval_photon_upper_total":radiation_num,
    "source_interval_local_Lya_energy_upper_erg":radiation_upper,
    "source_interval_local_Lya_lower_erg":0.0,
    "output_csv":csv_path.name,"output_csv_sha256":csv_hash,
    "source_raw_research_V2_NPZ_committed":False,
    "source_spatial_photon_transport_owned":False,
    "source_source_emission_not_observed":True,
    "fixed_original_local_gate":TOLERANCE,"fixed_original_width_gate":WIDTH,
    "no_legacy_V1_reinterpretation":True,
    "original_tick161_162_production":"NOT_ACCEPTED",
    "external_referee":"NOT_RUN","native_subagent":"NOT_RUN",
    "REI_canonical_DAG":"28/88_REPORTED","REI_working_DAG":"33/88_REPORTED",
    "physical_fast_DAG":"4/7_REPORTED","BASS_HE_physical_DAG":"14/18_REPORTED",
    "canonical_delta":0,"production":"HOLD",
    "science_rows":len(rows)}
 p=out/"SCIENCE_RESULT.json"
 p.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"status":"PASS_ORIGINAL_V2_T160_T162_NUCLEAR_HEII_LYA_SOURCE",
   "upper_erg":radiation_upper,"upper_photons":radiation_num,
   "source_rows":len(rows),"CSV_SHA256":csv_hash,"JSON_SHA256":sha(p)},sort_keys=True),flush=True)
 return data

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--rei",type=Path,required=True)
 p.add_argument("--private",type=Path,required=True)
 p.add_argument("--primary161",type=Path,required=True)
 p.add_argument("--he151",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 args=p.parse_args()
 execute(args.rei,args.private,args.primary161,args.he151,args.out)
