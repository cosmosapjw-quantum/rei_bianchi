# REI H1B1 — 대화 / 작업 / local Codex 3분할 인계

## 현재 결정과 단일 목표

이 대화는 범위·증거 판정 스레드로 유지한다. 작업 스레드는 구현·코드 검토·REI 게시를 맡고, local Codex는 사용자의 실제 workstation에서 지정 소스의 실행과 raw evidence 반환을 맡는다. 새 세션을 자동 생성하거나 실행을 자동 전달한 것은 아니다.

다음 작업은 기존 H1B1의 **인증된 DEB → control identity → 지정 regular member의 SHA-256** 연결이다. 새로운 geometry, 새로운 환경 승인 계층, 전체 rootfs builder를 만들지 않는다.

- 고정 code baseline: REI PR #68, commit `edec9771c1e725484ec1a7250ba0d340eb13e21b`, tree `d1250dac231688c1a0de7a84c93a15732a9a2660`.
- 기존 `signed_archive_chain.py`와 18개 시험은 재사용·불변. 기존 PASS는 합성 signed metadata를 실제 GnuPG로 검증한 결과이지 실제 Ubuntu census 완료가 아니다.
- REI #67의 native xAct 최초 1회, 12/12 true, 416 exact-zero entry와 `Verbose::shdw` 한계는 historical evidence다. 새 실행으로 세지 않는다. BASS owner 작업은 다른 스레드가 소유하며 여기서는 BASS를 다시 읽거나 수정하지 않는다.

## 이번 대화 스레드의 실제 산출

이전에 chat에만 있던 일곱 사례의 시험을 실제 파일로 materialize했다. 이는 새 source revision이며 과거 미게시 파일의 byte-identical 복구라는 주장이 아니다. 사례의 의미는 유지하고 create-only `--report` 출력을 추가했다.

실제 관측:

- Python 구문 컴파일 성공.
- 7 tests / 7 `MISSING_H1B1_DEB_MEMBER_CENSUS` assertion failures / 0 errors / 0 skips, process exit 1.
- 시험 import에 사용한 PR #68 `test_signed_archive_chain.py`를 GitHub connector에서 가져온 text로 materialize하고 Git blob `d47308ca29b7a4fdd8c02ca03060f977d5e7716f`와 일치 확인.
- 이 RED는 새 candidate와 exact donor-test의 isolated snapshot에서 수행했다. 전체 repository checkout/ancestry 검증 또는 GnuPG fixture 실행이 아니다. setup은 member 구현 부재에서 반환했다.
- 네 종류의 inert synthetic DEB를 `/usr/bin/dpkg-deb`의 `--ctrl-tarfile`, `--fsys-tarfile`로 읽어 정상 control/member, control version mismatch, symlink type, `./path`와 `path` 중복을 확인했다. archive를 filesystem에 extract하거나 payload를 실행하지 않았다.
- 이 세션의 terminal/Python/dpkg-deb는 작동했다. 직접 raw-GitHub 다운로드는 DNS 실패했고 같은 실패를 반복하지 않았다. GitHub connector read/write는 별도 경로다.

따라서 `EXPECTED_RED_OBSERVED`와 `PASS_SYNTHETIC_FIXTURE_FORMAT_ONLY`만 인정한다. member consumer GREEN, 실제 Ubuntu trust-chain, local workstation 검증, 전체 H1B1 완료는 아직 아니다.

## 세 역할과 인계 순서

대화 스레드: 승인된 범위·불변 입력·acceptance를 고정하고 반환 결과를 한 번 판정한다. 구현과 local 실행을 동시에 복제하지 않는다. 결과가 오면 원본 ZIP/manifest, 정확한 변경 bytes, 실행별 ID/count/exit/log, source 불변성, claim ceiling을 확인한다.

작업 스레드: 아래 WORK_THREAD_PROMPT_KO.md를 실행한다. 단일 구현 작성자다. `deb_member_census.py`를 작성하고 explicit RED→candidate GREEN 계획을 만든다. local 실행 대상 commit/tree를 채운 LOCAL_EXECUTION_INPUT.json을 발행하고 멈춘다. 반환 후 1회 PHYS-MATH, 이어서 1회 PHYS-MATH-CODE review 및 승인된 최대 1회 P0/P1 repair를 수행한다. REI child branch/Draft PR만 게시한다.

local Codex: LOCAL_CODEX_PROMPT_KO.md와 실제 LOCAL_EXECUTION_INPUT.json을 받는다. default는 executor-only다. 요청되지 않은 source patch, dependency install, rebase, push를 하지 않는다. candidate source를 바꿔야 하면 raw 실패와 최소 수정안을 작업 스레드로 반환한다. local의 수학 패키지 설치 여부를 다시 승인 받지 않으며 필요한 도구만 버전/경로 확인한다.

진행: 이 package → 작업 스레드(candidate + exact local input) → local Codex(raw results) → 작업 스레드(review + REI evidence publication) → 이 대화 최종 판정.

## Claim boundary

이번 slice의 최대 결과는 `PASS_H1B1_AUTHENTICATED_DEB_MEMBERS`: 주어진 explicit trust policy 하의 signed-chain과 archive 내부 regular bytes 연결이다. `authority_effect=NONE`, `installed_files_verified=false`, `full_census_complete=false`를 유지한다.

내부 member 확인은 설치된 canonical symlink, ELF closure, Rust closure, host epoch, Section-0, first interval 또는 provider 승인이 아니다. BASS/REC/HTT source, production attempt ref/lease/controller/worker, host package 변경, rootfs/Docker build, main/기존 evidence branch 변경, merge/ready/force-push는 범위 밖이다.

## 읽을 파일

1. WORK_THREAD_PROMPT_KO.md
2. LOCAL_CODEX_PROMPT_KO.md
3. WORK_CONTRACT.json
4. 위 docs 경로의 test_deb_member_census.py
5. evidence/CONTROL_THREAD_OBSERVATION.json 및 raw RED logs

문헌/API 근거는 Debian 공식 문서만 사용한다: https://manpages.debian.org/bookworm/dpkg/dpkg-deb.1.en.html 및 https://manpages.debian.org/bookworm/dpkg-dev/deb.5.en.html . `dpkg-deb`는 archive 조작 도구이지 인증기나 installer가 아니다. 향후 구현은 기존 signed-chain을 먼저 호출하고 package metadata/member를 읽어야 한다. CAS로 archive identity를 대신하지 않는다.
