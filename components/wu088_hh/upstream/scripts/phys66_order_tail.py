"""Reproduce exact individual-order radial cutoff budgets; no solver execution."""
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from wu088_hh.phys66_order_tail import cutoff_bounds,json_safe,minimum_cutoff,F
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--source',default=str(root/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'))
p.add_argument('--out',default=str(root/'research/hh_phys66_20261018/r5/results/ORDER_BOUNDS.json'))
x=p.parse_args()
rows=[cutoff_bounds(x.source,64,t,3) for t in (39,43,49,55,65)]
result={'schema':'PHYS66_R5_RESULTS_V1','certificates':json_safe(rows),
        'display_only':[{ 'outer':int(r['outer']), 'bounds':[float(v) for v in r['order_cutoff_bounds']]} for r in rows],
        'absolute_budget_examples':{str(j):minimum_cutoff(x.source,j,F(1,10**(29+23*(j-1)))) for j in (1,2,3)},
        'total_numerical_error_certified':False,'HH_R10':'OFF'}
out=Path(x.out);out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['display_only'],indent=2))
