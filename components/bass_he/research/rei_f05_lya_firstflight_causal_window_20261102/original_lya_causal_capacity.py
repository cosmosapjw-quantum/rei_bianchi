#!/usr/bin/env python3
"""SOURCE-LOCKED original F05 HeII Ly-alpha photon *causal-window capacity*
under a frozen homogeneous endpoint-absorber reference, NOT causal REI transfer.

No geometry reconstructed from quadrature W_node; never edits original REI.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,math,subprocess,sys,zipfile
from pathlib import Path
import numpy as np

REI_HEAD="70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00"
HE151_HEAD="eed3b50d2985ec4fb562032f9473cf31495d945d"
REC195_ZIP_SHA="ed08c131cb61b8cb5c5a52a8dadeb4fc7350945eefc5c2e1c1bf12c1a2052657"
SOURCE_TAR_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
SOURCE_KERNEL_SHA="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
SOURCE_160_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
HE151_CSV_SHA="13e05ff26adfb8eec5c2e0d0d028a1106f190771c642c2bb4306db79d9a80daf"
HE151_JSON_SHA="545f363740a8533f643d1f26b9dd6fd0c30d42078800fc6dce0d3c604156a993"
SOURCE_STATES={
 64:("private/first64_original_source.state","aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425"),
 128:("private/replayed128_pinned.state","bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6"),
 160:("private/replayed160_pinned.state","74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6")}
INTERVALS=((0,64),(64,128),(128,160))
N=46080;C=2.99792458e10;EV=1.602176634e-12
CHI_H=13.598434599702;CHI_HE=24.587389011;CHI_HE2=54.417760
E_LYA=40.81332
LANE="LOCAL_NEUTRAL_HAZARD_PRIMARY"

def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for z in iter(lambda:f.read(1048576),b""):h.update(z)
 return h.hexdigest()
def hashbytes(z):return hashlib.sha256(z).hexdigest()
def ensure(p,label):
 if not p:raise ValueError("HE152_SOURCE_ORIGINAL_"+label)
def L(n,p):
 s=importlib.util.spec_from_file_location(n,str(p))
 ensure(s is not None and s.loader is not None,"MODULE_NOT_FOUND")
 mod=importlib.util.module_from_spec(s);sys.modules[n]=mod;s.loader.exec_module(mod);return mod
def nsum(a):
 return float(np.sum(np.asarray(a),dtype=np.longdouble))
def escaped_prob(tau):
 """Stable 1-exp(-tau), tau>=0; no assumptions on actual IGM rays."""
 tau=np.asarray(tau,dtype=np.float64)
 ensure(np.isfinite(tau).all() and (tau>=0).all(),"TAU_INVALID")
 out=-np.expm1(-tau)
 ensure(np.all((out>=0)&(out<=1)),"PHOTON_PROB_NOT_PHYSICAL")
 return out
def uniform_prob(tau):
 """ONE illustrative uniform emission-time model; not source-owned."""
 a=np.asarray(tau,dtype=np.float64)
 p=np.empty_like(a)
 mask=a>=1.e-4
 p[mask]=1.+np.expm1(-a[mask])/a[mask]
 x=a[~mask]
 p[~mask]=x/2.-x*x/6.+x*x*x/24.-x**4/120.+x**5/720.
 ensure(np.all((p>=0)&(p<=1)),"UNIFORM_REFERENCE_NONPHYSICAL")
 return p
def wquantiles(v,w):
 order=np.argsort(v)
 v=v[order];w=w[order]
 total=nsum(w)
 ensure(total>0,"NO_NATIVE_LINE_PHOTONS")
 cdf=np.cumsum(w,dtype=np.longdouble)/np.longdouble(total)
 return [float(v[orderidx]) for orderidx in [int(np.searchsorted(cdf,q,side="left")) for q in (.01,.1,.5,.9,.99)]]
def gzwrite(p,rows):
 with Path(p).open("wb") as f,gzip.GzipFile(filename="",fileobj=f,mode="wb",compresslevel=6,mtime=0) as g:
  with io.TextIOWrapper(g,encoding="utf-8",newline="") as stream:
   out=csv.writer(stream,lineterminator="\n")
   out.writerow(("left_tick","right_tick","node","source_escape_upper_photons",
     "kappa_HI_end_cm_inv","kappa_HeI_end_cm_inv","kappa_HI_end_upper_cm_inv",
     "kappa_HeI_end_upper_cm_inv","tau_light_horizon_end",
     "same_window_absorbed_upper_reference_photons","same_window_absorbed_HI_upper_reference",
     "same_window_absorbed_HeI_upper_reference","photo_binding_upper_reference_erg",
     "primary_heat_upper_reference_erg","box_upper_total_absorbed_photons",
     "uniform_emission_upper_reference_photons"))
   out.writerows(rows)
 return sha(p)
def do(rei,rec,source,out):
 rei=Path(rei).resolve();rec=Path(rec).resolve();source=Path(source).resolve();out=Path(out).resolve()
 ensure(subprocess.check_output(["git","-C",str(rei),"rev-parse","HEAD"],text=True).strip()==REI_HEAD,"REI_SOURCE_HEAD_DRIFT")
 ensure(sha(rec)==REC195_ZIP_SHA,"REC195_SOURCE_ZIP_DRIFT")
 ensure(sha(source/"results/ORIGINAL_REI_F05_ACCEPTED_0_64_128_160_LYA_ESCAPE_138240.csv.gz")==HE151_CSV_SHA,
        "PR151_LINE_SOURCE_CSV_DRIFT")
 ensure(sha(source/"results/SCIENCE_RESULT.json")==HE151_JSON_SHA,"PR151_LINE_SOURCE_JSON_DRIFT")
 src=json.loads((source/"results/SCIENCE_RESULT.json").read_text())
 edge=L("he152_source_edge",rei/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
 worker=L("he152_source_worker",rei/edge.REL_STAGE/"analysis/attempt_worker.py")
 worker.jax_guard.install_if_missing()
 ensure(sha(worker.KERNEL_PATH)==SOURCE_KERNEL_SHA,"ORIGINAL_KERNEL_DRIFT")
 kernel=worker._kernel();rim=kernel.rim
 ensure(abs(float(rim.SIGMA_OTS_H41)-2.884642817876362e-19)<1e-31,
        "ORIGINAL_HI_LINE_CROSS_SECTION_DRIFT")
 ensure(abs(float(rim.SIGMA_OTS_HEI41)-3.0402144676144673e-18)<1e-30,
        "ORIGINAL_HEI_LINE_CROSS_SECTION_DRIFT")
 ensure(abs(E_LYA-float(rim.HEII_LYA_EV))<1e-12,"ORIGINAL_LINE_ENERGY_DRIFT")
 ensure(CHI_H<E_LYA and CHI_HE<E_LYA<CHI_HE2,"LINE_IONIZATION_THRESHOLD_ORDER")
 original,lock=edge.source_state(rei/edge.REL_STAGE,LANE,worker.state_io)
 ensure(lock["archive_sha256"]==SOURCE_TAR_SHA and lock["accepted_array_sha256"]==SOURCE_160_SHA,
        "ACCEPTED_SOURCE_ARRAY_DRIFT")
 model=rim.ReducedIntervalModel.from_repo(rei)
 base,y,lt,n_H,n_He=worker._context(kernel,LANE)
 ensure(len(n_H)==N and np.all(n_H>0) and np.all(n_He>0),"ORIGINAL_SPECIES_INVENTORY")
 duration=float(base.forcing.duration_seconds(0)); tick=duration/131072.
 states={0:{"point":y,"lo":y,"hi":y}}
 with zipfile.ZipFile(rec) as z:
  ensure(z.testzip() is None,"REC195_ZIP_CRC_FAILED")
  for t,(name,expected) in SOURCE_STATES.items():
   blob=z.read(name);ensure(hashbytes(blob)==expected,"ACCEPTED_STATE_TICK_"+str(t))
   s=worker.state_io.decode_state(blob)
   ensure(s.metadata.get("endpoint_tick")==t,"ACCEPTED_METADATA_TICK_"+str(t))
   p=edge.element_conserving_parent_candidate(s.population_lower,
           s.population_upper,n_H,n_He)
   states[t]={"point":p,"lo":s.population_lower,"hi":s.population_upper}
 ensure(np.array_equal(states[160]["lo"],original.population_lower),"ACCEPTED160_ARRAY_NOT_IDENTICAL")
 stepdata=[];rows=[];sigH=float(rim.SIGMA_OTS_H41);sigHe=float(rim.SIGMA_OTS_HEI41)
 sourcecsv=source/"results/ORIGINAL_REI_F05_ACCEPTED_0_64_128_160_LYA_ESCAPE_138240.csv.gz"
 src_id=src["original_source_accepted_intervals"]
 with gzip.open(sourcecsv,"rt",newline="") as inp:
  rdr=csv.DictReader(inp)
  for aa,bb in INTERVALS:
   h=tick*(bb-aa)
   photon=np.empty(N);_left=np.empty(N)
   for j in range(N):
    row=next(rdr)
    ensure((int(row["tick_left"]),int(row["tick_right"]),int(row["cell"]))==(aa,bb,j),
       "PR151_SOURCE_ROW_ORDER")
    photon[j]=float(row["escaped_photon_hi"])
    _left[j]=float(row["escaped_photon_lo"])
   ensure(np.all(photon>=0) and np.all(_left==0),"PR151_POSITIVE_SOURCE_ESCAPE_LOWER_NOT_ZERO")
   original_ref=next(x for x in src_id if x["ticks"]==[aa,bb])
   ensure(abs(nsum(photon)-original_ref["integrated_escaped_line_photons_twohalf"][1])
          <=1e-12*original_ref["integrated_escaped_line_photons_twohalf"][1],"PR151_INTEGRATED_SOURCE_MISMATCH")
   records={}
   for t in (aa,bb):
    zval=float(model.forcing_bounds(t*tick,t*tick).z.lo)
    vproper=model.inputs.comoving_volume_cm3/(1.+zval)**3
    ensure(np.all(vproper>0) and np.all(np.isfinite(vproper)),"NATIVE_SOURCE_PROPER_VOLUME")
    p=states[t]["point"]
    ensure(np.all(p>0) and np.all(np.abs(p[:,0]+p[:,1]-n_H)
          <=7e-14*np.maximum(n_H,1e-300)),"NATIVE_H_CONSERVATION")
    ensure(np.all(np.abs(p[:,2]+p[:,3]+p[:,4]-n_He)
          <=7e-14*np.maximum(n_He,1e-300)),"NATIVE_HE_CONSERVATION")
    kH=sigH*p[:,0]/vproper;kHe=sigHe*p[:,2]/vproper
    kHhi=sigH*states[t]["hi"][:,0]/vproper
    kHehi=sigHe*states[t]["hi"][:,2]/vproper
    ensure(np.all(np.isfinite(kH+kHe+kHhi+kHehi)) and np.all(kH>=0) and np.all(kHe>=0),"SOURCE_ABSORBER_KAPPA")
    records[t]={"kH":kH,"kHe":kHe,"kHhi":kHhi,"kHehi":kHehi,"z":zval}
   # Reference frozen to ORIGINAL accepted material state at RIGHT endpoint.
   kH=records[bb]["kH"];kHe=records[bb]["kHe"]
   kapp=kH+kHe;kapphi=records[bb]["kHhi"]+records[bb]["kHehi"]
   tau=C*h*kapp;tauhi=C*h*kapphi
   p_end=escaped_prob(tau);p_start=escaped_prob(C*h*(records[aa]["kH"]+records[aa]["kHe"]))
   p_end_upper=escaped_prob(tauhi)
   pu=uniform_prob(tau)
   fracH=np.divide(kH,kapp,out=np.zeros_like(kapp),where=kapp>0)
   fracHe=np.divide(kHe,kapp,out=np.zeros_like(kapp),where=kapp>0)
   absorbed=photon*p_end;HI=absorbed*fracH;HeI=absorbed*fracHe
   cap_abs_hi=photon*p_end_upper
   U=uniform_prob(tau)*photon
   Ebinding=EV*(CHI_H*HI+CHI_HE*HeI)
   Eheat=EV*((E_LYA-CHI_H)*HI+(E_LYA-CHI_HE)*HeI)
   energy_res=np.abs((Ebinding+Eheat)-E_LYA*EV*absorbed)
   rescale=np.maximum(np.maximum(E_LYA*EV*absorbed,Ebinding+Eheat),1e-290)
   maxres=float(np.max(energy_res/rescale))
   ensure(maxres<6e-15,"ORIGINAL_LYA_PHOTO_BINDING_ENERGY_IDENTITY")
   ensure(np.all(cap_abs_hi+1e-10>=absorbed) and np.all(U<=absorbed+1e-8),
          "SOURCE_BOX_OR_EMISSION_TIME_ORDERING")
   lam=1./np.maximum(kapp,1e-300)
   # Do not infer a spatial mesh or ray path from W_node, macro_index.
   for j in range(N):
    rows.append((aa,bb,j,*[format(float(v),".17g") for v in (
       photon[j],kH[j],kHe[j],records[bb]["kHhi"][j],records[bb]["kHehi"][j],
       tau[j],absorbed[j],HI[j],HeI[j],Ebinding[j],Eheat[j],
       cap_abs_hi[j],U[j])]))
   meanp=nsum(absorbed)/nsum(photon)
   site={
      "accepted_ticks":[aa,bb],"source_duration_s":h,
      "original_source_right_endpoint_z":records[bb]["z"],
      "input_source_escape_upper_photons":nsum(photon),
      "photon_source_lower":0,
      "source_horizon_proper_length_cm":C*h,
      "source_horizon_proper_length_kpc":C*h/(3.085677581491367e21),
      "right_endpoint_homogeneous_frozen_capacity_absorption_probability_emission_weighted":meanp,
      "left_endpoint_homogeneous_frozen_capacity_absorption_probability_emission_weighted":
         nsum(photon*p_start)/nsum(photon),
      "source_end_accepted_box_upper_frozen_capacity_prob_emission_weighted":
         nsum(cap_abs_hi)/nsum(photon),
      "uniform_emission_time_reference_absorption_probability_emission_weighted":
         nsum(U)/nsum(photon),
      "source_escape_upper_remaining_photons_if_all_emitted_at_start_in_frozen_gas":nsum(photon-absorbed),
      "right_endpoint_frozen_conditional_absorbed_photons":nsum(absorbed),
      "right_endpoint_frozen_conditional_absorbed_HI_photons":nsum(HI),
      "right_endpoint_frozen_conditional_absorbed_HeI_photons":nsum(HeI),
      "right_endpoint_frozen_conditional_binding_gain_erg":nsum(Ebinding),
      "right_endpoint_frozen_conditional_primary_electron_heat_erg":nsum(Eheat),
      "right_endpoint_frozen_conditional_line_absorbed_energy_erg":nsum(absorbed)*EV*E_LYA,
      "source_box_hi_cap_absorbed_photons":nsum(cap_abs_hi),
      "uniform_emission_time_reference_absorbed_photons":nsum(U),
      "emission_upper_weighted_lambda_quantiles_cm_01_10_50_90_99":wquantiles(lam,photon),
      "max_cell_energy_ledger_relative_residual":maxres,
      "source_node_count":N
   }
   stepdata.append(site)
   print(json.dumps({"interval":[aa,bb],
      "escaped_original_upper":site["input_source_escape_upper_photons"],
      "frozen_endpoint_capacity_frac":meanp,
      "frozen_endpoint_absorbed_HI":site["right_endpoint_frozen_conditional_absorbed_HI_photons"],
      "frozen_endpoint_absorbed_HeI":site["right_endpoint_frozen_conditional_absorbed_HeI_photons"],
      "max_cell_energy_res":maxres,"dag":"28/88_REPORTED"},sort_keys=True),flush=True)
  ensure(next(rdr,None) is None,"SOURCE_CSV_EXTRA_ROWS")
 ensure(len(rows)==3*N,"SOURCE_CSV_ROW_COUNT")
 out.mkdir(parents=True,exist_ok=True)
 csvpath=out/"REI_F05_LYA_FROZEN_CAUSAL_WINDOW_CAPACITY_138240.csv.gz"
 csvsha=gzwrite(csvpath,rows)
 totals={}
 keys=("input_source_escape_upper_photons",
  "right_endpoint_frozen_conditional_absorbed_photons",
  "right_endpoint_frozen_conditional_absorbed_HI_photons",
  "right_endpoint_frozen_conditional_absorbed_HeI_photons",
  "right_endpoint_frozen_conditional_binding_gain_erg",
  "right_endpoint_frozen_conditional_primary_electron_heat_erg",
  "right_endpoint_frozen_conditional_line_absorbed_energy_erg",
  "source_box_hi_cap_absorbed_photons",
  "uniform_emission_time_reference_absorbed_photons")
 for name in keys:totals[name]=float(math.fsum(float(a[name]) for a in stepdata))
 totals["right_endpoint_homogeneous_frozen_source_weighted_absorption_probability"]=(totals["right_endpoint_frozen_conditional_absorbed_photons"]/totals["input_source_escape_upper_photons"])
 totals["source_box_hi_absorption_capacity_fraction"]=(totals["source_box_hi_cap_absorbed_photons"]/totals["input_source_escape_upper_photons"])
 totals["uniform_emission_time_reference_absorption_probability"]=(totals["uniform_emission_time_reference_absorbed_photons"]/totals["input_source_escape_upper_photons"])
 data={
  "schema":"BASS_HE_REI_ORIGINAL_F05_LYA_LOCAL_FROZEN_FIRSTFLIGHT_CAPACITY_V1",
  "source_scope":"ONE_ACCEPTED_ORIGINAL_MATERIAL_HISTORY_TICK0_64_128_160",
  "source_ref_REI_head":REI_HEAD,"source_ref_HE151_head":HE151_HEAD,
  "source_original_TAR_SHA256":SOURCE_TAR_SHA,
  "source_original_26event_kernel_SHA256":SOURCE_KERNEL_SHA,
  "source_accepted_160_array_SHA256":SOURCE_160_SHA,
  "source_REC195_archive_SHA256":REC195_ZIP_SHA,
  "source_HE151_lya_CSV_SHA256":HE151_CSV_SHA,
  "source_HE151_lya_JSON_SHA256":HE151_JSON_SHA,
  "source_original_accepted_ticks":[0,64,128,160],
  "source_original_material_nodes":N,
  "source_original_data_rows":len(rows),
  "source_40p81332_eV_line_energy_erg":E_LYA*EV,
  "source_original_opacity_constants_cm2":{"HI_41":sigH,"HeI_41":sigHe},
  "original_source_quadrature_nodes_not_spatial_ray_cells":True,
  "original_causal_geometry_not_identified":True,
  "source_f_interval":[0.1,1.0],
  "conditional_reference":"SOURCE_RIGHT_ACCEPTED_STATE_STATIC_HOMOGENEOUS_ABSORBER_ALL_PHOTONS_AT_INTERVAL_START",
  "source_endpoint_midpoint_nuclei_conservation_checked":True,
  "original_line_transported":"NO_SOURCE_RAY_PATHS",
  "physical_inference":"LOCAL_FROZEN_ABSORPTION_HORIZON_CAPACITY_NOT_ACTUAL_CAUSAL_RT",
  "original_HII_HeII_HeIII_worker_modified":False,
  "original_tick161":"NOT_ACCEPTED",
  "intervals":stepdata,"totals":totals,
  "derived_CSV":csvpath.name,"derived_CSV_SHA256":csvsha,
  "native_subagent":"NOT_RUN","external_blind_referee":"NOT_RUN",
  "REI_canonical_DAG":"28/88_REPORTED","REI_working_DAG":"33/88_REPORTED",
  "physical_fast_DAG":"4/7_REPORTED","BASS_HE_physical_DAG":"14/18_REPORTED",
  "canonical_delta":0,"production":"HOLD"}
 science=out/"SCIENCE_RESULT.json"
 science.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":"ORIGINAL_HEII_LYA_CAUSAL_WINDOW_FROZEN_CAPACITY_COMPUTED",
  "total_source_photon_upper":totals["input_source_escape_upper_photons"],
  "conditional_frozen_absorbed":totals["right_endpoint_frozen_conditional_absorbed_photons"],
  "conditional_binding_erg":totals["right_endpoint_frozen_conditional_binding_gain_erg"],
  "conditional_heat_erg":totals["right_endpoint_frozen_conditional_primary_electron_heat_erg"],
  "source_CSV_SHA256":csvsha,"science_JSON_SHA256":sha(science),"canonical_delta":0},sort_keys=True),flush=True)

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--rei",required=True,type=Path)
 p.add_argument("--rec195",required=True,type=Path)
 p.add_argument("--he151",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args();do(a.rei,a.rec195,a.he151,a.out)
