"""Frozen changed-dependency suite; execute only through bounded runner."""
import hashlib
import json
import os
from pathlib import Path
import sys
import traceback

HERE=Path(__file__).resolve().parent; UNIT=HERE.parent; INPUT=UNIT/'runtime_inputs'
sys.path.insert(0,str(INPUT/'helpers'));sys.path.insert(0,str(INPUT/'provider'))
import numpy as np
import scipy
from donor_projection import SavedBackground
import atomic_network
from primary_electron import (emit_atoms,weights,weight_jvp,validate_binding,
    receiver_packet,C_M_S,CHI_EV,SOURCE_NAMES,EVENT)

OUT=Path(os.environ['PRIMARY_ELECTRON_OUTPUT_DIR']); checks=[]; payload={}
CONTRACT=json.loads((UNIT/'theory/IMPLEMENTATION_CONTRACT.json').read_text())
TOL=CONTRACT['acceptance']


def clean(value):
    if isinstance(value,np.ndarray):return value.tolist()
    if isinstance(value,np.generic):return value.item()
    if isinstance(value,dict):return {k:clean(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [clean(v) for v in value]
    return value


def write(path,value):path.write_text(json.dumps(clean(value),indent=2,allow_nan=False)+'\n')
def checkpoint(label):
    write(OUT/'partial_payload.json',payload);write(OUT/'checks_partial.json',checks)
    print(label,flush=True)
def check(name,passed,**details):checks.append({'name':name,'pass':bool(passed),**clean(details)})
def relative(actual,reference):return np.abs(actual-reference)/np.abs(reference)


try:
    binding=json.loads((INPUT/'endpoint/ACTUAL_STATE_BINDING.json').read_text())
    saved=json.loads((INPUT/'endpoint/AGGREGATE_PAYLOAD.json').read_text())
    config=json.loads((INPUT/'source_history/MODEL_CONFIG.json').read_text())
    donor=json.loads((INPUT/'source_history/DONOR_CONTRACT.json').read_text())
    y=binding['actual_abundance_per_ref'][binding['consumer_species_order'].index('H1_0')]
    r=binding['reference']['r_m3'];alpha=np.ones(2);eta=CONTRACT['physics']['observer_eta']
    bg=SavedBackground(INPUT/'endpoint/grid044_history.npz',donor['inputs']['background_sha256'],donor['background']['expected_shapes'])
    provider=atomic_network._load_provider()
    def sigma(E):return provider.sigma('HI',E)*1e-22
    Eo,Ee,Eb,A,meta=emit_atoms(bg,config['sources'],config['birth_energy_support_eV'],saved['source_normalizers_reused'],eta,sigma)
    w=weights(A,y,alpha,r)
    atom_file=OUT/'PRIMARY_SOURCE_ATOMS.npz'
    np.savez(atom_file,E_observer_eV=Eo,E_electron_eV=Ee,E_birth_eV=Eb,
             per_source_A=A,per_source_weight_ref=w)
    payload.update({'unit_id':CONTRACT['unit_id'],'event_owner':EVENT,
      'source_names':SOURCE_NAMES,'frame':binding['frame'],'reference':binding['reference'],
      'y_H1_actual_per_ref':y,'r_m3':r,'alpha':alpha,'eta':eta,'metadata':meta,
      'array_file':'PRIMARY_SOURCE_ATOMS.npz','array_sha256':hashlib.sha256(atom_file.read_bytes()).hexdigest(),
      'array_units':{'E_observer_eV':'eV','E_electron_eV':'eV','E_birth_eV':'eV',
        'per_source_A':'m2 per reference','per_source_weight_ref':'per reference per proper second'},
      'physical_weight_rule':'r_m3 * per_source_weight_ref; m^-3 s^-1',
      'source_history':'forward continuous zero-opacity births with anisotropic redshift',
      'finite_measure_CDF_convergence':'not evaluated; inherited moment accuracy only',
      'receiver':receiver_packet(),'new_IVPs':0,'historical_suites_rerun':0,
      'environment':{'numpy':np.__version__,'scipy':scipy.__version__}})
    check('finite_positive_source_atom_support',len(Eo)>0 and np.all(np.isfinite(Eo)) and np.all(np.isfinite(Ee)) and np.all(np.isfinite(A)) and np.all(np.isfinite(w)) and np.all(Eo>=CHI_EV) and np.all(Eo<=150) and np.all(Ee>=0) and np.all(Ee<=136.4) and np.all(A>=0) and np.all(w>=0),
          E_observer_range_eV=[Eo.min(),Eo.max()],E_electron_range_eV=[Ee.min(),Ee.max()])
    checkpoint('atoms_saved')
    basis=np.stack([A.sum(axis=1),(A*Eo).sum(axis=1),(A*Ee).sum(axis=1)],axis=1)
    moment_ref=weights(basis,y,alpha,r); moment_phys=r*moment_ref
    saved_basis=np.asarray(saved['production_response'])[:,0,:]
    saved_ref=y*np.asarray(saved['rates_per_source_target'])[:,0,:]
    basis_error=relative(basis,saved_basis);rate_error=relative(moment_ref,saved_ref)
    check('same_quadrature_source_moments',np.max(basis_error)<=TOL['same_quadrature_moments_relative'],relative_by_source_quantity=basis_error)
    check('admitted_endpoint_H1_source_moments',np.max(rate_error)<=TOL['same_quadrature_moments_relative'],relative_by_source_quantity=rate_error,
          reference_scope='saved fine rates, already admitted under inherited1e-4 moment gate')
    partition=np.abs(moment_ref[:,1]-CHI_EV*moment_ref[:,0]-moment_ref[:,2])/moment_ref[:,1]
    check('single_owner_energy_partition',np.max(partition)<=TOL['partition_relative'],relative_by_source=partition)
    payload['moments']={'quantity_order':['number','absorbed_photon_eV','primary_kinetic_eV'],
      'A_moments':basis,'per_ref_per_s':moment_ref,'physical_per_m3_s':moment_phys,
      'energy_reservoirs_J_m3_s':np.stack([-moment_phys[:,1],CHI_EV*moment_phys[:,0],moment_phys[:,2]],axis=1)*CONTRACT['physics']['ev_to_J'],
      'reservoir_order':['radiation','binding','fast_kinetic'],'thermal_heat_J_m3_s':None}
    cdfs=[]
    for edge in (10.2,13.6,24.59,54.42,100.):
        mask=Ee<=edge
        cdfs.append({'E_electron_upper_eV':edge,'number_fraction':w[:,mask].sum(axis=1)/moment_ref[:,0],
                     'kinetic_energy_fraction':(w[:,mask]*Ee[mask]).sum(axis=1)/moment_ref[:,2]})
    payload['CDF']=cdfs
    payload['energy_eligibility']=[{'threshold_eV':edge,'comparison':'E_electron >= threshold',
      'number_fraction':w[:,Ee>=edge].sum(axis=1)/moment_ref[:,0],
      'kinetic_energy_fraction':(w[:,Ee>=edge]*Ee[Ee>=edge]).sum(axis=1)/moment_ref[:,2],
      'meaning':'energy eligibility only; stopping efficiency and deposition unspecified'} for edge in (10.2,13.6)]
    check('CDF_fractions_monotone_and_bounded',all(np.all(np.diff(np.array([p[key] for p in cdfs]),axis=0)>=0) and np.all(np.array([p[key] for p in cdfs])>=0) and np.all(np.array([p[key] for p in cdfs])<=1) for key in ('number_fraction','kinetic_energy_fraction')))
    derivatives={};h=TOL['complex_step_h']
    for physical in (False,True):
        analytic=[];cs=[]
        for column in range(4):
            dy=float(column==0);da=np.array([float(column==1),float(column==2)]);dr=float(column==3)
            analytic.append(weight_jvp(basis,y,alpha,r,dy,da,dr,physical=physical))
            cs.append(np.imag(weights(basis,y+1j*h*dy,alpha+1j*h*da,r+1j*h*dr,physical=physical))/h)
        analytic=np.stack(analytic,axis=-1);cs=np.stack(cs,axis=-1)
        scale=np.max(np.abs(analytic),axis=-1);zero=scale==0
        scaled=np.divide(np.max(np.abs(analytic-cs),axis=-1),scale,out=np.zeros_like(scale),where=~zero)
        check(('physical' if physical else 'reference')+'_local_complex_step_tangent',np.max(scaled)<=TOL['complex_step_derivative_scaled'] and np.all(cs[zero]==0),row_scaled_error=scaled)
        derivatives['physical' if physical else 'reference']={'columns':['y_H1','alpha_stellar','alpha_IGM','r_m3'],'moment_Jacobian':analytic}
    payload['local_derivatives']=derivatives
    physical_r=derivatives['physical']['moment_Jacobian'][:,:,-1]
    check('physical_density_partial_has_two_factors_of_r',np.max(relative(physical_r,2*moment_phys/r))<=TOL['complex_step_derivative_scaled'])
    zero_y=weights(basis,0.,alpha,r);zero_a=weights(basis,y,[0.,1.],r)
    check('zero_target_and_amplitude_boundaries',np.all(zero_y==0) and np.all(zero_a[0]==0) and np.all(np.isfinite(weight_jvp(basis,0.,[0.,1.],r,1.,[1.,0.],0.))))
    bad=[dict(y=y,alpha=alpha,r=0.),dict(y=y,alpha=alpha,r=-1.),dict(y=-1.,alpha=alpha,r=r),dict(y=y,alpha=[-1.,1.],r=r)]
    bad += [dict(y=y,alpha=alpha,r=r,**{k:v}) for k,v in [('frame','wrong'),('reference','wrong'),('source_id','wrong'),('source_names',('wrong','external_IGM')),('owners',(EVENT,EVENT))]]
    rejected=[]
    for arguments in bad:
        try:validate_binding(**arguments)
        except ValueError:rejected.append(True)
        else:rejected.append(False)
    check('invalid_inputs_and_duplicate_owner_rejected',all(rejected),cases_rejected=rejected)
    wrong_birth=(weights(A,y,alpha,r)*Eb).sum(axis=1)
    failures={'omit_r':np.max(relative(moment_ref/r,saved_ref)),
              'birth_instead_of_observer_energy':np.max(relative(wrong_birth,saved_ref[:,1])),
              'omit_threshold_subtraction':np.max(relative(moment_ref[:,1],saved_ref[:,2]))}
    check('discriminating_negative_controls',all(v>TOL['same_quadrature_moments_relative'] for v in failures.values()),relative_errors=failures)
    packet=receiver_packet()
    check('unqualified_stopping_has_no_heat',packet['physical_stopping_provider_admitted'] is False and packet['thermal_heat_J_m3_s'] is None)
    check('two_templates_add_one_event_extent',np.array_equal(moment_ref.sum(axis=0),np.sum(weights(basis,y,alpha,r),axis=0)) and packet['event_owner']==EVENT)
    checkpoint('suite_finished')
    write(OUT/'test_results.json',{'checks':checks,'pass_count':sum(c['pass'] for c in checks),'total':len(checks),'passed':all(c['pass'] for c in checks)})
    write(OUT/'SOURCE_PAYLOAD.json',payload)
    raise SystemExit(0 if all(c['pass'] for c in checks) else 1)
except BaseException as exc:
    if isinstance(exc,SystemExit):raise
    payload['failure']={'class':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
    checkpoint('exception')
    raise
