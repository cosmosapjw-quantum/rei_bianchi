# 시간구간 물리 소스 적분 이론

가정: frozen REI `ON_refined` 7개 `(t_i,z_i,y_i)`는 원본 source의 proper seconds와 mean-z label. `lambda_j(t_i)` 및 `Q_heat,j(t_i)`는 Puchwein 2019 D1 13-knot six-moment를 별도의 원 REI 시뮬레이션과 조합한 **조건부 hybrid source**다.

두 양의 endpoint `a,b` 사이에 `r(t_i+s Δt) = exp((1-s) log a+s log b)`로 보간.

`Integral r dt = Δt*(b-a)/(log b-log a)` (단 a=b는 Δt a). 이는 정확하게 로그평균 `L(a,b)`이며 `sqrt(ab) ≤ L(a,b) ≤ (a+b)/2`. 사다리꼴 `I_tr=Δt(a+b)/2`는 두 번째 선언된 interpolation diagnostic이다. 이 사이의 차이는 물리 연속해/적분 오차 상계가 아니다.

각 H1/D/T/He3/He4의 7개의 원 REI ionization 사건 j마다 양수 source `lambda_j=Y_src Γ_c`, `h_j=Y_src H_c`, ionization threshold I_j (eV).

`N_j=integral lambda_j dt` (events/Href), `Heat_j=integral h_j dt` (eV/Href), `Ion_j=I_j*N_j` (eV/Href), `Abs_j=Heat_j+Ion_j` (eV/Href). `Abs_j`를 별도 로그보간하지 않는다. 그러면 사건별 전자 생성 횟수 1, 핵자수 보존은 원본 S 행의 linear invariants에서 계속 성립.

경계: 실제 P19-fiducial 전개된 chemistry `(y(t),T(t),H(t))`가 아니다. 서로 다른 UVB 노출과 원 REI frozen 이력의 hybrid. Source injection/recombination/collisions 및 광자 전달, 실제 proper τ/Thomson K/directional redshift 미포함.

행렬 산출: 6 intervals × 7 events × 2 cases =84, 12 interval totals, 14 cumulative, 2 totals. 조건부 source H1↔He4 dominance proxy도 two endpoint linear time label의 model output에 불과.

실행 기록: 첫 `LOGLINEAR_ABS_ENERGY_LEDGER` 실패를 근거로 energy construction 교정. 12 Python PASS, 168 mpmath90 PASS, Wolfram symbolic logmean identity residual zero.
