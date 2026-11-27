# BASS_HE E13C2 독립 최종 과학·코드 검토

## 판정

**`PASS_SCOPED` — 지정된 여섯 fixed-path transaction의 유한 수치 결과와 해석 범위에 한정한다.** Contract 검토는 `CONFIRMED_WITH_EXPLICIT_SCOPE`, Quality 검토는 `CONFIRMED_AFTER_RESOLVED_GATE_DEFECT`다. 현재 남은 blocking finding은 없다. 최종 판정은 이 문서를 작성한 독립 decision reviewer가 내렸으며, 이 reviewer와 Decimal sub-reviewer는 검토 대상 과학 코드의 contributor가 아니다.

승인한 주장은 다음과 같다. OFF/KF/GM의 저장된 첫 두 macro transaction, 총 14,652개 native event segment에서 같은 affine gas 경로·source·binary64 상수·event 규약을 유지하여 연속 coefficient correction의 부호와 크기, 흡수수와 에너지의 직접항/광자장 항을 계산했다. 저장된 두 적분 정밀도 결과, 여섯 독립 local Decimal control, 17개 exact formal identity 및 제한된 독립 검토가 이 유한 주장을 뒷받침한다. 이 판정은 완전 결합 gas 해, 전 시간 이력의 continuum error certificate, atomic accuracy, 물리·production 승격 또는 receiver adoption을 승인하지 않는다.

검토는 제공된 primary 경로와 oracle를 다시 실행하지 않았다. 원 코드와 source, saved evidence를 읽고 입력 identity·topology·수치 요약을 별도 계산했다. 실제 실행 검사는 검증기의 실패 경계에 대한 작은 negative fixture와 Decimal tableau 항등식으로 제한했다. Native 실행, gas advance, 기존 suite 재실행, 외부 mutation은 0회다.

## 실제 지적 사항과 해결

| ID | 심각도·분류 | 위치 | 관측한 문제 | 최종 상태 |
|---|---|---|---|---|
| IR-01 | Medium · implementation validation | 원 `code/verify_research.py:56–72`, 수정본 `:56–79` | symbolic evidence를 출력에 넣지만 `all_passed`를 PASS gate에 연결하지 않아 symbolic 실패를 무시할 수 있었다. | 수정 및 실제 negative regression 확인 |
| IR-02 | Low · provenance documentation | 양 primary 결과의 `input_hashes_verified`; `REPORT_KO.md:29–33`; `state/RUN_HISTORY.json:20–71` | 원 실행은 23개 입력을 확인했는데 최종 manifest는 24개여서 실행 당시와 전달 상태가 구별되어야 했다. | 원값 보존·시간 순서 명시·최종 24개 독립 hash 확인 |
| IR-03 | Low · reproduction documentation | 원 `ORACLE_METHOD_KO.md:119,149–151`; 수정본 `:119,158–166` | 원 작업장의 경로를 사용한 명령만 있었고 전달된 contract 경로가 달랐다. | historical 명령 보존·package 기준 명령 추가·contract 경로 수정 |

### IR-01의 실제 실패와 수정 확인

원 verifier의 SHA-256은 `b0a5c5f6597ee26573f49e0a1a840a649eef334efbd398ddd12138a0338fc423`다. 검토 중 읽은 원 source와 정확히 같은 hash가 되도록 이전 verifier를 복원했다. 원 candidate evidence는 수정하지 않고, 별도의 fixture에서 **symbolic `all_passed` 한 값만 `false`로 변경**했다.

| 같은 negative fixture | process exit | 출력 verdict | symbolic gate |
|---|---:|---|---|
| 원 verifier | 0 | `PASS_SCOPED` | 없음 |
| 수정 verifier | 1 | `FAIL` | `false` |

이 비교는 원 구현의 실제 잘못된 PASS를 보여주고 수정본의 거부 동작을 확인한다. 수정본 SHA-256은 `92f1e1b1250b8b95c625fda9a057ac03539cbaf817347cbc0f737b0b0e80fb7a`다. 수정본은 symbolic `all_passed`, 정확한 17/17 count, 여섯 unique local control을 gate에 포함한다. 진짜 저장 evidence에는 `VERIFICATION_FINAL.json`의 9개 gate가 모두 true다. 원 `VERIFICATION.json`과 negative fixture의 원 PASS·수정 FAIL을 모두 보존했다. 이 구현 결함을 물리 또는 수학 실패로 분류하지 않았다.

정확한 명령·exit code·결과 경로는 `NEGATIVE_GATE_REGRESSION.json`에, 해당 stdout/stderr와 JSON은 `FALSE_SYMBOLIC_*` 파일에 있다. 이 검사는 metadata gate와 이미 존재하는 작은 constant-coefficient zero-defect control만 실행했으며 primary variable-coefficient 경로를 재계산하지 않았다.

### IR-02의 시간 순서와 한계

두 원 primary 결과의 `input_hashes_verified=23`은 그대로 남아 있다. 이후 oracle provenance에서 참조한 원 `photon_green.py`를 24번째 입력으로 추가했다. Primary implementation은 이 파일을 import하거나 호출하지 않는다. Reviewer는 최종 manifest의 24개 입력 모두에 대해 SHA-256과 byte count를 직접 확인했고, oracle가 기록한 5개 source identity도 전달된 대응 파일과 일치함을 확인했다.

원 primary 결과는 실행 당시 producer script hash를 기록하지 않았다. `RUN_HISTORY.json:29,40,71`은 이를 명시하며, 현재 파일 hash를 과거 실행 당시의 hash 증거로 바꾸지 않는다. 현재 코드를 검토한 identity와 저장된 numerical evidence를 구별한다. 이 제한된 provenance를 정직하게 공개한 유한 검토를 승인하며, 기록되지 않은 과거 source identity까지 인증하지 않는다.

## 수학과 구현 검토

### 1. 차이 방정식과 moment의 부호

`code/continuous_defect.py:139–157`의 상태 배열은 endpoint defect 1개, 직접·광자장 count 6개, 직접·광자장 eV energy 6개, redshift 1개, source number·energy 2개로 총 16개다. 구현은

\[
e'=\delta q-\delta\Lambda\widehat P-\Lambda e,
\qquad
\Delta A_i'=\delta\lambda_i\widehat P+\lambda_i e
\]

를 사용한다. 연속 opacity가 feedback의 damping 및 moment 계수에 들어가는 것이 맞다. Frozen Green 함수와 연속 photon factor를 사용하는 다른 exact identity와 혼합하지 않았다. `energy*direct`, `energy*feedback`, `energy*e`, `energy*dq`는 각각 eV absorption, redshift, source energy 차이에 필요한 계수다. 정규화한 시간으로 적분하기 위해 마지막에 각 segment의 `h`를 곱한다.

`projection`의 HI, HeII, HeIII 방향은 각각 \(\Delta A_{HI}\), \((\Delta A_{HeI}-\Delta A_{HeII})/f_{He}\), \(\Delta A_{HeII}/f_{He}\)다. 에너지는 \(\epsilon\sum_i(\Delta B_i^{\rm eV}-\chi_i\Delta A_i)\)다. `continuous_defect.py:189–191`의 부호와 단위가 이 정의와 일치한다. Heat binding energy와 Verner support cutoff를 별도로 유지했다.

### 2. 구간 및 macro 경계의 전달

`continuous_defect.py:205–236`은 mode마다 초기화한 `previous`를 step 1에서 step 2까지 유지한다. 각 segment 뒤의 보정량은 연속 stock과 captured native endpoint의 차이이며, 다음 segment의 초기 defect는 그 연속 stock에서 다음 captured `f0`를 뺀 값이다. 작은 analytical-frozen/native 차이를 전달하여 연속 stock을 매번 native 값으로 reset하지 않는다.

전체 capture를 읽은 독립 검사에서 segment key 14,652개가 모두 unique이고 node/macro pair는 14,640개였다. Native photon number, 시간 경계, weight의 seam mismatch는 모두 0이었다. 각 mode의 첫 macro에서 모든 incoming stock은 0이었다. Binary64로 계산한 energy anchor의 인접 차이 최대값은 약 \(5.68\times10^{-14}\) eV였다. 따라서 segment energy ledger와 일반 macro의 anchor-reset ledger를 구별하는 보고서의 주의가 필요하며 적절하다.

집계 endpoint correction은 native endpoint 기준이고 moment defect는 각 captured `f0`로 시작한 local mathematical frozen 곡선 기준이다. `continuous_*_estimate`는 이 moment defect에 native baseline을 더한 추정치다. 이것을 전 구간에서 하나의 정확한 frozen stock을 재귀적으로 전달한 고정밀 baseline으로 바꾸어 읽으면 안 된다. `REPORT_KO.md:230–233`은 이 차이와 sealed/native baseline 차이를 명시한다. 여기서 segment ledger의 작은 값이 그 별도 baseline 층을 없애지는 않는다.

### 3. Source, branch, positivity와 outflow

Pinned `radiation.rs`, `e9_common_domain.cfg`, `atomic_provider.rs`, `igm_background.rs`와 두 구현을 비교했다. 상수 external source rate, \(E^{-2}\) number spectrum의 log-energy normalization, affine gas target fractions, proper density, FLRW Hubble 식, Verner 상수, binary64 \(\pi\)를 포함한 lift 규약이 일치한다. 별도 RCT photon source는 없다.

열린 event segment의 absorber mask는 captured midpoint, source mask는 captured `source_on`으로 유지한다. 선택된 threshold 직후 control은 HeI branch가 꺼지는 것이 맞다. 정확한 Green 표현에서 비음수 source와 opacity는 비음수 photon 해를 준다. 실제 primary 검사는 endpoint positivity이며, 여섯 oracle는 collocation stage와 끝점의 positivity를 확인한다. 보고서는 이를 전체 interval의 수치 positivity certificate로 확대하지 않는다.

현재 범위의 **segment, NODES, AGGREGATE** 세 층 모두 native outflow가 0임을 독립적으로 확인했다. Segment constructor의 nonzero-outflow rejection은 이 고정 입력 범위를 방어한다. 일반 HI cutoff outflow를 구현·검증한 결과는 아니다. 이후 capture 범위를 넓히면 node/macro outflow와 anchor 항을 포함한 새 계약이 필요하다.

### 4. Formal cubic 식과 유한 광학적 두께

`THEORY.md:213–318`의 endpoint, 일반 weighted moment, count, energy, heat, source 및 redshift leading coefficient는 직접 ODE 유도와 일치한다. 특히 absorption energy의 추가 \(-2\lambda_i'p\) 항과 redshift 부호가 맞다. `e13c2_symbolic_check.py`는 exact rational polynomial Picard 적분과 제시한 식을 비교하며, 현재 source hash와 저장된 17/17 결과가 일치한다.

이 차수 진술은 같은 incoming stock, smooth event-free coefficient, 고정된 계수 함수 및 도함수 bound를 전제로 한다. Threshold나 source discontinuity를 가로질러 적용하지 않는다. 실제 최대 \(\Lambda_mh=0.6405675703635162\)이므로 단순히 작은 무차원 \(h\)만으로 cubic truncation을 정량 보증할 수 없다. 보고서는 cubic 식을 설명용으로 제한하고 full defect ODE와 유한 refinement를 수치 근거로 사용한다. Duhamel coefficient-variation remainder의 bound도 enclosure를 실제로 계산했다는 주장 없이 제시한다.

## 수치 증거와 해석

| 독립적으로 확인한 항목 | 관측값·결과 | 허용되는 해석 |
|---|---:|---|
| 두 saved precision 결과의 최대 projected gap | \(1.2121859072\times10^{-9}\) old TOL | 사전 0.01 stability 기준 통과 |
| 여섯 local control의 Primary–Decimal \(P/A\) 차이 | \(7.6341288351\times10^{-24}\) | 사전 \(10^{-22}\) 비교 기준 통과 |
| 여섯 local control의 Primary–Decimal \(B\) 차이 | \(5.1048918360\times10^{-23}\) eV | 사전 \(10^{-20}\) 비교 기준 통과 |
| Decimal 20점–12점 최대 number 차이 | \(3.0633264815\times10^{-42}\) | 유한 차수 안정성 |
| Decimal 20점–12점 최대 energy 차이 | \(4.1967541098\times10^{-41}\) eV | 유한 차수 안정성 |
| Fine primary segment number ledger | 최대 \(5.6545549686\times10^{-27}\) | 구현된 segment identity의 수치 일치 |
| Fine primary segment energy ledger | 최대 \(8.0853518094\times10^{-26}\) eV | 구현된 segment identity의 수치 일치 |

Decimal sub-reviewer는 saved differences를 Decimal로 다시 계산하고 모든 embedded CSV row·stage와 code/source hash를 대조했다. ODE를 풀지 않는 tableau 검사에서는 모든 stage moment와 symplectic identity도 확인했다. 20점의 최대 stage-moment residual은 \(7.130450921490\times10^{-58}\), symplectic residual은 \(4.219840314249\times10^{-60}\)이었다. 독립 식·구현 검사에서 수학적 또는 수치적 결함을 찾지 못했다.

Primary 비교기는 Decimal 값을 binary64로 변환한 뒤 차이를 계산한다. 원 binary64 값을 Decimal로 정확히 lift하여 다시 비교해도 최대값은 각각 약 \(7.6341217171\times10^{-24}\), \(5.1048871015\times10^{-23}\) eV로 같은 사전 기준을 충족한다. 표시 마지막 자리의 차이는 gate 결론을 바꾸지 않는다.

여섯 control은 각자 captured `f0`로 시작하는 local problem이다. 모든 node의 둘째 macro까지 독립 고정밀 correction을 운반한 실험이 아니며, KF·source-off·zero-opacity와 일반 event construction을 독립 oracle로 모두 검증한 것도 아니다. Number ledger는 같은 quadrature로 구성되므로 작은 ledger와 높은 Decimal 자릿수가 error enclosure를 의미하지 않는다.

저장된 결과의 부호도 별도로 확인했다. 여섯 total heat 및 HI·HeI count defect는 음수, HeII count defect는 양수다. HeI 직접항은 첫 macro에서만 양수이고 둘째 macro에서는 음수이며, 광자장 항은 양 macro에서 음수다. 보고서가 첫 macro의 예를 전체 여섯 transaction으로 일반화하지 않는다.

총 heat 상대 차이는 약 \(-2.16279\times10^{-7}\)부터 \(-1.45775\times10^{-7}\)다. Energy correction을 원 algebraic TOL로 나눈 크기 약 142–278은 coefficient freezing 변화의 크기를 보여주는 비교 좌표다. 사전에 정하지 않은 continuum accuracy budget을 대신하지 않으며, physical FAIL 또는 physical PASS를 뜻하지 않는다.

## 보존한 실패 및 보호 상태

실제 발견한 실패는 IR-01의 validation gate implementation defect다. 원래 false PASS와 수정 후 예상된 FAIL을 보존했다. Reviewer는 새 mathematical/numerical failure를 발견하지 못했다. Producer가 기록한 `mpmath`·`sympy` 미설치와 문서 편집 도구 오류는 환경·도구 문제로 분류했으며 물리 실패로 합치지 않는다. Decimal/Fraction 대체가 그 환경 제한을 해결했다는 사실과 물리 정확도는 별개다.

| 보호 항목 | 유지 상태 |
|---|---|
| baseline RCT | `OFF` |
| actual atomic photon/heat/recoil moments | `null` |
| physical / production | `HOLD` / `HOLD` |
| HE-F2 / F09 | `OPEN` / `OPEN` |
| late k7/k59 stock | 별도 입력, 미해결 |
| legacy Gamma alias | `3.543295 FAIL` 보존 |
| receiver adoption | 별도 |
| global continuum certificate | 없음 |

## 판정이 묶인 파일 상태

`INDEPENDENT_REVIEW.json`은 검토한 네 scientific/verifier code, PLAN, THEORY, REPORT, oracle method, RUN_HISTORY, input manifest, 원 primary/node 결과, oracle·symbolic·검증 evidence의 byte count와 SHA-256을 기록한다. 입력 24개 각각의 identity는 검토된 manifest와 독립 read-only 확인 결과로 묶었다.

이 source 또는 scientific evidence의 변경은 새 검토가 필요하다. 패키지 파일 지도, 재현 wrapper, archive 및 외부 delivery receipt 추가는 이번 과학적 판정의 검증 대상이 아니다. Root owner는 이 `PASS_SCOPED`를 유한 E13C2 노드의 실제 독립 검토 결과로 기록할 수 있다. 외부 게시·보관·수신·채택의 성공을 이 reviewer가 확인했다고 표현하지 않는다.
