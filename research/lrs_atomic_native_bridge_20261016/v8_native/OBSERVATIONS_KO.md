# V8 native RR/DR 부분계 실행 관측

과학적 채택 판정 전 원시 관측이다. 원본 PR #150 소스 `6ea2b1b4b3875c9163cafc45efe720afded43fc4`의 `igm_rates`와 `IgmGasState`, `FlatFlrwBackground`, `HHeModel`을 새 NCP 폴더의 독립 Rust 실행기에 연결했다. 원본 production 소스와 checkpoint는 수정하지 않았다. 비교 상대는 V8의 독립 17차원 연속 RHS를 SciPy Radau로 적분한 해이다. 두 경로는 `X=ln(a/a0)`, `a0=1/21`, `nH=D*nH0/a^3`, 고정 `H(a)`, 초기 `(HII,HeII,HeIII)=(0.075,0.12,0.03)`와 같은 원자계수·냉각계수를 사용한다.

| 조건 | N=8 온도오차 K | N=128 온도오차 K | 마지막 64→128 관측 차수 |
|---|---:|---:|---:|
| D=1, Xend=1e-5, T0=15000 K | 7.28e-12 | 1.27e-10 | roundoff 구간 |
| D=100, Xend=.002, T0=15000 K | 8.07e-5 | 3.15e-7 | 1.9992 |
| D=1000, Xend=.002, T0=15000 K | 8.20e-3 | 3.16e-5 | 2.0002 |
| D=10000, Xend=.0003, T0=15000 K | 1.15e-2 | 4.28e-5 | 2.0009 |
| D=1000, Xend=.002, T0=22000 K | 9.47e-3 | 3.68e-5 | 2.0001 |
| D=1e6, Xend=.0001, T0=15000 K | 6.36e-1 | 7.80e-2 | 1.5418 |

최종 30개 NCP 실행의 exit code가 모두 0이었다. 원시 CSV 1488개 단계에서 모든 상태가 유한·비음수이고 온도는 10,000–24,000 K 안에 있었다. Rust–Python FLRW 기하 최대 상대차는 `1.82e-15`, 전자 event ledger 최대 절대차는 `1.40e-16/H`, H/He 핵수 최대 절대차는 `8.88e-16/H`, 전체 에너지 ledger 최대 상대차는 `7.64e-16`이었다. 최대 implicit root 잔차는 `1.98e-10 K`였다. 여기서 escaped radiation은 네 채널의 결합에너지 방출과 열 냉각 에너지로 따로 기록되며 photon count를 추정하지 않았다. 광자 유입/흡수, collisional chemistry, free-free, CMB는 이 부분계에 없다.

고강성 D=1e6 조건에서 첫 단계 온도오차는 N=8일 때 `3.43 K`, N=128일 때 `0.131 K`였다. RR_HII 단일 채널의 시작 전자 분율·시작 온도 계수로 만든 exposure 최대는 N=8에서 `25.23` 정도이고, 마지막 온도 오차의 마지막 쌍 차수는 `1.54`이다. 이 exposure도 `ΔX nH(Xmid)/H(Xmid)`를 공통으로 사용하므로 시작 시점의 `nH/H` 값을 뜻하지 않는다. 이 5단계 격자만으로 고강성 영역의 균일 2차 수렴을 말할 수 없다. D=1의 온도차는 부동소수점 바닥에 있어 시간 차수를 추정하지 않는다.

NCP의 첫 빌드는 Rust private module import 오류(exit 101)였고 `HHeModel`의 공개 재수출을 사용하도록 import 한 줄을 바꾸어 빌드했다. 첫 실패 stderr는 원시 archive에 있다. 이후 8단계 smoke 1건, 최초 30건 batch, 진단 열을 보완한 최종 30건 batch가 모두 exit 0이었다. 누적 native 호출은 **61건·2984단계**이며, 직접 Radau 비교와 assertion은 **최종 30건·1488단계**에 수행했다. 두 batch의 `/usr/bin/time` 기록 합은 각각 wall/user `0.06/0.06 s`이고, smoke 시간은 별도 계측하지 않았다. 이 작은 실행의 개별 시간은 `0.01 s` 단위로 반올림된다. 최종 build exit 0, 로컬 SciPy 비교 exit 0, 최종 원시 1488단계 assertion 검사 exit 0이다. NCP 실제 경로는 `/root/REI_LRS_V8_NATIVE_RR_jmixqM`, hostname은 `s1a0e5abed09`다. 자세한 SHA·환경·자원은 `NCP_RUN_RECEIPT.json`에 있다.

`NATIVE_RADAU_RESULTS.json`은 각 실행의 4채널 event·cooling·binding/escape, FLRW gas work, 오차와 Radau 민감도, 강성 단계별 exposure/오차를 담는다. `NATIVE_CHECKS.json`은 실행 결과 assertion 요약이다. 원시 CSV·stdout/stderr·빌드 실패 로그·원본 owner archive는 `NCP_NATIVE_RRDR_RAW.tar.gz` (SHA-256 `5f981e327813adb4696c76b83bdfec98b42dbc675dac8fd1348ac41187d34abe`)에 보관한다.
