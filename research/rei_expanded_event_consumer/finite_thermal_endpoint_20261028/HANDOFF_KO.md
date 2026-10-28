# 유한 열적 끝점 연구: R1 단독 종료 인계

2026-10-28 KST. 이번 사용자 범위는 중단된 노드 하나의 마무리다. R1 연구 위치·계약의 게시와 원문 이중백업만 완료했고 R2 및 코딩 단계는 시작하지 않았다.

## 실제 재개 경계

저장소 `cosmosapjw-quantum/rei_bianchi`, 브랜치 `research/rei-causal-prefix-consumer-20261027`, 기존 Draft PR #240을 사용한다.

- 중단 전 HEAD: `da525e474a1fb583931897e82808c92101f963c3`
- 재사용한 미게시 tree: `a48ac5acd34042843d827238c888f0bc488cef35`
- R1 원문 게시 commit: `dcf13e3ff12a2e5b722383cffde60833a6c59143`
- 원문 파일: `CONTRACT.json`, `checkpoints/R1.md`
- 실제 백업 ACK: `delivery/R1_CLOSEOUT_RECEIPT_20261028.json`

원문 commit은 두 파일만 추가하며 기존 파일 수정·삭제가 없음을 Git 비교로 확인했다. 이 인계서와 영수증은 그 이후의 종료 메타데이터다. 이 문서의 commit SHA를 문서 내부에서 미리 만들어 쓰지 않는다. 재개 시 실제 branch HEAD를 확인한다.

## 무엇이 완료되었는가

새 단위 `finite_thermal_endpoint_20261028`은 이론 R1/10, 코딩 C0/10, 합계 **1/20**이다. 기존 atomic-storage 연구의 **20/20**과 구분한다. 원래 DAG는 작업 **33/88**, 중앙 **28/88**, 88 IDs/17 edges, 이번 증분 0을 보존한다. 중앙 숫자는 이 단독 종료 작업에서 재조사한 최신 총계가 아니라 승계한 관측값이다.

R1은 공통 기준부피의 열적 입자수 N, 병진 에너지 U, 적분된 사건 에너지 Q와 부피 일 W, 양의 부피비 R, 조건부 caloric EOS를 명시했다. 계약의 기호 c는 입자당 열용량이며 광속이 아니다. binding/excitation 저장량은 gas heat와 분리한다. 저장 residual을 보정·clipping하지 않으며 이미 적분된 W를 다시 적용하지 않는다.

원문의 `COMPLETE_DERIVED_CONTRACT`는 R1 계약 완료로만 해석한다. `theorems` 목록은 뒤 단계에서 유도·검증할 식과 수용 기준을 포함한다. 이 게시를 R5 증명 완료, R6 독립 검토, C단계 구현·실행 완료로 승격하지 않는다. 계약의 implementation 경로와 테스트 목록은 계획이며 이번에 게시한 구현물이 아니다.

이번 처리는 순차 게시·백업과 동일 문맥의 범위 확인이다. `native_subagent: NOT_RUN`. 새로운 독립 심사나 runtime PASS를 주장하지 않는다. 이전 조사·에이전트 기록은 역사적 근거이며 이번 전체 재조사로 표시하지 않는다.

## 백업과 무결성의 실제 범위

두 원문을 각각 새 파일로 저장했으며 양쪽 provider 완료 ACK 네 개를 받았다. 로컬 raw 사본의 Git blob은 게시 원문과 일치한다. Drive의 별도 metadata 크기와 Dropbox의 completed ACK 크기도 일치한다.

| 원문 | bytes | Git blob | Drive ID | Dropbox ID |
|---|---:|---|---|---|
| CONTRACT.json | 6675 | e1c326e4652a26ce84b0fc848bcce26415bc8731 | 1FUiCA05EGUuOLTJXk6P_d-ueA7nrUFeB | id:BSpOijBcT10AAAAAAEDIiw |
| checkpoints/R1.md | 1814 | 3b701c4b0361b084fe68f5fd78693c3b72b53df5 | 1FJUCXKc0HFE7Lk0K8Mju5IdjAGvDbfYr | id:BSpOijBcT10AAAAAAEDIjA |

Dropbox 부모는 `/bianchi/research_backups/rei_bianchi`이며 전체 파일명은 영수증에 있다. 이는 ZIP이 아니라 그대로의 UTF-8 파일이다. 원격 전체 bytes 재다운로드·새 SHA-256 검증을 했다는 주장은 하지 않는다. 종료 메타데이터인 본 인계서와 영수증 자체는 Git 게시이며 별도 이중백업 완료를 주장하지 않는다. 백업 영수증을 재귀적으로 포장하지 않는다.

기존 116개 source JSON, source ZIP, 단계별 이전 백업은 복원하거나 재생성하지 않았다. 새 과학·테스트·CAS·IVP/provider 실행과 ZIP/CRC/ZIP SHA 실행은 각각 0이다. 원문 백업을 위해 새 문서 두 개의 파일 쓰기·크기 확인·Git blob 비교만 수행했다.

## 예산과 물리 판정

이월 planning known `15.929490885 CPU s`, 마지막 명시적 cap 16; presentation 측정·예약 하한 `48.263016494 CPU s`, 마지막 명시적 cap 47을 보존한다. 읽기·원문 파일 쓰기·전송·커넥터의 이번 미계측 비용은 `UNKNOWN_NOT_ZERO`이며 이 숫자를 현재 정확한 전체 CPU로 주장하지 않는다. 새 cap 60/reservation 8 승인은 없고, 포장 helper는 실행하지 않았다. main `595.225063/600 NO_MORE_IVPs`, 기존 예산 초과 및 타 owner 예산을 보존한다.

기존 과학 판정 `PASS_SCOPED_FINITE_BASS_ATOMIC_STORAGE_REPRESENTATION` 유지. 실패 분류 `runtime_environment/resource_budget` 유지. `L4_ready=false`, `global_physical_completion=null`. 실제 source-matched bath/EOS, recipient nb, native25, temperature update, physical radii는 null이며 전체 상태 업데이트는 false다.

## 다음 스레드용 지시

```text
$physmath-research-loop로 cosmosapjw-quantum/rei_bianchi를 재개하라.
Branch research/rei-causal-prefix-consumer-20261027, Draft PR #240.
현재 HEAD와 AGENTS를 확인하고 다음 경로를 읽어라:
research/rei_expanded_event_consumer/finite_thermal_endpoint_20261028/
  CONTRACT.json
  checkpoints/R1.md
  delivery/R1_CLOSEOUT_RECEIPT_20261028.json
  HANDOFF_KO.md

R1 원문 commit dcf13e3ff12a2e5b722383cffde60833a6c59143.
R1 게시·두 원문 Drive/Dropbox 백업은 완료됐다. 재생성하지 마라.
새 단위 이론1/10, 코딩0/10, 합계1/20.
기존 atomic-storage20/20과 원래 DAG 작업33/88·중앙28/88을 구별하라.
원래88IDs/17edges, L4=false, global=null을 보존하라.

다음 단계는 별도 사용자 지시가 있을 때 R2 근거·재사용만 진행한다.
R1 계약의 식·theorems 목록을 이미 입증된 신규 정리로 세지 마라.
기존 BASS saved transaction과 PR237 differential thermal source의
정의·단위·소유권·수신 bath/EOS 일치 여부를 확인할 계획을 유지한다.
실제 nb/EOS가 없으면 physical temperature/native25/null을 유지한다.

planning15.929490885, presentation하한48.263016494 및
UNKNOWN_NOT_ZERO를 보존하고 예산을 리셋·이관하지 마라.
cap60/reserve8은 미승인이다. 별도 명시적 승인 없이
포장·새 과학 실행·기존 테스트·IVP/provider 재실행을 하지 마라.
이번 종료 지시는 R2나 코딩 단계의 자동 실행을 승인하지 않는다.
```
