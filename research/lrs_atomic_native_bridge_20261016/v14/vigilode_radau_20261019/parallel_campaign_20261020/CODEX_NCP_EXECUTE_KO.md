# CURRENT NCP SSH·read-only preflight 인계 — 2026-10-21

이번 요청은 연결 계약과 인계 갱신이다. 이 갱신에서 SSH 접속이나 원격 실행을 시도하지 않았다. 다음 실제 연결은 아래 사용자 지정 명령과 read-only 범위에 따른다.

## 고정 상태와 경계

- Repository: `cosmosapjw-quantum/rei_bianchi`; [PR198](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/198); branch: `research/rei-lrs-v14-physical-birth-20261018`.
- 이번 문서 갱신의 frozen base HEAD: `3d8c029e1c485c8043fad2321461dc9d765670b3`. 실제 원격 checkout HEAD는 접속 후 관측하며 이 값으로 자동 변경하지 않는다.
- 연결 계약: [ncp_backlog_20261021/followup_20261021/NCP_CONNECTION_CONTRACT.json](ncp_backlog_20261021/followup_20261021/NCP_CONNECTION_CONTRACT.json). 이번 갱신은 `SSH UPDATED`, `NOT_ATTEMPTED_THIS_UPDATE`; read-only preflight도 아직 수행하지 않았다.
- 246 DAG jobs는 144 completed / 100 not run / 2 blocked다. V12는 44/144 완료, V13 및 SSPRK는 완료다. current source의 19설정, borrowed N2, original V14 84 완료를 유지하고 재실행하지 않는다.
- V12 historical debit `200.39897231891518 s`, historical cap `180 s`는 고정이며 reset하지 않는다. 남은 V12 100개, 완료 dependency 9개, 완료 V12 44개의 identity와 digest는 기존 prospective skeleton 그대로 보존한다.
- 새 native campaign은 `NOT_AUTHORIZED`. 새 aggregate budget은 `null` / `NOT_FROZEN`, prior-debit import rule도 `NOT_FROZEN`이다. 별도 승인된 prospective amendment 없이 실행으로 전이하지 않는다.
- `EXIT_ACCOUNTING_V1` supervisor opt-in은 prospective only다. timing은 관측값이며 polling/teardown overshoot가 가능하다. budget을 자동 승인하거나 과거 초과 debit을 소급 소거하지 않는다.
- SSH 연결 권한은 scientific admission이 아니다. 기존 과학적 범위의 `HOLD`, production `NOT_ISSUED`를 유지한다. PR199는 별도이며 건드리지 않는다.

## Agent의 다음 동작: 연결과 read-only preflight

사용자가 agent에게 승인한 연결 명령은 정확히 다음과 같다.

```bash
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```

1. 이 identity 경로는 SSH를 실행하는 **client 환경**의 경로다. 원격 경로나 key의 존재를 가정하지 않는다. 실제 인증 가능한 환경에서 agent가 연결을 시도하고 실제 argv, stdout/stderr, exit code를 기록한다. private-key 내용을 읽거나 출력하지 않고 host verification을 끄는 옵션을 추가하지 않는다.
2. 성공하면 기존 checkout의 실제 위치를 먼저 확인한다. 경로를 추측해 생성하지 않는다. 그 checkout의 branch, HEAD, remote, dirty/untracked 상태와 실제 host/toolchain 및 CPU affinity·cgroup quota·available memory/resource receipt를 read-only로 관측한다. 64 cores나 특정 가용 메모리를 미리 보장하지 않는다.
3. dirty/untracked 파일을 보존한다. clone/worktree/reset/clean, dirty 파일 덮어쓰기, 자동 pull·checkout 갱신을 하지 않는다. receipt/metadata 읽기나 fetch 요청을 자동 pull의 허가로 바꾸지 않는다. build/test/native 실행은 이 preflight 범위 밖이다.
4. 연결 실패 시 실제 stderr와 exit code를 보존하고 preflight/실행을 `NOT_RUN`으로 보고한다. 사용자에게 수동 SSH/SCP나 파일 다운로드를 요구하지 않는다. 성공한 경우에도 관측 receipt를 반환하고 새 native campaign을 시작하지 않는다.

이전 launch 지침과 게시·백업 이력은 frozen Git history에서 확인한다. 현재 문서의 연결·preflight 지침을 과거 전체 실행 지침으로 대체하지 않는다.
