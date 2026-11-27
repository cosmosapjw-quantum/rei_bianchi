"""Signed conditional Bianchi-I geometry tangent on actual native matter records.
All densities normalized by rho_crit,0 (energy density). u=ln a.
Closure: prescribed external STF forcing, induced total trace response=delta rho.
Not the full material Jacobian or a production tangent.
"""
import numpy as np,json
from pathlib import Path
from scipy.interpolate import PchipInterpolator
from scipy.integrate import solve_ivp
from scipy.constants import c,G,electron_volt
D=Path(__file__).resolve().parent;OL=.684908;H0=2.1842852410855023e-18;RHO0=3*c*c*H0*H0/(8*np.pi*G)
def stf(P):
 return np.stack([(P[...,0]-P[...,1])/np.sqrt(2),(-P[...,0]-P[...,1]+2*P[...,2])/np.sqrt(6),np.sqrt(2)*P[...,3],np.sqrt(2)*P[...,4],np.sqrt(2)*P[...,5]],axis=-1)
def run_one(p):
 h=np.genfromtxt(p/'history.csv',names=True,delimiter=',');m=np.genfromtxt(p/'matter.csv',names=True,delimiter=',');assert np.array_equal(h['a'],m['a'])
 t=np.log(h['a']/h['a'][0]);S=np.stack([h[f'S{i}'] for i in range(5)],axis=1);H=h['h'];rho=m['rho']
 P=np.stack([m[k] for k in ['Pxx','Pyy','Pzz','Pxy','Pxz','Pyz']],axis=1);pi=stf(P);tr=P[:,:3].sum(axis=1)
 C=np.stack([h[k] for k in ['corr_Pxx','corr_Pyy','corr_Pzz','corr_Pxy','corr_Pxz','corr_Pyz']],axis=1)
 fac=m['nh_m3']*electron_volt/RHO0;dPi=stf(C)*fac[:,None];dr_meas=h['corr_U']*fac
 # Actual matter trace and native constraint, no derivative-based reconstruction.
 gauss=1-(S*S).sum(axis=1)/6-(rho+OL)/H**2;assert max(abs(gauss-h['gauss']))<1e-12
 hp=H[0]**2;fscale=float(np.max(np.linalg.norm(dPi,axis=1))/hp);assert fscale>0
 V=np.c_[S,H,rho,tr,pi,dPi/(fscale*hp),dr_meas/(fscale*hp)]
 base=PchipInterpolator(t,V,axis=0)
 def unpack(u):
  a=base(u);return a[:5],a[5],a[6],a[7],a[8:13],a[13:18],a[18]
 def rhs(u,y,kind='free',amp=0.):
  s,H,rho,tr,pi,P,meas=unpack(u);v=y[:5];l=y[5];r=y[6]
  if kind=='projected':l=(H**2*s@v/3+hp*r)/(2*(rho+OL))
  if kind=='measured':r=meas
  q=s@s/3+(rho+tr-2*OL)/(2*H**2)
  if amp==0:
   dq=2*s@v/3+hp*r/H**2-(rho+tr-2*OL)*l/H**2
   dv=(q-2)*v+dq*s+3*(hp*P-2*pi*l)/H**2
   dr=-4*r-v@pi/hp-s@P
  else:
   # Stable exact nonlinear perturbation quotient with prescribed closure.
   z=np.expm1(-2*amp*l);d=np.exp(-2*amp*l)
   dq=(2*s@v+amp*v@v)/3+((rho+tr-2*OL)*z/amp+2*hp*r*d)/(2*H**2)
   dv=(q-2)*v+dq*(s+amp*v)+3*(pi*z/amp+hp*P*d)/H**2
   dr=-4*r-v@pi/hp-s@P-amp*v@P
  return np.r_[dv,-dq,0. if kind=='measured' else dr]
 def solve(kind,amp=0.,tol=1e-11,ref=2):
  z=solve_ivp(lambda u,y:rhs(u,y,kind,amp),(t[0],t[-1]),np.zeros(7),rtol=tol,atol=tol*1e-4,max_step=max(np.diff(t))/ref,t_eval=t,method='DOP853')
  assert z.success
  Y=z.y.T.copy()
  if kind=='projected':Y[:,5]=(H**2*np.sum(S*Y[:,:5],axis=1)/3+hp*Y[:,6])/(2*(rho+OL))
  if kind=='measured':Y[:,6]=dr_meas/(fscale*hp)
  return Y
 free=solve('free');proj=solve('projected');meas=solve('measured');fine=solve('free',tol=1e-12,ref=4)
 norm=lambda x:float(np.linalg.norm(x))
 def gres(Y):return -np.sum(S*Y[:,:5],axis=1)/3-hp*Y[:,6]/H**2+2*(rho+OL)*Y[:,5]/H**2
 amp=[]
 for a in [.01,.1,1.]:
  N=solve('free',a);amp.append(dict(amplitude=a,relative_shear=norm(N[-1,:5]-fine[-1,:5])/norm(fine[-1,:5]),relative_all=norm(N[-1]-fine[-1])/norm(fine[-1])))
 assert max(x['relative_all'] for x in amp)<1e-3
 # Compare induced total density closure vs directly observed signed DG stock.
 # At fixed geometry direct correction continuity would be R'=-4R-S:Pi.
 obs=PchipInterpolator(t,dr_meas/(fscale*hp));Rdot=obs.derivative()(t)
 source_def=Rdot+4*dr_meas/(fscale*hp)+np.sum(S*dPi/(fscale*hp),axis=1)
 ulp=norm(np.spacing(abs(S[-1])));row=dict(label=p.name,source_scale=fscale,terminal_shear=(fine[-1,:5]*fscale).tolist(),terminal_shear_norm=norm(fine[-1,:5])*fscale,terminal_dlnh=float(fine[-1,5]*fscale),terminal_drho=float(fine[-1,6]*fscale*hp),terminal_direct_drho=float(dr_meas[-1]),measured_shear_norm=norm(meas[-1,:5])*fscale,measured_dlnh=float(meas[-1,5]*fscale),projected_relative=norm(proj[-1]-fine[-1])/norm(fine[-1]),free_constraint_abs=float(max(abs(gres(fine)))*fscale),projected_constraint_abs=float(max(abs(gres(proj)))*fscale),measured_constraint_abs=float(max(abs(gres(meas)))*fscale),time_solver_relative=norm(free[-1]-fine[-1])/norm(fine[-1]),amplified=amp,shear_to_ulp=norm(fine[-1,:5])*fscale/ulp,measured_continuity_residual_relative=float(max(abs(source_def))/max(np.max(np.linalg.norm(dPi/(fscale*hp),axis=1)),1e-300)),native_gauss_reconstruction_abs=float(max(abs(gauss-h['gauss']))),scope='conditional radiation-like induced total trace, frozen background anisotropic stress and prescribed measured DG STF; not full H/He or Vlasov matter tangent. Actual source recorded; independent nonlinear quotient check.')
 np.savez_compressed(D/(p.name+'_tangent.npz'),u=t,S=S,h=H,rho=rho,traceP=tr,Pi=pi,dPi=dPi,dr_meas=dr_meas,free=fine*fscale,projected=proj*fscale,measured=meas*fscale)
 return row
def run():
 rows=[]
 for p in sorted(D.glob('fine_*')):
  if p.is_dir() and (p/'RETURN.txt').exists():
   row=run_one(p);rows.append(row);print(row,flush=True)
 assert rows
 (D/'TANGENT.json').write_text(json.dumps(dict(rows=rows),indent=2)+'\n')
if __name__=='__main__':run()
