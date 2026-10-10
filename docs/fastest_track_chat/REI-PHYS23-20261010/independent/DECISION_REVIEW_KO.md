# PHYS23 독립 최종 판정

## 판정과 채택 범위

**판정: PROMOTE_SCOPED. 연구 단계의 결정은 PROMOTE이며 physical admission은 HOLD다.**

고정 후보 PHYS23_REPORT_KO.md와 원시 증거를 읽은 결과, 실제 HI fit의 초기 HII·heat·50000 K 온도 부호, signed curvature ratio의 단조성, 양의 spectrum으로의 확장, 상속한 수치 Jacobian에 조건부인 HeIII 전환과 같은 N/U의 반례를 아래 범위로 채택한다. 남은 필수 수정은 0개다. 유한시간 history 또는 production 실행 구간을 승격하는 판정은 아니다.

후보 보고서 SHA256은 ae030aa17c34f1eda35b092ade8ea14b5f9e967bbd446db60edfb97b063b353b, RESULTS_SUMMARY.json SHA256은 a9ec4146ad3e2fa93e2079f2ec872d3024c95ab4445b77f5ae449a5a2816562b다. 고정 시점의 32개 파일은 CANDIDATE_FREEZE.json에 기록된 크기·SHA256과 모두 일치했다. Freeze 파일 자체의 SHA256은 4c6f3f66f92c0c943b37ee9ff034a95cb6760eeeab076d4fe3d21b2906e5f49f다.

## 검토자의 독립성과 실제 읽기

검토자는 /root/phys23_decision이며 trusted host metadata가 지정한 GPT-6 Astra다. 후보 유도, exact certificate 설계, 수치 검산 설계, owner 통합에 참여하지 않았다. 별도 agent라는 역할 분리는 충족하지만 parent의 full-history context를 상속했으므로 비맹검 검토다. 독립적인 native 구현 또는 별도 physical dataset 검증으로 부르지 않는다.

Astra core, phase08 독립 판정 gate, physics/math validation과 stop rules, PHYS22 최종 판정 및 후속 handoff를 읽었다. 이번 검토에서 읽은 과학 후보와 증거는 다음과 같다.

- [통합 보고서](../PHYS23_REPORT_KO.md) 전체, [결과](../RESULTS_SUMMARY.json)의 주장·대표값·반례·실행 구분, [claim DAG](../CLAIM_DAG.json), [후속 PHYS24 계약](../PHYS24_NEXT_HANDOFF_KO.md).
- [부호 유도문](../contributions/signs/SPECTRAL_SIGN_DERIVATION_KO.md)과 exact_sign_certificate.py 전체. Exact JSON의 정의·domain·31개 assertion 및 네 다항식 certificate의 차수·부호·극값·basis 일치 기록.
- [수치 기여문](../contributions/numerics/SPECTRAL_NUMERICS_KO.md)과 spectral_response.py 전체. 원시 JSON의 65개 check와 actual/expected/error, He Jacobian 행, root endpoint 및 혼합 수치.
- 두 contribution의 EXECUTION.json, numerical stdout/stderr, dependency manifest, owner 통합·원격 입력 identity·문헌 범위 기록.
- Pinned atomic_provider.rs의 실제 HI fit/cutoff, hhe_events.rs의 단위·threshold, paired_runtime.rs의 실제 초기값 부분. PHYS22의 닫힌 초기시간 식과 Jacobian은 상속 입력으로 소비했다.
- Figure script의 함수 평가·정규화·plot 구간과 실제 PNG. 네 panel의 축·단위·zero·조건부 전이·국소 계수 caption이 보고서와 일치한다.

검토자는 새 science main, native 계산, gas IVP, 과거 PHYS22 이하 suite, 원격 요청 또는 mutation을 실행하지 않았다. 32개 파일의 local identity 확인과 JSON 읽기는 새로운 과학 검산으로 합산하지 않는다. 현 branch/source의 remote identity는 owner의 현재-turn read-only 기록을 소비했다.

## 주장별 판단

| Claim | 판정 | 채택하는 근거 수준 |
|---|---|---|
| C23.1: HI-only 구간의 HII·heat·온도 부호 및 영점 0 | PROMOTE_SCOPED | derived + implementation-verified exact rational certificate |
| C23.2: r(E)의 엄격한 증가와 안전한 범위 | PROMOTE_SCOPED | derived + implementation-verified exact rational certificate |
| C23.3: 모든 허용된 비영 양의 spectrum의 H/T 부호 | PROMOTE_SCOPED | derived; finite positive measure와 compact support 조건 |
| C23.4: HeIII의 하나의 monoenergetic 전이 | PROMOTE_SCOPED | derived conditional + numerically checked; 고정 serialized Jnp |
| C23.5: 동일 N/U인데 HeIII 부호가 다른 spectrum | PROMOTE_SCOPED | algebraic construction + numerically checked; 고정 serialized Jnp |
| C23.6: HeII의 전 구간 음의 선도 계수 | PROMOTE_SCOPED | derived conditional + numerically checked; 고정 serialized Jnp |

### 1. 정확한 부호 증명이 성립하는 이유

실제 HI branch의 원래 fit에서 얻은
\[
\alpha=-\frac72+\frac2{X-1}+\frac{P}{2(1+z)},\qquad
\beta=-\frac{2X}{(X-1)^2}-\frac{Pz}{4(1+z)^2}
\]
는 \(D=E\partial_E=(z/2)\partial_z\)와 일치한다. 따라서
\[
A=\alpha^2+3\alpha+\beta,\qquad
H_{c_0}=(E-c_0)A+E(2\alpha+4)
\]
가 각각 \(\mathscr C\lambda/\lambda\) 및 \(\mathscr C[\lambda(E-c_0)]/\lambda\)다. 이 단계에서 gas state와 \(c_0\)는 고정되어 있다.

보고서의 \(N,G,P_A,P_{H,c_0}\) 대수식과 실제 코드의 polynomial construction이 일치한다. \(z\in[49/50,33/25]\)의 exact domain enclosure가 물리적인 열린 cutoff 구간 전체를 포함하고, \(G>0\) 및 나머지 normalization의 양수가 확보된다. 네 다항식의 Bernstein coefficient 부호와 역 basis 변환 기록은 적절한 구간 증명서다. Basis가 음이 아니고 합이 1이므로, 모든 계수의 엄격한 같은 부호는 sample 사이를 포함한 polynomial 전체의 엄격한 부호를 준다.

기록된 7/7, 9/9, 9/9 negative coefficient로 HII·heat·temperature numerator의 영점이 없음을 채택한다. \(P_R=P'_QP_A-P_QP'_A\)의 14/14 positive coefficient는
\[
\frac{dr}{dE}=\frac{P_R}{2(E_0y_a)zP_A^2}>0
\]
에 대응한다. \(\lambda\)의 크기나 비정수 지수 자체를 유리수 polynomial이라고 잘못 취급한 것이 아니다. 양의 \(\lambda\)를 부호 문제에서 소거한 뒤 로그 미분의 유리함수를 다루었다.

증명서의 정확한 끝점값을 느슨하게 바깥쪽 반올림한 \(16.98<r<68.33\) eV도 타당하다. 보조 구간에서 analytic fit을 다루었다는 사실을 cutoff 아래 actual piecewise opacity의 변경으로 확대하지 않았다. Elementary bound는 같은 부호의 해석을 돕는 보조 논증이며 추가 독립 검산 수를 만들지 않는다.

이는 source binary64 literal을 exact-real 상수로 해석한 continuum 정리다. Proof-assistant kernel에서의 형식 검증 또는 native floating-point 연산의 동등성 인증은 포함하지 않는다.

### 2. Spectrum, 정규화와 부호의 전달

유한 비영 양의 photon-number measure가 열린 HI-only 구간 안의 compact set에 지지되면 \(-\mathscr C\lambda>0\)로 정의한 \(dW_\nu\)는 확률 measure다. 따라서 \(R_\nu\)는 \(r\)의 범위를 벗어나지 않으며
\[
a_{3,w}=a_{3,x}R_\nu,\qquad
\theta_3=\frac{\mathcal A_T}{\Pi_*}a_{3,x}(R_\nu-e_{\mathrm{th},*})
\]
가 성립한다. 실제 \(e_{\mathrm{th},*}\simeq6.463\) eV보다 \(R_\nu\)의 하한이 높으므로 HII·heat·온도는 모두 음수다.

이 주장은 spectrum 자체를 미분하거나 integration by parts를 수행하지 않는다. Kernel의 spectral 미분과 초기시간 전개 후 fixed label measure에 적분한다. Threshold에서 양의 거리만큼 떨어진 compact support를 요구하여 국소 미분과 적분 교환의 범위를 명시했다. Cutoff에 누적되는 measure나 threshold crossing에 자동 적용하지 않았다.

\(d\nu=N_0dP_N\), 고정 shape를 같은 U에 맞추는 양의 rescaling, \(d\nu=(U_0/E)dP_U\)를 정확히 구분했다. Equal-number와 equal-energy 혼합을 같은 weight로 계산하지 않았다. \(q=0\) 또는 zero measure에서는 leading coefficients가 0이라는 퇴화 경우도 보존된다.

### 3. HeIII의 조건부 전이

HI-only support에서는 직접 He photo forcing의 선도 항이 0이므로 PHYS22에서 닫힌
\[
a_{4,h_2}=\tfrac14a_{3,x}
\bigl(J_{h_2,x}+J_{h_2,w}R_\nu\bigr)
\]
를 적용할 수 있다. Actual serialized 행은 \(J_{h_2,x}<0\), \(J_{h_2,w}>0\)이며 임계비는 약 23.7904763 eV다. \(a_{3,x}<0\)이므로 임계비보다 작은 \(R_\nu\)가 양의 HeIII response를 준다는 부호 방향도 맞다.

정확한 \(r'(E)>0\)는 고정된 이 J에서 root가 많아야 하나임을 보인다. [14,16] eV의 numerical endpoint와 bisection 및 직접 FD가 하나의 root 존재와 약 15.43367 eV의 위치를 지지한다. 보고서가 이 두 근거를 구분하여, 존재·위치까지 exact interval certificate로 격상하지 않은 점이 중요하다.

최종 numerical bracket 폭 \(6.7762635780344\times10^{-21}\) eV는 serialized numerical 입력에 대한 계산 정밀도다. J의 수치·물리 오차, 원자 fit의 정확도, 실제 physical transition uncertainty의 상계가 아니다. Root에서 \(t^4\) 계수가 0이라는 사실로 다음 비영 시간차수나 유한시간 부호를 추정하지 않았다.

HeII 행의 전환 비는 약 3.84 eV로 보수적 r 하한보다 작다. 따라서 HeII의 모든 허용 spectrum에 대한 음의 부호도 해당 serialized J에 조건부로 채택한다.

### 4. 같은 N/U의 반례와 차분 검산의 범위

고정 \(N_0\)에서 14/24 eV 혼합의 \(p_{14}=0.6986721567407912\ldots\)와 그 평균 에너지 \(17.01327843259209\ldots\) eV 단일선은 정의상 같은 광자 수와 총 에너지를 가진다. 혼합과 단일선의 HeIII 계수가 각각 \(+4.83979193153\times10^{-65}\), \(-8.67571640532\times10^{-65}\,\mathrm{s}^{-4}\)로 반대이고, HII·온도는 둘 다 음수다.

반례의 평균 에너지에서 원래 fit의 직접 FD가 실제 수행되었고 원시 check 배열에도 있다. 같은 에너지 분율의 다른 예에서 \(336/19\) eV mean은 analytic 함수 평가만 있었으며, 보고서가 그 차이를 명시했다. 후자의 점에 별도 FD를 했다고 확대하지 않는다.

수치 경로는 원래 \(\sigma(Ee^z)\) 및 energy-weighted observables를 직접 차분하며 \(\alpha,\beta,A\)를 사용하지 않는다. 9점 중심차분의 exact moment, 8차 오차에 맞는 Richardson factor 256, cutoff 내부에서만 평가하는 domain guard, cancellation이 큰 He root endpoint에서 두 항의 절댓값 합으로 error를 정규화하는 방식이 적절하다. 이 차분의 일치는 global derivative-error enclosure로 주장되지 않았다.

## 실제 실행 근거와 오류 분류

| 근거 | 기록된 결과 | 이 판정이 인정하는 의미 |
|---|---|---|
| Exact certificate 최초 실행 | 31/31 PASS, exit 0 | 한 finite certificate 프로그램의 성공 |
| Direct FD·계수·혼합 최초 실행 | 65/65 PASS, exit 0 | 새로운 bounded numerical validation |
| 11개 에너지의 33 curvature 비교 | 최대 상대 차이 \(1.6199310674\times10^{-51}\), tolerance \(10^{-42}\) | high-precision numerical agreement |
| 한 13.7 eV anchor의 5계수 | 최대 상대 차이 \(2.1127238052\times10^{-78}\) | 닫힌 PHYS22와 새 구현의 좁은 연결 |
| HeIII root의 양 endpoint FD | 부호 일치; 취소 전 scale error 약 \(6.73\times10^{-52}\) | numerical endpoint corroboration |
| 161점 그림 | render exit 0; reviewer 시각 확인 | 표시용 함수 평가, proof 또는 추가 test 아님 |

Assertion 수나 Bernstein coefficient 수를 독립 물리 법칙의 수로 해석하지 않는다. 검토자는 위 과학 프로그램을 재실행하지 않고 코드·실제 원시 결과·명령과 exit 기록을 검토했다.

최초 과학 assertion failure는 기록되지 않았다. Mpmath 부재의 두 probe는 환경 의존성 문제이고 stdlib Decimal 경로로 해결됐다. 부호 기여문 작성 중 parsing 실패는 mutation 전에 발생한 문서 도구 사건이다. 이 둘을 이론·수치 실패로 분류하지 않는다.

검토자가 발견한 SOURCE_MANIFEST.json의 잔존 PHYS22 task 표기는 metadata 오류였다. 원본을 evidence/SOURCE_MANIFEST_v1.json에 보존한 뒤 task를 PHYS23으로 수정했으며 corrected SHA256 a4f6e4aff6d61e6f8e2f1df2379fd6aebfbc0dd9be409a30680faa33e049e42d를 확인했다. Source bytes, 계약, 과학 코드·결과·tolerance는 바뀌지 않았다. 이 finding은 후보 동결 전에 해결됐다.

## 채택하지 않는 주장과 종료

다음은 미해결 또는 이 판정의 범위 밖이다: finite-time remainder의 크기와 gas trajectory, native arithmetic 또는 native Jacobian의 interval 동등성, cutoff crossing, Einstein-backreacted mean expansion, 관측 검출 가능성, 전 문헌에 대한 최초성, HeIII root에서의 다음 비영 시간차수.

Physical=HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED가 보존된다. 독립 검토에서 source/default/runtime 변경은 없었으며 이를 요구하지도 않는다.

PHYS24_FIXED_MOMENT_HEIII_ENVELOPE는 동일 N/U의 반례로 드러난 정보 손실을 정량화하는 단일 후속 문제로 적절하다. Envelope와 extremizer는 아직 실행·입증하지 않은 질문으로 handoff에 분리되어 있다. 이 판정은 PHYS24의 결과를 선행 승인하지 않는다.

Portability replay, 최종 ZIP restore, remote publication은 판정 뒤 owner의 closeout 작업이다. 이 리뷰는 그것들이 완료됐다고 주장하지 않는다. 관련 중대 claim 위험이 해소됐으므로 추가 과학 검산이나 재귀적 review를 요구하지 않고 집중 검토를 종료한다.
