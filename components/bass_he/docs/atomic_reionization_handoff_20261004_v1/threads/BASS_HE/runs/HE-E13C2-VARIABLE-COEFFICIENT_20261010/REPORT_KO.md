# BASS_HE E13C2 — 같은 gas 경로에서 광자 계수의 시간 변화가 만드는 편향

2026-10-10 · GPT-6 Astra 물리 연구 루프 · 연구 결과, 독립 판정의 범위는 `INDEPENDENT_REVIEW.json` 참조

## 1. 이번에 얻은 결과

E13C1이 남긴 다음 노드 `E13C2_VARIABLE_COEFFICIENT_BIAS_ON_FIXED_GAS_PATH`를 실행했다. OFF/KF/GM의 저장된 첫 두 macro transaction, 총 14,652개 event segment에서 gas 경로를 고정하고 광자 방정식의 source와 opacity를 연속 평가했다. 각 mode의 첫 구간에서 생긴 광자 차이는 둘째 구간까지 운반했다. 새로운 gas 해를 구하거나 기존 native 전체 campaign을 다시 실행하지 않았다.

**여섯 transaction 모두 연속계수 계산의 총 primary photoheating이 frozen 계산보다 작았다.** 상대 차이는 약 \(-1.46\times10^{-7}\)에서 \(-2.16\times10^{-7}\)다. HI·HeI 흡수 수는 감소하고 HeII 흡수 수는 증가했다. 특히 첫 macro에서 HeI 계수 변화의 직접 기여는 양수지만, 광자장 변화의 기여가 더 큰 음수여서 순변화가 음수가 된다. 종별 opacity 변화만으로 흡수와 열의 변화를 판단할 수 없음을 실제 저장 경로에서 확인했다.

이 결과는 **지정한 manufactured source와 affine gas 경로에 대한 유한 수치 결과**다. 관측 우주론, 실제 RCT 방출 스펙트럼, 완전 결합 gas 응답 또는 모든 시간 단계에 대한 정확도 판정으로 확대하지 않는다. `physical=HOLD`, `production=HOLD`를 유지한다.

결과 원본은 [fine 결과](evidence/defect_rtol_2e11/RESULTS.json), [정밀도 대조 및 검증](evidence/VERIFICATION_FINAL.json), [독립 Decimal reference](evidence/ORACLE_RESULTS.json)에 있다. 수식의 정의와 유도는 [THEORY.md](THEORY.md)에 있다.

## 2. 어느 상태에서 이어갔는가

| 항목 | 고정한 근거 |
|---|---|
| 저장소 | `cosmosapjw-quantum/BASS_HE` |
| 연구 branch | `research/shared-c64-crossrepo-20260928` |
| intake HEAD | `81c1dacc1439807d41dc2684619dee499f3e06b0` |
| intake tree | `bbbbaa0fcd39d6993699db0034275b1761215666` |
| 이전 연구 노드 | `HE-E13C1-PHOTON-PHYSICS_20261010` |
| 이전 core commit | `f7199c5c100578fa345b026cd6d4ac8e983e50a9` |
| 원 archive | `BASS_HE_E13C_PHOTON_PHYSICS_20261010_v1.zip` |
| 원 archive SHA-256 | `06b5c02afb92e356ec66072a918e014f61fab5a795f26024fae55ca4d93acb33` |
| 원 archive 크기 | 4,096,240 bytes |

원 archive를 Drive에서 실제로 받아 SHA-256과 ZIP CRC를 확인했다. repo intake의 26개 문서는 Git blob identity를 대조했다. 이번 계산에 필요한 입력은 archive에서 그대로 복사하고 별도의 상대경로 SHA-256 manifest로 고정했다. 세부 근거는 [입력 manifest](inputs/INPUT_FILES.json)와 [snapshot reconciliation](inputs/SNAPSHOT_RECONCILIATION.json)에 있다.

같은 날짜의 `BASS_HE_E13C1_PHOTON_HEATING_20261010_v1.zip`은 동일 E13B parent에서 나온 별도의 미게시 draft였다. SHA-256은 `ed5ab041e678ff61a46686ecf5e44b32deb030b95d7318b15dc32a0dd6ba6bd9`다. 그 draft의 RCT 조성 응답과 late k7/k59 입력 문제는 별도 상태로 보존했다. 현재 게시된 PHOTON_PHYSICS의 NEXT_DAG가 이번 순서를 결정한다. 오래된 top-level 시작문이나 PR 설명의 연구 요약을 최신 계산 완료 상태로 대신하지 않았다.

**입력 개수의 시간 순서:** 두 primary 실행 당시 manifest는 23개 파일이었으며, 두 원 `RESULTS.json`의 `input_hashes_verified=23`을 보존했다. 이후 독립 oracle의 provenance를 자체 완결적으로 전달하기 위해 원 `code/photon_green.py`를 24번째 파일로 추가했다. 이 파일은 primary 계산에서 import하거나 호출하지 않는다. 최종 패키지의 24개 파일은 모두 다시 hash 확인했다. 23을 24로 소급해서 고치지 않았다.

## 3. 고정한 물리 문제와 단위

시간 변수는 \(s=\ln a\), characteristic 좌표는 \(\eta=s+\ln(E/\mathrm{eV})\)다. \(P\)는 수소 원자핵 하나·단위 \(\eta\)당 광자 수다. 각 native event segment에서

\[
E(u)=E_0e^{-u},\qquad
P'=q-\Lambda P,\qquad
\Lambda=\lambda_{\mathrm{HI}}+\lambda_{\mathrm{HeI}}+\lambda_{\mathrm{HeII}},
\]

\[
\lambda_i=\frac{c\,n_i\sigma_i(E)}{H},\qquad
q=\frac{R}{(1/E_{\min}-1/E_{\max})E H}
\]

를 사용했다. \(u=s-s_a\)이고 prime은 \(s\) 미분이다. Source support 내부에서 \(R=10^{-15}\) photons/(H nucleus·s), \(E_{\min}=13.7\) eV, \(E_{\max}=100\) eV다. 이 식은 \(dN/dE\propto E^{-2}\)인 외부 source의 단위 log-energy 주입을 나타낸다. 별도 RCT 광자를 primary source에 넣지 않았다.

Gas의 \(x=x_{\mathrm{HII}},y=x_{\mathrm{HeII}},z=x_{\mathrm{HeIII}}\)는 저장된 macro 양끝 값 사이의 affine 함수다. Target 밀도는 \(n_H(1-x),n_{He}(1-y-z),n_{He}y\) 순서다. Proper 밀도는 \(a^{-3}\)으로 변하고, Hubble rate는 pinned \(\Omega_r,\Omega_m,\Omega_\Lambda,H_0\)의 FLRW 식을 연속 평가한다. Config의 초기값은 redshift 12, \(T=2000\) K, \(x=0.1,y=0.05,z=0.9\)다. 이번 작업에서 이 gas history를 새로 적분하지 않았다.

| 정의 | HI | HeI | HeII |
|---|---:|---:|---:|
| 가열 계산의 \(\chi_i\), eV | 13.598434599702 | 24.587389011 | 54.41776 |
| fit support cutoff, eV | 13.6 | 24.59 | 54.42 |

두 행은 다른 역할이며 서로 치환하지 않았다. Cross-section의 함수형과 상수는 pinned native source를 따랐다. Verner 저자 제공 [photoionization fit 자료](https://www.pa.uky.edu/~verner/photo.html)는 함수의 출처를 확인하는 데 사용했으며, 이번 수치 일치 검사가 atomic fit 자체의 오차를 검증하지는 않는다.

CSV와 source의 숫자들은 원 binary64 값을 정확히 lift한다. 예컨대 문자열을 고정밀 실수의 정확한 십진값으로 새롭게 해석하지 않았고, \(\pi\)도 source의 binary64 `math.pi`를 lift했다. 이 규약을 두 독립 구현에 동일하게 적용했다.

## 4. 차이 방정식과 흡수·가열의 분해

Captured midpoint-frozen 해를 \(\widehat P\), 연속계수 해를 \(P\), 차이를 \(e=P-\widehat P\)로 둔다. \(\delta q=q-q_m\), \(\delta\lambda_i=\lambda_i-\lambda_{i,m}\), \(\delta\Lambda=\sum_i\delta\lambda_i\)이면

\[
e'=\delta q-\delta\Lambda\widehat P-\Lambda e.
\]

이 식을 직접 적분했다. 큰 두 photon 해를 독립적으로 계산한 뒤 뺄 때 생기는 작은 차이의 소실을 줄이기 위해서다. 이 수식은 근사 선형화가 아니다. 지정한 두 scalar 문제의 **정확한 차이 방정식**이다. Green 함수

\[
G(u,v)=\exp\!\left[-\int_v^u\Lambda(w)\,dw\right]
\]

로 쓰면

\[
e(u)=G(u,0)e_a+
\int_0^uG(u,v)[\delta q(v)-\delta\Lambda(v)\widehat P(v)]\,dv.
\]

Frozen damping \(e^{-\Lambda_m(u-v)}\)을 사용하는 다른 exact 표현에서는 forcing에 \(\widehat P\) 대신 \(P\)가 들어가야 한다. 두 표현을 섞지 않았다.

관측량 \(J_{w,i}=\int w\lambda_iP\,du\)의 차이는

\[
\Delta J_{w,i}=
\underbrace{\int w\,\delta\lambda_i\widehat P\,du}_{\text{직접 계수 변화}}
+\underbrace{\int w\,\lambda_i e\,du}_{\text{광자장 변화}}.
\]

\(w=1\)이면 흡수 수 \(A_i\), \(w=E\)이면 eV 단위 흡수 에너지 \(B_i^{\rm eV}\), \(w=E-\chi_i\)이면 eV 단위 가열 \(Q_i^{\rm eV}\)다. 에너지의 cgs 변환은 \(\epsilon=1.602176634\times10^{-12}\) erg/eV를 곱한다. 정확히

\[
\Delta Q_i^{\rm eV}=\Delta B_i^{\rm eV}-\chi_i\Delta A_i.
\]

두 항의 이름은 이 기준 해를 택했을 때의 수학적 분해다. Coupled gas의 원인별 반사실 실험이나 RCT 전체 효과로 해석하지 않는다.

### 차수와 광학적 두께

같은 incoming stock으로 시작하는 smooth event-free 한 구간에서 \(p=\widehat P(m)\), \(f=q-\Lambda p\), \(d=q'-\Lambda'p\)라 두면

\[
\Delta P_h=\frac{h^3}{24}
(q''-\Lambda''p+2\Lambda q'-2\Lambda'q)+O(h^4),
\]

\[
\Delta A_i=\frac{h^3}{24}
(\lambda_i''p+2\lambda_i'f-2\lambda_i d)+O(h^4),
\]

\[
\Delta B_i^{\rm eV}=\frac{E_mh^3}{24}
[\lambda_i''p+2\lambda_i'(f-p)-2\lambda_i d]+O(h^4).
\]

Energy 식의 추가 \(-2\lambda_i'p\) 항은 흡수 시점 변화와 redshift 에너지 가중을 반영한다. 구간 내부의 \(e\)는 일반적으로 \(O(h^2)\), 같은 초기값을 갖는 끝점과 누적 moment의 leading difference는 \(O(h^3)\)다. 적절한 smoothness와 안정성 조건을 추가해야 global \(O(h^2)\)를 논할 수 있다.

여기서 macro 폭은 약 \(5.2083333335\times10^{-7}\)이지만 실제 최대 \(\Lambda_m h\simeq0.64057\)이다. 따라서 위 cubic 식을 실제 오차의 인증값으로 사용하지 않았다. 계산값은 full defect ODE에서 얻었다. [THEORY.md](THEORY.md)는 base damping을 그대로 유지한 1차 coefficient-variation correction \(e_1\)과

\[
e-e_1=-\int_0^u e^{-\Lambda_m(u-v)}\delta\Lambda(v)e(v)\,dv,
\qquad
\sup|e-e_1|\le D_\Lambda B_r
\]

를 유도한다. 마지막 bound에 필요한 적분량을 엄밀히 둘러싼 enclosure는 이번에 계산하지 않았다.

## 5. 실제 수치 결과

모든 부호는 **continuous − frozen**이다. 아래의 heat는 한 macro transaction의 primary photoheating이다. Step 2의 photon correction은 step 1에서 이어지지만 표의 heat 적분은 step 2 구간에 해당한다.

| mode | step | \(\Delta Q_{\rm total}\), eV/H nucleus | \(\Delta Q/Q_{\rm frozen}\) | \(\epsilon\Delta Q/10^{-26}\) |
|---|---:|---:|---:|---:|
| OFF | 1 | −8.89350559895×10⁻¹³ | −2.10120256791×10⁻⁷ | −142.489669 |
| OFF | 2 | −1.71370918733×10⁻¹² | −1.45774927029×10⁻⁷ | −274.566482 |
| KF | 1 | −8.90883946885×10⁻¹³ | −2.10482538977×10⁻⁷ | −142.735344 |
| KF | 2 | −1.71494808448×10⁻¹² | −1.45880312987×10⁻⁷ | −274.764975 |
| GM | 1 | −9.15418140712×10⁻¹³ | −2.16279054520×10⁻⁷ | −146.666156 |
| GM | 2 | −1.73477042994×10⁻¹² | −1.47566487638×10⁻⁷ | −277.940865 |

마지막 열의 분모는 원 gas solve의 energy algebraic residual tolerance, \(10^{-26}\) erg/H nucleus다. **그 열이 1보다 크다는 사실로 기존 solver나 physical model이 실패했다고 판정하지 않는다.** 기존 tolerance가 continuum time-discretization budget이라는 계약은 없다. 이 수치는 이미 작게 풀린 대수 잔차와 구별해야 하는 계수 freezing 효과가 있음을 보여준다.

종별 count 결과는 다음과 같다.

| mode | step | \(\Delta A_{HI}\), /H | \(\Delta A_{HeI}\), /H | \(\Delta A_{HeII}\), /H |
|---|---:|---:|---:|---:|
| OFF | 1 | −1.802793109×10⁻¹³ | −4.990005596×10⁻¹⁶ | +4.151218293×10⁻¹⁵ |
| OFF | 2 | −3.089163236×10⁻¹³ | −1.395308876×10⁻¹⁵ | +4.173712235×10⁻¹⁵ |
| KF | 1 | −1.806230995×10⁻¹³ | −4.990003636×10⁻¹⁶ | +4.174944701×10⁻¹⁵ |
| KF | 2 | −3.091602005×10⁻¹³ | −1.395308373×10⁻¹⁵ | +4.197233463×10⁻¹⁵ |
| GM | 1 | −1.861237176×10⁻¹³ | −4.989973636×10⁻¹⁶ | +4.554567121×10⁻¹⁵ |
| GM | 2 | −3.130622280×10⁻¹³ | −1.395299887×10⁻¹⁵ | +4.573572754×10⁻¹⁵ |

HeII count의 상대 변화는 약 \(+6.05\times10^{-6}\)에서 \(+1.97\times10^{-5}\)다. 해당 channel의 작은 baseline에 대한 상대값이므로 총 가열의 상대 변화와 직접 비교하지 않는다. HeII count·heat의 양의 기여가 HI heat의 음의 기여를 상쇄하기에는 작다.

### 첫 OFF macro: 직접 효과만 보면 부호를 잘못 판단하는 예

| channel | 직접 \(\Delta A_i\), /H | 광자장 기여, /H | 합계, /H |
|---|---:|---:|---:|
| HI | −1.512890249×10⁻¹⁴ | −1.651504084×10⁻¹³ | −1.802793109×10⁻¹³ |
| HeI | +2.365058876×10⁻¹⁶ | −7.355064472×10⁻¹⁶ | −4.990005596×10⁻¹⁶ |
| HeII | +4.201211572×10⁻¹⁵ | −4.999327958×10⁻¹⁷ | +4.151218293×10⁻¹⁵ |

이는 첫 macro의 결과다. 세 mode의 둘째 macro에서는 HeI 직접항 자체도 음수이므로, “직접 양수·최종 음수”라는 설명을 여섯 transaction 전체에 적용하지 않는다. 둘째 macro는 들어오는 광자장 차이까지 포함한다. 각 mode는 자체 저장 gas 경로를 사용했으므로 mode 간 숫자의 차이를 새 coupled OFF→ON 인과 효과로 부르지 않는다.

Gas 방정식 방향으로의 투영은

\[
(\Delta A_{HI},\; (\Delta A_{HeI}-\Delta A_{HeII})/f_{He},\;
\Delta A_{HeII}/f_{He},\;\epsilon\sum_i\Delta Q_i^{\rm eV})
\]

이다. 이것은 저장된 transaction에 대한 photo forcing 변화다. Jacobian을 역으로 작용시키거나 gas Newton을 다시 풀지 않았으므로 gas state의 실제 변화량은 아니다.

## 6. 무엇을 어떻게 확인했는가

### Primary 적분과 precision 대조

16개 defect·moment 변수를 node별로 적분했다. Coefficient는 이 host에서 64 significand bits인 `np.longdouble`, ODE state는 binary64다. dtype 이름이 `float128`으로 표시될 수 있어도 128-bit 유효 정밀도라고 부르지 않는다. 환경은 Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0이었다. [SciPy 1.17.0 공식 문서](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.solve_ivp.html)의 DOP853을 사용했다.

사전 설정은 `rtol=2e-9`와 `2e-11`, component `atol=1e-25`, 정규화한 segment 시간에서 `max_step=0.25`였다. 같은 새 E13C2 문제의 두 precision 계산을 수행했고 둘 다 exit 0이었다. 전체 projection의 두 결과 차이는 기존 algebraic TOL 단위로 최대 **1.2121859072×10⁻⁹**, 사전 안정성 기준은 0.01이었다. 이는 적분 정밀도 변화에 대한 안정성 검사이며 physical discretization 허용오차가 아니다.

첫 실행은 약 7.11초, fine 실행은 약 7.61초였고, 최대 RSS는 각각 107,356 KiB와 109,480 KiB였다. 별도 native binary 또는 외부 simulation은 실행하지 않았다. 원 결과·node별 차이·로그를 보존했다.

### 별도 구현의 70자리 Decimal oracle

다른 contributor가 표준 라이브러리만으로 12점·20점 Gauss–Legendre collocation과 Decimal 선형계 풀이를 구현했다. Primary DOP853 코드와 원 `photon_green.py` 함수를 호출하지 않았다. 물리 정의와 입력은 의도적으로 공유하지만 수치 적분 방법과 구현은 분리했다.

실제 입력에서 미리 정한 여섯 local segment를 골랐다. 13.7, 35, 70, 55, 99 eV 근처와 HeI threshold를 막 지난 segment가 포함된다. Oracle은 각 구간의 captured `f0`로 시작하는 **국소 reference**다. Primary의 별도 local control과 비교했으며, 둘째 macro까지 correction을 운반하는 모든 node의 독립 고정밀 재실행으로 표현하지 않는다.

| 검사 | 실제 최대값 | 사전 기준 |
|---|---:|---:|
| Primary–Decimal \(P,A_i\) 절대차 | 7.6341288351×10⁻²⁴ | 10⁻²² |
| Primary–Decimal \(B_i^{\rm eV}\) 절대차 | 5.1048918360×10⁻²³ | 10⁻²⁰ eV |
| Decimal 20점–12점 number 차이 | 3.0633264815×10⁻⁴² | 10⁻²⁵ |
| Decimal 20점–12점 energy 차이 | 4.1967541098×10⁻⁴¹ eV | 10⁻²³ eV |

선택된 모든 collocation stage와 끝점의 photon 수가 비음수였다. 전체 primary에서는 endpoint positivity를 확인했고, 입력의 물리적 gas domain을 각 RHS 평가에서 검사했다. 이 유한 표본 체크를 interval 전체의 수치 positivity certificate로 부르지 않는다.

### Exact algebra와 회계식

표준 라이브러리 `Fraction`의 sparse polynomial로 variable-coefficient ODE의 cubic Picard jet를 계산했다. Endpoint, 일반 weighted moment, direct/feedback 분리, heat, redshift, source number/energy, ledger, constant/affine limit, Duhamel remainder를 포함한 **17/17 exact identity 검사가 실제 통과**했다. 이 검사는 smooth event-free Taylor 항등식의 구현 검산이며 remainder의 엄밀한 크기를 결정하지 않는다.

각 segment의 signed number ledger는

\[
e_b-e_a+\sum_i\Delta A_i-\Delta Q_N=0
\]

이고, eV energy ledger는

\[
E_b e_b-E_a e_a+\sum_i\Delta B_i^{\rm eV}
+\Delta Z^{\rm eV}-\Delta Q_E^{\rm eV}=0.
\]

Fine 계산의 최대 absolute residual은 각각 5.65×10⁻²⁷과 8.09×10⁻²⁶ eV다. Source를 연속 평가하므로 injection 차이 \(\Delta Q_N,\Delta Q_E\)도 남겼다. Oracle의 ledger가 더 작지만 동일 quadrature로 구성한 회계 항등식만으로 truncation error를 인증하지 않는다.

상수 coefficient에서 defect가 정확히 0이 되는 limit, 음의 초기 stock·지원하지 않는 outflow·source flag 불일치의 rejection도 확인했다. 최초 verifier는 symbolic packet을 결과에 포함했지만 PASS gate에 연결하지 않은 문제가 검토 중 확인되었다. 이를 수정하고 별도의 `VERIFICATION_FINAL.json`을 생성했으며 최초 결과를 보존했다. 이 수정으로 물리 계산을 다시 실행하지 않았다.

## 7. 해석 범위와 남은 오차

1. **고정 gas 경로:** affine 경로의 gas time-discretization error와 coupled response는 조사하지 않았다. 이번 차이는 photon coefficient freezing에 대한 조건부 비교다.
2. **Event 규약:** native event 시점, weight, \(E_0\) anchor, 열린 구간 내부의 support mask를 유지했다. Endpoint에서 반올림된 energy로 branch를 재분류하지 않았다. Smooth Taylor 식을 사건을 가로질러 적용하지 않았다.
3. **Anchor와 IEEE 차이:** 각 segment의 exact frozen endpoint와 native binary64 endpoint의 작은 차이를 다음 correction에 전달했다. 전역적으로 하나의 exact characteristic을 새로 정의한 인증은 아니다. 일반 macro energy ledger에는 anchor reset 항이 필요하다.
4. **Outflow:** 현재 첫 두 macro의 native `outn`, `oute`는 모두 0이다. 실행 코드는 nonzero outflow 입력을 거부한다. 이후 HI domain 탈출을 포함한 일반 문제는 THEORY의 outflow 항을 구현·검증해야 한다.
5. **Frozen baseline:** `delta_A`, `delta_B`는 segment별 수학적 frozen 곡선에 대한 defect moment다. 보고된 `continuous_*_estimate`에는 captured native baseline을 더했다. Sealed E13C1와 native baseline 차이를 별도 필드에 남겼으며 그 최대 projection 차이는 기존 TOL 단위로 약 1.08×10⁻⁵다. Native baseline을 exact reference라고 부르지 않는다.
6. **Coefficient 실수화:** mathematical midpoint 재평가와 captured coefficient의 상대 차이는 opacity 최대 5.67×10⁻¹⁴, source 최대 1.65×10⁻¹⁵다. 이 구현·반올림 층과 시간 변화의 effect를 구별했다. 모든 node에 대해 고정밀 enclosure로 상계한 것은 아니다.
7. **원자물리와 우주론:** 실제 RCT photon/heat/recoil moment, atomic-fit uncertainty, spectrum-average sign, late k7/k59 stock, 실제 관측량 오차는 이번 결과로 닫히지 않는다.

## 8. 판정과 다음 연구 질문

이번에 닫을 주장은 “정의한 여섯 transaction에서 연속계수 correction의 부호·크기와 direct/feedback 분해를 계산했고, 두 적분 정밀도와 독립 local oracle 및 exact algebra가 지정 기준 안에서 일치한다”이다. 독립 최종 검토의 실제 판정·파일 identity·지적 사항은 `INDEPENDENT_REVIEW.json`과 `INDEPENDENT_REVIEW_KO.md`에 기록한다.

| Gate | 이번 작업 뒤의 상태 |
|---|---|
| E13C2 finite fixed-path 계산·검증 | `PASS_SCOPED`, 최종 독립 review 참조 |
| baseline RCT | `OFF` |
| actual atomic photon/heat/recoil | `null` |
| physical / production | `HOLD` / `HOLD` |
| HE-F2 / F09 | `OPEN` |
| receiver owner adoption | 별도 수신·채택 절차 |
| legacy Gamma alias | `3.543295 FAIL` 보존 |
| global continuum certificate | 없음 |

다음 노드는 **`E13C3_EXPONENTIAL_DEFECT_CORRECTION_ON_FIXED_GAS_PATH`**로 제안한다. E13C2에서 저장한 reference를 재사용하여, base optical depth를 그대로 유지하는 저비용 coefficient-variation correction \(e_1\)이 count·heat의 실제 차이를 얼마나 설명하는지 평가한다. 직접항과 광자장 항을 모두 포함하고 source energy/redshift ledger를 보존해야 한다. 먼저 현 first2 경로의 대표 segment에서 판별한 후 필요한 범위만 넓힌다. Frozen 단계의 1/2/4 세분 비교는 E13C2 결과를 반복하는 목적이 아니라 approximation order 또는 정량 오차 budget이라는 구체적인 미결 문제를 해소할 때만 사용한다.

성공해도 아직 정하지 않은 continuum accuracy budget을 기존 Newton TOL로 대체하지 않는다. 다음 분석은 gas·coupled owner에게 적용안을 전달할 근거를 만들며 실제 채택은 별도다. 세부 acceptance, 중단 조건, 입력, 보호 상태는 [NEXT_DAG.json](NEXT_DAG.json), 실행 인계문은 [NEXT_CODEX_PROMPT_KO.md](NEXT_CODEX_PROMPT_KO.md)에 있다.

## 9. 파일과 재현

`README.md`가 파일 지도와 명령을 제공한다. 기본 재현 명령은 기존 evidence와 input hash를 확인하는 제한된 verification이다. 선택 실행은 **이번 E13C2에 새로 정의한 계산만** 별도 출력 디렉터리에 생성한다. 기존 Rust suite, 3×384 campaign 또는 새로운 gas advancement는 호출하지 않는다.

원 numerical evidence는 불변으로 보존했다. `mpmath`와 `sympy`가 없는 환경 문제는 수학·물리 실패와 분리해 기록하고 설치 없이 Decimal/Fraction으로 처리했다. 별도 독립 reviewer의 지적과 수정 내역도 함께 보존한다. Git 게시·Drive/Dropbox 백업의 실제 완료 상태는 archive 바깥의 detached delivery receipt에 담는다. Archive 자기 hash와 외부 commit identity를 archive 안에 자기참조로 넣지 않는다.
