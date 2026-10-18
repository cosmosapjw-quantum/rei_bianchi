#!/usr/bin/env python3
"""Frozen bounded Unit8 early thermal atomic bridge; no native activation."""
import csv,hashlib,json,math,os,platform,re,shutil,signal,sys,time
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp,quad
from scipy.interpolate import PchipInterpolator
from scipy.special import logsumexp
from li_thermal_rates import Provider,KB,EV,ME,H,C,C_LIGHT
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/laneA'

def dump(path,obj):path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def csvout(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def serial(r):return {k:v for k,v in r.items() if not k.startswith('scaled_')}
def rel(a,b):return abs(a-b)/max(abs(a),abs(b)) if a or b else 0.

from scipy.integrate._ivp.bdf import BDF
from scipy.linalg import matrix_balance, lu_factor, lu_solve
from types import SimpleNamespace

BALANCE_RECORDS=[]
def balanced_factor(A):
    B,(scales,permutation)=matrix_balance(A,permute=False,scale=True,separate=True,overwrite_a=False)
    if not np.all(np.isfinite(scales)&(scales>0)):
        raise ValueError('nonfinite or nonpositive balancing scale')
    BALANCE_RECORDS.append(scales.copy())
    return lu_factor(B,overwrite_a=False),scales

def balanced_solve(factors,b):
    lu,scales=factors
    return scales*lu_solve(lu,np.asarray(b)/scales,overwrite_b=False)

class BalancedBDF(BDF):
    """Frozen BDF with equivalent dyadic-similarity Newton linear algebra only."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        def lu(A):
            self.nlu+=1
            return balanced_factor(A)
        self.lu=lu
        self.solve_lu=balanced_solve

def main():
    start=time.perf_counter()
    def timeout(*_):raise TimeoutError('single continuation26-second deadline')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(26)
    contract=json.loads((ROOT/'spec/LI_THERMAL_CONTRACT.json').read_text())
    paths={}
    for key,info in contract['inputs'].items():
        dest=ROOT/'inputs/laneA'/(key+'_'+Path(info['path']).name)
        assert hashlib.sha256(dest.read_bytes()).hexdigest()==info['sha256'] and dest.stat().st_size==info['bytes'],key+' immutable source mismatch'
        paths[key]=dest
    provider=Provider(paths,contract['atomic_channels'])
    donor=json.loads(paths['donor'].read_text());bc=json.loads(paths['Be_contract'].read_text());br=json.loads(paths['Be_result'].read_text())
    expected=np.array([2.**-20,1.]);A=np.array([[4.,2.**-20],[2.**20,4.]])
    factors=balanced_factor(A);answer=balanced_solve(factors,np.array([5.*2.**-20,5.]))
    wrapper={'relative_error':float(np.max(abs(answer/expected-1))),'limit':64*np.finfo(float).eps,'scales':factors[1].tolist(),'passed':False}
    wrapper['passed']=bool(wrapper['relative_error']<=wrapper['limit'])
    dump(OUT/'balanced_wrapper_check.json',wrapper)
    assert wrapper['passed'],'frozen wrapper arithmetic check failed'
    BALANCE_RECORDS.clear()
    metrics={'rate64_128_max_relative':0.,'tail60_80_max_relative':0.,'identity_max_relative':0.,'W_K_Q_max_relative':0.,'Decimal_formula_max_relative':0.}
    raw=json.loads((OUT/'rate_quadrature_raw.json').read_text())
    for coarse,final in zip(raw[::2],raw[1::2]):
        for typ in ['electron','photon']:
            v=np.array(final['scaled_'+typ]);w=np.array(coarse['scaled_'+typ]);tail=np.array(final['scaled_'+typ+'_tail']);mask=v>0
            if np.any(mask):
                metrics['rate64_128_max_relative']=max(metrics['rate64_128_max_relative'],float(np.max(abs(v[mask]-w[mask])/v[mask])))
                metrics['tail60_80_max_relative']=max(metrics['tail60_80_max_relative'],float(np.max(abs(tail[mask])/v[mask])))
        metrics['W_K_Q_max_relative']=max(metrics['W_K_Q_max_relative'],rel(final['W_abs_J_s'],final['K_primary_J_s']+final['Q_threshold_J_s']))
        te=final['Te_K'];tg=final['Tgamma_K'];isc=final['core']
        if tg>0:
            sp=final['scaled_photon'];x0=(64.39 if isc else provider.rows[final['ion']]['chi_eV'])*EV/(KB*tg)
            metrics['W_K_Q_max_relative']=max(metrics['W_K_Q_max_relative'],rel(sp[2],sp[3]+x0*sp[1]))
        if te==tg and not isc:
            residual=abs(math.expm1(final['log_beta_s_inverse']-math.log(final['alpha_g_stim_cm3_s'])-final['log_Saha_cm3_inverse']))
            metrics['identity_max_relative']=max(metrics['identity_max_relative'],residual)
    finals=raw[1::2]
    metrics['nonfinite_or_nonpositive_alpha_count']=sum(not(math.isfinite(r['alpha_g_sp_cm3_s']) and r['alpha_g_sp_cm3_s']>0 and math.isfinite(r['alpha_g_stim_cm3_s']) and r['alpha_g_stim_cm3_s']>0) for r in finals if not r['core'])
    metrics['nonfinite_log_beta_count']=sum(not math.isfinite(r['log_beta_s_inverse']) for r in finals if r['Tgamma_K']>0)
    metrics['Decimal_formula_max_relative']=max(r['relative'] for r in json.loads((OUT/'decimal_formula_checks.json').read_text()))
    metrics['independent_quad_max_relative']=max(v for r in json.loads((OUT/'independent_quad_checks.json').read_text()) for v in r['relative'])
    mid=np.load(OUT/'rate_midpoint_checks.npz');metrics['rate_midpoint_direct_max_relative']=float(np.max(abs(np.expm1(mid['log_interpolated']-mid['log_direct']))))
    dump(OUT/'reconstructed_rate_metrics.json',metrics)
    saved=np.load(OUT/'kinetic_rate_table.npz');ugrid=saved['u'];table=saved['log_rates'];uend=float(ugrid[-1])
    interp=PchipInterpolator(ugrid,table,axis=0,extrapolate=False);coarseinterp=PchipInterpolator(ugrid[::2],table[::2],axis=0,extrapolate=False)
    history=np.genfromtxt(paths['Be_history'],delimiter=',',names=True);bu=history['u'];bF=history['Fdecay']
    Ffull=PchipInterpolator(bu,bF,extrapolate=False);Fhalf=PchipInterpolator(bu[::2],bF[::2],extrapolate=False)
    b3=PchipInterpolator(bu,history['x_Be3'],extrapolate=False);b4=PchipInterpolator(bu,history['x_Be4'],extrapolate=False)
    output=np.linspace(0,uend,1025);z=100001*np.exp(-output)-1;F=Ffull(output)
    H0=br['H0_s-1'];Or=br['Omega_r'];Om=br['Omega_m'];OL=br['Omega_Lambda'];Ye=contract['kinetics']['Ye'];nb0=contract['kinetics']['nb0_cm3_inverse']
    def coefficients(u,source,model='ground_Milne'):
        x=100001*math.exp(-float(u));logs=source(u);beta=np.exp(logs[:3]);alpha=np.exp(logs[3:6] if model=='ground_Milne' else logs[6:9]);r=Ye*nb0*x**3*alpha;hh=H0*math.sqrt(Or*x**4+Om*x**3+OL)
        b0,b1,b2=beta;r0,r1,r2=r
        matrix=np.array([[-b0,r0,0],[b0,-b1-r0,r1],[-r2,b1-r2,-b2-r1-r2]])/hh
        return matrix,r2/hh,beta,r,hh
    production=np.load(OUT/'ground_production.npz')
    assert np.array_equal(production['u'],output),'saved output grid mismatch'
    saved_dense=PchipInterpolator(output,production['states'],axis=1,extrapolate=False)
    solutions={'ground_production':(production['populations'],SimpleNamespace(sol=saved_dense))};timings={};solverdiag=[{'label':'ground_production','success':True,'message':'preserved completed Radau production; original counters unavailable','nfev':None,'njev':None,'nlu':None,'observed_from':'saved full1025 output artifact'}]
    def solve(label,model,source,Fsource,method,rtol,atol):
        tic=time.perf_counter()
        def fun(u,y):
            matrix,reward,*_=coefficients(u,source,model);result=np.empty(6)
            result[:3]=matrix@y[:3]+np.array([0,0,reward]);result[3:]=matrix@y[3:]+np.array([0,0,reward*float(Fsource(u))]);return result
        def jac(u,y):
            matrix,*_=coefficients(u,source,model);result=np.zeros((6,6));result[:3,:3]=matrix;result[3:,3:]=matrix;return result
        sol=solve_ivp(fun,(0,uend),np.zeros(6),method=method,jac=jac,rtol=rtol,atol=atol,t_eval=output,dense_output=True)
        timings[label]=time.perf_counter()-tic;solverdiag.append({'label':label,'success':sol.success,'message':sol.message,'nfev':sol.nfev,'njev':sol.njev,'nlu':sol.nlu})
        diagnostic=solverdiag[-1]
        diagnostic.update({'status':sol.status,'method':'BalancedBDF' if method is BalancedBDF else method,'wall_seconds':timings[label],'time_reached_u':float(sol.sol.ts[-1]),'last_output_u':float(sol.t[-1]) if len(sol.t) else None})
        if method is BalancedBDF:
            scales=np.array(BALANCE_RECORDS)
            diagnostic['balancing']={'factorizations':len(BALANCE_RECORDS),'scale_min':float(scales.min()),'scale_max':float(scales.max()),'unique_scales':np.unique(scales).tolist()}
        dump(OUT/(label+'_solver.json'),diagnostic)
        if not sol.success:
            np.savez(OUT/(label+'_partial.npz'),u=sol.t,states=sol.y,internal_breakpoints=sol.sol.ts,last_state=sol.sol(sol.sol.ts[-1]))
            raise RuntimeError(label+': '+sol.message)
        normalized=np.vstack([sol.y[:3],1-np.sum(sol.y[:3],axis=0),sol.y[3:],Fsource(output)-np.sum(sol.y[3:],axis=0)])
        np.savez(OUT/(label+'.npz'),u=output,z=z,states=sol.y,populations=normalized,internal_u=sol.t)
        solutions[label]=(normalized,sol)
    solve('ground_BDF_balanced','ground_Milne',interp,Ffull,BalancedBDF,3e-9,3e-14)
    solve('ground_257','ground_Milne',coarseinterp,Ffull,'Radau',1e-8,1e-13)
    solve('ground_half_Be','ground_Milne',interp,Fhalf,'Radau',1e-8,1e-13)
    solve('total_RR_sensitivity','total_RR_sensitivity',interp,Ffull,'Radau',1e-8,1e-13)
    baseline=solutions['ground_production'][0]
    comparisons={}
    for label in ['ground_BDF_balanced','ground_257','ground_half_Be']:
        other=solutions[label][0];mask=baseline>=1e-8
        comparisons[label]={'max_absolute_per_origin':float(np.max(abs(other-baseline))),'max_relative_above_1e_8':float(np.max(abs((other-baseline)[mask]/baseline[mask])))}
    histories=[];diagnostics=[];inventory=[];abund=donor['result']['Y_final'];B=abund['Be7'];L=abund['Li7'];charge=bc['cosmology']['element_charge_map']
    def za(name):
        symbol=re.match('[A-Za-z]+',name)[0];A=1 if name in ['n','p'] else int(re.search('[0-9]+',name)[0]);return charge[symbol],A
    assert len(history)==32769 and np.all(np.diff(bu)>0)
    assert abs(Ye-br['Ye'])<1e-15 and abs(nb0-br['nb0_cm-3'])<1e-20
    original_mass=math.fsum(za(name)[1]*v for name,v in abund.items());original_charge=math.fsum(za(name)[0]*v for name,v in abund.items())
    assert abs(original_charge-Ye)<1e-15
    included=['n','p','H2','H3','He3','He4','Li7','Be7'];excluded={k:v for k,v in abund.items() if k not in included}
    excluded_mass=math.fsum(za(k)[1]*v for k,v in excluded.items());excluded_charge=math.fsum(za(k)[0]*v for k,v in excluded.items())
    spectators=np.array([abund['n'],0,abund['p'],0,abund['H2'],0,abund['H3'],0,0,abund['He3'],0,0,abund['He4']])
    mass17=np.array([1,1,1,2,2,3,3,3,3,3,4,4,4,7,7,7,7]);charge17=np.array([0,0,1,0,1,0,1,0,1,2,0,1,2,0,1,2,3]);Z17=np.array([0,1,1,1,1,1,1,2,2,2,2,2,2,3,3,3,3])
    ledgers=[];popmins=[];normal=[];sourcechecks=[];stationary={}
    for model,label in [('ground_Milne','ground_production'),('total_RR_sensitivity','total_RR_sensitivity')]:
        pops,sol=solutions[label];popmins.append(float(pops.min()));normal.extend([float(np.max(abs(pops[:4].sum(axis=0)-1))),float(np.max(abs(pops[4:].sum(axis=0)-F)))])
        for j,uu in enumerate(output):
            directp=pops[:4,j];ecp=pops[4:,j];Y=L*directp+B*ecp
            sourcechecks.append(abs(Y.sum()-(L+B*F[j]))/max(L,B*F[j],1e-30))
            row={'model':model,'u':float(uu),'z':float(z[j]),'Fdecay':float(F[j])}
            for q in range(4):row.update({f'direct_q{q}':float(directp[q]),f'EC_per_initial_Be_q{q}':float(ecp[q]),f'EC_conditional_q{q}':float(ecp[q]/F[j]) if F[j]>0 else None,f'Y_Li7_q{q}':float(Y[q])})
            histories.append(row)
            if model=='ground_Milne':
                array=np.r_[spectators,Y];be3=B*float(b3(uu));be4=B*float(b4(uu));boundLi=float(np.dot(3-np.arange(4),Y));bound=boundLi+be3
                # Trace algebra avoids subtracting two O(1) donor charge sums.
                delta_nuclear=3*(Y.sum()-L)+4*(be3+be4-B);expected_nuclear=-B*F[j];delta_free=delta_nuclear-bound
                ionic_delta=3*(Y.sum()-L)-boundLi+3*be3+4*be4-4*B
                fullmass=float(np.dot(mass17,array)+7*(be3+be4)+excluded_mass)
                ledger={'mass':abs(fullmass-original_mass)/max(abs(original_mass),1e-25),
                    'nuclear_charge':abs(delta_nuclear-expected_nuclear)/max(B,1e-25),'ionic_free':abs(ionic_delta-delta_free)/max(B,1e-25),
                    'electron_total':abs(delta_free+bound-expected_nuclear)/max(B,1e-25),
                    'tracked17_electrons':abs(np.dot(charge17,array)+boundLi-np.dot(Z17,array))/max(abs(np.dot(Z17,array)),1e-25)}
                ledgers.append(ledger)
                inv={'u':float(uu),'z':float(z[j]),**dict(zip(contract['inventory']['order'],map(float,array))),
                    'Be7_4_aux':be4,'Be7_3_aux':be3,'excluded_unchanged_mass':excluded_mass,'excluded_unchanged_nuclear_charge':excluded_charge,'full_baryon_sum':fullmass,
                    'delta_nuclear_charge':delta_nuclear,'bound_electrons_Li':boundLi,'bound_electrons_Be':be3,'delta_free_electrons':delta_free,'delta_ionic_charge':ionic_delta,
                    'delta_total_electrons':delta_free+bound,'trace_electron_delta_over_Ye':abs(delta_free)/Ye}
                inventory.append(inv)
        for zz in [100000,50000,30000,20000,15000,10000]:
            uu=math.log(100001/(1+zz));states=sol.sol(uu);ff=float(Ffull(uu));pp=np.r_[states[:3],1-sum(states[:3]),states[3:],ff-sum(states[3:])]
            _,_,beta,r,hh=coefficients(uu,interp,model);logs=np.r_[0,np.cumsum(np.log(beta)-np.log(r))];pi=np.exp(logs-logsumexp(logs));T=2.7255*(1+zz)
            if zz==100000:stationary[model]={'pi':pi.tolist(),'initial_stationary_bound_fraction':float(pi[:3].sum())}
            row={'model':model,'state_diagnostic_method':'PCHIP_of_saved_1025_output_states' if label=='ground_production' else 'solver_dense_output','z':zz,'T_K':T,'ne_cm3_inverse':Ye*nb0*(1+zz)**3,'H_s_inverse':hh}
            for q in range(4):row.update({f'pi_q{q}':float(pi[q]),f'direct_minus_pi_q{q}':float(pp[q]-pi[q]),f'EC_conditional_q{q}':float(pp[4+q]/ff) if ff>0 else None,f'EC_conditional_minus_pi_q{q}':float(pp[4+q]/ff-pi[q]) if ff>0 else None})
            row.update({'direct_mean_charge':float(np.dot(np.arange(4),pp[:4])),'direct_bound_electrons':float(np.dot(3-np.arange(4),pp[:4])),'EC_conditional_mean_charge':float(np.dot(np.arange(4),pp[4:])/ff) if ff>0 else None,'EC_conditional_bound_electrons':float(np.dot(3-np.arange(4),pp[4:])/ff) if ff>0 else None})
            for q in range(3):row.update({f'beta_q{q}_over_H':float(beta[q]/hh),f'ne_alpha_q{q}_over_H':float(r[q]/hh)})
            diagnostics.append(row)
    csvout('li_charge_history.csv',histories);csvout('li_charge_diagnostics.csv',diagnostics);csvout('inventory17_early.csv',inventory)
    metrics.update({'population_min':min(popmins),'per_origin_sum_abs':max(normal),'Li_source_sum_normalized':max(sourcechecks),'ledger_max_relative':max(v for r in ledgers for v in r.values())})
    availability={'channels':provider.rows,'isotope_consumers':{'HI':['H1','D','T'],'HeI':['He3','He4'],'HeII':['He3','He4'],'LiI':['Li7'],'LiII':['Li7'],'LiIII':['Li7']},'n_atomic_channel':None,'isotope_recoil_accuracy':'not resolved',
        'native_product_activation':False,'first13':'frozen fully ionized early donor bath spectators','missing_dependencies':contract['dependency_boundary'],'missing_processes':['multilevel','dielectronic recombination','electron-impact ionization','charge exchange','radiation transfer']}
    dump(OUT/'rate_availability_map.json',availability)
    sensitivity={'maximum_population_difference_per_origin':float(np.max(abs(solutions['total_RR_sensitivity'][0]-baseline))),'endpoint_ground':baseline[:,-1].tolist(),'endpoint_total_RR':solutions['total_RR_sensitivity'][0][:,-1].tolist(),'interpretation':'model sensitivity; not statistical uncertainty or LTE identity'}
    summary={'contract_id':contract['contract_id'],'metrics':metrics,'solver_comparisons':comparisons,'solver_diagnostics':solverdiag,'timings':timings,'rate_tables_wall_seconds':'UNKNOWN; original saved work reused',
        'stationary_initial':stationary,'early_Be_source_omitted_bound':br['early_tail_bound'],'donor_original_baryon_sum':original_mass,'donor_original_nuclear_charge':original_charge,'excluded_donor_unchanged':excluded,
        'RR_sensitivity':sensitivity,'maximum_sampled_energy_eV':max(r['max_sampled_eV'] for r in finals),'trace_electron_delta_over_Ye_max':max(r['trace_electron_delta_over_Ye'] for r in inventory),
        'tiny_fraction_reporting_floor':1e-8,'tiny_neutral_fraction_relative_accuracy':'not established by ODE absolute tolerance','scope':'Reduced radiative ground model; early frozen donor bath; standalone17 adapter; no native activation or late history',
        'public_Fortran_execution':'NOT_RUN_compiler_unavailable' if shutil.which('gfortran') is None else 'COMPILER_PRESENT_NOT_EXECUTED'}
    dump(OUT/'li_thermal_summary.json',summary)
    sys.path.insert(0,str(ROOT/'tests'));from test_li_thermal_validation import validate
    tests=validate(metrics,comparisons,solverdiag,summary)
    tests['checks'].append({'name':'balanced_wrapper_arithmetic','observed':wrapper['relative_error'],'limit':float(wrapper['limit']),'passed':wrapper['passed']})
    tests['passed']=tests['passed'] and wrapper['passed']
    dump(OUT/'li_thermal_tests.json',tests)
    elapsed=time.perf_counter()-start;signal.alarm(0)
    evidence=json.loads((ROOT/'evidence/LI_THERMAL_EXECUTION.json').read_text())
    evidence.update({'status':'PASS_PENDING_INDEPENDENT_REVIEW' if tests['passed'] else 'FAIL_RETURN_TO_AUTHORITY','repairs':1,'continuation_internal_wall_seconds':elapsed,'continuation_command_wall_seconds':'PENDING_EXTERNAL_MEASUREMENT','tests':tests,'timings':timings,'solver_diagnostics':solverdiag,'wrapper_check':wrapper,'quadrature_repeated':False,'production_repeated':False,'rate_metrics':'algebraic reconstruction from preserved raw records','repair_id':contract['repair_amendment']['id'],'executor_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'continuation_command':'OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 timeout 26s python code/li_thermal_resume.py > results/laneA/resume.log 2>&1','observed_runtime_model':'UNKNOWN'})
    dump(ROOT/'evidence/LI_THERMAL_EXECUTION.json',evidence)
    print(json.dumps({'status':evidence['status'],'wall_seconds':elapsed,'metrics':metrics,'comparisons':comparisons,'timings':timings,'RR_sensitivity':sensitivity}))
    return 0 if tests['passed'] else 1

if __name__=='__main__':
    try:sys.exit(main())
    except BaseException as error:
        if not isinstance(error,SystemExit):
            failure={'error_type':type(error).__name__,'error':str(error),'repair_consumed':True,'status':'FAIL_RETURN_TO_AUTHORITY'}
            dump(OUT/'continuation_failure.json',failure)
        raise
