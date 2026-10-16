#!/usr/bin/env python3
"""Inspect preserved native physical outputs, source ages, and serial equality."""
from pathlib import Path
import hashlib,json,math,re,sys
HERE=Path(__file__).resolve().parent; ROOT=HERE/'evidence/native'
checks=[]
def check(name,passed,**evidence):checks.append(dict(check=name,passed=bool(passed),**evidence))
def rows(path):return [json.loads(v) for v in path.read_text().splitlines() if v]
def relative(a,b,tol=1e-12):return abs(a-b)<=tol*max(abs(a),abs(b)) if a or b else a==b
for summary in sorted(ROOT.rglob('*.summary.json')):
    obj=json.loads(summary.read_text());path=summary.with_suffix('').with_suffix('.jsonl');history=rows(path)
    check(str(path.relative_to(ROOT))+':ledger',obj['max_invariant_normalized']<=1,maximum_normalized=obj['max_invariant_normalized'])
    check(str(path.relative_to(ROOT))+':admissible',all(1<=r['temperature']<=1e6 and r['w']>0 and 0<=r['fractions'][0]<=1 and min(r['fractions'][1:])>=0 and sum(r['fractions'][1:])<=1 and all(v>=0 and math.isfinite(v) for v in r['photons']) for r in history))
    check(str(path.relative_to(ROOT))+':transaction_ledgers',all(all(v[2]<=1 for v in r['transaction_checks']) for r in history))
    check(str(path.relative_to(ROOT))+':positive_time_progress',all(b['time_s']>a['time_s'] for a,b in zip(history,history[1:])))
for name,mean_age in [('pulse_early',2.25e12),('pulse_delayed',.75e12)]:
    stem=ROOT/'pulse_repair'/f'{name}_n32';cohorts=rows(stem.with_suffix('.cohorts.jsonl'));end=rows(stem.with_suffix('.jsonl'))[-1]
    number=math.fsum(c['number'] for c in cohorts);energy=math.fsum(c['energy_ev'] for c in cohorts)
    age=math.fsum(c['emission_age_at_observation']*c['number'] for c in cohorts)/number
    check(name+':source_count',relative(number,.02) and relative(number,end['source_n']),sum_cohort_number=number,native_source_number=end['source_n'])
    check(name+':source_energy',relative(energy,end['source_u']),sum_cohort_energy=energy,native_source_energy=end['source_u'])
    check(name+':emission_age',relative(age,mean_age),weighted_mean_age=age,expected_age=mean_age,limit='emission ages; surviving-cohort distribution not tracked')
    check(name+':cursor',len(cohorts)==end['source_cursor'])
serial=rows(ROOT/'campaign/mixed1e4_n32.jsonl');parallel=rows(ROOT/'campaign/mixed1e4_n32_threads8.jsonl')
left=[{k:v for k,v in r.items() if k!='transport_workers'} for r in serial];right=[{k:v for k,v in r.items() if k!='transport_workers'} for r in parallel]
check('serial1_threads8_same_physics',left==right,compared_rows=len(left),ignored_field='transport_workers only')
rollback=json.loads((ROOT/'tests/rollback.json').read_text());check('rollback',all(rollback[k] for k in ['invalid_dt_rejected','invalid_no_rhs','native_failure_after_source','accepted_state_bitwise_unchanged']),evidence=rollback)
controls=rows(ROOT/'tests/isolated_event_controls.jsonl');check('isolated_native_event_controls',len(controls)==12 and all(r['energy_normalized']<=1 for r in controls),count=len(controls),limit='test-only native event decomposition; integrated trajectories use full physics')
for name,positive in [('cmb_heating10',True),('cold100',False)]:
    end=rows(ROOT/'campaign'/f'{name}_n32.jsonl')[-1];check(name+':CMB_sign',(end['cmb_ev_per_h']>0)==positive and end['cmb_ev_per_h']!=0,signed_into_gas_ev_per_h=end['cmb_ev_per_h'])
nohe=rows(ROOT/'campaign/no_helium_n32.jsonl');check('absent_helium_fractions_constant',all(r['fractions'][1:]==nohe[0]['fractions'][1:] for r in nohe))
dynamic=rows(ROOT/'dynamic/dynamic_smoke.jsonl');check('original_driver_dynamic_three_signed_cases',len(dynamic)==3 and all(r['accepted']==3 and r['a']>r['initial_a'] and r['elapsed_proper_s']>0 and r['source_n']>0 and r['thermal_work_ev_per_h']>0 and r['photon_work_ev_per_h']>0 for r in dynamic),scope='three accepted original native steps only')
recovery=json.loads((ROOT/'pulse_repair/retry_recovery.json').read_text());check('reject_once_then_successful_half_retry',all(recovery[k] for k in ['test_only_reject_after_native_success','old_state_bitwise_unchanged','recovered_equal_clean_half_steps','no_duplicate_source']),evidence=recovery)
for mode,filename,process in [('stiff_rr','stiff_recomb8000_n1','RR'),('stiff_ci','stiff_collision1e5_n1','CI')]:
    data=rows(ROOT/mode/(filename+'.jsonl'));check(mode+':full_native_accepted',len(data)==2 and data[-1]['time_s']>data[0]['time_s'],process=process,scope='full native physics; stiff admissibility only, no accuracy claim')
# Report actual resources and existing original-test exits; no extra campaign.
resources={}
for p in ROOT.rglob('*.time'):
    content=p.read_text();entry={}
    for label,key in [('Elapsed (wall clock) time (h:mm:ss or m:ss)','wall'),('Maximum resident set size (kbytes)','rss_kib'),('Exit status','exit')]:
        match=next((line.strip() for line in content.splitlines() if line.strip().startswith(label+':')),None)
        if match:entry[key]=match[len(label)+1:].strip()
    resources[str(p.relative_to(ROOT))]=entry
log=(ROOT/'focused_tests.log').read_text();testcounts=[tuple(map(int,m)) for m in re.findall(r'test result: ok\. (\d+) passed; (\d+) failed',log)]
check('original_focused_tests',bool(testcounts) and sum(v[1] for v in testcounts)==0,native_test_count=sum(v[0] for v in testcounts),targets=len(testcounts))
result=dict(status='PASS' if all(v['passed'] for v in checks) else 'HOLD',checks=checks,resources=resources,scope='native physical postconditions, conservation, source ages, transaction rollback, serial comparison; independent accuracy and coefficient review separate')
(ROOT/'mechanical_summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],checks=len(checks),failures=sum(not v['passed'] for v in checks),focused_native_tests=sum(v[0] for v in testcounts)),indent=2))
sys.exit(0 if result['status']=='PASS' else 1)
