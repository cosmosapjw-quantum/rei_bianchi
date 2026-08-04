"""Exact-zero-G3 primary H/He/thermal evolution for B2C1C."""
from __future__ import annotations
import math
from typing import Mapping
import jax
jax.config.update('jax_enable_x64',True)
import jax.numpy as jnp
import numpy as np
from monolithic_model_b2a import (
 C_LIGHT,EV_ERG,KB_ERG,MPC_CM,alpha_a_heiii,alpha_b_heiii,beta_heii,
 chemistry_rates,electron_density,gamma_species,lambda_heii,opacity_cMpc_inv,
 temperature,
)
from b2b_physical_model import physical_rhs_history
Array=jax.Array

def state_from_z7(z7:Array,p:Mapping[str,Array])->Mapping[str,Array]:
 n123=jnp.exp(z7[:3]); n=jnp.concatenate([n123,jnp.zeros(1,dtype=z7.dtype)])
 xh=jax.nn.sigmoid(z7[3]); he=jax.nn.softmax(jnp.array([0.,z7[4],z7[5]],dtype=z7.dtype)); u=jnp.exp(z7[6])
 pref=C_LIGHT*(1+p['z_cos'])**3/MPC_CM**3
 gamma=pref*jnp.sum(p['sigma_HI'][:3]*n123)
 return {'N':n,'xHII':xh,'xHeI':he[0],'xHeII':he[1],'xHeIII':he[2],'u':u,'GammaHI':gamma}

def z7_from_state(n123,xh,x2,x3,u):
 n123=np.asarray(n123,float); x1=1-x2-x3
 if np.any(n123<=0) or min(xh,1-xh,x1,x2,x3,u)<=0: raise ValueError('nonphysical state')
 return np.r_[np.log(n123),math.log(xh/(1-xh)),math.log(x2/x1),math.log(x3/x1),math.log(u)]

def z7_rhs(z7:Array,emissivity:Array,p:Mapping[str,Array])->Array:
 s=state_from_z7(z7,p); rhs=physical_rhs_history(s,emissivity,p)
 n=s['N'][:3]; xh=s['xHII']; x1,x2,x3=s['xHeI'],s['xHeII'],s['xHeIII']; dxh,dx2,dx3=rhs['x']; dx1=-dx2-dx3
 return jnp.concatenate([rhs['N'][:3]/n,jnp.array([dxh/(xh*(1-xh))]),jnp.array([dx2/x2-dx1/x1,dx3/x3-dx1/x1]),jnp.array([rhs['u']/s['u']])])

def physical_state(z7,p):
 s=state_from_z7(jnp.asarray(z7),p); gH,gHeI,gHeII,_=gamma_species(s,p)
 return {'N':np.asarray(s['N'],float),'xHII':float(s['xHII']),'xHeI':float(s['xHeI']),'xHeII':float(s['xHeII']),'xHeIII':float(s['xHeIII']),'u':float(s['u']),'T':float(temperature(s,p)),'ne':float(electron_density(s,p)),'GammaHI':float(gH),'GammaHeI':float(gHeI),'GammaHeII':float(gHeII)}

def heiii_rates(s,p):
 T=temperature(s,p); ne=electron_density(s,p); nH=p['nH_phys']; nHe=p['nHe_phys']
 nHI=nH*(1-s['xHII']); nHeI=nHe*s['xHeI']; nHeII=nHe*s['xHeII']
 opH=nHI*p['sigma_ots_H54']; opHeI=nHeI*p['sigma_ots_HeI54']; opHeII=nHeII*p['sigma_ots_HeII54']; total=opH+opHeI+opHeII+1e-300; y2a=opHeII/total
 aA=alpha_a_heiii(T); aB=alpha_b_heiii(T); aEff=aB+(1-y2a)*(aA-aB)
 coll=ne*beta_heii(T)*s['xHeII']; rec=ne*aEff*s['xHeIII']
 return {'T':T,'ne':ne,'y2a':y2a,'alphaA':aA,'alphaB':aB,'alphaEff':aEff,'coll_fraction_s-1':coll,'recomb_fraction_s-1':rec,'net_fraction_s-1':coll-rec,'unsupported_density_cm-3_s-1':nHe*rec,'collisional_density_cm-3_s-1':nHe*coll}

def thermal_components(s,p):
 T=temperature(s,p); ne=electron_density(s,p); gH,gHeI,gHeII,gHgroups=gamma_species(s,p)
 nH=p['nH_phys']; nHe=p['nHe_phys']; nHI=nH*(1-s['xHII']); nHII=nH*s['xHII']; nHeI=nHe*s['xHeI']; nHeII=nHe*s['xHeII']; nHeIII=nHe*s['xHeIII']
 pref=C_LIGHT*(1+p['z_cos'])**3/MPC_CM**3; gHeIgroups=pref*p['sigma_HeI']*s['N']; gHeIIgroups=pref*p['sigma_HeII']*s['N']
 heatH=EV_ERG*nHI*jnp.sum(gHgroups*p['excess_HI_eV']); heatHeI=EV_ERG*nHeI*jnp.sum(gHeIgroups*p['excess_HeI_eV']); heatHeII=EV_ERG*nHeII*jnp.sum(gHeIIgroups*p['excess_HeII_eV']); heat=heatH+heatHeI+heatHeII
 thresholdH=EV_ERG*13.598*nHI*gH; thresholdHeI=EV_ERG*24.587*nHeI*gHeI; thresholdHeII=EV_ERG*54.416*nHeII*gHeII
 llH=315614/T; llHeI=570670/T; llHeII=lambda_heii(T)
 recH=3.435e-30*T*llH**1.970/(1+(llH/2.250)**0.376)**3.720; recHeII=KB_ERG*T*(1.26e-14*llHeI**0.750); recHeIII=8*3.435e-30*T*llHeII**1.970/(1+(llHeII/2.250)**0.376)**3.720
 excH=7.5e-19*jnp.exp(-118348/T)/(1+jnp.sqrt(T/1e5)); excHeII=5.54e-17*T**-0.397*jnp.exp(-473638/T)/(1+jnp.sqrt(T/1e5)); ff=1.42e-27*jnp.sqrt(T)*(1.1+0.34*jnp.exp(-(5.5-jnp.log10(T))**2/3))
 from monolithic_model_b2a import beta_hi,beta_hei
 coolRec=ne*nHII*recH+ne*nHeII*recHeII+ne*nHeIII*recHeIII; coolExc=ne*nHI*excH+ne*nHeII*excHeII; coolIon=EV_ERG*(ne*nHI*13.598*beta_hi(T)+ne*nHeI*24.587*beta_hei(T)+ne*nHeII*54.416*beta_heii(T)); coolFF=ne*(nHII+nHeII+4*nHeIII)*ff; cool=coolRec+coolExc+coolIon+coolFF
 pressure=(nH+nHe+ne)*KB_ERG*T; expansion=3*p['Hubble']*pressure
 return {'photoheat':heat,'photoheat_H':heatH,'photoheat_HeI':heatHeI,'photoheat_HeII':heatHeII,'threshold_H':thresholdH,'threshold_HeI':thresholdHeI,'threshold_HeII':thresholdHeII,'recombination_cooling':coolRec,'excitation_cooling':coolExc,'collisional_ionization_cooling':coolIon,'free_free_cooling':coolFF,'cooling_total':cool,'expansion_work':expansion,'thermal_rhs':heat-cool-expansion}
