#!/usr/bin/env python3
"""BASS_HE: original REI 26-event F05 [160,161] H/He ionization-potential
storage increment on native 46080-cell nonauthoritative preview, no new IVP.
This is NOT radiated recombination emission, heat input or official admission.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math
from decimal import Decimal,localcontext
from pathlib import Path
HERE=Path(__file__).resolve().parent
S=HERE/"source_inputs"
ORIGINAL_STATE_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
ORIGINAL_TAR_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
PREVIEW_CSV_SHA="713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d"
INCREMENT_CSV_SHA="11df439390209bd48742ca9f4303c8743c9e14900289805e13d1ed489450a5dd"
N=46080
CHI_H=Decimal("13.598434599702")
CHI_HEI=Decimal("24.587389011")
CHI_HEII=Decimal("54.41776")
EV_ERG=Decimal("1.602176634e-12")
C={"H":CHI_H,"He_first":CHI_HEI,"He_second":CHI_HEII}
TWOHALF="original_twohalf_increment"
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def I(row,key):
 l=Decimal(row[key+"_lower"]);u=Decimal(row[key+"_upper"])
 if not (l.is_finite() and u.is_finite() and l<=u):
  raise ValueError("source interval invalid: "+key)
 return (l,u)
def plus(*args):
 return (sum((x[0] for x in args),Decimal(0)),
         sum((x[1] for x in args),Decimal(0)))
def mul(a,b):
 prod=[x*y for x in a for y in b]
 return (min(prod),max(prod))
def sc(a,c):
 if c>=0:return (a[0]*c,a[1]*c)
 return (a[1]*c,a[0]*c)
def conservative(x,upper):
 f=float(x)
 if not math.isfinite(f):raise OverflowError("result cannot be serialized as f64")
 f=math.nextafter(f,math.inf if upper else -math.inf)
 return format(f,".17g")
def pin():
 physical=S/"ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz"
 increment=S/"REI_ORIGINAL26_COMMON_PARENT_INCREMENT_46080.csv.gz"
 if sha(physical)!=PREVIEW_CSV_SHA or sha(increment)!=INCREMENT_CSV_SHA:
  raise ValueError("immutable original REI input mismatch")
 pr=json.loads((S/"REI352_PREVIEW_RESULT.json").read_text())
 old=json.loads((S/"REI350_ORIGINAL_INCREMENT_RESULT.json").read_text())
 if not (pr["physical_csv_sha256"]==PREVIEW_CSV_SHA and
     pr["original_accepted_state_array_sha256"]==ORIGINAL_STATE_SHA and
     pr["original_source_tar_sha256"]==ORIGINAL_TAR_SHA and
     pr["official_state_161"]=="NOT_ACCEPTED_OR_WRITTEN" and
     pr["original_tick"]=="160/131072" and pr["source_original_14_ledger_pass"] and
     old["csv_sha256"]==INCREMENT_CSV_SHA and
     old["original_state_array_sha256"]==ORIGINAL_STATE_SHA and
     old["original_local_error_gate"]==2e-4 and
     old["original_native_table_event_pass"] and
     old["original_set_ledgers"]["evaluated_ledgers"]==14 and
     old["original_set_ledgers"]["passed"]):
  raise ValueError("original first interval authority/source policy mismatch")
 return physical,increment,pr,old
def atom(row_inc,row_phys):
 nh=I(row_phys,"source_H_nuclei_N")
 nehe=I(row_phys,"source_He_nuclei_N")
 if nh[0]<=0 or nehe[0]<=0:raise ValueError("nonpositive original nuclei")
 # F05 owns He/H = 0.079; neither F08 0.083 nor any P19 substitution.
 if not Decimal("0.0789999999998")<nehe[0]/nh[0]<Decimal("0.0790000000002"):
  raise ValueError("original F05 He/H source clock or nuclei drift")
 dH=I(row_inc,"x_HII_"+TWOHALF)
 dA=I(row_inc,"x_HeII_"+TWOHALF)
 dB=I(row_inc,"x_HeIII_"+TWOHALF)
 # Ionization potential stored relative to neutral H+He ground.
 H=sc(mul(nh,dH),CHI_H*EV_ERG)
 He_first=sc(mul(nehe,plus(dA,dB)),CHI_HEI*EV_ERG)
 He_second=sc(mul(nehe,dB),CHI_HEII*EV_ERG)
 He=plus(He_first,He_second)
 total=plus(H,He)
 electron=plus(mul(nh,dH),mul(nehe,plus(dA,sc(dB,Decimal(2)))))
 # Original half1+half2 charge count must be enclosed by PREVIEW result.
 official=I(row_phys,"tick160_to_161_delta_electron_N")
 if electron[0]>official[1] or electron[1]<official[0]:
  raise ValueError("candidate electron source inconsistency")
 xH=I(row_phys,"tick161_preview_xHII")
 xA=I(row_phys,"tick161_preview_xHeII")
 xB=I(row_phys,"tick161_preview_xHeIII")
 B161=plus(sc(mul(nh,xH),CHI_H*EV_ERG),
  sc(mul(nehe,plus(sc(xA,CHI_HEI),sc(xB,CHI_HEI+CHI_HEII))),EV_ERG))
 U161=I(row_phys,"tick161_preview_U_erg")
 if U161[0]<=0 or B161[0]<=0:raise ValueError("unphysical energy scale")
 perH=sc(mul(total,(Decimal(1)/nh[1],Decimal(1)/nh[0])),Decimal(1)/EV_ERG)
 return {"dB_H":H,"dB_He_first":He_first,"dB_He_second":He_second,
         "dB_He":He,"dB_total":total,"dNe":electron,
         "dB_total_eV_per_H":perH,"B161":B161,"U161":U161}
def run(out):
 with localcontext() as ctx:
  ctx.prec=90
  physical,increment,pr,old=pin()
  out=Path(out);out.mkdir(parents=True,exist_ok=True)
  file=out/"ORIGINAL_REI_F05_TICK161_H_HE_LATENT_ENERGY_46080.csv.gz"
  vals=("dB_H","dB_He_first","dB_He_second","dB_He","dB_total",
        "dNe","dB_total_eV_per_H","B161","U161")
  totals={k:[Decimal(0),Decimal(0)] for k in vals if k!="dB_total_eV_per_H"}
  row_per_H_range=[None,None]
  counts={k:0 for k in ("H_certain_decrease","He_certain_decrease",
    "He_certain_increase","total_certain_decrease","total_certain_increase",
    "total_contains_zero","net_He_increase_while_H_decrease")}
  n=0
  with gzip.open(physical,"rt",newline="") as fp,gzip.open(increment,"rt",newline="") as fi:
   rp=csv.DictReader(fp);ri=csv.DictReader(fi)
   if len(rp.fieldnames or [])!=27 or len(ri.fieldnames or [])!=30:
    raise ValueError("original two native F05 data schema changed")
   with file.open("wb") as fout:
    with gzip.GzipFile(fileobj=fout,filename="",mode="wb",mtime=0,compresslevel=6) as gz:
     with io.TextIOWrapper(gz,encoding="utf8",newline="") as txt:
      names=["node"]+[k+"_"+side for k in vals for side in ("lower","upper")]
      writer=csv.DictWriter(txt,fieldnames=names,lineterminator="\n")
      writer.writeheader()
      for b,a in zip(rp,ri):
       if int(a["node"])!=n or int(b["node"])!=n:raise ValueError("source row identity changed")
       x=atom(a,b)
       outrow={"node":n}
       for k,iv in x.items():
        if k in totals:
         totals[k][0]+=iv[0];totals[k][1]+=iv[1]
        else:
         row_per_H_range[0]=iv[0] if row_per_H_range[0] is None else min(row_per_H_range[0],iv[0])
         row_per_H_range[1]=iv[1] if row_per_H_range[1] is None else max(row_per_H_range[1],iv[1])
        outrow[k+"_lower"]=conservative(iv[0],False)
        outrow[k+"_upper"]=conservative(iv[1],True)
       writer.writerow(outrow)
       counts["H_certain_decrease"]+=int(x["dB_H"][1]<0)
       counts["He_certain_decrease"]+=int(x["dB_He"][1]<0)
       counts["He_certain_increase"]+=int(x["dB_He"][0]>0)
       counts["total_certain_decrease"]+=int(x["dB_total"][1]<0)
       counts["total_certain_increase"]+=int(x["dB_total"][0]>0)
       counts["total_contains_zero"]+=int(x["dB_total"][0]<=0<=x["dB_total"][1])
       counts["net_He_increase_while_H_decrease"]+=int(x["dB_He"][0]>0 and x["dB_H"][1]<0)
       n+=1
  if n!=N:raise ValueError("expected original 46080 cells, received "+str(n))
  h,he,allB=totals["dB_H"],totals["dB_He"],totals["dB_total"]
  if not(allB[1]<0 and he[1]<0 and h[1]<0):
   raise ValueError("original source global ionization potential did not decline")
  # Share of a signed decrease with positive numerator and denominator.
  he_share=(he[1]/allB[0],he[0]/allB[1])
  if not (Decimal(0)<=he_share[0]<=he_share[1]<=Decimal(1)):
   raise ValueError("invalid helium fraction of latent-energy change")
  # Compare the changed potential-energy reservoir to actual original gas
  # thermal ENERGY scale; NOT an equation asserting that latent energy heats gas.
  gas=totals["U161"]
  material=(abs(allB[1])/gas[1],abs(allB[0])/gas[0])
  original_DNe=pr["observables"]
  if not (totals["dNe"][0]<=Decimal(str(original_DNe["delta_electron_N_total_upper"]))
          and totals["dNe"][1]>=Decimal(str(original_DNe["delta_electron_N_total_lower"]))):
   raise ValueError("original global REI electron increment overlap lost")
  result={"schema":"BASS_HE_REI_F05_46080_H_HE_TICK161_IONIZATION_POTENTIAL_V1",
     "original_owner":"cosmosapjw-quantum/rei_bianchi PR352",
     "original_owner_head":"ea8d6bf94197392c69f939f03c1673ed3afe349c",
     "original_increment_source":"PR350 M-matrix native full/half/half",
     "state_sha256":ORIGINAL_STATE_SHA,"original_source_tar_sha256":ORIGINAL_TAR_SHA,
     "source_preview_csv_sha256":PREVIEW_CSV_SHA,"source_increment_csv_sha256":INCREMENT_CSV_SHA,
     "binding_thresholds_eV":{"HI":str(CHI_H),"HeI":str(CHI_HEI),"HeII":str(CHI_HEII)},
     "electronvolt_to_erg":str(EV_ERG),
     "math":"dB_H=E_H*dNHII; dB_He=E_HeI*(dNHeII+dNHeIII)+E_HeII*dNHeIII; signed ionization-potential storage",
     "source_scenario":"original 26-event real F05 46k first canonical interval tick160 to candidate tick161, z=5.95, He/H=.079",
     "sampled_original_physical_cells":n,
     "counts":counts,
     "global_intervals":{k:{"lower":float(v[0]),"upper":float(v[1]),
       "unit":"electrons" if k=="dNe" else "erg"} for k,v in totals.items()},
     "per_cell_eV_per_H_extrema":{"lower":float(row_per_H_range[0]),"upper":float(row_per_H_range[1])},
     "helium_share_of_global_ionization_storage_decline":{"lower":float(he_share[0]),"upper":float(he_share[1])},
     "global_ionization_change_abs_over_candidate_gas_U":{"lower":float(material[0]),"upper":float(material[1])},
     "output_sha256":sha(file),
     "provenance_scope":"source-native discrete-state preview; no actual recombination-photon emission/heat deposition inference",
     "first_original_tick":"160/131072_NOT_ADVANCED",
     "official_tick161":"NOT_ACCEPTED",
     "source_three_lanes_one_physical_dataset":True,
     "status":"SCOPED_SOURCE_AUTHENTIC_DERIVED_NUMERICALLY_CHECKED",
     "new_cosmological_IVPs":0,"new_observed_datasets":0,
     "central_rei":"28/88_REPORTED","working":"33/88_REPORTED",
     "fast":"4/7_REPORTED","BASS_HE":"14/18_REPORTED",
     "canonical_delta":0,"production":"HOLD","auto_next":False}
  (out/"RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
  print(json.dumps({"rows":n,"output_sha256":result["output_sha256"],
    "counts":counts,"global_intervals":result["global_intervals"],
    "helium_share":result["helium_share_of_global_ionization_storage_decline"],
    "binding_to_U":result["global_ionization_change_abs_over_candidate_gas_U"]},sort_keys=True))
  return result
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--out",required=True,type=Path)
 args=ap.parse_args();run(args.out)
