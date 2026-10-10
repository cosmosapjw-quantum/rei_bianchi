# 다음 연구 루프: REI-PHYS22_INITIAL_TIME_COUPLED_SHEAR_RESPONSE

PHYS21에서 지정하는 단일 후속 물리 문제다. 이 문서는 PHYS22를 이미 실행했다는 기록이 아니다. PHYS21의 별도 최종 판정은 `independent/DECISION_REVIEW.json`, 게시 commit과 archive identity는 detached publication receipt를 따른다.

## 1. 바로 이어갈 질문

실제 paired initial state와 PHYS21의 scalar 2차 radiation forcing을 사용해, **coupled ionization 및 temperature response의 초기시간 첫 비영차 계수**를 구하라. Gas IVP 없이 local asymptotic expansion을 사용한다. Initial cohort와 continuous birth source의 시간 차수를 구분하고, 총 입자수 변화와 He의 간접 반응을 유지하라.

출발 가설은 initial cohort의 direct geometric forcing이 `O(shear^2 t^2)`, 그에 따른 gas response가 `O(shear^2 t^3)`이며 continuous-birth contribution은 한 차수 늦는다는 것이다. 이 차수·계수·부호는 **PHYS22가 검증할 대상**이다. 이 handoff를 확정된 asymptotic coefficient로 인용하지 말 것.

## 2. 입력 identity와 읽는 순서

저장소 `cosmosapjw-quantum/rei_bianchi`, 브랜치 `forward/rust-reion-kernels-20260922`, [기존 draft PR83](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/83).

- PHYS21 input commit: `faec51259ed26f660cf14568bcaa3d288e54bf9a`.
- 그 root tree: `d4c734ac2047e68966ccecc81da79eb68420f8a1`.
- Scientific Rust src tree: `cb69b4736dd046e4675557577eb8e0ead037d1f3`.
- PHYS21 integrated report SHA256: `59fca954d998f9ffd5af2ed857ae15992f24c9779a77e9c7ba099d058990ab7a`.
- Canonical Astra harness: `physmath-research-harness-gpt6-astra-v4.0.0-20260908.zip`, SHA256 `dae76c90f2e5d691bcdd595dadbe470bacacba3bb2a036ff9788ffe7d3bfabb7`.

최소 읽기 순서는 이 handoff → `PHYS21_REPORT_KO.md` §§2–4, 8–10 → `RESULTS_SUMMARY.json` → `independent/DECISION_REVIEW.json` → `contributions/source_gas/GAS_RESPONSE_FUNCTIONAL.json`이다. 국소 반응식을 구현할 때에만 `SOURCE_GAS_NOTE_KO.md` SG17–SG22와 pinned source를 읽는다. Tensor 유도는 불확실한 항이 있을 때 해당 식만 확인한다.

PHYS21 publication은 입력 commit 뒤 같은 branch의 additive docs commit이다. 실제 published head는 detached receipt에서 읽고 다음 시작 시 source identity만 필요한 범위에서 확인한다. Source subtree가 같다면 PHYS20/21에서 닫힌 과학 결과를 다시 실행하지 않는다. 현재 archive에는 7개 materialized Rust source와 source identity, 결과 JSON, 코드, 별도 판정이 포함된다.

## 3. 고정하는 convention과 실제 입력

`F_epsilon = F0 + epsilon F1 + epsilon^2 F2 + o(epsilon^2)`이며 `F2=(1/2) second derivative`. Metric signature `(-,+,+,+)`, proper time [s], energy [eV], thermal state `w` [eV/H].

`a_i=a exp(epsilon B_i)`, `sum B_i=0`, fixed principal axes. Mean `H`, `n_H(t)`, scalar initial state와 source amplitude/spectrum은 epsilon-independent prescribed quantities다. Einstein-backreacted mean expansion은 별도 문제다.

실제 초기조건:

- `H=1e-14 s^-1`; shear는 실제 binary64 `((1.01e-14)-(0.99e-14))/2`, 대략 `1e-16 s^-1`.
- `B(t)=shear*t*diag(1,-1,0)`.
- `n_H(t)=1e-4 exp(-3 H t) cm^-3`, `f_He=0.083`.
- `(x_HII,x_HeII,x_HeIII,T)=(0.9,0.3,0.6,50000 K)`.
- Initial cohort `0.05 photons/H`, birth energy `13.7 eV`.
- Constant source `S=5e-15 photons/H/s`, birth energy `13.7 eV`.
- `chi_HI=13.598434599702 eV`; HI opacity cutoff `13.60 eV`와 구분한다.
- Thermal conversion `eV_erg=1.602176634e-12`, `k_B=1.380649e-16`.

Generic FT03 fixture의 [20,35,70] eV photons를 paired initial 대신 사용하지 않는다. Per-H photon count에 `-3HN`을 더하지 않는다. `coupled_primary::raw`는 zero-photon nonphoto RHS 뒤 primary photo/heating을 한 번 추가한다. RR/DR emission은 escaped ledger로 간다.

## 4. PHYS21에서 닫힌 구조

Physical birth angle `m`에서 `A_s=B(s)-B(b)`, `E0(s)=Eb a(b)/a(s)`, `R_s=(sum m_i^2 exp(-2 epsilon A_si))^(1/2)`. Birth-angle 평균에는 `J_b`를 더하지 않는다. Fixed-q 계산이면 coordinate energy와 `J_b`를 함께 사용한다.

`D=E d/dE`, `lambda=sum c n_j sigma_j`, `P0=exp(-integral lambda0 ds)`, `M=integral (D lambda0) A_s ds`, `V=integral [(D^2+3D)lambda0] tr(A_s^2) ds`일 때

\[
K_{\phi,2}=\frac{P_0}{15}\left[
((D^2+3D)L_{\phi,0})\operatorname{tr}A_t^2
-2(DL_{\phi,0})\operatorname{tr}(A_tM)
+L_{\phi,0}\operatorname{tr}M^2-L_{\phi,0}V\right].
\]

이것은 epsilon² coefficient다. `L=1,E,c n_H sigma_j,lambda_j,sum lambda_j(E-chi_j)`가 각각 count, energy, Gamma, event, heat다. 전체 forcing은 초기 atom과 연속 source measure에 cohort 계수를 적분한다. 일반 `y0(s)`는 시간에 따라 진화하며 epsilon 미분 동안만 고정한다.

`y=(x,h1,h2,w)`, `eta=[epsilon^2]y`, `Pi=1+f+x+f(h1+2h2)`일 때

\[
\eta_T=T_0\left(\frac{\eta_w}{w_0}
-\frac{\eta_x+f(\eta_{h1}+2\eta_{h2})}{\Pi_0}\right).
\]

\[
D_yR_\phi[\eta]=\int d\mu P_0\left[L_{\phi,y}\eta(t)
-L_{\phi,0}\int_b^t\lambda_y\eta(s)ds\right],
\quad
\dot\eta=J_{\rm np}\eta+\mathsf B D_y\mathbf R[\eta]+\mathsf B\mathbf r,
\quad\eta(0)=0.
\]

`R=(A_HI,A_HeI,A_HeII,Q)`, injection matrix의 rows는 `(1,0,0,0)`, `(0,1/f,-1/f,0)`, `(0,0,1/f,0)`, `(0,0,0,1)`이다. `A_j`를 사용하면 endpoint abundance를 중복해서 미분하지 않는다. `Gamma_j`를 사용하면 `A_j,2=ell_j,0 Gamma_j,2+ell_j,2 Gamma_j,0`가 필요하다. `y1=0`이므로 `gas Hessian[y1,y1]`는 없다.

고정 gas inverse-cube opacity에서는 mean optical depth가 보존되고 cumulative absorption은 감소한다. 순간 absorption/heating 부호는 optical depth에 따라 달라질 수 있다. PHYS21의 frozen-neutral-fraction HI cohort 결과를 actual evolving-gas 또는 temperature coefficient로 사용하지 않는다.

## 5. 최소 실행 설계

1. PHYS21 판정과 convention을 읽고 초기시간 확장의 정확한 성공 기준을 고정한다. Physical shear amplitude와 formal epsilon을 구분한다.
2. 실제 initial spectrum과 local source를 사용해 각 geometry forcing의 첫 nonzero time coefficient를 유도한다. Birth integration의 lower limit 및 initial delta measure를 분리한다.
3. 식 (32)의 local/memory/forcing 항이 어느 시간 차수부터 기여하는지 판정한다. 필요한 차수의 baseline derivative만 실제 local RHS에서 계산한다. 임의의 frozen-neutral approximation으로 actual local coefficient를 바꾸지 않는다.
4. H/He fractions, `w`, `T`에 대해 첫 계수를 구하고 차원·particle count·photo/nonphoto 소유권·count/energy ledger와 확인한다. He direct photo forcing의 부재와 간접 response를 구분한다.
5. 새 주장에 한정한 작은 independent analytic/algebraic 검산을 한 번 설계한다. 필요하면 높은 정밀도의 작은 kernel 계산을 사용하되 gas IVP는 실행하지 않는다.
6. 별도 final reviewer가 후보/검산 설계에 참여하지 않은 상태에서 scope와 수치 근거를 판정한다. 보고서, 결과 JSON, DAG, 다음 handoff를 남긴 뒤 멈춘다.

Time asymptotics가 cutoff/C2 경계나 scalar differentiability 가정에 걸리면 해당 항의 claim ceiling을 낮추고 구체적인 조건을 기록한다. 허용 오차 완화로 결과를 통과시키지 않는다. 실제 초기 coefficient를 닫는 데 전체 dense baseline이 필요하지 않다면 archive 탐색을 반복하지 않는다.

## 6. 재실행·권한·종료선

PHYS21 actual checks는 HI 39/39, tensor 44/44, local gas 60/60으로 모두 exit 0이다. Source/gas v1도 처음부터 통과했고, DR 상수 연산 순서만 source에 맞게 수정해 같은 step/tolerance로 재검사했다. V1 evidence를 보존했다. 이 수정은 runtime failure가 아니다.

PHYS21 archive bytes가 의심되면 `reproduce.py --verify-only`를 우선 사용한다. `--output-dir`의 전체 작은 diagnostic replay는 portability 필요가 있을 때만 사용하며 closed science의 기본 시작 절차로 반복하지 않는다. Remote ACK/tree/blob identity와 fresh local restore는 서로 다른 evidence다.

`physical=HOLD`, `[160,161] FAIL`, `tick160`, auxiliary escape `FAIL`, HH/RCT/CR `OFF`, precision atomic `PARKED`를 유지한다. Native history, new gas IVP, firstmacro 8/16/32 campaign, full raw, NCP, old PHYS19/20/21 proof replay, 다른 atomic lane, source/default/runtime returns mutation은 이 후속 이론 루프 범위에 없다.

세션에서 이미 허용된 같은 branch의 additive docs publication은 nonforce CAS로 이어갈 수 있다. 기존 파일을 덮어쓰지 않고 새 PHYS22 docs 경로를 사용한다. Merge는 하지 않는다. 새 수학/물리 결과와 검산이 완료되면 artifact와 최소 metadata를 저장하고, 후속 문제 하나를 정한 뒤 루프를 종료한다.
