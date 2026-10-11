# PHYS28 별도 경로 재현 결과

판정: **REPLAY_PASS / implementation-verified**. PHYS28의 첫 수치 결과를 새 경로에서 같은 코드·입력으로 한 번 재현하여 결과 바이트와 parsed JSON이 모두 같음을 확인했다. 재현은 독립 물리 검증 credit **0**이며, 이 문서는 연구 후보의 최종 PROMOTE 판정이 아니다.

## 1. 실제 실행과 결과

실행자는 현재 연구 대화 안의 assistant cloud 직접 하위 실행자 `/root/phys28_portability`다. 별도 사용자 작업 스레드나 사용자 컴퓨터의 local Codex로 작업을 넘기지 않았다. 수치 생성자와 실행자는 다르지만 같은 과학 프로그램·입력·정밀도와 두 대수 경로를 공유한다. parent 전체 이력을 받았고 첫 결과를 읽은 **NONBLIND** 재현이다.

| 항목 | 관측값 |
|---|---|
| 새 복원 경로 | `/workspace/scratch/603081e41728/phys28_portability_fresh_20261011` |
| 실행 파일 | `contributions/numerics/small_width_sensitivity.py` |
| Python | 3.12.14, 표준 라이브러리 Decimal80 |
| UTC 시작 | 2026-10-11T05:29:19.026090+00:00 |
| UTC 종료 | 2026-10-11T05:29:19.166064+00:00 |
| 측정 subprocess wall | 0.13930382800026564 s |
| 프로세스 상한·결과 | 30 s, 실제 exit 0, timeout false |
| 새 프로그램 replay | 1회 |
| 첫 계산의 기존 판정 재현 | 120/120 PASS |
| 결과 비교 | byte equal true, parsed JSON equal true |
| 결과 크기 | 첫 결과와 재현 결과 모두 76416 bytes |
| stdout·stderr | 1327 bytes, 0 bytes |

첫 결과와 재현 결과의 SHA256은 모두 `563e52f9ed2dec6ef379a2e26ca3ec14d06679fef02c2bd0c7328e3022182c84`다. stdout도 첫 stdout과 동일하며 SHA256은 `3e27e7713b2ea826616523a9ba65864168181e361a62e73ba3915505f9df7899`다. 시간·명령·환경은 결정적인 과학 결과 JSON과 분리하여 `REPLAY_RECEIPT.json` 및 `REPLAY_INVOCATION.json`에 남겼다.

실제 명령은 다음과 같다. 이 기록은 실행 증거이며 추가 실행의 권한을 만들지 않는다.

```bash
python3 -B /workspace/scratch/603081e41728/phys28/portability/repro.py \
  --archive /workspace/scratch/603081e41728/phys28/portability/PHYS28_PORTABLE_STAGE.zip \
  --archive-sha256 c9de647f3a6b6c8914089bffd3f2e3e743a2100c6be7f181da18c63cae0847cb \
  --destination /workspace/scratch/603081e41728/phys28_portability_fresh_20261011 \
  --record-prefix /workspace/scratch/603081e41728/phys28/portability/REPLAY \
  --replay
```

## 2. 입력과 복원 범위

최종 v2 `PROTOCOL.json`은 18개 입력을 지정한다. `PREEXECUTION_FROZEN.json`은 이 입력들과 새 코드·protocol·사전 static 기록까지 21개를 고정하며, 동결 manifest 자체를 더한 runtime 의존성은 **22개**다. 첫 결과·EXECUTION·stdout·stderr 4개와 재현 runner·사용법 2개를 합쳐 stage는 **28개 payload + PORTABLE_MANIFEST.json = 29개 ZIP 항목**이다.

| 식별 대상 | SHA256 |
|---|---|
| 최종 새 수치 코드 | `1e3276730868b0062d5c8773f8a111005108220c4b107f0144d5d5b6d2f7a72e` |
| 최종 수치 protocol | `5298c389da5ddd7eb2a5246c3cb472faba93c7d97a39efe7ee99de441200b56a` |
| 최종 사전 동결 manifest | `4a14c4be05e093d21cb652c23b6dea990e168f2c5d8e707c03cfa681b28d0e6e` |
| PHYS22 J 원자료 | `6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79` |
| 재현 runner | `9f0886609901ee004303f4f9e269389d85ba156d81b3991209b275340acf1c82` |
| portable manifest | `b0ab0c2bbc8d809d82388f5886ae86b50cf7773f042cf1d75d7a6ae6d8ee2a4f` |
| portable stage ZIP | `c9de647f3a6b6c8914089bffd3f2e3e743a2100c6be7f181da18c63cae0847cb` |

`PHYS28_PORTABLE_STAGE.zip`은 **211188 bytes**, portable manifest는 7829 bytes다. ZIP을 읽으며 모든 경로·항목 수·payload 크기와 SHA256을 확인했다. 새 경로 복원 뒤 실행 전과 후에 **28/28 payload**의 SHA256·크기·archive 바이트·regular file·mode 100644, 정확한 항목 집합과 manifest 바이트 동일성을 모두 확인했다. protocol18 → frozen21 → runtime22 의존성 연결도 PASS다.

현재 루프에서는 `--replay` 안에서 수행하는 사전 복원 검증을 사용했다. 별도 `--verify-only` 명령을 먼저 실행하지 않았다. 최종 보고서 전체 ZIP이나 원격 저장본을 재다운로드·복구했다는 주장은 하지 않는다. 이 재현은 위에서 명시한 로컬 portable stage에 한정된다.

## 3. 실제 호출 ledger

| 실제 작업 | 첫 계산 | 이번 재현 | 누적 |
|---|---:|---:|---:|
| 새 PHYS28 main | 1 | 1 | 2 |
| Jet 공동 `(k,k′)` 평가 | 4 | 4 | 8 |
| scalar 공동 `(k,k′)` 평가 | 4 | 4 | 8 |
| 공동 커널·도함수 평가 합 | 8 | 8 | 16 |
| k 출력 | 8 | 8 | 16 |
| k′ 출력 | 8 | 8 | 16 |
| k와 k′ 출력 합 | 16 | 16 | 32 |
| 보조 σ 출력 | 8 | 8 | 16 |
| 저장된 값의 branch 식 평가 | 4 | 4 | 8 |
| 새 물리 영점 탐색·반복 | 0 | 0 | 0 |
| PHYS19–27 main·suite·영점 재실행 | 0 | 0 | 0 |
| quadrature·node solve·유한차분 | 0 | 0 | 0 |
| width sweep·새 도함수 부호 campaign | 0 | 0 | 0 |
| native·gas IVP·dense LP | 0 | 0 | 0 |
| 표시용 새 커널·도함수 평가 | 0 | 0 | 0 |

각 실행은 같은 서로 다른 에너지 4개에서 두 경로를 평가한다. 첫 과학 main 1회와 허용된 portability replay 1회를 구분하며, 재현을 새 독립 과학 결과로 계수하지 않는다. 이번 재현에 부여된 1회 예산은 모두 사용했고 자동 재시도는 0이다.

## 4. 읽기·실패·판정 범위

실제 물리 연구 skill/router와 REI cloud 실행 정책, research v4.0.0 core·phase06/07·evidence/stop, coding v4.0.0 core·task-contract template·validation matrix·ultralight·model routing을 읽었다. 템플릿의 NOT_RUN/빈 칸은 연구 실행 증거로 사용하지 않았다. 실제 읽기 경로·범위·identity는 `INTAKE_READS.json`과 `PROVENANCE.json`에 기록한다.

최종 v2 새 과학 코드 563줄을 전부 읽었고 `ROOT=Path(__file__).resolve().parents[2]`, 명시적인 fresh `--output`, 표준 라이브러리 import, 경로·시간을 제외한 결정적 결과, 실제 counter 증가 위치를 확인했다. 첫 raw JSON에서는 identity·summary·고정 노드·오차 최대값·기존 폭 비교·정밀도와 Python 필드를 읽었다. 모든 과학 predicate를 별도로 다시 유도하거나 재판정한 것은 아니다. 원 전체 바이트와 parsed JSON 비교는 전 내용을 대상으로 했다.

수치 담당의 사전 v1 문서 수식 구분자 오류는 과학 실행 전에 수정되었다. 그 최초 5개 파일과 수정 영수증은 `contributions/numerics/preexecution_versions/v1/` 및 `PREEXECUTION_CORRECTION.json`에 보존되어 있다. 해당 v1로 stage하거나 실행하지 않았으며 과학 식·허용오차·입력 값·평가 횟수를 바꾸지 않았다. 이번 stage 작성과 실제 replay에는 관측된 실패가 없었다. runner는 기존 목적지/기록 파일을 거부하고 first failure를 보존하며, 오류를 숨기는 재시도 경로를 갖지 않는다.

이 검증은 관측한 Python/Decimal 환경에서 실행·입력·출력의 재현성을 지지한다. 다른 환경에서의 바이트 동일성, 해석적 정리의 정확성, J·원자율·gas 불확실성, native 동등성, 유한 시간/유한 ε remainder 또는 emitter 승인을 추가로 주장하지 않는다. distinct 최종 decision review는 owner가 별도로 통합한다.

**Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED, production source/default/runtime changes 0**을 보존한다.
