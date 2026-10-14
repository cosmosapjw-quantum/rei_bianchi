"""Finite analytic, sample-binding and recorded-result diagnostics; no trajectory replay."""
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from reference import Reference,coefficients,cross_sections,END,FHE,CHI
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def main():
    r=json.loads((HERE/'RESULTS.json').read_text());native_path=ROOT/r['native_output_directory']/'native.json';native=json.loads(native_path.read_text())
    checks=[]
    def check(name,condition,detail=None):
        if not bool(condition):raise AssertionError(name+' '+str(detail))
        checks.append({'name':name,'status':'PASS','detail':detail})
    model=Reference(native,'FLRW');rng=np.random.default_rng(20261005)
    check('real energy grid33 directions128',model.n==33 and model.nd==128)
    check('original source node13.7',model.e[model.birth]==13.7)
    check('native initial gas temperature',abs(model.temperature(model.initial[:4])-50000)<1e-10)
    check('no initial lowest node population',np.all(model.unpack(model.initial)[1][:,0]==0))
    for geometry in ['FLRW','BI']:
        m=Reference(native,geometry)
        for t in [0.,2e9,1e10]:
            p=rng.random((m.nd,m.n))*1e-5;p[:,0]=0;u=rng.random(m.nd)*1e-4
            dp,dn,du,work=m.transport(p,u,t)
            number=abs(dp.sum()+dn.sum());energy=abs((dp*m.e).sum()+du.sum()+work)
            check(geometry+' number generator '+str(t),number<1e-25,number)
            check(geometry+' energy generator '+str(t),energy<1e-24,energy)
            weights,hd=m.weights_hd(t)
            check(geometry+' source normalized '+str(t),abs(weights.sum()-1)<5e-16 and np.all(weights>0),float(weights.sum()))
            if geometry=='FLRW':check('isotropic Hd '+str(t),np.max(abs(hd-1e-14))<1e-29)
            # Full chemical+source+work derivative ledger cancellation.
            y=m.initial.copy();d=m.rhs(t/END,y)/END
            dg,dp,dgn,dgu,dl=m.unpack(d)
            nr=dp.sum()+dgn.sum()+dl[5]-dl[3]
            er=dg[3]+CHI[0]*dg[0]+FHE*(CHI[1]*dg[1]+(CHI[1]+CHI[2])*dg[2])+(dp*m.e).sum()+dgu.sum()+dl[0]+dl[1]+dl[2]-dl[4]
            check(geometry+' full number RHS '+str(t),abs(nr)<1e-25,float(nr))
            check(geometry+' full energy RHS '+str(t),abs(er)<2e-25,float(er))
    # One occupied j1 has exact exponential survival, N retention, guard redshift.
    lam=1e-14*model.e[1]/(model.e[1]-10);h=1e-14;p1=.05;t=END
    analytic=np.array([p1*np.exp(-lam*t),p1*(-np.expm1(-lam*t)),10*lam*p1*(np.exp(-h*t)-np.exp(-lam*t))/(lam-h)])
    sol=solve_ivp(lambda s,v:END*np.array([-lam*v[0],lam*v[0],-h*v[2]+10*lam*v[0]]),(0,1),[p1,0,0],method='DOP853',rtol=2e-13,atol=1e-16)
    check('two component lower projected analytic solution',sol.success and np.max(abs(sol.y[:,-1]-analytic))<2e-15,float(np.max(abs(sol.y[:,-1]-analytic))))
    sigma=cross_sections(model.e);ns=np.array(native['sigma_cm2'])
    check('provider fit cutoffs exact',np.array_equal(sigma==0,ns==0))
    check('provider fit native sample agreement',r['coefficient_binding']['sigma_max_relative_error']<3e-14,r['coefficient_binding'])
    check('independent FT03 coefficient native sample agreement',r['coefficient_binding']['max_relative_error']<3e-14)
    check('binding threshold distinct from sigma cutoff',np.all(sigma[(model.e>=CHI[0])&(model.e<13.6),0]==0))
    try:coefficients(29999.)
    except ValueError:check('FT03 domain rejects out of range',True)
    else:raise AssertionError('domain acceptance')
    check('two independent numerical methods',r['reference_comparison']['status']=='PASS' and r['reference_comparison']['scaled_max_endpoint_disagreement']<=1e-8)
    check('six trajectories112 macro calls',len(r['discrete_runs'])==6 and sum(x['accepted_steps'] for x in r['discrete_runs'])==112)
    for row in r['discrete_runs']:
        g=np.array(row['gas']);check(row['geometry']+' gas simplex '+str(row['macro_dt_s']),np.all(np.isfinite(g)) and 0<=g[0]<=1 and g[1]>=0 and g[2]>=0 and g[1]+g[2]<=1 and g[3]>0)
        check(row['geometry']+' frozen gates '+str(row['macro_dt_s']),row['actual_paired_trial'] and row['max_local_bound']<2e-4 and row['max_public_width']<2e-3 and row['max_ledger']<=1e-12)
    check('reused historical endpoint parity',all(x['status']=='PASS' for x in r['historical_endpoint_parity']),r['historical_endpoint_parity'])
    for g,methods in r['reference_comparison']['solver_metadata'].items():
        for method,meta in methods.items():
            check(g+' '+method+' number balance',meta['max_number_ledger_residual_per_h']<1e-12,meta['max_number_ledger_residual_per_h'])
            check(g+' '+method+' energy balance',meta['max_energy_ledger_residual_ev_per_h']<1e-10,meta['max_energy_ledger_residual_ev_per_h'])
    # A nonzero guard jump, whose secant diverges as dt decreases, is a boundary witness.
    witness=r['lowest_node_witness']
    check('occupied10eV entire count exported',all(abs(x['guard_n']-.05)<1e-15 and x['final_p0']==0 for x in witness))
    check('occupied10eV secant grows inversely with dt',abs((witness[1]['guard_n']/witness[1]['dt_s'])/(witness[0]['guard_n']/witness[0]['dt_s'])-10)<1e-12)
    check('initial projected secant approaches derivative',r['initial_derivative_consistency'][1]['scaled_derivative_error_times_1e10']<r['initial_derivative_consistency'][0]['scaled_derivative_error_times_1e10'],r['initial_derivative_consistency'])
    check('claim boundaries',r['scientific_admission']=='HOLD' and r['continuum_time_error_certificate']=='NOT_ESTABLISHED' and r['new_full_campaign_executions']==0 and not r['production_source_modified'])
    validation={'status':'PASS','scope':'candidate self-check only; no independent review or scientific admission','checks':checks,'check_count':len(checks),'scientific_admission':'HOLD','results_sha256':hashlib.sha256((HERE/'RESULTS.json').read_bytes()).hexdigest(),'native_sha256':hashlib.sha256(native_path.read_bytes()).hexdigest()}
    (HERE/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n');print(json.dumps({'status':'PASS','self_check_count':len(checks),'scientific_admission':'HOLD'}))
if __name__=='__main__':main()
