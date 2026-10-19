"""RUN08 joint finite native birth packet on original time-dependent BASS.

Native gas RHS, independent vectorized photon assembly, comoving normalisation.
Depth coordinates are an exact change of variables between source impulses.
No continuum source, EFE feedback, or uniform positivity certification claimed.
"""
from __future__ import annotations
import sys,json,pathlib,time,subprocess,hashlib
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.sparse import lil_matrix
from gas_integrator_parent import GasServer,EV_J
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'inputs'))
from source_table import BackgroundTable
KB=1.380649e-23;C=299792458.;LO=np.array([1,10,11,3]);UP=np.array([2,11,12,4]);CHARGE=np.array([0,0,1,0,1,0,1,0,1,2,0,1,2])
PARAMETERS=np.array([[13.60,.4298,5.475e4,32.88,2.963,0,0,0],[24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136],[54.42,1.720,1.369e4,32.88,2.963,0,0,0]])
def sigma_native_formula(energy,chi):
    e=np.asarray(energy);o=np.zeros((len(e),4))
    if not np.isfinite(e).all() or (e<=0).any() or (e>50000).any():raise ValueError('energy provider domain')
    for i,(eth,e0,s0,ya,p,yw,y0,y1) in enumerate(PARAMETERS):
        mask=e>=max(eth,chi[i]);x=e[mask]/e0-y0;y=np.sqrt(x*x+y1*y1)
        o[mask,i]=s0*((x-1)**2+yw*yw)*y**(p/2-5.5)*(1+np.sqrt(y/ya))**(-p)*1e-22
    o[:,3]=o[:,0]*(e>=chi[3])
    return o
class RetardedModel:
    def __init__(self,packet=None):
        path=ROOT/'inputs/FINITE_BIRTH_PACKET.json'
        self.f=json.loads(path.read_text()) if packet is None else packet
        self.coh=np.asarray(self.f['cohorts'],dtype=float)
        if self.coh.ndim!=2 or self.coh.shape[1]!=9 or not np.isfinite(self.coh).all() or (self.coh[:,6]<=0).any():raise ValueError('positive finite exact birth packet required')
        self.x0=self.f['x0'];self.x1=self.f['x1'];self.dx=self.x1-self.x0;self.a0=self.f['a0'];self.chi=np.array(self.f['chi_eV'])
        self.nh=sum(self.f['state'][1:3]);self.birth=(self.coh[:,0]-self.x0)/self.dx
        if self.dx<=0 or (np.diff(self.birth)<0).any() or self.birth.min()<=0 or self.birth.max()>=1:raise ValueError('source birth ordering/domain')
        self.B=self.coh[:,6]/self.nh;self.eb=self.coh[:,4];self.mu2=self.coh[:,5]**2
        self.m=len(self.coh);self.p=27+self.m;self.dim=self.p+10
        self.table=BackgroundTable(ROOT/'inputs/bass164/PRODUCER_RECEIPT.json',ROOT/'inputs/bass164/PROPOSED_REI_BACKGROUND.csv')
        self.nodes,self.segs,_=self.table.samples[self.f['case']];self.xnodes=np.array([n.x for n in self.nodes])
        self.gscale=np.full(27,self.nh);self.gscale[13:16]=self.nh*EV_J;self.gscale[26]=self.nh*EV_J
        self.y0=np.zeros(self.dim);self.y0[:14]=np.array(self.f['state'])/self.gscale[:14]
        self.bind=np.zeros(13);self.bind[2]=self.chi[0];self.bind[4]=self.chi[3];self.bind[11]=self.chi[1];self.bind[12]=self.chi[1]+self.chi[2]
        self.calls=0;self.server=None
    def geometry(self,z):
        x=self.x0+self.dx*z;j=int(np.searchsorted(self.xnodes,x,side='right')-1);j=min(max(j,0),len(self.segs)-1)
        b,h,s,_=self.segs[j].state(x);a=self.a0*np.exp(self.dx*z);return a,b,h,s/h
    def rays(self,z,count):
        a,b,h,bx=self.geometry(z);co=self.coh[:count]
        # Evaluate actual birth scale factors, not an assumed common source frame.
        perp=(1-self.mu2[:count])*(co[:,2]/a)**2*np.exp(2*(b-co[:,3]))
        para=self.mu2[:count]*(co[:,2]/a)**2*np.exp(-4*(b-co[:,3]));r=perp+para
        e=self.eb[:count]*np.sqrt(r);de=-e*((1-bx)*perp+(1+2*bx)*para)/r
        return e,de,h,a
    def raw_rhs(self,z,y,active,mode='joint',frozen_gas=None):
        if y.shape!=(self.dim,) or not np.isfinite(y).all() or not 0<=active<=self.m:raise ValueError('RHS shape/domain')
        self.calls+=1;a,b,h,bx=self.geometry(z);vol=(a/self.a0)**3;out=np.zeros(self.dim)
        if mode in ('joint','gas'):
            raw=self.server.rhs(y[:14]*self.gscale[:14]/vol,2.7255/a)[:27]
            out[:27]=self.dx*vol/h*raw/self.gscale
            out[13]-=2*self.dx*y[13];out[self.p+8]=2*self.dx*y[13]
        if active and mode in ('joint','photo','frozen'):
            e,de,_,_=self.rays(z,active);sig=sigma_native_formula(e,self.chi)
            n=(y[:13] if frozen_gas is None else frozen_gas[:13])*self.nh/vol
            hazard=C*self.dx/h*sig*n[LO][None,:]
            depth=y[27:27+active]
            population=self.B[:active]*np.exp(-depth)
            events=hazard*population[:,None];net=events.sum(axis=0)
            heat=(events*(e[:,None]-self.chi[None,:])).sum(axis=0)
            out[27:27+active]=hazard.sum(axis=1)
            np.add.at(out,LO,-net);np.add.at(out,UP,net)
            out[13]+=heat.sum();out[self.p:self.p+4]=net;out[self.p+4:self.p+8]=heat
            out[self.p+9]=-self.dx*np.dot(population,de)
        return out
    def events(self):
        # Monotone BASS donor verified by original receiver; fixed provider edges.
        end=self.rays(1.,self.m)[0];edges=np.maximum(self.chi,np.array([13.6,24.59,54.42,13.6]));cuts=[]
        for edge in edges:
            for j in np.flatnonzero((self.eb>edge)&(end<edge)):
                def fun(z):return self.rays(z,j+1)[0][j]-edge
                root=brentq(fun,float(self.birth[j]),1.,xtol=2e-13,rtol=4*np.finfo(float).eps);cuts.append(root)
        return sorted(set([0.,1.,*self.birth.tolist(),*cuts])),len(cuts)
    def sparsity(self):
        # Arrow structure of depth coordinates: every photon depth depends on gas,
        # not on its own depth; photo/gas/energy depend on all active depths.
        a=lil_matrix((self.dim,self.dim),dtype=np.int8)
        a[:27,:14]=1;a[[1,2,3,4,10,11,12,13],27:self.p]=1
        a[27:self.p,:13]=1;a[self.p:,:14]=1;a[self.p:,27:self.p]=1
        return a.tocsc()
    def observables(self,y,z=1.,active=None):
        active=self.m if active is None else active;e,_,_,a=self.rays(z,active);P=self.B[:active]*np.exp(-y[27:27+active]);born=self.B[:active].sum();bornE=np.dot(self.B[:active],self.eb[:active]);vol=(a/self.a0)**3
        gas=y[:13];init=self.y0[:13];thermal=float(y[13]);gasE=thermal+gas@self.bind+y[14]+y[15];initialE=self.y0[13]+init@self.bind
        work=y[self.p+8]+y[self.p+9];res=gasE+P@e+work-initialE-bornE
        ne=gas@CHARGE;temp=2*thermal*EV_J/(3*KB*((1+CHARGE)@gas))
        photonscale=self.nh*self.a0**3;pred=init.copy();net=y[16:20]-y[20:24]+y[self.p:self.p+4]
        for j in range(4):pred[LO[j]]-=net[j];pred[UP[j]]+=net[j]
        pred[11]-=y[24];pred[10]+=y[24];pred[2]-=y[25];pred[1]+=y[25];pred[3]-=y[25];pred[4]+=y[25]
        return dict(T_K=float(temp),x_HII=float(gas[2]/sum(gas[1:3])),x_DII=float(gas[4]/sum(gas[3:5])),x_HeII=float(gas[11]/sum(gas[10:13])),x_HeIII=float(gas[12]/sum(gas[10:13])),survivor_com3=float(P.sum()*photonscale),HI_com3=float(y[self.p]*photonscale),HeI_com3=float(y[self.p+1]*photonscale),HeII_com3=float(y[self.p+2]*photonscale),DI_com3=float(y[self.p+3]*photonscale),thermal_J_m3=float(thermal*self.nh*EV_J/vol),photon_energy_J_com3=float(P@e*photonscale*EV_J),gas_work_J_com3=float(y[self.p+8]*photonscale*EV_J),photon_work_J_com3=float(y[self.p+9]*photonscale*EV_J),born_com3=float(born*photonscale),photon_ledger_rel=float(abs(P.sum()+sum(y[self.p:self.p+4])-born)/born),energy_ledger_rel_initial=float(abs(res)/initialE),energy_ledger_rel_source=float(abs(res)/bornE),species_event_rel_H=float(max(abs(gas-pred))),species_event_D_fraction=float(max(abs(gas[3:5]-pred[3:5]))/sum(init[3:5])),max_depth=float(max(y[27:self.p])))

def solve_packet(model,method='DOP853',rtol=3e-10,max_step=.02,split=None,n=1,wall_cap=35.):
    if rtol<=0 or max_step<=0 or n<1:raise ValueError('positive control required')
    points,cuts=model.events();points=sorted(set(points+np.linspace(0,1,n+1).tolist())) if split else points
    y=model.y0.copy();start=time.perf_counter();receipts=[];initialcalls=model.calls
    atol=np.full(model.dim,1e-13);atol[:13]=1e-17;atol[14:27]=1e-20;atol[27:model.p]=1e-11;atol[model.p:]=1e-19
    implicit=method in ('Radau','BDF')
    # Effective RMS error becomes the component-scaled L2 norm, without dilution.
    norm_factor=np.sqrt(model.dim)
    effective_rtol=rtol/norm_factor;atol/=norm_factor
    with GasServer() as server:
        model.server=server
        for left,right in zip(points[:-1],points[1:]):
            active=int(np.searchsorted(model.birth,left,side='right'))
            seq=[('joint',1.)] if split is None else ([('frozen',1.),('gas',1.)] if split=='frozen_lie' else [('photo',1.),('gas',1.)])
            for mode,_ in seq:
                frozen=y[:14].copy() if mode=='frozen' else None
                def rhs(z,state):
                    if time.perf_counter()-start>wall_cap:raise TimeoutError(f'RUN08 bounded case: {left:.6f}..{right:.6f} / {mode}')
                    return model.raw_rhs(z,state,active,mode,frozen)
                options={} if not implicit else {'jac':lambda z,state:analytic_jacobian(model,z,state,active,mode,frozen)}
                sol=solve_ivp(rhs,(left,right),y,method=method,rtol=effective_rtol,atol=atol,max_step=max_step,**options)
                if not sol.success or sol.t[-1]!=right:raise RuntimeError(str(sol.message))
                if (sol.y[:13]<0).any() or (sol.y[13]<=0).any():raise ValueError('negative accepted gas; no clipping')
                if active and sol.y[27:27+active].min() < -1e-12:raise ValueError('negative accepted optical depth')
                y=sol.y[:,-1].copy();receipts.append({'left':left,'right':right,'mode':mode,'active':active,'nfev':sol.nfev,'njev':sol.njev,'nlu':sol.nlu,'nodes':len(sol.t)})
    model.server=None
    return y,dict(method=method,rtol=rtol,effective_rtol=effective_rtol,error_norm='component_scaled_L2',max_step=max_step,split=split,n=n,dimension=model.dim,cohorts=model.m,birth_times=len(np.unique(model.birth)),threshold_roots=cuts,rhs_calls=model.calls-initialcalls,wall_s=time.perf_counter()-start,segments=receipts,observable=model.observables(y))

def analytic_jacobian(model,z,y,active,mode='joint',frozen_gas=None):
    """Sparse arrow Jacobian. Gas derivative is centred native FD on invariant
    H/D/He4 thermal manifold; photon/depth/work blocks are analytic."""
    from scipy.sparse import coo_matrix
    a,b,h,bx=model.geometry(z);vol=(a/model.a0)**3;dim=model.dim;p=model.p
    rows=[];cols=[];vals=[]
    def put(rr,cc,vv):
        rr,cc,vv=np.broadcast_arrays(rr,cc,vv);rows.extend(rr.ravel().tolist());cols.extend(cc.ravel().tolist());vals.extend(vv.ravel().tolist())
    if mode in ('joint','gas'):
        for j in (1,2,3,4,10,11,12,13):
            delta=2e-6*max(abs(y[j]),1e-12);plus=y[:14].copy();minus=plus.copy();plus[j]+=delta;minus[j]-=delta
            q1=model.server.rhs(plus*model.gscale[:14]/vol,2.7255/a)[:27]
            q0=model.server.rhs(minus*model.gscale[:14]/vol,2.7255/a)[:27]
            der=(q1-q0)/(2*delta)*model.dx*vol/h/model.gscale
            put(np.arange(27),j,der)
        put(13,13,-2*model.dx);put(p+8,13,2*model.dx)
    if active and mode in ('joint','photo','frozen'):
        e,de,_,_=model.rays(z,active);sig=sigma_native_formula(e,model.chi);kk=C*model.dx/h*sig*model.nh/vol
        pg=model.B[:active]*np.exp(-y[27:27+active]);ng=(y if frozen_gas is None else frozen_gas)
        ev=kk*ng[LO][None,:]*pg[:,None];coltau=np.arange(27,27+active);heat=e[:,None]-model.chi
        for j in range(4):
            if frozen_gas is None:
                dnet=np.sum(kk[:,j]*pg);dheat=np.dot(kk[:,j]*pg,heat[:,j]);put(LO[j],LO[j],-dnet);put(UP[j],LO[j],dnet)
                put(13,LO[j],dheat);put(p+j,LO[j],dnet);put(p+4+j,LO[j],dheat);put(coltau,LO[j],kk[:,j])
            put(LO[j],coltau,ev[:,j]);put(UP[j],coltau,-ev[:,j]);put(13,coltau,-ev[:,j]*heat[:,j]);put(p+j,coltau,-ev[:,j]);put(p+4+j,coltau,-ev[:,j]*heat[:,j])
        put(p+9,coltau,model.dx*pg*de)
    return coo_matrix((vals,(rows,cols)),shape=(dim,dim)).tocsc()

def coalesce_reflections(packet):
    """Exact scalar-observable reduction, restricted to paired LRS +/-mu,
    untilted isotropic atomic hazards and the same per-pair birth/energy data.
    No arbitrary spectral/age compression or angular continuum assertion."""
    import copy
    groups={}
    for index,row in enumerate(packet['cohorts']):
        key=tuple(row[:5])+ (abs(row[5]),row[7])
        groups.setdefault(key,[]).append((index,row))
    out=copy.deepcopy(packet);out['cohorts']=[];mapping=[]
    for group in groups.values():
        if len(group)!=2 or group[0][1][5] != -group[1][1][5]:raise ValueError('not exact reflection pairs')
        a=group[0][1].copy();a[5]=abs(a[5]);a[6]=sum(v[1][6] for v in group)
        out['cohorts'].append(a);mapping.append([v[0] for v in group])
    out['representation']='exact_reflection_pair_scalar_quotient'
    out['original_count']=len(packet['cohorts']);out['reflection_mapping']=mapping
    return out
