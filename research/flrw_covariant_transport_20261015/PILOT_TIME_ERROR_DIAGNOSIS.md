# Q128 pilot 시간 오차 진단: 12000-step snapshot

상태: **실제3-comparison 판독 완료; HI threshold cell의 정상 O(h²) photon error가 병목으로 확인됨**. 아래 최초 예비 진단을 보존하고 말미에 실제 결과와 root-approved passive-compartment control을 추가했다. 허용오차 local_target=1e-5 및 기존 scientific acceptance를 유지한다.

## 관측된 사실

고정 입력은 raw/q128_attempt1/checkpoints/00012000.txt다. a=0.047660747356025206, z=19.98162650556048, stored next_dln_a=4.8828125e-8, last_error=3.96329539979e-6, wall=282.45 s, accepted=12000, rejects=20이다. 이 checkpoint를 읽은 동안 live pilot은 계속 진행 중이었다.

| accepted | 다음 dln a | last error | photon N/H | 첫 HI cell의 support 중 문턱 아래 길이 비율 |
|---:|---:|---:|---:|---:|
| 60 | 7.62939453125e-10 | 5.68096e-6 | 1.03251e-9 | 1.00504e-6 |
| 1200 | 1.953125e-7 | 7.70135e-6 | 3.85139e-8 | 0.00332265 |
| 5760 | 9.765625e-8 | 9.72785e-6 | 3.86334e-8 | 0.0195331 |
| 12000 | 4.8828125e-8 | 3.96330e-6 | 3.87129e-8 | 0.0304576 |

마지막 열은 **support의 기하학적 길이 비율**이며 photon mass fraction이 아니다. 12000-step ray0의 cell0은 N=3.39054798528e-11, mean ε=13.7963669198 eV, support=[13.600000001297,13.991017738755], HI cut ε=13.611909444881이다. 각도 가중치가 이미 포함된8 rays의 이 cell N을 실제 합산하면 전체 N의 약0.017303790736이다(이전8×ray0 추산 정정). HeI cut cell20과 HeII cut cell48도 고정 cell 안에서 이동한다.

HI photo rate 약3.99e-18/s와 총 photon inventory는 이미 매우 완만하게 변하는 반면 gas 온도와 HeII fraction은 계속 완만히 증가한다. 20 rejections 중18개가 시작점에 있다. 이것은 반복적인 Newton 실패 때문에 step이 축소되는 모습은 아니다.

driver error_metric는 gas fractions 3개, thermal relative error, 동일 q-cell N L1 error, physical U L1 error 중 최대를 취한다. support endpoint 자체를 비교하지 않으므로 endpoint 차이가 metric에 직접 들어가는 coding bug는 확인되지 않았다. support가 reconstruction과 다음 reaction에 간접 영향을 주는 것은 별도 문제다.

## 초기 비단조 rejection의 설명

상수 source와 opacity인 scalar 문제 N'=S−λN, N(0)=0에서 현재 source-before-BE 조합은

$$N_f=\frac{Sh}{1+x},\qquad
N_{hh}=\frac{Sh(1+x/4)}{(1+x/2)^2},\quad x=\lambda h.$$

따라서 photon-relative full-vs-two-half 차이는

$$\frac{|N_f-N_{hh}|}{N_{hh}}=\frac{x}{(1+x)(4+x)}.$$

x=2에서 최대1/9이고, 큰 x에서는 양쪽 해가 모두 강제 평형으로 접근하여 차이가 작아진다. 실제 초기 rejection의 0.0208→약0.10→0.0233 비단조 패턴은 이 메커니즘과 일치한다. 따라서 시작점의 peak만으로 representation bug를 판정할 수 없다. 초기 N floor가 작동하는 구간의 실제 metric은 위 순수 relative formula와 다르다.

## 이후 quasi-steady 구간의 유력한 판별 대상

미세한 emission upper support 차이, 실제 source/time dependence, gas feedback, threshold-crossing closure가 모두 후보다. 아직 특정 후보가 실제 max error라는 결론은 없다.

다만 현재 방식은 four-variable gas에 대해서 implicit이며 **photon two-moment closure 자체에 대해 완전 implicit인 것은 아니다**. old plus injected moment를 재구성하고 그 고정 node bank에서 BE를 푼다. 이 차이는 quasi-steady 순간에도 시간 오차 계수를 만들 수 있다.

M=(N,Q), P=moment projection, r(M)=positive reconstruction, Λ=고정 node opacity operator라 하자. F(M)=PΛr(M), G(M)=PΛ²r(M), source moment=S. positivity 및 smoothness가 유지되는 국소 영역에서 현재 한 step은

$$T_h(M)=M+h[S-F(M)]+h^2[G(M)-DF(M)S]+O(h^3).$$

closed moment ODE의 equilibrium S=F(M)에서도 h² coefficient는

$$G-DF\,F=P\Lambda[I-Dr(M)P]\Lambda r(M)$$

가 되어 일반적으로 0이 아니다. opacity 곱셈이 reconstruction family의 tangent space 밖 성분을 만들기 때문이다. threshold를 가로지르는 cell에서 Λ의 jump가 커지면 이 coefficient가 커질 수 있다. 이는 **국소 O(h²) splitting/closure 오차**라는 가능한 설명이며, 아직 실제 pilot의 원인 판정은 아니다. steady photon inventory만으로 큰 step을 보장할 수 없는 이유를 제공한다.

반대로 error가 h→h/2에서 거의4배 줄지 않고2배 또는 plateau라면 support activation/비매끄러운 branch, quadrature 또는 arithmetic floor를 우선 조사해야 한다.

## 승인된 최소 진단 실행 계약

production source를 고치지 않는 별도 example을 worker가 작성한다. 같은 config·source build로 고정 12000 checkpoint를 읽고 다음 **3 comparisons만** 수행한다.

- h=stored next_dln_a, h/2, h/4.
- 각 comparison에서 full와2half를 계산하므로 총9 tentative solves.
- tentative helper는 native 순서 그대로 old clone → geometric midpoint → interval_increment의 dt → geometry_map(mid) → transport.inject와 source N/U ledger commit → chemical_stage(dt) → geometry_map(end) → validate(1e-8).
- source와 chemistry는 같은 실제 finite-interval proper dt를 쓴다. 계산과 원본 live checkpoint의 상태를 섞지 않는다.
- cumulative wall cap60s, RHS cap10000, 첫 substantive failure에서 root에게 반환한다. 원본 run·checkpoint·생산 source는 수정하지 않는다.

각 comparison이 반드시 기록할 값:

1. actual dln a와 proper dt; gas3 normalized errors; thermal error; N_L1/max(N,1e-8), Uphysical_L1/max(U,1e-8); native error_metric과 decomposition의 일치.
2. source N/U increments, photon event HI/HeI/HeII 및 gas/thermal ledger의 full-half 차이.
3. combined photon error top8 cells: ray/cell, q edges, full/half N/Q/support, physical cut/R, straddle flags, absolute/normalized ΔN와ΔU. 지원되면 all-cell component sums도 보존한다.
4. h→h/2,h/4별 p=log2(error(h)/error(h/2)); 각 component와 지배 cell에 별도 계산한다. 0인 component는 p를 억지로 정의하지 않는다.
5. input checkpoint/config/source hashes와 실제 executable, elapsed/RHS counts.

첫3 comparisons의 결과를 보기 전 source-off/λ-zero 등 추가 control을 자동으로 늘리지 않는다. 아래 HI의 **closure mass**가 필요하면 기하학적 support 길이 비율로 대체하지 않는다.

## 결과별 다음 행동

- gas 또는 smooth photon components가 p≈2이며 전체 error가 정상 감소: 실제 stiff finite-step error다. h를 완화하지 않고 실제 throughput 및 bounded prefix reach를 기준으로 NCP pilot 예산을 정한다.
- HI/HeI threshold cells가 우세하고 p≈2: representation은 동작하지만 closure/splitting이 비용을 지배할 수 있다. 다음 독립 energy-grid refinement로 계수 감소와 비용을 비교한다. conservation만으로 시간 효율을 판정하지 않는다.
- p≈1, plateau, branch jumps 또는 floor: 실제 cell/branch 기록을 지정해 한 가지 targeted diagnosis/repair 계약으로 반환한다. 전체 캠페인 예산을 먼저 크게 늘리지 않는다.
- source increments가 비교 기준 이상의 일관성 결함: source quadrature/geometry bookkeeping을 고친다. physical source를 바꾸거나 local_target을 완화하지 않는다.

현재 dln이 고정된다고 가정하면 ln(21/5)/h≈2.94e7 steps다. 12000-step 관측 평균 약0.02354s/step을 그대로 곱하면 단일 history 약8일이지만 이는 **일정 step/속도라는 가상 비용 산술**이며 실제 full-history 예측이 아니다. step size와 rate/neutral density는 이후 크게 달라질 수 있다. 따라서 이 계산을 근거로 무제한 full launch나 blanket no-go를 선언하지 않는다. 먼저3-comparison 진단이 다음 유한 allocation의 근거다.

## 실제 3-comparison 결과와 판정

raw/q128_step_diagnostic_001/diagnostic.json을 읽었다. 9 tentative,63 RHS, diagnostic solve wall0.047812104s이며 native metric와 component maximum이 모두 일치한다.

| step scale | N L1 error | physical U L1 error | 최대 gas fraction error | thermal error |
|---:|---:|---:|---:|---:|
| h | 3.963479149419194e-6 | 2.2412498526443475e-6 | 2.4961193178721988e-9 | 1.620914700540026e-12 |
| h/2 | 1.0722307640564845e-6 | 6.05735796578824e-7 | 6.423434000402128e-10 | 2.2486418309264915e-13 |
| h/4 | 2.794455764758477e-7 | 1.577848477171789e-7 | 1.6295461854428177e-10 | 3.1977494478485806e-14 |

N order는1.88615→1.93998, U order는1.88754→1.94073이다. 8개의 top cells는 모든 ray의 energy cell0이며 combined normalized N+U error의95.1851%,95.3436%,95.4296%를 차지한다. full/half의 이 cell support는 완전히 같다. source N full/half relative 차이는3.81e-12~1.52e-11이고 source U increment는 같았다.

**판정:** 현재 병목은 정상적으로 h²로 감소하는, HI 문턱을 가로지르는 두 모멘트 closure/splitting의 photon error다. source clock inconsistency, support-distance norm bug, quadrature plateau 또는 gas Newton bottleneck으로 볼 근거는 없다. 따라서 local_target을 완화할 이유가 없다. 위 commutator 설명은 관측된 우세 cell과 수렴 차수에 부합한다.

## 다음 root-approved control: passive compartment cut cell

root는 생산 driver를 바로 바꾸기보다 pure partition utility와 별도 진단 wrapper를 먼저 승인했다. 새 utility가 compile identity를 바꾸므로 이전 core/driver 실행은 그 원래 identity의 유효 근거로 보존한다.

현재 bounded exponential closure가 f(ε)=C exp(αε)라면 restriction f·1_[cut,H]도 같은 exponential family다. 따라서 N_active,Q_active를 그 구간에서 적분하고 support를 [cut,H]로 줄이는 것은 **선택된 closure의 restriction을 복원**한다. 임의의 true child spectrum을 알아냈다는 주장은 아니다. inactive 부분 역시 두 모멘트로 보존한다. 이 특성이 현재 HI opaque/transparent mixture를 한 exponential로 반복 혼합하는 오차를 줄일 이론적 근거다.

Utility는 기존 moment-matched threshold-cut positive quadrature를 재사용해 actual E<13.60 eV 부분을 나눈다. equality delta는 원래 AtomicProvider 행동을 따른다. 전부 위·아래인 cell은 원래 모멘트를 정확히 복사하고, mixed cell은 양의 compensated/anchored 합을 쓴다. N partition residual64eps*N, Q partition residual128eps*max(|Q|,Nwidth)를 freeze했다. old closure의 instantaneous Gamma/heat와 restricted active closure는 relative1e-9 이내, 양쪽 zero는 exact zero여야 한다. 임의의 작은 rate floor는 추가하지 않는다.

Candidate wrapper:

1. 동일12000 checkpoint에서 한 번 분할하여 공통 initial active+inactive state를 만든다.
2. 매 geometry_map에서 active와 기존 inactive 모두의 R 변화 work를 계상한다. 이후 새 HI cut 아래로 이동한 active photon만 inactive pool에 추가한다. initial full support를 반복 분할하지 않는다.
3. inactive N/Q는 **q-cell별** sidecar로 저장하여 gas와 영구 분리하지만 계속 적색편이시키고 전체 inventory에 포함한다.
4. source는 기존 그대로이며 chemical_stage는 active state만 받는다. 모든 ray의 비증가 physical energy 조건을 확인한다. 이번 control은 FLRW이며, 재청색편이 가능한 모델에 영구 inactive 처리하지 않는다.
5. native residual만으로 wrapper를 통과시키지 않는다. augmented residual은 driver.residuals(active)+(ΣN_inactive,ΣR Q_inactive)이고, unpartitioned initial residual을 기준으로 기존 acceptance를 적용한다.
6. 기존 total-cell norm은 active+inactive를 합친 각 q cell로 계산한다. 더 강한 separated L1=Σ(|Δactive|+|Δinactive|)도 동일 total normalization으로 보고한다. active-only error를 개선 지표로 몰래 대체하지 않는다.

Candidate도 h,h/2,h/4의3 comparisons,총9 tentative,60s/10000 RHS 한도만 수행한다. retained baseline 결과는 재사용한다. 집중 unit coverage는 empty/δ/outside, mixed positive moment partition, 같은 geometry의 idempotence, 두 cut의 work/conservation, instantaneous rate/heat parity다.

root는 측정 전에 유용성 기준을 고정했다: h에서 **total error와 strong split error가 모두 baseline/5 이하**, 즉7.926958298838388e-7 이하이며 gas·ledger의 기존 기준과 positive domain을 지켜야 한다. 이5배 기준은 state 추가를 정당화할 경험적 성능 기준이며 물리 정확도 기준을 완화한 것이 아니다. 통과하면 명시적인 native inactive-pool 구현과 fresh pilot을 시작한다. 실패하면 이 control의 비용 대비 이득이 부족하다고 판정하며 global no-go로 확대하지 않는다.




## Candidate actual outcome

실제 raw/q128_partition_diagnostic_001 결과를 읽었다. h의 total/strong split metric은 모두2.64820642375e-7로 사전 baseline/5 기준을 통과했다. Local defect 개선은14.966655배이고 gas/augmented conservation도 기존 경계 안이다. h/2,h/4는7.18501660803e-8,1.87472170644e-8이다. 새 focused partition tests3/3 PASS;9 tentative,63 RHS,0.057589372s solve wall이다. 상세 R1–R10 및 source identity는 CUT_CELL_THEORY.md/json에 기록했다. 다음은 explicit native passive-pool 구현과 fresh finite pilot이다. 이 결과는 전구간 완료나 runtime speedup 증거가 아니다.
