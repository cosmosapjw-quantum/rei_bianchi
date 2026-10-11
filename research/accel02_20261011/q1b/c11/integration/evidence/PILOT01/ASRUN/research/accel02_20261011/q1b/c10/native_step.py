"""Bounded positive photon functional + four-variable implicit native gas step.

Only fixed source/incident measures enter gas Newton. The map is first-order
source/redshift then backward Euler absorption/gas. All ledgers are operator
counters; no ledger residual is assigned to a physical counter. No full-history
or continuum error claim follows from a bounded step.
"""
from __future__ import annotations
import hashlib
import math
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
sys.path.insert(0,str(HERE.parent.parent/'n1'))
from provider import Native
from source_entry import integrate_source,advance_source,provider_event_times
from positive_absorption import prepare_incident,absorb
EV_ERG=1.602176634e-12
KB=1.380649e-16
CHI=np.array([13.598434599702,24.587389011,54.41776])
CELL_SHA='e29245acfee5be4d43c27935e2abd212d578685efa70dffbeffa8f96dd3e4b6f'
COUNTER_NAMES=('Nsource','Nabs','Esource_eV','Eescape_eV','Wrad_eV','Wthermal_eV','ECMB_eV')


def gas_temperature(y,g):
    h,he1,he2,w=np.asarray(y,float)
    f=g['nHe']/g['nH']
    return 2*w*EV_ERG/(3*KB*(1+f+h+f*(he1+2*he2)))


def gas_admissible(y,g):
    y=np.asarray(y,float)
    if y.shape!=(4,) or not np.isfinite(y).all():return False
    h,he1,he2,w=y
    return bool(0<=h<=1 and he1>=0 and he2>=0 and he1+he2<=1 and w>0
                and 1<=gas_temperature(y,g)<=1e6)


def gas_energy_eV(y,nH_ref,nHe_ref):
    h,he1,he2,w=np.asarray(y,float)
    return nH_ref*(w+CHI[0]*h)+nHe_ref*(CHI[1]*he1+(CHI[1]+CHI[2])*he2)


def implicit_gas_solve(y0,h,g,evaluate,*,residual_rtol=1e-11,max_iterations=18):
    """Admissible damped Newton using central/one-sided finite differences.

    Domain-invalid finite differences and line-search trials are never sent to
    native gas. Fixed residual scales are fractions1 and initial thermal w.
    Starting neutral helium is handled by one-sided admissible probes.
    """
    y0=np.asarray(y0,float)
    if not gas_admissible(y0,g):raise ValueError('ENTRY_GAS_DOMAIN_INITIAL')
    if not (math.isfinite(h) and h>0 and 0<residual_rtol<=1e-11):raise ValueError('ENTRY_SOLVER_CONTROLS')
    scales=np.r_[np.ones(3),y0[3]]
    calls=0
    def residual(y):
        nonlocal calls
        if not gas_admissible(y,g):raise ValueError('ENTRY_GAS_DOMAIN_TRIAL')
        f,payload=evaluate(y)
        calls+=1
        f=np.asarray(f,float)
        if f.shape!=(4,) or not np.isfinite(f).all():raise ArithmeticError('ENTRY_RHS_DOMAIN')
        return (y-y0-h*f)/scales,payload
    y=y0.copy(); rejected=0; sided=[0,0]
    for iteration in range(max_iterations+1):
        r,payload=residual(y);norm=float(np.max(np.abs(r)))
        if norm<=residual_rtol:
            return y,payload,dict(iterations=iteration,evaluations=calls,scaled_residual=norm,
                residual_scales=scales.tolist(),residual_target=residual_rtol,
                rejected_line_search_trials=rejected,central_probes=sided[0],one_sided_probes=sided[1],
                fraction_projection=False)
        if iteration==max_iterations:break
        jac=np.empty((4,4))
        for j in range(4):
            # Prospective fixed finite-difference size; do not infer accuracy
            # from the derivative itself. Native residual remains acceptance.
            eps=1e-6*scales[j]
            for _ in range(30):
                yp=y.copy();ym=y.copy();yp[j]+=eps;ym[j]-=eps
                vp,vm=gas_admissible(yp,g),gas_admissible(ym,g)
                if vp or vm:break
                eps*=.5
            if not(vp or vm):raise ArithmeticError('ENTRY_NO_ADMISSIBLE_FD_DIRECTION')
            if vp and vm:
                rp,_=residual(yp);rm,_=residual(ym);jac[:,j]=(rp-rm)/(2*eps);sided[0]+=1
            elif vp:
                rp,_=residual(yp);jac[:,j]=(rp-r)/eps;sided[1]+=1
            else:
                rm,_=residual(ym);jac[:,j]=(r-rm)/eps;sided[1]+=1
        delta=np.linalg.solve(jac,-r)
        alpha=1.;accepted=False
        for _ in range(45):
            trial=y+alpha*delta
            if gas_admissible(trial,g):
                rt,_=residual(trial)
                if float(np.max(np.abs(rt)))<=(1-1e-4*alpha)*norm:
                    y=trial;accepted=True;break
            rejected+=1;alpha*=.5
        if not accepted:raise ArithmeticError('ENTRY_ADMISSIBLE_NEWTON_LINE_SEARCH_FAILED')
    raise ArithmeticError('ENTRY_NATIVE_GAS_RESIDUAL_NOT_CONVERGED')


def split_thermal_work(native,gas,g,lambdas,U):
    """Return explicit thermal eV/refcm3/s and check the native combined owner."""
    nHref=g['nH']*g['a_rel']**3
    thermal=2*g['H']*nHref*gas[3]
    radiation=math.fsum((np.asarray(lambdas)*np.asarray(U)).ravel())
    combined=thermal+radiation
    native_eV=float(native[5])/EV_ERG
    scale=max(abs(combined),abs(native_eV))
    error=abs(combined-native_eV)/scale if scale else (0. if native_eV==0 else math.inf)
    if error>1e-12:raise ArithmeticError('ENTRY_NATIVE_WORK_SPLIT_MISMATCH')
    return thermal,dict(relative_work_owner_disagreement=error,
        native_combined_eV_s=native_eV,thermal_eV_s=thermal,radiation_eV_s=radiation,
        native_combined_integrated=False)


class NativeCell:
    def __init__(self,binary=HERE.parent/'native/target/release/rei_q1b_cell_native_v1'):
        self.binary=Path(binary); self.binary_sha256=hashlib.sha256(self.binary.read_bytes()).hexdigest()
        if self.binary_sha256!=CELL_SHA:raise ValueError('ENTRY_NATIVE_BINARY_IDENTITY')
        self.native=Native(self.binary);self.calls=0
    def rhs(self,t,g,gas,cells):
        cells=np.asarray(cells,float).reshape(-1,13)
        values=np.r_[t,g['a_rel'],g['b'],g['H'],g['s'],g['nH'],g['nHe'],gas,g['Tcmb_K'],len(cells),cells.ravel()]
        result=self.native.call('CELL_RHS_V1',values);self.calls+=1
        if len(result)!=15+2*len(cells):raise ValueError('ENTRY_NATIVE_ABI_SHAPE')
        return result
    def close(self):
        self.native.close();self.native.proc.stdout.close();self.native.proc.stderr.close()
    def __enter__(self):return self
    def __exit__(self,*args):self.close()


def initial_state(source,*,saved_initial=None):
    """Use saved C09B exact C2 moments where supplied, without source-IC replay."""
    p=source.provider
    if saved_initial is None:raise ValueError('ENTRY_REQUIRES_SAVED_C09B_IC')
    N=np.asarray(saved_initial['initial_N']).copy();U=np.asarray(saved_initial['initial_U_eV']).copy()
    if N.shape!=(len(source.mu),len(source.edges)-1):raise ValueError('ENTRY_INITIAL_GRID_SHAPE')
    support=np.stack(np.broadcast_arrays(source.edges[:-1][None,:]+np.zeros_like(N),
        np.minimum(source.edges[1:],50000.)[None,:]+np.zeros_like(N)),axis=-1)
    # Dormant-cell support has zero width; no physical positive support yet.
    support[:,:,1]=np.maximum(support[:,:,0],support[:,:,1])
    g=p.geometry(0.)
    return dict(t_s=0.,gas=p.initial_gas.copy(),N=N,U_eV=U,R=np.ones_like(N),support=support,
        counters={k:0. for k in COUNTER_NAMES},nH_ref=g['nH'],nHe_ref=g['nHe'])


def positive_native_step(state,t1,source,opacity,native):
    t0=float(state['t_s']);h=float(t1)-t0;p=source.provider;g=p.geometry(t1)
    events=provider_event_times(source,t0,t1)
    integrated=integrate_source(source,t0,t1,event_times=events)
    incident=advance_source(state['N'],state['U_eV'],integrated)
    nangle,nenergy=incident['N'].shape
    _,mu,R=p.ray(np.ones(nangle),source.mu,t1)
    if not np.array_equal(R,integrated['R1']):raise ValueError('ENTRY_ENDPOINT_RAY_IDENTITY')
    lambdas=g['H']+g['s']*(3*mu*mu-1)
    prep=[];supports=[]
    for a in range(nangle):
        for j in range(nenergy):
            lo=float(source.edges[j]);hi=min(float(source.edges[j+1]),50000./R[a])
            if hi<lo:
                if incident['N'][a,j]!=0 or incident['U_eV'][a,j]!=0:raise ValueError('ENTRY_DORMANT_NONZERO')
                hi=lo  # support metadata only; not a state projection
            supports.append([lo,hi])
            try:
                prep.append(prepare_incident(float(incident['N'][a,j]),float(incident['U_eV'][a,j]),
                    float(R[a]),lo,hi,opacity,orders=(64,128),rtol=1e-7))
            except Exception as exc:
                exc.add_note(f'angle={a},energy_cell={j},q_left={lo},q_right={hi},t0={t0},t1={t1}')
                raise
    def evaluate(gas):
        lower=np.array([g['nH']*(1-gas[0]),g['nHe']*(1-gas[1]-gas[2]),g['nHe']*gas[1]])
        results=[absorb(cell,lower,h) for cell in prep]
        cells=np.zeros((len(prep),13))
        cells[:,0]=np.repeat(mu,nenergy);cells[:,1]=np.repeat(R,nenergy)
        cells[:,2]=np.repeat(lambdas,nenergy)
        for i,result in enumerate(results):
            cells[i,3:5]=[result['N'],result['U']]
            cells[i,7:10]=result['K0'];cells[i,10:13]=result['KE']
        out=native.rhs(t1,g,gas,cells)
        return out[:4],(out,results,cells)
    gas,(out,absorbed,cells),solver=implicit_gas_solve(state['gas'],h,g,evaluate)
    N=cells[:,3].reshape(nangle,nenergy);U=cells[:,4].reshape(nangle,nenergy)
    thermal,workdiag=split_thermal_work(out,gas,g,cells[:,2],cells[:,4])
    increments=dict(Nsource=math.fsum(integrated['dN'].ravel()),
        Nabs=math.fsum(float(v) for a in absorbed for v in a['number_absorbed_species']),
        Esource_eV=math.fsum(integrated['injected_energy_eV'].ravel()),
        Eescape_eV=h*out[4]/EV_ERG,Wrad_eV=math.fsum(incident['radiation_work_eV'].ravel()),
        Wthermal_eV=h*thermal,ECMB_eV=h*out[14]/EV_ERG)
    counters={key:state['counters'][key]+increments[key] for key in COUNTER_NAMES}
    nh,he=state['nH_ref'],state['nHe_ref']
    e0=math.fsum(state['U_eV'].ravel())+gas_energy_eV(state['gas'],nh,he)
    e1=math.fsum(U.ravel())+gas_energy_eV(gas,nh,he)
    energy=math.fsum([e1,-e0,increments['Wrad_eV'],increments['Wthermal_eV'],
        increments['Eescape_eV'],-increments['Esource_eV'],-increments['ECMB_eV']])
    number=math.fsum([math.fsum(N.ravel()),-math.fsum(state['N'].ravel()),increments['Nabs'],-increments['Nsource']])
    nabs_owner=h*out[7]
    abs_scale=max(abs(nabs_owner),abs(increments['Nabs']))
    abs_error=abs(nabs_owner-increments['Nabs'])/abs_scale if abs_scale else 0.
    if abs_error>1e-12:raise ArithmeticError('ENTRY_NATIVE_ABSORPTION_COUNTER_MISMATCH')
    return dict(t_s=float(t1),gas=gas,N=N,U_eV=U,R=np.repeat(R[:,None],nenergy,axis=1),
        support=np.array(supports).reshape(nangle,nenergy,2),counters=counters,nH_ref=nh,nHe_ref=he,
        diagnostics=dict(source=integrated['diagnostics'],source_pairing=incident['diagnostics'],
            newton=solver,work=workdiag,local_energy_residual_eV=energy,local_number_residual=number,
            native_absorbed_counter_disagreement=abs_error,native_local_number_residual=float(out[12]),
            native_local_energy_residual=float(out[13]),
            gas_temperature_K=float(out[11]),gamma=out[8:11].tolist(),increments=increments,
            source_events_s=list(events),prepared_cells=len(prep),claim='BOUNDED_FIRST_ORDER_SPLIT_STEP_ONLY'))
