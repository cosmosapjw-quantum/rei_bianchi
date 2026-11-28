# AUDIT5 — DR10B phase-authority inventory

## 1. 질문

현재 contour_geometry()가 Eq. (56)용으로 계산하는 local complex branch action의 실수부를 그대로 coherent Stückelberg phase로 사용할 수 있는가?

판정은 **아니다**. 계산량 문제가 아니라 source definition 문제다.

## 2. Source hierarchy

### Janev–Pop-Jordanov–Solov'ev 1997

He2+ + H의 advanced-adiabatic/Zwaan formulation에서 heavy-particle wavefunction의 action은 nuclear radial momentum P_alpha(R)의 contour integral로 정의된다. 두 독립 topological contours L1,L2에 대해 xi = |Im int_L P(R)dR|, chi = 1/2 Re[int_L1 P dR - int_L2 P dR], square-root branch의 adiabatic topological phase gamma = pi/2, one-pass p=q^2=exp(-2 xi), two-pass P=4p(1-p) cos^2(chi+gamma)이다. 즉 coherent phase는 complete path action의 차이다.

### Grozdanov–Solov'ev 2015

같은 He2+ + H 문제의 dynamical-adiabatic formulation은 ordinary branch에 대해 p=exp(-2 Delta)를 유지하고, Delta는 real axis에서 branch point까지의 local branch contour imaginary action으로 계산한다. 그러나 coherent final amplitude는 여러 complete reaction paths C^(k)의 합으로 쓰며 phi^(k)=Re int_C(k) E(t) dt와 branch encircling count에 따른 n^(k) pi/2를 따로 포함한다. 논문 예제에서는 final states에 22개와 14개의 paths가 존재한다.

따라서 local branch integral은 Delta_X를 공급하지만 full phi^(k)를 공급하지 않는다.

### ARSENY CPC 2023

Eq. (56)은 Delta 계산에 local complex energy-gap contour를 사용한다. 현재 clean-room contour_geometry.integral은 이 scoped 역할을 구현한다. 실수부는 저장될 수 있지만 complete reaction-path phase authority는 없다.

## 3. Common-trajectory bridge

P_a=sqrt(2M(A-U_a)), P_b=sqrt(2M(A-U_b))이면 정확히 P_b-P_a = -2M (U_b-U_a)/(P_b+P_a). common-trajectory limit에서는 P_b-P_a ~= -M DeltaU/P. dt=M dR/P이므로 Delta S ~= - int DeltaU dt. straight-line X=v t에서는 Delta S ~= -(1/v) int DeltaU dX.

이것은 ARSENY Eq. (56) electronic-action form의 1/v scale과 nuclear-action formulation 사이의 leading-order bridge다. 그러나 complete path의 real action, path topology, Stokes/topological phases를 복원하지 않는다.

## 4. Coding gate

허용:
- local action imaginary part -> p=exp(-2 Delta) single-pass lane;
- square-root adiabatic topological phase -> pi/2;
- independently authorized complete real path action + integer encircling count -> path phase bookkeeping.

금지:
- contour_geometry.integral.real을 chi 또는 phi^(k)라고 재명명;
- local contour 하나로 full coherent Eq. (50) network를 구성;
- missing real-path phase를 0/random/fitted value로 impute;
- phase-averaged total-cross-section authority를 state-resolved/differential arbitrary-v output에 자동 승격.

## 5. Next gate

DR10C_SINGLE_BRANCH_COMPLETE_PATH_PHASE_Q23를 열려면 source-defined complete paths L1,L2 또는 equivalent full-time paths를 실제로 구성해야 한다. 그 뒤에만 full real path action, local imaginary branch action, topological phase, close-coupling/1997 impact-parameter oscillation benchmark를 한꺼번에 비교할 수 있다.

현재 blocker는 CPU/GPU가 아니라 **path construction authority**다. Heavy local handoff는 열지 않는다.
