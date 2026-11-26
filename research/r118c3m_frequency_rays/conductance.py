"""Physically normalized conditional dispersive momentum diffusion."""
import numpy as np,json,sys
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3j_live_spectral'))
from plasma import cutoff
sys.path.insert(0,str(D.parent/'r118c3l_directional_secondary'))
from bose_pair import pair
def run():
 h=np.genfromtxt(D.parent/'r118c3i_event_ledger/native/history.csv',names=True,delimiter=',');a=h['a'];g=cutoff(h['ne'],2.7255/a)
 # Physical normalization in x=q c/(kBT0), time in seconds.
 theta=8.617333262145e-5*h['T']/510998.9499961642
 rate=theta*h['ne']*1e6*299792458.*6.6524587051e-29
 out=[]
 for gap in [0.,.3,1.]:
  for n in [32,64,128]:
   edges=np.geomspace(.01,5.,n+1);x=np.sqrt(edges[:-1]*edges[1:]);c=np.diff(edges**3)/3
   E=np.hypot(x,gap);de=np.diff(E);q=np.exp(-de);mid=np.sqrt(x[:-1]*x[1:])
   for flag in [0,1]:
    speed2=mid**2/(mid**2+gap**2);G=mid**4/np.diff(x)*de/(-np.expm1(-de))*(speed2 if flag else 1.)
    f=1/np.expm1(E+.2);N=c*f*(1+.1*np.sin(3*x));N0=N.copy();Q=0.
    def free(N):
     f=N/c;return np.sum(c*(f*np.log(f)-(1+f)*np.log1p(f))+E*N)
    f0=free(N)
    for _ in range(8):
     for j in range(n-1):
      d=pair(N[j],N[j+1],c[j],c[j+1],q[j],.002*G[j]);N[j]+=d;N[j+1]-=d;Q-=de[j]*d
    row=dict(gap=gap,bins=n,vg2=bool(flag),number_res=float(abs(N.sum()-N0.sum())/N0.sum()),energy_res=float(abs(E@(N-N0)-Q)),free_change=float(free(N)-f0),min_stock=float(N.min()))
    assert row['number_res']<1e-13 and row['energy_res']<1e-12 and row['free_change']<0 and row['min_stock']>0
    out.append(row)
 o=dict(rows=out,gap_range=[float(g.min()),float(g.max())],rate_s_inv=[float(rate.min()),float(rate.max())],scope='conditional diffusion conductance D_x=theta ne sigmaT c x² times 1 or vg²/c², actual rate normalization; dimensionless order-unity gap tests not cosmological gaps; no microscopic plasma kernel')
 (D/'R7.json').write_text(json.dumps(o,indent=2)+'\n');print({k:v for k,v in o.items() if k!='rows'},'max number',max(x['number_res'] for x in out),'max energy',max(x['energy_res'] for x in out))
if __name__=='__main__':run()
