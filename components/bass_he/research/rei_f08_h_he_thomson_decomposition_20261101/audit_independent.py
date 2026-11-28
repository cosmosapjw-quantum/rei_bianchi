#!/usr/bin/env python3
"""Separate raw-source quadrature referee: does not import science.py."""
import bisect,csv,gzip,hashlib,json,math,statistics
from pathlib import Path
P=Path(__file__).resolve().parent
S=P/"source_inputs"
O=P/"results"
def rows(p):
 with gzip.open(p,"rt") as f:return list(csv.DictReader(f))
def integrate(t,y,e):
 i=min(max(bisect.bisect_right(t,e)-1,0),len(t)-2)
 yy=y[i]+(y[i+1]-y[i])*(e-t[i])/(t[i+1]-t[i])
 return math.fsum([.5*(yy+y[i+1])*(t[i+1]-e)]+
  [.5*(y[j]+y[j+1])*(t[j+1]-t[j]) for j in range(i+1,len(t)-1)])
def main():
 sc=json.loads((S/"science_scenario_v1.json").read_text())
 op=float(sc["constants"]["c_cm_s"])*6.6524587051e-25
 histories={}
 max_source=0.
 for label in ("BI","FLRW"):
  d=rows(S/("S0_"+label+"-electron_density.csv.gz"))
  c=rows(S/("S0_"+label+"-curve.csv.gz"))
  x=[dict(time_s="0",x_HII=.9,x_HeII=.3,x_HeIII=.6)]+c
  t=[float(z["normal_time_s"]) for z in d]
  he=[float(q["nHe_proper_cm3"])*(float(a["x_HeII"])+2*float(a["x_HeIII"])) for a,q in zip(x,d)]
  h=[float(q["nH_proper_cm3"])*float(a["x_HII"]) for a,q in zip(x,d)]
  max_source=max(max_source,max(abs(float(q["ne_proper_cm3"])-(u+v)) for q,u,v in zip(d,h,he)))
  histories[label]=(t,h,he)
 actual=rows(S/"ORIGINAL_F08_S0_BIANCHI_THOMSON_SKY.csv.gz")
 new=rows(O/"ORIGINAL_F08_S0_H_HE_THOMSON_SKY_10752.csv.gz")
 if len(actual)!=10752 or len(new)!=10752:raise ValueError("original 10752 rays not matched")
 maximum=0.;num=0
 sampled=[0,1,63,127,128,511,512,639,1024,2047,2048,4095,4096,5376,6143,8191,9471,10751]
 for idx in sampled:
  a=actual[idx];r=new[idx]
  for species,j in (("H",1),("He",2)):
   for label,time in (("BI",float(a["emission_time_s"])),("FLRW",float(a["flrw_reference_emission_time_s"]))):
    t,h,he=histories[label]
    indep=op*integrate(t,(h,he)[j-1],time)
    got=float(r["tau_"+label+"_"+species])
    err=abs(indep-got)
    maximum=max(maximum,err)
    if err>1e-16:raise ValueError(f"independent trapezoid failed row {idx}: {label}/{species} {err}")
    num+=1
 maxall=0.
 for a,r in zip(actual,new):
  if any(a[k]!=r[k] for k in ("mu_bin","phi_bin","window_fraction","angular_nmu","angular_nphi")):
   raise ValueError("ray order drift")
  for typ,src in [("delta_tau_geometry","delta_tau_geometry_fixed_relative_z"),("delta_tau_material","delta_tau_material_fixed_time"),("tau_BI","tau_BI"),("tau_FLRW","tau_FLRW")]:
   recon=math.fsum([float(r[typ+"_H"]),float(r[typ+"_He"])])
   err=abs(recon-float(a[src]))
   maxall=max(maxall,err)
   if err>6e-18:raise ValueError("full original ray-level species closure failure")
 receipt={"schema":"BASS_HE_REI_F08_SEPARATE_FSUM_QUADRATURE_AUDIT_V1",
 "independent_script_does_not_import_primary_science":True,
 "raw_input_electron_identity_max_abs_cm3":max_source,
 "independent_raw_source_trapezoid_checks":num,
 "independent_sampled_tau_max_abs_error":maximum,
 "all_original_10752_ray_closure_max_abs":maxall,
 "scientific_admission":"SOURCE_CONDITIONAL_NOT_PRODUCTION"}
 (O/"INDEPENDENT_AUDIT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
 print(json.dumps(receipt,sort_keys=True))
if __name__=="__main__":main()
