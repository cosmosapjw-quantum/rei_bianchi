"""Refine actual narrow patch and nonzero manufactured field, and test Bose Kompaneets interior."""
import numpy as np,json
from pathlib import Path
from scipy.interpolate import PchipInterpolator
from experiments import actual,evaluate
from jump import ray_grid,kernel,proposal
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
def isotropic_flux(x,theta,tr,f,r):
 # Angle-averaged jump measure (64-point quadrature), same symmetric
 # proposal and MH detailed balance, sum energy-space transfer exactly.
 y=np.log(x);dy=y[1]-y[0];mu,w=leggauss(64);w*=3/8*(1+mu*mu)
 P={}
 for m,ww in zip(mu,w):
  for j,p in proposal(y,np.sqrt(2*theta*(1-m))):
   if j:P[j]=P.get(j,0.)+ww*p
 out=np.zeros_like(x,dtype=np.longdouble);f=f.astype(np.longdouble);r=r.astype(np.longdouble);d=f-r
 for j,p in P.items():
  a=x[:-j];b=x[j:];dg=(b-a)/tr;rate=p*dy*np.minimum(a**3,b**3*np.exp(-dg))
  z=rate*(d[:-j]-d[j:]-np.expm1(dg)*(d[j:]*(1+r[:-j])+r[j:]*d[:-j]+d[:-j]*d[j:]))
  out[:-j]-=z;out[j:]+=z
 return out
def km():
 # analytic smooth distribution F=R+d, R=Planck at photon reference;
 # signed Kompaneets moment per unit optical depth (not y parameter).
 rows=[];tr=.7
 for theta in [1e-4,1e-5,1e-6]:
  for cells in [4,8]:
   dy=np.sqrt(theta)/cells;y=np.arange(-1.5,1.5+dy/2,dy);x=np.exp(y);r=1/np.expm1(x);d=.02*np.exp(-.5*(y/.4)**2);f=r+d
   o=isotropic_flux(x,theta,tr,f,r)/(x**3*dy)
   # ∂tau f = theta/x³ ∂y[x³ ∂y f + x⁴/tr f(1+f)]
   # full-reference difference; analytic derivatives
   ry=-x*r*(1+r);dy1=-y/.16*d;dy2=(y*y/.16**2-1/.16)*d
   z=d*(1+2*r)+d*d;zy=dy1*(1+2*r+2*d)+2*d*ry
   target=theta*(3*dy1+dy2+x/tr*(4*z+zy))
   mask=abs(y)<1.;rel=np.linalg.norm((o[mask]-target[mask]).astype(float))/np.linalg.norm(target[mask])
   rows.append(dict(theta=theta,cells_per_sqrt=cells,relative_L2=float(rel),finite_number_res=float(abs(np.sum(o*x**3*dy)))))
 return rows
def run():
 rows={};n,w=ray_grid(3);N=1024;x=np.exp(np.linspace(-3,1,N));f=1/np.expm1(x/.7);R=np.broadcast_to(f,(len(w),N));v=.02*(3*n[:,2,None]**2-1)/2*np.exp(-.5*(np.log(x)[None,:]/.6)**2)
 rows['manufactured_1024']=evaluate(x,n,w,4e-4,.7,R+v,R)
 X,delta,d,n,w,theta,tr,cap,energy=actual();interp=PchipInterpolator(np.log(X),delta,axis=1);N=1024;x=np.exp(np.linspace(-.005,.005,N));f=1/np.expm1(x);R=1/np.expm1(x[None,:]/d[:,None]);R*=f/(w@R);R=R.astype(np.longdouble);F=R+interp(np.log(x)).astype(np.longdouble)
 q=evaluate(x,n,w,theta,tr,F,R);q.update(energy_eV_H_per_tau=float(cap*energy*q['energy']),cells_per_sqrt=float(np.sqrt(theta)/np.log(x[1]/x[0])));rows['actual_patch_1024']=q
 out=dict(rows=rows,kompaneets=km(),scope='actual interpolated local patch and manufactured nonzero quadrupole; angle-integrated signed Bose Kompaneets interior check, not global live coupling')
 (D/'REFINEMENT.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run()
