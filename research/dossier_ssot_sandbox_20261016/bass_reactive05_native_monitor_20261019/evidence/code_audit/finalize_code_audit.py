#!/usr/bin/env python3
"""Finalize the scoped C9 review from recorded, separately attributed evidence."""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone


ROOT = pathlib.Path('/workspace/scratch/996fc62899da')
UNIT = ROOT / 'repo/research/dossier_ssot_sandbox_20261016/bass_reactive05_native_monitor_20261019'
WORK = ROOT / 'br05_work'
OUT = WORK / 'code_audit'


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: pathlib.Path):
    return json.loads(path.read_text())


execution_path = OUT / 'execution_01/ADVERSARIAL_EXECUTION.json'
execution = read(execution_path)
source = read(WORK / 'implementation/SOURCE_IDENTITY_FINAL.json')
proof = read(WORK / 'implementation/MECHANICAL_HOOK_PROOF_FINAL.json')
theory = read(WORK / 'theory/PHYS_MATH_AUDIT.json')
runtime = read(UNIT / 'evidence/runtime/FULL_RUST_CLIPPY_VERIFICATION.json')
fresh = read(UNIT / 'evidence/fresh_restore/FRESH_RESTORE_VERIFICATION.json')
native = read(UNIT / 'evidence/independent/monitor/MONITOR_INDEPENDENT_VERIFICATION.json')
panel = read(WORK / 'theory/native_full/NATIVE_PANEL_VERIFICATION.json')
replay = read(WORK / 'theory/native_full/NATIVE_PANEL_REPLAY_VERIFICATION.json')

assert execution['status'] == 'PASS_SCOPED'
assert execution['baseline']['returncode'] == 0
assert len(execution['mutations']) == 3
assert all(x['caught'] and x['returncode'] == 1 and x['changed_cells'] == 1
           and not x['successful_verification_written'] for x in execution['mutations'])
assert execution['source_unchanged_after'] and execution['sample_unchanged_after']
assert execution['mechanical_proof_recovered']
assert all(x['byte_identical'] for x in execution['physical_bodies'].values())
for path, expected in execution['source_identity']['hashes'].items():
    assert sha(UNIT / path) == expected, path
for path, expected in execution['sample_input_identity'].items():
    assert sha(pathlib.Path(path)) == expected, path
assert len(execution['source_identity']['hashes']) == 133
assert runtime['status'] == 'PASS_SOURCE_FROZEN'
assert fresh['status'] == 'PASS_SCOPED_FRESH_RESTORE'
assert native['status'] == 'PASS_SCOPED' and native['birth_rows_all'] == 314624
assert panel['status'] == 'PASS' and replay['status'].startswith('PASS')

# This reads an existing independent runtime log; it executes no Rust tests.
runtime_test_log = UNIT / 'evidence/runtime/ALL_RUST_TESTS.log'
summaries = re.findall(r'test result: ok\. (\d+) passed; (\d+) failed;', runtime_test_log.read_text())
test_count = sum(int(passed) for passed, _ in summaries)
failed_count = sum(int(failed) for _, failed in summaries)
assert (test_count, failed_count, len(summaries)) == (233, 0, 60)

completed = datetime.now(timezone.utc).isoformat()
for predecessor in (runtime['completed_utc'], fresh['completed_utc'], panel['created_utc']):
    assert datetime.fromisoformat(completed) > datetime.fromisoformat(predecessor)

refs = {
    'adversarial_execution': execution_path,
    'adversarial_harness': OUT / 'run_adversarial_checks.py',
    'math_contract': WORK / 'theory/MONITOR_MATH_CONTRACT.md',
    'phys_math_audit': WORK / 'theory/PHYS_MATH_AUDIT.json',
    'theory_native_decimal90': WORK / 'theory/native_full/NATIVE_PANEL_VERIFICATION.json',
    'theory_native_panel_replay': WORK / 'theory/native_full/NATIVE_PANEL_REPLAY_VERIFICATION.json',
    'mechanical_hook_proof': WORK / 'implementation/MECHANICAL_HOOK_PROOF_FINAL.json',
    'mechanical_hook_generator': WORK / 'implementation/generate_monitored_midpoint.py',
    'parent_input_manifest': UNIT / 'contracts/PARENT_INPUT_SHA256.json',
    'source_identity_frozen': WORK / 'implementation/SOURCE_IDENTITY_FINAL.json',
    'implementation_test_log_prior': WORK / 'implementation/SCOPED_TESTS_FINAL.log',
    'runtime_full': UNIT / 'evidence/runtime/FULL_RUST_CLIPPY_VERIFICATION.json',
    'runtime_all_tests_log': runtime_test_log,
    'runtime_clippy_log': UNIT / 'evidence/runtime/STRICT_CLIPPY.log',
    'native_run': UNIT / 'evidence/native/ap_n16_r8.json',
    'root_native_independent': UNIT / 'evidence/independent/monitor/MONITOR_INDEPENDENT_VERIFICATION.json',
    'root_native_pair': UNIT / 'evidence/independent/pair/NATIVE_PAIR_VERIFICATION.json',
    'fresh_restore': UNIT / 'evidence/fresh_restore/FRESH_RESTORE_VERIFICATION.json',
}
evidence = {name: {'path': str(path), 'sha256': sha(path)} for name, path in refs.items()}

checks = [
    ('C9-01', 'Source ownership and additivity', 'PASS',
     '125 parent inputs and eight new code/build inputs hash-identical before, after the adversarial executions, and at finalization; physical owners, CX and four-corner sources unchanged.'),
    ('C9-02', 'Mechanical clone', 'PASS',
     'Ten reversible edits recover the parent AP source exactly. Deterministic scoped-format proof matches the final generated SHA. Independent byte extraction confirms identical emit_births and photo bodies.'),
    ('C9-03', 'Default and monitor OFF', 'PASS_SCOPED',
     'Ordinary advance and advance_with_diagnostics, and explicit MonitorMode::Off, delegate directly to the parent. Existing new tests cover fitted/legacy OFF and both BASS shear signs; no universal exhaustive-input parity claim.'),
    ('C9-04', 'Actual corrector selector and births', 'PASS',
     'The first hook receives actual rate_gas and the actual emit_births result. It does not replace them with endpoint gas or a standalone frozen source. Original physical operation order is retained.'),
    ('C9-05', 'Predictor exclusion', 'PASS',
     'The temporary predictor recursively invokes advance_core with capture None. Only the outer corrector supplies the monitor capture.'),
    ('C9-06', 'Acceptance scope', 'PASS_SCOPED',
     'The accepted hook follows final original physics and energy-ledger checks. Export acceptance means successful local fixed macrostep only; outer S10/four-corner acceptance is not instrumented.'),
    ('C9-07', 'Failure separation', 'PASS_SCOPED',
     'NetworkError remains the solver result. Capture failures remain an inner MonitorError without cancelling accepted physics. Existing tests cover record quota, invalid controls, unsupported legacy monitor, Cx(WorkLimit), and negative population.'),
    ('C9-08', 'Three measures and mass/shape separation', 'PASS_SCOPED',
     'Target-node frozen kernel, actual-source/clock under frozen propagation, and actual retained native measure have separate data. Only the first two have a stated frozen comparator; native widths are resolution statistics.'),
    ('C9-09', 'Panel reference and units', 'PASS_SCOPED',
     'Actual rule nodes and panel recurrence are reused with bit checks. tau is dimensionless, kappa is s^-1, counts are reference-comoving m^-3. W1 on normalized-age x is dimensionless; multiply by dt, or dt*d for local panels, to obtain seconds. Exact panel composition requires matched panel masses.'),
    ('C9-10', 'Clock and Killing provenance', 'PASS',
     'Target age and represented clocks are distinct; physical clock defect is evaluated directly. Raw birth directions are retained, while K uses the original CharacteristicRay normalization. No cohort coalescing is introduced.'),
    ('C9-11', 'Finite, zero and underflow states', 'PASS_SCOPED',
     'Diagnostic empty/zero/subnormal and invalid inputs are explicit. Absolute and selected normalized underflows are flagged. Source-normalization quotient underflow is an acknowledged uncovered extreme; no full native zero-source contract is introduced.'),
    ('C9-12', 'CSV joining and original schema', 'PASS_SCOPED',
     'Six final-schema monitor CSVs link persistent append indices and step/template/rule/node/panel IDs. Normal native stdout retains 54 columns. Final retained cohorts are streamed once; no O(N^2) retained-history snapshots are required.'),
    ('C9-13', 'Adversarial baseline', 'PASS',
     'This audit actually reran the root-authored Python auditor on the unchanged final small fixture: exit 0 and PASS_SCOPED.'),
    ('C9-14', 'Adversarial fault detection', 'PASS',
     'Three separate one-cell mutations were executed and rejected at cohort append join, Killing birth constant, and born source weight checks. No mutated case emitted a success receipt.'),
    ('C9-15', 'Independent runtime and fresh evidence attribution', 'PASS',
     'Read and hash-verified the independent 233-test/Clippy receipt and separate fresh 9-test/Clippy/small-fixture receipt. This C9 audit did not execute Rust tests or another native solve.'),
    ('C9-16', 'Scope of scientific conclusion', 'PASS_SCOPED',
     'The evidence supports read-only monitoring of the completed fixed-step native run and stated frozen references. It supplies neither nonlinear absolute error, full longspan convergence, spectral/angular convergence, universal second order, nor Einstein feedback.'),
]

limitations = [
    {
        'id': 'L1_SOURCE_QUOTIENT_UNDERFLOW', 'priority': 'P2', 'kind': 'DECLARED_SCOPE_LIMITATION',
        'status': 'OPEN_OUTSIDE_ADMITTED_DOMAIN',
        'description': 'actual_n / constant_born can underflow to zero for extreme positive ratios before the generic certificate sees the value. No separate predivision quotient-underflow flag exists. Ordinary reconstruction can also differ by a few ulps from direct count/attenuation sums.',
        'observed_native_impact': 'No such quotient loss was found in the actual fixtures or stated native audits; no universal all-source-ratio underflow-detection claim is admitted.',
        'action': 'Keep the limitation explicit. A future diagnostic extension can use log weights or a predivision loss flag; frozen Rust source is not changed in this review.',
    },
    {
        'id': 'L2_PERSONNEL_INDEPENDENCE', 'priority': 'P2', 'kind': 'REVIEW_PROVENANCE_LIMITATION',
        'status': 'DISCLOSED',
        'description': 'This reviewer authored the Rust monitor. The fault-injection executions use a separate root-authored Python route, but are not independent personnel review. Separate theory and runtime agents supply independently authored/executed evidence.',
    },
    {
        'id': 'L3_ACCEPTANCE_AND_ERROR_SCOPE', 'priority': 'P2', 'kind': 'INTENTIONAL_BOUNDARY',
        'status': 'DISCLOSED',
        'description': 'The local fixed-step successful transaction is monitored. A future adaptive caller must buffer observations until outer acceptance. Frozen-reference certificates and retained-weighted widths do not certify the unknown nonlinear native solution.',
    },
]

result = {
    'schema': 'rei.br05.C9_PHYS_MATH_CODE_AUDIT.v1',
    'status': 'PASS_SCOPED',
    'completed_utc': completed,
    'reviewer': '/root/birth_implementation',
    'reviewer_authored_rust_code': True,
    'independence': {
        'personnel_independent_from_rust_author': False,
        'new_method': 'Byte proofs plus actual CSV fault injection against byte-identical snapshots of root-authored independent Python/Decimal owner checks.',
        'separate_personnel_evidence': ['/root/birth_theory', '/root/rust_runtime', '/root'],
    },
    'review_scope': 'Read-only code/math mapping and adversarial data audit of the additive BR05 fixed-step native birth monitor.',
    'rust_source_modified_in_this_audit': False,
    'rust_tests_executed_in_this_audit': 0,
    'native_solver_runs_executed_in_this_audit': 0,
    'executions_new_in_this_audit': {'python_baseline': 1, 'single_cell_mutations': 3, 'source_hashes_checked': 133},
    'predecessors': {
        'phys_math_recorded_utc': theory['recorded_utc'],
        'phys_math_native_numerical_completed_utc': panel['created_utc'],
        'runtime_completed_utc': runtime['completed_utc'],
        'fresh_restore_completed_utc': fresh['completed_utc'],
        'note': 'The mathematical audit JSON includes later native evidence; its exact bytes are pinned by the evidence SHA, separately from its original recorded_utc.',
    },
    'counts': {'P0': 0, 'P1': 0, 'declared_P2_scope_limits': len(limitations), 'review_checks': len(checks), 'mutations_caught': 3},
    'source_identity': {
        'parent_inputs': 125, 'new_inputs': 8, 'all_133_rechecked_at_finalization': True,
        'new_sha256': source['new_files'],
        'unchanged_physics_function_bodies': execution['physical_bodies'],
        'mechanical_recovered_sha256': proof['recovered_sha256'],
        'generated_module_sha256': proof['generated_file_sha256'],
    },
    'checks': [{'id': a, 'topic': b, 'status': c, 'finding': d} for a, b, c, d in checks],
    'limitations': limitations,
    'actual_mutations': execution['mutations'],
    'sample_scope': {'macrosteps': 1, 'duration_s': 1e9, 'refinement': 1, 'shear_case': 'SIGNED_MINUS',
                     'births': 768, 'rules': 48, 'panels': 48, 'templates': 384,
                     'role': 'Export/checker fault-detection fixture; not another longspan accuracy result.'},
    'referenced_runtime_scope': {'tests_passed': test_count, 'failed': failed_count, 'harnesses': len(summaries),
                                  'new_execution_by_this_reviewer': False,
                                  'strict_clippy_all_targets': 'PASS'},
    'referenced_fresh_scope': {'new_tests_passed': 9, 'all_target_clippy': 'PASS', 'fresh_source_inputs': 133,
                             'small_native_fixture_only': True, 'six_monitor_csvs_byte_identical': True,
                             'normal_native_non_wall_columns_identical': 53,
                             'raw_archive_or_provider_restore': False},
    'referenced_full_native_scope': {
        'steps': native['steps'], 'rules': native['rules_all'], 'panels': native['panels_all'],
        'templates': native['templates_all'], 'births': native['birth_rows_all'], 'final_cohorts': native['final_rows_all'],
        'root_checked_all_cohort_K_source_and_join_fields': True,
        'root_actual_source_shapes_sampled': native['actual_source_shape_templates_sampled'],
        'root_source_shape_sampling': native['sampling'],
        'theory_panel_certificate_field_comparisons': panel['certificate_field_comparisons'],
        'new_execution_by_this_reviewer': False,
    },
    'admissible_claim': 'The additive monitor preserves the stated parent physics path and records actual corrector births and retained cohorts with independently checked provenance and stated frozen-reference diagnostics, within the successful local fixed-step scope.',
    'not_admitted': ['Universal bit parity over all possible source implementations', 'Outer adaptive-trial acceptance monitoring',
                     'Native zero-source pipeline beyond the original positive source contract',
                     'Directed-rounding error enclosure', 'Absolute nonlinear H/He/D error', 'Full longspan convergence',
                     'Universal second order', 'Full spectral/angular convergence', 'Two-way Einstein feedback'],
    'evidence': evidence,
}

rows = '\n'.join(f'| {a} | {b} | {c} | {d} |' for a, b, c, d in checks)
mut_rows = '\n'.join(
    f"| {m['id']} | `{m['column']}` | `{m['old_value']}` → `{m['new_value']}` | {m['returncode']} | `{m['expected_failure_message']}` |"
    for m in execution['mutations'])
source_rows = '\n'.join(f'| `{p}` | `{h}` |' for p, h in source['new_files'].items())
evidence_rows = '\n'.join(f"| {key} | `{str(path.relative_to(ROOT))}` | `{evidence[key]['sha256']}` |" for key, path in refs.items())

md = f'''# BR05 C9 PHYS–MATH–CODE 적대적 감사

**판정: `PASS_SCOPED`**  
**확정 UTC: {completed}**  
**P0/P1 발견: 0/0. Rust 소스 변경: 0. 이번 감사의 Rust 시험/새 native solve 실행: 0/0.**

이 판정은 BR05의 성공한 **고정 macrostep 로컬 계산**에 연결된 읽기 전용 출생·cohort 모니터에 적용한다. 실제 corrector의 opacity 선택 기체와 출생 cohort를 읽는 경로, 원 물리 연산 보존, 출생과 최종 생존 cohort의 연결, 세 측도의 구분을 검토했다. 원 샘플을 Python으로 다시 검산한 뒤 사본에 각각 하나의 잘못된 값을 넣어 검사기의 실패를 확인했다. 전체 해의 수렴이나 모니터 폭으로부터 비선형 H/He/D 절대오차를 인정하는 판정은 아니다.

## 1. 감사 주체와 증거의 독립성

검토자 `/root/birth_implementation`은 이 Rust 모니터를 작성한 주체이기도 하다. 따라서 이 문서를 작성자와 인적으로 독립된 코드 리뷰라고 부르지 않는다. 이번 새 실행은 **root가 별도로 작성한 Python 검사기의 정확한 사본**을 사용했고, 해당 검사기는 Rust의 내부 출력만 상호 비교하는 대신 별도 Verner/MD14/Killing/Decimal 계산과 결합한다. 사본의 SHA와 명령, 표준 오류, 변조 입력을 모두 보존했다. 인적으로 별도인 증거는 `/root/birth_theory`의 유도·CAS·Decimal 검산, `/root/rust_runtime`의 Rust/복원 실행, `/root`의 전체 native 수치 감사로 구분해 참조한다.

PHYS–MATH 계약을 먼저 읽었고, 그 계약의 3측도·패널 질량·시계 반올림·조건부 경계에 맞춰 equation-to-code 대응을 검토했다. 이 C9 확정 시각은 독립 전체 Rust 실행, native 패널 검산, 작은 fixture의 fresh source restore 완료 시각보다 뒤다. 수학 감사 JSON의 `recorded_utc`는 최초 기록 시각이며 이후 추가된 native 근거는 별도 실행 시각과 현재 파일 SHA로 식별했다.

## 2. 원 소유권과 실제 실행 경로

부모의 **125개 입력 파일**과 BR05의 **새 8개 입력 파일**을 실행 전후 및 최종 확정 시점에 재해시했다. 133개 모두 일치한다. 원 physical owners, source, CX half-flow, four-corner 제어기, 이전 AP/BR04 코드에 수정이 없다.

`monitored_midpoint.rs`는 부모 `ap_midpoint.rs`에 10개의 명시적·가역적인 편집을 적용한 새 파일이다. 편집을 역으로 적용하면 부모 SHA를 정확히 복구한다. 저장된 scoped rustfmt 재현 증명도 최종 생성 파일 SHA와 일치한다. 이번 감사는 추가로 두 파일에서 `emit_births`와 `photo` 함수 본문을 분리해 직접 바이트 비교했고 두 본문이 동일함을 확인했다. 관측 hook 외의 원 물리 연산을 재작성하지 않았다는 증거이며, 이를 모든 가능한 외부 source 구현에 대한 무조건적 동작 동치 증명으로 확대하지 않는다.

관측 순서는 다음과 같다.

1. 원 `emit_births(..., &rate_gas)`가 반환한 **실제 birth 배열**과 **실제 corrector의 rate_gas**를 읽는다.
2. 원 photo 계산이 반환한 후 cohort의 실제 광자 수를 읽는다.
3. 원 full chemistry, CX, drift와 최종 energy ledger 검사까지 성공한 뒤 accepted state를 읽는다.

예측기는 `capture=None`으로 호출되어 임시 predictor birth를 export하지 않는다. 원 solver의 `NetworkError`가 발생하면 로컬 accepted 모니터 결과를 반환하지 않는다. 여기서 accepted는 한 `advance_core` 호출의 성공이다. 현재 driver는 고정 macrostep이며, 외부 적응 controller의 rejected trial을 걸러주는 계층까지 구현했다고 주장하지 않는다. 향후 적응 호출자는 outer acceptance까지 관측을 보류해야 한다.

일반 `advance`/`advance_with_diagnostics`와 `MonitorMode::Off`는 부모 경로에 직접 위임한다. Fitted mode를 감시할 때만 새 hook 경로를 쓴다. legacy `BirthMode::Off`에서 감시 On을 요청하면 부모 물리를 그대로 실행한 뒤 `UnsupportedBirthMode`를 별도 진단 오류로 돌려준다. 임의의 legacy selector 기체를 만들어 참조 해석에 쓰지 않는다.

## 3. 수식–코드–관측량 대응

기호는 accepted batch의 끝을 t1, 길이를 dt, 정규화 target age를 x, 실제 표현된 나이를 A=t1−tb라 둔다. κ는 실제 corrector selector 기체와 birth energy에서 얻은 4종 흡수율의 합이며 τ=κdt다. B는 source label별 중간 시점 상수방출 기준의 총 출생 수다.

| 수학적 대상 | 코드/데이터 위치 | 의미와 제한 |
|---|---|---|
| `B exp(−τx) dx` 대 `B Σw exp(−τx) δx` | `build_birth_capture`, `MONITOR_RULES.csv`, `MONITOR_PANELS.csv` | 원 rule의 actual target nodes/weights를 사용한 상수 source·상수 opacity 참조. rule에는 단위 B certificate, template에는 실제 B를 따로 둔다. |
| `Σ n_born exp(−κA) δA` | `MONITOR_BIRTHS.csv`, `MONITOR_TEMPLATES.csv` | 실제 source amplitude와 실제 clock을 사용하되 opacity를 고정한 반사실적 비교. 순수 quadrature 오차와 동일시하지 않는다. |
| `Σ n_accepted δA`, 최종 retained measure | birth의 after-photo/accepted 필드, `MONITOR_FINAL_COHORTS.csv` | 실제 solver가 남긴 광자 수와 나이. 원 연산의 기록이며 알려지지 않은 비선형 연속 해의 certificate가 아니다. |
| 패널 질량 `B exp(−τl) d Φ(τd)` | `rule_panels`, `local_reference` | actual rule recurrence와 half-weights를 대조한다. 동일 패널 질량에서만 local W1의 질량가중 합 관계를 그대로 쓸 수 있다. |
| target/clock 이동 | birth의 `clock_age_defect_x`, `clock_age_defect_s` | 각각 `(t1−tb)/dt−x`, `(t1−tb)−dt*x`를 직접 기록한다. 두 번째를 첫 번째에 dt를 곱한 값으로 대체하지 않는다. |
| `K_i=a_i(tb) E_b n_unit,i` | birth K 및 geometry, template raw direction, final E/direction | `CharacteristicRay::new`의 원 정규화를 적용한다. raw birth direction도 별도로 보존한다. |

κ의 단위는 s⁻¹, τ와 x는 무차원, 광자 수는 reference-comoving m⁻³다. `w1_normalized`가 x 또는 패널 내부의 정규화 좌표에 대해 출력되면 무차원이다. 전체 batch는 dt, 내부 패널은 dt·d를 곱해야 초 단위 Wasserstein 거리가 된다. 이것에 광자 질량을 곱한 비용은 m⁻³ s다. CDFsup는 무차원이며 질량 결함과는 다른 양이다.

불일치하는 native/source 패널 질량에 matched-mass 합 공식을 물려주지 않는다. 동일 질량에 대한 구성적 비교나 추가 TV 항이 있어야 한다. 실제 retained-weighted 패널 폭은 해상도 통계로 해석한다. 작은 clock 이동의 같은 가중치 결합은 W1을 제어할 수 있지만 원자 측도의 CDF jump 높이에 같은 결론을 자동 적용할 수 없다.

## 4. 실패·0·underflow·회귀 범위

solver와 monitor 결과는 중첩된 별도 `Result`다. quota, 잘못된 monitor controls, legacy 감시 미지원 등의 진단 실패가 이미 승인된 물리 상태를 거부하지 않는다. driver의 solver 실패는 exit 2, 완료된 물리와 별도 monitor 실패는 exit 3, 파일 입출력 실패는 exit 4로 구분한다. 빌드·binary 실패와 panic은 이 과학적 상태를 상속하지 않는다. `Cx(WorkLimit)`는 그대로 작업 예산 종료이며 수렴 실패나 해 부재로 바꾸지 않는다.

기존 신규 9개 Rust 시험은 fitted/legacy OFF와 양쪽 shear, 두 단계의 monitor ON 물리 비트 일치, 잘못된 controls/quota, work limit/음수 population, transparent/thick 패널, 시계 반올림, 잘못된 weights와 불완전 cover, empty/zero/subnormal diagnostic measure, CSV 쓰기·overwrite 거부를 포함한다. 이 감사에서는 해당 시험을 다시 실행하지 않고 소스와 실제 완료 로그를 읽었다. 독립 runtime이 같은 frozen source로 전체 233개 시험과 strict Clippy를 실제 실행했다.

원 MD14 source의 양수 입력 계약은 유지된다. diagnostic helper의 zero/empty 처리가 원 native source-off pipeline을 새로 검증한 것은 아니다. κ=0인 frozen selector도 미래 geometry blueshift로 문턱을 넘을 수 있는 실제 광선 전체의 투명성을 증명하지 않는다.

**명시적 P2 제한:** template certificate의 `actual_n / constant_born`은 극단적인 양의 비에서 0으로 underflow할 수 있으며, 나누기 이전의 별도 quotient-loss flag는 없다. 일반적인 경우에도 이 재정규화 후의 합은 direct native count·attenuation 합과 몇 ulp 다를 수 있다. 실제 fixture와 명시된 native 검사에서 이 극단적인 quotient 손실은 발견되지 않았다. 모든 양의 source 비율에 대한 underflow 감지 완전성을 주장하지 않는다. 기존 born-count, 직접 frozen attenuation, reference mass, normalized shifted tail, moment 항의 해당 underflow 진단과 이 제한을 구분한다. 이 C9의 제한된 판정에 Rust 변경을 요구하는 P0/P1은 아니다.

## 5. 이번 감사에서 새로 실행한 적대적 검사

`run_adversarial_checks.py`는 원 `sample_final`을 읽고 root의 Python 검사기 두 파일을 바이트 그대로 별도 디렉터리에 복사한다. 원 샘플은 Nt=1, T=10⁹ s, r=1, `SIGNED_MINUS`, 원 spectrum grid 121의 작은 계약 검증 fixture다. birth/final 768개, rules 48개, panels 48개, templates 384개다. 이 fixture를 긴 구간의 정확도 증거로 재분류하지 않는다.

원 샘플 검사 **exit 0 / PASS_SCOPED**를 먼저 확인했다. 이후 세 개의 별도 사본에서 첫 birth row의 한 셀만 변경했다. 성공 receipt의 부재, exit 1, 의도한 오류 문자열까지 모두 검사했다.

| 변조 | 필드 | 실제 값 변경 | 종료 코드 | 실제 실패 위치 |
|---|---|---|---:|---|
{mut_rows}

이 세 실패는 의도적으로 만든 adversarial fixture의 성공적인 탐지다. solver나 원 연구 데이터의 실패 사례가 아니다. 원 7개 sample CSV와 133개 source 파일이 실행 전후 변하지 않았음을 SHA로 확인했다. 실행 시각은 {execution['started_utc']}부터 {execution['completed_utc']}까지이며, 원본/변조 로그와 exact command는 `execution_01/ADVERSARIAL_EXECUTION.json`에 있다.

재현 명령은 다음과 같다. output에는 아직 존재하지 않는 별도 경로를 사용한다.

```bash
python3 br05_work/code_audit/run_adversarial_checks.py \\
  --unit repo/research/dossier_ssot_sandbox_20261016/bass_reactive05_native_monitor_20261019 \\
  --work br05_work \\
  --output br05_work/code_audit/execution_replay
```

## 6. 별도로 완료된 실행에서 참조한 근거

| 실행 주체와 근거 | 실제 완료 범위 | C9에서 한 일 |
|---|---|---|
| `/root/rust_runtime`, FULL_RUST_CLIPPY_VERIFICATION | 233 passed, 0 failed, 60 harness; all-target strict Clippy; frozen 133 source | receipt/hash와 원 로그를 읽고 test 요약 233/0/60을 재집계했다. 새 Rust 실행은 없다. |
| `/root/rust_runtime`, FRESH_RESTORE_VERIFICATION | 별도 source 133개·새 target, 신규 9 tests, all-target strict Clippy, 작은 10⁹ s fixture | JSON/hash를 읽었다. 6 monitor CSV byte parity와 정상 53 non-wall 열 parity가 기록돼 있다. 8×10¹² s 재실행 또는 cloud ZIP raw restore는 아니다. |
| `/root`, MONITOR_INDEPENDENT_VERIFICATION | 16 steps, 768 rules, 19,664 panels, 6,144 templates, 314,624 births/final; 모든 source/K/join/raw moment 검산 | 결과 JSON을 읽어 참조했다. source shape는 rule당 첫 template 총 768개 표본이며 모든 template 질량·raw moment 검사는 별도다. |
| `/root/birth_theory`, NATIVE_PANEL_VERIFICATION 및 replay | 19,664 패널에서 235,968 certificate 필드의 Decimal90 비교, 58,992 경계 필드의 exact replay | 결과와 입력 hash를 읽었다. 수학 비교를 C9에서 다시 계산했다고 주장하지 않는다. |

최종 실제 native cohort의 positive/zero 개수도 증거가 구분한다. f64 0이라는 값 하나만으로 물리적 완전흡수와 표현 underflow를 보편적으로 분류할 수는 없다. 보존 ledger, 검증된 owner 재구성, frozen 참조 오차, 유한 격자 차분, 해 수렴은 서로 다른 검증 항목으로 유지한다.

## 7. 체크리스트와 판정

| ID | 대상 | 판정 | 근거·범위 |
|---|---|---|---|
{rows}

P0/P1 수정 요구는 없다. P2 범위 항목은 source quotient underflow의 완전 감지 부재, 작성자와 감사자의 인적 중복, 로컬 accepted·frozen 참조의 의도된 범위다. 세 항목 모두 위에서 공개했다. 새로운 출생 노드나 source weight를 바꾸지 않았고 원 branch/physics owner를 수정하지 않았다.

현재 허용되는 결론은 실제 corrector와 실제 retained cohort에 연결된 additive monitor가 명시된 provenance·참조 진단을 출력한다는 것이다. `LONGSPAN_SOLUTION`, 보편적 2차 정확도, 전체 age/spectral/angular 수렴, 양방향 Einstein feedback의 상태는 이 감사로 승격되지 않는다. 그림의 축·정규화·crop·범위 표현은 후속 별도 plot adversarial audit의 대상이다.

## 8. 소스와 증거 identity

기준 디렉터리는 `/workspace/scratch/996fc62899da`이다. 아래 경로는 그 기준의 상대 경로이며 JSON에는 절대 경로와 해시가 함께 있다.

### 새 frozen code/build 입력 8개

| 파일 | SHA-256 |
|---|---|
{source_rows}

### 감사가 읽은 증거

| 키 | 경로 | SHA-256 |
|---|---|---|
{evidence_rows}
'''

md_path = OUT / 'C9_PHYS_MATH_CODE_AUDIT.md'
md_path.write_text(md)
result['markdown_sha256'] = sha(md_path)
json_path = OUT / 'C9_PHYS_MATH_CODE_AUDIT.json'
json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
assert read(json_path)['markdown_sha256'] == sha(md_path)
print(json.dumps({'status': result['status'], 'completed_utc': completed,
                  'json': str(json_path), 'json_sha256': sha(json_path),
                  'markdown': str(md_path), 'markdown_sha256': sha(md_path),
                  'P0': 0, 'P1': 0, 'new_mutations_caught': 3,
                  'source_133_unchanged': True}, ensure_ascii=False, indent=2))
