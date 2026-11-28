"""Generate source-locked finite-cutoff full-exterior analytic bounds."""
from pathlib import Path
from fractions import Fraction
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from wu088_hh.phys65_exterior_bounds import certificate
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,default=ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz')
p.add_argument('--max-ell',type=int,default=64)
p.add_argument('--orders',type=int,default=3)
p.add_argument('--outer',type=Fraction,default=Fraction(39))
p.add_argument('--out',type=Path,default=ROOT/'research/hh_phys65_20261018/r5/results/EXTERIOR_CERTIFICATE.json')
a=p.parse_args();d=certificate(a.source,a.max_ell,a.orders,a.outer)
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:d[k] for k in ['status','max_ell','orders','outer','gamma','numeric_display','total_error_certified']},indent=2))
