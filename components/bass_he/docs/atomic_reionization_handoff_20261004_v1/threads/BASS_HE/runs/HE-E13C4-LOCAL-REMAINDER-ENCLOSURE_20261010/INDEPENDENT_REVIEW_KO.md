# BASS_HE E13C4 — 독립 decision review

## 판정

**`PASS_SCOPED` — 같은 여섯 exact-lift local initial-value problem의 correction enclosure에 한하여 채택한다.** Physical/production 판정은 **HOLD**다. 확인된 범위에서 미해결 blocking finding은 없다. NCP actual host replay와 전체 path의 incoming/anchor 전파는 이 판정으로 완료되지 않는다.

검토자는 `/root/e13c4_independent_review`이며 후보의 이론·구현·acceptance 설계 또는 contributor 검산을 작성하지 않았다. 후보가 실행된 뒤 별도 역할로 PLAN, 실제 코드, 결과와 raw 실행 기록, 이론 기여, 최종 보고서와 NCP 인계문을 읽었다. 검토자가 추가로 실행한 수치 검사는 저장된 endpoint를 `fractions.Fraction`으로 읽는 작은 독립 audit다. Owner solver를 import하지 않았고 coefficient, continuous reference, native/gas/Newton 계산을 다시 실행하지 않았다. 공유한 것은 고정 과학 입력과 검토 대상 증거이며, 독립성은 다른 원자 단면적 데이터셋 또는 다른 물리모형과의 일치를 뜻하지 않는다.

## 1. 방어된 과학적 주장

`PLAN.json`은 첫 primary run보다 먼저 작성됐으며, 세 P60 primary 및 P80 precision control의 START가 동일한 PLAN·입력·두 핵심 source SHA를 결속한다. 대상은 OFF/1/0/0, OFF/1/1162/0, OFF/1/1976/0, GM/2/1727/0, GM/2/2333/0, OFF/2/700/1이다. 각 구간의 captured f0, 정확한 incoming 0, affine gas path, mask, source law와 energy anchor를 유지한다.

다음 항목을 정의에서 구현까지 확인했다.

1. **True defect와 remainder의 부호.** e=P−P_f, r=δq−δΛP_f로부터 e′+Λe=r이고, R=e−e1은 R′+LR=−δΛe다. 비음수 true opacity의 Green 함수로 `sup|e|≤B_r`를 얻은 다음 frozen Green 함수를 사용하므로, S=B_r와 weighted remainder bound의 결합은 유효하다. Λ와 L을 같은 계수로 바꾸거나 δΛe1의 original-equation residual을 지우지 않았다.
2. **종별 결합 kernel.** R_Ai=∫[δλ_i−λ_if K0 δΛ]e, R_Bi=∫[Eδλ_i−λ_if KE δΛ]e의 적분순서 교환과 코드의 effective integrand가 일치한다. Heat에는 E−χ_i와 KE−χ_iK0를 함께 유지한다. 총 count remainder를 endpoint remainder로 제한하는 것과 총 energy ledger를 사용하는 것도 정확하다. 총 opacity의 cancellation을 종별 count/heat의 정확성으로 확대하지 않는다.
3. **Positive heat kernel의 사용 범위.** Active species의 E−χ_i≥0를 전체 cell에서 확인한 뒤에만 triangle heat kernel을 비음수 영역과 교차한다. Inactive species의 opacity와 frozen opacity는 정확히0이므로 사용하지 않는 음수 heat weight가 잘못된 기여나 domain 실패를 만들지 않는다.
4. **Captured freezing과 branch.** q_f, λ_if는 mathematical midpoint로 다시 정의되지 않는다. 직접 δq와 δλ를 포함시킨 interval 적분이 midpoint mismatch도 감싼다. 고정 branch의 analytic extension과 실제 threshold-event placement 문제를 구분한다. Verner 식의 log·sqrt·division domain, gas fraction과 opacity/source positivity가 각 실제 whole-cell 평가에서 확인된다.
5. **정규화.** P/count는 photons per H nucleus per dη, B/H/Z는 여기에 eV를 곱한 정규화다. 새 moment 적분에 spectral weight나 erg 변환을 중복 적용하지 않는다. Binary64 상수와 CSV의 exact lift, 기존 math.pi 및 binding energy를 유지한다.

이 판정의 대상은 **continuous-minus-exact-frozen correction**이다. Native saved baseline에 correction을 더한 absolute output의 certificate에는 exact-frozen/native-frozen representation 항이 추가로 필요하다. `THEORY.md` 식(33), `REPORT_KO.md` 및 `PHYSICAL_RESULT.json`이 이 한계를 명시한다.

## 2. Interval 및 적분 인증의 근거

기본 사칙연산은 explicit FLOOR/CEILING context를 사용한다. 부호 반전과 exact input은 ambient Decimal precision의 영향을 받지 않는다. Exp/ln의 올바른 최근접 반올림 결과를 양쪽 representable neighbour로 넓히는 방식은 Python 3.12의 문서화된 보장을 전제로 한다. Sqrt는 반환 endpoint의 제곱 부등식을 방향 반올림으로 추가 확인한다. 일반 C Decimal의 비정수 power를 보장 없이 사용하지 않는다. 관련 arithmetic API와 한계는 [Python Decimal 문서](https://docs.python.org/3.12/library/decimal.html)에서 직접 확인했다. 실행 환경은 CPython3.12.14/libmpdec4.0.0이고, 현재 열람 문서 제목은 Python3.12.15다. 전체 runtime을 proof assistant로 형식 검증했다고 해석하지 않는다.

`Jet2.d2`는 normalized t에 대한 실제 2차 도함수다. 곱·역수·제곱·exp·ln·sqrt의 chain rule 계수와 interval 합성이 맞는다. Signed integrand f의 cellwise bound M_j를 사용한 midpoint 잔차는

\[
\left|h\int_0^1 f(t)dt-\frac{h}{N}\sum_j f(m_j)\right|
\le \sum_j\frac{hM_j}{24N^3}
\]

이며, t=u/h에 따른 chain factor를 놓치지 않는다. Grid는 dyadic rational partition이므로 같은 exact [0,1]을 덮는다. 절댓값의 내부 kink가 가능한 D_L, B_r와 effective remainder에는 이 smooth midpoint 정리를 적용하지 않고 whole-cell Riemann range를 사용한다.

정확한 first variation이 J=[J−,J+] 안에 있고 수학적 remainder가 B_rem 이하이면, 저장 후보 C에 대한

\[
|X-C|\le B_{\rm rem}+\max(|C-J_-|,|C-J_+|)
\]

는 타당하다. 이 식은 저장 후보가 새 midpoint 알고리즘으로 만들어졌다는 전제를 요구하지 않는다. 후보의 numerical enclosure와 수학적 coefficient truncation은 결과에서 분리된다. Source correction의 수학적 truncation0과 유한 source 적분오차0을 혼동하지 않는다.

유한 고정밀 point 대조는 구현 진단이다. 전체구간의 포함성을 그 일치로 증명한 것으로 취급하지 않았다. 각 연산·도함수·고정 branch의 합성에 대한 직접 검토가 이론적 포함성 논증을 제공하고, 실제 interval 실행 및 별도 rational/derivative controls가 구현의 판별 근거를 제공한다.

## 3. 실제 증거와 검토자 실행

| 근거 | 실제 확인한 결과 | 판단 범위 |
|---|---:|---|
| N32/P60, N128/P60, N512/P60, N32/P80 | 네 actual exit0; run당168 saved comparison; 실패0 | 고정 six-local 실행과 출처 일관성 |
| Theory contributor의 exact toy | 63 PASS | remainder/kernel/ledger/incoming 및 midpoint 반례 |
| 별도 numerical contributor의 primitive/Jet2 | 386 PASS | Decimal transcendental을 쓰지 않는 Fraction enclosure 및 독립 도함수 진단 |
| 별도 coefficient diagnostics | 632 PASS | 원 CSV 선택,30개 point의 coefficient·E/q derivative 비교 |
| Owner saved-evidence audit | 448 PASS | owner의 결과 일관성 검사; 독립 판정으로 세지 않음 |
| 이 decision reviewer의 exact Fraction audit | **291 PASS, actual exit0** | 저장된 interval·bound 결합·분모/ratio·입력/로그 출처를 owner 산술 없이 대조 |
| NCP adapter boundary fixtures | 7 PASS | synthetic child의 새 결과 비교, source mismatch, output 충돌, timeout 보존 |

검토자 audit의 raw stdout/stderr, 실제 argv·시작/종료·source SHA와 결과는 `evidence/review/REVIEW_AUDIT_RUN.json`, `SAVED_EVIDENCE_AUDIT.json` 등에 있다. Audit process elapsed는0.265621599초였고 수치 본문 elapsed는0.193538764초였다. 새 solver 실행 수는0이다. 독립 audit가 확인한 것은 선언된 상계의 저장·결합 산술이며, 291이라는 개수가 전체 물리 증명을 대신하지 않는다.

Audit는 E13C3 원본 JSON과 selected six controls의 row/stage·mask·후보·reference 연결, START/checkpoint/run 및 원 로그, 저장 interval의 유효성, η_num+B_rem의 outward 합성, source remainder0, inactive species0, ledger 포함성과 floor/ratio 규칙을 확인했다. N refinement의 firstvariation interval nesting과 P60/P80 nesting도 실제 성립했다. 이는 sharpness·일관성 진단이며 독립적인 연속해 oracle로 기록하지 않는다.

N512/P60 총 heat의 후보 전체오차 상계는 여섯 구간에서 **2.77425549e−19–1.06699941e−17 eV-normalized** 규모이며, 해당 saved signed defect 절댓값으로 나눈 진단 비율은 **7.69234e−6–1.15454e−5**다. 보고서의 양의 상계 표기는 JSON 값보다 작아지지 않도록 표시되었음을 exact rational 비교로 확인했다. Reference의 order gap은 수치 증거이며 엄밀한 reference uncertainty가 아니다. 따라서 이 비율을 exact physical budget이나 원래 관측된 약1e−8 오차의 엄밀 인증으로 확대하지 않는다. Number1e−25, energy/heat1e−24 eV 아래의 상대값과 sharpness는 unresolved로 남는다.

## 4. 발견 항목과 처리

| 항목 | 근거와 처리 | 상태 |
|---|---|---|
| 최초 J zero-rate domain 실패 | 보존된 구 source에서 J(0,−1)이−1을 반환했다. Width guard를 zero-rate 분기 앞으로 옮긴 diff와 후속 primitive control을 확인했다. 실제 six control의 양의 폭에는 영향이 없었다. | **RESOLVED** |
| 실행 순서 설명 | N32/P80은 N128/P60과 겹쳤다. 세 P60 primary는 순차였다. Owner 보고서와 acceptance가 이를 명시하며 speedup claim을 하지 않는다. | **RESOLVED** |
| Git 최소 runtime과 전체 research payload의 표현 | README와 NCP contract의 용어 차이를 지적했다. Contract는 현재 minimal runtime 포함과 full research payload 미포함을 따로 기록하고 archive의 provenance 목적을 명시한다. | **RESOLVED** |
| NCP wrapper의 마지막 변경 | 7개 fixture의 adapter에서 최종 adapter로의 변경은 allowlisted host environment 기록4줄이다. 실행·parity·timeout 경로의 동등 diff와 최종 source/lock을 읽는 verify-only actual exit0을 확인했다. | **DEFENDED** |

Negative fixture의 예상 nonzero exit를 physical primary failure로 세지 않았다. 실패한 domain probe와 당시 source는 그대로 보존되었다. 저장된 후보/reference의 합치는 검사만으로 remainder 부등식의 잘못을 덮지 않았다.

## 5. NCP handoff와 남은 경계

NCP 인계문은 CPython3.12.x, 동일 N512/P60·여섯 local controls, 단일 scientific process, wall180초와1GiB RLIMIT_AS의 host replay를 구체적으로 지시한다. Source/input lock과 actual fresh output의 deterministic numerical projection을 따로 확인한다. Source/host 확인만 한 `VERIFY_ONLY_PASS`는 과학 실행이나 새 numerical parity를 뜻하지 않는다. 새 output mismatch를 의도적으로 주는 synthetic fixture가 실제로 실패하므로 saved-only 검사를 fresh parity라고 부르는 경로가 아니다.

현재 **actual NCP execution은 NOT_RUN**이다. Synthetic pass fixture의 child 실행도 NCP 물리 계산으로 해석하지 않는다. 최종 wrapper의 metadata-only verify는 과학 실행0이며 `new_result_accuracy=NOT_EVALUATED`다. 다른 host에서의 numerical equality와 runtime은 실제 NCP output이 있어야 판단할 수 있다.

미확립 범위는 전체 first2/path, nonzero incoming uncertainty와 anchor/representation 전파, native absolute output, 새 gas/native/continuous history, actual atomic RCT spectrum·heat·recoil, late k7/k59 stock, receiver/physical budget이다. 다음 연구 node는 **E13C5_FIXED_PATH_INCOMING_AND_ANCHOR_ENCLOSURE**이며 ChatGPT 연구 스레드에서 작은 seam/incoming 문제를 먼저 유도·구현하는 것으로 남긴다. 이번 NCP executor에 그 설계를 묵시적으로 넘기지 않는다.

`baseline_RCT=OFF`, actual atomic photon/heat/recoil `null`, physical/production `HOLD`, HE-F2/F09 `OPEN`, receiver `SEPARATE`, Gamma alias `3.543295 FAIL`을 유지한다.

## 6. 판정의 결속과 종료

실제로 읽은 범위와 현재 SHA256/크기는 `evidence/review/READ_FILE_IDENTITIES.json` 및 `INDEPENDENT_REVIEW.json`에 기록한다. 큰 JSON은 완전히 parse한 뒤 관련 필드·모든 검사 상태를 대조한 범위를 명시하며, 이를 모든 byte의 수동 의미 검토로 부르지 않는다. 원 helper는 상수·선택 구조와 coefficient 정의 부분을 읽었으며 old solver 본문은 새로 실행하지 않았다. 보고서 그림은 직접 시각 확인했고 수치 certificate의 원본은 JSON이다.

`state/RESEARCH_STATE.json`은 owner의 판정 직전 snapshot이다. 최종 decision source는 이 review이며, owner가 이어 작성하는 CLOSEOUT과 delivery receipt가 실제 봉인·게시·백업 상태를 기록한다. 이 독립 과학 판정은 아직 실행되지 않은 publication 또는 remote backup/restore를 검증했다는 뜻이 아니다. 후속 운영 파일을 추가할 수 있으나, 결속한 과학 입력·코드·결과·보고서/인계문을 변경하면 영향받는 결속과 검토 범위를 다시 밝혀야 한다.

필수 국소 정확성 검토와 구체적 발견 사항의 처리가 끝났으므로 추가 과학 실행이나 재귀적인 리뷰 없이 **PASS_SCOPED**로 종료한다.
