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

def main():
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    def timeout(*_):raise TimeoutError('30-second new numerical budget exhausted')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(30)
    contract=json.loads((ROOT/'spec/LI_THERMAL_CONTRACT.json').read_text());paths={};manifest={}
    for key,info in contract['inputs'].items():
        dest=ROOT/'inputs/laneA'/(key+'_'+Path(info['path']).name);source=dest if dest.exists() else Path(info['path'])
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        assert digest==info['sha256'] and source.stat().st_size==info['bytes'],key+' immutable source mismatch'
        if source!=dest:shutil.copyfile(source,dest)
        paths[key]=dest;manifest[key]={'original_path':info['path'],'original_sha256':digest,'copied_path':str(dest.relative_to(ROOT)),'copied_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bytes':dest.stat().st_size}
    dump(ROOT/'inputs/laneA/manifest.json',manifest)
    provider=Provider(paths,contract['atomic_channels']);donor=json.loads(paths['donor'].read_text());bc=json.loads(paths['Be_contract'].read_text());br=json.loads(paths['Be_result'].read_text())
    dump(OUT/'provider_rates.json',{'channels':provider.rows,'LiI_core_PH1':provider.core,'public_Fortran_execution':'NOT_RUN_compiler_unavailable' if shutil.which('gfortran') is None else 'COMPILER_PRESENT_NOT_EXECUTED',
        'source_manifest':manifest,'LiI_ground_inverse':'2s only; 1s core opacity separate','alpha_g_stim_definition':'spontaneous plus stimulated','RR_charge_convention':'table label is recombined product','HeI_RR':'b table row'})
    metrics={'rate64_128_max_relative':0.,'tail60_80_max_relative':0.,'identity_max_relative':0.,'W_K_Q_max_relative':0.,'Decimal_formula_max_relative':0.}
    rates=[];two=[];core=[];raw=[]
    def pair(name,te,tg,isc=False):
        final=provider.rate(name,float(te),float(tg),128,isc);coarse=provider.rate(name,float(te),float(tg),64,isc)
        for typ in ['electron','photon']:
            v=np.array(final['scaled_'+typ]);w=np.array(coarse['scaled_'+typ]);tail=np.array(final['scaled_'+typ+'_tail'])
            mask=v>0
            if np.any(mask):
                metrics['rate64_128_max_relative']=max(metrics['rate64_128_max_relative'],float(np.max(abs(v[mask]-w[mask])/v[mask])))
                metrics['tail60_80_max_relative']=max(metrics['tail60_80_max_relative'],float(np.max(abs(tail[mask])/v[mask])))
        metrics['W_K_Q_max_relative']=max(metrics['W_K_Q_max_relative'],rel(final['W_abs_J_s'],final['K_primary_J_s']+final['Q_threshold_J_s']))
        if tg>0:
            sp=final['scaled_photon'];x0=(64.39 if isc else provider.rows[name]['chi_eV'])*EV/(KB*tg)
            metrics['W_K_Q_max_relative']=max(metrics['W_K_Q_max_relative'],rel(sp[2],sp[3]+x0*sp[1]))
        if te==tg and not isc:
            residual=abs(math.expm1(final['log_beta_s_inverse']-math.log(final['alpha_g_stim_cm3_s'])-final['log_Saha_cm3_inverse']))
            metrics['identity_max_relative']=max(metrics['identity_max_relative'],residual)
            final['detailed_balance_relative']=residual
        else:final['detailed_balance_relative']=None
        raw.extend([dict(coarse,core=isc),dict(final,core=isc)])
        return serial(final)
    for T in np.geomspace(100,1e6,81):
        for name in provider.rows:rates.append(pair(name,T,T))
        cr=pair('LiI',T,T,True);cr={k:v for k,v in cr.items() if not any(x in k for x in ['alpha_','Saha','RR','stimulated','detailed_balance'])};cr['shell']='1s_core';outer=next(r for r in rates[-6:] if r['ion']=='LiI');cr['X_core_J_s']=(64.39-5.392)*EV*cr['beta_s_inverse'];cr.update({'total_opacity_'+f:cr[f]+outer[f] for f in ['beta_s_inverse','W_abs_J_s','K_primary_J_s','Q_threshold_J_s']});core.append(cr)
    for name in ['LiI','LiII','LiIII']:
        for te in contract['two_temperature_grid']['Te_K']:
            for ratio in contract['two_temperature_grid']['Tgamma_over_Te']:two.append(pair(name,te,te*ratio))
    metrics['nonfinite_or_nonpositive_alpha_count']=sum(not(math.isfinite(r['alpha_g_sp_cm3_s']) and r['alpha_g_sp_cm3_s']>0 and math.isfinite(r['alpha_g_stim_cm3_s']) and r['alpha_g_stim_cm3_s']>0) for r in rates+two)
    metrics['nonfinite_log_beta_count']=sum(not math.isfinite(r['log_beta_s_inverse']) for r in rates+core)
    csvout('thermal_rates.csv',rates);csvout('two_temperature_rates.csv',two);csvout('LiI_core_blackbody.csv',core)
    dump(OUT/'rate_quadrature_raw.json',raw)
    decimal=[]
    for name in provider.rows:
        for T in [100,1e4,1e6]:
            e=provider.rows[name]['chi_eV']+KB*T/EV
            for kind,value,reference in [('cross_section_Mb',float(provider.sigma(name,e)),provider.sigma_decimal(name,e)),('total_RR_cm3_s',float(provider.rr(name,T)),provider.rr_decimal(name,T))]:
                error=rel(value,reference);metrics['Decimal_formula_max_relative']=max(metrics['Decimal_formula_max_relative'],error)
                decimal.append({'ion':name,'T_K':T,'kind':kind,'kernel':value,'Decimal_reference':reference,'relative':error})
    dump(OUT/'decimal_formula_checks.json',decimal)
    independent=[]
    for name,row in provider.rows.items():
        for T in [300,1e4,1e6]:
            x0=row['chi_eV']*EV/(KB*T);values=[];errors=[]
            for kind in ['alpha_sp','alpha_stim','beta']:
                def fn(t):
                    e=row['chi_eV']+KB*T*t/EV;s=float(provider.sigma(name,e));base=s*(x0+t)**2*math.exp(-t)
                    return base if kind=='alpha_sp' else base/(-math.expm1(-(x0+t)))
                val=err=0.
                edges=provider.intervals(name,T)
                for lo,hi in zip(edges[:-1],edges[1:]):
                    v,er=quad(fn,lo,hi,epsabs=1e-11,epsrel=2e-12,limit=100);val+=v;err+=er
                values.append(val*1e-22);errors.append(err)
            actual=provider.rate(name,T,T,128)
            target=[actual['scaled_electron'][0],actual['scaled_electron'][1],actual['scaled_photon'][1]]
            independent.append({'ion':name,'T_K':T,'independent_scaled_alpha_sp_stim_beta':values,'QUADPACK_error_Mb_units':errors,'relative':[rel(a,b) for a,b in zip(values,target)]})
    metrics['independent_quad_max_relative']=max(v for r in independent for v in r['relative']);dump(OUT/'independent_quad_checks.json',independent)
    rate_elapsed=time.perf_counter()-start
    # Early kinetic tables, positive logs only; no physical quadrature in any RHS.
    uend=math.log(100001/10001);ugrid=np.linspace(0,uend,513);li=['LiI','LiII','LiIII']
    def kinetic_row(u):
        T=2.7255*100001*math.exp(-float(u));rs=[provider.rate(name,T,T,128) for name in li]
        return [r['log_beta_s_inverse'] for r in rs]+[math.log(r['alpha_g_stim_cm3_s']) for r in rs]+[math.log(r['alpha_total_RR_cm3_s']) for r in rs]
    table=np.array([kinetic_row(u) for u in ugrid]);np.savez(OUT/'kinetic_rate_table.npz',u=ugrid,log_rates=table)
    interp=PchipInterpolator(ugrid,table,axis=0,extrapolate=False);coarseinterp=PchipInterpolator(ugrid[::2],table[::2],axis=0,extrapolate=False)
    midpoint=(ugrid[:-1:2]+ugrid[1::2])/2
    direct=np.array([kinetic_row(u) for u in midpoint]);estimated=interp(midpoint)
    metrics['rate_midpoint_direct_max_relative']=float(np.max(abs(np.expm1(estimated-direct))))
    np.savez(OUT/'rate_midpoint_checks.npz',u=midpoint,log_direct=direct,log_interpolated=estimated)
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
    solutions={};timings={};solverdiag=[]
    def solve(label,model,source,Fsource,method,rtol,atol):
        tic=time.perf_counter()
        def fun(u,y):
            matrix,reward,*_=coefficients(u,source,model);result=np.empty(6)
            result[:3]=matrix@y[:3]+np.array([0,0,reward]);result[3:]=matrix@y[3:]+np.array([0,0,reward*float(Fsource(u))]);return result
        def jac(u,y):
            matrix,*_=coefficients(u,source,model);result=np.zeros((6,6));result[:3,:3]=matrix;result[3:,3:]=matrix;return result
        sol=solve_ivp(fun,(0,uend),np.zeros(6),method=method,jac=jac,rtol=rtol,atol=atol,t_eval=output,dense_output=True)
        timings[label]=time.perf_counter()-tic;solverdiag.append({'label':label,'success':sol.success,'message':sol.message,'nfev':sol.nfev,'njev':sol.njev,'nlu':sol.nlu})
        assert sol.success,label+' solver failure'
        normalized=np.vstack([sol.y[:3],1-np.sum(sol.y[:3],axis=0),sol.y[3:],Fsource(output)-np.sum(sol.y[3:],axis=0)])
        np.savez(OUT/(label+'.npz'),u=output,z=z,states=sol.y,populations=normalized,internal_u=sol.t)
        solutions[label]=(normalized,sol)
    solve('ground_production','ground_Milne',interp,Ffull,'Radau',1e-8,1e-13)
    solve('ground_BDF','ground_Milne',interp,Ffull,'BDF',3e-9,3e-14)
    solve('ground_257','ground_Milne',coarseinterp,Ffull,'Radau',1e-8,1e-13)
    solve('ground_half_Be','ground_Milne',interp,Fhalf,'Radau',1e-8,1e-13)
    solve('total_RR_sensitivity','total_RR_sensitivity',interp,Ffull,'Radau',1e-8,1e-13)
    baseline=solutions['ground_production'][0]
    comparisons={}
    for label in ['ground_BDF','ground_257','ground_half_Be']:
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
            row={'model':model,'z':zz,'T_K':T,'ne_cm3_inverse':Ye*nb0*(1+zz)**3,'H_s_inverse':hh}
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
    summary={'contract_id':contract['contract_id'],'metrics':metrics,'solver_comparisons':comparisons,'solver_diagnostics':solverdiag,'timings':timings,'rate_tables_wall_seconds':rate_elapsed,
        'stationary_initial':stationary,'early_Be_source_omitted_bound':br['early_tail_bound'],'donor_original_baryon_sum':original_mass,'donor_original_nuclear_charge':original_charge,'excluded_donor_unchanged':excluded,
        'RR_sensitivity':sensitivity,'maximum_sampled_energy_eV':max(r['max_sampled_eV'] for r in rates+two+core),'trace_electron_delta_over_Ye_max':max(r['trace_electron_delta_over_Ye'] for r in inventory),
        'tiny_fraction_reporting_floor':1e-8,'tiny_neutral_fraction_relative_accuracy':'not established by ODE absolute tolerance','scope':'Reduced radiative ground model; early frozen donor bath; standalone17 adapter; no native activation or late history',
        'public_Fortran_execution':'NOT_RUN_compiler_unavailable' if shutil.which('gfortran') is None else 'COMPILER_PRESENT_NOT_EXECUTED'}
    dump(OUT/'li_thermal_summary.json',summary)
    sys.path.insert(0,str(ROOT/'tests'));from test_li_thermal_validation import validate
    tests=validate(metrics,comparisons,solverdiag,summary)
    dump(OUT/'li_thermal_tests.json',tests)
    elapsed=time.perf_counter()-start;signal.alarm(0)
    evidence={'contract_id':contract['contract_id'],'requested_executor_model':'gpt-6.1-sol','observed_runtime_model':'UNKNOWN','requested_authority':'Astra','observed_authority_model':'UNKNOWN','threads':1,
        'command':'OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 timeout 30s python code/li_thermal_run.py > results/laneA/run.log 2>&1',
        'rate_midpoint_selection':'u=(2j+0.5)*U/512,j=0..255; theory-authorized mechanical clarification','wall_seconds':elapsed,'numerical_seconds_limit':30,'timings':timings,'test_passes':1,'repairs':0,'tests':tests,'status':'PASS_PENDING_INDEPENDENT_REVIEW' if tests['passed'] and elapsed<=30 else 'FAIL_RETURN_TO_AUTHORITY',
        'public_Fortran_execution':summary['public_Fortran_execution'],'versions':{'Python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform()},'runtime_model_cost_telemetry':'UNKNOWN; unavailable'}
    dump(ROOT/'evidence/LI_THERMAL_EXECUTION.json',evidence)
    print(json.dumps({'status':evidence['status'],'wall_seconds':elapsed,'metrics':metrics,'comparisons':comparisons,'timings':timings,'RR_sensitivity':sensitivity}))
    return 0 if tests['passed'] and elapsed<=30 else 1
if __name__=='__main__':
    try:sys.exit(main())
    except BaseException as error:
        if not isinstance(error,SystemExit):
            OUT.mkdir(parents=True,exist_ok=True);dump(OUT/'failure.json',{'error_type':type(error).__name__,'error':str(error)})
        raise
