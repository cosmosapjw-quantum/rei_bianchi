#!/usr/bin/env python3
"""WU R50: passive primordial deuterium electron-opacity ceiling on original REI F08 S0 sky.

No D chemistry, no HD cooling, no feedback, no new REI cosmic history.
"""
from __future__ import annotations
import bisect
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source_inputs"
SOURCE_SHA = {
    "S0_BI-electron_density.csv.gz": "663911291bea564d314e1d46df9750c03a39fd5d9404eca6a7485776d894f723",
    "S0_FLRW-electron_density.csv.gz": "0b81cae87d6f90888d1d3def1995cd8d029625d1cc1dd11bffab94e8d30e7efa",
    "science_scenario_v1.json": "c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1",
    "ORIGINAL_F08_S0_BIANCHI_THOMSON_SKY.csv.gz": "41fb767cc6c826047abf3799164f9e5b6a970c9dc879566147ad036226e4588d",
}
SOURCE_SUMMARY_GIT_BLOB = "99b951035605bbe58e8ce49b8fd611e85b72ec71"
REI_SOURCE_PAIR_ID = "0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8"
ETA_D = 2.5e-5  # explicit upper scenario parameter, NOT a primordial observational CI
SIGMA_T_CM2 = 6.6524587051e-25
C_CM_S = 29979245800.0


def digest(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def git_blob(p):
    b = p.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()


def rel(a, b):
    return abs(a - b) / max(abs(a), abs(b), 1e-300)


def h_integral(te, to, h, nh0):
    """Exact proper-time integral of n_H0 exp(-3 H t), stable for nearby times."""
    if not (0 <= te <= to and h > 0 and nh0 > 0):
        raise ValueError("invalid source proper-clock/hydrogen history")
    return nh0 * math.exp(-3 * h * te) * (-math.expm1(-3 * h * (to - te))) / (3 * h)


def analytic_cap(te, to, h, nh0, eta=ETA_D):
    if not (0 <= eta <= 1):
        raise ValueError("invalid nonnegative isotope fraction cap")
    return C_CM_S * SIGMA_T_CM2 * eta * h_integral(te, to, h, nh0)


def sample_quantiles(a):
    s = sorted(a)
    def q(t):
        p = t * (len(s) - 1)
        i, f = int(p), p - int(p)
        return s[i] * (1 - f) + s[min(i + 1, len(s) - 1)] * f
    return dict(min=s[0],median=q(.5),p95=q(.95),max=s[-1])


class History:
    def __init__(self, path, nh0, h, to):
        self.t, self.ne, self.nh = [], [], []
        with gzip.open(path, "rt", newline="") as f:
            for row in csv.DictReader(f):
                t = float(row["normal_time_s"])
                nh = float(row["nH_proper_cm3"])
                ne = float(row["ne_proper_cm3"])
                lo = float(row["ne_conditional_lo"])
                hi = float(row["ne_conditional_hi"])
                if not (0 <= t <= to and nh > 0 and ne > 0 and lo <= ne <= hi
                        and row["D_gas_normal_observer"] in ("1.0","1")):
                    raise ValueError("original nH / ne provenance or physical range invalid")
                if self.t and t <= self.t[-1]:
                    raise ValueError("nonmonotone source proper clock")
                if rel(nh,nh0*math.exp(-3*h*t)) > 1e-12:
                    raise ValueError("native F08 nH different from analytic volume law")
                self.t.append(t)
                self.ne.append(ne)
                self.nh.append(nh)
        if len(self.t) != 16001 or self.t[0] != 0 or self.t[-1] != to:
            raise ValueError("native F08 16001-sample source length/clock drift")
        self.suffix = [0.0] * len(self.t)
        for j in range(len(self.t)-2,-1,-1):
            self.suffix[j] = (self.suffix[j+1] + 0.5*(self.ne[j]+self.ne[j+1])
                              * (self.t[j+1]-self.t[j]))

    def ne_at(self,te):
        j=min(len(self.t)-2,max(0,bisect.bisect_right(self.t,te)-1))
        a=(te-self.t[j])/(self.t[j+1]-self.t[j])
        return self.ne[j]*(1-a)+self.ne[j+1]*a

    def int_ne(self,te):
        if not (self.t[0] <= te <= self.t[-1]):
            raise ValueError("F08 ray emission time outside source clock")
        if te == self.t[-1]:
            return 0.0
        j=min(len(self.t)-2,bisect.bisect_right(self.t,te)-1)
        y=self.ne_at(te)
        return self.suffix[j+1]+0.5*(y+self.ne[j+1])*(self.t[j+1]-te)


def write_gzip(path,rows,keys):
    with path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw,mode="wb",mtime=0,filename="",compresslevel=6) as comp:
            with io.TextIOWrapper(comp,encoding="utf-8",newline="") as text:
                w=csv.DictWriter(text,fieldnames=keys,lineterminator="\n")
                w.writeheader()
                for row in rows:w.writerow(row)


def run(out):
    for name,expected in SOURCE_SHA.items():
        if digest(SOURCE/name) != expected:
            raise ValueError("original REI source SHA256 mismatch: "+name)
    if git_blob(SOURCE/"SOURCE_F08_THOMSON_SKY_SUMMARY_12.csv") != SOURCE_SUMMARY_GIT_BLOB:
        raise ValueError("original REI sky-summary Git blob mismatch")
    s=json.loads((SOURCE/"science_scenario_v1.json").read_text())
    if (s["source"]["family"]!="S0" or s["background"]["tilt"]!=[0,0,0]
        or s["background"]["pairs"]["BIANCHI_I"]["H_per_s"]!=[1.01e-14,9.9e-15,1e-14]
        or s["background"]["pairs"]["FLRW"]["H_per_s"]!=[1e-14]*3
        or s["constants"]["c_cm_s"]!=C_CM_S
        or s["initial_state"]["nH0_cm3"]!=1e-4):
        raise ValueError("original S0 physical scenario mutated")
    to=float(s["time"]["t_end_s"])
    h=float(s["background"]["H_mean_per_s"])
    nh0=float(s["initial_state"]["nH0_cm3"])
    coeff=C_CM_S*SIGMA_T_CM2
    BI=History(SOURCE/"S0_BI-electron_density.csv.gz",nh0,h,to)
    FL=History(SOURCE/"S0_FLRW-electron_density.csv.gz",nh0,h,to)
    if BI.t != FL.t or BI.nh != FL.nh:
        raise ValueError("original paired hydrogen density and proper-clock mismatch")
    groups={}
    with open(SOURCE/"SOURCE_F08_THOMSON_SKY_SUMMARY_12.csv",newline="") as f:
        for r in csv.DictReader(f):
            key=(int(r["angular_nmu"]),int(r["angular_nphi"]),float(r["fraction"]))
            groups[key]=r
    if len(groups)!=12:raise ValueError("expected original four windows times three angular grids")
    newkeys=["window_fraction","angular_nmu","angular_nphi","mu_bin","phi_bin",
             "nx","ny","nz","emission_time_s","original_tau_BI",
             "D_fullion_tau_cap","D_fullion_cap_over_original_tau","tau_BI_with_fullion_D",
             "D_emitter_electron_fraction_cap","fullion_transmission","fullion_visibility",
             "visibility_lower_bound_any_D_ionization","visibility_upper_bound_any_D_ionization",
             "D_fullion_delta_tau_FLRW","D_fullion_BI_minus_FLRW",
             "original_geom_delta_tau","original_tau_FLRW",
             "fullion_extra_tau_Qxx_kernel","fullion_extra_tau_Qyy_kernel","fullion_extra_tau_Qzz_kernel"]
    entries=[]
    original_sky_tau_max_rel=0.0
    original_sky_emitter_ne_max_rel=0.0
    max_tau_orig_source_difference=0.0
    with gzip.open(SOURCE/"ORIGINAL_F08_S0_BIANCHI_THOMSON_SKY.csv.gz","rt",newline="") as src:
        for r in csv.DictReader(src):
            nmu=int(r["angular_nmu"]);nphi=int(r["angular_nphi"]);fr=float(r["window_fraction"])
            key=nmu,nphi,fr
            if key not in groups:raise ValueError("unknown original observer sky grid")
            te=float(r["emission_time_s"])
            tf=float(r["flrw_reference_emission_time_s"])
            tau=float(r["tau_BI"])
            tauF=float(r["tau_FLRW"])
            if not (0<=te<=to and 0<=tf<=to and tau>0 and tauF>0):
                raise ValueError("nonphysical sky ray")
            original_sky_tau_max_rel=max(original_sky_tau_max_rel,rel(tau,coeff*BI.int_ne(te)),
                rel(tauF,coeff*FL.int_ne(tf)))
            ne_e=BI.ne_at(te)
            original_sky_emitter_ne_max_rel=max(original_sky_emitter_ne_max_rel,
                rel(ne_e,float(r["ne_BI_emitter_cm3"])))
            cap=analytic_cap(te,to,h,nh0)
            capF=analytic_cap(tf,to,h,nh0)
            rho=ETA_D*nh0*math.exp(-3*h*te)/ne_e
            vis=float(r["visibility_BI_per_relative_z"])
            if not (cap>=0 and 0<=rho<1 and vis>0):
                raise ValueError("unphysical passive isotope cap")
            fullvis=vis*(1+rho)*math.exp(-cap)
            xx,yy,zz=float(r["nx"]),float(r["ny"]),float(r["nz"])
            entries.append((key,{
                "window_fraction":fr,"angular_nmu":nmu,"angular_nphi":nphi,
                "mu_bin":int(r["mu_bin"]),"phi_bin":int(r["phi_bin"]),
                "nx":xx,"ny":yy,"nz":zz,"emission_time_s":te,"original_tau_BI":tau,
                "D_fullion_tau_cap":cap,"D_fullion_cap_over_original_tau":cap/tau,
                "tau_BI_with_fullion_D":tau+cap,"D_emitter_electron_fraction_cap":rho,
                "fullion_transmission":math.exp(-(tau+cap)),
                "fullion_visibility":fullvis,
                "visibility_lower_bound_any_D_ionization":vis*math.exp(-cap),
                "visibility_upper_bound_any_D_ionization":vis*(1+rho),
                "D_fullion_delta_tau_FLRW":capF,
                "D_fullion_BI_minus_FLRW":cap-capF,
                "original_geom_delta_tau":float(r["delta_tau_geometry_fixed_relative_z"]),
                "original_tau_FLRW":tauF,
                "fullion_extra_tau_Qxx_kernel":cap*(xx*xx-1/3),
                "fullion_extra_tau_Qyy_kernel":cap*(yy*yy-1/3),
                "fullion_extra_tau_Qzz_kernel":cap*(zz*zz-1/3)}))
    if len(entries)!=10752:raise ValueError("original F08 sky has wrong row count")
    if original_sky_tau_max_rel>1e-11 or original_sky_emitter_ne_max_rel>1e-11:
        raise ValueError("independent reconstructed source-electron optical depth mismatches")
    out.mkdir(parents=True,exist_ok=True)
    full=out/"R50_ORIGINAL_F08_S0_D_ELECTRON_THOMSON_CAP_10752.csv.gz"
    write_gzip(full,(row for key,row in entries),newkeys)
    stats=[]
    for key,reported in sorted(groups.items()):
        arr=[r for k,r in entries if k==key]
        if len(arr)!=key[0]*key[1]:raise ValueError("angular source sampling inconsistent")
        mean=lambda name:statistics.fmean(a[name] for a in arr)
        geom=float(reported["delta_geometry_sky_rms_centered"])
        if geom<=0:raise ValueError("source geometry contrast absent")
        caps=[r["D_fullion_tau_cap"] for r in arr]
        m=max(caps)
        srow=dict(angular_nmu=key[0],angular_nphi=key[1],window_fraction=key[2],
                  z_relative=float(reported["z_rel"]),ray_rows=len(arr),
                  mean_D_max_tau=mean("D_fullion_tau_cap"),max_D_max_tau=m,
                  max_cap_over_original_tau=max(r["D_fullion_cap_over_original_tau"] for r in arr),
                  max_emitter_ne_ratio=max(r["D_emitter_electron_fraction_cap"] for r in arr),
                  original_Bianchi_geometry_RMS=geom,
                  max_centered_sky_rms_perturbation_over_original_geometry_RMS=m/geom,
                  fullion_Qxx=mean("fullion_extra_tau_Qxx_kernel"),
                  fullion_Qyy=mean("fullion_extra_tau_Qyy_kernel"),
                  fullion_Qzz=mean("fullion_extra_tau_Qzz_kernel"),
                  original_source_tau_mean=float(reported["source_BI_tau_mean"]),
                  original_ray_tau_mean=mean("original_tau_BI"),
                  fullion_template_tau_mean=mean("tau_BI_with_fullion_D"))
        if rel(srow["original_source_tau_mean"],srow["original_ray_tau_mean"])>1e-12:
            raise ValueError("original observer sky row-to-summary mismatch")
        stats.append(srow)
    summary=out/"R50_SOURCE_SKY_SUMMARY_12.csv"
    with summary.open("w",encoding="utf-8",newline="") as fo:
        wr=csv.DictWriter(fo,fieldnames=list(stats[0]),lineterminator="\n")
        wr.writeheader()
        for row in stats:wr.writerow(row)
    witness=out/"R50_REI_OBSERVER_WITNESS_12.csv"
    with witness.open("w",encoding="utf-8",newline="") as fo:
        wr=csv.DictWriter(fo,fieldnames=newkeys,lineterminator="\n")
        wr.writeheader()
        for key in sorted(groups):
            arr=[r for k,r in entries if k==key]
            wr.writerow(max(arr,key=lambda x:x["D_fullion_tau_cap"]))
    result=dict(schema="WU_R50_REI_F08_S0_PASSIVE_DEUTERIUM_OPACITY_V1",
       status="SOURCE_CONDITIONAL_S0_BOUNDED_ISOTOPE_THOMSON_OBSERVER_SCREEN",
       source_PR=349,source_REI_head="58f7ffb685c3758f1fed1113ff8134a24478c3df",
       parent_WU_PR=188,parent_WU_head="f5d09daf5e70baa964aadda2156cd61facf495c4",
       source_pair_id=REI_SOURCE_PAIR_ID,original_source_sha256=SOURCE_SHA,
       original_summary_git_blob=SOURCE_SUMMARY_GIT_BLOB,
       assumptions=dict(passive_deuterium=True,max_D_per_H=ETA_D,admitted_primordial_D_measurement=False,
           no_HHe_or_geometry_feedback=True,n_Dplus_density_between="0 and eta_D*nH_proper(t)",
           original_F08_S0_prescribed_not_cosmic_history=True,
           fullion_is_upper_template_not_predicted_ionization=True),
       exact_formula="tau_Dcap=sigma_T*c*eta_D*nH0*(exp(-3H te)-exp(-3H to))/(3H)",
       ray_rows=len(entries),per_window=stats,
       original_source_check=dict(history_rows_BI=len(BI.t),history_rows_FLRW=len(FL.t),
          max_recomputed_original_sky_tau_relative_error=original_sky_tau_max_rel,
          max_recomputed_original_emitter_ne_relative_error=original_sky_emitter_ne_max_rel),
       observer_conclusion=dict(max_bound_to_geometry_RMS=max(z["max_centered_sky_rms_perturbation_over_original_geometry_RMS"] for z in stats),
              max_tau_fraction=max(z["max_cap_over_original_tau"] for z in stats),
              max_emitter_ne_ratio=max(z["max_emitter_ne_ratio"] for z in stats)),
       output_sha256={str(full.name):digest(full),str(summary.name):digest(summary),str(witness.name):digest(witness)},
       DAG=dict(WU="34/49",REI_central="28/88",REI_working="33/88",physical_fast="4/7",
                new_canonical_nodes=0,REI_26event_tick="160/131072_HOLD",F08_scientific_admission="HOLD"),
       policy=dict(production="HOLD",no_merge=True,auto_next_node=False,HH_R10="OFF",REI_L4=False),
       no_go_claim=False,full_D_chemistry_run=False)
    (out/"R50_RESULTS.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return result


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=HERE/"results")
    args=p.parse_args()
    res=run(args.out)
    print(json.dumps({"source":res["original_source_check"],"observer":res["observer_conclusion"],
                      "outputs":res["output_sha256"],"DAG":res["DAG"]},indent=2))
