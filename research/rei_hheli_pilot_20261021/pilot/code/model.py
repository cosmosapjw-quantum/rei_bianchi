"""New isotope electron owner coupled to the unchanged HE32 LRS transport."""
import math
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import legvander
import atomic as at
from compact_transport import CompactTransport,source,unit_matter_pi,KAPPA_T,SQRT6,cosmology

class CoupledModel:
 def __init__(self,config):
  self.config=config;self.atomic=at.rates();sigma=config['Sigma_F0'];orientation=config.get('orientation',1)
  src=source(2.);q=sigma/math.sqrt(6-sigma*sigma);h2=src.href**2*(1+q*q)
  pref=src.omega_m*.1/src.aref**3
  cm=KAPPA_T*SQRT6*src.rhocrit_j_m3*pref*unit_matter_pi()/h2
  fr=src.h0**2*src.omega_r/(src.aref**4*src.href**2)
  pm=config['A_m']*cm;pr=config['A_r']*SQRT6*fr/(5*(1+q*q))
  self.transport=CompactTransport(sigma,pm,pr,ellmax=config['L'],orientation=orientation)
  self.offset=self.transport.size;self.size=self.offset+22
  self.nB_pref=cosmology()['Omega_b']*src.rhocrit_j_m3/(at.MU*at.C**2)
  self.axes=(orientation*sigma,pm,pr)
 def initial(self):return np.r_[self.transport.initial_state(),at.initial_fractions(),0.]
 def rhs(self,x,y):
  f=y[self.offset:self.offset+21];a=self.transport.source.aref*math.exp(x);nb=self.nB_pref/a**3;ne=nb*float(at.QY@f)
  td,geom=self.transport.rhs(x,y[:self.offset],ne*1e-6,with_geometry=True)
  h=geom[1];df,_,_,_=self.atomic.derivatives(f,ne*1e-6,1/a-1)
  return np.r_[td,df/h,6.6524587051e-25*at.C_CM*(ne*1e-6)/h]
 def diagnostics(self,x,y):
  a,h,s,pm,pg,pn,towers,m=self.transport.geometry(x,y[:self.offset]);f=y[self.offset:self.offset+21];nb=self.nB_pref/a**3;ne=nb*float(at.QY@f)
  df,pi,rr,(t,tx,uv_a)=self.atomic.derivatives(f,ne*1e-6,1/a-1)
  obs=self.transport.observables(x,y[:self.offset],ne*1e-6,float(y[-1]))
  heavy=nb*float(at.Y@f);npart=heavy+ne;se=nb*float(at.QY@df)
  qthermal=1.5*at.KB*npart*h*tx+1.5*at.KB*t*se+3*h*at.KB*t*npart
  qbinding=nb*float((at.Y*self.atomic.binding)@df);pphoto=0.
  for name,_,zc,ab in at.GROUPS:
   if ab==0:continue
   sl=at.SLICES[name]
   for q in range(zc):pphoto+=nb*at.Y[sl.start+q]*pi[sl.start+q]*self.atomic.mean_energy_ev[at.CHANNELS[(zc,q)]]*at.EV
  uth=1.5*at.KB*t*npart;ub=nb*float((at.Y*self.atomic.binding)@f);uuv=uv_a*self.atomic.uv_energy_integral*at.EV*1e6
  rad=(self.transport.omega_gamma*towers[0,0]+self.transport.omega_nu*towers[2,0])/a**4
  eps=self.transport.source.rhocrit_j_m3*(self.transport.dust_omega/a**3+self.transport.mass_pref*m.rho+rad)
  relative_baryon=float((at.MASS*at.Y)@f)-1
  obs.update(n_B_m3=nb,ne_m3=ne,heavy_m3=heavy,T_K=t,UV_A_cm3_eV=uv_a,U_thermal_J_m3=uth,U_binding_J_m3=ub,U_UV_J_m3=uuv,epsilon_background_J_m3=eps,test_fluid_energy_ratio=(uth+ub+uuv)/eps,S_e_m3_s=se,Q_thermal_required_J_m3_s=qthermal,Q_binding_J_m3_s=qbinding,Q_gas_required_J_m3_s=qthermal+qbinding,P_photo_J_m3_s=pphoto,bath_minus_escaped_requirement_J_m3_s=qthermal+qbinding-pphoto,baryon_relative_residual=relative_baryon,charge_electron_algebraic_residual=ne-nb*float(at.QY@f))
  h2=(self.transport.source.h0**2*(self.transport.dust_omega/a**3+self.transport.mass_pref*m.rho+rad+self.transport.source.omega_lambda)+s*s)
  obs['Friedmann_algebraic_relative_residual']=h2/h**2-1
  return obs
 def brightness_minimum(self,y):
  # Exactly257 angular nodes; sampled positivity, no continuous certificate.
  mu=np.linspace(-1,1,257);basis=legvander(mu,self.config['L'])[:,::2]*(4*np.arange(self.transport.n)+1)
  towers=np.asarray(y)[3:self.offset].reshape(4,self.transport.n,-1)
  return float(np.min(np.einsum('al,tle->tae',basis,towers)))
