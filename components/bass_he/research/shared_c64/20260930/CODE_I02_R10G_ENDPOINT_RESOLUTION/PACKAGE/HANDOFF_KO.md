# BASS_HE R10G handoff: 준비된 첫 구간 전용 코드의 검토·실행

## 먼저 읽을 사항

이 패키지는 원격 repo에 이미 존재한다고 가정하지 않는다. DELIVERY_STATUS.json에 원격 게시 상태가 NOT_RUN이면 첨부 ZIP을 입력으로 사용한다. 예전 R10F의 깨진 UTF-8 handoff나 decimal cutoff를 재구성하지 않는다. 이 package의 CONTRACT.json과 MANIFEST.json을 기준으로 삼는다.

repo: cosmosapjw-quantum/BASS_HE
PR15 expected source HEAD: b8b2fe47a367459f6faf6796eb2f251feacbbd7c
PR17 R10F basis: 5efe052460e85f7e9785b9391d188ba394efee73
PR17 branch: research/shared-c64-crossrepo-20260928
새 연구 namespace 권장: research/shared_c64/20260930/CODE_I02_R10G_ENDPOINT_RESOLUTION/

현재 refs와 root AGENTS.md를 읽는다. 문서가 추가된 것만으로 scientific source를 바꾸지 않는다. 실제 dependency source가 달라지면 중지하고 reconcile한다. 기존 사용자 worktree에 reset/clean/stash/delete하지 않는다.

## 1. 입력과 상태

R10F full archive:
BASS_HE_R10F_BOUNDARY_SPLIT_GK_UNRESOLVED_20260930T1026KST_v1.zip
3105199 bytes
SHA256 082fd7ec94e2873ee218043828179e3c4db8d9f0d4ce28f9fa29f8c807207578
Drive object 1Ri935GB7dVbryKyU4DLzIVk-NaFpA9xw
Dropbox object id:BSpOijBcT10AAAAAADwK8w

원 R10F의 1035-row table 및 945개 신규 Delta 기록은 재실행하지 않는다. 첫 interval 밖 16개의 high/error vectors를 원문 그대로 재사용한다. 첫 interval의 q query에 실제로 필요한 새 Delta만 허용한다.

CODE_I02_CLOSED=true; full_certificate_fail_closed=true;
scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN.
R10F_BOUNDARY_SPLIT_GK_UNRESOLVED는 historical verdict로 그대로 남긴다.

## 2. 준비된 코드와 검증 범위

ChatGPT에서 다음을 이미 구현하고 실행했다:
- eta_rotation.py: 동일 Coulomb trajectory/Eq47의 eccentric-anomaly Magnus4, full-matrix DOP853 auditor.
- endpoint_quadrature.py: 첫 interval만 q=asinh(rho/a_ref)에서 shared vector GK15/G7로 처리.
- audit_archived.py: 변경 없는 원 adapter의 frozen first-panel 재현과 새 표현의 overlap 검증.
- execute_endpoint.py: source/environment/cache identity 검증, bounded 신규 exact geometry, phase별 durable checkpoint.
- tests/test_core.py: 16개 focused tests. core는 RED12 -> GREEN12 후 확장.

이 코드를 처음부터 다시 설계하지 않는다. 잘못된 source mapping, 수학적 가정, tolerances 또는 구조 변경이 필요하면 실제 실패를 보존하고 연구 스레드로 반환한다. 이 문서는 previous R10F의 no-refinement를 소급 변경하지 않고 새 R10G local refinement 계약을 명시한다.

## 3. 실행 순서

(1) ZIP SHA256과 MANIFEST의 모든 payload를 검증한다. 전체 파일은 strict UTF-8로 읽고 JSON을 parse한다. 자체 생성 오류 메시지를 handoff 내용으로 취급하지 않는다.

(2) 새 격리 context에서 영향 범위만 확인:

    PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OPENBLAS_NUM_THREADS=1 \
      python -m pytest -q -p no:cacheprovider tests/test_core.py
    OPENBLAS_NUM_THREADS=1 python audit_archived.py --out /tmp/R10G_REVIEW_EVIDENCE

이 검토는 새 integrator representation에 대한 독립 실행 확인이지, CODE-I02와 whole repository suite를 다시 실행하는 것이 아니다. audit은 새 Delta를 계산하지 않는다. 최대 overlap difference1e-8, archived first-panel high/error difference1e-12를 넘으면 실행에 들어가지 않는다. Outcome-blind 검토라고 부르지 않는다.

(3) source checkout과 R10F archive를 지정해 inventory:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
      python execute_endpoint.py --repo /ABS/PINNED_BASS_HE \
        --r10f-archive /ABS/R10F_ARCHIVE.zip --out /ABS/R10G_RUN

(4) 검토/inventory가 통과하고 이 handoff의 새 실행 범위를 수행할 때만 --execute를 붙인다:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
      python execute_endpoint.py --repo /ABS/PINNED_BASS_HE \
        --r10f-archive /ABS/R10F_ARCHIVE.zip --out /ABS/R10G_RUN --execute

원 endpoint/cache reuse authority는 Python3.12.3/NumPy2.3.5 및 source digest
496a1d9be062e074e72f4d2d8033dd865c4671b65f95daaeaeafa2fcde4eb4ba
를 요구한다. 이 gate를 지우거나 다른 host를 같은 identity로 기록하지 않는다. 환경이 달라서 멈추면 호환 host 또는 별도 승인된 재생성 계약이 필요하다.

## 4. 사전에 고정된 새 범위

- B hex=0x1.05bbc59d8ffb1p-1.
- a_ref hex=0x1.bb83cf2cf95d4p-8, E=5keV/u의 물리 Coulomb scale.
- 첫 interval만 q로 변경, 다른 16개 interval의 원 high/error는 불변.
- 초기 equal q panels2, 최대 leaf8, 최대 rho evaluations210, 새 exact Delta call1050 이하.
- 각 refinement는 현재 가장 큰 normalized component error의 local panel만 이분한다.
- 90성분 모두 기존 atol1e-10+rtol2e-4*abs(total)를 만족해야 한다.
- 연속 두 complete-grid embedded PASS와 high 변화 <=0.25*tolerance가 모두 필요하다.
- budget exhaustion이면 ENDPOINT_BUDGET_UNRESOLVED. 같은 실행에서 상한을 늘리지 않는다.

새 q query는 원 R10E보다 작은 rho를 포함한다. 그러므로 이전 1024step PASS를 자동 상속하지 않는다. 준비된 eta128/256 검증을 각 batch에 적용하며 probability1e-7, unitarity/stochasticity5e-13을 유지한다. worst-point DOP853(rtol1e-12,atol1e-14) agreement1e-8도 검사한다. Fail이면 새 Delta 계산 전에 중지한다. 기존 x-Magnus를 몰래 eta로 덮어쓰지 않는다.

Delta는 반드시 기존 bass_he.geometry.contour_geometry, depth96/panels32를 사용한다. 새로운 surrogate fitting, 64-panel 대체, sturm_geometry로의 경로 변경은 없다. Cache key에는 exact rho hex, source/environment/endpoint/contract identity가 들어간다. 원 캐시는 수정하지 않는다.

## 5. 반환과 claim gate

반환할 것은:
- 새 refs와 package/source/input hash 및 environment.
- focused test/archived-overlap 결과.
- 실제 leaf/refinement/query 수와 new/reused Delta 수.
- 새 query별 rotation gate와 첫 실패.
- global90component embedded 판정 및 successive-grid 확인.
- 재사용한 outside high/error의 원 SHA256.
- 완료한 수치 비교와 미실행 항목.

PASS 이름은 R10G_LOCAL_ENDPOINT_NUMERICAL_PASS_NOT_GLOBAL_OR_PHYSICAL_CERTIFICATE다. 이 PASS도 전체 연속 적분의 엄밀한 bound가 아니며 physics나 production promotion은 아니다. 정책 판정과 Appendix-A residual의 원인 해석을 자동으로 하지 않는다. 과거 3.333/1.880 수치를 새 결과로 재사용하지 않는다.

## 6. 게시·백업

현재 ChatGPT 원격 write가 수행되지 않았다면 먼저 새 namespace에 package의 연구 source/documents를 append-only로 게시한다. Source PDFs, author FORTRAN, 기존 실패 records는 변경하지 않는다. 새 commit과 Git tree/blob을 확인하고 비강제로 push한다. 기존 source dependency 파일은 stage하지 않는다.

새 실행 증거는 timestamped child namespace에 별도로 게시하고, create-only Drive folder 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI 및 Dropbox /BASS_DERIVATION_DOSSIERS_20260912/에 이중백업한다. Provider ACK/object ID/size/checksum과 실제 restore 여부를 구분한다. 가능한 한 selective readback으로 검증을 닫는다.

금지: production source/default/tolerance 변경, CODE-I02 재감사, old945 Delta 반복, full suite/56-action replay/worker sweep, author FORTRAN 실행, L2/Krawczyk, 새 physical channels, force-push/merge, budget 무단 확대.
