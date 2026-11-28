"""Read-only C0 channel metadata and admission checks. No scientific dispatch."""
from __future__ import annotations
import hashlib,json
from fractions import Fraction
from pathlib import Path
import numpy as np

INPUT_SHA='8482d2854ab620c58bb1d7a7a45cf88eb71fd75081242263a9ef48927f0a282c'
OD_SHA='63c0925ff938340feceb5768aba40da348b3afe323214a9792012e9d0bbc664d'
ANG_SHA='d019713f8a9c6e864d60cc796104a0cdef629e491e6ab8de757995aa4f3672f2'

def verify_sources(root: Path) -> dict:
    root=Path(root).resolve();lock=json.loads((root/'SOURCE_LOCK.json').read_text())
    ids={}
    for s in lock['sources']:
        p=(root/s['path']).resolve()
        if not p.is_relative_to(root) or not p.is_file():raise ValueError('SOURCE_IDENTITY path')
        b=p.read_bytes()
        if len(b)!=s['bytes'] or hashlib.sha256(b).hexdigest()!=s['sha256']:raise ValueError('SOURCE_IDENTITY '+s['id'])
        if s['id'] in ids:raise ValueError('SOURCE_IDENTITY duplicate id')
        ids[s['id']]=s
    for sid,want in [('HH_INPUT',INPUT_SHA),('HH_OD',OD_SHA),('HH_ANGULAR',ANG_SHA)]:
        if ids[sid]['sha256']!=want:raise ValueError('SOURCE_IDENTITY frozen '+sid)
    return ids

def derive_channels(root: Path) -> dict:
    ids=verify_sources(root)
    with np.load(Path(root)/ids['HH_INPUT']['path'],allow_pickle=False) as f:
        arrays={k:f[k] for k in f.files}
    for k,shape in [('s_eps',(12,)),('p_eps',(12,)),('s_C',(12,12)),('p_C',(12,12)),('phase_E',(49,)),('Q',(49,25)),('parity',(49,49))]:
        a=arrays[k]
        if a.shape!=shape or a.dtype.kind!='f' or a.dtype.itemsize!=8 or not np.isfinite(a).all():raise ValueError('ARRAY_CONTRACT '+k)
    # Literal ordering at pinned od_run.py:assemble; archived Python is NOT executed.
    reg=[(0,j) for j in range(24)]+[(1,j) for j in range(1,24)]
    e0=Fraction.from_float(float(arrays['s_eps'][0]));rows=[]
    for row,(active,j) in enumerate(reg):
        orbital=('s','px','pz')[j//8];key='s_eps' if orbital=='s' else 'p_eps';e=float(arrays[key][j%8]);gap=Fraction.from_float(e)-e0
        kind='NEGATIVE_ENERGY_RITZ' if e<0 else 'POSITIVE_ENERGY_PSEUDOSTATE' if e>0 else 'ZERO_ENERGY_UNCLASSIFIED'
        rows.append(dict(row=row,active_center=active,j=j,orbital=orbital,radial_index=j%8,spectator='other_center_s_radial_0',kind=kind,one_center_energy_hex=e.hex(),represented_gap_Eh=f'{gap.numerator}/{gap.denominator}',phase_energy_hex=float(arrays['phase_E'][row]).hex(),free_electron_delta=0 if e<0 else None,physical_threshold_J=None,physical_rate_admitted=False,relevance='CONDITIONAL' if e<0 else 'UNRESOLVED',sources=['HH_INPUT','HH_OD','HH_ANGULAR','HH_MODEL']))
    for row in (47,48):
        rows.append(dict(row=row,ionic_arrangement_index=row-47,kind='IONIC_VARIATIONAL_TRIAL',configuration='Hminus_trial + HII; arrangement label needs asymptotic crosswalk',phase_energy_hex=float(arrays['phase_E'][row]).hex(),physical_threshold_J=None,free_electron_delta=0,physical_rate_admitted=False,relevance='CONDITIONAL',sources=['HH_INPUT','HH_OD','HH_MODEL']))
    q=[]
    for col in range(25):
        support=np.flatnonzero(arrays['Q'][:,col]);q.append(dict(column=col,rows=[int(i) for i in support],weights_hex=[float(arrays['Q'][i,col]).hex() for i in support]))
    return dict(schema='WU088_C0_HH_CHANNEL_CROSSWALK_V1',source_input_sha256=INPUT_SHA,source_lock='SOURCE_LOCK.json',common=dict(model_spin_S=0,model_spin_multiplicity=1,physical_unpolarized_degeneracy=None,physical_principal_quantum_number=None,initial_reference_row=0,reference_row_is_not_admitted_collision_initial_condition=True,frame='local_matter_tetrad',represented_energy_unit='Eh',rate_unit='m^3 s^-1',event_density_unit='m^-3 s^-1',heat_unit='J m^-3 s^-1',symmetric_identical_pair_event_factor='1/2 only after defining an unordered HI+HI event cross section',q_weights='serialized binary64 values, not freshly evaluated 1/sqrt(2)',physical_cross_sections=None,atomic_constants_pin=None,process_assignment='Negative Ritz: elastic or excitation candidate; positive Ritz: continuum representation candidate only; ionic trial: ion-pair candidate only',physical_threshold_owner='Requires finite-model asymptotic projector and source-authorized continuum/flux normalization; phase_E is not a threshold',domain_ref='APPLICATION_CONTRACT.json#/physical_domain',state_ownership='No automatic rate injection into BASS'),summary=dict(neutral_total=47,neutral_negative_energy=sum(x['kind']=='NEGATIVE_ENERGY_RITZ' for x in rows),neutral_positive_energy=sum(x['kind']=='POSITIVE_ENERGY_PSEUDOSTATE' for x in rows),ionic_trial_total=2,physical_rate_admitted_count=0),rows=rows,q_columns=q)

def validate_contract(application: dict, crosswalk: dict, obligations: dict) -> list[str]:
    """Check this frozen C0 handoff, not approve an arbitrary future model."""
    errors=[]
    if not all(isinstance(x,dict) for x in (application,crosswalk,obligations)):
        return ['SCHEMA_NOT_OBJECT']
    try:
        source=verify_sources(Path(__file__).resolve().parent)
        expected=derive_channels(Path(__file__).resolve().parent)
        # Equality here binds the scientifically untouched represented input,
        # not a comparison of independently computed physical cross sections.
        if crosswalk!=expected:errors.append('CROSSWALK_SOURCE_OR_SEMANTICS_MISMATCH')
        wanted_ns={'geometry_coordinate':'geometry_z_au','cosmological_coordinate':'cosmological_redshift','hh_matrix':'D_HH','doppler':'doppler_factor','hh_error':'epsilon_D','correlation_amplitude':'opacity_correlation_amplitude'}
        if application['namespaces']!=wanted_ns:errors.append('NAMESPACE_ALIAS')
        if application['physical_application_admitted'] is not False:errors.append('PHYSICAL_GATE_PROMOTION')
        domain=application['physical_domain']
        required_domain={'temperature_K','collision_energy_J','cosmological_redshift','number_density_m3','relative_velocity_distribution','source_SED','finite_tilt_range','observable_error_budget','atomic_unit_to_SI_constants'}
        if set(domain)!=required_domain:errors.append('DOMAIN_FIELDS')
        for name,d in domain.items():
            if d!={'value':None,'status':'DOMAIN_CONTRACT_REQUIRED','source':None}:errors.append('UNBOUND_DOMAIN '+name)
        audit=application['audit_fixture']
        if audit['is_physical_production_domain'] is not False:errors.append('FIXTURE_AS_DOMAIN')
        if audit['photon_energy_eV']!=['10','100'] or audit['baseline_tilt']!=0:errors.append('FIXTURE_SOURCE_MISMATCH')
        if audit['number_density_cm3']!={'H':'5.16295e-5','He':'4.0787305e-6'}:errors.append('FIXTURE_DENSITY')
        expected_ids={a+'_'+s for a in ['PHOTOIONIZATION','ELECTRON_IMPACT_IONIZATION'] for s in ['HI','HeI','HeII']}
        expected_ids.update('RADIATIVE_RECOMBINATION_'+s for s in ['HII','HeII','HeIII'])
        expected_ids.update(['DIELECTRONIC_RECOMBINATION_HeII','COLLISIONAL_EXCITATION_COOLING_HHe','FREE_FREE_COOLING','COMPTON_EXCHANGE','ADIABATIC_WORK'])
        p=application['processes'];ids=[x['process_id'] for x in p]
        if len(ids)!=len(set(ids)) or set(ids)!=expected_ids:errors.append('PROCESS_OWNERSHIP')
        for x in p:
            owner='BASS_GEOMETRY_THERMAL_RECEIVER' if x['process_id']=='ADIABATIC_WORK' else 'BASS_EXISTING_MICRO0'
            if x['owner']!=owner:errors.append('WRONG_OWNER')
            if x['hh_replaces_baseline'] is not False:errors.append('HH_BASELINE_REPLACEMENT')
            if x['provider_admitted'] is not False or x['provider_implementation_identity'] is not None:errors.append('UNBOUND_PROVIDER')
            if x['source']['id']!='BASS_R1' or x['source']['sha256']!=source['BASS_R1']['sha256']:errors.append('PROCESS_SOURCE')
            if x['relevance']!='REQUIRED_FOR_SELECTED_CONSUMER':errors.append('BASELINE_RELEVANCE')
        items=obligations['items'];oi=[i['id'] for i in items]
        need={'O_DOMAIN','O_PROVIDER','O_R2N','O_HMINUS','O_CONTINUUM','O_SPIN','O_EXCITATION','O_ASYMPTOTIC','O_CERT','O_RELEVANCE'}
        if len(oi)!=len(set(oi)) or set(oi)!=need or any(i['status']!='OPEN' for i in items):errors.append('OBLIGATION_CEILING')
        if obligations['proved_irrelevant_channels']!=[]:errors.append('UNPROVED_NEGLIGIBILITY')
        c=obligations['counterexample']
        delta=c['ion_pair_delta'];nw=c['H_nuclei_weights'];qw=c['charge_weights']
        if delta!=[-2,1,1,0] or nw!=[1,1,1,0] or qw!=[0,1,-1,-1]:errors.append('ION_PAIR_SEMANTICS')
        if sum(a*b for a,b in zip(nw,delta))!=0 or sum(a*b for a,b in zip(qw,delta))!=0:errors.append('CONSERVATION')
    except (KeyError,TypeError,ValueError,AttributeError,OSError) as exc:
        errors.append('MALFORMED_OR_UNBOUND_CONTRACT '+str(exc))
    return sorted(set(errors))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--validate',action='store_true')
    p.add_argument('--require-application',action='store_true')
    args=p.parse_args()
    if args.validate or args.require_application:
        app=json.loads((args.root/'APPLICATION_CONTRACT.json').read_text())
        cross=json.loads((args.root/'HH_CHANNEL_CROSSWALK.json').read_text())
        obl=json.loads((args.root/'RELEVANCE_OBLIGATIONS.json').read_text())
        errors=validate_contract(app,cross,obl)
        print(json.dumps({'metadata_valid':not errors,'errors':errors,'physical_application_admitted':False,'native_dispatches':0},indent=2))
        raise SystemExit(2 if errors else 3 if args.require_application else 0)
    print(json.dumps(derive_channels(args.root),ensure_ascii=False,indent=2))
