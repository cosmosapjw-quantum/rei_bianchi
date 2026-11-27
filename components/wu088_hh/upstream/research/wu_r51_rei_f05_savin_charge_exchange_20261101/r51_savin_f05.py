#!/usr/bin/env python3
"""WU R51: Savin 2002 atomic D-H charge exchange on original REI F05 46,080 cells.

NO RATE TIMES UNQUALIFIED PARTICLE COUNT. Construct a density-normalized
actual frozen donor source generator, stationary isotope partition and
charge-conserving equilibrium comparison. No invented IVP or H/He owner write.
"""
from __future__ import annotations
import bisect, csv, gzip, hashlib, io, json, math, statistics
from pathlib import Path
from typing import Iterable

ROOT=Path(__file__).resolve().parent
SOURCES=ROOT/"sources"
SHA={
 "SAVIN2002_AR5IV_ORIGINAL_HTML.html":"8d22b670d2225de7a1e81ac1440e06188318cb7703b19e3b9ad214d12cb85d29",
 "SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv":"ba98ec463903f3589c6c68cd7d9e3b3bc637188bb5d25616addb2fb71ab689e8",
 "SAVIN2002_ORIGINAL_TABLE2_FITS.json":"b178d89b858ae58ed1fe873fe831e02b737532a2f1fc20a82c920e76d2c3b1bc",
 "ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz":"713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d",
 "REI_F05_ORIGINAL26_NATIVE_DISCRETE_ENERGY_46080.csv.gz":"024e1d1bbef95d3e254b8c54b3d1134de54eebce7b82d082401c522f813637c5",
}
SOURCE_REI_TAR="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
SOURCE_ACCEPTED_PARENT_STATE="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
REI_PR352_HEAD="ea8d6bf94197392c69f939f03c1673ed3afe349c"
WU_PARENT_PR189_HEAD="b711a6a7f6bfae257f0bcbcea44cad52b8086fc0"
NODES=46080
ETA_D=2.5e-5  # explicit R49/R50 shared *assumed scenario parameter*, not observational CI
EV_TO_ERG=1.602176634e-12
DELTA_E_EV=0.0037
DELTA_E_ERG=DELTA_E_EV*EV_TO_ERG
RATES_VALID=(2.7,200000.0)
FIELDS=[
 "node","original_H_nuclei_N","original_T160_K","original_xHII160",
 "preview_T161_K","preview_xHII161",
 "k_forward160_cm3_s","k_reverse160_cm3_s","k_forward161_cm3_s","k_reverse161_cm3_s",
 "generator_forward160_per_nH_cm3_s","generator_reverse160_per_nH_cm3_s",
 "generator_forward161_per_nH_cm3_s","generator_reverse161_per_nH_cm3_s",
 "CX_equilibrium_Dplus160","CX_equilibrium_Dplus161",
 "CX_equilibrium_Dneutral160","CX_equilibrium_Dneutral161",
 "CX_Dneutral_over_Hneutral160","CX_Dneutral_over_Hneutral161",
 "CX_Dneutral_over_Hneutral_response_161_minus_160",
 "CX_equilibrium_Dplus_response_161_minus_160",
 "CX_stationary_relaxation_per_nH160_cm3_s",
 "CX_stationary_relaxation_per_nH161_cm3_s",
 "Savin_fit_ratio160","Savin_table_ratio160","Savin_fit_ratio161","Savin_table_ratio161",
 "fit_table_ratio_difference160","fit_table_ratio_difference161",
 "CX_conserving_Dplus_eq160_initial_Dneutral",
 "CX_conserving_Hplus_eq160_initial_Dneutral",
 "CX_conserving_Dplus_eq160_initial_Dplus",
 "CX_conserving_Hplus_eq160_initial_Dplus",
 "CX_heat_initial_Dneutral_160_erg_per_H",
 "CX_heat_initial_Dplus_160_erg_per_H",
 "CX_absolute_energy_ceiling_erg_per_H",
 "original_F05_native_thermal_gain_erg_per_H",
 "CX_energy_ceiling_over_F05_abs_thermal_gain",
 "CX_global_Dnuclei_N_assumed",
 "CX_charge_conservation_residual_initial_Dneutral",
 "CX_charge_conservation_residual_initial_Dplus"
]


def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()


def require_sources():
 for n,d in SHA.items():
  if sha(SOURCES/n)!=d:
   raise ValueError("IMMUTABLE_SOURCE_SHA256_MISMATCH:"+n)
 table=[]
 with (SOURCES/"SAVIN2002_ORIGINAL_TABLE1_47_RATE_PAIRS.csv").open(newline="") as f:
  for row in csv.DictReader(f):
   table.append((float(row["T_K"]),float(row["k_forward_cm3_s"]),float(row["k_reverse_cm3_s"])))
 if len(table)!=47 or table[0][0]!=1 or table[-1][0]!=200000:
  raise ValueError("ORIGINAL_SAVIN_TABLE_LENGTH_OR_DOMAIN_DRIFT")
 if any(a>=b for (a,*_), (b,*_) in zip(table,table[1:])):
  raise ValueError("ORIGINAL_SAVIN_TABLE_UNSORTED")
 if any(a<=0 or b<=0 for _,a,b in table):
  raise ValueError("ORIGINAL_SAVIN_RATE_NONPOSITIVE")
 fits=json.loads((SOURCES/"SAVIN2002_ORIGINAL_TABLE2_FITS.json").read_text())
 if fits["source_html_sha256"]!=SHA["SAVIN2002_AR5IV_ORIGINAL_HTML.html"]:
  raise ValueError("PRIMARY_PUBLISHED_HTML_RATE_IDENTITY_DRIFT")
 if fits["DOI"]!="10.1086/324218" or fits["forward_endothermic_threshold_meV"]!=3.7:
  raise ValueError("CHEMICAL_SOURCE_ENERGY_AUTHORITY_DRIFT")
 return table,fits


def interp_published(table,T,axis):
 """Explicit logT-log(alpha) interpolation of ORIGINAL printed Table 1.

 This is the author's printed rounded RATE TABLE plus declared interpolation,
 not an exact unpublished author spline or a formally certified rate.
 """
 if not (RATES_VALID[0]<=T<=RATES_VALID[1]) or not math.isfinite(T):
  raise ValueError("SAVIN_T_OUTSIDE_FIT_QUALIFIED_DOMAIN")
 xs=[row[0] for row in table]
 i=bisect.bisect_right(xs,T)-1
 i=max(0,min(i,len(xs)-2))
 t0,t1=xs[i],xs[i+1]
 y0,y1=table[i][axis],table[i+1][axis]
 s=math.log(T/t0)/math.log(t1/t0)
 return math.exp(math.log(y0)*(1-s)+math.log(y1)*s)


def alpha_fit(f,T):
 if not (RATES_VALID[0]<=T<=RATES_VALID[1]) or not math.isfinite(T):
  raise ValueError("SAVIN_FIT_T_OUT_OF_RANGE")
 v=f["a"]*(T**f["b"])*math.exp(-f["c"]/T)+f["d"]*T**f["e"]
 if not math.isfinite(v) or v<=0:raise ValueError("PUBLISHED_FIT_NEGATIVE_OR_NONFINITE")
 return v


def exposure_coeff(kf,kb,x):
 """Per proper n_H, rate d y_D+/dt /n_H = kf*x*(1-y) - kb*(1-x)*y."""
 if not (0<=x<=1 and kf>0 and kb>0):
  raise ValueError("invalid H+ and Savin coefficient")
 a=kf*x
 b=kb*(1-x)
 return a,b


def stationary(kf,kb,x):
 a,b=exposure_coeff(kf,kb,x)
 if a+b<=0:raise ValueError("zero source charge exchange rate")
 y=a/(a+b)
 # D I/H I for equal-volume co-spatial gas, divided by total D/H.
 ratio=kb/(a+b)
 return y,1-y,ratio,a+b


def charge_conserving_eq(kf,kb,x,eta,y0):
 """Finite-tracer equilibrium under *only* CX at fixed total ion count.

 xH + eta*yD == x + eta*y0. H and D nuclei separately conserved.
 Enforces 0<=xH,yD<=1 via monotone root, no proper clock or n_H used.
 """
 if not (0<=x<=1 and 0<eta<1 and 0<=y0<=1):raise ValueError("invalid conserved CX inputs")
 total=x+eta*y0
 lo=max(0,(total-1)/eta)
 hi=min(1,total/eta)
 # exact finite xH representation is noisy near the endpoints in IEEE754,
 # hence use rate positivity and a bounded monotone physical interval.
 def net(y):
  xh=total-eta*y
  return kf*(1-y)*xh-kb*y*(1-xh)
 flo,fhi=net(lo),net(hi)
 if flo<-3e-25 or fhi>3e-25:
  raise ArithmeticError("COUPLED_CX_STATIONARY_ROOT_NOT_BRACKETED")
 for j in range(70):
  mid=(lo+hi)/2
  if net(mid)>0:lo=mid
  else:hi=mid
 y=(lo+hi)/2
 xh=total-eta*y
 if not(-1e-12<=xh<=1+1e-12 and -1e-12<=y<=1+1e-12):
  raise ArithmeticError("NONPHYSICAL_COUPLED_CX_ROOT")
 return y,xh


def energy_per_H_from_CX(y0,y1,eta=ETA_D):
 """Forward D0+H+ -> D++H consumes 3.7meV per forward net exchange."""
 return -eta*DELTA_E_ERG*(y1-y0)


def within(value,lo,hi,rel=5e-14):
 e=rel*max(abs(lo),abs(hi),abs(value),1e-30)
 return lo-e<=value<=hi+e


def quantiles(xs):
 s=sorted(xs)
 def get(p):
  t=p*(len(s)-1);j=int(t);u=t-j
  return (1-u)*s[j]+u*s[min(j+1,len(s)-1)]
 return {"min":s[0],"p05":get(.05),"median":get(.5),"p95":get(.95),"max":s[-1]}


def run(output:Path):
 table,fits=require_sources()
 output.mkdir(parents=True,exist_ok=True)
 prev=SOURCES/"ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz"
 ene=SOURCES/"REI_F05_ORIGINAL26_NATIVE_DISCRETE_ENERGY_46080.csv.gz"
 physical=output/"R51_REI_F05_SAVIN_H_D_CX_46080.csv.gz"
 count=0
 vals={key:[] for key in (
  "T160","T161","x160","x161",
  "Q_DIratio160","Q_DIratio161","delta_Q_DIratio",
  "eq_Dplus160","eq_Dplus161","delta_eq_Dplus",
  "ratetab160","ratefit160","ratio_disagreement",
  "CXenergy_capacity_ratio",
  "CXheat_pure_Dneutral_ratio",
  "CXheat_pure_Dplus_ratio",
  "gennorm160","gennorm161",
  "charge_corr_neutral","charge_corr_ionized",
 )}
 counts=dict(source_table_T_in_range=0,fit_direction_order_conflicts=0,table_direction_order_conflicts=0,
             input_parent_center_outside_preview_box=0,original_preview_rei_state_status_invalid=0,
             potential_CX_energy_ceiling_exceeds_1pct_f05_thermal=0,
             cx_neutral_bias_over_one_pct=0,exact_cx_charge_conservation_fail=0)
 sums={"original_total_H_nuclei_N":0.0,"assumed_total_D_nuclei_N":0.0,
       "CX_stationary_Dneutral_N160":0.0,"CX_stationary_Dneutral_N161":0.0}
 max_order_error=0.0; max_balance_res=0.
 with gzip.open(prev,"rt",newline="") as fa,gzip.open(ene,"rt",newline="") as fb:
  ra=csv.DictReader(fa);rb=csv.DictReader(fb)
  with physical.open("wb") as raw:
   with gzip.GzipFile(fileobj=raw,mode="wb",filename="",mtime=0,compresslevel=6) as gz:
    with io.TextIOWrapper(gz,encoding="utf-8",newline="") as txt:
     wr=csv.DictWriter(txt,fieldnames=FIELDS,lineterminator="\n")
     wr.writeheader()
     for A,B in zip(ra,rb):
      node=int(A["node"])
      if node!=count or int(B["node"])!=node:raise ValueError("REI_ORIGINAL_NODE_ALIGNMENT_FAILURE")
      T0=float(B["parent_T_center_K"]);x0=float(B["parent_xHII_center"])
      T1=0.5*(float(A["tick161_preview_Tgas_K_lower"])+float(A["tick161_preview_Tgas_K_upper"]))
      x1=0.5*(float(A["tick161_preview_xHII_lower"])+float(A["tick161_preview_xHII_upper"]))
      if not (within(T0,float(A["tick160_Tgas_K_lower"]),float(A["tick160_Tgas_K_upper"]))
              and within(x0,float(A["tick160_xHII_lower"]),float(A["tick160_xHII_upper"]))):
       counts["input_parent_center_outside_preview_box"]+=1
       raise ValueError("REI_SOURCE_PARENT_T_OR_XHII_PROVENANCE_DISAGREEMENT")
      if not (RATES_VALID[0]<=T0<=RATES_VALID[1] and RATES_VALID[0]<=T1<=RATES_VALID[1]
              and 0<x0<1 and 0<x1<1):raise ValueError("INVALID_ORIGINAL_HHE_SOURCE_DOMAIN")
      count+=1
      a0=interp_published(table,T0,1);b0=interp_published(table,T0,2)
      a1=interp_published(table,T1,1);b1=interp_published(table,T1,2)
      ka0=alpha_fit(fits["forward_a1"],T0);kb0=alpha_fit(fits["reverse_a2"],T0)
      ka1=alpha_fit(fits["forward_a1"],T1);kb1=alpha_fit(fits["reverse_a2"],T1)
      y0,d0,r0,lam0=stationary(a0,b0,x0)
      y1,d1,r1,lam1=stationary(a1,b1,x1)
      af,bf=exposure_coeff(a0,b0,x0);acf,bcf=exposure_coeff(a1,b1,x1)
      yn0,xhn0=charge_conserving_eq(a0,b0,x0,ETA_D,0)
      yi0,xhi0=charge_conserving_eq(a0,b0,x0,ETA_D,1)
      c0=(xhn0-x0)+ETA_D*(yn0-0)
      c1=(xhi0-x0)+ETA_D*(yi0-1)
      max_balance_res=max(max_balance_res,abs(c0),abs(c1))
      if abs(c0)>4e-16 or abs(c1)>4e-16:counts["exact_cx_charge_conservation_fail"]+=1
      totalH=float(A["source_H_nuclei_N_lower"])
      top=float(A["source_H_nuclei_N_upper"])
      if totalH<=0 or top<totalH:raise ValueError("REI_H_SOURCE_NUCLEI_INVALID")
      original_energy=float(B["thermal_energy_gain_twohalf_center_erg_per_H"])
      if original_energy==0:raise ValueError("REI_SOURCE_NATIVE_THERMAL_GAIN_ZERO")
      energycap=ETA_D*DELTA_E_ERG
      cap_ratio=energycap/abs(original_energy)
      heat_neutral=energy_per_H_from_CX(0,yn0)
      heat_ionized=energy_per_H_from_CX(1,yi0)
      rat0=a0/b0;rat1=a1/b1;fit0=ka0/kb0;fit1=ka1/kb1
      row={
       "node":node,"original_H_nuclei_N":totalH,
       "original_T160_K":T0,"original_xHII160":x0,
       "preview_T161_K":T1,"preview_xHII161":x1,
       "k_forward160_cm3_s":a0,"k_reverse160_cm3_s":b0,
       "k_forward161_cm3_s":a1,"k_reverse161_cm3_s":b1,
       "generator_forward160_per_nH_cm3_s":af,"generator_reverse160_per_nH_cm3_s":bf,
       "generator_forward161_per_nH_cm3_s":acf,"generator_reverse161_per_nH_cm3_s":bcf,
       "CX_equilibrium_Dplus160":y0,"CX_equilibrium_Dplus161":y1,
       "CX_equilibrium_Dneutral160":d0,"CX_equilibrium_Dneutral161":d1,
       "CX_Dneutral_over_Hneutral160":r0,"CX_Dneutral_over_Hneutral161":r1,
       "CX_Dneutral_over_Hneutral_response_161_minus_160":r1-r0,
       "CX_equilibrium_Dplus_response_161_minus_160":y1-y0,
       "CX_stationary_relaxation_per_nH160_cm3_s":lam0,
       "CX_stationary_relaxation_per_nH161_cm3_s":lam1,
       "Savin_fit_ratio160":fit0,"Savin_table_ratio160":rat0,
       "Savin_fit_ratio161":fit1,"Savin_table_ratio161":rat1,
       "fit_table_ratio_difference160":fit0-rat0,
       "fit_table_ratio_difference161":fit1-rat1,
       "CX_conserving_Dplus_eq160_initial_Dneutral":yn0,
       "CX_conserving_Hplus_eq160_initial_Dneutral":xhn0,
       "CX_conserving_Dplus_eq160_initial_Dplus":yi0,
       "CX_conserving_Hplus_eq160_initial_Dplus":xhi0,
       "CX_heat_initial_Dneutral_160_erg_per_H":heat_neutral,
       "CX_heat_initial_Dplus_160_erg_per_H":heat_ionized,
       "CX_absolute_energy_ceiling_erg_per_H":energycap,
       "original_F05_native_thermal_gain_erg_per_H":original_energy,
       "CX_energy_ceiling_over_F05_abs_thermal_gain":cap_ratio,
       "CX_global_Dnuclei_N_assumed":ETA_D*totalH,
       "CX_charge_conservation_residual_initial_Dneutral":c0,
       "CX_charge_conservation_residual_initial_Dplus":c1
      }
      for key in ("T160","T161","x160","x161"):
       vals[key].append({"T160":T0,"T161":T1,"x160":x0,"x161":x1}[key])
      for key,value in {
       "Q_DIratio160":r0,"Q_DIratio161":r1,"delta_Q_DIratio":r1-r0,
       "eq_Dplus160":y0,"eq_Dplus161":y1,"delta_eq_Dplus":y1-y0,
       "ratetab160":rat0,"ratefit160":fit0,"ratio_disagreement":fit0-rat0,
       "CXenergy_capacity_ratio":cap_ratio,
       "CXheat_pure_Dneutral_ratio":abs(heat_neutral/original_energy),
       "CXheat_pure_Dplus_ratio":abs(heat_ionized/original_energy),
       "gennorm160":lam0,"gennorm161":lam1,
       "charge_corr_neutral":abs(xhn0-x0),"charge_corr_ionized":abs(xhi0-x0)
      }.items(): vals[key].append(value)
      sums["original_total_H_nuclei_N"]+=totalH
      sums["assumed_total_D_nuclei_N"]+=ETA_D*totalH
      sums["CX_stationary_Dneutral_N160"]+=ETA_D*totalH*d0
      sums["CX_stationary_Dneutral_N161"]+=ETA_D*totalH*d1
      counts["source_table_T_in_range"]+=1
      if a0>b0:counts["table_direction_order_conflicts"]+=1
      if ka0>kb0:counts["fit_direction_order_conflicts"]+=1
      if cap_ratio>.01:counts["potential_CX_energy_ceiling_exceeds_1pct_f05_thermal"]+=1
      if abs(r0-1)>.01:counts["cx_neutral_bias_over_one_pct"]+=1
      wr.writerow({k:format(v,".17g") if isinstance(v,float) else v for k,v in row.items()})
 if count!=NODES:raise ValueError("ORIGINAL_NODE_COUNT_DRIFT")
 if any(v for k,v in counts.items() if k in ("input_parent_center_outside_preview_box",
        "exact_cx_charge_conservation_fail","original_preview_rei_state_status_invalid")):
  raise ArithmeticError("SOURCE_CHEMICAL_CHARGE_CONSERVATION_OR_PROVENANCE_FAIL")
 result={
  "schema":"WU_R51_REI_F05_SAVIN_D_H_CHARGE_EXCHANGE_REAL_SOURCE_V1",
  "science_status":"SOURCE_CONDITIONAL_CX_OPERATOR_AND_STATIONARY_RESPONSE_NOT_NEW_REI_IVP",
  "source_identity":SHA,
  "source_original_REI_tar_sha256":SOURCE_REI_TAR,
  "source_original_tick160_array_sha256":SOURCE_ACCEPTED_PARENT_STATE,
  "source_REI_preview_PR":352,"source_REI_head":REI_PR352_HEAD,
  "wu_parent_PR":189,"wu_parent_head":WU_PARENT_PR189_HEAD,
  "number_original_source_cells":NODES,
  "source_T_domain_K":RATES_VALID,
  "source_Savin_DOI":"10.1086/324218",
  "rate_interpolation":"LOGLOG_INTERPOLATION_OF_AUTHOR_PUBLISHED_3SIGFIG_TABLE1",
  "fitted_rates":"PUBLISHED_INDEPENDENT_TABLE2_FITS_COMPARISON_ONLY",
  "assumed_D_over_H":ETA_D,
  "reaction_energy_meV":3.7,
  "reaction_energy_erg":DELTA_E_ERG,
  "energy_transfer_max_per_H_erg":ETA_D*DELTA_E_ERG,
  "physical_source_state":{"tick160":"OFFICIAL_ACCEPTED","tick161":"UNAPPROVED_PREVIEW_ONLY"},
  "modeled_CX_scope":{"D_H_NUCLEI_CONSERVED":True,"H_D_ION_SUM_CONSERVED":True,
                       "CX_GENERATED_FREE_ELECTRON_CHANGE":"ZERO_AT_EXACT_H+D_CHARGE_CONSERVATION",
                       "NO_D_PHOTOIONIZATION":True,"NO_D_RECOMBINATION":True,
                       "NO_HD":True,"NO_FULL_26EVENT_COUPLING":True,
                       "NO_PROPER_NH_DENSITY_OR_PRETENDED_TIME_INTEGRATION":True,
                       "FROZEN_SOURCE_TEMPERATURE_PER_ENDPOINT":True,
                       "QUASISTATIC_EQUILIBRIUM_NOT_PROVED":True,
                       "RATE_SOURCE_INTERPOLATION_NOT_PHYSICALLY_EXACT":True},
  "counters":counts,"global_assumed_sums_N":sums,
  "summary_quantiles":{k:quantiles(v) for k,v in vals.items()},
  "max_charge_bookkeeping_residual":max_balance_res,
  "files":{"full_physical_csv":physical.name,"full_sha256":sha(physical)},
  "DAG":{"WU":"34/49","REI_central":"28/88","REI_working":"33/88",
         "REI_fast":"4/7","new_canonical_nodes":0,"original_F05_tick":"160/131072_HOLD"},
  "claim_gate":{"scientific_admission":"NOT_PROMOTED","PRODUCTION":"HOLD",
                "NO_MAIN_MERGE":True,"AUTO_NEXT_NODE":False,
                "NO_RATE_TIMES_COUNT_AS_DENSITY":True,
                "SAME_AUTHOR_R6_C9":"PENDING"}
 }
 (output/"R51_RESULTS.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 summary=output/"R51_SOURCE_PHYSICS_SUMMARY.json"
 summary.write_text(json.dumps({
  "schema":result["schema"],"count":count,
  "source_original_REI_tar_sha256":SOURCE_REI_TAR,
  "source_REI_head":REI_PR352_HEAD,
  "source_Savin_DOI":"10.1086/324218","assumed_D_over_H":ETA_D,
  "reaction_energy_meV":3.7,
  "selected_statistics":{k:result["summary_quantiles"][k] for k in (
   "Q_DIratio160","Q_DIratio161","delta_Q_DIratio","CXenergy_capacity_ratio",
   "CXheat_pure_Dneutral_ratio","CXheat_pure_Dplus_ratio","ratefit160","ratetab160","ratio_disagreement")},
  "source_counter":counts,
  "DAG":result["DAG"],
  "full_science_sha256":sha(physical)
 },indent=2,sort_keys=True)+"\n")
 print(json.dumps({"source_nodes":count,"counts":counts,
     "median_DI_HI_bias":result["summary_quantiles"]["Q_DIratio160"]["median"]-1,
     "maximum_exchange_energy_over_native":result["summary_quantiles"]["CXenergy_capacity_ratio"]["max"],
     "median_exchange_energy_over_native":result["summary_quantiles"]["CXenergy_capacity_ratio"]["median"],
     "table_to_fit_ratio_difference_median":result["summary_quantiles"]["ratio_disagreement"]["median"],
     "full_sha256":result["files"]["full_sha256"],
     "canonical_DAG":result["DAG"]},sort_keys=True))
 return result


if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser()
 p.add_argument("--out",type=Path,default=ROOT/"results")
 args=p.parse_args()
 run(args.out)
