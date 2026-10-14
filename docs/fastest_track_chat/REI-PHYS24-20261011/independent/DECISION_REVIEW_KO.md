# PHYS24 독립 최종 판정 — 고정 모멘트 HeIII 초기 응답

## 1. 판정

**PROMOTE_SCOPED — 연구 단계 PROMOTE, physical admission HOLD.**

고정된 수치 Jacobian \(J_{\mathrm{np},*}\), 초기 기체, 양의 \(q,N_0\), 에너지 구간 \(I=[13.61,24.58]\) eV와 비음수 photon-number measure라는 계약 아래, PHYS24의 C24.1–C24.5를 연구 보고 및 다음 단일 질문의 닫힌 입력으로 승격한다. 실제 커널의 엄격한 볼록성, 정확한 응답 구간, 최적 측도의 유일성, 모든 중간값의 달성, 평균 에너지의 완전한 부호 분할에 필요한 근거가 있다.

남은 필수 수정은 **0건**, 과학적 수정 요구는 **0건**, 치명적·차단 결함은 **0건**이다. 검토 중 발견한 수치 노트의 문서 포맷 문제 1건은 최종 후보 동결 전에 해결됐다. 구분자·제어문자만 수정했고 원본과 정정 기록을 보존했다.

이 판정은 초기 \(\epsilon^2t^4\) 계수의 조건부 수학 결과에 관한 것이다. 물리 source 승인, native 연산 동등성, 유한 시간·유한 전단의 부호 보장, Jacobian 입력 오차의 엄밀한 경계로 확대하지 않는다. 공식 기계 판독 판정은 [DECISION_REVIEW.json](DECISION_REVIEW.json)이다.

## 2. 검토자 독립성과 고정 후보

검토자는 **/root/phys24_decision**이다. 후보 생성과 과학 검증 설계에 참여하지 않은 별도의 최종 decision reviewer이며, owner의 역할 전환에 의한 자기 승격이 아니다. 전체 대화 이력을 상속했으므로 **NONBLIND 검토**다. 기여자 결과를 보지 않은 독립 발견이나 눈가림 검증이라고 주장하지 않는다.

이번 검토에서는 새 과학 프로그램·native·gas IVP·닫힌 과거 suite를 실행하지 않았다. 입력과 원 결과를 실제로 읽고, 필요한 수식·코드 논리·주장 범위를 검토했다. 별도로 수행한 것은 최종 후보의 바이트 identity, 실행 전후 provenance, 통합 JSON의 원 결과 전사와 발견된 문서 포맷 정정의 대조다. 이는 새 물리 검산으로 세지 않는다.

### 고정된 판정 대상

| 파일 | SHA256 |
|---|---|
| [CANDIDATE_FREEZE.json](../evidence/CANDIDATE_FREEZE.json) | f62dc1a2949a19c41caa18784b2dce4f0dcbfe02bbe00d4971eebe377de84fe7 |
| [PHYS24_REPORT_KO.md](../PHYS24_REPORT_KO.md) | 09e563406236f244aec8ac14dfbb1fb7b96b047fa8e2869398b744be4b6bc9a4 |
| [RESULTS_SUMMARY.json](../RESULTS_SUMMARY.json) | 5110d69bfadba1f3829082be5e1683db705d9ea39ebb1fd882dcce1ba01e6318 |
| [CLAIM_DAG.json](../CLAIM_DAG.json) | fa60a044ced9a21660f249dcc5a916fa58c82a4ed6584e8168c579f424b64615 |
| [PHYS25_NEXT_HANDOFF_KO.md](../PHYS25_NEXT_HANDOFF_KO.md) | adc3aa7644598ac86eeb83b2447bbea11977b2b516dac2b08c0f2e88616d0473 |
| [PHYSICS_CONTRACT.json](../PHYSICS_CONTRACT.json) | fd60772fa082a651034b21b965133e57cc0c3e37bb14cdab531a5ca3965266e2 |

검토자가 동결 목록 **61개 파일의 SHA256과 바이트 수를 직접 대조했고 전부 일치**했다. source 7개도 로컬 바이트·크기·Git blob을 source manifest 및 보존된 immutable remote tree 기록에 대조하여 모두 일치했다. 추가로 36개의 직렬화 데이터·실행 provenance·포맷 대조가 모두 통과했다. 이 수는 파일과 기록의 일치 검사 수이며 독립 과학 증명의 개수가 아니다.

Scientific input commit은 **6104a9655439b15143933a97b9926e61dfb62b53**, root tree는 **4677621ec12994af5f637f582888713e23845361**, scientific Rust src tree는 **cb69b4736dd046e4675557577eb8e0ead037d1f3**다. Owner가 새 원격 읽기를 수행했고 검토자는 그 [기록](../evidence/REMOTE_INPUT_IDENTITY.json)과 로컬 source 연결을 확인했다. 검토자가 별도의 원격 fetch를 수행했다거나 이후 publication commit을 검증했다고 주장하지 않는다.

### 실제 열람 범위

통합 보고서, 계약, claim DAG, 다음 handoff, 모멘트 유도문, 곡률 유도와 새 코드 전체, 수치 코드 전체, 양쪽 사전 protocol과 freeze, 최초 execution·stdout·stderr, 독립성 보정, 포맷 정정 및 owner의 통합 기록을 읽었다. Exact 결과에서는 정의·정의역·인증 구간·결론과 20개 검사 전체를, 수치 결과에서는 원 입력·근/끝점/chord/표본·156개 검사 이름과 판정·원시 비교값을 확인했다. 통합 결과에 복사한 root·envelope·mixture 등의 블록은 원 결과 JSON과 직접 일치시켰다.

Source에서는 HI fit와 cutoff 산술, 초기 기체·광자값, 전단 설정의 관련 부분을 읽었다. 그 밖의 상속된 파일은 닫힌 입력으로 identity를 묶었으며 모든 과거 내용을 새로 재심사했다고 주장하지 않는다. 큰 유리수 배열의 모든 계수를 검토자가 독립 재계산한 것도 아니다.

## 3. 여덟 판정 차원

총점을 만들지 않고 하네스의 여덟 차원을 따로 판단했다.

| 차원 | 판정 | 판단 근거와 남는 한계 |
|---|---|---|
| Evidence | 범위 내 충분 | 고정 입력, 명시적 유도, 정확한 유리수 인증, 최초 실행과 별도 원식 수치 경로가 연결된다. 해시 일치는 물리 정확성이나 독립성을 스스로 보증하지 않는다. |
| Physical/math validity | 조건부 수학 타당 | \(D\)에서 실제 에너지 이계 미분으로의 변환, 양의 전인자, 14차 분자, compact 모멘트 정리, 극값·등호·부호 분할이 일관된다. 상속된 초기시간 함수식과 고정 수치 \(J\) 조건을 유지한다. |
| Novelty | 구체적 적용으로 한정 | 일반 모멘트 극점 구조를 알려진 이론으로 인정하고 특수 문제를 직접 증명했다. 새 기여는 실제 HeIII 커널의 곡률 인증과 그 응용이다. 전역적인 신규성·우선권 주장은 없다. |
| Testability | 실제 제한 실행 있음 | 두 새 프로그램의 사전 코드/절차 동결과 exit 0 원 로그, exact 20/20 및 numerical 156/156 결과가 있다. 근·chord·모멘트 검사는 문제의 대안을 구분한다. |
| Robustness | 계약의 연속체 범위 지지 | 증명은 모든 에너지와 허용 스펙트럼을 덮는다. 격자에서 전 구간으로 비약하지 않는다. \(J\)·원자 적합식·초기 기체·추가 스펙트럼 제약에 대한 강건성은 별도 문제다. |
| Tractability | 작은 범위에서 완료 | 곡률 인증은 한 구간에서 분할 없이 성공했다. 수치 작업은 7개 곡률 표본과 명시적 chord 공식, 기존 근의 좁은 검사, 기존 반례 하나에 한정된다. |
| Assumptions | 명시적·일관됨 | 비음수 광자 수 측도, 선 허용, 양의 \(N_0,q\), 고정 평균·초기 기체, eV/H 정규화, source의 exact-real 해석과 수치 \(J\) 상한이 보존된다. |
| Original motivation | 계약 범위에서 해결 | 같은 \(N,U\)의 반대 부호 반례가 정확한 가능 구간과 평균별 부호 분할로 정량화됐다. 기존 반례를 최대 응답으로 오인하지 않았다. |

## 4. 주장별 검토

### C24.1 — 실제 커널의 엄격한 볼록성

**PROMOTE_SCOPED; derived + implementation-verified.**

새 곡률 코드는 원래 HI 단면적에서

\[
\alpha=D\log\sigma=\frac{N}{2G},
\qquad
H_\eta=\frac{P_\eta}{4G^2},
\qquad
\eta=\chi-\frac{J_x}{J_w}
\]

를 얻고,

\[
g=\frac{\kappa\sigma J_w}{4}H_\eta,\qquad
g''=\frac{\kappa\sigma J_w}{64E^2G^4}R
\]

로 정리한다. 코드와 유도문을 대조해 \(D=(z/2)\partial_z\), \(E^2g''=D(D-1)g\), 분모의 64 및 shifted heat 표현이 일관됨을 확인했다. \(J_w>0\), \(\kappa>0\), \(\sigma>0\), 분모의 양성이 명시돼 있다. [유도문](../contributions/curvature/CURVATURE_DERIVATION_KO.md), [코드](../contributions/curvature/exact_curvature_certificate.py).

실제 \(z(I)\)를 포함하는 유리수 구간 \([49/50,33/25]\) 전체에서 14차 \(R\)의 Bernstein 계수 **15/15가 엄밀히 양수**다. 두 다항식 미분 경로 및 Bernstein 역변환 항등식도 정확하게 일치한다. 끝점의 제곱근을 감싼 별도 유리수 구간에서 8차 \(P_\eta\)의 계수는 각각 **9/9 양수와 9/9 음수**다. 따라서 실제 계약 구간에서 \(g''>0\), \(g(a)>0>g(b)\)가 따른다. 연속성과 볼록 할선 기울기의 순서로 내부 영점의 존재·유일성도 성립한다. [인증 결과](../contributions/curvature/CURVATURE_CERTIFICATE.json).

보조 \(z\) 구간은 물리적 support보다 조금 넓지만, 매끄러운 HI fit의 대수적 연장을 다항식 부호 인증에만 사용한다. 실제 물리 결론은 두 cutoff 안의 \(I\)에 제한한다. 이 구분은 적절하다. Exact-arithmetic 코드와 명시적 증거를 가진 조건부 명제이며, proof assistant의 형식 검증이나 원래 수치 \(J\)의 오차 경계는 아니다.

### C24.2 — 정확한 가능 구간과 유일 극값 측도

**PROMOTE_SCOPED; derived.**

일반 연속 커널에서 그래프의 평면 볼록껍질은 compact하고, 고정 평균의 절편은 닫힌 달성 구간이다. 그래프 세 점으로 표현된 극값이 비공선 삼각형 내부에 있을 수 없다는 논법이 두 점 이하 극값 측도의 존재를 준다. 일반 커널의 모든 최적 측도가 두 점 이하라는 과장은 없다.

실제 엄격 볼록 커널에서는 Jensen 부등식과 끝점 chord 부등식으로

\[
k(m)\le a_{4,h_2}(P)=\int k\,dP\le
B(m)=\frac{b-m}{b-a}k(a)+\frac{m-a}{b-a}k(b).
\]

내부 평균에서 하단은 \(\delta_m\)만 달성한다. 상단의 gap \(B(E)-k(E)\)는 내부에서 엄격히 양수이므로 끝점 밖의 질량을 허용하지 않으며, 평균이 두 끝점의 가중치를 고정한다. \(m=a,b\)에서는 허용 측도 자체가 각각 단 하나다. 구간 안 모든 값의 달성은 두 극값 측도의 혼합으로 닫힌다. [모멘트 정리](../contributions/moments/MOMENT_EXTREMIZERS_KO.md) §§2–3.

### C24.3 — 모든 중간 응답의 두 선 이하 달성

**PROMOTE_SCOPED; derived.**

고정 왼쪽 끝점과 \(v\in[m,b]\)를 이용한 경로의 응답은

\[
k(a)+(m-a)\frac{k(v)-k(a)}{v-a}.
\]

엄격 볼록성 아래 할선 기울기가 연속·엄격히 증가하여 \(k(m)\)에서 \(B(m)\)까지의 전체 구간을 덮는다. 세 선의 명시적 혼합은 충분한 구성이고, 세 선이 필수라는 주장은 하지 않는다. 경로상의 \(v\)가 유일하다는 사실과 전 스펙트럼 표현의 유일성도 구별돼 있다. 이 결과는 다음 분산 최소화 문제의 최적성 증명이 아니다. [통합 보고서](../PHYS24_REPORT_KO.md) §6.

### C24.4 — 다섯 평균 에너지 부호 영역

**PROMOTE_SCOPED; 정확한 부호 정리와 수치 위치를 구분.**

정확한 경계는 \(k(E_-)=0\), \(B(E_+)=0\)으로 정의된다. 엄격한 chord gap은 \(a<E_-<E_+<b\)를 준다.

| 평균 | 가능한 부호 | 0의 등호 조건 |
|---|---|---|
| \(a\le m<E_-\) | 양수만 | 없음 |
| \(m=E_-\) | 0, 양수 | 단색 \(\delta_{E_-}\)만 0 |
| \(E_-<m<E_+\) | 음수, 0, 양수 | 적절한 스펙트럼 혼합으로 달성 |
| \(m=E_+\) | 음수, 0 | 정해진 양 끝점 혼합만 0 |
| \(E_+<m\le b\) | 음수만 | 없음 |

\(E_-\simeq15.43367086782694\) eV는 닫힌 PHYS23 수치 bracket을 소비하고 새 경로로 그 두 끝의 부호를 한 번 확인했다. \(E_+\simeq19.55655167718412\) eV는 새 affine 공식으로 평가했다. 새 bracket 폭 \(10^{-20}\) eV 및 기존 bracket 폭 약 \(6.77626\times10^{-21}\) eV는 **수치 계산의 결과**다. 보고서는 이를 엄밀 interval root enclosure나 물리 입력 불확실성의 상한으로 부르지 않는다. 양 경계에서의 정확한 등호 법칙과 표시용 가중치/소수도 구별한다. [수치 결과](../contributions/numerics/MOMENT_ENVELOPE.json).

### C24.5 — 원식에 연결된 제한 수치 검증

**PROMOTE_SCOPED; numerically checked + implementation-verified.**

새 수치 코드의 Taylor jet는 원래 cross-section 곱과 거듭제곱을 \(Ee^s\)에서 4차까지 직접 미분한다. 별도 경로는 원식의 함수값으로 13점 로그 에너지 차분을 만들며, 정확한 유리수 모멘트 방정식으로 가중치를 구한다.

\[
k''(E)=\frac{qN_0\kappa}{180E^2}
(D^4+2D^3-3D^2)f(E),
\quad
f=\sigma[J_x+J_w(E-\chi)]
\]

가 코드와 보고서에서 일치한다. 7개 표본의 최대 scaled difference는 약 \(2.154\times10^{-61}\)로 사전 허용오차 \(10^{-42}\)보다 작다. 39개의 stencil 모멘트 항등식을 포함하고, 모든 차분 노드가 해석적 HI-only 구간에 있음을 확인했다. 하지만 7개 표본이나 표본 중 최소 곡률을 전 구간 증명·전 구간 하한으로 확대하지 않는다. [코드](../contributions/numerics/moment_envelope.py), [protocol](../contributions/numerics/PROTOCOL.json).

원시 출력에는 첫 실행 **156/156 PASS, exit 0, 빈 stderr**가 있다. 총 질량·평균·광자 수·총 에너지의 구별, mono/endpoints/mixed law의 선형 응답, 반대 부호의 내부 지지 예시, PHYS23 반례 하나가 직접 검사됐다. 156개 assertion이 156개의 독립 물리 법칙이라는 뜻은 아니다. [실행 기록](../contributions/numerics/EXECUTION.json).

## 5. 정규화·정밀도·독립성의 상한

\[
F_2=[\epsilon^2]F=\frac12\partial_\epsilon^2F|_0,
\qquad
k=\frac{qN_0}{45}g,
\qquad
a_4(P)=\int k\,dP
\]

를 일관되게 사용했다. \(g\)에는 Jacobian 전달의 \(1/4\)가 들어 있고, \(k\)에는 이미 고정 \(N_0,q\)가 포함돼 있다. \(t^4\)에 추가 factorial을 붙이거나 \(k\)에 광자 수를 다시 곱하는 오류는 없다. \(P\)는 photon-number probability이며 energy fraction으로 바꾸어 읽으면 안 된다.

단위는 \(g:\mathrm{s}^{-2}\), \(g'':\mathrm{s}^{-2}\mathrm{eV}^{-2}\), \(k,a_4:\mathrm{s}^{-4}\), \(k'':\mathrm{s}^{-4}\mathrm{eV}^{-2}\)다. \(J_w\)의 \(w=\mathrm{eV/H}\) 정규화와 고정 초기 기체에서 에너지를 미분한다는 조건도 보존된다. Source binary64 literal을 정확한 실수로 해석하는 수학 모델과 실제 native 반올림 연산은 구별된다.

수치 **방법·검증 설계**는 다른 기여자의 성공 요약을 받기 전에 고정했지만, 첫 실행 전 그 성공·끝점 부호 요약을 받았다. 다른 기여자의 코드·상세 유도·원시 결과를 그 전에 읽지는 않았다는 기록이다. 따라서 인정하는 것은 **방법 설계의 독립성**이며 실행 시 눈가림은 아니다.

동결된 protocol의 원래 문구가 더 넓은 독립성을 말하는 부분은 [INDEPENDENCE_ACTUAL.json](../contributions/numerics/INDEPENDENCE_ACTUAL.json)이 실제 시점에 맞게 제한한다. 통합 보고서에도 이 한계가 반영돼 있다. 원 protocol을 사후 바꾸지 않은 처리와 제한된 독립성 주장을 수용한다.

## 6. 해결된 문서 결함과 그림

**R24-FORMAT-01 — 해결.** 최초 수치 노트에는 inline TeX 구분자 누락과 carriage return 10개가 있었다. 수치 기여자가 [원본](../contributions/numerics/history/MOMENT_NUMERICS_KO.before-format.md)을 보존하고 수식 63곳의 구분자 및 literal TeX를 복원했다.

검토자는 수정된 문서와 [정정 기록](../contributions/numerics/FORMAT_CORRECTION.json)을 읽고, CR을 의도한 literal TeX로 정규화한 뒤 역슬래시를 제외한 바이트가 동일함을 직접 확인했다. 코드·protocol·과학 결과·실행 기록 등 보호 파일 9개의 해시도 모두 그대로였다. 이 수정은 **문서 포맷 1건, 과학 수정 0건, 과학 재실행 0건**이다.

[최종 PNG](../figures/PHYS24_fixed_moment_envelope.png)를 직접 보았다. 하단과 상단의 순서, \(\mathrm{s}^{-4}\) 단위와 \(10^{-64}\) 축 배율, 평균 19 eV의 두 값, \(E_-,E_+\) 표시 및 경계의 등호 설명이 맞다. 고정 수치 \(J\), 초기 계수, physical HOLD라는 범위도 보인다. 곡선을 그린 241점은 표시용이며 독립 검산이나 continuum proof로 더하지 않았다. PDF는 동결 바이트만 연결했고 별도의 PDF 렌더 검토를 수행했다고 주장하지 않는다.

## 7. 문헌과 신규성의 판단 범위

Iosif Pinelis의 [On the extreme points of moments sets, arXiv:1204.0249v1](https://arxiv.org/abs/1204.0249)에서 서지/초록, Theorem 1과 관련 정의, Proposition 9의 Polish/Borel 조건 및 Corollaries 10–11을 직접 확인했다. 원문의 조건에서 \(f=(1,E)\)의 두 모멘트 극점 구조는 이번 적용과 부합한다. [원문 PDF](https://arxiv.org/pdf/1204.0249).

이 문헌은 일반적인 모멘트 구조를 지지하며 실제 HeIII 곡률, 새 경계의 소수값, Jacobian 정확도, 물리 admission을 지지하는 출처가 아니다. 이번 task-specific 정리는 평면 볼록껍질과 strict convexity로 직접 유도돼 있다. 2016년 저널 판본 전체나 그 논문의 인용문헌 원문까지 읽었다고 주장하지 않는다. 전역적 신규성·우선권 판단은 이 판정 범위에 넣지 않았다.

## 8. 유지되는 보류와 후속 질문

Physical HOLD, 기존 [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 그대로 유지한다. Source/default/runtime 변경으로의 승격 근거는 없다. 비영 초기 계수도 정량적 나머지 없이 유한 시간·유한 \(\epsilon\)의 전체 부호 보장으로 확대할 수 없고, 계수가 0이면 다음 시간차수는 미해결이다.

다음 단일 질문 **PHYS25_HEIII_SIGN_REVERSAL_VARIANCE_COST**는 적절하다. 평균을 18 eV로 고정하고 \(\int k\,dP\ge0\)를 만족시키는 최소 광자 에너지 분산을 묻는다. PHYS24가 보장한 anchored two-line zero-response law의 존재는 분산 최적성을 의미하지 않는다. [Handoff](../PHYS25_NEXT_HANDOFF_KO.md)는 이 차이를 명시하고, 제안한 dual inequality의 계수 부호도 비음수 응답 제약과 맞는다. 이번 판정은 그 질문의 수행을 위한 연결을 수용하는 것이며, 최솟값이나 최적 측도에 관한 PHYS25 결과를 승인한 것은 아니다.

## 9. 검토 종료와 후속 closeout의 경계

고정 질문의 과학적 근거는 위 조건부 상한에서 충분하다. 이 gate를 위해 추가 과학 실행이나 닫힌 PHYS19–23 suite의 재생은 필요하지 않다. 하나의 집중된 최종 판정으로 종료하며 재귀적 재검토를 요청하지 않는다.

이 검토문은 **61개 과학 후보 파일의 고정 identity**에 묶인다. 이후 portability replay, 최종 ZIP 복구, 저장 또는 Git 게시의 ACK/tree/blob 검증 성공을 이 판정에 미리 포함하지 않는다. 그 항목은 owner의 별도 closeout receipt에서 실제 증거로 확인해야 한다. 검토된 과학 바이트를 유지하는 범위의 이미 허용된 패키징·additive docs publication은 과학 최종 검토를 다시 돌리는 이유가 아니다.

