#!/usr/bin/env python3
"""Reproduce PHYS55 source-locked exact-rational certificate + finite witness."""
from pathlib import Path
import argparse
import json
from wu088_hh.phys55_hybrid_outgoing import (
    collar_certificate, central_impedance, fd_screened_collar_hybrid,
    ORIGINAL_SHA,
)
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--source',default=str(ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'))
parser.add_argument('--out',default=str(ROOT/'research/hh_phys55_20261016/results/PHYS55_HYBRID.json'))
args=parser.parse_args()
proof=collar_certificate(args.source)
rows=[central_impedance(ell,27,dps=80) for ell in (21,22,28,29,40,64,128,256)]
grids=[fd_screened_collar_hybrid(elements=n,ells=(21,22,23),m=0,nodes=96) for n in (20,40,64)]
result={'proof':proof,'central_finite_samples_NONCERTIFYING':rows,
        'physical_screened_collar_central_exterior_FEM_NONCERTIFYING':grids,
        'parent_head':'9a3054487db04feea99ff7d5714398043e15425d',
        'original_source_SHA256':ORIGINAL_SHA,
        'scientific_admission':'RIGOROUS_HYBRID_OPERATOR_INVERTIBILITY_ONLY',
        'NCP':'NOT_RUN_SANDBOX_ONLY','full_original_repo_tests':'NOT_RUN',
        'native_subagents':'NOT_RUN_NO_NATIVE_TOOL',
        'HH_R10':'OFF'}
p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print('proof cD',proof['cD_certified_fraction'],'central samples',len(rows),'FEM grids',len(grids))
for x in rows:print('ell=',x['ell'],'normalized=-ReZ/(ell+1)',x['weighted_negative_real_ratio'],'log10j=',x['log10_Im_Z'])
for x in grids:print('FEM n=',x['elements'],'collar=',x['min_eigen_weighted_collar'],'hybrid_min_sv=',x['min_singular_weighted_hybrid'])
