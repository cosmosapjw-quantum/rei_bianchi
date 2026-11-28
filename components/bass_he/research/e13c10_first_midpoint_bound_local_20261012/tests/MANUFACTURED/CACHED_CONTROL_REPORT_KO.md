# E13C10 cached-midpoint 수정의 제한된 추가 대조

## 수정 범위와 결과

N32 captured pilot의 raw admission 실패를 보존한 뒤, 동일한 원본 N/P/source/input에 묶인 midpoint 합계를 재사용하는 branch를 추가했다. 수학식은 동일하며, 새 branch는 midpoint 계수 평가를 생략하고 whole-cell Jet2 곡률만 다시 계산한다. 이 변경에 필요한 제조 문제 대조를 별도 `EXEC02_CACHED`로 첫 실행했고 **PASS / 실제 exit 0**을 얻었다. 기존 `EXEC01`이나 24회 uncached suite는 재실행하거나 덮어쓰지 않았다.

12개 기존 제조 문제의 N8 midpoint aggregate를 실제 `EXEC01/CONTROL_RESULTS.json`에서 읽었다. 원 raw 결과·receipt·control script의 SHA를 확인했고, 초기 후보와 계약은 `evidence/SOURCE_REVISIONS/INITIAL_N32`에 보존된 bytes를 당시 receipt의 SHA와 대조했다. 따라서 이전 통과를 현재 수정 후보의 실행으로 바꾸어 표시하지 않는다.

| 항목 | 실제 값 |
|---|---:|
| cached branch 문제/실행 수 | 12 / 12 |
| N, interval precision | 8, P60 |
| 독립 닫힌식 precision | P140 |
| 검사 통과/실패 | 941 / 0 |
| 신규 whole-cell 계수 평가 | 96 |
| 신규 midpoint 계수 평가 | 0 |
| uncached integrator 실행 | 0 |
| 기존 제조 suite 실행 | 0 |
| captured 계수 평가 / ODE / NCP | 0 / 0 / 0 |
| suite wall / CPU | 0.419446150 s / 0.419168747 s |
| 명령 전체 wall | 0.471834473 s |
| 해당 프로세스 peak RSS | 51,040 KiB |
| 최초 실패 / 재시도 | 0 / 0 |

## 새 branch에서 확인한 것

각 case의 동일 N과 정확 매개변수를 저장된 자료와 대조했다. 전달한 midpoint aggregate가 후보 출력에 그대로 보존되고 입력 dictionary도 바뀌지 않았음을 확인했다. 실제 제조 계수 객체는 Jet2 whole-cell 호출과 point 호출을 따로 셌으며, 모든 case에서 각각 N=8회와 0회였다. 결과의 cell evidence에도 새로운 midpoint value/term을 만들어 넣지 않았다.

17개 signed output은 독립 integrated-response 닫힌식 oracle을 모두 포함했다. 동일 N의 저장된 uncached curvature와 signed output에도 endpoints가 정확히 일치했다. 후자의 byte-equivalent 관계는 cache 분기의 동작 보존 검사이며, 독립 닫힌식 포함 검사를 대신하지 않는다.

검사 대상은 exact zero, frozen match, L=0와 L>0, opacity defect의 양·음 부호, nonzero species defect의 total cancellation, source off, quadratic 곡률 양·음 및 centered cubic 부호 전환을 포함한다. 각 문제의 nonzero incoming center/radius에 대해서도 독립 analytic gain으로 구한 `-eta`, `0`, `+eta` 값을 새 first enclosure가 포함했다. 실제 captured cache의 입력 결합 및 serial carry 전파 검증은 경로 wrapper와 독립 review의 별도 책임이다.

## Source identities와 원본 증거

- 수정 후보 SHA-256, 실행 전후 일치: `db59e9b696174fa9751a27c0d7502d5ba94cf6af2e634048c8d29615c4000344`.
- 수정 계약 SHA-256: `4fabab58bda4169ae18f341443e74a6f558af9addd09da787f66df8ea91c5bd4`.
- 이전 후보 SHA-256: `29203c91e01b7a439cd56b620b603fbe8bf843b2fdeef00c5e2c4f98bd5f6e09`; INITIAL_N32 원본과 EXEC01 receipt에 일치한다.
- 이전 control script와 oracle의 main을 호출하지 않고, pin을 확인한 독립 공식·evaluator 함수만 가져왔다. Python Decimal exp primitive의 공유 및 제조 모델이라는 독립성 한계는 EXEC01과 같다.

| 파일 | bytes | SHA-256 |
|---|---:|---|
| `run_cached_midpoint_controls.py` | 14,298 | `8f4f7cfbb5ada1deae35789f6a469a0b3211741a02aecb8adcff46faf0ac96a7` |
| `EXEC02_CACHED/CONTROL_RESULTS.json` | 428,942 | `d2373387437cba0d4216a19ba8694fa224319473feb002a7daf5edf556702a92` |
| `EXEC02_CACHED/RECEIPT.json` | 2,306 | `e79571396f3fe09afceb895d0c027f48f256f4c16f756cfebf2f96a2db5ee267` |
| `EXEC02_CACHED/COMMAND_RECEIPT.json` | 1,155 | `57496b4fccd26a115a94b58c10a8415651efad3b6830353986aecd1772e0ef0b` |

START, raw results, receipt, actual argv/exit, stdout 및 stderr를 모두 새 EXEC02_CACHED 폴더에 보존했다. 이 대조는 수정된 cache branch를 검증한 것이며, N32 captured admission 실패를 지우거나 full-population/physical claim을 높이지 않는다. 작성자는 source/control 기여자이고 최종 독립 reviewer가 아니다.
