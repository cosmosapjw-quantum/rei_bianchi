"""Hash-locked z=3 post-hoc comparison; this performs no scientific evaluation."""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
from scipy.linalg import norm

from research.r31aa_validation.local_candidate import local_candidate
from research.r31z_source_bound.source_bound import quintic_hermite, quadratic_three_nodes

INPUT_SHA = '565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079'
ARCHIVE_SHA = 'c10c932a6cdad817982e00920a893733b367827b116d058791bf5aacad517cd9'
OD = ('completion/mixed_h/od/B192_z3/ASSEMBLED_OD.npz',
      '47f41c15aba4fc3eb4e9a6b6f08202067cf525503a87431035ee692990b553af')
JVP = ('completion/mixed_derivative/B192_z3/ASSEMBLED.npz',
       '9223dfea7956a58a70595ab25dda457be64b966ce247830e5c12a73d87515661')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_npz(data):
    with np.load(io.BytesIO(data), allow_pickle=False) as f:
        return {key: f[key] for key in f.files}


def n2(x):
    return float(norm(x, 2))


def compare(snapshot, archive):
    raw = Path(snapshot).read_bytes()
    if len(raw) != 71481 or digest(raw) != INPUT_SHA:
        raise ValueError('fit input identity mismatch')
    archive = Path(archive)
    if digest(archive.read_bytes()) != ARCHIVE_SHA:
        raise ValueError('producer archive identity mismatch')
    fit = load_npz(raw)
    with zipfile.ZipFile(archive) as z:
        arrays = []
        for member, sha in (OD, JVP):
            data = z.read(member)
            if digest(data) != sha:
                raise ValueError('producer member identity mismatch: ' + member)
            arrays.append(load_npz(data))
    od, jvp = arrays
    if int(od['n']) != 192 or float(od['z']) != 3 or float(jvp['z']) != 3:
        raise ValueError('z3 node identity mismatch')
    cast = lambda a: np.asarray(a, dtype=np.complex128)
    O = [cast(fit['z0_od_O']), cast(fit['direct_O'][:47, 47:]), cast(fit['z4_od_O'])]
    dot = [cast(fit['z0_j_dotO']), cast(fit['direct_dotO'][:47, 47:]), cast(fit['z4_j_dotO'])]
    dc = [cast(fit['z0_od_D_col']), cast(fit['direct_D'][:47, 47:]), cast(fit['z4_od_D_col'])]
    dr = [cast(fit['z0_od_D_row']), cast(fit['direct_D'][47:, :47]), cast(fit['z4_od_D_row'])]
    K = [(c-r.conj().T)/2 for c, r in zip(dc, dr)]
    T = 4/float(fit['velocity'])
    global_O, global_dot = quintic_hermite(O, dot, T, .75)
    global_K = quadratic_three_nodes(K, .75)
    local_O, local_dot, local_dc, local_dr, local_K = local_candidate(O, dot, K, T, .75)
    actual = {'O': cast(od['O']), 'dotO': cast(jvp['dotO']),
              'D_col': cast(od['D_col']), 'D_row': cast(od['D_row'])}
    actual['K'] = (actual['D_col']-actual['D_row'].conj().T)/2

    def scores(o, derivative, k, col, row):
        values = {'E_O': n2(o-actual['O']), 'E_dotO_per_ta': n2(derivative-actual['dotO']),
                  'E_K_per_ta': n2(k-actual['K']), 'E_Dcol_per_ta': n2(col-actual['D_col']),
                  'E_Drow_per_ta': n2(row-actual['D_row']),
                  'candidate_metric_residual_2norm': n2(derivative-col-row.conj().T)}
        values['E_Dmax_per_ta'] = max(values['E_Dcol_per_ta'], values['E_Drow_per_ta'])
        return values

    global_dc = global_dot/2+global_K
    global_dr = (global_dot/2-global_K).conj().T
    global_scores = scores(global_O, global_dot, global_K, global_dc, global_dr)
    local_scores = scores(local_O, local_dot, local_K, local_dc, local_dr)
    return {'schema': 'WU088_R31AA_Z3_POSTHOC_COMPARISON_V1',
            'fit_nodes_z_a0': [0, 2, 4], 'posthoc_node_z_a0': 3,
            'input_sha256': INPUT_SHA, 'archive_sha256': ARCHIVE_SHA,
            'OD_member': {'path': OD[0], 'sha256': OD[1]},
            'JVP_member': {'path': JVP[0], 'sha256': JVP[1]},
            'comparison_dtype': 'complex128, matching R31Z/R31AA replay',
            'source_O_OD_minus_JVP_2norm': n2(actual['O']-cast(jvp['O'])),
            'source_metric_residual_2norm': n2(actual['dotO']-actual['D_col']-actual['D_row'].conj().T),
            'global_R31Z': global_scores, 'local_R31AA': local_scores,
            'local_minus_global': {k: local_scores[k]-global_scores[k] for k in global_scores},
            'independent_validation': False,
            'reason': 'R31AA local form was chosen after inspecting R31Z z3 failure',
            'z3_reused_as_new_confirmation': False,
            'new_scientific_nodes': 0}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.out.exists():
        raise FileExistsError(a.out)
    result = compare(a.input, a.archive)
    payload = json.dumps(result, indent=2, allow_nan=False)+'\n'
    a.out.write_text(payload)
    print(payload, end='')


if __name__ == '__main__':
    main()
