# B1 독립 최종 판정

**판정: `PROMOTE_SCOPED_PYTHON`. 원래 Rust/native 연결은 `HOLD_RUNTIME_ENVIRONMENT`를 유지한다.**

검토자는 `/root/b1_decision_review`이며 이번 후보 구현과 검증 설계에 참여하지 않았다. 고정 개발계획, 실행 계약, 수송·투영·충돌 코드, 독립 oracle, 13개 실행의 저장 결과와 영수증, 수치 평가와 분석 코드, 최종 보고서와 그림을 읽었다. 기존 저장 배열을 재집계했으며 새 수송·충돌·재이온화 ODE·NCP 실행은 하지 않았다. 작성한 파일은 이 검토문과 `DECISION.json`뿐이다. 근거 파일의 byte identity는 [판정 JSON](DECISION.json)에 보존한다.

## 채택 범위

채택하는 것은 **고정된 16,384개 reduced-history 셀, 등방 Planck 초기 test radiation, 초기 이후 방출 0, cold elastic Thomson, 초기 s/H=+0.1인 LRS Bianchi I, 평균 부피 z20→4**라는 조건의 실제 Python 결과다. 기준 격자는 시간128, μ24×φ8, 에너지263이며, 33개 저장 시각의 0.1≤y≤10에 있는96개 에너지를 분석했다. 이 유한 입력·근사 아래의 q2, 같은 기하의 전자 이력 차이, 적도 선형 편광에 대한 계산 결과를 다음 연구의 기준으로 사용할 수 있다.

기존 Python 원문을 실제로 호출했음은 구현 검증 범위에 포함된다. 반면 Rust C ABI와 source가 준비됐다는 사실은 실행 근거가 아니다. Rust compiler/prebuilt library 미확보 기록과 native 호출0을 확인했으므로 Python–Rust parity 및 PR27의 원래 native 연결 완료는 채택하지 않는다. 이 구분은 [실행 계약](../SCIENTIFIC_CONTRACT.md), [보고서](../REPORT_KO.md), [NCP handoff](../NCP_LOCAL_CODEX_HANDOFF_KO.md)에 명시돼 있다.

## 물리·구현 연결

- LRS backward map의 지수 부호는 a⊥=a exp(−b), a∥=a exp(2b)에서 보존되는 공간 공변 운동량과 맞는다. Occupation에는 추가 solid-angle Jacobian이나 redshift 진폭을 곱하지 않았으며, meridional screen의 회전0은 선언된 축대칭 조건에서 정합적이다.
- y=(a/a_i)E/(kBTγ,i)는 고정 시각에서 모든 방향에 공통인 물리 에너지에 대응한다. Thomson이 방향을 섞을 때 비등방 covariant-momentum slice를 그대로 사용하지 않았다.
- 원 producer의 tau 증분은 midpoint nΣ/H에 capped Q의 셀 적분을 곱한 값이다. F→B에 H_F(mid)/H_B(mid)를 곱하는 변환은 이 frozen-cell 표현을 보존한다. 원 N4의 셀 평균을 순간 밀도로 옮기는 경로와 다르며 기존 ODE를 재실행하지 않았다.
- B/M과 B_F/M_F의 시계·전자 이력 표현이 각각 같고, B/B_F의 기하와 source가 같다. 따라서 geometry 반응과 history 반응의 차이 정의가 실제 코드의 case 구성과 일치한다.
- 원래 Python kernel을 각 physical-energy slice에서 호출하고, 그 전후의 적분 보존과 U/V·방위각 잔차를 확인한 뒤 축대칭 표현으로 환원한다. 양의 occupation을 임의 clipping으로 만들어내는 경로는 발견하지 않았다.

이 항목들은 소스의 의미와 직접 유도에 대한 확인이다. 원자 입력 또는 전체 재이온화 모델에 대한 새로운 물리적 채택은 아니다. [입력 투영 근거](../source_notes/HISTORY_PROJECTION_VALIDATION.json) · [독립 이론 노트](B1_THEORY_ORACLE_KO.md)

## 실제 결과와 수치 판정

z=4,y=1에서 q2(B)=−0.0364635999884, q2(B0)=−0.0375267811314이며, 산란은 사중극의 절댓값을 약2.83% 줄였다. 적도 pL(B)=0.000808320304873이고 같은 기하의 전자 이력 차이는 δhist q2=−2.46431894099e−7이다. 양의 전단에서 q2<0, Thomson에 의해 Q_S>0이 생성되는 부호가 독립 저차 oracle과 맞는다. 이 두 처방 이력에서 얻은 작은 차이를 전체 천체물리 불확실성 또는 관측 가능한 신호로 해석하지 않는다.

저장된 모든 final_screen에서 q2와 Ibar를 다시 계산했을 때 저장값과 차이는0이었다. 13개 run의 source/input/output identity, stage 수, 실제 에너지 slice 호출 수가 각 영수증과 일치했다. 이 확인은 실제 호출 및 export의 정합성에 관한 것이고 hash 자체를 과학적 정확도 근거로 사용한 것은 아니다.

| 확인 | 최대 관측값과 해석 |
|---|---|
| F/M/M_F의 q2 null | 2.68551e−15; 절대 null |
| F/M/M_F의 적도 pL null | 2.92911e−14; 절대 null |
| B0 pL null | 4.35607e−14; 비물리 신호로 승격하지 않음 |
| 충돌 intensity 적분 보존 | 상대8.77076e−15 |
| 환원 전 U/I, V/I | 3.90450e−16, 6.55554e−17 |
| 모든 실행의 최소 occupation | 1.90187e−73>0 |
| 실제 저장 B 상태의 충돌 대 독립 dense-matrix expm | 상대1.77636e−15 |
| B0 exact one-shot 대 전체33×96점 | q2 절대1.22607e−7, Ibar 상대8.66077e−7 |

독립 충돌 oracle은 동일한 물리 Thomson 핵과 quadrature를 공유하지만, 후보의 packing·고유공간 분해·three-term 계산 대신 직접 축대칭 moment 행렬과 expm을 사용한다. B0의 해석적 검사는 특성선 부호·스펙트럼 수송·절대 이산화 오차를 확인하며, 그 자체가 작은 paired history 반응의 오차를 제한하지는 않는다. [실제 oracle 비교](B1_ACTUAL_ORACLE_COMPARISON.json)

시간128→256, μ24→48, 기본 에너지257→513의 개별 refinement에서 **paired history 반응 자체**를 비교했다. 본 검토자는 미리 고정된6개 보고 에너지의 모든 비초기 시점을 별도로 재집계해 같은 결론을 확인했고, 전체96개 energy 판정은 분석 코드의 공통 좌표 대응·차이식·null 처리와 함께 읽었다. 세 관측 변화의 절댓값 합에 네 항 비교의 경험적 null floor를 더한 척도/반응비는3072개 비초기점에서 최대 q2 **1.07854%**, 적도 pL **1.19429%**다. 모두 사전에 정한10% 탐색 기준을 충족한다. 마지막 시각의 최대값은 각각 **0.000488259%**, **0.00319509%**다. 초기점은 상대 오차나 검출 판정을 만들지 않고 absolute NULL로 유지한다.

이 수치는 **관측된 수치 민감도**이며 rigorous enclosure, continuum convergence proof, 통계적 신뢰구간, 전체 물리 오차 상계가 아니다. 비교된 두 history 외의 source·closure·열적 에너지 재분배가 이 작은 반응에 미치는 영향은 미평가다. [수치 평가](../analysis/B1_NUMERICAL_ASSESSMENT.json)

## 보고·그림·실행 범위

최종 보고서의 수치 표와 근사·미실행 구분이 저장 증거와 맞는다. PNG와 plotting source를 읽어 공통 energy 축, 평균 redshift 축, 편광 백분율 변환, history 차이 정의가 정합적인 것을 확인했다. 그림(d)은 세 refinement 변화의 합만 표시하고, 수치 판정은 여기에 null floor를 더한다. 그림은 이를 경험적 민감도로 표시하며 관측 CMB Cℓ 또는 observer-tail 결과로 부르지 않는다.

기존 broad benchmark domain [−8,5]의 사용은 pinned test_q7b_modeb.py에 실제로 존재한다. planck_state 함수의 기본 [−6,4]와 구분한 보고서 표현을 수용한다. 이는 문서 provenance 확인이며 과학 실행을 다시 열 이유가 아니다.

실제 수송은 pilot1개와 campaign12개다. campaign wall time55.2247초, pilot 포함 CPU 합149.8259초, 단일 process peak RSS92132 KiB의 관측이 있으므로 현재 결과를 위해 새64코어 NCP 작업을 만들 근거가 없다. native compiler 확보만을 별도 무거운 과학 작업으로 바꾸지 않는 handoff도 요청된 계산 분담과 맞는다.

## 종료 결정

이 scoped Python benchmark에 대해 추가 blocking finding은 없다. 같은 범위의 불변 입력·완료 계산을 재실행하거나 더 정밀화하는 작업은 종료한다. E13C11은 대기, 새 NCP work list는[]로 유지한다.

원래 native gate는 환경상 **HOLD**, Python–Rust parity는 **NOT_RUN**이다. 관측 mapping, ionizing-spectrum/gas feedback, production 저장소 통합과 원 producer의 continuum 정확도는 이번 PROMOTE에 포함되지 않는다. 다음 단계는 필요할 때 별도의 관측량·입력·성공조건을 정해 시작하며, 이 검토를 재귀적으로 검토하는 루프를 만들지 않는다.
