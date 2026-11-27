# BASS_HE E13C3 — 고정 가스 경로의 지수 감쇠 보정

2026-10-10 · GPT-6 Astra 연구/코딩 하네스 v4.0.0 · 유한 입력에 대한 연구 판정

## 1. 이번 루프의 결과

**E13C2가 측정한 연속 계수의 광자 흡수·가열 편향을, frozen 감쇠를 그대로 유지하는 1차 보정으로 재현했다.** 동일한 OFF/KF/GM first2의 14,652개 native event segment를 합산한 **여섯 macro transaction의 총 열결함**에서 최대 상대오차는 **1.6479380×10⁻⁸**였다. 실행 전에 고정한 후보 판정 기준은 열결함의 1%였고, 여섯 국소 control과 여섯 macro transaction이 모두 통과했다. 여기서 상대오차의 분모는 총 가열량이 아니라 **저장된 continuous-minus-frozen 열결함**이다. [근거: `PLAN.json`, `evidence/LOCAL_ACCEPTANCE.json`, `evidence/FINAL_ACCEPTANCE.json`.]

GL12 구현은 first2 전체에 과학적 계수 평가 **175,824회**를 사용했다. 같은 저장 경로의 E13C2 연속 적분은 RHS·segment 평가 **2,711,100회**를 기록했다. 평가 횟수의 비는 **15.4194**이며, 이번 GL12 실행 시간은 **1.220697초**, peak RSS는 **103,956 KiB**였다. 이 비교는 계수 샘플 수의 감소를 보여 준다. 서로 다른 실행 시점과 부대 작업을 포함한 두 시간의 비를 통제된 가속 배율로 해석하지 않는다. [근거: `evidence/paths_gl12/RESULTS.json`, `inputs/e13c2/evidence/defect_rtol_2e11/RESULTS.json`, `evidence/FINAL_ACCEPTANCE.json`.]

이 결과가 보여 주는 물리적 내용은 제한적이지만 명확하다. **현재의 affine gas path에서 midpoint freezing이 만든 작은 signed 광자·가열 편향은, source/opacity 변화의 직접 효과와 감쇠된 광자장 response를 함께 넣으면 저비용으로 설명된다.** 새로운 gas history나 실제 원자 RCT emission을 계산한 것은 아니다. 이번 계산 판정은 `PASS_SCOPED`이며, 별도 심사자의 최종 독립 판정은 `INDEPENDENT_REVIEW.json`과 `INDEPENDENT_REVIEW_KO.md`가 권위 있는 기록이다.

## 2. 입력을 어떻게 고정했는가

출발점은 repository `cosmosapjw-quantum/BASS_HE`, branch `research/shared-c64-crossrepo-20260928`, draft PR #17의 intake HEAD `7e82c807c372392b9f48c0ba3d77986e74d71aea`다. 바로 앞 E13C2 archive는 SHA-256 `b8804561a86d8a171c478dbc0baf6313efb5b0c0e19fea9e1d0a095a9df661b5`, 7,275,484 bytes다. [근거: `PLAN.json`, `inputs/INPUT_MANIFEST.json`.]

E13C2의 기존 24개 원자료와 입력 manifest, 저장된 full/local continuous 결과, coefficient helper와 이론·인계 자료를 합쳐 **34개 파일, 22,963,662 bytes**를 먼저 고정했다. 각 파일의 바이트 수와 SHA-256을 부모 packet의 manifest와 대조한 뒤 복사했다. 새 계산마다 이 34개 입력의 identity를 확인한다. 부모의 과거 producer 기록을 새로 작성하거나 과거 실행의 코드 해시를 소급해서 주장하지 않는다. 새 E13C3 producer는 실행 전에 자기 코드, helper, 입력 manifest의 해시를 `RUN_STARTED.json`에 남긴다. [근거: `inputs/INPUT_MANIFEST.json`, 각 `RUN_STARTED.json`.]

물리 입력은 이전 루프와 같다.

| 항목 | 현재 계약 |
|---|---|
| 경로 | OFF/KF/GM 각각 저장된 첫 두 macro gas transaction; endpoint 사이 affine gas path |
| 좌표 | \(s=\ln a\), 사건 내부 \(u=s-s_a\); 동일한 spectral characteristic |
| 광자 에너지 | \(E(u)=E_0e^{-u}\), native event anchor 유지 |
| source | manufactured external source, \(R=10^{-15}\) photons/(H nucleus·s), 13.7–100 eV, \(dN/dE\propto E^{-2}\) |
| 배경 | 상속된 analytic FLRW, proper density 변화 및 source/absorber mask 유지 |
| 결합 에너지 | HI 13.598434599702, HeI 24.587389011, HeII 54.41776 eV; fit cutoff와 구분 |
| 수 표현 | 저장된 binary64 값을 정확히 올림; CSV의 십진 문자열을 별도의 exact real 정의로 바꾸지 않음 |
| outflow | 현재 first2는 0; nonzero 입력은 imported domain guard가 거부 |

위 수치는 관측 우주론 결과가 아니라 고정한 실험 입력의 정의다. `q_f`와 `lambda_if`는 captured native midpoint 값의 exact lift다. 수학적 midpoint에서 연속 함수를 재평가한 값과의 작은 realification 차이도 `delta_q`, `delta_lambda`에 포함한다. 이 차이를 0으로 놓지 않는다. [근거: `inputs/e13c2/inputs/upstream_e13c1/`, `inputs/e13c2/code/continuous_defect.py`, `THEORY.md` §1.]

## 3. 보정식과 비용 감소의 이유

한 사건 구간에서 광자 수를 \(P\), 종별 흡수율을 \(\lambda_i\), 총 흡수율을 \(\Lambda=\sum_i\lambda_i\)라 두면

\[
P'=q-\Lambda P,\qquad P_f'=q_f-LP_f,\qquad L=\sum_i\lambda_{if}.
\]

차이는 \(e=P-P_f\), 계수 차이는 \(\delta q=q-q_f\), \(\delta\Lambda=\Lambda-L\)다. Frozen 해에 대한 forcing을

\[
r=\delta q-\delta\Lambda P_f
\]

로 만들고, 첫 coefficient-variation response를

\[
e_1'+Le_1=r,\qquad e_1(0)=e_a
\]

로 정의한다. \(Lh\)를 작은 양으로 전개하지 않는다. 다음 함수를 cancellation 없이 계산한다.

\[
J(L,h)=\frac{-\operatorname{expm1}(-Lh)}{L},\qquad J(0,h)=h.
\]

필요한 endpoint와 두 moments는 모두 한 차원 적분이다.

\[
e_1(h)=e^{-Lh}e_a+\int_0^h e^{-L(h-v)}r(v)\,dv,
\]

\[
I_0=e_aJ(L,h)+\int_0^h J(L,h-v)r(v)\,dv,
\]

\[
I_E=E_0e_aJ(L+1,h)+\int_0^h E(v)J(L+1,h-v)r(v)\,dv.
\]

종별 count와 absorption energy의 일관된 1차 보정은, 여기서 에너지를 eV 단위로 쓰면,

\[
\Delta A_i^{(1)}=\int_0^h\delta\lambda_iP_f\,dv+\lambda_{if}I_0,
\]

\[
\Delta B_i^{(1)}/\epsilon=\int_0^hE\delta\lambda_iP_f\,dv+\lambda_{if}I_E.
\]

Heat는 \(\Delta H_i^{(1)}=\Delta B_i^{(1)}/\epsilon-\chi_i\Delta A_i^{(1)}\), redshift energy는 \(I_E\)다. Direct 항과 광자장 response를 따로 보존한다. Source number/energy 차이도 같은 quadrature로 적분한다. [새 유도: `THEORY.md` §§2–4; 구현: `code/exponential_correction.py`.]

이 방법은 각 quadrature node마다 내부 convolution을 다시 풀 필요가 없다. 공통 nodes/weights에서 계수와 frozen stock을 한 번 평가해 endpoint, 두 moments, direct 항과 source 항을 함께 누적한다. 주 구현은 Gauss–Legendre 8/12점을 사용했다. NumPy의 `leggauss`는 초기 근을 제공하고, Legendre recurrence/Newton 보정과 moments 확인을 longdouble에서 수행한다. Gauss–Legendre의 다항식 정확도 성질은 [NumPy 공식 문서](https://numpy.org/doc/2.3/reference/generated/numpy.polynomial.legendre.leggauss.html)에 정의되어 있다. 그것만으로 이번 비다항식 integrand의 오차를 보증하지 않으므로 GL8/12와 별도 Decimal 계산을 비교했다.

경계에서는 이전 보정량을 0으로 reset하지 않는다. Native endpoint와 다음 captured `f0`의 representation 차이를 포함해 incoming correction을 넘긴다. Energy anchor는 각 사건의 기존 값을 사용한다. 저장한 ledger 최대값은 **segment 내부의 1차 ledger**다. 전체 macro의 anchor seam까지 포함한 새 엄밀한 energy certificate를 계산했다는 주장은 하지 않는다. [근거: `code/exponential_correction.py::path_work`, `THEORY.md` §8.]

## 4. 여섯 국소 control과 독립 구현

먼저 E13C2가 사용한 동일한 여섯 local segment만 계산했다. 각 control은 captured `f0`와 \(e_a=0\)을 쓴다. 주 구현 GL8/12와 별도 contributor가 작성한 70자리 Decimal GL12/20을 비교했다. Decimal contributor는 부모의 coefficient 정의와 Gauss rule helper만 공유하고, frozen field, 지수 kernel, Fubini moments, direct/response, heat와 ledger 계산을 새로 구현했다. 기존 continuous collocation 및 oracle은 실행하지 않았다. [근거: `evidence/decimal/METHOD_AND_RESULTS_KO.md`, `READONLY_SELF_CHECK.json`, `RUN_RECEIPT.json`.]

이 절의 local photon/count 단위는 photons/(H nucleus·dη), energy/heat는 eV/(H nucleus·dη)다. 다음 절의 macro 결과는 spectral weight를 적용한 뒤의 per-H 값이다.

| 검사 | 관측된 최대값 | 사전 기준 |
|---|---:|---:|
| 주 구현 heat defect 대 저장된 local continuous reference 상대오차 | 9.8204725×10⁻⁹ | 0.01 |
| 독립 Decimal heat defect 대 같은 reference 상대오차 | 9.8169628×10⁻⁹ | 0.01 |
| 주 구현 GL8/12 heat defect 상대 차이 | 1.9533766×10⁻¹¹ | 10⁻⁵ |
| 주 구현 대 새 Decimal, photon/count 절대 차이 | 2.6043265×10⁻²⁴ | 10⁻²² |
| 주 구현 대 새 Decimal, absorption energy 절대 차이 | 2.8135450×10⁻²³ eV | 10⁻²⁰ eV |
| 독립 Decimal GL12/20 number 차이 | 8.4880658×10⁻⁵³ | 10⁻²⁵ |
| 독립 Decimal GL12/20 energy/heat 차이 | 1.1628642×10⁻⁵¹ eV | 10⁻²⁴ eV |

Photon/count의 absolute floor는 10⁻²⁵, energy/heat의 floor는 10⁻²⁴ eV다. Reference가 floor 아래인 항에는 상대오차를 주장하지 않고 `UNRESOLVED_BELOW_ABSOLUTE_FLOOR`를 기록한다. 이번 여섯 총 열결함은 모두 floor보다 컸다. 종별 영값은 그대로 남긴다. [근거: `PLAN.json`, `evidence/LOCAL_ACCEPTANCE.json`, `evidence/decimal/DECIMAL_RESULTS.json`.]

실제 primary kernel의 영흡수율, 영구간, 큰 감쇠율의 pointwise identity, 상수계수와 일반 incoming stock 검사는 **64/64 PASS**였다. 별도의 exact Fraction exponential-polynomial 대수 검산은 **317/317 PASS**였다. 유한한 exact control은 일반 bound의 수치 enclosure가 아니다. 새 검산을 이전 E13C2의 17개 검산과 섞어 세지 않는다. 두 suite의 판정과 as-run code identity는 local/final gate에 실제로 포함되어 있다. Local gate **104개**가 통과한 뒤에만 first2 확장을 실행했다. [근거: `evidence/KERNEL_CHECKS.json`, `evidence/theory/THEORY_CHECKS.json`, `code/verify_correction.py`.]

## 5. first2 전체 경로의 signed 결과

다음 표의 단위는 eV/H nucleus다. \(D_H\)는 저장된 E13C2 continuous-minus-frozen total heat, \(C_H\)는 이번 GL12 1차 보정이다. 마지막 열은 \(|C_H-D_H|/|D_H|\)다.

| Mode | Macro | 저장된 \(D_H\) | 새 보정 \(C_H\) | 열결함 상대오차 |
|---|---:|---:|---:|---:|
| OFF | 1 | −8.893505598948×10⁻¹³ | −8.893505587234×10⁻¹³ | 1.3171223×10⁻⁹ |
| OFF | 2 | −1.713709187331×10⁻¹² | −1.713709159909×10⁻¹² | 1.6001431×10⁻⁸ |
| KF | 1 | −8.908839468849×10⁻¹³ | −8.908839456838×10⁻¹³ | 1.3482574×10⁻⁹ |
| KF | 2 | −1.714948084476×10⁻¹² | −1.714948056988×10⁻¹² | 1.6028663×10⁻⁸ |
| GM | 1 | −9.154181407115×10⁻¹³ | −9.154181390629×10⁻¹³ | 1.8008593×10⁻⁹ |
| GM | 2 | −1.734770429942×10⁻¹² | −1.734770401355×10⁻¹² | 1.6479380×10⁻⁸ |

여섯 보정 모두 열결함의 음의 부호를 유지한다. 종별 count defect도 현재 E13C2의 HI/HeI 음수, HeII 양수 패턴을 재현한다. Macro 종별 count defect의 최대 상대오차는 **3.3304869×10⁻⁸**, absorption energy defect의 최대 상대오차는 **2.8214711×10⁻⁸**다. 이 두 값은 signed defect 비교의 관측 결과이며 별도 physical budget을 정의하지 않는다. [근거: `evidence/paths_gl12/RESULTS.json`, `evidence/FINAL_ACCEPTANCE.json`.]

전체 경로 GL8/12 열결함의 최대 상대 차이는 **4.7004319×10⁻¹³**이다. 따라서 이번 관측에서는 구적 차이보다 계수변화 근사의 잔여오차가 더 크다. 이 판단은 두 차수와 저장된 기준해의 비교에 한정된다. Arbitrary stiff interval에서 GL12가 자동으로 충분하다는 결론은 아니다. 실제 최대 frozen optical depth는 **0.6405675704**였다. [동일 근거.]

보정 뒤 reference와 남은 total-heat 차이는 가장 큰 경우 **2.8587941×10⁻²⁰ eV/H**다. 이를 기존 frozen total heat로 나눈 진단값의 최대치는 약 **2.4318042×10⁻¹⁵**다. 오래된 gas algebraic `TOL`로 photo heat 차이를 표시하면 최대 **4.5802931×10⁻⁶ TOL**이다. 이 수치는 **E13C2 defect projection − E13C3 correction projection**의 차이이며, native baseline representation까지 인증한 전체 continuum error가 아니다. 이전 E13C2의 열결함 자체가 약 142–278 old TOL이었던 것과 나란히 읽을 수 있지만, old TOL을 새로운 연속계수 정확도 기준으로 채택하지 않는다. [근거: `evidence/FINAL_ACCEPTANCE.json::summary.macro_comparisons`; inherited baseline 한계: `inputs/e13c2/REPORT_KO.md`.]

Corrected photon endpoint는 모든 계산된 segment에서 비음수였으며 최소값은 **0**이었다. Zero support도 포함하므로 strictly positive라고 쓰지 않는다. Native baseline에 보정을 더한 aggregate absorption/heat의 비음수 검사도 통과했다. 구간 내부 전체에 대한 positivity enclosure나 실제 gas update의 positivity를 증명한 것은 아니다. [근거: `code/exponential_correction.py`, `evidence/paths_gl12/RESULTS.json`.]

## 6. 정확히 닫힌 ledger가 보증하는 것

Kernel identities

\[
e^{-L(h-v)}+LJ(L,h-v)=1,
\]

\[
E_h e^{-L(h-v)}+(L+1)E(v)J(L+1,h-v)=E(v)
\]

때문에 일관된 1차 moments의 number/energy ledger는 exact arithmetic에서 정확히 닫힌다. 전체 first2에서 관측한 최대 segment 잔차는 number **5.4234187×10⁻³¹**, energy **8.5071760×10⁻³⁰ eV**였다. [유도: `THEORY.md` §3; 관측: `evidence/FINAL_ACCEPTANCE.json`.]

그런데 보정된 field \(P_c=P_f+e_1\)을 원래 연속 계수 식에 대입하면

\[
\boxed{P_c'+\Lambda P_c-q=\delta\Lambda e_1}
\]

가 남는다. 실제 full-coefficient moment에는 \(\int\delta\lambda_i e_1\)도 들어간다. 따라서 1차 ledger closure는 원래 모델을 정확히 풀었다는 증거가 아니다. 총 opacity 변화가 0이어도 종별 opacity 변화가 서로 상쇄할 수 있어, photon field는 정확하지만 종별 흡수·heat에는 잔여항이 남는 경우가 있다. 이 예외도 새 exact control에 포함했다. [유도·검산: `THEORY.md` §4, `evidence/theory/THEORY_CHECKS.json`.]

Incoming mismatch가 \(\eta_a\) 이내이고 true/frozen opacity가 비음수라고 하자. 구간 전체의 실제 적분

\[
D_L=\int|\delta\Lambda|,\qquad
B_r=\int\bigl(|\delta q|+|\delta\Lambda|P_f\bigr)
\]

에 대해 다음 bound를 얻는다.

\[
\|e-\widetilde e_1\|_\infty
\le\eta_a+D_L\bigl(|\widetilde e_a|+B_r\bigr).
\]

Weighted moment와 species bounds는 `THEORY.md` §§5–6에 분리해 유도했다. Incoming \(e_a\)도 coefficient variation과 같은 순서여야 전체 remainder를 균일하게 2차라고 부를 수 있다. Incoming을 독립적인 \(O(1)\)로 놓으면 \(D_L|e_a|\)가 남는다. [새 유도: 동일 문서.]

현재 코드의 \(D_L,B_r\)는 quadrature 추정치이며 `variation_integrals_are_certified_bounds=false`다. 적분의 절댓값에서 생기는 비매끄러움까지 interval enclosure로 다룬 것이 아니다. 이번 루프는 **rigorous uniform error certificate를 확립하지 않았다.**

## 7. 실제 실행, 검토 중 수정, 재현성

| 실제 새 실행 | 내부 경과시간 | 결과 |
|---|---:|---|
| Primary local GL8 | 0.373135 s | exit 0 |
| Primary local GL12 | 0.373827 s | exit 0 |
| Primary first2 GL8 | 1.151899 s | exit 0 |
| Primary first2 GL12 | 1.220697 s | exit 0 |
| 새 Decimal 6 controls GL12/20 | 0.543713 s | exit 0; 외부 process wall 0.591616 s |
| 새 exact algebra | 외부 process 0.169045 s | 317 PASS, exit 0 |

Primary code SHA-256 as run은 `751a3899d2e78261be872c67a7730e3333234d4590c1a7ead1897e0ad51a5e69`다. Decimal 새 code는 `b3d5830363911c892039547623ade74eaad0fc311808cf46eec11b6613650903`, exact checker는 `0e4f5e2824440fc0ef4f3b445d4e53edcef02c145105a2ca9d176940c04fa213`이다. 실행 후 코드 identity를 결과와 대조했다. [근거: 각 실행 receipt 및 `evidence/FINAL_ACCEPTANCE.json`.]

이론 검토에서는 captured midpoint 값과 mathematical midpoint 값의 구별을 명시했다. 이에 맞춰 Lipschitz 설명식도

\[
D_L\le\|\Lambda'\|_\infty h^2/4+h|\Lambda(m)-L|
\]

로 바로잡았다. 마지막 항은 exact midpoint freezing일 때만 0이다. 이는 원래 구현과 일치하도록 문서 가정을 분명히 한 수정이며, 수치 판정 기준이나 실행 결과를 변경하지 않았다. 새로운 과학 계산의 첫 실행은 모두 exit 0이었으며, 실패한 결과를 삭제하고 성공으로 대체한 이력은 없다. 검토자의 세부 기록과 최종 decision은 별도 독립 심사 파일에 남긴다.

기본 재현 명령은 입력과 payload의 identity 및 저장된 E13C3 비교만 검증한다. 실행 출력은 새로운 외부 디렉터리에 쓴다. 선택적 `--recompute`도 새 E13C3 primary correction과 focused kernel만 다시 계산하며, 이전 continuous reference나 gas/native history를 재실행하지 않는다. 선택적 실행의 새 출력과 저장된 reference 사이의 parity/accuracy는 이 wrapper가 다시 판정하지 않는다. 이를 `new_output_parity_checked=false`, `new_output_accuracy_verdict=NOT_EVALUATED`로 명시했고, wrapper의 `PASS_SCOPED`는 저장된 증거 검증에만 적용한다. 자세한 명령과 의존성은 `README.md`에 있다.

## 8. 다음 최소 연구 노드

이번 관측으로 fixed-path의 저비용 보정 후보는 확보했다. 다음 수학적 병목은 **관측된 작은 remainder를 저장된 reference 없이도 안전하게 제한할 수 있는가**다. 다음 노드는 `E13C4_LOCAL_REMAINDER_ENCLOSURE_ON_FIXED_GAS_PATH`로 둔다.

첫 범위는 같은 여섯 local controls, 같은 source/마스크/anchor, \(e_a=0\)이다. \(D_L,B_r,H_h,H_0,H_E,V_i,V_{E,i}\) 또는 원래 방정식의 residual \(\delta\Lambda e_1\)을 이용한 bounds를 outward rounding/enclosure로 구현할 수 있는지 판정한다. 종별 \(\delta\lambda_i e_1\), source·redshift·representation 항을 빠뜨리지 않는다. 저장된 E13C2/E13C3 결과는 read-only 비교 자료다. Reference 자체의 수치 불확실성도 구별해야 하며, sampled quadrature를 enclosure라고 바꾸어 부르지 않는다.

Bound의 엄밀성과 sharpness는 별도로 보고한다. Physical accuracy budget은 receiver owner가 별도로 정의할 사안이며, 여기서 1%나 old algebraic TOL로 대신 정하지 않는다. Local enclosure를 제대로 구성하기 전에는 전체 path로 확대하지 않는다. Incoming uncertainty를 전파하지 못하면 full-path certificate를 주장하지 않는다. 구체적인 입력·중단 조건은 `NEXT_DAG.json`, 이어받을 지시문은 `NEXT_CODEX_PROMPT_KO.md`에 적었다.

## 9. 유지한 상태와 전달 범위

| Gate | 상태 |
|---|---|
| baseline RCT | OFF |
| actual atomic photon / heat / recoil | null |
| physical / production | HOLD / HOLD |
| HE-F2 / F09 | OPEN / OPEN |
| receiver adoption | SEPARATE |
| legacy Gamma alias 3.543295 | FAIL |
| uniform interval certificate | NOT_ESTABLISHED |

저장된 gas path, source, atomic cross-section uncertainty, anisotropic redshift나 장기 history에 대한 승격은 없다. 현재 draft PR의 같은 연구 branch에 새 packet을 additive로 반영하는 범위이며 merge나 production default 변경은 포함하지 않는다. 전체 archive에는 raw inputs와 node evidence가 들어가고, Git projection은 코드·보고서·compact evidence를 제공한다. 실제 commit, archive identity, Drive/Dropbox의 저장 acknowledgement는 별도 delivery receipt에서 확인한다. Upload acknowledgement와 remote restore verification은 서로 다른 증거 수준이다.
