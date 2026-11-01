#!/usr/bin/env python3
"""Original F05 12-site global-photon exact curvature, source-conditional only.

Consume PR337 original MPRK22/SDIRK2 12-site SOURCE output (not another IVP).
The same-clock variation of global photon denominators holds local source
numerators/forcing fixed: it is NOT a full 26-event D_h(X,theta) certificate.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,io,json,math,zipfile
from collections import defaultdict
from pathlib import Path
import numpy as np

N=46080; SITES=12; GROUPS=4; SPECIES=("HI","HeI","HeII")
ORIGINAL_TAR_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab9999e7e3508a5161edb01"
STAGE_CSV_SHA="acb3fa92d081aeb372ef5194b9c12a063604673916397c22fd26936072b4d0e2"
ORIGINAL_ARTIFACT_SHA="41105018944d7b7bab3a7be84741cb47aeb3758aac1aff1fe44bb925fdb04d73"

def get_data(source):
    source=Path(source)
    if source.is_file() and source.suffix==".zip":
        if hashlib.sha256(source.read_bytes()).hexdigest()!=ORIGINAL_ARTIFACT_SHA:
            raise ValueError("original PR337 immutable ZIP SHA256 mismatch")
        with zipfile.ZipFile(source) as z:
            if z.testzip() is not None:raise ValueError("original GitHub Actions ZIP CRC failure")
            info=json.loads(z.read("RESULT.json"))
            bits=z.read("ORIGINAL_26EVENT_ACTUAL_STAGE_PHOTON_FEEDBACK_552960.csv.gz")
    else:
        info=json.loads((source/"RESULT.json").read_text())
        bits=(source/"ORIGINAL_26EVENT_ACTUAL_STAGE_PHOTON_FEEDBACK_552960.csv.gz").read_bytes()
    if info["source_array_sha256"]!=STATE_SHA or info["original_source_sha256"]!=ORIGINAL_TAR_SHA:
        raise ValueError("original physical source owner mismatch")
    if info["original_stage_physics_rows"]!=N*SITES or len(info["source_group_rows"])!=SITES*GROUPS:
        raise ValueError("original 12-site×4-group cardinality mismatch")
    if hashlib.sha256(bits).hexdigest()!=STAGE_CSV_SHA:
        raise ValueError("original source 552960 rows SHA256 mismatch")
    return info,bits

def derive_group(info):
    rows=info["source_group_rows"]
    ref=np.asarray(next(a for a in rows if a["map_step"]=="full" and a["site"]=="parent" and a["group"]==0)["original_global_neutral_moments"])
    grouped=defaultdict(list);new=[]
    for a in rows:
        name=(a["map_step"],a["site"])
        ratio=np.asarray(a["original_global_neutral_moments"],float)/ref
        psite=np.asarray(a["absorber_fractions"],float)
        external=float(a["external_fraction"])
        if np.any(ratio<=0) or np.any(psite<0) or external<0:raise ValueError("nonpositive original photon source")
        Dref_over_Dsite=float(external+np.sum(psite/ratio))
        if Dref_over_Dsite<=0:raise ValueError("denominator sign violation")
        r=1/Dref_over_Dsite-1
        pref=psite/ratio/Dref_over_Dsite
        linear=pref*(ratio-1-r)
        rem=-r*linear/(1+r)
        residual=float(np.max(np.abs(psite-pref-linear-rem)))
        if residual>8e-16:raise ValueError("exact original photon fraction identity")
        group=dict(map_step=name[0],site=name[1],group=int(a["group"]),
          time_s=float(a["source_time_s"]),redshift=float(a["redshift"]),
          r_global_denominator=float(r),
          source_fraction_R_HI=float(rem[0]),source_fraction_R_HeI=float(rem[1]),
          source_fraction_R_HeII=float(rem[2]),
          max_abs_fraction_R=float(np.max(abs(rem))),
          original_group_heat_erg_s=float(a["photon_heat_erg_per_s"]),
          exact_denominator_only_photoheat_R_erg_s=float(a["photon_heat_erg_per_s"]*r*r),
          fraction_identity_residual=residual)
        new.append(group);grouped[name].append((a,group))
    if len(grouped)!=SITES or any(len(z)!=GROUPS for z in grouped.values()):
        raise ValueError("original 12-site structure")
    return grouped,new

def per_site_coeff(group):
    rates=np.zeros((GROUPS,3));rv=np.zeros(GROUPS)
    for a,v in group:
        rates[a["group"]]=a["source_photons_per_s"]
        rv[a["group"]]=v["r_global_denominator"]**2
    total=rates.sum(axis=0)
    weights=np.divide(rates,total[None,:],out=np.zeros_like(rates),where=total[None,:]>0)
    return (weights*rv[:,None]).sum(axis=0),float(np.max(rv))

def run(source,outdir):
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    info,bits=get_data(source);grouped,groups=derive_group(info)
    factors={key:per_site_coeff(gr) for key,gr in grouped.items()}
    fields=["node","map_step","site","time_s","xHII","xHeII","T_K",
      "original_photo_e_rate_per_H_s","global_denominator_e_source_R_per_H_s",
      "original_photoheat_erg_per_H_s","global_denominator_photoheat_R_upper_erg_per_H_s"]
    outpath=outdir/"ORIGINAL_F05_12_SITES_GLOBAL_PHOTON_R_552960.csv.gz"
    med=defaultdict(list);allcount=0
    with gzip.open(io.BytesIO(bits),mode="rt",newline="") as stream:
        with outpath.open("wb") as f:
            with gzip.GzipFile(fileobj=f,mode="wb",filename="",mtime=0,compresslevel=6) as gz:
                with io.TextIOWrapper(gz,encoding="utf-8",newline="") as writer_file:
                    writer=csv.DictWriter(writer_file,fieldnames=fields);writer.writeheader()
                    for line in csv.DictReader(stream):
                        name=(line["map_step"],line["source_site"])
                        if name not in factors:raise ValueError("original source site not indexed")
                        weights,max_r2=factors[name]
                        rate=np.asarray([float(line["photo_"+s+"_events_per_H_s"]) for s in SPECIES])
                        heat=float(line["primary_photoheat_erg_per_H_s"])
                        e=float(np.dot(rate,weights));heating=heat*max_r2
                        if min(e,heating)<0 or not math.isfinite(e+heating):raise ValueError("original nonnegative source curvature")
                        row=dict(node=line["node"],map_step=name[0],site=name[1],
                          time_s=line["source_time_s"],xHII=line["x_HII"],xHeII=line["x_HeII"],T_K=line["T_K"],
                          original_photo_e_rate_per_H_s=format(float(np.sum(rate)),".17g"),
                          global_denominator_e_source_R_per_H_s=format(e,".17g"),
                          original_photoheat_erg_per_H_s=format(heat,".17g"),
                          global_denominator_photoheat_R_upper_erg_per_H_s=format(heating,".17g"))
                        writer.writerow(row);med[name].append(e);allcount+=1
    if allcount!=SITES*N or any(len(s)!=N for s in med.values()):raise ValueError("actual physical record count")
    manifest=dict(schema="REI_F05_12_ACTUAL_SOURCE_SITES_DENOMINATOR_CURVATURE_V1",
      original_pr=337,original_run=41281584019,original_artifact=13073074438,
      source_artifact_SHA256=ORIGINAL_ARTIFACT_SHA,source_csv_SHA256=STAGE_CSV_SHA,
      source_array_SHA256=STATE_SHA,group_count=len(groups),node_site_model_rows=allcount,
      unique_original_nodes=N,source_reference_status="original physically executed stage sites",
      formula="f_stage * r_g^2 exact when local numerator and stage forcing fixed",
      allX_joint_Dh_certified=False,first_F05_interval_completed=False,
      REI_canonical="28/88",REI_working="33/88",REI_fast="4/7",REC_H5="0/313",
      central_delta=0,production="HOLD",
      max_group_r=max(abs(g["r_global_denominator"]) for g in groups),
      max_group_heat_R_erg_s=max(g["exact_denominator_only_photoheat_R_erg_s"] for g in groups),
      group_fraction_max_error=max(g["fraction_identity_residual"] for g in groups),
      source_data_csv_SHA256=hashlib.sha256(outpath.read_bytes()).hexdigest(),
      site_e_median={":".join(k):float(np.median(v)) for k,v in med.items()},groups=groups)
    (outdir/"SCIENTIFIC_12_SITE_RESULT.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"node_site_rows":allcount,"group_rows":len(groups),
      "max_group_r":manifest["max_group_r"],"max_group_heat_R_erg_s":manifest["max_group_heat_R_erg_s"],
      "csv_sha256":manifest["source_data_csv_SHA256"],"central":"28/88"},sort_keys=True))
    return manifest
if __name__=="__main__":
    q=argparse.ArgumentParser();q.add_argument("--source",type=Path,required=True);q.add_argument("--out",type=Path,required=True);a=q.parse_args()
    run(a.source,a.out)
