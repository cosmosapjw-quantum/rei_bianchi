#!/usr/bin/env python3
"""Continuous-stage diagonal stiff solve for the same fixed-bath diagnostic.

Unlike frozen-midpoint exponential steps, the implicit multistep solution owns
the endpoint source and opacity. Sparse analytic Jacobian is exact for this
prescribed-bath problem; no gas feedback is claimed.
"""
from pathlib import Path
import argparse,json,time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import diags,bmat,csr_matrix
from run_transport import (BianchiBackground,load_hm12,make_grid,geometry_nodes,
                          source_reference,sigma,C,CHI,compare)


def execute(r,ne,nmu,rtol,inspect_mesh=False):
    start=time.perf_counter(); bg=BianchiBackground(r=r,z_i=15.9,t_max=1e17)
    tf=bg.time_of_redshift(4.); last=bg.at(tf)
    q,m,w=make_grid(ne,nmu,50000*max(last['scale_rel']))
    tables=load_hm12(); n=len(q); init=np.zeros(n);active=q<=50000
    init[active]=tables['uvb'].photon_number_log(q[active],15.9)*w[active]
    x=np.linspace(0,np.log(16.9/5),65);zz=16.9/np.exp(x)-1;zz[0]=15.9;zz[-1]=4.
    tt=np.array([bg.time_of_redshift(float(z)) for z in zz])
    scale=max(init.sum(),bg.nH_i)
    y0=np.r_[init/scale,np.zeros(6)]
    cache={}
    def stage(u):
        if cache.get('u')==u:return cache['v']
        g=bg.at(float(u*tf));e,mu,_=geometry_nodes(q,m,g)
        s=source_reference(q,m,w,g,tables['emissivity'])
        lower=np.array([.9*g['nH'],.9*g['nHe'],.1*g['nHe']])
        k=C*sigma(e)*lower
        edot=-(g['H']+g['s']*(3*mu**2-1))*e
        cache.update(u=u,v=(g,e,s,k,edot))
        return cache['v']
    def rhs(u,y):
        g,e,s,k,edot=stage(u); N=y[:n]*scale
        dN=s-k.sum(axis=1)*N
        dabs=(k*N[:,None]).sum(axis=0)
        return tf*np.r_[dN,s.sum(),dabs,np.dot(s,e),-np.dot(N,edot)]/scale
    def jac(u,y):
        g,e,s,k,edot=stage(u)
        lower=np.vstack([np.zeros(n),k.T,np.zeros(n),-edot])
        return tf*bmat([[diags(-k.sum(axis=1)),None],[csr_matrix(lower),csr_matrix((6,6))]],format='csc')
    sol=solve_ivp(rhs,(0.,1.),y0,method='BDF',rtol=rtol,atol=rtol*1e-5,
                  jac=jac,t_eval=None if inspect_mesh else tt/tf,
                  dense_output=inspect_mesh,max_step=1/128)
    if not sol.success:raise RuntimeError(sol.message)
    trace=None
    if inspect_mesh:
        node,epoch=np.unravel_index(np.argmin(sol.y[:n]),sol.y[:n].shape)
        g,e,s,k,edot=stage(float(sol.t[epoch]))
        trace=dict(min_accepted_scaled=float(sol.y[node,epoch]),node=int(node),time_s=float(sol.t[epoch]*tf),
                   q_eV=float(q[node]),energy_eV=float(e[node]),source_ref=float(s[node]),
                   opacity_per_s=k[node].tolist(),accepted_negative_count=int(np.count_nonzero(sol.y[:n]<0)))
        sol.y=sol.sol(tt/tf)
    rows=[];minvalue=float(sol.y[:n].min())
    for i,t in enumerate(tt):
        g=bg.at(float(t));e,mu,_=geometry_nodes(q,m,g);N=sol.y[:n,i]*scale
        sn,ah,ahe,ahe2,se,work=sol.y[n:,i]*scale
        sg=sigma(e);proper=N/g['a_rel']**3
        rows.append(dict(t_s=float(t),z=g['z'],photon_reference=float(N.sum()),energy_reference_eV=float(np.dot(N,e)),
            Gamma=(C*(sg*proper[:,None]).sum(axis=0)).tolist(),
            heat_per_target_eV_s=(C*(sg*proper[:,None]*np.maximum(e[:,None]-CHI,0)).sum(axis=0)).tolist(),
            active_number_reference=[float(N[e>=v].sum()) for v in [13.60,24.59,54.42]],
            source_reference=float(sn),absorbed_reference=float(ah+ahe+ahe2),absorbed_species_reference=[float(ah),float(ahe),float(ahe2)],
            photon_ledger=float((N.sum()+ah+ahe+ahe2-init.sum()-sn)/max(init.sum()+sn,1e-100))))
    return dict(r=r,n_energy=ne,n_mu=nmu,rtol=rtol,elapsed_s=time.perf_counter()-start,
                nfev=sol.nfev,njev=sol.njev,nlu=sol.nlu,min_scaled_photon=minvalue,
                accepted_mesh_trace=trace,
                history=rows,scientific_scope='prescribed_bath_diagnostic_not_reionization')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--energy',type=int,default=128);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    result=[]
    for r in [0.,.05]:
        group=[]
        for tol in [1e-6,1e-8]:
            case=execute(r,args.energy,1 if r==0 else 4,tol);group.append(case)
            (args.output/f'r{r}_tol{tol}.json').write_text(json.dumps(case,indent=2)+'\n')
            print(json.dumps({k:v for k,v in case.items() if k!='history'}),flush=True)
        error=compare(*group);ledger=max(abs(row['photon_ledger']) for case in group for row in case['history'])
        result.append(dict(r=r,temporal=error,max_ledger=ledger,temporal_pass=max(error.values())<=2e-6,
                           positivity_pass=all(case['min_scaled_photon']>=0 for case in group)))
    report=dict(status='PASS_TEMPORAL_ONLY' if all(x['temporal_pass'] and x['positivity_pass'] for x in result) else 'FAIL',results=result,
                spectral_status='TRANSPORT001_FAILED_NOT_SUPERSEDED',coupled_status='ROOT_OWNED_NOT_EVALUATED_HERE')
    (args.output/'COMPARISON.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    raise SystemExit(0 if report['status']=='PASS_TEMPORAL_ONLY' else 1)


if __name__=='__main__':main()
