# BASS_HE CODE-I02 outcome-blind independent re-audit

이 프롬프트만 새 독립 Codex context에 전달한다. 이 문서는 기존 결과의 개수나 결론을 제공하지 않는다. 이전 구현·검토 대화, PR 댓글, 연구 보고서를 이미 읽었다면 blind=false를 기록하고 독립/비공개 결과 검토라고 과장하지 않는다. 작업은 audit-only다. 구현을 고친 사람이 이 실행에서 independent review를 승인하지 않는다.

## 고정 대상과 권한

Repository: cosmosapjw-quantum/BASS_HE
Target PR: 15
Execution commit: ac04d2a9e62120a0da4377ddf92451fde0c44431
Execution tree: 5697bfb7b2ceae5854499a8132b44e573672df85
Source subtree: fb9344caec799308f995aee67a231890f602e16d

src/bass_he/spectral.py blob: cad7901342cf7003e55e40dcff2202486fb8a223
src/bass_he/sturm_geometry.py blob: a9b09af1ffd165c7fc03a2e100bb0a0dfe84c580
tests/test_dr11h_certificate_binding.py blob: ea7e768b6a15815a083787d459ab130ebc6bb40d

사용자는 이 프로젝트의 read/write/download/upload, GitHub non-force evidence publication, Google Drive+Dropbox create-only 백업을 승인했다. merge/force-push/reset/clean, 다른 session process 조작, VM·credential·firewall 변경, 유료 자원 생성은 금지한다. 이 review target의 production code는 변경하지 않는다.

전달된 audit packet의 디렉터리를 PACKET_ROOT로 고정한다. 포함된 audit/test_hostile_certificate.py는 이미 작성된 실행 파일이므로 다시 설계하지 않는다. 다만 Phase 1이 끝나기 전에는 그 내용, evidence/, HOSTILE_AUDIT_REPORT_KO.md, AUDIT_RESULT.json을 읽지 않는다. 패킷은 별도 publication commit/tree 또는 외부 SHA sidecar와 MANIFEST.sha256에 묶어 확인한다. moving PR #17 HEAD를 execution code로 사용하지 않는다.

## Phase 0: identity와 환경

먼저 PR #15 ref를 fresh-read한다. 현재 head가 위 실행 commit과 달라도 자동 승격하거나 checkout 기준을 바꾸지 않는다. 변경을 기록하고 명시적 대상 재지정이 필요한 것으로 반환한다.

기존 repository에서 다음과 같은 고유 detached worktree를 만든다. 기존 경로를 덮어쓰거나 기존 작업을 stash하지 않는다.

```bash
set -eu
REPO_ROOT=$(git rev-parse --show-toplevel)
REV=ac04d2a9e62120a0da4377ddf92451fde0c44431
TREE=5697bfb7b2ceae5854499a8132b44e573672df85
RUN_ROOT=$(mktemp -d "$HOME/bass-he-i02-reaudit.XXXXXXXX")
git -C "$REPO_ROOT" fetch origin "$REV"
git -C "$REPO_ROOT" worktree add --detach "$RUN_ROOT/target" "$REV"
TARGET="$RUN_ROOT/target"
OUT="$RUN_ROOT/evidence"
mkdir "$OUT"
test "$(git -C "$TARGET" rev-parse HEAD)" = "$REV"
test "$(git -C "$TARGET" rev-parse 'HEAD^{tree}')" = "$TREE"
test "$(git -C "$TARGET" rev-parse HEAD:src)" = fb9344caec799308f995aee67a231890f602e16d
test -z "$(git -C "$TARGET" status --porcelain)"
export TARGET OUT
```

해당 ref를 읽을 수 없으면 IDENTITY_OR_SOURCE_BLOCKED로 반환한다. 기존 main을 대신 사용하지 않는다. root AGENTS.md를 읽고, 역할/권한 충돌을 먼저 해소한다.

Python >=3.11, NumPy 2.3.5, SciPy 1.17.0, pytest를 확인한다. 정확한 버전과 import 경로를 기록한다. root requirements-dr11e.txt가 optional Sturm dependency authority다. 기존 격리 환경을 재사용할 수 있다. 없으면 새 RUN_ROOT/venv 안에만 다음을 설치한다. 전역 apt/pip 설정은 바꾸지 않는다.

```bash
python3 -m venv "$RUN_ROOT/venv"
PY="$RUN_ROOT/venv/bin/python"
"$PY" -m pip install -r "$TARGET/requirements-dr11e.txt" 'pytest==9.0.2'
export PYTHONPATH="$TARGET/src"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
"$PY" - <<'PY'
import os, pathlib, platform, numpy, scipy, pytest
import bass_he.spectral as s
assert pathlib.Path(s.__file__).resolve() == pathlib.Path(os.environ['TARGET'],'src/bass_he/spectral.py').resolve()
print(platform.python_version(),numpy.__version__,scipy.__version__,pytest.__version__)
print(s.__file__)
PY
```

설치 실패·import failure는 ENVIRONMENT_BLOCKED이지 과학 test FAIL이나 PASS가 아니다. 이미 맞는 환경을 재사용하면 PY를 그 interpreter의 절대 경로로 지정하고 변경 사유를 기록한다.

## Phase 1: 결과 비공개 초기 감사

읽기 허용: target의 AGENTS.md, src/bass_he/spectral.py, src/bass_he/sturm_geometry.py, 필요 최소한의 geometry.py, sturm_anchor.py, 관련 입력/직렬화 정의. 기존 author 보고서와 test 결과를 정답으로 삼지 않는다.

입력 domain, canonical representation, certificate validity, consumer call order를 자체적으로 추적한다. 정상 constructor 결과와 외부/복원 결과를 구분하고, 정확한 identity contract를 먼저 정의한다. 형식·구조 검사를 numerical evidence나 origin authentication과 혼동하지 않는다. 추정만으로 finding을 만들지 말고 최소 반례 또는 직접 코드 증거를 제시한다.

INITIAL_FINDINGS.md에 findings, severity, 근거, 반례, 범위 밖 항목을 기록한다. 숨은 사고과정이 아니라 검증 가능한 근거만 쓴다. 이 파일을 생성한 뒤 SHA256와 UTC를 INITIAL_SEAL.json에 create-only로 기록하고 fsync한다. Phase 2에서 초기 파일을 수정하지 않고 추가 판단은 별도 파일에 남긴다. 이 seal은 절차적 기록이지 독립성을 증명하는 암호학적 attestation은 아니다.

## Phase 2: 준비된 테스트와 상호 대조

이제 packet manifest, audit/test_hostile_certificate.py, 이전 evidence와 report를 읽어도 된다. packet의 원문은 수정하지 않는다. 아래 두 검사를 각 한 번만 실행한다. 패킷 경로는 실제 materialization 경로를 사용한다.

```bash
cd "$TARGET"
set +e
"$PY" -m pytest -q -p no:cacheprovider \
  tests/test_dr11h_certificate_binding.py \
  --junitxml="$OUT/official.xml" >"$OUT/official.log" 2>&1
OFFICIAL_RC=$?
BASS_AUDIT_EVIDENCE="$OUT" "$PY" -m pytest -q -p no:cacheprovider \
  -c "$TARGET/pyproject.toml" \
  "$PACKET_ROOT/audit/test_hostile_certificate.py" \
  --tb=short --junitxml="$OUT/hostile.xml" >"$OUT/hostile.log" 2>&1
HOSTILE_RC=$?
set -e
printf 'official=%s\nhostile=%s\n' "$OFFICIAL_RC" "$HOSTILE_RC" >"$OUT/EXIT_CODES.txt"
```

기대 test 개수나 기존 severity에 결과를 맞추지 않는다. pytest failure를 artifact capture 성공과 구분한다. xfail/skip으로 돌리거나 assert를 반대로 바꿔 GREEN을 만들지 않는다. 실제 module import path가 target/src인지와 source hash가 검사 전후 그대로인지 확인한다.

테스트가 관찰하는 경계가 validator인지 anchor 호출인지, 실제 action 계산인지 구분한다. malformed payload 통과와 실제 잘못된 물리량 관측을 섞지 않는다. 새로운 반례가 필요하면 한 원인당 최소 집중검사만 추가한다.

금지: resume-004 재실행, 56-action replay, 15-arm worker sweep, 전체 unchanged suite, R1/R2 재분석, bass_cr F1/F2/F3, HH M3B, Eq55 또는 production probability. 이 검수 때문에 cloud batch를 새로 만들지 않는다.

## 반환·게시

최종 RETURN_REPORT.json에는 execution commit/tree, source subtree, packet identity, 실제 환경, command/cwd/UTC/exit codes/JUnit counts, 초기 seal SHA, fresh observations, reused evidence, 미실행 항목을 기록한다.

판정 필드: critical_findings, important_findings, minor_findings, CODE_I02_CLOSED, lossy_integer_repair_supported, full_certificate_fail_closed, independent_context, prior_exposure, outcome_blind_phase1, PROMOTE, Eq55_next_node_authorized. 조건부 claim과 좁은 endpoint-reuse contract를 분리한다. 초기에 defect를 읽지 못했다는 것만으로 blind=true라고 하지 않는다.

Critical/Important finding, identity mismatch 또는 환경 blocker가 있으면 HOLD로 반환한다. certificate policy/schema/physical tolerance 수정은 연구 스레드에 반환한다. 이 reviewer가 수정하고 자기 변경을 independent PASS로 승인하지 않는다. Critical=0, Important=0, 충분한 fresh focused evidence, 적격 independent context가 모두 확인되더라도 Eq55 실행은 이 프롬프트가 승인하지 않는다. 다음 연구 노드에 대한 권고만 반환한다.

publication checkout은 execution checkout과 분리한다. fresh-read한 PR #17 research/shared-c64-crossrepo-20260928의 새로운 research/shared_c64/20260929/CODE_I02_HOSTILE_RETURN/<UTC-id>/ 경로에 결과를 non-force로 게시한다. concurrent 변경은 읽고 append-only로 reconcile한다. target PR #15를 수정하거나 merge하지 않는다.

새 evidence ZIP과 manifest/receipt를 Google Drive folder 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI, Dropbox /BASS_DERIVATION_DOSSIERS_20260912/에 create-only로 백업한다. 기존 packet은 중복 업로드하지 않는다. 두 provider의 실제 ACK/object id/size/checksum 확인 후에만 완료라 하고, remote restore는 실제 수행 여부로 별도 표기한다. SELECTIVE READBACK tier가 닫히면 반복 다운로드를 중지한다.

마지막에 판정, exact identities, actual test 결과, backup 상태, 남은 최소 조치만 반환한다. 기존 이론 전체를 다시 작성하지 않는다.
