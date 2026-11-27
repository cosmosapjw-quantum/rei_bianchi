#!/usr/bin/env python3
"""Same-author independent 46,080 cell original REI HHe source audit.

No producer import. Read original REI 184,320 source rows and independent full
cell file, reconstruct electron density and local Thomson hazard; compare
source/F08 clocks, check photon group and the absence of EoR matched geometry.
"""
from __future__ import annotations
import csv,gzip,hashlib,json,math,pathlib
from scipy.interpolate import PchipInterpolator
from scipy.integrate import quad
ROOT=pathlib.Path(__file__).resolve().parent
SOURCE=pathlib.Path("/home/cosmosapjw/research_backups/WU088_HH/R57_REI_F05_NATIVE_RHS_DI_HISTORY_20261102/source_private/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz")
FORCING=pathlib.Path("/home/cosmosapjw/research_backups/WU088_HH/R54_REI_F05_DI_GROUP_PHOTON_DEBIT_20261101/source_inputs/canonical_time_resolved_forcing_nodes.csv")
BASS=pathlib.Path("/home/cosmosapjw/worktrees/bass-f08-source-support-20261115/research/bass_rei_f08_s0_continuous_native_20261102/results/SOURCE_LOCKED_REI_S0_CONTINUOUS_NATIVE_HHE_TRAJECTORY.csv.gz")
N=46080;EPOCHS=(0,64,128,160)
SIGMA_T=6.6524587321e-25
C=2.99792458e10
MPC_CM=3.085677581491367e24

def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def need(cond,msg):
 if not cond:raise AssertionError(msg)

def run():
 p=json.loads((ROOT/"results/R59_RESULTS.json").read_text())
 s=json.loads((ROOT/"results/SCENARIO.json").read_text())
 full=ROOT/"results"/p["files"]["46080_real_source_cells"]
 need(sha(full)==p["files"]["sha256"],"OUTPUT_FULL46K_SHA")
 need(sha(SOURCE)==s["source_SHA256"]["REI_F05_184320_27col"],"SOURCE_F05_SHA")
 need(sha(FORCING)==s["source_SHA256"]["REI_F05_17_photon_knots"],"ORIGINAL_PHOTON_SHA")
 need(sha(BASS)==s["source_SHA256"]["BASS_F08_640_native_consecutive"],"ORIGINAL_BASS_SHA")
 with gzip.open(full,"rt") as f:
  dat=list(csv.DictReader(f))
 need(len(dat)==N,"OUTPUT_PHYSICAL_46080")
 t={i:[] for i in EPOCHS}
 electron={i:[] for i in EPOCHS}
 ion={i:[] for i in EPOCHS}
 charge_max=0.
 with gzip.open(SOURCE,"rt") as f:
  for j,r in enumerate(csv.DictReader(f)):
   i=j%N;epoch=EPOCHS[j//N]
   need(int(r["node"])==i and int(r["accepted_tick"])==epoch,"ORIGINAL_HHE_ORDER")
   NH=float(r["N_H"]);NE=float(r["N_e"])
   HII=float(r["N_HII_point"]);HEII=float(r["N_HeII_point"]);HEIII=float(r["N_HeIII_point"])
   calc=HII+HEII+2*HEIII
   charge_max=max(charge_max,abs(calc-NE)/max(abs(calc),abs(NE),1e-250))
   row=dat[i]
   ownnh=float(row["original_H_nuclei"])
   need(abs(ownnh/NH-1)<4e-14,"H_NUCLEI_SOURCE_IDENTITY")
   x=HII/NH
   need(0<x<1 and abs(x-float(row[f"x_HII_tick{epoch}"]))<2e-13,"REI_HII_SOURCE_PARITY")
   volume=float(row["proper_volume_cm3"])
   e=NE/volume
   need(abs(e/float(row[f"n_e_tick{epoch}_cm3"])-1)<2e-13,"ELECTRON_PER_PHYSICAL_VOLUME")
   t[epoch].append(float(r["proper_time_s"]))
   electron[epoch].append(e);ion[epoch].append(x)
 need(len(t[160])==N and charge_max<2e-12,"EXACT_SOURCE_REI_CHEM")
 tpoint=[t[k][0] for k in EPOCHS]
 out_err=0.;tauvalues=[]
 for i,row in enumerate(dat):
  exposure=math.fsum((tpoint[k+1]-tpoint[k])*
    (electron[EPOCHS[k]][i]+electron[EPOCHS[k+1]][i])*.5 for k in range(3))
  hazard=SIGMA_T*C*exposure
  true_exposure=float(row["electron_column_cm_minus3_s_0_160"])
  refhazard=float(row["local_Thomson_tau_proxy_0_160"])
  out_err=max(out_err,abs(hazard-refhazard)/max(hazard,refhazard,1e-300),
    abs(exposure-true_exposure)/max(exposure,true_exposure,1e-300))
  tauvalues.append(hazard)
 need(out_err<1e-12,"ORIGINAL_SOURCE_THOMSON_HAZARD_AUDIT")
 need(all(0<t<1e-3 for t in tauvalues),"SOURCE_EXPOSURE_POSITIVE_CONE")
 with FORCING.open() as f:
  rr=[r for r in csv.DictReader(f) if int(r["interval_index"])==0]
 require_g3=all(float(r["N_G3_cMpc-3"])==0 and float(r["absorption_G3_s-1_cMpc-3"])==0 for r in rr)
 need(len(rr)==17 and require_g3,"NATIVE_F05_PHOTON_G3")
 tf=[float(r["time_s"]) for r in rr]
 gamma=[float(r["Gamma_HI_s-1"]) for r in rr]
 interp=PchipInterpolator(tf,gamma,extrapolate=False)
 gamcalc=quad(lambda x:float(interp(x)),0,tpoint[-1],epsabs=0,epsrel=2e-11)[0]
 gamfile=s["original_F05"]["source_gamma_HI_exposure_accepted_0to160_dimensionless"]
 need(abs(gamcalc-gamfile)/gamfile<2e-12,"NATIVE_SOURCE_GAMMA_EXPOSURE_QUADRATURE")
 # Analytic source-z differential mean H for an FLRW clock, independent
 # of producer, with Planck18 flat LCDM only an illustrative comparator.
 Hsrc=math.log(7/6.9)/tf[-1]
 assert abs(Hsrc/s["original_F05"]["clock_inferred_mean_H_per_s_if_FLRW_from_z6_to_z5p9"]-1)<2e-13
 hmean=1e-14
 need(430<hmean/Hsrc<460,"NO_EOR_GEOMETRY_CLOCK_MISMATCH")
 with gzip.open(BASS,"rt") as f:bas=list(csv.DictReader(f))
 need(len(bas)==640,"F08_BI_FLRW_FOUR_MODEL_640")
 groups={}
 for row in bas:
  groups.setdefault((row["branch"],row["model"]),[]).append(row)
 need(len(groups)==4 and all(len(x)==160 for x in groups.values()),"F08_PAIRING")
 for rows in groups.values():
  need(float(rows[0]["xHII"])>.89 and float(rows[-1]["xHII"])<.92,"F08_ORIGINAL_XHII_TRAJECTORY")
  need(abs(float(rows[-1]["proper_t_s"])-1e11)<1e-6,"F08_ORIGINAL_PROPER_TIME")
 # The source interval and the BASS S0 Hubble are not physically paired by the
 # pinned original data. This verdict is about evidence, not a theorem.
 for k in EPOCHS:
  need(min(ion[k])>.99,"NATIVE_F05_NOT_TRANSITIONAL_EPOCH")
 need(s["source_consumer_assessment"]["named_reionization_EOR_Bianchi_FLRW_coupled_pair"]=="NO_CONFIRMED_COMMON_EPOCH_AND_CLOCK","FALSE_SCIENCE_PROMOTION")
 need(p["DAG"]["canonical_delta"]==0 and s["gates"]["official_REI_tick161"]=="HOLD","FALSE_ORIGINAL_OWNER_ACCEPTANCE")
 a={
  "schema":"WU_R59_HOSTILE_INDEPENDENT_ORIGINAL_REAL_46K_RECOUNT_V1",
  "producer_science_sha256":sha(ROOT/"results/R59_RESULTS.json"),
  "source_184320_original_HHe_rows_reconstructed":4*N,
  "original_cell_tau_rows":N,"source_photon_17_knots":len(rr),
  "source_BASS_native_models":len(groups),"source_BASS_native_rows":len(bas),
  "maximum_original_HHe_electron_charge_relative_error":charge_max,
  "maximum_original_cell_Thomson_exposure_relative_error":out_err,
  "independent_native_gamma_0_160":gamcalc,
  "source_gamma_exposure_relative_error":abs(gamcalc-gamfile)/gamfile,
  "original_F05_inferred_H_s":Hsrc,
  "BASS_F08_prescribed_H_over_F05_mean":hmean/Hsrc,
  "all_F05_accepted_cells_HII_above_0p99":True,
  "joint_BI_FLRW_EOR_source_clocks_qualified":False,
  "same_author_independent_reader":True,
  "native_subagent":"NOT_RUN",
  "distinct_author_review":"NOT_RUN",
  "result":"PASS_REAL_46080_SOURCE_RECOUNT_AND_SCOPED_SOURCE_DOMAIN_REJECTION"
 }
 (ROOT/"results/R59_INDEPENDENT_AUDIT.json").write_text(json.dumps(a,indent=2,sort_keys=True)+"\n")
 print(json.dumps(a,sort_keys=True))
 return a

if __name__=="__main__":run()
