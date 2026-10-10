# N1 물리 해석 — 새 native 전구간 H/He·열 history

이 문서는 `NATIVE002`와 `EVENT_COUPLED001`에 저장된 결과를 읽은 해석 초안이다. solver·기존 RUN002·검증 suite를 재실행하지 않았다. 아래 수치는 **현재 유한 grid의 계산 결과**이며, 고정된 number/time/spectral acceptance가 닫히기 전에는 최종 과학 결과로 승격하지 않는다. 이후 더 정밀한 run의 실제 증거가 추가되면 해당 상태를 우선해야 한다.

이번에는 초기 `z_a=15.9`, `T=20 K`, `x_HII=2e-4`, 중성 He에서 출발해 `z_a=4`까지 약 **1.2713 Gyr**의 H/He ionization·thermal·photon history가 실제로 계산되었다. HM12의 초기 UVB와 이후 emissivity, 기존 Grackle Case-A 원자율, 같은 gas state의 opacity, 정확한 dust+Lambda FLRW background가 연결되어 있다. 이전 축약모형의 `Q_HII(z)`와 달리 이번 `x_HII`는 homogeneous gas의 ionic fraction이다. source·clumping·closure·IC가 달라 두 값을 같은 관측량처럼 겹쳐 일치시켜서는 안 된다.

| 저장된 epoch | x_HII | x_HeII | x_HeIII | T [K] |
|---|---:|---:|---:|---:|
| z=15.9 | 0.0002 | 0 | 0 | 20 |
| z≈10.0425 | 0.48594 | 0.66285 | 3.92×10^-5 | 9842 |
| z≈6.9970 | 0.92496 | 0.97150 | 0.001574 | 11672 |
| z=4 | 0.9999948 | 0.713710 | 0.286283 | 11596 |

표는 `NATIVE002`의 저장된 epoch를 그대로 요약한 것으로, 지정한 redshift에 보간한 독립 정밀 해가 아니다. 이 계산은 source에 의해 cold gas가 가열·이온화되고, 후반에는 hydrogen이 거의 이온화된 상태에서 HeII→HeIII 전환과 temperature 변화가 함께 나타나는 **선택된 조건부 모형의 유한시간 해 후보**를 제공한다. H/He의 실제 결합 진화가 가능해졌다는 진전은 분명하다. 관측 우주의 reionization epoch 또는 HeII reionization 완료시기를 측정한 결과는 아니다.

## 에너지 좌표의 효과와 아직 닫히지 않은 수치 기준

초기 number 좌표 run `NATIVE001`은 z≈6.09까지의 저장된 output 뒤에서 `Required step size is less than spacing between numbers`로 실패했다. 최대 initial-energy-normalized residual은 `4.77×10^-5`로 기준 `10^-9`를 통과하지 못했다. 작은 국소 RHS ledger residual만으로 장구간 정확도가 보장되지 않는 실제 사례로 보존해야 한다.

그 뒤의 좌표 변환은 물리를 바꾸지 않는다. 각 characteristic에 대해

\[
U_j=E_j(t)N_j,\qquad
\dot E_j=-\lambda_jE_j,\qquad
\lambda_j=H+s(3\mu_j^2-1)
\]

이므로

\[
\dot U_j=E_j S_j-(\kappa_j+\lambda_j)U_j,
\quad N_j=U_j/E_j,
\quad \kappa_j=c\sum_a n_a\sigma_a(E_j).
\]

reference-volume total energy는 `sum U_j`, gas thermal energy, ionization fractions와 별도 source/escape/CMB/work counters의 **선형 결합**이 된다. 이를 통해 `NATIVE002`는 같은 physical problem의 z15.9→4 구간을 완주했고 최대 initial-energy-normalized residual은 `6.00×10^-11`이었다. 에너지를 임의로 투영하거나 residual을 source에 되먹인 것이 아니다.

반면 photon number `sum U_j/E_j(t)`는 시간 의존 계수를 가진 관측량이다. `NATIVE002` 최대 number residual은 **4.55×10^-8**, event segmentation을 추가한 `EVENT_COUPLED001`의 sampled maximum도 **4.06×10^-8**로 기존 `10^-9`를 아직 넘는다. 후자는 accepted/sample positivity와 전체 구간 완주 및 energy 기준을 통과했으나 **number gate는 FAIL**이다. event 구간 endpoint의 energy maximum `4.67×10^-11`과 sampled maximum `5.32×10^-11`도 구별해야 한다. 두 run의 가까운 최종 값이나 local residual≈10^-15는 미충족 number 기준을 대체하지 않는다.

따라서 현재 판정은 `computed / implementation-verified conditional evolution; numerical promotion HOLD`가 적절하다. time refinement의 field criterion `2×10^-6`, number `10^-9`, energy `10^-9`를 그대로 유지하고, 선택된 refined run 또는 number/energy를 함께 보존하는 discrete map의 실제 결과로 판단해야 한다. 성공한 에너지 metric으로 acceptance 자체를 재정의하지 않는다.

## HeII·고에너지 source·CMB의 해석 범위

지금 source band는 physical **10–50000 eV**이고 CR·secondary cascade·RCT·diffuse reabsorption은 꺼져 있다. 원 HM12 emissivity의 H-ionizing 전체 energy 중 50keV 위에서 제외된 비율은 z15.9에서 **0.300%**, z4에서 **7.668%**다. 이는 photon count tail의 작은 비율과 달리 무시할 수 있다고 자동 결론내릴 양이 아니다. 다만 **source energy 누락률은 HeII ionization 또는 gas heating 오차율과 동일하지 않다.** 실제 영향은 cross section, optical depth, Compton/secondary deposition과 transport를 통해 계산해야 한다.

특히 z4의 `x_HeIII≈0.2863`은 54.4eV 이상 field와 evolving opacity를 포함한 선택된 모델의 결과지만, 이 수치를 정밀 HeII reionization 예측으로 쓰려면 threshold 주변 spectral refinement가 먼저다. fixed-q finite quadrature에서는 node가 edge를 통과할 때 Gamma가 계단처럼 변할 수 있다. 정확한 event 위치를 찾아 적분하는 일은 시간 오차를 줄이지만, 그 자체로 에너지 방향의 continuum 오차를 제거하지 않는다. 50keV tail 문제와 54.4eV 부근 spectral quadrature 문제는 별도로 남겨야 한다.

CMB는 `T_gamma=2.7255(1+z)`의 **prescribed isotropic blackbody bath**다. signed Compton energy exchange는 external bath counter에 기록되어 Case-A escape와 분리된다. FLRW에서도 별도 prescribed bath 근사이며, Bianchi로 옮기면 실제 anisotropic CMB spectrum·angular moments의 해가 아니다. radiation stress backreaction과 CMB bath의 자체 진화도 현재 풀지 않는다. 따라서 다음 Bianchi run은 이 조건부 열적 배경 아래에서의 차이를 측정한다.

## 가장 작은 다음 과학 비교

time/number/energy gate가 닫힌 동일 FLRW baseline에 대해 **r=s_i/H_i=0.05의 한 개 paired Bianchi history**가 가장 작은 다음 과학 계산이다. 새로운 원자율이나 CR을 먼저 완결할 필요는 없다. 같은 mean-redshift 구간·초기 물리 상태·HM12 source·band·Case-A closure·CMB bath·수치 budget을 유지하고, q coverage와 angular resolution만 해당 geometry에 맞게 충분히 잡는다. 공통 `z_a`에서 `Delta x_HII`, `Delta x_HeII`, `Delta x_HeIII`, `Delta T`, `Delta Gamma_a`와 가능하면 photon energy quadrupole을 비교한다. 방향별 observed-redshift의 차이나 total CMB tau로 해석하지 않는다.

isotropic source/IC와 isotropic local atomic physics를 두었으므로 angular quadrupole이 shear에 먼저 반응하고 scalar 평균은 angular averaging과 mean expansion의 영향을 함께 받는다는 예상은 직접 시험할 수 있다. 그러나 완전한 scalar parity나 r의 일차항 부재를 이미 계산된 결과처럼 주장하지 않는다. 필요할 때 r=-0.05 companion을 추가하면 angular sign 및 scalar leading-order behavior를 분리할 수 있다. 하나의 실제 paired long run과 그 수렴 판정이 다음 목표이며, 좁은 구간의 같은 probe를 다시 반복하는 것은 목표가 아니다.

## 읽은 증거

- `integration/CONTRACT.json`: 실행 전 수치·과학 범위와 보호된 acceptance.
- `integration/evidence/NATIVE001/RESULT.json`, `NATIVE002/{RESULT.json,IDENTITY.json,driver_as_run.py}`: 저장된 실행·실패·좌표 구현.
- N2 worktree의 `n2/evidence/EVENT_COUPLED001/{RESULT.json,IDENTITY.json,EVENTS.json}`: event segmentation과 실제 남은 number failure.
- `n1/{REPORT_KO.md,CONTRACT.json,evidence/BINDING_CHECKS.json}`: source provenance, cold IC·Case-A·CMB·50keV tail.

새 문헌 조사나 추가 solver 실행은 이 해석 초안에 사용하지 않았다. 원 source는 pinned HM12 author tables와 Grackle3.4.1; 재사용한 자료의 물리적 허용 범위는 N1 source manifest를 따른다.
