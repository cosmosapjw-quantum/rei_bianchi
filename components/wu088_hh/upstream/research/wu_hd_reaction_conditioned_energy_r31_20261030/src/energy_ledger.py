"""R31: Exact reaction-conditioned HD rotational-energy partition from original R30.

Provenance: GL2022 printed SQM H+ collision and reactive rates, REC161 A
transcriptions, Sung 2022 four fitted HD line centres inherited through an
immutable R30 SOURCE ZIP. The conditional fixed-bath/selected-channel model
is NOT a complete astrophysical heating/cooling function or reaction enthalpy.

All per-molecule energies in J and per-event rates in s^-1, n(H+) in cm^-3.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import math
import sys
import zipfile
import csv
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent.parent
R30_ARCHIVE='WU_R30_SOURCE_ORIGINAL_20261030.zip'
R30_SHA256='d1aa63fedb6527d6aab59df447f1f2b4aa557fab98789b962464a2b86bb5bf16'
R29_SHA256='65ed097acb02f8eb91ff6518c26c8ad61e721e3fadd9b904aa2157e3508cb0ea'
J_PER_EV=1.602176634e-19

class ImmutableSourceError(ValueError): pass

def file_sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(128*1024),b''):h.update(chunk)
    return h.hexdigest()

def restore_parent():
    p=ROOT/'archive'/R30_ARCHIVE
    if not p.is_file() or file_sha(p)!=R30_SHA256:
        raise ImmutableSourceError('original R30 source ZIP absent/mismatched')
    dest=ROOT/'_r30_restored'
    with zipfile.ZipFile(p) as z:
        if z.testzip() is not None:raise ImmutableSourceError('original ZIP CRC failed')
        names=z.namelist()
        if any((name.startswith('/') or '..' in Path(name).parts) for name in names):
            raise ImmutableSourceError('unsafe source ZIP names')
        # Trust only manifest-listed immutable content; do NOT use stale mutable restored files.
        if not dest.exists():
            dest.mkdir(parents=True)
            z.extractall(dest)
        for name in ['src/spectral.py','sources/REC164_SUNG2022_PRIMARY_TABLE4_LOCK.json',
                     'archive/WU_R29_SOURCE_ORIGINAL_20261030.zip']:
            q=dest/name
            if not q.is_file() or q.read_bytes()!=z.read(name):
                raise ImmutableSourceError('modified restored source '+name)
    if file_sha(dest/'archive'/'WU_R29_SOURCE_ORIGINAL_20261030.zip')!=R29_SHA256:
        raise ImmutableSourceError('R29 nested source identity failed')
    spec=importlib.util.spec_from_file_location('wu_r30_source_spectral',dest/'src'/'spectral.py')
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod

def case_key(T,policy,ratio,initial_J,n):
    return dict(T_K=int(T),policy=policy,n_over_ncrit_J2=float(ratio),initial_HD_J=int(initial_J),nHplus_cm3=float(n))

def one_case(parent,base,new,T,policy,ratio,initial_J):
    n=parent.reference_density(base,T,policy)*ratio
    G,GC,Gfirst,kchem=parent.assemble(new,T,policy,n)
    initial=np.zeros(5);initial[initial_J]=1
    m=np.linalg.solve(-G,initial)
    if np.any(m < -1e-6):raise AssertionError('negative integrated residence time')
    energies=np.array([new.energies_cm1[j]*100*parent.PLANCK*parent.SPEED_LIGHT for j in range(5)])
    key=case_key(T,policy,ratio,initial_J,n)
    collision=[]
    for high in range(1,5):
      for low in range(high):
        dE=energies[high]-energies[low]
        kd=n*new.down[(T,high,low)]
        ku=kd*((2*high+1)/(2*low+1))*math.exp(-dE/(parent.BOLTZMANN*T))
        count_down=kd*m[high]
        count_up=ku*m[low]
        collision.append(dict(**key,high_J=high,low_J=low,
          source_downward_k_cm3_per_s=float(new.down[(T,high,low)]),
          detailed_balance_derived_upward_k_cm3_per_s=float(ku/n),
          expected_down_collisions_per_initial_HD=float(count_down),
          expected_up_collisions_per_initial_HD=float(count_up),
          expected_net_down_collisions=float(count_down-count_up),
          energy_gap_J=float(dE),
          energy_gained_by_proton_bath_J=float(dE*(count_down-count_up))))
    chemistry=[]
    for j in range(5):
        p=float(kchem[j]*m[j])
        chemistry.append(dict(**key,terminal_HD_J=j,
          probability_reaction_at_HD_J=p,
          terminal_HD_rotational_energy_J=float(energies[j]),
          weighted_terminal_HD_rotational_energy_J=float(energies[j]*p)))
    photons=[]
    for j in range(1,5):
        p=float(new.A[j]*m[j])
        photons.append(dict(**key,emission_J=j,lower_J=j-1,
          source_A_per_s=float(new.A[j]),
          fitted_sung_wavenumber_cm_minus1=float(new.energies_cm1[j]-new.energies_cm1[j-1]),
          expected_photons_per_initial_HD=p,
          photon_energy_J=float(energies[j]-energies[j-1]),
          emitted_energy_J=float((energies[j]-energies[j-1])*p)))
    bath=float(sum(r['energy_gained_by_proton_bath_J'] for r in collision))
    photon=float(sum(r['emitted_energy_J'] for r in photons))
    terminal=float(sum(r['weighted_terminal_HD_rotational_energy_J'] for r in chemistry))
    energy_initial=float(energies[initial_J])
    error=energy_initial-(bath+photon+terminal)
    scale=max(sum(abs(r['energy_gained_by_proton_bath_J']) for r in collision)+photon+terminal,energies[-1])
    if abs(error)>3e-12*scale:
        raise AssertionError('HD rotational energy ledger violated: '+str(error))
    if abs(sum(r['probability_reaction_at_HD_J'] for r in chemistry)-1)>5e-11:
        raise AssertionError('reaction endpoint normalization')
    # R30 published observable replay, not an invented new astrophysical measurement.
    R30_expected_photon_energy=sum((new.energies_cm1[j]-new.energies_cm1[j-1])*100*parent.PLANCK*parent.SPEED_LIGHT*new.A[j]*m[j] for j in range(1,5))
    if abs(photon-R30_expected_photon_energy)>1e-32:raise AssertionError('photon energy parity failed')
    result=dict(**key,initial_HD_rotational_energy_J=energy_initial,
      integrated_proton_bath_energy_gain_J=bath,
      integrated_photon_energy_J=photon,
      terminal_HD_rotational_energy_J=terminal,
      net_collisional_heat_event_is_signed=True,
      energy_balance_residual_J=float(error),
      max_HD_rotational_energy_J=float(energies[-1]),
      expected_collision_down_events=sum(r['expected_down_collisions_per_initial_HD'] for r in collision),
      expected_collision_up_events=sum(r['expected_up_collisions_per_initial_HD'] for r in collision),
      expected_photons=sum(r['expected_photons_per_initial_HD'] for r in photons),
      mean_restricted_reaction_time_s=float(m.sum()),
      chemical_Q_J=None,untracked_product_energy_J=None,
      physical_system='PRESCRIBED_BATH_REACTION_CONDITIONED_HD_ROTATIONAL_ACCOUNTING')
    return result,collision,chemistry,photons

def build_atlas():
    mod=restore_parent()
    parent=mod.load_r29()
    orig=parent.load_grid()
    new=mod.get_grid(orig)
    cases=[];coll=[];terminal=[];phot=[]
    for T in parent.TEMPS:
      for policy in parent.POLICIES:
        for ratio in parent.DENSITY_RATIOS:
          for j in parent.LEVELS:
            case,c,t,p=one_case(parent,orig,new,T,policy,ratio,j)
            cases.append(case);coll.extend(c);terminal.extend(t);phot.extend(p)
    if (len(cases),len(coll),len(terminal),len(phot))!=(210,2100,1050,840):
        raise AssertionError('source physical case coverage')
    return cases,coll,terminal,phot

def matched_density_policy_pairs():
    """At equal physical n(H+), compare policies without density confounding.

    Density is the spin-effective J2 critical density at each source T, not cosmic.
    """
    mod=restore_parent(); parent=mod.load_r29();orig=parent.load_grid();new=mod.get_grid(orig)
    out=[]
    for T in parent.TEMPS:
      nphys=parent.reference_density(orig,T,'Eq6-7_spin_effective')
      for initial in parent.LEVELS:
        a={}
        for policy in parent.POLICIES:
          ratio=nphys/parent.reference_density(orig,T,policy)
          row,*_=one_case(parent,orig,new,T,policy,ratio,initial)
          a[policy]=row
        raw=a['raw_SQM'];spin=a['Eq6-7_spin_effective']
        out.append(dict(T_K=T,initial_HD_J=initial,nHplus_matched_cm3=nphys,
            raw_ratio_n_over_own_ncrit=raw['n_over_ncrit_J2'],
            spin_ratio_n_over_own_ncrit=spin['n_over_ncrit_J2'],
            raw_proton_bath_heat_J=raw['integrated_proton_bath_energy_gain_J'],
            spin_proton_bath_heat_J=spin['integrated_proton_bath_energy_gain_J'],
            spin_minus_raw_bath_heat_J=spin['integrated_proton_bath_energy_gain_J']-raw['integrated_proton_bath_energy_gain_J'],
            raw_photon_energy_J=raw['integrated_photon_energy_J'],
            spin_photon_energy_J=spin['integrated_photon_energy_J'],
            spin_minus_raw_photon_energy_J=spin['integrated_photon_energy_J']-raw['integrated_photon_energy_J'],
            raw_terminal_HD_rot_energy_J=raw['terminal_HD_rotational_energy_J'],
            spin_terminal_HD_rot_energy_J=spin['terminal_HD_rotational_energy_J'],
            spin_minus_raw_terminal_energy_J=spin['terminal_HD_rotational_energy_J']-raw['terminal_HD_rotational_energy_J'],
            matched_energy_difference_residual_J=(spin['integrated_proton_bath_energy_gain_J']-raw['integrated_proton_bath_energy_gain_J'])
                  +(spin['integrated_photon_energy_J']-raw['integrated_photon_energy_J'])
                  +(spin['terminal_HD_rotational_energy_J']-raw['terminal_HD_rotational_energy_J'])))
    if len(out)!=35:raise AssertionError('matched fixed physical density cases')
    if max(abs(x['matched_energy_difference_residual_J']) for x in out)>1e-30:
        raise AssertionError('matched-density energy-difference invariant')
    return out

def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf8') as f:
      w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction='raise')
      w.writeheader();w.writerows(rows)

def main():
    out=ROOT/'results';out.mkdir(exist_ok=True)
    cases,coll,terminal,phot=build_atlas()
    matched=matched_density_policy_pairs()
    for name,rows in [('R31_ROTATIONAL_ENERGY_210.csv',cases),
                      ('R31_COLLISION_ENERGY_2100.csv',coll),
                      ('R31_TERMINAL_STATE_1050.csv',terminal),
                      ('R31_PHOTON_ENERGY_840.csv',phot),
                      ('R31_POLICY_FIXED_DENSITY_35.csv',matched)]:write_csv(out/name,rows)
    eg=next(x for x in cases if (x['T_K'],x['policy'],x['n_over_ncrit_J2'],x['initial_HD_J'])==(105,'Eq6-7_spin_effective',1.,2))
    eg_ground=next(x for x in cases if (x['T_K'],x['policy'],x['n_over_ncrit_J2'],x['initial_HD_J'])==(105,'Eq6-7_spin_effective',1.,0))
    summary={'schema':'wu.r31.reaction_conditioned_HD_rotational_energy_v1',
      'canonical_DAG':{'done':34,'total':49,'delta':0},
      'new_auxiliary_R31':{'done':1,'total':1,'canonical_promotions':0},
      'source_head':'72d189752d81febe48292e7532d0e96beac51f7f',
      'immutable_R30_original_source_sha256':R30_SHA256,
      'immutable_R29_nested_source_sha256':R29_SHA256,
      'new_source_bytes':'NONE; source-derived new physical quantity from immutable 2022 SQM rates and 2022 Sung experimental fitted centers',
      'cases':len(cases),'matched_density_policy_pairs':len(matched),'collisional_edge_rows':len(coll),'terminal_state_rows':len(terminal),'photon_rows':len(phot),
      'example_105K_J2':eg,'example_105K_J0':eg_ground,
      'example_105K_matched_density_policy_effect':next(x for x in matched if x['T_K']==105 and x['initial_HD_J']==2),
      'worst_abs_energy_balance_residual_J':max(abs(x['energy_balance_residual_J']) for x in cases),
      'signed_collisional_bath_energies':{'min':min(x['integrated_proton_bath_energy_gain_J'] for x in cases),
          'max':max(x['integrated_proton_bath_energy_gain_J'] for x in cases)},
      'limits':{'fixed_T_and_nHp':True,'full_cosmological_cooling':False,'unknown_physical_Q':None,'reversibility_beyond_HD_internal':False,
        'original_EMAA_raw_bytes':False,'original_Velilla_PES':False,'original_Sung_full_covariance':False,
        'owner_ACK':None,'HH_R10':'OFF','FULL_A':None,'L4':False,'production':'NOT_ISSUED',
        'R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN','native_subagent':'NOT_EXPOSED'}}
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ['cases','collisional_edge_rows','terminal_state_rows','photon_rows','example_105K_J2','example_105K_J0','worst_abs_energy_balance_residual_J','signed_collisional_bath_energies']},indent=2))
if __name__=='__main__':main()
