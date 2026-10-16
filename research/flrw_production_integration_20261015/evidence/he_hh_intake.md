# HE / HH 최신 원전 통합 조사 — 2026-10-15

이 조사는 공개 GitHub의 최신 발견 branch/PR와 연결된 실제 Rust/Python 소스를 읽은 결과다. 기존 검산·캠페인을 재실행하지 않았다. 현재 사용자 승인은 production 수정·실행을 포함한다. 아래의 과학적 입력 부족은 승인 대기와 구별한다.

HE는 기존 cold H/He API와 covariant photon reference를 즉시 재사용할 수 있다. 다만 현재 production driver도 이미 characteristic pullback으로 에너지를 이동한 뒤 고정 에너지 격자에 보존적으로 투영한다. 이번 cold bridge의 문제는 **에너지 이동 자체의 부재가 아니라, 반복 투영 뒤 grid 에너지에서 문턱과 단면적을 평가하는 표현**에 있다. 따라서 short-clock 수정만으로 이 문제가 전부 해결되었다고 주장하면 안 된다. Root의 short-clock, native cold performance, fresh donor 연결을 먼저 통합하고 전체 cohort transport는 별도 변경으로 남겨도 된다.

## 실제 읽은 최신 식별자

| 대상 | branch / head | 직접 읽은 근거 |
|---|---|---|
| BASS_HE warm P01 | PR64, `research/he18-p01-remaining-cells-20261015`, `b0af50b052862320896085fac70250f51c077944` | `research/p01_remaining_cells_20261015/results/RESULT_STATUS.json`, `RESULT_KO.md` |
| BASS_HE cold transfer | `research/he18-rei-cold-tau-bridge-20261015`, `0ac62432d6950482ec6f8387dbeae8e2ef41a8d0` | `research/HE18_REI_COLD_CASE_A_GRACKLE_SOURCE_COUPLING_20261015.md` |
| 실제 cold bridge Rust | rei_bianchi `research/bass-he-optical-depth-transfer-20261015`, source-tested `9e484874aa83f3d7631352271f869e8835ce27b6` | `research/bass_he16_transfer_20261015/hhe_case_a_source_20261015/` 및 아래 crate API |
| WU088_HH | PR89, `research/hh-phys50-infinite-ell-trace-dtn-20261015`, `6db2b278aeed8c938098a92fb874e5b996d68e2e` | `src/wu088_hh/phys50_trace_dtn.py`, `research/hh_phys50_20261015/NEXT_DAG.json`, `results/EXECUTION_RECEIPT.json` |

PR64/89는 읽은 시점 모두 open이다. 최신 발견 head이지 main에 병합되었다는 뜻이 아니다. 전체 source URL·Git blob SHA·조회 범위는 동반 JSON에 있다.

## HE: 실제 API와 소유권

`rust/rei_microphysics/src/axbi_q_reference.rs`는 다음을 제공한다.

- `CovariantPhoton::{from_local,energy_at,direction_at}`: 보존량 $k_i=a_i E n_i$, 물리 에너지 $E(t)=\sqrt{\sum_i(k_i/a_i)^2}$. FLRW에서는 $E=E_{\rm birth}a_{\rm birth}/a$.
- `emit_from_axbi_source`: native source의 photons/H/s × proper seconds × spectral photon fraction × local angular count fraction. 이 API에 각도 Jacobian을 다시 곱하면 안 된다.
- `absorb_frozen_gas`: proper density와 geometry를 고정한 한 step의 $\lambda_i=c n_i\sigma_i(E)$, $\Delta N=N[1-e^{-\lambda\Delta t}]$, 종별 사건·binding·heat. 이 exponential은 **frozen 한 step**에만 exact하며 moving threshold나 coupled gas solver의 exact 해가 아니다.

`axbi_driver.rs::geometry_map`은 실제 pullback 뒤 `deposit`으로 두 이웃 energy cell에 N/U를 나눈다. `evaluate`는 grid $E_i$의 단면적을 쓰며, $N_{new}=N_\star/(1+\Delta t\,c\kappa)$, (\Gamma_j=\sum_i c n_H\sigma_j$E_i$N_{new,i})와 photo heat power를 계산한다. 이후 `AxbiProvider::point`를 호출하는 coupled backward-Euler residual이 있고, `chemical_stage`가 photo/CI/RR/DR/escape/CMB 장부를 단독 소유한다. 연구용 `Gas::photo`와 frozen exponential을 여기에 추가 적용하면 중복 이온화가 된다.

기존 point provider는 `rust/rei_microphysics/src/axbi_rates.rs::AxbiProvider::point(&IgmGasState,n_h_cm3,n_he_cm3,mean_h_per_s,tcmb_k,IgmPhotoInput)`다. provider ID는 `AXBI_GRACKLE_3_4_1_CASE_A_POINT_V1`, Grackle source는 `af7939494ce65007887ada7b98d1813df6843346`이다. 수치 동작 범위는 EOS로 복원한 $1\le T\le10^6$ K이며, 밖으로 나가면 fail closed한다. 범위는 경험적 fit 정확도 인증을 뜻하지 않는다.

| 값 / 사건 | 단위와 소유권 |
|---|---|
| gas state | fractions $[x_{HII},x_{HeII},x_{HeIII}]$, thermal energy erg/H |
| density / clock | proper cm⁻³ / proper seconds; 이미 적용한 팽창을 다시 적용하지 않음 |
| photo input | `gamma_s`: absorber당 s⁻¹; `heat_erg_per_absorber_s`: 사건당 에너지가 아닌 absorber당 power |
| 전자 수 | $n_e=n_Hx_{HII}+n_{He}(x_{HeII}+2x_{HeIII})$ |
| expansion | driver의 adiabatic half map이 소유하면 point RHS에 H=0 |
| Case A | capture escape, clumping=1, primary photo; escape energy는 emitted-photon SED가 아님 |
| source regularization | 기존 CI floor / CE cap을 유지하고 별도 diagnostics를 보존 |
| 에너지 항등식 | thermal + binding + escape = photo input + CMB input; expansion work 별도 |

원전 cold bridge는 q=0, E₀=54.42 eV, 희박한 초기 packet, 128 outer step에서 projected lane의 HeII 사건/초기광자 약 0.627702119356, covariant lane은 0이라고 보고한다. 대응 코드를 읽었으며 수치를 새로 계산하지 않았다. 이는 실제 FLRW 방향의 문턱 표현 결함을 수정할 근거지만, ongoing emissivity나 전구간 수렴을 이미 입증하지는 않는다.

선택한 7개 rate/RHS/EOS 함수의 source hash 일치 근거가 있다. 이는 전체 repo나 전체 compiled object 동일성을 증명하지 않는다. 또한 `case_a_source.rs` 첫 주석은 아직 photo-only/no recombination이라 쓰지만 실제 `include!("case_a_micro.inc.rs")`와 `apply_original_case_a` 호출은 CI/RR/DR/CE/free-free/Compton을 포함한다. 추출 시 주석을 실제 코드에 맞춰 고쳐야 한다.

## warm P01 결과의 재사용 범위

최신 PR64는 원래 warm source `a5c958c414dea41216b445c05f58df837f05cacb`의 saved 16/16 cells와 누적 tau 약 $1.27998310917643009\times10^{-7}$를 보고한다. 상태는 `SOURCE_SCOPED_INTERVAL_CERTIFICATE_CONDITIONAL_ON_PRIMITIVES`다. 기존 검산은 그대로 재사용한다.

이 결과를 cold Grackle FLRW의 수치 오차 인증으로 이전할 수는 없다. 원전 자체가 physical EoR ionic history, native binary64 rounding proof, formal primitive backend proof를 주장하지 않는다. warm 17 saved time nodes를 donor 17 species/state registry와 혼동하지 않는다.

## HH: 최신 진전과 정확히 남은 입력

PHYS50 실제 코드의 `verified_high_trace_lifting(frozen,terms=192,digits=24,...)`는 frozen SHA256 `f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d`를 고정한다. 원자단위 $a_0,E_a=2I_0$, screened H-H, $r\in[20,27]a_0$, 모든 m 및 ell≥21인 finite collar의 positive two-boundary Dirichlet DtN bound $4849/16800$가 현재 결과다.

실행 receipt는 새 targeted tests 24개, whole project 357개, Wolfram 교차확인 통과를 기록한다. 이 조사에서 재실행하지 않았다. receipt는 declared NumPy 2.3.5와 actual 2.4.2 차이도 보존한다.

최신 코드 자체가 physical outgoing high-boundary trace, global outgoing inverse/incoming adjoint, driven source, microscopic channel cross section, thermal $k_{HH}(T)$, rei HH_R10 source를 **아직 제공하지 않는다**고 명시한다. 따라서 numerical DtN bound를 반응률로 변환하거나 임의의 HH heating/electron source를 추가할 수 없다. 이는 **과학 입력 부족**이며 사용자 permission 문제가 아니다. HE/FLRW 실행을 막을 이유도 아니다.

현재 tip에 남은 과거 consumer interface의 `WAITING_ON_REI_DOMAIN`은 오래된 consumer commit과 404 조회를 담고 있어 현재 승인의 근거로 사용할 수 없다. 미래 HH 연결은 실제 rate, domain/distribution, identical-pair convention, stoichiometry, threshold/thermal/binding owner, physical uncertainty와 numerical error를 제공받는 좁은 계약으로 남긴다. electron-impact CI와 HH 사건을 이중 계수하지 않는다.

## root 통합의 구체적 범위

현재 authorized short-clock/native cold performance/fresh donor 작업은 위 API와 source identity를 재사용해 계속할 수 있다. 전체 transport를 완료했다는 표시는 아직 하지 않는다.

별도 transport 수정은 `axbi_driver.rs`의 photon state / geometry_map / inject / evaluate를 대상으로 한다. 기존 coupled solve를 유지하며 characteristic invariant 또는 birth-cohort energy에서 단면적과 heat를 평가하는 변경이다. 계속 방출되는 source cohort의 clock·수·에너지와 문턱 crossing 처리를 연결해야 한다. 기존 photons Vec와 24-value ledger checkpoint에 새로운 characteristic/birth state를 저장할 schema version이 필요하다. 기존 projected checkpoint를 새 물리 상태로 조용히 해석하지 않는다.

연속 방출 cohort는 step 수에 따라 커지므로 HPC 메모리 상한과 durable checkpoint를 함께 설계한다. cohort merge/compression은 문턱과 에너지 오차 통제가 생긴 뒤 적용한다. 필요한 신규 검증은 바뀐 연결의 문턱/ledger/clock/실제-source 수렴과 resume 재현성에 한정한다. 완료된 warm certificate, PHYS50 전체 suite, 기존 캠페인은 반복하지 않는다.

원격 mutation, git mutation, 새 numerical run은 이 조사에서 모두 0회다.

