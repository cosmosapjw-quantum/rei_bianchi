# REI owner-current JVP — 실제 로컬 검증 반환

STATUS: **EXACT_REAL_RESOLVED_OWNER_REFERENCE_PASS_10_OF_10__PHYSICAL_TUBE_UNKNOWN**

PR #77의 새 결과가 없는 것을 해당 PR/branch에서 확인한 뒤, 후보를 격리
worktree에서 **1회 실행하여 O01–O10 전부 PASS**를 관측했다. 두 Python 파일은
수정하지 않았다. Python 3.12.3, process exit 0, timeout 없음, failure/error/skip 0.
이는 합성 Fraction reference 검증이며 production PASS나 Rust-first numerical
gate를 대체하지 않는다.

| 구분 | Exact identity |
|---|---|
| 부모 문맥 PR #76 | commit `9651959529b1048d9346f695e52ace2558d9bed6`, tree `1440a7610e01cd4ed8abadf80319f7dcad8f863e` |
| TESTED_SOURCE / 실제 실행 후보 | commit `12d64833419651a532451ad4c9a180aa65a0a70b`, tree `93f34e2c869e888a0f78bd67b53d905c74e83710` |
| owner_current_reference.py | blob `c684702d16d9c656555bf38a454207101fff1b1e` |
| test_owner_current_reference.py | blob `9b5348f799206ad210ac8e7bb85f0147584bb5b6` |
| PUBLISHED_HEAD / 증거 게시 | 이 HANDOFF와 local_evidence를 추가한 후속 commit. 고정 Git 파일 URL의 commit이 게시 SHA이며 위 실행 후보와 다르다. |
| PR / branch | [Draft PR #77](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/77), `research/rei-owner-current-jvp-20260907-r1` |

실행 명령:

```text
python3 -B research/rei_owner_current_jvp_20260907/test_owner_current_reference.py
```

[원본 stderr: 각 O01–O10 결과](local_evidence/O01-O10.stderr.log),
[원본 stdout: 빈 파일](local_evidence/O01-O10.stdout.log),
[실행 메타데이터](local_evidence/EXECUTION.json),
[machine-readable 반환](RETURN_STATUS.json),
[exact source/data commit·blob](local_evidence/SOURCE_BINDINGS.json).
실행 메타데이터의 시각은 완료 뒤 기록 시각이며 process 시작 시각으로 주장하지 않는다.

실제 source의 `NH0_CM3`, `YHE`, `MPC_CM`, sigma CSV와 owner support에서
`p_s(z)=q_s(1+z)^2`를 구성했다. HeII의 분모 **H**와 이미 weight를 포함한 N을
유지했다. 원래 두 normalization을 미분한 별도 Dual reference와 전역 δR을
포함한 reduced JVP가 일치했다. 고정 J/e/c/N에서만 κ가 직접 상쇄되며,
실제 forcing 및 totals의 종속성은 chain rule에 남는다.

**실제 물리적 uniform owner bound는 UNKNOWN이다.**
보존된 `VALIDATED_PUBLIC_BOXES.npz`의 primary lane은 실제 최종 endpoint
enclosure다. producer를 읽어 second-half 최종 상태임을 확인했으며, 이를
전체 source-input tube로 바꾸지 않았다. 완결된 N/time/site/forcing 방향의
공동 enclosure와 그 위의 kappa 양의 하한, R>=r>0를 이번 입력에서 확립하지
못했다. sigma/support와 nominal totals는 보존돼 있다. 누락 여부와 가용
정보를 파일·field별로 [TUBE_INPUT_STATUS.md](TUBE_INPUT_STATUS.md) 및
[INPUT_INSPECTION.json](local_evidence/INPUT_INSPECTION.json)에 기록했다.

[PHYS-MATH → PHYS-MATH-CODE 순차 검토](VALIDATION_MATRIX.md)는 같은 assistant의
검토다. 독립 reviewer 인증이나 전체 proof 완료 승인이 아니다. 원래
WORK_UNIT의 실행 0회 및 ClientError/MCP 404는 과거 기록으로 보존했다.
당시 실패는 process/kernel 전 실패이며 수학적 RED가 아니다.

NOT_VERIFIED: binary64 argmax residual correction/rounding parity, interval
enclosure arithmetic, unresolved subgrid NODE allocation, OTS/atomic rate
derivatives, 전체 flux bound, thermal coupled bound, exact-flow rho, production.
실수식의 항등식으로 이 항목들의 성공을 주장하지 않는다.

population RHS y0, predictor/gamma denominator y0, corrector denominator yp와
(F0+F1)/2, 네 독립 source site는 유지했다. #73–#76 suite, native/GCC/XZ,
production import/worker, canonical interval은 실행하지 않았다. one-shot budget,
production code/물리식/허용오차/lock 및 다른 repository는 변경하지 않았다.
게시 commit은 `[skip ci]`; 새 workflow/dispatch/re-run은 없고 CI skipped/pending을
PASS로 사용하지 않는다. non-force push, PR Draft 유지.

NEXT boundary: 기존 자료만으로 완결된 source-input tube를 연결할 수 있을 때
그 owner 항의 조건부 경계를 평가한다. 이 반환은 새 실행이나 입력 생성의
승인이 아니다.
