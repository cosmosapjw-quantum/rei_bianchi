"""Li II vacuum 2E1/M1 photon-count capacity on immutable BASS193 Li I 1s events.

This does NOT calculate emitted photon transfer, spin branching, Auger yields,
nonthermal electron heating, REI photo.heat, or new cosmological IVPs.
Measured atomic lifetimes and NIST levels are joined to SOURCE-OWNED archived
Li I K-shell photoevent source rates. The two-photon frequency distribution is
NOT assumed: deterministic sharp count bounds follow from photon-energy sum.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path
from collections import defaultdict
from math import isclose

import numpy as np
from scipy.integrate import cumulative_simpson

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / 'source/PR279_FULL.zip'
ORIGINAL_SHA = '6e50586131ab6f8f76b72ee8c7125dfd3225211d528609c862e01a305a0ab6d3'
PR279_PREFIX = 'REI_F4_LI1S_KINEMATIC_BRANCH_20261030/'
PR277_SHA='6a5794996b0fe0473558bc07c866f2f3f0315cb72aef9b284e805cd40ba897a8'
SOURCE_OWNER='cc602e209e7deeb511ab2a1f3b2268d55206c43c'
NIST_LEVELS='https://physics.nist.gov/PhysRefData/Handbook/Tables/lithiumtable6_a.htm'
NIST_ION='https://physics.nist.gov/cgi-bin/ASD/ie.pl'
PRL_SINGLET='https://doi.org/10.1103/PhysRevLett.27.902'
PRA_TRIPLET='https://doi.org/10.1103/PhysRevA.60.R3350'
PRA_TRIPLET_CROSSCHECK='https://doi.org/10.1103/PhysRevA.21.179'

H_PLANCK=6.62607015e-34
C_SI=299792458.0
EV_J=1.602176634e-19
E_TRIPLET_EV = 476034.24*(H_PLANCK*C_SI*100.0/EV_J)
E_SINGLET_EV = 491373.58*(H_PLANCK*C_SI*100.0/EV_J)
E_LII_EV = 5.391714996
THRESHOLDS_EV = {'H_I': 13.598434599702,
                 'He_I': 24.587389011,
                 'He_II': 54.417765486}
# Source-measured, NOT extrapolated by Z-scaling. Experimental uncertainties reported.
TAU_MEASURED={'LiII_singlet_2E1':(503.0e-6,26.0e-6),
              'LiII_triplet_M1':(52.2,5.0)}
EV_ERG=1.602176634e-12


def sha256_bytes(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()


def read_source():
    raw=ORIGINAL.read_bytes()
    if sha256_bytes(raw)!=ORIGINAL_SHA:
        raise ValueError('PR279_ARCHIVE_BYTE_IDENTITY_FAIL')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:
            raise ValueError('PR279_ZIP_CRC_FAIL')
        donor=z.read(PR279_PREFIX+'source/PR277_FULL.zip')
        if sha256_bytes(donor)!=PR277_SHA:
            raise ValueError('PR277_NESTED_OWNER_FAIL')
        bin_rows=list(csv.DictReader(io.StringIO(z.read(PR279_PREFIX+'results/LI1S_BIN_8492.csv').decode('utf-8'))))
        epoch_rows=list(csv.DictReader(io.StringIO(z.read(PR279_PREFIX+'results/LI1S_EPOCH_193.csv').decode('utf-8'))))
        old=json.loads(z.read(PR279_PREFIX+'results/RESULT.json'))
    if len(bin_rows)!=8492 or len(epoch_rows)!=193:
        raise ValueError('PR279_SOURCE_GRID_SHAPE_FAIL')
    if old['counts']['new_IVPs']!=0 or old['source']['BASS_owner_commit']!=SOURCE_OWNER:
        raise ValueError('PR279_SOURCE_OWNER_MISMATCH')
    return bin_rows,epoch_rows,old


def two_photon_count_bounds(excitation_ev:float,threshold_ev:float):
    """Sharp min/max *number* (0..2) of photons with E_gamma > chi.

    For E1+E2=E, E1,E2>=0. The extrema are bounds on SUPPORT,
    not on measured probability, angular distribution or deposited energy.
    Strict inequalities at equality avoid false emission-threshold claims.
    """
    if excitation_ev <= threshold_ev:
        return (0,0)
    if excitation_ev <= 2*threshold_ev:
        return (0,1)
    return (1,2)


def allowed_event_bounds(only_triplet:bool,threshold_ev:float):
    trip_n=int(E_TRIPLET_EV>threshold_ev)
    if only_triplet:
        return (trip_n,trip_n)
    sing_min,sing_max=two_photon_count_bounds(E_SINGLET_EV,threshold_ev)
    return (min(trip_n,sing_min),max(trip_n,sing_max))


def time_integral(y,x,h):
    return float(cumulative_simpson(np.asarray(y,dtype=float)/np.asarray(h,dtype=float),x=np.asarray(x,dtype=float),initial=0)[-1])


def compute():
    bins,original_epochs,prev=read_source()
    H=np.array([float(row['H_s']) for row in original_epochs])
    x=np.array([float(row['x']) for row in original_epochs])
    if len(x)!=193 or not np.all(np.diff(x)>0) or not np.all(H>0):
        raise ValueError('SAVED_CLOCK_INVALID')
    if E_TRIPLET_EV<=THRESHOLDS_EV['He_II'] or not (2*THRESHOLDS_EV['He_I']<E_SINGLET_EV<2*THRESHOLDS_EV['He_II']):
        raise ValueError('ATOMIC_THRESHOLD_ORDERING_CHANGED')
    b_out=[];count=defaultdict(lambda:np.zeros(193));err_abs=0.0
    for row in bins:
        k=int(row['epoch']);r=float(row['source_events_per_baryon_s']);e=float(row['photon_eV'])
        only=(row['singlet_1s2s_allowed']=='False')
        if row['triplet_1s2s_allowed']!='True' or r<0 or not 0<=k<193:
            raise ValueError('UNEXPECTED_ORIGINAL_SINGLE_K_SOURCE')
        if only and e<E_LII_EV+E_TRIPLET_EV:
            raise ValueError('NEGATIVE_KINETIC_ENERGY')
        if not only and e<E_LII_EV+E_SINGLET_EV:
            raise ValueError('FORBIDDEN_SINGLET_EVENT')
        # Recompute source ledger identity rather than copying original envelopes.
        kmin=e-E_LII_EV-(E_TRIPLET_EV if only else E_SINGLET_EV)
        kmax=e-E_LII_EV-E_TRIPLET_EV
        assert kmin>=-1e-10 and kmax>=kmin-1e-12
        err_abs=max(err_abs, abs(e-(E_LII_EV+E_TRIPLET_EV+kmax)))
        err_abs=max(err_abs, abs(e-(E_LII_EV+(E_TRIPLET_EV if only else E_SINGLET_EV)+kmin)))
        b_out_entry={
            'epoch':k,'z':float(row['z']),'isotope':row['isotope'],'bin_index':int(row['bin_index']),
            'photon_eV':e,'native_K_events_per_baryon_s':r,
            'forced_triplet_only':only,'allowed_singlet_2E1':not only,
            'triplet_M1_photon_eV':E_TRIPLET_EV,
            'singlet_two_E1_total_eV':E_SINGLET_EV if not only else '',
            'triplet_only_M1_events_per_baryon_s':r if only else 0.,
            'allowed_singlet_events_per_baryon_s':r if not only else 0.,
            'conditional_vacuum_ionizing_photon_count_min':1,
            'conditional_vacuum_ionizing_photon_count_max':1 if only else 2,
            'source_photoelectron_kinetic_min_eV':kmin,
            'source_photoelectron_kinetic_max_eV':kmax,
            'photo_thermal_heat_source':'UNBOUND'
        }
        count['K_events'][k]+=r
        count['triplet_forced_events'][k]+=r if only else 0.
        count['singlet_allowed_events'][k]+=r if not only else 0.
        count['conditional_total_radiative_photons_min'][k]+=r
        count['conditional_total_radiative_photons_max'][k]+=r*(1 if only else 2)
        count['vacuum_triplet_line_energy_min_eV'][k]+=r*E_TRIPLET_EV if only else 0.
        count['vacuum_triplet_line_energy_max_eV'][k]+=r*E_TRIPLET_EV
        count['vacuum_singlet_pair_energy_max_eV'][k]+=r*E_SINGLET_EV if not only else 0.
        count['vacuum_total_radiative_energy_min_eV'][k]+=r*E_TRIPLET_EV
        count['vacuum_total_radiative_energy_max_eV'][k]+=r*(E_TRIPLET_EV if only else E_SINGLET_EV)
        count['source_absorption_eV'][k]+=r*e
        count['source_li_valence_ion_eV'][k]+=r*E_LII_EV
        count['conditional_photoelectron_kinetic_min_eV'][k]+=r*kmin
        count['conditional_photoelectron_kinetic_max_eV'][k]+=r*kmax
        for name,chi in THRESHOLDS_EV.items():
            low,hi=allowed_event_bounds(only,chi)
            b_out_entry[f'potential_{name}_ionizing_photons_min_per_event']=low
            b_out_entry[f'potential_{name}_ionizing_photons_max_per_event']=hi
            count[f'potential_{name}_photons_min'][k]+=r*low
            count[f'potential_{name}_photons_max'][k]+=r*hi
        b_out.append(b_out_entry)
    assert len(b_out)==8492
    # Compare with the archived P279 native rate and energy for all epochs;
    # this is independent of the algebraic branch accounting above.
    for k,row in enumerate(original_epochs):
        oldrate=float(row['source_Li1s_events_per_baryon_s'])
        oldeng=float(row['source_absorbed_eV_per_baryon_s'])
        if not isclose(count['K_events'][k],oldrate,rel_tol=2e-14,abs_tol=1e-65):
            raise ValueError('PR279_NATIVE_RATE_REGRESSION')
        if not isclose(count['source_absorption_eV'][k],oldeng,rel_tol=2e-14,abs_tol=1e-64):
            raise ValueError('PR279_NATIVE_ABSORPTION_REGRESSION')
        if not isclose(count['source_absorption_eV'][k],count['source_li_valence_ion_eV'][k]
                       +count['vacuum_total_radiative_energy_min_eV'][k]
                       +count['conditional_photoelectron_kinetic_max_eV'][k],rel_tol=3e-14,abs_tol=1e-64):
            raise ValueError('LOWER_VACUUM_RADIATION_ENERGY_LEDGER_DEFECT')
        if not isclose(count['source_absorption_eV'][k],count['source_li_valence_ion_eV'][k]
                       +count['vacuum_total_radiative_energy_max_eV'][k]
                       +count['conditional_photoelectron_kinetic_min_eV'][k],rel_tol=3e-14,abs_tol=1e-64):
            raise ValueError('UPPER_VACUUM_RADIATION_ENERGY_LEDGER_DEFECT')
    counts={}
    output_epochs=[]
    for k,row in enumerate(original_epochs):
        entry={'epoch':k,'z':float(row['z']),'x':x[k],'H_s':H[k],
               'H_tau_triplet':H[k]*TAU_MEASURED['LiII_triplet_M1'][0],
               'H_tau_singlet':H[k]*TAU_MEASURED['LiII_singlet_2E1'][0]}
        for name,val in count.items():entry[name+'_per_baryon_s']=float(val[k])
        output_epochs.append(entry)
    for key,value in count.items(): counts[key]=time_integral(value,x,H)
    event_exp=counts['K_events']
    if not isclose(event_exp,prev['source_exposures_per_baryon']['events'],rel_tol=5e-14):
        raise ValueError('SOURCE_EXPOSURE_INTEGRAL_MISMATCH')
    if not isclose(counts['source_absorption_eV'],prev['source_exposures_per_baryon']['absorbed_eV'],rel_tol=5e-14):
        raise ValueError('SOURCE_ABSORPTION_INTEGRAL_MISMATCH')
    # Purely frozen-epoch Hubble comparison. Not a bound on d ln Gamma/dt,
    # collisions or delayed reabsorption. No new IVP or photon transport.
    lifetime_ratios={k:{'tau_s':tau,'uncertainty_s':dtau,'A_per_s':1/tau,
        'A_min_per_s':1/(tau+dtau),'A_max_per_s':1/(tau-dtau),
        'max_H_tau':float(np.max(H*(tau+dtau))),
        'max_H_tau_nominal':float(np.max(H*tau))}
        for k,(tau,dtau) in TAU_MEASURED.items()}
    assert lifetime_ratios['LiII_triplet_M1']['max_H_tau']<1e-12
    result={
      'schema':'REI_BASS_LI1S_SOURCE_LOCKED_VACUUM_RADIATIVE_CAPACITY_V1',
      'status':'SCOPED_SOURCE_NATIVE_PHOTON_CAPACITY_NOT_RADIATION_TRANSFER_NOT_THERMAL_HEAT',
      'science_owner':{'PR279_head':'46d7d3192c32a069ef2b6d9aa5b7202e9c2bfa78','PR279_archive_sha256':ORIGINAL_SHA,
                       'parent_PR277_archive_sha256':PR277_SHA,'BASS_native_owner_commit':SOURCE_OWNER},
      'literature':{'NIST_LiII_levels':NIST_LEVELS,'NIST_HHe_thresholds':NIST_ION,
                    'measured_singlet_lifetime':PRL_SINGLET,'measured_triplet_lifetime':PRA_TRIPLET,
                    'independent_triplet_crosscheck':PRA_TRIPLET_CROSSCHECK},
      'energy_eV':{'LiII_triplet_M1':E_TRIPLET_EV,'LiII_singlet_2E1_pair_total':E_SINGLET_EV,
                   'HHe_ionization_thresholds':THRESHOLDS_EV},
      'measured_radiative_lifetimes':lifetime_ratios,
      'counts':{'epochs':len(output_epochs),'isotope_bins':len(b_out),
                'active_bins_per_isotope':22,'HHe_thresholds':len(THRESHOLDS_EV),
                'threshold_potential_cells':len(b_out)*len(THRESHOLDS_EV),
                'new_IVPs':0},
      'saved_trajectory_exposures_per_baryon':counts,
      'max_energy_identity_abs_defect_eV':err_abs,
      'scientific_scope':{'vacuum_only':True,'full_cascade_thermalization':False,
                          'original_K_events_are_single_ejection_not_double_photoionization':True,
                          'actual_singlet_triplet_branch_probabilities':'UNBOUND',
                          'two_photon_differential_spectrum':'UNBOUND',
                          'intermediate_metastable_collisional_quench':'UNBOUND',
                          'photon_escape_reabsorption':'UNBOUND',
                          'cosmological_radiative_transfer':'NOT_RUN',
                          'REI_IgmPhotoInput_heat_erg_per_absorber_s':'UNBOUND',
                          'full_REI17_BASS21_common_chemistry_clock':'UNRESOLVED'},
      'progress':{'working_DAG':'33/88','central_DAG':'28/88','F4_fast_DAG':'4/7',
                  'canonical_physical_delta':0,'F4':'PARTIAL','L4_ready':False,
                  'NO_MORE_IVPs':True,'NO_MERGE':True,'NO_FORCE_PUSH':True,
                  'AUTO_NEXT_NODE':False,'PRODUCTION':'HOLD',
                  'native_subagent':'NOT_RUN','different_author_R6':'NOT_RUN','different_author_C9':'NOT_RUN'}
    }
    return {'bins':b_out,'epochs':output_epochs,'result':result}


def to_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def run():
    output=compute()
    root=ROOT/'results';root.mkdir(exist_ok=True)
    to_csv(root/'LI1S_VACUUM_PHOTON_CAPACITY_8492.csv',output['bins'])
    to_csv(root/'LI1S_PHOTON_CAPACITY_EPOCH_193.csv',output['epochs'])
    (root/'RESULT.json').write_text(json.dumps(output['result'],ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
    return output

if __name__=='__main__':
    print(json.dumps(run()['result'],ensure_ascii=False,indent=2))
