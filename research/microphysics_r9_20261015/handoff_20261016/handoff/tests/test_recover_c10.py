"""Synthetic n=64 archive fixtures; no PySCF or physics run is used."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

SCRIPT = Path(__file__).resolve().parents[1] / 'recover_c10.py'
spec = importlib.util.spec_from_file_location('recover_c10', SCRIPT)
c10 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c10)
PAYLOAD = Path(os.environ.get('C10_PAYLOAD', str(SCRIPT.parent.parent / 'unit2' / 'ncp_results')))


class RecoveryFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'root'
        (self.root / 'code').mkdir(parents=True)
        (self.root / 'runs').mkdir()
        shutil.copyfile(PAYLOAD / c10.SOURCE, self.root / c10.SOURCE)
        shutil.copyfile(PAYLOAD / c10.CONTRACT, self.root / c10.CONTRACT)
        self.attempt = self.root / c10.RUN

    def attempted(self):
        self.attempt.mkdir(parents=True)
        shutil.copyfile(PAYLOAD / c10.RUN / 'input.json', self.attempt / 'input.json')
        (self.attempt / 'stdout.log').write_text('historical fixture log\n')
        return self.attempt

    def terminal(self):
        p = self.attempted()
        n, ao = 64, 66
        ci = np.zeros((n * (n - 1) // 2, n))
        cf = ci.copy()
        ci[0, 0] = 1.0
        cf[0, 0], cf[0, 1] = .8, .6
        A = np.vdot(cf, ci)
        q = ci - A * cf
        rdm = np.zeros((n, n))
        rdm[0, 0], rdm[1, 1], rdm[2, 2] = 1, 1, 1
        np.savez_compressed(p / 'data.npz', CI_parent=ci, CI_daughter_ground=cf,
                            CI_complement=q, common_orbital_matrix=np.eye(ao, n),
                            AO_overlap_eigenvalues=np.ones(ao), rdm1_parent=rdm,
                            rdm1_daughter=rdm)
        state = {'E_BO_Eh': -7.0, 'E_electronic_Eh': -7.0, 'spin_squared': .75,
                 'nelec': [2, 1], 'norb': n, 'solver_backend': c10.BACKEND,
                 'finite_model_numerics_passed': True,
                 'checks': {**{k: 0.0 for k in c10.LIMITS}, 'fci_converged': True}}
        r = {'case': copy.deepcopy(c10.CASE),
             'case_sha256': c10.hashlib.sha256(json.dumps(c10.CASE, sort_keys=True).encode()).hexdigest(),
             'input_sha256': c10.FROZEN['input'], 'runtime': {'source_sha256': c10.FROZEN['source']},
             'status': 'finite_model_computed', 'exit_code': 0, 'finite_model_numerics_passed': True,
             'retained_ao_rank': n, 'ao_rank': ao, 'parent': copy.deepcopy(state),
             'daughter': copy.deepcopy(state), 'data_sha256': c10.sha(p / 'data.npz'),
             'P_ground': float(A * A), 'A_ground_real': float(A),
             'unresolved_excitation_including_bound_probability': float(np.vdot(q, q)),
             'daughter_energy_mean_Eh': -10.0, 'daughter_energy_second_moment_Eh2': 101.0,
             'daughter_energy_variance_Eh2': 1.0,
             'checks': {'closure_error': 0.0, 'ground_complement_overlap': 0.0}}
        c10.dump(p / 'receipt.json', r)
        return r

    def observed(self):
        with patch.object(c10, 'process_snapshot', return_value=([], [])):
            return c10.inspect(self.root)

    def gate(self, result, name):
        return next(g for g in result['gates'] if g['name'] == name)

    def validation(self):
        return c10.validate(self.attempt / 'receipt.json', self.attempt / 'input.json',
                            self.root / c10.SOURCE, self.root / c10.CONTRACT)

    def test_terminal_valid_real_npz(self):
        self.terminal()
        result = self.observed()
        self.assertEqual(result['runtime_class'], 'complete-success', result)
        self.assertTrue(result['validation']['passed'])
        self.assertTrue(self.gate(result['attempts'][0]['validation'], 'recomputed.q_identity_error')['pass'])

    def test_incomplete_partial_is_stale_and_preserved(self):
        self.attempted()
        (self.attempt / 'data.tmp.npz').write_bytes(b'partial archive')
        result = self.observed()
        self.assertEqual(result['runtime_class'], 'stale')
        out = self.base / 'evidence'
        stdout, rc = c10.write_evidence(result, out, collect=True)
        self.assertEqual(rc, 0)
        self.assertEqual((out / 'attempts/000/data.tmp.npz').read_bytes(), b'partial archive')
        self.assertTrue((out.parent / 'evidence.tar.gz').exists())
        self.assertTrue(json.loads(stdout)['runtime_class'] == 'stale')

    def test_failed_terminal_never_accepted_from_exit_zero(self):
        self.attempted()
        c10.dump(self.attempt / 'receipt.json', {'case': c10.CASE, 'status': 'worker_failed', 'exit_code': 0})
        self.assertEqual(self.observed()['runtime_class'], 'complete-fail')

    def test_missing_accessible_root(self):
        result = self.observed()
        self.assertEqual(result['runtime_class'], 'missing')
        self.assertFalse(result['validation']['passed'])

    def test_live_terminal_is_in_progress_and_npz_not_copied(self):
        self.terminal()
        live = {'active': True, 'output': str(self.attempt), 'pid': 1001}
        with patch.object(c10, 'process_snapshot', return_value=([live], [])):
            result = c10.inspect(self.root)
            self.assertEqual(result['runtime_class'], 'in-progress')
            c10.write_evidence(result, self.base / 'live', collect=True)
        self.assertFalse((self.base / 'live/attempts/000/data.npz').exists())

    def test_duplicate_terminals_conflict(self):
        self.terminal()
        shutil.copytree(self.attempt, self.root / 'runs/relocated/duplicate')
        observed = self.observed()
        self.assertEqual(observed['runtime_class'], 'conflict')
        with patch.object(c10, 'process_snapshot', return_value=([], [])):
            _, rc = c10.write_evidence(observed, self.base / 'conflict', collect=True)
        self.assertEqual(rc, 2)
        self.assertTrue((self.base / 'conflict/attempts/000/data.npz').exists())
        self.assertTrue((self.base / 'conflict/attempts/001/data.npz').exists())
        saved = c10.read_json(self.base / 'conflict/inspection.json')
        self.assertEqual(saved['runtime_class'], 'conflict')
        self.assertFalse(saved['validation']['passed'])

    def test_corrupt_zip_checksum_matched_is_failed_and_preserved(self):
        r = self.terminal()
        data = self.attempt / 'data.npz'
        broken = data.read_bytes()[:-30]
        data.write_bytes(broken)
        r['data_sha256'] = c10.sha(data)
        c10.dump(self.attempt / 'receipt.json', r)
        observed = self.observed()
        self.assertEqual(observed['runtime_class'], 'complete-fail')
        self.assertFalse(self.validation()['passed'])
        with patch.object(c10, 'process_snapshot', return_value=([], [])):
            _, rc = c10.write_evidence(observed, self.base / 'broken', collect=True)
        self.assertEqual(rc, 0)
        self.assertEqual((self.base / 'broken/attempts/000/data.npz').read_bytes(), broken)

    def test_malformed_receipt_schema_is_failed_and_preserved(self):
        r = self.terminal()
        r['runtime'] = []
        c10.dump(self.attempt / 'receipt.json', r)
        self.assertEqual(self.observed()['runtime_class'], 'complete-fail')

    def test_actual_parent_run_manifest_is_copied(self):
        self.attempted()
        manifest = self.attempt.parent / 'run_manifest.json'
        manifest.write_text('{"fixture": "original V6 manifest name"}\n')
        observed = self.observed()
        with patch.object(c10, 'process_snapshot', return_value=([], [])):
            _, rc = c10.write_evidence(observed, self.base / 'manifest', collect=True)
        self.assertEqual(rc, 0)
        self.assertEqual((self.base / 'manifest/attempts/000/parent/run_manifest.json').read_bytes(), manifest.read_bytes())

    def test_denied_process_inspection_is_unknown(self):
        with patch.object(c10, 'process_snapshot', return_value=([], [{'error': 'permission denied'}])):
            result = c10.inspect(self.root)
        self.assertEqual(result['runtime_class'], 'unknown')
        self.assertFalse(result['all_roots_accessible'])

    def test_bad_nested_gate_and_case_hash_rejected(self):
        r = self.terminal()
        r['daughter']['checks']['original_H_residual_Eh'] = 2e-7
        r['parent']['finite_model_numerics_passed'] = False
        r['case_sha256'] = c10.FROZEN['input']  # input-byte hash is not case semantic hash
        c10.dump(self.attempt / 'receipt.json', r)
        result = self.validation()
        self.assertFalse(result['passed'])
        self.assertFalse(self.gate(result, 'daughter.checks.original_H_residual_Eh')['pass'])
        self.assertFalse(self.gate(result, 'receipt.case_sha256')['pass'])

    def test_npz_identity_failure_even_with_matching_file_sha(self):
        r = self.terminal()
        with np.load(self.attempt / 'data.npz', allow_pickle=False) as archive:
            arrays = {k: archive[k] for k in archive.files}
        arrays['CI_complement'][0, 0] += .01
        np.savez_compressed(self.attempt / 'data.npz', **arrays)
        r['data_sha256'] = c10.sha(self.attempt / 'data.npz')
        c10.dump(self.attempt / 'receipt.json', r)
        result = self.validation()
        self.assertFalse(result['passed'])
        self.assertFalse(self.gate(result, 'recomputed.q_identity_error')['pass'])

    def test_npz_nonfinite_shape_and_missing_rejected(self):
        r = self.terminal()
        with np.load(self.attempt / 'data.npz', allow_pickle=False) as archive:
            arrays = {k: archive[k] for k in archive.files}
        arrays['rdm1_parent'][0, 0] = np.nan
        arrays['common_orbital_matrix'] = arrays['common_orbital_matrix'][:, :-1]
        np.savez_compressed(self.attempt / 'data.npz', **arrays)
        r['data_sha256'] = c10.sha(self.attempt / 'data.npz')
        c10.dump(self.attempt / 'receipt.json', r)
        result = self.validation()
        self.assertFalse(result['passed'])
        self.assertFalse(self.gate(result, 'npz.common_orbital_matrix.shape')['pass'])
        self.assertFalse(self.gate(result, 'npz.rdm1_parent.finite')['pass'])
        (self.attempt / 'data.npz').unlink()
        self.assertEqual(self.observed()['runtime_class'], 'complete-fail')

    def test_collection_detects_mutation(self):
        self.terminal()
        observed = self.observed()
        (self.attempt / 'stdout.log').write_text('changed between inspection and collection\n')
        with patch.object(c10, 'process_snapshot', return_value=([], [])):
            _, rc = c10.write_evidence(observed, self.base / 'mutating', collect=True)
        self.assertEqual(rc, 2)
        saved = c10.read_json(self.base / 'mutating/inspection.json')
        self.assertEqual(saved['runtime_class'], 'unknown')
        self.assertFalse(saved['validation']['passed'])

    def test_source_mutation_and_extra_unavailable_root(self):
        self.terminal()
        (self.root / c10.SOURCE).write_text('changed source')
        self.assertEqual(self.observed()['runtime_class'], 'complete-fail')
        with patch.object(c10, 'process_snapshot', return_value=([], [])):
            result = c10.inspect(self.root, [self.base / 'unavailable'])
        self.assertEqual(result['runtime_class'], 'unknown')

    def test_proc_exact_identity_and_start_ticks(self):
        self.attempted()
        proc = self.base / 'proc'
        proc.mkdir()
        (proc / 'uptime').write_text('10000.0 1000.0\n')
        def worker(pid, args):
            p = proc / str(pid)
            p.mkdir()
            (p / 'cmdline').write_bytes(b'\0'.join(a.encode() for a in args) + b'\0')
            (p / 'cwd').symlink_to(self.root)
            (p / 'stat').write_text(f'{pid} (python) ' + ' '.join(['S'] + ['0'] * 18 + ['100'] + ['0'] * 4))
            (p / 'status').write_text('VmRSS:\t12000 kB\n')
        worker(90001, [sys.executable, str(self.root / c10.SOURCE), 'case', '--case-file',
                       str(self.attempt / 'input.json'), '--out', str(self.attempt)])
        worker(90002, [sys.executable, 'microphysics_driver_v6.py'])
        worker(90003, [sys.executable, str(self.root / c10.SOURCE), 'run', '--only', c10.CASE_ID,
                       '--contract', str(self.root / c10.CONTRACT), '--out', str(self.attempt.parent)])
        worker(90004, [sys.executable, str(self.root / c10.SOURCE), 'run',
                       '--contract', str(self.root / c10.CONTRACT), '--out', str(self.attempt.parent)])
        worker(90005, [sys.executable, str(self.root / c10.SOURCE), 'run', '--only', 'unrelated_case',
                       '--contract', str(self.root / c10.CONTRACT), '--out', str(self.attempt.parent)])
        matches, errors = c10.process_snapshot(self.root, [self.attempt], proc)
        self.assertFalse(errors)
        self.assertEqual({m['pid'] for m in matches}, {90001, 90003, 90004})
        self.assertTrue(all(m['start_ticks'] == 100 for m in matches))
        self.assertTrue(all(m['wall_supervisor_anomaly'] for m in matches))

    def test_cli_collect_actual_local_subprocess_and_no_overwrite(self):
        self.attempted()
        out = self.base / 'cli'
        command = [sys.executable, str(SCRIPT), 'collect', '--root', str(self.root), '--out', str(out)]
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['runtime_class'], 'stale')
        recorded = c10.read_json(out / 'collector_execution.json')
        self.assertEqual(recorded['exit_code'], 0)
        self.assertEqual((out / 'collector.stdout.log').read_text(), result.stdout)
        again = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(again.returncode, 2)
        self.assertIn('File exists', again.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
