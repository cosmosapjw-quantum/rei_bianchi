# 저장된 endpoint에서 확인한 step-size 감소

C2_FULL004의 완료된 attempt67–102, accepted gen61–96만 읽었다. 모두 수용되었고 hard-event clipping 없이 PROPOSED step이었다. 사용 h는 1.78152064e+12에서 1.15982703e+11 s로 15.360배 감소했고 마지막 다음 h는 1.03779032e+11 s다. 새 map·native·검증 실행은 없다.

Limiter는 {'U_eV_ref_distribution': 12, 'GammaHI_s': 24}이며 GammaHI가 attempt79/gen73부터 지배한다. 현재 controller의 next_h/h=0.8/sqrt(ratio)이므로 수용조건 ratio≤1과 step증가조건 ratio<0.64는 다르다. 후기 ratio≈0.8은 수용되면서도 h를 약0.895배로 줄인다. 원인은 controller 구현의 모순이 아니라 현재 결함 추정치가 안전계수의 중립값보다 계속 큰 데 있다.

마지막 full–two-half GammaHI 차이는 1.59873762e-19 s⁻¹, fine GammaHI의 0.298348%다. 저장된 native K0를 cell별로 합하면 q=[13.6,14.65077331729082] eV의 HI threshold cell24가 그 signed차이의 99.908401%를 만든다. 새 logq 경로를 쓰는 HeII cell66의 직접기여 비율은 1.09986714e-06뿐이다. 따라서 새 logq quadrature jitter가 주된 직접원인이라는 설명은 저장된 자료와 맞지 않는다. 장기적인 간접영향을 배제한 것은 아니다.

Fine GammaHI 진폭은 전체 관측 sequence에서 1.2428% 증가한 데 비해 h는 약15배 감소한다. 후기 GammaHI 결함은 약1.6e-19 s⁻¹에 머물고, HI cell24의 full/half N와 평균에너지는 눈에 띄게 다르다. 저장된 post-attenuation K0/N로 계산한 유효 hκ는 마지막 coarse에서 8.059, fine half에서 5.311다. 이는 optically thick source–attenuation–reconstruction 결합 및 stiff order reduction 가설을 지지하는 진단 단서다. 물리적 상태가 바뀌는 동안의 자료이므로 고정 상태에서의 h→0 errorfloor나 Zeno 수렴을 증명하지는 않는다.

다음 우선 작업은 **HI_THRESHOLD_CELL24_STIFF_DEFECT_DIAGNOSIS**다. 최신 accepted 상태를 고정한 이론적 map 분석과, 새로 예산을 정한 미실행 미래구간 h/h2/h4 결함 비교로 stiffness·closure·time discretization을 분리해야 한다. 현재 스케일·허용 기준을 완화하지 않는다. 추가100회 예산만으로 throughput 위험이 해소된다고 주장할 근거도 없다. 측정된 평균 19.777 s/attempt는 이 국소 sequence의 비용이며 전구간 ETA가 아니다.
