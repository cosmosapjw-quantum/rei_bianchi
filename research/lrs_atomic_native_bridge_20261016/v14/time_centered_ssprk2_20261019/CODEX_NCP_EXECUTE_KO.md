# Codex 실행 인계: V14 후속 native SSPRK2

사용자가 이론·구현·경량 검증·GitHub 게시·백업을 승인했다. 사용자에게 다운로드, 수동 SSH/SCP, 압축 repair 코드 붙여넣기를 요구하지 않는다. 기존 인증과 source를 Codex가 직접 사용한다. production v3/rux와 별개인 독립 LRS다.

## 먼저 확인할 최신 상태

Repository cosmosapjw-quantum/rei_bianchi, draft PR https://github.com/cosmosapjw-quantum/rei_bianchi/pull/198, branch research/rei-lrs-v14-physical-birth-20261018.

AGENTS.md, v14/RESEARCH_DELIVERY_KO.md, 원SOURCE_DELTA.json, stages/FINAL_DELIVERY.json을 읽고 time_centered_ssprk2_20261019/RESEARCH_CONTINUATION_KO.md, SOURCE_DELTA_SSPRK2.json, ROOT_SCIENTIFIC_ADMISSION.json, stages/SSPRK2_FINAL_DELIVERY.json으로 이어간다. 새 Drive/Dropbox 실행 receipt가 있으면 실제 source hashes, stdout, exit, CSV부터 읽는다. 파일 목록과 archive 이름만으로 성공을 추정하지 않는다.

원래 V14 native compile·36개 고유 표적시험·smoke28·full84이력은 NCP에서 이미 완료됐다. 기존 제조76/Python57/projection62행도 재실행하지 않는다. 새 SSPRK sandbox 결과는14고유표적시험, transport52행, coupled16고유이력이다. Clock 수정 전후16+16 실행은 같은16설정의 재현이며32새사례가 아니다.

새 code는 두 명시적 opt-in child/module hook이다. 원본 default/adaptive/checkpoint/MD14/Verner/Grackle/EOS와 physical_birth 파일 본문을 유지했다. 두FEstage의 실제node CFL<=1, 같은gas midpoint, 같은event/heat/binding weights를 지킨다. 새 clock은 log1p 상대 간격과 실제 accepted dt를 공유한다. SourceGL2 HeIII endpoint 차수는 HOLD다.

## NCP에 남은 유한한 작업

1. 기존 repository 위치와 dirty 상태를 읽는다. reset/clean/새 clone/새 Git worktree를 만들지 않는다. 필요한 원격 branch를 fetch하고 최종 delivery receipt의 source_publication_sha를 고정한다.
2. 해당 Git commit의 research/lrs_atomic_native_bridge_20261016 subtree를 새 run-input 디렉터리에 git archive로 내보낸다. 이것은 실행 입력 staging이며 기존 작업 checkout을 바꾸지 않는다.
3. 아래 정상 Python runner로 source 복원→offline/locked/release build→14표적시험→transport52행→fixed6+birth10이력을 실행한다. Jobs는 최대2다. 과학 실행 총300초, 개별 build180초/tests120초/transport60초/coupled각180초 한도를 유지한다.
4. 호환성 오류가 실제 나타나면 최소 수정과 해당 회귀만 수행하고 새 source hash/diff를 보존해 같은branch에 게시한다. 허용오차·률·source·closure를 통과용으로 바꾸지 않는다. Rust/cargo 실제-Vv를 기록한다. Sandbox1.94.1로 downgrade할 필요는 없으며 과거NCP 관측버전은1.99.0이다.
5. RUN_RECEIPT.json, 모든 command/stdout/stderr/exit/timing, source hashes, raw CSV를 읽는다. Exit0은 과학적 차수의 자동PASS가 아니다. theory/independent_coupled_audit.py의 실제 원시 회계/채널 자기차분과 기존 post-clock 결과를 대조한다. 플랫폼 수치결과는 정당한 잔차·관측량/차수로 비교하며 CSV bytes 자체의 일치를 요구하지 않는다.
6. 새 실행결과를 GitHub와 Drive/Dropbox 지정백업에 보존하고 전체 archive readback 및 DAG 상태를 기록한다. 실패/부분완료도 종료코드와 함께 보존한다. 사용자에게 파일 이동을 맡기지 않는다.

## NCP shell에서 Codex가 실행할 명령 형태

REI_REPO는 Codex가 발견한 기존 checkout이다. REI_SOURCE_SHA는 최종deliveryreceipt의 source_publication_sha다. 별도 Git checkout을 만들지 않는다.

```bash
set -euo pipefail
REI_REPO="$(git rev-parse --show-toplevel)"
REI_BRANCH='research/rei-lrs-v14-physical-birth-20261018'
git -C "$REI_REPO" status --short
git -C "$REI_REPO" fetch origin "$REI_BRANCH"
REI_SOURCE_SHA="$(git -C "$REI_REPO" show "origin/$REI_BRANCH:research/lrs_atomic_native_bridge_20261016/v14/stages/SSPRK2_FINAL_DELIVERY.json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["source_publication_sha"])')"
REI_JOB_ROOT="/tmp/rei_lrs_ssprk2_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$REI_JOB_ROOT/input"
git -C "$REI_REPO" archive "$REI_SOURCE_SHA" research/lrs_atomic_native_bridge_20261016 | tar -x -C "$REI_JOB_ROOT/input"
REI_INPUT_ROOT="$REI_JOB_ROOT/input/research/lrs_atomic_native_bridge_20261016"
python3 "$REI_INPUT_ROOT/v14/time_centered_ssprk2_20261019/run_ssprk2_native.py" \
  --input-root "$REI_INPUT_ROOT" \
  --output-root "$REI_JOB_ROOT/run" \
  --cargo cargo --jobs 2 --mode all
```

Codex가 NCP 외부의 허가된 장치에서 실행을 시작할 때 사용할 기존 연결 정보는 다음과 같다. 비밀키 내용을 출력하거나 복사하지 않는다.

```text
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```

이 연결을 사용자에게 수동으로 수행하라는 뜻이 아니다. 이 session의 controller에서는 해당키가없고 DesktopCommander 월간한도에걸렸으므로 새NCP실행은 NOT_RUN이다. 도구제한을 재접속으로 우회하지 않는다. 실행 가능한 NCP Codex가 위 완성된 자료를 이어받는다.

## 기대하는 구조와 반환물

run/native_owner는 복원된 정확한 source, run/evidence는 명령·로그·종료코드·CSV, run/RUN_RECEIPT.json은 실제 실행 호스트/버전/상태다. --prepare-only는 실제 source 복원과 compiler metadata 확인만 수행한다. 이번 sandbox에서는 fresh prepare-only와 실패 receipt를 검증했으며 wrapper 자체의 all mode를 이미 NCP에서 실행했다고 주장하지 않는다.

NCP에서 새로 반환할 것은 실제 Git/source identity, toolchain/host, 각 단계의 stdout/stderr/exit,14tests의 실제수량,52 transport행과16 coupled설정의 완료/실패수량, raw사건/에너지/clock/차수분석, runtime/resource, Gitcommit/백업objectID와readbackSHA다. 기존 source-on 전체2차/uniformstiff/CaseB/fullEoR/signedBianchi는 별도 실제증거 없이 승격하지 않는다.
