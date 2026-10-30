"""Li I 1s final-state kinematics applied to the *original* 193 BASS epochs.

No photo-Auger, fluorescence yields or thermalization are invented. The BASS
single-ionization photo cross sections and source populations are immutable;
NIST level thresholds are independent external atomic data, not BASS-fitted rates.
This is a conditional model-comparison diagnostic, not a source-closed cascade.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import tempfile
import zipfile
from pathlib import Path

import numpy as np
from scipy.integrate import cumulative_simpson

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/'source/PR277_FULL.zip'
ORIGINAL_SHA='6a5794996b0fe0473558bc07c866f2f3f0315cb72aef9b284e805cd40ba897a8'
BASS_SHA='cc602e209e7deeb511ab2a1f3b2268d55206c43c'
BASS_K_EDGE_EV=64.39
BASS_VALENCE_EV=5.392
BASS_CORE_EV=BASS_K_EDGE_EV-BASS_VALENCE_EV
# Exact SI constants, NIST Atomic Spectra Database levels, in cm^-1 above Li+ ground.
H_J_S=6.62607015e-34
C_M_S=299792458.0
ELECTRONVOLT_J=1.602176634e-19
EV_ERG=1.602176634e-12
CM1_TO_EV=H_J_S*C_M_S*100./ELECTRONVOLT_J
I_LI_EV=5.391714996
I_LIPLUS_EV=75.6400970
E_TRIPLET_EV=476034.24*CM1_TO_EV
E_SINGLET_EV=491373.58*CM1_TO_EV
E_DOUBLE_EV=I_LI_EV+I_LIPLUS_EV
E_LI_TRIPLET_EDGE=I_LI_EV+E_TRIPLET_EV
E_LI_SINGLET_EDGE=I_LI_EV+E_SINGLET_EV
SOURCE_INDICES=(13,17)
PHOTO_HHE=((1,'H1I',0),(10,'He4I',1),(11,'He4II',2))


def digest(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def load_source():
    if digest(ORIGINAL.read_bytes()) != ORIGINAL_SHA:
        raise ValueError('ORIGINAL_PR277_ZIP_SHA_MISMATCH')
    root=tempfile.TemporaryDirectory(prefix='rei_li1s_owner_')
    with zipfile.ZipFile(ORIGINAL) as z:
        if z.testzip() is not None:
            root.cleanup();raise ValueError('ORIGINAL_ZIP_CRC_ERROR')
        z.extractall(root.name)
    parent=Path(root.name)/'rei_f4_bass193_photo_energy_20261030'
    atlas_file=parent/'code/energy_atlas.py'
    spec=importlib.util.spec_from_file_location('src_owner_atlas',atlas_file)
    atlas=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(atlas)
    net,data,old,hashes=atlas.source_owner(Path(root.name)/'donor')
    npz=np.load(parent/'results/PHOTO_ENERGY_ATLAS_193.npz',allow_pickle=False)
    pinned={key:npz[key].copy() for key in npz.files}
    npz.close()
    for key in ('Y','x','z'):
        if not np.array_equal(data[key],pinned[key]):
            root.cleanup();raise ValueError('SOURCE_ATLAS_TRAJECTORY_IDENTITY_'+key)
    return root,net,data,pinned,hashes


def integrate_time(rate,x,H):
    """Postprocess the immutable saved clock dx/dt=H, no IVP."""
    return float(cumulative_simpson(np.asarray(rate)/np.asarray(H),x=x,initial=0.)[-1])


def physics():
    owner,net,data,atlas,hashes=load_source()
    try:
        x=data['x'];z=data['z'];Y=data['Y'];E=np.asarray(net.photon_energy_eV,float)
        H=np.asarray(atlas['H_s'],float)
        uv=np.asarray(atlas['uv_scale'],float)
        base_flux=np.asarray(net.photon_flux_bins_base,float)
        if len(x)!=193 or len(E)!=71 or Y.shape!=(193,21):
            raise AssertionError('UNEXPECTED_BASS_GRID')
        if not np.all(np.diff(x)>0) or np.min(H)<=0:
            raise AssertionError('NON_MONOTONIC_OR_NON_PHYSICAL_SAVED_CLOCK')
        if E_TRIPLET_EV>=I_LIPLUS_EV or E_SINGLET_EV>=I_LIPLUS_EV:
            raise AssertionError('UNEXPECTED_NIST_LEVEL_ORDERING')
        if E_LI_TRIPLET_EDGE>=E_LI_SINGLET_EDGE or E_DOUBLE_EV<=E_LI_SINGLET_EDGE:
            raise AssertionError('UNEXPECTED_PHYSICAL_THRESHOLD_ORDERING')
        all_bin=[];all_epoch=[];all_hhe=[]
        li_rate=np.zeros(len(x));trip_only=np.zeros(len(x));above_double=np.zeros(len(x))
        primary_min=np.zeros(len(x));primary_max=np.zeros(len(x))
        core_min=np.zeros(len(x));core_max=np.zeros(len(x))
        total_energy=np.zeros(len(x))
        source_core=np.zeros(len(x));source_primary=np.zeros(len(x));source_ion=np.zeros(len(x))
        max_li_native_abs=0.0;max_li_source_rel=0.0;hhe_rate_abs=0.0
        used_bins=set();first_trip_only=[]
        for k in range(len(x)):
            F=base_flux*uv[k]
            # This calls the native original source, no evolved state or pseudo-rate.
            rates=net.rates(float(atlas['temperature_K'][k]),float(uv[k]))
            if not np.array_equal(F,np.asarray(rates['photon_flux_bins'])):
                raise AssertionError('ORIGINAL_FLUX_CHANGED')
            k_li_rate=0.;k_trip=0.;k_double=0.;k_pmin=0.;k_pmax=0.;k_cmin=0.;k_cmax=0.;k_energy=0.;k_old_core=0.;k_old_pri=0.
            for idx in SOURCE_INDICES:
                sigma=np.asarray(net.li1s_photo_sigma_m2[idx],float)
                if np.any(sigma<0):raise AssertionError('NEGATIVE_LI_CROSS_SECTION')
                rr=Y[k,idx]*sigma*F
                bins=np.flatnonzero(sigma>0)
                for b in bins:
                    e=float(E[b]);r=float(rr[b])
                    if e<E_LI_TRIPLET_EDGE-1e-10:
                        raise AssertionError('BASS_NONZERO_K_EVENT_BELOW_PHYSICAL_TRIPLET_EDGE')
                    allow_singlet=e>=E_LI_SINGLET_EDGE
                    only=not allow_singlet
                    emin=E_TRIPLET_EV
                    emax=E_SINGLET_EV if allow_singlet else E_TRIPLET_EV
                    # R*excited-state energy and prompt photoelectron energy are
                    # bounds, NOT assigned spin branches or eventual deposited heat.
                    bound_e_min= r*emin
                    bound_e_max= r*emax
                    pe_min=r*(e-I_LI_EV-emax)
                    pe_max=r*(e-I_LI_EV-emin)
                    if pe_min<-1e-48:raise AssertionError('KINEMATIC_NEGATIVE_PRIMARY_ENERGY')
                    k_li_rate+=r
                    k_trip+=r if only else 0.
                    k_double+=r if e>=E_DOUBLE_EV else 0.
                    k_cmin+=bound_e_min;k_cmax+=bound_e_max
                    k_pmin+=pe_min;k_pmax+=pe_max
                    k_energy+=r*e
                    k_old_core+=r*BASS_CORE_EV
                    k_old_pri+=r*(e-BASS_K_EDGE_EV)
                    used_bins.add(int(b))
                    if only:first_trip_only.append(int(b))
                    all_bin.append(dict(epoch=k,z=float(z[k]),isotope=str(data['species_names'][idx]),source_index=idx,bin_index=int(b),photon_eV=e,source_events_per_baryon_s=r,triplet_1s2s_allowed=True,singlet_1s2s_allowed=allow_singlet,conditional_double_threshold_open=bool(e>=E_DOUBLE_EV),double_photoionization_rate_known=False,conditional_excitation_eV_min=emin,conditional_excitation_eV_max=emax,primary_electron_eV_min=e-I_LI_EV-emax,primary_electron_eV_max=e-I_LI_EV-emin,source_BASS_primary_eV=e-BASS_K_EDGE_EV,source_BASS_core_eV=BASS_CORE_EV))
            li_rate[k]=k_li_rate;trip_only[k]=k_trip;above_double[k]=k_double
            primary_min[k]=k_pmin;primary_max[k]=k_pmax;core_min[k]=k_cmin;core_max[k]=k_cmax
            total_energy[k]=k_energy;source_core[k]=k_old_core;source_primary[k]=k_old_pri;source_ion[k]=k_li_rate*BASS_VALENCE_EV
            assert np.isclose(k_energy,k_li_rate*I_LI_EV+k_cmin+k_pmax,rtol=3e-14,atol=1e-70)
            assert np.isclose(k_energy,k_li_rate*I_LI_EV+k_cmax+k_pmin,rtol=3e-14,atol=1e-70)
            assert np.isclose(k_energy,source_ion[k]+k_old_core+k_old_pri,rtol=3e-14,atol=1e-70)
            max_li_native_abs=max(max_li_native_abs,abs(k_li_rate-atlas['total_inner_events'][k]))
            if atlas['total_inner_events'][k]>0:
                max_li_source_rel=max(max_li_source_rel,abs(k_li_rate/atlas['total_inner_events'][k]-1.))
            all_epoch.append(dict(epoch=k,z=float(z[k]),x=float(x[k]),H_s=float(H[k]),source_Li1s_events_per_baryon_s=k_li_rate,triplet_only_kinematically_per_baryon_s=k_trip,source_single_K_events_above_double_threshold_per_baryon_s=k_double,source_absorbed_eV_per_baryon_s=k_energy,physical_ion_base_eV_per_baryon_s=k_li_rate*I_LI_EV,conditional_bound_excitation_min_eV_per_baryon_s=k_cmin,conditional_bound_excitation_max_eV_per_baryon_s=k_cmax,conditional_primary_kinetic_min_eV_per_baryon_s=k_pmin,conditional_primary_kinetic_max_eV_per_baryon_s=k_pmax,source_BASS_core_eV_per_baryon_s=k_old_core,source_BASS_primary_eV_per_baryon_s=k_old_pri))
            # Matched BASS input rates, but NO REI heat port (different owner).
            for idx,name,port in PHOTO_HHE:
                sigma=np.asarray(net.photo_sigma_m2[idx],float)
                threshold=float(net.transition_energy_eV[idx])
                gamma=float(np.sum(sigma*F))
                native=float(rates['photo_s'][idx])
                hhe_rate_abs=max(hhe_rate_abs,abs(gamma-native))
                potential=float(np.sum(sigma*F*np.maximum(E-threshold,0.)))
                all_hhe.append(dict(epoch=k,z=float(z[k]),source_species=name,BASS_source_index=idx,REI_HHe_port_index_for_shape_only=port,BASS_gamma_per_absorber_s=gamma,BASS_primary_electron_eV_per_absorber_s=potential,BASS_primary_electron_erg_per_absorber_s=potential*EV_ERG,REI_heat_erg_per_absorber_s='UNBOUND_NO_COMMON_OWNER',REI_thermal_port_valid=False))
        if len(used_bins)!=22:raise AssertionError('EXPECTED_22_LI1S_ACTIVE_BINS')
        if not np.allclose(li_rate,atlas['total_inner_events'],rtol=3e-14,atol=3e-50):
            raise AssertionError('SOURCE_NATIVE_LI1S_RATE_DISAGREEMENT')
        if not np.allclose(source_core,atlas['total_core_eV'],rtol=3e-14,atol=3e-48):
            raise AssertionError('SOURCE_NATIVE_LI1S_CORE_DISAGREEMENT')
        exp={name:integrate_time(a,x,H) for name,a in {'events':li_rate,'triplet_only_events':trip_only,'single_K_events_above_double_threshold':above_double,'NIST_excitation_min_eV':core_min,'NIST_excitation_max_eV':core_max,'NIST_primary_min_eV':primary_min,'NIST_primary_max_eV':primary_max,'NIST_valence_ion_eV':li_rate*I_LI_EV,'absorbed_eV':total_energy,'BASS_core_eV':source_core,'BASS_primary_eV':source_primary}.items()}
        if not np.isclose(exp['BASS_core_eV'],2.0310979599168846e-9,rtol=2e-13):
            raise AssertionError('PARENT_LI_CORE_EXPOSURE_MISMATCH')
        for key in ('min','max'):
            pkey='NIST_primary_'+key+'_eV'; ckey='NIST_excitation_'+('max' if key=='min' else 'min')+'_eV'
            if not np.isclose(exp['absorbed_eV'],exp['NIST_valence_ion_eV']+exp[pkey]+exp[ckey],rtol=1e-14):
                raise AssertionError('INTEGRATED_BRANCH_ENERGY_DEFECT')
        return dict(
            result={'schema':'REI_BASS_LI1S_KINEMATIC_BRANCH_V1','status':'SCOPED_KINEMATIC_SOURCE_DIAGNOSTIC_NOT_CASCADE_NOT_HEAT',
                'source':{'PR277_head':'b9610ccefd8ddddab89c98ccad09152b49ba6762','PR277_archive_sha256':ORIGINAL_SHA,'BASS_owner_commit':BASS_SHA,'BASS_network_sha256':hashes['BASS_ATOMIC_NETWORK.py'],'original_trajectory_sha256':'37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086','REI_thermal_source_blob':'0648618d9822e169e9672ac3c556f86595c3b0b6'},
                'NIST':{'LiI_ionization_eV':I_LI_EV,'LiII_ionization_eV':I_LIPLUS_EV,'LiII_1s2s_3S1_cm_inverse':476034.24,'LiII_1s2s_1S0_cm_inverse':491373.58,'triplet_excitation_eV':E_TRIPLET_EV,'singlet_excitation_eV':E_SINGLET_EV,'triplet_K_edge_eV':E_LI_TRIPLET_EDGE,'singlet_K_edge_eV':E_LI_SINGLET_EDGE,'LiI_double_ionization_threshold_eV':E_DOUBLE_EV,'units':'eV; SI h,c,e exact','refs':['https://physics.nist.gov/PhysRefData/Handbook/Tables/lithiumtable6_a.htm','https://physics.nist.gov/cgi-bin/ASD/ie.pl']},
                'counts':{'epochs':len(x),'isotopes':2,'original_photon_bins':71,'active_Li1s_bins':len(used_bins),'bin_rows':len(all_bin),'epoch_rows':len(all_epoch),'hhe_potential_rows':len(all_hhe),'new_IVPs':0},
                'source_exposures_per_baryon':exp,
                'derived':{'max_relative_Li1s_event_vs_PR277':max_li_source_rel,'max_abs_Li1s_event_per_baryon_s':max_li_native_abs,'max_abs_HHe_gamma_per_absorber_s':hhe_rate_abs,'first_Li_active_bin_energy_eV':float(E[min(used_bins)]),'triplet_only_bins':len(set(first_trip_only)),'field_free_Auger_allowed_from_1s2s_singlet_or_triplet':False,'singlet_and_triplet_branch_probabilities':'UNBOUND','direct_double_photoionization_partial_sigma':'NOT_SOURCE_QUALIFIED','fluorescence_photon_escape_and_lifetime':'NOT_SOURCE_QUALIFIED','secondary_electron_thermal_deposition_kernel':'NOT_SOURCE_QUALIFIED','REI_IgmPhotoInput_heat':'UNBOUND'},
                'holds':{'F4':'PARTIAL','L4_ready':False,'REI17_BASS21_full_chemistry_clock':'UNRESOLVED','NO_MORE_IVPs':True,'NO_MERGE':True,'NO_FORCE_PUSH':True,'AUTO_NEXT_NODE':False,'PRODUCTION':'HOLD','working_DAG':'33/88','central_DAG':'28/88','F4_fast_DAG':'4/7','canonical_physical_delta':0,'R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN'}},
            bins=all_bin,epochs=all_epoch,hhe=all_hhe)
    finally:
        owner.cleanup()


def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=tuple(rows[0]));writer.writeheader();writer.writerows(rows)


def generate():
    d=physics()
    dest=ROOT/'results';dest.mkdir(parents=True,exist_ok=True)
    write_csv(dest/'LI1S_BIN_8492.csv',d['bins'])
    write_csv(dest/'LI1S_EPOCH_193.csv',d['epochs'])
    write_csv(dest/'HHE_193x3_SOURCE_ELECTRON_INPUT_NOT_HEAT.csv',d['hhe'])
    (dest/'RESULT.json').write_text(json.dumps(d['result'],ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return d['result']

if __name__=='__main__':
    print(json.dumps(generate(),ensure_ascii=False,indent=2))
