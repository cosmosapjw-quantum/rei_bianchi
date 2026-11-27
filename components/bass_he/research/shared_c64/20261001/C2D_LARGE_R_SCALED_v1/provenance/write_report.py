"""Write the report and next handoff from completed scalar audit evidence."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from mpi_batch import atomic_create,json_bytes
a=json.loads((ROOT/'evidence/FINAL_AUDIT.json').read_bytes());c=json.loads((ROOT/'CONTRACT.json').read_bytes())
ok=a['stop']=='SCOPED_LARGE_R_SCALED_SEQUENCE_CONVERGED';b=a['budgets'];rec=a.get('recovery_audit')
rows=[]
for r in a['sequence']:
 rows.append(f"| {r['R']:g} | {r['Q_O']:.12g} | {r['Q_B']:.12g} | {100*r['Q_O_relative_difference_from_C']:+.7g}% | {100*r['Q_B_relative_difference_from_C']:+.7g}% | {'새 quartet' if r['new_point'] else '상속 scalar'} |")
table='\n'.join(rows)
pairchecks=[];spatial={'Q_O':[],'Q_B':[]}
for row in a['state_audit']['rows']:
 chosen=next((t for t in row['tiers'] if t['tier']==row['selected_tier']),None)
 if not chosen:continue
 audit=chosen['audit'];pairchecks.extend(p['checks'] for p in audit['pairs'].values())
 for refinement in audit['checks']['refinements'].values():
  for lane in ('direct','force'):
   for q in spatial:spatial[q].append(refinement[lane]['scaled_abs'][q])
metricrows=[]
for name,key,limit in [('공간 정밀화','spatial','spatial_abs'),('direct–force','direct_force_scaled_abs','direct_force_abs'),('원점 항등식','origin_scaled_abs','origin_abs'),('momentum 항등식의 전파','momentum_scaled_abs','momentum_abs')]:
 for q in ('Q_O','Q_B'):
  value=max(spatial[q]) if key=='spatial' else max(v[key][q] for v in pairchecks)
  metricrows.append(f"| {q} {name} | {value:.6g} | {c['scaled_criteria'][q+'_'+limit]:.6g} |")
metrics='\n'.join(metricrows)
continuation=a['continuation_audit'];parity=a['parity_audit'];anchor=a['anchor_audit']
min_overlap=min((abs(r['selected']['normalized_overlap']) for r in continuation.get('rows',[])),default=float('nan'))
anchor_values={g['name']:g['value'] for row in anchor.get('comparisons',[]) if row['label']=='l96' for g in row['gates']}
runtime='\n'.join(f"| {Path(r['folder']).name} | {r['elapsed_seconds']:.6f} | {r['returncode']} | {r.get('recovery_status',r['status'])} |" for r in a['batches'])
nextnode='C2E_COLLISION_DOMAIN_AND_SPECTRAL_TARGET_CONTRACT' if ok else 'C2D_IDENTIFIED_BLOCKER_RESOLUTION'
report=f'''# BASS_HE C2d: 큰 R의 두 원점 scaled coupling 검증

최종 상태: **{a['stop']}**. 범위는 새 x=R/a_A=32,64의 수치 quartet, x=32의 독립 구면 표현, x=16,18,…,64의 공통 O 원점 상태 연결이다. 전체 C2와 물리 production 승격은 보류한다. 이 구현은 논문에서 독립적으로 도출한 코드이며 저자의 ARSENY 코드는 아니다.

## 두 coupling의 결과

ell=L/(-i hbar), Q_O=ell_O/x, Q_B=-x² ell_B를 사용했다. 상속된 해석적 계수는 각각 32√2/243={c['coefficients']['Q_O']['value']:.15g}, 128√2/729={c['coefficients']['Q_B']['value']:.15g}다.

| x | Q_O | Q_B | Q_O의 극한계수 대비 차이 | Q_B의 극한계수 대비 차이 | 근거 |
|---:|---:|---:|---:|---:|---|
{table}

이 차이는 유한 R에서 극한계수와 떨어진 정도다. 수치 오차 막대나 엄밀한 오차 상한으로 쓰지 않는다. x=4,8,16은 기존 C2a/C2b 결과를 재사용했고 새 세 적분 차수의 closure로 승격하지 않았다. 새로운 두 점으로 remainder 차수·상수·유효 반경을 개선하거나 단조 수렴을 인증하지 않았다.

## 독립 판정과 정확도

각 새 점에서 base/h/p/tail 네 격자, 직접 적분 q16/24/32와 force 적분 q12/20/28, 두 연속 증가량과 terminal 3×3 교차 비교를 적용했다. tail은 원래 내부 knot를 그대로 보존한다. raw 기준과 다음 scaled 기준을 모두 요구했다.

| 경험적 검산 | 관측 최댓값 | 등록 기준 |
|---|---:|---:|
{metrics}

독립 구면 l96과 prolate의 x=32 차이는 Q_O {anchor_values.get('Q_O_agreement',float('nan')):.6g}, Q_B {anchor_values.get('Q_B_agreement',float('nan')):.6g}다. 구면 표현은 별도의 l72→96 증가량, 적분 증가량, norm·잔차·momentum 검사를 포함한다. 구면 anchor 승인={anchor['accepted']}.

공통 O 좌표의 인접 거리 연결은 {continuation.get('edge_sector_count',0)}개 edge-sector, 최소 |normalized overlap|={min_overlap:.12g}이다. 세 적분 차수의 두 증가량·양방향 일치·self norm을 검사했다. continuation 승인={continuation['pass']}; 네 native/reference parity 승인={parity['pass']}. 중간 bridge의 base 상태는 phase/residual/overlap 근거이며 h/p/tail 공간 수렴 근거로 사용하지 않았다.

B coupling을 큰 항의 차감으로 계산하면 x=64에서 약393207의 상쇄 지표가 발생한다. 따라서 B 원점 직접 integrand와 Q_B=x³ T_A/Delta의 안정적인 force 경로를 각각 평가하고 원점 항등식은 검산으로 남겼다. 큰 R의 지수적으로 작은 A 쪽 꼬리에서 부호를 정하던 코드는 가장 큰 regular spline 표본을 양수로 정하도록 고쳤다. 이는 전체 ± 위상만 바꾸며, 표본 음의 L² 질량 진단과 physical overlap을 별도로 확인했다.

## 실행과 정확도를 보존하는 병렬화

Fortran real64/OpenMP/SIMD 커널, 명시적인 OpenMPI, OMP/BLAS 1 thread, strict 부동소수점 옵션을 유지했다. fast-math·혼합 정밀도·암묵적 backend fallback은 없다. 초기 상태 작업은 memory preflight가 허용한 2 workers, 후속 적분은 3 workers를 사용했다. 관측된 환경은 CPU quota8/affinity9, 메모리8GiB이며 NCP64 실제 scaling은 NOT_RUN이다.

로컬 MPI unbound 예외에서도 OpenMP close/cores가 native ABI 로드 시 모든 작업자를 CPU0에 묶는 문제를 발견했다. fresh subprocess 및 3 MPI ranks의 제조 검사로 원인을 재현했다. 명시적 local-unbound에서 부모 MPI와 자식 worker 모두 OMP_PROC_BIND=FALSE를 유지하도록 실행 경계만 수정했다. NCP의 core/close 기본값과 계산 worker·native·수식 코드는 그대로다. 실제 worker mask의 관측 기록은 review의 affinity 증거에 있다. 각 batch의 작업이 달라 동일 workload 속도 배수는 산출하지 않았다.

| Batch | 실측 wall 초 | 원 return code | 상태 |
|---|---:|---:|---|
{runtime}

선택 상태 {b['new_selected_states']}개, 완료된 고유 task {sum(b['counts_by_kind'].values())}개. 실제 시작 시도는 {sum(b['attempted_counts_by_kind'].values())}개이며 중단 시도도 포함한다. 완료 작업의 재실행은 {rec['completed_task_replays'] if rec else 0}회다. 전체 launcher의 보수적 과금 wall은 {b.get('charged_all_launch_wall_seconds',b['active_batch_wall_seconds']):.6f}초/등록3600초, 관측 최대 worker RSS는 {b['max_worker_rss_mib']:.6f}MiB다.

원래 후속 batch의 1800초 상한·timeout·종료 기록을 보존했다. PARTIAL_BATCH_INDEX는 원본 BATCH_SUMMARY를 위조하지 않고 완료된 TASK_EXECUTION/RESULT/DATA를 결합한다. 복구는 정확히 같은 미완료 입력·상태·적분 차수만 대상으로 하며, 종료 신호가 확인된 중단 작업도 시도수에 포함한다. 메모리 preflight와 프로세스 cleanup, 완료 재실행0, 원래 총시간·시도수 한도를 별도로 검증한다. 실행 복구 상태={rec['status'] if rec else 'NOT_USED'}; 이것만으로 과학 PASS를 추론하지 않는다.

## 남은 연구 범위

full_C2_closed=false, scientific_PROMOTE=HOLD, full_certificate_fail_closed=true, Eq55=NOT_RUN, production_default_change=NOT_AUTHORIZED를 유지한다. 전체 충돌 R 범위, hidden crossing/isolation, H1s+He n2의 rank-five target, 연속공간 enclosure와 collision evolution·단면적은 아직 닫지 않았다.

다음 단일 의존성은 **{nextnode}**다. 통과 시 먼저 실제 충돌 영역과 추적할 spectral projector/외부 gap의 정의를 회수·고정한다. large-R의 다섯 상태를 전 R의 고정 rank-five cluster로 자동 연장하지 않는다. 새 수치 실행 범위나 허용치를 이 보고서에서 임의로 추가하지 않는다.

## 재현 근거

현재 계약 SHA256: {a['contract_sha256']}. 실행 당시 소스는 provenance의 MAIN/FOLLOWUP/RECOVERY_CODE_SNAPSHOT.zip, scalar 판정은 evidence/FINAL_AUDIT.json, 독립 검토는 review에 있다. 전체 archive에는 상태·입력·로그·실패와 복구 증거를 포함한다. 원본 논문 PDF는 공개하지 않는다. archive의 로컬 CRC와 모든 payload SHA 검증, 외부 저장 ACK/size 확인을 구별하며 ACK를 restore 검증으로 부르지 않는다.
'''
atomic_create(ROOT/'REPORT_KO.md',report.encode())
handoff=f'''# 다음 단일 의존성: {nextnode}

C2d STOP={a['stop']}. 새 x32,64 raw+QO/QB quartet 승인={a['gates']['state_quartets']}, 구면 anchor={a['gates']['anchor']}, continuation={a['gates']['continuation']}, parity={a['gates']['parity']}. 최종 근거는 evidence/FINAL_AUDIT.json과 review의 독립 scalar 검산이다. full C2=false/PROMOTE=HOLD/Eq55=NOT_RUN을 유지한다.

새 선택 상태64개 및 초기34 tasks를 완료했다. 이후 overlap144·sphere observation2·parity4의 고유 task를 계약에 따라 검사했다. 완료된 task를 재실행하지 말고 입력·상태 SHA를 pin하여 재사용한다. 원 timeout과 실제 복구 ledger를 함께 읽고, 실패한 원 실행을 정상 종료로 바꾸지 않는다. 새 source identity는 original snapshots와 구별한다.

다음은 충돌에 필요한 R 영역과 spectral target 계약이다. 기존 trajectory/impact/energy 범위를 원자료에서 회수하고, fixed-m ground/bright pair의 검증과 rank-five He n2+H1s target을 구별한다. 큰 R의 다섯 상태가 모든 R에서 격리된 같은 projector라는 가정을 먼저 검사한다. UA n2/n3 multiplet 구조 때문에 최저 다섯 excited states를 자동 추적하는 방식의 외부 gap은 R→0에서 균일하게 유지된다고 가정할 수 없다. 등록되지 않은 production 범위·tolerance·D1·Eq55를 추가하지 않는다. 상세 권고는 review/NEXT_DEPENDENCY_RECOMMENDATION_KO.md다.

HPC 정책은 Fortran real64/OpenMP/SIMD + explicit OpenMPI, strict/no-fast-math, 실제 topology/memory preflight다. local --bind-to none은 BASS_LOCAL_UNBOUND=1/OMP_PROC_BIND=FALSE를 부모와 worker에 전파한다. NCP default core/close는 유지한다. CPU0 몰림을 고친 소스와 제조·실제 affinity 증거를 재사용하고 NCP64 성능을 가정하지 않는다. 새 성능 측정은 새로 등록한 영향을 받는 workload만 대상으로 한다.

복원 시 완료 과학 suite를 반복하지 않는다. 필요한 코드·DATA·STATE만 manifest와 size/SHA로 확인한다. 공개 Git subset에는 PDF와 상태 바이너리를 넣지 않았으며, 전체 archive에 실행 근거가 있다. 업로드 ACK/size는 restore 검증이 아니다.
'''
atomic_create(ROOT/'NEXT_HANDOFF_KO.md',handoff.encode())
claims={'node':c['node'],'stop':a['stop'],'scoped_gates':a['gates'],'global_gates':c['gates'],'new_scientific_endpoints':[32,64],'inherited_scalars':[4,8,16],'bridge_spatial_closure_claimed':False,'continuum_enclosure':False,'asymptotic_radius_certificate':False,'NCP64_actual_scaling':'NOT_RUN','same_workload_speedup_measured':False,'physics_worker_and_native_unchanged_during_execution_recovery':True,'recovery_status':rec['status'] if rec else None,'next_node':nextnode,'budgets':b}
atomic_create(ROOT/'CLAIMS.json',json_bytes(claims))
print(json.dumps({'stop':a['stop'],'next_node':nextnode,'reports_written':3}))
