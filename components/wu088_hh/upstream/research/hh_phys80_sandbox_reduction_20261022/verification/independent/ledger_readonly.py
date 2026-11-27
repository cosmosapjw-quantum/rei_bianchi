#!/usr/bin/env python3
"""Read-only typed ledger reconciliation; never executes tests or kernels."""
import ast
import hashlib
import json
from pathlib import Path
import platform
from datetime import datetime, timezone
ROOT=Path('/tmp/hh_phys79_work/WU088_HH/research/hh_phys80_sandbox_reduction_20261022')
OUT=Path('/tmp/phys80_review/ledger_audit_001.json')
if OUT.exists():raise SystemExit('CREATE_ONLY_LEDGER_AUDIT_ALREADY_EXISTS')
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ledger_path=ROOT/'EXECUTION_LEDGER.json';ledger=read(ledger_path);unit=ledger['this_unit']
science=read(ROOT/'verification/SCIENCE_STDOUT.json');resume=read(ROOT/'verification/RESUME_STDOUT.json')
finite=read(ROOT/'verification/independent/check_result_001.json')
supplement=read(ROOT/'verification/independent/jacobian_supplement_001.json')
mathpath=ROOT/'source/maxwellian/BELL_KERNEL_VERIFY_RECEIPT.json';mathreceipt=read(mathpath)
postpath=Path('/tmp/phys80_review/postflight_audit_001.json');postflight=read(postpath)
checks=[]
def check(label,condition,observed):
    checks.append({'label':label,'status':'PASS' if condition else 'FAIL','observed':observed})
new=unit['new_isolated_ODE'];independent=unit['independent_review'];generic=unit['generic_maxwellian']
check('three new scientific calls, three complete, zero failed',new['calls']==3 and new['completed']==3 and new['failed']==0 and postflight['new_scientific_ODE_calls_observed']==3 and postflight['scientific_failures_observed']==0,{'calls':new['calls'],'completed':new['completed'],'failed':new['failed']})
check('two controls and one distinct refinement',new['controls']==2 and new['distinct_refinements']==1,{'controls':new['controls'],'refinements':new['distinct_refinements']})
expected=[{k:e[k] for k in ('task_id','science_id','status','new_ODE_calls','solver')} for e in science['entries']]
check('ledger identity and solver detail equal execution stdout',new['identities']==expected,{'identities':len(new['identities'])})
check('verified skips are not new ODE calls',unit['resume']=={'completed_verified_skips':3,'new_ODE':0} and resume['new_ODE_calls']==0 and all(e['status']=='SKIP_COMPLETE_VERIFIED' for e in resume['entries']),unit['resume'])
mapped={'logical_groups':finite['unique_check_groups'],'initial_passed':finite['passed'],'initial_failed':finite['failed'],
        'supplement_new_Jacobian_points':supplement['new_Jacobian_points'],
        'completed_points_replayed':supplement['completed_Jacobian_points_replayed'],
        'full_operator_points':finite['internal_counts']['full_operator_points'],
        'Jacobian_completed_points':finite['internal_counts']['jacobian_points']+supplement['new_Jacobian_points'],
        'Jacobian_completed_columns':finite['internal_counts']['jacobian_columns']+supplement['new_Jacobian_columns'],
        'rate_derivative_points':finite['internal_counts']['rate_derivative_points'],
        'expected_guard_rejections':finite['internal_counts']['expected_guard_rejections'],
        'identity_fixtures':finite['internal_counts']['runner_identity_fixtures'],
        'old_suite_executions':finite['old_suite_executions']+supplement['old_suite_executions'],
        'ODE':finite['actual_ODE_calls']+supplement['actual_ODE_calls']}
check('16 logical groups and subordinate point counts remain typed',all(independent[k]==v for k,v in mapped.items()),mapped)
check('first fixture failure is retained',independent['initial_failed']==1 and independent['failure_class']=='TEST_FIXTURE_OUTSIDE_STRICT_PHYSICAL_DOMAIN' and independent['failed_receipt_preserved'] is True and supplement['original_failure_preserved'] is True and supplement['passed'] is True,{'first_failed':1,'supplement_passed':supplement['passed'],'completed_points_replayed':supplement['completed_Jacobian_points_replayed']})
tree=ast.parse((ROOT/'source/maxwellian/verify_bell_kernel.py').read_text())
method_names=sorted(node.name for node in ast.walk(tree) if isinstance(node,ast.FunctionDef) and node.name.startswith('test_'))
recorded_names=sorted(name.split('.')[-1] for name in mathreceipt['unique_test_names'])
check('six distinct Maxwellian unittest methods, not sixteen groups',len(method_names)==6 and method_names==recorded_names and generic['unique_unittest_methods']==mathreceipt['unique_test_count']==6 and generic['tests_run']==mathreceipt['tests_run']==6 and generic['failures']==mathreceipt['failures']==mathreceipt['errors']==0,{'method_names':method_names,'tests_run':mathreceipt['tests_run']})
math_counts={'pure_A_witnesses':len(mathreceipt['grid']),
             'order_profiles':mathreceipt['operation_counts']['completed_order_profiles'],
             'scalar_quadrature_sums':mathreceipt['operation_counts']['scalar_quadrature_sums'],
             'E1_oracles':mathreceipt['operation_counts']['E1_oracle_evaluations'],'ODE':mathreceipt['operation_counts']['new_ODE']}
check('Maxwellian internal witnesses/profiles/sums are not independent tests',all(generic[k]==v for k,v in math_counts.items()) and generic['physical_admission']==mathreceipt['physical_admission']=='NOT_ISSUED',math_counts)
check('one Maxwellian attempt and two byte-identical receipt names',mathreceipt['attempt']==1 and sha(mathpath)==sha(ROOT/'source/maxwellian/BELL_KERNEL_VERIFY_ATTEMPT_001.json'),{'attempt':mathreceipt['attempt'],'receipt_sha256':sha(mathpath)})
mathpins={name:sha(ROOT/'source/maxwellian'/name) for name in mathreceipt['source_hashes']}
check('Maxwellian source pins preserved',mathpins==mathreceipt['source_hashes'],mathpins)
wolfram=[read(p) for p in (ROOT/'theory').glob('WOLFRAM*json')]
contexts=[d for d in wolfram if d['tool'].endswith('wolframcontext')]
evaluators=[d for d in wolfram if d['tool'].endswith('wolframlanguageevaluator')]
failures=[d for d in evaluators if '$Failed' in json.dumps(d['result'])]
wc={'context_calls':len(contexts),'evaluator_calls':len(evaluators),'successful_algebra_calls':len(evaluators)-len(failures),'preserved_syntax_failures':len(failures),'local_ODE':sum(d.get('ODE_calls',0) for d in evaluators)}
check('Wolfram evaluator failure not hidden by transport isError false',all(unit['Wolfram'][k]==v for k,v in wc.items()),wc)
check('local source result audit passes',postflight['status']=='PASS_SCOPED' and postflight['actual_new_ODE_calls_by_auditor']==0,{'accepted_points':postflight['accepted_mesh_points'],'dense_samples':postflight['dense_samples'],'ODE':0})
report={'schema':'PHYS80_TYPED_LEDGER_READONLY_AUDIT_V1','utc':datetime.now(timezone.utc).isoformat(),
        'command':'python -B /tmp/phys80_review/ledger_readonly.py','Python':platform.python_version(),
        'ledger_sha256':sha(ledger_path),'postflight_receipt_sha256':sha(postpath),'audit_script_sha256':sha(__file__),
        'status':'PASS_SCOPED' if all(c['status']=='PASS' for c in checks) else 'FAIL','checks':checks,
        'new_ODE':0,'old_test_suite_runs':0,'new_kernel_evaluations':0,
        'scope':'current unit execution/review/Maxwellian/Wolfram typed counts against saved receipts; inherited historical totals, figure visual QA, publication and backup delivery are not re-audited',
        'suggested_additive_ledger_entry':{'kind':'independent saved-result postprocessing audit','batches':1,'accepted_mesh_points':403,'dense_samples':483,'new_ODE':0,'RHS':0,'Jacobian':0,'rate_evaluations':0},
        'HH_R10':'OFF','production_admission':'NOT_ISSUED'}
with OUT.open('x') as stream:json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps({'status':report['status'],'checks':len(checks),'failed':[c for c in checks if c['status']!='PASS'],'ledger_sha256':report['ledger_sha256'],'new_ODE':0},indent=2))
raise SystemExit(0 if report['status']=='PASS_SCOPED' else 1)
