# 복구된 전구간 spectral 비교

실제 재계산된 `EVENT_COUPLED003_RECOVERED`는 mean-redshift 15.9→4 전구간을 완료했다. `EVENT_COUPLED002`의 보존된 128 energy × 2 angle 결과와, 새 256 × 2 결과의 저장 상태를 비교했다. 두 결과 모두 r=0, rtol=1e-11이며 physical provider, native binary, base RHS 및 event source identity가 일치한다. 003 event driver에는 accepted-gas/finite 진단과 sampled+endpoint ledger 판정이 추가됐다. 수식/RHS와 적분 상태를 변경하는 차이는 없다. 정확한 diff는 comparison JSON에 보존했다.

003의 218 segment 적분 시간은 629.197834 s였다. 보고된 endpoint와 129 공통 epoch를 합친 최대 energy residual/initial energy는 6.64932786e-11, photon-number residual/initial nH는 5.50148574e-10이다. 둘 다 고정 1e-9 기준을 만족한다. 003의 모든 accepted state에서 가스 분율·EOS 온도·유한성 및 광자 양성이 명시적으로 검사됐다. 002의 모든 accepted gas state 검사는 **NOT_MEASURED**로 유지한다.

그러나 **spectral refinement는 FAIL**이다. 24개 비교 항목 중 23개가 1e-3 기준을 넘었다. 원 계약의 65 공통 epoch 정규화와 추가 129 epoch 정규화를 각각 적용했으며, 양쪽 모두 최대 오차가 0.1401807633이었다. 광자 보존 및 같은 격자의 시간 수렴은 에너지 적분의 정확도를 대신하지 않는다.

| 관측량 | 129 epoch 최대 정규화 차이 | 그 차이의 mean z |
|---|---:|---:|
| xHII | 0.00179100 | 7.88156 |
| xHeII | 0.00259590 | 9.18599 |
| xHeIII | 0.00677235 | 4.30748 |
| T | 0.00413458 | 6.59959 |
| GammaHI | 0.12691813 | 4.13629 |
| GammaHeI | 0.14018076 | 4.13629 |
| GammaHeII | 0.06315329 | 4.00000 |
| 순간 source number/reference volume | 0.11504560 | 4.20796 |
| 순간 source energy/reference volume | 0.08630366 | 4.20796 |
| 누적 source number/reference volume | 0.00336450 | 4.20796 |
| 누적 source energy/reference volume | 0.00268351 | 4.20796 |
| radiation energy/proper volume | 0.00442667 | 4.60736 |
| 총 primary photoheat/proper volume | 0.01632884 | 15.04297 |

Source, radiation energy와 photoheat는 `n2/CONTRACT.md`에 있던 기존 의무다. 이번에 저장 상태 후처리로 빠졌던 측정치를 복구했으며, 새로운 선택적 진단으로 격하하지 않았다. Photoheat는 primary photoelectron의 초과에너지 전달이며 cooling/Compton/팽창을 포함한 net thermal power가 아니다. 에너지별 Gamma와 photoheat는 실제 native `SIGMA`만 호출해 산출했다. ODE 또는 RHS를 재실행하지 않았다. 저장된 원래 Gamma/photon 관측량 재구성도 1e-13 상대 기준 안에서 일치했다.

## 원인 국소화와 다음 조치

`SPECTRAL_BAND_LOCALIZATION_RECOVERED.json`은 실제 최대오차 epoch에서 saved-state 에너지대역별 합을 계산한다. z=4.13629에서 GammaHI의 coarse−fine 차이는 −2.37732661e-13 s^-1이며, 13.6–24.59 eV 대역이 −2.62709030e-13을 제공하고 24.59–54.42 eV 대역이 일부 상쇄한다. GammaHeI 차이 +1.47568422e-13 s^-1는 사실상 24.59–54.42 eV 대역에 모여 있다. 순간 source number의 최대 차이 z=4.20796에서는 10–13.6 eV 대역이 주된 기여를 한다. 고에너지 tail 확대만으로 이 차이가 해소된다고 볼 근거는 없다.

이는 fixed log-q midpoint quadrature가 움직이는 원자 threshold와 source spectral jump를 격자별로 다르게 표본화한다는 가설을 지지한다. 시간 event 분할은 source/threshold crossing 시점을 해결하지만, 그 자체로 에너지 적분 오차를 제거하지 않는다. 다만 대역 합은 **원인 전체를 증명하지 않는다**. 축적된 spectrum과 가스 abundance의 피드백도 photoheat 차이에 포함된다.

다음 계산은 기존 RUN002/128 same-grid 시간 검산을 반복할 단계가 아니다. source-only의 알려진 spectral knot와 원자 threshold를 분리한 적분 기준을 세우고, 그 기준에 맞는 q 적분 또는 보존적 spectral 재구성을 실제 결합 driver에 도입하는 것이 우선이다. 변경 후 동일 15.9→4 전구간 및 동일 1e-3 spectral, 1e-9 ledger 기준으로 비교해야 한다. 차이가 남은 상태에서 r=.05 angular-pair의 과학적 효과나 BASS의 새 native-history 수신을 승인하지 않는다.

003의 원래 raw bytes와 ce40 local commit은 scratch 정리 뒤 회수되지 않았다. 따라서 그 옛 수치를 새 결과로 채택하지 않았다. 본 문서의 숫자는 `EVENT_COUPLED003_RECOVERED/RESULT.json`, 새 saved-state moments와 새 비교 JSON에서만 가져왔다. 독립 판정은 별도 reviewer 산출물을 따른다.
