# PHYS30 실제 단일 재현 결과

**REPLAY_PASS / implementation-verified.** Root가 최초 main 1회의 실제 성공과 동결 입력 보존을 확인한 뒤 명시적으로 승인한 별도 경로 replay를 정확히 한 번 실행했다. 이 기여자는 과학적 `PROMOTE`를 판정하지 않는다.

## 실제 실행

| 항목 | 관측값 |
|---|---|
| 시작 UTC | 2026-10-11T08:37:44.820464+00:00 |
| 종료 UTC | 2026-10-11T08:37:44.882153+00:00 |
| subprocess wall time | 0.06169016000058036 s |
| 실제 exit | 0 |
| timeout / launch error | false / null |
| 새 replay main | 1회 |
| 결과 | 56/56 grouped checks PASS |
| 최초 raw와 재현 raw | bytes 및 parsed JSON 모두 동일 |
| stderr | 0 bytes |

실제 child command는 다음과 같다. 실행 cwd는 `/workspace/scratch/603081e41728/phys30_single_replay_20261011/runtime`이었다.

```text
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B contributions/numerics/profile_second_order.py --output /workspace/scratch/603081e41728/phys30_single_replay_20261011/run/PROFILE_SECOND_ORDER_REPLAY.json
```

30초 timeout을 유지했다. Python은 3.12.14이며, 기록된 interpreter 경로·버전·platform이 최초 실행 기록과 일치했다. 재현 호스트는 공유 클라우드 작업공간의 `32d990e06a18`이다. `PYTHONDONTWRITEBYTECODE=1`을 설정했고 원래 candidate·protocol·tolerance는 바꾸지 않았다.

## 복원과 identity

새 경로가 존재하지 않음을 확인한 뒤 frozen payload 14개와 원래 경로의 `contributions/numerics/PREEXECUTION_FROZEN.json` 1개를 ZIP으로 만들고 복원했다. ZIP의 정확하고 중복 없는 15개 member, 안전한 상대 경로, 일반 파일 유형, mode와 실제 bytes를 검사했다. 실행 전후에 복원된 정확한 파일 집합과 각 payload의 SHA256·bytes·mode·원본 bytes가 모두 일치했고, 원본 동결 파일과 manifest도 그대로였다. 출력과 로그는 runtime의 형제 `run`에 기록했다.

| 실제 artifact | bytes | SHA256 |
|---|---:|---|
| `PHYS30_PORTABLE_STAGE.zip` | 95,832 | `0183316b6d39cc9c83519c5eaadb4ce06f215ff67bbbd759c6c4c1864c648f02` |
| `REPLAY_RECEIPT.json` | 26,650 | `24d524143200502d2039fe9695cc9dc23d2be325833f81cb47a1bcdab1e7e950` |
| `raw/PROFILE_SECOND_ORDER_REPLAY.json` | 231,082 | `5184af6139423792abc0a95e53bd5ccabca459820761aa1a3f350bda4ac7082e` |
| `raw/replay.stdout.txt` | 1,459 | `2524b624055df99ea597e8ea3a1f0ad84a16a1204743026bd0b1302b163b41d2` |
| `raw/replay.stderr.txt` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

`raw/`에는 실제 별도 경로의 결과·stdout·stderr와 bytes·mode가 같은 복사본을 남겼다. 최초 raw와 재현 raw의 SHA256은 같다. 이 노트의 판정 근거는 준비 템플릿이 아니라 실제 `REPLAY_RECEIPT.json`과 보존된 raw다.

## 실행 예산과 의미

재현 프로그램의 실제 counter는 최초 실행과 동일했다. 이번 replay 안에서 cached affine 갱신 4개, cached 이변수 응답 series 4개, cached 모멘트 series 4개, 정확 profile 다항식 모멘트 적분 6개, 정확한 비영 A 이차 toy branch 4개를 수행했다. 이들은 한 번의 승인된 main 안에 있는 고정 대수 계산이며, 물리 커널·도함수·에너지 노드·물리 근 탐색/보정은 모두 0개다. old PHYS19–29 import/main, old suite replay, quadrature, finite difference, sweep, derivative-sign campaign, native, gas IVP, dense LP도 모두 0이다.

최초 실행과 이번 replay를 합쳐 새 main은 2회다. 추가 main이나 자동 재시도는 없었다. 결과의 일치는 같은 호스트와 Python에서 분리된 경로로 원본을 운반·복원한 구현 재현성의 증거다. 다른 알고리즘이나 독립 물리 자료에 대한 검증 지분을 추가하지 않으며 **independent physics credit는 0**이다. root가 전체 소스를 검토한 기록을 인수했고, 이 기여자는 추가 물리 유도·과학 검증 설계·최종 승격 판단을 수행하지 않았다.

Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED를 유지한다. Production source/default/runtime 변경은 0이다. 필수 단일 재현을 마쳤으므로 이 contributor의 실행을 종료하고 최종 판정자에게 실제 증거를 넘긴다.
