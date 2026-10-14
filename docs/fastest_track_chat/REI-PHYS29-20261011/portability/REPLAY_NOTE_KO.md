# PHYS29 새 경로 재현 기록

## 판정과 범위

**REPLAY_PASS / implementation-verified.** `/root/phys29_portability`가 동결된 새 PHYS29 프로그램을 별도 절대 경로에 복구하여 **정확히 한 번** 실행했다. 실제 결과는 **238/238 PASS**, exit0이며 원 최초 결과와 137,037 bytes 전체 및 파싱된 JSON이 일치한다. 재현은 동일 프로그램·동일 입력·동일 cloud host/Python의 경로 이동에 대한 증거다. 독립 물리 credit은 **0**이다. 이 기록은 최종 과학 승격 판정이 아니며 porter는 수치 후보 생성자나 최종 판정자가 아니다.

root가 최초 실행 결과를 읽은 뒤 `EXPLICIT REPLAY GO`를 전달했다. porter는 이어서 runtime·stage·protocol을 먼저 동결하고 metadata 사전 검사를 끝낸 후 단 한 번의 새 과학 subprocess를 실행했다. `PORTABILITY_PROTOCOL.json`의 시각은 실제 replay 시작보다 앞선다. 준비·stage 구성·AST 검사는 과학 실행으로 세지 않았다.

## 실제 실행

| 항목 | 관측값 |
|---|---|
| 최초 PHYS29 main | 2026-10-11 06:48:30.264255–06:48:30.358291 UTC |
| 별도 경로 replay | 2026-10-11T06:52:55.749094+00:00–2026-10-11T06:52:55.864023+00:00 |
| replay subprocess wall | 0.114370452997 s |
| Python | 3.12.14, Decimal precision80 |
| 실제 exit / timeout | 0 / false |
| stdout / stderr | 1,828 bytes / 0 bytes |
| 수치 판정 | 238 PASS, 0 FAIL |
| 결과 byte 일치 / JSON 일치 | true / true |

복구 경로는 `/workspace/scratch/603081e41728/phys29_portability_fresh_20261011`이다. 복구 전에 존재하지 않았고, runner는 기존 복구 경로나 기록 파일이 있으면 덮어쓰기를 거부한다. 실제 argv와 cwd는 `REPLAY_INVOCATION.json`, 시작·종료·원 로그 identity와 모든 복구 검사는 `REPLAY_RECEIPT.json`에 남겼다. 실행은 `-B` 및 `PYTHONDONTWRITEBYTECODE=1`로 bytecode 파일을 만들지 않았으며 결과 JSON은 복구 runtime 밖에 썼다.

원 최초 결과와 replay 결과의 SHA256은 모두

`40d686d2646ac7dbaff1bd768a789fcfdbaf5043a16b26512c42ffbedbdd8d6f`

다. stdout 역시 원 최초 stdout과 같은 bytes/SHA256을 갖고, stderr는 빈 파일이다. raw result의 고정 `role` 문자열은 프로그램 작성자가 넣은 생성 provenance를 보존한다. 실제 이번 실행 주체·명령·시간은 별도 replay invocation/receipt가 식별한다.

## Runtime closure와 불변성

**20개 protocol 입력 + 추가 동결 파일 5개 = 동결 identity 25개**, 여기에 `PREEXECUTION_FROZEN.json` 자체를 더한 **runtime 26개**다. 추가 5개는 새 scientific entrypoint, scientific protocol, input provenance, static checks, preexecution changes이다. protocol 입력에는 물리 계약·source manifest·새 theory/과학 계약과 실제 소비하는 PHYS22/26/27/28 자료·pinned source가 포함된다.

stage ZIP에는 이 **runtime 26개와 manifest 1개**, 총 **27개**만 있다. 원 최초 결과는 ZIP 내부의 실행 입력이 아니며 manifest에 identity를 기록한 외부 비교 기준이다. 복구 runner가 비교를 위해 원 결과를 읽고, 과학 entrypoint는 runtime의 동결 입력만 읽는다. 이전 PHYS28 코드 payload는 provenance byte 검사용 입력이며 import·실행되지 않는다.

모든 ZIP 경로는 정규 상대 경로이고 모든 member mode는 `100644`다. 정렬한 member 순서, 고정 ZIP 시각 1980-01-01, DEFLATE level9로 stage를 만들었다. 원본에서 stage로의 bytes·SHA256·size·mode, protocol과 freeze의 부분집합 관계, 별도 경로 복구 후의 전체 member 집합을 검사했다. replay 전후 **26개 runtime와 manifest 모두 내용·member 집합·regular mode가 그대로**였다. `STAGE_RECEIPT.json`과 `REPLAY_RECEIPT.json`이 각 파일의 실제 검사 행을 보존한다.

candidate 786줄을 읽고 stdlib import 목록, `ROOT=Path(__file__).resolve().parents[2]`, `HERE`, freeze 순회 hash 검사, 실제 JSON 읽기 및 output 경로 처리를 확인했다. 이것은 선언된 입력 closure의 정적 확인이며 OS 전체 file-open trace나 환경의 완전한 격리를 주장하지 않는다.

| 고정 파일 | bytes | SHA256 |
|---|---:|---|
| 새 scientific program | 40,589 | faf7c3911d54f9739b4d486f88fa388af7165c50684bfbb036dcf02e5a8c5bda |
| scientific PROTOCOL | 16,527 | 6ab5d3c488a00ebfb868e4d4e83d98a2fe1db9479956b587f673d9d9b86e7573 |
| PREEXECUTION_FROZEN | 5,472 | 544efcc1dda9cd0a4f63d5806cb59c2a092484016de8b20755f785f47a0b9c7b |
| PHYS29_PORTABLE_STAGE.zip | 229,766 | 8d33fe3493dad0164c0134def6e5d7a78c4250a4365b07949449022fec819230 |
| replay runner | 15,971 | 28a032f37b06757b3283ebdb0e0afa02be82514814f2e2f789b97639d02b40da |
| PORTABILITY_PROTOCOL | 4,293 | 6ba7566d365f0da2f44b0aa8ef1f5e952b355d614d6a83fea6495336734db31d |
| REPLAY_RECEIPT | 33,383 | ed754b4d43ad8cc231a2b16edb61eda491dfa7582a7939040aa9edb7ee64d0e9 |

## 실제 예산

| 항목 | 최초 main | 이번 replay | PHYS29 합계 |
|---|---:|---:|---:|
| 과학 main | 1 | 1 | 2 |
| joint kernel/derivative 평가 | 8 | 8 | 16 |
| k 산출 | 8 | 8 | 16 |
| k′ 산출 | 8 | 8 | 16 |
| k″ 산출 | 8 | 8 | 16 |
| 위 세 성분 산출 합계 | 24 | 24 | 48 |
| 보조 sigma 산출 | 8 | 8 | 16 |
| 각 kernel 경로의 평가 | 4 | 4 | 8 |
| 새 물리 영점 | 0 | 0 | 0 |
| old PHYS19–28 main/import/suite/root | 0 | 0 | 0 |

네 개의 같은 저장근 유래 node를 각각 두 대수 경로에서 평가했다. replay는 추가 8 joint 평가로 별도 계산했다. 각 실행에서 cached chain branch2, cached bivariate branch2, kernel 없는 moment series2, exact Fraction toy branch2와 각 toy 구현2회가 원 counters에 기록된다. finite differences·quadrature·width/root sweep·derivative-sign campaign·native·gas IVP·dense LP와 figure용 추가 kernel 평가도 모두0이다.

## 실패·한계·보호 상태

이번 porter 실행에는 사전 검사 실패·scientific failure·timeout·retry·candidate 수정이 없었다. 숫자·허용오차를 수정하지 않았으며 첫 실행의 동결 v3를 그대로 소비했다. 수치 작성 단계의 보존된 이전 draft와 문서 표기 수정은 main provenance에 남아 있고, porter가 그 옛 버전을 실행하지 않았다.

byte 동일성은 재현된 계산의 identity를 확인한다. 독립 물리 자료, 별도 scientific implementation, exact-root enclosure, J/원자물리 불확실성 enclosure, native equivalence, Taylor 나머지 상계 또는 폭 구간 수렴 인증을 추가하지 않는다. 최종 과학 검토와 승격은 별도 NONBLIND reviewer의 범위다.

**Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED, production source/default/runtime changes0**를 유지한다.
