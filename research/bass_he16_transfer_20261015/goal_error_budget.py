"""Conditional goal-oriented ionization-fraction accuracy budget for signed-q tau.

The bound covers errors in saved ion fractions at fixed nH and proper clock;
it does NOT cover H(t), t(a), truncation, photon-source, temperature or source
ODE error unless separate upstream error enclosures are supplied.
"""
import argparse
import json
from pathlib import Path
import numpy as np

from clock_decompose_signed import CASE_ORDER, read_caches, tau_at_t
from signed_prefix_tau import EXPECTED_Q, PREC

SIGMA_C=PREC("6.6524587321e-29")*PREC("299792458")*PREC("1000000")
F_HE=PREC(1227)/PREC(15092)
N_H0=PREC("0.0017579215852062606")  # archived cold normal-frame initial source value
A_REF=PREC(1)/PREC(21)


def integral_nh(t,a,up_to_s=None):
    """Return sigma_T*c*integral(nH_proper_cm^-3 dt)*1e6 by trapezoid."""
    t=np.asarray(t,dtype=PREC)
    a=np.asarray(a,dtype=PREC)
    if len(t)<2 or len(t)!=len(a) or not np.all(t[1:]>t[:-1]) or np.any(a<=0):
        raise ValueError("Invalid proper-time and scale history")
    nh=N_H0*(A_REF/a)**3
    if up_to_s is None:
        val=np.sum(np.diff(t)*(nh[:-1]+nh[1:])/2,dtype=PREC)
        return SIGMA_C*val
    end=PREC(up_to_s)
    if end<t[0] or end>t[-1]:
        raise ValueError("Common proper time outside source domain")
    j=int(np.searchsorted(t,end,side="right")-1)
    if j==len(t)-1:return integral_nh(t,a)
    integral=np.sum(np.diff(t[:j+1])*(nh[:j]+nh[1:j+1])/2,dtype=PREC)
    frac=(end-t[j])/(t[j+1]-t[j])
    nh_end=nh[j]+frac*(nh[j+1]-nh[j])
    integral+=(end-t[j])*(nh[j]+nh_end)/2
    return SIGMA_C*integral


def budget(by_case,signed,clock,alpha=PREC("0.1")):
    if not PREC(0)<alpha<PREC(1):raise ValueError("Need 0<alpha<1")
    all_case={}
    for case,v in by_case.items():
        all_case[case]=integral_nh(v["t_s"],v["a"])
    r={
      "schema":"he18.axbi.goal_tau_ion_fraction_budget.v1",
      "status":"CONDITIONAL_BUDGET_NOT_CERTIFIED_ODE_ERROR",
      "target_relative_error":str(alpha),
      "n_H0_proper_cm3":str(N_H0),
      "a_ref":str(A_REF),
      "helium_to_hydrogen_number_ratio":str(F_HE),
      "species_error_assumption":"Each of |delta x_HII|, |delta x_HeII|, |delta x_HeIII| is <= epsilon pointwise for all t, across all three q histories; nH and proper clocks are exact inputs",
      "bound":"|delta E| <= [I_plus/2 + I_minus/2 + I_ZERO]*(1+3 fHe)*epsilon; I_case=sigmaT*c*1e6*int nH_proper_cm3 dt",
      "I_case":[{"case":c,"I":str(all_case[c])} for c in CASE_ORDER],
      "profiles":{}
    }
    end_index=-1
    tstar=PREC(clock["t_common_s"][end_index])
    for h in ("0.005","0.01"):
        plus="SHEAR_HALF_PLUS" if h=="0.005" else "SHEAR_PLUS"
        minus="SHEAR_HALF_MINUS" if h=="0.005" else "SHEAR_MINUS"
        I_E=(all_case[plus]+all_case[minus])/2+all_case["ZERO"]
        L_E=(PREC(1)+PREC(3)*F_HE)*I_E
        E=abs(PREC(signed["even_half_q005"][end_index] if h=="0.005" else signed["even_half_q010"][end_index]))
        threshold=alpha*E/L_E
        I_Et=(integral_nh(by_case[plus]["t_s"],by_case[plus]["a"],tstar)+
              integral_nh(by_case[minus]["t_s"],by_case[minus]["a"],tstar))/2+integral_nh(
                  by_case["ZERO"]["t_s"],by_case["ZERO"]["a"],tstar)
        L_Et=(PREC(1)+PREC(3)*F_HE)*I_Et
        Et=abs(PREC(clock["decompositions"][h]["even_common_time"][end_index]))
        r["profiles"][h]={
          "abs_E_at_common_a":str(E),
          "weighted_ionization_sensitivity_integral":str(L_E),
          "uniform_species_error_sufficient_for_target_relative_E":str(threshold),
          "abs_E_at_common_proper_time":str(Et),
          "weighted_common_time_integral":str(L_Et),
          "uniform_species_error_sufficient_for_target_relative_Et":str(alpha*Et/L_Et)
        }
    r["limitations"]="No assertion that native last_error bounds fractions. This is a conditional worst-case Lipschitz criterion for fraction error only; full tau error needs density, clock, source, quadrature and collision error budgets."
    return r


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--cache-dir",type=Path,required=True)
    p.add_argument("--signed",type=Path,required=True)
    p.add_argument("--clock",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    arrays,manifest,elapsed=read_caches(args.cache_dir)
    result=budget(arrays,json.loads(args.signed.read_text()),json.loads(args.clock.read_text()))
    result["source_history_sha256"]={c:v["history_sha256"] for c,v in manifest["cases"].items()}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
