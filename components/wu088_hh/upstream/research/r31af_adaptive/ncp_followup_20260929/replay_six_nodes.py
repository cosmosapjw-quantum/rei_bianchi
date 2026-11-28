"""Read-only R31AF six-node replay and z=3.5 prediction-only preregistration."""
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
    'engine': 'ab220248066580fc77af70c412251dbe3ed643a6fadc266cf5c25a7a3a6651a0',
    'adaptive_policy': '720b221a9e01ab7fc1bbd482b600ea785fed0b8c6b80b5834c576a75c2b70756',
    'global': '4ba03ba2adbdc9533f6472558b33a7edf86959bfc397e5fc8e3e90f8765ba034',
    'z05_od': '1505463b2329e9398b92077d51a9704c4b5f2c5d71288cf811571763a672f80a',
    'z05_jvp': '88b44ec142eef45ef7232f7fd050a0c5ca1773db416986a9a5857d60959b5fc3',
    'z1_od': '020dc2c2c580f7e7f8a2d5d322b771b4957fbcc1166ab4e2c363f5a9c3d06818',
    'z1_jvp': 'b6a9926052999c70cc6092c0d47001eff0716d2aefb6ff380edfa18558696819',
    'z3_od': '47f41c15aba4fc3eb4e9a6b6f08202067cf525503a87431035ee692990b553af',
    'z3_jvp': '9223dfea7956a58a70595ab25dda457be64b966ce247830e5c12a73d87515661',
    'parent_z05_comparison': 'f83ad382778509b7c249bda7a803a54c98fb47371bbeecabe15fa7b8ed09a2bb',
    'parent_selection': '2761664a75d7609c7ac0b1df4daf36a50e01d82a80b28a42885a22c5042a800b',
    'future_rule': '52b995b2f5516cf586cf1cbcdb681ec521f1b911a7538e3999a11d0f3bd62560',
}


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def npz(blob):
    with np.load(io.BytesIO(blob), allow_pickle=False) as f:
        return {key: f[key] for key in f.files}


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def n2(x):
    return float(norm(np.asarray(x, dtype=np.complex128), 2))


def write(path, obj):
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--snapshot', type=Path, required=True)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--outdir', type=Path, required=True)
    a = p.parse_args()
    repo, out = a.repo.resolve(), a.outdir.resolve()
    paths = {
        'snapshot': a.snapshot, 'archive': a.archive,
        'engine': repo/'research/r31ad_five_node/unit_cell_model.py',
        'adaptive_policy': repo/'research/r31af_adaptive/adaptive_policy.py',
        'global': repo/'research/r31z_source_bound/source_bound.py',
        'z05_od': repo/'research/r31ae_z05_gate/authorized_z05_20260929/OD_RAW/ASSEMBLED_OD.npz',
        'z05_jvp': repo/'research/r31ae_z05_gate/authorized_z05_20260929/JVP_RAW/ASSEMBLED.npz',
        'z1_od': repo/'research/r31ac_z1_authorization/authorized_z1_20260929/OD_RAW/ASSEMBLED_OD.npz',
        'z1_jvp': repo/'research/r31ac_z1_authorization/authorized_z1_20260929/JVP_RAW/ASSEMBLED.npz',
        'parent_z05_comparison': repo/'research/r31ae_z05_gate/authorized_z05_20260929/Z05_COMPARISON.json',
        'parent_selection': repo/'research/r31ad_five_node/ncp_followup_20260929/MIDPOINT_SELECTION.json',
        'future_rule': out/'FROZEN_Z35_DECISION_RULE.json',
    }
    blobs = {key: path.read_bytes() for key, path in paths.items()}
    for key, blob in blobs.items():
        if sha(blob) != EXPECTED[key]:
            raise ValueError(f'hash drift: {key}')
    fit = npz(blobs['snapshot'])
    z05_od,z05_jvp = npz(blobs['z05_od']),npz(blobs['z05_jvp'])
    z1_od,z1_jvp = npz(blobs['z1_od']),npz(blobs['z1_jvp'])
    with zipfile.ZipFile(a.archive) as z:
        od3_member = 'completion/mixed_h/od/B192_z3/ASSEMBLED_OD.npz'
        jvp3_member = 'completion/mixed_derivative/B192_z3/ASSEMBLED.npz'
        z3_od_blob,z3_jvp_blob = z.read(od3_member),z.read(jvp3_member)
        if sha(z3_od_blob)!=EXPECTED['z3_od'] or sha(z3_jvp_blob)!=EXPECTED['z3_jvp']:
            raise ValueError('z3 source drift')
        z35_members = [name for name in z.namelist() if name.startswith('completion/mixed_h/od/B192_z3.5/') or name.startswith('completion/mixed_derivative/B192_z3.5/')]
    runtime = Path('/root/WU088_R31AE_Z05_RUNTIME_20260929')
    if z35_members or (runtime/'completion/mixed_h/od/B192_z3.5').exists() or (runtime/'completion/mixed_derivative/B192_z3.5').exists():
        raise ValueError('existing direct z3.5 output would contaminate fresh validation')
    z3_od,z3_jvp = npz(z3_od_blob),npz(z3_jvp_blob)
    zvals = [0.,.5,1.,2.,3.,4.]
    roles = ['TRAINING','PRIOR_INDEPENDENT_VALIDATION_CONSUMED_AS_R31AF_TRAINING',
             'TRAINING','TRAINING','TRAINING','TRAINING']
    raw = [
        (fit['z0_od_O'],fit['z0_od_D_col'],fit['z0_od_D_row'],fit['z0_j_dotO']),
        (z05_od['O'],z05_od['D_col'],z05_od['D_row'],z05_jvp['dotO']),
        (z1_od['O'],z1_od['D_col'],z1_od['D_row'],z1_jvp['dotO']),
        (fit['direct_O'][:47,47:],fit['direct_D'][:47,47:],fit['direct_D'][47:,:47],fit['direct_dotO'][:47,47:]),
        (z3_od['O'],z3_od['D_col'],z3_od['D_row'],z3_jvp['dotO']),
        (fit['z4_od_O'],fit['z4_od_D_col'],fit['z4_od_D_row'],fit['z4_j_dotO']),
    ]
    sources = [
        {'path':str(a.snapshot),'objects':['z0_od_O','z0_od_D_col','z0_od_D_row','z0_j_dotO'],'sha256':EXPECTED['snapshot'],'bytes':len(blobs['snapshot'])},
        {'OD_path':str(paths['z05_od']),'OD_sha256':EXPECTED['z05_od'],'OD_bytes':len(blobs['z05_od']),'JVP_path':str(paths['z05_jvp']),'JVP_sha256':EXPECTED['z05_jvp'],'JVP_bytes':len(blobs['z05_jvp'])},
        {'OD_path':str(paths['z1_od']),'OD_sha256':EXPECTED['z1_od'],'OD_bytes':len(blobs['z1_od']),'JVP_path':str(paths['z1_jvp']),'JVP_sha256':EXPECTED['z1_jvp'],'JVP_bytes':len(blobs['z1_jvp'])},
        {'path':str(a.snapshot),'objects':['direct_O[:47,47:]','direct_D[:47,47:]','direct_D[47:,:47]','direct_dotO[:47,47:]'],'sha256':EXPECTED['snapshot'],'bytes':len(blobs['snapshot']),'upstream_member':'WU088_HH_R31S_NCP_20260928/evidence/z2/R31S_FULL49_z2.npz'},
        {'archive':str(a.archive),'OD_member':od3_member,'OD_sha256':EXPECTED['z3_od'],'OD_bytes':len(z3_od_blob),'JVP_member':jvp3_member,'JVP_sha256':EXPECTED['z3_jvp'],'JVP_bytes':len(z3_jvp_blob)},
        {'path':str(a.snapshot),'objects':['z4_od_O','z4_od_D_col','z4_od_D_row','z4_j_dotO'],'sha256':EXPECTED['snapshot'],'bytes':len(blobs['snapshot'])},
    ]
    v = float(fit['velocity'])
    manifest_rows=[]
    for idx,(O,Dc,Dr,dot) in enumerate(raw):
        if (O.shape,Dc.shape,Dr.shape,dot.shape)!=((47,2),(47,2),(2,47),(47,2)):
            raise ValueError(f'node {zvals[idx]} shape drift')
        row={'z_a0':zvals[idx],'time_ta':zvals[idx]/v,'role':roles[idx],'source':sources[idx],
             'fields':{'O':'47x2','D_col':'47x2','D_row':'2x47','independent_dotO':'47x2'},
             'raw_dtypes':{'O':str(O.dtype),'D_col':str(Dc.dtype),'D_row':str(Dr.dtype),'dotO':str(dot.dtype)},
             'raw_metric_identity_max_abs':float(np.max(np.abs(dot-Dc-Dr.conj().T))),
             'basis_order_phase_contract':'CP4 frozen B192 47 channel order: centre0 24 then centre1 excited23; ionic columns 2; phase_E and tau=z/velocity; independent dotO is analytic JVP in 1/t_a; producer lines pinned in R31Y PRODUCER_INTAKE.json'}
        if idx in (1,2,4):
            srcO = {1:z05_jvp,2:z1_jvp,4:z3_jvp}[idx]['O']
            row['OD_vs_JVP_O_raw_max_abs'] = float(np.max(np.abs(O-srcO)))
        manifest_rows.append(row)
    manifest={'schema':'WU088_R31AF_SIX_NODE_INPUT_MANIFEST_V1','nodes':manifest_rows,
              'R31AF_independent_validation_points':[],
              'comparison_dtype':'complex128; original mixed raw arrays preserved in source',
              'source_array_mutation':False,
              'upstream_provenance':'research/r31y_lowrank/ncp_followup_20260929/PRODUCER_INTAKE.json'}
    write(out/'SIX_NODE_INPUT_MANIFEST.json',manifest)
    engine = module(paths['engine'],'r31ad_engine_unchanged')
    policy = module(paths['adaptive_policy'],'r31af_policy_unchanged')
    global_model = module(paths['global'],'r31z_global_unchanged')
    values=[np.asarray(x[0],dtype=np.complex128) for x in raw]
    dcs=[np.asarray(x[1],dtype=np.complex128) for x in raw]
    drs=[np.asarray(x[2],dtype=np.complex128) for x in raw]
    dots=[np.asarray(x[3],dtype=np.complex128) for x in raw]
    ks=[(c-r.conj().T)/2 for c,r in zip(dcs,drs)]
    times=[z/v for z in zvals]
    maxima={'O':0.,'dotO':0.,'K':0.,'D_col':0.,'D_row':0.}
    for j,t in enumerate(times):
        O,dot,Dc,Dr,K,_=engine.piecewise_candidate(times,values,dots,ks,t)
        for key,err in [('O',O-values[j]),('dotO',dot-dots[j]),('K',K-ks[j]),('D_col',Dc-dcs[j]),('D_row',Dr-drs[j])]:
            maxima[key]=max(maxima[key],n2(err))
    continuity={'O':0.,'dotO':0.,'K':0.,'D_col':0.,'D_row':0.}
    for j in range(1,5):
        left_o,left_dot=engine.cubic_hermite(values[j-1],values[j],dots[j-1],dots[j],times[j]-times[j-1],1.)
        right_o,right_dot=engine.cubic_hermite(values[j],values[j+1],dots[j],dots[j+1],times[j+1]-times[j],0.)
        for key,err in [('O',left_o-right_o),('dotO',left_dot-right_dot),('K',ks[j]-ks[j]),
                        ('D_col',left_dot/2+ks[j]-right_dot/2-ks[j]),
                        ('D_row',(left_dot/2-ks[j]).conj().T-(right_dot/2-ks[j]).conj().T)]:
            continuity[key]=max(continuity[key],n2(err))
    metric=0.
    for t in np.linspace(times[0],times[-1],321):
        O,dot,Dc,Dr,K,_=engine.piecewise_candidate(times,values,dots,ks,float(t))
        metric=max(metric,n2(dot-Dc-Dr.conj().T))
    if max(maxima.values())>1e-12 or max(continuity.values())>1e-12 or metric>1e-12:
        raise ValueError('six-node algebraic replay failed')
    model_replay={'schema':'WU088_R31AF_SIX_NODE_MODEL_REPLAY_V1','engine_sha256':EXPECTED['engine'],
                  'cells_z_a0':[[0,.5],[.5,1],[1,2],[2,3],[3,4]],
                  'node_reproduction_max_2norm':maxima,'internal_node_continuity_max_2norm':continuity,
                  'dense_grid_points':321,'dense_grid_metric_identity_max_2norm':metric,
                  'source_array_mutation':False,'science_node_count':0,'predictive_validation_performed':False}
    write(out/'R31AF_MODEL_REPLAY.json',model_replay)
    # Reproduce the a posteriori indicator from the pre-refinement R31AD cell.
    old_indices=(0,2,3,4,5)
    old_times=[times[i] for i in old_indices]
    old_values=[values[i] for i in old_indices]
    old_dots=[dots[i] for i in old_indices]
    old_ks=[ks[i] for i in old_indices]
    old_o,_,_,_,old_k,_=engine.piecewise_candidate(old_times,old_values,old_dots,old_ks,times[1])
    EO=n2(old_o-values[1]); EK=n2(old_k-ks[1])
    prior=json.loads(blobs['parent_z05_comparison'])['R31AD_five_node']
    if not math.isclose(EO,prior['E_O'],rel_tol=0,abs_tol=1e-13) or not math.isclose(EK,prior['E_K_per_ta'],rel_tol=0,abs_tol=1e-13):
        raise ValueError('z0.5 parent direct indicator mismatch')
    bounds=policy.midpoint_lower_bounds(EO,EK,1/v,1.)
    indicator={'schema':'WU088_R31AF_Z05_APOSTERIORI_INDICATOR_V1','E_O':EO,'E_K_per_ta':EK,
               'cell_width_ta':1/v,'cell_width_a0':1.,'necessary_lower_bounds':bounds,
               'certified_source_error_enclosure':False,'interval_arithmetic':False,
               'direct_point_role':'PRIOR_INDEPENDENT_VALIDATION_CONSUMED_AS_R31AF_TRAINING'}
    write(out/'Z05_APOSTERIORI_INDICATOR.json',indicator)
    # z3.5 is unchanged by a refinement confined to [0,1].
    t35=3.5/v
    new=engine.piecewise_candidate(times,values,dots,ks,t35)[:5]
    previous=engine.piecewise_candidate(old_times,old_values,old_dots,old_ks,t35)[:5]
    identical={name:n2(new[i]-previous[i]) for i,name in enumerate(('O','dotO','Dcol','Drow','K'))}
    if max(identical.values())>1e-14:
        raise ValueError('right-cell prediction changed after left refinement')
    gO,gdot=global_model.quintic_hermite([values[i] for i in (0,3,5)],[dots[i] for i in (0,3,5)],times[-1],3.5/4)
    gK=global_model.quadratic_three_nodes([ks[i] for i in (0,3,5)],3.5/4)
    global_pred=(gO,gdot,gdot/2+gK,(gdot/2-gK).conj().T,gK)
    separation=engine.separation(global_pred,new)
    previous_table=json.loads(blobs['parent_selection'])['rows']
    row35=next(row for row in previous_table if row['z_a0']==3.5)
    for actual,expected in [('K',row35['DeltaK_model']),('Dmax',row35['DeltaDmax_model']),('T_like_primary',row35['S_design_only'])]:
        if not math.isclose(separation[actual],expected,rel_tol=0,abs_tol=1e-13):
            raise ValueError(f'pre-output selection table drift: {actual}')
    fresh=[row for row in previous_table if row['z_a0'] in (2.5,3.5) and row['fresh_candidate']]
    selected=max(fresh,key=lambda row:(row['S_design_only'],-row['z_a0']))
    if selected['z_a0']!=3.5:
        raise ValueError('z3.5 selection drift')
    prediction={'schema':'WU088_R31AF_Z35_PREDICTION_ONLY_SELECTION_V1',
                'z35_direct_output_accessed':False,'z35_absent_recovered_CP4_and_local_runtime':True,
                'unchanged_right_cell_prediction_max_2norm':identical,
                'remaining_fresh_candidate_rows':fresh,
                'selected_z_a0':3.5,'selected_time_ta':t35,
                'DeltaK_model':separation['K'],'DeltaDcol_model':separation['Dcol'],
                'DeltaDrow_model':separation['Drow'],'DeltaDmax_model':separation['Dmax'],
                'S_design_only':separation['T_like_primary'],
                'truth_independent_half_gaps':{'E_K':separation['K']/2,'E_Dmax':separation['Dmax']/2},
                'S_used_as_final_model_selection_score':False,'science_node_count':0}
    write(out/'Z35_PREDICTION_SELECTION.json',prediction)
    prereg={'schema':'WU088_R31AF_Z35_FROZEN_PREREGISTRATION_V1',
            'selected_z_a0':3.5,'selected_time_ta':t35,'radial_order':192,
            'required_outputs_only':['mixed_O_47x2','mixed_D_col_47x2','mixed_D_row_2x47','independent_mixed_dotO_47x2'],
            'training_node_z_a0':zvals,'R31AF_independent_validation_points':[],
            'frozen_source_sha256':{'R31AF_interpolation_engine':EXPECTED['engine'],
                                    'R31AF_adaptive_policy':EXPECTED['adaptive_policy'],
                                    'R31Z_global_model':EXPECTED['global']},
            'six_node_manifest_sha256':sha((out/'SIX_NODE_INPUT_MANIFEST.json').read_bytes()),
            'z35_prediction_selection_sha256':sha((out/'Z35_PREDICTION_SELECTION.json').read_bytes()),
            'future_decision_rule_sha256':EXPECTED['future_rule'],
            'parent_pre_output_selection_sha256':EXPECTED['parent_selection'],
            'future_primary_metrics':['E_K','E_Dmax'],'comparison_tolerance':1e-10,
            'future_verdicts':['PARETO_SUPPORTED_AT_Z35','GLOBAL_SUPPORTED_AT_Z35','TRADEOFF_UNRESOLVED'],
            'weighted_score_for_final_decision':False,'execution_authorized':False,
            'direct_z35_output_accessed':False,'science_node_count_this_handoff':0,
            'forbidden':['H','neutral47','ionic2','full49','trajectory','other_z','M3_reference','post_prereg_model_retuning']}
    write(out/'NEXT_VALIDATION_PREREGISTRATION.json',prereg)
    for key,path in paths.items():
        if sha(path.read_bytes())!=EXPECTED[key]:
            raise ValueError(f'source mutated: {key}')
    print(json.dumps({'replay':model_replay,'indicator':indicator,'prediction':prediction,
                      'preregistration_sha256':sha((out/'NEXT_VALIDATION_PREREGISTRATION.json').read_bytes())},indent=2))


if __name__ == '__main__':
    main()
