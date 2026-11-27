# E13C3 Decimal 수치 기여: 국소 1차 계수변화 보정

## 결과와 역할

이 패킷은 **수치 기여자**의 산출물이다. 최종 decision reviewer의 판정이 아니다. E13C2에 저장된 동일한 여섯 segment에 대해 새 1차 계수변화 보정을 70자리 Decimal, Gauss–Legendre 12/20점으로 계산했다. 첫 계산은 exit 0으로 끝났으며, 여섯 국소 수치 gate와 여섯 signed total-heat-defect 연구 진단이 모두 통과했다. 직접 증거는 `DECIMAL_RESULTS.json`, 실행 증거는 `RUN_RECEIPT.json` 및 `DECIMAL_RUN.stdout`/`DECIMAL_RUN.stderr`이다.

가장 큰 총 열결함 상대오차는 **9.816962792678898 × 10⁻⁹**이다. 이는 저장된 continuous-minus-frozen **열결함**에 대한 비율이다. baseline의 총 열에 대한 오차 비율로 해석하지 않는다. 이 여섯 국소 비교와 현재 1% 연구 진단은 production tolerance, 전체 E13C2 경로의 오차 상계 또는 receiver adoption을 부여하지 않는다.

## 고정 입력과 의미

입력은 E13C2 `evidence/ORACLE_RESULTS.json`의 여섯 고정 key, 그 안에 저장된 원래 CSV row 및 stage row, 그리고 원래 캡처 CSV의 일치 확인으로 한정했다. 저장된 oracle 결과와 helper 코드의 SHA-256을 실행 전에 고정했다. 원래 캡처/입력 다섯 파일의 해시 및 바이트 수도 E13C2 기록과 대조했다. 이 사실은 입력의 동일성을 확인하며, 물리 모형의 타당성이나 별도 승인을 증명하지 않는다.

각 segment는 자신의 captured `f0`에서 시작한다. 보정 초기값은 모두 `e1(0)=0`이다. segment 사이에 보정된 photon state를 전달하지 않았다. `a`, `h`, `e0`, gas old/new stage와 source/frozen 계수는 E13C2와 같은 `CSV → binary64 → Decimal.from_float` 경로로 정확히 올렸다. source mask와 absorber mask는 저장된 segment의 내부 support를 유지한다.

열의 이온화 에너지는 다음 binary64 값들을 정확히 올렸다.

| 종 | χ [eV] |
|---|---:|
| HI | 13.598434599702 |
| HeI | 24.587389011 |
| HeII | 54.41776 |

이 값들은 atomic-fit support cutoff와 다른 입력이다. 계산에서는 둘을 교환하지 않았다.

## 유도와 구현

`u=s-a`, `0≤u≤h`, `E(u)=e0 exp(-u)`로 둔다. `Lf=Σ_i λf_i`와 captured `qf`를 사용한 frozen field는

\[
P_f(u)=f_0 e^{-L_f u}+q_f J(L_f,u),\qquad
J(a,t)=\frac{1-e^{-at}}a,\quad J(0,t)=t
\]

이다. coefficient difference는 `δq=q-qf`, `δλ_i=λ_i-λf_i`, `δΛ=Σδλ_i`로 정의했다. 새 보정이 푸는 방정식은

\[
e_1'+L_f e_1=r,\qquad r=\delta q-\delta\Lambda P_f,
\qquad e_1(0)=0.
\]

새 코드는 이 식의 damped endpoint와 두 Fubini moment를 각각 1차원 quadrature로 평가한다.

\[
e_1(h)=\int_0^h e^{-L_f(h-v)}r(v)\,dv,
\]

\[
I_0=\int_0^h J(L_f,h-v)r(v)\,dv=\int_0^h e_1(u)\,du,
\]

\[
I_E=\int_0^h E(v)J(L_f+1,h-v)r(v)\,dv
=\int_0^h E(u)e_1(u)\,du.
\]

에너지 moment의 `Lf+1`은 `E'=-E`에서 나온다. 따라서 직접 계수변화와 photon-field 반응은

\[
\delta A_i=\underbrace{\int_0^h\delta\lambda_iP_f\,du}_{D_{A,i}}
+\lambda_{f,i}I_0,
\]

\[
\delta B_i=\underbrace{\int_0^h E\delta\lambda_iP_f\,du}_{D_{B,i}}
+\lambda_{f,i}I_E
\]

로 분리된다. `δZ=IE`, `δQN=∫δq du`, `δQE=∫Eδq du`를 함께 계산한다. 1차 primary heat는 `δH_i=δB_i-χ_iδA_i`, 총 열결함은 `Σ_iδH_i`이다. `DECIMAL_RESULTS.json`은 직접 항과 반응 항을 각각 보존한다.

수/에너지 ledger는

\[
e_1(h)+\sum_i\delta A_i-\delta Q_N=0,
\]

\[
E(h)e_1(h)+\sum_i\delta B_i+\delta Z-\delta Q_E=0
\]

이다. 이들은 1차 모델과 moment 구현의 일관성을 검사한다. 전체 variable-coefficient 방정식에 `Pf+e1`을 넣으면 잔차 `δΛ e1`이 남는다. 따라서 1차 ledger 폐합은 이 잔차의 소멸이나 실제 2차 오차의 전역 상계를 뜻하지 않는다.

## 독립성의 범위

E13C2 `decimal_collocation.py`의 **물리 계수 정의 `Coefficients`와 Gauss rule `gauss_rule` 및 그 내부 dependency**를 바이트 변경 없이 사용했다. 따라서 atomic/source/gas 정의와 quadrature root 구현은 저장된 참조와 공유된다.

새 파일 `decimal_first_variation.py`는 frozen field, `J`의 닫힌 Decimal exponential 식, first-variation endpoint, Fubini moments, 직접/반응 항, heat와 ledger, 비교 metric을 별도로 구현했다. `collocate`, `integrated_lagrange`, `solve_decimal`, `frozen_exact`, `read_and_select`, 기존 `main`은 호출하지 않았다. 새 파일의 AST에서 확인되는 helper 호출은 `Coefficients`, `gauss_rule` 둘뿐이다. 기존 continuous ODE나 collocation을 다시 실행하지 않고 **저장된** 20점 Decimal continuous-minus-frozen 값을 읽어 비교했다.

이 기여자는 부모의 longdouble GL8/12 구현을 작성하거나 그 결과를 보고 조정하지 않았다. 이 비교는 새 correction 구현의 교차 검사이며, 공유 물리 정의까지 독립적으로 검증한 것으로 분류하지 않는다.

## 실행 전 gate와 실제 결과

`TASK_CONTRACT.json`은 새 계산 전에 작성했고, 입력 pin과 아래 기준을 고정했다. 기준 변경 및 실패 은폐는 없었다.

| 검사 | 고정 기준 | 실제 최댓값/결과 |
|---|---:|---:|
| 새 GL12/20 number 차이 | ≤ 10⁻²⁵ | 8.488065754288217 × 10⁻⁵³ |
| 새 GL12/20 energy/heat 차이 [eV] | ≤ 10⁻²⁴ | 1.162864229943782 × 10⁻⁵¹ |
| 1차 number ledger | ≤ 10⁻⁴⁵ | 7 × 10⁻⁸² |
| 1차 energy ledger [eV] | ≤ 10⁻⁴⁵ | 2.1187823 × 10⁻⁸⁰ |
| Gauss polynomial moments | ≤ 10⁻⁵⁰ | 12/20점 모두 PASS |
| `J(0,t)=t`, zero-duration limit | 정확 일치 | PASS |
| 입력 해시/row/key/support | 정확 일치 | PASS |
| 국소 total heat-defect 상대오차 | ≤ 0.01, 연구 전용 | 최대 9.816962792678898 × 10⁻⁹ |

상대오차는 참조 절댓값이 energy `10⁻²⁴ eV`, number `10⁻²⁵` 이상일 때만 정의해서 보고한다. 그 아래 값은 `UNRESOLVED_BELOW_ABSOLUTE_FLOOR`로 표시하고, 절대오차가 해당 floor 이내인지 별도로 보고한다. `error/max(|reference|,floor)`는 별도 regularized normalization 필드에 보존한다. 여섯 **total heat** 참조는 모두 floor 이상이었다. zero-support 종의 영값 같은 항에는 이 제한이 적용된다.

| (mode, step, node, segment) | 새 1차 총 열결함 [eV] | 저장된 총 열결함 [eV] | 상대오차 |
|---|---:|---:|---:|
| OFF, 1, 0, 0 | −6.172112576813734 × 10⁻¹⁴ | −6.172112607155903 × 10⁻¹⁴ | 4.916010250426077 × 10⁻⁹ |
| OFF, 1, 1162, 0 | −4.592914611309619 × 10⁻¹³ | −4.592914611794652 × 10⁻¹³ | 1.056047203207190 × 10⁻¹⁰ |
| OFF, 1, 1976, 0 | +2.918182241744331 × 10⁻¹⁴ | +2.918182213096645 × 10⁻¹⁴ | 9.816962792678898 × 10⁻⁹ |
| GM, 2, 1727, 0 | −3.019158552264705 × 10⁻¹³ | −3.019158554509014 × 10⁻¹³ | 7.433556596576175 × 10⁻¹⁰ |
| GM, 2, 2333, 0 | +2.826989280452860 × 10⁻¹⁴ | +2.826989276126903 × 10⁻¹⁴ | 1.530234695378294 × 10⁻⁹ |
| OFF, 2, 700, 1 | −1.297959067331960 × 10⁻¹² | −1.297959077237063 × 10⁻¹² | 7.631290029028076 × 10⁻⁹ |

각 segment의 `u/h=0,1/4,1/2,3/4,1`에서 `Pf+e1`을 추가로 평가했으며 모두 비음수가 나왔다. OFF 첫 step의 시작값은 0이다. 이는 30개 지정 sample의 진단이며 구간 전체의 positivity를 증명하지 않는다.

## 재현성과 출력 schema

실제 실행은 `2026-10-10T11:18:56.793210+00:00`에 시작하여 `11:18:57.384817+00:00`에 끝났다. 외부 process wall time은 0.591616042 s, 코드 내부 elapsed는 0.543713304 s, 실제 exit는 **0**이다. CPython 3.12.14, libmpdec 4.0.0, 표준 라이브러리만 사용했다. 이 시간은 같은 환경에서 실행한 여섯 참조 계산의 관측값이며 성능 벤치마크나 native 실행 대비 speedup이 아니다.

실제 명령의 argv 및 전체 환경은 `RUN_RECEIPT.json`과 `DECIMAL_RESULTS.json`에 보존했다. 명령 형태는 다음과 같다.

```text
python decimal_first_variation.py --prior-root <E13C2-root> --contract TASK_CONTRACT.json --output DECIMAL_RESULTS.json
```

주요 hash는 다음과 같다.

| 대상 | SHA-256 |
|---|---|
| 새 코드, 실제 실행 전/후 동일 | `b3d5830363911c892039547623ade74eaad0fc311808cf46eec11b6613650903` |
| 새 결과 JSON | `29f682478cf28d51e1b83d412db05097fd2b844e73ad50b8330527db76fc77cf` |
| 실행 전 contract | `71a1cfc227185c503e9b5c5a2ff94c249a59687f5224e6f29ecc7600e9adb12f` |
| 저장된 E13C2 oracle 결과 | `0f719a1c24ef36dbb9248bf386989a0028ba84b913235be80d57ad437cad4d85` |
| 공유 E13C2 helper 코드 | `6ca9de462ac24e3a559a5f8de7df01c04b79ed9172b5474546103eedcb2385a5` |

비교 구현은 `results[].key`로 대응시킨 뒤 `results[].calculated_by_degree["20"]`을 읽으면 된다. `P1`, `A`, `B_eV`, `Z_eV`, `QN`, `QE_eV`, `H_eV`, `H_total_eV`는 모두 **signed first variation**이다. frozen endpoint와 corrected endpoint는 명시적으로 다른 필드에 있다. 모든 Decimal 수는 precision 손실을 피하려고 문자열로 직렬화했다. 직접/반응 항은 `direct_A`, `direct_B_eV`, `response_A`, `response_B_eV`, 응답 moments는 `I0`, `IE_eV`이다.

## Claim ceiling과 보존 상태

근거 상태는 식에 대해 `derived`, 이 여섯 실행에 대해 `numerically checked` 및 `implementation-verified`이다. 독립 decision review, 전체 경로 연속성 오차, interval certification, atomic fit 불확실성 및 gas/coupled advancement는 이 기여의 범위 밖이다.

`baseline_RCT=OFF`, actual photon/heat/recoil `null`, physical/production `HOLD`, `HE-F2/F09=OPEN`, `Gamma alias3.543295=FAIL`을 유지했다. owner gate 변경은 없다. 부모가 별도 구현과 증거를 통합하고, 실제 독립 decision reviewer가 scoped 판정을 내릴 수 있도록 이 패킷을 반환한다.
