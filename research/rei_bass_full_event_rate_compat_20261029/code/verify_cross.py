"""Verify independent C++20 long-double source-only oracle against Decimal80 and exact SymPy witnesses."""
from decimal import Decimal
from pathlib import Path
import sys
p=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(p/'code'))
import event_rate_compat as m
rows={x.split()[0]:Decimal(x.split()[1]) for x in (p/'results/CPP_STDOUT.txt').read_text().splitlines() if x.strip()}
v=m.minimax_two_epochs();rank=m.rank_witness()
ref={"RATIO_FACTOR":Decimal(v['rmax_over_rmin']),
     "OPTIMAL_K":Decimal(v['optimal_static_ratio']),
     "MINIMAX_REL":Decimal(v['minimax_relative_error']),
     "ATTAINED_HIGH":Decimal(v['minimax_relative_error']),
     "ATTAINED_LOW":Decimal(v['minimax_relative_error']),
     "DETERMINANT3_E36":Decimal(str(rank['witness_det_scaled']))}
assert set(rows)==set(ref),(set(rows),set(ref))
for name in sorted(ref):
    if ref[name]:
        err=abs(rows[name]-ref[name])/abs(ref[name])
        assert err<Decimal('2e-15'),(name,str(err))
        print(f'{name} relative_discrepancy={err:.3E} PASS')
print('CPP_PYTHON_INDEPENDENT_ORACLE 6/6 PASS')
