#!/usr/bin/env python3
"""Bind independently reviewed E13C9 source, raw numerics and controls."""
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).parent

def read(p): return json.loads(Path(p).read_bytes())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):
    p=Path(p)
    return {'relative_path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}
def b(x): return F(x['lo']),F(x['hi'])
def contains(x,y): return x[0]<=y[0]<=y[1]<=x[1]
def save(name,x):
    with (HERE/name).open('x') as f:
        json.dump(x,f,indent=2,ensure_ascii=False,sort_keys=True,allow_nan=False);f.write('\n')

def main():
    start=time.perf_counter(); checks=[]
    def check(name,ok):
        checks.append({'check':name,'pass':bool(ok)})
        if not ok: raise AssertionError(name)
    arithmetic=read(HERE/'SAVED_ARITHMETIC_REVIEW.json')
    analysis=read(ROOT/'analysis/ACTUAL_PORTABLE/LOCAL_ANALYSIS.json')
    selected=read(ROOT/'analysis/ACTUAL_PORTABLE/SELECTED_CANDIDATE.json')
    alloc=read(ROOT/'analysis/ACTUAL_PORTABLE/BOUND_ALLOCATION.json')
    manufacture=ROOT/'tests/MANUFACTURED'
    receipt=read(manufacture/'EXEC01/RECEIPT.json'); controls=read(manufacture/'EXEC01/CONTROL_RESULTS.json')
    check('independent_saved_arithmetic_complete',arithmetic['status']=='PASS_SAVED_ARITHMETIC' and arithmetic['failures']==[] and len(arithmetic['selected_comparisons'])==170)
    check('candidate_unchanged_since_independent_review',sha(ROOT/'SOURCE_LOCK.json')==arithmetic['candidate_source_lock']['sha256'])
    check('manufactured_candidate_identity',sha(ROOT/'code/signed_volterra.py')==receipt['candidate_sha256'])
    check('manufactured_control_code_identity',sha(manufacture/'run_manufactured_controls.py')==receipt['oracle_code_sha256'])
    check('manufactured_result_identity',sha(manufacture/'EXEC01/CONTROL_RESULTS.json')==receipt['results_sha256'])
    check('manufactured_contract_identity',sha(ROOT/'SCIENTIFIC_CONTRACT.md')==receipt['contract_sha256'])
    check('manufactured_checks_complete',receipt['status']=='PASS_MANUFACTURED_CLOSED_FORM_CONTROLS' and len(controls['checks'])==receipt['checks_passed']==3686 and receipt['checks_failed']==0 and all(c['pass'] for c in controls['checks']))
    check('manufactured_nine_cases_two_resolutions',len(controls['rows'])==18 and {(x['case']['name'],x['M_second']) for x in controls['rows']}=={(name,m) for name in receipt['cases'] for m in (8,32)})
    for row in controls['rows']:
        label=row['case']['name']+'/M'+str(row['M_second'])
        for k,oracle in row['signed_oracle'].items():
            check('manufactured_saved_signed_contains_oracle/'+label+'/'+k,contains(b(row['signed_candidate'][k]),b(oracle)))
        for cell in row['cells']:
            for part in ('left','right','whole'):
                check('manufactured_saved_prefix_contains_oracle/'+label+'/'+str(cell['cell'])+'/'+part,contains(b(cell['candidate_'+part]),b(cell['prefix_oracle_'+part])))
        for error in row['actual_residuals']:
            for k,oracle in error['true_remainder_oracle'].items():
                bound=F(row['remainder_candidate']['total_before_numerical_upper'][k])
                check('manufactured_saved_remainder_contains_oracle/'+label+'/'+error['incoming_error_exact']+'/'+k,contains((-bound,bound),b(oracle)))
    check('selected_analysis_byte_identity',sha(ROOT/'analysis/ACTUAL_PORTABLE/LOCAL_ANALYSIS.json')==selected['analysis_sha256'])
    finalized=[r for r in arithmetic['reviewed_saved_runs'] if r['selected_final']]
    for sp in selected['paths']:
        rr=next(x for x in finalized if x['node']==sp['node'])
        check('selected_result_pin/'+str(sp['node']),sp['result']['sha256']==rr['result']['sha256'] and sp['result']['bytes']==rr['result']['bytes'] and sp['result']['relative_path']==rr['result']['path'])
        check('selected_comparison_pin/'+str(sp['node']),sp['comparison']['sha256']==rr['comparison']['sha256'])
    for level in ('M32','M128','SELECTED'):
        records=[r for r in arithmetic['reviewed_saved_runs'] if (r['selected_final'] if level=='SELECTED' else r['phase']==('M32_REPAIRED' if level=='M32' else 'M128'))]
        pairs=[read(ROOT/r['comparison']['path']) for r in records]
        for row in analysis['aggregate_comparisons'][level]:
            kind,q=row['kind'],row['quantity']
            old=tuple(sum(b(x['baseline_raw_weighted'][kind][q])[i] for x in pairs) for i in (0,1))
            new=tuple(sum(b(x['candidate_raw_weighted'][kind][q])[i] for x in pairs) for i in (0,1))
            check('analysis_exact_aggregate_parity/'+level+'/'+kind+'/'+q,old==b(row['baseline']) and new==b(row['candidate']) and F(row['baseline_width'])==old[1]-old[0] and F(row['candidate_width'])==new[1]-new[0])
    for q,a in arithmetic['selected_aggregate'].items():
        own=analysis['selected_aggregate_summary'][q]
        check('analysis_gain_parity/'+q,F(own['gain_fraction'])==F(a['selected_gain_exact']) and F(own['candidate_width'])==F(a['selected_width_exact']))
        total=alloc['selected_totals'][q]
        check('positive_bound_allocation_reconstructs_halfwidth/'+q,all(F(v)>=0 for v in total['components'].values()) and sum(F(v) for v in total['components'].values())==F(total['halfwidth'])==F(a['selected_width_exact'])/2)
        check('bound_allocation_path_sum/'+q,all(F(total['components'][k])==sum(F(p['quantities'][q]['components'][k]) for p in alloc['paths']) for k in total['components']))
    finding=read(ROOT/'evidence/FIRST_ASSOCIATION_FINDING/FINDING.json')
    check('first_failure_result_preserved',sha(ROOT/finding['first_result'])==finding['first_full_result_sha256'])
    check('targeted_resolution_math_kernel_unchanged',sha(ROOT/'code/signed_volterra.py')==sha(ROOT/'evidence/SOURCE_REVISIONS/REV02_M32_M128/signed_volterra.py'))
    check('uniform_M128_failure_not_promoted',analysis['uniform_M128_nested_count']==169 and analysis['selected_mixed_resolution_nested_count']==170)
    evidence={
        'scientific_contract':pin(ROOT/'SCIENTIFIC_CONTRACT.md'),
        'current_source_lock':pin(ROOT/'SOURCE_LOCK.json'),
        'current_method':pin(ROOT/'code/signed_volterra.py'),
        'current_runner':pin(ROOT/'code/run_path.py'),
        'prior_M32_M128_source_lock':pin(ROOT/'evidence/SOURCE_REVISIONS/REV02_M32_M128/SOURCE_LOCK.json'),
        'targeted_resolution_amendment':pin(ROOT/'evidence/TARGETED_M256_AMENDMENT.json'),
        'first_association_finding':pin(ROOT/'evidence/FIRST_ASSOCIATION_FINDING/FINDING.json'),
        'theory_design':pin(ROOT/'theory/SIGNED_PREFIX_DESIGN.md'),
        'independent_arithmetic':pin(HERE/'SAVED_ARITHMETIC_REVIEW.json'),
        'independent_arithmetic_source':pin(HERE/'review_saved_arithmetic.py'),
        'manufactured_oracle_source':pin(manufacture/'run_manufactured_controls.py'),
        'manufactured_results':pin(manufacture/'EXEC01/CONTROL_RESULTS.json'),
        'manufactured_receipt':pin(manufacture/'EXEC01/RECEIPT.json'),
        'selected_candidate':pin(ROOT/'analysis/ACTUAL_PORTABLE/SELECTED_CANDIDATE.json'),
        'actual_analysis':pin(ROOT/'analysis/ACTUAL_PORTABLE/LOCAL_ANALYSIS.json'),
        'bound_allocation':pin(ROOT/'analysis/ACTUAL_PORTABLE/BOUND_ALLOCATION.json'),
    }
    judgments=[
        {'id':'FINITE_IDENTITY','status':'DEFENDED','basis':'derived + direct source review','finding':'From delta = delta1 + F e - K delta, subtraction of delta1-Kdelta1 gives (I-K)F e + K^2 delta. Positivity of actual opacity bounds true delta by S=|c|+eta+Br; no contraction assumption D<1 is introduced.'},
        {'id':'NORMALIZED_PREFIX','status':'DEFENDED','basis':'derived + implementation-verified + manufactured controls','finding':'For x=u/h and a=h Lambda_f, the forcing-integral radius is h Delta^3 sup|exp[-a(b-x)](r_xx+2a r_x+a^2 r)|/24. Endpoint induction starts at c and within-cell variation of constants uses the left prefix and a nonnegative kernel. All normalized h factors and causal ordering are present.'},
        {'id':'SIGNED_KERNELS','status':'DEFENDED','basis':'direct derivation + manufactured 17-output closed forms','finding':'Photon uses -W DeltaLambda; redshift -KE DeltaLambda; A, B and H species retain direct DeltaLambda_i minus frozen adjoint terms. Energy uses E(h) for final stock and E(u) inside moments. Zero total defect does not erase nonzero individual species corrections. Source QN/QE second corrections are exactly zero.'},
        {'id':'CACHE_AND_CARRY','status':'DEFENDED','basis':'implementation-verified + exact saved arithmetic','finding':'Only incoming-independent first signed quadrature and coefficient bounds are reused at original N1024/N512, P60. Prefix M controls only the new correction. New S and all eta contributions use the newly propagated photon center/radius. Old outgoing radii are diagnostic only. No old first-variation integration is replayed.'},
        {'id':'TAIL_AND_NUMERICAL_RADIUS','status':'DEFENDED','basis':'derived + exact arithmetic + manufactured true residuals','finding':'Tail is (|G|+T)eta+T D S with D from whole-segment D_L, not terminal H_h. Numerical prefix width remains in signed rectangle intervals. Baseline fine first-variation quadrature remains in final assembly; coarse new terminal prefix is not substituted. Centering and representation widths remain outward.'},
        {'id':'SEAMS_TOTALS_LEDGERS','status':'DEFENDED','basis':'unchanged source + exact saved arithmetic','finding':'The original captured photon stitch and signed DeltaE*P anchor are called without modification. Total comparison intervals use exact species sums and original positive weight once. All selected segment/global number, energy and heat ledger enclosures contain zero. Captured event/mask semantics at nodes 1620/2344 remain fixed.'},
        {'id':'FAILURE_HANDLING','status':'INFORMATIVE_FAILURE_RESOLVED_FOR_SELECTED_OUTPUTS','basis':'preserved raw evidence and source diff','finding':'The original association widened unchanged QN/QE at directed-rounding scale; restoring frozen-minus-captured grouping preserved the numerical meaning. Uniform M128 remains 169/170 because the node1162 anchor was wider. One recorded targeted M256 extension passed; no intersection, fallback, precision relaxation or unrecorded blanket rerun was used.'},
        {'id':'NUMERICAL_ADMISSION','status':'DEFENDED','basis':'independent exact saved arithmetic + manufactured controls','finding':'Admit only nodes1,1976,1620,2344 at M128 and node1162 at M256, twelve serial segments. All170 raw metric intervals are nested/nonincreasing; selected P/H width reductions exceed the predeclared10% local usefulness threshold.'},
        {'id':'RESOURCE_AND_NEXT_QUESTION','status':'TRADEOFF','basis':'actual local timings and positive bound allocation','finding':'All required actual captured-path invocations were short (maximum3.378689538s). Current selected widths allocate about98% to inherited first-variation midpoint bounds. No new full-population accuracy objective is established, so there is no justified new NCP work list. Further second-correction or precision work without a discriminating question is not required.'}
    ]
    decision={
        'schema':'bass-he-e13c9-independent-final-decision-v1',
        'decision':'PROMOTE_SCOPED_LOCAL_SIGNED_VOLTERRA',
        'created_utc':datetime.now(timezone.utc).isoformat(),
        'reviewer':{'agent':'/root/e13c9_independent_decision','role':'INDEPENDENT_FINAL_NUMERICAL_SCIENTIFIC_DECISION_REVIEWER','candidate_author':False,'theory_design_contributor':False,'manufactured_validation_contributor':False,'candidate_edits':0,'recursive_reviews':0,'independence_scope':'Separate reviewer context and separately authored Fraction saved-evidence reconstruction; direct critical source proof. Candidate and oracle were authored by other agents. Model-level diversity or independent physical coefficient model is not claimed.'},
        'scope':{'mode':'OFF','nodes':[1,1162,1976,1620,2344],'segments':12,'selected_M_second':{'1':128,'1162':256,'1976':128,'1620':128,'2344':128},'N_base':{'1':1024,'1162':1024,'1976':1024,'1620':512,'2344':512},'precision':60,'captured_problem_unchanged':True},
        'selected_paths':selected['paths'],
        'acceptance':{'raw_metric_checks':170,'raw_nested':170,'raw_nonincreasing':170,'local_P_H_gain_threshold':'1/10','selected_aggregate':arithmetic['selected_aggregate'],'uniform_M32_nested':145,'uniform_M128_nested':169,'uniform_M128_decision':'HOLD_AS_A_COMPLETE_FIVE_PATH_CANDIDATE','intersection_used':False,'old_interval_fallback_used':False},
        'source_and_evidence':evidence,
        'scientific_judgments':judgments,
        'unresolved_blocking_findings':[],
        'validation':{'independent_saved_arithmetic_checks':arithmetic['check_total'],'independent_saved_arithmetic_failures':0,'independent_saved_arithmetic_elapsed_seconds':arithmetic['elapsed_seconds'],'manufactured_cases':9,'manufactured_executions':18,'manufactured_checks':3686,'manufactured_failures':0,'manufactured_elapsed_seconds':receipt['wall_seconds'],'final_saved_evidence_checks':len(checks),'final_saved_evidence_failures':0,'final_saved_evidence_elapsed_seconds':time.perf_counter()-start,'review_entire_human_reading_wall_time':'NOT_MEASURED','final_evidence_check_details':checks},
        'resources':analysis['resources'],
        'not_performed_by_reviewer':{'candidate_integrations':0,'coefficient_evaluations':0,'old_baseline_replays':0,'full_population_runs':0,'NCP_launches':0,'manufactured_reexecutions':0},
        'claim_ceiling':{'E13C9_selected_finite':'PROMOTE_SCOPED_LOCAL_SIGNED_VOLTERRA','E13C8_full_finite':'UNCHANGED_PROMOTE_SCOPED_FULL_FINITE_CAPTURED_OFF','full_population_second_correction':'NOT_RUN','physical':'HOLD','continuum':'HOLD','production':'HOLD','receiver':'HOLD','same_work_serial_speedup':'NOT_ESTABLISHED','provider_attestation':'NOT_ASSERTED'},
        'limitations':['Promotion is bound to these exact five selected path outputs; their32.57%/30.48% gains cannot be extrapolated to the full population.','Bounds enclose a fixed captured finite problem. They are not measured true errors, statistical confidence intervals or physical-model uncertainty.','The signed second-Volterra index does not imply second-order global quadrature; new correction uses whole-cell rectangles.','Manufactured mathematical oracle and saved-prefix cross-check share Python Decimal exp. No proof-assistant verification or independent physical coefficient implementation is claimed.','Actual nonnegative coefficients and smoothness within each captured branch are inherited premises verified by unchanged code and selected domain checks.','The method remains dependent on the validity of admitted first-variation bounds; hashes bind identity, not mathematical validity on their own.'],
        'NCP_disposition':{'new_jobs':0,'action':'NO_NEW_NCP_JOB_FROM_E13C9','reason':'Current required local work completed in seconds, and no unresolved full-population accuracy objective or new bulk work contract is established. Next useful numerical question concerns inherited first-midpoint bounds, before considering heavy parallel work.'},
        'completion':'Necessary selected-path scientific/numerical gates are closed. Stop optional testing and complete additive delivery.'
    }
    save('INDEPENDENT_DECISION.json',decision)
    print(json.dumps({'decision':decision['decision'],'decision_sha256':sha(HERE/'INDEPENDENT_DECISION.json'),'decision_bytes':(HERE/'INDEPENDENT_DECISION.json').stat().st_size,'independent_arithmetic_checks':arithmetic['check_total'],'final_evidence_checks':len(checks),'final_evidence_elapsed_seconds':decision['validation']['final_saved_evidence_elapsed_seconds']},sort_keys=True))

if __name__=='__main__': main()
