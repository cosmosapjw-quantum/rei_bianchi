# REI AX11 owner 연구 루프: 광자·반응·에너지 장부와 시계 반응

## 결론과 수용 판정

완료된 원 T0/T1 native 궤적에서 새 물리 관측량을 추출하고, 원 IGM 목표의
scenario·IC·결합 history owner로서 **ADMIT_SCOPED_SOURCE_QUALIFIED_PHYSICAL_CONSUMPTION**을
기록했다. 핵심 결과는 포화된 최종 HII fraction의 작은 변화와 누적 광이온화·재결합·
광자 에너지의 더 큰 변화가 공존한다는 것이다. 동일 경과 proper time에서 나타나는
HII 반응의 부호는 고정-a 성분과 시계 이동 성분으로 직접 분해했다.

새 진화 실행은0회다. 기존 AX08 다섯 baseline, continuation002와 이번 이전에 완료된
T1 ZERO/PLUS를 재실행하지 않았다. 새로 계산한 결과는 실제 저장 궤적에 대한 물리
consumer 산출물이다. **원 workflow10/17, 확장 DAG28/88**, 새 완료 node0을 유지한다.
AX11에는 D12 및 분리된 dt/dE/dmu 진화 검증 의무가 남아 있다.

수용 범위와 근거는 [OWNER_SCIENTIFIC_ADMISSION.json](OWNER_SCIENTIFIC_ADMISSION.json),
[결과 원자료](results_v1/SUMMARY.json), [native 시점 구간](localization_v1/LOCALIZATION.json)에
있다. 아래 수치는 이 세 산출물의 직접 계산값이다.

## 정본·원본·조사 범위

원 목표는 REI-AXBI-GOAL-20261014, 중앙 정본은
`research/rei-igm-goal-sync-20261116`의
`56dc609ea9b801c88d3364aed3eee140b3a20d46`이다. 시작과 closeout의 해당 HEAD가
같음을 원격 ref로 확인했다. 원17-file 물리 source corpus SHA256은
`d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185`다.

Scenario는 PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1, homogeneous non-tilted
axisymmetric Bianchi I, zbar20→4, primary-only H/He Case-A escape다.
CR/HH/RCT/secondary/molecules는 OFF다. Source escape fraction0.2, 원 초기조건과
clock·state를 유지했다. F05 OTS/F08 constant-H 결과의 상태를 이 궤적에 섞지 않았다.

이전 census를 재사용해7개 저장소의 현재2080개 branch head를 대조했다. 저장소별
head 수는 REI430, BASS428, VigilODE370, WU088_HH210, rec_bianchi221,
bass_cr246, BASS_HE175이며 새로 바뀐 head는21개였다. 관련 PR·commit·파일의
변경분을 읽었고 기존244 draft 전체를 재감사하지 않았다. [조사 기록](receipts/REMOTE_DELTA.json),
[원격 head 전체](receipts/CURRENT_REMOTE_HEADS.json), [closeout ref](receipts/CLOSEOUT_HEADS.json)를
보존했다. 이 unit의 후속 자체 commit은 별도 stage publication ledger로 추적한다.

대화 검색용 Personal Context는 unavailable을 반환했다. 주어진 대화와 저장소
handoff는 읽었지만 접근할 수 없는 private 대화의 전수조사를 주장하지 않는다.
기존9개 archive의 byte 검증을 재사용했고, 실제 Dropbox 폴더12개 항목은 끝까지
조회했다. 광범위 검색의 날짜 필터는 오래된 항목도 반환했으므로 검색 부재를
백업 부재로 해석하지 않았다. 세부 범위는 [donor 판정](DONOR_OWNER_ADMISSION.json)에 있다.

## 실제로 소비한 다른 저장소 결과

| 공급자 | 정확한 근거 | owner가 소비한 내용 | 범위 |
|---|---|---|---|
| VigilODE PR189 | `ba2793b7131fb5c9ab50cc696dbff8271ef3de55` | 원 controller의6개 오차성분, normalization floor, strict 승인/증가 조건 |12개 compact specimen의 최대값·결정·다음 step을 owner가 재현 |
| BASS geometry | `a0d0983fc31bf637b86b9c33fa1c472af004c5f5` | 원 H(a), t(a), b(a)와 정확한 배경 재사용 source 계약 |4097-node quadrature 유지; 측정 timing은 별도로 고정된 공급자 receipt 범위 |
| WU088_HH | 유지된 source-qualified HHe provider | 원 반응·열 source 해석 | 새 반응 channel 추가 없음 |
| BASS_HE | 유지된 escape/energy guard | 원 source·escape 의미 보존 | OTS state import 없음 |
| rec_bianchi | 기존 승인된 scalar photon 결과 재사용 | photon 진단의 제한 유지 | 신규 F08 polarized result는 공급자 범위 보존 |
| bass_cr / BASS TypeII | 신규 변경분의 scope 확인 | CR-OFF와 AXBI geometry 경계 유지 | 원 owner node와 연결되지 않는 확장은 유예 |

VigilODE의 초기 probe에서는 photon energy L1가 controller의 최대성분이고,
accepted199980 plateau의 세 probe에서는 photon number L1가 최대성분이다. 예를 들어
ZERO plateau에서 h=3.125e-6의 metric2.644638422e-6은 target1e-5의 승인 조건을
만족하지만 quarter-target2.5e-6보다 커서 step을 두 배로 늘리지 않는다. h를
절반으로 줄인 두 국소 defect ratio는2.61048,2.71718이다. 이 값은 해당 고정 parent의
국소 진단이며 전체 history의 수렴차수로 사용하지 않았다. 공급자의 raw native state
감사와 owner의 compact 데이터 재계산을 구분했다. [검산](audit_v1/AUDIT.json),
[공급자 profile](donors/vigilode/results/ERROR_COMPONENT_PROFILE.json).

## 광자와 에너지의 실제 수지

모든 photon count와 reaction event는 H nucleus당 누적 수다. Helium element fraction은
He nucleus 기준이므로 f_He=0.2454/[4(1−0.2454)]를 적용한다. 따라서 반복 이온화·
재결합이 있으면 누적 event 수가1을 넘을 수 있다.

zbar4의 T1 ZERO에는 주입된4.446590310528219 photons/H 중 다음과 같은 재고가 남는다.

| 항목 | photons/H | 주입 수 대비 |
|---|---:|---:|
| 남은 photon stock |2.2490922339691903 |50.58015416% |
| 누적 흡수 |1.5723076426430702 |35.35984952% |
| grid boundary 장부 |0.6251904339140475 |14.05999632% |

`boundary`는 실제 spectral grid-boundary 장부다. 공간적 escape fraction과 동일시하지
않는다. 열적으로 빠져나간 radiation energy와 source의 f_esc도 별도 양이다.
반올림 전 숫자로 재구성한 photon residual은 약−1.91e-12/H다.

동일 endpoint의 external source는90.16171261328917eV/H, initial energy는
0.00385176572207226835eV/H다. source+initial의 에너지 분배는 다음과 같다.

| 항목 | eV/H | source+initial 대비 |
|---|---:|---:|
| photon stock |44.7529430252 |49.63418499% |
| gas thermal |2.2177565280 |2.45964914% |
| gas binding |15.7115703545 |17.42524484% |
| escaped thermal radiation |8.4682298970 |9.39186701% |
| grid boundary |8.5025832822 |9.42996735% |
| thermal expansion work |3.4496200341 |3.82587306% |
| photon expansion work |5.2737171920 |5.84892606% |
| CMB cooling |1.7891440703 |1.98428755% |

원 signed CMB input이 음수이므로 이 분배표에서는 양의 cooling loss로 들어간다.
에너지 residual은 약4.22e-9eV/H이며 원 source-scaled ledger gate를 만족한다.
보존 수지는 물리적 장부 해석과 구현 확인에 쓰이고 진화 오차 추정치는 별도로 요구한다.
[전체 endpoint 수지](results_v1/endpoint_inventory.csv), [직접 유도](DERIVATION.md).

## 최종 ion fraction이 감추는 history 변화

T0→T1의 ZERO endpoint 변화는 다음과 같다. D01=T1−T0다.

| 물리량 | T0 | T1 | D01 |
|---|---:|---:|---:|
| x_HII |0.9999973170987931 |0.9999973196589066 |+2.56011e-9 |
| H photo events/H |1.4527271003 |1.4492450138 |−0.0034820864 |
| H radiative recombination events/H |0.4532802602 |0.4498134467 |−0.0034668135 |
| photon stock/H |2.2518080058 |2.2490922340 |−0.0027157719 |
| photon energy, eV/H |44.8043162973 |44.7529430252 |−0.0513732721 |
| escaped thermal energy, eV/H |8.4925368000 |8.4682298970 |−0.0243069031 |
| Tgas, K |7900.6213657 |7925.9696913 |+25.3483257 |

누적 H 광이온화와 재결합의 변화는 T1 값 대비 각각−0.240269%,−0.770723%다.
두 event 변화가 대부분 상쇄되어 포화된 최종 HII fraction의 D01은 작게 남는다.
이 결과는 원 IGM 목적에서 최종 fraction 외에 source absorption, recombination,
가열·냉각 history를 함께 비교해야 할 직접적인 근거다.

새 photon paired response도 추출했다. zbar4의 T1 PLUS−ZERO photon stock은
−4.119856800e-6/H이며 paired D01은−8.935493403e-7/H다. Photon energy response는
−7.355916034e-5eV/H, 그 D01은−1.227493388e-5eV/H다. 새로운 photon response floor를
만들어 검출을 선언하지 않았다. 최종 HII response−1.304956143e-12와 Tgas
response+0.00811650K는 각각 기존1e-7,0.01K floor 아래다. CSV의 상대비 열은
기술적 산술값이며 below-floor admission에 쓰이지 않는다.
[전체 D01](results_v1/endpoint_inventory_D01.csv), [floor 판정](audit_v1/AUDIT.json).

## 고정-a와 동일 proper time 반응의 연결

원 background에서 H_PLUS(a)>H_ZERO(a)이고 동일 초기 slice 이후
a_PLUS(t)>a_ZERO(t)다. 각 표현 가능한 query에서 다음 finite identity를 적용했다.

\[
\Delta_t X =
\underbrace{X_+(a_0(t))-X_0(a_0(t))}_{\text{fixed-a 성분}}
+\underbrace{X_+(a_+(t))-X_+(a_0(t))}_{\text{clock displacement}}.
\]

1001개 공통 시간 query 중953개가 보관된 PLUS native window로 a_ZERO(t)를
bracket한다. 나머지48개는 결과를 비워 두었다. 적합된 sparse curve를 통해
빈 구간을 메우지 않았다. 두1001-point response grid의 기존 gas 값28028개가
원 owner consumer와 bit 단위로 같음을 먼저 확인했다.

HII의 |동일-time 반응|이 가장 큰 표현 가능한 표본(t=2.5691720595e16s)은
a_ZERO=0.1494545693, a_PLUS=0.1494553060이다.

| 항목 | HII fraction response |
|---|---:|
| 실제 a_ZERO(t)에서의 fixed-a 성분 |−2.484578262e-6 |
| clock displacement |+1.959487732e-5 |
| 합: 동일-time 반응 |+1.711029905e-5 |

953개 중952개 표본에서 HII의 fixed-a 성분과 동일-time 반응의 부호가 반대다.
Tgas의 최대 표본에서는−0.01441577K+0.17005773K=+0.15564196K다. 동일 native
window에서 PCHIP와 linear-in-ln(a)의 최대 차이는 HII8.52e-10, Tgas1.71e-5K였다.
이는 보간 민감도이며 D12를 대신하지 않는다. [시계 분해 원자료](results_v1/T1_clock_decomposition.csv.gz).

## 재이온화 milestone의 native 시점 구간

처음 위로 통과하는 x_HII=0.1,0.5,0.9의 원 native 두 행을 사용했다. 두 case의
crossing이 각각 그 step 안에 있다는 조건에서 paired time 구간은
[t_PLUS,lo−t_ZERO,hi, t_PLUS,hi−t_ZERO,lo]다.

| x_HII | T1 paired 보간값, yr | T1 native paired 구간, yr | paired D01, yr |
|---|---:|---:|---:|
|0.1 |−3547.693 |[−3835.400,−1695.523] |−3.411 |
|0.5 |−5715.858 |[−9683.374,−2296.604] |−5.238 |
|0.9 |−6337.019 |[−10696.656,−1615.780] |+1.945 |

세 native 구간이 모두 음수다. 저장된 T1 궤적의 해당 first-upward milestone에서는
PLUS가 ZERO보다 먼저 도달한다는 부호가 보간 위치와 무관하게 유지된다. 이 구간은
실제 연속해의 enclosure나 unresolved intra-step recrossing의 배제가 아니다.
몇 년 크기의 paired D01과 수천 년 크기의 native localization을 별도로 보존했다.
T0 bracket을 이 consumer에서 확보하지 않았으므로 D01 구간을 만들어내지 않았다.
[직접 계산](localization_v1/NATIVE_CROSSING_INTERVALS.csv).

## 검증, 오류 보존, drift 판정

Producer를 import하지 않는 별도 parser·Decimal 산술·interpolation 구현으로
네 endpoint와953개 시계 분해를 검산했다. CMB 부호, helium 정규화, 누적 장부 중복,
strict controller boundary, 외삽, below-floor 상대 판정에 관한14개 의미 오류를
거부했다. Wolfram의 exact stoichiometric matrix에서도 H/He nuclei와 전하의 세
conservation row가 모두0임을 확인했다. 이 검증은 동일 작성자의 별도 구현과 도구
검산이며 독립 blind referee 판정으로 표시하지 않았다.

검산기 구현 오류2개와 Wolfram symbolic JSON export 오류1개를 보존했다. 물리
데이터나 원 tolerance는 바꾸지 않았다. 새 no-go theorem을 제시하지 않았으며
NG1–NG7은 그러한 주장의 부재에 따라 비적용으로 기록했다.
[Hostile review](HOSTILE_REVIEW.json), [실패 기록](audit_v1/ATTEMPTS.json).

Named consumer는 REI owner의 AX11 진화 검증이다. 이번 결과는 실제 source별
event/energy 및 두 clock 비교를 소비하는 데 기여한다. Census·문서·백업·검산
횟수는 과학적 진전 수에 넣지 않았다. 다음 진전은 native T2와 D12다. 변경 없는
대상의 재감사와 다른 geometry/closure 개발은 유예한다. [Watchdog](DRIFT_WATCHDOG.json).

## 다음 T2: 잘못된 binary 재사용 가정을 수정한 유한 실행안

준비 과정에서 기존 T1 production binary가 target2.5e-6, startup1e-4와 T1 cap을
hardcode한 사실을 확인했다. Stage4의 binary 재사용·build0 계획을 철회했다.
T2 전용 wrapper는 원 physical library와 출력 loop를 유지하며 target6.25e-7,
startup1e-10 및 승인 대상 자원 상한만 바꾼다. 새 native build1회와32 accepted의
복원 preflight가 필요하다. 현재 cloud에는 Rust compiler가 없으며 native build·
preflight·T2 continuation은 아직 실행하지 않았다.

기존 ZERO/PLUS T2_FLOOR_START의 성공한4096-step prefix를 재사용한다.20개 입력의
native·보관본 byte hash와 각4096번째 complete state trace가 일치했다. 기존
original-start reject-cap 실패와 unknown historical debit은 그대로 보존한다.

| 제안 항목 | 한도 또는 예상 |
|---|---|
| 대상 |T2 ZERO/PLUS 두 case, 최대2개 병렬 |
| 시간 예상 |T1 실제 비용×4의 조건부 예상: CPU합12.97h, job-wall합14.74h, 병렬 경과 약7.41h |
| science output 예상 |합31.43GiB; 상한 보장 아님 |
| CPU/job-wall cap |각 case39000s; aggregate 각각80000s |
| 누적 trial/RHS cap |합25000000 /200000000 |
| 출력·백업 |science64GiB + backup reserve64GiB |
| 실행 시작 상한 |build1회, preflight3회, full segment32회; retry0 |
| 예약 비용 |prepare600s + controller60s + postprocess1200s 포함; 최대예약79860s |

기존 T1 allocation은 T1 두 case로 닫혔다. 이 새 장기 T2 예산은 그 잔여분에서
자동 발생하지 않는다. `physmath-research-loop/references/REI_EXECUTION_POLICY.md`의
새 heavy allocation 규칙에 따라, 위 한정 실행안의 승인이 필요한 상태다. 입력·
source·명령·중단 규칙·반환 계약은 이미 [T2_RUNBOOK.md](T2_RUNBOOK.md),
[ALLOCATION.json](t2_package/ALLOCATION.json), [정정된 제안](T2_FINITE_PROPOSAL.json)에
준비했다. [검사 결과](audit_v1/T2_PACKAGE_AUDIT.json)는 source/input/static 범위다.

## 게시와 재현

이론 R1–R10과 구현 C1–C10을10개의 순차 checkpoint로 기록했다. 각 단계의
archive는 committed Git byte와 전수 비교했고, 원격 commit의 전체 tree identity를
local tree와 대조했다. 각 단계에서10/17,28/88을 유지했다.
[단계 기록](STAGE_LEDGER.json), [publication 영수증](receipts/PUBLICATIONS.json).

최종 publication과 provider upload는 자기 commit을 포함하는 순환 참조를 피하려고
별도 FINAL_DELIVERY 영수증과 다운로드 bundle의 최상위 HANDOFF에 기록한다.
원 PR377은 중앙 branch 대상 draft를 유지한다. 중앙 정본을 merge하거나 AX11을
완료로 변경하지 않았다. 재현 절차와 입력 dependency는 [REPRODUCE.md](REPRODUCE.md)에 있다.
