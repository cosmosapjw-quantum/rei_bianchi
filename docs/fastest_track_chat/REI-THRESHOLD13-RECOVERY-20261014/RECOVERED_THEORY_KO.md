# RUX-BI-THRESHOLD13: 복구한 이론 본문

복구일 2026-10-14 KST. 직전 ChatGPT 응답의 수식과 설명을 현재 파일로 재구성했다. 이전 실행은 ChatGPT container/Python ClientError로 PDF/ZIP을 생성하지 못했다고 보고했다. 이 파일은 새로운 복구 판본이며, 없던 원본 ZIP/원시 CAS 출력의 byte-restoration이 아니다. 이전 대화에 보고된 계산 횟수와 수치는 historical transcript evidence로만 유지한다. 새 독립 심사 또는 production 승격은 없다.

게시 전 확인한 PR83은 open/draft/unmerged, head 84ee71a26949c6d5216542a49a5f6258cf7a4a95, branch forward/rust-reion-kernels-20260922였다. AGENTS.md 조회는 이 head에서 404였다. 생산 source, PR 본문, 기존 실패/승격 상태는 변경하지 않는다. SHEAR12의 실제 보존 archive는 SHA256 3b275b00a9542f34a1e4075c7eb1ab8f7248a63e65226d4be40756a5789b2ce9, 776788 bytes, Drive id 1R6fFT4xTlCSqCNduCCMUI4EWeSdCDBfp 이다.

## 1. 대상과 convention

계량 ds²=-c²dt²+a(t)² sum_i exp(2 epsilon B_i(t)) dx_i², sum B_i=0. 모든 비교는 같은 mean a(t), 물질 IC와 physical source를 사용한다. 유한 양의 photon quadrature에 결합된 H/He, 열, 누적 관측량 ODE를 다룬다. 가지별 RHS는 C³, 유한 번의 문턱 횡단은 transverse이며 endpoint와 분리된다. Fit 활성 문턱 b_a와 결합 에너지 chi_a는 구별한다. State는 연속이며 vector field만 바뀐다.

유도 convention: z=partial_epsilon y, w=partial_epsilon² y. SHEAR12의 계수 y2는 w/2이다.

## 2. 기하학적 문턱 시각

광자 E=q/a sqrt(sum omega_i² exp(-2 epsilon B_i)). g=log(E/b_a)=0이 사건이며 상태 y에는 의존하지 않는다. t_e'=a_e, t_e''=b_e. 일반 암시적 미분식은

    a_e=-g_epsilon/g_t,
    b_e=-(g_epsilonepsilon+2 g_tepsilon a_e+g_tt a_e²)/g_t.

기준 epsilon=0에서 b_omega=B:omega omega, c_omega=B²:omega omega, s_omega=dot B:omega omega이면

    a_e=-b_omega/H,
    b_e=[2(c_omega-b_omega²)-2s_omega a_e-dot H a_e²]/H.

두 시각 미분은 시간 단위다. Transversality |g_t|>0가 필요하다. 고정 에너지 photon의 기체 opacity가 바뀌어도 주어진 geometry의 crossing time은 같은 사건식에서 정해진다.

## 3. 가지별 변분과 접합

F^-,F^+를 사건 양쪽 vector field, J=F_y라 두면 가지 내부에서

    z'=Jz+F_epsilon,
    w'=Jw+F_yy[z,z]+2F_yepsilon z+F_epsilonepsilon.

이때 실제 온도, 조성, source, photon state 의존성을 미분한다.

연속 상태 y^-(t_e(epsilon),epsilon)=y^+(t_e(epsilon),epsilon)의 연쇄법칙으로

    z^+=z^-+(F^--F^+)a_e,

    w^+=w^-+2(J^-z^--J^+z^++F_epsilon^--F_epsilon^+)a_e
         +(F_t^-+J^-F^--F_t^+-J^+F^+)a_e²
         +(F^--F^+)b_e.

증명: 사건 위치의 2차 미분은 w+2(Jz+F_epsilon)a_e+(F_t+JF)a_e²+F b_e 이며 이를 양쪽에서 맞춘다. 일반 saltation/second-order hybrid sensitivity는 선행 구조다. 현재 결과는 identity reset과 주어진 Bianchi energy threshold에 대한 특수화이다.

## 4. 광학깊이의 2차 표면항

kappa_T=c sigma_T n_H, C'=kappa_T xi_e. xi_e는 물리적으로 연속하므로 z_C jump는 0이다. 하지만 2차에는

    [w_C]_e=-kappa_T(t_e) Delta F_xi,e a_e²,
    Delta F_xi,e=F_xi^- - F_xi^+.

일반적인 연속 관측률 C'=G(t,y,epsilon)에는 [w_C]_e=-G_y(F^--F^+)a_e².

고립된 사건의 distributional parameter derivative를 쓰면

    partial_epsilon² y=w_regular-[z]_e a_e delta(t-t_e),

따라서 optical-depth coefficient는

    C2=(1/2) integral kappa_T w_xi,regular dt
       -(1/2) sum_e kappa_T(t_e) Delta F_xi,e a_e².

구현은 delta를 grid에 넣는 대신 누적 C를 state에 넣고 위 jump를 적용할 수 있다.

동일 사건 벡터는 photon -1, electron +1, binding +chi, thermal +(b-chi)를 가져 photon+electron 및 에너지 보존을 만족한다. 에너지 invariant가 epsilon에 명시적으로 의존하면 I_y w+2 I_epsilon,y z+I_epsilonepsilon까지 포함한다.

## 5. 사건 residual과 adjoint

z'=Jz+f, event jump b_e인 선형 응답계와 근사에 대해 lambda'=-J^T lambda를 사용한다. 현재 기하학적 사건의 homogeneous state map은 identity이므로 lambda는 event에서 연속이다. r=z_hat'-J z_hat-f, d_e=[z_hat]_e-b_e이면

    delta O=lambda(t0)^T delta z(t0)-integral lambda^T r dt-sum lambda(t_e)^T d_e.

시간에 따른 Thomson weight에는 W_T(s)=integral_s^T kappa_T(t)dt를 사용한다. 각 step에서 전역 종료시각 weight를 reset하지 않는다. 이는 BASS_HE THEORY11의 signed electron-event correction을 변하는 density로 연결하는 구조적 재사용이며 그 warm source의 수치 상수는 재사용하지 않는다.

## 6. 동시 angular cohort

기준점에서 같은 시각의 events가 epsilon 부호에 따라 다른 순서로 갈라지면 각 순서를 실제 event-time 전개로 정한다. 사건 위치에 맞춘 state의 미분을 eta,xi라 하고 이웃 사건 사이 d=t_b'-t_a', e=t_b''-t_a''라 두면

    eta_b=eta_a+F d,
    xi_b=xi_a+F e+2d(J eta_a+F_epsilon+F_t t_a')+d²(F_t+JF).

증명은 짧은 flow y(t+Delta)=y+Delta F+(Delta²/2)(F_t+JF)+O(Delta³)의 연쇄법칙이다. 각 부호의 순서를 따라 합성하면 one-sided second response를 구성한다. 양쪽이 일치하는 관측량만 공통 2차 coefficient로 읽는다.

## 7. 이전 응답이 보고한 판별값

아래는 이전 ChatGPT 본문의 기록이다. 원 입력/원출력을 이 복구에서 확보한 것은 아니며, 새로 재실행한 결과로 세지 않는다.

수소 exact clock witness: H t*=1/5, S1 t*=3/10, k(t)t*=exp(-3 t/(5t*)), h0=.1, N0=.4, log(E_initial/b)=1/5, endpoint 2t*. Event t_e/t*=(1/5)/(1/5+3epsilon/10). 기준 te/t*=1, te'/t*=-1.5, te''/t*=4.5.

Reported values: h_final=.280410343005030, C0=.268000813381914, h1=-.130080249917943, h2=.086298567599900, C1=-.053683560702682, C2=-.017927117719626. C2 surface=-.053542166085740; omission gives +.035615048366114. C=integral k h dt; physical tau=(sigma_T/sigma_*)C.

Three-axis witness: S_i t*=(.3,-.2,-.1), equal opposite-beam populations. Event order plus:1,3,2; minus:2,3,1. Reported h1=C1=0, h2=.0508437862517072 and C2=-.00677959232488525 on both sides, while one directional photon coefficient differs. This finite six-beam rule is only second-moment isotropic, not a continuous isotropic angular measure.

## 8. Cross-repo sources and use

- BASS_HE THEORY11 a0a3ba4ecb17c779a713705a45ee3fa3a9638c94: signed electron residual and global horizon weighting. Source-specific numerical bounds remain with that source.
- BASS_HE THEORY13 d9cb8c3ec3524ebd7d5c8418f2fda5fd329ef62f: separate Thomson/recoil functional and model/numerical bounds.
- BASS_CR TIME_DONOR and WU088_HH PHYS23: same-event invariants and sensitivity-triggered channel use. Exact current heads are to be reread before further reuse.
- SHEAR12 retains smooth spectral response. Finite threshold branch uses the formulas above.

## 9. Next use and evidence status

Continue existing SOURCE07-CONSUMER, with per-event (t_e,a_e,b_e,F^±,J^±,F_t^±,F_epsilon^±). Preserve actual event order, including one-sided simultaneous clusters. Return state responses, photon/electron/thermal ledgers, tau surface and separate continuous/event residuals. This is not a new prerequisite for unrelated runtime tasks. Full-spectrum uniform limits, grazing and physical source-backed execution remain specific open tasks.

Current recovery status: CHAT_DERIVATION_RECONSTRUCTED; ORIGINAL_CAS_RAW_NOT_RECOVERED; ORIGINAL_NUMERICAL_RUN_TRANSCRIPT_ONLY; independent reviewer NOT_RUN. This reconstruction may be checked and reused mathematically, but no missing old test receipt is invented. New work must record its own executed scripts/results. No fonts, private credentials, compiled binaries, or unrelated user files are included.
