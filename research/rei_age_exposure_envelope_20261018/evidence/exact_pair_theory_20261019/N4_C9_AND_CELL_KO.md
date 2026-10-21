# N4 C9 독립 검토와 마지막 실패 셀의 정확한 표현 조건

## 판정

**N4 소스에 대한 범위 지정 독립 검토는 PASS다.** 요청된 4개 동결 파일의 SHA256이 모두 일치했고, 검증 동안 바뀌지 않았다. 새 focused tests만 한 번 실행해 **3/3 PASS, 0.951초**를 확인했다. 실제 N2/N3 셀에 대한 Rust 1.94.1 컴파일·실행과 Fraction oracle의 일치, 189개 부호 있는 정수 구간 대조, overflow/domain/budget 검증이 포함된다.

전체 native time8 실행의 판정은 **FAILED / HOLD 그대로**다. 읽은 실제 receipt는 exit 1, 22.15056397800072초, `timed_out=false`다. 독립 검토자가 추가한 전체 native 실행은 0회이며, 구현 소스를 수정하지 않았다.

`PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.

## 1. 실제 소스 검토

검토 대상은 `src/subnormal_pair_search.py`, `src/prepare_native.py`, 새 테스트와 실제 셀 fixture다. 정확한 hash와 테스트 원문은 `N4_C9_SOURCE_REVIEW.json`, `N4_C9_TESTS.log`에 있다.

### 정수 구간이 원래 검사와 연결되는 조건

노드를 공통 dyadic denominator로 \(q_i=A_i/D\)라고 쓴다. 코드는 normal·양의·유한한 \(q_i\), 비음 subnormal/0 질량, 양의 subnormal 총량을 요구한다. 표현 불가능한 shift나 i128 중간값은 `UNSUPPORTED`로 반환한다.

\[
2A_{\max}T+mD<2^{53}D
\]

검사는 \(q_{\max}T+m/2<2^{52}\)와 동일하다. 이는 양의 저장 에너지 곱과 모든 부분합이 subnormal 영역 안에 남는 충분조건이다. 코드가 실제 \(\operatorname{RN}(q_i z_i)\) bit 값과 정확한 ties-to-even 정수 곱을 비교하고, 원래 compensated sum과 정수 에너지 합의 일치까지 확인하는 점도 검토했다.

두 노드의 저장 곱을 제외한 정수 에너지 합을 \(C\)라 할 때,

\[
B_0=(C-U)D+A_at_a+A_bt_b,\qquad B_1=A_b-A_a.
\]

각 저장 곱의 반올림 오차가 최대 \(1/2\) quantum이므로 모든 성공 후보는

\[
|B_0+kB_1|\le(\tau+1)D
\]

안에 있다. 코드의 radius, 양·음·0 slope 분기, signed ceil/floor, \(1\le k\le t_a-1\) 및 receiver의 표현 범위 교차는 이 필요조건과 일치한다. 부호로 방향을 제외하지 않는다. 동일 \(q\)도 해당 유한 양의 지지 구간을 유지한다.

### 산술과 실행 상태

- checked shift는 shift 수뿐 아니라 남은 유효 bit 범위도 확인한다.
- signed division은 양의 분모만 받아 Rust의 0 방향 나눗셈을 수학적 floor/ceil로 보정한다.
- 분자, 곱, 합, 음수화에서 i128 overflow를 검사한다.
- min-heap은 \((k,\mathrm{donor},\mathrm{receiver})\) 순서다. 성공 시 최소성은 **고정 count-base에서 단일 pair의 최소 \(k\)**다.
- 65,536회는 계산 예산이다. 소진은 `SEARCH_BUDGET_EXHAUSTED`이고 feasibility claim은 발급하지 않는다.
- 완전한 해당 구간 탐색의 실패와 지원하지 않는 산술 영역은 각각 다른 상태로 보고한다.
- 후보는 원래 벡터의 별도 복사본이며, 기존 두 compensated-sum 검사와 기존 tolerance를 통과한 후보만 반환한다.
- 원래 실패 분기에서만 작동하고, \(|F|<8\epsilon\)를 다시 요구한다. 이미 통과한 원래 결과는 변경하지 않는다.
- 모든 미수용 경로는 기존 `AXBI_COVARIANT_MOMENT_FIT` 오류로 이어진다.

새 prepare mode를 선택하지 않은 none/count/k1의 기존 준비 결과 일치 receipt를 실제로 읽었다. 해당 준비 identity는 각각 `e376b58e…`, `ef15de03…`, `6b05bb7b…`이며 전체 값은 검토 JSON에 보존했다. 이를 추가 전체 준비 캠페인을 반복한 것으로 기록하지 않았다.

검토한 범위에서 수정이 필요한 결함을 발견하지 않았다.

## 2. N4 실제 마지막 실패 셀

입력은 다음 파일이다.

`/workspace/scratch/36ed695112a9/runtime_probe/session_20261019T0933Z/N4_FULL_DIAGNOSTIC_BITS.json`

SHA256:

`a6f1fc70462b661e7dad9cf05f89b7633bca609b09ccc8c3be2aaa82c501a109`

\(\eta=2^{-1074}\)라고 하자. 16개 고정 노드의 저장 질량은

\[
(t_0,\ldots,t_{15})=(0,0,1,1,1,1,1,0,0,0,1,1,1,1,1,0)
\]

quantum이다. 양의 지지는
\[
I=\{2,3,4,5,6,10,11,12,13,14\}
\]
이고, 나머지 6개는 0이다. 목표 총량은 \(T=10\), 목표 에너지는 \(U=245\) quantum이다. 원래 count와 energy tolerance는 모두 정확히 0이다.

양의 노드 순서의 저장 에너지 곱은

\[
22,\ 23,\ 23,\ 24,\ 24,\ 25,\ 26,\ 26,\ 26,\ 27
\]

quantum이고 합은 246이다. 모두 subnormal 정수 격자에 있으므로 원래 Kahan 합도 정확히 \(246\eta\)다. count는 \(10\eta\)로 맞지만 energy는 \(+\eta\) 초과한다. 원래 \(F=-5.766874737210527\times10^{-17}\)는 수렴 조건 안에 있다.

## 3. 이 셀에서 가중치가 유일하다는 보조정리

**조건.** 이 16개 노드를 유지하고, 기존 10개 양의 지지와 기존 6개 0을 유지하며, 각 저장 질량이 비음 정수 quantum이고 총량이 정확히 \(10\eta\)라고 하자.

기존 양의 각 노드의 새 정수 질량 \(s_i\)는 \(s_i\ge1\)이다. 따라서

\[
\sum_{i\in I}(s_i-1)=\sum_{i\in I}s_i-|I|=10-10=0.
\]

좌변의 모든 항은 비음 정수이므로 모든 \(s_i-1=0\)이다. 0인 노드는 그대로 0이다. 따라서 허용된 질량 벡터는 **원래 벡터 하나뿐**이다.

그 유일한 벡터가 원래 energy 검사에 실패하므로, 이 셀에서는 해당 표현·지지·정확한 총량을 보존하는 **어떠한 가중치만의 보정도** 두 원래 검사를 함께 통과할 수 없다. 여러 pair를 조합해도 허용 벡터 집합이 하나라는 결론은 변하지 않는다.

실제 N4 로그의 `nonempty_intervals=0`, `candidate_evaluations=0`는 이 사실과 일치한다. 모든 양의 donor가 1 quantum이라 하나라도 내주면 기존 양의 지지가 사라진다.

이 결론의 범위는 **이 실제 셀의 binary64 저장 격자, 고정 지지, 정확한 count와 원래 검사**다. 전체 물리 모형이나 다른 수치 표현의 불가능성을 주장하지 않는다. 새로운 strong no-go의 보편성·신규성을 주장하는 결과도 아니다.

## 4. 표현 조건을 분리하는 정확 실수 대조

현재 가중치의 정확 실수 에너지 잔차는

\[
\left(\sum_iq_it_i-U\right)\eta
=\frac{275130971747253}{281474976710656}\eta
\simeq0.9774615667881399\eta
\]

다. 저장 곱의 합이 만드는 \(1\eta\) 잔차와 구별했다.

수치 표현 조건을 분리하기 위한 작은 대조로, 같은 양의 지지 위에서 **실수** 가중치를 허용하면 두 실수 모멘트를 맞출 수 있다. 노드 14에서 2로

\[
\alpha\eta,\qquad
\alpha=\frac{91710323915751}{418146595942864}
\simeq0.21932576949229163
\]

를 옮긴다. \(0<\alpha<1\)이므로 두 가중치는 계속 양수이고 총량은 그대로다. \(\alpha\)를 정확 에너지 잔차를 \(q_{14}-q_2\)로 나눈 값으로 정의했으므로 실수 에너지도 정확히 \(245\eta\)다.

이 가중치는 binary64 subnormal 질량으로 표현할 수 없다. 대조는 물리 모멘트 방정식 자체와 현재 저장 격자의 제한을 구분하기 위한 것이며, native 코드에 적용하지 않았다.

## 5. 단계 종료

이 native 보정 단계는 N4에서 멈춘다. 같은 지지와 저장 격자에 대한 탐색 확대는 위의 유일성 때문에 이 셀을 해결하지 못한다. 현재 실패·HOLD를 보존하고, 부모가 지정한 다음 목적은 완료된 age64 block-max를 재사용하는 같은 source의 age32 실제 실행이다.

검토자는 코드에 쓰기 작업을 하지 않았고, 전체 native 실행을 추가하지 않았다. skill 1.3.0 문맥은 앞선 단계에서 실제로 읽은 동일 버전을 재사용했다. 현재 materialized tree에서는 AGENTS.md가 발견되지 않아 다시 읽었다고 기록하지 않았으며, 부모가 제공한 기존 문맥과 명시적인 read-only C9 범위를 따랐다.

독립 검토 결과와 새로운 셀의 정확 계산은 각각 `N4_C9_SOURCE_REVIEW.json`, `N4_QUANTIZED_SUPPORT_LEMMA.json`에 보존했다.

