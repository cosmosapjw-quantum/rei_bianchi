"""Create-only PHYS81 isolated CI cohort; one owner, new identities only."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, sys, time, traceback
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from registry import load_rates
from parcel import HazardParcel

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/parcel'
MODEL={'B':[1.,.083,4.6e-10],'X0':[2e-4,0.,0.],'T0_K':25370.66308424773,'nref_cm3':1e-3,'t_end_s':1e14,'scope':'declared fixed-density H1/He4/Li7 finite-window CI-only exploratory parcel; stationary-target rate closure; no isotope abundance inference'}
TASKS=[{'label':'hazard_base','coordinates':'hazard3','method':'Radau','rtol':2e-8,'atol':2e-11}, {'label':'hazard_refined','coordinates':'hazard3','method':'Radau','rtol':2e-10,'atol':2e-13}, {'label':'original7_reference','coordinates':'full7','method':'DOP853','rtol':2e-10,'atol':2e-13}]
GATES={'maximum_normalized_7state_comparison':1e-7,'maximum_T_fraction_of_T0':1e-7,'nucleus_fraction_error':1e-10,'relative_energy_error':2e-10,'minimum_fraction':0.}

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_once(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def binding():
    files=['source/run_science.py','source/parcel.py','source/finite_ci.py','source/registry.py','source/vendor/ci_finite_c22d.py','source/vendor/CCC_TICS_1S.txt','source_data/ADMITTED_FINITE_CI_REGISTRY.json','source_data/PHYS81_CI_FINITE_WINDOW_LITERAL_DATA.csv']
    return {'code_and_inputs':{f:sha(ROOT/f) for f in files},'runtime':{'python':sys.version.split()[0],'numpy':np.__version__,'scipy':scipy.__version__},'model':MODEL,'gates':GATES,'samples':161,'time_coordinate':'s=t/t_end; RHS and Jacobian multiplied by t_end; no time-domain approximation'}

def decoded(parcel,y,coordinate):
    states=[parcel.lift(v) if coordinate=='hazard3' else parcel.full_lift(v) for v in y.T]
    # Retain the independent solver's raw normalized coordinates verbatim.
    scaled=y.T.copy() if coordinate=='full7' else np.array([np.r_[s['neutral_abundance']/parcel.B,s['ion_abundance']/parcel.B,s['u']/parcel.u0] for s in states])
    return scaled,np.array([s['T'] for s in states]),np.array([s['xe'] for s in states]),sum(s['neutral_underflow'] for s in states)

def one(task,plan,parcel,resume):
    identity={**plan,'solver':{k:v for k,v in task.items() if k!='label'}}
    key=hashlib.sha256(canonical(identity)).hexdigest();dest=OUT/key
    record_path=dest/'COMPLETE.json'
    if record_path.exists():
        r=json.loads(record_path.read_text())
        if r['status']!='COMPLETE' or r['ODE']!=1 or r['science_id']!=key or r['identity']!=identity or sha(dest/'trajectory.npz')!=r['trajectory_SHA256']:raise ValueError('RESUME_IDENTITY_OR_BYTES_MISMATCH')
        return {'label':task['label'],'science_id':key,'status':'VERIFIED_SKIP','ODE':0,'original_record':str(record_path.relative_to(ROOT))}
    if resume:raise FileNotFoundError('RESUME_REQUIRES_COMPLETE:'+key)
    dest.mkdir(parents=True,exist_ok=False)
    write_once(dest/'CLAIM.json',{'identity':identity,'science_id':key,'started_utc':now(),'pid':os.getpid()})
    start=time.monotonic();calls={'rhs':0,'jac':0};tend=MODEL['t_end_s']
    if task['coordinates']=='hazard3':
        y0=np.zeros(3)
        def rhs(t,z):calls['rhs']+=1;return tend*parcel.rhs(t*tend,z)
        def jac(t,z):calls['jac']+=1;return tend*parcel.jac(t*tend,z)
        kwargs={'jac':jac}
    else:
        y0=parcel.initial_full()
        def rhs(t,w):calls['rhs']+=1;return tend*parcel.full_rhs(t*tend,w)
        kwargs={}
    try:
        sol=solve_ivp(rhs,(0.,1.),y0,method=task['method'],rtol=task['rtol'],atol=task['atol'],dense_output=True,**kwargs)
        if not sol.success or sol.t[-1]!=1.:raise RuntimeError('SOLVER_INCOMPLETE:'+sol.message)
        s=np.linspace(0.,1.,161);dense=sol.sol(s)
        w,T,xe,underflow=decoded(parcel,dense,task['coordinates'])
        aw,aT,axe,aunderflow=decoded(parcel,sol.y,task['coordinates'])
        b=parcel.B;I=parcel.Ichemical_eV
        energy=aw[:,6]*parcel.u0+np.sum(aw[:,3:6]*b*I,axis=1)
        energy0=parcel.u0+np.dot(parcel.X0,I)
        checks={'maximum_nucleus_fraction_error':float(np.max(abs(aw[:,:3]+aw[:,3:6]-1.))),'maximum_relative_total_energy_error':float(np.max(abs((energy-energy0)/energy0))),'minimum_accepted_fraction':float(np.min(aw[:,:6])),'minimum_sampled_fraction':float(np.min(w[:,:6])),'accepted_T_range_K':[float(aT.min()),float(aT.max())],'neutral_underflow_samples':underflow,'neutral_underflow_accepted':aunderflow}
        passed=checks['maximum_nucleus_fraction_error']<=GATES['nucleus_fraction_error'] and checks['maximum_relative_total_energy_error']<=GATES['relative_energy_error'] and min(checks['minimum_accepted_fraction'],checks['minimum_sampled_fraction'])>=0
        with (dest/'trajectory.npz').open('xb') as stream:np.savez_compressed(stream,s=s,t_s=s*tend,coordinates=dense.T,scaled7=w,T_K=T,xe=xe,accepted_s=sol.t,accepted_coordinates=sol.y.T,accepted_scaled7=aw,accepted_T_K=aT,accepted_xe=axe)
        record={'label':task['label'],'science_id':key,'identity':identity,'status':'COMPLETE' if passed else 'FAILED_INVARIANT_GATE','trajectory_SHA256':sha(dest/'trajectory.npz'),'completed_utc':now(),'wall_s':time.monotonic()-start,'dimension':len(y0),'nfev':sol.nfev,'njev':sol.njev,'nlu':sol.nlu,'observed_calls':calls,'accepted_mesh_points':len(sol.t),'accepted_steps':len(sol.t)-1,'saved_samples':len(s),'checks':checks,'final_T_K':float(T[-1]),'final_xe':float(xe[-1]),'final_ion_fractions':w[-1,3:6].tolist(),'final_hazards':dense[:,-1].tolist() if task['coordinates']=='hazard3' else None,'energy_residual_interpretation':'hazard energy is construction; independent trajectory accuracy requires full7/refinement comparison','ODE':1}
        write_once(record_path if passed else dest/'FAILED_GATE.json',record)
        if not passed:raise ArithmeticError('POSTFLIGHT_INVARIANT_FAILED')
        return {k:record[k] for k in ('label','science_id','status','wall_s','dimension','nfev','njev','nlu','accepted_mesh_points','saved_samples','final_T_K','final_ion_fractions','ODE')}
    except Exception as e:
        write_once(dest/'FAILED_ATTEMPT.json',{'science_id':key,'label':task['label'],'status':'FAILED','elapsed_s':time.monotonic()-start,'exception':repr(e),'traceback':traceback.format_exc(),'observed_calls':calls,'ODE':1,'new_identity_required_for_retry':True});raise

def saved_comparisons(records):
    arrays={r['label']:np.load(OUT/r['science_id']/'trajectory.npz',allow_pickle=False) for r in records}
    comparisons=[]
    try:
        for name in ('hazard_base','original7_reference'):
            x,y=arrays[name],arrays['hazard_refined']
            if not np.array_equal(x['s'],y['s']):raise ValueError('COMPARISON_SAMPLE_GRID_MISMATCH')
            d=float(np.max(abs(x['scaled7']-y['scaled7'])));dt=float(np.max(abs(x['T_K']-y['T_K']))/MODEL['T0_K'])
            comparisons.append({'pair':[name,'hazard_refined'],'max_scaled7_error':d,'max_T_fraction_T0':dt,'passed':d<=GATES['maximum_normalized_7state_comparison'] and dt<=GATES['maximum_T_fraction_of_T0']})
    finally:
        for x in arrays.values():x.close()
    return comparisons

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--resume',action='store_true');a=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);plan=binding()
    plan_path=OUT/'PLAN.json'
    if plan_path.exists():
        if json.loads(plan_path.read_text())!={'binding':plan,'tasks':TASKS}:raise ValueError('FROZEN_PLAN_MISMATCH')
    else:write_once(plan_path,{'binding':plan,'tasks':TASKS})
    parcel=HazardParcel(load_rates(),MODEL['B'],MODEL['X0'],MODEL['T0_K'],MODEL['nref_cm3'])
    records=[one(t,plan,parcel,a.resume) for t in TASKS]
    comparisons=saved_comparisons(records)
    binding_sha=hashlib.sha256(canonical(plan)).hexdigest()
    trajectory_hashes={r['science_id']:sha(OUT/r['science_id']/'trajectory.npz') for r in records}
    if a.resume:
        old=json.loads((OUT/'SCIENCE_SUMMARY.json').read_text())
        if old['status']!='PASS_SCOPED' or old['binding_SHA256']!=binding_sha or old['trajectory_SHA256_by_id']!=trajectory_hashes or old['comparisons']!=comparisons or not all(c['passed'] for c in comparisons):raise ValueError('RESUME_COHORT_VERIFICATION_FAILED')
        print(json.dumps({'status':'RESUME_VERIFIED','new_ODE':0,'verified_skips':len(records),'saved_comparisons_rechecked':len(comparisons),'summary_SHA256':sha(OUT/'SCIENCE_SUMMARY.json'),'records':records}));return
    actual_new=sum(r['ODE'] for r in records)
    result={'status':'PASS_SCOPED' if all(c['passed'] for c in comparisons) else 'FAILED_COMPARISON','binding_SHA256':binding_sha,'trajectory_SHA256_by_id':trajectory_hashes,'records':records,'comparisons':comparisons,'new_ODE_attempts':actual_new,'new_ODE_completed':actual_new,'reused_completed_identities':len(records)-actual_new,'completed_identity_replays':0,'new_cosmological_ODE':0,'NCP':0,'benchmark':0,'method_comparison':'independent-coordinate and solver convergence, not timed performance benchmark'}
    write_once(OUT/'SCIENCE_SUMMARY.json',result);print(json.dumps(result))
    if result['status']!='PASS_SCOPED':raise SystemExit(2)

if __name__=='__main__':main()
