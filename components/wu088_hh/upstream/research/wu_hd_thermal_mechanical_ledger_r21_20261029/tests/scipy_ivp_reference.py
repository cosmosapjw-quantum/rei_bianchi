"""Independent IVP of source-prescribed single-segment reactive+dilution+work model."""
import json
from pathlib import Path
import math
import numpy as np
from scipy.integrate import solve_ivp
from research.wu_hd_source_bound_r18_20261029.src.native_rates import load_native_grid
from research.wu_hd_source_grid_r20_20261029.src.grid_exposure import Segment
from research.wu_hd_thermal_mechanical_ledger_r21_20261029.src.thermal_ledger import build_ledger,K_B_J_PER_K

root=Path(__file__).resolve().parents[1]; pdf=Path(__file__).resolve().parents[3]/'ORIGINAL_SOURCES/GL2022_CSIC_supplement.pdf'
grid=load_native_grid(pdf)
errors=[]
for initial,T,theta,dt in [((1e6,1e6,0,0),105,0.,1e10),((1e6,2e6,1e5,1e5),255,2e-11,3e9),((8e5,3e6,2e5,7e5),505,-2e-11,1e9),((1e4,1e4,1.,1.),105,1e-11,2e9)]:
    seg=Segment(T,dt,theta)
    flow,l=build_ledger(grid,initial,[seg])
    k=float(grid.lookup(T).nominal_m3_s)
    ntot=sum(initial)
    def rhs(t,y):
        flux=k*y[0]*y[1]
        return [-flux-theta*y[0],-flux-theta*y[1],flux-theta*y[2],flux-theta*y[3],ntot*K_B_J_PER_K*T*theta]
    ivp=solve_ivp(rhs,(0,dt),[*initial,0.],method='DOP853',rtol=2e-12,atol=[1e-8]*4+[1e-25])
    assert ivp.success,ivp.message
    dn=float(max(abs(a-b) for a,b in zip(ivp.y[:4,-1],flow.final_state_m_minus3)))
    dw=float(abs(ivp.y[4,-1]-l.pressure_work_by_material_J_per_ref_m3))
    assert dn<5e-5,(T,theta,dn)
    assert dw<2e-25,(T,theta,dw)
    errors.append({'T_K':T,'theta_s':theta,'state_max_abs_m3':dn,'work_abs_J_ref_m3':dw,'nfev':ivp.nfev})
record={'schema':'wu.r21.scipy_ivp.v1','cases':len(errors),'pass':len(errors),'method':'DOP853','rtol':2e-12,'atol_m3':1e-8,'atol_energy_J':1e-25,'cases_detail':errors,'max_state_abs_m3':max(e['state_max_abs_m3'] for e in errors),'max_work_abs_J_ref_m3':max(e['work_abs_J_ref_m3'] for e in errors),'full_network':False,'physical_Q_supplied':False}
(root/'results'/'SCIPY_IVP.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
