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
`git diff --check`도 exit 0이다. 독립 review는 구현자 밖에서 수행해야 한다.

현재 단위에는 commit 권한이 위임되지 않았으므로 production clean-build receipt
생성은 `NOT_RUN`이다. review 후 담당자가 task files를 commit하고 clean 상태에서:

```bash
python3 rust/rei_microphysics/python/conditional_build.py --output /tmp/rei-clean-build-UNIQUE
python3 rust/rei_microphysics/python/source_bound_interval.py --check-build-only \
  --binary /tmp/rei-clean-build-UNIQUE/target/release/axisym_conditional \
  --build-receipt /tmp/rei-clean-build-UNIQUE/BUILD_RECEIPT.json
```

실제 binary path는 receipt의 `binary.path`를 사용한다. Cargo target 설정이 있으면
경로가 위 예와 다를 수 있다. receipt 생성 후 과학 실행은 별도 계약에 따라 판단한다.
CR physics, cold IC, thermal closure, PhysicalHistory, global admission은 `HOLD`다.
