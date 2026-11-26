import numpy as np,json,hashlib
from pathlib import Path
from scipy.integrate import solve_ivp
from scipy.sparse import diags
from scipy.optimize import brentq
from nonlinear import Kompaneets
D=Path(__file__).resolve().parent;P=D.parent/'r118c3c_spectral_exchange/table512_spectrum.csv';z=np.genfromtxt(P,names=True,delimiter=',')
rows=[]
for n in (64,128,256):
 o=Kompaneets(np.geomspace(1e-3,40,n+1))
 # Manufactured initially BE radiation, non-equilibrium with electron bath.
 N=o.equilibrium(1.,.2)
 for t in (.5,2.):
    y=.01;scale=np.maximum(N,1e-20);ref=solve_ivp(lambda y,v:o.rhs(v*scale,t)/scale,(0,y),N/scale,method='BDF',rtol=2e-10,atol=1e-12,jac_sparsity=diags([np.ones(n-1),np.ones(n),np.ones(n-1)],[-1,0,1]));assert ref.success
    q=ref.y[:,-1]*scale
    for k in (32,128,512):
      s=o.advance(N,t,y,k);err=np.sum(abs(s-q))/np.sum(abs(q-N));num=abs(s.sum()-N.sum())/N.sum();H=o.entropy(s,t)-o.entropy(N,t)
      assert num<1e-12 and H<=1e-12 and min(s)>=0
      row=dict(n=n,theta=t,steps=k,increment_relative=float(err),number_defect=float(num),entropy_change=H,energy_change=o.energy(s)-o.energy(N),reference_nfev=ref.nfev)
      rows.append(row);print(row,flush=True)
# actual signed FF shape (IR cutoff, add full Planck), conditional fixed theta=1
o=Kompaneets(np.geomspace(1e-5,50,257));fp=1/np.expm1(o.x);d=np.interp(np.log(o.x),np.log(z['x']),z['delta'])
assert max(abs(d/fp))<.01
N=o.c*(fp+d);N0=o.c*fp;y=.01
q=o.advance(N,1.,y,1024);q0=o.advance(N0,1.,y,1024)
actual=dict(scope='actual C3C distortion, manufactured y=.01, fixed Te=Tgamma',number_relative=float(abs(q.sum()-N.sum())/N.sum()),energy_distortion_initial=o.energy(N-N0),energy_distortion_final=o.energy(q-q0),max_fraction=float(max(abs(d/fp))))
# Closed fixed volume thermal cell with manufactured photon/gas ratio. Fix heat
# capacity C=2 dimensionless energy per theta, use conservative implicit root.
closed=[];o=Kompaneets(np.geomspace(.001,40,129));N=o.equilibrium(1.,.2)
for t0 in (.5,2.):
 def fun(t):
  q=o.advance(N,t,.01,512);return 2*(t-t0)+o.energy(q-N)
 t=brentq(fun,min(t0,1.),max(t0,1.),xtol=1e-12);q=o.advance(N,t,.01,512)
 closed.append(dict(theta_initial=t0,theta_final=t,radiation_energy=o.energy(q-N),gas_energy=2*(t-t0),residual=fun(t),number_relative=float(abs(q.sum()-N.sum())/N.sum())))
 assert abs(fun(t))<1e-10
out=dict(status='SCOPED_NONLINEAR_KOMPANEETS',rows=rows,actual=actual,closed=closed,source_sha=hashlib.sha256(P.read_bytes()).hexdigest(),scope='finite reflecting frequency domain, nonrelativistic fixed electron temperature or manufactured implicit thermal cell; not live cosmology')
(D/'RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print(actual,closed)
