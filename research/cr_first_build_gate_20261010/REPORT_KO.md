# CR_FIRST_V3 production build gate

PR97 receipt가 지정한 `4c547c2d15f63b788c28d01e8eb8f54cbe4bce3c`
(tree `d3340a083324e31ef0833addb5d0324d00fddb76`)에 한정한 변경이다.
과거 P01 출력과 연구 자료는 수정하지 않는다.

`conditional_build.py`는 clean committed revision에서 Cargo 입력, 전체 Rust
source 및 production launcher/gate를 고정하고 새 target directory에서
`axisym_conditional`만 빌드한다. compiler identity, build command/exit/logs,
빌드 전후 source 일치 및 Cargo가 반환한 실제 executable SHA를 receipt로 남긴다.
실행 파일이나 solver를 실행하지 않는다. 출력은 처음에는 checkout 밖에 생성한다.

production runner와 `NativeConsumer`는 subprocess를 시작하기 전에 receipt,
현재 source set 및 executable SHA를 검사한다. `--check-build-only`는 input/build
검사를 수행한 후 native/provider/solver 실행 없이 반환한다. 기존 `--binary`만
전달하는 실행은 이제 `BUILD_RECEIPT_REQUIRED`로 거부된다.

검증은 protocol-compatible stale binary, source 변경/추가, receipt 부재·실패가
`Popen`, provider, `ProductionInterval`, `solve_ivp` 호출 0회에서 거부되는지
확인한다. positive test도 gate-only이다. test fixture receipt는 실제 production
build 증명이 아니다.

최초 component 실행은 13/13 PASS(exit 0): 신규 gate 8개와 기존 production
boundary 5개다. 최초 failure는 없고 repair round는 사용하지 않았다.
`VALIDATION.json`과 `evidence/component_tests.log`에 결과를 보존했다.
`git diff --check`도 exit 0이다. 후속 independent Astra review
(controller-recorded)는 `PASS_BUILD_RECEIPT_REVIEW`로 판정했다.

담당자는 gate source를 commit한 뒤 clean revision
`f9135eca0d41dd00465fcd524c07872a9c3c8fb8`
(tree `35389ad8e9a6baf7dcde91a93e5e7d53495911fd`)에서 새 target으로
실제 build를 수행했다. exit 0, build wall 2.72260482198908 s이며,
556,616-byte executable SHA는
`e098111ee8e403c5985fea20cfca7b0408e5d82ea77c2eded50cff72d1392d0f`다.
receipt SHA는 `eba5b76a2d1056586aba3d06370ffd81585c1d470c4a1ea5b6835d6de51a52fa`이며
로컬 Dropbox의 `REI_CR_FIRST_BUILD_RECEIPT_20261010_f9135ec/`에 compiler/build
명령·stdout/stderr·실행 파일과 함께 보존되어 있다. 정확한 경로와 34개 source hash
집합의 연결은 `BUILD_CLOSEOUT.json`에 있다.

receipt와 현 source 34개 및 실행 파일을 읽기 전용으로 대조한
`validate_build_receipt`는 `PRELAUNCH_BUILD_PASS`를 반환했다.
build와 closeout 동안 solver interval과 production binary launch는 모두 0이다.
이 결과는 과거 P01 실행을 인증하거나 과학 admission을 바꾸지 않는다.

본 closeout의 metadata publication commit은 위 **built revision과 별개**다.
gate는 현재 consumed source set와 binary SHA를 receipt에 대조하며 current HEAD/tree
일치를 요구하지 않는다. 따라서 문서만 추가한 후속 tree를 clean-built tree로
표시해서는 안 된다. `CONTRACT.json`의 `NOT_RUN_UNTIL...`은 실행 전 frozen 계약이며,
실제 사후 상태는 `BUILD_CLOSEOUT.json`, `DAG_STATUS.json`, `VALIDATION.json`에 기록한다.

PR101의 CI runs `38037289658`, `38037285205`는 inherited
`flrw_three_probe.rs` 등의 `cargo fmt --check`에서 실패했고 후속 tests는 skipped다.
상태는 `BASELINE_FORMATTER_HOLD`이며 whole-CI PASS를 주장하지 않는다.

향후 새 build가 필요한 경우의 재현 명령은 다음과 같다:

```bash
python3 rust/rei_microphysics/python/conditional_build.py --output /tmp/rei-clean-build-UNIQUE
python3 rust/rei_microphysics/python/source_bound_interval.py --check-build-only \
  --binary /tmp/rei-clean-build-UNIQUE/target/release/axisym_conditional \
  --build-receipt /tmp/rei-clean-build-UNIQUE/BUILD_RECEIPT.json
```

실제 binary path는 receipt의 `binary.path`를 사용한다. Cargo target 설정이 있으면
경로가 위 예와 다를 수 있다. 같은 source의 기록 게시만을 이유로 재빌드하지 않는다.
다음 CR-first 실행은 CR injection/deposition source, secondary partition, cold IC,
저온 thermal closure와 물리 tolerance에 대한 owner 계약이 필요하다.
동일 입력 warm interval도 별도로 수용된 실행 계약에 따라 판단한다.
CR physics, cold IC, thermal closure, PhysicalHistory, global admission은 `HOLD`다.
