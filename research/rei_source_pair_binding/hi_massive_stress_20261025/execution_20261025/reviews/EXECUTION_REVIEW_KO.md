# HI massive-stress 실제 실행 독립 검토

**판정: PASS_SCOPED_INDEPENDENT_R6_C9. 현재 finding 0, blocker 0.**

단위는 `HI_NATIVE_MASSIVE_STRESS_20261025`다. 실제 4,368개 HI 원자 측도와 선언된 전자 rest-energy 입력을 결속한 유한 stress·pressure source·질량 민감도 범위에서 독립 검토를 마쳤다. 부모가 최종 scoped admission을 소유하며, 이 기록의 작성 시점에 원시 결과의 admission은 `ROOT_PENDING`이다.

## 같은 독립 pass의 완료

실제 native task `/root/resume_independent_review`가 도구 중단 뒤 이전 `/root/source_and_review`의 미완료 R6/C9 pass를 이어받았다. 이전 `REVIEW.json`과 `INDEPENDENT_REVIEW_KO.md`는 역사적 snapshot으로 보존했다. 앞선 source·이론·초기 구현 검토 결과를 재사용하고, 현재 authority와 physmath 1.3.0 원문, frozen theory/contract, 수정 구간, 실제 저장된 코드·입력·manifest·raw·자원 기록을 읽었다.

새로운 광역 심사나 review-of-review를 열지 않았다. 검토자는 이론·구현 작성자가 아니며 새 science/test/project import/CAS/render/old replay는 모두 0이다. 실제 native child task가 존재한다는 것과 실행 모델명은 구별한다. 요청된 역할은 Astra-tier independent review이고 runtime model identity는 외부 관측 근거가 없어 `NOT_OBSERVED`다. CAS를 독립 모델 검토로 세지 않았다.

## R6C9-01 해소

`stress_source.py`의 `Interval.certified()`는 이제 두 endpoint의 수치와 `float.hex()` 표현이 모두 같아야 binary64를 확정한다. 따라서 정확한 구간 `[-2^-1100,+2^-1100]`의 `-0.0/+0.0`를 동일한 bit 표현으로 취급하지 않는다. 한쪽 부호만 가진 비영 underflow는 부호를 보존한다.

단일 실행의 `raw/stdout.jsonl`에는 다음 회귀 결과가 실제로 보존되어 있다.

| raw 항목 | 결과 | 해석 |
|---|---|---|
| `controls.tiny_crossing` | `ROUNDING_UNRESOLVED`, value `null`, exact_zero `false` | 영점 양쪽을 포함한 구간의 sign bit를 확정하지 않음 |
| `controls.negative_underflow` | `CERTIFIED_BINARY64`, value `-0.0`, `final_underflow_to_zero`, exact_zero `false` | 비영 음수의 최종 underflow와 부호 보존 |

음의 영점은 JSON의 실제 `-0.0` 표기와 실행된 `math.copysign` assertion으로 함께 확인된다. 따라서 R6C9-01을 **CLOSED_REPAIR_AND_ACTUAL_REGRESSION**으로 닫는다. 물리식·입력·정밀도·허용오차·예산 변경이나 추가 실행이 필요하지 않다.

## 실제 수용 결과

CSV와 이전 raw의 SHA는 frozen 입력과 일치한다. 이전 A/K/B/P 및 support maximum은 저장된 필드를 내용 그대로 재사용한다. 실행 경로가 기존 moment consumer를 호출하지 않으며 선택된 행은 4,368개다. mass decimal 입력은 `510998.95069 eV`, 민감도 점은 `510998.95053/510998.95085 eV`다.

세 질량 모두에서 W/S의 P160 구간은 P128 안에 있으며 폭 상계가 통과했다. 두 정밀도의 endpoint certificate가 유한하고 동일한 binary64라는 명시적 assertion이 실행되었다. 대체 계산식의 Decimal100 W/S 참조 6개는 P160 enclosure에 들어갔고, 최대 기록 상대차는 약 `9.06934e-17`로 고정 기준 `2e-15` 이하다. nominal과 endpoint pressure·synthetic source·JVP도 binary64 certificate를 반환했다.

`K≤W≤2K`, defect support bound와 D/W 상계, 질량 단조성 및 양쪽 concavity 검사는 올바른 보수적 interval endpoint를 사용한다. 실제 raw가 모두 통과했음을 기록한다. 여덟 control group은 손계산 W/S/D/pressure/source/JVP, empty/zero, signed enclosure와 cancellation, 이번 tiny crossing/negative underflow, adjacent-float unresolved, 잘못된 입력 거절, overflow 거절, pressure underflow/subnormal을 포함한다. 원래 L0 gate `2e-12`는 변경하지 않았다.

명목 질량의 관측값은 다음과 같다. W·pressure·D는 eV target⁻¹ proper_s⁻¹, S는 target⁻¹ proper_s⁻¹다.

| 수량 | 원시 결과의 certified binary64 |
|---|---:|
| W | `8.872364769167228e-12` |
| S = dW/dM | `1.5716050524387194e-22` |
| pressure injection W/3 | `2.9574549230557428e-12` |
| D = 2K−W | `8.031185484505185e-17` |
| D/W | `9.05191084164476e-6` |
| synthetic source, a=2, X=3 | `1.7744729538334456e-11` |
| synthetic JVP, da=−1, dX=2, dM=3 | `2.9574549239987056e-12` |

질량 endpoint W는 각각 `8.872364769167202e-12`, `8.872364769167254e-12`다. 정확한 interval 차를 먼저 계산한 뒤 확정한 forward 변화는 `2.5145680831146385e-26`, backward 변화는 `2.5145680846892634e-26`, uS는 `2.514568083901951e-26`이다. 표시된 endpoint float를 사후 빼서 이 작은 변화를 추정한 것이 아니다. 이 점들은 선언된 표준불확실성 sensitivity probe이며 보장된 신뢰구간으로 승격하지 않는다.

## 실행·증거 연결

실행 명령은 `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B focused_check.py`이며 task leaf가 cwd다. `ROOT_GO.json`은 실제 manifest `28b1a29c0fcec720deab69b99c5b914713495c79aa7f320993ac5125072f5d42`에 결속되어 있다. 실행 launcher의 manifest 검사, 단일 child 경로, 자원 제한과 wait4 receipt를 읽었다.

| 항목 | 관측 |
|---|---:|
| child 수 / 재시도 | 1 / 0 |
| exit code | 0 |
| CPU | `0.39529200000000003 s` |
| wall | `0.4002169160012272 s` |
| CPU / wall cap | `6 s` / `8 s` |
| max RSS | `15948 kB` |
| stderr | 0 bytes |
| old suite replay / child network calls | 0 / 0 |

stdout는 25,177 bytes, SHA `ac125413b7b5857009c78c84e8dc79dc7bb9673c79cb4e8fec389e47be0246b4`다. 실제 code/input/raw SHA readback은 해당 manifest/receipt와 일치했다. `RESULT_SUMMARY.json`의 mass results, sensitivity, control 목록이 읽은 raw와 내용상 같은 것도 확인했다. 해시를 numerical validity 대신 사용하지 않았다. 수치 판정은 enclosure, 불변식, reference agreement, 실제 실행 결과에 근거한다.

이번 새 단위의 cap은 통과했다. 이전 `10.110448 s / 10 s` 실패와 known partial before `10.765369 s`, whole-L0 `UNKNOWN_NOT_ZERO`, 원 누적 cap `NOT_FROZEN`은 그대로 보존한다. 이번 성공이 과거 초과를 지우거나 누적 비용을 0으로 되돌리지 않는다.

## 주장 범위와 종료

이 결과는 유한 HI source measure에 대한 massive stress·등방 pressure injection과 mass sensitivity를 지지한다. flux/STF의 정확한 0은 선언한 isotropic closure 아래의 값이다. thermal heat는 `null`이고 rest energy MA를 기존 에너지 ledger에 추가하지 않는다. synthetic a/X/JVP control은 실제 밀도나 초기 stock을 제공하지 않는다.

n_HI/time history, initial stock, geometry/time/frame, collision/stopping/photon supply는 unresolved다. `L4_ready=false`, `whole_model_completion=null`, ANGTHERM02 read-only, C23E conditional D43K, HE94 partial window, PHYS85 historical state를 유지한다. strong no-go 주장은 없다.

부모가 이 실제 raw와 최종 검토 기록을 읽고 scoped admission을 결정하면 된다. 이 동일 R6/C9 pass는 완료되었으며 추가 reviewer·광역 검사·추가 계산·다음 science unit을 요구하지 않는다. 기계가 읽을 상세 기록과 관측 identity는 같은 폴더의 `EXECUTION_REVIEW.json`에 있다.
