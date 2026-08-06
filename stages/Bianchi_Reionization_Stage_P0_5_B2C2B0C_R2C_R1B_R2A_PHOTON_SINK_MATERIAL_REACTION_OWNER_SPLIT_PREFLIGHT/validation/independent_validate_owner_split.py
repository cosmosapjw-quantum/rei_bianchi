#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd


def rel(a: float, b: float) -> float:
    return abs(a-b)/max(abs(b),1e-300)


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('--stage',type=Path,required=True); args=ap.parse_args()
    root=args.stage; data=root/'data'
    split=pd.read_csv(data/'time_resolved_owner_split.csv')
    audit=pd.read_csv(data/'owner_group_closure_audit.csv')
    cap=pd.read_csv(data/'capacity_refinement_matrix.csv')
    totals=pd.read_csv(data/'capacity_refinement_totals.csv')
    node=pd.read_csv(data/'midpoint_node_owner_disintegration_audit.csv')
    summary=json.loads((data/'owner_split_preflight_summary.json').read_text())

    regroup=[]
    for key,sub in split.groupby(['interval_index','node_index','group'],sort=True):
        k=float(sub['conditioned_component_kappa_cMpc_inv'].sum())
        j=float(sub['owner_absorption_rate_s-1_cMpc-3'].sum())
        kt=float(sub['authoritative_total_kappa_cMpc_inv'].iloc[0])
        jt=float(sub['authoritative_total_absorption_rate_s-1_cMpc-3'].iloc[0])
        regroup.append((rel(k,kt), rel(j,jt) if jt else abs(jt-j)))
    max_k=max(x[0] for x in regroup); max_j=max(x[1] for x in regroup)
    corrected=cap[cap['mode']=='OWNER_CORRECT']
    invalid=cap[(cap['mode']!='OWNER_CORRECT') & cap['reachable']]
    subgrid=split[split.component=='EFFECTIVE_HI_SUBGRID']

    q8=totals[(totals.refinement==8)&(totals.species_reservoir!='INVALID_HI')].set_index(['interval_index','species_reservoir'])['assigned_total_cMpc-3']
    refinement=[]
    for rec in totals[(totals.species_reservoir!='INVALID_HI')].to_dict(orient='records'):
        ref=float(q8.loc[(rec['interval_index'],rec['species_reservoir'])]); value=float(rec['assigned_total_cMpc-3'])
        refinement.append(rel(value,ref) if ref else abs(value))

    result={
      'classification':'INDEPENDENT_R1B_R2A_VALIDATION',
      'owner_group_cases':len(regroup),
      'max_recomputed_kappa_closure_residual':max_k,
      'max_recomputed_current_closure_residual':max_j,
      'owner_correct_capacity_failures':int((~corrected.feasible).sum()),
      'invalid_unsplit_reachable_failures':int((~invalid.feasible).sum()),
      'invalid_unsplit_reachable_rows':int(len(invalid)),
      'max_refinement_total_relative_residual':max(refinement),
      'subgrid_source_zero':bool((subgrid[['resolved_H_source_coefficient','resolved_He_source_coefficient','resolved_thermal_source_coefficient']]==0).all().all()),
      'node_negative_count':int(node.negative_allocation_count.sum()),
      'node_zero_support_violation_count':int(node.zero_support_nonzero_allocation_count.sum()),
      'max_node_sum_residual':float(node.allocation_sum_relative_residual.max()),
      'summary_verdict':summary['verdict'],
    }
    result['pass']=bool(
      max_k<1e-11 and max_j<1e-11 and result['owner_correct_capacity_failures']==0
      and result['invalid_unsplit_reachable_failures']==20
      and result['invalid_unsplit_reachable_rows']==20
      and result['max_refinement_total_relative_residual']<1e-12
      and result['subgrid_source_zero'] and result['node_negative_count']==0
      and result['node_zero_support_violation_count']==0 and result['max_node_sum_residual']<1e-11
    )
    out=root/'validation'/'independent_validation_results.json'
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
    if not result['pass']: raise SystemExit(2)
if __name__=='__main__': main()
