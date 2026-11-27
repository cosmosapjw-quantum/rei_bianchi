# BASS_HE E13C3 — 독립 decision review

## 판정

**`PASS_SCOPED`.** `E13C3_EXPONENTIAL_DEFECT_CORRECTION_ON_FIXED_GAS_PATH`의 새 1차 보정은 고정한 여섯 국소 control과 OFF/KF/GM first2의 **여섯 macro transaction**에서 사전 선언한 signed total-heat defect 기준을 만족한다. 이 범위의 연구 후보로 받아들인다. 물리·production 판정은 **HOLD**다.

심사자는 `/root/e13c3_independent_review`이며, 주 구현·Decimal 구현·이론 검산·실험 acceptance 설계의 contributor가 아니다. 완성된 계산을 읽고, 원래 solver를 호출하지 않는 저장 증거 감사만 별도로 작성·실행했다. 검토 문맥은 owner의 과제 설명과 기존 문맥을 포함하며, blinded review나 독립적인 원자물리 모델 검증을 주장하지 않는다. 검토한 바이트와 범위는 함께 제공한 `INDEPENDENT_REVIEW.json`에 고정했다.

## 1. 판정의 직접 근거

`PLAN.json`은 heat defect의 1%를 후보 판정 기준으로 둔다. 분모는 저장된 continuous-minus-frozen **열결함**이며, 전체 가열량이나 물리 허용오차가 아니다.

| 확인 항목 | 실제 증거 | 판정 |
|---|---:|---|
| 여섯 local total-heat defect 최대 상대오차 | 9.820472540361232×10⁻⁹ | 사전 0.01 기준 충족 |
| 여섯 macro total-heat defect 최대 상대오차 | 1.6479380133725416×10⁻⁸ | 사전 0.01 기준 충족 |
| Local GL8/12 최대 상대 차이 | 1.9533765984744287×10⁻¹¹ | 사전 10⁻⁵ 기준 충족 |
| Macro GL8/12 최대 상대 차이 | 4.700431869011842×10⁻¹³ | 사전 10⁻⁵ 기준 충족 |
| 새 주 구현·Decimal photon/count 최대 절대 차이 | 2.604326459834923×10⁻²⁴ | 사전 10⁻²² 기준 충족 |
| 새 주 구현·Decimal absorption energy 최대 절대 차이 | 2.813544993674019×10⁻²³ eV | 사전 10⁻²⁰ eV 기준 충족 |
| 실제 primary kernel 검사 | 64/64 PASS | 영흡수율·영구간·일반 incoming·상수계수 포함 |
| 새 exact algebra 검사 | 317/317 PASS | 유한 rational-rate control, 일반 incoming 변수 포함 |
| Local / final 판정 파일 | 104 / 136 checks PASS | 개별 flags가 최종 verdict에 포함됨 |

위 숫자는 `evidence/LOCAL_ACCEPTANCE.json`, `evidence/FINAL_ACCEPTANCE.json`, `evidence/decimal/DECIMAL_RESULTS.json`, `evidence/KERNEL_CHECKS.json`, `evidence/theory/THEORY_CHECKS.json`에서 읽고 대조했다. 검사 수는 증거의 종류를 식별하기 위한 값이며 수가 많다는 이유로 과학적 독립성이 커지는 것은 아니다.

## 2. 수식과 구현의 대응

Frozen stock과 계수의 정의, forcing의 부호, eV/erg 구분, species count 및 heat의 결합 에너지를 확인했다. 특히 `q_f`, `lambda_if`는 captured binary64 midpoint 값의 exact lift다. 다시 계산한 실수 midpoint와의 작은 차이도 delta coefficients에 포함한다.

새 endpoint와 Fubini moment 계산은 다음 방정식을 일관되게 구현한다.

\[
e_1'+L_f e_1=\delta q-\delta\Lambda P_f,
\qquad e_1(0)=e_a.
\]

에너지 response kernel은 forcing 시점의 \(E(v)\)와 감쇠율 \(L_f+1\)을 사용한다. 초기값은 endpoint뿐 아니라 두 적분 moment에도 포함된다. `expm1`의 제거 가능한 영흡수율 극한과 감쇠 exponential의 직접 평가를 확인했다. \(L_fh\)를 작은 양으로 전개하지 않지만, 이것이 임의의 큰 optical depth에서 GL12의 정확도를 보증하지는 않는다.

`path_work`는 이전 correction을 0으로 reset하지 않는다. 이전 native endpoint, analytic frozen endpoint와 다음 captured `f0`의 representation 차이를 기존 E13C2와 같은 방식으로 운반한다. 입력 분할·source/absorber mask·energy anchor를 바꾸지 않는다. 현재 zero-outflow 범위를 벗어난 입력은 재사용한 domain guard가 거부한다.

1차 number/energy ledger의 closure는 공통 quadrature에서 성립하는 kernel 항등식이다. 이 수치 잔차가 작다는 사실은 원래 연속계수 해의 정확도를 독립적으로 보증하지 않는다. 보정 field \(P_c=P_f+e_1\)에는

\[
P_c'+\Lambda P_c-q=\delta\Lambda e_1
\]

가 남고, full species moments에는 \(\int\delta\lambda_i e_1\)가 남는다. 총 opacity 변화가 상쇄되더라도 종별 moment의 정확성을 자동으로 결론내릴 수 없다. 보고서와 이론은 이 차이를 명시한다. Incoming이 독립적인 \(O(1)\)이면 전체 remainder가 균일하게 2차라는 주장을 할 수 없다는 조건도 맞게 유지했다.

## 3. 독립 저장 증거 감사

심사자는 별도 review 작업 디렉터리에서 `audit_saved_evidence.py`를 한 번 실행했고, 그 코드와 실제 command receipt를 `evidence/review/`에 보존한다. 실제 exit code는 **0**, **184 checks PASS**다. 이 실행은 입력·코드 해시, AST의 helper 호출 목록, 저장된 숫자의 합산과 비교만 수행했다. 주 후보나 부모 solver를 import하거나 새로운 물리 해를 계산하지 않았다.

감사에서 확인한 내용은 다음과 같다.

- 상속 입력 34개가 각각 고정된 SHA-256·바이트 수와 일치한다.
- 네 primary 실행의 코드·helper·입력 manifest 해시가 실행 전 기록과 결과에서 동일하다. 실제 차수, stage, longdouble significand 및 계수 샘플 수가 맞다.
- Decimal·theory·kernel의 개별 check flags도 통과한다. 요약의 PASS 문자열만 신뢰하지 않았다.
- GL12의 exported node row **14,640개**는 중복 없이 여섯 macro에 2,440개씩 있다. 각 row의 16개 moment를 독립 Decimal 산술로 가중 합산해 macro 출력을 재구성했다.
- 재구성 차이는 number 계열 최대 **3.83×10⁻²⁹**, energy 계열 최대 **1.45×10⁻²⁸ eV**였다. 이 감사의 직렬화 산술 여유는 과학적 허용오차나 새로운 candidate criterion이 아니다.
- 두 차수에서 사용한 event segment 수는 각각 **14,652개**다. 저장된 결과만으로 여섯 macro heat 및 GL 기준을 별도로 계산해 같은 판정을 얻었다.

독립 감사는 exported binary64 값을 Decimal로 정확히 올려 합산한다. Owner의 binary64 합산을 거친 reference total과 극미한 마지막 자리 차이가 있어 macro 상대오차의 표시 마지막 자리는 완전히 같지 않을 수 있다. 최대값은 동일하게 약 \(1.6479380\times10^{-8}\)이며 판정과 해석에 영향을 주지 않는다. 감사의 상세한 항목·해시·실행 receipt는 `evidence/review/`에 있다.

## 4. 구현 독립성과 재사용의 한계

주 구현은 부모 `SegmentBatch`의 계수 정의·frozen stock·입력 parsing·unit projection을 재사용한다. 별도 Decimal contributor는 부모 Decimal의 `Coefficients`와 Gauss rule을 재사용하되 frozen field와 response/moment 식을 새로 구현했다. AST와 코드 읽기에서 허용된 helper만 호출함을 확인했다. 기존 `solve`, `collocate`, oracle main이나 native/gas 실행은 새 코드의 호출 경로에 없다.

따라서 새 Decimal 비교는 coefficient-variation 보정 구현과 산술의 별도 검증이다. 공유한 원자 cross-section, source, gas path, cosmology 또는 기존 reference의 완전한 독립 검증은 아니다. 원래 continuous reference와 옛 과학 suite는 다시 실행하지 않았으며, 관련 scientific authority는 고정된 E13C2 증거에 의존한다.

## 5. 검토 중 수정한 항목

| ID | 분류 | 수정과 확인 |
|---|---|---|
| THEORY-01 | 수학적 bound의 조건 | Captured frozen 값에는 \(D_L\le\|\Lambda'\|_\infty h^2/4+h|\Lambda(m)-L_f|\)가 필요하다. 마지막 항과 exact-midpoint 조건을 확인했다. |
| REPORT-01 | 결과의 집계 단위 | 최대 heat-defect 상대오차가 여섯 macro aggregate에 대한 값임을 보고서 첫 문단과 다음 인계문에 명시했다. |
| REPRO-01 | 재현 verdict의 의미 | Optional recompute는 fresh-output parity를 판정하지 않는다. 코드·README·보고서에 `new_output_parity_checked=false`, `new_output_accuracy_verdict=NOT_EVALUATED`, saved-evidence-only verdict 범위를 명시했다. |

세 항목은 모두 최종 바이트를 고정하기 전에 해결되었다. 보정 알고리즘·실행 결과·사전 수치 기준을 바꾸지 않았으므로 새 과학 실행은 필요하지 않았다. 이것들은 검토 finding이며, 실패한 solver 실행을 성공으로 바꾼 기록이 아니다. 원래 발견과 해결은 `evidence/review/REVIEW_FINDINGS.json`에 보존한다.

## 6. 비용 및 물리적 claim ceiling

GL12의 scientific coefficient samples **175,824회**와 저장된 E13C2 path RHS/segment 평가 **2,711,100회**의 비 **15.4194**를 확인했다. 계수 평가 수의 비교이며 전체 기계 연산 수나 통제된 wall-time 가속 배율이 아니다. 이번 GL12 시간 1.220697 s와 과거 전체 실행의 7.612775 s는 서로 다른 부대 작업과 실행 시점의 측정이다.

Endpoint 비음수와 aggregate absorption/heat 비음수는 계산한 유한 값에 대한 확인이다. 전체 구간의 positivity proof, macro energy anchor seam을 포함한 엄밀한 certificate, cross-section uncertainty, 새 gas evolution이나 실제 원자 RCT emission을 검증하지 않았다. Quadrature로 추정한 절댓값 적분은 rigorous upper bound로 쓰지 않는다. 저장 reference와의 비교값에도 reference 자체의 수치 불확실성이 있으며, 이를 interval certificate로 해석하지 않는다.

다음 `E13C4_LOCAL_REMAINDER_ENCLOSURE_ON_FIXED_GAS_PATH`의 제안은 적절하다. 먼저 같은 여섯 국소 구간에서 domain 포함성·outward rounding·species remainder를 명시해야 한다. Local 성공만으로 incoming error와 energy anchor를 포함하는 full-path certificate를 주장할 수 없다. 물리 accuracy budget과 receiver adoption은 별도 owner gate다.

## 7. 보호 상태 및 전달 경계

| 상태 | 최종 심사에서 유지 |
|---|---|
| baseline RCT | OFF |
| actual atomic photon / heat / recoil | null |
| physical / production | HOLD / HOLD |
| HE-F2 / F09 | OPEN / OPEN |
| receiver adoption | SEPARATE |
| legacy Gamma alias 3.543295 | FAIL |
| uniform interval certificate | NOT_ESTABLISHED |

`PHYSICAL_RESULT.json`의 summary는 실행된 `FINAL_ACCEPTANCE.json`과 같고, 보호 상태는 `PLAN.json`·`NEXT_DAG.json`·판정 파일에서 일치한다. 새 보고서·이론·인계문·재현 코드·상태 기록을 함께 검토했다.

이 decision은 과학 payload를 고정하고 다음 연구 단계로 넘길 수 있다는 범위다. 최종 manifest 생성, 기본 saved-evidence 재현 명령, 실제 Git publication과 Drive/Dropbox acknowledgement는 owner의 후속 전달 단계다. 심사 시점에 아직 실행하지 않은 저장·원격 복원·optional recompute를 완료했다고 인증하지 않는다. Owner는 이미 허용된 전달을 완료하고 실제 receipt를 별도로 남겨야 한다.

**해결되지 않은 E13C3 blocker는 없다.** 현재의 finite fixed-path correction에 대한 `PASS_SCOPED`를 승인하며, 추가적인 옛 solver 재실행이나 반복 전면 검토는 요구하지 않는다.
