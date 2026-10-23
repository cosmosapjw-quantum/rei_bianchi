#!/usr/bin/env python3
"""One bounded offline diagnostic. Raw arrays and partial failures survive."""
import os
import sys
import json
import time
import hashlib
import platform
import resource
import traceback
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp, quad
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from local_flows import *

OUT = BASE/'results'
FIG = BASE/'figures'
CHECKS = []
ARRAYS = {}
DATA = {'thermal': [], 'beta': [], 'timing': []}
START = time.perf_counter()
CPU_START = time.process_time()


def plain(value):
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, np.generic): return value.item()
    raise TypeError(type(value).__name__)


def write(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, default=plain, allow_nan=False)+'\n')


def check(name, value, tolerance=None, detail=None):
    passed = bool(value) if tolerance is None else bool(np.isfinite(value) and value <= tolerance)
    CHECKS.append(dict(name=name, passed=passed, value=value, tolerance=tolerance, detail=detail))
    write('checks.json', CHECKS)
    if not passed:
        raise AssertionError(f'{name}: observed {value}, tolerance {tolerance}')


def counters(sol):
    return dict(nfev=sol.nfev, njev=sol.njev, nlu=sol.nlu, success=sol.success, message=sol.message)


def timed(label, solve, repeats=3):
    # Warmup excluded. Seven independent batches; setup/reference costs excluded.
    warm = solve()
    times = []
    for _ in range(7):
        t0 = time.perf_counter()
        for _ in range(repeats): result = solve()
        times.append((time.perf_counter()-t0)/repeats)
    row = dict(label=label, seconds_per_solve=times, median_s=float(np.median(times)),
               range_s=[min(times),max(times)], solves_per_batch=repeats, batches=7,
               warmup_solves=1, clock='perf_counter wall; integration + output + reconstruction; excludes setup/reference',
               counters=counters(warm) if hasattr(warm,'nfev') else {'exact_subflow_stages': 3*256})
    DATA['timing'].append(row)
    return row


def solve_thermal(Ti, grid, reduced, method='DOP853', reference=False):
    xi=.9
    U0,I0=energies(xi,0.,Ti)
    if reference:
        sol=solve_ivp(lambda s,y: reference_thermal_rhs(s,y,Ti,U0+I0),
                      [0,grid[-1]],[xi,0.,0.],method='Radau',t_eval=grid,rtol=2e-12,atol=1e-14)
    else:
        sol=solve_ivp(lambda s,y: reduced_rhs(s,y,Ti) if reduced else thermal_rhs(s,y,Ti),
                      [0,grid[-1]],[0.] if reduced else [xi,0.],method=method,
                      t_eval=grid,rtol=1e-9,atol=1e-12)
        if reduced:
            w=sol.y[0]; x=reconstruct_x(w,Ti)
        else: x,w=sol.y
        U,I=energies(x,w,Ti)
        sol.production=np.array([x,w,(U0+I0-U-I)/(U0+I0)])
    if not sol.success: raise RuntimeError(sol.message)
    return sol


def thermal_checks():
    # Complex-step verification, including full matrix entries, in interior states.
    deriv_errors=[]
    for Ti in (100.,1000.,5000.):
        for x,w in ((.35,.03),(.7,.11)):
            T=Ti*np.exp(w); alpha,D,Dw=rate(T)
            cs=1e-25
            alpha_w=np.imag(rate(T*np.exp(1j*cs))[0])/cs
            D_w=np.imag(rate(T*np.exp(1j*cs))[1])/cs
            deriv_errors.extend([abs(alpha_w-alpha*D)/abs(alpha*D), abs(D_w-Dw)/abs(Dw)])
            analytic=thermal_jac(0,[x,w],Ti)
            numeric=np.column_stack([np.imag(thermal_rhs(0,np.array([x,w],complex)+1j*cs*np.eye(2)[i],Ti))/cs for i in range(2)])
            deriv_errors.append(float(np.max(np.abs(analytic-numeric)/np.maximum(np.abs(analytic),1e-30))))
    check('VF_D_Dw_and_thermal_Jacobian_complex_step',max(deriv_errors),1e-7,deriv_errors)
    for Ti in (100.,1000.,5000.):
        setup0=time.perf_counter()
        xi=.9; xf=xi/4
        lo=np.log((1+xi)/(1+xf))/3
        hi=np.log((1+xi)/(1+xf))
        wf=brentq(lambda w: reconstruct_x(w,Ti)-xf,lo,hi,xtol=1e-14)
        sf, sf_quad_error=quad(lambda w: 1/reduced_rhs(0,[w],Ti)[0],0,wf,epsabs=2e-12,epsrel=2e-12)
        setup=time.perf_counter()-setup0
        grid=np.linspace(0,sf,129)
        ws=np.r_[0.,1e-12,np.linspace(wf/15,wf,15)]
        q=np.array([1.5*quad(lambda z:1/rate(Ti*np.exp(z))[1],0,w,epsabs=1e-13,epsrel=1e-13)[0] for w in ws])
        check(f'primitive_{Ti:g}',float(np.max(np.abs(primitive(ws,Ti)-q))),2e-11)
        check(f'root_endpoint_{Ti:g}',abs(reconstruct_x(wf,Ti)-xf),2e-11)
        r0=time.perf_counter(); ref=solve_thermal(Ti,grid,False,reference=True); reference_cost=time.perf_counter()-r0
        full=solve_thermal(Ti,grid,False); red=solve_thermal(Ti,grid,True)
        xr,wr,eg=ref.y; U0,I0=energies(xi,0.,Ti); Escale=U0+I0
        Ur,Ir=energies(xr,wr,Ti)
        energy=(Ur+Ir+eg*Escale-Escale)/Escale
        check(f'reference_energy_{Ti:g}',float(np.max(np.abs(energy))),2e-10)
        errors={}
        for name,sol in [('full',full),('reduced',red)]:
            x,w,_=sol.production; U,I=energies(x,w,Ti); T=Ti*np.exp(w)
            errors[name]=dict(x_scaled=float(np.max(np.abs(x-xr))/xf),T_relative=float(np.max(np.abs(np.exp(w-wr)-1))))
            check(f'{name}_x_{Ti:g}',errors[name]['x_scaled'],5e-8)
            check(f'{name}_T_{Ti:g}',errors[name]['T_relative'],5e-8)
            check(f'{name}_physical_{Ti:g}', bool(np.all(x>=0) and np.all(1-x>=0) and np.all(T>=100) and np.all(T<=10000) and np.all(np.diff(T)>0) and np.all(np.diff(U)<0)))
            alpha,D,_=rate(T); kinetic=KB*T*alpha*(1.5+D)
            check(f'{name}_positive_kinetic_moment_{Ti:g}',bool(np.all(kinetic>0)))
            f,g=np.array([thermal_rhs(s,[xx,ww],Ti) for s,xx,ww in zip(grid,x,w)]).T
            # EOS identity: (3/2)k[(1+x)Tdot+T xdot] = -k T(3/2+D)*a*x².
            lhs=1.5*KB*T*((1+x)*g+f)
            rhs=-KB*T*(1.5+D)*(alpha/rate(Ti)[0])*x*x
            check(f'{name}_EOS_source_identity_{Ti:g}',float(np.max(np.abs(lhs-rhs)/np.maximum(np.abs(rhs),1e-300))),1024*np.finfo(float).eps)
        agreement=max(np.max(np.abs(full.production[0]-red.production[0]))/xf,np.max(np.abs(np.exp(full.production[1]-red.production[1])-1)))
        check(f'full_reduced_{Ti:g}',float(agreement),5e-8)
        a,D,_=rate(Ti)
        correct=thermal_rhs(0,[xi,0],Ti)[1]
        omitted=-(2/3)*(xi*xi/(1+xi))*(1.5+D)
        check(f'omitted_Cdot_control_sign_detected_{Ti:g}',bool(correct>0 and omitted<0))
        row=dict(Ti_K=Ti,nB_m3=1e12,alpha_i_m3_s=rate(Ti)[0],s_final=sf,t_final_s=sf/(1e12*rate(Ti)[0]),w_final=wf,
                 setup_wall_s=setup,s_final_quadrature_error=sf_quad_error,reference_wall_s=reference_cost,
                 reference_counters=counters(ref),full_counters=counters(full),reduced_counters=counters(red),errors=errors,
                 full_reduced_error=agreement,reference_energy_residual_max=float(np.max(np.abs(energy))),
                 control={'correct_wdot_s':correct,'omitted_particle_count_wdot_s':omitted})
        DATA['thermal'].append(row)
        key=f'thermal_{int(Ti)}'
        ARRAYS[key+'_s']=grid; ARRAYS[key+'_reference']=ref.y
        ARRAYS[key+'_full']=full.production; ARRAYS[key+'_reduced']=red.production
        ARRAYS[key+'_energy_residual']=energy; ARRAYS[key+'_primitive_w']=ws
        ARRAYS[key+'_primitive_quadrature']=q; ARRAYS[key+'_primitive_closed']=primitive(ws,Ti)
        for name,reduced in [('full',False),('reduced',True)]:
            tr=timed(f'thermal_{int(Ti)}_{name}',lambda reduced=reduced:solve_thermal(Ti,grid,reduced))
            tr['reference_error']=errors[name]
        write('partial_results.json',DATA); np.savez(OUT/'raw_arrays.npz',**ARRAYS)


def beta_checks():
    sample=np.linspace(0,4,129)
    for rho in (.1,1.,10.):
        r0=time.perf_counter(); exact=bessel_reference(sample,rho); bessel_setup=time.perf_counter()-r0
        r0=time.perf_counter()
        ref=solve_ivp(lambda v,y:beta_rhs(v,y,rho),[0,4],[.1,.2,.7],method='Radau',jac=lambda v,y:beta_jac(v,y,rho),t_eval=sample,rtol=2e-12,atol=1e-14)
        radau_cost=time.perf_counter()-r0
        check(f'bessel_Radau_{rho:g}',float(np.max(np.abs(exact-ref.y))),2e-10)
        check(f'n_analytic_Radau_{rho:g}',float(np.max(np.abs(ref.y[0]-.1*np.exp(-sample)))),2e-12)
        check(f'baryons_Radau_{rho:g}',float(np.max(np.abs(np.sum(ref.y,axis=0)-1))),2e-12)
        errs=[]; rows=[]
        for N in (32,64,128,256):
            grid=np.linspace(0,4,N+1); y=strang(rho,N); ex=bessel_reference(grid,rho)
            error=float(np.max(np.abs(y-ex))); errs.append(error)
            check(f'population_min_{rho:g}_{N}',bool(np.min(y)>=-1e-15))
            check(f'baryons_Strang_{rho:g}_{N}',float(np.max(np.abs(np.sum(y,axis=0)-1))),2e-12)
            rows.append(dict(N=N,max_absolute_error=error,minimum=float(np.min(y)),n_analytic_error=float(np.max(np.abs(y[0]-.1*np.exp(-grid))))))
            ARRAYS[f'beta_{rho:g}_{N}_v']=grid; ARRAYS[f'beta_{rho:g}_{N}_strang']=y; ARRAYS[f'beta_{rho:g}_{N}_exact']=ex
        orders=np.log2(np.array(errs[:-1])/np.array(errs[1:]))
        check(f'Strang_decreasing_{rho:g}',bool(np.all(np.diff(errs)<0)))
        check(f'Strang_last_two_orders_{rho:g}',bool(np.all((orders[-2:]>=1.8)&(orders[-2:]<=2.2))),detail=orders)
        grid=np.linspace(0,4,257)
        def adaptive():
            return solve_ivp(lambda v,y:beta_rhs(v,y,rho),[0,4],[.1,.2,.7],method='DOP853',t_eval=grid,rtol=1e-9,atol=1e-12)
        dop=adaptive(); dop_error=float(np.max(np.abs(dop.y-bessel_reference(grid,rho))))
        check(f'DOP_accuracy_at_least_Strang_{rho:g}',dop_error,errs[-1])
        for name,fn,err in [('strang',lambda:strang(rho,256),errs[-1]),('DOP853',adaptive,dop_error)]:
            tr=timed(f'beta_{rho:g}_{name}',fn); tr['max_absolute_reference_error']=err
        row=dict(rho=rho,nB_m3=rho*LAMBDA/rate(1000.)[0],T_K=1000.,steps=rows,orders=orders,
                 bessel_Radau_error=float(np.max(np.abs(exact-ref.y))),bessel_reference_wall_s=bessel_setup,
                 Radau_reference_wall_s=radau_cost,Radau_counters=counters(ref),DOP853_error=dop_error,DOP853_counters=counters(dop))
        DATA['beta'].append(row)
        ARRAYS[f'beta_{rho:g}_reference_v']=sample; ARRAYS[f'beta_{rho:g}_bessel']=exact; ARRAYS[f'beta_{rho:g}_Radau']=ref.y
        ARRAYS[f'beta_{rho:g}_DOP853']=dop.y
        write('partial_results.json',DATA); np.savez(OUT/'raw_arrays.npz',**ARRAYS)
    # Elementary limits check the exact subflows independently across the full grids.
    grid=np.linspace(0,4,257)
    for rho,initial,label in [(1.,(0.,.2,.8),'no_neutrons'),(0.,(.1,.2,.7),'no_RR')]:
        y=strang(rho,256,initial=initial); exact=bessel_reference(grid,rho,initial)
        check('elementary_limit_'+label,float(np.max(np.abs(y-exact))),2e-12)
        ARRAYS['limit_'+label]=y; ARRAYS['limit_'+label+'_exact']=exact
    onset=strang(1.,256,initial=(.1,0.,.9)); onset_exact=bessel_reference(grid,1.,(.1,0.,.9))
    check('source_onset_positive',bool(np.all(onset[1,1:]>0)))
    ARRAYS['source_onset_v']=grid; ARRAYS['source_onset']=onset; ARRAYS['source_onset_bessel']=onset_exact
    tiny=1e-104; trace=strang(1.,256,end=1.,initial=(tiny,0.,1.)); tg=np.linspace(0,1,257)
    source=tiny*(-np.expm1(-tg)); rel=float(np.max(np.abs(trace[1,1:]/source[1:]-1)))
    check('trace_source_positive',bool(np.all(trace[1,1:]>0)))
    check('trace_component_relative_error',rel,1e-10)
    ARRAYS['trace_v']=tg; ARRAYS['trace_state']=trace; ARRAYS['trace_analytic_p']=source
    DATA['onsets']=dict(source_final_p=onset[1,-1],source_Bessel_absolute_error=float(np.max(np.abs(onset-onset_exact))),
                        trace_final_p=trace[1,-1],trace_relative_error=rel,trace_loss_relative_bound=1e-104,
                        tiny_n_inventory=tiny,h_rounding='h remains exactly 1 at binary64; tiny n,p retained separately')
    # Original state-order embedding: A and q agree on retained slots; inactive slots exactly zero.
    A21=np.array([1,1,1,2,2,3,3,3,3,3,4,4,4,6,6,6,6,7,7,7,7])
    q21=np.array([0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3,0,1,2,3])
    inactive=np.array([j for j in range(21) if j not in (0,1,2)])
    errors=[]
    for y in (np.array([.1,.2,.7]),onset[:,-1],trace[:,-1]):
        Y=embed(y); F=embedded_rhs(0,Y,1.); mapped=embed(beta_rhs(0,y,1.))
        check('embedding_inactive_zero_'+str(len(errors)),bool(np.all(Y[inactive]==0) and np.all(F[inactive]==0)))
        errors.extend([float(np.max(np.abs(F-mapped))),abs(float(A21@Y)-float(np.sum(y))),abs(float(q21@Y)-y[1])])
    check('embedding_RHS_baryons_charge',max(errors),2e-12,errors)
    DATA['embedding']={'A21':A21,'q21':q21,'inactive_indices':inactive,'max_error':max(errors)}


def input_checks():
    manifest=json.loads((BASE/'inputs/copy_manifest.json').read_text())
    rows=[]
    for row in manifest['copies']:
        a=row['source_sha256']; b=hashlib.sha256((BASE/row['copy']).read_bytes()).hexdigest()
        rows.append(dict(source=row['source'],copy=row['copy'],source_sha256=a,copy_sha256=b))
        check('input_copy_'+Path(row['copy']).name,a==b)
    DATA['inputs']={'copies':rows,'selected_H_RR':ROW,'chi_H_eV':CHI/EV,'neutron_lifetime_s':1/LAMBDA,
                    'atomic_donor_pin':'8be7533cc97b3302bf42608699d6e8313ed6af8a','sandbox_science_pin':'569f784e78676123513b7390001d317eb62d6372',
                    'PR219_provider_pin':'6a12f3865d9ea427c1391c41caed8bb7cb7ec00d'}
    saved=json.loads((BASE/'inputs/nuclear_saved_metadata.json').read_text())
    Qbare=saved['constants']['Q_J']['n_beta']; Q0=Qbare+CHI
    ledger=Q0-CHI-Qbare
    check('neutron_energy_reference_ledger',abs(ledger)/Qbare,1024*np.finfo(float).eps)
    negative=Qbare-CHI-Qbare
    check('direct_Qbare_as_Q0_control_detected',bool(negative<0 and abs(negative/CHI+1)<1e-10))
    photo=COEFF['photo_VF1996']; dd=photo['2:0']['Eth_eV']+photo['2:1']['Eth_eV']-2*photo['1:0']['Eth_eV']
    check('DD_ionization_reference_eV',abs(dd-51.81),1e-12)
    DATA['energy_reference']={'kind':'algebraic declared-reference convention only; no independently evaluated neutral mass Q0',
                              'Q_bare_saved_J':Qbare,'Q0_declared_J':Q0,'dI_n_beta_J':CHI,'ledger_residual_J':ledger,
                              'negative_control_residual_J':negative,'DD_to_He3III_n_dI_eV':dd,
                              'beta_thermal_partition':'not supplied; no thermally coupled beta admission'}


def figures():
    fig,ax=plt.subplots(1,3,figsize=(13,3.8))
    for row in DATA['thermal']:
        Ti=row['Ti_K']; key=f'thermal_{int(Ti)}'; s=ARRAYS[key+'_s']; ref=ARRAYS[key+'_reference']; red=ARRAYS[key+'_reduced']
        ax[0].plot(s,red[0],label=f'{Ti:g} K reduced'); ax[0].plot(s,ref[0],':',color=ax[0].lines[-1].get_color())
        ax[1].plot(s,Ti*np.exp(red[1]),label=f'{Ti:g} K'); ax[2].plot(s,ARRAYS[key+'_energy_residual'],label=f'{Ti:g} K')
    ax[0].set(xlabel='s = nB alpha(Ti) t',ylabel='HII abundance x',title='Reduced lines; Radau dots')
    ax[1].set(xlabel='s',ylabel='T [K]',title='Escaping RR photons; rising T'); ax[1].set_yscale('log')
    ax[2].set(xlabel='s',ylabel='(U + I + Egamma - E0) / E0',title='Independent Radau energy')
    for a in ax: a.legend(fontsize=7); a.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(FIG/'thermal.png',dpi=160); plt.close(fig)
    fig,ax=plt.subplots(1,3,figsize=(13,3.8))
    for row in DATA['beta']:
        ns=[r['N'] for r in row['steps']]; er=[r['max_absolute_error'] for r in row['steps']]
        ax[0].loglog(ns,er,'o-',label=f"rho={row['rho']:g}")
    ax[0].set(xlabel='Strang steps N',ylabel='Maximum absolute population error',title='Finite convergence vs Bessel'); ax[0].legend()
    ax[1].plot(ARRAYS['source_onset_v'],ARRAYS['source_onset'][1],label='Strang'); ax[1].plot(ARRAYS['source_onset_v'],ARRAYS['source_onset_bessel'][1],':',label='Bessel')
    ax[1].set(xlabel='v = lambda t',ylabel='p',title='Source onset n0=0.1, p0=0'); ax[1].legend()
    ax[2].plot(ARRAYS['trace_v'],ARRAYS['trace_state'][1]/1e-104,label='Strang p / 1e-104'); ax[2].plot(ARRAYS['trace_v'],ARRAYS['trace_analytic_p']/1e-104,':',label='Analytic source')
    ax[2].set(xlabel='v',ylabel='p / initial neutron inventory',title='Trace onset: p component retained'); ax[2].legend(fontsize=7)
    for a in ax:a.grid(alpha=.2)
    fig.tight_layout(); fig.savefig(FIG/'beta_convergence_onset.png',dpi=160); plt.close(fig)
    fig,ax=plt.subplots(1,2,figsize=(13,5.2))
    for a,kind in zip(ax,('thermal','beta')):
        rows=[r for r in DATA['timing'] if r['label'].startswith(kind)]
        yy=np.arange(len(rows)); med=np.array([r['median_s'] for r in rows])
        ranges=np.array([r['range_s'] for r in rows])
        a.barh(yy,med*1e3,color='steelblue'); a.errorbar(med*1e3,yy,xerr=np.array([med-ranges[:,0],ranges[:,1]-med])*1e3,fmt='none',color='black',capsize=2)
        labels=[]
        for r in rows:
            if kind=='thermal': err=max(r['reference_error'].values())
            else: err=r['max_absolute_reference_error']
            labels.append(r['label']+f'\nerror {err:.2g}')
        a.set_yticks(yy,labels,fontsize=7); a.set(xlabel='Wall milliseconds / solve, median and range',title=kind+'; measured errors differ')
    fig.tight_layout(); fig.savefig(FIG/'timing_with_errors.png',dpi=160); plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
    if (OUT/'execution.json').exists():
        raise RuntimeError('Existing execution evidence: preserve it; a repair needs a separately named output directory.')
    metadata={'command':sys.argv,'cwd':os.getcwd(),'requested_executor_model':'gpt-6.1-sol (root delegation)',
              'observed_tool_environment':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__},
              'model_identity_note':'Requested model is not an observed inference-runtime identity.',
              'thread_env':{k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')},
              'resource_limits':{'cpu_s':list(resource.getrlimit(resource.RLIMIT_CPU)),'address_space_bytes':list(resource.getrlimit(resource.RLIMIT_AS))},
              'clock_scope':'Whole diagnostic excludes shell startup; solver batch timing excludes preparation and independent references.'}
    status='FAIL'; failure=None
    try:
        input_checks(); thermal_checks(); beta_checks(); figures(); status='COMPLETED_PENDING_INDEPENDENT_REVIEW'
    except BaseException as exc:
        failure={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
        print(failure['traceback'],file=sys.stderr)
    finally:
        np.savez(OUT/'raw_arrays.npz',**ARRAYS)
        write('results.json',DATA); write('checks.json',CHECKS)
        metadata.update(status=status,failure=failure,wall_s=time.perf_counter()-START,cpu_s=time.process_time()-CPU_START,
                        peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                        check_count=len(CHECKS),passed_count=sum(c['passed'] for c in CHECKS),raw_array_count=len(ARRAYS),figure_count=len(list(FIG.glob('*.png'))))
        write('execution.json',metadata)
        print(json.dumps({k:metadata[k] for k in ('status','wall_s','cpu_s','peak_RSS_KiB','check_count','passed_count','raw_array_count','figure_count')},indent=2))
    return 0 if failure is None else 1


if __name__=='__main__': sys.exit(main())
