#!/usr/bin/env python3
"""Bind completed R1 Rust executions to independent reference comparisons.

No process is run here. Incomplete runs are omitted and named explicitly.
Split-spectrum output is compared only to its declared same-source control;
it is never scored as an error against the original-spectrum continuum.
"""
from __future__ import annotations
import argparse
import datetime
import json
import math
from pathlib import Path
from compare_rust_matrix import compare, diff, rows
from independent_birth_reference import sha

TARGETS={'count_relative':1e-8,'raw_age1_relative':1e-7,'raw_age2_relative':1e-7,
         'main_energy_relative':1e-8,'energy_weighted_q2_absolute':1e-11}


def admission(run):
    values=run['continuous_comparison']
    tests={
       'count':abs(values['survivor_com3']['relative'])<=TARGETS['count_relative'],
       'raw_age1':abs(values['age_sum_com_s']['relative'])<=TARGETS['raw_age1_relative'],
       'raw_age2':abs(values['age2_sum_com_s2']['relative'])<=TARGETS['raw_age2_relative'],
       'energy_weighted_q2':abs(values['energy_weighted_q2']['difference'])<=TARGETS['energy_weighted_q2_absolute']}
    for name in ('source_j','surviving_j','absorbed_j','thermal_j','chemical_j'):
        tests[name]=abs(values[name]['relative'])<=TARGETS['main_energy_relative']
    return {'status':'MEETS_BOUNDED_CONTINUOUS_REFERENCE_TARGETS' if all(tests.values()) else 'DOES_NOT_MEET_ALL_BOUNDED_TARGETS',
        'tests':tests,'direct_work_relative_error':values['work_independent_j']['relative'],
        'ledger_work_relative_error':values['work_ledger_j']['relative'],
        'ledger_work_error_over_source_energy':values['work_ledger_j']['difference_over_source_energy'],
        'geometry_work_admission':'Independent integral and energy subtraction remain separately reported; whole-operator interval certification is not assigned.'}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--matrix',type=Path,required=True)
    ap.add_argument('--reference',type=Path,required=True)
    ap.add_argument('--reference-plus',type=Path,required=True)
    ap.add_argument('--source-identity',type=Path,required=True)
    ap.add_argument('--matched',action='append',default=[],help='LABEL=MATCHED_JSON')
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    intent_path=args.matrix/'MATRIX_INTENT.json';intent=json.loads(intent_path.read_text())
    identity=json.loads(args.source_identity.read_text());identity_sha=sha(args.source_identity)
    if identity_sha!=intent['source_identity']['sha256']:raise ValueError('matrix and supplied source identity differ')
    for item in identity['source_files']:
        p=args.source_identity.parent/item['path']
        if sha(p)!=item['sha256']:raise ValueError('frozen R1 source mutation: '+str(p))
    reference_docs={case:json.loads(path.read_text()) for case,path in
        (('SIGNED_MINUS',args.reference),('SIGNED_PLUS',args.reference_plus))}
    refs={case:d['executions'][-1]['result'] for case,d in reference_docs.items()}
    matched={name:Path(path) for name,path in (v.split('=',1) for v in args.matched)}
    runs=[];pending=[];failed=[];completed=[];split_rows=[]
    for case in intent['cases']:
        name=case[0];directory=args.matrix/name;record_path=directory/'EXECUTION.json'
        if not record_path.exists():pending.append(name);continue
        record=json.loads(record_path.read_text())
        if record['source_identity']['sha256']!=identity_sha or record['binary_identity']!=intent['binary_identity']:
            raise ValueError('execution identity mismatch: '+name)
        if record['status']!='PROGRAM_COMPLETED' or record['exit_code']!=0:
            failed.append({'label':name,'receipt':str(record_path),'status':record['status']});continue
        data=directory/'data'
        for basename in ('SUMMARY.csv','TEMPLATES_RESULT.csv','BIRTHS.csv'):
            key='data/'+basename
            if sha(data/basename)!=record['files'][key]['sha256']:
                raise ValueError('post-execution data hash mismatch: '+name+'/'+basename)
        summary=rows(data/'SUMMARY.csv')[0]
        source_binding={'execution_receipt':str(record_path),'execution_receipt_sha256':sha(record_path),
            'source_identity_sha256':identity_sha,'binary_sha256':record['binary_identity']['sha256'],'wall_s':record['wall_s']}
        if int(summary['templates'])!=int(summary['available_templates']):raise ValueError('incomplete source: '+name)
        completed.append({'label':name,'cohorts':int(summary['cohorts']),'templates':int(summary['templates']),**source_binding})
        if summary['split']=='true':
            split_rows.append((name,data,summary,source_binding));continue
        run=compare(name,data,refs[summary['case']],matched.get(name))
        run['execution_binding']=source_binding
        run['target_disposition']=admission(run)
        runs.append(run)
    split_results=[]
    for name,data,split,binding in split_rows:
        control_name='gauss_r1_d8_m4_o8_e16';control_dir=args.matrix/control_name/'data'
        if control_name not in {r['label'] for r in runs}:
            split_results.append({'label':name,'status':'CONTROL_NOT_COMPLETED'});continue
        control=rows(control_dir/'SUMMARY.csv')[0]
        for k in ('case','birth','refinement','birth_degree','path_slabs','opacity_degree','event_degree'):
            if split[k]!=control[k]:raise ValueError('split/control changes more than spectrum: '+k)
        fields={k:diff(float(split[k]),float(control[k])) for k in
            ('born_com3','survivor_com3','age_sum_com_s','age2_sum_com_s2','source_j','surviving_j','thermal_j','chemical_j','absorbed_j','work_independent_j','work_ledger_j','HI','HeI','HeII','DI')}
        for key,field in fields.items():
            if key.endswith('_j'):field['difference_over_control_source_energy']=field['difference']/float(control['source_j'])
        fields['mean_age_s']=diff(float(split['age_sum_com_s'])/float(split['survivor_com3']),float(control['age_sum_com_s'])/float(control['survivor_com3']))
        fields['energy_weighted_q2']=diff(float(split['q2_numerator_j'])/float(split['surviving_j']),float(control['q2_numerator_j'])/float(control['surviving_j']))
        template_rows=rows(data/'TEMPLATES_RESULT.csv')
        if len(template_rows)!=int(split['templates']):raise ValueError('split template accounting count')
        sums={}
        for key in ('born_com3','survivor_com3','thermal_j','chemical_j','source_j','surviving_j','absorbed_j','HI','HeI','HeII','DI'):
            summed=math.fsum(float(r[key]) for r in template_rows);target=float(split[key]);rel=abs(summed-target)/max(abs(target),1e-300)
            sums[key]=rel
            if rel>3e-12:raise ValueError('split summary/template mismatch')
        split_results.append({'label':name,'status':'MEASURED_SPECTRAL_REPRESENTATION_SHIFT_NOT_ABSOLUTE_ERROR',
            'control':control_name,'templates':int(split['templates']),'cohorts':int(split['cohorts']),
            'fields':fields,'template_accounting_relative':sums,'execution_binding':binding,
            'data_identity':[{'path':str(data/k),'sha256':sha(data/k)} for k in ('SUMMARY.csv','TEMPLATES_RESULT.csv','BIRTHS.csv')],
            'scope':'Both cases use the unchanged source owner. Finer spectral representation changes quadrature; no independent split-spectrum continuum error or spectral convergence is claimed.'})
    ref_changes={}
    for case,d in reference_docs.items():
        low=d['executions'][0]['result'];high=d['executions'][-1]['result']
        ref_changes[case]={k:diff(low[k],high[k]) for k in ('survival','age','age2','energy','work','mean_age_s','mean_age2_s2','energy_weighted_q2')}
        for key in ('heat','binding'):
            ref_changes[case][key]=diff(math.fsum(low[key].values()),math.fsum(high[key].values()))
    receipt={'schema_version':2,'revision':'BR06_THEORY_RECOVERY_R1','historical_pass_inherited':False,
        'status':'COMPLETED_ALL_DECLARED_FRESH_CASE_COMPARISONS' if not pending and not failed else 'PARTIAL_FRESH_CASE_COMPARISONS',
        'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runs':runs,'split_representation_comparisons':split_results,
        'completed_cases':completed,'completed_case_count':len(completed),'total_cohort_evaluations':sum(r['cohorts'] for r in completed),
        'pending_cases':pending,'failed_or_refused_cases':failed,'targets':TARGETS,
        'reference':{'path':str(args.reference),'sha256':sha(args.reference)},
        'reference_plus':{'path':str(args.reference_plus),'sha256':sha(args.reference_plus)},
        'empirical_reference_order_changes':ref_changes,
        'source_identity':{'path':str(args.source_identity),'sha256':identity_sha},
        'matrix_intent':{'path':str(intent_path),'sha256':sha(intent_path)},
        'script_sha256':sha(__file__),'comparison_module_sha256':sha(Path(__file__).with_name('compare_rust_matrix.py')),
        'scope':'One actual recorded frozen-comoving gas operator. Original384-label cases are compared to continuous independent birth reference. Matched cases hold individual birth times, weights and Killing constants fixed. Split-spectrum shift is reported separately. Tiny ledgers do not admit age moments, own-W precision, or nonlinear histories.'}
    out=args.output/'RUST_INDEPENDENT_COMPARISONS.json';out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'output':str(out),'sha256':sha(out),'status':receipt['status'],'completed':len(completed),
       'cohorts':receipt['total_cohort_evaluations'],'pending':pending,'failed':failed,
       'quantities':[{'label':r['label'],'N_relative':r['continuous_comparison']['survivor_com3']['relative'],
            'raw_age1_relative':r['continuous_comparison']['age_sum_com_s']['relative'],
            'heat_relative':r['continuous_comparison']['thermal_j']['relative']} for r in runs]}))


if __name__=='__main__':main()
