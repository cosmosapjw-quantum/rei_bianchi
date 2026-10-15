#!/usr/bin/env python3
"""Read-only conversion of REAL AX08 full stress-history to Σ and tensor π_ab.

Do not identify the stress-free original source's Pi with a self-consistent
backreaction. Effective radiation and ionizing photon Pi are distinguishable.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from coupled_pi import Moments, H0, K, RHO_CRIT, OR

CASES={
 "FLRW":"research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO_composed_001",
 "Sigma_init_half_axis_plus":"research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_HALF_PLUS_composed_002",
 "Sigma_init_half_axis_minus":"research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_HALF_MINUS_composed_001",
 "Sigma_init_full_axis_minus":"research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_MINUS_composed_001",
}
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def load(owner,rel):
    folder=owner/rel
    rec=json.loads((folder/"COMPOSITION_RECEIPT.json").read_text())
    if rec["status"]!="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION":
        raise RuntimeError("READ_ONLY_CASE_NOT_COMPLETED")
    for fn in ("history.csv","feedback.csv"):
        if sha(folder/fn)!=rec["output_sha256"][fn]:
            raise RuntimeError("SOURCE_FROZEN_CASE_CHANGED:"+str(folder/fn))
    # history: time=3,a=4,b=6,H=7,s=8.
    # feedback: time=1,a=2,eff_radiationDeltaP=4,ionizingDeltaP=5,
    # effective signed energy=6, totalDeltaP=9.
    h=np.loadtxt(folder/"history.csv",delimiter=",",skiprows=1,
                 usecols=(3,4,6,7,8),dtype=np.float64)
    f=np.loadtxt(folder/"feedback.csv",delimiter=",",skiprows=1,
                 usecols=(1,2,4,5,6,9),dtype=np.float64)
    if h.shape!=(312238,5) or f.shape!=(312238,6) or not np.all(np.isfinite(h)) or not np.all(np.isfinite(f)):
        raise RuntimeError("COMPLETE_MOMENT_REGISTRY_MISSING")
    # The original feedback proper times and scales are bitwise equal to original history.
    if not(np.array_equal(h[:,0],f[:,0]) and np.array_equal(h[:,1],f[:,1])):
        raise RuntimeError("SOURCE_FEEDBACK_CLOCK_NOT_EQUAL")
    return h,f,rec,folder

def vector_moments(b):
    # Same exact 14th-order angular series as verified native Rust candidate,
    # output is dimensionless P2/rho_iso.
    import coupled_pi as cp
    from numpy.polynomial.polynomial import polyval
    return b*valpoly(b,cp.COEF_M2),1+b*b*valpoly(b,cp.COEF_M0)
def valpoly(x,c):
    result=np.zeros_like(x)
    for v in c[::-1]:result=result*x+v
    return result

def main(owner):
    out={}
    for tag,rel in CASES.items():
        h,f,receipt,folder=load(owner,rel)
        t,a,b,H,s=h.T
        delta_eff,delta_ion,delta_eps,delta_tot=f[:,2],f[:,3],f[:,4],f[:,5]
        m2,m0=vector_moments(b)
        eff_theory=RHO_CRIT*OR/a**4*m2
        eff_energy_theory=RHO_CRIT*OR/a**4*(m0-1)
        norm=RHO_CRIT*OR/a**4
        err_delta=float(np.max(np.abs(delta_eff-eff_theory)/norm))
        err_energy=float(np.max(np.abs(delta_eps-eff_energy_theory)/norm))
        # Refraction moment = (p_parallel-p_perp); actual Pi_ab uses Pi=DeltaP/3.
        if np.max(abs(delta_eff+delta_ion-delta_tot))/max(float(np.max(norm)),1e-300)>1e-12:
            raise RuntimeError("AX08_FEEDBACK_DELTA_P_ADDENDS_NOT_SUM")
        if err_delta>2e-13:
            raise RuntimeError("ACTUAL_SAVED_RADIATION_STRESS_MOMENT_INCONSISTENT:"+tag)
        sigma=np.sqrt(3)*np.abs(s)/H
        if np.any(~np.isfinite(sigma)) or np.max(sigma)>np.sqrt(3):
            raise RuntimeError("SIGMA_LRS_DOMAIN_INVALID")
        eps=np.sign(s).astype(int)
        if tag=="FLRW":
            if np.any(sigma!=0) or np.any(eps!=0):
                raise RuntimeError("FLRW_SIGMA_NOT_ZERO")
        out[tag]={
           "history_sha256":sha(folder/"history.csv"),
           "feedback_sha256":sha(folder/"feedback.csv"),
           "rows":len(h),
           "source_final_zbar":float(1/a[-1]-1),
           "Sigma_user_ref":float(sigma[0]),
           "Sigma_user_end":float(sigma[-1]),
           "Sigma_user_max":float(np.max(sigma)),
           "signed_orientation":int(eps[-1]),
           "Sigma_WainwrightEllis_ref":float(sigma[0]/np.sqrt(3)),
           "Sigma_WainwrightEllis_end":float(sigma[-1]/np.sqrt(3)),
           "source_effective_radiation_Pi_end_J_m3":float(delta_eff[-1]/3),
           "source_ionizing_photon_Pi_end_J_m3":float(delta_ion[-1]/3),
           "source_radiation_Pi_total_end_J_m3":float(delta_tot[-1]/3),
           "max_abs_ionizing_Pi_J_m3":float(np.max(abs(delta_ion))/3),
           "max_abs_effective_rad_Pi_J_m3":float(np.max(abs(delta_eff))/3),
           "max_abs_saved_effective_rad_P2_ratio_discrepancy":err_delta,
           "max_abs_signed_energy_ratio_discrepancy":err_energy,
           "source_matter_Pi_status":"NOT_PRESENT_IN_ORIGINAL_FROZEN_PERFECT_MATTER",
           "scope":"original stress-free background with saved radiation stress diagnostic, not coupled Einstein stress evolution",
        }
    result={
      "schema":"rei.axbi.legacy_to_Sigma_and_actual_Pi_replay.v1",
      "status":"FOUR_ACTUAL_COMPLETED_SOURCES_SIGMA_PI_MOMENTS_VERIFIED",
      "Sigma_user":"sqrt(sigma_ab sigma^ab/2)/H, nonnegative; sign orientation separate",
      "Sigma_WE":"sqrt(sigma_ab sigma^ab/6)/H, equals Sigma_user/sqrt3",
      "Pi_tensor":"diag(-Pi,-Pi,2Pi); Pi=(p_parallel-p_perp)/3 for radiation and matter",
      "source_only":out,
      "not_reintegrated":"the original source stress has not been fed back into the original cold HHe native solver",
      "scientific_admission":"NOT_ISSUED"
    }
    p=Path(__file__).resolve().parent/"results"/"actual_Sigma_Pi_history.json"
    p.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:{"Sigma_ref":v["Sigma_user_ref"],
         "Sigma_end":v["Sigma_user_end"],
         "Pi_eff_end_Jm3":v["source_effective_radiation_Pi_end_J_m3"],
         "Pi_ion_end_Jm3":v["source_ionizing_photon_Pi_end_J_m3"],
         "source_rad_angular_error":v["max_abs_saved_effective_rad_P2_ratio_discrepancy"]}
        for k,v in out.items()},indent=2))
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--owner-root",type=Path,required=True)
    args=p.parse_args();main(args.owner_root)
