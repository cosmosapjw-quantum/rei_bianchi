# BASS_HE R10G: head-on 좌표 검토와 첫 구간 교체 계약

## 목적과 현재 상태

R10F 실패를 보존한다. 이 작업은 다른 16구간과 production source를 그대로 두고, 첫 구간의 두 수치 좌표만 바꾸는 연구용 후보의 검토 및 조건부 실행이다. 새 물리 궤적, 새 허용오차, 저자 코드 번역이 아니다.

PR15: b8b2fe47a367459f6faf6796eb2f251feacbbd7c
PR17 입력 basis: 5efe052460e85f7e9785b9391d188ba394efee73
branch: research/shared-c64-crossrepo-20260928
원문 namespace: research/shared_c64/20260930/CODE_I02_R10F_EXECUTION/20260930T1026KST/

root AGENTS.md, R10F REPORT/EXECUTION_VERDICT, 이 패킷의 REPORT_KO.md와 DECISION.json을 읽는다. 새 ref가 있으면 영향 파일만 대조한다. force/reset/merge, 기존 worktree 정리 금지.

완전한 실행 패킷의 이름/크기/SHA256/Drive/Dropbox ID는 같은 R10G namespace의 BACKUP_RECEIPT.json에 있다. GitHub subset을 전체 패킷으로 오인하지 않는다. ZIP의 MANIFEST.json을 실제 bytes로 검증한다. UTF-8 decoding 실패나 오류 문자열을 정상 prompt로 취급하지 않는다.

## 1. 입력 identity

R10F archive SHA256:
082fd7ec94e2873ee218043828179e3c4db8d9f0d4ce28f9fa29f8c807207578
Drive: 1Ri935GB7dVbryKyU4DLzIVk-NaFpA9xw
archive bytes: 3105199; manifest payloads: 2014.

R10F exact table SHA256:
a5c2422820b56b0ae6b5cc3857b0d24508452bb274ad40e1818373facb1e8031
기존 geometry source SHA256:
496a1d9be062e074e72f4d2d8033dd865c4671b65f95daaeaeafa2fcde4eb4ba
기존 Coulomb x-adapter blob:
543ff5e5c20ff2969547f03410cd30353998348c

geometry 실행은 R10F의 depth=96, panels=32 및 endpoint/source/environment 권위를 그대로 요구한다. research adapter의 새 SHA256와 geometry source identity는 별개로 기록한다. 상위 commit이 달라졌다는 이유만으로 모든 cache를 무효화하지 않는다.

## 2. 먼저 준비된 좌표 변경을 검토한다

eta_rotation.py는 같은 Eq.(47)을 hyperbolic anomaly로 표현한다:
R=a+b cosh(eta), b=hypot(a,rho), dt/deta=R/v, dtheta/deta=-rho/R.
원래 rotating-frame A의 생성자는 (epsilon R^3/v)Lx^2-(rho/R)Lz다.
L은 dimensionless angular-momentum matrix이고 실행 수치는 legacy atomic units다.

핵심 검토 항목: 부호, 양 끝 초기조건, 기존 molecular-x 및 |m| collapse와의 일치, rho->0 및 a->0 극한. epsilon_override/a_override는 test control이고 과학 실행에서 사용 금지다.

    PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 \
      python -m pytest -q -p no:cacheprovider tests
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
      python preflight.py --out NEW_REVIEW_PREFLIGHT

이 코드를 다시 설계/번역하지 않는다. 현재 sandbox에서 22 tests PASS와 새 노드 60개/12조합 preflight PASS를 관측했지만, 별도 검토자는 새 변경 범위에 대한 자기 판정을 반환한다. 같은 구현자의 판단은 독립 물리 증명이 아니다.

preflight는 eta steps 128/256/512, |P256-P512|<=1e-7, unitary/stochastic defects<=5e-13, 별도 x-gauge DOP853와 확률 차이<=1e-8이다. 허용오차는 기존과 같다. DOP853 rtol=1e-12, atol=1e-14. 실패하면 더 높은 steps로 넘어가지 말고 R10G_PREFLIGHT_UNRESOLVED로 중단한다. 통과하면 새 첫 구간에만 eta512를 사용한다. 나머지 구간의 기존 x1024 결과를 재계산하지 않는다.

## 3. 첫 구간 log 좌표 계약

첫 구간 끝 rho hex: 0x1.05bbc59d8ffb1p-1
scale s=a(5 keV/u)^2 hex: 0x1.8030b971ab5cep-15
u=rho^2; tau=log1p(u/s); u=s*expm1(tau); du/dtau=s*exp(tau).

QUERY_PLAN.json의 hex 노드/가중치가 실행 SSOT다. runtime은 저장 hex를 float.fromhex로 읽는다. generate_rule은 작성용 sanity helper이며 libm 재계산의 마지막 비트 차이로 normative node를 덮어쓰지 않는다. pi와 Jacobian은 이미 wk/wg에 포함돼 있다. 중복 pi/rho/Jacobian을 곱하지 않는다.

첫 구간만 log 좌표의 네 고정 GK15/GK7 panel로 교체한다:
- 새 rho 60개, 다섯 branch가 모두 active: 최대 새 Delta 300개.
- 기존 첫 구간 15개/75 pair는 새 적분에서 제외하되 원본은 보존한다.
- 나머지 240 rho/960 pair, 16 interval의 high/error는 R10F archive에서 재사용한다.
- 새 전체 표현: 300 rho, 1260 active pair, 20 panel.
- adaptive refinement=0. 결과를 본 뒤 s, panel 수, node, tolerance 변경 금지.

## 4. 조건부 geometry 실행

독립 좌표 검토와 preflight가 통과하고 이 새 실행 계약이 승인된 경우에만 새 Delta를 계산한다. 그 전에는 Delta=0회다. 계산 wrapper는 R10F r10f_runner.py의 검증된 endpoint_authority/contour_key/contour_geometry 경로를 그대로 사용한다. 바뀌는 것은 제공된 QUERY_PLAN의 300행 및 새 namespace/output 경로뿐이다. 일반화된 새로운 solver를 구현하지 않는다.

source/endpoint/environment가 맞는 같은 branch+rho_hex+depth+panels만 cache 재사용한다. 가까운 rho를 반올림해 같은 것으로 취급하지 않는다. 각 행을 atomic write+fsync로 보존한다. 최대 300개를 넘거나 새 endpoint 생성이 필요하면 멈춘다. 비유한/음수 Delta 또는 contour/certificate failure는 중단 사유다. panels64, 추가 refinement, 다른 source로의 fallback은 승인하지 않는다.

geometry host는 R10F의 Python3.12.3/NumPy2.3.5/SciPy1.17.0 및 pinned source 계약을 확인한다. 이번 ChatGPT의 Python3.13.5 회전 연구 결과는 geometry 환경 호환성의 증거가 아니다.

## 5. 적분 조립

첫 구간에서 기존 다섯 lane과 두 에너지, factor-two 및 sink/branch-order를 유지한다. straight는 기존64, Coulomb은 새 eta512. Δ0는 기존 FROZEN_DELTA0_RECORD를 재사용한다. 단면적/효과/Appendix 값을 이 단계에서 production으로 승격하지 않는다.

새 integrand shape=(60,90)에 대해 panel_plan.reduce_first(values)를 사용한다. panel_plan.join_outer(first,R10F_FIXED_GK_DIAGNOSTIC)는 기존 첫 interval을 제거하고 나머지16 high/error에 새4 high/error를 더한다. 원래 전체 error에서 첫구간 error를 부정확하게 빼거나 상쇄된 signed error를 쓰지 않는다.

모든90성분에서 error<=1e-10+2e-4*abs(total)이어야 R10G_RESEARCH_GK_PASS다. 이는 embedded numerical estimator이며 continuum interval bound가 아니다. 하나라도 실패하면 R10G_FIRST_PANEL_UNRESOLVED, raw integrand/error 보존, 추가 노드/step/정책 변경 없이 반환한다.

PASS 뒤에도 R10F BASELINE_REGRESSION_RULE_PRECOMMITTED.json의 동일 기준으로 SL_CPC를 점검한다. 그 후에만 기존 R10D 물질성 기준에 따른 효과 분해/Appendix 비교를 한다. 표지는 AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION이다.

## 6. 반환과 금지

실제 source/plan/code hashes, 독립 검토 판정, preflight 명령/카운트, 새/reused Delta 수, 각 interval high/error, 전체90 gate, baseline, 미실행 항목을 반환한다. geometry collector의 입출력 연결 외 과학 설계 변경이 필요하면 이 연구 스레드로 반환한다.

production source/default/tolerance, 저자 FORTRAN 실행, CODE-I02 재감사, 56-action replay, worker sweep, 다른16 interval 재실행, L2/Krawczyk는 금지다. 새 수치설계는 outcome-informed이며 blind/pre-registered라고 부르지 않는다.

CODE_I02_CLOSED=true; full_certificate_fail_closed=true;
scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN.

새 증거는 PR17 새 namespace에 non-force/append-only 게시한다. 기존 Drive folder 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI 및 Dropbox /BASS_DERIVATION_DOSSIERS_20260912/에 create-only 백업하며 ACK/metadata/restore를 구별한다.
