"""Derived local gas observable derivatives from actual implicit-stage Jacobian and native EOS."""
from pathlib import Path
import numpy as np,json
from scipy.constants import c,G,electron_volt
D=Path(__file__).resolve().parent;J=json.loads((D/'STAGE_JACOBIAN.json').read_text());ld=np.longdouble
f=ld('.2454')/(4*(1-ld('.2454')));kb=ld('8.617333262145e-5');rho0=ld(3)*ld(c)**2*ld('2.1842852410855023e-18')**2/(8*ld(str(np.pi))*ld(G));e=ld(electron_volt)
cv=np.array([1,f,2*f,0],ld);bc=np.array([ld('13.598434599702'),f*ld('24.587389011'),f*(ld('24.587389011')+ld('54.41776')),1],ld)
rows=[]
for r in J['rows']:
 if r['status']!='COMPLETE':continue
 h=np.genfromtxt(D/(r['tag']+'_external.csv'),names=True,delimiter=',',dtype=ld);a=ld(str(r['a']));nh=h['nh_m3'][0]*(h['a'][0]/a)**3;z=np.array(r['state'],ld);X=np.array(r['inverse'],ld);w=z[-1];xe=cv@z;nt=1+f+xe;T=w/(ld('1.5')*kb*nt);fac=nh*e/rho0
 derivT=(-T/nt*cv);derivT[-1]=1/(ld('1.5')*kb*nt)
 deriv=np.stack([nh*cv,derivT,fac*bc,fac*ld(2)/3*np.array([0,0,0,1],ld)])@X
 def obs(z):
  w=z[-1];xe=cv@z;return np.array([nh*xe,w/(ld('1.5')*kb*(1+f+xe)),fac*(bc@z),fac*ld(2)/3*w])
 # Independent algebraic EOS directional difference along actual implicit local state response.
 check=[]
 for k in range(4):
  eps=ld('1e-9') if k<3 else ld('1e-10');v=X[:,k];num=(obs(z+eps*v)-obs(z-eps*v))/(2*eps)
  err=np.linalg.norm((num-deriv[:,k])/np.maximum(np.abs(deriv[:,k]),ld('1e-20')))
  check.append(float(err))
 row=dict(tag=r['tag'],stage=r['stage'],a=float(a),nH_m3=float(nh),xe=float(xe),T_K=float(T),jacobian_keys=['ne_m3','temperature_K','rho_gas_thermal_binding_over_rho0','pressure_gas_over_rho0'],J=deriv.astype(float).tolist(),eos_fd_relative_scaled=check,scope='analytic EOS derivative of actual fixed-prepared native gas substage response; excludes radiation stress, geometry and incoming source changes')
 rows.append(row);print(row,flush=True)
(D/'LOCAL_GAS_OBSERVABLE_JAC.json').write_text(json.dumps(dict(rows=rows,scope='gas-only conditional derivative of charge, EOS T, thermal+binding energy, isotropic pressure; fixed a and prepared radiation, native local implicit response'),indent=2)+'\n')

