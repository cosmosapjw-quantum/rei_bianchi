#!/usr/bin/env python3
"""Original BASS193 frozen-source crosswalk: PR297/298/299/300, no IVP.

All rows are actually source-owned physical epoch/interval values, not synthetic
initial conditions. Separate source-operator comparison from physical admission.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'inputs'
OUT = ROOT / 'results'
OUT.mkdir(parents=True, exist_ok=True)
EV_ERG = 1.602176634e-12  # exact SI eV -> cgs erg
KB_ERG_K = 1.380649e-16  # exact SI kB -> cgs erg/K
CHI_H_Ev = 13.598434599702  # REI original threshold (not BASS rounded)
SOURCE_LOCK = {
 'PR297_ALL_EPOCH_CAUSAL_ARRIVAL_192.csv':'652187a2299e99d1be15c2827563936bca23be106705ae25ccbfe595a821754a',
 'PR298_HYBRID_FJ_THERMAL_193.csv':'08e6b70a9808a61a18955515555152d80b40c7a3a0766ead8a5d6f6cee82120e',
 'PR299_FROZEN_SOURCE_TANGENCY_193.csv':'a373604cdf5c096f02cfb8e2c3859c95897b942c4574e3fcf58f4c4bcb1741ab',
 'PR300_FS2010_SELECTED_ARRIVAL_192.csv':'a073f89c4396cdbeb1fda0c7a20dae2335fec0bef001112641beed7ef78ed79c',
}

def verified_read(name):
 p=SRC/name
 assert hashlib.sha256(p.read_bytes()).hexdigest()==SOURCE_LOCK[name],f'SOURCE SHA mismatch: {name}'
 return pd.read_csv(p)

def arr(frame,key): return frame[key].to_numpy(dtype=np.float64)

def compute():
 h=verified_read('PR298_HYBRID_FJ_THERMAL_193.csv')
 t=verified_read('PR299_FROZEN_SOURCE_TANGENCY_193.csv')
 p=verified_read('PR297_ALL_EPOCH_CAUSAL_ARRIVAL_192.csv')
 s=verified_read('PR300_FS2010_SELECTED_ARRIVAL_192.csv')
 assert [len(h),len(t),len(p),len(s)]==[193,193,192,192]
 assert list(h.epoch)==list(range(193)) and list(t.epoch)==list(range(193))
 assert list(p.arrival_interval)==list(range(192)) and list(s.arrival_interval)==list(range(192))
 assert np.max(np.abs(arr(h,'z')-arr(t,'z')))<1e-12
 assert np.max(np.abs(arr(h,'z')[:-1]-arr(p,'z_high')))<1e-12
 assert np.max(np.abs(arr(p,'z_high')-arr(s,'z_high')))<1e-12
 assert np.max(np.abs(arr(p,'z_low')-arr(s,'z_low')))<1e-12
 assert np.max(np.abs(arr(h,'nHref_over_nb')-arr(t,'nHref_over_nb')))<1e-14
 dx=np.diff(arr(h,'x'))
 dt=arr(p,'proper_interval_s')
 assert np.all(dx>0) and np.all(dt>0)
 proper=np.diff(arr(h,'elapsed_s'))
 clock_rel=np.abs(proper-dt)/dt
 assert clock_rel.max()<5e-13,(clock_rel.max(),'DIFFERENT SOURCE CLOCK')
 Hmid=(arr(h,'H_s')[:-1]+arr(h,'H_s')[1:])/2
 clock_disc=Hmid*dt/dx-1
 assert np.max(np.abs(clock_disc)) < 5e-5  # observed saved mesh midpoint quadrature, NOT exact identity
 zmid=np.sqrt((1+arr(h,'z')[:-1])*(1+arr(h,'z')[1:]))-1
 xmid=(arr(h,'x')[:-1]+arr(h,'x')[1:])/2
 nbmid=1.e-6*np.sqrt(arr(h,'nb_m3')[:-1]*arr(h,'nb_m3')[1:])
 cvb=arr(h,'REI_common_Cv21_erg_cm3_K')/(arr(h,'nb_m3')*1e-6)
 cvbmid=(cvb[:-1]+cvb[1:])/2
 Cv=nbmid*cvbmid
 Ntherm=cvbmid/(1.5*KB_ERG_K)
 assert np.all(Ntherm>0)
 Tmid=(arr(h,'T_K')[:-1]+arr(h,'T_K')[1:])/2
 rho=(arr(h,'nHref_over_nb')[:-1]+arr(h,'nHref_over_nb')[1:])/2

 selected=arr(s,'FS_low_e_heat_kinematic_eV_per_b')
 primary_sel=arr(s,'total_primary_e_eV_per_b')
 primary_all=arr(p,'conditional_all_species_primary_e_eV_per_b')
 unselected=primary_all-primary_sel
 # Genuine original source support: no loss-of-measure or negative remaining energy
 assert np.all(unselected>=-1e-28)
 assert np.all(selected>=-1e-35)
 assert np.all(primary_sel>=selected-1e-28)
 assert np.all(primary_all>=primary_sel-1e-28)
 unselected=np.maximum(unselected,0)
 terminal_ub=selected+unselected
 selected_high=primary_sel-selected
 # These are three distinct energy budgets, not one bound on total heating.
 # 1. selected low-first-generation terminal component,
 # 2. maximum possible low-first-generation component after adding all unselected energy,
 # 3. all-primary-electron energy (ceiling if ALL primary energy became heat).
 assert np.all(selected_high>=-1e-28)
 assert np.all(terminal_ub<=primary_all+1e-28)
 assert np.all(terminal_ub<=primary_all*(1+1e-11)+1e-32)

 pri_e=arr(p,'delta_ne_HHe_per_b_s')*dt
 sum_abs=arr(p,'directwindow_LiII_2E1_HI_counts_upper_per_b')+arr(p,'directwindow_LiII_2E1_HeI_counts_upper_per_b')+arr(p,'directwindow_LiII_2E1_HeII_counts_upper_per_b')
 assert np.max(np.abs(pri_e-sum_abs))<1e-23  # charge from 3 HHe primary absorption channels
 sec_selected=arr(s,'discrete_H_secondary_max_count_per_b')
 sec_ub=sec_selected+unselected/CHI_H_Ev
 assert np.all(sec_selected>=0) and np.all(sec_ub>=sec_selected)

 qlow=selected*EV_ERG*nbmid/dt
 qhi=terminal_ub*EV_ERG*nbmid/dt
 heat_low=qlow/Cv
 heat_hi=qhi/Cv
 heat_all=primary_all*EV_ERG*nbmid/dt/Cv
 assert np.all(heat_all>=heat_hi-1e-40)
 loading=-Tmid/Ntherm*arr(p,'delta_ne_HHe_per_b_s')
 formal_low=heat_low+loading
 formal_hi=heat_hi+loading
 bridge=(arr(t,'formal_total_Tdot_bridge_K_s')[:-1]+arr(t,'formal_total_Tdot_bridge_K_s')[1:])/2
 binding=(arr(t,'delta_chemical_binding_erg_cm3_s')[:-1]+arr(t,'delta_chemical_binding_erg_cm3_s')[1:])/2
 bridge_abs=np.abs(bridge)
 ratio_hi=np.divide(heat_hi,bridge_abs,out=np.zeros_like(heat_hi),where=bridge_abs>0)

 cumul_sel=np.cumsum(selected)
 cumul_hi=np.cumsum(terminal_ub)
 # This row-level envelope counts all unselected primary kinetic energy as terminal thermal energy.
 # It is a rigorously conservative upper envelope ONLY in the frozen discrete kernel, no real epsilon(E,x) estimate.
 result=pd.DataFrame(dict(
 arrival_interval=np.arange(192),z_mid=zmid,ln_a_mid=xmid,H_mid_per_s=Hmid,proper_interval_s=dt,
 clock_rel_to_PR298=clock_rel,clock_midpoint_Hdt_dx_minus_1=clock_disc,
 n_b_mid_per_cm3=nbmid,nHref_over_nb_mid=rho,T_BASS_mid_K=Tmid,
 N_thermal_BASS21_per_baryon=Ntherm,Cv_BASS21_per_baryon_erg_per_K=cvbmid,
 conditional_terminal_selected_low_e_eV_per_b=selected,
 conditional_terminal_unselected_unknown_e_upper_eV_per_b=unselected,
 conditional_terminal_low_e_upper_eV_per_b=terminal_ub,
 conditional_total_primary_energy_all_eV_per_b=primary_all,
 conditional_selected_high_Ee_eV_per_b=selected_high,
 conditional_all_primary_to_heat_energy_ceiling_eV_per_b=primary_all,
 selected_low_e_cumulative_eV_per_b=cumul_sel,terminal_upper_cumulative_eV_per_b=cumul_hi,
 conditional_HHe_primary_electrons_per_b=pri_e,
 conditional_HHe_primary_electron_rate_per_b_s=arr(p,'delta_ne_HHe_per_b_s'),
 conditional_discrete_H_secondary_selected_upper_per_b=sec_selected,
 conditional_H_secondary_all_upper_per_b=sec_ub,
 terminal_Q_selected_erg_cm3_s=qlow,terminal_Q_upper_erg_cm3_s=qhi,
 terminal_Tdot_selected_K_s=heat_low,terminal_Tdot_upper_K_s=heat_hi,
 conditional_all_primary_to_heat_Tdot_ceiling_K_s=heat_all,
 hypothetical_instant_electron_loading_Tdot_K_s=loading,
 hypothetical_coupled_Tdot_selected_K_s=formal_low,
 hypothetical_coupled_Tdot_upper_K_s=formal_hi,
 original_hybrid_source_replacement_formal_Tdot_K_s=bridge,
 terminal_Tdot_upper_over_hybrid_abs=ratio_hi,
 original_hybrid_binding_source_erg_cm3_s=binding,
 source_status=['SOURCE_DISJOINT_PR299_HYBRID_VS_PR300_CONDITIONAL_2E1_NOT_ADDED_TO_NATIVE_FJ']*192
 ))
 (OUT/'CROSS_OWNER_TERMINAL_THERMAL_192.csv').write_text(result.to_csv(index=False,float_format='%.17g',lineterminator='\n'))
 # Record exact scientific results without treating the signed tangency exposure as evolving chemistry.
 hybrid_e_signed= float(arr(t,'cumulative_delta_electron_source_trap_per_baryon')[-1])
 hyb_bind_signed=float(arr(t,'cumulative_delta_binding_erg_per_baryon_trap')[-1])
 all_pri=float(np.sum(pri_e))
 all_secondary_upper=float(np.sum(sec_ub))
 sel_ev=float(np.sum(selected)); hi_ev=float(np.sum(terminal_ub))
 thermal_response_ratio_hi=hi_ev*EV_ERG/abs(hyb_bind_signed)
 result_summary={
 'science_unit':'F4_PR299_PR300_CAUSAL_TERMINAL_THERMAL_ELECTRON_CLOCK_CROSSWALK',
 'source_prs':{'hybrid':298,'tangency':299,'causal':297,'terminal':300},
 'samples':{'source_epochs':193,'arrival_intervals':192,'selected_emission_epochs':30,'FS_source_kernel_rows':3554},
 'input_sha256':SOURCE_LOCK,
 'source_assumptions':{
 'gas':'original BASS193 frozen states', 'photon':'Ferrett singlet source conditional upper',
 'thermalization':'FS2010 E<10.2 eV FIRST-GENERATION terminal; unselected all E only upper bound on missing first-generation low-E energy; selected high-E future cascade deliberately outside this upper',
 'number_loading':'independent immediate-electron-thermal-pool hypothesis; not admitted',
 'causal_clock':'PR297 proper interval = PR298 BASS saved elapsed time differences',
 'source_ownership':'NOT admitted for additive or replacement combined physical evolution',
 'upper_scope':'FS_low_e upper is only FIRST-GENERATION subthreshold energy; total eventual primary-electron thermal ceiling uses total primary energy',
 'anisotropic_K':'NOT bound; no Bianchi directional photon transport',
 'no_new_ivps':True},
 'source_clock':{'max_relative_dt_mismatch':float(clock_rel.max()),'max_Hdt_over_dx_midpoint_defect':float(np.max(np.abs(clock_disc)))},
 'energies':{
 'FS_selected_low_kin_eV_per_b':sel_ev,'FS_all_low_upper_eV_per_b':hi_ev,
 'FS_unselected_primary_e_upper_eV_per_b':float(np.sum(unselected)),
 'FS_selected_high_e_eV_per_b':float(np.sum(selected_high)),
 'PR297_all_primary_kin_eV_per_b':float(np.sum(primary_all)),
 'original_PR299_signed_binding_exposure_erg_per_b':hyb_bind_signed,
 'terminal_upper_erg_per_b':hi_ev*EV_ERG,
 'max_abs_terminal_to_hybrid_signed_binding_ratio':thermal_response_ratio_hi},
 'electron_counts':{
 'PR297_conditional_HHe_primary_count_per_b':all_pri,
 'FS_conditional_H_secondary_upper_per_b':all_secondary_upper,
 'primary_plus_secondary_upper_per_b':all_pri+all_secondary_upper,
 'PR299_signed_hybrid_source_electron_exposure_per_b':hybrid_e_signed,
 'max_ratio_to_PR299_frozen_signed_electron_exposure':(all_pri+all_secondary_upper)/abs(hybrid_e_signed)},
 'thermal':{
 'max_terminal_heat_rate_K_s':float(np.max(heat_hi)),
 'max_immediate_e_loading_magnitude_K_s':float(np.max(np.abs(loading))),
 'max_hybrid_replacement_formal_rate_magnitude_K_s':float(np.max(np.abs(bridge))),
 'max_pointwise_terminal_vs_hybrid_formal_Tdot_ratio':float(np.max(ratio_hi)),
 'frozen_terminal_selected_Tdot_exposure_K':float(np.sum(heat_low*dt)),
 'frozen_terminal_upper_Tdot_exposure_K':float(np.sum(heat_hi*dt)),
 'frozen_all_primary_energy_Tdot_ceiling_exposure_K':float(np.sum(heat_all*dt)),
 'max_all_primary_energy_Tdot_ceiling_K_s':float(np.max(heat_all)),
 'frozen_electron_loading_exposure_K':float(np.sum(loading*dt))},
 'admission':{'Working':'33/88','Central':'28/88','PhysicalFast':'4/7','CanonicalDelta':0,'Auxiliary':'1/1 scoped','F4':'PARTIAL','L4':False,'Production':'HOLD','native_REI17':'NOT_RUN','R6_C9_distinct_author':'NOT_RUN'}
 }
 (OUT/'SCIENCE_RESULTS.json').write_text(json.dumps(result_summary,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n')
 return result,result_summary

if __name__=='__main__':
 _,rs=compute()
 print(json.dumps({k:rs[k] for k in ['samples','source_clock','energies','electron_counts','thermal','admission']},indent=2))
