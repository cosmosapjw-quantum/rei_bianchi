# HE37 H1 gain 진단과 동일 kernel 계산비용

이 패키지는 Le–Cambier Eq.85와 §III.E의 등방 outgoing 각도 모형을 새로 계산합니다. 이전 HE36 CCC 결과는 `reused/ccc_moments.csv`의 저장된 129행을 읽어 비교에 사용합니다. 이전 kernel, IVP, 과학 suite 또는 그림을 재실행하지 않았습니다.

## 실제 결과

2000–200000 K의 129개 온도에서 source-native α,β,γ,δ와 number/energy/STF에 필요한 계수를 계산했습니다. 20000 K에서:

| 양 | 저장된 값 |
|---|---:|
| α | 9.39264787331677e−18 m³/s |
| κ₂ | 2.407095355857991e−16 m³/s |
| κ₂/α | 25.62744167910542 |
| 입사 제거 평균 에너지 | 16.745419384350164 eV |
| 생성 전자 두 개의 반환 평균 에너지 | 3.1454193843501645 eV |
| 순 열손실 | 13.6 eV/event |
| LC α / saved finite-CCC α | 3.4227965000657132 |

위 비율은 두 별도 source의 차이를 보여 줍니다. LC는 I=13.6eV인 semiclassical 전체 에너지 모형이고, HE36 CCC는 13.6058–968.61eV의 positive PL 유한 표 적분입니다. Threshold, 단면적 모형과 support가 모두 다르므로 이 비율을 calibrated H1 오차막대로 사용하지 않습니다. 두 kernel을 혼합하지 않았습니다. LC/CCC 비율 범위는 1.4914460903852345–7.095479155037354입니다.

각도 envelope는 같은 LC 사건 단면적에서 비음수·회전 공변·recoil-free outgoing 모형이 가질 수 있는 범위입니다. θ=kBT라 하면 전자 STF의 감쇠율은

    4 I β/(15 θ²) ≤ ν/n_H ≤ 2(3γ−Iβ)/(15 θ²).

등방 source는 ν/n_H=κ₂=4γ/(15θ²)입니다. 이는 π_e의 first variation입니다. 전체 gas π_b로 대입하는 closure와 실제 H1 각분포에 대한 오차막대는 공급하지 않습니다.

## 양의 원적분과 정확도

독립 수치 lane은 원래 σ(E) v(E) Maxwell energy measure를 그대로 적분합니다. `t=(E−I)/θ`로 옮긴 뒤 t∈[0,64]에서 양의 Gauss–Legendre weights를 사용합니다. 미리 고정한 후보 차수는 64→96→128이며 첫 통과에서 멈춥니다. 같은 129온도×4모멘트에서 상대 gate는 3e−12입니다.

- GL64: 최대 상대차 **9.138023671084738e−12**, 계획된 refinement 필요.
- GL96: 최대 상대차 **2.2426505097428162e−14**, 통과.
- GL128: 실행하지 않음. 남은 정확도 위험이 없어 추가 계산을 하지 않음.

모형의 t>64 잘린 tail은 GL discretization과 별도로 상한을 계산했습니다. `x=I/θ`, `L=64`, `p1=L+1`, `p2=L²+2L+2`, `p3=L³+3L²+6L+6`일 때 모멘트별 상대 상한은

    α: (x+2)e^(−L)
    β: p1 e^(−L)
    γ: (x p1+p2)/(x+2) e^(−L)
    δ: (x² p1+2x p2+p3)/(x²+4x+6) e^(−L).

α의 식은 positive integral F(x)≥1/(x+2)를 이용하며 나머지는 polynomial incomplete gamma 적분입니다. 모든 온도·모멘트의 최대 상한은 **4.617226718601215e−24**입니다. 이는 선택한 analytic 모형의 수치 tail에 대한 상한이며 CCC 표의 미측정 tail이나 실제 H1 source의 물리 오차를 제한하지 않습니다.

## 실제 비용 비교

같은 native source, 129온도, 4개 SI Maxwell 모멘트를 대상으로 analytic `expn2` 계산과 GL96 원적분을 비교했습니다. 각 lane 2회 warmup 이후 5쌍을 번갈아 실행했고, 각 trial에서 같은 batch를 64회 계산했습니다. GL node 준비는 별도 기록이며 매 timed call마다 에너지·단면적·Maxwell weights를 다시 계산합니다. Analytic lane의 추가 diagnostics/immutable return overhead도 그대로 포함했습니다.

| 측정 | 결과 |
|---|---:|
| 쌍별 GL/analytic 비율 중앙값 | 4.4825080029195785× |
| 쌍별 비율 범위 | 3.892765018690632–8.538838605855716× |
| 중앙 시간의 비율 | 4.41035830843409× |
| analytic 129T batch 중앙 시간 | 0.21943646875 ms |
| GL96 129T batch 중앙 시간 | 0.967793453125 ms |
| 전체 진단 wall time | 0.49922332899586763 s |
| 최대 RSS | 47180 KiB |

이는 공유 sandbox의 reference kernel 측정입니다. IVP·전체 network·Fortran·production 처리량의 속도 향상 주장이 아닙니다. 머신은 Xeon Platinum8573C, affinity9 CPU, quota8 CPU, memory8GiB이며 Python3.12.14/NumPy2.3.5/SciPy1.17.0, BLAS/OMP/MKL thread1을 기록했습니다.

## 그림과 재개

`plots/h1_gain_diagnostic.png`와 `.svg`는 새 scientific figure 한 쌍입니다. 첫 render에서 footer와 x축 label의 overlap을 직접 확인해 `plots/attempts/render_001`에 보존했습니다. Margin·annotation 위치만 바꾼 두 번째 render를 저장했고, scientific CSV·진단·benchmark는 반복하지 않았습니다. Renderer는 saved CSV만 읽으며 model을 import하지 않습니다. 최종 실제 그림을 열어 축·주석·footer 분리를 확인했습니다.

새 실행 집계: 진단1, analytic primary batch1, planned GL resolution batch2, benchmark1(5쌍×각lane64batch; warmup2쌍), render2(최종1쌍), 기존 CCC model 평가0, IVP0, 완료 suite replay0.

기본 재개 명령은 다음의 읽기 전용 검사입니다.

```bash
python verify_saved.py
```

실행 근거는 `outputs/DIAGNOSTIC.json`, `outputs/BENCHMARK.json`, `plots/RENDER_RECEIPT.json`과 `FILE_MANIFEST.json`입니다. 관련 입력·코드·계약이 바뀌기 전에는 `run_diagnostic.py` 또는 renderer를 다시 실행하지 않습니다. 바뀐 의존성이 있으면 기존 attempt를 보존하고 새 범위/출력 경로를 먼저 정합니다.
