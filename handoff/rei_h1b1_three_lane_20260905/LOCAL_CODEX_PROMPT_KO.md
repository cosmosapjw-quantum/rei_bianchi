# COPY TO LOCAL CODEX — REI H1B1 DEB-member execution

이곳은 실제 사용자 workstation의 local Codex다. 대화 스레드는 scope/최종 결과를 판정하고, 작업 스레드는 source 작성·REI publication을 담당한다. default는 **executor-only**다.

## 먼저 받아야 하는 입력

작업 스레드가 발행한 실제 `LOCAL_EXECUTION_INPUT.json`과 그 immutable GitHub source locator가 필요하다. 그것에 candidate commit/tree가 아직 없으면 현 문서만으로 candidate GREEN을 실행하지 마라. 입력 부족을 한 번 반환하고 새 wrapper·kernel 설치·readiness 단계는 만들지 않는다.

계약 code baseline:

    repo cosmosapjw-quantum/rei_bianchi
    baseline commit edec9771c1e725484ec1a7250ba0d340eb13e21b
    baseline tree   d1250dac231688c1a0de7a84c93a15732a9a2660

그 baseline의 signed_archive_chain.py와 test_signed_archive_chain.py를 그대로 사용한다. 새 test/member code는 작업 스레드의 정확한 candidate에 따라야 한다. 문서만 보고 과거 SHA를 새 candidate로 가정하지 마라. 다른 세션의 ChatGPT runtime/DNS 실패를 이 workstation에 상속하지 않는다.

## 소스와 실행

사용자 dirty checkout을 reset/clean하지 않는다. 별도 worktree에서 input의 commit/tree, base ancestry, expected test/code SHA256·Git blobs, no partial/promisor state를 확인한다. 정확한 source baseline과 candidate를 섞지 않는다. 새 persistent output root는 기존 파일을 덮지 않는다.

현재 작업에 필요한 것은 Python, gpg/gpgv, dpkg-deb와 구현이 실제 사용하는 표준 도구뿐이다. Wolfram/SymPy/mpmath/Octave/Sage/Singular/Lean 등이 local에 있다는 사용자 진술은 환경 계획의 입력으로 수용하되, 이번 byte 검증에 불필요한 모든 CAS probe/재설치는 하지 않는다. 이후 수학 작업은 선택된 실제 kernel/version/source를 당시 기록한다.

작업 input의 exact argv를 사용한다. 핵심 command 형태:

    python3 -B docs/rei_runtime_03a4_h1b1_snapshot_package_census/test_deb_member_census.py --report <새 절대 JSON 경로>
    python3 -B docs/rei_runtime_03a4_h1b1_snapshot_package_census/test_signed_archive_chain.py --report <다른 새 절대 JSON 경로>
    python3 -B scripts/verify_repo.py

RED revision에서는 첫 명령의 7개 구현부재 assertion/exit1을 기대하고 import/API 오류와 구별한다. candidate에서는 7/7 PASS, 기존 donor18은18/18 PASS여야 한다. 새 parser/limit test가 있으면 그 ID/count/결과를 별도로 기록한다. imported 부모 test를 재발견해25개를 신규시험이라고 세지 않는다.

모든 실행은 command, start/end, source commit/tree, elapsed, 실제 exit/timeout, stdout/stderr 전체, test IDs/개수, skip/error, source 전후 hash를 보존한다. expected RED도 process exit를0으로 바꾸지 않는다. 실패하면 최초 결과를 남기고 무조건 재실행하지 않는다. source 수정이 필요하면 직접 고치지 말고 작업 스레드에 최소 수정안을 반환한다.

## 실제 archive 관측

WORK_THREAD_PROMPT_KO.md의 기존 GCC DEB가 실제 존재하고 checksum이 맞으면 read-only decoder로 control과 지정 regular member를 확인하는 진단을 수행할 수 있다. 그 코드가 signed-chain API와 분리된 관측인지 명시한다. 실제 Ubuntu signed metadata/keyring이 없으면 `NOT_RUN_MISSING_REAL_SIGNED_CHAIN_INPUTS`; historical pinned package/member 확인은 `REAL_GCC_MEMBER_BYTES_CONFIRMED_ONLY`로만 기록한다. 다운로드/apt install/downgrade, rootfs build, maintainer scripts, payload 실행, installed symlink 변경은 하지 않는다.

## 반환 계약

새 디렉터리 `REI_H1B1_MEMBER_LOCAL_RETURN_<run-id>` 아래 최소한 다음을 생성한다.

- 실제 입력 LOCAL_EXECUTION_INPUT.json 사본과 그 hash.
- RETURN_INDEX.json: source/revision별 IDs, command별 exit/timeout/count/status, source 불변성, 실행 invocation 수, 새 caller-authority 주장 없음.
- commands/ 아래 raw stdout/stderr 및 각 machine result.
- identity/ 아래 exact HEAD/tree, donor/test/code hashes와 필요한 도구 경로/version/observed hash.
- patches/ 는 source 변경이 금지돼 기본 비어 있음. 작업 스레드가 사전에 별도 한정 위임한 경우에만 실제 patch/변경목록.
- SHA256SUMS: payload 전 파일을 나열하고 파일 수/extra/missing까지 확인. 자기 자신과 최종 ZIP hash를 내부 manifest에 넣지 않는다.

디렉터리를 ZIP으로 만들고 외부 SHA256을 계산한다. 실제 ZIP bytes를 첨부/전달하며 호스트 경로만 반환하지 않는다. temp key/private signing key/token은 포함하지 않는다. 내용이 같은 재전달을 새 native invocation으로 세지 않는다.

local은 GitHub/Atlassian push의 기본 담당자가 아니다. raw return을 작업 스레드에 전달하고 종료한다. 이 작업은 REI production runtime이 아니다. attempt ref·lease·Section-0·controller/worker, BASS/REC/HTT 소스·조회, first interval/provider, merge/ready/force push를 전부 금지한다.
