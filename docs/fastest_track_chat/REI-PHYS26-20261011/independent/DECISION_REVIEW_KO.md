# PHYS26 독립 최종 판정

## 1. 판정과 채택 범위

**판정: PROMOTE_SCOPED. 물리적 채택: HOLD.**

평균 18 eV, 지원구간 [13.61, 24.58] eV, 광자 수 기준 Borel 확률측도와 델타 선 허용, source binary64 리터럴과 직렬화 수치 J를 정확한 실수 입력으로 해석하는 계약에서 PHYS26의 결과를 연구 보고와 다음 루프의 닫힌 입력으로 채택한다. 이 범위의 **치명적 결함 0건, blocking finding 0건, 필수 과학 수정 0건, 필수 문서 수정 0건**이다.

채택하는 새 결과는 모든 허용 분산의 정확한 응답 구간, 각 상·하한을 달성하는 유일한 측도, 두 분산 끝점의 퇴화, 두 영점의 엄격한 순서와 모든 strict/nonstrict 부호 영역이다.

\[
\mathcal A(W)=[A_-(W),A_+(W)],
\qquad 0\le W\le28.8862\ {\rm eV}^2,
\]

\[
A_+(W)=\frac{Wk(a)+L^2k(m+W/L)}{L^2+W},
\qquad
A_-(W)=\frac{H^2k(m-W/H)+Wk(b)}{H^2+W},
\]

여기서 a=13.61, b=24.58, m=18 eV, L=4.39, H=6.58 eV다. 상단은 왼쪽 끝점을 포함하는 두 선, 하단은 오른쪽 끝점을 포함하는 두 선이 달성한다. 이 결과는 임의의 다선·연속 스펙트럼을 포함하는 허용집합 전체에 적용된다. [전체 유도](../contributions/theory/ENVELOPE_DERIVATION_KO.md), [통합 보고서](../report/PHYS26_REPORT_KO.md).

PHYS25에서 하나의 비교 경로 영점이었던 W₀가 이제 모든 같은 모멘트 측도에 대한 하단의 영점이 된다. 이 진전은 새로운 근 반복이 아니라 새로운 전역 극값 증명에서 나온다.

이 판정 시점의 최종 완성 ZIP 복원, 동일 브랜치의 원격 게시와 전달은 아직 완료로 판정하지 않는다. 그 실제 완료는 owner의 CLOSEOUT 및 detached 게시 receipt에 기록해야 한다.

## 2. 검토자와 동결 identity

검토자는 **/root/phys26_decision, GPT-6 Astra**다. Owner /root, 이론 생성자 /root/phys26_theory, 수치·검증 설계자 /root/phys26_numerics, 포터빌리티 실행자 /root/phys26_portability와 다른 새 최종 판정 역할이다. 후보 생성과 수치 검산 설계에 참여하지 않았다.

전체 이력과 결과 요약에 노출된 **NONBLIND** 검토다. 실제 역할·판정의 분리는 성립한다. 맹검, 다른 원자 데이터, 다른 J, 다른 모델 계열을 이용한 검증으로 표현하지 않는다.

| 동결 대상 | SHA256 |
|---|---|
| 후보 freeze, payload 59개 | 5bc796232a3513f1ff79e8dd7c9a2c5e2ce8c773ae051fdb542ba20ba326d8ac |
| PHYS26 보고서 | 8a9773e333f60c2d4e1525367474d26229797852e5b5130692356d6ecd5fabea |
| 물리 계약 | d4ff7556332f75447d93e0c6a8da4a0d96cb8a86b257f111809d388b7f2b80ce |
| 수치 J 입력 | 6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79 |
| 첫 수치 원 결과 | 23efff335062c1e32fd6888d86fdf862dc9faca915fb120a97420187d6a9a4fe |

검토 전후의 두 읽기 전용 identity 확인에서 **59/59 payload의 크기·SHA가 모두 일치**했고 후보 파일을 변경하지 않았다. 최초 identity 확인의 개별 UTC는 별도로 기록하지 않았으며 실제 tool chunk는 a7373a다. 최종 확인 시각과 전체 파일별 identity는 [DECISION_REVIEW.json](DECISION_REVIEW.json)에 있다. 해시는 읽은 후보의 정체성을 고정하며 수학적 타당성을 대신하지 않는다.

## 3. 핵심 주장별 판정

| 주장 | 판정 | 직접 판단 근거 |
|---|---|---|
| I0–I3: 입력·닫힌 곡률·두 근 기록 | CONSUME_SCOPED | 동일 J·소스·구간·정규화와 이전 판정 범위를 확인했다. 기존 부호 suite나 근 탐색을 재개하지 않는다. |
| TH26.1–2 / C1: 모든 허용 W와 끝 분산 | PROMOTE_SCOPED | 비음수 적분 항등식이 W≤LH를 주고 두 명시적 측도가 전 범위의 실현성을 준다. W=0과 LH의 영점 조건이 유일 law를 정한다. |
| TH26.3–4 / C2: 연속 이차 dual | PROMOTE_SCOPED | 적분 Taylor 잔차의 엄격 감소가 Q₊≥k≥Q₋의 방향과 정확한 접촉 집합을 결정한다. |
| TH26.5–6 / C3: 전역 극값과 모든 등호 측도 | PROMOTE_SCOPED | 세 모멘트로 모든 이차식의 기대값이 고정된다. 비음수 연속 잔차의 영 적분이 두 접촉점 지지를 강제한다. |
| TH26.7–8 / C4: 엄격한 폭과 전체 응답 구간 | PROMOTE_SCOPED | 내부 분산의 하단 law는 상단 접촉 밖에 양의 질량을 가지므로 간격이 엄격하다. 볼록 혼합이 구간 내부를 모두 달성한다. |
| TH26.9 / C5: 두 경계의 단조성 | PROMOTE_SCOPED | W 미분은 각각 Hᵥ(a), Hᵤ(b)이고 k″>0로 양수다. u에 대한 미분과 W에 대한 미분 방향을 구별했다. |
| TH26.10–11 / C6: 두 영점과 순서 | PROMOTE_SCOPED | 양 끝 부호와 단조성으로 각각 유일근을 얻고, V*에서의 엄격한 간격으로 V*<W₀를 증명한다. |
| TH26.12–14 / C7: 부호의 모든 양화 | PROMOTE_SCOPED | 달성된 sharp bounds가 존재·모든 law, 엄격·비엄격, 문턱의 유일 영 law와 infimum/minimum을 구분한다. |
| TH26.15: 양의 상수배 | PROMOTE_SCOPED | 응답 크기만 바뀌고 law와 영점은 보존된다. 커널 모양을 바꾸는 입력 변화에는 적용하지 않는다. |
| N1–N2: 제한 수치·같은 분산의 반대 부호 | PROMOTE_SCOPED | 실제 원식 두 경로, 모멘트·접촉·혼합, 사전 실행 예산과 원 281개 검사가 보고된 수치 범위를 지지한다. |
| D0: 그림 | ACCEPT_DISPLAY_ONLY | 실제 픽셀의 단위·방향·선 지지·확률·경계와 표시 provenance가 일치한다. |
| R0: 새 프로그램 재현 | ACCEPT_PORTABILITY_SCOPED | 12개 입력 payload, 새 main 1회, exit 0, 원 바이트·전체 JSON 동일 기록을 읽었다. 독립 물리 계산이나 최종 전체 ZIP 복원은 아니다. |
| P0: 물리적 채택 | HOLD | 물리 admission을 바꿀 새 불확실성·유한 시간·native 근거가 없다. |
| PHYS27 | ACCEPT_SINGLE_NEXT_QUESTION | 반폭 0.05 eV 균일 대역족이라는 다음 계약 후보가 명시적이고 아직 실행하지 않았다. |

### 연속구간과 등호 논증

고정 s에서

\[
H_s(E)=\int_0^1(1-t)k''(s+t(E-s))\,dt
\]

이고

\[
\partial_EH_s(E)=\int_0^1t(1-t)k'''(s+t(E-s))\,dt<0
\]

다. E<s에서도 같은 적분 Taylor 항등식을 사용하며 부호를 추가로 뒤집지 않는다. E=s의 값은 k″(s)/2여서 특이점도 없다. 따라서

\[
Q_+(E)-k(E)=(E-v)^2[H_v(a)-H_v(E)]\ge0,
\]

\[
k(E)-Q_-(E)=(E-u)^2[H_u(E)-H_u(b)]\ge0
\]

가 전체 I에서 성립한다. 잔차 영점은 정확히 {a,v}, {u,b}다. 모든 허용 Borel 측도에 적분할 수 있고, 등호는 잔차 영점만 지지하도록 강제한다. 이는 두 선만 임의로 가정하여 최적화한 결과가 아니다. [유도 §§3–4](../contributions/theory/ENVELOPE_DERIVATION_KO.md).

0<W<LH에서는 하단 law가 b에 양의 질량을 가지며 b는 상단 잔차의 영점이 아니므로 A₋<A₊다. 임의의 목표 응답은

\[
P_\theta=(1-\theta)P_W^b+\theta P_W^a,\qquad
\theta=\frac{A_{\rm target}-A_-}{A_+-A_-}
\]

로 달성된다. 두 끝 분산에서는 유일 law 하나가 구간을 한 점으로 만든다. 내부 응답의 모든 표현에 대한 유일성이나 최소 선 수는 채택 범위에 들어 있지 않다.

## 4. 두 문턱의 엄격·비엄격 의미

정확한 경계는

\[
(v_*-m)k(a)+Lk(v_*)=0,\quad
V_*=L(v_*-m),
\]

\[
Hk(u_0)+(m-u_0)k(b)=0,\quad
W_0=H(m-u_0)
\]

의 유일근으로 정의한다. 상속된 소수 평가는 각각

\[
V_*\simeq16.339944654589707345109,\qquad
W_0\simeq23.420218992353392972114
\quad({\rm eV}^2)
\]

다. A₋(V*)<A₊(V*)=0이고 A₋가 엄격 증가하므로 0<V*<W₀<LH는 소수 비교에 의존하지 않는다.

| 분산 | 채택하는 정확한 명제 |
|---|---|
| 0≤W<V* | 모든 허용 law에서 A<0 |
| W=V* | 모든 A≤0; 상단 law 하나만 A=0 |
| V*<W<W₀ | 같은 광자 수·평균·분산에서 음·영·양 응답 모두 가능 |
| W=W₀ | 모든 A≥0; 하단 law 하나만 A=0 |
| W₀<W≤LH | 모든 허용 law에서 A>0 |

따라서 양수 응답 law의 존재를 요구하는 분산 집합은 (V*,LH], 모든 law의 양수 응답을 요구하는 집합은 (W₀,LH]다. 두 집합에는 최소 원소가 없으며 각각의 infimum은 V*, W₀다. 비음수로 바꾸면 아래끝을 포함한다. 영 응답 law가 존재하는 분산은 정확히 [V*,W₀]다. 허용 분산 밖의 공집합에 이 양화 명제를 확대하지 않는다.

유한 root 중점의 실제 응답은 약 −2.27486876684×10⁻¹³⁷, −3.25826546129×10⁻¹³⁷ s⁻⁴다. 후보는 이를 정확한 0이나 엄밀한 feasible law로 부르지 않는다. 원 수치 bracket도 rigorous interval certificate로 승격하지 않았다. 이 구분은 필수적이며 현재 보고서·원 JSON·handoff가 일관되게 유지한다. [상속 원 근 기록](../inputs/inherited/PHYS25_VARIANCE_CANDIDATE.json), [새 원 결과](../contributions/numerics/FIXED_VARIANCE_ENVELOPE_FIRST.json).

## 5. 수치 구현과 실제 실행 증거

새 과학 코드 전체를 읽었다. 주 경로의 3차 로그 Taylor jet은 E(t)=Eeᵗ를 원 적합식에 넣어 Dⁿf/n!를 구성한다. F=qN₀κ/180, f=σ[Jₓ+Jw(E−χ)]에서

\[
k=F(D^2+3D)f,\qquad
k'=\frac{F}{E}(D^3+3D^2)f
\]

를 계산한다. k″ 또는 k‴의 새 부호 계산을 수행하지 않는다. 별도 scalar 로그미분 경로의 ℓ₁, ℓ₂, ℓ₃와 곱미분 계수를 읽어 확인했다. 두 표현은 같은 소스 적합식·J·Decimal 계열을 공유한다. [새 코드](../contributions/numerics/fixed_variance_envelope.py), [사전 protocol](../contributions/numerics/PROTOCOL.json).

원 J의 필요한 두 전체 문자열과 atomic_provider.rs의 실제 HI cross_section 블록도 읽었다. χ=13.598434599702 eV의 binary64 해석과 HI opacity cutoff 13.60 eV가 구별되며, 현재 I는 HeI cutoff 24.59 eV 아래다. 정규화 qN₀/45는 k에 한 번 포함되고, 원식의 1/4와 합쳐져 코드의 /180이 된다.

| 첫 실행 항목 | 실제 기록 |
|---|---:|
| 사전 고정 분산 / 별도 비교 에너지 | 7 / 5 |
| Jet 커널 평가 / scalar 평가 | 13 / 5 |
| 총 커널 평가 / 캐시 조회 | 18 / 132 |
| 전체 검사 | 281/281 PASS |
| 각 W의 세 에너지에서 두 dual 표본 | 42 |
| 실제 exit / 과학 실패 | 0 / 0 |
| 새 root / 새 부호 campaign / old main·suite | 0 / 0 / 0 |
| Native / gas IVP | 0 / 0 |

실행 전 protocol·코드·입력 9개를 동결했고 첫 실행 후 과학 코드나 허용오차를 변경했다는 기록은 없다. 실제 command·UTC·stdout·빈 stderr·exit를 읽었다. 원 check 281개는 이름, pass와 모든 잔차·허용치 필드를 읽었으며 긴 수치 문자열은 표시용 14자리로 투영했다. 표시에서 잘린 188–239행은 별도 읽기로 보충했다. 일곱 law의 모멘트·확률·응답과 두 혼합 기록도 원 JSON에서 확인했다. [실행 기록](../contributions/numerics/EXECUTION.json), [검산 설명](../contributions/numerics/NUMERICS_NOTE_KO.md).

15개 원식 비교의 최대 scaled 차이는 3.9469×10⁻¹⁵⁷, 사전 허용치는 10⁻¹²⁰이다. 이 값은 구현 경로의 일치 정도다. 물리 정확도·J 불확실성 또는 엄밀 오차 구간으로 해석하지 않는다. 접촉을 구성한 뒤 검사한 항목은 대수 구현 검사이며, 42개 표본 slack은 연속구간 증명이 아니다.

W=19.74 eV²의 실제 두 응답은 약 −2.76487053624×10⁻⁶⁵와 +1.62032722687×10⁻⁶⁵ s⁻⁴다. 같은 모멘트의 영 응답 혼합에서 유한 Decimal 직접합 10⁻²²⁴ s⁻⁴와 affine 합의 반올림상 0×10⁻²²⁴가 모두 남아 있다. 정확한 혼합 공식의 영 응답과 유한 계산 잔차를 구별하는 처리는 타당하다.

## 6. 상속 증거, 문헌, 그림과 포터빌리티

PHYS24 곡률 유도와 PHYS25 세 번째 도함수 유도를 전체 읽었다. 후자의 원 인증에서는 같은 source/J identity, domain, 양의 인자와 /128E³G⁵ 표현, 18개의 정확히 음수인 Bernstein 분수, 전체 17개 검사와 한 구간·분할 0 기록을 읽었다. PHYS24 원 인증의 구간·곡률 attempt metadata·전체 20개 검사도 읽었다. 모든 중간 다항식 배열을 재구성하거나 과거 부호 프로그램을 재실행하지 않았다. 기존 평균 18 eV의 끝값 부호 역시 이전 판정의 닫힌 전제로 소비하며 그 수치·interval 등급을 새로 높이지 않는다.

일반 Hermite 보간의 맥락은 [Nicholas Hu의 저자 원문](https://math.ucla.edu/~njhu/notes/na/interp/polyinterp/)을 직접 열어 확인했다. 반환된 89행, 특히 반복 노드 보간, divided difference 평균값 정리와 오차 공식 부분을 읽었다. 페이지의 표시 갱신일은 2026-01-15다. 이 문헌은 보간 구조의 맥락을 지지하며 PHYS26의 HeIII 커널이나 분산 문턱을 제공하지 않는다. 그 결과는 위 직접 유도에 의존한다.

실제 PNG의 축·단위, 응답 band 방향, 두 영점, 일곱 표본, W=19.74의 선 위치·확률·부호와 HOLD 표기를 확인했다. legend와 두 경계 annotation도 읽을 수 있다. 86개 W와 171개 고유 에너지의 표시 평가, 배치 수정에 따른 총 두 번·342회 표시 커널 평가는 별도 표시 작업으로 기록되어 있으며 과학 인증으로 더하지 않는다. [그림](../figures/PHYS26_response_envelope.png), [표시 provenance](../figures/DISPLAY_PROVENANCE.json).

포터빌리티 wrapper 전체와 scope·staging manifest·receipt를 읽었다. 선택한 12개 payload를 복원한 경로에서 새 PHYS26 main을 한 번 실행했고, exit 0·원 바이트 및 전체 JSON 동일·비교 제외 필드 없음이 기록되어 있다. 이 검토자는 replay를 실행하지 않았다. 최초 빈 공유 출력 디렉터리 guard 오류는 과학 실행 전의 준비 오류로 보존되어 있으며 이를 실패한 과학 검산의 재시도로 세지 않는다. 이 기록은 최종 전체 ZIP의 복원을 대체하지 않는다. [포터빌리티 범위](../portability/PORTABILITY_SCOPE.json), [원 receipt](../portability/REPLAY_RECEIPT.json).

## 7. 실제 읽기·계산의 한계와 종료

이 검토자가 실행한 새 과학 main, 커널 평가, 근 탐색, 도함수 부호 campaign, old module·main·suite, native, gas IVP, replay와 그림 생성은 **모두 0회**다. 텍스트·JSON 투영, 읽기 전용 해시·기록 간 동일성 확인과 판정 파일 작성만 수행했다. 새 최종 검토자를 추가하지 않았다.

후보 59개를 모두 해시 확인했지만 각 내용의 실제 읽기 범위는 같지 않다. J는 필요한 행과 convention, Rust는 HI 블록, 과거 수치 결과는 필요한 두 근·law를 선택하여 읽었다. 다른 여섯 source의 모든 구현이나 모든 과거 raw 배열을 새로 감사한 것으로 기록하지 않는다. 전체 read scope는 판정 JSON에 남겼다.

Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 유지한다. 초기 ε²t⁴ 계수의 영점은 유한 시간 편차나 높은 시간차수의 소멸을 뜻하지 않는다. J·원자·기체 불확실성, native 동등성, 실제 방출원 admission, 모든 평균이나 세계 최초성은 이번 채택 범위에 없다.

PHYS27은 반폭 0.05 eV 균일 대역 혼합족에서 중심 분산과 광자 분산을 구별하는 다음 계약 후보다. 해당 평균화 커널·유한 폭 경계의 계산과 판정은 아직 실행하지 않았다. [단일 후속 질문](../next/PHYS27_NEXT_HANDOFF_KO.md).

**이 동결 후보에 대한 한 번의 집중 최종 검토를 종료한다.** 추가 과학 실행이나 재귀적 리뷰를 요청할 근거가 남아 있지 않다. Owner는 이 판정을 상태에 반영하고 최종 묶음의 검증 전용 복원, 승인된 동일 브랜치의 additive 문서 게시와 실제 readback, 전달을 완료할 수 있다.
