#!/usr/bin/env python3
"""Original BASS193 Li II 2E1 first-flight causal response, not a native REI17 F/J.

Every stored source event is a first-generation photoabsorption from original PR302.
Rows are historical transport observations on an immutable frozen BASS21 background.
The optical response K is linear in emission pair counts only at that background.
No differential simulation, real gas heating, model closure, or photon-source mutation.
"""
from __future__ import annotations
import hashlib, json, sys, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
S=ROOT/'input'; BS=ROOT/'source_bass'; O=ROOT/'results'
O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'code'))
from fs2010_reference import FS2010, XI
SPECIES=('H_I','He_I','He_II','Li_I')
BANDS=('e0_10p2','e10p2_13p6','e13p6_24p59','e24p59_54p42','e54p42_plus')
LIMITS=((0.,10.2),(10.2,13.598434599702),(13.598434599702,24.587389011),(24.587389011,54.41776),(54.41776,60.922559447552))
EV_ERG=1.602176634e-12
YR_S=31557600.
EXPECTED={
 'input/PUBLIC_results_FULL193_KERNEL_18528.csv':'d7ca818ce55835f8c38408e4c575f42d6529d6e225aab346fad76709b4354538',
 'input/PUBLIC_results_FULL193_ARRIVAL_192.csv':'155c70c1c4363d75db46b6898eca6bbf9496bc3cdd586b6cf0994fa2384df6df',
 'input/PUBLIC_results_FULL193_HHE_TERMINAL_THERMAL_192.csv':'292a23d3034b073442900f8fcacef05ad85544720cb6edf9fb5973352a58b3e6',
 'input/BASS193_FS2010_SPECIES_COMPAT_192.csv':'dd0b2ba58effb6ee5929a7091b4b2a91fa172e2d26df7a85dc858ff53f7c1a09',
 'input/FS2010_NATIVE_CROSSWALK_192.csv':'f52689f0332a7e81395d24046c24fe4b5327a1922de5c672400a803ed0172c34',
 'input/FS2010_BANDS_3840.csv':'0911237a669d13535e37f4777dd1201024c099c99db8859987e8889e6a28e937',
 'source_bass/trajectory.npz':'37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086',
 'source_bass/PR293_SOURCE_FJ21_193.npz':'487ee365a3ff2a88921b3bab5dec8f1c28caf7cf75e9e0b4b538017839fa09ae',
 'source/elec_interp.tar':'e9760d637b5bd97fe981cb459a7e2d733692a9f9f8deb9a757224b14be632101'
}
def sha(path:Path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ensure_identity():
 for name,h in EXPECTED.items():
  assert sha(ROOT/name)==h,('IMMUTABLE_SOURCE_SHA',name,sha(ROOT/name),h)
 assert not zipfile.is_zipfile(ROOT/'source/elec_interp.tar')  # source is a tar, not zip
 return True

def construct(*,write=True):
 ensure_identity()
 k=pd.read_csv(S/'PUBLIC_results_FULL193_KERNEL_18528.csv')
 a=pd.read_csv(S/'PUBLIC_results_FULL193_ARRIVAL_192.csv')
 th=pd.read_csv(S/'PUBLIC_results_FULL193_HHE_TERMINAL_THERMAL_192.csv')
 b=pd.read_csv(S/'BASS193_FS2010_SPECIES_COMPAT_192.csv')
 prev=pd.read_csv(S/'FS2010_NATIVE_CROSSWALK_192.csv')
 fs=FS2010()
 with np.load(BS/'trajectory.npz',allow_pickle=False) as z:
  tim=z['diagnostics'][:,np.where(z['diagnostic_names']=='elapsed_s')[0][0]].copy()
  z_orig=z['z'].copy();Y=z['Y'].copy();q_orig=z['q'].copy();A_orig=z['A'].copy()
 with np.load(BS/'PR293_SOURCE_FJ21_193.npz',allow_pickle=False) as src:
  f_native=src['F21_per_baryon_s'].copy();jac_native=src['J21_per_s'].copy();q=src['q21'].copy();ba=src['A21'].copy()
 assert k.shape[0]==18528 and a.shape[0]==th.shape[0]==b.shape[0]==prev.shape[0]==192
 assert Y.shape==(193,21) and f_native.shape==(193,21) and jac_native.shape==(193,21,21)
 np.testing.assert_array_equal(q,q_orig)
 np.testing.assert_array_equal(ba,A_orig)
 assert np.max(abs(np.diff(tim)-th.proper_interval_s.to_numpy()))<200.
 assert np.max(abs(np.diff(tim)/th.proper_interval_s.to_numpy()-1))<1e-12
 assert np.max(abs(a.z_high.to_numpy()-z_orig[:-1]))<1e-13
 assert np.max(abs(a.z_low.to_numpy()-z_orig[1:]))<1e-13
 j=k.arrival_interval.to_numpy(int);orig=k.emission_epoch.to_numpy(int)
 assert np.all((0<=orig)&(orig<=j)&(j<192))
 assert len(np.unique(orig*192+j))==18528
 assert (np.bincount(orig,minlength=193)[:192]==np.arange(192,0,-1)).all()
 Q=k.source_emitted_2E1_pairs_per_b.to_numpy(float)
 assert (Q>=0).all()
 n_components=np.empty((len(k),4,5));e_components=np.empty_like(n_components)
 for s,sp in enumerate(SPECIES):
  for ib,band in enumerate(BANDS):
   n_components[:,s,ib]=k[f'{sp}_{band}_counts_per_pair']
   e_components[:,s,ib]=k[f'{sp}_{band}_primary_e_eV_per_pair']
 assert n_components.min()>=-1e-12 and e_components.min()>=-1e-10
 assert np.isfinite(n_components).all() and np.isfinite(e_components).all()
 n_pair=n_components.sum(axis=2)
 e_pair=e_components.sum(axis=2)
 n_species=Q[:,None]*n_pair
 e_species=Q[:,None]*e_pair
 n_link=n_species.sum(axis=1)
 e_link=e_species.sum(axis=1)
 terminal_link=Q*e_components[:,:,0].sum(axis=1)
 N=np.bincount(j,weights=n_link,minlength=192)
 E=np.bincount(j,weights=e_link,minlength=192)
 T=np.bincount(j,weights=terminal_link,minlength=192)
 assert np.max(abs(N-a.total_absorbed_ionizations_per_b.to_numpy()))<2e-24
 assert np.max(abs(E-a.total_primary_e_eV_per_b.to_numpy()))<2e-23
 assert np.max(abs(T-a.FS_low_e_heat_kinematic_eV_per_b.to_numpy()))<2e-23
 # The complete master source includes one last emission Q_192 with no arrival interval before z=2.
 Qsource=np.array([Q[np.flatnonzero(orig==kk)[0]] for kk in range(192)]+[0.],float)
 q_total=float(a.emission_source_pairs_all_epochs_per_b.iloc[0])
 Qsource[-1]=q_total-Qsource[:-1].sum()
 assert Qsource[-1]>=0 and np.max(abs(Q-Qsource[orig]))<1e-20
 per_emission_abs=np.bincount(orig,weights=n_link,minlength=193)
 per_emission_energy=np.bincount(orig,weights=e_link,minlength=193)
 unabsorbed=2*Qsource-per_emission_abs
 assert unabsorbed.min()>-2e-25
 assert np.all(per_emission_abs<=2*Qsource+2e-25)
 unabsorbed=np.maximum(0.,unabsorbed)
 # Causal frozen 2E1 kernel is K_{j,k,s}; there is no current-state local Jacobian closure.
 K_species=n_pair
 K_total=n_pair.sum(axis=1)
 assert np.max(K_total)<=2+1e-12
 # Exact endpoint time windows; an absorption within the jth interval lies between them.
 t_lower=tim[j]-tim[orig]
 t_upper=tim[j+1]-tim[orig]
 assert np.all(t_lower>=0) and np.all(t_upper>=t_lower)
 delay=j-orig
 delayed=(delay>=1)
 old_N=np.bincount(j,weights=n_link*delayed,minlength=192)
 old_E=np.bincount(j,weights=e_link*delayed,minlength=192)
 local_N=N-old_N;local_E=E-old_E
 assert old_N.min()>=0 and local_N.min()>=-2e-25
 # Real rate of tagged Li-II photons in original first-flight model, not inserted into F_BASS.
 dt=th.proper_interval_s.to_numpy()
 rho=th.nHref_over_nb.to_numpy()
 assert np.max(abs(rho/rho[0]-1))<1e-12
 Ndot=N/dt
 nHref_rate=N/(rho*dt)
 rate_nat=f_native[:-1]@q
 assert len(rate_nat)==192
 # Original first-absorption map creates exactly one electron per event in the
 # BASS coarse-grained atomic source, including Li I (NOT a verified Auger yield).
 assert np.max(abs(N-sum(np.bincount(j,weights=n_species[:,i],minlength=192) for i in range(4))))<2e-24
 # Source ownership: construct candidate single tagged port, never mutate legacy F21/J21.
 # FS2010 source-derived projected energy bound: min/max only if native xi domain holds.
 valid=prev.FS_xi_in_native_domain.to_numpy(bool)
 assert int(valid.sum())==87
 coeff_low=np.full((192,5),np.nan)
 coeff_high=np.full_like(coeff_low,np.nan)
 coeff_low[:,0]=coeff_high[:,0]=1.
 for jj in np.flatnonzero(valid):
  lo=min(float(b.xHII_start.iloc[jj]),float(b.xHII_end.iloc[jj]));hi=max(float(b.xHII_start.iloc[jj]),float(b.xHII_end.iloc[jj]))
  for bi in range(1,5):
   f0,f1=fs.extrema(LIMITS[bi][0],LIMITS[bi][1],lo,hi)
   coeff_low[jj,bi]=f0[1];coeff_high[jj,bi]=f1[1]
 heat_min=Q*np.sum(e_components*coeff_low[j][:,None,:],axis=(1,2))
 heat_max=Q*np.sum(e_components*coeff_high[j][:,None,:],axis=(1,2))
 # Explicit invalid-xi bins do not inherit an extrapolated high-energy heat yield.
 heat_min[~valid[j]]=np.nan
 heat_max[~valid[j]]=np.nan
 valid_min=np.bincount(j[valid[j]],weights=heat_min[valid[j]],minlength=192)
 valid_max=np.bincount(j[valid[j]],weights=heat_max[valid[j]],minlength=192)
 assert np.max(abs(valid_min[valid]-prev.fheat_lower.to_numpy()[valid]))<2e-22
 assert np.max(abs(valid_max[valid]-prev.fheat_upper.to_numpy()[valid]))<2e-22
 heat_old_lo=np.bincount(j[valid[j]&delayed],weights=heat_min[valid[j]&delayed],minlength=192)
 heat_old_hi=np.bincount(j[valid[j]&delayed],weights=heat_max[valid[j]&delayed],minlength=192)
 # Re-express proper-clock thermal source into frozen HHe heat capacity (not evolved T).
 cv=th.HHe_Cv_erg_per_Href_K.to_numpy()
 assert (cv>0).all()
 thermal_factor=EV_ERG/(cv*rho)
 # Link output and arrival-owned rates.
 df=pd.DataFrame(dict(emission_epoch=orig,arrival_interval=j,
       z_emission=k.z_emission.to_numpy(),z_arrival=k.z_arrival.to_numpy(),
       source_pairs_per_b=Q,photon_absorption_kernel_per_pair=K_total,
       first_absorption_events_per_b=n_link,primary_electron_energy_eV_per_b=e_link,
       terminal_E_lt10p2_eV_per_b=terminal_link,
       proper_lag_lower_year=t_lower/YR_S,proper_lag_upper_year=t_upper/YR_S,
       emission_age_bins=delay,lagged_from_previous_epoch=delayed,
       conditional_FS_xi_valid=valid[j],FS_heat_lower_eV_per_b=heat_min,
       FS_heat_upper_eV_per_b=heat_max))
 for ii,sp in enumerate(SPECIES):
  df[sp+'_kernel_per_pair']=K_species[:,ii]
  df[sp+'_first_absorption_per_b']=n_species[:,ii]
  df[sp+'_primary_energy_eV_per_b']=e_species[:,ii]
 link_source_total=2*q_total
 memory_count=float(old_N.sum()/N.sum());memory_energy=float(old_E.sum()/E.sum())
 arrival_df=pd.DataFrame(dict(arrival_interval=np.arange(192),z_high=a.z_high,z_low=a.z_low,
     proper_interval_s=dt,source_Href_over_nb=rho,absorption_events_per_b=N,
     local_same_epoch_events_per_b=local_N,delayed_events_per_b=old_N,
     delayed_events_fraction=np.divide(old_N,N,out=np.full(192,np.nan),where=N>0),
     primary_energy_eV_per_b=E,delayed_primary_energy_eV_per_b=old_E,
     delayed_primary_energy_fraction=np.divide(old_E,E,out=np.full(192,np.nan),where=E>0),
     photoelectron_rate_per_b_s=Ndot,photoelectron_rate_per_Href_s=nHref_rate,
     original_BASS_electron_RHS_per_b_s=rate_nat,
     FS_xi_valid=valid,FS_conditional_heat_lower_eV_per_b=np.where(valid,valid_min,np.nan),
     FS_conditional_heat_upper_eV_per_b=np.where(valid,valid_max,np.nan),
     FS_delayed_conditional_heat_lower_eV_per_b=np.where(valid,heat_old_lo,np.nan),
     FS_delayed_conditional_heat_upper_eV_per_b=np.where(valid,heat_old_hi,np.nan),
     FS_frozen_temperature_source_lower_K_s=np.where(valid,valid_min*thermal_factor/dt,np.nan),
     FS_frozen_temperature_source_upper_K_s=np.where(valid,valid_max*thermal_factor/dt,np.nan)))
 emission_df=pd.DataFrame(dict(emission_epoch=np.arange(193),z_emission=z_orig,
    original_conditional_2E1_pairs_per_b=Qsource,
    injected_2E1_photons_per_b=2*Qsource,
    first_absorbed_photons_until_z2_per_b=per_emission_abs,
    not_first_absorbed_by_z2_per_b=unabsorbed,
    first_absorption_fraction_by_z2=np.divide(per_emission_abs,2*Qsource,out=np.full(193,np.nan),where=Qsource>0),
    primary_electron_energy_until_z2_eV_per_b=per_emission_energy))
 # Negative controls: explicitly immutable base F and J, neutron beta column retained.
 assert abs(jac_native[100,2,0]-1/878.4)<1e-15
 assert abs(np.max(abs(np.einsum('j,ijk->ik',ba,jac_native))))<5e-20
 # An optional counterfactual diagonal source loses exactly the delayed, nonnegative mass.
 assert abs(np.sum(N-local_N)-np.sum(old_N))<2e-24
 unmodeled_energy_eV=60.922559447552*q_total-E.sum()
 assert unmodeled_energy_eV>=0
 res={
  'unit':'REI_F4_CAUSAL_MEMORY_PHOTON_SOURCE_20261031',
  'status':'SOURCE_CONDITIONAL_CAUSAL_FIRST_FLIGHT_NOT_NATIVE_FJ',
  'model': 'original 193 BASS21 frozen trajectory × 192/18528 first-flight Li II 2E1 kernel with FS2010 optional single-xi thermal envelope',
  'emission_epochs_all':193,'emission_epochs_before_horizon':192,'arrival_intervals':192,'causal_kernel_grid_links':18528,
  'positive_weighted_kernel_links':int(np.count_nonzero(n_link)),
  'source_pairs_per_original_baryon':q_total,'injected_photons_per_baryon':link_source_total,
  'first_absorptions_per_baryon':float(N.sum()),'not_absorbed_by_z2_per_baryon':float(unabsorbed.sum()),
  'not_first_absorbed_fraction_by_z2':float(unabsorbed.sum()/link_source_total),
  'first_generation_electron_energy_eV_per_baryon':float(E.sum()),
  'lagged_absorption_fraction':memory_count,'lagged_electron_energy_fraction':memory_energy,
  'count_weighted_lag_years_lower_upper':[float(np.dot(n_link,t_lower)/N.sum()/YR_S),float(np.dot(n_link,t_upper)/N.sum()/YR_S)],
  'energy_weighted_lag_years_lower_upper':[float(np.dot(e_link,t_lower)/E.sum()/YR_S),float(np.dot(e_link,t_upper)/E.sum()/YR_S)],
  'per_arrival_bins_lagged_majority':int(np.sum(old_N>N/2)),
  'delayed_majority_bins_share_of_all_absorptions':float(N[old_N>N/2].sum()/N.sum()),
  'first_absorptions_by_absorber_per_baryon':{sp:float(n_species[:,idx].sum()) for idx,sp in enumerate(SPECIES)},
  'first_primary_electron_energy_by_absorber_eV_per_baryon':{sp:float(e_species[:,idx].sum()) for idx,sp in enumerate(SPECIES)},
  'peak_photoelectron_rate_per_baryon_s':float(Ndot.max()),
  'peak_photoelectron_rate_arrival_interval':int(Ndot.argmax()),
  'max_arrival_clock_relative_mismatch':float(np.max(abs(np.diff(tim)/dt-1))),
  'photon_to_electron_source_charge_per_event':1,
  'native_bass21_source_unchanged':True,'neutron_weak_jacobian_retained':True,
  'FS_conditional_valid_arrivals':int(valid.sum()),
  'FS_conditional_total_heat_eV_per_baryon':[float(valid_min.sum()),float(valid_max.sum())],
  'FS_conditional_delayed_heat_eV_per_baryon_bounds':[float(heat_old_lo.sum()),float(heat_old_hi.sum())],
  'FS_conditional_delayed_heat_fraction_bounds':[float(heat_old_lo.sum()/valid_max.sum()),float(heat_old_hi.sum()/valid_min.sum())],
  'unpartitioned_emitted_photon_energy_minus_primary_kinetic_eV_per_b':float(unmodeled_energy_eV),
  'unpartitioned_energy_explanation':'Contains binding, cosmological redshift and unabsorbed photons; not actual heat',
  'scope_and_nonpromotions':['source conditional singlet upper, not measured LiII abundance',
    'unchanged optical opacity/history; K is not full state-response Jacobian',
    'single-xi FS thermal response applies to a counterfactual manifold, not BASS multi-ion chemistry',
    'source ports are diagnostics awaiting source replacement; not added to native BASS or REI RHS',
    'no new IVP, no F4/L4 production closure, no CMB or actual evolved DeltaT'],
  'DAG':{'working':'33/88','central':'28/88','physical_fast':'4/7','canonical_physical_delta':0,'F4':'PARTIAL','L4_ready':False,'production':'HOLD'},
  'source_expected_sha256':EXPECTED
 }
 if write:
  df.to_csv(O/'CAUSAL_EMISSION_ARRIVAL_18528.csv',index=False,float_format='%.17g')
  arrival_df.to_csv(O/'CAUSAL_ARRIVAL_CLOCK_SOURCE_192.csv',index=False,float_format='%.17g')
  emission_df.to_csv(O/'CAUSAL_EMISSION_SURVIVAL_193.csv',index=False,float_format='%.17g')
  (O/'RESULTS.json').write_text(json.dumps(res,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
 return res,df,arrival_df,emission_df

if __name__=='__main__':print(json.dumps(construct()[0],indent=2))
