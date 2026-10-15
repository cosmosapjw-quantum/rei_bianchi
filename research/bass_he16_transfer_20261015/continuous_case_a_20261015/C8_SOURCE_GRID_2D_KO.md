# C8: 원래 MD14 source의 에너지 격자 × 시간분할 독립 검증

2026-10-15 KST. 기존 `C7` 연구 코드는 source-scoped로 보존했으며, 이번 `C8`은 **source-only photon birth + native `Driver::deposit`/`geometry_map`**에 대한 독립 검증이다. 원자 반응, H/He 가열, Case-A recombination, 광자 emissivity를 제외한 다른 물리적 모델을 임의로 추가하지 않았다. `zbar=20→19.998`, 원래 cold MD14 BB50K (fesc=.2), normal-comoving q_ref=0. 기존 `q_ref`는 역사적 signed shear adapter이며 표준 양의 `Σ=|σ|/H`와 혼동하지 않는다.

## 1. 실제 수행한 2차원 실험

에너지 구간당 원본 광자 source 셀 수 `m=4,8,16,32,64` (H/He 문턱 구간 [13.6,24.59,54.42,100] eV를 원본처럼 분할), proper-time source midpoint/geometry substeps `n=1,8,32,128`의 총 **20개 완전한 Rust 계산**을 수행했다. 원본 source의 photon number `Nγ/H`, source energy `Uγ/H`, lower-boundary number 및 energy, 최초 source cell에 대한 두 노드 분배 weight, photon-number ledger, 공변운동량으로 전파된 source centroid의 최소 종점 에너지를 동시에 기록했다.

| 원본 에너지 구간당 셀 | 1 step 경계 유출 | 128 steps 경계 유출 | `m×f_boundary`(128) |
|---:|---:|---:|---:|
| 4 | 13.14757204% | 13.15584075% | 0.52623363 |
| 8 | 6.56972188% | 6.57812109% | 0.52624969 |
| 16 | 3.28016388% | 3.28856188% | 0.52616990 |
| 32 | 1.63846303% | 1.64684461% | 0.52699028 |
| 64 | 0.81877231% | 0.82714188% | 0.52937080 |

고정된 `n=128`에서 에너지 해상도를 두 배로 높일 때 경계 유출 비율은 차례로 `0.5000153,0.4999242,0.5007796,0.5022586`배였다. 반대로 에너지 해상도를 고정하고 시간분할을 `1→128`로 늘리면 유출이 제거되지 않고 약간 커졌다. **경험적 (O(1/m)) 격자 수렴**은 현재 4~64 셀의 source centroid 이산 표현에만 적용되는 진술이다.

각 케이스 photon-number ledger 절대 잔차는 `2e-18 / H` 이하였고, 원래 m=16 이전 source-only n=1/128 결과와의 호환도 검증했다. 정확한 source-cell centroid를 covariant geodesic으로 최장 구간 전파한 최소 종점 에너지는 `m=64`에서도 `13.66179179eV > 13.6eV`였다. **이 source-cell centroid 표현에서는** 하한 유출이 물리적 photon energy crossing 때문이 아니다.

## 2. 해석적 최초 투영 가중치

\(E_0=13.6\,\mathrm{eV}\)이고, 같은 문턱 구간의 첫 두 격자 노드는 \(E_0\), \(E_1=E_0+\delta\)이다. 원래 source의 spectral photon-number density를 \(\Phi(E)>0\), 전체 적분을 \(I=\int_{13.6}^{100}\Phi(E)\,dE\)라 두자.

원래 첫 source cell의 centroid \(\bar E\)를 두 노드에 barycentric projection하면 하한 노드의 weight는 \(w_0=(E_1-\bar E)/(E_1-E_0)\)이다. 첫 source cell의 photon fraction \(f_{\rm first}=(1/I)\int_{E_0}^{E_1}\Phi(E)\,dE\)를 곱한 전체 birth fraction은

\[
p_{\rm first}(\delta)
=\frac{1}{I\delta}\int_0^\delta
(\delta-x)\Phi(E_0+x)\,dx.
\]

\(\Phi(E_0+x)=\Phi_0+\Phi'_0x+O(x^2)\)가 문턱 우측에서 성립할 때

\[
p_{\rm first}(\delta)
=\frac{\Phi_0\delta}{2I}
+\frac{\Phi'_0\delta^2}{6I}
+O(\delta^3).
\]

원본 logarithmic energy grid에서 \(\delta=E_0[\exp(\ln(24.59/13.6)/m)-1]\sim E_0\ln(24.59/13.6)/m\)이므로 최초 투영으로 인한 하한 population은 \(O(1/m)\)이다. 이것이 이번 source-only 테스트에서 관찰한 energy-grid scaling의 구체적인 원인이다. \(\Phi=f_0+f_1x\)의 선형 확장에 대해 Wolfram은 정확히 \(\delta(3f_0+\delta f_1)/(6I)\)를 반환했고, \(p_{\rm first}/\delta\to f_0/(2I)\)를 검산했다.

최초 투영에서 하한 노드에 배치된 photon stock은 이후 양의 적색편이를 받으면 \(E<13.6\,\mathrm{eV}\)로 변환되며, 원본 \`Driver::deposit\`이 이를 numerical boundary loss로 기록한다. 따라서 고정 \(m\)에서 시간분할만 줄여도 최초 barycentric population 자체는 사라지지 않는다.

## 3. 정확도 및 외삽 경계

본 실험에서 source-only 유출은 **수치적 에너지 재투영 artifact**로 명시할 수 있으나, 이 수치를 전체 재이온화 이력, `τ`, 또는 스펙트럼의 연속 분포에 대한 global error bound로 바꾸지 않는다. 원래 BB50K **연속적** SED에는 13.6eV 바로 위의 실제 photon 에너지도 있으므로, 실제 유한 구간을 적색편이로 진행하면 진짜 UV support crossing도 있을 수 있다. 지금의 Bianchi cohort baseline은 셀 `centroid`만 전달하며 4~64 셀에서는 최저 centroid가 물리적 UV 하한을 넘지 않는다. 연속 SED의 정확한 finite interval threshold flux는 별도 적분이 필요하다.

또한 source-only 검증에서 chemistry는 OFF이다. 앞선 C7의 Grackle Case-A source는 원래 16 cells/threshold segment에서 24 matched A/B runs를 실행했고, 원자·온도 ledger를 닫았지만, 본 새로운 2D source-only 해상도 표의 gas xHII, xHeIII, T 예측은 존재하지 않는다. 두 계산을 결합하여 가짜 global gas-grid convergence를 주장하지 않는다.

## 4. 건설적 수치설계 판단

후속 비교는 (1) source-cell centroid를 전파 구간 동안 covariant-momentum으로 유지하는 method B, (2) 원래 고정격자 A에 **conservative incoming energy-bin flux** 및 물리적 UV cutoff 처리 규약을 독립적으로 부과하는 대안을 분리한다. 단순히 `13.6eV` 하한 노드의 광자를 강제로 E>13.6로 옮기는 처방은 conservation과 spectrum을 왜곡할 수 있으므로, photon number/energy/atomic binding/photoheating 및 원래 threshold owner를 동시에 검증해야 한다.

현재 release gate: **DERIVED + ACTUALLY_EXECUTED + NUMERICALLY_CHECKED, SOURCE_ONLY_C8**. Original complete EoR and CMB observable: HOLD. Original production worktree or solver was not modified. Native AI subagent `NOT_RUN`, local Codex `NOT_USED`.

## 5. 실행 원본

- `source_boundary_2d.rs`: 실제 원본 Rust `AxbiSource`, `Driver::deposit`, `Driver::geometry_map`, `CovariantPhoton` 호출
- `results/SOURCE_BOUNDARY_2D.csv`: 20개 실행 original raw number/energy/boundary ledger
- `analyze_boundary_2d.py`, `results/BOUNDARY_2D_ANALYSIS.json`: source-scoped identity, particle support 및 m-n 비교
- `test_boundary_2d.py`: 10개 unit/regression/negative fixtures (10/10 PASS)
- `results/BOUNDARY_2D_REFINEMENT.svg`: white-background numerical chart

새 자료는 기존 C7 source/epoch pin과 동일한 별도 Rust `librei_microphysics-2db3552c92b16edc.rlib`를 링크했으며, 전체 compiled source가 원래 frozen production binary와 동일하다고 주장하지 않는다.
