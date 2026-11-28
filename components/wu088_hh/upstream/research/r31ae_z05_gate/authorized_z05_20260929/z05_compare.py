"""Apply the frozen R31AD/R31Z Pareto comparison at the one-shot z=0.5 node."""
import argparse
import hashlib
import importlib.util
import io
import json
import zipfile
from pathlib import Path

import numpy as np
from scipy.linalg import norm


EXPECTED = {
    'R31AD': 'ab220248066580fc77af70c412251dbe3ed643a6fadc266cf5c25a7a3a6651a0',
    'R31Z': '4ba03ba2adbdc9533f6472558b33a7edf86959bfc397e5fc8e3e90f8765ba034',
    'manifest': '05f4068dffad51080942c466e19943a73c508b004d3d46f3b9a2b69a58cefc49',
    'selection': '2761664a75d7609c7ac0b1df4daf36a50e01d82a80b28a42885a22c5042a800b',
    'rule': '835c0a53719849652557737ef61d343c58222d847cf6d1b2ee6fb4831fb656dc',
    'prereg': 'a111005296954c303563be6aaab10379d22694c544576fb1869a37938ab9247d',
    'snapshot': '565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079',
    'archive': 'c10c932a6cdad817982e00920a893733b367827b116d058791bf5aacad517cd9',
    'z1_od': '020dc2c2c580f7e7f8a2d5d322b771b4957fbcc1166ab4e2c363f5a9c3d06818',
    'z1_jvp': 'b6a9926052999c70cc6092c0d47001eff0716d2aefb6ff380edfa18558696819',
    'z3_od': '47f41c15aba4fc3eb4e9a6b6f08202067cf525503a87431035ee692990b553af',
    'z3_jvp': '9223dfea7956a58a70595ab25dda457be64b966ce247830e5c12a73d87515661',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def loadnpz(blob):
    with np.load(io.BytesIO(blob), allow_pickle=False) as src:
        return {key: src[key] for key in src.files}


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def cast(array):
    return np.asarray(array, dtype=np.complex128)


def n2(array):
    return float(norm(cast(array), 2))


def main():
    p = argparse.ArgumentParser()
    for field in ('repo', 'snapshot', 'archive', 'od', 'jvp', 'ledger', 'out'):
        p.add_argument('--'+field, required=True, type=Path)
    a = p.parse_args()
    if a.out.exists():
        raise FileExistsError(a.out)
    root = a.repo.resolve()
    paths = {
        'R31AD': root/'research/r31ad_five_node/unit_cell_model.py',
        'R31Z': root/'research/r31z_source_bound/source_bound.py',
        'manifest': root/'research/r31ad_five_node/ncp_followup_20260929/FIVE_NODE_INPUT_MANIFEST.json',
        'selection': root/'research/r31ad_five_node/ncp_followup_20260929/MIDPOINT_SELECTION.json',
        'rule': root/'research/r31ad_five_node/ncp_followup_20260929/FROZEN_SELECTION_RULE.json',
        'prereg': root/'research/r31ad_five_node/ncp_followup_20260929/NEXT_VALIDATION_PREREGISTRATION.json',
        'snapshot': a.snapshot, 'archive': a.archive,
        'z1_od': root/'research/r31ac_z1_authorization/authorized_z1_20260929/OD_RAW/ASSEMBLED_OD.npz',
        'z1_jvp': root/'research/r31ac_z1_authorization/authorized_z1_20260929/JVP_RAW/ASSEMBLED.npz',
    }
    if any(sha(path) != EXPECTED[key] for key, path in paths.items()):
        raise ValueError('frozen model, rule, training data or archive drift')
    prereg = json.loads(paths['prereg'].read_text())
    selection = json.loads(paths['selection'].read_text())
    if prereg['selected_z_a0'] != selection['selected_z_a0'] or selection['selected_z_a0'] != .5:
        raise ValueError('selected midpoint drift')
    if prereg['comparison_tolerance'] != 1e-10:
        raise ValueError('comparison tolerance drift')
    ledger = json.loads(a.ledger.read_text())
    if not ledger['authorization_consumed'] or ledger['one_shot_state'] != 'CONSUMED_OUTPUTS_COMPLETE' or ledger['science_commands_started'] != 2:
        raise ValueError('one-shot ledger incomplete')
    od_report = json.loads(a.od.with_name('RESULTS.json').read_text())
    jvp_report = json.loads(a.jvp.with_name('RESULTS.json').read_text())
    od_id = json.loads(a.od.with_name('IDENTITY.json').read_text())
    jvp_id = json.loads(a.jvp.with_name('IDENTITY.json').read_text())
    if sha(a.od) != od_report['sha256'] or sha(a.jvp) != jvp_report['sha256']:
        raise ValueError('direct output hash mismatch')
    if float(od_id['z']) != .5 or float(jvp_id['z']) != .5 or od_id['n'] != 192 or jvp_id['n'] != 192:
        raise ValueError('direct output geometry/order mismatch')
    if od_report['Hamiltonian_included'] is not False or od_report['independent_dotO_included'] is not False:
        raise ValueError('OD output scope mismatch')
    fit = loadnpz(paths['snapshot'].read_bytes())
    od = loadnpz(a.od.read_bytes())
    jvp = loadnpz(a.jvp.read_bytes())
    if (od['O'].shape, od['D_col'].shape, od['D_row'].shape, jvp['dotO'].shape) != ((47,2),(47,2),(2,47),(47,2)):
        raise ValueError('direct mixed block shape mismatch')
    if jvp['O'].shape != (47,2):
        raise ValueError('independent JVP O shape mismatch')
    source_O_gap = jvp['O']-od['O']
    source_metric = jvp['dotO']-od['D_col']-od['D_row'].conj().T
    with zipfile.ZipFile(a.archive) as z:
        m_od = 'completion/mixed_h/od/B192_z3/ASSEMBLED_OD.npz'
        m_jvp = 'completion/mixed_derivative/B192_z3/ASSEMBLED.npz'
        z3_od_blob, z3_jvp_blob = z.read(m_od), z.read(m_jvp)
    if hashlib.sha256(z3_od_blob).hexdigest() != EXPECTED['z3_od'] or hashlib.sha256(z3_jvp_blob).hexdigest() != EXPECTED['z3_jvp']:
        raise ValueError('z3 training node drift')
    z1_od = loadnpz(paths['z1_od'].read_bytes())
    z1_jvp = loadnpz(paths['z1_jvp'].read_bytes())
    z3_od = loadnpz(z3_od_blob)
    z3_jvp = loadnpz(z3_jvp_blob)
    raw = [
        (fit['z0_od_O'],fit['z0_od_D_col'],fit['z0_od_D_row'],fit['z0_j_dotO']),
        (z1_od['O'],z1_od['D_col'],z1_od['D_row'],z1_jvp['dotO']),
        (fit['direct_O'][:47,47:],fit['direct_D'][:47,47:],fit['direct_D'][47:,:47],fit['direct_dotO'][:47,47:]),
        (z3_od['O'],z3_od['D_col'],z3_od['D_row'],z3_jvp['dotO']),
        (fit['z4_od_O'],fit['z4_od_D_col'],fit['z4_od_D_row'],fit['z4_j_dotO']),
    ]
    vals = [cast(x[0]) for x in raw]
    dcs = [cast(x[1]) for x in raw]
    drs = [cast(x[2]) for x in raw]
    dots = [cast(x[3]) for x in raw]
    ks = [(c-r.conj().T)/2 for c,r in zip(dcs,drs)]
    v = float(fit['velocity'])
    times = [j/v for j in range(5)]
    t = .5/v
    new = load_module(paths['R31AD'], 'r31ad_z05_frozen')
    old = load_module(paths['R31Z'], 'r31z_z05_frozen')
    new_o,new_dot,new_dc,new_dr,new_k,_ = new.piecewise_candidate(times,vals,dots,ks,t)
    old_o,old_dot = old.quintic_hermite([vals[i] for i in (0,2,4)],[dots[i] for i in (0,2,4)],times[-1],.125)
    old_k = old.quadratic_three_nodes([ks[i] for i in (0,2,4)],.125)
    old_dc = old_dot/2+old_k
    old_dr = (old_dot/2-old_k).conj().T
    direct = {'O':cast(od['O']), 'dotO':cast(jvp['dotO']), 'Dcol':cast(od['D_col']), 'Drow':cast(od['D_row'])}
    direct['K'] = (direct['Dcol']-direct['Drow'].conj().T)/2

    def errors(O,dot,Dc,Dr,K):
        result = {'E_O':n2(O-direct['O']), 'E_dotO_per_ta':n2(dot-direct['dotO']),
                  'E_K_per_ta':n2(K-direct['K']), 'E_Dcol_per_ta':n2(Dc-direct['Dcol']),
                  'E_Drow_per_ta':n2(Dr-direct['Drow']),
                  'candidate_metric_identity_residual_2norm':n2(dot-Dc-Dr.conj().T)}
        result['E_Dmax_per_ta'] = max(result['E_Dcol_per_ta'],result['E_Drow_per_ta'])
        return result

    ne = errors(new_o,new_dot,new_dc,new_dr,new_k)
    ge = errors(old_o,old_dot,old_dc,old_dr,old_k)
    primary = ('E_K_per_ta','E_Dmax_per_ta')
    tol = prereg['comparison_tolerance']
    new_support = all(ne[k] <= ge[k]+tol for k in primary) and any(ge[k]-ne[k] > tol for k in primary)
    old_support = all(ge[k] <= ne[k]+tol for k in primary) and any(ne[k]-ge[k] > tol for k in primary)
    if new_support and old_support:
        raise ValueError('inconsistent Pareto verdict')
    verdict = ('PARETO_SUPPORTED_AT_SELECTED_MIDPOINT' if new_support else
               'GLOBAL_SUPPORTED_AT_SELECTED_MIDPOINT' if old_support else 'TRADEOFF_UNRESOLVED')
    gap = float(np.max(np.abs(source_O_gap)))
    metric = float(np.max(np.abs(source_metric)))
    bridge_pass = max(gap,metric) <= 2e-12
    result = {
        'schema':'WU088_R31AE_Z05_FROZEN_MODEL_COMPARISON_V1',
        'z_a0':.5,'time_ta':t,'radial_order':192,'training_node_z_a0':[0,1,2,3,4],
        'direct_node_used_in_selection_or_training':False,
        'frozen_sha256':{key:EXPECTED[key] for key in ('R31AD','R31Z','manifest','selection','rule','prereg')},
        'comparison_dtype':'complex128, same as frozen R31AD/R31Z replays; raw complex256 retained',
        'direct_outputs':{'OD':{'path':str(a.od),'sha256':sha(a.od),'bytes':a.od.stat().st_size},
                          'JVP':{'path':str(a.jvp),'sha256':sha(a.jvp),'bytes':a.jvp.stat().st_size}},
        'direct_source_O_OD_minus_JVP_raw_max_abs':gap,
        'direct_source_O_OD_minus_JVP_2norm_complex128':n2(source_O_gap),
        'direct_metric_identity_raw_max_abs':metric,
        'direct_metric_identity_2norm_complex128':n2(direct['dotO']-direct['Dcol']-direct['Drow'].conj().T),
        'source_bridge_pass_at_existing_2e_minus_12_tolerance':bridge_pass,
        'R31AD_five_node':ne,'R31Z_global':ge,
        'primary_comparison_tolerance':tol,'frozen_decision_rule_verdict':verdict,
        'S_design_score_used_for_final_decision':False,
        'independent_z05_single_point_validation':bridge_pass,
        'interval_wide_accuracy_admitted':False,'transition_error_admitted':False,
        'trajectory_accuracy_admitted':False,'full_cell_admitted':False,
        'H_skip_admitted':False,'production_admitted':False,
    }
    for key,path in paths.items():
        if sha(path) != EXPECTED[key]:
            raise ValueError(f'post-comparison frozen input drift: {key}')
    payload = json.dumps(result,indent=2,allow_nan=False)+'\n'
    a.out.write_text(payload)
    print(payload,end='')


if __name__ == '__main__':
    main()
