# AX11: T1 ZERO/PLUS native 이력과 실제 D01 수용

원 목표는 **REI-AXBI-GOAL-20261014**이고, consumer는
**rei_bianchi scientific admission owner / AX11**이다. T1 ZERO와 PLUS를
동일한 물리적 zbar20 초기조건에서 zbar4까지 실제 실행했다. 원래 T0 자료를
재사용하여 고정 a와 동일 경과 proper-time 각각 1001점에서 두 수준의 차이를
계산했다. 두 native 이력과 이 비교 자료를
`ADMIT_T1_TWO_CASE_NATIVE_HISTORY_AND_SAMPLED_D01_ONLY`로 수용한다.
원 DAG **10/17**, 확장 **28/88**이며 새 완료 노드는 0이다.
[Owner 판정](OWNER_ADMISSION.json), [실행 ledger](receipts/CLOSED_RUN_LEDGER.json),
[비교 결과](results_v1/SUMMARY.json).

## 고정된 물리와 실제 실행

중앙 정본은 `56dc609ea9b801c88d3364aed3eee140b3a20d46`이다.
시나리오 `PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1`의 homogeneous,
non-tilted axisymmetric Bianchi I, primary-only H/He Case-A escape를 유지했다.
CR/HH/RCT/secondary/molecules는 OFF다. T0의 local target=1e-5에서
T1=2.5e-6으로 time refinement를 수행했고 energy16, mu8, background4096,
source, IC, 원래 보존 허용오차와 저장할 scientific outputs를 유지했다.
기존 AX08 다섯 baseline과 원래 continuation002는 재실행하지 않았다.
[설정·출처 계약](SCIENCE_CONTRACT.md), [source identity](SOURCE_BINDING.json),
[T0 재사용](receipts/BASELINE_REUSE.json).

| Case | q_ref | Accepted | Trials | RHS | 최종 a | 종료 |
|---|---:|---:|---:|---:|---:|---|
| ZERO | 0 | 757,073 | 2,271,279 | 15,898,977 | 0.2 | exit 0, native zbar4 |
| PLUS | +0.01 | 757,073 | 2,271,279 | 15,898,977 | 0.2 | exit 0, native zbar4 |

각 case는 250000+250000+250000+7073 accepted의 네 segment로 이어졌다.
모든 continuation의 전체 checkpoint identity와 경계 상태를 확인했다.
중복 경계 행만 제외한 각각 **757,074개 native 상태**를 소비했다.
원래 sampling query 1001개가 두 좌표 방식에서 모두 표현되었다.
[Native 추출 receipt](native_inputs/EXTRACTION_RECEIPT.json).

## 절대 이력 변화와 이온화 시점

여기서 D01=X(T1)-X(T0)다. 아래 최대값은 원래의 공통 1001점 표본에서의
최대 절댓값이며, 연속 구간 supremum이나 참오차의 인증값으로 정의하지 않는다.
두 case의 큰 공통 변화와 작은 PLUS−ZERO 반응을 각각 보존했다.
[Fixed-a 원자료](results_v1/comparison_fixed_a.csv.gz),
[Fixed-time 원자료](results_v1/comparison_fixed_t.csv.gz).

| 관측량 | 고정 a: ZERO의 최대 \|D01\| | 고정 a: PLUS의 최대 \|D01\| | ZERO 최대의 zbar |
|---|---:|---:|---:|
| x_HII | 0.005495827614 | 0.005495852962 | 5.739161386 |
| x_HeII | 0.003534465476 | 0.003534474814 | 5.690978129 |
| x_HeIII | 0.00002789974445 | 0.00002789976857 | 4 |
| xe/H | 0.005770128225 | 0.005770152548 | 5.739161386 |
| Tgas [K] | 75.39852351 | 75.39878412 | 5.586184130 |

x_HII의 최대 변화는 음수다. 동일 a에서 T1의 이온화가 T0보다 덜 진행된
구간이 있으며, 실제 첫 상향 crossing도 늦어졌다. ZERO의 결과는 다음과 같다.
PLUS의 대응 변화는 [전체 milestone 표](results_v1/milestone_T0_T1.csv)에 보존했다.

| local x_HII | T0 crossing zbar | T1 crossing zbar | T1−T0 elapsed proper-time [Myr] |
|---|---:|---:|---:|
| 0.1 | 10.248068402 | 10.234817730 | +0.806439107 |
| 0.5 | 6.816991168 | 6.802775487 | +2.148358780 |
| 0.9 | 5.804537190 | 5.794711153 | +2.097361669 |

T1의 native crossing bracket 폭은 각각 약 1070, 3693, 4540년이다.
각 case·threshold에서 상향 crossing은 정확히 하나였고 추가 상향 교차는
없었다. 이 값은 local element fraction의 crossing이며 공간 충전율 QV의
재이온화 시점으로 바꾸어 부르지 않는다.
[전체 crossing 표](results_v1/all_upward_crossings_T1.csv).

원래 empirical full-history fraction absolute scale 0.001보다 큰 변화가
x_HI/x_HII에서는 각 case의 **301/1001점**, x_HeI/x_HeII에서는
**78/1001점**에서 나타났다. 두 좌표 방식의 개수는 같다. x_HeIII는 이
scale을 넘지 않았다. xe와 Tgas에 새로운 절대 허용오차를 만들지 않았다.
이 결과는 T0와 T1 사이의 관측된 변화이며, 어느 한 수준의 참오차로
전부 배정하지 않는다. 기존 AX08의 conditional baseline admission을
보존하면서 AX11의 추가 정확도 의무에 이 자료를 사용한다.
[원래 기준의 실제 소비](OWNER_ADMISSION.json).

최종 zbar4에서는 ZERO의 x_HII가 T0=0.9999973170987931,
T1=0.9999973196589066으로 차이가 2.5601e-9에 불과하다.
그러나 같은 이력의 중간 변화는 0.00550에 이른다. 따라서 이 사례의
endpoint 일치만으로 전체 이력의 정확도를 판정할 수 없다.
최종 ZERO 온도는 T0=7900.6213657 K, T1=7925.9696913 K이며
T1−T0=25.3483257 K다. [비교 표와 최대값](results_v1/SUMMARY.json).

## Paired 반응의 변화와 두 clock의 의미

Delta_k=X_PLUS(Tk)-X_ZERO(Tk), D01_pair=Delta_1-Delta_0로 계산했다.
각 물리량에 대해 개별 D01_ZERO, D01_PLUS와 D01_pair를 함께 저장했다.
정확한 산술에서는 D01_pair=D01_PLUS-D01_ZERO이므로, 공통 변화의 상쇄가
큰 절대 상태 변화를 가릴 수 있다. 이 항등식은 각 상태의 정확도를 대신하는
조건으로 사용하지 않는다. [정의와 단위](SCIENCE_CONTRACT.md).

아래 ratio는 T1 반응이 원래 floor 이상인 각 표본에서 계산한
|D01_pair|/|Delta_1|의 최대값이다. 기준 초과 개수는 ratio>0.1인 표본 수다.
분수 floor는 1e-7, 온도 floor는 0.01 K이며 electron floor는 전하 관계를
따라 전파했다. 두 수준의 변화 진단으로 기록한다.

| 좌표 | 관측량 | 최대 \|D01_pair\| | 최대 ratio | 0.1 초과 / floor 이상 |
|---|---|---:|---:|---:|
| fixed a | x_HII | 7.7052242e-7 | 0.76523 | 5 / 766 |
| fixed a | x_HeII | 3.9015024e-7 | 0.69653 | 5 / 768 |
| fixed a | Tgas [K] | 0.011390237 | 0.43894 | 3 / 753 |
| equal elapsed t | x_HII | 5.3689743e-6 | 0.76296 | 7 / 682 |
| equal elapsed t | x_HeII | 2.7161746e-6 | 0.86040 | 8 / 877 |
| equal elapsed t | Tgas [K] | 0.081525190 | 3.65807 | 5 / 791 |

주요 paired 차이의 최대는 fixed-a zbar=5.6240997735, 또는 원래 fixed-t
표의 elapsed time=2.6166549033e16 s 부근에 모였다. 대부분의 floor 이상
표본에서는 두 수준의 변화가 10% scale보다 작지만, 이 국소 구간 때문에
전체 이력에 대한 기준 통과를 발행하지 않는다.
[Owner 판정](OWNER_ADMISSION.json), [실제 반응 그림](results_v1/responses.png),
[개별·paired 변화 그림](results_v1/discrepancies.png).

T1 x_HII의 PLUS−ZERO 반응은 주요 이온화 구간의 fixed-a 비교에서
음수이고 최대 절댓값은 2.49344e-6이다. Equal elapsed-time 비교의 주요
반응은 양수이며 최대는 1.71103e-5다. 서로 다른 slice의 비교다.
선택된 배경에서 H_PLUS(a)>H_ZERO(a)이므로 같은 elapsed time의
a_PLUS(t)는 a_ZERO(t)보다 크다. 두 항을 더하고 빼면 정확히

    X_PLUS(a_PLUS(t)) - X_ZERO(a_ZERO(t))
      = [X_PLUS(a_PLUS(t)) - X_PLUS(a_ZERO(t))]
        + [X_PLUS(a_ZERO(t)) - X_ZERO(a_ZERO(t))]

가 된다. 첫 항이 clock에 따른 이동이고 둘째 항이 같은 a의 반응이다.
이온화가 증가하는 구간에서 clock 이동이 fixed-a 억제를 넘어서는 것은
두 데이터의 서로 다른 부호와 양립한다. 이 설명은 source·clock·상태를
교환하지 않으며 F05 OTS/F08 constant-H 결과를 섞지 않는다.
[고정된 배경](../rei_axbi_owner_loop_20261115/ORIGINAL_SCENARIO_LOCK.json).

## 적대적 검증과 수용 범위

검증은 동일 저자가 수행한 별도 semantic audit다. 독립된 blind referee
검토를 받았다고 기록하지 않았다. Producer의 summary 계산 함수를 가져오지
않고 실제 CSV에서 차이의 정의, 핵종·전하 항등식, 최대값, 좌표, 실행 수와
종료, 원래 resource cap 및 UNKNOWN 누적 비용의 보존을 확인했다.
[감사 코드](harness/audit_t1_response.py), [실행 판정](receipts/ADVERSARIAL_AUDIT.json),
[실제 명령·종료 기록](receipts/CLOUD_ANALYSIS_EXECUTION.json).

모든 native 상태의 핵종·전하·공변 수소 밀도 잔차는 3.33e-16 이하였다.
모든 저장 ledger batch를 원래 tolerance로 검사했다. 최대
|residual|/tolerance는 ZERO/PLUS 각각 photon count가
5.27e-5/3.34e-5, augmented energy가 0.01569/0.01550,
reflection-odd moment가 6.90e-4/5.83e-4 이하였다.
Fixed-t 보간의 t→ln(a)→t roundtrip 최대 차이는 8 s였다.
이들 보존·보간 수치는 진화 오차 상계와 별도로 기록했다.
[Native receipt](native_inputs/EXTRACTION_RECEIPT.json),
[semantic audit](receipts/ADVERSARIAL_AUDIT.json).

T1 PCHIP−linear paired contrast의 최대는 fixed-a x_HII에서 6.72e-10,
Tgas에서 1.115e-5 K, fixed-t에서는 각각 8.10e-10과 1.337e-5 K다.
이번 paired D01 최대보다 작지만, 이는 **T1 보간 방법 민감도**다.
T0 보간의 검증이나 엄밀한 보간·진화 오차 상계로 확대하지 않는다.
[방법과 scope](SCIENCE_CONTRACT.md), [수치 결과](results_v1/SUMMARY.json).

이번 수용 범위는 두 새 native 이력, 일곱 gas 관측량의 sampled D01,
crossing과 실제 비용이다. D12, 관측 수렴 차수, dt/dE/dmu의 원래 세 수준
검증, 남은 원래 관측량 및 최종 AX11 수용은 열려 있다. Photon TCshift나
shear 진단을 gas/abundance 오차 상계로 사용하지 않았다. 원래 목표와
무관한 새 전역 theorem을 선행조건으로 추가하지 않았다.

## 비용, 백업, 다음 소비

본 T1 두 이력만으로 accepted=1,514,146, trials=4,542,558,
RHS=31,797,954, CPU=11,672.92 s, 합산 process-wall=13,268.872744 s를
사용했다. 준비·controller 예약 및 실제 추출·archive 비용을 포함한 이번
native allocation debit은 CPU=11,922.53 s, 합산 wall=13,552.735295 s다.
각 한도 18,000 s 안이며, 이전 전체 누적 비용의 UNKNOWN은 유지했다.
[완료 비용 기록](FULL_NATIVE_COST.json), [후처리 비용](receipts/POSTPROCESS_LEDGER.json).

T1 한 case의 실측 trial은 2,271,279다. 동일 작업량 12회 상당량은
27,255,348 trial이며, 기존 baseline12회 상당량 11,241,216 trial과
구분된다. 둘 다 서로 다른 dt/dE/dmu 전체 행렬의 비용 예측은 아니다.
폐기된 12run·780만 trial 예산을 다시 사용하지 않는다.
Inclusive output_batch 시간 비중은 전체 T1 이력에서 ZERO 약84.78%,
PLUS 약83.18%였다. 이 scope는 중첩되며 특정 내부 연산 하나의 비용으로
전부 귀속하지 않는다. [측정과 해석 제한](FULL_NATIVE_COST.json).

원본 case 출력 8,435,762,880 bytes를 보존했고, 총 1,754,912,733 bytes의
9개 manifested archive 및 matching native Dropbox 사본을 만들었다.
Control/source/preflight/analysis archive는 provider에서 실제 복원하여
native SHA256 및 Dropbox content hash와 일치를 확인했다.
나머지 raw archive도 모두 provider에서 실제 바이트를 읽어 native SHA256 및
Dropbox content hash와 일치를 확인했다. **9/9 archive, 총1,754,912,733 bytes**다.
[전체 provider 검증](receipts/PROVIDER_BACKUP_VERIFICATION.json).
[Native backup receipt](receipts/NATIVE_BACKUP_RECEIPT.json),
[control 복원 근거](receipts/CONTROL_PROVIDER_RESTORE.json).

다음 과학적 의무는 동일 물리적 IC의 native T2 ZERO/PLUS와 그 D12다.
실측 비용으로 별도 유한 실행량을 정한 뒤 진행하며, 이번 wave의 남은
예산을 새 T2 자동 실행 권한으로 해석하지 않는다. 기존 T2 startup 실패와
그 뒤 승인된 좁은 startup 진단은 앞 연구 단위에 그대로 보존했다.
Energy와 angle의 분리된 의무, 음의 shear와 half-amplitude의 별도
오차 근거도 유지한다. AX12 FESC_025/TGAS20K는 이 wave에서 시작하지 않았다.
[재개 지점](HANDOFF.md), [drift watchdog](DRIFT_WATCHDOG.json).

과학 결과 공개 pin: `f75c35360d64420a840df6454c88ef0c7f1f2d4c`,
tree `ee6c30f63fb2d912bfadb400a33b3d93b746b9db`. 최종 backup/handoff 변경은
이 과학 자료의 바이트나 수치를 바꾸지 않는다. [게시 receipt](receipts/SCIENCE_PUBLICATION.json).
