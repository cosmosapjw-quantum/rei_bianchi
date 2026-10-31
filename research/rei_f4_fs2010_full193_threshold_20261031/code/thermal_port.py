#!/usr/bin/env python3
"""Only model-assigned terminal (<10.2 eV) energy on original BASS193 frozen REI H/He thermal EOS.

A point *coefficient* (not a new IVP / not an admitted physical lower heat bound).
Only conditional Ferrett maximum singlet source is evaluated.
"""
import io,zipfile,json
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
PR300=ROOT/'source'/'PR300_FULL.zip'
EV_ERG=1.602176634e-12

def compute():
 d=pd.read_csv(ROOT/'results'/'FS2010_FULL193_ARRIVAL_192.csv')
 with zipfile.ZipFile(PR300) as z:
  raw=z.read('REI_F4_FS2010_LOW_E_THRESHOLD_20261031/source/PR297_FULL.zip')
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  parent=pd.read_csv(io.BytesIO(z.read('REI_F4_LI2E1_HHE_CAUSAL_POINT_SOURCE_20261031/results/LI2E1_HHE_CAUSAL_SOURCE_192.csv')))
 assert len(d)==len(parent)==192
 assert np.max(abs(d.z_high-parent.z_high))<1e-12
 assert np.max(abs(d.z_low-parent.z_low))<1e-12
 n=parent.nHref_over_nb.to_numpy();dt=parent.proper_interval_s.to_numpy()
 cv=parent.HHe_Cv_erg_per_Href_K.to_numpy();eta=parent.eta_HHe_particles_per_Href.to_numpy();T=parent.T_BASS_saved_K.to_numpy()
 assert np.all(n>0)&np.all(dt>0)&np.all(cv>0)&np.all(eta>0)&np.all(T>0)
 e=d.FS_low_e_heat_kinematic_eV_per_b.to_numpy();tot=d.total_primary_e_eV_per_b.to_numpy()
 assert np.all(e>=0)&np.all(e<=tot+1e-20)
 hrate=e*EV_ERG/(n*dt)
 Tdot=hrate/cv
 # Original H/He electron loading from primary photoelectrons, NOT a FS electron yield.
 load=parent.delta_Tdot_HHe_electron_loading_K_s.to_numpy()
 upper=parent.delta_Tdot_conservative_upper_K_s.to_numpy()
 # independent original all-primary upper energy normalization
 own=parent.conditional_all_species_primary_e_eV_per_b.to_numpy()
 assert np.allclose(own,tot,rtol=2e-12,atol=2e-24)
 assert np.max(Tdot-upper)<1e-25
 out=pd.DataFrame({'arrival_interval':d.arrival_interval,'z_high':d.z_high,'z_low':d.z_low,
  'proper_interval_s':dt,'nHref_over_nb':n,'T_BASS_saved_K':T,'HHe_Cv_erg_per_Href_K':cv,
  'FS_model_terminal_eV_per_b':e,
  'FS_model_terminal_erg_per_Href_s':hrate,
  'FS_model_terminal_temperature_rhs_coefficient_K_s':Tdot,
  'original_all_primary_unit_heat_temperature_rhs_cap_K_s':upper,
  'original_primary_photoelectron_loading_K_s':load,
  'conditional_electron_source_per_Href_s':parent.delta_ne_HHe_per_Href_s,
  'original_native_HHe_primary_heat_erg_per_Href_s':parent.native_BASS_original_HHe_photoheat_erg_per_Href_s,
  'source_status':'FERRETT_MAX_SINGLET_BASS_FIRSTFLIGHT__MODEL_TERMINAL_HEAT_ONLY__NOT_INJECTED_IN_FJ'})
 out.to_csv(ROOT/'results'/'FS2010_FULL193_HHE_TERMINAL_THERMAL_192.csv',index=False,float_format='%.17g')
 S={'schema':'REI_F4_FS2010_FROZEN_TERMINAL_HHE_EOS_COEFFICIENT_V1',
 'whole_source_terminal_eV_per_baryon':float(e.sum()),
 'cumulative_model_terminal_heat_erg_per_Href':float(np.sum(hrate*dt)),
 'max_model_terminal_photo_temperature_rhs_K_s':float(Tdot.max()),
 'max_original_all_primary_unitheat_temperature_rhs_K_s':float(upper.max()),
 'ratio_total_model_terminal_to_primary_kinetic_energy':float(e.sum()/tot.sum()),
 'max_parent_electron_loading_magnitude_K_s':float(np.max(abs(load))),
 'model':'Furlanetto–Stoever 2010 terminal E<10.2eV classification on conditional Ferrett upper source; not actual IGM heat or evolved T; delayed deposition not assessed; no full 2D fractions',
 'REI17_operator':'UNBOUND','source_ownership':'PR300 frozen original BASS chemistry and PR297 HHe source read-only; no new F,J source injection'}
 (ROOT/'results'/'THERMAL_COEFFICIENT.json').write_text(json.dumps(S,indent=2,sort_keys=True)+'\n')
 return out,S
if __name__=='__main__':
 _,s=compute();print(json.dumps(s,indent=2))
