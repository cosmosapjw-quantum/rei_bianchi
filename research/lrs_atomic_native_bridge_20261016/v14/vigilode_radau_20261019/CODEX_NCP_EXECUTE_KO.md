# 현재 상태 — VigilODE NCP 완료 및 2026-10-20 복원 확인

2026-10-19 NCP에서 고정 source `d87ba9ca25acb8a2a032154fa23057b45acd6207`의 locked/offline release build, 표적시험 7개와 **샌드박스와 같은 19개 고유 설정**이 완료됐다. 모두 exit 0, 실패·중단 0, native RHS 38,840회, native wall 15.824811033초다. 두 host의 실행을 38개 고유 설정으로 합산하지 않는다. 실행 근거 commit은 `09bfe94bc270623b014bc6db78c59211152739aa`, C11 전달 commit은 `46a29285ad7095959bb0e5b5a10dab0fec97501f`다.

[실제 NCP 실행 receipt](ncp_20261019T171038Z/NCP_EXECUTION_RECEIPT.json), [NCP delivery/DAG](stages/NCP_DELIVERY_20261019.json), [2026-10-20 복원 보고](recovery_20261020/RECOVERY_REPORT_KO.md)를 먼저 읽는다. 이번 host에서는 native run 0·build 0이며 prepare-only 복원과 저장 결과 readback만 수행했다. 316,540개 raw 비시간 수치 leaf와 209개 endpoint, 435+323개 분석 leaf가 유한 f64이고 packed IEEE64로 일치했다. 기존 walker와 같은 시간 leaf 38개는 제외했다. 이는 같은 유한 설정의 결과 재현 확인이다.

일반 source-on 차수·HeIII endpoint 단일 차수·uniform stiff 정확도·일반 양수성·Case B·full EoR·signed Bianchi·positive CMB/비영 boundary는 HOLD이며 production admission은 NOT_ISSUED다.

최신 receipt를 먼저 읽고 원본 source·C10/C11 raw·이전 transcript는 고정된 근거로 보존한다. 이번 2026-10-20 복원에서는 NCP에 접속하거나 native를 실행하지 않았다. 아래 절차는 이미 완료한 작업의 선택적 재현 가이드이며, 향후 명시적 재현 요청이 있을 때만 새 실행을 수행한다.

확인된 launcher 결함은 single-branch checkout에서 `git fetch origin BRANCH`가 FETCH_HEAD만 갱신하고 `origin/BRANCH`를 오래된 상태로 둔 것이었다. 아래의 fetch 한 줄만 실제 성공한 [refspec 수정 diff](ncp_20261019T171038Z/tools/launcher_r1_to_r4.diff)와 같은 명시적 refspec으로 고쳤다. 첫 세 launcher는 native 이전 exit 1이었다. 네 번째는 `prepare_and_run.py` exit 0으로 19개 실행을 끝낸 뒤 system Python의 matplotlib 부재로 analyzer exit 1이었다. 분석 전용 venv의 analyzer 재실행 exit 0은 `NCP_EXECUTION_RECEIPT.json`의 보고값이며, 저장된 `analysis_r2` stdout 요약과 빈 stderr가 이를 뒷받침한다. 별도의 재실행 `EXIT_CODE` 파일은 관찰하지 못했다. 이 호환 수정은 이미 수행된 기록이며 이번 복원에서 의존성을 설치하지 않았다.

---

## 아래 본문은 실행 전 인계의 역사적 기록 및 선택적 재현 절차

아래의 NCP NOT_RUN·NCP에 남은 작업 문장은 당시 상태다. 현재 완료 결과는 위 receipt를 따른다. 아래 명령의 fetch 한 줄만 위에서 설명한 실제 수정으로 반영했다.

# Codex NCP 인계 — 독립 LRS V14 / VigilODE native Radau

사용자는 source 복원·코드 수정·컴파일·실제 실행·동일 연구 branch push와 Drive/Dropbox 백업을 승인했다. 사용자가 다운로드나 수동 SSH/SCP를 수행하도록 요구하지 않는다. Production v3/rux, BASS, atomic, age-reference DAG와 별개인 독립 LRS 작업이다.

## 먼저 읽을 것

Repository `cosmosapjw-quantum/rei_bianchi`, PR198, branch `research/rei-lrs-v14-physical-birth-20261018`이다. Repository AGENTS.md를 읽고 다음 순서로 현재 상태를 확인한다.

1. `research/lrs_atomic_native_bridge_20261016/v14/RESEARCH_DELIVERY_KO.md`, 원 `SOURCE_DELTA.json`, `stages/FINAL_DELIVERY.json`, `CODEX_NCP_EXECUTE_KO.md`.
2. 새 `v14/vigilode_radau_20261019/RESEARCH_DELIVERY_KO.md`, `THEORY.md`, `SOURCE_DELTA.json`, `stages/FINAL_DELIVERY.json`, `README.md`.
3. 원격 backup에 이 전달 이후 실행이 생겼다면 source SHA/manifest, stdout/stderr, 실제 종료코드, raw JSON을 먼저 읽는다. 목록이나 archive 이름으로 실행 완료를 추정하지 않는다.

완료된 원래 V14 NCP84이력, 이전 SSPRK2 sandbox16설정 및 제조76/Python57을 새 연구로 다시 세지 않는다. 이번 추가 native 비교는 **고유19설정, 19완료, 실패·중단0**, 38,840 RHS, native9.146159986초다. 이19설정은 sandbox에서 실행했고 새 NCP Radau 결과는 아직 NOT_RUN이다.

## 이미 준비된 코드와 실제 증거

- Actual VigilODE source: `8a8bd409b1d96c7b7421f496d229e119fd3d284e`; exact source whitelist477개와 immutable archive SHA가 정상 JSON에 있다.
- Baseline native152개 bytes + transport173-byte append hook + 새 `axbi_native_rhs.rs`로 구성한다. Default/adaptive/checkpoint, MD14, Verner/Grackle/EOS 원본을 변경하지 않는다.
- Native Radau는 실제 3-stage implicit solve, honest FD Jacobian, 재구성 stage 공통 ledger를 사용한다. `PerturbationDomain`만 단측 FD fallback을 허용한다.
- Final numerical executable SHA256 `358d254f88d196cd1ada4f71283fa3a69a068bbbf25ae28980af287575106905`. Sandbox Rust/cargo1.94.1. NCP를 이 버전으로 강제 downgrade하지 말고 실제 `-Vv`를 기록한다.
- Native focused6 + FD분류1 PASS. Runner process-only4 PASS. Fresh source prepare-only와 exactarchive477hash 검증 PASS. 이 process 검증을 native 이력으로 더하지 않는다.
- 원시 결과 `receipts/`, 재계산 `analysis/`, 독립 검토 `c9_code/`와 `theory_review/`를 보존했다.

## NCP에 남은 유한 작업

1. Codex가 기존 checkout과 dirty 상태를 읽는다. `reset --hard`, `clean`, 새 clone/새 Git worktree를 만들지 않는다. 기존 branch를 fetch하고 최종 `source_publication_sha`를 고정한다.
2. 그 commit의 `research/lrs_atomic_native_bridge_20261016` subtree를 새 run-input 경로로 `git archive`한다. 기존 checkout을 수정하는 작업이 아니다.
3. 정상 `prepare_and_run.py --all`로 source 복원, locked dependency fetch, offline locked release build, 7표적시험, 정확히19설정을 수행한다. Jobs1, native RHS200000/case다. Radau내부30초, 모든 process는 최대40초 및 남은 총예산180초로 제한한다. SSPRK에는 내부 elapsed check가 없으므로 외부 제한을 유지한다.
4. Native default biology/source/closure/허용오차를 성공용으로 바꾸지 않는다. Radau scaled Newton atol1e-13/rtol0과 SSPRK 기존 coupling tolerance1e-15를 구분한다. 실제 호환성 오류만 최소 수정하고 diff/새 source SHA와 해당 회귀를 남긴다.
5. 모든 완료/실패/중단 receipt와 raw를 읽는다. 실패 또는 family-blocked/budget-unrun이 있으면 portable runner 전체 exit는 비영이어야 한다. 실패 로그를 지우고 성공으로 대체하지 않는다.
6. 완료19설정의 endpoint/finite difference/cost를 아래 정상 분석기로 재구성하고 sandbox자료와 비교한다. NCP bitwise 동일 결과를 요구하지 않는다. 사건·전자·binding·열·escape/CMB/work/photon 회계는 `THEORY.md`의 항등식과 raw channels로 다시 검사한다.
7. 결과를 동일 PR branch와 Drive/Dropbox 기존 연구백업 경로에 보존한다. Full-file readback SHA, Git source commit, compiler/host, stdout/stderr/exit, 결과 수량, DAG status를 기록한다. 사용자에게 파일 이동을 맡기지 않는다.

## Codex가 실행할 복사 가능한 명령

다음은 **NCP의 기존 repo에서 Codex가 실행**하는 명령이다. 사용자 수동 실행 요청이 아니다. REI_REPO가 잘못된 repo인지 먼저 확인한다. 최종 receipt는 publication commit을 가리키므로 later metadata HEAD와 구분된다.

```bash
set -euo pipefail
REI_REPO="$(git rev-parse --show-toplevel)"
REI_BRANCH='research/rei-lrs-v14-physical-birth-20261018'
REI_REL='research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019'
git -C "$REI_REPO" status --short
git -C "$REI_REPO" fetch origin "+refs/heads/$REI_BRANCH:refs/remotes/origin/$REI_BRANCH"
REI_SOURCE_SHA="$(git -C "$REI_REPO" show "origin/$REI_BRANCH:$REI_REL/stages/FINAL_DELIVERY.json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["source_publication_sha"])')"
REI_JOB_ROOT="/tmp/rei_lrs_vigilode_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$REI_JOB_ROOT/input"
git -C "$REI_REPO" archive "$REI_SOURCE_SHA" research/lrs_atomic_native_bridge_20261016 | tar -x -C "$REI_JOB_ROOT/input"
REI_INPUT_ROOT="$REI_JOB_ROOT/input/research/lrs_atomic_native_bridge_20261016"
REI_TASK_ROOT="$REI_INPUT_ROOT/v14/vigilode_radau_20261019"
python3 "$REI_TASK_ROOT/prepare_and_run.py" \
  --input-root "$REI_INPUT_ROOT" \
  --output-root "$REI_JOB_ROOT/run" \
  --cargo cargo --all
python3 "$REI_TASK_ROOT/analyze_matrix.py" \
  --receipts "$REI_JOB_ROOT/run/evidence" \
  --out "$REI_JOB_ROOT/analysis"
```

Exact VigilODE archive가 없으면 runner가 pinned URL을 자동 회수하고 전체 SHA를 검산한다. 이미 회수한 compact backup의 `vigilode_source/`를 쓰려면 `--vigilode-source`를, crate cache를 쓰려면 `--cargo-home`를 지정한다. `--offline`은 source와 cache가 이미 있는 경우 사용한다. 부분/실패 matrix의 정확도 분석은 거부하며 먼저 실패 원문을 해석한다. Matplotlib이 없다면 native결과는 이미 보존된 상태에서 분석용 의존성만 준비한다.

외부의 기존 허가된 장치에서 Codex가 NCP에 접근할 때의 연결 정보:

```text
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```

키 내용을 출력하거나 복사하지 않는다. 이 ChatGPT sandbox에는 해당 키 파일이 없고 기존 외부실행 connector도 사용할 수 없어 새 NCP 실행을 하지 않았다. 접근 제한을 우회하지 않고 이 완성된 source/runner와 실제 sandbox evidence를 전달한다.

## 과학적 승격 금지와 다음 판정

고정 geometry의 finite 약5차/약2차 관측과 source-on 전체 차수를 구분한다. Source-on HeIII는 수 ulp cancellation이고 단일 차수 HOLD다. GL2의 두 method endpoint/source weight는 최대한ulp 차이가 있어 bitwise-identical forcing이 아니다. 현재는 q0, negative CMB, passive/boundary0 범위다. Uniform stiff, 일반 positivity, Case B, fullEoR, signed Bianchi, positive-CMB/비영 boundary는 실제 새 증거 없이 승격하지 않는다.
