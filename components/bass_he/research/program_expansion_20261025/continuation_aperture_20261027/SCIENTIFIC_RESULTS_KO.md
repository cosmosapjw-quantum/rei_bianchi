# 과학적 판별 결과 — R7/C7

새 32개 검사와 저장값 생성은 S05 local `3e41e230ff028fe28eb8aa35d9d6fecb1b22fd1f`의 고정 소스에서 첫 실행으로 통과했다. 동일 tree의 원격 소스는 `1e6d82845e922e0d733be3d2f80e9bd2efc41e04`다. 누적 실제 CPU0.235556515s/4s, wall0.246533713s/15s, repair0이다. 실행·원전·수학적 유도·물리 적용 범위를 각각 구분한다.

## 1. Fold의 유한 관측량

정확한 제조 map γ=1,a=5/4에서 창 `[3/5,4/5]`의 uniform event mass는 `sqrt(7)/5`다. 40-bit CM bracket의 저장 경계는

\[
 \frac{11636137322867}{21990232555520}
 \le Y\le
 \frac{2909034330721}{5497558138880}.
\]

이것은 약 `[0.5291502622124881,0.5291502622132611]`이며 표시용 소수와 별도로 정확한 rational 끝점이 저장되어 있다. 폭은 `17/21990232555520`, 약7.7307049651e−13이다. 양의 두 끝점의 제곱이7/25를 감싼다는 독립 판별을 통과했다. singular lab point density를 유한한 가짜 수로 바꾼 결과가 아니라 CM 역상 전체의 적분이다.

| δ의 bit 수 | 저장된 mass 폭 |
|---:|---:|
| 8 | 0.0033203125 |
| 16 | 1.2969970703125e−5 |
| 24 | 5.066394805908203e−8 |
| 40 | 7.73070496506989e−13 |

같은 입력에서 inner set은 확대되고 outer set은 축소되는 검사를 통과했다. 새 fold-bin6개는 lab 폭1/4부터1/128까지의 유한 질량을 저장했다. 이 범위의 실제 값으로 그림을 만들며 보간된 데이터나 추가 과학 실행을 사용하지 않는다.

## 2. 사건 상관과 입자 수

제조 identity map의 두 반대 창에서 coincidence 사건 measure는1/2, 각 창의 사건 hit도1/2다. hit의 곱1/4는 이 공유 사건의 coincidence가 아니다. 선택된 coincidence 사건이 대표하는 daughter measure는1이다. 선언된 test weight E±=3±μ MeV에서 pair energy 적분은3MeV이다. 이 값은 관측함수를 먼저 합친6Y에서 나온다.

이 계산은 이벤트를 중복 세지 않는 한편, 사건당 두 daughter를 입자 수에 정확히 반영한다. 열용량·열적 heating·결합 에너지 항을 새로 만들지 않는다. binding/rest owner와 비열적 energy의 분리는 `MODEL_CONTRACT.json`에 유지한다.

## 3. 선형 모멘트와 기호 검증

Wolfram Language evaluator를 신규 할당된1회(timeConstraint15s) 실행했다. n=0..8의45개 Bernstein basis 질량식과45개 선형 weight 식, 두 fold 경계식의 잔차가 **92개 모두0**이었다. 원래 부호와 domain 판정 두 개도 True였다. 부호 있는 불확실 구간의 경계 `[−3/64,3/64]`, coincidence1/2, hit product1/4, 선언된 pair-energy3도 일치했다. 실제 응답과 입력 코드는 `evidence/WOLFRAM_APERTURE07.json`에 보존했다.

원격 CAS의 실제 CPU는 제공되지 않았으므로 null이다. 이를 로컬 CPU0.235556515s에 포함하거나0으로 표시하지 않는다. 기존 ANGULAR06 map 유도 전체나 기존 suite를 다시 실행한 기록은 없다.

## 4. 저장 native parameter의 새 적용

기존 ANGULAR06 저장 데이터12행의 `source_row,γ,a`만 읽어 새 annular 창 `[1/2,1]`, `[−1,−1/2]`의 관측량을 계산했다. 밀도는 명시적인 제조 `b=[0,3/2,0]`, 즉 `3/4(1−μ²)`이며 σ=1이다. DCS·오차 열은 사용하지 않는다. 같은 에너지의 행은 같은 parameter를 공유할 수 있으므로12개의 서로 독립적인 물리 검증을 주장하지 않는다.

첫 행의 저장 γ≈1.0014642194398002, a≈0.1791462571214452에서 coincidence 표시 경계는 약 `[0.18196616615217792,0.18196616615300437]`다. 정확한 rational endpoints가 원본 JSON에 있다. 이 값은 실제 실험 단면적이나 사건률이 아니다.

저장된 native·fold-bin 예들은 명시적으로 δ=2⁻⁴⁰을 지정했다. 각각의 `width`와 `width_bound`가 이 설정의 인증 범위다. 별도의 **기본 API**는 δ=σ2⁻⁴⁰/(16M)를 선택하여 요구한 상대 질량 폭을 보장한다. 수동 δ 예의 모든 hit 경계를 기본 API의2⁻⁴⁰ 목표와 동일시하지 않는다.

## 5. S07 시점의 채택 범위 — 원래 체크포인트 기록

실행 근거는 고정 parameter의 rational preimage·양성 measure·signed moment·공유 사건 구현을 지지한다. 원전 Rice의 convention 확인은 유한 수용각·동일 입자 계수의 과학적 연결을 제공한다. M0475 원본 정규화, 실제 full angular law+photon flux, 명명된 deuteron stopping/deposition의 세 물리 입력은 계속 열린다.

현재 local DAG는 **7complete+1pending+3physicalopen/11**이다. 최종 구현 제품은 저장 데이터 그림과 실제 결과 독립 검토 후 채택한다. 중앙28/88, HEdelta0, globalphysicalnull, L4false와 모든 선행 실패 기록은 유지한다.


## 6. S09 독립 검토 후 채택

이 절은 위 S07 기록 이후의 실제 채택 상태다. 새 그림의 첫 실행 PASS와 실제 결과를 같은 독립 review pass에서 이어 검토하여 결과 검사10개 PASS, 결함0으로 판정했다. root는 `ACCEPT_SCOPED_CONDITIONAL_APERTURE_REFERENCE`를 채택했고 `APERTURE07-VALIDATED-REFERENCE`를 완료로 기록했다. 현재 continuation DAG는 **8 complete + 0 pending + 3 physical open / 11**이다. 근거는 `review/RESULT_REVIEW.json`, 채택 정리와 사용 범위는 `ACCEPTANCE_KO.md`, actual plot 판독은 `evidence/PLOT_READ_KO.md`다.

새32/32 검사, 한 번의 기호 검증92개 영잔차, 새 저장값 그림PASS는 위에 기록한 동일 실행을 재사용한다. 추가 과학 실행이나 tolerance 변경은 없다. 고정 저장 parameter·연속 measure·전체 방위각 annular 창이라는 인증 범위, 수동 δ와 기본 ε 보장의 차이, 세 열린 물리 입력과 중앙28/88·HE delta0는 그대로다. S10 인계 전이므로 workflow는 IN_PROGRESS로 유지한다.
