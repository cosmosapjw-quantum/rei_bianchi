"""Finite analytic/algebraic controls; no scientific IVP."""
from decimal import Decimal,localcontext
import json,math,time
from pathlib import Path
import numpy as np
import atomic as a
from model import CoupledModel

def run():
 start=time.process_time();r64=a.AtomicRates(64);r128=a.AtomicRates(128);rows=[]
 for key in r64.photo:
  x=r64.photo_integrals[key];y=r128.photo_integrals[key];err=abs(x-y)/abs(y) if y else 0.
  xe=r64.photo_energy_integrals[key];ye=r128.photo_energy_integrals[key];energyerr=abs(xe-ye)/abs(ye) if ye else 0.
  assert err<=2e-8 and energyerr<=2e-8
  rows.append({'channel':key,'spectral_relative_64_128':err,'energy_integral_relative_64_128':energyerr,'photo_integral64_cm2_eV':x,'zero_for_prescribed_support':x==0})
 rrmax=0.
 for t in (100.,1000.,10000.):
  rates=r64.alpha(t)
  for i,name in enumerate(('HI','HeI','HeII','LiI','LiII','LiIII')):
   with localcontext() as c:
    c.prec=50;aa,b,t0,t1=map(lambda x:Decimal(str(x)),r64.rr[name]);tt=Decimal(str(t));u=(tt/t0).sqrt();v=(tt/t1).sqrt()
    independent=(aa.ln()-u.ln()-(1-b)*(1+u).ln()-(1+b)*(1+v).ln()).exp()
   err=abs(rates[i]/float(independent)-1);assert err<2e-14;rrmax=max(rrmax,err)
 beta,alpha,_,_,_=r64.coefficients(5.);gens=[]
 for z in (1,2,3):
  g=r64.generator(z,beta,alpha,1.);off=g.copy();np.fill_diagonal(off,0.);assert np.all(off>=0);assert np.max(abs(g.sum(axis=0)))<1e-26;gens.append({'Z':z,'column_sum_max':float(np.max(abs(g.sum(axis=0))))})
 li=np.array([.1,.2,.3,.4]);g=r64.generator(3,np.zeros(6),alpha,1.);d=g@li
 assert d[3]<0 and abs(d[3]+alpha[5]*li[3])<1e-26
 expected=np.array([alpha[3]*li[1],alpha[4]*li[2]-alpha[3]*li[1],alpha[5]*li[3]-alpha[4]*li[2],-alpha[5]*li[3]])
 np.testing.assert_allclose(d,expected,rtol=0,atol=1e-26)
 f=a.initial_fractions();assert abs((a.MASS*a.Y)@f-1)<3e-16;assert f[a.SLICES['Li6']][1]==1;assert np.all(f[a.SLICES['n']]==0) and np.all(f[a.SLICES['T']]==0)
 model=CoupledModel({'Sigma_F0':.6,'A_m':1.6,'A_r':-.8,'orientation':1,'L':16});y=model.initial();dy=model.rhs(0.,y);obs=model.diagnostics(0.,y)
 np.testing.assert_allclose([obs['signed_Sigma'],obs['P_m'],obs['P_r']],model.axes,rtol=0,atol=2e-10)
 assert model.transport.size==39 and model.size==61 and np.isfinite(dy).all();assert np.all(dy[model.offset+a.SLICES['T'].start:model.offset+a.SLICES['T'].stop]==0)
 report={'status':'PASS_NON_IVP_CONTROLS','spectral':rows,'independent_decimal_RR_max_relative':rrmax,'generators':gens,'high_charge_Li_RR_direction':'PASS at frozen T=forcing(z5), ne=1cm^-3, fractions[.1,.2,.3,.4] with photo disabled','abundance_baryon_normalization':float((a.MASS*a.Y)@f),'initial_axes':model.axes,'L16_transport_states':39,'joint_states':61,'actual_rhs_calls':1,'IVPs':0,'cpu_seconds':time.process_time()-start}
 return report
if __name__=='__main__':
 report=run();out=Path(__file__).resolve().parents[1]/'evidence/LIGHT_CHECKS.json';out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
