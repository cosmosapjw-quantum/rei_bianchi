# PHYS27 단일 재실행과 입력 복구 기록

## 결과

**PORTABILITY_PASS — 동결된 PHYS27 프로그램을 새로운 디렉터리에서 정확히 1회 재실행했고, 첫 결과와 전체 바이트 및 파싱된 JSON이 일치했다.** 이는 관측한 Python 3.12.14 환경에서의 재현성에 대한 `implementation-verified` 결과다. 독립 물리 증거로 추가 계상하지 않으며, 최종 연구 승격 판정도 수행하지 않았다.

`REPLAY_RECEIPT.json`이 실제 명령, 환경, 복구 경로, 파일 정체성, 종료 코드, 시간, 출력 비교 및 계산 횟수를 담는다. 원 결과와 재실행 결과는 모두 305,521 바이트이며 SHA-256은 다음과 같다.

`3b2c71b7c2d650ac92e78e6eed041039ddd41f0d9e48cdfa95d9ebfec1448314`

## 먼저 동결한 재현 입력

`PHYS27_PORTABLE_STAGE.zip`에는 원 수치 사전 동결 목록의 13개 파일, 그 목록을 담는 `PREEXECUTION_FROZEN.json`, 그리고 비교 대상인 `FINITE_WIDTH_FIRST.json`을 넣었다. 과거 PHYS26 코드가 포함되는 이유는 원 PHYS27 동결 목록이 그 파일의 정체성도 요구하기 때문이다. 이 작업에서 해당 코드를 import하거나 실행하지 않았다.

따라서 ZIP은 **15개 payload와 내부 `MANIFEST.json` 1개**로 이루어진다. 단계 묶음은 131,648 바이트이며 SHA-256은 `dd0db43f6b4809764964a433a241b81c53e9ebb67f4aa07f12a29b4d5e327409`이다. 내부 manifest의 바이트는 외부 `STAGE_MANIFEST.json`과 같다. 압축 전 파일, ZIP 내부 파일, 복구 후 파일의 바이트를 보존했으며 텍스트 줄바꿈을 정규화하지 않았다.

재실행 전에 `PORTABILITY_PROTOCOL.json`과 `PORTABILITY_PREEXECUTION_FROZEN.json`을 작성했다. 동결 시점에 portability 재실행 횟수는 0이었다. 프로토콜은 wrapper의 정체성, stage ZIP과 manifest의 정체성, 정확한 비교 기준, 새 복구 디렉터리 요구, 최대 1회 실행, 실패 보존 및 재실행 금지를 고정한다.

## 실제 수행

다음 명령을 `/workspace/scratch/603081e41728/phys27`에서 한 번 실행했다.

```bash
python3 portability/repro.py --replay --destination /workspace/scratch/603081e41728/phys27_portability_fresh_20261011 --record-prefix /workspace/scratch/603081e41728/phys27/portability/REPLAY
```

복구 전 존재하지 않았던 디렉터리를 생성했고, **15/15 payload의 SHA-256과 크기를 복구 전후 확인했다.** 상대 경로를 그대로 유지했으므로 원 프로그램의 `Path(__file__).resolve().parents[2]`가 새 프로젝트 루트가 되었다. 첫 결과 파일은 비교 대상으로 보존하고, 프로그램에는 새 출력 경로 `contributions/numerics/FINITE_WIDTH_REPLAY.json`을 전달했다.

실제 새 프로그램 명령은 다음과 같다.

```bash
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 /workspace/scratch/603081e41728/phys27_portability_fresh_20261011/contributions/numerics/finite_width_envelope.py --output /workspace/scratch/603081e41728/phys27_portability_fresh_20261011/contributions/numerics/FINITE_WIDTH_REPLAY.json
```

시작은 `2026-10-11T04:34:15.423727+00:00`, 종료는 `2026-10-11T04:34:18.047678+00:00`이다. 관측한 실행 시간은 2.622226280000177초, 종료 코드는 0이다. `REPLAY_STDOUT.txt`는 1,254 바이트이며 `REPLAY_STDERR.txt`는 빈 파일이다. 재실행 결과의 별도 보존본은 `REPLAY_RESULT.json`이다. 전체 바이트 동등성과 전체 JSON 동등성을 각각 확인했고 두 비교 모두 `true`였다.

## 실행 횟수의 해석

| 항목 | 원 첫 과학 실행 | 이번 재현 실행 |
| --- | ---: | ---: |
| PHYS27 main 호출 | 1 | 1 |
| 새 물리 근을 위한 탐색 | 2 | 동일한 2개 재현 |
| 각 물리 근의 이분법 반복 | 80, 80 | 80, 80 |
| 구적 노드 방정식 풀이 | 20 | 20 |
| 구적 노드 Newton 반복 합계 | 118 | 118 |
| Jet kernel 평가 | 3,020 | 3,020 |
| 독립 표기의 scalar kernel 평가 | 903 | 903 |
| 합계 kernel 평가 | 3,923 | 3,923 |
| 수치 검사 결과 | 405/405 PASS | 동일한 405/405 PASS 재현 |
| 이 작업이 추가하는 독립 물리 증거 | 해당 없음 | 0 |

동결 프로그램은 호출마다 내부 필드 `new_scientific_main_invocations=1`을 출력한다. 파일을 수정하지 않았으므로 이 필드도 첫 결과와 동일하다. 이번 두 번째 호출은 별도의 영수증에서 `portability_replay_main_invocations=1`, `new_physics_evidence_main_invocations=0`으로 분류했다. 재현한 405개 검사를 새 독립 검증 405개로 더하지 않았다.

PHYS19–26 main, 과거 물리 근 탐색, 과거 suite, 새 도함수 부호 조사, native 실행, gas IVP 실행은 모두 0이다. 첫 결과의 코드와 허용오차를 수정하지 않았고 패키지를 설치하지 않았다. 과학 실행 실패나 자동 재시도는 없었다. 완료 노트 작성 중 패치 헤더 오타로 한 번의 문서 작성 도구 호출이 거부되었으며, 그 비과학적 사건은 `PROVENANCE.json`에 보존했다.

## wrapper 사용 범위와 남는 한계

`repro.py`는 `--verify-only`와 `--replay`를 지원한다. 두 모드는 배타적이며 존재하지 않는 복구 디렉터리와 사용하지 않은 결과 기록 prefix를 요구한다. `--verify-only`는 압축물 정체성과 payload의 크기·해시를 확인하고 복구하며 물리 프로그램을 실행하지 않는다. 이번 실제 호출은 `--replay` 한 번이며, 그 안에서 동일한 복구 검증을 완료했다. 별도의 `--verify-only` 호출을 실행했다고 주장하지 않는다.

이 결과는 동일한 관측 Python 환경에서 첫 결과의 바이트를 재현했다는 범위에 한정된다. 다른 운영체제나 Python 버전에서의 일치, 연속 영역의 수학적 부등식, 엄밀한 구간 오차한계, 독립 물리 데이터의 검증을 보장하지 않는다. 이 연산자는 full-history 문맥을 받은 `NONBLIND` portability 담당이며, 수치 후보 생성자나 최종 decision reviewer가 아니다. Physical HOLD와 보호된 연구 상태는 기존 계약을 따른다.
