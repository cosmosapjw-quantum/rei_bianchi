# HI massive-stress 독립 심사 — PREEXECUTION_ONLY

단위: `HI_NATIVE_MASSIVE_STRESS_20261025`  
검토자: `/root/source_and_review`  
선택 단계: **R6/C9의 한 번의 독립 pass**. 새 theory/code authoring0, science/CAS/test/render0, 추가 reviewer0, review-of-review0.

## 현재 판정

**PREEXECUTION_ONLY — frozen 이론의 blocker0; 초기 구현에서 현재 certificate finding1을 확인했고 pre-GO 최소 수리 중이다.** 코드·diff는 읽었고 실행 raw는 아직 받지 않았으므로 구현/실행의 최종 PASS를 발행하지 않는다. 부모의 scoped admission과 실행 GO를 대신하지 않는다. 수리된 부분과 raw가 제공되면 이 동일 pass를 완료한다.

## 적용한 skill context

부모가 공급한 PhysMath Research Loop **1.3.0**의 다음 원문을 실제로 전체 읽었다.

- `authority/skill_context/SKILL.md`
- `authority/skill_context/POLICY_INTEGRATION.md`
- `authority/skill_context/THEORY_LOOP.md`, R6 정의 적용
- `authority/skill_context/CODING_LOOP.md`, C9 정의 적용
- `authority/skill_context/SUBAGENT_MODE.md`

이 범위에서 단위·부호·제한·수치 의미와 현재 변경의 위험을 확인하고, 증거 없는 일반 hardening이나 주변 연구 재실행을 요구하지 않았다. 과거 source intake는 입력 사실을 읽는 역할이었으며 현재 심사 대상 theory/implementation의 작성에 참여하지 않았다. 이 검토는 실제 native child의 독립 pass다. cross-family/실제 실행 model label은 관측 근거가 없으므로 주장하지 않는다.

## 실제 읽은 대상과 source

`theory/THEORY_MASSIVE_STRESS_KO.md`, `authority/IMPLEMENTATION_CONTRACT.json`, `authority/BUDGET_FREEZE.json`, `authority/AGENTS_CURRENT.md`, `theory/LITERATURE_INTAKE.json`을 실제 읽었다. 정확한 byte identity는 같은 폴더의 `REVIEW.json`에 기록한다.

NIST 공식 [2022 CODATA complete table](https://physics.nist.gov/cuu/Constants/Table/allascii.txt)의 electron mass energy equivalent in MeV 행(L104)을 직접 열었다. `0.51099895069 MeV`, 표기 uncertainty `0.00000000016 MeV`는 계약의 decimal nominal `510998.95069 eV`, `u=0.00016 eV`와 일치한다. 명목 decimal을 exact 입력으로 정의하는 것과 물리 참값을 exact라 주장하는 것이 구별되어 있다.

Sarbach–Zannias [arXiv:1303.2899v1](https://arxiv.org/html/1303.2899v1) §7, Eqs.54–58 및 바로 뒤 mean-pressure 정의를 직접 열었다. local orthonormal observer frame의 stress moment를 finite source measure에 적용하는 사용은 해당 식의 범위와 일치한다. 이 확인은 새 물리 source history/geometry를 제공하지 않는다.

## R6 확인 내용

| 항목 | 독립 확인 | 현재 판정 |
|---|---|---|
| Kinetic trace | `E=k+M`, `p²c²=k(k+2M)`, `v=pc²/E`에서 `pv=g`. 등방 평균은 대각 trace/3, flux/STF0 | 확인 |
| 단위·owner | W는 eV/target/proper-second의 source moment. 실제 stock·thermal heat가 아니며 `MA`를 에너지 ledger에 추가하지 않음 | 확인 |
| M의 의미 | 새 M0는 NIST nominal decimal binding. 과거 미사용 `_ME_EV` 및 native χ를 수정하지 않음. ±u는 sensitivity probe | 확인 |
| 미분·concavity | `g_k=1+M²/(k+M)²`, `g_M=k²/(k+M)²`; Hessian quadratic form은 `−2(Ma−kb)²/(k+M)³` | 확인 |
| 범위·극한 | k=0, M→0+, M→∞, finite positive weights에서 `K≤W≤2K`; empty/zero에서 ratio null | 확인 |
| Support bound | `k/(k+M)≤L/(L+M)`에 `kw`를 곱해 적분하면 D bound. W 하한으로 ratio bound의 방향도 맞음 | 확인 |
| Mass endpoint | 증가·concavity로 오른쪽 increment≤uS0, 왼쪽 increment≥uS0. M−u>0인 frozen 입력 | 확인 |
| JVP | 고정 μ에서 `dm=a dX+X da`, `dq=(dm W+m dM S)/3`. dM은 모델 tangent이며 질량 시간진화를 뜻하지 않음 | 확인 |
| Hand control | `(0,1),(2,3), M=1`에서 W8, S4/3, D4, pressure8/3. m6,dm1,dM3은 source16,JVP32/3 | 확인 |

위 손계산은 식을 읽고 대수적으로 대조한 검토이며 실행된 test/CAS로 기록하지 않았다. actual atom 합은 재계산하지 않았다.

## Directed enclosure의 증명 확인

각 rational term을 양의 dyadic δ로 나눈 floor/ceil은 signed term에도 정확한 하·상계다. 항별 enclosure를 정수로 합하면 실제 합이 그 interval에 있고 각 항의 폭은 δ 이하이므로 총 폭은 Nδ 이하다. `E=floor(log2(max|t|))`가 exact 비교로 고정되고 P만128→160으로 바뀌면 fine dyadic grid가 coarse grid를 세분하므로 두 interval이 nested한다. 서로 다른 일반 분모의 총합을 만들지 않아도 이 결론은 유지된다.

정확한 interval에 부호 있는 scalar를 곱할 때 endpoint 순서를 필요에 따라 교환하고, interval 합/차 및 양의3 나눗셈을 하면 source/JVP/D의 enclosure가 보존된다. 정확한 두 endpoint가 같은 finite binary64로 반올림되면 그 사이 정확한 값도 같은 수치로 반올림된다는 단조성 논증은 맞다. 코드에서는 signed zero를 포함한 출력/분류 의미를 확인해야 한다.

정확한 합이0이라는 보장은 `[0,0]`에서만 발행하고,0을 제외한 interval이0으로 반올림되면 final underflow로 분류하는 설계가 타당하다.0을 포함하는 비퇴화 interval에는 exact-zero 분류를 내지 않는다. 고정 precision이 취소/반올림 경계를 해결하지 못하면 명시적인 unresolved가 정상 결과다. 이 상태를 PASS를 위한 precision/tolerance 변경으로 감추지 않는 계약을 확인했다.

Decimal100은 별도의 유한정밀도 numerical reference이며 정수 interval proof를 대신하지 않는다. 다른 식의 Decimal sum을 exact finite decimal로 파싱하여 interval 안에 있는지 확인하는 acceptance는 numerical agreement 검사로 유효하다. 이 containment만으로 실제 continuum spectrum의 quadrature/physics error가 증명되었다고 하지 않는다.

## 코드·raw를 받으면 같은 pass에서 남아 있는 확인

1. 입력 float ratio/M decimal parse, immutable source의 실제 copy/read identity, saved moments 재사용 경로와 old imports/replays0.
2. exact E/floor/ceil, P nesting·폭, signed scalar multiplication, final nearest rounding와 overflow·subnormal·zero provenance 구현.
3. 실제 합에 대한 bound/concavity의 검사가 안전한 endpoint를 쓰는지, nominal/endpoint/reference acceptance가 frozen criterion을 지키는지.
4. diff 범위, one child command·exit·resource raw, cap debit 및 source-vs-stock/heat output metadata.

현재 이 네 항목은 구현 자료가 아직 없어서 남은 C9 범위이며 새 finding이나 추가 실행 요구가 아니다. 이전22/66/83/ANG/NCP/HI-summary/stock/work/native-HI/donor quadrature를 재생하지 않았다. 원 L0 gate2e−12, 과거 cap 초과·UNKNOWN_NOT_ZERO·NOT_FROZEN, ANGTHERM02 read-only와 전체 모델 완료율null은 그대로다.

## C9 초기 구현 읽기와 R6C9-01

이후 제공된 `stress_source.py`, `focused_check.py`, `run_focused_once.py`, `PRE_EXECUTION_MANIFEST.json`, input JSON과 README를 전체 읽었다. `PATCH.diff`는 새 파일6개의 상대경로 추가만 포함하며 읽은 구현/이론/정책 문서가 그 내용이다. 실제 연구 코드/test 실행은 하지 않았다. floor-log2의 integer 비교, signed floor/ceil, interval endpoint 연산, saved K/L 재사용과 old consumer import 부재, Decimal 대체식, bound/concavity의 보수적인 endpoint 방향, 단일 child와 자원 receipt 경로에는 다른 현재-task finding이 없다.

**R6C9-01 — signed zero를 구별하지 않는 binary64 certificate.** 초기 `stress_source.py`의 `Interval.certified()`는 두 endpoint의 float를 `left != right`만으로 비교했다. 정확한 interval `[-2^-1100,+2^-1100]`의 endpoint는 각각 IEEE `-0.0`, `+0.0`으로 반올림되지만 Python 수치 비교는 같다고 한다. 그 결과 함수는 `value=-0.0`, `tag=zero_in_enclosure`, `status=CERTIFIED_BINARY64`를 반환한다. exact_zero=false는 맞으나 실제 합의 sign bit는 이 interval에서 결정되지 않았다.

이 finding은 **representation/certificate issue, FIX_BEFORE_GO**다. 실제 양의 HI W/S 값이나 유도의 반증은 아니다. 최소 수정은 두 endpoint의 반올림 결과가 sign bit까지 같을 때만 단일 binary64를 확정하고, 위 tiny-crossing 한 control을 기존 focused pass에 넣는 것이다.0을 제외하는 양/음의 interval이 같은 부호의0으로 반올림되는 정상 underflow 분류는 보존한다. 새 reviewer, 광역 test gate, 별도 실행을 요구하지 않는다. 수리한 변경 부분을 이 동일 pass에서 읽어 finding을 닫고, 실제 raw를 받으면 최종 판정한다.
