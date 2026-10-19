# Codex: REI-LRS V14 현재 실행 인계 — 2026-10-19

사용자에게 파일 다운로드·압축 해제·SSH/SCP를 요구하지 않는다. Codex가 기존 인증과 repository 소스를 직접 사용한다. 작업은 production v3/rux와 별개인 독립 LRS 연구다.

## 먼저 읽을 실제 상태

Repository `cosmosapjw-quantum/rei_bianchi`, draft PR https://github.com/cosmosapjw-quantum/rei_bianchi/pull/198, branch `research/rei-lrs-v14-physical-birth-20261018`.

`AGENTS.md`, `v14/RESEARCH_DELIVERY_KO.md`, `SOURCE_DELTA.json`, `stages/FINAL_DELIVERY.json`, `stages/PROJECTION_DIAGNOSTIC_20261019.json`, `projection_diagnostic_20261019/RESEARCH_CONTINUATION_KO.md`를 읽는다. Drive `REI_RESEARCH_BACKUPS/rei_bianchi/`와 Dropbox `/bianchi/research_backups/rei_bianchi/`에서 새 execution receipt가 있는지도 먼저 확인한다. 목록만으로 실행을 판단하지 않는다.

**원래 native compile→36개 표적시험→smoke→84 histories는 이미 완료됐다. 재실행하지 않는다.** NCP host `s1a0e5abed09`, Rust1.99.0. Smoke exit0/28 histories/336 rows, full exit0/84 histories/7056 rows. 첫 입력 형제경로 누락 실패도 보존됐다. 원본은 `executions/REI_LRS_V14_20261018T124115Z/`에 있다.

V14 source byte anchor는 `f6046418d15e2f44418dfbc04ca67999f389a7df`, V13 parent는 `7fb18cec3d6d6eebad5fe418ec83b36d82cfff1e`다. `2676c31…`는 기존 source-intake 문맥, `ef94f08…`는 실행 후 증거 게시 commit이며 실행 checkout SHA로 승격하지 않는다.

새 진단은 sandbox Rust1.94.1에서 실제 compile/run/analyze를 완료했다. 62 summary rows와13,312 cell rows는 native fixed-gas/fixed-geometry transport 진단이다. 제공 runner의 fresh sibling restoration도 실제 통과했고 원시 CSV가 최초와 바이트 단위로 같다. 이를 기존84 우주론 이력 또는 새로운124개 사례로 잘못 세지 않는다.

## NCP에서 남은 실행 전용 작업

새 native 진단의 NCP 플랫폼 재현이 필요할 때만 아래 완성된 runner를 실행한다. 현재 controller는 Desktop Commander 월 사용량 SERVICE_ERROR를 실제 받았으므로 이 스레드에서 NCP에 새로 실행하지 않았다. 서비스 제한을 우회하거나 같은 실패 호출을 반복하지 않는다.

기존 승인 접속 경로는 Codex가 직접 사용한다:

```bash
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```

기존 repository의 active branch/reset/clean을 하지 말고 현재 HEAD와 작업 상태를 읽는다. 해당 branch 소스를 기존 checkout의 `git archive` 또는 인증된 connector로 확보해 `/root/REI_LRS_V14_PROJECTION_<UTC>/input/` 아래 세 형제 디렉터리 `v12/native_owner`, `v13`, `v14`를 유지한다. 새 clone/worktree는 만들지 않는다. Production checkpoint와 다른 연구 실행을 수정하거나 종료하지 않는다.

호스트·시간·CPU/RAM·디스크·부하와 이미 실행 중인 동일 작업을 확인한다. Rust가 PATH에 없으면 기존 `/root/.cargo/bin`만 추가한다. 완성된 runner 위치와 실행은 다음과 같다:

```bash
bash /root/REI_LRS_V14_PROJECTION_<UTC>/input/v14/projection_diagnostic_20261019/RUN_PROJECTION_DIAGNOSTIC.sh \
  - /root/REI_LRS_V14_PROJECTION_<UTC>/projection_output
```

`<UTC>`는 Codex가 실제 새 UTC 식별자로 치환한다. Runner는 기존 output을 거부하고 sibling `RESTORE_V14.py`로 복원한다. 네 기존 native SHA와 새 example SHA를 검사하며 offline locked release/jobs2 build를180초, 새 진단만60초로 제한한다. 실제 hostname/platform/commands/stdout/stderr/exit/elapsed/output SHA를 `EXECUTION.json`에 기록한다. Matplotlib이 있으면 PNG/PDF도 만든다.

기준 summary SHA256:
`ca4b20024bd2f8adfac5995ffeebfecd0c56f47d7cbe89d38f874a909402dc3e`

기준 cell CSV SHA256:
`3e9af61a432d40e743901c5000611a00788b3766b90840df4806a56466737b6b`

다른 compiler/platform에서 byte 일치하지 않으면 원시 차이를 기록하고 row matrix, finite, signed differences, conservation, delta floor를 비교한다. Byte 불일치를 physics 실패나 정확도 개선으로 자동 해석하지 않는다. 실제 실패 stdout/stderr/exit를 보존하며 컴파일 경로/API/type의 작은 호환 수정만 허용한다. Native closure·source·rate·광속·tolerance를 통과 목적으로 바꾸지 않는다.

## 연구 판정과 게시

Full-vs-two-halves의 local slope≈2는 global second order가 아니다. 이 진단의 broad-spectrum 반복 적분은 약1차이고 delta60는 roundoff floor다. 기존 coupled GL2 T p≈1.06/0.95, full source-on p2·uniform stiff·CaseB·fullEoR·signed Bianchi는 HOLD다. 양의 초기 photon을 가진 evolving-gas source-free 수정 실험과 시간 중심 closed-moment stage 설계는 별도 연구 단위이며 여기서 즉흥적으로 고치지 않는다.

실제 새로운 실행이 완료되면 이 branch에 code/receipt/result를 commit/push하고 PR 범위를 갱신한다. 원본 default/production에 merge하지 않는다. Drive 지정 V14 폴더와 Dropbox 지정 경로에 create-only archive를 저장한 뒤 양쪽 전체파일 readback SHA256을 확인한다. ACK와 readback을 따로 기록하고 DAG의 NCP 플랫폼 재현 단계만 실제 증거에 맞춰 갱신한다. 사용자에게 수동 파일작업을 넘기지 않는다.
