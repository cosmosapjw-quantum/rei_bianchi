#!/usr/bin/env python3
"""Read-only cross-PR source owner bridge on 192 original BASS193 arrival intervals.
No IVP, no native REI17 transport or rate mutation, no assumption of deposited heat.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, io, json, zipfile
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
EV_ERG=1.602176634e-12  # erg/eV (exact definition)
KB_ERG=1.380649e-16     # erg/K (exact definition)
P294='REI_F4_SPIN_BOUNDED_CAUSAL_BRIDGE_20261030'
P295='REI_F4_REI_HHE_THERMAL_SOURCE_20261030'
CH_BASS=np.array([13.6,24.59,54.42],float) # original BASS21 H,He I,He II (eV)
CH_REI=np.array([13.598434599702,24.587389011,54.41776],float) # REI Rust Grackle (eV)
ABS=['conditional_H_I_ionization_rectangle_upper','conditional_He_I_ionization_rectangle_upper','conditional_He_II_ionization_rectangle_upper']


def sha(path:Path)->str:
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def assert_locked_source(path:Path, expected_sha256:str, expected_bytes:int):
    if sha(path)!=expected_sha256 or path.stat().st_size!=expected_bytes:
        raise AssertionError('SOURCE_LOCK_MISMATCH:'+path.name)


def _read_csv(z:zipfile.ZipFile, member:str)->pd.DataFrame:
    return pd.read_csv(io.BytesIO(z.read(member)))


def load():
    locks=json.loads((ROOT/'evidence'/'SOURCE_LOCK.json').read_text())
    for stem in ('PR294_FULL.zip','PR295_FULL.zip'):
        assert_locked_source(ROOT/'source'/stem,locks[stem]['sha256'],locks[stem]['bytes'])
    with zipfile.ZipFile(ROOT/'source'/'PR294_FULL.zip') as z:
        assert z.testzip() is None
        a=_read_csv(z,f'{P294}/results/CAUSAL_SPIN_BOUND_ARRIVALS_192.csv')
        emission=_read_csv(z,f'{P294}/results/EMITTED_SPIN_ENVELOPE_193.csv')
        parent294=json.loads(z.read(f'{P294}/results/RESULT.json'))
    with zipfile.ZipFile(ROOT/'source'/'PR295_FULL.zip') as z:
        assert z.testzip() is None
        h=_read_csv(z,f'{P295}/results/HHE_IGM_THERMAL_193.csv')
        ev=_read_csv(z,f'{P295}/results/HHE_IGM_EVENTS_579.csv')
        parent295=json.loads(z.read(f'{P295}/results/RESULT.json'))
    return a,emission,h,ev,parent294,parent295


def compute(write=True):
    arr, em, h, events, p294, p295=load()
    assert len(arr)==192 and len(em)==len(h)==193 and len(events)==579
    assert np.max(abs(arr.z_high.to_numpy()-h.z.to_numpy()[:-1]))<1e-10
    assert np.max(abs(arr.z_low.to_numpy()-h.z.to_numpy()[1:]))<1e-10
    assert np.max(abs(np.diff(h.proper_elapsed_s.to_numpy())/arr.proper_interval_s.to_numpy()-1))<1e-10
    nHref=h.nHref_over_nb.to_numpy()[:-1]
    dt=arr.proper_interval_s.to_numpy()
    z=arr.z_high.to_numpy()
    T=h.T_BASS_saved_K.to_numpy()[:-1]
    cv=h.REI_HHe_Cv_erg_per_Href_per_K.to_numpy()[:-1]
    neH=h.ne_HHe_cm3.to_numpy()[:-1]
    nH=h.nHref_cm3.to_numpy()[:-1]
    nHe=h.nHe4_cm3.to_numpy()[:-1]
    eta=(nH+nHe+neH)/nH
    assert np.all(nHref>0)&np.all(dt>0)&np.all(T>0)&np.all(cv>0)
    assert np.max(abs(cv/(1.5*KB_ERG*eta)-1))<2e-12
    N=arr[ABS].to_numpy(float) # per original baryon/arrival interval
    Li=arr.conditional_Li_I_ionization_rectangle_upper.to_numpy(float)
    Ntotal=arr.singlet_2E1_directwindow_ionizations_rectangle_splitting_upper.to_numpy(float)
    assert np.min(N)>=0 and np.min(Li)>=0
    assert np.allclose(N.sum(axis=1)+Li,Ntotal,rtol=2e-12,atol=1e-28)
    rates=N/dt[:,None] # source per original baryon / s
    H,He1,He2=rates.T
    F=np.stack([-H,H,-He1,He1-He2,He2],axis=1) # H I,H II,He I,He II,He III; per baryon s
    q5=np.array([0.,1.,0.,1.,2.])
    AH=np.array([1.,1.,0.,0.,0.]);AHe=np.array([0.,0.,1.,1.,1.])
    ne_rate_b=F@q5
    ne_rate_Href=ne_rate_b/nHref
    assert np.max(abs(F@AH))<1e-35 and np.max(abs(F@AHe))<1e-35
    assert np.allclose(ne_rate_b,rates.sum(axis=1),rtol=1e-13,atol=1e-35)
    primary=arr.conditional_primary_electron_eV_rectangle_upper.to_numpy(float)
    bind_parent=arr.conditional_binding_eV_rectangle_upper.to_numpy(float)
    assert np.min(primary)>=0 and np.min(bind_parent)>=0
    bass_binding_hhe=N@CH_BASS
    rei_binding_hhe=N@CH_REI
    delta_binding=rei_binding_hhe-bass_binding_hhe
    leftover_binding=bind_parent-bass_binding_hhe
    assert np.min(leftover_binding)>-2e-24 # includes Li I (not silently zero)
    assert np.max(abs(delta_binding-(N@(CH_REI-CH_BASS))))<5e-26
    # Conservative HHe thermal upper uses ALL primary electrons (including tiny Li I contribution)
    # which upper-bounds HHe primary thermal input. Unknown deposition fractions are not assigned.
    q_p_eV_b_s=primary/dt
    q_p_erg_Href_s=q_p_eV_b_s*EV_ERG/nHref
    # Energy-cone bound for any additional H/He secondary collisional ionizations:
    # each costs at least chi_HI(REI) eV from the same photoelectron energy reservoir.
    # This is a rigorous relaxed energy upper, not a predicted Monte-Carlo yield.
    secondary_max_per_b=primary/float(CH_REI[0])
    secondary_max_per_Href_s=secondary_max_per_b/(dt*nHref)
    heat_upper_K_s=q_p_erg_Href_s/cv
    loading_K_s=-T*ne_rate_Href/eta
    upper_fixed_source_K_s=heat_upper_K_s+loading_K_s
    assert np.min(heat_upper_K_s)>=0 and np.max(loading_K_s)<=0
    # Unknown amplitude of real 1S source (0 .. sourceU) and unknown heat fraction
    # implies conservative independent extrema [-|loading_U|, heat_U].
    rigorous_Tdot_lower=-T*(ne_rate_Href+secondary_max_per_Href_s)/eta
    rigorous_Tdot_upper=heat_upper_K_s
    # These are not simultaneous confidence bounds for lab data and are not a solved thermal trajectory.
    delta_owner_erg_Href_s=delta_binding*EV_ERG/(nHref*dt)
    hhe_source_photo = h.REI_HHe_primary_heat_erg_per_Href_s.to_numpy()[:-1]
    core_ratio=np.divide(q_p_erg_Href_s,hhe_source_photo,out=np.full_like(q_p_erg_Href_s,np.nan),where=hhe_source_photo>0)
    output=pd.DataFrame(dict(
       arrival_interval=arr.arrival_interval.astype(int),z_high=arr.z_high,z_low=arr.z_low,
       proper_interval_s=dt,nHref_over_nb=nHref,T_BASS_saved_K=T,eta_HHe_particles_per_Href=eta,
       native_BASS_original_HHe_photoheat_erg_per_Href_s=hhe_source_photo,
       directwindow_LiII_2E1_HI_counts_upper_per_b=N[:,0],
       directwindow_LiII_2E1_HeI_counts_upper_per_b=N[:,1],
       directwindow_LiII_2E1_HeII_counts_upper_per_b=N[:,2],
       directwindow_LiII_2E1_LiI_counts_upper_per_b=Li,
       delta_F_HI_per_b_s=F[:,0],delta_F_HII_per_b_s=F[:,1],
       delta_F_HeI_per_b_s=F[:,2],delta_F_HeII_per_b_s=F[:,3],delta_F_HeIII_per_b_s=F[:,4],
       delta_ne_HHe_per_b_s=ne_rate_b,
       delta_ne_HHe_per_Href_s=ne_rate_Href,
       delta_ne_LiI_excluded_from_REI_HHe_F5_per_b_s=Li/dt,
       maximum_additional_HHe_secondary_ionizations_per_b_energy_cap=secondary_max_per_b,
       maximum_additional_HHe_secondary_ionizations_per_Href_s_energy_cap=secondary_max_per_Href_s,
       total_primary_plus_secondary_HHe_electron_source_rate_upper_per_Href_s=ne_rate_Href+secondary_max_per_Href_s,
       conditional_all_species_primary_e_eV_per_b=primary,
       conditional_primary_upper_erg_per_Href_s=q_p_erg_Href_s,
       HHe_Cv_erg_per_Href_K=cv,
       delta_Tdot_primary_K_s_if_all_primary_to_heat_upper=heat_upper_K_s,
       delta_Tdot_HHe_electron_loading_K_s=loading_K_s,
       delta_Tdot_frozen_source_if_all_primary_heat_upper_K_s=upper_fixed_source_K_s,
       delta_Tdot_conservative_lower_K_s=rigorous_Tdot_lower,
       delta_Tdot_conservative_upper_K_s=rigorous_Tdot_upper,
       delta_REI_binding_minus_BASS_HHe_eV_per_b=delta_binding,
       delta_REI_binding_minus_BASS_HHe_erg_per_Href_s=delta_owner_erg_Href_s,
       conditional_BASS_HHe_binding_eV_per_b=bass_binding_hhe,
       conditional_REI_HHe_binding_eV_per_b=rei_binding_hhe,
       conditional_parent_binding_remainder_LiI_eV_per_b=leftover_binding,
       conditional_original_Li2E1_all_primary_to_original_HHe_photoheat_ratio=core_ratio,
       source_status='CONDITIONAL_SPIN_UPPER_FROZEN_FIRST_FLIGHT__NOT_INJECTED_IN_NATIVE_FJ',
       epsilon_status='NO_SECONDARY_DEPOSITION_OWNER__0_TO_1_COEFFICIENT_ONLY',
       background_status='BASS_SAVED193_PROPER_CLOCK_H_T_NHREF__NOT_SAME_REI17_IC'
    ))
    integral_hhe=N.sum(axis=0)
    total_HHe=float(integral_hhe.sum())
    integrated_heat=float(np.sum(q_p_erg_Href_s*dt))
    integrated_owner_defect=float(np.sum(delta_owner_erg_Href_s*dt))
    original_baseline=float(np.trapezoid(h.REI_HHe_primary_heat_erg_per_Href_s,h.proper_elapsed_s))
    expected_source=float(Ntotal.sum())
    summary={
      'schema':'REI_F4_CAUSAL_LI2E1_REI_HHE_FROZEN_SOURCE_V1',
      'science_unit':'SOURCE_COMMON_FROZEN_HHE_PHOTO_RHS_AND_EOS_RESPONSE',
      'verified_source_zip_sha256':{v:sha(ROOT/'source'/v) for v in ['PR294_FULL.zip','PR295_FULL.zip']},
      'input_rows':{'BASS193':193,'PR294_arrival_intervals':192,'PR295_HHe_event_rows':579,'PR294_conditional_BASS_event_rows':1158,'new_cosmic_IVP':0},
      'physical_outputs':{
        'H_I_conditional_photo_events_per_baryon_upper':float(integral_hhe[0]),
        'He_I_conditional_photo_events_per_baryon_upper':float(integral_hhe[1]),
        'He_II_conditional_photo_events_per_baryon_upper':float(integral_hhe[2]),
        'Li_I_conditional_photo_events_per_baryon_upper_separate':float(Li.sum()),
        'HHe_conditional_photo_events_per_baryon_upper':total_HHe,
        'all_conditional_photo_events_per_baryon_upper':expected_source,
        'all_conditional_primary_e_eV_per_baryon_upper':float(primary.sum()),
        'secondary_HHe_ionizations_energy_ceiling_per_baryon':float(secondary_max_per_b.sum()),
        'primary_plus_secondary_HHe_ionizations_energy_ceiling_per_baryon':float(total_HHe+secondary_max_per_b.sum()),
        'min_conditional_temperature_RHS_with_secondary_energy_ceiling_K_s':float(rigorous_Tdot_lower.min()),
        'upper_conditional_temperature_RHS_with_unknown_heat_K_s':float(rigorous_Tdot_upper.max()),
        'all_primary_heat_upper_erg_per_Href':integrated_heat,
        'baseline_REI_HHe_original_photo_primary_erg_per_Href':original_baseline,
        'ratio_all_primary_upper_to_baseline_original_HHe_primary':integrated_heat/original_baseline,
        'max_conditional_HHe_electron_injection_per_Href_s':float(ne_rate_Href.max()),
        'max_conditional_primary_heat_coefficient_K_s':float(heat_upper_K_s.max()),
        'min_conditional_electron_loading_K_s':float(loading_K_s.min()),
        'max_conditional_all_primary_unitheat_plus_loading_K_s':float(upper_fixed_source_K_s.max()),
        'min_conditional_all_primary_unitheat_plus_loading_K_s':float(upper_fixed_source_K_s.min()),
        'integrated_source_REI_minus_BASS_threshold_defect_erg_per_Href':integrated_owner_defect,
        'integrated_source_REI_minus_BASS_threshold_defect_eV_per_b':float(delta_binding.sum()),
        'max_absolute_HHe_nuclear_conservation_error_per_b_s':float(max(np.max(abs(F@AH)),np.max(abs(F@AHe)))),
        'max_absolute_HHe_electron_stoich_error_per_b_s':float(np.max(abs(ne_rate_b-rates.sum(axis=1)))),
        'max_relative_proper_interval_mismatch':float(np.max(abs(np.diff(h.proper_elapsed_s.to_numpy())/dt-1))),
        'max_relative_Cv_EOS_mismatch':float(np.max(abs(cv/(1.5*KB_ERG*eta)-1))),
        'cumulative_photo_HHe_counts_per_Href':float(np.sum(N.sum(axis=1)/nHref)),
      },
      'qualifications':{
        'Ferrett_operator':'CONDITIONAL_K_NATIVE_EQ_LAB_N2PLUSN3_UNRESOLVED',
        'Li_1S':'NO_POSITIVE_LOWER_BOUND; FERRETT_DIRECT_R31_R32_RECTANGLE_MAX',
        'REI_HHe_FJ':'SOURCE_TRANSLATED_5STATE_POINT_MODEL_ONLY; TRUE_REI17_J_UNBOUND',
        'new_li2e1_photo_port':'FROZEN_NO_FEEDBACK; POSSIBLE_UV_SOURCE_OVERLAP_UNCHECKED',
        'secondary_electron_heat_fraction':'UNBOUND; CONSERVATIVE_0_TO_1_ENVELOPE_NOT_MONTE_CARLO_INPUT',
        'secondary_HHe_ionizations':'ENERGY_ONLY_CEILING_EKIN/CHI_HI_REI; no species partition and no extra external energy',
        'chemistry':'NO_REPLACEMENT_OR_ADDITION_TO_NATIVE_F; NO_NEW_IVP',
        'energy':'OWNER_THRESHOLD_DIFFERENCE_EXPLICIT; LiI_PRIMARY_INCLUDED_IN_CONSERVATIVE_HEAT_CAP',
        'background':'BASS193_PROPER_TIME_ONLY; ANISOTROPIC_DIRECTIONAL_K_UNBOUND',
        'distinct_author_R6_C9':'NOT_RUN',
      },
      'gates':{'WORKING':'33/88','CENTRAL':'28/88','F4_FAST':'4/7','CANONICAL_DELTA':0,'AUXILIARY_NEW_UNIT':'1/1_SCOPED',
         'F4':'PARTIAL','L4_ready':False,'NO_MORE_IVPS':True,'NO_MERGE':True,'NO_FORCE_PUSH':True,
         'AUTO_NEXT_NODE':False,'PRODUCTION':'HOLD'}
    }
    if write:
        OUT.mkdir(parents=True,exist_ok=True)
        output.to_csv(OUT/'LI2E1_HHE_CAUSAL_SOURCE_192.csv',index=False,float_format='%.17g')
        em.to_csv(OUT/'PR294_ORIGINAL_SPIN_EMISSION_193_READONLY.csv',index=False,float_format='%.17g')
        (OUT/'RESULT.json').write_text(json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    return output,summary

if __name__=='__main__':
    _,res=compute(True)
    print(json.dumps(res['physical_outputs'],indent=2,sort_keys=True))
