# ISO-COUPLE P4/S5: 관측량을 분리한 양의 비영 source-age truncation

2026-10-17, `rei_bianchi`의 P4/S4 독립 Rust reference 다음에 추가되는 연구. **기존 PR #186 및 production PR #150은 변경하지 않음**. 1+3/source frame proper seconds, SI m, c=299792458 m/s, photon energy eV, thermal energy J, proper nuclei m^-3, photon inventory reference-comoving m^-3. Bianchi-I prescribed off-shell background: metric sign (-,+,+,+), 축대칭 방향 scale `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`.

## R1/R3. 유도에 필요한 가정과 주장 범위

* 입자수/광자 가중치 `w_c>=0`. 광자는 흡수되면 한 번만 HI/HeI/HeII/DI 중 하나에 소유됨. Photochemical owner와 CX/FF/CMB owner는 이전 P4/S4 소스 그대로.
* 제거 시각 `t*` 이후의 **직접 기여**를 추정하며, 광자의 방향 전환/산란/분할·새 방출은 제거한 동일 photon의 자손으로 생기지 않는 수송 문제를 대상으로 한다.
* 각각의 광자 가중치 `w`를 양수 상태에서도 버리는 행위는 **수치 모델 변경**이다. `w=0`만 제거하던 P4/S4와 같지 않다. 사용자 설정한 절대 photon/energy/species budget을 한 번만 사용한다. Error budget을 소진하면 그 이후 후보는 그대로 남는다.
* 원래 gas를 재계산한 `actual coupled` 비교에서는 남은 광자의 opacity가 달라질 수 있다. 여기서 추론한 photon-only direct error upper bound를 gas/electron/temperature/observer optical-depth error의 upper bound로 **옮기지 않는다**.

## R5. Positive survival 및 누락 사건수의 직접 상한

Photon number `w_c`가 `t*`에서 제거되었다고 한다. 고정된 임의의 비음수 κ_i(t) 이력에서는 `S(t) = exp(-∫ κ_total)`이 `0<=S<=1`이고 species `i` 흡수수는

\[
  A_{i,c}=w_c\int_{t_*}^T\kappa_i(t)\exp\left[-\int_{t_*}^t\sum_j\kappa_j(u)du\right]dt.
\]

따라서 `0<=A_{i,c}<=w_c`, 그리고 `Σ_i A_{i,c} + N_c(T)=w_c`. 여러 삭제 cohort에 대해 `R_N=Σ_deleted w_c`라 놓으면 직접 수송 누락 광자수와 전체 직접 누락 event 수는 **각각** `R_N`을 넘지 않는다. `R_N`은 HI/HeI/HeII/DI별 상대오차를 bound하지 않는다. 각 channel은 선택된 방향/에너지의 미래 최대 에너지 `E_max,c`가 해당 단면적의 threshold 미만일 때 A_i=0이며, 아니면 `A_i<=w_c`이다. Hence

\[
 A^{\rm omitted,dir}_i\leq \sum_{c\ \mathrm{deleted}} w_c\,\mathbf 1\{E_{\max,c}\geq E_{\rm edge,i}\}=R_i.
\]

추가 channel caps (`max_direct_species_events_com3[4]`)은 `R_i` 각각에 적용한다. 이는 **원래 흡수 사건수**에서 제거 photon이 기여했을 직접 사건수의 bound이며, 나머지 cohort가 새 gas를 만나 변한 효과까지 bound하는 게 아니다.

## R5. 유한 지평선에서 Bianchi photon 에너지 상한

Killing covector `P_i=a_i(t_b)E_b n_{b,i}`가 보존되므로

\[E(t)^2=\sum_i(P_i/a_i(t))^2,\quad \frac{d\ln E}{dt}=-\sum_i H_i(t)\,q_i(t),\quad q_i\geq0,\quad\sum_iq_i=1.\]

Axisymmetric constant directional rates `H_perp=H-s` and `H_parallel=H+2s`에서는 `h_min=min(H_i)`, `gamma=max(0,-h_min)`. 그러면 `t*<=t<=T`에서

\[
 E(t)\leq E(t_*)\,\exp[\gamma(T-t_*)]= E_{\max,c}.
\]

이는 한 축이 수축하는 prescribed background도 허용한다. Contraction에서 `E_future<=E_now`라고 가정하지 않는다. 직접 방출/흡수 광자 에너지의 상한은

\[
  Q^{\mathrm{omitted,dir}}_{\gamma}\leq R_E=\sum_{c\ \mathrm{deleted}} w_c E_{\max,c}(1.602176634\times10^{-19}\,\mathrm{J/eV}).
\]

`R_E`는 comoving m³당 J이며, 별도 `energy_at_cut`은 정확한 삭제시점 광자 에너지 장부다. 이 두 양을 혼동하지 않는다. Thermal+binding 분배 자체는 이전 source-native owner가 담당하며, 반응에 의한 온도 간접 효과는 이 식에 포함되지 않는다. Wolfram에서 `dlnE/dt` identity가 zero residual임을 확인하고, Python DOP853에서 FLRW+mixed directional 부호 사례 4개의 scalar envelope를 검사했다.

## C3/C5. 구현 불변량과 numerical robustness

* `age_remainder.rs`는 기존 `PositiveThresholdBridge.advance_with_diagnostics`를 먼저 실행한 뒤, 그 트랜잭션이 수용된 경우에만 제거한다. Photo events/temperature/chemical ledger를 소급 수정하지 않는다.
* `BudgetedAgeHistory`의 `TailRemainder`는 수치 제거 photon count·삭제 시각 photon energy·미래 photon energy bound·channel 상한을 소유한다. **수치 제거 photon은 실제 absorption ledger에 포함되지 않는다**.
* `source_injected = retained + physically_absorbed + numerical_removed`를 확인한다. 엄밀한 숫자 보존에 대한 floating 잔차는 별도 출력한다. 다음 단계 S4는 버려진 photon 에너지를 원래 radiation field에 다시 얹지 않는다.
* 각 후보는 `max_weight_per_cohort_com3`, cumulative photon budget, energy budget, **4채널** budget을 동시에 만족해야 한다. 모든 선택은 결정론적으로 작은 w부터. 입력 NaN/negative, 불가한 horizon, overflow, invalid ray는 fail-closed.
* 비영 `w*E*EVJ`가 floating 언더플로되어 0이 되면 0으로 간주하지 않는다. 최소 양의 subnormal로 위쪽 보수 추정한다. 양의 합/곱은 outward `next_up`으로 보수화한다. 이는 IEEE-754 represented numerics의 방향성 검사로서, 원자율·우주론 모델 불확실성까지 엄밀한 interval 인증했다는 뜻은 아니다.
* 기존 owner source 12개, old P4/S4 threshold roots, chemistry, source and solver code는 불변. 새 방법은 `with_tail_budget` + `advance_budgeted` 선택 시에만 작동한다.

## R7/C7-C8. source-native 실제 수치 결과

`evidence/p5_tail_campaign.csv` = 3환경 조합 (high opacity N12, low opacity N8/N16) × 4모드 (무압축, exact-zero, photon-mass-only, species_guard) × 3회 alternating order = 36행. 모든 시점의 `HHeModel` / `AxbiSource` / Verner / DAtomic / original photo events를 호출한다. Photochemistry와 P2 gas state는 매 step 함께 업데이트되며, full EoR 또는 Einstein on-shell 조건을 주장하지 않는다.

* `high_opacity N12`: 원본 9216 cohorts, 기존 exact-zero 2542, 새로운 비영 budget 0. 수치 제거 count `1.415925398046e-16` per c m³; 마지막 surviving photon count `1.512403475671e-17`이 사라짐. 무압축 대비 시간 중앙값 speedup 약 4.1배. Gas temperature는 출력 정밀도 내 일치. 이 결과는 high-opacity 제조 모델에 한정된다.
* `low_opacity N16`: mass-only 예산 `1e-10` photons/com³ 사용, 3837 비영 cohorts 제거, 총 실행시간 중앙값 1.53배 가속. 그러나 희귀 HeII photo events 상대 차이 **−80.1101%**. 총 photon budget이 작더라도 희귀 species 상대 수용이 실패할 수 있다는 **구체적 수치 반례**.
* 같은 조건에서 4채널 절대 event 상한 `[1e-10,1e-11,2e-14,1e-11] photons/com³`을 추가하면 248 cohorts만 제거되고 HeII photo event 차이는 **−0.0348%**, 3회 타이밍 중앙값 speedup 약 **1.001**. 물리적 상대 결과는 `numerically-checked`이며, 이 절대 cap을 native SA-02 상대 수렴 0.5% 주장으로 이식하면 안 된다.
* `low_opacity N8`: mass-only HeII 상대 차이 약 −58.59%; species_guard 약 −0.0308%, speedup 약 1.06.
* 특별히 작은 gas HeII 광이온화 채널에서는 전체 photon-number budget이 물리적 정확도 게이트를 대체할 수 없으므로, P4/S5의 일반 optimization production admission은 HOLD.

## R8/R9/C10. 주장 판정 및 DAG

`P4/S5 = PASS_SCOPED_DIRECT_REMAINDER_ACCOUNTING_AND_RUST_COMPARATORS`, `P4 full = PARTIAL`. SA-01/02, FLRW-CONV, BI-SIGNED, FULL EOR are HOLD. 향후 per-channel sensitivity-Jacobian/adjoint를 사용하여 full coupled observable error bound를 세우거나, **정확한 phase-space identity**를 이용한 lossless nonzero pooling/recursive age-slab propagation 등 다른 수송 복잡도 개선 후보를 독립적으로 개발해야 한다. 사용자 소스 PR150 immutable 및 P4/S1~S4 모두 read-only.

### 원 논문 및 재사용의 적용 범위

* Mellema et al. (2006), C²-Ray, https://doi.org/10.1016/j.newast.2005.09.004: photon-conserving RT와 photoionization 거동에 관한 방법론 비교. 본 `R_N,R_i,R_E`의 가정과 유도 자체는 **우리의 직접 유도**다.
* Mackey (2012), https://www.aanda.org/articles/aa/full_html/2012/03/aa17984-11/aa17984-11.html: multi-frequency 시간 차수와 photon conservation의 다른 error axes.
* Verner et al. (1996), https://www.pa.uky.edu/~verner/photo.html: 원본 H/He cross section reference. 새 원자율을 추정하지 않음.
