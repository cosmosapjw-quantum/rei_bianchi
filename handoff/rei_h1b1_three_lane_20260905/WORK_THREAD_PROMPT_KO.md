# COPY TO WORK THREAD — REI H1B1 authenticated DEB members

@GitHub @Superpowers @Atlassian Rovo

이곳은 작업 스레드다. 별도 대화 스레드가 scope와 반환 evidence를 판정하고 local Codex가 실제 workstation 실행을 담당한다. 사용자는 필요한 수학 패키지가 local에 있다고 명시했다. 새 runtime-readiness 작업이나 패키지 설치를 반복하지 마라.

## 목표와 기준

`cosmosapjw-quantum/rei_bianchi`의 PR #68 signed-chain component에 DEB control/member 검증을 붙인다. 이 인계 commit은 #68의 child이며 그 파일을 포함하지만 **구현이 없는 test-first 상태**다. 작업 시작시 이 문서를 실제 읽은 immutable handoff commit/tree를 기록하고, 그 head에서 새 격리 child branch를 만든다. canonical code baseline은 다음과 같다.

    commit edec9771c1e725484ec1a7250ba0d340eb13e21b
    tree   d1250dac231688c1a0de7a84c93a15732a9a2660

AGENTS.md, handoff WORK_CONTRACT.json, 기존 signed_archive_chain.py, 기존 test_signed_archive_chain.py, 새 test_deb_member_census.py를 전체 읽는다. 최신 REI PR만 확인해 동시 동일 구현 존재 여부와 parent drift를 기록한다. BASS/REC/HTT 조사·수정, 기존 xAct calibration 재실행, #67 history 수정은 하지 않는다. 다른 source가 이미 scope를 닫았다면 기존 결과를 intake하고 중복 구현하지 않는다.

## 단일 구현 계약

함수 `deb_member_census.verify_member_census`는 기존 `verify_chain`의 keyword inputs와 `required_members=((archive_filename, regular_member_path, expected_sha256), ...)`를 받는다. 기존 signed-chain을 실제 호출해야 하며 caller가 준 PASS dictionary를 신뢰하지 않는다. donor source/test blobs를 변경하거나 복제하지 않는다.

새 consumer는 먼저 signed-chain 검증, 그다음 DEB format/control identity, 마지막 data tar의 지정 regular member hash를 검증한다. control의 package/version/architecture는 authenticated index와 같아야 한다. `./name` 정규화 정책을 명시하고 정규화 후 중복은 거부한다. 지정 member가 symlink/hardlink/device인 경우 regular witness로 승격하지 않는다. 절대경로·상위경로·모호한 경로와 누락 member를 fail-closed한다. unrelated 정상 symlink가 있다는 이유로 package 전체를 일반적으로 거부하지는 않는다.

추천 구현은 기존 `dpkg-deb --ctrl-tarfile/--fsys-tarfile`를 read-only archive decoder로 재사용하고 tar stream을 제한된 parser로 읽는 것이다. custom ar/DEB parser 전체를 새로 만들지 않는다. payload execution, `dpkg -i`, maintainer scripts, extractall/filesystem extraction은 금지다. 입력·stdout/stderr·decompressed/member/control 크기와 process timeout 한도를 선언하고 한도 초과·truncation·unsupported format을 타입별로 보존한다. single-member 성공만 보고 stream 후반 중복/오류를 생략하지 않는다. 새로운 primitive가 필요하면 최소 추가 테스트로 같은 작업 안에서 검증한다.

반환은 `PASS_H1B1_AUTHENTICATED_DEB_MEMBERS`, 실제 `signed_chain`, 각 `archive_filename/member_path/sha256`를 포함한다. 실제 package bytes와 control/member 관측, decoder 도구 경로·버전·관측 hash, 입력/출력 identity를 연결한다. `authority_effect=NONE`, `installed_files_verified=false`, `full_census_complete=false`를 유지한다. 과거 Ubuntu trust-root authority를 새롭게 승인하는 일은 아니다.

## TDD와 local 인계

일곱 core test의 의미와 파일 bytes를 freeze한다. 기존 대화 스레드 RED는 7/7 intended assertion failure, 0 error/skip, exit1인 isolated-source 관측이다. repo-level/real-signature GREEN으로 부르지 마라. 구현 candidate 이전에 이 handoff exact revision의 RED를 source guard와 함께 보존한다. 주어진 RED evidence를 이유 없이 반복하지 말되 local은 target-host 기준점의 첫 실행으로 한 번 기록할 수 있다.

작업 스레드가 구현 source 작성자다. candidate commit/tree가 생기면 `LOCAL_EXECUTION_INPUT.json`을 발행한다. 반드시 실제 handoff/test baseline commit/tree, candidate commit/tree, changed-file 목록과 hashes, donor/test hashes, 정확한 command arrays, 결과를 받을 새 root 정책, 요청한 gate ID 목록을 채운다. TBD/가짜 SHA를 넣은 문서를 실행 인계로 부르지 마라. immutable input은 publication commit에 자기 hash를 넣는 순환 구조로 만들지 않는다.

local이 확인할 core 순서는 baseline seven-case RED → candidate seven-case GREEN → 기존18 donor regression → 추가 parser/limit 사례 → repository/diff/source checks다. synthetic signature에는 실제 gpg/gpgv를 쓰며 key는 temporary로만 둔다. local은 반환 패키지에서 secret key·token·무관한 홈 파일을 제외한다. 작업 스레드에서 이미 실행한 검사와 local 실행은 서로 다른 invocation으로 기록하고 독립 reviewer라고 부르지 않는다.

## 실제 GCC 파일 확인의 제한된 재사용

local에는 아래 historical DEB가 보고돼 있다. 존재·해시를 새로 확인할 수 있지만 source of trust를 새로 발명하지 않는다.

    $HOME/Dropbox/bianchi/_runtime_receipts/REI_03A4_CC_PROVENANCE_20260904T075833Z-889795/downloads/20250115T120000Z/gcc-13-x86-64-linux-gnu_13.3.0-6ubuntu2~24.04_amd64.deb
    DEB SHA256 7cd398670e8306eabc9e77202f356a3206c440bd9f3dc764680a19be01784776
    regular member usr/bin/x86_64-linux-gnu-gcc-13
    member SHA256 6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234

실제 signed InRelease/Packages/admitted keyring이 없으면 synthetic signature로 이 DEB를 서명해 Ubuntu PASS라고 쓰지 마라. 별도 `REAL_GCC_MEMBER_BYTES_CONFIRMED_ONLY` 관측은 허용한다. full authenticated real-Ubuntu consumer 실행은 `NOT_RUN_MISSING_REAL_SIGNED_CHAIN_INPUTS`로 구분한다. 이 missing input은 synthetic component GREEN을 지우지는 않으며 전체 H1B1을 닫지도 않는다. 이 단계에서는 새 download/census/root build를 확장하지 않는다.

## 반환 intake / 게시

local raw return에서 manifest·실제 source/test bytes·각 command/exit/timeout·정확한 IDs/count·원본 logs·도구 관측을 확인한다. SHA 목록만 보고 의미론적 PASS를 내지 않는다. PHYS-MATH(인증 체인의 논리/claim boundary), 이어 PHYS-MATH-CODE(실제 code path/오류·한도·입력불변성)를 한 번씩 수행한다. 같은 assistant면 SEQUENTIAL_REVIEW. coherent work unit의 감사 후 P0/P1 repair는 최대1회이며 원 RED/실패는 보존한다.

성공한 code/evidence는 REI 새 child branch/Draft PR에 non-force 게시한다. 실패도 사실대로 evidence-only 보존할 수 있으나 GREEN이라 하지 않는다. 원격 commit/tree/files/CI가 실행됐는지 재판독한다. 새 native process나 first interval이 아니다. Jira BASS-18에는 append-only scope/result/pins를 기록하되 status/links/claim gate를 바꾸지 않는다.

여기에 반환할 것은 WORK_RETURN_INDEX.json, 실제 변경 source/patch 또는 commit, local return ZIP+SHA256, gate별 결과와 원 logs 위치, 두 review 결과, 새 PR/CI identity다. full census, installed ELF/Rust, Section-0/provider는 남겨둔다. 구현/실행 결과가 생기면 그때 종료하고 새로운 governance 단계로 연장하지 마라.
