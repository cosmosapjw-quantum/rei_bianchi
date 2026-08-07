#!/usr/bin/env python3
"""Merge chunked R2B-R1 evidence and apply the predeclared gates."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
STAGE=HERE.parent


def rel(a: float,b: float,floor: float=1e-300)->float:
    return abs(float(a)-float(b))/max(abs(float(a)),abs(float(b)),floor)


def read_chunks(root: Path,name: str)->pd.DataFrame:
    paths=sorted((root/'chunks').glob(f'*/{name}'))
    frames=[]
    for p in paths:
        if p.stat().st_size > 1:
            try:
                frames.append(pd.read_csv(p))
            except pd.errors.EmptyDataError:
                pass
    return pd.concat(frames,ignore_index=True) if frames else pd.DataFrame()


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=STAGE/'data');args=ap.parse_args();out=args.output
    owner=read_chunks(out,'owner_law_time_matrix.csv')
    node=read_chunks(out,'node_allocation_audit.csv')
    snap=read_chunks(out,'snapshot_closure_audit.csv')
    pert=read_chunks(out,'state_sensitivity_audit.csv')
    tv=read_chunks(out,'subgrid_lane_tv_audit.csv')
    summaries=[json.loads(p.read_text()) for p in sorted((out/'chunks').glob('*/chunk_summary.json'))]
    covered=sum(int(x['forcing_rows']) for x in summaries)
    if covered!=85 or len(snap)!=85 or len(owner)!=1360 or len(node)!=1360:
        raise RuntimeError(f'incomplete chunk coverage: rows={covered}, snap={len(snap)}, owner={len(owner)}, node={len(node)}')
    owner.to_csv(out/'owner_law_time_matrix.csv',index=False)
    node.to_csv(out/'node_allocation_audit.csv',index=False)
    snap.to_csv(out/'snapshot_closure_audit.csv',index=False)
    pert.to_csv(out/'state_sensitivity_audit.csv',index=False)
    tv.to_csv(out/'subgrid_lane_tv_audit.csv',index=False)
    meta=json.loads((out/'initial_material_state_metadata.json').read_text())
    npz=np.load(out/'initial_material_state_z6.npz')
    h=npz['N_HI']+npz['N_HII']; he=npz['N_HeI']+npz['N_HeII']+npz['N_HeIII']
    initial_metrics={
      'H_nuclei_relative_residual':rel(math.fsum(map(float,h)),meta['global_H_nuclei_cMpc-3']),
      'He_nuclei_relative_residual':rel(math.fsum(map(float,he)),meta['global_He_nuclei_cMpc-3']),
      'xHII_relative_residual':rel(math.fsum(map(float,npz['N_HII']))/math.fsum(map(float,h)),meta['global_xHII']),
      'xHeI_relative_residual':rel(math.fsum(map(float,npz['N_HeI']))/math.fsum(map(float,he)),meta['global_xHeI']),
      'xHeII_relative_residual':rel(math.fsum(map(float,npz['N_HeII']))/math.fsum(map(float,he)),meta['global_xHeII']),
      'xHeIII_relative_residual':rel(math.fsum(map(float,npz['N_HeIII']))/math.fsum(map(float,he)),meta['global_xHeIII']),
      'U_relative_residual':rel(math.fsum(map(float,npz['U_resolved'])),meta['global_U_resolved_erg_cMpc-3']),
      'minimum_species':float(min(np.min(npz[k]) for k in ['N_HI','N_HII','N_HeI','N_HeII','N_HeIII'])),
      'minimum_temperature_K':float(np.min(npz['T_K'])),
      'thermal_normalization_factor':float(meta['thermal_normalization_factor']),
    }
    closure_cols=['H_nuclei_relative_residual','He_nuclei_relative_residual','xHII_relative_residual','xHeI_relative_residual','xHeII_relative_residual','xHeIII_relative_residual','U_relative_residual']
    max_snapshot=float(snap[closure_cols].to_numpy(float).max())
    max_kappa=max(float(x['max_owner_kappa_sum_relative_residual']) for x in summaries)
    max_current=max(float(x['max_owner_current_sum_relative_residual']) for x in summaries)
    max_node=max(float(x['max_node_allocation_sum_relative_residual']) for x in summaries)
    structural=sum(int(x['structural_zero_violations']) for x in summaries)
    negative=sum(int(x['negative_allocation_count']) for x in summaries)
    zero_support=sum(int(x['zero_support_nonzero_allocation_count']) for x in summaries)
    sensitivity=sum(int(x['state_sensitivity_failures']) for x in summaries)
    passed=(max(initial_metrics[k] for k in closure_cols)<=1e-11 and max_snapshot<=1e-11 and max_kappa<=1e-11 and max_current<=1e-11 and max_node<=1e-11 and structural==0 and negative==0 and zero_support==0 and sensitivity==0 and bool(pert['pass'].all()))
    results={
      'classification':'R2B_R1_CANONICAL_MATERIAL_STATE_OWNER_LAW_RESULTS',
      'stage':'P0.5-B2C2B0C-R2C-R1B-R2B-R1-CANONICAL-INITIAL-MATERIAL-STATE-AND-STATE-DERIVED-OWNER-LAW-LOCK',
      'verdict':'DURABLE_PASS_R2C_R1B_R2B_R1_CANONICAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK_R2B_R2_AUTHORIZED' if passed else 'DURABLE_FAIL_CLOSED_R2C_R1B_R2B_R1_MATERIAL_STATE_OR_OWNER_LAW_GATE',
      'R2C_R1B_R2B_R1_completed':bool(passed),'R2C_R1B_R2B_R2_authorized':bool(passed),
      'production_history_integrated':False,'production_node_chemistry_authorized':False,
      'node_count':46080,'forcing_rows':len(snap),'owner_rows':len(owner),'node_allocation_cases':len(node),'snapshot_cases':len(snap),'perturbation_cases':len(pert),'subgrid_tv_cases':len(tv),
      'initial_metrics':initial_metrics,'max_snapshot_closure_relative_residual':max_snapshot,
      'max_owner_kappa_sum_relative_residual':max_kappa,'max_owner_current_sum_relative_residual':max_current,'max_node_allocation_sum_relative_residual':max_node,
      'structural_zero_violations':structural,'negative_allocation_count':negative,'zero_support_nonzero_allocation_count':zero_support,'state_sensitivity_failures':sensitivity,
      'subgrid_TV_range':[float(tv.total_variation.min()),float(tv.total_variation.max())],
      'primary_subgrid_lane':'LOCAL_NEUTRAL_HAZARD_PRIMARY','auditor_lanes':['RECOMBINATION_WEIGHTED_AUDITOR','SCRIPT_SELF_SHIELDING_AUDITOR'],
      'post_hoc_lane_selection_used':False,'clipping_used':False,'per_node_fit_used':False,'claim_boundary':'INPUT_OPERATOR_LOCK_ONLY_NO_HISTORY_INTEGRATION',
    }
    (STAGE/'results.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
    print(json.dumps(results,indent=2,sort_keys=True)); return 0 if passed else 2
if __name__=='__main__': raise SystemExit(main())
