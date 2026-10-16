# REI Rust 개발 명세: 실제 코드 계약과 실패 분류

Version `rei.ssot.impl.2`, 2026-10-16. 이 파일은 원본 Rust `rei_microphysics`를 직접 수정하지 않는다. 이론 정식화는 `REIONIZATION_DOSSIER_V2_KO.md`, 실제 노드는 `contracts/RESEARCH_DAG.json`이 기준이다.

## 핵심 typed interfaces

`GeometrySnapshot`은 `{proper_time_s, a_i:[3], H_i_per_s:[3], tetrad_convention, geometry_source_SHA}`를 가진다. `normal observer`의 energy/direction은 `E_ev>0`, `sum(e_i²)=1`, photon occupation>=0이고 정확 Killing transport는 `E1/E0=||diag(a_i0/a_i1)e0||`, `J_Ω=det(diag(a_i0/a_i1))/r³`. 음수 scale factor, NaN, 0 E, 도메인 밖 t는 typed error. 연속 ODE integration 대신 direct characteristic을 사용해 오차 축을 분리한다.

`RadiationCohort`는 `{birth_time_s, observer_frame, original_emission_energy_eV, conserved_p_i, photon_count_per_H, source_group_id, source_rev, source_event_id}`. `SourceOperator`는 `{emissivity: dN/dt and dU/dt, spectrum/support, angle, source proper time, unit/s, photon ownership}`를 요구한다. `AbsorptionOperator`는 `{proper absorber densities, sigma(E), channel_id, threshold_event, n_e/heating/chemical source, signed radiation/gas transaction}`. `PreparedAbsorption`/`PreparedDirectRates`는 한 이벤트, 한 에너지 공급자만 사용하며 source/event를 두 번 consume하는 함수를 차단한다. 빠른 근사는 `SOURCE_SUBCELLS`, `TRANSPORT_REFINEMENT` 둘 모두 최소 수용조건이 맞을 때만 opt-in.

`GasState`는 `{nuclei:[{isotope, charge_state, proper_density_m3}], n_e_rest_m3, Tgas_K, U_thermal_J_m3, U_binding_J_m3, U_nonthermal_J_m3, H_i_per_s, external_heat_J_m3_s}`. 단일 charge-neutral closure를 가지며 partial LTE/Case-A/Case-B 등 closure 이름 필수. `nB` 중복 계산은 금지. `ThermalRxnOwner`는 `AtomicRhs|ThermalSubstep` 단일 enum, helium spectator component가 존재하면 fixed-pure-H-D 경로가 error를 돌려준다. `CoupledStep`은 absolute proper seconds와 `X=ln(a/a0)` adapter를 혼동하지 않고, 같은 `dt`에서 radiation/gas source 공급 시각을 검증한다.

`ObserverRay`는 `{direction, screen basis if E/B, fixed observation event, emissivity/opacity history, n_e rest current, observed redshift root policy, tail known/unknown}`. `OpticalDepthResult`는 구간 유한 적분 `tau_partial`, `visibility_bin_masses` 및 `tail_status` 필수. unknown tail이면 `tau_total=null`, `P_total=null`; fill-in 1은 금지. `Q_V`를 `n_e`에 독립 곱하지 않는다.

## 입력 데이터 잠금

Production 입력 필수 필드: `cosmology_identifier`, `H(t)` 혹은 source-bound geometry `H_i(t)`, proper time origin, `T_CMB0`, `n_H0`, `Y_He`/isotope census, rate coefficients with unit and temperature domain, source/emissivity spectral+angular history, `source_owner_SHA`, `domain/rate_branch`, recombination IC donor SHA. CMB transfer에서는 별도 BASS collision kernel/screen rotation을 pin한다. 대역 혹은 적색편이 바깥 부분은 extrapolate하지 않고 unknown tail로 반환한다.

## 오차 예산: 서로 다른 다섯 축과 실행 판별법

`E_numerical=(time_native, transport_spectral, angle, birth_age, source_substep, interpolation, linear_solver, roundoff)`를 하나의 값으로 조기 합산하지 않는다. 각 refinement는 다른 축 고정과 동일 immutable source 및 physical input이 필요하다. `E_atomic`은 Grackle/Verner/HE source와 rate domain, `E_source`는 emissivity/UVB 및 photon birth ages, `E_geometry`는 H/shear/observer, `E_closure`는 effective homogeneous approximations와 unknown tails. Unit target은 frozen 입력의 외부 요구치를 계승한다. 예를 들어 PR171 HeI **integrated event** adjacent target `<0.005`는 `Gamma` target과 대체 불가능하며, 자체 error bound는 별도 수학적 증거가 있어야 한다.

구조적 불변량은 photon number `N_init+B=A+N_next`, nuclear `∑ A n_A`, charge `n_e`, energy `radiation + binding + heat + escape + CMB + work`이며 부호는 transaction convention을 고정한다. **보존식 PASS는 method temporal order PASS가 아니다**. 목표 시간 차수 평가에는 같은 원본 RHS의 independent reference(필요하면 Radau)와 복수 독립 grid ratio를 사용하고, source/on 및 stiff/nonstiff를 분리한다. Native Rust `FE` 관측기 stage O5/O6가 실패하면 물리 출력과 관측 패킷 실패를 분리한다.

## 매 턴 실행·게시 절차

읽을 순서: 1) `README_KO.md`, 2) `contracts/RESEARCH_DAG.json`의 `status`, 3) `contracts/SOURCE_REGISTRY.json`의 frozen parent, 4) `docs/DAG_NODE_GUIDE_KO.md`에서 다음 READY node, 5) `docs/REIONIZATION_DOSSIER_V2_KO.md` 해당 formula, 6) 관련 GitHub source file at exact SHA. 정확한 source semantic identity를 확인하기 전에는 코드 합본을 하지 않는다. `git status`가 불가한 커넥터 환경에서는 isolated new branch의 source HEAD만 사용하고 owner worktree는 만지지 않는다.

`T0`: T<=30 s, RAM<=256 MiB (schema/analytic). `T1`: T<=120 s, RAM<=1024 MiB (isolated Rust unit). `T2`: T<=180 s, RAM<=2048 MiB (single bounded native component). 최신 실제 환경을 측정해 더 낮추고 `CARGO_BUILD_JOBS=1`, `RUSTFLAGS`를 변경하지 않으며 cargo `--offline --locked`를 기본으로 한다. 임의 full EoR / NCP / external local subprocess는 이번 요청의 샌드박스 모드에 포함되지 않는다.

각 단위는 `source identity`, `input`, `claim ceiling`, `commands+exit code`, `tests`, `artifacts SHA`, `DAG changed status`, `known blockers`, `next executable unit`을 남긴다. 새 결과가 없으면 meta-audit만 늘리지 말고 다음 READY 단위로 이동한다. `BACKUP NOW` 요청 시 선택적 실험을 중지하고 체크포인트부터 한다. 새 원본 사용자 첨부파일의 원문을 public GitHub에 무단 통째로 복제하지 않는다.