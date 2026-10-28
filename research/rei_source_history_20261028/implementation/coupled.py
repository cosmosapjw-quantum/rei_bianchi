"""Runnable prescribed-bath 17-heavy + two fast stocks + two energies pilot.

Import/setup and RHS evaluation do not solve an IVP. The CLI requires a separate
explicit execution flag; the present source-history unit never supplies it.
"""
import argparse
import json
import sys
import numpy as np
from scipy.sparse import csc_matrix
from history import UNIT,SOURCE,old,baseline,diagnose


def old_bath(data):
    sys.path.insert(0,str(SOURCE/'code'))
    import angular_model as angular
    model=angular.Reduced(M=4)
    with np.load(old.NPZ_PATH,allow_pickle=False) as d:
        g=d['photon_groups'].copy(); temp=d['temperature_K'].copy(); v=d['electron_per_Href'].copy()
    if g.shape!=(24,201) or temp.shape!=(201,) or v.shape!=(201,):
        raise ValueError('saved old photon/T/electron schema unavailable')
    if np.any(g<0) or np.any(v<0) or not np.isfinite(g).all() or not np.isfinite(temp).all():
        raise ValueError('invalid prescribed old bath')
    photo=np.empty((201,6)); rec=np.empty_like(photo)
    mismatch=np.zeros(2)
    for k,eta in enumerate(data['eta']):
        h,n,_,_,_,_,_,sigma,_=model.coefficients(float(eta))
        mismatch=np.maximum(mismatch,np.abs([h/data['H'][k]-1,n/data['nref'][k]-1]))
        photo[k]=angular.C*data['nref'][k]*(sigma@g[:,k])
        rec[k]=data['nref'][k]*v[k]*angular.thermal(float(temp[k]))[0]
    if np.any(mismatch>1e-10):
        raise ValueError('donor coefficients do not match saved H/nref: '+repr(mismatch))
    if np.any(photo<0) or np.any(rec<0) or not np.isfinite(photo+rec).all():
        raise ValueError('invalid reconstructed old hazards')
    edges=[(l,u,ch) for l,u,ch in angular.ATOM.edges if l<17 and l not in (0,5,6)]
    identities={str(p.relative_to(UNIT.parent)):old.digest(p) for p in
        (SOURCE/'code/angular_model.py',SOURCE/'inputs/background/grid044_history.npz',
         SOURCE/'vendor/c22/atomic_network.py')}
    return photo,rec,edges,{'source_identities':identities,'max_relative_H_nref_mismatch':mismatch.tolist(),
                           'raw_fields':['photon_groups','temperature_K','electron_per_Href'],'old_beta':'EXCLUDED'}


def dynamic_new(y,B,U,nref,alpha,c,escape):
    B,U=np.asarray(B),np.asarray(U)
    if np.any(B<0) or np.any(U<0) or np.any((B==0)&(U!=0)):
        raise ValueError('inconsistent or negative fast B/U stocks')
    c=c if escape else {**c,'ke_n_s':0.,'ke_T_s':0.,'kesc_s':0.}
    production=old.reservoirs(y,alpha,c)
    # Reuse particle/event definitions with zero assigned transport kinetic
    # energy, then book actual dynamic kinetic powers directly, never U/B.
    actual={'B':B,'P':np.zeros(2),'S':np.ones(2)}
    op=old.evaluate_operator(y,nref,alpha,c,escape=escape,res=actual)
    slow=np.array([c['ks_'+j+'_s'] for j in ('n','T')])*U
    outward=np.array([c['ke_'+j+'_s'] for j in ('n','T')])*U
    retained=np.array([c['lambda_'+j+'_s']/c['gamma_'+j] for j in ('n','T')])*U
    op['power']['heat']+=float((slow+retained).sum())
    op['power']['escaped_kinetic']+=float(outward.sum())
    op['power']['fast_kinetic_change']-=float((slow+outward+retained).sum())
    op['transport_power']={'slowing':slow,'escaping':outward,'beta_retained':retained}
    incoming=sum(op['power'][k] for k in ('photon_input','cr_input','injected_kinetic'))
    outgoing=sum(v for k,v in op['power'].items() if k not in ('photon_input','cr_input','injected_kinetic'))
    op['energy_residual']=incoming-outgoing
    dU=production['P']-production['L']*U
    return op,dU


def compile_new(c,mode):
    """Exact affine generator compiled from the frozen event operator.

    Capture is the only nonlinear new event and is added separately. Compilation
    evaluates no trajectory. Signed Newton trials use this polynomial extension.
    """
    alpha=1. if mode=='ON' else 0.
    c=c if mode=='ON' else {**c,'ke_n_s':0.,'ke_T_s':0.,'kesc_s':0.}
    def columns(y,B,cfg):
        # Zero fast kinetic energy avoids any mean-energy division in setup.
        result=old.evaluate_operator(y,0.,alpha,cfg,escape=mode=='ON',res={'B':B,'S':np.ones(2),'P':np.zeros(2)})
        return np.r_[result['dy'],result['external_baryon_rate'],result['electron_rate']]
    linear={**c,'thermal_injection_per_Href_s':[0.]*17,'fast_injection_per_Href_s':[0.,0.]}
    zero=np.zeros(17);base=columns(zero,np.zeros(2),c);matrix=np.empty((21,19))
    for j in range(19):
        y=np.zeros(17);B=np.zeros(2)
        if j<17:y[j]=1.
        else:B[j-17]=1.
        matrix[:,j]=columns(y,B,linear)
    production0=old.reservoirs(zero,alpha,c)
    power=np.empty((2,17))
    for j in range(17):
        unit=np.zeros(17);unit[j]=1.
        power[:,j]=old.reservoirs(unit,alpha,linear)['P']
    return base,matrix,production0['P'],power,production0['L']


class Coupled:
    def __init__(self,data=None):
        self.data=baseline() if data is None else data
        self.c=old.config(); self.t=self.data['t']
        self.photo,self.rec,self.edges,self.bath_metadata=old_bath(self.data)
        self.diagnostic=diagnose(self.data,self.c)
        self.new={mode:compile_new(self.c,mode) for mode in ('OFF','ON')}
        initial=self.data['y'][0].copy()
        self.y0=np.r_[initial,np.zeros(6)] #21 physical +2 accumulated boundary ledgers
        scale=np.empty(21)
        for start,thresholds in old.FAMILIES.values():
            end=start+len(thresholds)+1
            scale[start:end]=max(float(initial[start:end].sum()),1e-25)
        fixed=self.diagnostic['fixed']
        scale[0]=max(float(fixed[:,2].max()),1e-30)
        scale[5:7]=max(float(fixed[:,3:5].sum(axis=1).max()),1e-30)
        scale[17:19]=np.maximum(fixed[:,:2].max(axis=0),1e-30)
        scale[19:21]=1e6*scale[17:19]
        self.scale=np.r_[scale,max(float(old.A[:17]@initial),1e-30),max(float(old.Q[:17]@initial),1e-30)]
        self.initial_baryon=float(old.A[:17]@initial+6*self.data['hidden'][0].sum())
        self.initial_charge=float(old.Q[:17]@initial+np.arange(4)@self.data['hidden'][0])

    def interval(self,t):
        if not self.t[0]<=t<=self.t[-1]:raise ValueError('time outside finite bath')
        k=min(int(np.searchsorted(self.t,t,side='right'))-1,len(self.t)-2)
        return k,(t-self.t[k])/(self.t[k+1]-self.t[k])

    def fields(self,t):
        k,a=self.interval(t)
        p=(1-a)*self.photo[k]+a*self.photo[k+1]
        r=(1-a)*self.rec[k]+a*self.rec[k+1]
        n=np.exp((1-a)*np.log(self.data['nref'][k])+a*np.log(self.data['nref'][k+1]))
        hidden=(1-a)*self.data['hidden'][k]+a*self.data['hidden'][k+1]
        hidden_dot=(self.data['hidden'][k+1]-self.data['hidden'][k])/(self.t[k+1]-self.t[k])
        G=np.zeros((17,17))
        for l,u,ch in self.edges:
            G[l,l]-=p[ch];G[u,l]+=p[ch]
            G[u,u]-=r[ch];G[l,u]+=r[ch]
        return G,n,hidden,hidden_dot

    def rhs_physical(self,t,state,mode='ON'):
        y=state[:17]; B=state[17:19];U=state[19:21]
        G,n,hidden,hidden_dot=self.fields(t)
        base,matrix,power0,power,loss=self.new[mode]
        new=base+matrix@state[:19]
        for h,d in ((1,3),(2,4)):
            rate=n*self.c['capture_C_cm3_s']*y[0]*y[h]
            new[0]-=rate;new[h]-=rate;new[d]+=rate
        dU=power0+power@y-loss*U
        bath=G@y
        dy=np.r_[bath+new[:17],new[17:19],dU]
        # Charge counts all free electrons, including compensating external
        # supply and the prescribed Li6 charge history. A ledger is not n_e bath.
        electron=new[20]+old.Q[:17]@bath+np.arange(4)@hidden_dot
        return np.r_[dy,new[19],electron]

    def rhs(self,t,scaled,mode='ON'):
        return self.rhs_physical(t,scaled*self.scale,mode)/self.scale

    def jacobian_sparsity(self):
        pattern=np.zeros((23,23),bool)
        # Conservative dependency mask: source events depend on current heavy
        # targets, capture on n/H, transport on fast B. No energy feeds populations.
        pattern[:19,:19]=True
        pattern[19:21,:17]=True
        pattern[19,19]=True;pattern[20,20]=True
        pattern[21:,:19]=True
        return csc_matrix(pattern)

    def output_times(self):
        losses=[self.c['lambda_n_s'],self.c['lambda_T_s'],self.c['ks_n_s']+self.c['ke_n_s']+self.c['lambda_n_s'],
                self.c['ks_T_s']+self.c['ke_T_s']+self.c['lambda_T_s']]
        transient=np.concatenate([np.geomspace(.001/l,30/l,40) for l in losses])
        return np.unique(np.r_[self.t,transient[transient<self.t[-1]]])

    def solve(self,mode,refined=False):
        """Actual IVP path: only separately authorized callers may invoke."""
        from scipy.integrate import solve_ivp
        return solve_ivp(lambda t,x:self.rhs(t,x,mode),(self.t[0],self.t[-1]),self.y0/self.scale,
            method='Radau',t_eval=self.output_times(),rtol=2e-8 if refined else 1e-7,
            atol=2e-12 if refined else 1e-11,jac_sparsity=self.jacobian_sparsity())

    def balances(self,t,physical):
        hidden=np.array([self.fields(s)[2] for s in t]).T
        baryon=old.A[:17]@physical[:17]+physical[17]+3*physical[18]+6*hidden.sum(axis=0)
        charge=old.Q[:17]@physical[:17]+physical[18]+np.arange(4)@hidden
        return baryon+physical[21]-self.initial_baryon,charge-physical[22]-self.initial_charge


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-authorized',action='store_true',required=True)
    parser.add_argument('--case',choices=['OFF_base','ON_base','ON_refined'],required=True)
    args=parser.parse_args()
    model=Coupled();mode=args.case.split('_')[0]
    result=model.solve(mode,args.case.endswith('refined'))
    out=UNIT/'outputs';out.mkdir(exist_ok=True)
    physical=result.y*model.scale[:,None]
    b,q=model.balances(result.t,physical)
    np.savez_compressed(out/(args.case+'.npz'),t=result.t,physical=physical,baryon_residual=b,charge_residual=q,scales=model.scale)
    info={'status':'COMPLETED' if result.success else 'FAILED','message':result.message,'nfev':result.nfev,
          'njev':result.njev,'nlu':result.nlu,'minimum_scaled_stock':float((physical[:21]/model.scale[:21,None]).min()),
          'max_baryon_residual':float(abs(b).max()),'max_charge_residual':float(abs(q).max()),'bath':model.bath_metadata}
    (out/(args.case+'.json')).write_text(json.dumps(info,indent=2)+'\n')
    if not result.success:raise SystemExit(1)


if __name__=='__main__':main()
