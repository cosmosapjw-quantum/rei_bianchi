# BASS_HE R10B: 준비된 Q23 node-identity 수리 검토와 R10C 계약 인계

## 0. 목적과 변경 경계

R10A를 처음부터 재실행하지 않는다. Q23의 실패는 기존 parent GK7 midpoint와 추가 split midpoint가 같은 기하학적 점인데 1 ULP 다른 rho로 두 번 fitting에 들어간 문제로 재현됐다. R10B package는 원본을 바꾸지 않는 새 anchor view와 이미 실행한 12개 focused tests를 제공한다. 이 코드를 처음부터 다시 구현하거나 interpolation 방법을 바꾸지 않는다.

R10A의 SURROGATE_REBUILD_UNRESOLVED와 기존 세 lane 결과의 격리는 보존한다. 이 prompt의 기본 실행 범위는 준비된 자료의 identity 확인 및 제한된 수리 검토다. 아래 R10C 신규 Delta 계산은 PROPOSED_QUERY_CONTRACT.json에 대한 별도 승인이 있는 경우에만 진행한다. 단순히 R10B unit test가 통과했다고 그 승인을 추론하지 않는다.

## 1. Fresh identity

repo: cosmosapjw-quantum/BASS_HE
PR15 expected HEAD: b8b2fe47a367459f6faf6796eb2f251feacbbd7c
PR17 R10A evidence basis: 5954d5d31d1c4536b41e13b4868aa5fa97cd2924
PR17 branch: research/shared-c64-crossrepo-20260928
R10A namespace: research/shared_c64/20260929/CODE_I02_R10A_RHO_FREEZE_IMPACT/20260929T1535KST/
R10B namespace: research/shared_c64/20260929/CODE_I02_R10B_NODE_IDENTITY/

root AGENTS.md, R10A ADMISSION_VERDICT.json, NEXT_DECISION_PROMPT_KO.md, R10B DECISION.json을 읽는다. 실제 ref/source 변경이 있으면 겹치는 변경만 대조하고 force/reset/merge하지 않는다. PR description의 오래된 테스트 수를 현재 증거로 사용하지 않는다.

R10A 원시 archive:
BASS_HE_R10A_RHO_FREEZE_IMPACT_20260929T1535KST_v1.zip
640484 bytes
SHA256 2096b9f8347fd02f89bc689330fc76686a0c5c2553bf9232d7912f8a6f82ac75
Drive object 1A3sV-w-jhRt6VEHAY0b8UTYNiqWdPpOA

R10B의 완전한 실행 package 위치/크기/SHA256은 같은 namespace의 BACKUP_RECEIPT.json을 따른다. repo에 게시된 문서 subset과 package 전체를 혼동하지 않는다. archive 내부 MANIFEST.json의 각 파일을 실제 bytes로 확인한다. 오류 문구나 누락된 파일을 정상 내용으로 취급하지 않는다.

## 2. 제공 코드와 이미 확인한 결과

package root:
- node_view.py: 정확히 pin된 R10A manifest에만 적용한다.
- replay_support.py: blob-verified source에서 필요한 정의만 추출한다. BASS_HE package import 없음.
- replay_analysis.py: archived interpolation/conditioning만 수행한다.
- tests/test_node_view.py: 12개 focused tests.
- fixtures/: 원본 R10A 선택 파일, 수정하지 않는다.
- source_snapshot/: eq54.py와 geometry.py의 소스 identity 확인용.
- evidence/: RED 3 fail, GREEN 12 pass 및 실제 forensic 결과.

실행 예:

    PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 \
      python -m pytest -q -p no:cacheprovider tests/test_node_view.py
    OPENBLAS_NUM_THREADS=1 python replay_analysis.py

이것은 새 reviewer environment에서의 영향 범위 검토다. CODE-I02 또는 repository full suite를 반복하지 않는다. NumPy 버전이 다르면 기록하고, 수치 결과의 마지막 비트가 다르다는 이유만으로 historical 파일을 덮어쓰지 않는다.

검토할 핵심:
- 보존할 parent rho: 0x1.a0e8bdf74847dp+2
- fitting view에서만 제외할 추가 split rho: 0x1.a0e8bdf74847cp+2
- 수학적 identity: u/Rb^2=1/2
- source geometry GK7 중앙점과 R10A runner의 Rb/sqrt(2)에서 각각 생성됐음을 확인한다.
- 제외 record는 receipt에 남기며 다른 branch/ordinate/tolerance/차수는 변경하지 않는다.
- 가까운 좌표를 isclose로 일반 병합하거나 raw cache key를 반올림하지 않는다.

R10B 실제 관측값:
- witness rank 3 -> 4
- condition number 5.917069719313704e15 -> 139.679889423492
- 기존 64-panel reference 상대오차 1.4166045154428908e-3 -> 3.746852183319305e-8
- 기존 fixed holdout 30개 PASS
- 저장 nontraining reference 50개 위반 0, 모두 posthoc reuse
- 실제 105 GK15 좌표/360 active pair의 rank 결함 1 -> 0
- 새 Delta 계산 0, transport 적분 0

원래 단일 midpoint refinement는 더 수행하지 않았다. 이번 입력-node 수리는 별도의 R10B proposal이고 R10A 결과를 소급 승인하지 않는다. 이전 exact float dedup 지시만으로는 기하학적 중복을 막지 못했다는 원인도 보존한다.

## 3. 판정과 남은 범위

NODE_IDENTITY_REPAIR_REVIEW를 PASS/FAIL로 반환한다. 이는 Q23 중복 입력의 수리에 관한 판정이며 I2 수치 closure나 physical promotion이 아니다.

S23의 저장된 최악 상대오차 1.9715317060022399e-4는 2e-4에 가깝다. Q23 witness만 통과했다고 모든 소비 query가 정확하다고 선언하지 않는다. rank/condition-number 검사는 reference-accuracy 검사가 아니다.

기존 3.333/1.880 비율 및 Appendix A 비교는 아직 탐색값이다. 통과한 새 식별 수리를 이유로 그 숫자에 PASS 꼬리표를 붙이지 않는다.

## 4. R10C 제안: 고정된 소비 지점 reference 검사

PROPOSED_QUERY_CONTRACT.json은 기존 adaptive GK15가 실제 사용했던 105 rho 좌표/360 active branch-query pair를 고정한다. 이 새 계약은 별도 승인 전에는 실행하지 않는다. 새로운 refinement, 전체 grid 재생성, 새 fitting data 추가 없이 소비 지점에서 오차를 검사하는 것이 목적이다.

승인 시 적용할 범위:
1. 정확히 동일한 source/input/environment provenance를 가진 저장 reference만 재사용한다. 비슷한 rho나 다른 panel 결과를 같은 cache entry로 취급하지 않는다.
2. 기존 R10A의 geometry 계산 경로, depth=96, panels=32를 유지한다. sturm_geometry와 geometry를 임의로 교체하거나 다른 source HEAD의 solver를 혼용하지 않는다.
3. 없는 reference만 고정 queue 순서대로 계산한다. 최대 새 32-panel contour call은 360개이며 reuse만큼 차감한다. transport/rotation/Eq50/54/단면적 적분은 이 단계에서 실행하지 않는다.
4. 각 결과를 즉시 durable 저장한다. 오차는 abs(Delta_view-Delta_reference)/abs(Delta_reference) <= 2e-4. nonfinite/negative/zero denominator 또는 source mismatch는 별도 실패다.
5. 첫 정확도 위반에서 중단한다. 원인이 contour resolution인지 구분하는 64-panel 진단을 그 점에서 최대 1회만 허용한다. 이것을 이유로 기준값 또는 threshold를 바꾸지 않는다.
6. 360 pair 전부 PASS일 때만 CONSUMED_GK15_REFERENCE_PASS라는 좁은 판정을 내린다. 여전히 global interpolation bound가 아니며 원래 integral numbers를 소급 승인하지 않는다.
7. 최초 endpoint가 없거나 host 변경으로 reuse authority가 없으면 필요한 신규 endpoint 계산을 자동 확대하지 않는다. identity blocker와 필요한 최소 실행을 반환한다.

이 제안은 비용의 상한이지 현재 측정한 실행시간 예측이 아니다. 새 resource/paid cloud/pool을 생성하지 않는다. 기존 승인 host에서만 실행한다.

## 5. 금지와 반환

금지: production source/default/physical tolerance 변경, 다른 interpolation, rcond 완화, 두 번째 refinement, holdout을 fit에 편입, author FORTRAN 실행, CODE-I02 재감사, 56-action replay, worker sweep, R1/R2, L2/Krawczyk, 과학적 승격.

반환: fresh refs, package/inputs hash, repair review 판정, actual command/count/exit, R10C가 승인되었는지와 실행 여부, 재사용/새 reference 수, 첫 실패 또는 고정 queue 완료 상태, 독립성 한계, gate ledger.

CODE_I02_CLOSED=true; full_certificate_fail_closed=true;
scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN.

새 증거는 PR17의 새 namespace에 append-only/nonforce 게시하고 기존 Drive folder 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI와 Dropbox /BASS_DERIVATION_DOSSIERS_20260912/에 create-only 백업한다. provider ACK와 restore를 구별한다. 기존 raw failure를 삭제하거나 덮어쓰지 않는다.
