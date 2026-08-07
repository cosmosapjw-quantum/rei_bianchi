#!/usr/bin/env python3
"""Independent Decimal-90 replay of the R2B-R1 algebraic closure."""
from __future__ import annotations
import argparse, json
from decimal import Decimal, getcontext
from pathlib import Path
import pandas as pd

getcontext().prec = 90
HERE=Path(__file__).resolve().parent
STAGE=HERE.parent


def d(x: object)->Decimal:
    return Decimal(str(x))


def rel(a: Decimal,b: Decimal)->Decimal:
    return abs(a-b)/max(abs(a),abs(b),Decimal('1e-300'))


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,default=STAGE/'data');args=ap.parse_args()
    owner=pd.read_csv(args.data/'owner_law_time_matrix.csv',dtype=str)
    node=pd.read_csv(args.data/'node_allocation_audit.csv',dtype=str)
    max_k=Decimal(0); max_j=Decimal(0); max_n=Decimal(0)
    for _,sub in owner.groupby(['interval_index','node_index','group'],sort=False):
        ks=sum((d(x) for x in sub.conditioned_kappa_cMpc_inv),Decimal(0)); kt=d(sub.authoritative_kappa_cMpc_inv.iloc[0])
        js=sum((d(x) for x in sub.owner_current_s_inv_cMpc3),Decimal(0)); jt=d(sub.authoritative_current_s_inv_cMpc3.iloc[0])
        max_k=max(max_k,rel(ks,kt)); max_j=max(max_j,rel(js,jt))
    for r in node.itertuples(): max_n=max(max_n,d(r.allocation_sum_relative_residual))
    structural=owner[
        ((owner.component=='EFFECTIVE_HI_SUBGRID') & (~owner.group.isin(['G1','G2a']))) |
        ((owner.component=='EXPLICIT_HI_ATOMIC') & (~owner.group.isin(['G2b','G3']))) |
        ((owner.component=='EXPLICIT_HEI_ATOMIC') & (~owner.group.isin(['G2a','G2b','G3']))) |
        ((owner.component=='EXPLICIT_HEII_ATOMIC') & (owner.group!='G3'))
    ]
    structural_exact=all(d(x)==0 for x in structural.conditioned_kappa_cMpc_inv) and all(d(x)==0 for x in structural.owner_current_s_inv_cMpc3)
    result={
      'classification':'R2B_R1_DECIMAL_90_INDEPENDENT_VALIDATION',
      'precision_digits':90,
      'max_owner_kappa_sum_relative_residual':str(max_k),
      'max_owner_current_sum_relative_residual':str(max_j),
      'max_recorded_node_sum_relative_residual':str(max_n),
      'structural_zeros_exact':bool(structural_exact),
      'subgrid_resolved_source_vector':[0,0,0],
      'pass_at_1e-11':bool(max_k<=Decimal('1e-11') and max_j<=Decimal('1e-11') and max_n<=Decimal('1e-11') and structural_exact),
    }
    out=STAGE/'data'/'independent_exact_validation.json';out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True));return 0 if result['pass_at_1e-11'] else 2
if __name__=='__main__': raise SystemExit(main())
