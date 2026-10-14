#!/usr/bin/env python3
"""Assemble frozen PHYS30 evidence; no candidate import or science rerun."""
from pathlib import Path
from datetime import datetime,timezone
from decimal import Decimal
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def rd(name):return json.loads((ROOT/name).read_bytes())
def ident(name):
 b=(ROOT/name).read_bytes();return {'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def put(name,text):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
def js(name,obj):put(name,json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def fmt(v):return format(Decimal(v),'.12f')
r=rd('contributions/numerics/PROFILE_SECOND_ORDER_FIRST.json')
e=rd('contributions/numerics/EXECUTION.json')
rp=rd('portability/REPLAY_RECEIPT.json')
oi=rd('evidence/OWNER_FIRST_RESULT_INTAKE.json')
ct=rd('PHYSICS_CONTRACT.json')
tc=rd('contributions/theory/THEORY_CLAIMS.json')
assert r['summary']['all_pass'] and r['summary']['passed']==56
assert e['exit_code']==0 and e['actual_main_invocations']==1
assert rp['status']=='REPLAY_PASS' and rp['new_program_replay_invocations']==1
assert rp['result_byte_equal'] and rp['result_parsed_json_equal']
assert rp['actual_counts']==r['actual_counts']
assert (ROOT/'portability/raw/PROFILE_SECOND_ORDER_REPLAY.json').read_bytes()==(ROOT/'contributions/numerics/PROFILE_SECOND_ORDER_FIRST.json').read_bytes()
now=datetime.now(timezone.utc).isoformat()
profiles=('uniform','triangular');branches=('upper_root','lower_root')
def a(p,b):return r['profile_results'][p]['branches'][b]['affine']
names={'upper_root':r'\(W_*\): 상단 응답의 근','lower_root':r'\(W_0\): 하단 응답의 근'}
number_table='\n'.join('| '+names[b]+' | '+' | '.join(fmt(v) for v in (a('uniform',b)['c_eV'],a('uniform',b)['d_dimensionless'],a('triangular',b)['d_dimensionless'],a('triangular',b)['d_profile_increment_from_uniform']))+' |' for b in branches)
term_labels=[
 ('profile_band_averaging','프로파일 평균화'),('center_variance_V_second','실제 분산 보정'),
 ('endpoint_curvature','끝점 속도 제곱'),('center_curvature','내부 중심 속도 제곱'),
 ('endpoint_acceleration','끝점 가속도'),('center_acceleration_at_fixed_V','고정 V의 내부 중심 가속도'),
 ('probability_acceleration_at_fixed_V','고정 V의 확률 가속도'),('probability_endpoint_motion_cross','확률×끝점 이동'),
 ('probability_center_motion_cross','확률×내부 중심 이동'),('implicit_root_delta_W_cross','암묵근 δ–W 혼합'),
 ('implicit_root_W_curvature','암묵근 W 곡률')]
term_table='\n'.join('| '+label+' | '+' | '.join(fmt(a(p,b)['d_decomposition_dimensionless'][key]) for b in branches for p in profiles)+' |' for key,label in term_labels)
totals={k:v+rp['actual_counts'][k] for k,v in r['actual_counts'].items()}
scope=[
 'Conditional direct theorem for fixed symmetric Borel probability profiles, an unchanged common center interval and inherited kernel regularity/signs.',
 'Physical one-sided C2 at an exact interior simple root; exact-root existence remains a premise, not a new enclosure.',
 'Profile-invariant c and affine mu2 dependence of d; equal mu2 gives equality through local second order only.',
 'Retained finite-point same-A-level algebra for uniform and triangular profiles, with nonzero A numerator correction.',
 'Two disclosed algebra paths and one same-host separate-path deterministic replay; no independent physical data.'
]
next_state={'task':'PHYS31','status':'PROPOSED_NOT_RUN','question':'For fixed symmetric profiles with the same mu2 but different higher moments, at what next local order can the threshold expansions first differ?','new_theorem_or_numerical_execution':0,'handoff':'next/PHYS31_NEXT_HANDOFF_KO.md'}
summary={
 'task':r['task'],'name':ct['name'],'assembled_utc':now,'scientific_status':r['status'],
 'final_decision_authority':'independent/DECISION_REVIEW.json',
 'status_chronology':'Scientific content frozen for a distinct reviewer; later decision/CLOSEOUT own promotion. No decision preclaim.',
 'primary_result':{'c':'c_nu=c_uniform','d':'d_nu=d_uniform+(mu2-1/3)*(1-calH/(2*C))','K':'K_nu=K_uniform+(mu2-1/3)*(calH-2*C))','calH':'p*k_second(e)+q*k_second(x)','convention':'d=Wsecond(0+)/2, delta outer halfwidth eV, W actual variance eV2'},
 'first_summary':r['summary'],'raw':ident('contributions/numerics/PROFILE_SECOND_ORDER_FIRST.json'),
 'first_execution':{'identity':ident('contributions/numerics/EXECUTION.json'),'exit_code':e['exit_code'],'started_utc':e['started_utc'],'ended_utc':e['ended_utc'],'wall_seconds':e['wall_seconds'],'timeout_seconds':e['timeout_seconds']},
 'check_detail':{'numeric_groups':31,'exact_groups':15,'discrete_groups':10,'component_rows':oi['component_count'],'identity_member_rows':oi['identity_member_count'],'maximum_stored_scaled_error':oi['maximum_stored_scaled_error']['maximum_scaled_error'],'frozen_tolerance':'1e-60','interpretation':'Arithmetic consistency, not physical/root/J/Taylor uncertainty.'},
 'profiles':r['exact_profile_moments'],'branch_profile_slopes':r['branch_profile_slopes'],
 'profile_coefficients':{p:{b:a(p,b) for b in branches} for p in profiles},
 'retained_nonzero_A':{p:{b:r['profile_results'][p]['branches'][b]['retained_nonzero_A_diagnostics'] for b in branches} for p in profiles},
 'gap':r['gap_results'],'same_mu2_scope':'Equal local expansion through second order at the same exact root, or same retained A-level; o(delta2), no positive-width identity.',
 'variance_gap_cancellation':{'theory':'Exact common mu2 cancellation','observed_uniform':'-2E-80','observed_triangular':'0E-80','interpretation':'Retained Decimal roundoff, not overwritten by exact zero.'},
 'replay':{'status':rp['status'],'byte_equal':rp['result_byte_equal'],'parsed_json_equal':rp['result_parsed_json_equal'],'receipt':ident('portability/REPLAY_RECEIPT.json'),'raw':ident('portability/raw/PROFILE_SECOND_ORDER_REPLAY.json'),'exit_code':rp['actual_exit_code'],'started_utc':rp['started_utc'],'ended_utc':rp['ended_utc'],'wall_seconds':rp['wall_seconds'],'restored_runtime_payloads':14,'restored_files_with_manifest':15,'before_after_exact_set_SHA_size_mode':True,'same_host_same_Python':True,'independent_physics_credit':0},
 'total_execution':{'new_main':2,'first_main':1,'replay_main':1,'new_physical_kernel_or_derivative_evaluations':0,'new_physical_roots':0,'old_PHYS19_through_PHYS29_main_suite_imports':0,'all_main_event_totals':totals,'independent_physical_evidence_credit':0,'report_and_figure_cached_postprocessing_is_science_main':False},
 'inherited_execution_not_repeated':{'PHYS29_main':2,'PHYS29_joint_kernel_node_evaluations':16,'PHYS29_checks_per_main':238,'new_credit_this_loop':0},
 'claim_scope':scope,'retained_limits':ct['claim_limits'],'protected':ct['protected_state'],'next':next_state
}
# Formula typography only; the program/result are already immutable.
summary['primary_result']['K']='K_nu=K_uniform+(mu2-1/3)*(calH-2*C)'
js('report/PHYS30_RESULTS_SUMMARY.json',summary)
body=(ROOT/'owner_tools/REPORT_BODY_KO.template.md').read_text()
body=body.replace('@NUMBER_TABLE@',number_table).replace('@TERM_TABLE@',term_table)
body=body.replace('@FIRST_TIME@',f"{e['wall_seconds']:.6f}").replace('@REPLAY_TIME@',f"{rp['wall_seconds']:.6f}")
proof=(ROOT/'contributions/theory/DERIVATION_KO.md').read_text()
proof=proof.replace('](../../','](../').replace('](THEORY_CLAIMS.json)','](../contributions/theory/THEORY_CLAIMS.json)').replace('](PROVENANCE.json)','](../contributions/theory/PROVENANCE.json)')
proof='\n'.join('#'+line if line.startswith('#') else line for line in proof.splitlines())+'\n'
body+='\n## 부록 A. 첫 실행 전에 동결한 전체 직접 증명\n\n아래는 이론 기여의 완전한 본문이다. 이 기여자가 수치 실행을 하지 않았다는 NOT_RUN 표시는 그 역할과 작성 시점의 기록이며, 본 보고서 앞부분의 실제 first/replay 결과와 구별한다. 원 본문에 상대 링크와 제목 깊이만 맞췄고 수식·주장은 변경하지 않았다.\n\n'+proof
put('report/PHYS30_REPORT_KO.md',body)
put('next/PHYS31_NEXT_HANDOFF_KO.md',(ROOT/'owner_tools/NEXT_BODY_KO.template.md').read_text())
numeric=[
 {'id':'NC30-01','claim':'Exact profile moments and A1 quadratic limits, including the residual-omission negative control, pass.','evidence_status':'numerically checked with exact arithmetic','depends_on':['TC30-01','TC30-14','TC30-17','TC30-18'],'evidence':['exact_profile_moments','exact_quadratic_toys','checks']},
 {'id':'NC30-02','claim':'Uniform/triangular retained same-A-level coefficients agree between disclosed affine and bivariate paths at fixed tolerance.','evidence_status':'numerically checked','depends_on':['TC30-09','TC30-11','TC30-13'],'evidence':['profile_results','branch_profile_slopes','checks']},
 {'id':'NC30-03','claim':'The eleven d contributions and gap transfer agree, with exact-theory mu2 cancellation distinguished from stored roundoff.','evidence_status':'numerically checked','depends_on':['TC30-08','TC30-12'],'evidence':['profile_results','gap_results','checks']},
 {'id':'IC30-01','claim':'Sole first main and sole same-host separate-path replay pass with identical raw bytes/JSON and unchanged runtime identities.','evidence_status':'implementation-verified','depends_on':['NC30-01','NC30-02','NC30-03'],'evidence':['contributions/numerics/EXECUTION.json','portability/REPLAY_RECEIPT.json'],'limit':'No new physical data/evaluations or provider diversity.'}]
js('evidence/CLAIM_LEDGER.json',{'task':r['task'],'theory_source':ident('contributions/theory/THEORY_CLAIMS.json'),'theory_claims':tc['claims'],'numeric_and_implementation_claims':numeric,'raw_evidence':ident('contributions/numerics/PROFILE_SECOND_ORDER_FIRST.json'),'scope':scope,'unresolved':ct['claim_limits'],'review_authority':'independent/DECISION_REVIEW.json','derived_theory_claims':19,'proposals':1,'generated_before_final_decision':True})
old=(ROOT/'state/EXECUTION_LEDGER.json').read_text();put('state/INTAKE_EXECUTION_LEDGER.json',old)
ledger={'task':r['task'],'utc':now,'status':'SCIENCE_COMPLETE_AWAITING_DISTINCT_DECISION','first':ident('contributions/numerics/EXECUTION.json'),'replay':ident('portability/REPLAY_RECEIPT.json'),'actual_current_totals':summary['total_execution'],'inherited_not_rerun':summary['inherited_execution_not_repeated'],'scientific_failures':0,'metadata_failures_preserved':True,'protected':ct['protected_state']}
(ROOT/'state/EXECUTION_LEDGER.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
put('README_KO.md',"""# REI-PHYS30-20261011\n\nreport/PHYS30_REPORT_KO.md는 전체 직접 증명 부록과 실제 수치 결과를 포함한다. 최종 판정은 independent/DECISION_REVIEW.json, 실제 연구 종료는 state/CLOSEOUT.json을 따른다. 최종 MANIFEST.json은 자기 자신을 제외한 모든 payload의 SHA256·bytes·mode를 연결한다.\n\n새 cached 프로그램의 실행 입력은 contributions/numerics/PREEXECUTION_FROZEN.json의14개 payload와 manifest 자체다. 과거 PHYS29 프로그램을 import하지 않는다. 최초 raw와 portability/raw의 재현 raw가 동일하다. 단일시도와 신규출력 guard가 있으며, 현재 세션의 first1+replay1 예산은 이미 사용했다. 현재 파일을 읽거나 archive를 검증하는 작업에서 과학 프로그램을 다시 실행하지 않는다.\n\n전체 ZIP에는 연구·코드·입력·실패이력·재현·판정 자료가 있다. 후속 publication receipt와 실제 전달 ACK는 해시 순환을 피하는 분리된 기록이다. 원격 ZIP 전체 복원 주장은 하지 않는다. PHYS31은 제안이며 NOT_RUN이다.\n""")
js('evidence/REPORT_ASSEMBLY.json',{'task':r['task'],'utc':now,'method':'Direct prose, stored-value display formatting and counter aggregation only; no candidate import or coefficient reevaluation. Full theory appendix changes heading depth and relative links only.','inputs':[ident(p) for p in ['contributions/numerics/PROFILE_SECOND_ORDER_FIRST.json','contributions/numerics/EXECUTION.json','portability/REPLAY_RECEIPT.json','contributions/theory/DERIVATION_KO.md']],'outputs':[ident(p) for p in ['report/PHYS30_REPORT_KO.md','report/PHYS30_RESULTS_SUMMARY.json','next/PHYS31_NEXT_HANDOFF_KO.md','evidence/CLAIM_LEDGER.json']],'science_main':0,'physical_kernel_derivative_root':0})
print(json.dumps({'status':'REPORT_SUMMARY_NEXT_LEDGER_WRITTEN','science_main':0,'report':ident('report/PHYS30_REPORT_KO.md'),'summary':ident('report/PHYS30_RESULTS_SUMMARY.json'),'next':ident('next/PHYS31_NEXT_HANDOFF_KO.md')},ensure_ascii=False))

