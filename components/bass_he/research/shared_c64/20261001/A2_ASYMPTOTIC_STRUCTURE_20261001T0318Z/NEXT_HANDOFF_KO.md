# 다음 단일 node: C1 electronic solver architecture

ROLE=BASS_HE_C1_TWO_CENTER_ELECTRONIC_STRUCTURE_NUMERICAL_DESIGN

기존 `cosmosapjw-quantum/BASS_HE`, branch `research/shared-c64-crossrepo-20260928`에서 이어간다. 이번 A2 publication commit/tree는 외부 delivery receipt가 소유한다. 부모 A1b commit은 `771b1fe1b70930196a0f812bdb118bec04049c8c`, scientific source pin은 `1a83a67e12de1ddc2aede0ff67168f7071450ab3`다. 기존 source/production 파일은 변경하지 않는다. 먼저 fresh HEAD/tree를 읽고 해당 dependency의 변경 여부만 판별한다.

필수 입력은 `RESULT.json`, `A2_ASYMPTOTIC_DERIVATION_KO.md`, 두 `derivations/*_AUTHOR_KO.md`, `review/A2_INDEPENDENT_REVIEW.json`, `CONVENTIONS.json`, `BASS_HE_NUMERICAL_ARCHITECTURE.md`다. 이전 A1b full P⊕Q 정식화와 source v3는 nested immutable dependency다. A1과 A2의 범위는 정확한 단일전자 prescribed-path 정식화와 analytic asymptotics다. Whole program, finite-R numerical accuracy, six-channel closure는 완료하지 않았다.

이번 한 질문: **exact fixed-sector two-center Coulomb eigenstates와 direct/torque coupling을 안정적으로 계산할 독립 reference/efficient 표현을 어떻게 정하고, 그 구현·검증 계약을 재현 가능하게 고정할 것인가?**

1. 현재 원전 DB에서 C1 관련 subset만 읽는다. Prolate spheroidal separation, 고차 FEM/spectral element, B-spline, Lagrange-mesh/DVR, two-center STO/GTO를 conditioning·cusp·축 조건·무한영역·상태 continuation·coupling 평가 기준으로 비교한다. 라이브러리/코드 사용 시 정확한 version/commit을 확인한다. Authors' ARSENY code를 독립 구현으로 부르지 않는다.
2. 최소 하나의 고정밀 reference representation과 하나의 효율적 representation을 채택한다. 같은 discretization의 tolerance만 바꾼 두 실행을 독립 reference로 취급하지 않는다. 선택의 물리·수치 이유를 기록하고 실제 weak/operator form, 경계조건, quadrature와 cache identity를 먼저 유도한다.
3. 대상은 g=lowest m=0 및 bright lowest real-cosφ |m|=1이다. R-grid에서 energy sorting만으로 state label을 결정하지 않는다. Overlap matching/phase continuation, isolated projector, near-degenerate cluster transport를 설계한다. Full n=2/H1s rank-5 cluster와 fixed-sector simple eigenstates의 차이를 보존한다.
4. Point-Coulomb cusp, ρ=0의 m별 regularity, infinite-domain mapping/truncation, spectral pollution, eigenresidual 및 Rayleigh gap을 명시한다. State convergence와 L_y/torque convergence를 분리한다. 가능하면 원래 point-Coulomb 문제에 직접 작용하는 표현을 사용하며 임의 softening을 silently 도입하지 않는다.
5. Direct lane은 ⟨g,L_y^O b⟩, torque lane은 −iℏ C_R(T_B−T_A)/Δ_R다. 두 lane을 같은 analytic formula의 복제본으로 구현하지 않는다. R10R의 positive-phase 부호, dark π_y=0, equal-charge symmetry, origin shift 및 exact momentum commutator를 analytic tests로 준비한다. Singular torque는 별도 Hardy/form treatment와 quadrature convergence가 필요하다.
6. A2 analytic checks를 실제 실행 계약에 넣는다: x=R/a_A→0에서 iL/(ℏx³)→4√2/15, x→∞에서 iL/(ℏx)→32√2/243, He-origin −iL_B/(ℏx⁻²)→128√2/729. Raw unscaled absolute error만으로 cubic limit를 통과시키지 않는다. Leading power와 spatial/basis error를 분리한 scaled residual·sequence convergence를 설계한다. Big-O/global envelope 상수와 유효 반경은 수치로 구하지 않았으므로 이를 tolerance나 finite-R bound로 사용하지 않는다.
7. UA eigenvalues·단일중심 hydrogenic energies·large-R fixed-sector limits·virial/Hellmann–Feynman의 적용 조건을 analytic regression으로 정한다. Large-R energies의 common −κ_A/R와 quadrupole correction, H1s/He n2의 unequal 1/R detuning을 유지한다.
8. Chat thread에서 수학·코드·최소 tests·bounded pilot contract를 최대한 완성한다. C1 scope의 작은 검증 모델만 허용하고, C2의 collision-relevant R-grid 전체 audit나 collision solver는 먼저 실행하지 않는다. Heavy 실행이 필요하면 정확한 input/code identity, tolerance, 종료조건, 예산과 반환 스키마를 가진 실행 handoff를 작성한다. Runtime가 물리 모델이나 tolerance를 임의 변경하지 못하게 한다.
9. 실제 실행한 것과 준비만 한 것을 명확히 구분한다. Unchanged A1/A1b/A2 CAS나 closed scientific suites를 새 라벨로 반복하지 않는다. 새 discretization/구현에 영향받는 analytic·invariant·convergence·failure checks만 실행한다. Authoring과 independent scientific review를 분리한다.

C1의 목표 STOP은 `ELECTRONIC_SOLVER_ARCHITECTURE_FROZEN`, 또는 실제 증거에 따른 `ELECTRONIC_DISCRETIZATION_NOT_CONVERGED`다. architecture가 고정되었다는 사실만으로 C2 magnitude convergence를 선언하지 않는다. 다음 단일 node를 실제 gate에 맞춰 정한다.

기존 B1 1,131개 native cells·13행 benchmark matrix는 그대로다. Source-native exact cells만 사용하며 interpolation, fitting, missing shell sum, energy/frame reinterpretation을 하지 않는다. 이번 C1의 solver 선택을 benchmark 일치도로 조정하지 않는다.

Gate: CODE_I02_CLOSED=true; full_certificate_fail_closed=true; scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN; production_default_change=NOT_AUTHORIZED.

같은 branch의 새로운 research namespace에 append-only/non-force로 게시한다. 원문 PDF/페이지 이미지는 private backup에만 포함한다. 기존 Drive folder `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`와 Dropbox `/BASS_DERIVATION_DOSSIERS_20260912`에 create-only 이중 백업한다. UTF-8 content는 `read_bytes().decode('utf-8')`로 전송하여 CSV 줄바꿈도 보존한다. Remote Git blob·size, provider ACK·metadata, 실제 raw restore를 구분하고 충분한 tier가 닫히면 중복 readback을 멈춘다. 새 branch/merge/force push/production 변경은 승인되지 않았다.
