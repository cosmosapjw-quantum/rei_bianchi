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


if __name__ == '__main__':
    sys.exit(main())
