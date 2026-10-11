"""Work ownership and fixed-node photo absorption derivatives, not full gas RHS."""
import math
from pathlib import Path
import sys
import numpy as np
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE/'q1b_source_entry04'))
from positive_entry import attenuate
from opacity_native import EV_ERG, C_CM_S, CHEMICAL_CHI_EV

FIELDS=['N','U_eV']+[f'{kind}_{sp}' for kind in ('count','binding_eV','heat_eV','K0','KE','Gamma','per_absorber_heat_eV') for sp in ('HI','HeI','HeII')]+['gas_work','radiation_work']

def work_split(g,gas,cells,abi):
    cells=np.asarray(cells,float).reshape(-1,13);V=g['a_rel']**3
    mu,U=cells[:,0],cells[:,4]
    lam=g['H']+g['s']*(3*mu*mu-1)
    radiation=EV_ERG*math.fsum(lam*U)
    thermal=2*g['H']*EV_ERG*g['nH']*gas[3]*V
    pressure=EV_ERG*(g['H']*math.fsum(U)+g['s']*math.fsum((3*mu*mu-1)*U))
    scale=EV_ERG*math.fsum((abs(g['H'])+abs(g['s']*(3*mu*mu-1)))*abs(U))+abs(thermal)
    return {'radiation_work_rate':radiation,'gas_work_rate':thermal,
            'abi_combined_work_rate':float(abi[5]),'pressure_form_radiation':pressure,
            'termwise_scale':scale,'pairing_residual':radiation+thermal-abi[5],
            'unit':'erg/reference_cm3/proper_second','ownership':'source step owns integrated radiation work; do not add this diagnostic again'}

def domain(gas):
    x,y,z,w=np.asarray(gas,float)
    if not np.isfinite(gas).all() or not (0<=x<=1 and y>=0 and z>=0 and y+z<=1 and w>0):
        raise ValueError('GAS_TRIAL_OUTSIDE_DOMAIN_NO_PROJECTION')

def absorption_map(q,p,R,h,sigma,g,gas,directions=()):
    """Values and analytic JVPs at fixed incident quadrature and fixed geometry."""
    domain(gas);q,p,sigma=np.asarray(q),np.asarray(p),np.asarray(sigma)
    E=R*q;cross=C_CM_S*sigma;nh,ne=g['nH'],g['nHe'];V=g['a_rel']**3
    x,y,z,w=gas;lower=np.array([nh*(1-x),ne*(1-y-z),ne*y])
    ks=cross*lower;den=1+h*ks.sum(axis=1)
    survive,absorbed=attenuate(p,ks,h)
    def pack(ps,ab,gaswork):
        count=np.sum(ab,axis=0);bind=CHEMICAL_CHI_EV*count
        heat=np.sum((E[:,None]-CHEMICAL_CHI_EV)*ab,axis=0)
        K0=np.sum(cross*ps[:,None],axis=0);KE=np.sum(E[:,None]*cross*ps[:,None],axis=0)
        perheat=np.sum((E[:,None]-CHEMICAL_CHI_EV)*cross*ps[:,None],axis=0)/V
        return np.r_[sum(ps),np.dot(E,ps),count,bind,heat,K0,KE,K0/V,perheat,gaswork,0.]
    values=pack(survive,absorbed,2*g['H']*EV_ERG*nh*V*w)
    jvps=[];scales=[];pairs=[]
    for direction in np.asarray(directions,float).reshape(-1,4):
        dx,dy,dz,dw=direction;dlower=np.array([-nh*dx,-ne*(dy+dz),ne*dy])
        # Absolute directional contributions, including cancellation in HeI.
        slower=np.array([nh*abs(dx),ne*(abs(dy)+abs(dz)),ne*abs(dy)])
        dks=cross*dlower;sks=cross*slower
        dp=-survive*h*dks.sum(axis=1)/den
        sp=survive*h*sks.sum(axis=1)/den
        da=h*dks*survive[:,None]+h*ks*dp[:,None]
        sa=h*sks*survive[:,None]+h*ks*sp[:,None]
        jvps.append(pack(dp,da,2*g['H']*EV_ERG*nh*V*dw))
        # E>=60 eV in these fixtures; all heat kernels nonnegative.
        scales.append(pack(sp,sa,abs(2*g['H']*EV_ERG*nh*V*dw)))
        pairs.append({'node_residual':dp+da.sum(axis=1),
                      'node_scale':abs(dp)+abs(da).sum(axis=1),
                      'energy_residual':np.dot(E,dp)+np.sum(E[:,None]*da),
                      'energy_scale':np.dot(E,abs(dp))+np.sum(E[:,None]*abs(da))})
    return values,np.asarray(jvps),np.asarray(scales),pairs
