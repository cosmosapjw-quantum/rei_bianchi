import numpy as np,json
from scipy.integrate import quad
from pathlib import Path
D=Path(__file__).resolve().parent
def run():
 rng=np.random.default_rng(91);err=0.
 for _ in range(200):
  x0,xm,d,qc,m,c,w=rng.uniform(.1,2,7);c*=.01
  direct=w*(m*(xm/d-qc)+c/d)
  M=m;Vx=m*(xm-x0)+c;common=w*((x0/d-qc)*M+Vx/d)
  err=max(err,abs(direct-common))
 assert err<1e-14
 rows=[]
 for Q in [1e-5,.001,.1,1,10]:
  L=1+1/Q**2
  # scaled frequency y=L omega/nu; exact normalized variance 1/L
  v,e=quad(lambda y:1/(np.pi*(1+y*y))/L,-np.inf,np.inf,epsabs=1e-14)
  rows.append(dict(Q=Q,variance=v,expected=1/L,abs_error=abs(v-1/L)))
 out=dict(common_bin_abs=err,OU_rows=rows,scope='algebraic common-bin centered moment identity; conditional inertial Langevin variance only')
 (D/'R7.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
