"""Independent finite LP of six SIG points plus 330, not using envelope theorem."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal
import json,sys
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from sig_da_bridge import source_rows,joint_interval
sig=source_rows(ROOT/'source/M0475.x4')
ang=json.loads((ROOT/'evidence/PR105_ANGULAR_BOUNDS.json').read_text())

def run(Lkey,kappa,K=F(19,800)):
    I=ang[Lkey]
    energies=[float(r.energy_mev) for r in sig]+[330.0]
    bounds=[(float(r.lo),float(r.hi)) for r in sig]+[(float(Decimal(I['lo'])/kappa),float(Decimal(I['hi'])/kappa))]
    A=[];b=[]
    for i,e in enumerate(energies):
        for j,f in enumerate(energies):
            if i==j:continue
            row=[0.0]*len(energies);row[i]=1.0;row[j]=-1.0
            A.append(row);b.append(float(K)*abs(e-f))
    out=[]
    for sign in [1,-1]:
        c=[0.0]*len(energies);c[-1]=sign
        sol=linprog(c,A_ub=A,b_ub=b,bounds=bounds,method='highs')
        out.append({'success':bool(sol.success),'sigma330':float(sol.x[-1]) if sol.success else None,'message':sol.message})
    direct=joint_interval(sig,K,I['lo'],I['hi'],kappa)
    return {'L':Lkey,'kappa':kappa,'LP':out,'formula':direct}

if __name__=='__main__':
    result=[run(L,k) for L in ('1/700','1/200','1/100') for k in (1,2)]
    for x in result:
        print(x['L'],x['kappa'],x['LP'][0]['sigma330'],x['LP'][1]['sigma330'],x['formula']['sigma330_lower_nb'],x['formula']['sigma330_upper_nb'])
        assert x['LP'][0]['success']==x['formula']['compatible']
        assert x['LP'][1]['success']==x['formula']['compatible']
        if x['formula']['compatible']:
            assert abs(x['LP'][0]['sigma330']-float(x['formula']['sigma330_lower_nb']))<1e-8
            assert abs(x['LP'][1]['sigma330']-float(x['formula']['sigma330_upper_nb']))<1e-8
    (ROOT/'evidence/INDEPENDENT_LP.json').write_text(json.dumps(result,indent=2,default=str)+'\n')
