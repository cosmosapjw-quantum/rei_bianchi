# FT03 실제 온도 의존 successor — F04 부분 반환

원 FT03 ZIP SHA256 `0d8d28b5e4d63a9013b5c57f785680d2f3344b94127f2510b4037417356f5480`의 controlled Case-A 모형을 별도 Rust 모듈로 연결했다. 원 F00 synthetic fixture와 과거 source/검사는 그대로다. 실제 EOS 온도에서 HG RR·CI와 두 DR 항을 재계산하고, 각 BE 종말점의 사건을 종·광자·열·escape 수지에 함께 쓴다. RR kinetic moment는 원 연구에서 정의한 파생 모형이며 raw Grackle cooling parity가 아니다. 누락 채널은 controlled 정의에 따라 정확히0으로 두며 물리적으로 무시 가능하다는 뜻이 아니다.

외부 기준은 원 ZIP의 DOP853/Radau 및50자리 RK4 결과를 재사용했다. 완료된 reference campaign은 재실행하지 않았다. 새152개 rate/slope/moment 점과9개 Verner 값은 원 alpha 식의 독립 mpmath 미분으로 계산했다. working precision은80이지만 import 시50자리로 읽은 일부 상수와 numerical differentiation을 포함하므로80자리의 rigorous accuracy를 주장하지 않는다. HeII alpha가 순수 T^-0.654이므로 slope derivative는 분석적으로 정확한0이며 수치 미분의 약1e-86 잔여값은 제거했다. 3e-12 상대 허용오차는 그대로다.

Host가 처음 만든 테스트에는 f64 인수에 정수0을 쓰는3개 컴파일 오류가 있었다. original-invalid-test.rs, original-oracle.json, author-validator-red.log, test-reference-repair.json으로 실패와 수정 전후를 보존했다. native author의 실제 VALIDATOR_FAILED를 성공으로 고치지 않았다. prepared.json의 editable lib.rs/frozen validator dependency 충돌도 그대로 보존하고, prepared-continuation.json에서 현재 source를 edit input으로 묶었다. 이는 실행 후 continuation binding 수리이며 과거 준비 PASS나 새 execution을 뜻하지 않는다. Python bytecode는 archive source가 아닌 packaging metadata로 제외했다.

독립 reviewer는 한 P2를 재현했다: 극소 양의 밀도에서 volumetric event underflow가 representable 분율 도함수를 거짓0으로 반환했다. Host의 한 번 수정은 nonzero factor들의 곱이0이면 FT03_PRODUCT_UNDERFLOW로 거절한다. 진짜 zero channel은 허용하며 density floor·clipping·tolerance 변경은 없다. 4개 직접 경계 입력, transactional state 보존 및 zero-channel 경계를 검증했다. 최종 수정 bytes에 대한 두 번째 독립 리뷰는 하지 않았다.

최종71개 crate tests(신규8), 별도14개 경계 assertions, format, strict library Clippy 및 all-target Clippy PASS. All-target Clippy는 기존/고정 reference decimal의 excessive_precision만 허용한다. dt1e11/5e10/2.5e10에서 관측량 오차는2.3040561396237003e-5,1.1533612905123558e-5,5.770087748546704e-6이다. 큰1e14 trial은10번 거절 뒤1024step으로 완료했고 rejected writes0이다. final-checks.json의 실제 argv/exit와 각 log, fixture-results.json을 참조한다.

F04 logical state는 partial이다. actual parameter/source parent box, Krawczyk inclusion/q<1, implicit J/H, observable Taylor remainder, 같은 original parent의 half composition, 독립 checker와 public width 판정은 아직 수행하지 않았다. Point discrepancy와 잔차는 uniform proof가 아니다. 원 PREWORK§6.1 recipe, strict local<2e-4/public width<2e-3, [160,161] FAIL와 tick160을 보존하며 scientific/physical admission은 HOLD다.

새 checkout에서 아래 검증에 필요한4개 파일만 private path에 복원한다. 기존 다른 bytes가 있으면 덮어쓰지 않는다.

```bash
python3 - <<'PY_REPRO'
from pathlib import Path
src=Path('docs/atomic_reionization_handoff_20261004_v1/runtime_returns/evidence/F04_successor')
dst=Path('.cuh/fastest-track/REI-F04');dst.mkdir(parents=True,exist_ok=True)
for name in ['oracle.json','verify_candidate.py','verify_boundaries.py','review-probe.rs']:
    a=src/name;b=dst/name
    if b.exists() and b.read_bytes()!=a.read_bytes():raise RuntimeError('Existing different input: '+str(b))
    if not b.exists():b.write_bytes(a.read_bytes())
PY_REPRO
CUHG_EXECUTION_MODE=CODEX_ONLY cuhg-telemetry run --project "$PWD" --task REI-F04 -- /usr/bin/python3 .cuh/fastest-track/REI-F04/verify_candidate.py
CUHG_EXECUTION_MODE=CODEX_ONLY cuhg-telemetry run --project "$PWD" --task REI-F04 -- /usr/bin/python3 .cuh/fastest-track/REI-F04/verify_boundaries.py
```

CODEX_ONLY 유지, 새 local payload inference0. 실제 native author/reviewer2dispatch, 모델·effort MATCH, known total3438033tokens는 cached input을 중복 합산하지 않았다. 비용 NOT_MEASURED. soft target 초과 후 같은 task identity/usage를 유지하고 Host의 좁은 repair/validation/publication으로 재계획했다. 이전 F00/F02/F01/F03의 닫힌 accounting과 실패 영수증은 변경하지 않았다.

게시 전 concurrent FLRW payload c0b630d9와 문서 ccbc1501을 수신했다. lib.rs의 FT03/FLRW additive exports를 모두 보존하고 최종 merged crate92 tests(기존63+FT03 8+수신FLRW21)를 실제 실행해 통과했다. owned5개 파일 format도 통과했다. 앞선71-test와 Clippy 증거는 새 외부 FLRW 모듈 수신 전 scope이며, 외부 FLRW2352개 독립 대조 및 photon history는 재실행하지 않았다. post-integration.json이 현재 source/통합 검증 binding이다.
