"""Emit PHYS58 R5 exact-rational certificate, source-locked."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from wu088_hh.phys58_screen_multipoles import make_certificate
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--source',default=str(ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'))
p.add_argument('--out',default=str(ROOT/'research/hh_phys58_20261016/r5/results/R5_CERTIFICATE.json'))
a=p.parse_args()
d=make_certificate(a.source)
target=Path(a.out)
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(d,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
for x in d['rows']:
 print('N=',x['legendre_degree'],'first-high-ell=',x['physical_high_ell_min'],'bound 2S=',float(__import__('fractions').Fraction(x['physical_2S_low_to_far_high_op_norm_upper_exact'])))
print('ORIGINAL_SHA',d['frozen_SHA256'])
