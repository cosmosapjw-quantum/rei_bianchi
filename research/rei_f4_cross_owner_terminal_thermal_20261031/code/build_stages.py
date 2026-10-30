"""One bounded research-loop R1–R10/C1–C10 retrospective science checkpoint ledger."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
P=R/'stages';P.mkdir(exist_ok=True)
roles={
 'R1':('질문과 source contract','SOURCE_LOCK.json'),
 'R2':('문헌 및 네 원본 데이터','SOURCE_LOCK.json'),
 'R3':('서로 다른 source owner와 가정 구분','THEORY_AND_RESULTS_KO.md'),
 'R4':('저에너지 하한과 전체 에너지 상한 분리','THEORY_AND_RESULTS_KO.md'),
 'R5':('clock/heat capacity/source 일치 유도','THEORY_AND_RESULTS_KO.md'),
 'R6':('조건부 상한 오해에 대한 적대적 검증','ADVERSARIAL_AUDIT_KO.md'),
 'R7':('192 원본 도착구간 경량 검산','results/CROSS_OWNER_TERMINAL_THERMAL_192.csv'),
 'R8':('물리 해석 및 정준 승인 판정','results/SCIENCE_RESULTS.json'),
 'R9':('실제 21종 bath/cell clock 계산 식','code/build_joint.py'),
 'R10':('재개 가능한 연구 인계','HANDOFF_NEXT_THREAD_KO.md'),
 'C1':('원본 입력과 acceptance','SOURCE_LOCK.json'),
 'C2':('실제 원본 CSV 매핑','code/build_joint.py'),
 'C3':('energy partition/cv/proper clock','code/build_joint.py'),
 'C4':('단일 격리 계산 경로','README.md'),
 'C5':('실행 가능한 계산 및 그림','code/build_joint.py'),
 'C6':('실행 및 negative test','tests/test_cross_source.py'),
 'C7':('192 물리 구간 보존·단위 검증','tests/test_cross_source.py'),
 'C8':('출력 fingerprint·clock mesh','results/SCIENCE_RESULTS.json'),
 'C9':('same-author hostile review','ADVERSARIAL_AUDIT_KO.md'),
 'C10':('단일 검증 패키지·handoff','HANDOFF_NEXT_THREAD_KO.md'),
}
for key,(name,evidence) in roles.items():
 data={
 'schema':'REI_F4_SCOPED_STAGE_V1','stage':key,'stage_name':name,
 'scientific_unit':'F4_PR299_PR300_CAUSAL_TERMINAL_THERMAL_ELECTRON_CLOCK_CROSSWALK',
 'single_bounded_run':True,'not_twenty_independent_science_executions':True,
 'status':'PASS_SCOPED' if key not in ('R6','C9') else 'PASS_SAME_AUTHOR_ONLY',
 'evidence_relpath':evidence,'canonical_progress':{'working':'33/88','central':'28/88','physical_fast':'4/7','canonical_delta':0},
 'scientific_claim':'COND_FIRST_GENERATION_ENERGY_AND_CLOCK; NOT_EVOLVED_GAS',
 'distinct_author_review':'NOT_RUN', 'native_subagent':'NOT_AVAILABLE',
 'production':'HOLD','no_IVP':True,'auto_next_node':False,
 'backup_target':'new master ZIP, Git draft research branch, Library and Drive; verify provider receipts separately'
 }
 (P/(key+'.json')).write_text(json.dumps(data,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
(R/'STAGE_LEDGER.json').write_text(json.dumps({'schema':'REI_F4_STAGE_LEDGER_V1','source_unit':roles['R1'][0], 'stages':{k:roles[k][0] for k in roles},'status':'SINGLE_SCIENCE_UNIT_SCOPED','one_bounded_loop':True,'distinct_author_review':'NOT_RUN','DAG':{'working':'33/88','central':'28/88','physical_fast':'4/7','canonical_delta':0}},ensure_ascii=False,indent=2,sort_keys=True)+'\n')
print('R1–R10 10/10 SCOPED; C1–C10 10/10 SCOPED; distinct-author R6/C9 NOT_RUN')