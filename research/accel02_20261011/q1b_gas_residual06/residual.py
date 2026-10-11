"""Value-only endpoint gas residual. This module never commits a time step."""
from pathlib import Path
import sys
import numpy as np
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE/'q1b_work_gas_jvp05'))
from adapter import absorption_map, work_split, domain
from opacity_native import EV_ERG, CHEMICAL_CHI_EV

def admissible(gas,g):
    domain(gas);x,y,z,w=gas;ratio=g['nHe']/g['nH']
    T=w*EV_ERG/(1.5*1.380649e-16*(1+ratio+x+ratio*(y+2*z)))
    if not np.isfinite(T) or not 1<=T<=1e6:raise ValueError('EXISTING_ATOMIC_TEMPERATURE_DOMAIN')
    return T

def norm(r,y0):return float(max(np.max(abs(r[:3])),abs(r[3])/y0[3]))

class Residual:
    def __init__(self,caller,g,y0,t,h,R,mu,nodes,counters):
        self.caller=caller;self.g=g;self.y0=np.asarray(y0,float);self.t=t;self.h=h
        self.R=R;self.mu=mu;self.nodes=nodes;self.counters=counters
        nH,nHe=g['nH']*g['a_rel']**3,g['nHe']*g['a_rel']**3
        c=CHEMICAL_CHI_EV
        self.energy_gradient=EV_ERG*np.array([nH*c[0],nHe*c[1],nHe*(c[1]+c[2]),nH])

    def evaluate(self,y,order,empty_zero_step=False):
        y=np.asarray(y,float);T=admissible(y,self.g);h=0. if empty_zero_step else self.h
        cells=[];values=[];pairs=[]
        for mu,(q,p,sigma) in ([] if empty_zero_step else zip(self.mu,self.nodes[order])):
            if self.counters['positive_maps']>=18:raise RuntimeError('POSITIVE_MAP_CAP')
            self.counters['positive_maps']+=1
            v,j,s,pair=absorption_map(q,p,self.R,h,sigma,self.g,y,directions=())
            if j.size or s.size or pair:raise AssertionError('UNREQUESTED_JACOBIAN')
            values.append(v)
            cells.append([mu,self.R,self.g['H']+self.g['s']*(3*mu*mu-1),v[0],v[1],0.,0.,*v[11:14],*v[14:17]])
            pairs.append({'number_before':float(sum(p)),'number_after_abs':float(v[0]+sum(v[2:5])),
                          'energy_before':float(np.dot(self.R*q,p)),'energy_after_abs':float(v[1]+sum(v[5:11]))})
        if self.caller.counts['CELL_RHS_V1']>=9:raise RuntimeError('CELL_POINT_CAP')
        output=self.caller.submit(self.t,self.g,y,cells)
        r=y-self.y0-h*output[:4];work=work_split(self.g,y,cells,output)
        Eabs=EV_ERG*sum(sum(v[5:11]) for v in values)
        gradient=self.energy_gradient;delta=gradient*(y-self.y0)
        terms=np.r_[delta,-Eabs,h*work['gas_work_rate'],h*output[4],-h*output[14]]
        lhs=float(sum(terms));rhs=float(np.dot(gradient,r))
        scale=float(sum(abs(terms))+sum(abs(gradient*r)))
        return {'y':y.copy(),'order':order,'h':h,'temperature_preflight':T,'cells':np.array(cells).reshape(-1,13),
                'values':values,'photon_pairs':pairs,'native':output,'residual':r,'norm':norm(r,self.y0),
                'work':work,'energy_absorbed_erg':Eabs,'energy_gradient':gradient,
                'energy_identity':{'lhs':lhs,'rhs':rhs,'termwise_scale':scale,'terms':terms},
                'committed_timestep':False}
