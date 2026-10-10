"""Selected native finite-difference photon columns; no old campaign replay."""
import argparse
import json
from pathlib import Path
import numpy as np
from run_native_history import load, Coupled

p = argparse.ArgumentParser()
p.add_argument('--n1', type=Path, required=True)
p.add_argument('--n2', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
n1 = load('jac_n1', a.n1/'provider.py')
n2 = load('jac_n2', a.n2/'characteristics.py')
native = n1.Native(a.n1/'native/target/release/rei_n1_native')
problem = Coupled(n1.HistoryProvider(0), native, n2, 32, 2)
v = problem.y0/problem.scales
J = problem.jac(0, v).toarray()
f = problem.rhs(0, v)
result = []
for col in [6, 12, 24, 36]:
    h = 1e-4
    vp = v.copy()
    vp[col] += h
    fd = (problem.rhs(0, vp)-f)/h
    error = np.linalg.norm(fd-J[:, col], np.inf)/max(np.linalg.norm(fd, np.inf), 1e-100)
    result.append({'column': col, 'relative_inf': float(error), 'pass': bool(error < 1e-5)})
native.close()
out = {'criterion_relative_inf': 1e-5, 'checks': result,
       'status': 'PASS' if all(x['pass'] for x in result) else 'FAIL'}
a.output.write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps(out))
raise SystemExit(0 if out['status'] == 'PASS' else 1)
