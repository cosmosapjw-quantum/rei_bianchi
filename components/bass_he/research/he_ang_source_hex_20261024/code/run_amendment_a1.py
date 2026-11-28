"""A1 one-shot append-accounted focused test, diagnosed retry, synthetic plot."""
import json
import os
from pathlib import Path
import sys
from run_bounded import atomic_json, catalogue_validation, file_identity, freeze, now, plot_validation, run_child

UNIT = Path(__file__).resolve().parents[1]
OUT = UNIT/'evidence'/'execution'
PATH = OUT/'A1_ledger.json'


def main():
    if '--a3' in sys.argv:
        return main_a3()
    if '--a2' in sys.argv:
        return main_a2()
    old_path, diag_path = OUT/'bounded_ledger.json', OUT/'03_diagnostic.receipt.json'
    old, diag = json.loads(old_path.read_text()), json.loads(diag_path.read_text())
    amendment = json.loads((UNIT/'POLICY_AMENDMENT_A1.json').read_text())
    if amendment['id'] != 'A1_NEWLINE_SQL_DIALECT_REPAIR' or diag['status'] != 'FINISH':
        raise SystemExit('REFUSED: A1 or linked diagnostic missing')
    if diag['legacy_ledger_identity'] != file_identity(old_path):
        raise SystemExit('REFUSED: legacy ledger changed')
    if len(old['attempts']) != 2 or old['attempts'][1]['status'] != 'FAIL':
        raise SystemExit('REFUSED: approved failure history mismatch')
    try:
        descriptor = os.open(PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise SystemExit('REFUSED: A1 already reserved/executed; no automatic retry')
    os.close(descriptor)
    # run_child's sum includes this measured accounting carrier. It is not a
    # scientific attempt and does not change the immutable old FAIL receipt.
    history = {'index': 0, 'kind': 'preserved_prior_accounting', 'status': 'FINISH',
               'cpu_s': diag['cumulative_cpu_s'], 'wall_s': diag['cumulative_wall_s'],
               'prior_counts': {'algebra': 1, 'catalogue': 1, 'diagnostic': 1, 'plot': 0},
               'note': 'Old catalogue failure preserved in linked ledger; measured totals are carried, not reset.'}
    ledger = {'unit_id': old['unit_id'], 'created_utc': now(), 'amendment_id': amendment['id'],
              'amendment_identity': file_identity(UNIT/'POLICY_AMENDMENT_A1.json'),
              'legacy_identity': file_identity(old_path), 'diagnostic_identity': file_identity(diag_path),
              'freeze': freeze(), 'attempts': [history],
              'cumulative_cpu_s': history['cpu_s'], 'cumulative_wall_s': history['wall_s'],
              'same_unit_caps': {'cpu_s': 20, 'wall_s': 60, 'algebra': 3, 'catalogue': 2, 'diagnostic': 1, 'plot': 2}}
    # Reuse the unchanged resource/accounting implementation with scoped output
    # names to avoid overwriting the original START/FINISH/FAIL evidence.
    import run_bounded as bounded
    bounded.LEDGER = PATH
    bounded.OUT = OUT/'A1'
    bounded.OUT.mkdir(exist_ok=True)
    atomic_json(PATH, ledger)
    atomic_json(bounded.OUT/'source_freeze.json', ledger['freeze'])
    if not run_child(ledger, 'algebra', ['python', '-B', 'tests/test_hex_lines_a1.py']):
        return 1
    if not run_child(ledger, 'catalogue', ['python', '-B', 'code/hex_intake.py', '--dialect', 'hex-lines', '/workspace/scratch/47d8070ffff8/source_intake/Hex-170210.sql.xz'], validation=catalogue_validation):
        return 1
    if not run_child(ledger, 'plot', ['python', '-B', 'code/plot_synthetic_tail.py', 'figures/synthetic_tail.png'],
                     {'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1', 'MPLCONFIGDIR': '/tmp/he_hex_mpl'}, plot_validation):
        return 1
    return 0


def main_a3():
    import run_bounded as bounded
    authority = OUT/'RESOURCE_LEDGER.json'
    ledger = json.loads(authority.read_text())
    if 'A3_guard_repair' in ledger or ledger['invocation_counts'] != {'algebra': 3, 'catalogue': 3, 'diagnostic': 2, 'plot': 1}:
        raise SystemExit('REFUSED: A3 already reserved or prior counts mismatch')
    before = file_identity(authority)
    ledger['A3_guard_repair'] = {'authority': 'Explicit root Astra A3 instruction: one-line INSERT whitespace/EOF guard, punctuation negatives, exactly one existing unittest method; no catalogue or plot replay.',
        'prior_authority_identity': before, 'status': 'START_AUTHORIZED', 'max_algebra_invocations': 4,
        'cpu_s': 1, 'wall_s': 20, 'address_space_MiB': 256, 'global_cpu_s': 20, 'global_wall_s': 60}
    ledger['same_unit_caps']['algebra'] = 4
    ledger['A2_execution_freeze'] = ledger['freeze']
    ledger['freeze'] = freeze()
    bounded.LEDGER, bounded.OUT = authority, OUT/'A3'
    bounded.LIMITS['kind_caps']['algebra'] = 4
    bounded.OUT.mkdir(exist_ok=True)
    atomic_json(authority, ledger)
    atomic_json(bounded.OUT/'source_freeze.json', ledger['freeze'])
    result = run_child(ledger, 'algebra', ['python', '-B', 'tests/test_literal_a2.py', 'A2LiteralTests.test_schema_integer_finite_and_word_boundary_gates'])
    item = ledger['attempts'][-1]
    ledger['all_actual_attempts'].append(item)
    ledger['invocation_counts']['algebra'] += 1
    ledger['A3_guard_repair']['status'] = item['status']
    ledger['A3_guard_repair']['actual_receipt'] = str((bounded.OUT/(f"{item['index']:02d}_algebra."+item['status']+'.json')).relative_to(UNIT))
    atomic_json(authority, ledger)
    return 0 if result else 1


def main_a2():
    import run_bounded as bounded
    authority = OUT/'RESOURCE_LEDGER.json'
    prior_paths = [OUT/'bounded_ledger.json', OUT/'03_diagnostic.receipt.json', OUT/'A1_ledger.json']
    original, diagnostic, a1 = [json.loads(path.read_text()) for path in prior_paths]
    amendment_path = UNIT/'POLICY_AMENDMENT_A2.json'
    amendment = json.loads(amendment_path.read_text())
    if amendment['id'] != 'A2_LITERAL_SCAN_COST_REPAIR' or a1['attempts'][-1]['status'] != 'FAIL':
        raise SystemExit('REFUSED: A2 history mismatch')
    try:
        descriptor = os.open(authority, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise SystemExit('REFUSED: A2 authority already exists; no automatic retry')
    os.close(descriptor)
    actual = original['attempts'] + [dict(diagnostic, kind='diagnostic')] + a1['attempts'][1:]
    before_cpu, before_wall = sum(x['cpu_s'] for x in actual), sum(x['wall_s'] for x in actual)
    if abs(before_cpu-a1['cumulative_cpu_s']) > 1e-12 or abs(before_wall-a1['cumulative_wall_s']) > 1e-12:
        raise SystemExit('REFUSED: prior cumulative accounting mismatch')
    carrier = {'kind': 'preserved_prior_accounting', 'status': 'FINISH', 'cpu_s': before_cpu, 'wall_s': before_wall,
               'note': 'Accounting carrier only; actual failed attempts are preserved in all_actual_attempts and linked immutable raw receipts.'}
    ledger = {'unit_id': original['unit_id'], 'created_utc': now(), 'amendment_id': amendment['id'],
              'amendment_identity': file_identity(amendment_path), 'freeze': freeze(),
              'prior_receipts': {str(p.relative_to(UNIT)): file_identity(p) for p in prior_paths},
              'all_actual_attempts': actual, 'attempts': [carrier],
              'cumulative_cpu_s': before_cpu, 'cumulative_wall_s': before_wall,
              'authority': 'Same-unit aggregate, no reset; all prior failures and measured overshoot retained.',
              'same_unit_caps': {'cpu_s': 20, 'wall_s': 60, 'algebra': 3, 'catalogue': 3, 'diagnostic': 2, 'plot': 2}}
    bounded.LEDGER, bounded.OUT = authority, OUT/'A2'
    bounded.LIMITS['kind_caps']['diagnostic'] = 2
    bounded.OUT.mkdir(exist_ok=True)

    def sync():
        ledger['all_actual_attempts'] = actual + ledger['attempts'][1:]
        ledger['invocation_counts'] = {kind: sum(x['kind'] == kind for x in ledger['all_actual_attempts']) for kind in ('algebra', 'catalogue', 'diagnostic', 'plot')}
        atomic_json(authority, ledger)

    def invoke(kind, command, env=None, validation=None):
        if ledger['invocation_counts'][kind] >= ledger['same_unit_caps'][kind]:
            raise RuntimeError('aggregate kind cap reached')
        result = run_child(ledger, kind, command, env, validation)
        sync()
        return result

    def profile_validation(stdout):
        result = json.loads(stdout.read_text())
        if not result['exact_outputs_equal'] or result['decoded_bytes_read'] > 262144 or result['full_source_availability_inferred']:
            raise ValueError('A2 prefix diagnostic validation failed')
        return {'exact_outputs_equal': True, 'rows_profiled': result['literal_rows_profiled']}

    def pinned_catalogue_validation(stdout):
        result = json.loads(stdout.read_text())
        # Exact published compressed identity is fixed by acquisition evidence.
        expected_sha = 'afa8d83ada688ecf91c40340da669e204885ec5c52d04fc55b48837b52135101'
        if result['compressed_bytes'] != 7880672 or result['compressed_sha256'] != expected_sha:
            raise ValueError('compressed source identity mismatch')
        if len(result['compressed_sha256']) != 64 or len(result['uncompressed_sha256']) != 64 or not 0 < result['uncompressed_bytes'] <= 128*1024**2:
            raise ValueError('incomplete input identity')
        return {**catalogue_validation(stdout), 'compressed_sha256': result['compressed_sha256'],
                'compressed_bytes': result['compressed_bytes'], 'uncompressed_sha256': result['uncompressed_sha256'],
                'uncompressed_bytes': result['uncompressed_bytes']}

    sync()
    atomic_json(bounded.OUT/'source_freeze.json', ledger['freeze'])
    if not invoke('diagnostic', ['python', '-B', 'code/profile_literal_a2.py'], validation=profile_validation): return 1
    if not invoke('algebra', ['python', '-B', 'tests/test_literal_a2.py']): return 1
    if not invoke('catalogue', ['python', '-B', 'code/hex_intake.py', '--dialect', 'hex-lines', '/workspace/scratch/47d8070ffff8/source_intake/Hex-170210.sql.xz'], validation=pinned_catalogue_validation): return 1
    if not invoke('plot', ['python', '-B', 'code/plot_synthetic_tail.py', 'figures/synthetic_tail.png'],
                  {'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1', 'MPLCONFIGDIR': '/tmp/he_hex_mpl'}, plot_validation): return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
