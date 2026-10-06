"""Independent continuous-emissivity H/He Radau oracle in comoving log energy.

Imports only separately verified Python physics, never Rust or Rust trajectories.
Quadrature is not a spectrum certificate: independent spectral refinement is required.
"""
import math
import numpy as np
import igm_reference as physics


def phi(z):
    if z < 0 or not math.isfinite(z):
        raise ValueError('nonnegative finite optical depth required')
    return -math.expm1(-z)/z if z else 1.


def psi(z):
    if z < 0 or not math.isfinite(z):
        raise ValueError('nonnegative finite optical depth required')
    if z < .1:
        # Taylor sum with alternating, decreasing terms in this interval.
        term=.5
        answer=term
        for k in range(1,14):
            term *= -z/(k+2)
            answer += term
        return answer
    return (z+math.expm1(-z))/(z*z)


def fixed_rate_moments(n0,energy,q,rates,h):
    """Exact frozen ln(a)-rates with E'=-E and continuous monochromatic source."""
    rates=np.asarray(rates,dtype=float)
    if min(n0,energy,q,h)<0 or np.any(rates<0):
        raise ValueError('nonnegative inputs required')
    lam=float(rates.sum())
    z=lam*h
    r=(lam+1)*h
    return dict(N=n0*math.exp(-z)+q*h*phi(z),
                A=rates*(n0*h*phi(z)+q*h*h*psi(z)),
                U=n0*energy*math.exp(-r)+q*energy*h*phi(r),
                B=rates*energy*(n0*h*phi(r)+q*h*h*psi(r)),
                R=energy*(n0*h*phi(r)+q*h*h*psi(r)))


def spectral_grid(config,spectral_panels,order=2,grid='uniform'):
    from scipy.special import roots_legendre
    if spectral_panels<1 or order<1 or int(spectral_panels)!=spectral_panels or int(order)!=order:
        raise ValueError('positive integer spectral panels and order required')
    s0,s1=-math.log1p(config['z_start']),-math.log1p(config['z_end'])
    a=s0+math.log(config['energy_min_ev'])
    b=s1+math.log(config['energy_max_ev'])
    x,w=roots_legendre(order)
    if grid=='uniform':
        bounds=[a,b]
    elif grid=='threshold-bands':
        energies=[config['energy_min_ev'],config['energy_max_ev'],*physics.CUTOFF]
        bounds=sorted({a,b,*[t+math.log(e) for t in (s0,s1) for e in energies if a<t+math.log(e)<b]})
    else:
        raise ValueError('unknown spectral grid')
    if spectral_panels*order*(len(bounds)-1)>config['max_packets']:
        raise ValueError('spectral node resource limit')
    edges=np.concatenate([np.linspace(left,right,spectral_panels+1)[:-1] for left,right in zip(bounds[:-1],bounds[1:])]+[np.array([b])])
    half=np.diff(edges)/2
    eta=((edges[:-1]+edges[1:])[:,None]/2+half[:,None]*x).ravel()
    weights=(half[:,None]*np.broadcast_to(w,(len(half),order))).ravel()
    return eta,weights


def source_derivative(config,s,eta,weights,mask=None):
    energy=np.exp(eta-s)
    if mask is None:
        mask=(energy>=config['energy_min_ev'])&(energy<=config['energy_max_ev'])
    norm=1/config['energy_min_ev']-1/config['energy_max_ev']
    return np.where(mask,config['source_rate']*weights/(norm*energy*physics.background(config,s)['H']),0.)


def segment_masks(enter,leave,crossings,left,right):
    """One-sided topology on an event-bounded interval, even adjacent floats."""
    if not left<right:
        raise ValueError('positive event interval required')
    source=(enter<right)&(leave>left)
    channels=crossings>left
    return source,channels[:,0],channels


def solve_history(config,output_ln_a=None,spectral_panels=64,order=2,rtol=1e-11,atol=1e-14,method='Radau',grid='uniform'):
    """Coupled continuous source ODE, event-local time and mixed source/log counts.

    On source-active nodes the coordinate is photon count, initially exactly zero.
    After source switches off the coordinate is optical depth from the last event,
    and authoritative log-count carries between segments. No extinction deletion,
    clipping, source pulse, or spectrum renormalization occurs.
    """
    from scipy.integrate import solve_ivp,quad
    from scipy.sparse import lil_matrix
    import time
    started=time.monotonic()
    if method not in ('Radau','BDF'):
        raise ValueError('Radau or BDF required')
    s0,s1=-math.log1p(config['z_start']),-math.log1p(config['z_end'])
    if not s0<s1:
        raise ValueError('increasing ln(a) interval required')
    times=np.linspace(s0,s1,int(config['output_panels'])+1) if output_ln_a is None else np.asarray(output_ln_a,dtype=float)
    if times[0]!=s0 or times[-1]!=s1 or np.any(np.diff(times)<=0):
        raise ValueError('exact endpoints and increasing output coordinates required')
    eta,weights=spectral_grid(config,spectral_panels,order,grid)
    n=len(eta)
    enter=eta-math.log(config['energy_max_ev'])
    leave=eta-math.log(config['energy_min_ev'])
    crossings=eta[:,None]-np.log(physics.CUTOFF)[None,:]
    events=np.r_[times,enter,leave,crossings.ravel()]
    events=np.unique(events[(events>=s0)&(events<=s1)])
    f=physics.he_ratio(config)
    initial=np.array([config['x_hii'],config['x_heii'],config['x_heiii'],0.])
    initial[3]=1.5*physics.KB*config['temperature_k']*(1+f+initial[0]+f*(initial[1]+2*initial[2]))
    gas=initial.copy()
    gas_delta=0.
    logs=np.full(n,-np.inf)
    ledger=np.zeros(len(physics.LEDGERS)+4)
    # Added fields are emitted_N, emitted_E, out_N, out_E.
    L=len(physics.LEDGERS)
    scale=np.ones(4+n+len(ledger))
    scale[3]=physics.EV
    for i in physics.ENERGY_LEDGERS|{L+1,L+3}:
        scale[4+n+i]=physics.EV
    scale[4+n+L-1]=1e15
    rows=[]
    stats=dict(method=method,rtol=rtol,atol=atol,source_mode='continuous_comoving_eta',spectral_panels=spectral_panels,spectral_grid=grid,quadrature_order=order,spectral_nodes=n,nfev=0,njev=0,nlu=0,steps=0,segments=0,completed=False,min_forced_count=0.,accepted_number_budget_ratio=0.,accepted_energy_budget_ratio=0.)
    # Uniform bounds cover stock and source/owner underflows over physical time;
    # replenishment is included, unlike a source-free packet-only stock bound.
    tiny=np.finfo(float).tiny
    duration_bound=(s1-s0)/physics.background(config,s1)['H']
    under_n=n*tiny+16*n*tiny*duration_bound
    under_e=n*tiny*config['energy_max_ev']*physics.EV+16*n*tiny*duration_bound*(1+config['energy_max_ev']*physics.EV)
    if under_n>=1e-20 or under_e>=1e-30:
        raise RuntimeError('underflow envelope exceeds frozen limits')
    stats.update(ieee_underflow_N_bound=under_n,ieee_underflow_E_bound=under_e)

    def make_row(s):
        energy=np.exp(eta-s)
        count=np.exp(logs)
        active=crossings[:,0]>s
        count=np.where(active,count,0.)
        v=physics.evaluate(config,s,gas,energy,count,crossings>s)
        emitted_n,emitted_e,out_n,out_e=ledger[L:]
        row=dict(ln_a=s,z=v['bg']['z'],x_hii=gas[0],x_heii=gas[1],x_heiii=gas[2],w=gas[3],T=v['T'],Tcmb=v['bg']['Tcmb'],ne_per_h=v['ne_per_h'],Gamma_hi=v['Gamma'][0],Gamma_hei=v['Gamma'][1],Gamma_heii=v['Gamma'][2],Nactive=float(count.sum()),Eactive=physics.EV*float(energy@count),emitted_N=emitted_n,emitted_E=emitted_e,out_N=out_n,out_E=out_e)
        row.update(zip(physics.LEDGERS,ledger[:L]))
        row['number_residual']=row['Nactive']+sum(ledger[:3])+out_n-emitted_n
        row['energy_residual']=gas[3]-initial[3]+physics.binding(gas,config)-physics.binding(initial,config)+row['Eactive']+sum(ledger[10:14])+out_e-emitted_e
        exact_n=config['source_rate']*quad(lambda t:1/physics.background(config,t)['H'],s0,s,epsabs=.001,epsrel=1e-13)[0]
        mean=math.log(config['energy_max_ev']/config['energy_min_ev'])/(1/config['energy_min_ev']-1/config['energy_max_ev'])
        row.update(emitted_N_exact=exact_n,emitted_E_exact=exact_n*mean*physics.EV,source_N_error=emitted_n-exact_n,source_E_error=emitted_e-exact_n*mean*physics.EV,ieee_underflow_N_bound=under_n,ieee_underflow_E_bound=under_e)
        return row

    rows.append(make_row(s0))
    for previous,endpoint in zip(events[:-1],events[1:]):
        source,active,channel=segment_masks(enter,leave,crossings,previous,endpoint)
        source=source&(config['source_rate']>0)
        forced=source&active
        logbase=logs.copy()
        coordinate=np.where(forced,np.exp(logbase),0.)
        y0=np.r_[gas,coordinate,ledger]/scale
        y0[3]=gas_delta/physics.EV

        def decode(y):
            p=y*scale
            p[3]+=initial[3]
            photon_coord=p[4:4+n]
            with np.errstate(under='ignore'):
                counts=np.where(forced,photon_coord,np.exp(logbase-photon_coord))
            return p,np.where(active,counts,0.)

        def fun(xi,y):
            s=previous+xi
            p,counts=decode(y)
            energy=np.exp(eta-s)
            v=physics.evaluate(config,s,p[:4],energy,counts,channel)
            H=v['bg']['H']
            q=source_derivative(config,s,eta,weights,source)
            photon=np.where(forced,q+v['photon_dt']/H,np.where(active,v['opacity']/H,0.))
            ld=np.r_[v['photo'],v['ci'],v['rr'],v['dr'],v['escape'],v['work'],v['cmb_reservoir'],v['redshift'],v['ci_floor'],v['ce_cap'],v['excluded_dr'],1.]/H
            extra=np.array([q.sum(),physics.EV*(energy@q),q[~active].sum(),physics.EV*(energy[~active]@q[~active])])
            return np.r_[v['gas_dt']/H,photon,ld,extra]/scale

        def jac(xi,y):
            s=previous+xi
            matrix=lil_matrix((len(y),len(y)))
            base=fun(xi,y)
            for col in range(4):
                step=math.sqrt(np.finfo(float).eps)*max(abs(y[col]),1.)
                z=y.copy();z[col]+=step
                matrix[:,col]=((fun(xi,z)-base)/step)[:,None]
            p,count=decode(y)
            E=np.exp(eta-s)
            v=physics.evaluate(config,s,p[:4],E,count,channel)
            neutral=np.array([1-p[0],f*(1-p[1]-p[2]),f*p[1]])
            owner=physics.C*v['bg']['nH']*physics.cross_sections(E,channel)*neutral[None,:]/v['bg']['H']
            dc=np.where(active,np.where(forced,1.,-count),0.)
            derivative=owner*dc[:,None]
            matrix[0,4:4+n]=derivative[:,0]
            if f:
                matrix[1,4:4+n]=(derivative[:,1]-derivative[:,2])/f
                matrix[2,4:4+n]=derivative[:,2]/f
            matrix[3,4:4+n]=np.sum(derivative*(E[:,None]-physics.CHI),axis=1)
            for k in range(n):
                if forced[k]: matrix[4+k,4+k]=-v['opacity'][k]/v['bg']['H']
            for i in range(3): matrix[4+n+i,4:4+n]=derivative[:,i]
            matrix[4+n+13,4:4+n]=E*dc
            return matrix.tocsc()

        h=endpoint-previous
        solution=solve_ivp(fun,(0.,h),y0,method=method,jac=jac,rtol=rtol,atol=atol)
        if not solution.success or solution.t[-1]!=h:
            raise RuntimeError(f'continuous reference failed at {previous}: {solution.message}')
        accepted=solution.y*scale[:,None]
        delta_energy=accepted[3].copy()
        accepted[3]+=initial[3]
        if not np.all(np.isfinite(accepted)) or np.any(accepted[:3]<0) or np.any(accepted[0]>1) or np.any(accepted[1]+accepted[2]>1) or np.any(accepted[4:4+n]<0):
            raise RuntimeError(f'nonphysical accepted state at {endpoint}: minimum coordinate={accepted[4:4+n].min():.17g}, minimum fraction={accepted[:3].min():.17g}')
        # Admit cumulative invariants at every accepted Radau state, not only
        # requested output samples. Evaluate observables, never repair ledgers.
        sample_s=previous+solution.t
        sample_E=np.exp(eta[:,None]-sample_s[None,:])
        coord_all=accepted[4:4+n]
        with np.errstate(under='ignore'):
            sample_N=np.where(forced[:,None],coord_all,np.exp(logbase[:,None]-coord_all))
        sample_N=np.where(active[:,None],sample_N,0.)
        ld_all=accepted[4+n:]
        nr=sample_N.sum(axis=0)+ld_all[:3].sum(axis=0)+ld_all[L+2]-ld_all[L]
        bind=physics.EV*(physics.CHI[0]*accepted[0]+f*(physics.CHI[1]*accepted[1]+sum(physics.CHI[1:])*accepted[2]))
        er=delta_energy+bind-physics.binding(initial,config)+physics.EV*(sample_E*sample_N).sum(axis=0)+ld_all[10:14].sum(axis=0)+ld_all[L+3]-ld_all[L+1]
        nb=float(np.max(np.abs(nr)/(1e-10*np.maximum(ld_all[L],1e-10))))
        eb=float(np.max(np.abs(er)/(1e-10*np.maximum(ld_all[L+1]+ld_all[11]+ld_all[10]+np.abs(ld_all[12]),1e-20))))
        stats['accepted_number_budget_ratio']=max(stats['accepted_number_budget_ratio'],nb)
        stats['accepted_energy_budget_ratio']=max(stats['accepted_energy_budget_ratio'],eb)
        if nb>1 or eb>1:
            raise RuntimeError(f'accepted-state budget failure: number ratio={nb}, energy ratio={eb}')
        gas=accepted[:4,-1].copy()
        gas_delta=delta_energy[-1]
        coord=accepted[4:4+n,-1]
        if np.any(forced&(coord<=0)):
            raise RuntimeError('source-active endpoint lost positive count')
        logs[~forced]=logbase[~forced]-coord[~forced]
        logs[forced]=np.log(coord[forced])
        ledger=accepted[4+n:,-1].copy()
        exiting=active&(crossings[:,0]<=endpoint)
        if np.any(exiting):
            amount=float(np.exp(logs[exiting]).sum())
            ledger[L+2]+=amount
            ledger[L+3]+=amount*physics.CUTOFF[0]*physics.EV
            logs[exiting]=-np.inf
        # Inspect accepted EOS, never clip or project it.
        electron=accepted[0]+f*(accepted[1]+2*accepted[2])
        temp=2*accepted[3]/(3*physics.KB*(1+f+electron))
        if np.any(temp<1) or np.any(temp>1e6): raise RuntimeError('accepted EOS outside provider domain')
        for key in ('nfev','njev','nlu'): stats[key]+=getattr(solution,key)
        stats['steps']+=len(solution.t)-1
        stats['segments']+=1
        if stats['steps']>config['max_steps']: raise RuntimeError('accepted-step resource limit')
        if endpoint in times: rows.append(make_row(endpoint))
    stats.update(completed=True,runtime_s=time.monotonic()-started)
    nodes=np.column_stack((eta,weights,np.exp(eta-s1),enter,leave,logs,np.exp(logs)))
    return dict(rows=rows,stats=stats,nodes=nodes)


def main():
    import argparse,csv,hashlib,json,time
    from pathlib import Path
    import scipy
    from igm_compare import compare_rows
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',required=True);p.add_argument('--output',required=True)
    p.add_argument('--spectral-panels',type=int,default=64);p.add_argument('--order',type=int,default=2)
    p.add_argument('--spectral-grid',choices=['uniform','threshold-bands'],default='uniform')
    p.add_argument('--rtol',type=float,default=1e-11);p.add_argument('--atol',type=float,default=1e-14)
    p.add_argument('--method',choices=['Radau','BDF'],default='Radau');p.add_argument('--times-csv')
    args=p.parse_args()
    config_path=Path(args.config);config=physics.read_config(config_path)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    out.joinpath('config.cfg').write_bytes(config_path.read_bytes())
    out.joinpath('producing_igm_continuous_reference.py').write_bytes(Path(__file__).read_bytes())
    out.joinpath('producing_igm_reference.py').write_bytes(Path(physics.__file__).read_bytes())
    manifest=dict(source_mode='continuous_comoving_eta',implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),physics_sha256=hashlib.sha256(Path(physics.__file__).read_bytes()).hexdigest(),config_sha256=hashlib.sha256(config_path.read_bytes()).hexdigest(),scipy=scipy.__version__,numpy=np.__version__,method=args.method,rtol=args.rtol,atol=args.atol,spectral_panels=args.spectral_panels,spectral_grid=args.spectral_grid,quadrature_order=args.order,legacy_birth_panels_ignored=True,legacy_energy_panels_ignored=True)
    out.joinpath('manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    times=None
    if args.times_csv:
        with open(args.times_csv) as f: times=np.array([float(r['ln_a']) for r in csv.DictReader(f)])
    start=time.monotonic()
    try:
        result=solve_history(config,times,args.spectral_panels,args.order,args.rtol,args.atol,args.method,args.spectral_grid)
    except Exception as e:
        status=dict(completed=False,error_type=type(e).__name__,error=str(e),runtime_s=time.monotonic()-start)
        out.joinpath('status.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status));raise SystemExit(1)
    validation=compare_rows(result['rows'],result['rows'])
    stats=result['stats'];stats.update(ledger_valid=validation['passed'],budget_ratios=validation['budgets']['candidate'])
    with out.joinpath('history.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(result['rows'][0]));writer.writeheader();writer.writerows(result['rows'])
    with out.joinpath('nodes_final.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['eta','weight','energy_ev','source_enter','source_leave','log_count','count']);writer.writerows(result['nodes'])
    out.joinpath('status.json').write_text(json.dumps(stats,indent=2)+'\n');print(json.dumps(stats))
    if not stats['ledger_valid']: raise SystemExit(2)

if __name__=='__main__': main()
