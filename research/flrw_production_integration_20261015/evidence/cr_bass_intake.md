# BASS_CR·BASS 현재 소스 통합 intake — 2026-10-15

현행 FLRW 생산을 계속하면서 연결할 실제 코드가 있다. 먼저 root가 복원한 native short-clock driver를 정리하고, 다음 단위로 **양의 source subcell quadrature와 per-ray/per-age child moment 상태**를 붙이는 것이 가장 작고 실행 가능한 delta다. 비열적 CR 전체나 새 anisotropic background가 완성될 때까지 기존 FLRW lane을 멈출 근거는 이번 조사에서 찾지 않았다.

현재 GitHub API·exact-head 소스·저장 결과를 읽었다. clone, git mutation, 과학 계산, 기존 suite 재실행은 0회다. “passed”는 upstream 저장 근거이며 이번 세션의 재검산 결과가 아니다. 상세 URL·blob SHA·API·units·국소 prerequisites는 동반 JSON에 기록했다.

| 저장소 / 선택 lane | 현재 head | 상태 |
|---|---|---|
| bass_cr PR71 / C8 adaptive q | `ff23e118a72d268bb44f24a35a0eb053a80bb2c8` | open draft, mergeable; C7A·C10 상속 |
| bass PR161 / gamma–nu·FD96 | `a16c44d28357428b92f15d709eee86ca7bba4f21` | open draft, mergeable |
| bass PR155 / FA03 reduction | `a626540f499e99005bebc2cd3419acffc9ddde32` | open draft, mergeable |

범위는 각 repo의 updated 내림차순 open PR 첫 15개, 선택 PR 상세 및 exact-head tree/파일이다. 모든 branch/PR 감사는 아니다. default main은 bass_cr `77237751bdd2aed5934bf7fc3bc626d631a09058`, bass `9c6506e4e2087129a8b674ff10438e5db1a55c9d`로 최신 연구 head와 다르다.

Root는 REI `0fcb2dddf5de6b583c2e00f150abff0b2afb6315`의 `rust/rei_microphysics/src/axbi_driver.rs`, `axbi_sources.rs`를 복원했고 SOURCE07 Python은 prototype이라고 확인했다. 이는 root의 owner 확인이며 이 intake의 독립 관찰은 아니다. Python 구현 존재를 native production 완료로 승격하지 않는다.

## 첫 native delta: source shape·child moments

[CR71](https://github.com/cosmosapjw-quantum/bass_cr/pull/71)의 상속 `research/cr_c10_source_subcells_20261015/src/source_subcells.py`는 실제 실행 가능한 source quadrature다.

- `source_quadrature(n_energy, ratio_R=1, order=8, max_ref_eV=433)`: 원 native48·Simpson32 source fraction을 보존하는 양의 GL subcell.
- `source_and_reaction(q, neutrals_cm3, dt_s, total_emitted_per_H)`: 같은 q-cell의 N/U, species별 흡수 및 열량.
- `cached_source_kernel`, `batched_frozen_reactions`: 같은 source/geometry의 opacity 재사용과 독립 ray batch.

단위는 photons/initial-H, reference-eV/initial-H, physical-eV, proper-second, neutral cm⁻³, cross section cm²다. E=R E_ref. 현재 source는 BB50K의 13.6–100 eV, 0<R≤1, source 전체를 덮는 reference support에 제한된다. 임의로 hardening된 stock에 fresh-source closure를 다시 적용하면 안 된다.

Fit activation 13.60/24.59/54.42 eV와 물리 결합에너지 13.598434599702/24.587389011/54.41776 eV는 구분한다. Owner의 angular source Jacobian·R·emission clock은 바깥에서 한 번 적용한다. Photon destruction의 binding/heat와 surviving photon energy는 같은 사건 ledger에 둔다.

저장 `results/OWNER_REFERENCE_COMPARISON.json`의 nE256·동일 frozen gas에서 HeI subcell은 `1.4281834584164705e-9/H`, owner continuum은 `1.4281834584030507e-9/H`다. 한 단계 source 근거이며 전체 H/He 진화 정확도가 아니다.

구현 순서는 native short-clock 다음 `axbi_sources.rs`의 injection을 양의 subcell/진짜 moment로 옮기고 `axbi_driver.rs`가 source·age·ray·현재 proper clock을 전달하게 하는 것이다. Representation이 바뀌면 checkpoint manifest의 source/grid/clock identity도 새로 결속한다.

## Envelope와 선택적 refinement

현재 `research/cr_c7a_shapefree_20261015/src/moment_envelopes.py`는 support·N·U와 frozen gas/dt에서 shape-free event/heat bounds를 만든다. C8 `src/adaptive_q.py`의 실제 API는 다음과 같다.

```python
oracle = PositivePacketOracle(
    reference_energies, photons_per_h, source_id, ray_id, proper_epoch_s)
grid = AdaptiveQGrid(
    oracle, ref_edges, ratio_R, neutrals_cm3, dt_s,
    budgets, nodes_per_branch=4)
receipt = grid.run(max_cells, stop_on_precision=True)
```

여섯 budgets는 HI·HeI·HeII event count/H, 이어 species별 heat eV/H다. Threshold 우선 split, exact Fraction child moment 합, old/new enclosure 교집합을 쓴다. Oracle의 ID/clock 필드를 owner 현재 상태와 대조하는 책임은 adapter에 있다.

**진짜 child N/U가 없으면 split만 하지 않고 현재 grid의 parent-moment bound를 유지한다.** 이를 전체 solver no-go로 만들지 않는다. 다른 age/ray를 pooling해 oracle을 발명하지 않는다. Support·gas·proper dt가 바뀌면 template identity도 갱신한다.

저장 source 결과의 HeI width는 adaptive96 `1.6721198232907923e-10`, uniform96 `1.1776148705022724e-9`; adaptive128 `5.487881294736694e-11/H`다. 128-cell PASS_SCOPED는 HeI budget 1e-10을 만족한 결과다. 다른 다섯 budget은 0.1이므로 모든 관측량이 같은 상대정밀도를 얻었다는 뜻은 아니다. PR71의 47 tests 기록과 실제 test source를 읽었고 재실행하지 않았다.

## 비열적 CR-on은 별도 source coupling

현재 CR71 head에도 아래 실제 코드가 있다.

| 파일 | 기능 | 실제 추가 결속 |
|---|---|---|
| `research/cr_kernel_cutoff_20261013/kernel_event_adapter.py` | saved9600 kernel의 BoundKernel 사건 column | selected source, SI volume/density, 현재 에너지 |
| `research/cr_kernel_cutoff_20261013/thermal_cutoff_solver.py` | finite-box/atomic cutoff·EOS root | 양의 capacity, bracket 또는 atomic branch |
| `research/cr_feedback_step_20261013/feedback_solver.py` | 보존적 capacity-map Picard | caller가 제공하는 self-map/domain 및 q<1 |

이 코드는 source eV를 J로 바꾸고 comoving cell count·proper time·density m⁻³를 쓴다. Photon 공급자의 cm⁻³와 그대로 섞으면 안 된다. Thermal electron만 screening density와 열용량에 들어가며 active/all count와 구별한다. Cutoff join은 **실제 transferred energy와 count**를 둘 다 넘긴다. Threshold×count나 heat-only 추가로 대체하지 않는다. Primary birth-ionization과 secondary degradation도 별개다.

보존된 Q_e=t A(W), nH=140m⁻³, T=100K, xi=.01의 fixed-bath source는 현재 REI source와 자동으로 동일하지 않다. 선택 source와 actual coupling만 새로 결속·확인한다. 기존 원자 문제의 HOLD/NO_GO를 CR-off FLRW 생산 전체 금지로 옮기지 않는다. 현재 사용자의 production 수정/실행 승인에 비추어 과거 “native starts 0”은 실행 이력이지 현재 권한 금지가 아니다.

## BASS background: FLRW control부터

[PR161](https://github.com/cosmosapjw-quantum/bass/pull/161) `joint_kinetic.py`의 `KineticGammaNuMassive`는 원 AX03 source lock, 독립 gamma/nu hierarchy, FD96 massive moment를 Einstein H·shear·proper clock에 넣는다. `rust_rei_joint.rs`는 실제 REI BackgroundPoint/geometry type을 읽는 bridge다.

H·s는 s⁻¹, n_e는 cm⁻³, stress-energy는 J/m³, Sigma=sqrt(3)|s|/H, pi=diag(-Pi,-Pi,2Pi)다. Gamma만 Thomson damping을 받고 neutrino는 collisionless다. 원 Omega_r를 Tcmb0 photon과 나머지 neutrino로 나누며 massive fraction은 원 nonbaryonic Omega_m 일부를 **대체**한다. Matter를 추가하여 중복 계산하지 않는다.

가장 작은 native case는 저장 **FLRW_CONTROL**이다. Sigma, photon/nu P2, massive fraction을 모두 0으로 하면 원 Omega_m 법칙을 유지한다. Sigma만 0이고 anisotropic Pi가 있으면 뒤에 shear가 생기므로 FLRW control이 아니다. Isotropic massive fraction도 기존 cold-dust H와 다른 모델일 수 있다.

저장 `JOINT_CAMPAIGN/RESULTS.json`에는 8cases·3208rows, CSV SHA256 `bb1753f5f9e70bdce22f0f1f1e7f68426510c9786a4e102993030e6b2fa914a7`가 있다. Native bridge constraint 최대 상대잔차 `3.3306690738754696e-16`와 네 corruption rejection이 기록됐다. Table/type checker이며 native coupled HHe 생산 실행은 아니다.

AX08 electron donor는 과거 실제 312238-row 이력의 one-way 보간이며 저장 최대 상대오차는 약 1.9755e-4다. FLRW_CONTROL은 donor 없이 이미 실행되었다. Private donor 부재가 이 경로를 막지 않는다. 현재 ne의 self-consistent 공급은 별도 coupling·identity로 구현한다. 기존 AX08 accepted checkpoint를 다른 background로 이어붙이지 않는다.

## FA03 observer 최적화

[PR155](https://github.com/cosmosapjw-quantum/bass/pull/155)의 `deterministic_reducer.py`, 상속 C7 `stokes_vector.py`는 실제 코드다. Real-Stokes는 FA03의 고정 2×2 coherency equation 구현이며 full angular Thomson/HHe solver가 아니다.

C9 bound는 두 곱셈 후 balanced pairwise addition이라는 operation graph의 gamma_(2+ceil(log2N))다. 이전 opaque einsum bound를 이어쓰지 않는다. Model·weights·operation graph가 맞는 observer reduction에서만 포팅한다. 작은 문제의 저장 thread 성능은 더 느려 workers=1이 기본이다. 기록114tests와 작은 component timing을 64-core production scaling으로 확대하지 않는다.

## 변경 부분만 확인

1. Native source→ray/age/clock, R/J 단일 적용, cm⁻³↔m⁻³·eV↔J 경계.
2. 사건의 binding+heat+survival energy 및 true child N/U partition.
3. Donor 없는 FLRW_CONTROL의 source/geometry 단위·identity와 mismatched old restart 거부.
4. CR-on을 추가할 때 active/thermal electron·cutoff join·선택 source event ledger.
5. 새 병렬 구현의 같은 입력 결과·deterministic reduction·aggregate resource admission.

원 upstream suite는 반복하지 않았다. 현재 owner native API에 붙이는 변경으로 새로 생긴 위험만 검사하면 된다.

