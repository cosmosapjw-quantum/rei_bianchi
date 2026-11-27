"""Nonstationary transverse OU covariance on actual C3U thermal trajectory."""
import numpy as np,json
from pathlib import Path
from scipy.constants import k,m_e,e,epsilon_0,hbar,c
from scipy.interpolate import PchipInterpolator
D=Path(__file__).resolve().parent;H0=2.1842852410855023e-18
def run():
 h=np.genfromtxt(D.parent/'r118c3u_positive_owner/birth_1024_32ray/history.csv',names=True,delimiter=',')
 u=np.log(h['a']/h['a'][0]);T=h['T'];ne=h['ne']*1e6;v=np.sqrt(k*T/m_e);wp=np.sqrt(ne*e**2/(epsilon_0*m_e))
 ln=np.log(v/wp/np.maximum(e**2/(4*np.pi*epsilon_0*k*T),hbar/(m_e*v)))
 nu=4*np.sqrt(2*np.pi)/3*ne*e**4*ln/((4*np.pi*epsilon_0)**2*np.sqrt(m_e)*(k*T)**1.5);H=H0*h['h'];sig=ne*T/(ne[0]*T[0])
 f=PchipInterpolator(u,np.c_[nu,wp,H,v,sig],axis=0);rows=[]
 for q0 in [1e-8,1e-6,1e-5,2e-5,5e-5,1e-4]:
  def solve(n):
   x=np.concatenate([np.linspace(a,b,n,endpoint=False) for a,b in zip(u[:-1],u[1:])]+[u[-1:]]);z=(x[1:]+x[:-1])/2;nn,ww,HH,vv,ss=f(z).T
   q=q0*np.exp(-z)*wp[0]/ww;L=1+1/q**2;g=nn/L/HH;eq=ss/L
   V=np.array([0.,1/(1+1/q0**2)]);hist=[V.copy()]
   for dt,G,E in zip(np.diff(x),g,eq):
    V=V+(-np.expm1(-2*G*dt))*(E-V);hist.append(V.copy())
   a,b,Hf,vf,sf=f(u[-1]);qf=q0*np.exp(-u[-1])*wp[0]/b;target=sf/(1+1/qf**2)
   return V,target,float(np.sum(g*np.diff(x))),float(max(q*ww*vv/(c*nn)))
  a,t0,g0,kn0=solve(1);b,t1,g1,kn1=solve(4);d,t2,g2,kn2=solve(8)
  err=float(np.max(abs(b-d))/max(t2,1e-300));assert err<1e-5
  rows.append(dict(q0=q0,integrated_relaxation=g2,terminal_equilibrium=t2,from_zero=float(d[0]),from_initial_equilibrium=float(d[1]),ratio_zero=float(d[0]/t2),ratio_initial_equilibrium=float(d[1]/t2),refinement_abs_over_equilibrium=err,max_knudsen=kn2,fluid_domain_all=bool(kn2<=.1)))
 out=dict(rows=rows,scope='conditional nonautonomous Markov OU j equation, q physical redshifts with a, sigma0² normalized ne*T, finite z20->19.8 history and two initial covariance conditions; no complete ion kinetics/FDT or scattering rate')
 (D/'OU_EVOLVING.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run()
