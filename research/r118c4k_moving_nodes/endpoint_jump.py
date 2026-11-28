"""One-sided physical support-threshold derivative from continuum exponential reconstruction."""
import numpy as np,json,hashlib
from pathlib import Path
from rei import parse,bgeom,C,EV
D=Path(__file__).resolve().parent
_,cases,_=parse();r=cases[3,0,0.]
q,w=r['nodes'][:,:2].T;p=w/r['n'];m=p@q
logw=np.log(w/bgeom(q));kap=(p@((q-m)*(logw-p@logw)))/(p@(q-m)**2)
lo,hi=r['lo'],r['hi'];E=lo*r['r'];assert abs(E-13.60)<1e-12
width=hi-lo;density_at_lo=r['n']*kap/np.expm1(kap*width) if abs(kap*width)>1e-12 else r['n']/width
# Actual HI Verner parameters from native; fit switches at 13.60 eV.
x=E/.4298;y=abs(x);sig=5.475e4*1e-18*(x-1)**2*y**(2.963/2-5.5)*(1+np.sqrt(y/32.88))**(-2.963)
binding=float(q[0]*r['r']-r['nodes'][0,5]);ex=E-binding
assert r['scheme']==2 and np.all(r['nodes'][:,3:5]==0)
X=C*r['dt']*r['a'][0]*sig;phi=-np.expm1(-X)/X;psi=(1-phi)/X
A=X*psi;rate=C*r['nh']*sig*psi
below=np.r_[1.,lo,np.zeros(11)]
above=np.r_[phi,lo*phi,rate,0.,0.,rate*ex*EV,0.,0.,A,0.,0.,A*binding,A*ex]
pred=lo*density_at_lo*(below-above)
rows=[]
for h in [1e-3,1e-4]:
 up=cases[3,1,h];dn=cases[3,1,-h]
 jump=(up['out']+dn['out']-2*r['out'])/h
 active=np.abs(pred)>max(abs(pred))*1e-15
 # Each nonzero component normalized individually; no unphysical mixed-unit norm.
 rr=np.divide(abs(jump-pred),abs(pred),out=np.zeros_like(pred),where=pred!=0)
 rows.append(dict(h=h,nodes=[r['count'],up['count'],dn['count']],native_one_sided_gap=jump.tolist(),physical_jump=pred.tolist(),relative_by_component=rr.tolist(),number_balance=float((jump[0]+jump[8])/r['n']),survival_relative=float(rr[0]),HI_events_relative=float(rr[8]),binding_relative=float(rr[11]),excess_relative=float(rr[12])))
out=dict(source_sha256=hashlib.sha256((D/'1024_4_base.log').read_bytes()).hexdigest(),kappa=float(kap),threshold_eV=float(E),binding_eV=binding,density_per_H_per_eV=float(density_at_lo),sigma_cm2=float(sig),optical_depth=float(X),rows=rows,scope='Continuum exponential support endpoint one-sided boundary term at fixed mean, evaluated on one actual represented-cell probe. Native quadrature comparison only; no general production branch derivative implemented.')
(D/'ENDPOINT_JUMP.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
