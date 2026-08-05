from __future__ import annotations
import argparse, importlib.util, json, sys
from pathlib import Path
import numpy as np


def load_module(path: Path):
    sys.path.insert(0,str(path.parent))
    spec=importlib.util.spec_from_file_location('b0a_canonical',path)
    mod=importlib.util.module_from_spec(spec); assert spec.loader
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--b0a-root',type=Path,required=True)
    ap.add_argument('--r1-root',type=Path,required=True)
    ap.add_argument('--b2c0-root',type=Path,required=True)
    ap.add_argument('--p04-root',type=Path,required=True)
    ap.add_argument('--scratch-output',type=Path,required=True)
    ap.add_argument('--output-npz',type=Path,required=True)
    ap.add_argument('--audit-json',type=Path,required=True)
    args=ap.parse_args()
    H=load_module(args.b0a_root/'src/hierarchical_two_scale_closure.py')
    original=H.node_opacity_and_allocation
    captured={}
    diagnostics={}
    def wrapped(*a,**kw):
        requested=bool(kw.get('return_detail',False))
        kw['return_detail']=True
        frame,diag,detail=original(*a,**kw)
        # positional layout fixed by canonical signature
        history_state=a[1]; group=a[8]; lane=a[9]
        if group in {'G1','G2a'}:
            key=f"z{history_state.z:.2f}_{lane}_{group}"
            captured[key+'_q_node']=np.asarray(detail['q_node'],dtype=np.float64)
            captured[key+'_group_kappa_node']=np.asarray(detail['group_kappa_node'],dtype=np.float64)
            captured[key+'_macro_index']=np.asarray(detail['macro_index'],dtype=np.int16)
            captured[key+'_micro_index']=np.asarray(detail['micro_index'],dtype=np.int16)
            diagnostics[key]=diag
        return frame,diag,(detail if requested else None)
    H.node_opacity_and_allocation=wrapped
    result=H.run_stage(args.r1_root,args.b2c0_root,args.p04_root,args.scratch_output)
    if len([k for k in captured if k.endswith('_q_node')]) != 30:
        raise RuntimeError(f"expected 30 q arrays, got {len([k for k in captured if k.endswith('_q_node')])}")
    args.output_npz.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(args.output_npz,**captured)
    oracle=np.load(args.b0a_root/'data/primary_node_allocation_z5p75.npz')
    checks={}
    for group in ['G1','G2a']:
        q=captured[f'z5.75_LOCAL_NEUTRAL_HAZARD_PRIMARY_{group}_q_node']
        kap=captured[f'z5.75_LOCAL_NEUTRAL_HAZARD_PRIMARY_{group}_group_kappa_node']
        qo=oracle[f'{group}_q_node']; ko=oracle[f'{group}_group_kappa_node']
        checks[group]={
          'q_max_abs':float(np.max(np.abs(q-qo))),
          'q_relative_l1':float(np.sum(np.abs(q-qo))/max(np.sum(np.abs(qo)),1e-300)),
          'kappa_max_relative':float(np.max(np.abs(kap-ko)/np.maximum(np.abs(ko),1e-300))),
          'q_sum_residual':float(abs(q.sum()-1.0)),
        }
    passed=all(v['q_relative_l1']<=1e-13 and v['kappa_max_relative']<=1e-13 and v['q_sum_residual']<=1e-14 for v in checks.values())
    audit={'status':'PASS' if passed else 'FAIL_CLOSED','operator':'B2C2B0A canonical node_opacity_and_allocation intercepted at return_detail','fixed_weights_reused':True,'pdf_regenerated_for_production':False,'physics_changed':False,'captured_q_arrays':30,'nodes_per_array':46080,'oracle_regression':checks,'canonical_stage_result_gates':result.get('gates',{}),'diagnostics':diagnostics}
    args.audit_json.write_text(json.dumps(audit,indent=2)+'\n')
    if not passed: raise RuntimeError('canonical oracle regression failed')

if __name__=='__main__': main()
