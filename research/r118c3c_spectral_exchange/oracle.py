"""Independent direct spectral relaxation and closed gas/radiation cell tests."""
import json,hashlib
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.integrate import simpson
from scipy.optimize import brentq
D=Path(__file__).resolve().parent;P=D.parent/'r118c3b_ff_balance/gauntff.dat'
r=np.array([list(map(float,l.split('#')[0].split())) for l in P.read_text().splitlines() if len(l.split('#')[0].split())==81][:146])
interp=RegularGridInterpolator((-16+.2*np.arange(146),-6+.2*np.arange(81)),r)
kb=8.617333262145e-5
def g(u,t,f):
 a=np.log10(u);b=np.log10(13.605693122994/(kb*t))
 return (1-f)*interp(np.c_[a,np.full_like(a,b)])+f*interp(np.c_[a,np.full_like(a,b+np.log10(4.))])
X=np.geomspace(1e-10,60,8193)
def gnorm(t,f):return simpson(g(X,t,f)*np.exp(-X)*X,x=np.log(X))
def phase(x,dl,bb):return bb*15/np.pi**4*x**4*dl
def pl(x):
 with np.errstate(over='ignore'):return 1/np.expm1(x)
def step(x,dl,d,t,tc,f,b,bb,absolute=False):
 v=tc/t*x;z=gnorm(t,f);ratio=1.4255566872911698e-27*z/(1.43e-27*(1.1+.34*np.exp(-(5.5-np.log10(t))**2/3)))
 B=b*(ratio if absolute else 1.)
 amp=B*v*g(v,t,f)*dl/z;P=phase(x,dl,bb);tau=amp*(-np.expm1(-v))/P
 eq=pl(v)-pl(x);a=-np.expm1(-tau)
 # Independent affine expression using exp(-tau) times existing signed perturbation.
 dn=np.where(tau<1e-3,d+(eq-d)*a,d*np.exp(-tau)+eq*a)
 assert min(pl(x)+dn)>=0
 return dn,float(P@(dn-d)),float(np.sum(amp*np.exp(-v))),float(np.sum(P*tau*pl(x))),float(max(tau))
def run(name,stages,n,absolute=False):
 native=np.genfromtxt(D/(name+'_spectrum.csv'),names=True,delimiter=',');x=native['x'];dl=np.log(60/1e-10)/n
 d=np.zeros(n);net=0.;work=0.;thin=0.
 for row in np.genfromtxt(D/(stages+'_stages.csv'),names=True,delimiter=','):
  a,t,tc,f,b,bb0,bbmid,bb1=[float(row[k]) for k in row.dtype.names]
  old=phase(x,dl,bb0)@d;d,v,em,ab,tau=step(x,dl,d,t,tc,f,b,bbmid,absolute)
  new=phase(x,dl,bb1)@d;work+=old+v-new;net+=v;thin+=em-ab
 U=phase(x,dl,bb1)@d;native_hist=np.genfromtxt(D/(name+'.csv'),names=True,delimiter=',')
 err=np.sum(abs((d-native['delta'])*phase(x,dl,bb1)))/np.sum(abs(d*phase(x,dl,bb1)))
 out=dict(case=name,net=net,thin=thin,U=float(U),work=float(work),relative_net=float(abs(net/native_hist['net'][-1]-1)),energy_weighted_spectrum_relative=float(err),ledger=float(abs(U+work-net)),max_tau=tau)
 print(out,flush=True);return out
rows=[run('table512','table',512),run('late512','late_table',512),run('table_abs','table',512,True)]
# Isolated, fixed composition and volume thermal cell. Manufactured B_ref
# gives a resolvable exchange; no cosmological claim. Solve gas temperature
# implicitly with the exact exponential spectrum frozen at T_new.
x=np.geomspace(1e-10,60,1025);dl=np.log(60/1e-10)/1024;x=np.sqrt(x[:-1]*x[1:])
bb=3e4;tc=50.;frac=.2;cv=1.5*(1+.245/(4*(1-.245))+.001)*kb;closed=[]
for t0 in (10.,50.,100.):
 b0=1e-4;z0=gnorm(t0,frac)
 def at(t):return step(x,dl,np.zeros(len(x)),t,tc,frac,b0*np.sqrt(t/t0)*gnorm(t,frac)/z0,bb)
 def residual(t):return cv*(t-t0)+at(t)[1]
 tn=t0 if t0==tc else brentq(residual,min(t0,tc),max(t0,tc),xtol=1e-11)
 d,v,em,ab,tau=at(tn);defect=cv*(tn-t0)+v
 assert abs(defect)<1e-12 and min(t0,tc)<=tn<=max(t0,tc)
 row=dict(T0=t0,T_end=tn,gas_energy_change=cv*(tn-t0),radiation_net=v,energy_residual=defect,max_tau=tau,scope='manufactured closed fixed composition thermal-cell implicit step, not live reionization')
 closed.append(row);print(row,flush=True)
out=dict(status='SCOPED_SPECTRAL_AND_CLOSED_CELL_ORACLE',rows=rows,closed=closed,gaunt_sha=hashlib.sha256(P.read_bytes()).hexdigest())
(D/'ORACLE.json').write_text(json.dumps(out,indent=2)+'\n')
