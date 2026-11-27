"""Conditional cold-fluid transverse current response.
Fourier convention exp(i k.r-i omega t). All velocities normalized c=1
and frequencies by wp. Density-only exact only for vorticity-free mixing.
"""
import numpy as np,json
from pathlib import Path
from scipy.constants import k,m_e,c
D=Path(__file__).resolve().parent
def proj(v,k):
 return v-k*np.dot(k,v)/np.dot(k,k)
def run():
 rows=[];rng=np.random.default_rng(321);maxlong=0.;maxgeneral=0.;maxidentity=0.
 for _ in range(500):
  x=float(rng.uniform(1.01,5));xf=float(rng.uniform(1.01,5));ki=np.array([0.,0.,np.sqrt(x*x-1)]);kf=rng.normal(size=3);kf*=np.sqrt(xf*xf-1)/np.linalg.norm(kf);Q=kf-ki;Om=xf-x;vi=np.array([1.,0.,0.]);dv=Om*Q/(Q@Q)
  # e B_i/m = i k_i x vi; e B_fluct/m=0 for longitudinal electrostatic.
  B_i=1j*np.cross(ki,vi)
  v=(1j*(dv@ki)*vi+1j*(vi@Q)*dv+np.cross(dv,B_i))/(1j*xf)
  exact=kf*(dv@vi)/xf
  maxlong=max(maxlong,float(np.linalg.norm(proj(v,kf))/max(np.linalg.norm(v),1e-300)));maxidentity=max(maxidentity,float(np.linalg.norm(v-exact)/max(np.linalg.norm(exact),1e-300)))
  dv=rng.normal(size=3);Bf=rng.normal(size=3)+1j*rng.normal(size=3);C=Bf-1j*np.cross(Q,dv)
  v=(1j*(dv@ki)*vi+1j*(vi@Q)*dv+np.cross(dv,B_i)+np.cross(vi,Bf))/(1j*xf)
  expected=kf*(dv@vi)/xf-1j*np.cross(vi,C)/xf
  maxgeneral=max(maxgeneral,float(np.linalg.norm(v-expected)/max(np.linalg.norm(v),1e-300)))
 assert max(maxlong,maxidentity,maxgeneral)<1e-11
 # Static transverse eddy mode from Ampere; ratio at imposed
 # |dv|/vth = |dn|/n0, not an actual fluctuation spectrum.
 h=np.genfromtxt(D/'birth_1024_32ray/history.csv',names=True,delimiter=',');vth=np.sqrt(k*h['T']/(m_e*c*c));beta=float(vth[-1])
 for x in [1.000001,1.0001,1.01,1.1,2.,10.]:
  ki=np.array([0.,0.,np.sqrt(x*x-1)]);vi=np.array([0.,1.,0.])
  for ang in [.01,.1,1.,10.,90.]:
   a=np.deg2rad(ang);kf=np.linalg.norm(ki)*np.array([np.sin(a),0.,np.cos(a)]);Q=kf-ki;q=np.linalg.norm(Q)
   # dv in scattering plane perpendicular to Q: gives eddy vorticity
   # parallel pump polarization, so choose dv perpendicular to plane
   # to maximize a nonzero transverse response for this polarization.
   dv=beta*vi;C=-1j*(1+1/q**2)*np.cross(Q,dv)
   direct=proj(vi,kf);cur=proj(-1j*np.cross(vi,C)/x,kf)
   rows.append(dict(x=x,angle_deg=ang,Qc_over_wp=float(q),thermal_ratio_scale=float(beta*(q+1/q)/x),actual_selected_ratio=float(np.linalg.norm(cur)/np.linalg.norm(direct))))
 o=dict(max_longitudinal_transverse_residual=maxlong,max_longitudinal_identity=maxidentity,max_general_identity=maxgeneral,thermal_beta=beta,rows=rows,scope='nonrel pressureless electron-fluid mixing, electrostatic longitudinal perturbation yields transverse density-only exactly. Eddy C=B_e-iQ×dv independent; static Ampere conditional magnitude at chosen velocity/density amplitude. No current DSF, no physical rate or collective damping claim.')
 (D/'VERTEX.json').write_text(json.dumps(o,indent=2)+'\n');print({k:v for k,v in o.items() if k!='rows'},flush=True)
if __name__=='__main__':run()
