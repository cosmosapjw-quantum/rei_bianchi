"""Independent MP80 linear algebra of represented native M,Mdot, not an IVP."""
from __future__ import annotations
import json,sys
from pathlib import Path
import numpy as np
import mpmath as mp
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'code'))
import charge_jets as c

def recalc():
 mp.mp.dps=80
 a=c.load_original();net=c.src.new_native_network()
 out=[];max_err=0
 for i in range(193):
  r,(M,Mdot,*_)=c.source_point(net,a,i)
  mm=mp.matrix([[mp.mpf(float(M[j,k])) for k in range(4)] for j in range(4)])
  md=mp.matrix([[mp.mpf(float(Mdot[j,k])) for k in range(4)] for j in range(4)])
  v=mp.matrix([[mp.mpf(float(c.V[j,k])) for k in range(2)] for j in range(4)])
  q=mp.matrix([[0,1,2,3]])
  ss=max(abs(mm[j,k]) for j in range(4) for k in range(4))
  r1=q*mm*v
  r2=q*(mm*mm+md)*v
  obs=mp.matrix([[r1[0,0]/ss,r1[0,1]/ss],[r2[0,0]/ss**2,r2[0,1]/ss**2]])
  det=mp.det(obs)
  err=abs(float(det)-r['det_nonautonomous'])
  max_err=max(err,max_err)
  if r['det_nonautonomous']*float(det)<0:raise AssertionError('sign conflict at '+str(i))
  out.append({'index':i,'z':r['z'],'det_mp80':mp.nstr(det,55),'det_double':r['det_nonautonomous']})
 return {'schema':'REI_F4_LI_SAVED193_JET_MP80_V1','mp_dps':mp.mp.dps,'represented_native_coefficients':True,
   'claim':'MP80 matrix arithmetic on binary64 original-rate M and analytic Mdot; NOT source-data interval enclosure',
   'rows':len(out),'max_abs_double_mp_error':max_err,'sign_disagreements':0,
   'sign_change_pairs':c.sign_brackets([{'z':z['z'],'det_nonautonomous':float(z['det_mp80'])} for z in out],'det_nonautonomous'),
   'first':out[0],'middle':out[100],'last':out[-1]}
if __name__=='__main__':
 a=recalc();(BASE/'results'/'MP80_JET_REFERENCE.json').write_text(json.dumps(a,indent=2,allow_nan=False)+'\n');print(json.dumps(a,indent=2)[:6000])
