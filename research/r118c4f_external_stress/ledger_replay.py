"""Cancellation audit using directly recorded stocks and native integrated work."""
from pathlib import Path
import json,numpy as np,hashlib
D=Path(__file__).resolve().parent
ld=np.longdouble
RHO0=3.*299792458.*299792458.*(2.1842852410855023e-18)**2/(8.*np.pi*6.67430e-11)
EV=1.602176634e-19
def load(grid,case):
 p=D/f'{grid}_{case}_external.csv';a=np.genfromtxt(p,names=True,delimiter=',',dtype=ld)
 fac=a['nh_m3']*ld(EV/RHO0)
 stock=fac*(a['primary']+a['cool']+a['spec']+(a['thermal']-a['init_w'])+(a['binding']-a['init_b'])-a['source_u'])
 work=-fac*(a['thermal_work']+a['photon_work']+a['boundary_u']+a['secondary_work'])
 return np.column_stack([a['rho_stable'],a['rho_owner'],stock,work])
rows=[]
for grid in ['1024_4','2048_2']:
 b=load(grid,'base')
 for name in ['H','T','HeII','HeIII']:
  if name in ['H','T']:r=(load(grid,name+'_0.01')-load(grid,name+'_-0.01'))/ld('.02')
  else:r=(4*(load(grid,name+'_5e-07')-b)-(load(grid,name+'_1e-06')-b))/ld('1e-6')
  z=np.load(D/f'{grid}_{name}_TANGENT.npz')
  c=z['continuity_rho'].astype(ld)
  err={k:float(np.max(abs(r[:,i]-c))) for i,k in enumerate(['native_stable','native_owner','recomputed_ld_stock','ledger_work'])}
  rec=dict(grid=grid,direction=name,continuity_end=float(c[-1]),derivative_end=dict(zip(['native_stable','native_owner','recomputed_ld_stock','ledger_work'],map(float,r[-1]))),max_discrepancy=err,stock_work_fd_gap=float(max(abs(r[:,2]-r[:,3]))),scope='work reconstruction is a diagnostic of stock/ledger cancellation, not a substitute discrete tangent')
  rows.append(rec)
  print(json.dumps(rec),flush=True)
(D/'LEDGER_FD_AUDIT.json').write_text(json.dumps(dict(rows=rows,scope='all 18 bitwise-replayed native cases; differences evaluated before scaling for helium one-sided stencil; work identity checked against conditional continuity'),indent=2)+'\n')
