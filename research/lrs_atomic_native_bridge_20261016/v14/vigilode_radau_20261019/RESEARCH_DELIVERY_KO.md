# 독립 LRS V14 — VigilODE native Radau 후속 연구

2026-10-19. Root scientific owner: Astra `/root`. 수치 구현·유한 실행은 별도 하위 모델 agent, 이론과 코드·원시 결과 심사는 두 명의 실제 독립 Astra subagent가 수행했다. Production v3/rux, BASS, atomic, age-reference DAG와 별개다.

## 완료한 결과

**VigilODE의 실제 Radau IIA3를 native photon-moment–chemistry–thermal 결합계에 연결했고, Rust 컴파일과 고유 native 설정 19개를 실제 실행했다. 19개 모두 exit 0, 실패·중단 0개다.** 새 실행 바이너리 SHA256은 `358d254f88d196cd1ada4f71283fa3a69a068bbbf25ae28980af287575106905`다. Rust/cargo 1.94.1, x86_64 Linux sandbox에서 수행했다. 이 결과를 NCP 실행으로 표시하지 않는다.

고정 기하에서 Radau의 주요 관측량은 약 5차에 가까운 유한 refinement를 보였다. 실제 GL2 source birth를 포함한 gas 관측량에는 cancellation 및 혼합된 오차가 있어 단일 전체 차수를 부여하지 않는다. 보존과 endpoint agreement만으로 정확도·강성 일반화를 승인하지 않았다.

| 실제 실행/검증 | 결과와 범위 |
|---|---|
| Native focused tests | 6 PASS: 직접 RHS/사건·에너지, affine 좌표, 실패 transaction, 실제 Radau stage, GL2 clock, 실제 birth parity |
| FD 오류 분류 회귀 | 1 PASS; 물리적 perturbation domain 오류만 단측 차분 허용 |
| 유일 native 이력 | fixed 7 + source-on GL2 6 + seeded-disabled GL2 6 = 19 |
| 실행 원문 | 각 command/source/binary SHA, stdout/stderr, exit, raw JSON 보존·독립 readback |
| 전체 실제 native 비용 | RHS 38,840회, native wall 합 9.146159986초, subprocess wall 합 10.910020730초 |
| Radau accepted chemical segments | 198개, 저장된 accepted/replayed stages 594개 |
| 모든 method의 저장 macro endpoints | 198개; 위 chemical segment 수와 우연히 같으며 별도 계수 |
| 독립 심사 | 이론·native 단위/도메인, 코드·누적 회계를 서로 다른 실제 검토자가 확인 |
| Portable source 복원 | baseline 152개 + transport hook 173 bytes + 새 모듈, VigilODE 477개 hash 확인 |
| NCP | 새 Radau/후속 SSPRK 실행 NOT_RUN; 정상 파일 기반 복사 가능한 인계 포함 |

처음 gate와 수정 후 N4 replay는 **같은 유일 설정**이다. 18개 후속 실행의 추가 비용은 38,068 RHS, 8.979949891초였다. 과거 제조76/Python57 또는 다른 branch의 실행을 새 연구 수량으로 더하지 않았다. Runner의 process-stub 회귀는 실행 제어 검증이며 native 물리 이력이 아니다.

## 1. 연구 전에 새 실행부터 읽은 결과

`INTAKE_SUMMARY_KO.md`와 관련 receipts에 전체 범위를 기록했다. rei_bianchi branch 247개와 PR 205개, VigilODE branch 147개와 PR 71개를 pagination 끝까지 확인했다. 실제 source identity, stdout/stderr, 종료코드, CSV/JSON 원문으로 후속 판단을 했다. REI 관련 원문 13개는 bytes와 Git blob SHA를 대조했다.

PR198은 `fa9615a565a10a770eb1768d8f10cd503b0e1336`에서 시작했다. 기존 원래 V14 NCP compile/표적시험/smoke/84이력은 이미 완료된 상태이며, 후속 SSPRK2의 새 NCP 결과를 관측하지 못했다. BR05, age64/N4, RUN15/16에는 관련 새 자료가 있었지만 별도 과학 lane으로 분류했다. BR05의 실제 exit0 16행, age의 실제 성공과 실패, RUN16의 response/prefix 분석, RUN15의 원시 자료 유실을 서로 바꾸어 해석하지 않았다.

Drive와 Dropbox의 관련 LRS/BASS/age/VigilODE 백업 및 dossier를 읽었다. **Drive RUN15/16의 넓은 상위 폴더 한 곳은 1000개 제한과 pagination API 부재로 부분 목록**이다. 대응 Dropbox와 관측된 관련 파일을 추가 대조했지만 모든 Drive 객체를 완전 조사했다고 쓰지 않는다. 양쪽 과거 보존 상태와 현재 새 보존 상태도 구분했다.

VigilODE PR71 최신 관측 HEAD는 `0bab431e1031f86eb3ddb44371240bce49ae2376`다. 적용한 정확한 수치 source는 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`이고, 최신 게시본의 crates/manifests 461개와 byte-identical함을 확인했다. 회수한 run2 CSV는 2700개 행 중 2639 ok, 54 refused, 7 solver failure다. 원래 host/compiler/stdout/process-exit/reference/timing receipts가 재게시되어 있지 않아 이 자료는 보존 CSV의 관측이며 이번 native 실행을 대신하는 독립 실행 증거가 아니다.

## 2. VigilODE와 Rust 패키지의 실제 적용

이름만 참고한 것이 아니라 pinned source의 `OdeProblem::new`, `radau_step`, `radau_iia3_tableau`, `WorkCounters`와 실제 modified Newton/LU 경로를 컴파일·실행했다. 기존 scalar transport test를 Radau라고 이름 붙이지 않았다.

| 구성요소 | 검토·적용 결정 |
|---|---|
| VigilODE Radau IIA3 | 3-stage coupled native chemical ODE에 실제 적용. 반환 `K_i`로 stages를 재구성 |
| faer 0.24.4 | pinned VigilODE의 pivoted LU backend로 실제 컴파일. 별도 중복 linear-algebra backend 추가 없음 |
| diffsol 0.17.1 | 공식 API/정규화 Cargo manifest 검토. BDF/SDIRK 계열 후보지만 이번의 고정된 Radau 적용과 별도 solver 전환을 동시에 하지 않음 |
| nalgebra 0.35.0 | 작은 고정 크기 gas matrix 표현 가능성 검토. 현재 84D photon+gas 계에서는 기존 faer 경로 유지 |
| ode_solvers 0.6.2 | 공식 공개 solver는 Dopri5/DOP853/RK4 계열; 현재 stiff implicit native 후보로 추가하지 않음 |

Lock에는 yanked `private-gemm-x86` 0.1.20이 포함되어 있었다. 재해결을 유발하는 임의 dependency update 대신 정확한 Cargo.lock을 보존했고 실제 locked/offline release build가 통과했다. Source closure는 477개 파일, 8,339,626 bytes이고, 확인된 crate cache는 101개 archive, 8,165,551 bytes다. NCP runner는 locked fetch를 먼저 마친 뒤 offline locked build를 수행한다. `--offline`과 검증된 local source/cache도 사용할 수 있다.

SciSpace는 관련 문헌 발견에, Exa는 실제 solver 및 공식 Rust API·manifest 조사에, Wolfram은 사건 계수·tableau·stage 양수성 대수 검산에 사용했다. 검색 결과의 abstract나 generic ODE API를 이 native 계의 시간 정확도 증명으로 쓰지 않았다.

## 3. 결합 방정식과 보존의 의미

전체 유도는 `THEORY.md`와 독립 이론 검토서에 있다. Photon node의 수는 photons/total-H이고, proper energy는 일반 ray에서 `r_ray q`다. Source angular weight는 이미 node 수에 포함되어 있다. 각 native stage의 현재 moments를 decode한 뒤 양의 closure quadrature를 다시 구성하고,

\[
\dot N_c=-\sum_{\ell\in c,s}c\,n_{{\rm abs},s}\sigma_s(\epsilon_\ell)n_\ell,
\quad
\dot U_c^{\rm ref}=-\sum_{\ell\in c,s}q_\ell c\,n_{{\rm abs},s}\sigma_s(\epsilon_\ell)n_\ell
\]

를 직접 합산한다. `FE(state,1)-state`나 두 큰 derivative의 차감으로 energy offset RHS를 복원하지 않는다. Photo provider와 native Grackle/Verner/EOS는 기존 코드가 소유한다.

Gas는 `(x_HII,y_HeII,z_HeIII,w)`이고,

\[
Y=\frac{0.2454}{4(1-0.2454)}=\frac{1227}{15092},\qquad e=x+Y(y+2z).
\]

원시 P/C/R/D 사건, binding, photoheat, CE/RR/DR/FF, escape, signed CMB와 expansion work를 분리한다. 실제 native binding 상수를 사용하며 rounded fit threshold로 대체하지 않는다. Chemical stage의 expansion rate는 0으로 넣고 외부 geometry map의 work와 중복하지 않는다.

상태가 affine decoder `Z=Z_*+D theta`로 표현될 때 실제 반환 endpoint closure `rho`, stage residual `r_i`, native point identity `eta_i`를 모두 포함해야 한다.

\[
\rho=\theta_1-\theta_0-\sum_i b_iK_i,\quad
r_i=K_i-hf_i,\quad \eta_i=L\mathcal Df_i+g_i,
\]
\[
\Delta I=L\mathcal D\rho+\sum_i b_iL\mathcal D r_i+h\sum_i b_i\eta_i.
\]

Wolfram과 별도 rational 계수 검산으로 이 구조를 확인했다. Endpoint 항은 실제 비영이며, energy 성분 최대 약7.82e-16 eV/H였다. 이를 포함한 affine mismatch의 최대는 약8.39e-17 eV/H다. 이 항등식은 보존과 nonlinear residual 사이의 관계이지 시간 오차의 상계가 아니다.

**L-stability는 native 모든 stage의 양수성을 보장하지 않는다.** 실제 Radau tableau의 scalar absorption 두 번째 stage는 `tau=h k > 5.14892565376694...`에서 음수가 된다. `tau=10`이면 stages는 약 `(0.319357,-0.0607363,0.0517241)y0`인 반면 endpoint는 양수다. 이 정확한 scalar 반례를 새 native 사례로 세지 않았고, nonlinear 시스템의 보편 CFL 수치로 해석하지 않았다.

## 4. 유한 native 비교와 실제 정확도·비용

모든 설정은 q=0, transport cells=8, native 허용 최소 n_mu=8, threads=1, background_panels=128, 기존 source energy_subdivisions=16, 초기 fractions `(0.075,0.12,0.03)`, T=15000 K다. Seeded case의 MD14 `dt_seed=1e16 s`는 초기 photon packet 제작 weight이며 그 시간을 cosmology가 진화했다는 뜻이 아니다.

고정 기하의 총 시간은 `1/k_ref20`, `k_ref20=1.0778812197739478e-10 s^-1`다. Radau N=2,4,8,16; SSPRK2 N=8,16,32를 실제 실행했다. 아래 `p`는 `log2(|q_N-q_2N|/|q_2N-q_4N|)`의 **유한 관측 비율**이다.

| 고정 기하 관측량 | Radau 연속 두 비율 | SSPRK2 비율 |
|---|---:|---:|
| HII | 4.920 / 4.945 | 2.165 |
| HeII | 4.935 / 4.966 | 2.051 |
| Thermal w | 4.925 / 4.946 | 2.128 |
| Temperature | 4.888 / 4.940 | 2.008 |
| Photon N | 4.920 / 4.945 | 2.164 |
| Photon proper U | 4.921 / 4.945 | 2.157 |

이 고정 geometry의 smooth finite control은 Radau 약5차, SSPRK2 약2차에 가까운 감소를 지지한다. 일반 비선형 native, 임의 강성 또는 전체 source-on 차수를 증명하지 않는다. 고정 HeIII의 마지막 차이도 약1.73e-16에 접근하므로 모든 채널을 일괄 피팅하지 않는다.

가장 미세한 Radau N16을 **경험적 discrete-system reference**로 쓴 고정 geometry 비교는 다음과 같다. 그 reference의 N8→N16 HII 자기차이는 8.688e-10이며 rigorous error bound가 아니다.

| Method | N | HII reference 절대차 | Native RHS | Native wall s |
|---|---:|---:|---:|---:|
| Radau | 2 | 8.380e-7 | 395 | 0.088295 |
| Radau | 4 | 2.763e-8 | 772 | 0.166210 |
| Radau | 8 | 8.688e-10 | 1520 | 0.379202 |
| SSPRK2 | 8 | 7.971e-5 | 104 | 0.037777 |
| SSPRK2 | 16 | 1.806e-5 | 208 | 0.083300 |
| SSPRK2 | 32 | 4.310e-6 | 416 | 0.209908 |

따라서 이 작은 계에서 Radau는 유용한 정확도·비용 대안을 제공했다. 동일 N이면 dense FD/Newton 비용이 더 크다. Radau 전체10설정은 36,276 RHS·8.02747초, SSPRK2 전체9설정은 2,564 RHS·1.11869초다. 서로 다른 N과 정확도를 함께 보아야 하며, 단회 timing·작은84D 계의 결과를 일반 speedup으로 쓰지 않는다. `analysis/NATIVE_REFINEMENT_AND_COST.png`와 PDF/SVG, 전체 endpoint/cost CSV를 제공한다.

Source-on과 seeded-disabled GL2는 각각 `Delta ln a=1e-6`, 두 method 모두 N=4,8,16이다. Source-on Radau photon N/U의 유한 비율은 3.486/4.129로 서로 다르고, gas의 w 비율은1.191, HeII는1.060이다. HeIII의 실제 차이는 `2.0816681711721685e-17`와 `-6.938893903907228e-18`, endpoint 기준 6 ulp와 -2 ulp다. 이를 물리적 시간 차수로 해석하지 않는다. Seeded-disabled Radau의 HII 비율5.099, T비율0.303도 하나의 전체 차수를 지지하지 않는다.

Birth 시간 알고리즘은 기존 native GL2와 같지만 두 wrapper의 endpoint가 최대 한 ulp 다르다. 작은 proper weight에서는 최대 상대차2.33147e-9, 절대차0.6156초이고 source N/U 절대차는 약2.646e-18/H와5.366e-17 eV/H다. **Bitwise-identical forcing이라고 쓰지 않는다.** 이 차이는 현재 미세 채널 해석에 포함하며, 근거 없이 source/clock을 다시 변경하거나 더 큰 campaign을 추가하지 않았다.

## 5. 원시 사건·기체·photon 회계

두 독립 검토자는 energy residual 또는 adapter의 affine audit 값을 입력으로 신뢰하지 않았다. 실제 P/C/R/D, CE/RR/DR/FF/CMB/escape, shared-stage quadrature와 endpoint fractions/w, 모든 photon N/U 배열에서 회계를 재구성했다. 아래는 **초기 상태부터 모든 accepted endpoint까지 누적한 198개 prefix**의 최대 절댓값이다.

| 독립 재구성 | 최대 누적 잔차 |
|---|---:|
| Electron 사건 변화 | 9.591e-17 /H |
| Photo-binding 분해 | 3.212e-17 eV/H |
| Binding 변화 | 1.455e-15 eV/H |
| Escape 분해 | 1.953e-20 eV/H |
| Thermal + gas work | 8.010e-15 eV/H |
| Photon N + absorption − birth | 7.823e-17 /H |
| Proper photon U + photo input + work − birth | 9.260e-16 eV/H |
| Photon + gas + binding 전체 | 8.186e-15 eV/H |

이전 제조 CSV에서 빠졌던 photon energy를 이번에는 실제 raw moment arrays로 재구성할 수 있다. **비영 boundary photon은 아직 검증하지 않았다.** 이 lane의 passive/boundary N/U는0이다.

저장된 Radau stage 594개, photon cell23,400개에서 도메인 위반0을 확인했다. 현재 stage/FD마다 native closure를 다시 구성하고, source-on 최초 layout은 `4→84→84`로 첫 birth 뒤 photon 자유도가 생긴다. 저장하지 않은 모든 Newton trial을 개별 확인했다는 뜻은 아니다. CMB594개는 모두 음수이고 unchanged native analytic 식의 독립 평가와 최대 상대차9.50e-16으로 일치했다. 양의 CMB 가지를 새 native 이력으로 검증했다고 쓰지 않는다.

## 6. 고친 실제 결함과 전달 범위

1. 최초 FD Jacobian은 budget 이외의 오류에도 단측 차분으로 대체할 수 있었다. 지금은 `PerturbationDomain`과 `Fatal`을 분리해, 정상 계산으로 확인된 native 물리 envelope/EOS-temperature 이탈만 fallback을 허용한다. Nonfinite, decode/EOS arithmetic, prepare/provider/shape/resource 오류는 숨기지 않는다. 해당 회귀와 최종 native gate/19설정이 통과했다.
2. 초기 계약의 n_mu=2는 기존 source 허용 집합 `[8,16,32]` 밖이었다. Native RHS0회인 초기화 실패4건을 보존하고 최소 허용값8로 계약을 바로잡았다. Source quadrature implementation을 바꾼 것이 아니다.
3. Portable runner의 실패 후 exit0, 총예산 초과 허용, rustup symlink dispatch 문제를 실제 코드 검토에서 발견해 최소 수정했다. 이 검증은 작은 process-stub 및 source restore 검사이며 기존19 native 이력을 다시 세거나 rerun하지 않았다. 정확한 최종 개수·hash는 runner review와 normal manifest에 있다.

실제 디스크 부족으로 실패한 build도 로그에 보존했다. 자기 소유의 재생 가능한 build cache를 정리했고 과학 source와 결과를 제거하지 않았다. Final numerical source는 matrix 이후 변경0이다. NCP에는 정상 파일을 복원·컴파일하고 실제 실행하는 단계가 남는다.

`prepare_and_run.py`는 sibling SSPRK restore chain을 호출하고 source hashes를 확인한 뒤 새 모듈을 추가한다. VigilODE exact archive를 자동 회수하거나 backup/local closure를 사용한다. 사용자에게 download/SSH/SCP 작업을 요구하지 않는다. Source 복원 fresh-directory 검증과 archive477hash 검증은 실제 PASS다. Portable `--all` 전체를 NCP에서 이미 실행했다고 주장하지 않는다.

## 7. 최종 admission과 다음 작업

**승인: 현재 opt-in adapter의 native 방정식/단위/공통 stage 회계, 선언된19설정의 완료와 유한 정확도·비용 관측, 이 source를 복원·컴파일·실행할 수 있는 정상 코드 전달.**

**HOLD: source-on 전체2차 이상, 일반 nonlinear/native5차, uniform stiff accuracy/positivity, rigorous continuous error certificate, Case B, full EoR, signed Bianchi, 비영 boundary·positive-CMB의 새 native 검증.**

다음 유한 작업은 NCP에서 동일 정상 파일의 실제 compiler/호스트를 기록하고 표적시험과19설정을 실행하여 이 sandbox 결과와 비교하는 것이다. 다른 host의 CSV byte 동일성을 요구하지 않고, 사건 회계·observables·finite differences·실제비용을 비교한다. 원래 완료된84이력 또는 제조76을 다시 연구 수량으로 쌓지 않는다. 구체적인 호환 문제만 수정하고 diff/source SHA와 실패 로그를 보존한다.

단계별 Git commit, Drive/Dropbox object ID, 전체 readback SHA 및 DAG는 `stages/C1_C6_REMOTE_ACK.json`, `stages/FINAL_DELIVERY.json`과 최종 ack에 기록한다. 전체 사용 가능한 인계는 `CODEX_NCP_EXECUTE_KO.md`다.
