# 다른 스레드 / local Codex 실행 프롬프트 — REI M2 owner-native calibration

@GitHub @Superpowers @Wolfram @Atlassian Rovo

## 목표와 승인 범위

이 대화는 `cosmosapjw-quantum/rei_bianchi`의 연속 작업이다. 새 수식이나 실행기를 복제하지 말고, 이미 존재하는 BASS PR #130의 native xAct/xCoba calibration을 정확한 소스에서 한 번 실행하고 결과를 보존하라. REI PR #64/#65는 독립 비교 oracle이다. 공통 geometry owner는 BASS로 유지한다.

현재 사용자는 REI 저장소의 새 격리 branch/commit/non-force push/Draft PR 및 REI 관련 Atlassian append-only 동기화를 승인했다. BASS/REC/HTT source 변경은 이 프롬프트가 승인하지 않는다. BASS에서는 기존 diagnostic을 읽고 격리 worktree에서 실행하는 것만 허용한다. 오류가 BASS diagnostic 수정을 요구하면 원 결과와 최소 수정 제안을 보존하고 BASS owner로 넘겨라. 임의로 BASS production/registry를 고치지 마라.

이번 목표의 native xAct 수식검산은 REI Rust/MPFR production native attempt와 전혀 다른 실행이다. REI attempt-ledger ref, local lease, controller, worker, Section-0, first interval, provider, Docker historical-host 복원은 이번 작업에서 전부 금지한다. Rust는 사용자 시스템에 이미 있으므로 재설치하지 마라.

## 정확한 입력 소스

1. 실행 대상: `cosmosapjw-quantum/bass` PR #130
   - branch: `research/bg02-b0r1-native-xcoba-calibration-20260905-r1`
   - commit: `477371143f15ef2625a7de21a5d178b09ffc1c32`
   - tree: `fe4c9f9b6deae0bf072dd553cd046c0a4a7801e3`
   - status at handoff: `PREPARED_UNEXECUTED`
   - files: `research/diagnostics/bg02_b0_20260905/native/{CONTRACT.json,README.md,calibrate.wls,run_native.py}`
2. BASS typed reference PR #129
   - commit: `ac01009dec8678d9f1b8af10fb915b871e2358fd`
   - tree: `ef10fb3199645e3962fce3ad322e5a23d5971e2f`
3. REI 4D sign oracle PR #64
   - commit: `3f2f876b219d5c435cfd5d0dc70236a1edc1fd96`
   - tree: `87a30c114b00a987beefc34d757a0eb736dc54ba`
4. REI exceptional oracle PR #65
   - commit: `7d2fe29d46e3aab4a649c3679ae028e82ef0796c`
   - tree: `08970b6b35bc749b37be9db6b9aaa6a2848fe06e`
   - prior exact run: `33932820559`, job `101214764766`
   - artifact: `9959145017`
   - artifact ZIP SHA-256: `607c8dc15a88b318aef29fc7fd45eb9de24ce03f12a5480d61d920bb30959157`
5. xAct archive
   - name: `xAct_1.3.0.tgz`
   - required SHA-256 from BASS contract: `7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be`
   - known candidate locations, not assertions that these files currently exist:
     `/mnt/data/xAct_1.3.0.tgz`
     `/tmp/bass-bg02-cas-fix3/BASS_BG02_CAS_BATCH_FIX3_20260904/vendor/xAct_1.3.0.tgz`
     the user's existing downloaded/vendor copy.
   - locate an actual file and hash it. Never fabricate a matching path or digest, and do not download a replacement unnecessarily.

처음에 두 PR의 최신 head/comment를 읽어 다른 세션이 이미 native 결과를 게시했는지 확인하라. 새 head가 보이면 새 파일을 old tested bytes로 취급하지 마라. 기존 exact commit은 regression anchor로 보존하고, 새로운 결과가 실제 current gate를 닫았는지 내용으로 판정하라. 이미 닫힌 동일 실행은 중복하지 마라.

## 현재 과학적 경계

`(-,+,+,+)`, `epsilon_123=+1`, `tau=c*t`, `K_ab=+h_a^c h_b^d nabla_c n_d`, `q_a=-h_a^c T_cd n^d`, `kappa_G=8*pi*G/c^4`.

Reference target:

    C_a = D^b K_ab - D_a K
    M_a = -h_a^c n^d E_cd = -C_a - kappa_G q_a

곡률 view는 Riemann의 all-lower 순서와 Ricci 수축을 함께 지정한다. 물리적 Ricci 전체를 부호 반전하지 마라. `calibrate.wls`는 native xCoba curvature로 Einstein projection을 구성하며, reference는 좌표계 metric을 별도로 미분한다. expected momentum을 native output에 대입하는 방식은 금지한다.

검산 계량:

    ds^2 = -d tau^2 + exp(2 H1 tau) dx^2
           + exp(2 H2 tau-2 a0 x) dy^2
           + exp(2 H3 tau-2 a0 x) dz^2.

Full checks에서 H1,H2,H3,a0를 독립으로 유지한다. 비영 sign witness에서만 `a0=H1=1/ell`, `H2=H3=0`, `tau=x=0`, `ell>0`를 대입한다. 옛 momentum 식과의 discrepancy target은 `+4/ell^2`이다. 이는 off-shell identity witness이며 물리적 우주론 예측이 아니다.

## 실행 절차

### 1. 짧은 capability 확인

실제 terminal/container와 `python3`, `git`, `wolframscript`가 실행되는지 확인한다. Python은 orchestration이며 xAct 대체가 아니다. Wolfram MCP가 없더라도 local `wolframscript`가 작동하면 그 경로를 쓴다. process 시작 전 실패는 수학 FAIL이 아니다. 같은 capability 실패를 반복하지 말고 한 initial attempt와 한 diagnostic retry 이하로 제한한다.

### 2. 소스와 worktree 준비

해당 repo `AGENTS.md`와 native `CONTRACT.json`, `README.md`, `run_native.py`, `calibrate.wls`를 읽는다. 사용자의 dirty checkout을 reset/clean하지 않는다. 기존 BASS clone에 필요한 commit이 있으면 그로부터 새 detached worktree를 만들고, 없으면 정상적인 GitHub fetch/clone을 사용한다. partial/promisor clone을 authority로 쓰지 않는다.

실행 worktree에서 다음을 실제 비교하고 저장한다.

    git rev-parse HEAD
    git rev-parse 'HEAD^{tree}'
    git status --porcelain --untracked-files=all

HEAD/tree는 위 PR #130 pin과 같고 worktree는 깨끗해야 한다. 네 diagnostic/activation 파일의 Git blob 및 SHA-256도 기록한다. launcher는 실제 HEAD/tree를 기록할 뿐 이 문서의 고정값과 비교하지 않으므로, 이 비교를 생략하지 마라.

`XACT_ARCHIVE`를 실제 존재하며 SHA-256이 일치하는 archive 경로로 정한다. `BASS_WT`는 확인된 detached worktree, `OUT`은 checkout 밖의 새 persistent 절대경로로 정한다. 기존 evidence 디렉터리는 재사용하지 않는다.

### 3. 정확히 기존 launcher 실행

다음 한 명령을 사용한다. 변수는 위 단계에서 실제 확인한 값이다.

    PYTHONDONTWRITEBYTECODE=1 python3 \
      "$BASS_WT/research/diagnostics/bg02_b0_20260905/native/run_native.py" \
      --repo "$BASS_WT" \
      --xact-source "$XACT_ARCHIVE" \
      --output "$OUT"

필요하면 `--wolfram`에는 실행 가능한 `wolframscript` 경로만 명시한다. CLI 호환성을 확인하지 않고 raw kernel executable을 같은 옵션으로 대체하지 마라. 기본 timeout은 launcher에 설정된 값을 사용한다. checkout이나 output 디렉터리를 자동 삭제하지 않는다.

명령의 exit code, stdout/stderr, `CHECKPOINT.json`, `PROCESS_RECEIPT.json`, 생성된 경우 `native.json`을 모두 보존한다. auxiliary CAS 설치/실행이 이 primary lane을 막아서는 안 된다.

### 4. 결과 독립 판독

외형적인 exit 0이나 `native_xact_evaluated=true` 하나로 성공 판정하지 마라. 실제 source head/tree, input hashes, archive hash, final source cleanliness, native status, exact check IDs, 각 bool과 raw residual을 읽는다.

필수 12개 ID:

    PACKAGE_DEFINITIONS
    NORMAL_POSITIVE_K
    RAW_TO_BASS_RIEMANN
    PHYSICAL_RICCI_BASS
    PHYSICAL_RICCI_XACT
    GAUSS_POSITIVE_K
    CODAZZI_POSITIVE_K
    MIXED_RICCI
    MOMENTUM_MATTER
    HAMILTONIAN
    NONZERO_BIANCHI_V
    WRONG_RICCI_SIGN

성공에 필요한 두 terminal status:

    PROCESS_RECEIPT.json: PASS_NATIVE_CALIBRATION_ONLY
    native.json: PASS_NATIVE_TYPED_VIEW_CALIBRATION_ONLY

그리고 exit=0, timeout=false, failed_ids=[], messages=[], 정확한 12/12 true, source/input unchanged, clean checkout을 모두 확인한다. raw residual이 symbolic unevaluated expression으로 남으면 PASS가 아니다.

실패하면 최초 실패를 `RUNTIME_UNAVAILABLE`, `SOURCE_OR_ARCHIVE_IDENTITY`, `NATIVE_API_OR_MESSAGE`, `NONZERO_MATHEMATICAL_RESIDUAL`, `OUTPUT_OR_SOURCE_POSTCHECK`로 구분한다. 이 프롬프트는 BASS 소스 패치를 승인하지 않는다. 기존 실패 evidence를 보존하고 BASS owner에게 최소 재현/수정 요구를 넘긴다. 맞을 때까지 무제한 재실행하지 않는다.

## 1회 dual audit와 visual 경계

PHYS-MATH: curvature slots, K/q conventions, +4/ell^2 witness, Hamiltonian sign, 단위, isotropic/zero-momentum blind spot, calibration의 한정 범위를 점검한다.

PHYS-MATH-CODE: native output이 reference target으로 덮어써지지 않았는지, 실제 MetricCompute 경로, source pins, 메시지/시간초과/receipt 검사와 donor independence를 점검한다. 두 검토를 한 assistant가 수행하면 sequential review라고 기록하고 독립 reviewer라고 쓰지 않는다.

REI #64/#65 artifact의 PNG/SVG가 실제로 보이면 exact data와 함께 90 mm/180 mm 가독성·legend·zero display floor를 읽고 시각감사를 기록한다. 이미지 표시가 불가능하면 `VISUAL_REVIEW_PENDING`을 유지한다. 이 경우 native computation의 제한된 성공과 전체 visual closeout을 구별해 보고한다. plot 파일 생성만으로 visual PASS를 쓰지 않는다.

## REI 게시 및 Atlassian 동기화

실제 결과가 생기면 REI repo의 새 evidence-only child branch에 실행 receipt/log/소스 identity/감사문/변경된 다음 단계만 게시한다. secret, 토큰, 머신의 무관한 환경변수는 포함하지 않는다. 작업한 host의 `/home/...` 경로를 ChatGPT sandbox 링크로 꾸미지 않는다. source나 test를 수정했다면 실제 수정 여부와 모든 실패 이력을 따로 기록한다.

BASS PR #130에 소스 변경·status 변경·merge를 하지 않는다. 이 프롬프트 범위에서 REI에 보고만 게시한다. BASS owner 반영은 별도 권한과 owner 작업이다.

Atlassian은 `BASS-18`에 append-only 실행 요약과 GitHub exact 링크를 넣는다. 필요하면 기존 REI page `26574849`에 footer를 추가한다. issue status, 공식 dependency link, blocker severity, provider나 scientific status는 변경하지 않는다. 게시 후 원격 commit/tree/파일/PR/comment를 다시 읽어 실제 게시와 로컬 생성물을 구별한다.

## 금지 사항과 마지막 보고

금지: 기존 historical receipt 재구성/덮어쓰기, expected hash 교체, host GCC downgrade, Docker rootfs/H1B1 작업 혼합, production registry amendment, REI Section-0, attempt-ledger POST, local lease, controller, native worker, first interval, provider admission, ready/merge/force push.

최종 보고는 (1) 실제 실행한 것, (2) exact source/출력 identity와 실패 또는 통과 근거, (3) 게시된 GitHub/Atlassian 위치, (4) 남은 visual/native-owner/constraint-propagation/runtime gate, (5) 다음 단일 작업 순서로 작성한다. native calibration이 성공해도 다음은 별도 버전의 owner registry/consumer amendment이지 background evolution 또는 REI first interval이 아니다.

여기서도 native 실행 경로가 없으면 새로운 비슷한 runner나 또 다른 governance 단계는 만들지 마라. 이 exact launcher와 위 명령을 실제 Wolfram Engine이 있는 local Codex 세션으로 전달하고 `BLOCKED_NATIVE_RUNTIME_UNAVAILABLE`로 종료하라. 수식검산과 REI production attempt를 혼동하지 마라.
