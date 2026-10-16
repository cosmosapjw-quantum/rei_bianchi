# REI LRS V10 native 시간 배치 실험: 관측 기록

이 문서는 독립 과학 심사 전의 **잠정 수치 관측**이다. 원본 PR #150 고정
commit `6ea2b1b4b3875c9163cafc45efe720afded43fc4`을 별도 NCP 폴더에
풀고, PR #167 `1e6a3dd60d69b22483d07a30541736018a69dea8`의 연구용
old/newborn 광자 분리와 균일 출생 `phi1(-tau)`, old-photon exponential
감쇠 코드를 패치로 재사용했다. 원본 production과 checkpoint는 수정하지
않았다. PR #167 driver 패치에는 다른 BASS 연구 변경도 있으므로 아래
변형군은 **실험용 파생 소스**의 결과다. 패치 전 원본과 패치된
`legacy_be` N=8의 기존 41개 CSV 열은 바이트 동일했다. 이 한 사례의
일치는 모든 production 경로의 동등성을 뜻하지 않는다.

## 조건과 코드

`X=ln(a/a0)`의 `[0,1e-5]`, `a0=1/21`, 시작
`(HII,HeII,HeIII)=(0.075,0.12,0.03)`, `Tgas=15000 K`, 초기 광자 0이다.
total-H 핵수 밀도와 FLRW `H(a)`, proper `dt=geometry_increment`는 같은
고정 native owner에서 가져왔다. 광자 transport energy cell 64개,
source-energy subdivision 16개, angle cell 8개, escape fraction 0.2,
transport thread 1개다. `fixed_step → tentative`에서 midpoint geometry,
광자 birth, opacity/chemistry, endpoint geometry를 바꾸는 opt-in 제어군을
만들었다. `full_exp_half`의 opacity는 같은 midpoint geometry에서 옛 종과
Newton trial 종의 absorber 밀도 산술평균이다. photo event와 heat를 그
밀도에 맞게 보정하고, midpoint absorber는 양수인데 endpoint absorber가
0이면 중단한다. `full_exp_half_rrmp`는 V8의 Grackle Case-A RR_HII,
RR_HeII, RR_HeIII, DR_HeII 네 채널 midpoint exact-pair half-stage를
나머지 BE chemistry 양쪽에 배치한다. RR/DR의 species, cooling, escape를
BE RHS에서 한 번 제거했다. CI/CE/free-free/CMB는 여전히 endpoint BE다.

재현 도구는 [prepare_owner_v10.sh](prepare_owner_v10.sh),
[native_v10.rs](native_v10.rs), [README_REPLAY.md](README_REPLAY.md)에 있다.
실행 소스 driver SHA-256은
`925d933cd1d236d85c7e6462184bf8809357f56069bdd72f2fef3ac68327961f`,
transport는 `2405fd20fdc52568ccb0979bb49b600b69294ef36762839945defdc84f6df5e1`,
RR helper는 `e38b2393cc561efbe7a1efc4a9c7edeaeb28f2ba77c310ddc0bcb6f41b935446`이다.

## NCP 수치 관측

NCP `s1a0e5abed09`, Rust 1.99.0, Python 3.12.3에서 8개 기본 모드를
N=8,16,32,64,128로 실행했다(40개). 선택된 3개 모드는 N=512,1024 및
한 번의 N=2048 추가 세분화(9개), Newton `1e-13` 진단은 N=128에서
2개다. 최종 receipt의 51/51 실행이 exit 0과 완료 marker를 갖고,
초기 owner smoke/패치 parity 네 실행과 재빌드 parity 한 실행도 별도
원시 파일에 남았다. 기록된 51개 실행의 wall 합계는 64.07초,
실행기 최대 RSS는 4020 KiB다. NCP의 별도 R9 약 12코어 작업은 유지했고,
이 실험은 순차 실행했다. `axbi_driver` Rust focused test 13/13 PASS다.
첫 진단 필드 추가 빌드 exit 101과 checkpoint 필드 기본값 수선도 원시
로그에 남겼다.

| 제어군 | N=128 Tgas (K) | N=32→64 대 N=64→128 온도 self-difference 차수 |
|---|---:|---:|
| 원래 BE `legacy_be` | 14988.7686442872 | 0.99999 |
| 광자·source 없음, BE | 14988.7611352303 | 0.99998 |
| 광자·source 없음, RR4 midpoint | 14988.7611350647 | 0.99998 |
| old/newborn 분리, BE | 14988.7686442899 | 0.99999 |
| 균일 출생 `phi1` | 14988.7686094260 | 1.02031 |
| old exponential + 균일 출생 | 14988.7686419803 | 0.99991 |
| 이전 항 + half-species opacity | 14988.7686419803 | 0.99991 |
| 이전 항 + RR4 midpoint | 14988.7686418143 | 0.99991 |

이 표의 차수는 같은 알고리즘의 해상도 사이 차이다. 독립 source-on
연속 RHS 기준해는 이번 단계에 없다. N=1024→2048과 N=64→128의 온도
차이 비는 `legacy_be` 0.06370, `full_exp_half` 0.06371,
`full_exp_half_rrmp` 0.06371이다. 광자수 비는 각각 약 0.0600,
0.0641, 0.0641이었다. RR4 midpoint의 HeIII 차이는 roundoff 영역이라
차수를 판정하지 않는다. N=128의 Newton 1e-13 진단은 기존 1e-11
결과와 출력된 T, 종, 광자 값에서 차이가 없었다.

40개 기본 실행 전 단계에 대해 최대 photon number residual은
`5.83e-22/H`, electron event residual은 `1.76e-13/H`, 전체 에너지
residual은 `7.14e-11 eV/H`, Newton residual은 `2.08e-12`였다. HI의
최솟값은 0.924998, HeI는 0.850000, Tgas 최솟값은 14988.761 K다.
직접 기록한 photoheating과 광자/결합 에너지로 재구성한 값의 최대 차이는
`1.28e-20 eV/H`다. RR/DR 냉각, binding, escaped radiation,
CI/CE/free-free, CMB 및 gas/photon geometry work는 CSV에서 분리돼 있다.
이 항등식은 회계의 수치적 일치이며 연속해 정확도의 증명은 아니다.

원시 archive `V10_NATIVE_RAW_20261016.tar.gz`는 7,273,697 bytes,
SHA-256 `822f176dabb2d554abfabd6c13cff5779b8ff35e541e62d1d8724d27b1aa1a32`다.
[NCP_RUN_RECEIPT.json](NCP_RUN_RECEIPT.json)은 각 실행의 명령 인자,
종료 marker, 출력 SHA 및 terminal 값을 기록한다. 분석 스크립트의
세부 숫자는 별도 `MATRIX_ANALYSIS.json` 결과에 묶는다.

## 잠정 판정과 다음 계산

`source-on 2차 수렴 = HOLD`: photon birth/old-photon 감쇠/half opacity와
RR4 midpoint를 함께 바꾸어도 이 짧은 구간의 Tgas self-difference 차수는
약 1이다. 광자 없는 군도 약 1이므로 원인을 photon birth 하나로
귀속하지 않는다. CI/CE/free-free/CMB의 endpoint 시간 배치, 기하 split,
source-age quadrature와 spectral threshold 횡단은 별도 측정이 필요하다.
다음 계산은 두 갈래로 진행할 수 있다. source-off에서는 별도 계약을
고정한 뒤 CI/CE/free-free/CMB의 endpoint 시간 배치와 기하 split을
분리한다. 이 검사는 GL2 source-age를 기다릴 필요가 없다. source-on에서는
HE25/26와 bass_cr C21B의 실제 proper-time GL2 source-age/cohort 및
moving-cut 처리를 같은 입력에 결합한 뒤 남은 collision/thermal 항을
하나씩 비교한다. 현재
균일 출생 커널은 midpoint geometry에서의 frozen-slab 제어이며 전체
source-age GL2는 아니다. Full EoR, Case-B 재수송, signed Bianchi는
이번 유한 구간에서 평가하지 않았다.
