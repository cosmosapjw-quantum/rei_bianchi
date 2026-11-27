#!/usr/bin/env python3
"""Compose owner documents from final recorded evidence; no science execution."""
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import shutil

T = Path('/workspace/scratch/7fd51143e473/e13c10_research_20261012')
R = T / 'BASS_HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL_20261012_v1'


def read(rel): return json.loads((R / rel).read_bytes())
def pin(rel):
    p = R / rel
    return {'relative_path': rel, 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
def save(rel, obj):
    p = R / rel
    with p.open('x') as f:
        f.write(obj if isinstance(obj, str) else json.dumps(obj, indent=2, sort_keys=True))
        f.write('\n')


analysis = read('analysis/ACTUAL/LOCAL_ANALYSIS.json')
review = read('review/independent/EXEC01_FINAL/REVIEW_RESULTS.json')
decision = read('review/independent/INDEPENDENT_DECISION.json')
assert decision['decision'] == 'PROMOTE_SCOPED_LOCAL_SIGNED_CURVATURE_FIRST'
assert review['checks_failed'] == 0 and analysis['mechanical_acceptance']
assert pin('SOURCE_LOCK.json')['sha256'] == 'dab62d573a17d5333aa09369c1865b873a2c55d77efc3a88aeef872beeef4bbb'
shutil.copyfile(T/'delivery_tools/NCP_SCIENTIFIC_UTILITY_MEMO_KO.md', R/'analysis/NCP_SCIENTIFIC_UTILITY_MEMO_KO.md')
ph = analysis['selected_aggregate_summary']
batches = [read('evidence/' + name) for name in ['N32_PILOTS_COMMAND_RECEIPT.json', 'SAME_N_PILOTS_COMMAND_RECEIPT.json', 'REFINED_PILOTS_COMMAND_RECEIPT.json', 'REFINED_REMAINING_COMMAND_RECEIPT.json']]
batch_wall = sum(x['wall_seconds'] for x in batches)
selected_batch_wall = sum(x['wall_seconds'] for x in batches[2:])
selected_cpu = sum(x['cpu_seconds'] for x in analysis['selected_paths'])
node_rows = []
reason = {1:'HI, 저장된 최대 D 포함',1162:'HI+HeI',1976:'HI+HeI+HeII',1620:'HeII mask 전환, 3 segments',2344:'source OFF/OFF/ON, 3 segments'}
for x in analysis['selected_paths']:
    w = x['work']; g = x['P_H_summary']
    node_rows.append(f"| {x['node']} | {reason[x['node']]} | {w['N_first']} | {w['M_second']} | {float(g['P_final']['gain_percent_display']):.4f}% | {float(g['H_total_eV']['gain_percent_display']):.4f}% | {x['elapsed_seconds']:.4f} s |")
aggregate_rows = '\n'.join(f"| {q} | {ph[q]['baseline_width_display']} | {ph[q]['candidate_width_display']} | {float(ph[q]['gain_percent_display']):.10f}% |" for q in ['P_final','H_total_eV'])
next_question = 'Reduce the now-dominant signed second-integral rectangle enclosure using a rigorously derived coupled prefix/kernel rule and short local controls.'
dag = {
    'schema':'bass-he-e13c10-next-dag-v1',
    'completed':['E13C8_FULL_FINITE_CAPTURED_OFF','HE_E13C9_SIGNED_VOLTERRA_LOCAL01','HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL01'],
    'next_node':{'id':'HE_E13C11_SECOND_INTEGRAL_BOUND_LOCAL01','location':'HERE_LOCAL','status':'PROPOSED_NOT_RUN',
        'question':next_question,
        'motivation':'Selected remaining positive bound allocation: signed rectangle P98.8297170695%, H98.8338156793%; first curvature only about1.17%. This is not measured physical error.',
        'required_work':['Derive a valid enclosure for the coupled Volterra prefix and output kernel on fixed event-free cells, with explicit derivative/remainder assumptions.',
                         'Use independent closed-form controls for signs, zero, L=0, species cancellation, incoming uncertainty and events.',
                         'Fix a new bounded plan and meaningful raw-gain gate before executing the shortest discriminating local paths. Reuse identical completed components by source/input/N/P identity.',
                         'Preserve raw failures and obtain independent decision. Stop optional sweeps after the fixed local objective.',
                         'Evaluate an explicit downstream observable accuracy question before creating a full-population heavy work list.'],
        'restrictions':['No unproved fourth-derivative remainder from Jet2 alone.','No raw interval intersection, old-result fallback, tolerance relaxation, or precision/source/input/physics changes by default.','No replay of completed E13C7/E13C8/E13C9/E13C10 work units.']},
    'future_NCP_gate':{'status':'NO_CURRENT_HEAVY_WORK_CONTRACT','jobs':0,'new_work_units':[],
        'needed_before_launch':['An explicit full-population observable and absolute/relative accuracy objective with decision utility.',
                                'Locally validated method and source/input/work lock, genuinely unexecuted independent paths, preserved segment dependencies.',
                                'Measured per-unit CPU/wall/RSS and useful parallel work volume, with measured scaling where needed.',
                                'Provider/host/affinity/quota/NUMA observations and no unearned attestation.',
                                'Choose rank/thread layout from measurements; no BLAS/OpenMP oversubscription; preserve P60 semantics; retain at least20% RAM headroom.']},
    'physical_continuum_production_receiver':'HOLD'}
save('NEXT_DAG.json',dag)
save('NCP_ACTION.json',{'schema':'bass-he-e13c10-ncp-action-v1','action':'CLOSED_NO_NEW_HEAVY_TASK','new_NCP_work_units':[],
    'reason':'All fixed local tasks completed here; max path24.3629s and selected batches42.0999s. No specified new full-population accuracy objective or current heavy work list.',
    'next_local_node':dag['next_node']['id'],'existing_E13C7_heavy_return':'COMPLETE_PRESERVED_DO_NOT_RERUN','E13C10_full_population':'NOT_RUN',
    'transfer_restore':'Only when a receiver lacks the content-verified restored files; fresh output, one explicit invocation, preserve first failure, no automatic retry.'})
authority = ['SCIENTIFIC_CONTRACT.md','SOURCE_LOCK.json','WORK_PLAN.json','code/first_midpoint.py','code/first_path.py','code/run_path.py',
             'analysis/ACTUAL/LOCAL_ANALYSIS.json','analysis/ACTUAL/BOUND_ALLOCATION.json','analysis/ACTUAL/SELECTED_CANDIDATE.json',
             'review/independent/INDEPENDENT_DECISION.json','review/independent/INDEPENDENT_REVIEW_KO.md','review/independent/EXEC01_FINAL/REVIEW_RESULTS.json',
             'tests/MANUFACTURED/EXEC03_HALF_CELL/RECEIPT.json','analysis/NCP_SCIENTIFIC_UTILITY_MEMO_KO.md']
state = {'schema':'bass-he-e13c10-current-state-v1','updated_utc':datetime.now(timezone.utc).isoformat(),
         'node':'HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL01','status':'SCIENTIFIC_LOOP_COMPLETE','decision':decision['decision'],
         'scope':{'selected_nodes':[1,1162,1976,1620,2344],'segments':12,'raw_intervals':170,'nested':170,'nonincreasing':170,
                  'interval_precision':60,'N_first':{str(x['node']):x['work']['N_first'] for x in analysis['selected_paths']},
                  'M_second':{str(x['node']):x['work']['M_second'] for x in analysis['selected_paths']},'raw_intersections':0,'old_interval_fallbacks':0},
         'selected_weighted_widths':{q:{k:ph[q][k] for k in ['baseline_width_display','candidate_width_display','gain_percent_display']} for q in ph},
         'bound_allocation_percent':{q:x['percent'] for q,x in analysis['selected_bound_halfwidth_allocation'].items()},
         'validation':{'exact_polynomial_checks':207,'exact_polynomial_failures':0,'current_half_cell_manufactured_checks':993,
                       'current_half_cell_manufactured_failures':0,'current_half_cell_manufactured_executions':12,'current_half_cell_manufactured_calls':144,
                       'manufactured_history_three_distinct_revisions_checks':4224,'manufactured_history_executions':48,'manufactured_history_toy_calls':1200,
                       'independent_saved_arithmetic_checks':review['checks_passed'],'independent_saved_arithmetic_failures':0,
                       'independent_saved_arithmetic_elapsed_seconds':review['wall_seconds'],'reconstructed_ledger_checks':205,
                       'review_entire_manual_reading_wall_time':'NOT_MEASURED'},
         'resources':dict(analysis['resources'],actual_four_batch_wall_seconds_sum=batch_wall,selected_two_batch_wall_seconds_sum=selected_batch_wall,
                          selected_path_process_cpu_seconds_sum=selected_cpu,current_half_cell_manufactured_wall_seconds=read('tests/MANUFACTURED/EXEC03_HALF_CELL/RECEIPT.json')['wall_seconds']),
         'claim_ceiling':{'E13C8_full_finite':'UNCHANGED_PROMOTE_SCOPED_FULL_FINITE_CAPTURED_OFF',
                          'E13C9_selected_finite':'UNCHANGED_PROMOTE_SCOPED_LOCAL_SIGNED_VOLTERRA',
                          'E13C10_selected_finite':decision['decision'],'E13C10_full_population':'NOT_RUN',
                          'physical':'HOLD','continuum':'HOLD','production':'HOLD','receiver':'HOLD','provider_attestation':'NOT_ASSERTED','same_work_serial_speedup':'NOT_ESTABLISHED'},
         'new_NCP_work_units':[],'NCP_action':'CLOSED_NO_NEW_HEAVY_TASK','next_local_question':next_question,
         'authoritative_evidence':{rel:pin(rel) for rel in authority},
         'saved_status_policy':'Raw result/analysis pre-review pending statuses are preserved. The actual independent decision and this state govern scoped adoption.',
         'publication':'Actual backup ACK/readback, archive restore and draft PR identities are in the external delivery receipt after immutable package sealing.'}
save('CURRENT_STATE.json',state)

report = r'''# BASS_HE E13C10 — 첫 적분의 부호 있는 곡률 상계와 국소 채택

기록 일자: 2026-10-12 UTC. 현재 연구 노드: `HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL01`.

## 결과와 의미

끊긴 지점에서 실제 E13C9 백업과 다음 연구 노드를 복구한 뒤, 첫 적분의 중점 오차 상계를 개선하는 E13C10을 실행했다. **선택한 5개 captured OFF 경로, 12개 segment, 170개 raw 구간 모두 이전 E13C9 채택 구간에 포함되고 폭이 증가하지 않는다.** 실제 독립 판정은 **`PROMOTE_SCOPED_LOCAL_SIGNED_CURVATURE_FIRST`**다. 선택 경로의 양의 원래 가중치를 적용한 정확한 합산에서 P 구간 폭은 **97.7836860203%**, H 구간 폭은 **98.0689999175%** 감소했다.

이 수치는 광자량이나 가열량 자체가 그만큼 변했다는 뜻이 아니다. 동일한 고정 유한 문제의 값을 보증하는 **수치 포함 구간의 폭**이 줄었다. 전체 2,440개 경로의 개선율, 실제 해와의 측정 오차 또는 물리 정확도는 이번 결과에 포함되지 않는다. E13C8의 전체 유한 합산 채택과 E13C9의 국소 채택은 보존하며, E13C10 전체 경로 계산은 **NOT_RUN**, physical·continuum·production·receiver는 **HOLD**다.

근거: [실제 독립 결정](review/independent/INDEPENDENT_DECISION.json), [독립 검토서](review/independent/INDEPENDENT_REVIEW_KO.md), [정확한 가중 합산](analysis/ACTUAL/LOCAL_ANALYSIS.json), [선택 raw 결과의 identity](analysis/ACTUAL/SELECTED_CANDIDATE.json).

## 1. 실제 수치 결과

모든 경로의 interval precision은 P60이다. N은 첫 적분의 원래 격자이며, M은 유지한 E13C9 두 번째 보정 격자다. 새 중점값 평가는 하지 않았다.

| Node | 판별하는 경우 | N_first | M_second | P 폭 감소 | H 폭 감소 | 실제 경로 시간 |
|---:|---|---:|---:|---:|---:|---:|
''' + '\n'.join(node_rows) + r'''

| 선택 5개 경로의 가중합 | E13C9 구간 폭 | E13C10 구간 폭 | 감소율 |
|---|---:|---:|---:|
''' + aggregate_rows + r'''

이 표본은 HI/HeI/HeII 종과 mask/source event, serial carry의 구현 위험을 판별하도록 선택했다. 전체 분포를 대표하는 통계 표본이 아니다. P는 원래 photon/number 단위, H는 원래 eV 가중 단위를 유지했다.

![국소 구간 폭과 남은 상계 배분](figures/E13C10_LOCAL_WIDTHS.png)

## 2. 물리 문제를 유지하며 바꾼 수치 표현

원래 photon 방정식과 frozen 기준을 사용한다.

\[
P'=q-\Lambda P,\quad P_f'=q_f-\Lambda_fP_f,\quad
r=(q-q_f)-(\Lambda-\Lambda_f)P_f.
\]

E13C9에서 채택한 첫 변분과 부호 있는 두 번째 Volterra 보정, finite remainder는 그대로 둔다. 이번 변경은 첫 변분의 17개 적분량을 감싸는 수치 구간에만 있다. 정규화 좌표 \(x=u/h\)와 고정 event-free cell \([a,b]\), \(d=b-a=1/N\), \(m=(a+b)/2\)에 대해

\[
\int_a^b f(x)\,dx-d f(m)=\int_a^bK(s)f''(s)\,ds,
\quad
K(s)=\begin{cases}(s-a)^2/2,&a\le s\le m,\\(b-s)^2/2,&m\le s\le b.\end{cases}
\]

커널은 음이 아니고 전체 질량은 \(d^3/24\), 각 반 셀의 질량은 \(d^3/48\)이다. 원래 whole-cell Jet2가 실제 두 번째 도함수의 구간 \(D_{\rm whole}\)을 제공한다. 이번에 왼쪽 반 셀의 \(D_{\rm left}\)를 추가로 평가하면

\[
\int_0^h f(u/h)\,du\in Q_N+
\sum_j\frac{h}{48N^3}\left(D_{{\rm left},j}+D_{{\rm whole},j}\right).
\]

오른쪽 반 셀은 whole-cell의 부분집합이므로 그 부분의 도함수도 같은 whole-cell 구간으로 포함된다. 이 식은 양의 가중 커널을 갖는 두 적분을 직접 감싸며, 실패 구간과의 교집합이나 clipping을 사용하지 않는다. 곡률의 부호를 유지해 불필요한 대칭 반경을 줄인다. C²만 가정하며, 네 번째 도함수나 일반적인 3차 폭 수렴률을 주장하지 않는다.

원래 중점 합 \(Q_N\)은 동일 source·input·segment·N·P의 full RESULT SHA로 묶어 재사용했다. 먼저 실행했던 같은-N 두 경로의 whole-cell 곡률도 정확한 RESULT SHA와 cell 좌표를 검증해 재사용했다. 나머지 경로는 whole-cell와 left-half를 각각 한 번 평가했다. 중점 평가 0회는 실제 실행 기록으로 확인된다.

매 segment의 incoming center/radius는 새 carry로 전파한다. E13C9의 부호 있는 두 번째 적분 및

\[
(|G_k|+T_k)\eta+T_kDS,\qquad S=|c_{\rm new}|+\eta_{\rm new}+B_r
\]

를 새 incoming 값으로 계산한다. tail 계산에는 원래 input-independent fine-grid bounds를 재사용한다. signed energy seam, photon stitch, species 합산, cutoff와 binding energy 구분, 정확한 binary64 lift와 원래 에너지 변환은 유지했다. 새 gas 진화, source나 closure 변경은 없다.

근거: [고정 과학 계약](SCIENTIFIC_CONTRACT.md), [양의 커널 직접 유도와 대안](theory/THEORY_OPTIONS.md), [first_midpoint.py](code/first_midpoint.py), [최종 조립 diff](evidence/FINAL_FIRST_PATH_DERIVATION.diff), [diff의 역사 구분](evidence/DERIVATION_DIFF_STATUS.md).

## 3. 실패를 보존하고 원인에 맞춰 보완한 과정

최초 N32 두 경로는 계산 자체는 완료됐지만 raw admission을 통과하지 못했다. Node1은 12/34, node1976은 0/34 nested였다. 특히 node1의 H 폭은 기존의 약 2,253.74배여서, 거친 곡률 구간의 의존성 폭이 문제임을 확인했다. 폭이 좁아진 QN/QE도 기존 끝점을 넘을 수 있었다. 나머지 세 N32와 조건부 N64는 실행하지 않고 superseded로 기록했다.

다음 같은-N signed whole-cell 두 경로는 모든 폭이 줄었으나 node1은 33/34, node1976은 26/34 nested였다. Node1의 QN 끝점 초과는 약 2.72e−83이었다. Node1976에는 HeI 항과 새 carry 전파의 약 1.55e−9 old-width 상대 끝점 초과도 있었다. 작은 값이라는 이유로 허용 오차를 늘리지 않았다. 국소 first integral이 들어맞더라도 재중심화와 다음 segment 조립에서 포함 관계가 자동 보장되지는 않음을 확인했다.

반 셀의 양의 Peano 질량을 이용한 현재 보완 후에는 두 경로가 34/34를 통과했고, 나머지 세 경로도 첫 실행에서 모두 통과했다. 추가 해상도·정밀도 sweep은 하지 않았다. 과거 코드·lock·raw 결과와 첫 판단 기록은 그대로 보존했다. 이력의 실패 상태를 성공으로 덮어쓰지 않았다.

근거: [최초 N32 판단](evidence/FIRST_N32_RAW_ADMISSION_FINDING.json), [같은-N 끝점 판단](evidence/FIRST_SAME_N_RAW_ADMISSION_FINDING.json), [보존한 코드 revisions](evidence/SOURCE_REVISIONS), [최종 raw 선택](analysis/ACTUAL/SELECTED_CANDIDATE.json).

## 4. 독립성, 실제 검증과 한계

| 검증 범위 | 실제 실행과 결과 |
|---|---|
| 정확한 다항식 이론 통제 | 8개 다항식×5격자, 207 checks, 실패 0, 약 0.041초 |
| 최초 signed 구현 | 12 cases×2격자, 2,290 checks, 실패 0; 초기 revision의 증거 |
| cached midpoint 변경 | 12 cases, 941 checks, 실패 0; 해당 revision의 증거 |
| 현재 half-cell 변경 | 6 cases×fresh/cached parent, 993 checks, 실패 0; 0.4769초 |
| 현재 half-cell 실제 호출 | toy coefficient 144회=whole48+left96, midpoint0, 별도 cache setup0 |
| 실제 captured 결과 | 5개 경로·12 segments, 170/170 raw nested 및 nonincrease |
| 독립 Fraction 감사 | 413,507 checks, 실패 0, 9.5172초; science kernel import·호출 0 |

현재 제조 통제는 양·음 quadratic, 부호가 바뀌는 cubic, 정확한 zero, 종별 상쇄, L=0을 포함한다. P140 폐형식 oracle의 17개 출력이 구간에 포함되고, fresh/cache parent 방식이 동일한 endpoint를 생성하며 cache가 보존되는지 확인했다. 세 revision의 제조 이력을 합친 4,224 checks는 **모두 현재 소스를 실행한 수치가 아니다**. 현재 half-cell 코드에 직접 해당하는 것은 993 checks다.

후보와 제조 설계에 참여하지 않은 reviewer가 원래 17개 source pin, input·N·P·parent identity, 9,216개 cell의 split Peano 산술, midpoint 보존, 새 carry·tail·seam·가중치를 별도로 읽고 재구성했다. 170개 raw metric, 205개 보존식 재구성 검사, 양의 bound allocation이 정확히 일치했다. 검토의 실제 판정 파일이 채택 권한을 가지며, 그 전에 생성된 RESULT/분석의 PENDING 문자열은 역사 상태로 보존했다.

이 검증은 공유된 Python Decimal exp primitive나 원래 물리 계수 모델까지 독립적으로 증명하지 않는다. Jet2의 2차 도함수 convention과 원래 계수 구현은 source-bound 검토 대상이다. Python 문서는 exp의 반올림 및 Decimal 의미를 확인하는 참고이며, 이번 Peano 식의 증명은 직접 유도했다. 형식 증명기 인증 또는 물리 모형 검증으로 표시하지 않는다.

근거: [현재 제조 보고서](tests/MANUFACTURED/HALF_CELL_CONTROL_REPORT_KO.md), [실행 영수증](tests/MANUFACTURED/EXEC03_HALF_CELL/RECEIPT.json), [독립 원시 감사](review/independent/EXEC01_FINAL/REVIEW_RESULTS.json), [공식 문서와 source 근거](references/EXTERNAL_SOURCE_NOTES.md).

## 5. 실제 계산 비용과 NCP 경계

''' + f'''이번에 실행한 진단 포함 경로는 총 **9회**, 실제 계수 평가 **24,320회**다. 새 first-integral 계수 평가는 18,688회, 새 path 조립 중 second correction 평가는 5,632회다. 이전 전체 경로 work unit과 원래 first-variation quadrature를 재실행한 횟수는 0회다. 단, incoming center가 같게 유지된 일부 low-level second-correction 산술은 새 조립에서 결정적으로 반복될 수 있다.

네 실제 batch의 wall 합은 **{batch_wall:.4f}초**이며, 최종 다섯 경로를 수행한 두 batch는 **{selected_batch_wall:.4f}초**다. 이 수치는 연구 전체의 경과 시간이 아니다. 진단 포함 경로별 process CPU 합은 **125.5438초**, 최종 경로 CPU 합은 **{selected_cpu:.4f}초**다. 가장 긴 경로는 **24.3629초**, 경로 process의 개별 최대 RSS는 **173,412 KiB=169.35 MiB**다. 독립 감사의 별도 최대 RSS는 196,068 KiB다. 전체 동시 process memory peak와 CPU utilization은 측정하지 않았다.

실행 호스트는 `d48c07c99ee6`, CPython3.12.14, affinity0–8이다. provider attestation은 없다. 로컬 제한은 최대3 workers, 경로당120초·1GiB였고 실제 경로 모두 그 안에서 완료됐다. 다른 호스트·다른 workload 시간을 나눠 NCP speedup으로 표시하지 않는다.

''' + r'''따라서 **현재 새 NCP work unit은 0개**다. 64코어·128GB를 쓸 이유는 실제로 남아 있는 무거운 병렬 문제와 그 결과의 과학적 효용이어야 한다. 이번 국소 계산은 여기서 모두 마무리했다. 기존 2,331개 heavy return과 전체 2,440개 finite 합산도 보존하며 재실행하지 않았다.

기존 E13C8의 전체 유한 결과를 읽으면 P의 relative full interval width는 약 **1.07071908e−13**, H는 약 **5.76346954e−13**다. 이는 고정 captured 유한 목표의 수치 포함 폭이며 continuum 오차와 무관하다. 정확한 full observable·허용 폭·그 기준을 더 좁힐 필요성이 지정되지 않은 상태에서 이번 5개 경로의 개선율을 전체에 외삽해 heavy job을 만들지 않았다. 0에 가까운 ledger midpoint로 relative width를 계산해 큰 값을 얻는 것도 새 계산 필요성의 근거가 아니다.

향후 실제 중량 batch가 필요하면 source/input/work lock을 먼저 고정하고, 완료되지 않은 독립 path 단위만 편성해야 한다. path 안의 segment는 순서를 지켜 carry를 전달한다. rank×thread·BLAS/OpenMP 중첩·NUMA·affinity/quota·20% 이상 RAM 여유는 실제 자원 관측으로 결정한다. 64×1 등의 layout은 후보이며 측정 없이 최적이라고 확정하지 않는다. P60 구간 backend를 binary64로 바꾸는 것은 별개의 방법 변경이다.

근거: [NCP 행동](NCP_ACTION.json), [실제 비용 기록](analysis/ACTUAL/LOCAL_ANALYSIS.json), [기존 전체 결과와 NCP 효용 분석](analysis/NCP_SCIENTIFIC_UTILITY_MEMO_KO.md), [기존 HPC 정책](references/HPC_POLICY_KO.md).

## 6. 남은 수치 상계와 다음 연구 노드

| 선택 결과의 양의 반폭 배분 | P | H |
|---|---:|---:|
| 두 번째 signed rectangle 적분 및 carry | 98.8297170695% | 98.8338156793% |
| 첫 적분 곡률 구간 및 carry | 1.1702058174% | 1.1661477698% |
| finite Volterra tail 및 carry | 0.0000771131% | 0.0000365508% |
| 중점·기타 반올림 | 표시 정밀도에서 미미 | 표시 정밀도에서 미미 |

Fraction으로 각 반폭을 정확히 재구성한 **상계의 배분**이다. 실제 error attribution이 아니다. 첫 적분 상계를 줄이자는 E13C10의 목표는 달성했고, 같은 부분을 더 계산해 얻을 수 있는 현재 bound 감소는 약1.17%뿐이다.

다음 노드는 **`HE_E13C11_SECOND_INTEGRAL_BOUND_LOCAL01`**로 제안한다. location은 **HERE_LOCAL**, status는 **PROPOSED_NOT_RUN**이다. 새로 지배적인 coupled prefix/kernel의 두 번째 적분 상계를 엄밀한 국소 규칙으로 줄일 수 있는지 유도하고, 별도 closed-form 통제와 가장 짧은 판별 경로부터 실행해야 한다. 이번 세션에서 다음 노드를 실행한 것으로 표시하지 않는다. 실제 full-population 정확도 질문과 무거운 독립 work list가 생기기 전에는 NCP queue를 열지 않는다.

근거: [정확한 반폭 분해](analysis/ACTUAL/BOUND_ALLOCATION.json), [다음 DAG](NEXT_DAG.json).

## 7. 복구, 백업과 이어서 작업하는 방법

이번 재개에서 E13C9 COMPLETE의 bytes/SHA와 nested 원본 source/input·완료 heavy return을 확인하고 실제 restore를 한 번 수행했다. 9.0502초에 PASS_COMPLETE_RESTORE였다. 최초 로컬 expected SHA 입력의 전사 오류는 canonical 원본값으로 바로잡았으며, 그때 restore나 과학 실행은 아직 들어가지 않았다. 최초 오류와 모든 수치 실패는 보존했다. 과거 `.bin` 접미사로 실패한 NCP 전송 기록과 이번 완료 기록을 혼동하지 않는다.

새 COMPLETE에는 이번 코드·raw cell 결과·실패 이력·분석·독립 판정, 고정된 E13C9 COMPLETE/kit를 함께 넣는다. 그 predecessor에는 E13C8과 E13C7 source/input·실제 NCP 반환까지 포함돼 있으므로 추가 입력 첨부가 필요 없다. Recovery helper는 조각의 실제 bytes/SHA를 사용하고 Drive 파일명에 `.bin`이 추가되는 경우도 처리한다. 새 output만 사용하며 첫 실패를 남기고 자동 재시도하지 않는다.

새 COMPLETE build, 실제 restore, recovery kit, 원격 backup ACK/readback과 additive draft PR은 이 불변 package를 봉인한 뒤 외부 delivery receipt로 연결한다. 업로드 확인과 실제 archive-chain restore는 다른 증거이며, 어느 것도 NCP physics 실행 또는 provider attestation을 뜻하지 않는다. 승인된 Git 변경은 새 branch의 draft PR이며 merge나 force push는 없다.

현재 상태는 [CURRENT_STATE.json](CURRENT_STATE.json), 수신 작업은 [내부 NCP 인계문](NCP_HANDOFF_INTERNAL_KO.md), 경로와 실행 정책은 [REPRODUCIBILITY.md](REPRODUCIBILITY.md)를 따른다. 외부 최종 handoff에 실제 archive/kit SHA와 Drive·Dropbox 위치가 들어간다. raw RESULT의 PENDING 문구를 제거하기 위해 과학 결과를 다시 쓰거나 실행하지 않는다.
'''
save('REPORT_KO.md',report)

internal = '''# BASS_HE E13C10 — NCP local Codex 내부 인계문

사용자의 지속 지시: 짧은 이론·코딩·control·pilot는 ChatGPT 쪽에서 수행하고, 실제로 길고 무거우며 유용하게 병렬화되는 계산만 NCP64코어/128GB로 전달한다. 이번 E13C10은 해당 국소 작업을 완료했다.

## 현재 상태

- HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL01: PROMOTE_SCOPED_LOCAL_SIGNED_CURVATURE_FIRST.
- 5개 captured OFF 경로,12segments,170/170 raw nested 및 nonincrease, P60.
- 선택 가중 구간 폭 감소 P97.7836860203%,H98.0689999175%; full-population 개선율 아님.
- Source lock SHA256: dab62d573a17d5333aa09369c1865b873a2c55d77efc3a88aeef872beeef4bbb.
- 새 NCP work units: 빈 배열. NCP_ACTION=CLOSED_NO_NEW_HEAVY_TASK.
- E13C7 완료 heavy work, E13C8 full-finite, E13C9/E13C10 selected work는 닫힌 작업이다. 재실행하지 않는다.
- E13C10 full-population NOT_RUN; physical/continuum/production/receiver HOLD.

## 인수 절차

1. 외부 최종 handoff의 actual file ID/bytes/SHA로 승인된 backup에서 이 kit와 COMPLETE 또는 모든 조각을 가져온다. 추가 사용자 파일 첨부는 필요 없다. 기대 SHA는 final handoff의 고정값이어야 한다.
2. 동일 content identity로 완료된 복구가 현재 호스트에 있으면 그 receipt와 package state를 확인해 재사용한다. 이미 완료한 복구나 수치 검증을 반복할 필요가 없다.
3. 복구가 없으면 versioned restore_transfer_e13c10.py와 외부 transfer manifest를 사용해 fresh output에서 한 번만 --hydrate 한다. 조각 파일명의 .bin을 예상 이름으로 바꾸거나 이름만으로 연결하지 않는다. helper가 실제 bytes/SHA로 선택한다. 첫 실패를 보존하고 자동 재시도하지 않는다.
4. 새 package는 output/package/BASS_HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL_20261012_v1, predecessor는 output/runtime/E13C9다. CURRENT_STATE.json 및 실제 독립 decision의 identity를 확인한다.
5. 현재 heavy queue가 비어 있으므로 MPI/budget/physics/full-first2/N512/native/gas/ODE/full-population 작업을 시작하지 않는다. 후보 코드를 수정하거나 과거 PENDING 상태를 승격하기 위해 원시 결과를 다시 쓰지 않는다.
6. 수신 측 작업을 수행했다면 새 receipt에 실제 호스트·Python·affinity·관측 가능한 quota/memory/provider 정보를 적는다. provider attestation이 없으면 NOT_ASSERTED로 둔다. 다운로드 bytes/SHA, 복구 입력과 output, invocation 수와 오류를 기록한다. 업로드하는 경우 승인된 기존 폴더에 additive로 저장하고 ACK와 이름·크기 readback을 구분해서 남긴다.

## 다음 연구와 새 heavy gate

다음 노드는 HE_E13C11_SECOND_INTEGRAL_BOUND_LOCAL01, HERE_LOCAL, PROPOSED_NOT_RUN이다. 현재 선택 반폭에서 signed rectangle이 약98.83%를 차지한다. coupled prefix/kernel의 수학적 상계와 독립 짧은 통제부터 ChatGPT 쪽에서 진행한다.

실제로 필요한 full observable와 정확도 목표, 국소 채택 방법, 아직 계산하지 않은 독립 work list, 실제 비용·병렬효용 근거가 생기면 별도 고정 handoff를 만든다. source/input/P60 의미를 유지하고 path 안의 segment는 serial이다. rank×thread, BLAS/OpenMP 중첩 방지, NUMA/affinity/quota와20% RAM 여유는 측정으로 정한다. 현재 문서는 향후 계산 범위를 임의로 확장하라는 지시가 아니다.

완료 상태와 실제 invocation만 반환한다. 수치 계산을 하지 않았다면 physics NOT_RUN, invocation0이라고 명시한다. 복구 PASS를 물리 실행 PASS로 표시하지 않는다.
'''
save('NCP_HANDOFF_INTERNAL_KO.md',internal)

save('REPRODUCIBILITY.md',r'''# Reproducibility and preserved work

The authoritative scientific outcome is CURRENT_STATE.json plus the non-author INDEPENDENT_DECISION. Raw candidate/analysis files retain their historical pending statuses. Source/inputs/P60 and recorded failures are immutable.

The external final handoff binds actual COMPLETE/kit/transfer-manifest names, bytes and SHA256, with actual remote backup locations. The complete package embeds E13C9_COMPLETE.zip and E13C9_RECOVERY_KIT.zip; they hydrate E13C8 and then E13C7 source/input and completed heavy return. No additional user attachments are required.

From the small kit, restore an unavailable dataset once:

```bash
python3 -B restore_transfer_e13c10.py \
  --manifest BASS_HE_E13C10_TRANSFER_MANIFEST.json \
  --manifest-sha256 EXPECTED_FROM_FINAL_HANDOFF \
  --parts-dir ABSOLUTE_DOWNLOADED_PARTS_DIR \
  --output-dir ABSOLUTE_FRESH_RESTORE_DIR --hydrate
```

`--archive ABSOLUTE_COMPLETE_ZIP` is the alternative to `--parts-dir`; use one mode. The helper selects parts by actual bytes/SHA and tolerates the downloaded name suffix. Do not derive the expected SHA from the untrusted input itself. Do not rerun a successful restore merely to test the alternate transport mode. Preserve the first failed output and receipts; no automatic retry.

Restored paths below the fresh output:

| Item | Relative path |
|---|---|
| E13C10 package | package/BASS_HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL_20261012_v1 |
| E13C9 restore root | runtime/E13C9 |
| E13C9 package | runtime/E13C9/package/BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1 |
| E13C8 restore root | runtime/E13C9/runtime/E13C8 |
| E13C7 original inputs | runtime/E13C9/runtime/E13C8/runtime/E13C7_INPUT |
| Completed heavy return | runtime/E13C9/runtime/E13C8/runtime/E13C7_NCP_RETURN |

The saved-source `run_path.py --package ROOT10 --restored-e13c9 RESTORED9 --node NODE --N N --output-dir FRESH` describes the captured executions in WORK_PLAN. They have already completed and must not be rerun as part of transfer verification. All argv, logs, first failures and raw RESULT are retained under evidence and runs.

`analyze_local.py --package ROOT10 --restored-e13c9 RESTORED9 --output-dir FRESH` and the reviewer script consume saved data. Their already completed receipts provide the evidence; do not repeat them to keep a host busy. A future changed analysis or method must have a concrete affected dependency and fresh bounded outputs.

The original selected input manifest has historical absolute locators. SELECTED_INPUTS_USAGE.md explains which restore-relative fields are authoritative. Both new analyzer and wrapper take explicit restored roots. Source-lock hashes define scientific code; PACKAGE_MANIFEST pins all final documents, source, plots, data and dependency archives.

Future NCP work is empty. Existing full/selected work stays closed. Refer to NEXT_DAG.json and NCP_ACTION.json for the next unexecuted local question and heavy gate. Verification of backup bytes and archive hydration is not provider attestation or new physics execution.
''')
save('README.md','''# BASS_HE E13C10 local first-integral enclosure

Actual decision: PROMOTE_SCOPED_LOCAL_SIGNED_CURVATURE_FIRST. Five selected captured OFF paths,12segments,170/170 raw intervals nested. P/H selected width reductions97.783686%/98.069000%. Full E13C10 NOT_RUN; physical/continuum/production/receiver HOLD; new NCP work units0.

Read REPORT_KO.md, CURRENT_STATE.json, review/independent/INDEPENDENT_DECISION.json and NEXT_DAG.json. Source/input/cell caches are identity-bound. Original first quadrature and completed heavy workloads were not replayed. Failed initialN32 and sameN revisions/results remain available.

Complete raw cells and dependency archives belong to the full backup. The external Git projection index states exactly which large raw files are omitted from the review projection and binds them by bytes/SHA256. Package manifest and full backup are authoritative for those data. NCP_HANDOFF_INTERNAL_KO.md and REPRODUCIBILITY.md describe the self-contained recovery chain.
''')
(R/'state/RESEARCH_STATE.md').write_text(f'''# E13C10 research state

MODEL: GPT-6 Astra Pro from trusted host metadata; actual GPT6Astra v4.0.0 research/coding harnesses restored, SHA-checked and read. No model switch or model-performance claim.

CURRENT_PHASE: SCIENTIFIC_LOOP_COMPLETE; final additive delivery follows.
CURRENT_NODE: HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL01.
DECISION: {decision['decision']} from the actual non-author reviewer.
RESULT: five selected paths,12segments,170/170 nested and nonincreasing; P/H width gains97.7836860203%/98.0689999175%.

Initial N32 and same-N endpoint failures are preserved. Final LEFT_HALF_REFINED_WITH_PARENT_CACHE code passed direct manufactured controls and the independent413,507-check saved-arithmetic audit. Current source lock is {pin('SOURCE_LOCK.json')['sha256']}.

NEXT_NODE: HE_E13C11_SECOND_INTEGRAL_BOUND_LOCAL01, HERE_LOCAL, PROPOSED_NOT_RUN. Second signed rectangle now contributes approximately98.83% of selected positive halfwidth bounds.

New NCP jobs0; E13C10 full population NOT_RUN; physical/continuum/production/receiver HOLD. Existing E13C8 full finite and E13C9 selected admissions unchanged. Original completed heavy work is closed. Final actual backup IDs, hashes, restore receipts and draft PR will be recorded externally after package sealing.
''')
save('evidence/OWNER_COMPOSITION_RECEIPT.json',{'schema':'bass-he-e13c10-owner-composition-v1','created_utc':datetime.now(timezone.utc).isoformat(),
    'composer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scientific_invocations':0,
    'independent_decision':pin('review/independent/INDEPENDENT_DECISION.json'),'analysis':pin('analysis/ACTUAL/LOCAL_ANALYSIS.json'),
    'state':pin('CURRENT_STATE.json'),'report':pin('REPORT_KO.md'),'next_DAG':pin('NEXT_DAG.json'),'source_lock':pin('SOURCE_LOCK.json')})
print(json.dumps({'status':'COMPOSED_FROM_ACTUAL_INDEPENDENT_ADMISSION','report':pin('REPORT_KO.md'),'state':pin('CURRENT_STATE.json'),
                  'batch_wall_seconds':batch_wall,'selected_batch_wall_seconds':selected_batch_wall,'new_NCP_work_units':[]},indent=2))
