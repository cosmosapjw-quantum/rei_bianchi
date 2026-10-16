"""Independent dense H-only / He-only / mixed Case-A no-photon Radau study."""
from bootstrap_v6 import setup
setup()

import json, math
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from rate_table import CaseARates
from dynamic_chemistry import Gas
from study_v5 import rays
from recomb_thermal import evolve_thermal as old_evolve,particle_count,K_B_EV_PER_K,EV_J
from recomb_thermal_midpoint_v6 import evolve_thermal as new_evolve

N_STAR=.1;H0=1e-16;END=.01;T0=15000.; STEPS=(.0025,.00125,.000625,.0003125)
GASES={
 'H_only':Gas(.37,.03,0,0,0),
 'He_only':Gas(0,0,.085,.012,.003),
 'HHe_mixed':Gas(.37,.03,.085,.012,.003),
}

def independent_ref(initial,provider):
 y0=np.array([*initial.as_tuple(),1.5*K_B_EV_PER_K*T0*particle_count(initial.as_tuple())],float)
 def rhs(x,y):
  g=y[:5];u=y[-1]
  ne=g[1]+g[3]+2*g[4]
  t=u/(1.5*K_B_EV_PER_K*(sum(g)+ne))
  co=provider(float(t))
  alpha=np.array((co[0],co[1]+co[3],co[2]))
  cool=np.array((co[4],co[5]+co[7],co[6]))
  r=N_STAR/H0*np.exp(-3*x)*ne*np.array([g[1],g[3],g[4]])*alpha
  out=np.zeros_like(y)
  for j,(target,product) in enumerate(((0,1),(2,3),(3,4))):
   out[target]+=r[j];out[product]-=r[j]
  out[-1]=-2*u-float(np.dot(r,cool/alpha))/(EV_J*1e7)
  return out
 sol=solve_ivp(rhs,(0,END),y0,rtol=2e-11,atol=1e-14,method='Radau',max_step=.0001)
 assert sol.success,sol.message
 y=sol.y[:,-1]
 t=y[-1]/(1.5*K_B_EV_PER_K*(sum(y[:5])+y[1]+y[3]+2*y[4]))
 return y,float(t),int(sol.nfev)

def run():
 p=CaseARates(); data={}
 for name,gas in GASES.items():
  ref,T,nfev=independent_ref(gas,p)
  vals=[]
  for h in STEPS:
   opts=dict(temperature_initial_K=T0,max_step=h,atomic_rates=p,n_star_cm3=N_STAR,h0_s=H0)
   old=old_evolve(rays(0.,0.),gas,END,**opts)
   new=new_evolve(rays(0.,0.),gas,END,**opts)
   g2=np.array([*new.final.as_tuple(),new.final_thermal_ev])
   vals.append(dict(h=h,old_T_error=abs(old.final_temperature_K-T),new_T_error=abs(new.final_temperature_K-T),
                    old_ion_error=abs(old.final.electrons-(ref[1]+ref[3]+2*ref[4])),
                    new_ion_error=abs(new.final.electrons-(ref[1]+ref[3]+2*ref[4])),
                    max_state_error=float(np.max(abs(g2-ref))),energy_residual=new.energy_residual_ev,
                    gas_min=min(new.final.as_tuple()),T=new.final_temperature_K,
                    escaped_e=new.escaped_recomb_energy_ev))
  errors=[d['new_T_error'] for d in vals]
  orders=[math.log(a/b,2) for a,b in zip(errors[:-1],errors[1:])]
  data[name]={'refT':T,'nfev':nfev,'rows':vals,'orders':orders}
 return {'source':'original Grackle C11 129-row owner interpolation; 10--24kK','data':data}

if __name__=='__main__':
 result=run()
 Path(__file__).with_name('dense_multichannel_v6.json').write_text(json.dumps(result,indent=2)+'\n')
 for k,v in result['data'].items():
  print(k,'Tref',v['refT'],'old', [r['old_T_error'] for r in v['rows']],
        'new',[r['new_T_error'] for r in v['rows']], 'orders',v['orders'],flush=True)
