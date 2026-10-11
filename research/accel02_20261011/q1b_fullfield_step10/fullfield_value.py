"""176-row value adapter for the frozen same-N1 full-field trial contract."""
import math
from pathlib import Path
import sys
import numpy as np
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE/'q1b_gas_residual06'))
from residual import admissible,norm
from adapter import absorption_map,work_split
from opacity_native import EV_ERG,CHEMICAL_CHI_EV
from reconstruction import reconstruct

class FullFieldValue:
    def __init__(self,caller,g,y0,t,h,R,mu,edges,caps,nodes,counters):
        self.caller,self.g,self.t,self.h=caller,g,t,h
        self.y0=np.asarray(y0);self.R=R;self.mu=np.asarray(mu)
        self.edges=np.asarray(edges);self.caps=np.asarray(caps)
        self.nodes=nodes;self.counters=counters
        nh,ne=g['nH']*g['a_rel']**3,g['nHe']*g['a_rel']**3;c=CHEMICAL_CHI_EV
        self.energy_gradient=EV_ERG*np.array([nh*c[0],ne*c[1],ne*(c[1]+c[2]),nh])
    def evaluate(self,y,order):
        y=np.asarray(y,float);temperature=admissible(y,self.g)
        values=[];cells=[];pairs=[];states=[]
        for k,(q,p,sigma) in enumerate(self.nodes[order]):
            if self.counters['positive_maps']>=1408:raise RuntimeError('FULLFIELD_MAP_CAP')
            self.counters['positive_maps']+=1
            v,j,scales,jpairs=absorption_map(q,p,self.R,self.h,sigma,self.g,y,directions=())
            if j.size or scales.size or jpairs:raise AssertionError('UNREQUESTED_JACOBIAN')
            i=k%(len(self.edges)-1);mu=self.mu[k//(len(self.edges)-1)]
            rec=reconstruct(v[0],v[1],self.R,self.edges[i],self.caps[i])
            states.append(rec.status)
            values.append(v)
            cells.append([mu,self.R,self.g['H']+self.g['s']*(3*mu*mu-1),v[0],v[1],0.,0.,*v[11:14],*v[14:17]])
            pairs.append({'number_before':math.fsum(p),'number_after_abs':float(v[0]+math.fsum(v[2:5])),
                          'energy_before':float(np.dot(self.R*q,p)),'energy_after_abs':float(v[1]+math.fsum(v[5:11]))})
        if len(cells)!=176:raise AssertionError('FULLFIELD_ROW_COUNT')
        if self.caller.counts['CELL_RHS_V1']>=8:raise RuntimeError('FULLFIELD_CELL_CAP')
        native=self.caller.submit(self.t,self.g,y,cells)
        residual=y-self.y0-self.h*native[:4]
        work=work_split(self.g,y,cells,native)
        absorbed=EV_ERG*math.fsum(math.fsum(v[5:11]) for v in values)
        gradient=self.energy_gradient;terms=np.r_[gradient*(y-self.y0),-absorbed,
          self.h*work['gas_work_rate'],self.h*native[4],-self.h*native[14]]
        rhs=float(np.dot(gradient,residual));lhs=math.fsum(terms)
        return {'y':y.copy(),'order':order,'temperature_preflight':temperature,
          'values':np.asarray(values),'cells':np.asarray(cells),'states':states,
          'native':native,'residual':residual,'norm':norm(residual,self.y0),
          'photon_pairs':pairs,'work':work,'energy_gradient':gradient,
          'energy_identity':{'lhs':lhs,'rhs':rhs,'terms':terms,
                            'termwise_scale':math.fsum(abs(terms))+math.fsum(abs(gradient*residual))}}
