#!/usr/bin/env python3
"""Prepare six additive PHYS15 root drafts; external publication belongs to root."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
import json, hashlib

WORK=Path(__file__).resolve().parent.parent
SOURCE=WORK/'HH_PHYS14_20261012_v1/publication_overlay'
ROOT=WORK/'HH_PHYS15_THEORY_20261012_v1'
DEST=ROOT/'publication_overlay'
CORE='research/r31ao_unequal_ladder/hh_phys15_correlated_endpoint_theory_20261013_v1'
BRANCH='research/hh-phys15-correlated-endpoint-theory-20261013'
PARENT='087a16f28d0ee4fc7ae74ae50bfcafe578716e85'
TREE='61a4dc1ed1bf42530ed8fda9596a91962e9912e7'
THEORY=ROOT/'theory/CORRELATED_ENDPOINT_THEORY_KO.md'
THEORY_SHA=hashlib.sha256(THEORY.read_bytes()).hexdigest()
REVIEW='Independent review is in progress; root will update this draft from the actual decision before publication.'
SCOPE='Same-COMMON source-aligned geometric-isotropic Full versus actual two-half endpoint theory, with inherited fixed-alpha source/C2/root premises.'

prefixes={
 'AGENTS.md':f'''# Current priority - PHYS15 correlated endpoint theory, 2026-10-13 KST

Read CURRENT_DEVELOPMENT_PLAN.json and {CORE}/theory/CORRELATED_ENDPOINT_THEORY_KO.md. The current theory constructs the same-COMMON residual, seven photon absorption sectors and their scoped signs, the exact density/fhat source bridge, the original Full preconditioned endpoint bound, and finite T/e/w/adjoint readouts. Reuse the actual PHYS14 two-half carry and original Full source. The original Full UNIFORM_ARITHMETIC.json supplies fixed_C, B, radius and q=0.00011736830563768177 together.

Current status: {REVIEW} The admitted scientific baseline remains PHYS14 PROMOTE_SCOPED while this review is running. The successor is HH_CORRELATED_ENDPOINT_ENCLOSURE: evaluate the correlated residual and endpoint/observable intervals with existing source and carry data. This theory unit has zero new atomic source callbacks, physical root solves or physical history runs.

## Current workflow policy override

The user's 2026-10-12 explicit physmath-research-loop instructions select built-in 1.0.0, THEORY R1-R10, for this request. This replaces the historical v4 harness acquisition and default routing in preserved entries below. Use the current common research, evidence and handoff policies; use the original legacy harness when the user explicitly selects that version. This procedural correction keeps the fixed scientific models, inputs, established results and original scientific acceptance criteria.

Current user instructions have priority over project defaults. Carry forward authorization already evidenced in the session, and complete read-only or otherwise authorized steps without duplicate confirmation. Respect actual access controls and resolve a genuinely new dependency at its source. Reuse completed evidence when its identities and premises persist; validate changed dependencies and then continue the research.

Publish an additive branch stacked on PR49 head {PARENT}. Root updates review and actual publication identities before publishing. Preserve existing files and original global REI DAG evidence, and advance this theory node according to its final review. The next local inclusion task keeps heavy_queue=[] and launch=false; native and microscopic lanes retain their own scientific conditions. Use selective publication readback at the level needed to resolve an actual remaining identity question.

## Preserved PHYS14 and earlier instructions

The exact preceding entry follows. Current priorities and workflow authority are stated above.

''',
 'README.md':f'''# WU088_HH current research: PHYS15 correlated endpoint theory

PHYS15 derives the difference between Full and the actual PHYS14 two-half path from one shared COMMON. The theory connects an exact gas residual to seven photon absorption sectors, their original-grid sign relations, a density/fhat source-normalization bridge, and a finite temperature/adjoint decomposition. The original Full fixed_C, B, radius and q=0.00011736830563768177 give the endpoint transfer bound under the inherited source/C2/root premises.

**Current status:** {REVIEW} PHYS14 remains the admitted scientific baseline. This theory unit uses zero new atomic source evaluations, physical root solves or physical history runs.

Read [the PHYS15 derivation]({CORE}/theory/CORRELATED_ENDPOINT_THEORY_KO.md) and [CURRENT_DEVELOPMENT_PLAN.json](CURRENT_DEVELOPMENT_PLAN.json). The next task, **HH_CORRELATED_ENDPOINT_ENCLOSURE**, evaluates the correlated residual, gas/photon endpoint differences and T/e/w/ne intervals, retaining common inputs and the same inverse for sector contributions.

The current workflow is physmath-research-loop built-in 1.0.0, THEORY R1-R10. The proposed publication is an additive branch stacked on PHYS14 PR49. Existing scientific artifacts and the original global REI DAG remain available as their immutable source records.

## Preserved PHYS14 and earlier README

''',
 'README_KO.md':f'''# WU088_HH 최신 연구: PHYS15 상관된 endpoint 결함 이론

PHYS15는 같은 COMMON에서 출발한 Full과 PHYS14의 실제 two-half 경로를 하나의 잔차로 연결한다. 기체 잔차, 광자 흡수 결함의 일곱 항과 원 격자의 부호 관계, 밀도·fhat source 정규화 연결, 유한 온도 차이와 공통 adjoint 기여를 유도했다. 원 Full의 fixed_C·B·radius·q=0.00011736830563768177을 함께 재사용해 전처리 잔차에서 endpoint 차이로 가는 포함식을 구성했다.

**현재 상태:** 독립 검토가 진행 중이며, 게시 전에 root가 실제 판정에 따라 이 초안을 갱신한다. 채택된 과학 기준점은 PHYS14 PROMOTE_SCOPED다. 이 이론 단위의 새 원자 source 평가, 물리적 root solve와 물리 history 실행은 모두 0회다.

- [PHYS15 상세 유도]({CORE}/theory/CORRELATED_ENDPOINT_THEORY_KO.md)
- [현재 개발계획](CURRENT_DEVELOPMENT_PLAN.json)
- 다음 계산: **HH_CORRELATED_ENDPOINT_ENCLOSURE**. 같은 입력의 상관관계를 유지해 잔차, 기체·광자 endpoint 차이, ΔT/e/w/ne와 공통 inverse를 거친 항별 기여를 포함한다.

현재 운영 규약은 physmath-research-loop built-in 1.0.0의 THEORY R1–R10이다. 기존 과학 원본과 source·C²·근 전제를 재사용하고, PR49 위에 연구 브랜치를 추가하는 방식으로 게시한다. 원 전역 REI DAG와 기존 연구 기록은 각 시점의 근거로 보존한다.

## 보존된 PHYS14 및 이전 안내

''',
 'docs/coding/IMPLEMENTATION_PLAN.md':f'''# Current implementation priorities - PHYS15 endpoint theory, 2026-10-13 KST

Read {CORE}/theory/CORRELATED_ENDPOINT_THEORY_KO.md and root CURRENT_DEVELOPMENT_PLAN.json. Current status: {REVIEW} The existing independently admitted baseline is PHYS14.

The next bounded numerical task is HH_CORRELATED_ENDPOINT_ENCLOSURE. Build the common-input expression DAG from the actual two-half gas/photon equations, the seven absorption sectors, and the density/fhat bridge. Reuse Full UNIFORM_ARITHMETIC.json fixed_C, B, exact binary radius and q=0.00011736830563768177 as one binding. Evaluate the correlated residual r, include d=g2-gF, and use the finite temperature quotient and one shared average inverse for all sector contributions. Preserve the guard chronology and recover the actual photon endpoint difference from the same d_x.

Use the existing Full/half source and PHYS14 carry, root hull and source derivative domains. This PHYS15 theory unit has zero new atomic source callbacks, physical root solves and physical history runs. Any further tightening follows the measured residual width and its actual dependency; first evaluate the inherited-data inclusion. Heavy queue is empty and launch=false.

The current user-selected workflow is physmath-research-loop built-in 1.0.0, THEORY R1-R10; implementation work uses its C1-C10 contract when undertaken. Preserve the mathematical meaning of captured nHe/nH, heat and source leaves, the same alpha and global lambda,b, and all original successful scientific artifacts. Current session authorizations apply to read-only and already authorized work without repeated confirmation.

Publication is an additive branch stacked on PR49 head {PARENT}. The current draft awaits the actual independent decision before root finalizes publication metadata. Existing main and historical artifacts retain their original state.

## Preserved PHYS14 and earlier implementation guidance

'''}

old_plan=json.loads((SOURCE/'CURRENT_DEVELOPMENT_PLAN.json').read_text())
old_state=json.loads((SOURCE/'RESEARCH_STATE.json').read_text())
candidate={
 'loop':'PHYS15','core_path':CORE,'task':'theory','status':'THEORY_DERIVED_INDEPENDENT_REVIEW_IN_PROGRESS',
 'science_decision':'INDEPENDENT_REVIEW_IN_PROGRESS','review_status_text':REVIEW,
 'theory':CORE+'/theory/CORRELATED_ENDPOINT_THEORY_KO.md',
 'independent_decision':CORE+'/review/DECISION.json',
 'decision_file_state_at_draft':'Final review is being produced; root will bind its actual decision before publication.',
 'source_commit':PARENT,'source_root_tree':TREE,'source_pr':'https://github.com/cosmosapjw-quantum/WU088_HH/pull/49',
 'publication_target_branch':BRANCH,'candidate_scope':SCOPE,
 'new_atomic_source_callbacks':0,'new_physical_root_solves':0,'new_physical_history_runs':0,'new_NCP_jobs':0,
 'next_task':'HH_CORRELATED_ENDPOINT_ENCLOSURE','numerical_endpoint_defect_execution':'NOT_RUN_IN_THIS_THEORY_UNIT'}
override={
 'id':'PHYS15_CURRENT_USER_BUILTIN_THEORY_OVERRIDE','authority':'User 2026-10-12 explicit physmath-research-loop skill and reference instructions',
 'previous_rule':'Historical v4 default harness acquisition/routing in preserved project entries',
 'replacement':'Built-in 1.0.0 THEORY R1-R10 and current common/evidence policies; explicit legacy-version requests retain their original route.',
 'reason':'The current user supplied the updated built-in protocol for this theory request.',
 'affected_dependencies':'Workflow entry/routing and evidence reuse only; fixed scientific models and accepted results retain their identity and criteria.',
 'authorization_rule':'Carry existing session authorization forward; no duplicate confirmation for read-only or already authorized steps. Actual access controls remain authoritative.',
 'status':'APPLIED_TO_CURRENT_DRAFT'}

plan=deepcopy(old_plan)
plan.update({
 'plan_date':'2026-10-13','decision':'PHYS15_THEORY_DERIVED_INDEPENDENT_REVIEW_IN_PROGRESS',
 'scope':SCOPE,'active_plan':CORE+'/theory/CORRELATED_ENDPOINT_THEORY_KO.md',
 'dag':CORE+'/NEXT_DAG.json','observable_contracts':CORE+'/theory/CORRELATED_ENDPOINT_THEORY_KO.md',
 'ncp_tasks':CORE+'/NCP_TASKS.json','handoff':CORE+'/HANDOFF_KO.md',
 'planning_review':CORE+'/review/DECISION.json',
 'next_here':['HH_CORRELATED_ENDPOINT_ENCLOSURE'],
 'next_here_status':'DEFINED_BY_CURRENT_THEORY; NUMERICAL_INCLUSION_NOT_RUN',
 'current_result':candidate['theory'],'independent_science_review':candidate['independent_decision'],
 'current_science_state':CORE+'/state/RESEARCH_STATE.json',
 'next_action':'Finish current independent theory review, then evaluate correlated same-COMMON Full-vs-two-half residual and T/e/w/ne/photon endpoint enclosures using the existing source/carry/preconditioner binding.',
 'new_scientific_runs_in_current_loop':0,'new_atomic_source_callbacks_in_current_loop':0,
 'new_physical_root_solves_in_current_loop':0,'new_physical_history_runs_in_current_loop':0,
 'new_native_runs_in_current_loop':0,'new_NCP_jobs_in_current_loop':0,
 'publication_target_branch':BRANCH,'current_candidate':candidate,
 'execution_count_note':'A theory derivation and discriminating algebraic checks use the admitted data. New physical source/root/history executions and NCP jobs in this theory unit are zero; algebra-check counts are recorded in their own receipts.',
 'publication_preparation_status':'DRAFT_INDEPENDENT_REVIEW_IN_PROGRESS',
 'publication_review_status':REVIEW,'workflow_version':'1.0.0','workflow_track':'THEORY_R1_R10',
 'workflow_policy_override':override,
 'publication_stack':{'parent_commit':PARENT,'parent_tree':TREE,'base_branch':'research/hh-phys14-carried-second-half-20261012','parent_pr':49,'merge_main':False,'delete_existing_files':False},
 'original_global_DAG_identity_preserved':True,
 'previous_PHYS14_root_snapshot':old_plan})
# The admitted baseline deliberately remains the original PHYS14 object while review runs.
assert plan['scientific_baseline']==old_plan['scientific_baseline']
assert plan['current_scientific_baseline']==old_plan['current_scientific_baseline']

state=deepcopy(old_state)
state.update({
 'current_candidate':candidate,'current_execution':{
    'status':'THEORY_DERIVED_INDEPENDENT_REVIEW_IN_PROGRESS','scientific_status':'THEORY; PHYSICAL_ENDPOINT_ENCLOSURE_NOT_RUN',
    'actual_scientific_histories':0,'new_implicit_stages':0,'new_physical_root_solves':0,
    'new_native_runs':0,'new_atomic_source_callbacks':0,'new_NCP_jobs':0,'heavy_queue':[],'launch':False,
    'execution_evidence':'Current theorem and separate algebraic-check receipts; root binds final files before publication.'},
 'current_plan_update':{'path':CORE+'/NEXT_DAG.json','kind':'CORRELATED_ENDPOINT_THEORY_AND_NUMERICAL_SUCCESSOR',
    'status':'INDEPENDENT_REVIEW_IN_PROGRESS','theory':candidate['theory'],'review':candidate['independent_decision'],
    'external_RUX_nodes_newly_completed':[],'next_task':'HH_CORRELATED_ENDPOINT_ENCLOSURE'},
 'publication_preparation_status':'DRAFT_INDEPENDENT_REVIEW_IN_PROGRESS','publication_review_status':REVIEW,
 'admitted_current_science_remains_PHYS14_until_final_decision':True,
 'workflow_version':'1.0.0','workflow_track':'THEORY_R1_R10','workflow_policy_override':override,
 'previous_PHYS14_root_snapshot':old_state})
assert state['current_science']==old_state['current_science']

outputs={**{name:prefix.encode()+(SOURCE/name).read_bytes() for name,prefix in prefixes.items()},
 'CURRENT_DEVELOPMENT_PLAN.json':(json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode(),
 'RESEARCH_STATE.json':(json.dumps(state,ensure_ascii=False,indent=2)+'\n').encode()}
assert len(outputs)==6
assert not DEST.exists(), 'This draft writer is create-only; root owns later review updates.'
records=[]
for name,payload in outputs.items():
    path=DEST/name;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(payload)
    original=(SOURCE/name).read_bytes()
    method='exact prior UTF-8 bytes retained as suffix' if name in prefixes else 'complete original JSON object retained unchanged at previous_PHYS14_root_snapshot; current admitted PHYS14 science object unchanged'
    if name in prefixes:assert payload.endswith(original)
    else:assert json.loads(payload)['previous_PHYS14_root_snapshot']==json.loads(original)
    records.append({'path':name,'source_path':str(SOURCE/name),'source_bytes':len(original),'source_sha256':hashlib.sha256(original).hexdigest(),'source_git_blob_sha':hashlib.sha1(b'blob '+str(len(original)).encode()+b'\0'+original).hexdigest(),'draft_bytes':len(payload),'draft_sha256':hashlib.sha256(payload).hexdigest(),'preservation':method})
receipt={
 'schema':'WU088_HH_PHYS15_ROOT_OVERLAY_DRAFT_V1','created_at_utc':datetime.now(timezone.utc).isoformat(),
 'status':'DRAFT_INDEPENDENT_REVIEW_IN_PROGRESS','review_status_text':REVIEW,'cloud_writes':0,
 'source_parent_commit':PARENT,'source_parent_tree':TREE,'planned_core':CORE,'planned_branch':BRANCH,
 'theory_read':{'path':str(THEORY),'sha256_at_draft':THEORY_SHA,'scope':'Entire sections 1-11 and references'},
 'files':records,'all_six_source_files_unchanged':True,
 'review_owner_next_action':'Replace draft review status with actual final independent decision; bind generated DAG/state/handoff and actual publication identities before creating Git objects.',
 'policy_override':override}
evidence=ROOT/'evidence';evidence.mkdir(exist_ok=True)
(evidence/'ROOT_OVERLAY_DRAFT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':receipt['status'],'files':len(records),'core':CORE,'all_prior_content_preserved':True,'cloud_writes':0},indent=2))
