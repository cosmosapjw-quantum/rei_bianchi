# 다음 단일 node: C1b independent reference convergence

ROLE=BASS_HE_C1B_INDEPENDENT_REFERENCE_CONVERGENCE

기존 repository `cosmosapjw-quantum/BASS_HE`, branch `research/shared-c64-crossrepo-20260928`의 같은 append-only 연구 흐름에서 이어간다. 이번 C1 commit/tree는 외부 delivery receipt가 소유한다. 부모 A2 commit은 `6d16ac5d77d0113d1939eb6e04c52690184cc1d5`, scientific source pin은 `1a83a67e12de1ddc2aede0ff67168f7071450ab3`다. 먼저 fresh HEAD/tree와 관련 dependency 변경만 판별한다.

한 질문: **R=2 a_A의 exact g / bright b에서 독립 reference의 energy와 L_y 수렴을 사전 기준까지 확보할 수 있는가?**

필수 입력: RESULT, NUMERICAL_CONTRACT, CONVENTIONS, CODE_IDENTITY, C1_ELECTRONIC_DERIVATION_KO, evidence/C1_SINGLE_POINT_PILOT, review/C1_INDEPENDENT_REVIEW, code/partialwave.py, code/spheroidal.py, code/coupling.py. A2 이론은 private nested parent ZIP의 불변 dependency다. 기존 B1 matrix와 source numeric cells는 재추출하지 않는다.

현재 증거: prolate base/refined Lbar≈0.3409777577575, direct/torque·momentum consistency는 좋다. Spherical ℓ8/12/18은 순차적으로 접근하지만 ℓ18 E_g 차이=0.0012838976132703, Lbar 차이=0.0000819720487472로 각각 1e−5 기준을 넘는다. Spherical ℓ12→18은 같은 radial mesh/domain이므로 angular truncation의 미해결을 보인다. 아직 radial h/p, box, quadrature, roundoff의 독립 error budget은 없다. Prolate 두 설정도 mesh/extent를 함께 바꿨으므로 tail-only convergence evidence가 아니다. Full-space residual와 same-sector gap은 미계산이다.

1. 이 한 지점에서 먼저 원인과 실행 비용을 예상하고 **새 bounded 실행 계약을 실행 전에 작성**한다. 허용할 ℓ sequence, radial h/p, q, rmax, wall/memory cap, return schema와 실패 조건을 명시한다. 기존 기준을 사후 완화하지 않는다. 이전 C1 whole pilot/atomic suite를 새 라벨로 반복하지 말고 바뀐 dependency에 필요한 검사만 한다.
2. ℓ 증가만으로 비용이 감당되면 fixed radial axes에서 angular sequence를 수행한다. Radial h/p·q·rmax를 따로 변화시켜 plateau를 분리한다. Spectral Galerkin exactness나 작은 algebraic residual을 continuum certificate로 쓰지 않는다. 필요한 same-sector second root / residual-domain / gap 방법도 명시한다.
3. 비용 대비 수렴이 나쁘면 cusp enrichment 또는 independently assembled 2D method 등의 대체 reference를 연구 스레드에서 먼저 유도·구현·검토한다. 좌표와 basis가 같거나 다르다는 이름만으로 독립성을 주장하지 말고 assembly/operator/selection 오류가 공유되는 범위를 명시한다. Efficient solver의 tolerance만 바꾼 결과는 독립 reference가 아니다. Authors' ARSENY 코드 비교를 독립 구현으로 대체하지 않는다.
4. State, energy, direct L, torque 각각 수렴을 구분한다. Direct lane과 singular torque lane을 별도 구현한 현재 성질을 보존한다. Positive phase, dark symmetry, origin shift, momentum commutator와 exact units를 유지한다. 필요하면 phase/overlap·cluster continuation을 구현하되, 이번 한 지점 reference gap을 닫기 전에 broad R-grid로 확장하지 않는다.
5. 수렴 기준이 충족되면 C1b closure를 independent reviewer에게 검토받고 C2 finite-R audit의 새 실행 계약으로 인계한다. 미달이면 `ELECTRONIC_DISCRETIZATION_NOT_CONVERGED`와 측정된 한계·다음 최소 해결책을 반환한다. Method spread를 통계적 error bar로 만들지 않는다.

A2 numerical scaled sequences, broad collision-relevant C2 R-grid, collision propagation, cross sections, Eq55는 이 C1b의 자동 후속 실행이 아니다. A2 analytic constants를 finite-R tolerance/radius로 오용하지 않는다. B1 1,131 source-native cells와 13행 matrix는 그대로 유지한다.

프로덕션 source 변경, 새 branch, merge, force push는 금지다. 같은 branch의 새 research namespace에 append-only/non-force 게시한다. 원문 PDF는 private backup에만 포함하고 UTF-8 Git contents는 read_bytes().decode('utf-8')로 보내 줄바꿈을 보존한다. Cache/결과는 full identity와 atomic create-only write/fsync/checksum을 갖는다. 실행된 코드 bytes와 후속 수정본을 구분한다. 기존 실패 기록을 지우지 않는다.

Major node 종료 후 기존 Drive folder `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`, Dropbox `/BASS_DERIVATION_DOSSIERS_20260912`에 create-only 이중 백업한다. Git blob+size, provider ACK+metadata, raw restore verification을 구분하고 충분한 단계에서 중복 readback을 멈춘다.

Gate: CODE_I02_CLOSED=true; full_certificate_fail_closed=true; scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN; production_default_change=NOT_AUTHORIZED.
