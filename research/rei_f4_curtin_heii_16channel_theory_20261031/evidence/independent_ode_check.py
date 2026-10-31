"""Same-author independent differential-equation integrator vs finite-cell 16-channel recurrence.
The two paths use the same source tables/atomic data but different ODE vs cell solver.
This is NOT a distinct-author referee nor a different physical-source validation.
"""
import sys,json,pathlib,numpy as np,pandas as pd
from scipy.integrate import solve_ivp
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import compute_theory as t
m,arr,chem,th,pl,coul,data,owner,meta,bands,original=t.read_parent()
t.DATA=data;ccc=t.load_heii();E=t.make_grid(m,ccc,2100)
sig=np.r_[m.sigma_samples(data,owner,E),t.heii_sigma(E,ccc)]
den=t.species_densities(coul,chem,th)
speed=np.sqrt(2*E*m.EV_ERG/m.ELECTRON_MASS_G)
mono=pd.read_csv(ROOT/'results/HeII_16CHANNEL_MONO_1544.csv')
out=[]
for ep in (60,80,112):
 ne=den[ep,3];ds=np.r_[[den[ep,0]]*3,[den[ep,1]]*3,[den[ep,2]]*10]
 ln=np.log(4*E/(7.40e-11*ne))
 bee=4*np.pi*m.E_SQUARED_CGS**2*ne*ln/(m.ELECTRON_MASS_G*speed*m.EV_ERG)
 h=ds[:,None]*sig*speed/bee
 def func(x,p):
  v=np.array([np.interp(x,E,k) for k in h]);return v-p*v.sum()
 for e0 in (45.,55.,60.):
  sol=solve_ivp(func,(m.LOW,e0),np.zeros(16),method='DOP853',rtol=6e-9,atol=3e-13,max_step=0.03)
  assert sol.success,sol.message
  p=sol.y[:,-1]; ref=mono[(mono.epoch==ep)&(mono.E_eV==e0)].iloc[0]
  herr=abs(p[6:16].sum()-ref.P_HeII_any)/max(abs(ref.P_HeII_any),1e-90)
  terr=abs(p.sum()-ref.P_all_16)/max(abs(ref.P_all_16),1e-90)
  out.append(dict(epoch=ep,E0=e0,ODE_HeII=float(p[6:16].sum()),CELL_HeII=float(ref.P_HeII_any),relative_HeII_difference=float(herr),relative_all_difference=float(terr),steps=len(sol.t),method='DOP853'))
print(json.dumps(out,indent=2))
if not all(q['relative_HeII_difference']<0.005 and q['relative_all_difference']<0.002 for q in out):raise AssertionError('ODE mismatch needs inspection')
