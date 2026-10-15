# 목표에서 실제 결과까지의 개발 계획

**재이온화 이력을 완성해서 표준적인 BBN plot처럼 시간/온도에 따른 핵종/이온의 비율을 그린다.** source-backed homogeneous non-tilted axisymmetric Bianchi I와 matched FLRW에서 actual species abundance history를 계산하고 proper time 및 gas temperature 그림, paired abundance differences·수치 오차·source/IC robustness·재현 가능한 보고서를 제공한다. τ/visibility는 secondary optional output으로 둔다. 현재 완료된 identity/adapter/retained 자료는 재사용한다. 새 physical solver run은 0이며 scientific goal은 IN_PROGRESS다. 원본 [v2 PLAN](../REI-ATOMIC-REUSE-RESET-20261012/PLAN.json)의 17 의무는 새 [DAG](EXECUTION_DAG.json)에서 보존·매핑한다.

## 물리 모델과 비교

축대칭 geometry convention은

\[
a_\perp=a e^{-b},\qquad a_\parallel=a e^{2b},\qquad s=\dot b,\qquad
(H_\perp,H_\perp,H_\parallel)=(H-s,H-s,H+2s),\qquad \sigma^2=3s^2.
\]

non-tilted normal/gas frame에서 homogeneous H/He와 thermal state, energy–angle photon inventory를 진화시킨다. unit normal은 `n·n=-1`이며 physical four-velocity는 `U=c n`, `U·U=-c²`다. donor/provider가 쓰는 unit/physical four-velocity와 coordinate·clock convention을 명시적으로 이 표기로 map한다. 캠페인의 signed amplitude는 reference epoch에서 `q_ref=s_*/H_FLRW(a_*)`로 정의하고 instantaneous shear ratio `Σ=s/H`와 구분한다. 둘을 같은 수로 기록하거나 동일 normalization의 q로 혼용하지 않는다. 상세 정의는 [SCIENCE_GOAL_FRAMING.md](SCIENCE_GOAL_FRAMING.md)를 따른다. axisymmetry만으로 zero flux가 보장되지는 않는다. 초기 photons와 emissivity는 `μ→−μ`에 대해 even이어야 하고 microphysics도 그 symmetry를 보존해야 한다. angular reflection pairing과 net radiation momentum/net gas force residual을 확인한다. 이를 만족하지 않는 source는 동일 non-tilted baseline에 자동 편입하지 않는다.

물리적 비교는 같은 proper matter/radiation density·Λ와 동일 source/IC/provider convention을 쓰는 FLRW와 stress-free prescribed/test-field Bianchi I다. `H²=H_FLRW²+s²`, `s∝a⁻³`를 사용하고 mean expansion도 실제 차이로 유지한다. radiation anisotropic stress가 geometry에 주는 feedback은 이 baseline에서 생략하므로 그 생략의 유효성을 estimates/error budget으로 보여 준다. 이 생략이 목표 오차를 넘으면 해당 scope를 좁히거나 새 bounded geometry-feedback task를 열며 계산을 unqualified dynamical-universe prediction으로 승격하지 않는다. 같은 H를 강제한 isotropic-transport control은 transport/background 분해를 위한 별도 diagnostic이다.

특성선 photon evolution은

\[
\dot E=-E[H+s(3\mu^2-1)],\qquad \dot\mu=-3s\mu(1-\mu^2)
\]

에 맞춰 existing ray/packet transport에 연결한다. phase-space measure와 energy/angular cell remap, boundary flux/redshift work를 실제 geometry와 동일 clock으로 귀속한다. 물리 cutoff와 atomic binding threshold는 구분한다. gas photoabsorption·ionization·heat, recombination escape/OTS와 radiation loss를 같은 event에서 한 번만 센다. 기존 implicit primary solver/event ledger를 재사용하고 새 solver를 먼저 설계하지 않는다.

`z̄=a⁻¹−1`는 mean redshift다. 관측 redshift는 ray·방향과 endpoint를 갖는 별도 출력이다. cold comoving observer의 고정 cosmic-time endpoint에는 `τ=c σ_T∫n_e dt`가 방향 독립이다. directional observed-redshift endpoint의 비교를 fixed-time τ anisotropy로 혼동하지 않는다. full observer τ는 일관된 late history/tail이 공급될 때만 추가하고 unknown tail은 null로 둔다.

## Abundance 정의와 BBN 형식 출력

기본 network는 H/He ionization charge evolution이며 필수 표시는 HI/HII/HeI/HeII/HeIII와 electrons다. 총 핵종 inventory는 donor에서 공급된 양이고, 재이온화에서 핵종의 charge state가 진화하는 것과 구분한다. 추가 nuclide/isotope는 supported source/provider와 configuration을 갖고 실제 진화했을 때만 species registry·CSV·plot에 넣는다. 17-state registry만 공급됐다는 이유로 모든 17 species를 계산했다고 하지 않는다.

Element ion fractions는 `x_Hq=n_Hq/n_H`, `x_Heq=n_Heq/n_He`다. BBN 형식 baryon-normalized abundance는 `Y_i=n_i/n_b`다. `n_b`는 선택 모델의 **전체 baryon inventory**를 기준으로 하며 전체 inventory의 `Σ A_i n_i`와 같다. H/He-only baseline에서는 `n_b=n_H+4n_He`다. 실제 tracked species가 전체 inventory의 subset이면 그 subset만으로 n_b를 재정의하지 않고 omitted reservoirs를 기록한다. 따라서 `Σ_tracked A_i Y_i<1`도 가능하며 이를 인위적으로 1로 renormalize하지 않는다. electron은 baryon sum에 포함하지 않고 `n_e/n_b` 또는 다른 명시된 normalization으로 따로 표시한다. sum rule의 포함 species·omitted reservoirs를 기록한다. 제대로 진화한 zero와 지원되지 않은 null/absent를 구분하고 log-axis floor를 과학적 양으로 만들지 않는다.

두 필수 그림은 `research/axbi_goal_20261014/figures/abundance_vs_time.png`와 `abundance_vs_Tgas.png`다. matched overlay와 paired difference의 planned 파일은 같은 폴더의 `flrw_bianchi_abundance_comparison.png`, `delta_abundance_resolution.png`이며, 실제 history CSV는 `OUTPUT_CONTRACT.json`을 따른다. 이 이름은 미래 산출물 계약이며 현재 존재하는 새 과학 결과가 아니다. proper seconds와 clock origin을 지정하고, gas temperature를 배경/CMB temperature와 혼동하지 않는다. 재가열·비단조 T_g가 있으면 시간 순서의 parametric curve·분기·방향 화살표를 사용한다. T만 정렬해 모든 history를 single-valued T 함수처럼 만들지 않는다. optional `T_ref=T0/a`는 background reference이며 exact Bianchi angular CMB temperature가 아니다. matched FLRW/BI overlay, Δabundances와 time/energy/angle convergence·source/IC uncertainty를 그림에 연결한다.

## 입력 선택과 구현

계획 구간은 mean `z̄=20→4`이며 selected source/provider가 전체 trajectory에서 지원돼야 한다. cosmology·IC epoch·proper-time origin·H/He proper density·fractions·thermal IC·initial radiation·actual source role/history/units·closure를 AX01/02/04에서 근거와 exact identity로 결정한다. 20 K와 6.137 K는 provider/REC/cosmology가 맞는지를 조사해 해결할 입력 선택이며 새로운 사용자 approval을 요구하는 자동 trap이 아니다. supplied data와 근거 있는 모델 선택을 구분한다. matched REC donor가 필요하면 현재 pinned provider의 IC/clock/cosmology 조건을 맞춘다. full 17-state registry를 실제 donor history로 대신하지 않는다.

현재 warm adapter는 InitialStock만 받으며 ExternalEmissivity/ImposedUvb를 거부한다. full-goal driver에는 **실제 시간 변화 spectral emissivity callback**과 supported source/IC/provider가 연결돼야 한다. UVB 경로를 별도 선택하면 source ownership과 역할을 명시하고 photon evolution과 중복하지 않는다. 따뜻한 FT03 guard를 숫자로 넓히거나 admission flag를 바꾸어 cold domain을 승인하지 않는다. point와 root/interval provider가 다른 경우 scope를 구분하고 새 point physics에 old interval certificate를 상속하지 않는다.

## 실행 순서와 산출물

| Node | 실제 작업 | 결과와 다음 전이 |
|---|---|---|
| AX00 | 기존 scoped 완료/결손 가져오기 | 감사 identity와 retained 자료 재사용; old HOLD/예외 보존 |
| AX01 | source-backed scenario/IC/clock 해결 | 지원 범위·구체적 선택·null 결손. AX04 source binding 시작 |
| AX02 | H/He rate/thermal domain·owners 결정 | supported provider callback/domain; code integration과 독립 착수 |
| AX03 | axisymmetric background/μ-even contract | a_perp/a_parallel/shear/clock, matched physical FLRW, feedback validity budget |
| AX04 | actual emissivity·시간/단위 연결 | source history callback 및 초기 radiation/boundary ownership |
| AX05 | 기존 core에 coupled driver 구현 | AX02/03/04를 실제 RHS·ray/packet·ledger로 연결, changed-seam tests |
| AX06 | 첫 FLRW/AXBI 짧은 supported interval | 실제 CSV/ledger/figure, q_ref=0 대응·positivity/conservation·pilot cost |
| AX07 | selected full-interval FLRW history | species/ne/T/Γ/photons·체크포인트·단계별 그림 |
| AX08 | matched signed-axisymmetric family | AX06 뒤 AX07과 병행. q_ref=0 및 nonzero signed cases, identical source/IC |
| AX09 | optional receiver/interface 구현 | 기본 OFF. abundance goal을 막지 않고 실제 필요할 때 활성화 |
| AX10 | optional τsegment/visibility 출력 | 기본 OFF. unknown tail은 null; abundance finalization의 dependency가 아님 |
| AX11 | 시간·energy·angle refinement와 response | empirical convergence, signed response/resolution bound, uncertainty 분리 |
| AX12 | source/IC robustness | exact variants와 response; scenario range는 posterior가 아님 |
| AX13 | report workspace/methods 생성 | 지금 시작. 실제 milestone별 tex/CSV/figures/PDF 갱신 |
| AX14 | final abundance figures/manuscript | AX07/08/11/12/13 histories·error·limits를 실제 논문으로 연결 |
| AX15 | 관련 독립 scientific decision | 전체 selected-interval goal과 claim scope에 대한 판정 |
| AX16 | scoped release | 실제 최종 artifacts·reproduce commands·remote SHA/PR; 이후에만 GOAL_DONE |

처음 READY는 AX01/02/03/13이다. AX09/10은 기본 optional OFF이며 τ/visibility/full observer tail은 abundance goal의 완료 조건이 아니다. AX01/02/03은 source/provider/background 결정이고 integration 완료를 먼저 요구하지 않는다. 2–4 native writers가 가능하면 독립 경로로 나눈다. shared `lib.rs`/Cargo/primary source는 한 owner가 수정하고 같은 파일은 직렬화한다. controller만 checkout/stage/commit/push한다. 기존 checkout/dirty/untracked를 보존하고 자동 clone/worktree를 만들지 않는다.

## 결과 그림과 논문 구조

| Figure/output | 데이터 | 보여 줄 과학 질문·주의 |
|---|---|---|
| Background/validity | a_perp,a_parallel,H,s,stress-feedback estimate | physical FLRW과 expansion 차이·test-field 적용 범위 |
| abundance_vs_time | HI/HII/HeI/HeII/HeIII/electrons 및 실제 추가 evolved species versus proper time | elemental fractions와 Y_i=n_i/n_b를 구분; declared clock origin |
| abundance_vs_Tgas | 같은 history를 time-ordered T_g parametric curve로 그림 | reheat/nonmonotonic T는 branch/arrow; T sorting 금지 |
| Thermal/rates | T,Γ species, heating/cooling ledger | source/provider 작동과 thermal response |
| Radiation moments | spectra·J0/J2·μ-even/net flux residual | directional transport와 energy/angle resolution |
| Paired abundance response | matched FLRW/BI overlay, q_ref=0/±q, Δabundances/ΔT | resolved null shear-effect bound도 유효; 실제 histories 필요 |
| Reionization epochs | local xHII=.1/.5/.9 crossing 및 차이 | crossing 미발생은 null/status; patchy volume QV 아님 |
| Optional electron observables | τsegment, represented visibility | secondary/nonblocking; fixed-time와 redshift endpoint/tail 분리 |
| Convergence/error | time/energy/angle refinement, paired observable residuals | empirical error와 rigorous continuum certificate 구분 |
| Robustness | source/IC variants, error-component ledger | source/IC dependence와 numerical floor를 분리 |

논문은 (1) 질문·conditional model scope, (2) geometry/frame/symmetry와 equations, (3) source/IC/provider와 numerical methods, (4) FLRW/AXBI abundance histories·시간/온도 그림·paired response, (5) convergence·source/IC robustness·geometry validity와 limitations, (6) 재현법·scoped conclusion 순서로 작성한다. methods와 재사용 결과는 AX13에서 지금 작성하고 이후 실제 결과로 채운다. `.tex`, PDF, CSV, 그림 및 exact source/config/commands가 대응해야 한다. scientific HOLD에도 현재 결과와 정밀 결손을 보고한다.

empirical convergence가 필요한 범위를 넘어서 모든 atomic/continuum theorem을 새 global gate로 만들지 않는다. zero/negligible effect도 numerical resolution과 uncertainty로 정량화됐으면 유효한 결과이며 novelty를 강제로 만들지 않는다. baseline 밖 full sky, tilt, spatial QV/21cm, 전체 17-species, CR/HH는 실제 claim이 요구할 때 별도 활성화한다.

## Chunk·실패·재개 controller

기본 preparation chunk는 1800초·24 commands·2 targeted build/test·0 solver다. 미래 scientific run은 node/scenario의 pilot·cases·wall/CPU/RSS·thread·output limits를 먼저 bind한다. 승인 scope 안에서 coordinator가 다음 finite chunk를 자동 갱신할 수 있지만 누적 사용량·실패·기존 11/8 예외를 보존한다. budget reset으로 과거 위반을 지우거나 끝없는 run을 허용하지 않는다.

| 관측 상태 | 최소 행동 | 재개 조건 |
|---|---|---|
| 입력/domain unknown | 하나의 source-backed 결정 또는 supplier task로 실제 해결 | exact field/provider·scope 결정; 임의 zero/guard 확대 없음 |
| 새 seam test failure | 원인에 한 targeted repair와 필요한 regression | 같은 claim/contract이면 계속; 물리 변경이면 decision 갱신 |
| physical run 비수렴/ledger/domain failure | 실패 output 보존, 한 원인 분류·bounded repair | 유효성 실패만 justified scenario revision; fixture relabel 금지 |
| 예상보다 무거운 pilot | wall/CPU/RSS와 independent cases 측정 | NCP64/128 실제 checkpoint/capability 확인 후 finite allocation |
| driver source_identity 변경 | 기존 output 보존, 새 output dir | 이전 source로 compiled resume하지 않음 |
| ready=[]인데 goal 미완료 | unresolved dependency/owner/capability 조사 | 실제 next action 지정; 문서만 새로 만드는 terminal 금지 |
| runtime/context 종료 | STATE/checkpoint에 PAUSED_RESUMABLE·NEXT_ACTION 저장 | exact command/source/config/output로 다음 세션 즉시 재개 |

loop는 `state → critical ready → 실제 수행 → 한 relevant independent review → checkpoint → 다음 ready`다. independent review는 구현자가 아닌 reviewer가 관련 변화와 raw 결과를 한 번 검토하며 실제 결함에 한 bounded repair를 적용한다. historical tests/retained science 전체를 되풀이하거나 archive/durable upload를 매 chunk의 gate로 만들지 않는다. 외부 denial은 우회하지 않고 denied action과 범위 축소/실제 필요한 capability를 기록한다.

GOAL_DONE에는 selected 전체 지원 구간의 실제 FLRW와 q_ref=0/비영 signed AXBI histories, abundance time/T_g figures·paired differences·error·robustness·최종 report, scientific decision, 공개된 재현 산출물이 필요하다. 계획 채택·compiled demo·retained PDF·draft PR만으로는 완료할 수 없다.
