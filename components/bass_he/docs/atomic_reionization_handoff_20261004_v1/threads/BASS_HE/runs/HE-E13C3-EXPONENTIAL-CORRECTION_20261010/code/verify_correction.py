"""Saved-evidence acceptance, without recomputing any E13C2 reference."""
from decimal import Decimal, localcontext
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    with tempfile.NamedTemporaryFile('w',dir=path.parent,delete=False) as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
        f.flush();os.fsync(f.fileno());temp=f.name
    os.replace(temp,path)


def metric(candidate, reference, floor):
    x,y=float(candidate),float(reference)
    error=x-y
    above=abs(y)>=floor
    return {'candidate':x,'reference':y,'signed_error':error,'absolute_error':abs(error),
            'relative_absolute_error':abs(error/y) if above else None,
            'relative_status':'EVALUATED' if above else 'UNRESOLVED_BELOW_ABSOLUTE_FLOOR',
            'absolute_floor':floor}


def main(root, stage, output):
    identities={}
    def read(name):
        path=root/name
        identities[name]=sha(path)
        return json.loads(path.read_text())
    def file_hash(name):
        value=sha(root/name);identities[name]=value
        return value
    checks=[]
    def check(name,condition,value=None):
        checks.append({'name':name,'pass':bool(condition),'observed':value})
    plan=read('PLAN.json'); a=plan['acceptance']
    manifest=read('inputs/INPUT_MANIFEST.json')
    check('34_sealed_inputs',len(manifest)==34,len(manifest))
    for item in manifest:
        check('sealed:'+item['path'],(root/item['path']).stat().st_size==item['bytes'] and
              file_hash(item['path'])==item['sha256'])
    producer=file_hash('code/exponential_correction.py')
    helper=file_hash('inputs/e13c2/code/continuous_defect.py')
    theory=read('evidence/theory/THEORY_CHECKS.json')
    check('new_exact_theory_checks',theory['status']=='PASS' and theory['failed']==0 and
          theory['passed']==len(theory['checks']) and all(x['status']=='PASS' for x in theory['checks']),
          {'total':theory['total_checks'],'passed':theory['passed']})
    check('new_theory_code_as_run',theory['script_sha256']==file_hash('evidence/theory/check_theory_e13c3.py'))
    kernels=read('evidence/KERNEL_CHECKS.json')
    check('actual_primary_kernel_checks',kernels['status']=='PASS' and all(x['pass'] for x in kernels['checks'])
          and kernels['passed']==kernels['total']==len(kernels['checks']),kernels['total'])
    check('tested_primary_kernel_code',kernels['tested_code_sha256']==producer)
    check('kernel_checker_as_run',kernels['producer_sha256']==file_hash('code/kernel_checks.py'))
    decimal=read('evidence/decimal/DECIMAL_RESULTS.json')
    check('decimal_code_as_run',decimal['new_code_sha256_as_run']==file_hash('evidence/decimal/decimal_first_variation.py'))
    check('decimal_contract_as_run',decimal['contract_sha256_as_run']==file_hash('evidence/decimal/TASK_CONTRACT.json'))
    check('decimal_numerical_gates',not decimal['numerical_failures'] and
          decimal['summary']['numerical_pass_count']==6 and all(decimal['input_checks'].values()))
    check('decimal_research_heat_gate',not decimal['research_diagnostic_failures'] and
          decimal['summary']['research_heat_diagnostic_pass_count']==6)
    fine=read('evidence/local_gl12/RESULTS.json')
    coarse=read('evidence/local_gl8/RESULTS.json')
    def run_checks(label,data):
        check(label+':producer_as_run',data['producer_sha256']==producer)
        check(label+':input_manifest_as_run',data['input_manifest_sha256']==identities['inputs/INPUT_MANIFEST.json'])
        check(label+':helper_as_run',data['coefficient_helper_sha256']==helper)
        check(label+':no_out_of_scope_runs',all(data[k]==0 for k in
              ('native_runs','gas_advances','original_continuous_recomputations','old_campaign_replays')))
        groups=data.get('segment_groups',[r['meta'] for r in data.get('local_controls',[])])
        check(label+':number_ledger',max(g['max_number_first_variation_ledger'] for g in groups)<=a['first_variation_number_ledger_absolute'])
        check(label+':energy_ledger',max(g['max_energy_first_variation_ledger_eV'] for g in groups)<=a['first_variation_energy_ledger_eV_absolute'])
        check(label+':nonnegative_endpoints',min(g['min_corrected_photon_endpoint'] for g in groups)>=0)
    run_checks('local_GL8',coarse);run_checks('local_GL12',fine)
    expected={tuple(x) for x in plan['scope']['local_ids']}
    controls=[fine['local_controls'],coarse['local_controls'],decimal['results']]
    keys=['id','id','key']
    for label,rows,key in zip(['primary12','primary8','decimal'],controls,keys):
        check(label+':six_unique_ids',len(rows)==6 and {tuple(x[key]) for x in rows}==expected)
    c8={tuple(x['id']):x for x in coarse['local_controls']}
    dec={tuple(x['key']):x for x in decimal['results']}
    saved_oracle=read('inputs/e13c2/evidence/ORACLE_RESULTS.json')
    saved={tuple(x['key']):x['signed_continuous_minus_frozen'] for x in saved_oracle['results']}
    check('saved_oracle_six_keys',len(saved_oracle['results'])==6 and set(saved)==expected)
    chi=[Decimal.from_float(x) for x in (13.598434599702,24.587389011,54.41776)]
    local=[]
    for row in fine['local_controls']:
        key=tuple(row['id']); old=c8[key]; d=dec[key]; high=d['calculated_by_degree']['20']
        stored=saved[key]
        check(str(key)+':saved_reference_P',Decimal(d['saved_signed_reference']['P1'])==Decimal(stored['P1']))
        check(str(key)+':saved_reference_AB',all(Decimal(x)==Decimal(y) for field in ('A','B_eV')
              for x,y in zip(d['saved_signed_reference'][field],stored[field])))
        with localcontext() as context:
            context.prec=90
            saved_heat=sum(Decimal(b)-c*Decimal(n) for b,n,c in zip(stored['B_eV'],stored['A'],chi))
            check(str(key)+':saved_reference_heat_derived',abs(saved_heat-Decimal(d['saved_signed_reference']['H_total_eV']))<Decimal('1e-60'))
        number_errors=[abs(row['delta_P']-float(high['P1']))]+[
            abs(x-float(y)) for x,y in zip(row['delta_A'],high['A'])]
        energy_errors=[abs(x-float(y)) for x,y in zip(row['delta_B_eV'],high['B_eV'])]
        agreement_number=max(number_errors);agreement_energy=max(energy_errors)
        heat=metric(row['delta_total_heat_eV'],saved_heat,a['heat_near_zero_floor_eV'])
        gap=metric(old['delta_total_heat_eV'],row['delta_total_heat_eV'],a['heat_near_zero_floor_eV'])
        check(str(key)+':independent_number',agreement_number<=a['primary_new_Decimal_agreement_P_A_absolute'],agreement_number)
        check(str(key)+':independent_energy',agreement_energy<=a['primary_new_Decimal_agreement_B_eV_absolute'],agreement_energy)
        check(str(key)+':saved_continuous_heat_defect',heat['relative_absolute_error'] is not None and
              heat['relative_absolute_error']<=a['local_total_heat_defect_relative_error_max'],heat)
        check(str(key)+':GL8_12_heat_defect',gap['relative_absolute_error'] is not None and
              gap['relative_absolute_error']<=a['primary_GL8_12_heat_defect_relative_gap_max'],gap)
        local.append({'id':list(key),'heat_defect_error':heat,'GL8_12_heat_gap':gap,
                      'max_independent_number_absolute_error':agreement_number,
                      'max_independent_B_eV_absolute_error':agreement_energy,
                      'count_errors':[metric(x,y,a['count_near_zero_floor']) for x,y in zip(row['delta_A'],d['saved_signed_reference']['A'])]})
    summary={'local_controls':local,
             'max_local_heat_defect_relative_error':max(x['heat_defect_error']['relative_absolute_error'] for x in local),
             'max_local_GL8_12_heat_relative_gap':max(x['GL8_12_heat_gap']['relative_absolute_error'] for x in local),
             'max_local_independent_number_absolute_error':max(x['max_independent_number_absolute_error'] for x in local),
             'max_local_independent_B_eV_absolute_error':max(x['max_independent_B_eV_absolute_error'] for x in local)}
    if stage=='final':
        prior=read('evidence/LOCAL_ACCEPTANCE.json')
        check('local_gate_preceded_full_expansion',prior['verdict']=='PASS_SCOPED')
        path12=read('evidence/paths_gl12/RESULTS.json');path8=read('evidence/paths_gl8/RESULTS.json')
        run_checks('paths_GL8',path8);run_checks('paths_GL12',path12)
        ref=read('inputs/e13c2/evidence/defect_rtol_2e11/RESULTS.json')
        refs={(r['mode'],r['step']):r for r in ref['records']}
        p8={(r['mode'],r['step']):r for r in path8['records']}
        expected_path={(mode,step) for mode in ('OFF','KF','GM') for step in (1,2)}
        for name,records in [('path12',path12['records']),('path8',path8['records']),('saved',ref['records'])]:
            check(name+':six_macro_keys',len(records)==6 and {(r['mode'],r['step']) for r in records}==expected_path)
        macros=[]
        for row in path12['records']:
            key=(row['mode'],row['step']);r=refs[key]
            heat=metric(row['delta_total_heat_eV'],sum(r['delta_heat_eV_per_H']),a['heat_near_zero_floor_eV'])
            gap=metric(p8[key]['delta_total_heat_eV'],row['delta_total_heat_eV'],a['heat_near_zero_floor_eV'])
            check(str(key)+':path_heat_defect',heat['relative_absolute_error'] is not None and heat['relative_absolute_error']<=a['expanded_macro_total_heat_defect_relative_error_max'],heat)
            check(str(key)+':path_GL8_12_heat',gap['relative_absolute_error'] is not None and gap['relative_absolute_error']<=a['primary_GL8_12_heat_defect_relative_gap_max'],gap)
            macros.append({'mode':key[0],'step':key[1], 'heat_defect_error':heat,'GL8_12_heat_gap':gap,
                'count_errors':[metric(x,y,a['count_near_zero_floor']) for x,y in zip(row['delta_A'],r['delta_A_per_H'])],
                'energy_errors_eV':[metric(x,y,a['heat_near_zero_floor_eV']) for x,y in zip(row['delta_B_eV'],r['delta_B_eV_per_H'])],
                'remaining_photo_reference_minus_corrected_over_old_TOL':[
                    x-y for x,y in zip(r['projected_over_algebraic_TOL'],row['projected_over_old_algebraic_TOL'])],
                'heat_error_fraction_of_frozen_total':heat['relative_absolute_error']*abs(r['delta_heat_fraction_of_frozen_total']),
                'old_TOL_is_not_continuum_accuracy_budget':True})
        old_samples=sum(g['nfev']*g['segment_count'] for g in ref['segment_groups'])
        segments=sum(g['segments'] for g in path12['segment_groups'])
        check('14652_new_path_segments',segments==14652,segments)
        check('physical_sample_count_GL12',path12['physical_coefficient_samples']==12*segments)
        summary.update(macro_comparisons=macros,
             max_macro_heat_defect_relative_error=max(x['heat_defect_error']['relative_absolute_error'] for x in macros),
             max_macro_GL8_12_heat_relative_gap=max(x['GL8_12_heat_gap']['relative_absolute_error'] for x in macros),
             max_remaining_heat_reference_over_old_TOL=max(abs(x['remaining_photo_reference_minus_corrected_over_old_TOL'][3]) for x in macros),
             coefficient_cost={'saved_continuous_path_RHS_segment_evaluations':old_samples,
                               'new_GL8_path_coefficient_samples':path8['physical_coefficient_samples'],
                               'new_GL12_path_coefficient_samples':path12['physical_coefficient_samples'],
                               'saved_RHS_to_new_GL12_samples_ratio':old_samples/path12['physical_coefficient_samples'],
                               'interpretation':'scientific coefficient samples; excludes parse, frozen stock, projections, and validation; not an elapsed-time speedup'},
             times_seconds={'new_paths_GL8':path8['elapsed_seconds'],'new_paths_GL12':path12['elapsed_seconds'],
                            'saved_E13C2_full_run_context':ref['elapsed_seconds'],
                            'controlled_speedup_claimed':False},
             min_corrected_photon_endpoint=min(g['min_corrected_photon_endpoint'] for g in path12['segment_groups']),
             max_number_first_variation_ledger=max(g['max_number_first_variation_ledger'] for g in path12['segment_groups']),
             max_energy_first_variation_ledger_eV=max(g['max_energy_first_variation_ledger_eV'] for g in path12['segment_groups']),
             max_optical_depth=max(g['max_optical_depth'] for g in path12['segment_groups']))
    passed=all(x['pass'] for x in checks)
    result={'verdict':'PASS_SCOPED' if passed else 'FAIL', 'stage':stage,
            'producer_sha256':sha(Path(__file__)), 'checks':checks,
            'check_count':len(checks),'failed':[x for x in checks if not x['pass']],
            'summary':summary,'read_file_sha256':identities,
            'protected':plan['protected'],'original_continuous_recomputations':0,
            'not_claimed':['uniform interval certificate','production admission','independent decision review',
                           'old algebraic TOL as continuum tolerance','controlled runtime speedup']}
    write_json(output,result)
    print(json.dumps({'verdict':result['verdict'],'checks':len(checks),'failed':result['failed'],
                      'max_local_heat_error':summary['max_local_heat_defect_relative_error'],
                      'max_macro_heat_error':summary.get('max_macro_heat_defect_relative_error')}))
    if not passed:
        raise SystemExit(1)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--stage',choices=['local','final'],required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    main(args.root.resolve(),args.stage,args.output.resolve())
