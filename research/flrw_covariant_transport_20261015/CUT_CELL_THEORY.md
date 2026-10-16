# HI cut-cell passive compartment: 이론 단위

현재 상태: **이론·구현 계약 및 bounded candidate numerical control PASS; native production 구현이 다음 단계**. native production goal을 위한 수치법 단위이며 physics threshold/local_target을 바꾸지 않는다. 현재 H/He-only absorption에서 valid한 inactive 분리를 다룬다. 미래 3He/Li source/provider 작업은 별도 단위이며 이 실험의 blocker가 아니다.

## R1 — 문제·완료 기준

Q128 12000-step checkpoint의 photon time-error 병목을 줄이는 최소 변경을 검토한다. 기존 frozen reference-q positive N/Q/support representation, source, cold gas Newton, dt, physics provider, local_target=1e-5를 유지한다.

root가 승인한 범위는 pure partition utility, 새 focused unit tests, 외부 wrapper의3 candidate step comparisons다. native production 활성화와 full run은 이번 numerical control 결과 이후의 명시적 다음 작업이다. 기존 baseline과 completed tests는 재실행하지 않는다.

## R2 — 실제 근거와 재사용

PILOT_TIME_ERROR_DIAGNOSIS.md/json과 raw/q128_step_diagnostic_001/diagnostic.json을 읽었다. h,h/2,h/4의 N metric은3.963479149419194e-6,1.0722307640564845e-6,2.794455764758477e-7이다. local order1.886→1.940이며 top8 모두 HI energy cell0이다. 이8cells가 normalized N+U error의95.185→95.430%를 차지한다. support는 full/half에서 동일하고 source moments는 수치적으로 일치한다.

THEORY_TRANSPORT.md/json의 covariant energy, bounded exponential closure, source/BE event owners, frozen quadrature tolerances와 새 BE algebra의 Wolfram 결과를 재사용한다. 이번 선형 partition/work 식은 그 보존법칙에 Qtot=Qactive+Qinactive를 대입하는 확장이다. 같은 CAS identities를 재실행하지 않는다.

## R3 — 정확한 가정

각 reference ray j에서 physical E=R_j(t)ε다. selected H/He photo fit cuts의 최솟값은 E_cut=13.60eV이다. 모든 선택된 absorption cross section은 E<E_cut에서0이다. binding χ와 fit cut을 혼동하지 않는다.

영구 passive 분리는 해당 history에서 E_j(t)가 비증가일 때만 유효하다:

$$\frac{\dot E_j}{E_j}=-\sum_i H_i n_{j,i}^2\le0.$$

FLRW H>0에서는 성립한다. general Bianchi mode는 이 조건을 보증하지 않으면 영구 passive pool을 사용하지 않는다. future lower-threshold species/process를 활성화하면 cutoff owner와 passive admission을 다시 평가한다. 현재 H/He 연구의 실행을 그 미래 확장 때문에 멈추지 않는다.

각 q cell의 state는 active (N_A,Q_A,L_A,H_A)와 passive (N_P,Q_P)다. passive는 물리적으로 버린 광자가 아니라 흡수만 비활성인 radiation inventory다. 원래 q-cell index를 유지한다.

## R4 — 대안 비교와 선택

1. 기존 retained-inert closure로 NCP 예산만 늘리기: 유효한 수치법이지만 현재 관측 비용의 주원인을 남긴다.
2. 단순 threshold cull 후 boundary ledger에만 넣고 metric에서 제거하기: total radiation state/오차 의미가 달라지고 성능 개선을 오차 제외로 오인할 수 있다.
3. **선택: positive closure restriction + per-cell passive N/Q, continued redshift work, original total-cell norm과 stronger split norm 모두**.
4. photon moment에 대해 완전 implicit한 내부2×2 solve: 후속 대안이며 현재 단위보다 큰 method change다.

선택안은 bounded exponential family의 구간 restriction이 같은 family라는 구조를 활용한다. 임의 spectrum의 true child data를 얻었다고 가정하지 않는다.

## R5 — partition과 work의 실제 증명

### Positive restriction

cell closure는 positive measure dν=C exp(αε)dε 또는 실제 δ다. current cut c=E_cut/R에서

$$d\nu_A=1_{[c,\infty)}d\nu,\qquad d\nu_P=1_{(-\infty,c)}d\nu.$$

양쪽은 비음수이고 disjoint하게 전체를 덮으므로

$$N_A+N_P=N,\qquad Q_A+Q_P=Q,\quad
Q_X=\int\epsilon\,d\nu_X.$$

Exponential을 [max(L,c),H]에 제한해도 같은 α의 exponential이다. 그 restricted N_A,Q_A와 support로 복원되는 bounded exponential은 continuum closure 수준에서 기존 active 부분과 같다. 따라서 현재 H/He Γ와 photo heat integral은 분할 전후 동일하다. numerical quadrature 및 moment fit의 오차는 아래 수치 계약으로 검사한다.

c가 support 밖이면 전체 state를 정확히 복사한다. δ의 E=Rε가 cut와 정확히 같으면 AtomicProvider의 equality behavior를 따른다. mean clipping이나 support를 임의로 늘리는 조작은 없다.

같은 geometry에서 두 번째 partition은 active support 아래에 질량이 없으므로 이동0이다. cut가 c1≤c2로 증가하면 두 번 restriction의 active 결과는 c2에서 한 번 restriction한 것과 같다. 이 compositional 성질은 **partition 사이에 source/absorption으로 closure가 바뀌지 않은 경우**에 해당한다.

### Geometry와 총 에너지

N_A,N_P,Q_A,Q_P가 geometry half map에서 고정이면

$$U_\gamma(t)=\sum_jR_j(t)(Q_{A,j}+Q_{P,j}),$$
$$W_\gamma(t_0,t_1)=\sum_j[R_j(t_0)-R_j(t_1)](Q_{A,j}+Q_{P,j}).$$

따라서 Uγ(t0)−Uγ(t1)−Wγ=0이다. 새 geometry에서 partition은 Q_A+Q_P를 보존하므로 work/source/absorption 사건을 추가하지 않는다. boundary/escape energy로 중복 계상하지 않는다.

현재 source가 생성하는 physical photons는 E≥13.60이므로 source는 active에 들어간다. active photon absorption은 기존 chemical_stage가 한 번 소유한다. passive photon은 계속 radiation inventory와 redshift work에 포함된다.

### Wrapper conservation

생산 driver는 passive를 모르므로 driver.validate를 전체 wrapper 검산으로 사용할 수 없다. native residual 정의를 직접 읽어 다음을 적용한다:

$$r_{N,\rm aug}=r_{N,\rm native(active)}+\sum N_P,$$
$$r_{U,\rm aug}=r_{U,\rm native(active)}+\sum R_j Q_P.$$

단, native photon_work ledger에는 passive의 continued work를 추가해 둔다. unpartitioned initial checkpoint의 residual을 기준으로 기존 photon/energy tolerance를 적용한다. 기존 closure/state를 침묵리에 새 production checkpoint로 해석하지 않는다.

## R6 — 독립 검토와 수치 계약

선형 partition 항등식, geometry work 항등식, bounded exponential restriction, monotone-energy 조건을 직접 역대입·차원·부호 검토했다. 이전 Wolfram number/energy/work residual=0의 동일 선형 구조를 재사용했다. numerical partition은 다음 frozen 기준을 만족해야 한다.

- Number defect≤64 eps N.
- Reference-energy defect≤128 eps max(|Q|,N(H−L)).
- old vs restricted-active instantaneous Γ/heat relative difference≤1e-9; bothzero는exact0. 임의 absolute rate floor를 도입하지 않는다.
- genuine empty/full/δ cases는 직접 분기한다.
- samegeometry idempotence, growing-cut work/conservation, positive state 및 support realizability를 확인한다.

이 기준은 root가 candidate measurement 전에 승인했다. 기존 physics/science acceptance를 완화하지 않는다. 작은 arithmetic underflow 실패가 있으면 실제 사례로 반환하고 임의 floor로 숨기지 않는다.

## R7 — bounded numerical discriminant

**상태: 실제 candidate raw/receipt와 새 focused tests 3/3 PASS를 읽음.** 아래 사전 계약으로 실행되었다.

고정 raw/q128_attempt1/checkpoints/00012000.txt를 한 번 partition하여 공통 candidate initial state를 만든다. 각 tentative의 geometry half map마다 아래 순서를 따른다:

1. old R와 기존 passive Q를 보존.
2. native geometry_map(active,to): active work와 gas adiabatic map.
3. photon_work에 Σ(R_old−R_new)Q_passive를 추가.
4. pure utility로 active를 새 cut에서 partition하고 **newly** inactive만 sidecar에 추가.
5. 기존 source와 chemical_stage; 다음 geometry half map에서도1–4.
6. wrapper augmented residual과 positive domain 검사.

h,h/2,h/4의 full-vs2half3comparisons(9tentative),60s,10000 RHS 한도다. retained baseline3comparisons는 재사용한다. source-off와 추가 campaign을 자동으로 늘리지 않는다.

기록: total-cell original metric, strong separated metric, active-only diagnostic, gas/T, source/events, passive N/Q/work, augmented ledger residual, source identity/node counts/wall/RHS.

Original total norm은 각cell의 N_A+N_P,Q_A+Q_P로 비교한다. stronger split norm의 photon 항은

$$\frac{\sum_k(|\Delta N_{A,k}|+|\Delta N_{P,k}|)}{\max(N_{\rm total,half},10^{-8})}$$

이며 U도 R-weighted reference moments로 동일하게 구성한다. gas·thermal component와 최대를 취한다. pool을 perray로 미리 합쳐 q-cell cancellation을 숨기지 않는다.

### 실제 결과

raw/q128_partition_diagnostic_001/diagnostic.json 및 sibling receipt를 직접 읽었다. 세 비교는9 tentative,63 RHS였으며 solve wall=0.057589372s, command wall=0.753551645s였다. 새 partition-only tests는3/3 PASS이고 기존 core bytes는 exact prefix로 보존되었다. 새 core SHA256은 `f811c6c53964d903c695bf1463e287933601eabaca47e34036b05a37a2e37348`이다.

| Step | Total metric | Strong split metric |
|---|---:|---:|
| h | 2.648206423745888e-07 | 2.648206423744218e-07 |
| h/2 | 7.185016608031656e-08 | 7.185016608145378e-08 |
| h/4 | 1.874721706444513e-08 | 1.874721706397564e-08 |

Candidate local orders는1.881952,1.938315다. h에서 gas fraction max=2.496119435e-09, thermal=1.606751226e-12이며 augmented residual full/half는 N에서−3.00e-19/−3.04e-19, energy에서−2.372e-15/−2.375e-15이다. 기존 tolerance 안이며 split/total metric은 수치 정밀도 수준에서 일치한다. 따라서 passive pool을 metric에서 숨겨 얻은 개선이 아니다.

## R8 — 사전 고정 판정 규칙

Candidate h에서 **original total metric과 stronger split metric 모두≤7.926958298838388e-7**, 즉 retained baseline/5이어야 유용성 PASS다. 동시에 기존 gas·ledger acceptance, positivity, provider domain을 통과해야 한다.

**판정: PASS.** h의 두 metric 모두 사전 bound보다 작고 retained baseline 대비 defect 감소는14.966655배다. 이는 local step defect 개선이며 end-to-end runtime speedup 측정이 아니다.

5배 개선은 추가 state의 실제 이득을 평가하는 사전 선택 empirical criterion이다. continuum accuracy proof나 tolerance relaxation은 아니다. 이 조건에 못 미치면 이 control의 성능 이득이 부족하다고 기록한다. 전체 FLRW solver에 대한 no-go가 아니다.

새 strong no-go theorem을 채택하지 않으므로 NG1–NG7을 충족한 novel impossibility result를 주장하지 않는다. 그 대신 실제 대상·closure·단조 조건·근거 범위를 좁혀 제시한다.

## R9 — 코딩 연결

권장 pure API:

partition_below_hi(&PhotonState,&GeometrySnapshot)
→ active PhotonState + inactive_number Vec + inactive_energy_ref Vec + partition diagnostics.

기존 private cell_quadrature를 재사용하는 core method로 추가할 수 있다. core build identity가 바뀌므로 unit evidence를 새 source identity에 연결하되 과거 실행의 유효성을 소급 취소하지 않는다. driver production path는 아직 활성화하지 않는다.

Fixed-array passive memory는2×8×N_cells bytes이며 accepted-step 수와 무관하다. monotonicity guard는 wrapper에 적용한다. future production 활성화 시 checkpoint/metadata/observables/norm을 명시적으로 version/change 해야 한다. 이 작업을 통과한 것으로 미리 표시하지 않는다.

## R10 — 종료와 다음 실행

이 문서 시점에 **계약·수학적 정당화·R7 bounded numerical control·R8 사전 판정이 모두 완료**되었다. native production driver는 이 진단에서 변경하지 않았고 checkpoint는 EXPERIMENT_INITIALSTATE_NOT_PRODUCTION_RESUME으로 사용했다. 다음은 native passive-pool을 명시적으로 구현하는 단계다.

PASS→explicit native passive-pool implementation→changed tests/review→fresh finite pilot→energy/source/time refinement→이미 승인된 actual NCP bounded full run으로 연결한다. 사용자 승인을 다시 요구하지 않는다. future species source research는 별도 진행하며 이 native 경로를 process-only 상태에 묶지 않는다.

