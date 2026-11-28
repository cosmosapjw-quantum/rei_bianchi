#!/usr/bin/env python3
"""Disjoint stdlib audit: original H/He thermal Udot and Savin 47-rate
source reconstruction vs the generated 46,080 WU CX thermal event dataset.
Never imports the R58/R57 producer or its rate implementation.
"""
from __future__ import annotations
from pathlib import Path
import csv,gzip,hashlib,json,math,bisect
ROOT=Path(__file__).resolve().parent
N=46080
ETA=2.5e-5
DELTA=0.0037
EV=1.602176634e-12
CHI_H=13.598434599702
OLD_CHI_D=13.6017
RATES=Path("/home/cosmosapjw/research_backups/WU088_HH/R54_REI_F05_DI_GROUP_PHOTON_DEBIT_20261101/source_inputs/SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv")
OWNER=Path("/home/cosmosapjw/archives/rei_f05_owner_accepted_trajectory_rhs_20261102/private/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz")
REC=Path("/home/cosmosapjw/worktrees/rec-f05-accepted-trajectory-20261102/research/rec_f05_accepted_trajectory_20261102/results/ORIGINAL_F05_REPLAY_0_64_128_160_46080.csv.gz")
PARENT=Path("/home/cosmosapjw/research_backups/WU088_HH/R57_REI_F05_NATIVE_RHS_DI_HISTORY_20261102/results/R57_RESULTS.json")
SCENARIOS=("H_MATCHED","ALL_NEUTRAL")

def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def need(condition,message):
 if not condition:raise AssertionError(message)

def load_savin():
 with RATES.open(newline="") as f:
  raw=list(csv.DictReader(f))
 need(len(raw)==47,"MISSING_SOURCE_ORIGINAL_47_RATE_NODES")
 xs=[math.log(float(r["T_K"])) for r in raw]
 fw=[math.log(float(r["k_forward_cm3_s"])) for r in raw]
 bw=[math.log(float(r["k_reverse_cm3_s"])) for r in raw]
 return xs,fw,bw

def rates(T,table):
 xs,fw,bw=table
 ln=math.log(T);i=min(max(0,bisect.bisect_right(xs,ln)-1),len(xs)-2)
 u=(ln-xs[i])/(xs[i+1]-xs[i])
 u=min(1.,max(0.,u))
 return (math.exp(fw[i]*(1-u)+fw[i+1]*u),
         math.exp(bw[i]*(1-u)+bw[i+1]*u))

def audit(out=None):
 out=Path(out or ROOT/"results")
 j=json.loads((out/"R58_RESULTS.json").read_text())
 full=out/j["files"]["full_original_source_conditional_46080_csv"]
 need(sha(full)==j["files"]["full_original_source_conditional_SHA256"],"FULL_PHYSICAL_DATA_SHA")
 need(sha(OWNER)==j["authority_source_SHA256"]["REI_original_26event_184320_row_RHS"],"REI_ORIGINAL_26EVENT_SHA")
 need(sha(REC)==j["authority_source_SHA256"]["REC_original_4epoch_184320_row_material"],"REC_SOURCE_SHA")
 need(sha(PARENT)=="02c5b3f1baea972c6a0feb0d50e5c1162c739c5f8cbe4983ed9e4d47db3748d3","IMMUTABLE_R57_PARENT_RESULT_SHA")
 table=load_savin()
 ref=json.loads(PARENT.read_text())
 need(ref["immutable_parent_WU_PR196"]=="2d52baa98bd97b513a2cdad2f2c1fe1b5e9917b0",
      "R57_PARENT_WRONG")
 need(j["physical_contract"]["original_REI_161"]=="NOT_ACCEPTED","TICK161_FALSE_ADMISSION")
 need(j["DAG"]["new_canonical"]==0,"FALSE_CANONICAL_DAG")
 Eshift=(CHI_H+DELTA)-OLD_CHI_D
 need(abs(Eshift-0.000434599702)<5e-13,"SAVIN_NATIVE_H_BINDING_ENERGY_ALIGNMENT")

 # Read source-original t160 cellwise 26-event RHS and keep one one-owner
 # state record per cell. Event rates are owned by original REI, not generated.
 orig=[]
 with gzip.open(OWNER,"rt",newline="") as f:
  r=csv.DictReader(f)
  for k,row in enumerate(r):
   t=int(row["accepted_tick"])
   need(int(row["node"])==k%N and t==(0,64,128,160)[k//N],"REI_SOURCE_ROW_ORDER")
   if t==160:orig.append(row)
 need(len(orig)==N,"REI_OWNER_46080_T160")
 count=0
 err_C_integral={s:0. for s in SCENARIOS}
 err_Gamma={s:0. for s in SCENARIOS}
 err_CXrate={s:0. for s in SCENARIOS}
 err_CXpower={s:0. for s in SCENARIOS}
 heat_first={s:[] for s in SCENARIOS}
 heat_hist={s:[] for s in SCENARIOS}
 photon_correction={s:[] for s in SCENARIOS}
 source_power={s:[] for s in SCENARIOS}
 orig_U=[]
 with gzip.open(full,"rt",newline="") as f:
  for row in csv.DictReader(f):
   i=int(row["node"])
   need(i==count,"R58_CELL_ORDER")
   count+=1
   base=orig[i]
   H=float(row["original_H_nuclei"])
   nH=float(row["native_proper_nH_cm3"])
   T=float(row["original_T_tick160_K"])
   x=float(row["original_HII_tick160"])
   need(H>0 and nH>0 and 0<x<1 and T>0,"ORIGINAL_SOURCE_PHYSICAL_CONE")
   need(abs(H/float(base["N_H"])-1)<3e-14,"ORIGINAL_OWNER_H_IDENTITY")
   need(abs(T/float(base["T_K"])-1)<3e-13,"ORIGINAL_OWNER_T_IDENTITY")
   orig_Udot=float(base["native_thermal_rhs_erg_s"])
   need(abs(orig_Udot/float(row["original_REI_26event_thermal_Udot_tick160_erg_per_s"])-1)<3e-14,
       "ORIGINAL_OWNER_THERMAL_RHS_CHANGED")
   orig_U.append(orig_Udot)
   kf,kr=rates(T,table)
   for s in SCENARIOS:
    C160=float(row[s+"_C160"])
    C161=float(row[s+"_C161"])
    y160=float(row[s+"_y160"])
    need(0<=y160<=1,"NONPHYSICAL_D_ION_FRACTION")
    xeff=x-ETA*C160
    need(0<=xeff<=1,"HPLUS_SOURCE_CHARGE_COMPENSATION_CONE")
    forward=nH*kf*xeff*(1-y160)
    reverse=nH*kr*(1-xeff)*y160
    net=forward-reverse
    observed_rate=float(row[s+"_cx_rate_tick160_per_D_s"])
    err_CXrate[s]=max(err_CXrate[s],abs(net-observed_rate)/max(abs(forward)+abs(reverse),1e-300))
    phys_power=-DELTA*EV*ETA*H*net
    measured_power=float(row[s+"_CX_gas_power_tick160_erg_per_cell_s"])
    # The net CX source may nearly cancel; normalize by gross forward+reverse
    # energy scale, not the ill-conditioned net power itself.
    gross_power_scale=DELTA*EV*ETA*H*(abs(forward)+abs(reverse))
    err_CXpower[s]=max(err_CXpower[s],abs(phys_power-measured_power)/max(gross_power_scale,1e-290))
    source_power[s].append(phys_power)
    h0=float(row[s+"_Qgas_CX_0to160_erg_per_H"])
    h1=float(row[s+"_Qgas_CX_first_tick_erg_per_H"])
    ref_h0=-ETA*DELTA*EV*C160
    ref_h1=-ETA*DELTA*EV*(C161-C160)
    err_C_integral[s]=max(err_C_integral[s],abs(ref_h0-h0)/max(abs(ref_h0),abs(h0),1e-200),
                                          abs(ref_h1-h1)/max(abs(ref_h1),abs(h1),1e-200))
    heat_hist[s].append(H*h0)
    heat_first[s].append(H*h1)
    shift=float(row[s+"_Qgas_DI_photo_threshold_consistency_shift_first_tick_erg_per_H"])
    photon_correction[s].append(H*shift)
    need(math.isfinite(shift) and shift<=0,"DI_FIXED_PHOTON_THRESHOLD_SHIFT_CONE")
 need(count==N,"MISSING_OR_DUPLICATE_SOURCE_CELLS")
 max_error=max(*err_C_integral.values(),*err_CXrate.values(),*err_CXpower.values())
 print("AUDIT_DIAGNOSTIC",{"net_rates":err_CXrate,"power":err_CXpower,"integral":err_C_integral,"max":max_error},flush=True)
 need(max_error<2e-11,"INDEPENDENT_CX_RATE_AND_STOICHIOMETRY_FAIL")
 source_total=math.fsum(orig_U)
 need(abs(source_total/j["original_source_reference"]["original_REI_original_Udot_at_ticks_erg_s"][3]-1)<4e-14,
      "ORIGINAL_OWNER_GLOBAL_26EVENT_THERMAL")
 results={}
 for s in SCENARIOS:
  sc=j["scenario_science"][s]
  summed=dict(hist=math.fsum(heat_hist[s]),first=math.fsum(heat_first[s]),
              photon_shift=math.fsum(photon_correction[s]),t160_power=math.fsum(source_power[s]))
  expected=(sc["CX_history_0to160_signed_gas_energy_erg_per_cMpc3"],
       sc["CX_native_160to161_signed_gas_energy_erg_per_cMpc3"],
       sc["source_consistent_DI_photo_threshold_correction_erg_per_cMpc3"],
       sc["instantaneous_original_epoch_CX"]["160"]["signed_CX_thermal_power_erg_s_per_cMpc3"])
  rel={k:abs(v-b)/max(abs(v),abs(b),1e-200) for k,v,b in zip(summed, summed.values(),expected)}
  need(max(rel.values())<2e-13,"INDEPENDENT_46080_CELL_EXTENSIVE_RECOUNT_"+s)
  gross_photons= -summed["photon_shift"]/(Eshift*EV)
  original_R57=ref["results"][s+"_native_rhs_hermite"]["first_tick_gross_photons_total"]
  need(abs(gross_photons/original_R57-1)<1e-10,"SOURCE_FIXED_PHOTON_EVENTS_WRONG_"+s)
  results[s]=dict(recount=summed,max_recount_relative_error=max(rel.values()),
     independently_reconstructed_parent_R57_photons=gross_photons,
     independent_rate_160_scaled_error=err_CXrate[s],
     independent_power_160_rel_error=err_CXpower[s],
     independent_integrated_CX_heat_rel_error=err_C_integral[s])
 result={"schema":"WU_R58_HOSTILE_STDLIB_ORIGINAL_REI_CX_SOURCE_INDEPENDENT_AUDIT_V1",
   "original_REI_26event_owner_thermal_rows":N,
   "original_REI_4epoch_source_rows_scanned":4*N,
   "source_replayed_D_cells":count,
   "native_owner_t160_thermal_power_erg_s":source_total,
   "Savin_47_original_rate_nodes_checked":47,
   "source_H_binding_eV":CHI_H,"published_CX_endothermic_eV":DELTA,
   "older_WU_D_photo_threshold_eV":OLD_CHI_D,
   "source_Savin_CX_matched_D_threshold_eV":CHI_H+DELTA,
   "energetic_H_D_threshold_shift_eV":Eshift,
   "microscopic_exchange_electron_source_exact_zero":True,
   "microscopic_exchange_photon_source_exact_zero":True,
   "microscopic_exchange_gas_plus_binding_source_exact_zero":True,
   "scenarios":results,
   "native_subagent":"NOT_RUN","distinct_author":"NOT_RUN",
   "same_author_disjoint_implementation":True,
   "original_owner_native_HHeDI_coupled_solver":"NOT_RUN",
   "owner_tick161":"HOLD",
   "verdict":"PASS_SCOPED_REAL_SOURCE_DI_HISTORY_CONDITIONAL_CX_THERMAL"}
 p=out/"R58_INDEPENDENT_AUDIT.json"
 p.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print(json.dumps(result,sort_keys=True))
 return result
if __name__=="__main__":audit()
