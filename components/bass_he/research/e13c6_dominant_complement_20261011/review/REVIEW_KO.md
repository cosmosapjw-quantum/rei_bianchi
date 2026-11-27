# E13C6 독립 최종 판정

**판정: `PROMOTE_SCOPED` — `PASS_SCOPED_DOMINANT_COMPLEMENT_N512_REFINEMENT`.** OFF 101·102·410·413의 N512/P60 결과를 동일한 captured 두 구간 목표의 새 enclosure로 수용한다. 이번 교체는 원 positive spectral weight를 한 번 적용한 raw new interval을 사용한다. 교집합은 사용하지 않는다. 전체 OFF 유한 budget의 photon 폭은 **1.021889240910055%**, species-sum heat 폭은 **0.3156955305604365%** 감소했다.

이 판정은 실제 입력과 실행에 결합된 유한 문제의 enclosure를 수용한다는 뜻이다. 새로운 원자·기체 모형의 타당성, 연속 spectral quadrature 오차, physical/production 승격, receiver adoption을 승인하지 않는다. 실제 E13C6 NCP 재현은 아직 `NOT_RUN`이다.

## 검토자와 증거 독립성

검토자는 `/root/e13c6_return_intake`, 호스트가 표시한 모델은 GPT-6 Astra Pro다. 이 검토자는 이번 후보 코드·검증 설계·transfer 이론의 작성자가 아니다. 앞서 실제 E13C5 NCP 반환을 찾아 archive 및 semantic·CSV content를 확인하는 intake 작업을 수행했다. 같은 parent 문맥과 상속된 입력 계보를 공유한다는 점을 명시한다.

코드와 이론을 직접 읽은 뒤 별도 `independent_fraction_audit.py` 및 `compare_primary_analysis.py`를 한 번씩 실행했다. 전자는 **15,462개**, 후자는 **3,431개** 관계 대조를 통과했고 실패는 0이다. 이 수에는 저장된 interval의 유한·순서 검사도 포함된다. 검사 개수 자체를 독립적인 물리 증명의 개수로 해석하지 않는다. 검토 코드의 candidate/vendor import, coefficient evaluation, scientific solver, old full-budget 호출은 모두 0이다.

Old/new는 원 captured 자료, coefficient 모형 및 세 interval kernel을 공유한다. 따라서 양쪽이 겹친다는 사실이나 ledger가 0을 포함한다는 사실만으로 같은 목표 또는 정확성을 증명하지 않았다. 별도 Fraction 검산 역시 저장된 decimal endpoint 사이의 대수 관계와 mapping을 검증하며 coefficient 함수를 독립 적분하는 oracle은 아니다. 판정은 상속된 inclusion 수학 및 directed-Decimal 계약에 조건부다.

## 동일 목표와 합성식의 확인

원 PR20 `full_first2.py`를 보존 archive에서 읽어 고정 SHA `1f383e81d928d1afa3ecd5d22391d2a3ea82a289799dd54c9d4a18b741162ff8`과 일치함을 확인했다. 원 코드의 ordinary node 선택은 `(OFF,1,node,0)`와 `(OFF,2,node,0)`이며, 새 8개 control은 동일한 원 row·stage·node 및 binary64 실수화 정의에 묶여 있다. Frozen 초기값·source·opacity·gas interpolation·상수·weight·cutoff와 binding energy를 바꾸지 않았다.

첫 incoming은 정확히 0이고 둘째 incoming은 첫 true endpoint에서 둘째 captured `f0`를 뺀 것이다. 원 `run_track`의 generic 부분은 node 0/700용 `KEYS`와 분리되어 있으며, 이번 네 node는 `REUSED`에 속하지 않는다. 따라서 8개 local enclosure는 각 work unit에서 전부 새로 계산되고 다른 node의 certificate를 재사용하지 않는다.

연속 문제는 \(P'=q-\Lambda P\), frozen reference는 \(F'=q_f-LF\)다. \(e=P-F\), \(r=\delta q-\delta\Lambda F\)에 대해 \(e'+\Lambda e=r\)이며, \(\Lambda\ge0\)와 \(F\ge0\) 하에 \(\|e\|_\infty\le|c|+\eta+B_r\)를 사용한다. 원 코드가 incoming radius, coefficient-coupling remainder, numerical/representation radius를 각각 운반함을 확인했다. `nonlinear_upper`는 이 선형 photon 문제에서 coefficient-coupling bound의 이름이다.

새 실행은 각 구간 전체의 endpoint energy가 source 하한 13.7 eV보다 크고 initial energy가 HeI cutoff 24.59 eV보다 작음을 확인했다. 단조 redshifting trajectory와 결합하면 HI-only/source-on branch가 전체 구간에서 유지된다. 각 whole-cell coefficient 평가의 gas 및 rate 양성도 보존된다. 이 조건이 고정 branch의 smoothness와 동일 목표를 뒷받침한다.

Frozen-minus-captured 표현 차이는 local output에 한 번 포함되고, seam에서는 그 true-minus-captured correction과 실제 captured photon stitch residual을 전달한다. 이전 누적 moment radius는 photon처럼 damping하지 않는다. Native energy stock과 \(E_h n\)의 표현 차이도 남아 있다. Signed energy seam \(\Delta E=E_{0,2}-E_{1,h}\), \(J=\Delta E\,P_1(h_1)\)는 전체 energy ledger에서 뺀다. 실제 부호는 node 101·102·410에서 음수, 413에서 양수이며 `anchored=false`를 근거로 삭제하지 않았다.

## 실행·mapping·전역 budget

고정 `SOURCE_LOCK.json` SHA는 `0b4688c61c6070e0663fa78043a4ff3c37af2250f1e9d98d1e5485f568efaf47`이다. 15개 파일의 실제 identity, 세 vendor kernel의 원 PR19 bytes, 네 work unit의 source before/after 기록이 일치했다. 모든 실행은 exit 0이고 retry 0이다. N512/P60은 8개 local enclosure와 8,192회 coefficient evaluation을 기록했다.

Old absolute 필드는 이미 weighted이므로 weight를 다시 곱하지 않았다. Old correction은 최종 `DP`, 누적 종별 correction 및 energy-stock correction을 각각 읽고 weight를 한 번 적용했다. Old energy correction의 erg→eV 변환에는 원 binary64 상수의 정확한 lift를 한 번 사용했다. New correction은 이미 eV인 energy-stock correction을 그대로 읽었다. A/B/H total은 양쪽 모두 세 species interval의 Minkowski 합으로 다시 만들었으며 dedicated total을 한쪽에만 대입하지 않았다.

전체 교체식은 원 2,434개 OFF 경로와 이미 수용한 0·700 두 경로의 직접 retained sum에 네 새 weighted interval을 더한다. 34개 항에서 old K4 합과 retained+old K4가 기존 실제 반환 budget을 정확히 재현했다. 검토자는 이 exact endpoint bridge를 별도로 확인했으며 2,434개 raw reduction을 다시 실행하지 않았다. 원 primary 분석은 일반 interval subtraction을 사용하지 않는다.

| Work unit | Old/new overlap | Raw new nested | Full photon 폭 감소율 | Full heat 폭 감소율 | 판정 |
|---|---:|---:|---:|---:|---|
| N32/P60 | 136/136 | 48/136 | −16.92887343% | −5.75218878% | 저해상도 진단만 보존 |
| N128/P60 | 136/136 | 91/136 | 약 \(7.1\times10^{-49}\)% | 약 \(-1.4\times10^{-48}\)% | 동일 N 기준 비교, 개선 미입증 |
| N512/P60 | 136/136 | 136/136 | 1.02188924% | 0.31569553% | Raw new 교체 수용 |
| N32/P80 | 136/136 | 48/136 | −16.92887343% | −5.75218878% | 정밀도 민감도 진단 |

음의 감소율은 폭 증가다. N32는 같은 목표의 호환 가능한 coarse enclosure지만 refinement로 수용하지 않는다. N128의 일부 미세한 endpoint 차이는 outward rounding 크기이며, 같은 N에서 유의미한 formula gain을 관측했다는 주장을 지지하지 않는다.

N512의 full OFF photon 폭은 \(6.2103619403300204\times10^{-17}\)에서 \(6.1468989198402150\times10^{-17}\)로, heat 폭은 \(3.9111574389709289\times10^{-16}\)에서 \(3.8988100897429156\times10^{-16}\)로 줄었다. 단위·normalization은 원 유한 budget의 정의를 유지한다. 선택된 K4 항만 보면 photon 폭은 92.6400%, heat 폭은 93.1457% 감소했다. 이 선택 부분의 약 13.59배·14.59배 축소를 전체 물리 정확도의 배수로 표현하면 안 된다.

전체 N32 폭의 P80/P60 상대 변화는 photon 약 \(-4.03\times10^{-49}\), heat 약 \(-1.37\times10^{-44}\)다. 현재 관측된 폭 개선이 이 정밀도 범위의 roundoff 개선에서 비롯됐다는 근거는 없고, N512 subdivision refinement가 실질적인 변화다. 전체 radius의 엄밀한 \(N^{-2}\) 감소율이나 실제 해 오차의 양의 하한을 이 자료만으로 주장하지 않는다.

## 계약 해석과 남는 범위

봉인된 `SCIENTIFIC_CONTRACT.md`의 “N128에서 더 타이트한 remainder route를 시험한다”는 문장은 사전 가설로 보존한다. 실제 N128 비교는 측정 가능한 개선을 보이지 않았다. 그러므로 보고서에는 가설이 입증되지 않았다는 결과를 명시하고, N512 효과를 같은 N의 알고리즘 우월성으로 서술하지 않는다. 이 해석 정정은 scientific source나 이미 실행한 contract를 사후 변경할 이유가 아니다.

N512 교체 후에도 retained 항은 새 photon 전체 폭의 약 99.9180%, heat 폭의 약 99.9767%를 차지한다. 이 값은 고정한 Minkowski reduction과 retained 집합에 조건부다. 새로운 상관관계 처리나 다른 유효 enclosure 방법에 대한 보편적 하한이 아니다.

이번 bounded numerical admission에는 열린 blocker가 없다. 추가 scientific rerun 없이 검토된 결과를 전달하고, NCP에는 새 N512/P60 네 경로 work unit의 한 번 실행과 고정 semantic·exact-budget parity를 넘기면 된다. 이미 실제 성공한 E13C5 transport와 full-budget job을 다시 실행하지 않는다. NCP 재현은 실행환경의 재현성 검사이며 독립적인 물리·수학 oracle이 아니다.

## 증거 파일

- `INDEPENDENT_REVIEW.json`: 최종 범위 판정과 읽은 파일 bytes/SHA 목록.
- `INDEPENDENT_FRACTION_AUDIT.json`, `independent_fraction_audit.py`: 별도 정확 유리수 검사. 가상 old/new intersection 항은 reviewer의 사용하지 않은 진단이며 candidate 교체에는 포함되지 않는다.
- `PRIMARY_ANALYSIS_COMPARISON.json`, `compare_primary_analysis.py`: primary 4개 분석, 136개 경로-관측량 pair, 34개 전역 항, CSV와 semantic의 독립 비교.
- `PINNED_PR20_full_first2.py`: 직접 읽은 원 ordinary-path 구성 코드.
- `TRANSFER_THEORY_KO.md`: 별도 contributor의 transfer 정의 및 도출. 최종 검토자는 이 이론의 작성자가 아니다.
