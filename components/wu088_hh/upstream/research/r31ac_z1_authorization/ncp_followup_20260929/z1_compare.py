"""One-shot, preregistered z=1 OD/JVP comparison of the frozen models."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.linalg import norm


EXPECTED = {
    'input': '565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079',
    'prereg': '803b0968bd7f1fab41310469578b455ef03a64aae5beac1f23c1bab8afa19ddb',
    'rule': '68b0d4c4b80443f374b9c49fa4c1737a8e2f39ed6b06f7340d052aa8c7c537b6',
    'R31Z': '4ba03ba2adbdc9533f6472558b33a7edf86959bfc397e5fc8e3e90f8765ba034',
    'R31AA': 'f24d2acc0506e97dbefea107c126e53891d9879311aad60b9dd3b8e9a1be05d5',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def n2(value):
    return float(norm(value, 2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--od', type=Path, required=True)
    p.add_argument('--jvp', type=Path, required=True)
    p.add_argument('--ledger', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.out.exists():
        raise FileExistsError(a.out)
    repo = a.repo.resolve()
    prereg_path = repo/'research/r31aa_validation/Z1_PREREGISTRATION.json'
    rz_path = repo/'research/r31z_source_bound/source_bound.py'
    ra_path = repo/'research/r31aa_validation/local_candidate.py'
    paths = {'input': a.input, 'prereg': prereg_path, 'R31Z': rz_path, 'R31AA': ra_path}
    if any(sha(path) != EXPECTED[key] for key, path in paths.items()):
        raise ValueError('frozen input/model/prereg identity mismatch')
    prereg = json.loads(prereg_path.read_text())
    rule = {key: prereg[source] for key, source in (
        ('models', 'models_frozen_before_execution'), ('primary_metrics', 'primary_metrics'),
        ('secondary_metrics', 'secondary_metrics'), ('comparison_tolerance', 'comparison_tolerance'),
        ('decision_rule', 'decision_rule'))}
    rule_hash = hashlib.sha256(json.dumps(rule, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if rule_hash != EXPECTED['rule'] or prereg['comparison_tolerance'] != 1e-10:
        raise ValueError('frozen decision rule mismatch')
    ledger = json.loads(a.ledger.read_text())
    if not ledger['authorization_consumed'] or ledger['science_commands_started'] != 2:
        raise ValueError('one-shot producer ledger incomplete')
    od_report = json.loads(a.od.with_name('RESULTS.json').read_text())
    jvp_report = json.loads(a.jvp.with_name('RESULTS.json').read_text())
    od_id = json.loads(a.od.with_name('IDENTITY.json').read_text())
    jvp_id = json.loads(a.jvp.with_name('IDENTITY.json').read_text())
    if sha(a.od) != od_report['sha256'] or sha(a.jvp) != jvp_report['sha256']:
        raise ValueError('direct output hash mismatch')
    if od_id['n'] != 192 or float(od_id['z']) != 1 or jvp_id['n'] != 192 or float(jvp_id['z']) != 1:
        raise ValueError('direct output geometry/order mismatch')
    if od_report['Hamiltonian_included'] is not False or od_report['independent_dotO_included'] is not False:
        raise ValueError('OD output scope mismatch')
    with np.load(a.input, allow_pickle=False) as f:
        fit = {key: f[key] for key in f.files}
    with np.load(a.od, allow_pickle=False) as f:
        od = {key: f[key] for key in f.files}
    with np.load(a.jvp, allow_pickle=False) as f:
        jvp = {key: f[key] for key in f.files}
    if any(od[key].shape != (47, 2) for key in ('O', 'D_col')) or od['D_row'].shape != (2, 47):
        raise ValueError('OD block shape mismatch')
    if jvp['O'].shape != (47, 2) or jvp['dotO'].shape != (47, 2):
        raise ValueError('JVP block shape mismatch')
    raw_metric = jvp['dotO']-od['D_col']-od['D_row'].conj().T
    raw_overlap = jvp['O']-od['O']
    cast = lambda value: np.asarray(value, dtype=np.complex128)
    direct = {'O': cast(od['O']), 'dotO': cast(jvp['dotO']),
              'Dcol': cast(od['D_col']), 'Drow': cast(od['D_row'])}
    direct['K'] = (direct['Dcol']-direct['Drow'].conj().T)/2
    O = [cast(fit['z0_od_O']), cast(fit['direct_O'][:47, 47:]), cast(fit['z4_od_O'])]
    dot = [cast(fit['z0_j_dotO']), cast(fit['direct_dotO'][:47, 47:]), cast(fit['z4_j_dotO'])]
    dc = [cast(fit['z0_od_D_col']), cast(fit['direct_D'][:47, 47:]), cast(fit['z4_od_D_col'])]
    dr = [cast(fit['z0_od_D_row']), cast(fit['direct_D'][47:, :47]), cast(fit['z4_od_D_row'])]
    K = [(c-r.conj().T)/2 for c, r in zip(dc, dr)]
    T = 4/float(fit['velocity'])
    global_model = load_module(rz_path, 'r31z_frozen_z1')
    local_model = load_module(ra_path, 'r31aa_frozen_z1')
    global_o, global_dot = global_model.quintic_hermite(O, dot, T, .25)
    global_k = global_model.quadratic_three_nodes(K, .25)
    global_dc = global_dot/2+global_k
    global_dr = (global_dot/2-global_k).conj().T
    local_o, local_dot, local_dc, local_dr, local_k = local_model.local_candidate(O, dot, K, T, .25)

    def errors(o, derivative, k, col, row):
        result = {'E_O': n2(o-direct['O']), 'E_dotO_per_ta': n2(derivative-direct['dotO']),
                  'E_K_per_ta': n2(k-direct['K']), 'E_Dcol_per_ta': n2(col-direct['Dcol']),
                  'E_Drow_per_ta': n2(row-direct['Drow']),
                  'candidate_metric_identity_residual_2norm': n2(derivative-col-row.conj().T)}
        result['E_Dmax_per_ta'] = max(result['E_Dcol_per_ta'], result['E_Drow_per_ta'])
        return result

    ge = errors(global_o, global_dot, global_k, global_dc, global_dr)
    le = errors(local_o, local_dot, local_k, local_dc, local_dr)
    primary = ('E_K_per_ta', 'E_Dmax_per_ta')
    tol = prereg['comparison_tolerance']
    local_support = all(le[k] <= ge[k]+tol for k in primary) and any(ge[k]-le[k] > tol for k in primary)
    global_support = all(ge[k] <= le[k]+tol for k in primary) and any(le[k]-ge[k] > tol for k in primary)
    if local_support and global_support:
        raise ValueError('inconsistent Pareto rule')
    verdict = ('PARETO_SUPPORTED_AT_Z1' if local_support else
               'GLOBAL_SUPPORTED_AT_Z1' if global_support else 'TRADEOFF_UNRESOLVED')
    result = {
        'schema': 'WU088_R31AC_Z1_FROZEN_MODEL_COMPARISON_V1',
        'z_a0': 1.0, 'time_ta': 1/float(fit['velocity']), 'radial_order': 192,
        'fit_nodes_z_a0': [0, 2, 4], 'direct_node_used_to_fit_either_model': False,
        'frozen_model_sha256': {'R31Z': EXPECTED['R31Z'], 'R31AA': EXPECTED['R31AA']},
        'preregistration_sha256': EXPECTED['prereg'], 'metric_rule_sha256': rule_hash,
        'comparison_dtype': 'complex128 matching prior R31Z/R31AA replays',
        'direct_outputs': {'OD': {'path': str(a.od), 'sha256': sha(a.od), 'bytes': a.od.stat().st_size},
                           'JVP': {'path': str(a.jvp), 'sha256': sha(a.jvp), 'bytes': a.jvp.stat().st_size}},
        'direct_source_O_OD_minus_JVP_raw_max_abs': float(np.max(np.abs(raw_overlap))),
        'direct_source_O_OD_minus_JVP_2norm_complex128': n2(cast(raw_overlap)),
        'direct_metric_identity_raw_max_abs': float(np.max(np.abs(raw_metric))),
        'direct_metric_identity_2norm_complex128': n2(direct['dotO']-direct['Dcol']-direct['Drow'].conj().T),
        'global_R31Z': ge, 'local_R31AA': le,
        'primary_comparison_tolerance': tol, 'frozen_decision_rule_verdict': verdict,
        'z3_status': 'POST_HOC_TUNING_DATA_NOT_INDEPENDENT_CONFIRMATION',
        'independent_z1_model_comparison_point': True,
        'interval_wide_accuracy_admitted': False, 'trajectory_accuracy_admitted': False,
        'transition_error_admitted': False, 'full_cell_admitted': False,
        'production_admitted': False, 'H_skip_admitted': False,
    }
    payload = json.dumps(result, indent=2, allow_nan=False)+'\n'
    a.out.write_text(payload)
    print(payload, end='')


if __name__ == '__main__':
    main()
