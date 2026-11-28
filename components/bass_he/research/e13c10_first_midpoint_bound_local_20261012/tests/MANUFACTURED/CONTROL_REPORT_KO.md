# E13C10 first-integral 독립 닫힌식 대조 결과

## 결과

고정 후보 `code/first_midpoint.py`에 대한 새 제조 문제 대조를 **첫 실행에서 통과**했다. 12개 문제를 N8과 N32에서 한 번씩 실행했으며, 실제 하위 프로세스 종료 코드는 0이다. 총 24회 first-integral 호출에서 2,290개 검사가 모두 통과했다. 최초 실패, 수리, 재시도는 없다.

후보 SHA-256은 실행 전후 모두 `29203c91e01b7a439cd56b620b603fbe8bf843b2fdeef00c5e2c4f98bd5f6e09`이다. 원래 E13C7 Context를 통한 source-lock·입력 파일 게이트 후, 제조 계수 객체만 새 적분기에 전달했다. 기존 E13C9 제조 suite의 main, 기존 captured first quadrature, ODE 또는 NCP 실행은 호출하지 않았다.

| 항목 | 실제 값 |
|---|---:|
| 제조 문제 수 | 12 |
| 실행 수 | 24 = 12 × N8/N32 |
| 검사 통과/실패 | 2,290 / 0 |
| 제조 계수 평가 수 | 960 |
| captured 계수 평가 수 | 0 |
| 완료된 과학 작업 replay | 0 |
| 후보 interval precision | 60 decimal digits |
| 닫힌식 oracle precision | 140 decimal digits |
| suite wall time | 1.609321397 s |
| suite CPU time | 1.609203963 s |
| 명령 전체 wall time | 1.671111365 s |
| 해당 프로세스 peak RSS | 51,588 KiB |
| 실제 exit code | 0 |

## 무엇을 확인했는가

모든 문제·해상도 조합에서 17개 signed first-variation 적분 구간이 독립 닫힌식 값을 포함했다. 광자 수, 에너지 및 세 종의 heat ledger도 0을 포함했다. 실제 rate와 source의 비음수성 및 incoming uncertainty까지 포함한 초기 광자 수의 비음수성은 정확 Fraction 자료로 확인했다.

양의 opacity defect에서는 첫 광자 correction의 부호가 음이고, 음의 defect에서는 양이었다. 종별 defect가 서로 상쇄되어 `sum(dl)=0`인 문제에서는 광자 correction이 정확히 0인 동시에 HI와 HeI의 개별 흡수 correction은 각각 양·음으로 남았다. source-off/nonzero-stock 문제는 source number/energy가 정확히 0이면서 다른 correction이 존재하는 경우를 확인했다. frozen-match와 exact-zero 문제의 17개 local integrals는 모두 정확히 0이었다.

각 문제는 별도로 유도한 analytic incoming gain과도 대조했다. 후보의 local first integral에 gain을 더한 affine enclosure가 incoming error `-eta`, `0`, `+eta`에서 모두 닫힌식 결과를 포함했다. 이 검사는 first local integral이 zero-incoming 대상이라는 의미와 analytic uncertainty gain을 확인한다. 새 captured path 조립기의 seam·carry·Volterra remainder 전체를 대체하는 검사는 아니다.

## 곡률 부호를 실제로 유지하는가

`L=0`, `dq(u)=±u²`, `h=1/2`에서는 정확한 photon/source first integral이 `±1/24`이다. 양·음 두 경우 모두 N8과 N32에서 폭이 `1e-61`인 구간으로 해당 값을 포함했고, curvature correction도 각각 양·음 부호를 유지했다. 따라서 절대값을 취해 대칭 오차를 더하는 구현이나 잘못된 곡률 부호를 실질적으로 구분한다.

`dq(u)=(u-1/4)³`, `h=1/2`의 정확 photon/source 적분은 0이다. 부호가 바뀌는 곡률을 그대로 포함한 결과의 photon halfwidth는 N8에서 약 `1.52587890625e-5`, N32에서 약 `2.384185791015625e-7`였다. 이 특정 매끄러운 제조 문제의 64배 감소는 실제 저장된 구간의 진단이며, 일반 C² 함수의 보편적 수렴 차수나 captured 물리 문제의 수렴률을 주장하지 않는다.

## Oracle 독립성과 한계

상수 계수 문제의 oracle은 `Y'=dq-dL*Pf-L*Y`, `Y(0)=0`의 닫힌식을 먼저 얻고, `int Y`, `int E*Y`, `int Pf`, `int E*Pf`를 이용하여 17개 결과를 조립한다. 후보의 원래 kernel을 같은 quadrature로 다시 계산하지 않는다. `L=0`은 다항식 극한으로 직접 처리했다. 추가 다항 forcing 문제는 정확 유리수 primitive와 지수 가중 모멘트의 닫힌식 recurrence를 사용했다.

P140 interval evaluator와 일부 elementary closed-form utilities는 검증된 E13C9 oracle source에서 pin을 확인한 뒤 가져왔다. 해당 기존 suite를 실행하거나 수정하지 않았다. 후보와 oracle은 exact 입력 값과 Python Decimal의 exp primitive를 공유한다. 따라서 수학적 식과 evaluator의 독립 대조이며, 독립 물리 계수 모델이나 형식 증명은 아니다. 작성자는 source/control 기여자이며 최종 독립 admission reviewer가 아니다.

## 원본 증거

| 파일 | bytes | SHA-256 |
|---|---:|---|
| `run_first_integral_controls.py` | 18,479 | `1b29d5a81d68df8ae58e2bcc4e41cfb02494bd3af9ba52f4f9de9d9daad10521` |
| `EXEC01/CONTROL_RESULTS.json` | 909,432 | `5014c049c9b900e77dbbd64557cf92872ac7dcf4c7ccdcd589475e461018beb4` |
| `EXEC01/RECEIPT.json` | 2,801 | `7c0aa57ac61774096611ea38255bb68d0f001926475d2482d64e307a42bf6233` |
| `EXEC01/COMMAND_RECEIPT.json` | 1,336 | `6633e484e3aa012c376085242e7a68512b222e71096d47d9e991937bec472368` |

START에는 후보·계약·script·oracle identities를 기록했고, COMMAND_RECEIPT에는 실제 argv와 UTC 시작/종료·exit를 보존했다. stdout과 stderr도 같은 EXEC01 폴더에 그대로 보존했다. 이 결과의 claim ceiling은 제조 문제의 first-integral 구현 검증이다. E13C10 selected captured admission은 별도 실제 경로 결과와 최종 독립 결정으로 판단한다.
