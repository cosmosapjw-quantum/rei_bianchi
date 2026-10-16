"""Independent Radau and DOP853 solvers; shared unchanged native point RHS.
No independent atomic coefficient derivation is claimed by this comparison.
"""
import csv,json,subprocess,sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
binary=Path(sys.argv[1]);out=Path(sys.argv[2])
initial=np.loadtxt(out/'oracle_native_16.csv',delimiter=',',skiprows=1)[0,1:]
def solve(method):
    p=subprocess.Popen([str(binary),'rhs'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    calls=0
    def rhs(t,y):
        nonlocal calls
        calls+=1
        p.stdin.write(' '.join(format(v,'.17e') for v in y)+'\n');p.stdin.flush()
        line=p.stdout.readline()
        if not line:raise RuntimeError(p.stderr.read())
        return np.fromstring(line,sep=' ')
    r=solve_ivp(rhs,(0.,1e11),initial,method=method,rtol=2e-11,atol=np.array([1e-14]*3+[1e-13]+[1e-15]*3),dense_output=True)
    p.stdin.close();p.wait(timeout=20)
    assert r.success and p.returncode==0,(r.message,p.stderr.read())
    return r,calls
radau,rc=solve('Radau');dop,dc=solve('DOP853')
rows=[]
for n in [16,32,64,128]:
    raw=np.loadtxt(out/f'oracle_native_{n}.csv',delimiter=',',skiprows=1)
    ref=radau.sol(raw[:,0]).T
    err=np.max(np.abs(raw[:,1:]-ref),axis=0)
    rows.append(dict(steps=n,max_abs_error=err.tolist(),endpoint=raw[-1,1:].tolist()))
summary=dict(scope='independent solvers shared native continuous RHS; constant geometry no source',variables=['xHII','xHeII','xHeIII','w_eV_H','N20','N40','N80'],radau_calls=rc,dop853_calls=dc,independent_solver_endpoint_abs=np.abs(radau.y[:,-1]-dop.y[:,-1]).tolist(),native_refinement=rows)
(out/'independent_solver.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
