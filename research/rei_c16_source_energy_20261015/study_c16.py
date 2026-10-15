#!/usr/bin/env python3
"""C16 actual source stellar+escape open energy transfer and independent geometry work.

Run original C13+PR139 C15 astrophysical/polarized-restricted physical operators,
now with C16 Gauss8 observable gravitational-shear/thermal geometric work check.
No fictitious stellar reservoir EOS, no full Einstein source admission.
"""
from __future__ import annotations
import json,math,statistics,time
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from c16_exchange import (
  WorkAuditor,Config,NativeStellarSource,Scenario,ROOT,START,STOP)
from c15_coupled import Coupled

HERE=Path(__file__).resolve().parent
OUTPUT=HERE/"results"
def native_source():
  return NativeStellarSource.load(Scenario(ROOT),
    ROOT/"research/rei_c13_live_source_20261015/NATIVE_SOURCE_8X8.csv")
def summary(z):
  r=z["C16_scoped_open_Q_energy_audit"]
  q=r["explicit_source_exchange_flux"]
  h=z["endpoint"]
  return {
    "Sigma_ref":z["Sigma_ref_user"],"axis_sign":z["orientation_initial"],
    "kappa_gamma":z["numerical"]["kappa_gamma"],
    "kappa_nu":z["numerical"]["kappa_nu"],
    "accepted_macro_steps":z["numerical"]["nstep"],
    "accepted_photon_halfsteps":r["number_accepted_source_halfsteps"],
    "Sigma_end":h["Sigma"],"proper_time_elapsed_s":h["elapsed_s"],
    "xHII_end":h["x_HII"],"xHeII_end":h["x_HeII"],"xHeIII_end":h["x_HeIII"],
    "Tgas_K_end":h["Tgas_K"],"stellar_E_emitted_eV_perH":r["actual_stellar_energy_emitted_eV_perH"],
    "CaseA_escaped_E_eV_perH":r["actual_CaseA_escaped_energy_eV_perH"],
    "net_external_E_input_eV_perH":r["signed_external_net_eV_perH"],
    "ionizing_UV_still_live_eV_perH":r["observed_ionizing_UV_energy_end_eV_perH"],
    "total_geometric_UV_and_gas_work_eV_perH":r["actual_cumulative_pressure_work_eV_perH"],
    "max_absolute_open_ledger_residual_eV_perH":r["max_open_source_energy_ledger_abs_eV_perH"],
    "max_independent_Gauss8_shear_work_error_eV_perH":r["max_independent_GL_photon_pressure_shear_work_error_eV_perH"],
    "max_independent_total_geometric_work_error_eV_perH":r["max_independent_GL_pressure_shear_work_error_eV_perH"],
    "max_ratio_external_energy_Q_to_local_HrhoRad":max(abs(item["open_external_Q_over_H_rho_rad"]) for item in q),
    "mean_signed_external_energy_power_J_m3_s":statistics.mean(p["external_power_J_m3_s"] for p in q),
    "max_abs_rad_P1_flux_over_energy":r["angular_axis_reflection_source_momentum_dipole"]["max_ratio_uv_energy_flux_to_energy"],
    "max_PSTF_massless_radiation_dipole":r["angular_axis_reflection_source_momentum_dipole"]["max_BASS_PSTF_gamma_nu_dipole"],
    "C15_base_native_chemistry_function_untouched":True,
    "science_admission":"NOT_ISSUED"
  }
def main():
 src=native_source()
 start=time.perf_counter()
 cases={}
 for name,q,kap in (
  ("FLRW_SOURCE",0.,0.),("KAPPA_INDUCED_SIGMA",0.,.2),
  ("SIGNED_PLUS_SMALL",+.005,.2),("SIGNED_MINUS_SMALL",-.005,.2),
  ("SIGNED_PLUS_LARGE",+.01,.2),("SIGNED_MINUS_LARGE",-.01,.2)):
   z=WorkAuditor(Config(legacy_q_for_locked_source=q,
      kappa_gamma=kap,kappa_nu=kap,nstep=32,compression=True),src,order=8).run()
   cases[name]=z
   print("PHYSICS_C16",name,json.dumps(summary(z)),flush=True)
 # Changing quadrature cannot change the underlying source physics.
 independent=[]
 for rule in (4,8,16):
  r=WorkAuditor(Config(legacy_q_for_locked_source=.005,nstep=16),
                src,order=rule).run()
  independent.append({"gauss_order":rule,**summary(r)})
 if not(independent[0]["Sigma_end"]==independent[1]["Sigma_end"]==independent[2]["Sigma_end"]):
  raise RuntimeError("NO_INDEPENDENT_SHADOW_QUADRATURE_INVARIANCE")
 # Measure the observer/auditor overhead separately from native C15.
 bench={"real_C15":[],"independent_work_auditor":[]}
 for _ in range(5):
  for label,method in (("real_C15",Coupled),("independent_work_auditor",WorkAuditor)):
   solver=method(Config(legacy_q_for_locked_source=.005,nstep=32),src)
   t=time.perf_counter()
   sol=solver.run()
   bench[label].append(time.perf_counter()-t)
 old=cases["SIGNED_PLUS_SMALL"]["endpoint"]
 budget=cases["SIGNED_PLUS_SMALL"]["C16_scoped_open_Q_energy_audit"]
 phi=budget["independent_perH_energy_tables"]
 ext=budget["explicit_source_exchange_flux"]
 work=budget["independent_accepted_half_step_work_table"]
 assert len(phi)==33 and len(ext)==32 and len(work)==64
 fig,axes=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
 times=np.array([z["a"] for z in phi]);redshift=1/times-1
 axes[0,0].plot(redshift,[z["stellar_emission_source_eV_perH"] for z in phi],label="stellar UV emitted")
 axes[0,0].plot(redshift,[z["CaseA_escaped_external_eV_perH"] for z in phi],label="CaseA escape")
 axes[0,0].plot(redshift,[z["photon_eV_perH"] for z in phi],label="ionizing UV retained")
 axes[0,0].plot(redshift,[z["measured_expansion_work_eV_perH"] for z in phi],label="geometric work")
 axes[0,0].set_ylabel("Energy per H nucleus [eV/H]")
 axes[0,0].legend(fontsize=7)
 axes[0,1].plot(redshift,[z["open_energy_balance_residual_eV_perH"] for z in phi])
 axes[0,1].set_ylabel("Open source energy ledger residual [eV/H]")
 axes[1,0].plot([z["a_mid"] for z in ext],[z["external_power_J_m3_s"] for z in ext],label="emission minus CaseA escape")
 axes[1,0].set_ylabel("Explicit external Q0 [J m^-3 s^-1]")
 axes[1,1].plot([z["a1"] for z in work],[z["combined_physical_pressure_work_error_eV_perH"] for z in work],label="physical - Gauss8")
 axes[1,1].set_ylabel("Independent expansion/shear work discrepancy [eV/H]")
 for a in axes.flat:
  a.grid(alpha=.3);a.set_xlabel("Mean redshift / scale factor (bottom row a)")
 axes[0,0].invert_xaxis();axes[0,1].invert_xaxis()
 fig.suptitle("C16: native MD14 HHe source energy transfers and Bianchi shear work, open Einstein system")
 fig.savefig(OUTPUT/"C16_open_Q_energy_and_shear_work.png",dpi=170)
 plt.close(fig)
 med={k:statistics.median(v) for k,v in bench.items()}
 result={
  "schema":"rei.c16.original_C15_exact_photon_energy_exchange_audit.v1",
  "status":"C16_NATIVE_MD14_CASEA_AND_EINSTEIN_SHEAR_WORK_SOURCE_SCOPED_PASS",
  "original_c15_parent":"435c94308c0cd7b1ba8ff6518246da061f2fc2fa",
  "scientific_source":"original native MD14 spectral source plus original C11 CaseA and BASS gamma/nu C14, no supplier bytes changed",
  "cases":{k:summary(v) for k,v in cases.items()},
  "independent_Gauss_work_order_controls":independent,
  "auditor_cost":{"repetitions":5,"process_wall_seconds":bench,
     "median_seconds":med,
     "auditor_overhead_ratio":med["independent_work_auditor"]/med["real_C15"],
     "note":"Extra dense-output ODE source replay plus Gaussian work integral is independent postprocessing validation overhead; NOT a production C15 optimization."},
  "source_RHS":{"equations":"d(U_UV)/dln a=-U_UV-2(s/H) P2_UV, d(U_th)/dln a=-2U_th; photo+gas binding+thermal+escaped+work-emitted=const; source Qexternal=emitted-escaped",
     "momentum":"Under LRS parity-symmetric Q1 exactly zero; any dipole/tilt is explicitly rejected."},
  "important_open_Einstein_Q_gap":"stellar emission, escaped recombination radiation and their source rest-mass/pressure/Einstein stress history are NOT assigned; total covariant gravity constraint derivative not yet conserved even though local photon-gas energy transfer is balanced",
  "scientific_admission":"NOT_ISSUED",
  "total_wall_s":time.perf_counter()-start}
 (OUTPUT/"RESULTS_C16.json").write_text(json.dumps(result,indent=2)+"\n")
 # Keep one machine-readable per-accepted halfstep table, source plus momentum.
 (OUTPUT/"C16_SIGNED_PLUS_ACCEPTED_HALFSTEPS.json").write_text(json.dumps({
   "schema":"rei.C16.actual_signed_plus_scoped_halfstep_work.v1",
   "source_C15_real_UV_HHe_integrated":True,
   "work":work,
   "external_source_flux":ext,
   "momentum_Q1":budget["independent_momentum_checks"],
   "original_source_changed":False},indent=2)+"\n")
 print("C16_SUMMARY",json.dumps({
   "cases":len(cases),"source_work_error_max":max(x["max_independent_total_geometric_work_error_eV_perH"] for x in result["cases"].values()),
   "open_energy_ledger_max":max(x["max_absolute_open_ledger_residual_eV_perH"] for x in result["cases"].values()),
   "external_net_eVperH":result["cases"]["SIGNED_PLUS_SMALL"]["net_external_E_input_eV_perH"],
   "Qmax_over_HrhoRad":result["cases"]["SIGNED_PLUS_SMALL"]["max_ratio_external_energy_Q_to_local_HrhoRad"],
   "Gauss_orders":[v["gauss_order"] for v in independent],
   "audit_overhead_ratio":result["auditor_cost"]["auditor_overhead_ratio"],
   "elapsed_s":result["total_wall_s"]},indent=2))
if __name__=="__main__":
 main()
