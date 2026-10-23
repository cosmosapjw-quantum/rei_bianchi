#!/usr/bin/env python3
"""Controller-authorized timing-only follow-up; reuse saved reference evidence."""
import json
import time
import resource
import hashlib
import sys
import traceback
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from local_flows import BASE, beta_rhs, strang
from run_diagnostic import solve_thermal, counters, plain

START=time.perf_counter()
CPU=time.process_time()
OUT=BASE/'results'
saved=json.loads((OUT/'results.json').read_text())
raw=np.load(OUT/'raw_arrays.npz')
rows=[]
arrays={}
checks=[]


def assess(label,sol,ref,thermal=False):
    if thermal:
        y=sol.production
        ex=float(np.max(np.abs(y[0]-ref[0]))/.225)
        et=float(np.max(np.abs(np.exp(y[1]-ref[1])-1)))
        passed=ex<=5e-8 and et<=5e-8 and sol.success
        value={'x_scaled':ex,'T_relative':et}
    else:
        y=sol.y if hasattr(sol,'y') else sol
        value={'max_absolute_population_error':float(np.max(np.abs(y-ref)))}
        rho=float(label.split('_')[1])
        ceiling=next(r for r in saved['beta'] if r['rho']==rho)['steps'][-1]['max_absolute_error']
        passed=value['max_absolute_population_error']<=ceiling+2e-15
        passed=passed and np.min(y)>=-1e-15 and np.max(np.abs(np.sum(y,axis=0)-1))<=2e-12
        if hasattr(sol,'success'):passed=passed and sol.success
    checks.append({'label':label,'passed':bool(passed),'errors':value})
    if not passed:raise AssertionError(str(checks[-1]))
    arrays[label]=y
    return value


def pair(case,methods,reference,thermal=False):
    # Warm both methods once; all later calls use frozen grids and tolerances.
    samples={name:[] for name in methods}
    count={}
    accuracy={}
    for name,fn in methods.items():
        sol=fn(); accuracy[name]=assess(case+'_'+name,sol,reference,thermal)
        count[name]=counters(sol) if hasattr(sol,'nfev') else {'exact_subflow_stages':768}
    names=list(methods)
    for batch in range(7):
        order=names if batch%2==0 else names[::-1]
        for name in order:
            t0=time.perf_counter(); c0=time.process_time()
            for _ in range(3):sol=methods[name]()
            cpu=(time.process_time()-c0)/3; wall=(time.perf_counter()-t0)/3
            samples[name].append({'batch':batch,'position':order.index(name),'wall_s_per_solve':wall,'cpu_s_per_solve':cpu})
            assess(case+'_'+name,sol,reference,thermal)
    for name in names:
        row={'case':case,'method':name,'samples':samples[name],'warmup_solves':1,'solves_per_batch':3,'paired_batches':7,
             'counters':count[name],'reference_errors':accuracy[name]}
        for clock in ('wall','cpu'):
            v=[s[clock+'_s_per_solve'] for s in samples[name]]
            row[clock+'_median_s']=float(np.median(v));row[clock+'_range_s']=[min(v),max(v)]
        rows.append(row)


def main():
    target=OUT/'paired_timing.json'
    if target.exists():raise RuntimeError('Preserve existing paired timing; no repeated run authorized.')
    failure=None
    try:
        for r in saved['thermal']:
            Ti=r['Ti_K'];key=f'thermal_{int(Ti)}';grid=raw[key+'_s'];ref=raw[key+'_reference']
            pair(key,{'full':lambda Ti=Ti,grid=grid:solve_thermal(Ti,grid,False),
                      'reduced':lambda Ti=Ti,grid=grid:solve_thermal(Ti,grid,True)},ref,True)
        for r in saved['beta']:
            rho=r['rho'];key=f'beta_{rho:g}';grid=raw[key+'_256_v'];ref=raw[key+'_256_exact']
            pair(key,{'strang':lambda rho=rho:strang(rho,256),
                      'DOP853':lambda rho=rho,grid=grid:solve_ivp(lambda v,y:beta_rhs(v,y,rho),[0,4],[.1,.2,.7],method='DOP853',t_eval=grid,rtol=1e-9,atol=1e-12)},ref)
        fig,ax=plt.subplots(1,2,figsize=(13,5))
        labels=[r['case']+' '+r['method'] for r in rows]
        for a,clock in zip(ax,('wall','cpu')):
            median=np.array([r[clock+'_median_s'] for r in rows])*1e3
            bounds=np.array([r[clock+'_range_s'] for r in rows])*1e3
            y=np.arange(len(rows))
            a.barh(y,median);a.errorbar(median,y,xerr=np.array([median-bounds[:,0],bounds[:,1]-median]),fmt='none',capsize=2,color='black')
            a.set_yticks(y,labels,fontsize=7);a.set(xlabel=clock+' ms / solve',title='Paired, alternating order; median and range')
        fig.tight_layout();fig.savefig(BASE/'figures/paired_timing.png',dpi=160);plt.close(fig)
    except BaseException as exc:
        failure={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
        print(failure['traceback'],file=sys.stderr)
    finally:
        result={'status':'PASS_TIMING_FOLLOWUP_PENDING_REVIEW' if failure is None else 'FAIL','failure':failure,
                'clock_scope':'Body after Python/library imports; per-solve integration plus outputs/reconstruction; reference/setup excluded; assessment excluded from timed interval.',
                'body_wall_s':time.perf_counter()-START,'body_cpu_s':time.process_time()-CPU,
                'peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                'resource_limits':{'cpu_s':resource.getrlimit(resource.RLIMIT_CPU),'AS_bytes':resource.getrlimit(resource.RLIMIT_AS)},
                'unchanged_local_flows_sha256':hashlib.sha256((BASE/'code/local_flows.py').read_bytes()).hexdigest(),
                'method_rows':rows,'accuracy_checks':checks,'command':sys.argv}
        target.write_text(json.dumps(result,indent=2,default=plain)+'\n')
        np.savez(OUT/'paired_timing_outputs.npz',**arrays)
        print(json.dumps({k:result[k] for k in ('status','body_wall_s','body_cpu_s','peak_RSS_KiB')},indent=2))
    return 0 if failure is None else 1


if __name__=='__main__':sys.exit(main())
