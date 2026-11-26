import numpy as np,json
from pathlib import Path
from scipy.integrate import solve_ivp
D=Path(__file__).resolve().parent
rows=[]
for J,B,A in [(1.,-3.,.3),(-.2,-3.,.3),(1e-25,-10.,.3),(0.,-1.,.5)]:
 d=np.sqrt(B*B+4*A*J);h=.1;z=-np.expm1(-d*h);u=2*J*z/(d*(2-z)-B*z)
 q=solve_ivp(lambda t,v:J+B*v-A*v*v,(0,h),[0.],rtol=1e-12,atol=max(abs(J)*1e-15,1e-40),method='DOP853')
 assert abs(q.y[0,-1]-u)<1e-10*max(abs(u),1e-40)
 rows.append(dict(J=J,B=B,A=A,delta=u,reference=q.y[0,-1]))
(D/'RICCATI.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
