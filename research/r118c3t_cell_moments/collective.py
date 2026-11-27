"""Angle-dependent finite-width longitudinal pole on cold transverse kinematics.
Density-only model, conditional Thomson angular weight, not a microscopic rate.
"""
import numpy as np,json,warnings
from scipy.integrate import quad,IntegrationWarning
from scipy.optimize import brentq
from scipy.constants import hbar,k,m_e,m_p,c,e,epsilon_0
from numpy.polynomial.legendre import leggauss
from pathlib import Path
D=Path(__file__).resolve().parent;delta=m_e/m_p;O0=np.sqrt(1+delta);alpha=3*(1+delta*delta)/(1+delta)
def integrals(x,theta,beta,gam,nangle,disp=True):
 mu,w=leggauss(nangle);w*=3/8*(1+mu*mu);ki=np.sqrt(x*x-1);rows={}
 for sign in [-1,1]:
  hi=x-1 if sign==-1 else 5.;a=np.arctan(-O0/gam);b=np.arctan((hi-O0)/gam);v=0.;err=0.;pole=0.;warn=0
  for m,ww in zip(mu,w):
   def kin(z):
    out=x+sign*z;kp=np.sqrt(max(out*out-1,0.));K2=theta*max(0.,ki*ki+kp*kp-2*ki*kp*m);return out,kp,K2
   def f(t):
    q=gam*np.tan(t);z=O0+q;out,kp,K2=kin(z);dp=alpha*K2 if disp else 0.;Om2=O0*O0+dp
    # (Omega^2-z^2)/gamma evaluated without cancellation around the pole.
    term=(dp/gam)*np.cos(t)-np.sin(t)*(2*O0+q)
    jac=2*Om2/(np.pi*(term*term+4*np.cos(t)**2*z*z))
    # emission transfers positive frequency to plasma; absorption negative.
    y=-sign*beta*z;db=y/(-np.expm1(-y)) if abs(y)>1e-30 else 1.
    return jac*K2/(1+delta)**2*out*kp/(x*x)*db
   with warnings.catch_warnings(record=True) as ws:
    warnings.simplefilter('always',IntegrationWarning);q,e0=quad(f,a,b,epsabs=1e-18,epsrel=1e-7,limit=250);warn+=len(ws)
   v+=ww*q;err+=ww*e0
   # Pole root and Jacobian far enough from threshold. Near threshold
   # multiple/endpoint roots may occur; report only isolated root test.
   if hi>O0+100*gam:
    def fn(z):return z-np.sqrt(O0**2+(alpha*kin(z)[2] if disp else 0.))
    lo=max(0,O0-1e-3);h0=min(hi,O0+1e-3)
    if fn(lo)*fn(h0)<0:
     z=brentq(fn,lo,h0,xtol=1e-14);out,kp,K2=kin(z);Om=np.sqrt(O0**2+(alpha*K2 if disp else 0.));dK=2*theta*sign*out*(kp-ki*m)/max(kp,1e-300);jp=abs(1-alpha*dK/(2*Om)) if disp else 1.
     y=-sign*beta*z;db=y/(-np.expm1(-y)) if abs(y)>1e-30 else 1.
     pole+=ww*.5*K2/(1+delta)**2*out*kp/(x*x)*db/jp
  rows['emission' if sign==-1 else 'absorption']=dict(value=float(v),quad_error=float(err),warnings=warn,isolated_pole=float(pole))
 return rows
def run():
 h=np.genfromtxt(D.parent/'r118c3i_event_ledger/native/history.csv',names=True,delimiter=',');r=json.loads((D.parent/'r118c3r_subcell_moments/TRANSVERSE.json').read_text());ix=[int(np.argmin(h['T'])),int(np.argmax(h['T']))];gams=[v/2 for v in r['nu_ei_over_wp']]
 rows=[]
 for ii,gam in zip(ix,gams):
  T=h['T'][ii];wp=np.sqrt(h['ne'][ii]*1e6*e*e/(epsilon_0*m_e));theta=k*T/(m_e*c*c);beta=hbar*wp/(k*T)
  for x in [1.5,1+O0-10*gam,1+O0,1+O0+10*gam,2.001,3.]:
   a=integrals(x,theta,beta,gam,24);b=integrals(x,theta,beta,gam,48);q=integrals(x,theta,beta,gam,48,False)
   rows.append(dict(T=float(T),theta=float(theta),gamma=gam,x=float(x),disp=b,fixed_pole=q,angle_relative={k:abs(a[k]['value']-b[k]['value'])/max(abs(b[k]['value']),1e-300) for k in b}))
   print(rows[-1],flush=True)
 o=dict(rows=rows,scope='conditional density-only finite-width oscillator with angle-dependent K² pole weight and leading thermal dispersion; assumed gamma bounds and limited absorption domain; no transverse microscopic vertex, no scattering rate')
 (D/'COLLECTIVE.json').write_text(json.dumps(o,indent=2)+'\n')
if __name__=='__main__':run()
