"""Read-only, source-bound R31AD five-node replay and midpoint design."""
import argparse
import hashlib
import importlib.util
import io
import json
import math
import zipfile
from pathlib import Path

import numpy as np
from scipy.linalg import norm


EXPECTED = {
    'snapshot': '565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079',
    'archive': 'c10c932a6cdad817982e00920a893733b367827b116d058791bf5aacad517cd9',
    'z1_od': '020dc2c2c580f7e7f8a2d5d322b771b4957fbcc1166ab4e2c363f5a9c3d06818',
    'z1_jvp': 'b6a9926052999c70cc6092c0d47001eff0716d2aefb6ff380edfa18558696819',
    'z3_od': '47f41c15aba4fc3eb4e9a6b6f08202067cf525503a87431035ee692990b553af',
    'z3_jvp': '9223dfea7956a58a70595ab25dda457be64b966ce247830e5c12a73d87515661',
    'R31AD': 'ab220248066580fc77af70c412251dbe3ed643a6fadc266cf5c25a7a3a6651a0',
    'R31Z': '4ba03ba2adbdc9533f6472558b33a7edf86959bfc397e5fc8e3e90f8765ba034',
    'rule': '835c0a53719849652557737ef61d343c58222d847cf6d1b2ee6fb4831fb656dc',
}


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def jwrite(path, obj):
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def n2(a):
    return float(norm(np.asarray(a, dtype=np.complex128), 2))


def npz(blob):
    with np.load(io.BytesIO(blob), allow_pickle=False) as src:
        return {key: src[key] for key in src.files}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', required=True, type=Path)
    p.add_argument('--snapshot', required=True, type=Path)
    p.add_argument('--archive', required=True, type=Path)
    p.add_argument('--outdir', required=True, type=Path)
    a = p.parse_args()
    repo, out = a.repo.resolve(), a.outdir.resolve()
    rule_path = out/'FROZEN_SELECTION_RULE.json'
    model_path = repo/'research/r31ad_five_node/unit_cell_model.py'
    global_path = repo/'research/r31z_source_bound/source_bound.py'
    bound = {'snapshot': a.snapshot, 'archive': a.archive, 'R31AD': model_path,
             'R31Z': global_path, 'rule': rule_path}
    for key, path in bound.items():
        if digest(path.read_bytes()) != EXPECTED[key]:
            raise ValueError(f'{key} hash drift')
    rule = json.loads(rule_path.read_text())
    snapshot_blob = a.snapshot.read_bytes()
    fit = npz(snapshot_blob)
    velocity = float(fit['velocity'])
    z1dir = repo/'research/r31ac_z1_authorization/authorized_z1_20260929'
    z1_od_path = z1dir/'OD_RAW/ASSEMBLED_OD.npz'
    z1_jvp_path = z1dir/'JVP_RAW/ASSEMBLED.npz'
    z1_od_blob, z1_jvp_blob = z1_od_path.read_bytes(), z1_jvp_path.read_bytes()
    if digest(z1_od_blob) != EXPECTED['z1_od'] or digest(z1_jvp_blob) != EXPECTED['z1_jvp']:
        raise ValueError('z1 output hash drift')
    with zipfile.ZipFile(a.archive) as archive:
        od3_member = 'completion/mixed_h/od/B192_z3/ASSEMBLED_OD.npz'
        jvp3_member = 'completion/mixed_derivative/B192_z3/ASSEMBLED.npz'
        od3_blob, jvp3_blob = archive.read(od3_member), archive.read(jvp3_member)
        if digest(od3_blob) != EXPECTED['z3_od'] or digest(jvp3_blob) != EXPECTED['z3_jvp']:
            raise ValueError('z3 archive member hash drift')
        archive_names = set(archive.namelist())
        half_member = 'completion/mixed_h/od/B192_z1.5/ASSEMBLED_OD.npz'
        half_blob = archive.read(half_member)
        midpoint_inventory = []
        runtime = Path('/root/WU088_R31AC_Z1_RUNTIME_20260929')
        for z in rule['candidate_z_a0']:
            label = f'B192_z{z:g}'
            od_member = f'completion/mixed_h/od/{label}/ASSEMBLED_OD.npz'
            j_member = f'completion/mixed_derivative/{label}/ASSEMBLED.npz'
            od_present, j_present = od_member in archive_names, j_member in archive_names
            local_od = runtime/od_member
            local_jvp = runtime/j_member
            any_direct = od_present or j_present or local_od.exists() or local_jvp.exists()
            midpoint_inventory.append({
                'z_a0': z, 'time_ta': z/velocity,
                'CP4_OD_member': od_member if od_present else None,
                'CP4_JVP_member': j_member if j_present else None,
                'local_OD_path': str(local_od) if local_od.exists() else None,
                'local_JVP_path': str(local_jvp) if local_jvp.exists() else None,
                'equivalent_complete_direct_OD_plus_independent_dotO': od_present and j_present,
                'preexisting_or_preaccessed_direct_output': any_direct,
                'fresh_candidate': not any_direct,
            })
        midpoint_inventory[1]['partial_OD_sha256'] = digest(half_blob)
        midpoint_inventory[1]['partial_OD_bytes'] = len(half_blob)
        if midpoint_inventory[1]['partial_OD_sha256'] != '566ede0497f0754a11f4dd292f523812a10ebd50ee516cec4a7eec803d90e25d':
            raise ValueError('z1.5 OD inventory drift')
    jwrite(out/'MIDPOINT_DIRECT_DATA_INVENTORY.json', {
        'schema': 'WU088_R31AD_MIDPOINT_DIRECT_INVENTORY_V1',
        'archive': {'path': str(a.archive), 'sha256': EXPECTED['archive'], 'members': len(archive_names)},
        'local_runtime': str(runtime), 'rows': midpoint_inventory,
        'provider_search_scope': 'Drive and Dropbox filename search B192_z0.5/1.5/2.5/3.5; no independently verified complete direct midpoint pair; ZIP name search is not archive-member absence proof',
        'interpretation': 'z1.5 excluded because CP4 contains direct OD even though independent JVP is absent; other candidates fresh within searched sources, not a universal absence claim',
    })

    z1_od, z1_jvp = npz(z1_od_blob), npz(z1_jvp_blob)
    z3_od, z3_jvp = npz(od3_blob), npz(jvp3_blob)
    roles = ['TRAINING', 'PRIOR_INDEPENDENT_VALIDATION_CONSUMED_AS_R31AD_TRAINING',
             'TRAINING', 'PRIOR_POST_HOC_TUNING_CONSUMED_AS_R31AD_TRAINING', 'TRAINING']
    raw = [
        (fit['z0_od_O'], fit['z0_od_D_col'], fit['z0_od_D_row'], fit['z0_j_dotO']),
        (z1_od['O'], z1_od['D_col'], z1_od['D_row'], z1_jvp['dotO']),
        (fit['direct_O'][:47,47:], fit['direct_D'][:47,47:], fit['direct_D'][47:,:47], fit['direct_dotO'][:47,47:]),
        (z3_od['O'], z3_od['D_col'], z3_od['D_row'], z3_jvp['dotO']),
        (fit['z4_od_O'], fit['z4_od_D_col'], fit['z4_od_D_row'], fit['z4_j_dotO']),
    ]
    source = [
        {'path': str(a.snapshot), 'objects': ['z0_od_O','z0_od_D_col','z0_od_D_row','z0_j_dotO'], 'sha256': EXPECTED['snapshot'], 'bytes': len(snapshot_blob)},
        {'OD_path': str(z1_od_path), 'OD_sha256': EXPECTED['z1_od'], 'OD_bytes': len(z1_od_blob), 'JVP_path': str(z1_jvp_path), 'JVP_sha256': EXPECTED['z1_jvp'], 'JVP_bytes': len(z1_jvp_blob)},
        {'path': str(a.snapshot), 'objects': ['direct_O[:47,47:]','direct_D[:47,47:]','direct_D[47:,:47]','direct_dotO[:47,47:]'], 'sha256': EXPECTED['snapshot'], 'bytes': len(snapshot_blob), 'upstream_member': 'WU088_HH_R31S_NCP_20260928/evidence/z2/R31S_FULL49_z2.npz'},
        {'archive': str(a.archive), 'OD_member': od3_member, 'OD_sha256': EXPECTED['z3_od'], 'OD_bytes': len(od3_blob), 'JVP_member': jvp3_member, 'JVP_sha256': EXPECTED['z3_jvp'], 'JVP_bytes': len(jvp3_blob)},
        {'path': str(a.snapshot), 'objects': ['z4_od_O','z4_od_D_col','z4_od_D_row','z4_j_dotO'], 'sha256': EXPECTED['snapshot'], 'bytes': len(snapshot_blob)},
    ]
    manifest_rows = []
    for j, (O, Dc, Dr, dot) in enumerate(raw):
        if (O.shape, Dc.shape, Dr.shape, dot.shape) != ((47,2),(47,2),(2,47),(47,2)):
            raise ValueError(f'z{j} block shape')
        manifest_rows.append({
            'z_a0': j, 'time_ta': j/velocity, 'role': roles[j], 'source': source[j],
            'fields': {'O': '47x2', 'D_col': '47x2', 'D_row': '2x47', 'independent_dotO': '47x2'},
            'raw_dtypes': {'O': str(O.dtype), 'D_col': str(Dc.dtype), 'D_row': str(Dr.dtype), 'dotO': str(dot.dtype)},
            'raw_metric_identity_max_abs': float(np.max(np.abs(dot-Dc-Dr.conj().T))),
            'raw_metric_identity_2norm_cast_complex128': n2(dot-Dc-Dr.conj().T),
            'basis_order_phase_contract': 'CP4 frozen B192 47 channel order: centre0 24 then centre1 excited23; ionic columns 2; phase_E and tau=z/velocity; independent dotO is analytic JVP in 1/t_a; source lines in R31Y PRODUCER_INTAKE.json',
        })
    manifest_rows[1]['OD_vs_JVP_O_raw_max_abs'] = float(np.max(np.abs(z1_od['O']-z1_jvp['O'])))
    manifest_rows[3]['OD_vs_JVP_O_raw_max_abs'] = float(np.max(np.abs(z3_od['O']-z3_jvp['O'])))
    jwrite(out/'FIVE_NODE_INPUT_MANIFEST.json', {
        'schema':'WU088_R31AD_FIVE_NODE_INPUT_MANIFEST_V1', 'nodes':manifest_rows,
        'R31AD_independent_validation_points': [], 'upstream_provenance': 'research/r31y_lowrank/ncp_followup_20260929/PRODUCER_INTAKE.json',
        'diagnostic_interpolation_dtype': 'complex128 (same as R31Z/R31AA); raw complex256 retained in source',
        'source_array_mutation': False,
    })
    m = module(model_path, 'r31ad_frozen')
    g = module(global_path, 'r31z_frozen')
    vals = [np.asarray(x[0], dtype=np.complex128) for x in raw]
    dcs = [np.asarray(x[1], dtype=np.complex128) for x in raw]
    drs = [np.asarray(x[2], dtype=np.complex128) for x in raw]
    dots = [np.asarray(x[3], dtype=np.complex128) for x in raw]
    ks = [(c-r.conj().T)/2 for c,r in zip(dcs,drs)]
    times = [j/velocity for j in range(5)]
    maxima = {'O':0., 'dotO':0., 'K':0., 'D_col':0., 'D_row':0.}
    for j,t in enumerate(times):
        O,dot,Dc,Dr,K,_ = m.piecewise_candidate(times, vals, dots, ks, t)
        for key,err in [('O',O-vals[j]),('dotO',dot-dots[j]),('K',K-ks[j]),('D_col',Dc-dcs[j]),('D_row',Dr-drs[j])]:
            maxima[key] = max(maxima[key], n2(err))
    continuity = {'O':0., 'dotO':0., 'K':0., 'D_col':0., 'D_row':0.}
    for j in (1,2,3):
        hl=times[j]-times[j-1]; hr=times[j+1]-times[j]
        lo,ld=m.cubic_hermite(vals[j-1],vals[j],dots[j-1],dots[j],hl,1.)
        ro,rd=m.cubic_hermite(vals[j],vals[j+1],dots[j],dots[j+1],hr,0.)
        lk=ks[j]; rk=ks[j]
        for key,err in [('O',lo-ro),('dotO',ld-rd),('K',lk-rk),('D_col',ld/2+lk-rd/2-rk),('D_row',(ld/2-lk).conj().T-(rd/2-rk).conj().T)]:
            continuity[key]=max(continuity[key],n2(err))
    metric_max=0.
    for t in np.linspace(times[0],times[-1],257):
        O,dot,Dc,Dr,K,_=m.piecewise_candidate(times,vals,dots,ks,float(t))
        metric_max=max(metric_max,n2(dot-Dc-Dr.conj().T))
    if max(maxima.values())>1e-12 or max(continuity.values())>1e-12 or metric_max>1e-12:
        raise ValueError('five-node model identity failure')
    replay={'schema':'WU088_R31AD_FIVE_NODE_MODEL_REPLAY_V1',
            'node_reproduction_max_2norm':maxima,'internal_node_continuity_max_2norm':continuity,
            'dense_grid_points':257,'dense_grid_metric_identity_max_2norm':metric_max,
            'comparison_dtype':'complex128; raw dtype per manifest',
            'cubic_midpoint_remainder_factor':'h^4/384','linear_midpoint_remainder_factor':'h^2/8',
            'width_2_to_1_cubic_coefficient_ratio':16,'width_2_to_1_linear_coefficient_ratio':4,
            'empirical_error_reduction_claimed':False,'predictive_validation_performed':False,
            'source_array_mutation':False,'science_node_count':0}
    jwrite(out/'R31AD_MODEL_REPLAY.json',replay)
    rows=[]
    for inv in midpoint_inventory:
        z=inv['z_a0']; row={'z_a0':z,'fresh_candidate':inv['fresh_candidate']}
        if inv['fresh_candidate']:
            t=z/velocity
            new=m.piecewise_candidate(times,vals,dots,ks,t)[:5]
            s=z/4
            go,gd=g.quintic_hermite([vals[i] for i in (0,2,4)],[dots[i] for i in (0,2,4)],times[-1],s)
            gk=g.quadratic_three_nodes([ks[i] for i in (0,2,4)],s)
            old=(go,gd,gd/2+gk,(gd/2-gk).conj().T,gk)
            d=m.separation(old,new)
            row.update({'DeltaK_model':d['K'],'DeltaDcol_model':d['Dcol'],
                        'DeltaDrow_model':d['Drow'],'DeltaDmax_model':d['Dmax'],
                        'S_design_only':math.hypot(d['K'],d['Dmax'])})
        else:
            row.update({'excluded_reason':'preexisting direct OD output at z1.5; no independent JVP',
                        'DeltaK_model':None,'DeltaDcol_model':None,'DeltaDrow_model':None,'DeltaDmax_model':None,'S_design_only':None})
        rows.append(row)
    eligible=[r for r in rows if r['fresh_candidate']]
    if not eligible: raise ValueError('no fresh midpoint')
    winner=max(eligible,key=lambda r:(r['S_design_only'],-r['z_a0']))
    selection={'schema':'WU088_R31AD_MIDPOINT_SELECTION_V1','rows':rows,
               'selected_z_a0':winner['z_a0'],'selected_time_ta':winner['z_a0']/velocity,
               'model_source_sha256':{'R31AD':EXPECTED['R31AD'],'R31Z':EXPECTED['R31Z']},
               'selection_rule_sha256':EXPECTED['rule'],'selection_criterion':'max S among fresh; exact tie -> lower z',
               'S_is_final_model_selection_score':False,'direct_midpoint_output_accessed_after_selection':False,
               'science_node_count':0}
    jwrite(out/'MIDPOINT_SELECTION.json',selection)
    prereg={'schema':'WU088_R31AD_NEXT_VALIDATION_PREREGISTRATION_V1',
            'selected_z_a0':winner['z_a0'],'selected_time_ta':winner['z_a0']/velocity,'radial_order':192,
            'required_outputs_only':['mixed_O_47x2','mixed_D_col_47x2','mixed_D_row_2x47','independent_mixed_dotO_47x2'],
            'frozen_models':{'R31AD_FIVE_NODE_UNIT_CELL_CUBIC_O_LINEAR_K':EXPECTED['R31AD'],
                             'R31Z_GLOBAL_QUINTIC_O_QUADRATIC_K':EXPECTED['R31Z']},
            'training_node_z_a0':[0,1,2,3,4], 'R31AD_independent_validation_points':[],
            'five_node_manifest_sha256':digest((out/'FIVE_NODE_INPUT_MANIFEST.json').read_bytes()),
            'selection_sha256':digest((out/'MIDPOINT_SELECTION.json').read_bytes()),
            'selection_rule_sha256':EXPECTED['rule'],
            'future_primary_metrics':['E_K','E_Dmax'], 'comparison_tolerance':1e-10,
            'future_verdicts':['PARETO_SUPPORTED_AT_SELECTED_MIDPOINT','GLOBAL_SUPPORTED_AT_SELECTED_MIDPOINT','TRADEOFF_UNRESOLVED'],
            'decision_rule':'Pareto dominance on both primary errors with prelocked 1e-10 tolerance; no weighted score',
            'execution_authorized':False,'science_node_count_this_handoff':0,
            'forbidden':['H','neutral47','ionic2','full49','trajectory','other_z','M3_reference','post_selection_model_retuning']}
    jwrite(out/'NEXT_VALIDATION_PREREGISTRATION.json',prereg)
    for key,path in bound.items():
        if digest(path.read_bytes()) != EXPECTED[key]: raise ValueError(f'{key} mutated')
    print(json.dumps({'selected_z_a0':winner['z_a0'],'S':winner['S_design_only'],
                      'preregistration_sha256':digest((out/'NEXT_VALIDATION_PREREGISTRATION.json').read_bytes()),
                      'replay':replay},indent=2))


if __name__ == '__main__':
    main()
