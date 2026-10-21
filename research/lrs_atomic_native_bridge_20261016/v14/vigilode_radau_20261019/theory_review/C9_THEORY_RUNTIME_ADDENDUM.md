# C9 독립 물리·수학·원자료 검토 추가 기록

작성자: `/root/drive_v15_intake`, 실제 독립 Astra subagent. 다른 모델의 심사로 표현하지 않는다. 이 추가 검토는 기존 `INDEPENDENT_THEORY_REVIEW.md`와 그 정확 대수 검산을 재사용한다. native 실행 0회, 과학 소스 수정 0건, 외부 게시·업로드 0건이다. 실행과 결과 생성은 coder, 최종 연구 판정·게시·백업은 root 소유다.

## 판정과 검토 범위

최종 소스에서 각 chemical segment가 실제 현재 photon moments와 gas로 새 affine 좌표·Context를 만들고, 매 RHS와 FD 평가 및 수렴 stage 재생 때 native moment closure를 다시 구성함을 확인했다. 실제 19개 유한 이력 모두 원본 receipt, 입력, stdout, stderr, 종료코드, raw JSON, 소스 archive와 연결했다. 저장된 Radau stage의 단위·stoichiometry·공통 사건 구적·허용영역에서 미해결 구현 결함은 관측하지 않았다. **이 소스와 이 유한 자료를 좁은 native discrete-system 비교 근거로 받아들일 수 있다.** 전 구간 시간 차수·강성 양수성·우주론 이력의 일반적 정확도를 승인하는 판정은 아니다.

검토 대상은 `v16_work/implementation/src/{lib.rs,main.rs}`, focused tests, appended native child `axbi_native_rhs.rs`, 기존 native transport/thermal/EOS/provider, 실제 path dependency의 Radau/Newton/problem 원본이다. 실행별 원자료 경로와 SHA-256은 `C9_RUNTIME_CROSSCHECK.json`에 저장했다. 동일 폴더의 `c9_readonly_crosscheck.py`는 저장된 JSON/receipt만 읽으며 native 프로그램을 호출하지 않는다.

## 1. 실제 소스와 실행의 연결

19개 case 각각에서 다음을 직접 확인했다.

- `exit_code=0`, `truncated=false`, raw `completed=true`, `failure=null`, 저장 record 수 = 요청 N.
- stdout는 실제 빈 파일이며, stderr에는 마지막 `COMPLETE native_rhs=...`가 있다. 완료 판단은 stdout의 빈 상태가 아니라 이 전체 증거에 따른다. stdout/stderr 전체 bytes의 SHA도 outcome과 일치한다.
- `sources.tar.gz` 전체 SHA가 해당 inputs의 archive SHA와 일치한다. 각 archive 내부의 검토 대상 11개 파일 bytes는 inputs의 파일 SHA 및 현재 검토 소스와 일치한다.
- 실제 executable SHA는 `358d254f88d196cd1ada4f71283fa3a69a068bbbf25ae28980af287575106905`이며, 19개 inputs 및 matrix receipt와 모두 일치한다.
- 기준 manifest에 있던 152개 파일은 원래 bytes를 보존한다. transport는 appended module seam 이전의 전체 원본 prefix를 따로 hash해 비교했다. 실제 빌드에 쓰인 `native_source_closure`의 `radau.rs`, `nonlinear.rs`, `problem.rs`는 앞선 이론 검토의 immutable `8a8bd409b1d96c7b7421f496d229e119fd3d284e` 파일과 byte-identical이다.

현재 adapter `lib.rs` SHA는 `90a55821c585c0314484053b2efecc9a255e5ef1c5b80732e9c97796c6251f13`, native child SHA는 `56b88341c5d87c8a1f9a44f3bb364fcf13cefd424b5937e47693c787563480f2`다. 원래 PR198 HEAD `fa9615a565a10a770eb1768d8f10cd503b0e1336`와 source publication `339dab4336d1fcfd38106640ee9bf7056dabcfd8`는 기준선이며, 이 새 소스의 게시 성공은 별도 root receipt로 판단한다.

기록된 19개 이력은 fixed 7개, source-on GL2 6개, seeded-disabled GL2 6개다. 최종 소스 N4 재생을 한 번 재사용했고, 오래된 N4 gate를 현재 matrix의 실행으로 세지 않았다. 총 native RHS **attempt** 표기는 38,840이다. FD admissibility를 포함한 charge 수와 실제 native provider 호출 수가 항상 같은 개념은 아니므로 이 명칭을 유지한다. 이 검토는 NCP 실행을 주장하지 않는다.

## 2. Birth 뒤 좌표를 새로 만드는 실제 경로

`birth_step`은 각 stop에 대해 다음을 수행한다: `geometry_map(midpoint)` → `chemical_step` → `geometry_map(end)` → 실제 end에서 source injection. `chemical_step` 내부에서 `Coordinates::new(&photon(s), &s.gas)`를 호출한다. 따라서 다음 stop의 좌표와 template은 직전 birth로 바뀐 moments/support를 포함한다. 이전 segment의 빈-cell 제외 목록을 macrostep 전체에 고정하지 않는다.

source-on N4, N8, N16의 첫 macrostep에서 실제 dimension은 모두 **[4, 84, 84]**였다. 첫 segment의 세 stage에는 photon node가 0개이고 P/photo heat/photo binding도 0이다. 첫 birth 이후의 두 segment에는 stage당 node가 704개다. 여기서 84 = gas 4 + 점유된 extended-support cell 40 × moment 2다. seeded-disabled 첫 세 segment는 모두 dimension 84다.

Radau stiff accuracy로 raw 마지막 stage와 stage increments에서 segment의 시작 좌표를 역산했다. 198개 chemical segment의 시작 w 좌표와 7,800개 점유 cell 시작 N 좌표는 1과 최대 `2.23e-16` 차였다. Birth 직후 새 layout 112개 연결에서 총 N 변화와 기록된 source N, 그리고 총 Uref 변화와 `added_u × a_birth/a_ref`를 대조했다. 기존 inventory로 정규화한 최대 차는 각각 `6.66e-16`, `4.32e-16`였다. 이 역산은 저장된 stiffly accurate stage에 의존하므로 endpoint 합산 반올림을 측정 오차에 남긴다.

좌표를 새로 만드는 작업은 고정된 순간 RHS의 단순한 affine 재표현이다. 예전 `A exp(hL) R` map처럼 각 segment의 유한 진화를 spectrum에서 시작해 투영하는 시간적분 대체가 아니다. 각 native 평가에서 현재 decode → photon validate → `transport.prepare(current_state,current_geometry)` → direct node RHS → `AxbiProvider.point`를 수행한다.

## 3. 물리 단위와 사건·열 소유권

node number는 total-H당 photon 수다. reference node energy q의 proper energy는 `ray.scale × q`이다. 이번 q=0 이력에서는 `ray.scale=a_ref/a`; 일반적으로 q/a라고 바꾸면 안 된다. angular weight는 source가 이미 node number에 반영하며 RHS에서 중복 곱하지 않는다.

native child는 species j별로

\[
\Gamma_j=c\,n_H\sum_n\sigma_j(\epsilon_n)N_n,
\qquad P_j=c\,n_{\mathrm{abs},j}\sum_n\sigma_j(\epsilon_n)N_n
\]

를 계산한다. 첫 식은 absorber당 초당 photo rate, 둘째는 total-H당 초당 사건 수다. 그러므로 unchanged provider가 만드는 `photo_events_cm3_s/n_H`와 direct-node P가 같다. 열 입력은 absorber당 erg/s이며, `(epsilon-chi)`와 eV→erg 변환을 한 번만 곱한다. native `energy_offset_dt`는 `-(q-lo) × event`를 노드에서 직접 누적하여 큰 `Uref_dot-lo*Ndot` 차감 손실을 피한다.

원자료 검산은 gas fraction 도함수, photon moment 도함수를 저장된 `K_i - r_i = h f_i`로 회수했다. native 함수를 다시 실행한 독립 RHS라 주장하지 않는다. 별도의 사건·열 식으로 다음을 확인했다. 모든 P/C/R/D는 total-H/s, 열 항은 eV/H/s다.

\[
\begin{aligned}
\dot x&=P_H+C_H-R_H,\\
Y\dot y&=P_{HeI}+C_{HeI}-R_{HeI}-D-(P_{HeII}+C_{HeII}-R_{HeII}),\\
Y\dot z&=P_{HeII}+C_{HeII}-R_{HeII},\\
\dot e&=\sum_j(P_j+C_j-R_j)-D,\\
\dot w&=Q_{photoheat}-\sum_j\chi_j C_j-Q_{rad}+Q_{CMB},\\
\dot E_{escape}&=\sum_j\chi_jR_j+\chi_{HeI}D+Q_{rad},\\
\dot N_\gamma&=-\sum_jP_j,\qquad
\dot E_\gamma=-Q_{photoheat}-\sum_j\chi_jP_j.
\end{aligned}
\]

여기서 `Q_rad=sum(CE)+sum(RRkin)+DRkin+FF`이고 `Y=.2454/[4(1-.2454)]`다. CI binding sink는 escape에 다시 넣지 않는다. chemical provider에 전달한 H는 0이다. 팽창 work는 기존 geometry map이 담당하므로 chemical RHS에 중복 삽입하지 않는다. CI floor, CE cap, excluded DR는 native diagnostic이며 별도의 추가 반응이 아니다.

| 저장 원자료 대조 | 대상 수 | 최대 오차 |
|---|---:|---:|
| Photon P species 대 native P | 1,782 | 상대 `3.87e-15` |
| Photo binding 대 node binding | 594 | 상대 `4.28e-15` |
| Photo heat 대 node heat | 594 | 상대 `4.77e-15` |
| Escape 소유권 | 594 | 상대 `4.82e-16` |
| Thermal RHS의 위 식 | 594 | 항들의 L1 크기로 정규화 `1.31e-15` |
| Photon number/proper energy RHS | 각각 594 | 정규화 `2.36e-15` / `2.24e-15` |
| 같은 stage 가중치로 누적한 모든 사건·진단 scalar | 5,346 | 상대 `2.22e-16` |

세 stage의 b는 실제 Radau tableau의 양의 값이고, ledger는 모두 동일 accepted dt와 b로 누적된다. state를 commit하기 전에 stage 재생, endpoint validation, invariant validation이 성공해야 한다. 실패하면 physical state와 ledgers는 이전 값으로 남고 시도와 호출 비용만 기록한다. 양의 b만으로 Radau stage의 양수성을 증명할 수는 없다.

## 4. 실제 stage 허용영역과 signed CMB

198개 chemical segment의 **594개 저장된 accepted/replayed Radau stage**를 전부 읽었다. fraction simplex, 양의 w, EOS T 범위, 점유 N>0 및 extended cell offset cone `0<=v<=u`를 직접 확인했다. 23,400개 photon cell-stage 검사에서 허용영역 위반은 0이었다. T 범위는 `14998.873727070904 .. 15484.487126243159 K`다. 9개 stage는 빈 photon layout이고, 나머지는 extended support다. point-cell 이력은 이 matrix에 없다.

CMB는 594개 모두 음수였다. 저장된 fraction과 w에서 T와 e를 독립적으로 복원하여 unchanged native의 Thomson 식

\[
Q_{CMB}={4\sigma_T a_{rad}k_B\over m_ec\,\mathrm{eV}_{erg}}
\,e\,T_{CMB}^4(T_{CMB}-T),\quad T_{CMB}=2.7255/a
\]

을 Python에서 다시 계산했다. 최대 상대 차는 `9.50e-16`, 절대 차는 `9.86e-31 eV/H/s`였다. raw 음수값이 강제로 0으로 바뀌지 않았음을 확인한다. 이번 hot-gas 이력은 CMB의 음의 가지에 대한 실제 증거이며, 양의 CMB나 signed Bianchi 이력의 증거로 확장하지 않는다.

저장되지 않은 모든 Newton/FD trial state를 원자료에서 보았다는 주장은 하지 않는다. 소스는 domain을 검사하고, 최종 typed FD는 명시된 perturbation-domain error일 때만 one-sided fallback을 허용한다. arithmetic/reconstruction/provider/cap error는 fatal이다. `classified_focused`의 실제 stdout/outcome은 관련 internal test 1개와 integration test 6개, 합계 7 PASS를 보존한다. 검토자가 이를 재실행하지 않았다.

## 5. 비선형 stage 잔차와 보존 잔차의 구별

affine decoder `Z=Z*+D theta`, stage residual `r_i=K_i-h f_i`, endpoint residual `rho=theta_new-theta_0-sum b_i K_i`에 대해 기존 독립 유도의 필수 항은

\[
\Delta I=L D\rho+\sum_i b_iL D r_i+h\sum_i b_i\eta_i
\]

다. 여기에 실제 decode·합산·불변량 평가의 floating error가 더해진다. 최종 코드는 이 세 항을 모두 따로 저장한다. physical endpoint energy 항은 최대 `7.82e-16 eV/H`로 0이 아니므로 지울 근거가 없다. 마지막 identity mismatch의 energy 성분 최대값은 `8.39e-17 eV/H`였다.

전체 chemical report에서 max scaled stage residual은 `0.05509481759702339`, library WRMS는 `0.01081688600280145`, max scaled endpoint closure는 `0.002448128505472269`였다. scaling은 이 실행에서 atol `1e-13`, rtol 0이다. WRMS 수렴·순간 보존 항등식·실제 시간 정확도는 서로 다른 판정이다. 작은 보존 오차로 시간 차수를 판정하지 않는다.

## 6. GL2 clock의 실제 일치 범위

두 method는 같은 chronological GL2 nodes와 `Delta ln(a) × weight / H(a_birth)` recipe를 쓴다. source를 disabled해도 같은 stop 구조를 유지한다. 다만 Radau wrapper는 목표 a를 직접 받고, 기존 SSPRK wrapper는 전달받은 dln(a)로 목표 a를 다시 만든다. source-on/disabled의 112개 matched birth에서 최대 시각 차는 `6.938893903907228e-18`(약 1 ulp)였다. 매우 작은 dln(a)의 차감·재구성 때문에 다음 최대 차도 실제로 있다.

- proper weight: 절대 `0.6156129837036133 s`, 상대 `2.3314668814e-9`.
- source N: 절대 `2.645933231056034e-18 photon/H`.
- source U: 절대 `5.365053086605045e-17 eV/H`.

그러므로 동일한 clock recipe와 유한 정밀도 내 matched forcing이라고 서술할 수 있지만 bitwise-identical forcing이라고 쓰면 안 된다. 현재 유한 이력에서 상대적으로 아주 작은 forcing 차이지만 cancellation에 민감한 성분의 오차 분석에서는 보존해야 한다. 이는 현재 증거에서 추가 source 수정이나 실행 행렬 확대를 요구하는 결함으로 판정하지 않는다.

## 7. 물리·시간 정확도에 남는 한계

이번 initial fractions/T와 `seed_dt_s=1e16`의 MD14 packet은 초기값 제작이다. 그 1e16초의 실제 gas/photon 진화를 계산한 적이 없다. 별도 source-on은 빈 photons에서 시작한다. matrix는 n_mu 8, transport cells 8, q=0, source energy subdivisions 16, background panels 128, 단일 thread, 짧은 Xend `1e-6` 또는 fixed 시간 `1/k_ref20`다. 초기값을 만든 프로그램의 이름이나 라이브러리 함수명을 우주론 이력의 검증으로 바꾸지 않는다.

Radau의 formal order 5는 충분히 매끄러운 고정 geometry의 reconstructed-moment coupled ODE와 정확한 stage 풀이에 대한 이론적 성질이다. stage마다 현재 F를 쓰는 최종 코드는 이 경로를 구현한다. native closure의 quadrature panel 변경·endpoint/asymptotic 분기·유한 FD와 Newton 오차를 포함한 전 영역 오차 경계는 증명되지 않았다. source quadrature가 GL2라는 사실도 전체 geometry/source-coupled 이력의 4차 또는 5차를 뜻하지 않는다. 실제 refinement와 HeIII cancellation에 대한 수치 판정은 root의 별도 raw audit 소유이며 여기서 같은 campaign을 다시 만들지 않았다.

이전 정확 Radau 대수 검산의 반례를 유지한다: scalar decay의 endpoint는 양수여도 내부 stage 2는 `h*k > 5.1489256537...`에서 음수가 될 수 있다. 이번 유한 stage들의 양수성은 이 no-go를 반박하지 않는다. 또한 native-domain trial error를 받은 pinned Newton은 즉시 실패할 수 있다. admissible 정확 해가 있다고 해서 현재 globalization이 항상 그 해를 찾는다는 보장도 없다.

Case A native escape, clumping 1, primary photo input의 원래 ownership을 유지한다. Case B, diffuse reemission, `inactive_hi_split` passive boundary, full EoR, uniform stiff, signed Bianchi를 승인하지 않는다. 이번 matrix의 빈-photon segment는 zero-opacity matrix의 대체가 아니며, point support는 기존 focused roundtrip 증거까지만 인정한다. 어떤 양수성/보존 결과도 과거 stiff 생존량 상대오차 100% 반례를 삭제하지 않는다.

**C9 결과:** 현재 최종 소스와 19개 raw 이력에 대한 한정 물리·수학·저장 stage 검토 완료. 위 한계를 유지하면 미해결 blocker 없음. 외부 게시·백업·NCP 상태는 해당 책임자의 실제 receipt를 따로 결합해야 한다.
