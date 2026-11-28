"""Validate the frozen C2e semantic contract, not physical truth or readiness.

This is deliberately specific to schema v1. A future scientific registration
requires a new contract/version, not replacing its unresolved fields in place.
No solver, network, imports of physics kernels, or numerical tolerance inference.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DOMAIN_FIELDS=('production_energy_frame','mass_normalization',
 'projectile_isotope_and_mass','target_isotope_and_mass','production_trajectory',
 'finite_b_interval','finite_time_or_z_window','production_R_interval')

def validate(c):
    errors=[]
    def require(ok,code):
        if not ok:errors.append(code)
    try:
        require(c['schema']=='bass-he.c2e.domain-target.v1','SCHEMA_MISMATCH')
        d=c['collision_domain'];p=c['targets']['fixed_pair'];s=c['targets']['large_R_rank5']
        require(all(d[k] is None for k in DOMAIN_FIELDS),'UNREGISTERED_PRODUCTION_INPUT')
        require(d['missing_production_inputs']==list(DOMAIN_FIELDS),'MISSING_INPUTS_HIDDEN')
        require(d['diagnostic_cutoffs_imported_as_physical_domain'] is False,'DIAGNOSTIC_CUTOFF_PROMOTION')
        require(d['source_energy_frames_are_interchangeable'] is False,'ENERGY_FRAME_ALIASING')
        require(d['full_C2_collision_coverage_certified'] is False,'UNCERTIFIED_COVERAGE')
        require(d['priority_energy_anchors']==[
          {'value':.5,'unit':'keV/u','status':'RESEARCH_PRIORITY_ONLY'},
          {'value':5.,'unit':'keV/u','status':'RESEARCH_PRIORITY_ONLY'}],'ENERGY_ANCHOR_SEMANTICS')
        require(c['conventions']['nuclear_center_of_mass_is_electronic_origin'] is False,'ORIGIN_CM_ALIASING')
        require(c['conventions']['nuclear_repulsion_in_H_e'] is False and c['conventions']['H_e_continuum_threshold_E_A']==0,'THRESHOLD_CONVENTION')
        require(type(p['rank']) is int and p['rank']==2,'PAIR_RANK')
        require(p['is_full_H_energy_Riesz_projector'] is False and type(p['full_H_external_gap']) in (int,float) and p['full_H_external_gap']==0,'OMITTED_DEGENERATE_PARTNER')
        require(p['incoming_H1s_included'] is False,'PAIR_INCOMING_CHANNEL_ALIAS')
        require(type(s['rank']) is int and s['rank']==5 and s['sector_ranks']=={'m0':3,'m_plus1':1,'m_minus1':1},'CLUSTER_MULTIPLICITY')
        require(s['atomic_members']==['H_1s','He_2s','He_2p_m0','He_2p_m_plus1','He_2p_m_minus1'],'CLUSTER_MEMBERSHIP')
        require(s['certified_external_gap_lower_bound'] is None and s['finite_interval_R'] is None and s['quantitative_large_R_start'] is None,'GAP_CERTIFICATE_NOT_ESTABLISHED')
        require(s['actual_UA_correlation_established'] is False and s['equal_to_lowest_five_excited_for_all_R_claimed'] is False and s['uniform_full_H_gap_to_R_zero_claimed'] is False,'UNPROVED_GLOBAL_CORRELATION')
        require(c['targets']['D1_model']['replaced_by_rank5_or_rank6_automatically'] is False and c['targets']['D1_model']['status']=='NOT_RELEASED','D1_MODEL_PROMOTION')
        e=c['error_contract']
        require(all(e[k] is False for k in ('empirical_convergence_is_continuum_enclosure','Ritz_gap_is_certified_external_gap','L2_projector_error_certifies_Ly_matrix_elements')),'ENCLOSURE_PROMOTION')
        require(e['new_numeric_tolerances'] is None and e['new_R_grid'] is None,'UNREGISTERED_NUMERICAL_CONTRACT')
        x=c['execution']
        require(all(type(x[k]) is int and x[k]==0 for k in ('new_eigensolves','new_scientific_quadratures','new_time_propagations','old_scientific_suites_rerun')),'UNREGISTERED_PHYSICAL_EXECUTION')
        require(x['execution_ready'] is False and x['scientific_commands']==[] and x['Eq55']=='NOT_RUN' and x['NCP64_actual_scaling']=='NOT_RUN','EXECUTION_PROMOTION')
        require(c['global_gates']=={'CODE_I02_CLOSED':True,'full_C2_closed':False,'scientific_PROMOTE':'HOLD','full_certificate_fail_closed':True,'Eq55_next_node_authorized':False,'production_default_change':'NOT_AUTHORIZED'},'GLOBAL_GATE_MUTATION')
        h=c['hpc_policy']
        require(h['fast_math'] is False and h['implicit_backend_fallback'] is False and h['actual_host_preflight_required'] is True,'HPC_ACCURACY_POLICY')
    except (KeyError,TypeError):
        errors.append('MISSING_OR_MALFORMED_REQUIRED_FIELD')
    return {'contract_valid':not errors,'errors':errors,'physical_launch_enabled':False,
            'production_domain_status':'UNRESOLVED','validation_scope':'frozen C2e semantic invariants only; not proof of physical correctness'}

def atomic_create(path,data):
    temporary=path.with_suffix(path.suffix+'.pending')
    if path.exists():raise FileExistsError(path)
    with temporary.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    os.link(temporary,path);temporary.unlink()
    fd=os.open(path.parent,os.O_DIRECTORY);os.fsync(fd);os.close(fd)

def main():
    p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,default=ROOT/'contract/C2E_TARGET_AND_DOMAIN_CONTRACT.json');p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();raw=a.contract.read_bytes();result=validate(json.loads(raw))
    result.update(contract_sha256=hashlib.sha256(raw).hexdigest(),validator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),new_physical_evaluations=0)
    atomic_create(a.output,(json.dumps(result,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps(result));raise SystemExit(0 if result['contract_valid'] else 1)

if __name__=='__main__':main()
