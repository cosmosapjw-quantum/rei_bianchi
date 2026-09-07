# REI 실제 population-stage / 오차 경계 연결 결과

STATUS: `STATIC_POPULATION_STAGE_MAPPING_ESTABLISHED` /
`PRODUCTION_FOUR_SITE_REPLAY_UNAVAILABLE`

RETURN_TO=MAIN_CONVERSATION; WORK_THREAD_REQUIRED=false. 한 Host Codex writer가
기존 PR #73의 새 research child에서 수행했다. 기존 작업선을 PR #72 문서
branch로 되감지 않았다.

## 실제 결과

- 보존된 Python MPRK22(1)의 예측·gamma-population·보정 solve에 대해 실제
  `A(F,d)`와 RHS를 유도했다. 분모는 각각 `y0,y0,yp`이고 RHS는 모두 `y0`다.
  보정 matrix의 flux는 `(F0+F1)/2`; 보정자를 backward Euler 한 단계로
  대체하거나 RHS를 `yp`로 바꾸면 다른 결과가 나온다.
- 각 frozen population solve는 유효한 양수 입력에서 off-diagonal 비음수,
  H/He별 conserved left vector, 고정 양수 가중치, RHS 양수 조건을 구조적으로
  충족한다. 실제 event graph와 단위·species ordering·state/T/radiation 의존성을
  source에 연결했다. 원자핵의 open source는 없고 광자·열 계는 열린 계다.
- 실제 네 site의 호출 순서와 독립 source를 유지하여 분모 미분을 포함한
  population sensitivity 및 thermal predictor/SDIRK2 block sensitivity를
  유도했다. frozen solve의 비증폭이 nonlinear full-map 비증폭을 뜻하지 않는다.
- `CELL_LOWER_STRICT`의 온도 table jump는 `r_he3cas*A_H`를 통해 population
  matrix에 들어갈 수 있다. 해당 경계를 가로지르는 하나의 smooth Lipschitz
  bound는 적용할 수 없다. event 구분과 실제 tube bound가 필요하다.
- thermal 식의 가열·냉각·`-2HU` 팽창 항은 닫힌 conservative generator가
  아니다. SDIRK2의 고립된 팽창항에서 `2Hh=4`이면
  `Uf/U0=(5-4sqrt(2))/(5-2sqrt(2))^2<0`이다. 이는 무조건 양수라는 추론의
  반례이며 실제 REI trajectory 실행·불안정 판정이 아니다.
- 현재 `SourceBoundMprkSdirkOperator`의 constructor/from_repo는 소스상
  `RUST_THERMAL_REPLAY_ABI_MISSING`을 무조건 발생시킨다. 실제 ctypes/Rust
  ABI v4는 입력받은 2x2/3x3 implicit/tangent/mixed block을 인증하며,
  네 source site를 직접 재계산하는 production 구현은 아니다.

전체 식과 한계는 [STAGE_MAPPING.md](STAGE_MAPPING.md), 정확한 source path/commit/
blob는 [SOURCE_INDEX.md](SOURCE_INDEX.md)와 [SOURCE_BINDINGS.json](SOURCE_BINDINGS.json),
작은 기계 판독 결과는 [RETURN_STATUS.json](RETURN_STATUS.json)에 있다.

## 실제 검증 및 source identity

TESTED_SOURCE: `9605f8f89e35c2a25d60e8dc0098c6d859d38e66`

TESTED_TREE: `2663929364f577cb6f1dd4e09520bb3f56d5a336`

INSPECTED_IMPLEMENTATION: `81d54e1210b8654d3c8f545b3621b109d1011fdc` /
`3c4227088543c3ac346ce2769fa16df0fd433458`.
연결한 implementation blob들은 고정 바탕 `54a879231c68734fdda6990d67d8458d2918943e`와
동일하다. 전달 프롬프트가 처음 게시된 commit은 `019608c2a400423485795696ecb47523361d4c13`다.

해당 tested commit에서 실행한 독립 algebra fixture는 **10/10 PASS**, 실패·오류·skip 0.
기존 research Fraction helper만 재사용했고 production importer/guard/worker를
호출하지 않았다. 26개 source byte binding, 실제 event edge/세 solve,
잘못된 보정자 대체, 분모 tangent, variation bound, branch jump, thermal
팽창 반례, cross-stage derivative, estimator/defect 구분, 보존 가중치를 점검했다.
이는 실제 atomic rate 수치나 임의 차원 정리를 전수 검증했다는 뜻이 아니다.

`python3 -B scripts/verify_repo.py`는 60 main artifacts PASS;
`git diff --check`도 exit 0. 원본 결과는 [ALGEBRA_RESULT.json](ALGEBRA_RESULT.json),
[algebra log](logs/exact-stage-algebra.log), [repository log](logs/repository-verifier.log)에 있다.
첫 uncommitted fixture 실행도 10/10 PASS였으며 원본을 보존했다. 이후 source binding을
완성한 tested commit에서 실행한 것을 최종 검증으로 사용한다. 동일 10개 의무를
20개 독립 검증으로 세지 않는다.

기존 PR #73 job `101511110133`의 실제 CI log도 새로 읽었다: 10/10 PASS,
`104/85`, `production_mapping_verified=false`. [원본 발췌](logs/pr73-exact-ci-excerpt.log).
기존 checker·XZ consumer·GCC chain·native calibration은 재실행하지 않았다.

## UNKNOWN 및 적용 범위

실제 공통 enclosure에서의 rate derivative/Lipschitz 상수, Patankar denominator
최소값을 포함한 수치 gain, full thermal coupled Jacobian inverse bound,
outer residual-to-root-error bound, exact-flow defect `rho`는 **UNKNOWN**이다.

기존 `validated_local_error_bounds`는 full-step과 two-half-step의 discrete
output 차이 구간이다. 기존 implicit certificate의 `rho_upper`는 Krawczyk
contraction이고 `residual_*`는 implicit RHS이다. 어느 것도 별도 remainder
연결 없이 exact ODE flow에 대한 additive defect로 승격할 수 없다.
H/He nuclei 보존을 total energy 또는 photon closure 증명으로 사용하지 않았다.

검토는 같은 Host Codex의 순차 physics/math 및 code 검토 1회이며 독립 reviewer
승인이 아니다. 새로운 production defect를 확정하거나 protected code를 수정하지
않았다. first interval/provider/scientific admission 및 runtime authority 효과는 없다.

## 게시와 다음 한 단계

이 handoff와 결과/log만 추가하는 publication commit은 tested source와 구분한다.
commit 자신의 SHA를 파일에 재삽입하는 순환을 만들지 않고, 실제 non-force push 후
관찰한 publication SHA와 HANDOFF 고정 링크를 직접 반환한다. Draft PR의 base는
PR #73 research branch이며 ready/merge하지 않는다. CI가 자동 실행되면 repository
publication 검사이며 새 production 또는 scientific PASS가 아니다.

NEXT: main conversation에서 이 mapping을 바탕으로 한정된 event-free domain의
실제 source derivative bound와 exact-flow remainder 연결 중 다음 scientific
의무 하나를 결정한다. 이 반환 자체를 native 실행/first interval 지시로 해석하지 않는다.

BASS/REC/HTT 접근·변경, Snapshot GET, 설치/downgrade, rootfs/provider census,
production lock/물리식/허용오차/SSOT 변경, Section-0/ref/lease/worker,
first interval, ready/merge/force-push는 수행하지 않았다. 과거 one-shot 예산은 그대로다.
