#!/usr/bin/env python3
"""Source-locked REI tick160 energy materiality scale for optional WU HD consumer.
Derived model calculation, not source-native HD cooling or a REI IVP run."""
import argparse,csv,gzip,hashlib,json,math,pathlib,statistics
E_SHA="024e1d1bbef95d3e254b8c54b3d1134de54eebce7b82d082401c522f813637c5"
I_SHA="5c801190aac47da922efa7a89f5376bf54ec71191b44bbf9ee908bb5e1d59387"
W_BLOB="3ebcd64189bbeea7e1faa60576bb485e72c8f070"
EV_ERG=1.602176634e-12
D_FID=2.5e-5
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for x in iter(lambda:f.read(1<<20),b""):h.update(x)
 return h.hexdigest()
def blob(p):
 b=pathlib.Path(p).read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def rel(a,b):return abs(a-b)/max(abs(a),abs(b),1e-300)
def need(q,frac=.01,fmax=D_FID):
 if not (0<frac<=1 and fmax>0):raise ValueError("fraction and f_HD upper limit")
 return frac*abs(q)/fmax
def quant(v):
 s=sorted(v)
 def f(t):
  p=t*(len(s)-1);i=int(p);a=p-i
  return (1-a)*s[i]+a*s[min(i+1,len(s)-1)]
 return dict(min=s[0],p05=f(.05),median=f(.5),p95=f(.95),max=s[-1])
def run(energy,increment,witness,out):
 if sha(energy)!=E_SHA or sha(increment)!=I_SHA or blob(witness)!=W_BLOB:
  raise ValueError("protected original Git/source digest mismatch")
 out.mkdir(parents=True,exist_ok=True)
 path=out/"R49_REI_F05_HD_MATERIALITY_46080.csv"
 head=["node","T_K","xHII","joint_H_Hplus_T_center_only","photo_erg_per_H","nonphoto_sink_erg_per_H",
       "thermal_rhs_erg_per_H","thermal_energy_gain_erg_per_H","HD_1pct_required_erg_per_HD_DHfid",
       "HD_1pct_required_eV_per_HD_DHfid"]
 n=0;q_all=[];q_allowed=[];ledger=[0.,0.,0.];pcount=scount=negcount=0;state={}
 with gzip.open(energy,"rt",newline="") as ef,gzip.open(increment,"rt",newline="") as xf,open(path,"w",newline="") as fo:
  e_reader=csv.DictReader(ef);i_reader=csv.DictReader(xf);w=csv.writer(fo,lineterminator="\n");w.writerow(head)
  for e,i in zip(e_reader,i_reader):
   node=int(e["node"])
   if int(i["node"])!=node or node!=n:raise ValueError("node/grain mismatch")
   T=float(e["parent_T_center_K"]);x=float(e["parent_xHII_center"])
   photo=float(e["photo_total_full_center_erg_per_H"]);primary=float(e["photo_primary_full_center_erg_per_H"])
   ots=float(e["ots_resolved_full_center_erg_per_H"]);sink=float(e["nonphoto_sink_full_center_erg_per_H"])
   rhs=float(e["thermal_native_rhs_full_center_erg_per_H"]);gain=float(e["thermal_energy_gain_full_center_erg_per_H"])
   if not (math.isfinite(T) and T>0 and 0<=x<=1 and all(map(math.isfinite,[photo,primary,ots,sink,rhs,gain]))):
    raise ValueError("nonphysical source")
   ledger[0]=max(ledger[0],rel(photo,primary+ots))
   ledger[1]=max(ledger[1],rel(rhs,photo-sink))
   ledger[2]=max(ledger[2],rel(T,math.exp(float(i["source_tick160_parent_lnT_center"]))))
   window=(5<=T<=3005)
   q_all.append(abs(gain))
   if window:q_allowed.append(abs(gain))
   pcount+=photo>0;scount+=sink>0;negcount+=gain<0
   state[node]=(T,x,gain)
   req=need(gain)
   w.writerow([node,format(T,'.17g'),format(x,'.17g'),int(window),format(photo,'.17g'),
          format(sink,'.17g'),format(rhs,'.17g'),format(gain,'.17g'),format(req,'.17g'),format(req/EV_ERG,'.17g')])
   n+=1
  if next(e_reader,None) is not None or next(i_reader,None) is not None:raise ValueError("extra rows")
 if n!=46080 or max(ledger)>1e-12:raise ValueError("REI full parent/energy ledger failure")
 checks=[]
 with open(witness,newline="") as f:public=list(csv.DictReader(f))
 if len(public)!=5:raise ValueError("R48 witness count mismatch")
 for row in public:
  k=int(row["node"]);T,x,q=state[k]
  dT=rel(T,float(row["T_mid_K"]));dx=rel(x,float(row["xHII_mid"]))
  # Distinct REI source archives are not byte-identical. Record mismatch, never silently certify equality.
  checks.append(dict(node=k,upper=row["upper_original_level"],lower=row["lower_original_level"],T_K=T,
        xHII=x,relative_T_difference=dT,relative_xHII_difference=dx,
        cross_archive_rel_1eMinus11_gate_failed=max(dT,dx)>1e-11,
        R48_Hplus_over_H_collision_rate_ratio=float(row["ratio_mid"]),F05_thermal_gain_erg_per_H=q,
        HD_1percent_energy_requirement_erg_per_HD=need(q)))
 result=dict(status="SOURCE_CONDITIONAL_PHYSICAL_ENERGY_SCREEN_NOT_HD_COOLING",
  source=dict(REI_PR347_energy_sha256=E_SHA,REI_PR348_increment_sha256=I_SHA,WU_PR187_witness_git_blob=W_BLOB,
      REI_original_source_tar_reported_sha256="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b",
      WU_original_source_zip_reported_sha256="48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7",
      full_source_byte_or_numerical_equivalence="NOT_ESTABLISHED; 3 distinct witness nodes sampled; one with cross-archive T discrepancy"),
  experiment=dict(tick="160/131072",n=46080,center_T_joint_native_window_n=len(q_allowed),
      window_semantics="center-only. Does not certify whole original T enclosure or 19/52 closure",
      positive_photo=pcount,positive_sink=scount,negative_thermal_gain=negcount,
      max_relative_photo_split_residual=ledger[0],max_relative_native_rhs_residual=ledger[1],
      max_relative_two_REI_parent_T_residual=ledger[2],
      REI_thermal_gain_abs_erg_per_H=quant(q_all),in_WU_T_window_thermal_gain_abs_erg_per_H=quant(q_allowed),
      assumed_max_HD_per_H=D_FID,assumed_max_HD_is_not_REI_species_abundance=True,
      necessary_1pct_integrated_HD_energy_erg_per_HD=quant([need(q) for q in q_allowed]),
      necessary_1pct_integrated_HD_energy_eV_per_HD=quant([need(q)/EV_ERG for q in q_allowed]),
      WU_R48_five_witnesses=checks,
      WU_REI_cross_archive_max_T_relative_difference=max(z['relative_T_difference'] for z in checks),
      WU_REI_cross_archive_mismatch_count=sum(z['cross_archive_rel_1eMinus11_gate_failed'] for z in checks)),
  admitted=dict(WU="34/49",REI_central="28/88",REI_working="33/88",delta=0),
  blocked=dict(nHD=True,absolute_colliders_and_clock=True,full_HD52_Hplus=True,reactive_chemistry=True,
               signed_photon_current=True,native_Bianchi_observable=True,distinct_author_R6_C9=True),
  governance=dict(HH_R10="OFF",L4=False,PRODUCTION="HOLD",AUTO_NEXT_NODE=False,NO_MAIN_MERGE=True))
 (out/"R49_RESULTS.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 (out/"R49_WU_REI_WITNESS.json").write_text(json.dumps(checks,sort_keys=True,indent=2)+"\n")
 return result
if __name__=="__main__":
 a=argparse.ArgumentParser()
 for x in ("energy","increment","wu_witness","out"):a.add_argument("--"+x.replace("_","-"),required=True,type=pathlib.Path)
 p=a.parse_args()
 r=run(p.energy,p.increment,p.wu_witness,p.out)
 print(json.dumps(r["experiment"],indent=2))
