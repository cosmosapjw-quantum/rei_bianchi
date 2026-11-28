# NCP scientific utility memo — 기존 전체 유한 결과에 근거한 읽기 전용 gate 분석

## 1. 결론과 역할

**현재 제공된 근거에서는 새 전체 NCP 실행을 열 과학적 accuracy objective가 명시되지 않았다.** 기존 E13C8은 2,440개 경로 전체의 captured OFF 유한 target을 이미 채택했고, 아래에서 읽은 P/heat의 상대 전체 구간 폭은 각각 약 1.07e-13과 5.76e-13이다. E13C10의 새 방법은 선택한 5개 경로·12개 segment에 대한 국소 방법 연구다. 새 방법으로 전체 2,440개 경로를 계산한 결과는 `NOT_RUN`이며, 그 사실은 기존 E13C8 전체 결과의 완료 상태를 바꾸지 않는다. [S1–S4, S6]

따라서 전체 NCP 실행 gate의 첫 일은 **어떤 observable의 어떤 판단이 현재 enclosure 때문에 막혀 있는지**를 고정하는 것이다. 이 표의 작은 폭만 보고 모든 연구 목적이 이미 충족됐다고 선언하지도 않고, 64코어·128 GiB를 점유하기 위해 새 work list를 만들지도 않는다. 이 메모는 원본 파일을 읽은 기여자의 분석이며 최종 과학 판정, 정책 변경, 실행 허가, NEXT_DAG 수정이 아니다.

실제로 한 일은 저장된 JSON/정의 코드 읽기, 저장된 display 필드 전사, 작은 source 파일의 SHA 확인 및 이 메모 작성이다. `analyze_finite_observables.py`, 전체 Fraction reduction, coefficient 평가, path integration, MPI/NCP 실행을 호출하지 않았다. 외부 파일 업로드·변경도 없다.

## 2. 수치의 정확한 의미

이하 숫자는 `FINITE_OBSERVABLES.json`의 `midpoint_display`, `width_display`, `relative_full_width_display`를 **문자열 그대로** 옮겼다. 원본에는 정확한 Fraction 형식의 `lo`, `hi`, `width`도 있다. 원래 `report` 함수의 정의는

\[
m=(L+U)/2,\qquad w=U-L,\qquad
r_{\mathrm{full}}=w/|m|,\qquad
r_{\mathrm{half}}=w/(2|m|)
\]

다. display 함수는 Decimal precision 24로 표시한다. 따라서 아래 표시 문자열은 exact rational 그 자체도, 외측 방향 반올림된 새로운 경계도 아니다. 매우 가까운 threshold를 엄밀하게 비교할 때는 원본 Fraction endpoints를 사용해야 한다. Midpoint는 선택한 enclosure의 중심이며 독립적으로 측정한 정확한 해·물리 참값·통계 추정치가 아니다. [S1, S5]

모든 값은 동일한 finite weighted OFF captured first-two-step conditional target에 속한다. Number 계열은 기존 weighted photon/absorption-number 규약, `_eV` 계열은 기존 weighted eV 규약을 따른다. 이는 한 광자의 에너지를 새로 정의한 표가 아니다. 입력 realification, weight와 cutoff/binding-energy 구분은 바꾸지 않았다. [S1, S5, S6]

### 핵심 P 및 total heat

| Observable | 저장된 midpoint | 저장된 전체 폭 | 상대 전체 폭 | 상대 반폭 |
|---|---:|---:|---:|---:|
| `P_final` | `0.0000154783131598314069968765` | `1.65729252199014787706672E-18` | `1.07071907957714395512300E-13` | `5.35359539788571977561502E-14` |
| `H_total_eV` | `0.0000159884332091292421056850` | `9.21488478110373816809060E-18` | `5.76346954111934325567850E-13` | `2.88173477055967162783925E-13` |

P와 H의 midpoint 주변 수치 enclosure를 상대 오차 budget으로 사용할 때는 상대 **반폭**을 기준으로 삼는 경우와 전체 폭을 기준으로 삼는 경우를 구분해야 한다. 둘은 정확히 factor 2가 다르다. 연구 objective가 어느 정의를 쓰는지 먼저 명시해야 한다. 위 폭은 기존 수치 enclosure 폭이며 physical error bar가 아니다. [S1, S5]

### 기존 17개 전체 finite observables

| Observable | 저장된 midpoint | 저장된 전체 폭 | 상대 전체 폭 |
|---|---:|---:|---:|
| `P_final` | `0.0000154783131598314069968765` | `1.65729252199014787706672E-18` | `1.07071907957714395512300E-13` |
| `A_total` | `0.00000291906407881140009266868` | `1.91765109369698741843720E-18` | `6.56940389769664359283138E-13` |
| `A_HI` | `0.00000290473216439928662341427` | `1.87755892686031250059515E-18` | `6.46379363258299317401396E-13` |
| `A_HeI` | `1.34118110109448815920822E-8` | `6.92078880523010714253772E-21` | `5.16021945103633510378466E-13` |
| `A_HeII` | `9.20103401168587662329700E-10` | `3.31713780314448106995082E-20` | `3.60517937324382556774875E-11` |
| `B_total_eV` | `0.0000558680749570918682268373` | `3.67125104619231804332541E-17` | `6.57128610393670113744584E-13` |
| `B_HI_eV` | `0.0000553297334065712138429982` | `3.42465231724026986523490E-17` | `6.18953337814843400469559E-13` |
| `B_HeI_eV` | `4.76544805149224274187547E-7` | `2.40608671628646598458426E-19` | `5.04902517095539184000502E-13` |
| `B_HeII_eV` | `6.17967453714301096515540E-8` | `2.22537861789183518244668E-18` | `3.60112592421521426968941E-11` |
| `H_total_eV` | `0.0000159884332091292421056850` | `9.21488478110373816809060E-18` | `5.76346954111934325567850E-13` |
| `H_HI_eV` | `0.0000158299230393366786158834` | `8.72416222895970319253568E-18` | `5.51118423461727191568108E-13` |
| `H_HeI_eV` | `1.46783390481109304239960E-7` | `7.04552294187612737770840E-20` | `4.79994563334662207843688E-13` |
| `H_HeII_eV` | `1.17267793114541855616635E-8` | `4.20267322725273701777831E-19` | `3.58382563160181298651797E-11` |
| `QN` | `0.0000183973772386428070895451` | `2.53343454648943537061580E-24` | `1.37706288979500719839771E-19` |
| `QE_eV` | `0.000580540899699114028128300` | `1.57525946718079247390554E-23` | `2.71343408879068938436745E-20` |
| `Z_eV` | `2.82042481489454077875111E-10` | `7.02482853047576566490728E-23` | `2.49069873920338231540813E-13` |
| `anchor` | `8.17208712135956637114193E-22` | `1.21160991421870463378814E-33` | `1.48261991854185300895895E-12` |

특히 HeII의 상대 전체 폭은 absorption·energy·heat에서 약 3.6e-11로, P/total heat의 상대 폭과 다르다. 작은 total width를 모든 종별 observable의 상대 정밀도로 대체할 수 없다. 반대로 HeII의 큰 상대 폭을 total observable 전체의 절대 불확실도로 대체할 수도 없다. 필요한 판별 대상이 total인지 특정 종인지가 NCP 필요성의 일부다. [S1]

### 기존 파생 에너지

| Observable | 저장된 midpoint | 저장된 전체 폭 | 상대 전체 폭 |
|---|---:|---:|---:|
| `derived_final_energy_stock_eV` | `0.000524672542699540671264593` | `3.17188966558978326844994E-17` | `6.04546532827847963615978E-14` |
| `derived_threshold_energy_eV` | `0.0000398796417479626261211523` | `2.75071384891982317593824E-17` | `6.89753901578203579055249E-13` |

첫 행의 final energy stock은 저장된 captured terminal energy와 기존 full correction을 연결한 값이다. Threshold energy는 기존 species absorption과 고정 binding energy의 유한 합이다. 이 분석을 다시 계산하지 않았다. [S1, S5]

### 기존 finite ratios

| Ratio | 저장된 midpoint | 저장된 전체 폭 | 상대 전체 폭 |
|---|---:|---:|---:|
| `remaining_photons_per_injected_photon` | `0.841332596437711445878701` | `9.00832021843931631732470E-14` | `1.07072045664003375013020E-13` |
| `absorptions_per_injected_photon` | `0.158667403562288554121299` | `1.04235047789449800552151E-13` | `6.56940527475953338783858E-13` |
| `absorbed_energy_per_injected_energy` | `0.0962345202311283931488499` | `6.32384591626432113825914E-14` | `6.57128637528011001651478E-13` |
| `heat_per_injected_energy` | `0.0275405802027313085880673` | `1.58729302616151199275579E-14` | `5.76346981246275213474744E-13` |
| `threshold_energy_per_injected_energy` | `0.0686939400283970845607826` | `4.73819150133308075006116E-14` | `6.89753928712544466962143E-13` |

이 ratios는 양의 분모를 가진 저장 구간의 유한 비율이다. 예를 들어 remaining/injected number가 약 0.84133, absorption/injected number가 약 0.15867, heat/injected energy가 약 0.02754라는 **고정 finite target의 분배**는 이미 좁은 구간으로 기술되어 있다. 이를 continuum efficiency 또는 일반적인 physical efficiency로 승격하지 않는다. Source의 scope 필드도 그 구분을 명시한다. [S1, S5]

## 3. 기존 폭으로 무엇을 분별할 수 있는가

### 이미 가능한 finite 판단

P, species absorption, heat와 표의 주된 양의 observables는 원본 `lo`가 양수다. 따라서 같은 고정 finite target 안에서 그 양들이 0인가 하는 질문은 이미 구간으로 구분된다. Finite number/energy 분배 비율도 위 값 주변의 좁은 범위로 제한된다. 이 정도의 목적만을 위해 전체 경로를 새 방법으로 재실행할 이유는 이 자료에서 나타나지 않는다. [S1]

일반적으로 어떤 exact scalar threshold T에 대해 기존 구간의 `U < T` 또는 `L > T`가 성립하면 그 threshold의 어느 쪽인지는 이미 결정된다. 추가 numerical refinement가 결과를 바꿀 수 있는 경우는 threshold가 구간 안에 걸리거나, 요구한 폭 조건을 아직 만족하지 못하는 경우다. 두 예측 interval을 비교할 때도 한쪽 width만 보면 안 된다. 각각 중심 m1, m2와 반폭 r1, r2이면 `|m1-m2| > r1+r2`가 엄밀한 비겹침을 보장하는 충분조건이다. 이는 구간의 직접 성질이며 새 물리 계산 결과가 아니다.

다음 예시는 **임의의 user objective로 채택하지 않는 조건부 설명**이다.

- P 및 total heat에 상대 전체 폭 1e-12라는 목표를 세운다면 저장된 E13C8 폭은 둘 다 그 기준보다 작다. 그런 기준만을 위해 새 전체 실행은 필요하지 않다.
- HeII heat에 상대 전체 폭 1e-12가 필요하다면 저장된 약 3.58e-11은 그 목표를 만족하지 못한다. 이 경우에는 실제로 어떤 경로가 해당 width budget을 지배하는지 읽기 전용으로 조사한 뒤 최소 work list를 설계할 이유가 생길 수 있다.
- 기준이 전체 폭이 아니라 midpoint 중심 상대 반폭이면 위 비교에는 `relative_half_width_display`에 대응하는 exact ratio를 사용한다.

이 예시의 1e-12는 설명을 위한 가정일 뿐 기존 계약·tolerance·승격 조건으로 추가하지 않았다. 실제 과학 문제의 필요 정밀도가 선언되지 않았으므로 '이미 충분하다'와 '더 정확해야 한다' 모두 전역적으로 확정할 수 없다.

### Ledger에는 상대 폭을 accuracy 목표로 쓰지 않음

저장된 ledger들은 모두 0을 포함한다. [S1]

| Ledger | 저장된 전체 폭 | 0 포함 |
|---|---:|---|
| `energy_final_plus_B_plus_Z_minus_QE_minus_anchor` | `6.84314931187009908949448E-17` | `true` |
| `heat_H_minus_B_plus_threshold_energy` | `7.34345337322251503607271E-17` | `true` |
| `number_P_plus_A_minus_QN` | `3.57494614912168178493929E-18` | `true` |

Ledger midpoint는 거의 0이므로 파일에 있는 상대 폭이 1e46–1e49처럼 매우 커진다. 이는 tiny midpoint로 나눈 결과이며, 실제 conservation defect가 그만큼 크다는 뜻이 아니다. Ledger에는 exact identity의 0 포함과 적절한 절대 budget을 사용해야 한다. 이런 상대 표시값을 낮추려고 NCP batch를 만들면 판별 목적을 잘못 잡게 된다. 기존 보존식과 signed anchor의 의미는 유지한다. [S1, S5]

## 4. 좁은 numerical enclosure와 physical/continuum HOLD를 분리

`FULL_FINITE_ADMISSION.json`은 기존 결과를 `PROMOTE_SCOPED_FULL_FINITE_CAPTURED_OFF`로 채택했다. 동시에 physical, continuum, production, receiver는 `HOLD`다. 이는 동일한 하나의 error bar에 큰 오차와 작은 오차를 섞은 상태가 아니라 **서로 다른 주장 범위의 상태**다. [S2, S3]

현재 enclosure는 정확히 고정된 captured inputs, gas interpolation, species masks/source flags, finite weighted grid와 first-two-step 조건 아래 수치 target을 둘러싼다. 그 구간 폭을 줄여도 다음을 자동으로 얻지 못한다.

- 다른 resolution/grid나 연속극한에 대한 오차 상계.
- captured/frozen 조건 밖 gas evolution·closure·물리 model의 타당성.
- 새 parameter regime, receiver 또는 production 경로의 검증.
- 실제 실행 provider의 attestation이나 CPU utilization 증명.

이 자료에는 이런 별도 물리·연속극한 오차를 모두 수치화한 budget이 없다. 따라서 'physical error가 확실히 지배한다'는 정량 주장도 만들지 않는다. 정확한 말은 **이미 작은 finite arithmetic width만으로는 별도 HOLD를 해제할 수 없다**는 것이다. E13C10의 수치 개선은 같은 finite problem의 더 유용한 enclosure라는 범위에서 평가해야 한다. [S1–S3, S6]

## 5. 선택한 5개 경로에서 전체 이득·speedup을 외삽할 수 없는 이유

E13C10의 5개 경로는 ordinary HI, 혼합 종, 모든 종, mask/source event와 exact-zero prefix 등을 판별하기 위한 선택 경로다. 무작위 표본 또는 전체 path weight·runtime 분포를 대표하는 통계 표본이라는 근거가 아니다. 2,440개 경로 전체의 새 방법 실행은 `NOT_RUN`이다. [S2, S6]

따라서 선택 경로에서 얻은 width 감소율을 전체 weighted P/H 감소율에 곱하거나, 선택 경로 평균 시간에 2,440을 곱한 값을 확정 wall time으로 쓸 수 없다. 특히 다음은 별도 증거가 필요하다.

1. 전체 sum의 width 기여도와 species별 기여도. 5개 경로의 상대 감소율과 전체 weighted 감소율은 다른 양이다.
2. Segment 수, active species, event 구조, required derivative refinement, cache 가용성과 경로별 비용 분포.
3. 각 경로 내부의 serial carry와 경로 사이의 독립성. 64개의 가능한 작업자 수가 곧 64배 가속을 뜻하지 않는다.
4. 같은 실제 work list에 대한 scheduling, startup/I/O, load imbalance와 reduction 비용.
5. 실제 CPU topology, affinity, memory limit 및 rank/thread layout. 128 GiB라는 전체 용량에서 요구 메모리나 최적 동시성을 역으로 정하지 않는다.

기존 E13C8 state에는 과거 2,331개 새 경로가 64 computing MPI ranks에서 batch wall `2037.8253215699988` s에 완료된 기록이 있다. 이는 **기존 E13C7/NCP work의 실제 기록**이며 E13C10의 실행 시간이나 동일-work speedup 기록이 아니다. 같은 state는 same-work serial speedup을 `NOT_ESTABLISHED`, CPU utilization을 `NOT_MEASURED`, provider attestation을 `NOT_ASSERTED`로 둔다. 이 기록은 완료된 과거 batch를 다시 실행하거나 새 batch 성능을 보증하는 근거가 아니다. [S2]

새 방법이 경로 수준에서 병렬화 가능하다는 구조적 판단과, 실제로 NCP를 쓰는 것이 유익하다는 실측 판단도 분리해야 한다. 짧은 이론·코딩·controls·대표 경로·saved-data reduction은 계속 HERE에서 처리한다. 전체 자료를 이미 읽을 수 있는 상태에서는 width attribution이나 pending claim 정리 역시 우선 read-only 작업으로 수행할 수 있다.

## 6. 읽기 전용 NEXT_DAG 권고

현재 source-bound 권고는 **새 NCP work units 0개 유지**, 상태 이유는 **명시된 미해결 full accuracy objective/work list 없음**이다. 이는 이 메모가 canonical state를 변경했다는 뜻이 아니다. 기존 완료 노드와 E13C8 full finite admission은 닫힌 채 유지한다.

NCP 이관 gate는 새 전체 실행 노드를 먼저 만들기보다 아래 입력을 명시하는 읽기 전용 작업으로 두는 편이 합리적이다.

| Gate 항목 | 현재 자료에서의 상태 | 새 계산 전에 필요한 구체적 내용 |
|---|---|---|
| 실제 판별 대상 | 전체 새 accuracy objective 미지정 | Observable, fixed-target scope, 비교/threshold 또는 후속 연구 판단 |
| 필요한 numerical budget | P/H 등의 기존 폭은 위 표에 있음 | Absolute/relative, full/half width 정의와 과학 목적에서 나온 수치 기준 |
| 기존 결과가 그 판단을 막는가 | 목적이 없어 결정 불가 | Exact saved interval과 명시 기준의 비교; 이미 충족하면 새 run 없음 |
| 필요한 미실행 work | 전체 새 방법은 NOT_RUN | Width 기여도에 근거한 최소 path/segment set; 완료된 work를 제외 |
| 새 방법의 국소 근거 | E13C10 selected-path 연구 범위 | 실제 final independent decision과 source/input/implementation pin |
| 계산이 실제로 긴가 | 5개 선택 경로로 전체 확정 불가 | 필요한 work의 비용과 짧은 HERE 실행으로 끝나지 않는다는 근거 |
| 병렬화가 유익한가 | 구조적 가능성만으로 부족 | 동일 work 기준의 예상/측정 구분, 독립 단위, load/memory/thread 계획 |
| 실행·반환 계약 | 새 full work list 없음 | Fresh outputs, first-failure 보존, immutable work lock, local reduction/판정 |

실제 목적이 특정 species의 폭이라면 먼저 저장된 contributor 자료를 읽어 필요한 부분집합을 찾는다. 목적이 continuum/physical HOLD를 푸는 것이라면 먼저 그 주장에 어떤 별도 가정·검증이 필요한지 source로 연결한다. 단순히 같은 finite target의 구간을 더 좁히는 대량 계산이 그 HOLD를 해결한다고 간주하지 않는다.

필요한 accuracy 목표, 그 목표를 막는 실제 saved width, locally validated method와 아직 수행하지 않은 긴 work units가 함께 확인될 때만 owner가 새로운 NCP 계약을 만들 근거가 생긴다. 그때도 64코어 점유나 128 GiB 채우기를 목표로 하지 않고, 명시된 연구 질문을 가장 적은 낭비로 해결하는 layout을 선택한다. 기존 user의 '짧은 일은 여기서, 무거운 병렬 부분만 NCP' 의도와 기존 E13C8/E13C10 gate에 부합하는 권고다. [S4, S6]

## 7. 실제 읽은 source와 hash

다음은 메모 작성 시 실제 읽은 파일의 identity다. S6는 진행 중 ROOT10 계약의 **읽은 시점 snapshot**이며, 이 메모는 그 계약을 수정하지 않는다. S1–S5는 복구된 E13C8 원본이다. hash는 byte identity이며 과학적 검증이나 실행 권한의 대체물이 아니다.

TASK:

`/workspace/scratch/7fd51143e473/e13c10_research_20261012`

ROOT8:

`/workspace/scratch/7fd51143e473/e13c10_research_20261012/RESTORED_E13C9/runtime/E13C8/package/BASS_HE_E13C8_FULL_FINITE_REDUCTION_20261011_v1`

| ID | TASK 기준 상대 경로 | bytes | SHA-256 |
|---|---|---:|---|
| S1 | `RESTORED_E13C9/runtime/E13C8/package/BASS_HE_E13C8_FULL_FINITE_REDUCTION_20261011_v1/analysis/FINITE_OBSERVABLES.json` | 28069 | `2fbfec9d258e75177e0add1a046b07751b25975fedd9f7b735234c08ccad2561` |
| S2 | `RESTORED_E13C9/runtime/E13C8/package/BASS_HE_E13C8_FULL_FINITE_REDUCTION_20261011_v1/CURRENT_STATE.json` | 2451 | `292b864d86e72d3255f7695fde6c77fa2b0985ba65a9403354cf2f0f41126851` |
| S3 | `RESTORED_E13C9/runtime/E13C8/package/BASS_HE_E13C8_FULL_FINITE_REDUCTION_20261011_v1/FULL_FINITE_ADMISSION.json` | 1325 | `e8c76e4d33d08eada5ceb05b2cdf333c913c249531a2b49c326f1a712fcf721c` |
| S4 | `RESTORED_E13C9/runtime/E13C8/package/BASS_HE_E13C8_FULL_FINITE_REDUCTION_20261011_v1/NEXT_DAG.json` | 2224 | `3ee27ad51e5aa5d11f5680d87f72fa5192bb7e788c5828bd0e0bf53d545dce47` |
| S5 | `RESTORED_E13C9/runtime/E13C8/package/BASS_HE_E13C8_FULL_FINITE_REDUCTION_20261011_v1/code/analyze_finite_observables.py` | 5882 | `0c644bb0b2212a2f1f01f444d02eb84e8015d2a900568a0f63a8622659b5cc7a` |
| S6 | `BASS_HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL_20261012_v1/SCIENTIFIC_CONTRACT.md` | 11236 | `467333ed1123008aa2e43c81016269ad14e69bf4aef0f58804dbc1dc1a761459` |

S1이 참조하는 기존 raw reduction SHA-256은
`14053cb89ce7078010554525888e2f730c25478ea87b40d484bdd472f0578f54`,
captured segments SHA-256은
`2a43dae808a0ca262dd175d2a1b74eeecc2c674d537f524bdba08e9d709076f7`다.
기존 full reduction semantic SHA-256은 S2/S3의
`d647ba154b84baf22a3f85f9b7dca19f029b97f466838c036a9d3321f4c315d1`이다.
이 큰 원본 데이터와 reduction은 이번 메모에서 재계산하거나 반복 검증하지 않았다.

**실행/변경 카운트:** 기존 finite analyzer 실행 0, full reduction 실행 0,
coefficient 호출 0, path integration 0, MPI/NCP 실행 0, external mutation 0,
canonical NEXT_DAG/CURRENT_STATE/정책 수정 0. 새 산출물은 이 메모 한 파일이다.

## 8. 완료된 E13C10 국소 증거와 E13C11 제안의 연결

이 메모를 닫는 시점에 새로 확정된 selected-path 산출물의 summary 필드도 읽었다.
`review/independent/EXEC01_FINAL/REVIEW_RESULTS.json`은 독립 저장 산술검사를
`PASS_INDEPENDENT_SAVED_ARITHMETIC`, **413,507 checks / 0 failures**로 기록한다.
아래는 해당 파일의 selected aggregate gain과 `analysis/ACTUAL/BOUND_ALLOCATION.json`의
`selected_totals.percent` 필드를 직접 옮긴 값이다. 이 메모는 reviewer의 전체 검사를
다시 수행하지 않았다. [S7, S8]

| Selected observable | E13C9 대비 전체 폭 감소율 % | 남은 반폭 중 signed rectangle % | 남은 반폭 중 first curvature % | 남은 반폭 중 finite tail % |
|---|---:|---:|---:|---:|
| `P_final` | `97.7836860203087025981346276037` | `98.8297170695052296458825` | `1.17020581738666431733713` | `0.0000771131081060367803720823` |
| `H_total_eV` | `98.0689999175101306660941604406` | `98.8338156793180753906269` | `1.16614776983539923530266` | `0.0000365508465253740703921947` |

이 분해는 source가 명시하듯 **propagated carry를 포함한 양의 반폭 상계 분해**다.
실제로 관측한 오차의 비중이 아니다. 선택된 5개 경로에서는 첫 적분을 줄인 뒤 남은
P/H 반폭의 약 98.83%가 signed rectangle 쪽에 있으므로, 같은 국소 방법 연구를
이어갈 때 prefix와 kernel의 결합 적분 상계를 다루는 것이 구체적인 후보가 된다.
이것은 전체 2,440개 경로에서 같은 개선율이나 같은 지배 항이 나온다는 증거가 아니다.
위 97.78%/98.07%를 E13C8 전체 폭에 곱해서 '개선된 full width'를 만들지 않는다. [S7, S8]

Owner가 제안한 후속 노드 `HE_E13C11_SECOND_INTEGRAL_BOUND_LOCAL01`은 이 점에서
HERE의 이론 → 짧은 controls → 필요한 representative pilots라는 범위와 연결된다.
새 prefix/kernel 결합 적분 규칙은 필요한 정칙성·remainder·carry 계약을 먼저
유도하고, 실제 유용한 짧은 판별만 수행하는 다음 국소 연구다. **이번 메모에서는
E13C11을 구현하거나 실행하지 않았고 상태는 PROPOSED/NOT_RUN이다.**

이 국소 연구를 제안하는 것과 새 전체 NCP batch를 여는 것은 다른 gate다.
E13C11의 짧은 방법 연구를 수행하기 위해 hardware occupancy 목표를 만들 필요가 없고,
국소 개선이 다시 확인되더라도 full accuracy objective와 실제 미실행 heavy work의
필요성·비용·병렬화 근거를 대신하지 않는다. 6절의 zero-new-NCP 권고는 이 구분을 유지한다.

추가로 읽은 파일은 다음과 같다. 읽은 범위는 selected totals, definition,
status/check-count 및 aggregate metrics 필드다.

| ID | ROOT10 상대 경로 | bytes | SHA-256 |
|---|---|---:|---|
| S7 | `analysis/ACTUAL/BOUND_ALLOCATION.json` | 29748 | `9966fa89d60ccb16502bc9782bec28722333a4a76a7379ebea7cb3c545c1418e` |
| S8 | `review/independent/EXEC01_FINAL/REVIEW_RESULTS.json` | 250517 | `84665d71fa85a4b2279767dbbc6deed080df91d61ff481c3e3f0be8bd51348ab` |
