#!/usr/bin/env python3
"""WU R59: actual 46,080-cell F05 H/He source vs 640 native S0 Bianchi/FLRW states.

Core REI-EXP-SCENARIO science intake: quantify original source redshift/clock
consistency, real cell Thomson hazard on ACCEPTED 0->160 original H/He points,
and whether F08 S0 BI geometry is a source/clock/epoch matched EoR provider.

Never claim sky tau(z), a Bianchi-FLRW matched EoR pair, full native dense
trajectory, original tick161 acceptance, or a source-qualified HD consumer.
"""
from __future__ import annotations
import csv,gzip,hashlib,io,json,math,pathlib
import numpy as np
from scipy.interpolate import PchipInterpolator
ROOT=pathlib.Path(__file__).resolve().parent
R54=pathlib.Path("/home/cosmosapjw/research_backups/WU088_HH/R54_REI_F05_DI_GROUP_PHOTON_DEBIT_20261101/source_inputs")
REI27=pathlib.Path("/home/cosmosapjw/research_backups/WU088_HH/R57_REI_F05_NATIVE_RHS_DI_HISTORY_20261102/source_private/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz")
FORCING=R54/"canonical_time_resolved_forcing_nodes.csv"
INIT=R54/"initial_material_state_z6.npz"
BASS=pathlib.Path("/home/cosmosapjw/worktrees/bass-f08-source-support-20261115/research/bass_rei_f08_s0_continuous_native_20261102")
F08=BASS/"results/SOURCE_LOCKED_REI_S0_CONTINUOUS_NATIVE_HHE_TRAJECTORY.csv.gz"
F08_SCOPE=BASS/"THEORY_AND_SCOPE.md"
LOCKS={
"REI_F05_184320_27col":"d8d8ce4f3fea820a3b6cfe6bd5d1c4ac48e9f160612cde0ebe00ca04f32af37e",
"REI_F05_17_photon_knots":"9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268",
"REI_F05_initial_material":"7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d",
"BASS_F08_640_native_consecutive":"75a8e6b0f63db0f9972c15fc2e9580261574ac87f70167ab3343d667094e9843"
}
C_CM_S=2.99792458e10
MPC_CM=3.085677581491367e24
SIGMA_T_CM2=6.6524587321e-25
N=46080
EPOCHS=(0,64,128,160)
H0_KM_S_MPC=67.4
OMEGA_M=.315
OMEGA_L=1.-OMEGA_M
BASS_H_BI=(1.01e-14,.99e-14,1.00e-14)
BASS_H_FLRW=(1e-14,1e-14,1e-14)

def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def qstat(v):
 q=np.quantile(np.asarray(v,dtype=float),[0,.05,.5,.95,1])
 return {k:float(a) for k,a in zip(["min","p05","median","p95","max"],q)}
def require(ok,msg):
 if not ok:raise AssertionError(msg)

def read_original():
 for path,key in [(REI27,"REI_F05_184320_27col"),(FORCING,"REI_F05_17_photon_knots"),(INIT,"REI_F05_initial_material"),(F08,"BASS_F08_640_native_consecutive")]:
  require(sha(path)==LOCKS[key],"SOURCE_IMMUTABLE_SHA_CHANGED_"+key)
 scope=F08_SCOPE.read_text()
 require("H_i=(1.01,0.99,1)e-14" in scope and "nH(t)=1e-4" in scope,
         "BASS_ORIGINAL_F08_GEOMETRY_OR_BARYON_CONTRACT_CHANGED")
 ini=np.load(INIT,allow_pickle=False)
 V=ini["W_node"]*MPC_CM**3/(1+5.95)**3
 NH=ini["N_HI"]+ini["N_HII"]
 require(V.shape==(N,) and np.all(V>0) and np.all(NH>0),"ORIGINAL_CELL_NH_V_CONE")
 require(abs(float(ini["W_node"].sum())-1)<3e-14,"ORIGINAL_SOURCE_WEIGHT_SUM")
 ne=[];x=[];T=[];NHe=[];time=[]
 with gzip.open(REI27,"rt") as f:
  for j,row in enumerate(csv.DictReader(f)):
   idx=j%N;tick=EPOCHS[j//N]
   require(int(row["node"])==idx and int(row["accepted_tick"])==tick,"ORIGINAL_REI_F05_184K_SEQUENCE")
   n_h=float(row["N_H"]); n_he=float(row["N_He"])
   require(abs(n_h/NH[idx]-1)<2e-13,"ORIGINAL_CELL_H_COUNT_IDENTITY")
   ne.append(float(row["N_e"])/V[idx])
   x.append(float(row["N_HII_point"])/n_h)
   NHe.append(n_he)
   T.append(float(row["T_K"]))
   time.append(float(row["proper_time_s"]))
 require(len(ne)==4*N,"REI_4EPOCH_REAL_NODES_MISSING")
 arrays={"ne":np.asarray(ne).reshape(4,N),"x":np.asarray(x).reshape(4,N),"T":np.asarray(T).reshape(4,N),"NHe":np.asarray(NHe).reshape(4,N),"NH":NH,"V":V}
 t=np.asarray(time).reshape(4,N)
 require(np.all(np.max(t,axis=1)-np.min(t,axis=1)<1e-5),"ORIGINAL_PROPER_CLOCK_NOT_COMMON")
 times=t[:,0]
 require(np.all(np.diff(times)>0),"ORIGINAL_F05_CLOCK_NONMONOTONIC")
 require(np.all((arrays["x"]>0)&(arrays["x"]<1)) and np.all(arrays["ne"]>0),"F05_HHE_PHYSICAL_CONE")
 with FORCING.open(newline="") as f:
  forcing=[row for row in csv.DictReader(f) if int(row["interval_index"])==0]
 require(len(forcing)==17,"F05_PHOTON_SOURCE_NODES")
 z0={float(r["z_start"]) for r in forcing}; zm={float(r["z_mid"]) for r in forcing};z1={float(r["z_end"]) for r in forcing}
 require(z0=={6.0} and zm=={5.95} and z1=={5.9},"F05_REDSHIFT_LABEL_CHANGED")
 tf=np.asarray([float(r["time_s"]) for r in forcing])
 require(np.all(np.diff(tf)>0) and abs(tf[0])<1e-9,"F05_FULL_SOURCE_CLOCK")
 # 17 source photon values and original 26-event 46k cells are independent
 # but share the pinned F05 proper-time origin and original source interval.
 dt=tf[-1]/131072.
 require(abs(times[-1]/160/dt-1)<2e-12,"F05_ACCEPTED_HISTORY_AND_FULL_SOURCE_CLOCK_MISMATCH")
 f08={}
 with gzip.open(F08,"rt") as f:
  for row in csv.DictReader(f):
   branch=(row["branch"],row["model"])
   f08.setdefault(branch,[]).append({k:float(row[k]) for k in ("step","proper_t_s","xHII","xHeII","xHeIII","T_K","N_photons_per_H")})
 require(len(f08)==4 and all(len(a)==160 for a in f08.values()),"F08_640_TRUE_SOURCE_ROWS")
 for key,rows in f08.items():
  require([int(q["step"]) for q in rows]==list(range(1,161)),"BASS_F08_ORIGINAL_STEPS_NOT_CONSECUTIVE")
  require(abs(rows[-1]["proper_t_s"]-1e11)<1e-6,"BASS_F08_ORIGINAL_CLOCK_CHANGED")
 return arrays,times,forcing,tf,dt,f08,sha(F08_SCOPE)

def hubble_planck_reference(z):
 # Illustrative, explicitly model-dependent flat LCDM Planck18 reference;
 # negligible radiation term at 6-10 in this approximate comparator.
 H0=H0_KM_S_MPC*1e5/MPC_CM
 return H0*math.sqrt(OMEGA_M*(1.+z)**3+OMEGA_L)

def run(out):
 out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
 a,times,forcing,ft,dt,f08,scope_sha=read_original()
 source_time=float(ft[-1])
 hf=math.log((1.+6.)/(1.+5.9))/source_time
 refH={str(z):hubble_planck_reference(z) for z in (5.95,6,8,10)}
 meanF08=sum(BASS_H_BI)/3
 # Known original 26-event accepted four-point source, not dense output:
 # for each original cell, prescribed piecewise-affine electron density
 # yields an exact time integral of that declared interpolant.
 integ=np.zeros(N)
 for j in range(3):
  integ+=(times[j+1]-times[j])*(a["ne"][j]+a["ne"][j+1])/2.
 tau=C_CM_S*SIGMA_T_CM2*integ
 integrated_4epochs_s=float(times[-1])
 # baryon mass or H nucleus weighting is original source spatial scaling,
 # not a cosmological observed angular average.
 nweight=a["NH"]/np.sum(a["NH"])
 npart={str(t):{
  "HII":qstat(a["x"][i]),
  "HI_neutral":qstat(1-a["x"][i]),
  "proper_n_e_cm_minus_3":qstat(a["ne"][i]),
  "gas_temperature_K":qstat(a["T"][i]),
  "N_H_weighted_HII_mean":float(np.dot(nweight,a["x"][i])),
  "cells_below_xHII_0p9":int(np.count_nonzero(a["x"][i]<.9)),
  "cells_below_xHII_0p99":int(np.count_nonzero(a["x"][i]<.99)),
  "nucleus_weighted_neutral_mean":float(np.dot(nweight,1-a["x"][i]))
 } for i,t in enumerate(EPOCHS)}
 branch={}
 for (bg,mod),rows in sorted(f08.items()):
  branch[f"{bg}_{mod}"]={
   "source_time_steps":len(rows),"first_t_s":rows[0]["proper_t_s"],
   "last_t_s":rows[-1]["proper_t_s"],
   "xHII_first":rows[0]["xHII"],
   "xHII_last":rows[-1]["xHII"],
   "T_first_K":rows[0]["T_K"],"T_last_K":rows[-1]["T_K"],
   "N_photons_last_per_H":rows[-1]["N_photons_per_H"]}
 require(all(v["cells_below_xHII_0p99"]==0 for v in npart.values()),"NEW_F05_NEUTRAL_CELLS_FOUND_RECHECK_SCIENCE")
 # Historical F05 source H/He 46k and photons are close to end-of-reionization
 # boundary (6.0->5.9), not the 6->10 first-reionization source/geometry pair.
 if not .5<hf/refH["5.95"]<1.5:raise ArithmeticError("F05_PHYSICAL_CLOCK_MISMATCH_PLANCK_REFERENCE")
 if not meanF08/hf>100:raise AssertionError("F08_BACKGROUND_CLOCK_EXPECTED_MISMATCH_NOT_FOUND")
 # Source neutron-relative opacity: original F05 G3 exact zero, G1-2b populated.
 groups={g:{"min":float(min(float(r[f"N_{g}_cMpc-3"]) for r in forcing)),
            "max":float(max(float(r[f"N_{g}_cMpc-3"]) for r in forcing))}
           for g in ("G1","G2a","G2b","G3")}
 require(groups["G3"]=={"min":0.,"max":0.},"NATIVE_ORIGINAL_F05_G3_NOT_ZERO")
 # F05 total full-source 17 time nodes are from a prescription for z in 6->5.9;
 # 0->160 covers a small fraction of full run, not an accepted full EoR evolution.
 ratio=integrated_4epochs_s/source_time
 source={
  "schema":"WU_R59_ORIGINAL_REI_IGM_CORE_REI_EXP_SCENARIO_SOURCE_DISCOVERY_V1",
  "unit":"SOURCE_AUTHENTIC_LATE_REIONIZATION_BOUNDARY_FLRW_CONTROL_AND_F08_GEOMETRY_ELIGIBILITY",
  "original_F05":{"z_source_start":6.0,"z_mid":5.95,"z_end":5.9,
    "full_source_proper_T_s":source_time,
    "accepted_last_tick":160,"source_total_ticks":131072,
    "accepted_source_proper_t_s":integrated_4epochs_s,
    "accepted_fraction_of_full_source_interval":ratio,
    "original_accepted_HHe_real_cells":N,
    "original_HHe_state_t0_64_128_160":npart,
    "full_source_17_knots":17,
    "original_native_group_photons":groups,
    "source_gamma_hi_first_s_inv":float(forcing[0]["Gamma_HI_s-1"]),
    "source_gamma_HI_exposure_accepted_0to160_dimensionless":float(PchipInterpolator(ft,np.asarray([float(r["Gamma_HI_s-1"]) for r in forcing])).integrate(0.,integrated_4epochs_s)),
    "source_gamma_hi_last_s_inv":float(forcing[-1]["Gamma_HI_s-1"]),
    "clock_inferred_mean_H_per_s_if_FLRW_from_z6_to_z5p9":hf,
    "hubble_compare_planck18_flat_LCDM_model_dependent":refH,
    "clock_H_over_Planck18_5p95":hf/refH["5.95"],
    "original_F05_photon_and_matter_source_unit":"cMpc^-3 photon counts / original 46k matter cells"},
  "original_F08":{"source_rows":640,"H_i_Bianchi_prescribed_s_inv":list(BASS_H_BI),
    "H_i_FLRW_prescribed_s_inv":list(BASS_H_FLRW),
    "H_mean_s_inv":meanF08,
    "H_BASS_over_source_F05_FLRW_clock":meanF08/hf,
    "H_BASS_over_Planck18_at_z6":meanF08/refH["6"],
    "H_BASS_over_Planck18_at_z10":meanF08/refH["10"],
    "source_duration_s":1e11,"source_redshift_absolute_epoch":"NOT_SPECIFIED_IN_S0_SOURCE",
    "source_reference_photon_energy_eV":13.7,
    "source_initial_nH_cm_minus_3":1e-4,
    "source_hhe_4_true_branches":branch},
  "new_F05_Thomson_material":{
    "definition":"c sigma_T integral n_e(t)dt from tick0 to160 with exact original accepted electron endpoints and declared affine interpolation between epochs; cell-local rest-frame hazard, NOT tau(z) sky.",
    "electron_are_original_26_event_HHe_only":True,
    "sigma_T_cm2":SIGMA_T_CM2,"c_cm_per_s":C_CM_S,
    "source_accepted_duration_s":integrated_4epochs_s,
    "electron_column_cm_minus_3_s":qstat(integ),
    "local_hazard_tau":qstat(tau),
    "H_nucleus_weighted_tau_proxy":float(np.dot(nweight,tau)),
    "positive_cells":int(np.count_nonzero(tau>0)),
    "observed_Bianchi_or_CMB_tau":"NOT_COMPUTED"},
  "source_consumer_assessment":{
    "F05":"SOURCE_MATCHED_LATE_EOR_BOUNDARY_FLRW_MATERIAL_AND_PHOTON_CLOCK_BUT_NOT_FULL_EOR_HISTORY",
    "F08":"SOURCE_MATCHED_TOY_BIANCHI_FLRW_PAIR_BUT_NOT_ABSOLUTE_COSMOLOGICAL_EOR_EPOCH_OR_F05_CLOCK",
    "Puchwein2019":"PUBLISHED_HIGH_Z_UVB_MODEL_SPECTRUM_AVAILABLE_IN_LITERATURE_BUT_NOT_BOUND_TO_ORIGINAL_F05_F08_SOURCE_OWNER",
    "named_reionization_EOR_Bianchi_FLRW_coupled_pair":"NO_CONFIRMED_COMMON_EPOCH_AND_CLOCK",
    "require_new_REI_owner_matched_source":"YES",
    "new_canonical_completion":"NO"},
  "gates":{"REI_EXP_SCENARIO":"PARTIAL_SOURCE_QUALIFIED_FLRW_END_BOUNDARY",
    "REI_L0_L1":"NOT_NEWLY_ACCEPTED",
    "REI_L4":"HOLD",
    "full_26event_observer_BI_FLRW_matched":"NOT_RUN",
    "official_REI_tick161":"HOLD"},
  "DAG":{"WU":"34/49","REI_central":"28/88","REI_working":"33/88","FAST":"4/7","canonical_delta":0},
  "source_SHA256":{**LOCKS,"F08_SOURCE_SCOPE_TEXT":scope_sha}}
 owner={
 "schema":"WU_R59_REI_SOURCE_ABSORBER_OWNER_MATRIX_V1",
 "source_consumers":[
 {"source":"F05 17-node UVB groups+Gamma_HI","owner":"REI original 26-event F05","epoch":"source endpoints 6.0→5.9, original native proper 131072 ticks","physics":"H/He ionization and absorbed photon/gas heat","qualified":"SOURCE_BOUNDED_FLRW_LATE_EOR_END_ONLY","missing":"accepted full 0→131072 H/He history + real Bianchi geometry"},
 {"source":"F05 original H/He 184320 accepted rows","owner":"REI #367 / REC #195 + WU R57 byte-locked replay","epoch":"ticks 0,64,128,160 only","physics":"H/He nuclei,electrons,T native 26event","qualified":"ENDPOINT_SOURCE_ACCEPTED","missing":"accepted dense continuous state past tick160"},
 {"source":"F08 original S0 640 H/He coupled plus photon trajectory","owner":"BASS #328 original REI F08 Rust microphysics","epoch":"proper time 0→1e11 s, no absolute z anchor","physics":"one Bianchi/FLRW controlled four-case photon/HHe source","qualified":"EXPERIMENTAL_S0_SOURCE_ONLY","missing":"cosmologically calibrated BI H_i and redshift mapping; original F05 source matching"},
 {"source":"Puchwein 2019 literature UVB","owner":"published UVB synthesis","epoch":"EoR redshift 6-10 source candidate","physics":"volume-average HI/He photo rates and energy","qualified":"LITERATURE_ONLY_NO_OWNER_COUPLED_DATA","missing":"unique original REI source spectrum/escape/observer geometry/initial state"},
 {"source":"WU R48 HD19 original collision operator","owner":"WU microscope conditional source","epoch":"only 5616 F05 original cells in 19-state shared collider T grid","physics":"molecular internal collision operator; NO true nHD","qualified":"OPTIONAL_NONCRITICAL","missing":"actual HD abundance, full radiative and chemical owner, observation materiality"}],
 "one_validated_source_matched_full_EOR_scenario":False,
 "owner_admission_missing":"REI first EoR original H/He+photon+thermal + Bianchi/FLRW common source-clock-geometry physical run",
 "new_canonical_completion":0}
 f05_tau=out/"R59_REAL_ORIGINAL_F05_46080_CELL_THOMSON_SOURCE.csv.gz"
 with f05_tau.open("wb") as f:
  with gzip.GzipFile(fileobj=f,filename="",mtime=0,mode="wb",compresslevel=6) as z:
   with io.TextIOWrapper(z,encoding="ascii",newline="") as w:
    wr=csv.writer(w,lineterminator="\n")
    wr.writerow(["node","original_H_nuclei","comoving_W","proper_volume_cm3",
                 "x_HII_tick0","x_HII_tick64","x_HII_tick128","x_HII_tick160",
                 "n_e_tick0_cm3","n_e_tick64_cm3","n_e_tick128_cm3","n_e_tick160_cm3",
                 "original_T_tick160_K","electron_column_cm_minus3_s_0_160","local_Thomson_tau_proxy_0_160"])
    for i in range(N):
     wr.writerow([i,*[format(float(k),".17e") for k in
       (a["NH"][i],a["V"][i]/(MPC_CM**3/(1+5.95)**3),
        a["V"][i],*[a["x"][j,i] for j in range(4)],
        *[a["ne"][j,i] for j in range(4)],a["T"][3,i],integ[i],tau[i])]])
 public_result={
    "schema":"WU_R59_SOURCE_MATCHED_EOR_CORE_SCIENCE_RESULT_V1",
    "original_F05_source":source["original_F05"],
    "BASS_F08_source":source["original_F08"],
    "source_matched_Thomson_proxy":source["new_F05_Thomson_material"],
    "physical_decision":source["source_consumer_assessment"],
    "DAG":source["DAG"],
    "files":{"46080_real_source_cells":f05_tau.name,"sha256":sha(f05_tau)},
    "source_SHA256":source["source_SHA256"],
    "operational_claim":"SOURCE_QUALIFIED_FLRW_LATE_EOR_BUT_NO_GENUINE_SOURCE_MATCHED_BIANCHI_FIRST_REIONIZATION"}
 for name,data in [
 ("SCENARIO.json",source),("SOURCE_ABSORBER_OWNER_MATRIX.json",owner),
 ("MATCHED_INPUT_IDENTITY.json",{"schema":"WU_R59_SOURCE_INPUT_IDENTITIES_V1",
 "original_rei_F05":{k:LOCKS[k] for k in ("REI_F05_184320_27col","REI_F05_17_photon_knots","REI_F05_initial_material")},
 "original_bass_F08":LOCKS["BASS_F08_640_native_consecutive"],
 "source_scope_F08_SHA256":scope_sha,"common_cosmological_epoch_clock":"NOT_ESTABLISHED",
 "F05_accepted_only_ticks":[0,64,128,160],
 "F08_source_neither_full_REI_F05_26event_nor_true_EOR_absolute_z":True,
 "asserted_equivalence":"NO_UNJUSTIFIED_SOURCE_TRANSPORT"}),
 ("R59_RESULTS.json",public_result)]:
  (out/name).write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"RESULT":"R59_REI_EXP_SCENARIO_SOURCE_DOMAIN_SCOPED","REI_F05_xHII160":npart["160"]["HII"],
 "F05_ACCEPTED_tau":source["new_F05_Thomson_material"]["local_hazard_tau"],
 "F05_clock_H_s":hf,"F08_H_over_F05":meanF08/hf,"F05_full_source_time_s":source_time,
 "source_46080_csv_sha256":sha(f05_tau),"canonical_DAG":"WU 34/49; REI central 28/88"},sort_keys=True))
 return source

if __name__=="__main__":
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument("--out",type=pathlib.Path,default=ROOT/"results")
 arg=ap.parse_args()
 run(arg.out)
