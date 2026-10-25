"""One scoped changed-contract suite; no historical suite or ODE invocation."""
import argparse
import copy
import importlib.metadata
import json
from pathlib import Path
import sys
import traceback

import numpy as np
import consumer as c
from write_rust_client import write_client

ROOT=Path(__file__).resolve().parent
CHECKS=[]

def check(name,condition,details=None):
    row={'name':name,'passed':bool(condition),'details':details}
    CHECKS.append(row)
    c.write_json(ROOT/'checks_partial.json',CHECKS)
    if not condition:raise AssertionError(name+': '+str(details))

def row_error(actual,expected,scale):
    a,b,s=np.asarray(actual),np.asarray(expected),np.asarray(scale)
    delta=np.abs(a-b)
    if delta.ndim==2:s=s[:,None]
    broadcast=np.broadcast_to(s,delta.shape)
    if np.any((broadcast==0)&(delta!=0)):return float('inf')
    return float(np.max(np.divide(delta,broadcast,out=np.zeros_like(delta,dtype=float),where=broadcast>0)))

def rejected(name,fn):
    try:fn()
    except (ValueError,c.wu.LedgerError) as exc:
        check(name,True,{'exception':type(exc).__name__,'message':str(exc)})
    else:check(name,False,'expected input rejection')

def normalization_checks():
    x=np.asarray([0.31,0.23]);dx=np.asarray([-0.06,0.08]);r=2.7;dr=0.4
    def direct(x,r):
        n=r*x
        s=np.asarray([-0.7*n[0]*n[1]+0.13,0.7*n[0]*n[1]-0.17*n[1]])
        R=0.11*r+0.05*n[0]**2
        return (s-x*R)/r,s,R
    n=r*x;dn=r*dx+dr*x
    ds=np.asarray([-0.7*(dn[0]*n[1]+n[0]*dn[1]),
                    0.7*(dn[0]*n[1]+n[0]*dn[1])-0.17*dn[1]])
    dR=0.11*dr+0.1*n[0]*dn[0]
    expected,s,R=direct(x,r)
    f,df=c.normalize_source_directional(x,s,r,reference_source=R,dx=dx,dsource=ds,
                                        dreference=dr,dreference_source=dR)
    h=1e-100
    oracle=np.imag(direct(x+1j*h*dx,r+1j*h*dr)[0])/h
    scale=(np.abs(ds)+np.abs(R*dx)+np.abs(x*dR))/r+np.abs(f*dr/r)
    directional=row_error(df,oracle,scale)
    check('changed_reference_directional_derivative',directional<=3e-12,{'row_scaled':directional})
    wrong=s/r
    mutation=float(np.max(np.abs(wrong-f)))
    check('omitted_quotient_term_mutation_detected',mutation>1e-3,{'max_absolute_error':mutation})
    wrong_derivative=(ds-R*dx-x*dR)/r
    derivative_mutation=row_error(wrong_derivative,oracle,scale)
    check('omitted_density_derivative_quotient_mutation_detected',derivative_mutation>1e-3,
          {'row_scaled_error':derivative_mutation,'omitted_term':'-F*dr/r'})
    a=0.5;r0=0.25;da=0.04;rf=r0*a**-3;drf=-3*rf*da/a
    def fixed(a):
        rr=r0*a**-3;nn=rr*x
        ss=np.asarray([nn[0]**2+nn[1],nn[0]*nn[1]-2*nn[1]])
        return ss/rr,ss
    nf=rf*x;dnf=drf*x
    dsf=np.asarray([2*nf[0]*dnf[0]+dnf[1],dnf[0]*nf[1]+nf[0]*dnf[1]-2*dnf[1]])
    ff,dff=c.normalize_source_directional(x,fixed(a)[1],rf,dsource=dsf,dreference=drf)
    fo=np.imag(fixed(a+1j*h*da)[0])/h
    fs=np.abs(dsf/rf)+np.abs(ff*drf/rf)
    fixed_error=row_error(dff,fo,fs)
    check('fixed_comoving_scale_factor_derivative',fixed_error<=3e-12,{'row_scaled':fixed_error})
    for value in [0.0,-1.0,float('nan'),float('inf')]:
        rejected('normalization_invalid_reference_'+str(value),lambda value=value:c.normalize_source_directional(x,s,value))
    return {'scope':'manufactured algebraic controls; not astrophysical source data',
            'changed_reference_directional_row_scaled':directional,
            'fixed_comoving_a_directional_row_scaled':fixed_error,
            'omitted_quotient_term_mutation_max_abs':mutation,
            'omitted_density_derivative_quotient_mutation_row_scaled':derivative_mutation,
            'x':x.tolist(),'dx':dx.tolist(),'r':r,'dr':dr,'S':s.tolist(),'R':R,
            'dS':ds.tolist(),'dR':dR,'computed_derivative':df.tolist(),
            'complex_step_derivative':oracle.tolist()}

def run_python():
    result,binding,records,events,contrib=c.evaluate_endpoint()
    c.write_endpoint_files(result,binding,records,events,contrib)
    x=np.asarray(result['x']);rates=np.asarray(result['saved_rates_per_source_target'])
    f=np.asarray(result['rec_output_25']);J=np.asarray(result['rec_jacobian_25_by_23'])
    wu=np.asarray(result['wu_source_22']);scales=np.asarray(result['source_row_scales_22'])
    r=result['reference_density_m3']
    check('exact_source_identity',len(result['input_identity_checked'])==10,result['input_identity_checked'])
    check('actual21_labels_and_mapping',len(x)==21 and len(set(binding['consumer_to_donor_indices']))==21)
    check('actual_neutron_tritium_zeros',all(x[c.rec.SPECIES.index(k)]==0 for k in ['n','T_0','T_1']))
    check('actual_He4_abundance_not_scaled_fraction',abs(sum(x[10:13])-0.082)<1e-14,{'sum':float(sum(x[10:13]))})
    coherence={'r_relative':abs(binding['reference']['donor_nH_ref_cm3_to_m3']/r-1),
               'a_relative':abs(binding['endpoint']['a']/(1/3)-1),
               'z_relative':abs(binding['endpoint']['z']/2-1),
               'eta_relative':abs(binding['endpoint']['eta']/binding['time']['eta_log_a_over_a_initial']-1)}
    check('endpoint_reference_epoch_coherence',max(coherence.values())<=1e-14,coherence)
    source_err=row_error(wu,f[:22],scales)
    check('WU_REC_species_and_electron_match',source_err<=3e-13,{'row_scaled':source_err})
    check('WU_exact_incidence_conservation',all(v=='0' for v in result['exact_decimal_representation_conservation']['isotopes'].values()) and result['exact_decimal_representation_conservation']['charge']=='0' and result['exact_decimal_representation_conservation']['baryon']=='0',result['exact_decimal_representation_conservation'])
    physical=np.asarray(result['physical_species_and_e_fast_source_m3_s'])
    si_err=row_error(physical/r,wu,scales)
    energy_si=np.asarray(result['signed_energy_source_J_m3_s'])
    si_energy_err=row_error(energy_si/(r*c.EV_TO_J),f[22:25],np.abs(f[22:25]))
    check('per_reference_SI_conversions',max(si_err,si_energy_err)<=3e-14,{'number':si_err,'energy':si_energy_err})
    # Direct independently supplied K is retained; no subtraction-derived K.
    energy_rows=np.asarray([v['energy_eV_per_ref_s'] for v in contrib])
    balances=np.sum(energy_rows,axis=1)
    energy_scales=np.sum(np.abs(energy_rows),axis=1)
    energy_err=row_error(balances,np.zeros(26),energy_scales)
    total_energy_err=abs(float(sum(f[22:25])))/float(sum(abs(f[22:25])))
    per_event_err=max(abs(v['CR_generic_event_ledger_eV']['residual_ev'])/(2*v['CR_generic_event_ledger_eV']['imported_photon_ev']) for v in contrib)
    check('collision_energy_and_CR_event_partition',max(energy_err,total_energy_err,per_event_err)<=3e-12,{'26_component_row_scaled':energy_err,'total_row_scaled':total_energy_err,'CR_per_event_row_scaled':per_event_err})
    derivative=np.zeros((25,23));h=1e-100
    for j in range(23):
        xx=x.astype(complex);aa=np.asarray([1.0,1.0],dtype=complex)
        if j<21:xx[j]+=1j*h
        else:aa[j-21]+=1j*h
        derivative[:,j]=np.imag(c.rec.target_response(xx,rates,aa)[0])/h
    jscale=np.max(np.abs(J),axis=1)
    jerr=row_error(derivative,J,jscale)
    check('REC_actual_point_all23_Jacobian_columns',jerr<=3e-12,{'row_scaled':jerr,'zero_rows_exact':bool(np.all(derivative[jscale==0]==0))})
    # New helper consumes physical source, never divides the REC f twice.
    fback,_=c.normalize_source_directional(x,r*f[:21],r)
    check('normalized_REC_not_divided_twice',row_error(fback,f[:21],scales[:21])<=3e-14)
    jback=r*J/r
    check('physical_source_J_chain_mapping',row_error(jback,J,jscale)<=3e-14)
    args=[x,rates,c.SOURCE_NAMES,(1.0,1.0),c.rec.SPECIES,r,c.FRAME,c.SUPPORT_EV,c.REFERENCE,c.SOURCE_ID]
    mutations=[('wrong_label',4,tuple(reversed(c.rec.SPECIES))),('wrong_reference_density',5,2*r),
               ('wrong_frame',6,'electron_rest'),('wrong_support',7,(13.6,50000.0)),
               ('wrong_reference_mode',8,'actual_baryon_density'),('negative_source_amplitude',3,(-1.0,1.0)),
               ('missing_required_source',2,('stellar',)),('missing_source_data',1,None),
               ('C23B_spectral_substitution',9,'C23B_original_z2.316_50000eV')]
    for name,index,value in mutations:
        modified=list(args);modified[index]=value
        rejected(name,lambda modified=modified:c.validate_binding(*modified))
    species=c.wu.catalog(records)
    duplicate=copy.deepcopy(events[0]);duplicate['provider']='competing_extent_owner';duplicate['provider_domain']='different domain prose'
    # Original exact-key registry is correctly reused; this test exposes why
    # the scientific physical key must independently ignore arbitrary prose.
    native=c.wu.register_ownership([events[0],duplicate],species)
    check('original_WU_domain_key_not_overlap_certificate',len(native)==2)
    rejected('domain_text_duplicate_physical_extent',lambda:c.check_extent_owners([events[0],duplicate],species))
    state_prose_duplicate=copy.deepcopy(duplicate)
    state_prose_duplicate['state_resolution']='different prose for the same WU ground-state and electron-pool identities'
    rejected('state_resolution_prose_duplicate_physical_extent',lambda:c.check_extent_owners([events[0],state_prose_duplicate],species))
    norm=normalization_checks()
    result['checks']=CHECKS
    result['metrics']={'WU_REC_source_row_scaled':source_err,'REC_Jacobian_complex_step_row_scaled':jerr,
                       'energy_component_row_scaled':energy_err,'total_energy_row_scaled':total_energy_err,
                       'CR_event_partition_row_scaled':per_event_err,'SI_number_row_scaled':si_err,
                       'SI_energy_row_scaled':si_energy_err,'endpoint_coherence':coherence}
    result['scaling_definition']={'source':'sum absolute individual event contributions; exact zero when scale zero',
                                  'Jacobian':'maximum absolute analytic reference coefficient over23columns per row; exactzero when rowzero',
                                  'energy':'sum absolute signed sector powers; exactzero for no event'}
    result['complex_step_Jacobian_raw']=derivative.tolist()
    result['Jacobian_row_scales']=jscale.tolist()
    result['energy_component_residuals_eV_per_ref_s']=balances.tolist()
    result['energy_component_scales_eV_per_ref_s']=energy_scales.tolist()
    result['normalization_controls']=norm
    result['python_test_status']='pass_scoped'
    result['rust']={'status':'not_run','scientific_domain':'OPEN'}
    result['scientific_admission']='pending independent review'
    result['environment']={'python':sys.version,'numpy':np.__version__,
                           'scipy':importlib.metadata.version('scipy'),
                           'matplotlib':importlib.metadata.version('matplotlib'),
                           'BLAS_threads':1,'workers':1}
    result['generated_rust_client']=write_client(result)
    c.write_json(ROOT/'results.json',result)
    from render_sources import render
    render(result,contrib)
    print(json.dumps({'status':'pass_scoped','checks':len(CHECKS),'metrics':result['metrics']},indent=2))

def check_rust(path):
    result=json.loads((ROOT/'results.json').read_text())
    raw=json.loads(Path(path).read_text())
    f=np.asarray(result['rec_output_25']);J=np.asarray(result['rec_jacobian_25_by_23'])
    scales=np.asarray(result['source_row_scales_22'])[:21]
    jscale=np.asarray(result['Jacobian_row_scales'])[:21]
    rhs_err=row_error(raw['actual_rhs'],f[:21],scales)
    jac_err=row_error(raw['actual_jacobian'],J[:21,:21],jscale)
    check('Rust_actual21_RHS_against_REC',rhs_err<=3e-13,{'row_scaled':rhs_err})
    check('Rust_fullwrite21_Jacobian_against_REC',jac_err<=3e-13,{'row_scaled':jac_err})
    positive=np.asarray(raw['positive_supported_point'])
    rates=np.asarray(result['saved_rates_per_source_target'])
    pref=c.rec.target_response(positive,rates,(1.0,1.0))[0][:21]
    A=np.asarray(result['wu_coefficient_matrix_21_by_21'])
    pscale=np.abs(A)@positive
    perr=row_error(raw['positive_supported_rhs'],pref,pscale)
    check('Rust_positive_supported_point',perr<=3e-13 and all(positive[c.rec.SPECIES.index(k)]==0 for k in ['n','T_0','T_1']),{'row_scaled':perr})
    check('Rust_zero_boundary',all(v==0 for v in raw['zero_boundary_rhs']))
    for name in ['negative_state_rejected','outside_time_rejected','outside_upper_rejected','time_derivative_stencil_rejected']:
        check('Rust_'+name,raw[name])
    wrong_err=row_error(raw['wrong_finite_jacobian'],J[:21,:21],jscale)
    check('Rust_finite_wrong_J_gate_vs_accuracy',raw['wrong_finite_jacobian_gate_admitted'] and wrong_err>1e-3,
          {'gate_admitted':raw['wrong_finite_jacobian_gate_admitted'],'independent_row_scaled_error':wrong_err})
    result['rust']={'status':'ADAPTER_TESTED','raw':raw,
                    'RHS_row_scaled':rhs_err,'Jacobian_row_scaled':jac_err,'positive_point_row_scaled':perr,
                    'wrong_finite_J_row_scaled':wrong_err,'checks':CHECKS,
                    'physical_domain_certification':'OPEN','trajectory_error_control':'OPEN',
                    'witness':'transparent caller assertion, not native floating-point certification'}
    result['all_changed_contract_checks_observed_pass']=True
    c.write_json(ROOT/'results.json',result)
    print(json.dumps({'rust_status':'ADAPTER_TESTED','checks':len(CHECKS),'rhs_error':rhs_err,'jac_error':jac_err,'wrong_finite_J_error':wrong_err},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--rust-output');args=parser.parse_args()
    try:
        check_rust(args.rust_output) if args.rust_output else run_python()
    except Exception as exc:
        c.write_json(ROOT/'execution_failure.json',{'class':'implementation_or_input_pending_diagnosis','exception':repr(exc),'traceback':traceback.format_exc(),'checks':CHECKS})
        raise
