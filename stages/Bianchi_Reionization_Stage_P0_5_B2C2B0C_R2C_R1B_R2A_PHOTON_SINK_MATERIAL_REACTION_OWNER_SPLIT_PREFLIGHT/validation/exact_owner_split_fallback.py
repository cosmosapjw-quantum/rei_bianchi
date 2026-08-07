#!/usr/bin/env python3
from __future__ import annotations
from decimal import Decimal, getcontext
import argparse, json
from pathlib import Path
import pandas as pd

getcontext().prec=90

def D(x): return Decimal(str(x))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--stage',type=Path,required=True); a=ap.parse_args()
    d=pd.read_csv(a.stage/'data'/'time_resolved_owner_split.csv')
    max_k=Decimal(0); max_j=Decimal(0); cases=0
    for _,sub in d.groupby(['interval_index','node_index','group'],sort=True):
        kt=D(sub.iloc[0]['authoritative_total_kappa_cMpc_inv']); jt=D(sub.iloc[0]['authoritative_total_absorption_rate_s-1_cMpc-3'])
        raw=[D(x) for x in sub['raw_component_kappa_cMpc_inv']]
        support=sum(raw,Decimal(0))
        if support==0:
            parts=[Decimal(0)]*len(raw)
        else:
            parts=[kt*x/support for x in raw]
            nonzero=[i for i,x in enumerate(raw) if x>0]
            parts[nonzero[-1]] += kt-sum(parts,Decimal(0))
        if kt>0:
            currents=[jt*x/kt for x in parts]
        else:
            currents=[Decimal(0)]*len(parts)
        rk=abs(sum(parts,Decimal(0))-kt)/(abs(kt) if kt else Decimal(1))
        rj=abs(sum(currents,Decimal(0))-jt)/(abs(jt) if jt else Decimal(1))
        max_k=max(max_k,rk); max_j=max(max_j,rj); cases+=1
    result={'classification':'DECIMAL_90_OWNER_SPLIT_FALLBACK','cases':cases,'max_kappa_residual':str(max_k),'max_current_residual':str(max_j),'pass':max_k<Decimal('1e-70') and max_j<Decimal('1e-70')}
    out=a.stage/'validation'/'exact_fallback_results.json'; out.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
    if not result['pass']: raise SystemExit(2)
if __name__=='__main__': main()
