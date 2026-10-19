# V14 native 이력의 열·사건 채널 분석

작성일: 2026-10-19. 범위: 보존된 2026-10-18 NCP full CSV의 독립 재분석과 2026-10-19 고정 gas·geometry native 진단의 결과 연결.

## 결론과 근거 상태

기존 coupled GL2 이력의 약 1차 온도 refinement는 photoheating과 species별 photoabsorption 채널에서 나타난다. 동일한 subsegment 구조의 source-off 결과를 뺀 matched refinement에서도 finest observed order는 Xend=1e-5에서 0.9850, Xend=1e-4에서 0.9506이다. 전체 source number·energy 차이는 약 1.6e-14 상대크기 이하로, 이 온도 차이를 운반하는 열이 아니다. Scalar source 보존만으로 spectrum bin 분포와 remapping 정확도를 확정하지는 않는다.

이 보고서의 EOS 항등식은 **derived**, 실제 CSV의 채널 분해·차분은 **numerically checked**이다. 추가된 양의 초기 photon 진단은 **실제 native 구현으로 실행 완료**됐으며, gas와 geometry를 고정한 operator 실험이다. 그 결과를 coupled evolving-gas 우주론 이력이나 source-on 전체 2차의 증거로 합치지 않는다. 본 분석 작업은 기존 84이력·36개 표적시험·76개 제조 문제를 재실행하지 않았다.

입력 full CSV는 NCP run/source commit `ef94f08df149b57959b868646b397a2bff2b268b`, native code anchor `f6046418d15e2f44418dfbc04ca67999f389a7df`에 연결돼 있다. 각 CSV의 SHA256은 다음과 같다.

| 입력 | SHA256 |
|---|---|
| `birth_1e-5.csv` | `a4105e751d66ba59975c39d70c5d5822029cb5be0dd64094224417b28939e2f9` |
| `birth_1e-4.csv` | `58bde576741a8f8a980721da80990e2397c97f3e94a3500bac790e6745476e5f` |

모든 7개 mode와 N=8,16,32,64,128,256 endpoint 및 전 열의 adjacent 차분은 `native_refinement_decomposition.json`에 보존했다. 재현 스크립트는 `decompose_native.py`다. CSV 문자열은 60자리 Decimal로 읽었다.

## 1. EOS의 정확한 차분과 사건·열 회계

He/H 핵수비와 전자수/H는

\[
Y=\frac{0.2454}{4(1-0.2454)},\qquad
e=x+Y(y+2z),\qquad s=1+Y+e
\]

다. x,y,z는 각각 HII, HeII, HeIII 분율이다. Native `igm_state.rs::from_temperature/eos`와 `hhe_events.rs::temperature`의 monatomic EOS는

\[
w=A T s,\qquad A=\frac32 k_B
\]

이며, w는 total-H nucleus당 thermal energy다. 여기서는 k_B=1.380649e-16 erg/K와 1 eV=1.602176634e-12 erg를 유지해 w를 eV/H, A를 eV/K로 계산한다. Y를 고정하면

\[
\boxed{\frac{\delta T}{T}=\frac{\delta w}{w}
-\frac{\delta e}{1+Y+e}}.
\]

실제 유한 차분에는 선형화 오차를 더하지 않았다. Coarse c=N, fine f=2N, Delta q=q_c-q_f라 하면

\[
\Delta w=A(s_c\Delta T+T_f\Delta e),\qquad
\boxed{\Delta T=\frac{\Delta w}{A s_c}
-\frac{T_f\Delta e}{s_c}}
\]

가 정확히 성립한다.

P,C,R은 각 채널의 photoionization, collisional ionization, radiative recombination 사건/H이고 D는 HeII dielectronic recombination 사건/H다. 문턱 에너지는 chi=(13.598434599702,24.587389011,54.41776) eV이며, B_CI=sum chi_a C_a다. 누적 native 열을 이용하면

\[
\begin{aligned}
w-w_0={}&Q_{\rm ph}+E_{\rm CMB}-W_{\rm gas}-B_{\rm CI}\\
&-Q_{\rm CE}-Q_{\rm RR}-Q_{\rm DR}-Q_{\rm FF}+r_w,\\
e-e_0={}&P_{\rm tot}+C_{\rm tot}-R_{\rm tot}-D+r_e.
\end{aligned}
\]

CMB는 기체 유입을 양으로 하는 signed 열을 그대로 사용했다. r_w와 r_e는 각각 원시 열과 EOS, 사건과 전자수 사이에 남는 실제 잔차다. 위 식을 정확한 EOS 차분에 대입해 각 열의 K 기여를 계산했다. 예를 들어 photo 채널은

\[
\Delta T_{\rm ph}=\frac{\Delta Q_{\rm ph}}{A s_c}
-\frac{T_f\Delta P_{\rm tot}}{s_c}
\]

다. Escape와 photo-binding의 원시 차분도 JSON에 보존했으나, 이미 포함한 cooling과 photoheat에 중복해 더하지 않았다. 전체 photon energy 독립 회계는 생존 photon energy와 boundary photon number가 빠진 기존 CSV만으로 구성하지 않았다.

## 2. 모든 GL2 refinement에서의 leading 채널

아래는 Delta_N=T_N-T_2N이며 단위는 K다. Photo 열은 photoheat와 photoelectron의 합이다.

| Xend | N→2N | GL2 Delta T | Photo 채널 | Source-off GL2 Delta T |
|---|---:|---:|---:|---:|
| 1e-5 | 8→16 | +2.135721e-6 | +2.040350e-6 | -4.15658e-8 |
| 1e-5 | 16→32 | +1.125049e-6 | +1.101516e-6 | -1.01608e-8 |
| 1e-5 | 32→64 | +5.896563e-7 | +5.701877e-7 | +1.15415e-8 |
| 1e-5 | 64→128 | +2.969282e-7 | +2.895479e-7 | +6.2518e-9 |
| 1e-5 | 128→256 | +1.425051e-7 | +1.458544e-7 | -4.3492e-9 |
| 1e-4 | 8→16 | +3.915125e-4 | +3.533964e-4 | -3.768369e-5 |
| 1e-4 | 16→32 | +1.480855e-4 | +1.321197e-4 | -9.418101e-6 |
| 1e-4 | 32→64 | +6.511129e-5 | +6.065722e-5 | -2.494724e-6 |
| 1e-4 | 64→128 | +3.444760e-5 | +3.347486e-5 | -4.878111e-7 |
| 1e-4 | 128→256 | +1.786888e-5 | +1.792286e-5 | -2.066972e-7 |

Photoheat 자체의 finest observed order는 각각 0.9895와 0.9581이다. Matched GL2 minus source-off GL2 차이에서 p는 Xend=1e-5의 N=8,16,32,64에 대해 0.9396,0.9735,0.9919,0.9850이고, Xend=1e-4의 finest 두 값은 0.9525,0.9506이다.

## 3. HI·HeI 사건 배분과 binding·heat 차이

Xend=1e-4, N=128→256의 원시 coarse-minus-fine 값은 다음과 같다.

| 누적량 차이 | 실제 값 |
|---|---:|
| Delta P_HI | +2.54080458167e-10 /H |
| Delta P_HeI | -2.50078163889e-10 /H |
| Delta P_HeII | -8.6147521764e-15 /H |
| Delta P_total | +3.9936795260e-12 /H |
| Delta Q_photoheat | +2.72044139897e-9 eV/H |
| Delta B_photo | -2.69414140077e-9 eV/H |
| Delta(Q_photoheat+B_photo) | +2.62999982036e-11 eV/H |

HI와 HeI에 배분된 흡수 사건 수가 거의 반대 방향으로 움직여 total absorption count의 차이는 작아진다. Coarse 결과에서 HeI 대신 HI에 배분된 사건은 binding-energy 소모를 줄이고 photoheat를 늘리는 방향이다. 이 refinement에서는 binding 차이가 photoheat 차이의 99.03%를 상쇄한다.

온도 기여는 photoheat +1.7973647322e-5 K, photoelectron -5.0785565304e-8 K이며, 합 +1.7922861757e-5 K가 전체 +1.78688788e-5 K를 대부분 설명한다.

Xend=1e-5에서도 HeI 사건과 photoheat 차이는 약 1차다. N=16,32,64,128에서 N Delta Q_photoheat는 (2.6703,2.6545,2.6841,2.7038)e-9 eV/H이고, N Delta P_HeI는 (-2.8444,-2.9149,-2.9492,-2.9663)e-10 /H이다. 다만 짧은 구간의 finest pair에서는 Delta Q_photoheat=+2.1123e-11, Delta B_photo=-3.2154e-11 eV/H라서 흡수된 총 photon energy 차이도 남는다. 모든 구간의 차이를 순수 species exchange 하나로 환원하지 않는다.

## 4. CE·RR·DR·FF·CMB·work와 signed cancellation

다음 표는 N=128→256의 정확한 EOS 분해다. CI, RR, DR은 해당 반응의 thermal/binding 영향과 전자수 영향을 합쳤다. 단위는 K다.

| 채널 | Xend=1e-5 | Xend=1e-4 |
|---|---:|---:|
| Photoheat | +1.3955964e-7 | +1.7973647e-5 |
| Photoelectron | +6.2947932e-9 | -5.0785565e-8 |
| CE | -4.4936519e-9 | -9.9457775e-9 |
| CI | -7.8089831e-11 | -1.4529289e-9 |
| RR | +3.8180257e-13 | -1.6235214e-10 |
| DR | -2.1160e-22 | +1.3046e-19 |
| FF | -4.3548516e-13 | +8.7316333e-11 |
| Signed CMB | -2.1038474e-10 | +1.7215652e-8 |
| Gas work | +7.9220252e-10 | -8.7434599e-10 |
| Gas+electron 회계 잔차 | +6.4064941e-10 | -5.8850521e-8 |
| 합: 실제 Delta T | +1.4250510e-7 | +1.7868879e-5 |

CE는 전체 냉각량에서는 크지만 이 GL2 refinement의 leading 채널은 아니다.

`common_combined`의 큰 apparent p 및 부호 반전에는 명시적인 cancellation이 있다. Xend=1e-4, 64→128에서 EOS 열에너지 기여는 -8.26448e-5 K, 전자수 기여는 +7.73815e-5 K라서 합이 -5.26329e-6 K다. 다음 pair에서 각각 -4.56594e-7 K, +2.12626e-5 K로 바뀌어 합의 부호가 반전한다. 이러한 구간의 log2 absolute ratio만으로 수렴 차수를 채택하지 않는다.

## 5. 기존 source-off 제어군과 endpoint drift

두 Xend 각각에서 source-off, source-off-midpoint, source-off-GL2의 1,512개 row를 읽었다. 전부 photons_per_H=0이고 세 photo-event 열도 0이다. 이 제어군은 gas-only substep을 검사한다. 양의 기존 photon population을 갖는 source-free absorption map의 차수 검증에는 별도 입력이 필요했고, 다음 절의 고정 gas·geometry 진단에서 그 입력을 실제로 사용했다.

Xend=1e-5의 작은 source-off 차이는 최종 X의 어긋남과도 비슷한 크기다. Native 마지막 step의 secant를 사용한 endpoint displacement 진단은 다음과 같다.

| Source-off GL2 비교 | Delta X | 마지막-step dT/dX [K] | 추정 endpoint 기여 [K] | 실제 Delta T [K] |
|---|---:|---:|---:|---:|
| Xend=1e-5, 64→128 | -6.6612721e-15 | -1.1208783e6 | +7.4665e-9 | +6.2518e-9 |
| Xend=1e-5, 128→256 | +3.3306352e-15 | -1.1208543e6 | -3.7332e-9 | -4.3492e-9 |

이는 원자료 secant를 이용한 진단 추정이며 exact endpoint resampling이 아니다. Xend=1e-4의 source-off GL2 finer 두 pair에서는 독립적으로 재구성한 회계 잔차의 온도 기여가 +1.0286e-7 K와 -6.2301e-8 K다. 실제 차이에 비해 작지 않으므로 observed p를 흔든다. 이 현상을 모두 단일 temperature-ulp floor로 설명하지 않는다.

## 6. 완료된 양의 photon native 진단과 연결

위 source-off 제어의 빈 photon 입력을 보완한 native 진단이 2026-10-19 샌드박스에서 실행됐다. 근거는 [PROJECTION_ANALYSIS.json](../evidence/PROJECTION_ANALYSIS.json)과 [EXECUTION_NOTES.md](../EXECUTION_NOTES.md)다. Native summary CSV SHA256은 `ca4b20024bd2f8adfac5995ffeebfecd0c56f47d7cbe89d38f874a909402dc3e`, diagnostic source SHA256은 `868a4f8e28acebce0f1d78ff62f0adaf6a5d411c6896ea0b528afb8a16a0085f`다. 분석은 62행(48 pair,14 fixed-medium history)을 확인했고 모든 numeric field가 finite다.

이 실험은 source를 초기화한 뒤 gas와 geometry를 고정해 기존 public native photon transport API를 호출한다. MD14 broad spectrum에서는 하나의 full map과 두 half map 사이에 nonzero composition defect가 실제로 나타났다. 16 cells에서 theta=.05→.025의 local defect slope는 number 1.9426, energy 1.9552다. 고정 total interval을 m=16,32,64회로 나눈 native 반복 결과의 successive-difference slope는 다음과 같다.

| 고정 medium 관측량 | Finest self-difference slope |
|---|---:|
| 생존 photon number | 1.0092 |
| 생존 photon energy | 1.0074 |
| H I photo events | 0.9452 |
| He I photo events | 0.9932 |
| He II photo events | 0.9987 |
| Photo binding | 1.0009 |
| Photoheat | 0.9798 |

60 eV delta-spectrum 제어에서는 pair와 repeated-map 차이가 정해진 64-ulp rule 아래이며 모든 관련 slope가 null로 기록됐다. Number와 energy 보존 잔차는 초기 inventory로 정규화했을 때 약 1.9e-15 이내다. 따라서 scalar 보존과 양성성을 유지하면서 broad-spectrum native map의 composition 차이가 남는다는 실제 근거가 있다.

새 projection 분석기의 signed history difference는 O_2m-O_m로 기록되어 이 보고서 앞부분의 O_N-O_2N과 부호 관례가 반대다. Slope의 절댓값 ratio 비교에는 영향이 없지만 signed 표를 혼합할 때에는 변환해야 한다. Local pair defect의 약 2차 scaling은 global 2차 정확도 주장이 아니다.

이 결과는 birth-time quadrature와 evolving-gas 피드백을 제거한 상태에서도 native photon operator에 약 1차 repeated-map 추세가 있음을 보인다. 기존 coupled CSV의 leading photo 채널과 연결되는 구체적 원인 후보를 좁히는 근거다. 기존 우주론 이력의 전체 오차를 이 한 메커니즘으로 모두 설명하는 claim은 채택하지 않는다. 고정-medium 실험을 coupled evolving-gas 이력으로 다시 세지 않는다.

## 7. 현재 claim과 남은 연결

- EOS differential 및 finite difference 항등식과 원시 사건·열항의 분해는 완성됐다.
- 보존된 coupled GL2의 source-on 약 1차 추세는 photoheat·species partition 채널에서 확인됐다.
- 고정 gas·geometry positive-photon native 진단은 실제 완료됐고, broad-spectrum map의 nonzero local composition defect와 약 1차 반복-map self-difference를 확인했다.
- Source-on 전체 2차, uniform stiff accuracy, Case-B photon 재수송, full EoR, signed Bianchi는 기존 HOLD를 유지한다.
- 기존 coupled CSV에는 생존 photon energy와 boundary photon number가 없어 완전한 global photon 회계로 확장하지 않는다. 새 고정-medium inventory 검사와 그 범위를 구분한다.
- 구체적인 native projection/재구성 메커니즘의 유도, 최소 수정 후보, coupled 검증 재개점은 [상위 연구 보고서](../RESEARCH_CONTINUATION_KO.md)와 DAG에 연결한다.

본 보고서 작성 과정에서는 분석 스크립트나 native source를 변경하지 않았고 trajectory를 재실행하지 않았다.
