#!/usr/bin/env python3
"""Frozen bounded Unit8 early thermal atomic bridge; no native activation."""
import csv,hashlib,json,math,os,platform,re,shutil,signal,sys,time
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp,quad
from scipy.interpolate import PchipInterpolator
from scipy.special import logsumexp
from types import SimpleNamespace
from li_thermal_rates import Provider,KB,EV,ME,H,C,C_LIGHT
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/laneA'

def json_scalar(value):
    if isinstance(value,np.generic):return value.item()
    raise TypeError(type(value).__name__)
def dump(path,obj):path.write_text(json.dumps(obj,indent=2,allow_nan=False,default=json_scalar)+'\n')
def csvout(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def serial(r):return {k:v for k,v in r.items() if not k.startswith('scaled_')}
def rel(a,b):return abs(a-b)/max(abs(a),abs(b)) if a or b else 0.

def main():
    start=time.perf_counter()
    def timeout(*_):raise TimeoutError('single dependency-safe25-second deadline')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(25)
    contract=json.loads((ROOT/'spec/LI_THERMAL_CONTRACT.json').read_text())
    paths={}
    for key,info in contract['inputs'].items():
        dest=ROOT/'inputs/laneA'/(key+'_'+Path(info['path']).name)
        assert hashlib.sha256(dest.read_bytes()).hexdigest()==info['sha256'] and dest.stat().st_size==info['bytes'],key+' immutable source mismatch'
        paths[key]=dest
    provider=Provider(paths,contract['atomic_channels'])
    donor=json.loads(paths['donor'].read_text());bc=json.loads(paths['Be_contract'].read_text());br=json.loads(paths['Be_result'].read_text())
    metrics={'rate64_128_max_relative':0.,'tail60_80_max_relative':0.,'identity_max_relative':0.,'W_K_Q_max_relative':0.,'Decimal_formula_max_relative':0.}
    raw=json.loads((OUT/'rate_quadrature_raw.json').read_text())
    energy_rows=[];scaled_max=normal_raw_max=0.;subnormal_count=0
    for coarse,final in zip(raw[::2],raw[1::2]):
        for typ in ['electron','photon']:
            v=np.array(final['scaled_'+typ]);w=np.array(coarse['scaled_'+typ]);tail=np.array(final['scaled_'+typ+'_tail']);mask=v>0
            if np.any(mask):
                metrics['rate64_128_max_relative']=max(metrics['rate64_128_max_relative'],float(np.max(abs(v[mask]-w[mask])/v[mask])))
                metrics['tail60_80_max_relative']=max(metrics['tail60_80_max_relative'],float(np.max(abs(tail[mask])/v[mask])))
        metrics['W_K_Q_max_relative']=max(metrics['W_K_Q_max_relative'],rel(final['W_abs_J_s'],final['K_primary_J_s']+final['Q_threshold_J_s']))
        raw_error=rel(final['W_abs_J_s'],final['K_primary_J_s']+final['Q_threshold_J_s'])
        normal=bool(max(final['W_abs_J_s'],final['K_primary_J_s']+final['Q_threshold_J_s'])>=np.finfo(float).tiny)
        if final['Tgamma_K']>0:
            if normal:normal_raw_max=max(normal_raw_max,raw_error)
            else:subnormal_count+=1
            energy_rows.append({'ion':final['ion'],'T_K':final['Tgamma_K'],'core':final['core'],'raw_relative':raw_error,'W':final['W_abs_J_s'],'K':final['K_primary_J_s'],'Q':final['Q_threshold_J_s'],'normal_range':normal})
        te=final['Te_K'];tg=final['Tgamma_K'];isc=final['core']
        if tg>0:
            sp=final['scaled_photon'];x0=(64.39 if isc else provider.rows[final['ion']]['chi_eV'])*EV/(KB*tg)
            scaled_error=rel(sp[2],sp[3]+x0*sp[1]);scaled_max=max(scaled_max,scaled_error)
        if te==tg and not isc:
            residual=abs(math.expm1(final['log_beta_s_inverse']-math.log(final['alpha_g_stim_cm3_s'])-final['log_Saha_cm3_inverse']))
            metrics['identity_max_relative']=max(metrics['identity_max_relative'],residual)
    finals=raw[1::2]
    metrics['nonfinite_or_nonpositive_alpha_count']=sum(not(math.isfinite(r['alpha_g_sp_cm3_s']) and r['alpha_g_sp_cm3_s']>0 and math.isfinite(r['alpha_g_stim_cm3_s']) and r['alpha_g_stim_cm3_s']>0) for r in finals if not r['core'])
    metrics['nonfinite_log_beta_count']=sum(not math.isfinite(r['log_beta_s_inverse']) for r in finals if r['Tgamma_K']>0)
    metrics['Decimal_formula_max_relative']=max(r['relative'] for r in json.loads((OUT/'decimal_formula_checks.json').read_text()))
    metrics['independent_quad_max_relative']=max(v for r in json.loads((OUT/'independent_quad_checks.json').read_text()) for v in r['relative'])
    mid=np.load(OUT/'rate_midpoint_checks.npz');metrics['rate_midpoint_direct_max_relative']=float(np.max(abs(np.expm1(mid['log_interpolated']-mid['log_direct']))))
    energy={'raw_all_rows_max_relative':metrics['W_K_Q_max_relative'],'raw_worst_row':max(energy_rows,key=lambda row:row['raw_relative']),'normal_range_raw_max_relative':normal_raw_max,'scaled_all_rows_max_relative':scaled_max,'subnormal_or_zero_exclusion_count':subnormal_count,'criterion':2e-8,'scaled_passed':scaled_max<=2e-8,'normal_raw_passed':normal_raw_max<=2e-8}
    metrics['W_K_Q_max_relative']=max(scaled_max,normal_raw_max)
    dump(OUT/'ready_energy_checks.json',energy)
    independent=[];spot_failures=[];priorchecks=json.loads((OUT/'independent_quad_checks.json').read_text())
    for name,row in provider.rows.items():
        for T in [300.,1e4,1e6]:
            try:
                chi=row['chi_eV']*EV;x0=chi/(KB*T)
                def photon_coordinate(x):
                    energy_eV=KB*T*x/EV
                    cross=float(provider.sigma(name,energy_eV))
                    return cross*x*x*math.exp(-(x-x0))/(-math.expm1(-x))
                def electron_coordinate(y):
                    energy_eV=chi*(1+y)/EV
                    cross=float(provider.sigma(name,energy_eV))
                    return cross*(1+y)**2*math.exp(-x0*y)/(-math.expm1(-x0*(1+y)))
                Ibeta=Ialpha=betaerror=alphaerror=0.
                edges=provider.intervals(name,T)
                for lo,hi in zip(edges[:-1],edges[1:]):
                    val,err=quad(photon_coordinate,x0+lo,x0+hi,epsabs=0,epsrel=2e-12,limit=100);Ibeta+=val;betaerror+=err
                    val,err=quad(electron_coordinate,lo/x0,hi/x0,epsabs=0,epsrel=2e-12,limit=100);Ialpha+=val;alphaerror+=err
                D=row['saha_d']*(2*math.pi*ME*KB*T/H**2)**1.5
                logbeta=math.log(C)+3*math.log(KB*T)-x0+math.log(Ibeta)+math.log(1e-22)
                logalpha=math.log(C)+3*math.log(chi)-math.log(D)+math.log(Ialpha)+math.log(1e-22)+math.log(1e6)
                logS=math.log(D)-x0-math.log(1e6)
                residual=abs(math.expm1(logbeta-logalpha-logS))
                old=next(v for v in priorchecks if v['ion']==name and v['T_K']==T)
                bcross=rel(Ibeta*1e-22,old['independent_scaled_alpha_sp_stim_beta'][2]);across=rel(x0**3*Ialpha*1e-22,old['independent_scaled_alpha_sp_stim_beta'][1])
                independent.append({'ion':name,'T_K':T,'x0':x0,'Ibeta_Mb':Ibeta,'Ialpha_Mb':Ialpha,'photon_quad_error':betaerror,'electron_quad_error':alphaerror,'log_beta':logbeta,'log_alpha_cm3':logalpha,'log_S_cm3':logS,'identity_relative':residual,'saved_beta_crosscheck_relative':bcross,'saved_alpha_stim_crosscheck_relative':across,'passed':max(residual,bcross,across)<=2e-8})
            except Exception as error:
                if isinstance(error,TimeoutError):raise
                spot_failures.append({'ion':name,'T_K':T,'error_type':type(error).__name__,'error':str(error)})
            dump(OUT/'independent_detailed_balance_spots.json',{'spots':independent,'failures':spot_failures,'required_count':18,'completed':len(independent)==18,'passed':len(independent)==18 and not spot_failures and all(v['passed'] for v in independent),'coordinates':'separate photon x=epsilon/kT and electron y=(epsilon-chi)/chi callbacks/quadrature'})
    metrics['independent_DB_max_relative']=max([v['identity_relative'] for v in independent],default=0.)
    metrics['independent_DB_saved_crosscheck_max_relative']=max([max(v['saved_beta_crosscheck_relative'],v['saved_alpha_stim_crosscheck_relative']) for v in independent],default=0.)
    dump(OUT/'ready_reconstructed_rate_metrics.json',metrics)
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
    solutions={'ground_production':(production['populations'],SimpleNamespace(sol=saved_dense))};timings={};solverdiag=[json.loads((OUT/'ground_BDF_balanced_solver.json').read_text()),{'label':'ground_production','success':True,'message':'preserved completed Radau production; original counters unavailable','nfev':None,'njev':None,'nlu':None,'observed_from':'saved full1025 output artifact'}]
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
        diagnostic.update({'status':sol.status,'method':method,'wall_seconds':timings[label],'time_reached_u':float(sol.sol.ts[-1]),'last_output_u':float(sol.t[-1]) if len(sol.t) else None})
        dump(OUT/(label+'_solver.json'),diagnostic)
        if not sol.success:
            np.savez(OUT/(label+'_partial.npz'),u=sol.t,states=sol.y,internal_breakpoints=sol.sol.ts,last_state=sol.sol(sol.sol.ts[-1]))
            return
        normalized=np.vstack([sol.y[:3],1-np.sum(sol.y[:3],axis=0),sol.y[3:],Fsource(output)-np.sum(sol.y[3:],axis=0)])
        np.savez(OUT/(label+'.npz'),u=output,z=z,states=sol.y,populations=normalized,internal_u=sol.t)
        solutions[label]=(normalized,sol)
    for label,model,source,Fsource in [('ground_257','ground_Milne',coarseinterp,Ffull),('ground_half_Be','ground_Milne',interp,Fhalf),('total_RR_sensitivity','total_RR_sensitivity',interp,Ffull)]:
        try:solve(label,model,source,Fsource,'Radau',1e-8,1e-13)
        except Exception as error:
            if isinstance(error,TimeoutError):raise
            diagnostic={'label':label,'success':False,'error_type':type(error).__name__,'message':str(error)}
            solverdiag.append(diagnostic);dump(OUT/(label+'_solver.json'),diagnostic)
    baseline=solutions['ground_production'][0]
    comparisons={}
    for label in ['ground_257','ground_half_Be']:
        if label not in solutions:continue
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
        if label not in solutions:continue
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
            for q in range(3):
                row.update({f'beta_q{q}_over_H':float(beta[q]/hh),f'ne_alpha_q{q}_over_H':float(r[q]/hh)})
                if model=='ground_Milne':
                    ion=provider.rows[['LiI','LiII','LiIII'][q]];D=ion['saha_d']*(2*math.pi*ME*KB*T/H**2)**1.5;logratio=math.log(D)-ion['chi_eV']*EV/(KB*T)-math.log(Ye*nb0*(1+zz)**3*1e6)
                    row.update({f'Saha_q{q}_ratio':math.exp(logratio),f'stationary_q{q}_ratio':float(beta[q]/r[q]),f'stationary_Saha_relative_q{q}':abs(math.expm1(math.log(beta[q]/r[q])-logratio))})
            diagnostics.append(row)
    csvout('li_charge_history.csv',histories);csvout('li_charge_diagnostics.csv',diagnostics);csvout('inventory17_early.csv',inventory)
    metrics.update({'population_min':min(popmins),'per_origin_sum_abs':max(normal),'Li_source_sum_normalized':max(sourcechecks),'ledger_max_relative':max(v for r in ledgers for v in r.values())})
    availability={'channels':provider.rows,'isotope_consumers':{'HI':['H1','D','T'],'HeI':['He3','He4'],'HeII':['He3','He4'],'LiI':['Li7'],'LiII':['Li7'],'LiIII':['Li7']},'n_atomic_channel':None,'isotope_recoil_accuracy':'not resolved',
        'native_product_activation':False,'first13':'frozen fully ionized early donor bath spectators','missing_dependencies':contract['dependency_boundary'],'missing_processes':['multilevel','dielectronic recombination','electron-impact ionization','charge exchange','radiation transfer']}
    dump(OUT/'rate_availability_map.json',availability)
    sensitivity={'maximum_population_difference_per_origin':float(np.max(abs(solutions['total_RR_sensitivity'][0]-baseline))),'endpoint_ground':baseline[:,-1].tolist(),'endpoint_total_RR':solutions['total_RR_sensitivity'][0][:,-1].tolist(),'interpretation':'model sensitivity; not statistical uncertainty or LTE identity'} if 'total_RR_sensitivity' in solutions else {'available':False,'reason':'total RR solve unsuccessful'}
    summary={'contract_id':contract['contract_id'],'metrics':metrics,'solver_comparisons':comparisons,'solver_diagnostics':solverdiag,'timings':timings,'rate_tables_wall_seconds':'UNKNOWN; original saved work reused',
        'stationary_initial':stationary,'early_Be_source_omitted_bound':br['early_tail_bound'],'donor_original_baryon_sum':original_mass,'donor_original_nuclear_charge':original_charge,'excluded_donor_unchanged':excluded,
        'RR_sensitivity':sensitivity,'maximum_sampled_energy_eV':max(r['max_sampled_eV'] for r in finals),'trace_electron_delta_over_Ye_max':max(r['trace_electron_delta_over_Ye'] for r in inventory),
        'tiny_fraction_reporting_floor':1e-8,'tiny_neutral_fraction_relative_accuracy':'not established by ODE absolute tolerance','scope':'Reduced radiative ground model; early frozen donor bath; standalone17 adapter; no native activation or late history',
        'public_Fortran_execution':'NOT_RUN_compiler_unavailable' if shutil.which('gfortran') is None else 'COMPILER_PRESENT_NOT_EXECUTED'}
    dump(OUT/'li_thermal_summary.json',summary)
    sys.path.insert(0,str(ROOT/'tests'));from test_li_thermal_validation import validate
    tests=validate(metrics,comparisons,solverdiag,summary)
    tests['checks'].append({'name':'required_independent_BDF_comparison','observed':'FAILED_REFERENCE','limit':'successful independent comparison required','passed':False})
    for key in ['independent_DB_max_relative','independent_DB_saved_crosscheck_max_relative']:
        tests['checks'].append({'name':key,'observed':metrics[key],'limit':2e-8,'passed':metrics[key]<=2e-8 and len(independent)==18 and not spot_failures})
    tests['passed']=False
    rate_checks=[v for v in tests['checks'] if v['name'] in ['nonfinite_or_nonpositive_alpha_count','nonfinite_log_beta_count','rate64_128_max_relative','tail60_80_max_relative','identity_max_relative','W_K_Q_max_relative','Decimal_formula_max_relative','independent_quad_max_relative','rate_midpoint_direct_max_relative','independent_DB_max_relative','independent_DB_saved_crosscheck_max_relative']]
    groups={'rates':{'completed':True,'passed':all(v['passed'] for v in rate_checks) and len(independent)==18 and not spot_failures,'admitted':'PENDING_INDEPENDENT_REVIEW','checks':rate_checks},'BDF':{'completed':False,'passed':False,'admitted':False,'status':'REFERENCE_HOLD','failed_reference':solverdiag[0]},'ledger':{'completed':True,'passed':metrics['ledger_max_relative']<=1e-12,'admitted':'INTERNAL_CONSISTENCY_ONLY_PENDING_REVIEW','max_relative':metrics['ledger_max_relative']}}
    for label in ['ground_production','ground_257','ground_half_Be','total_RR_sensitivity']:
        if label not in solutions:groups[label]={'completed':False,'passed':False,'admitted':False};continue
        pp=solutions[label][0];minpop=float(pp.min());norm=max(float(np.max(abs(pp[:4].sum(axis=0)-1))),float(np.max(abs(pp[4:].sum(axis=0)-F))))
        source_res=float(np.max(abs((L*pp[:4]+B*pp[4:]).sum(axis=0)-(L+B*F))/np.maximum(np.maximum(L,B*F),1e-30)))
        group={'completed':True,'passed':minpop>=-2e-11 and norm<=2e-11 and source_res<=2e-11,'admitted':'PROVISIONAL_BDF_REFERENCE_HOLD','population_min':minpop,'per_origin_sum_abs':norm,'Li_source_sum_normalized':source_res}
        if label in comparisons:group.update(comparisons[label]);group['passed']=group['passed'] and comparisons[label]['max_absolute_per_origin']<=5e-6
        groups[label]=group
    tests['scoped_groups']=groups;tests['status']='PARTIAL_READY_BDF_REFERENCE_HOLD'
    tests['algebraic_identity_label']='shared-quadrature algebraic consistency; separate independent_DB spots provide independent numerical identity check'
    summary.update({'status':'PARTIAL_READY_BDF_REFERENCE_HOLD','full_suite_passed':False,'BDF_comparison_available':False,'scoped_groups':groups,'energy_checks':energy,'independent_detailed_balance_spots':'independent_detailed_balance_spots.json','shared_quadrature_identity_role':'algebraic consistency only','production_diagnostic_reconstruction':'PCHIP_of_saved_1025_output_states','repair_consumed':True})
    dump(OUT/'li_thermal_summary.json',summary)
    dump(OUT/'li_thermal_tests.json',tests)
    elapsed=time.perf_counter()-start;signal.alarm(0)
    evidence=json.loads((ROOT/'evidence/LI_THERMAL_EXECUTION.json').read_text())
    evidence.update({'status':'PARTIAL_READY_BDF_REFERENCE_HOLD','ready_continuation_internal_wall_seconds':elapsed,'ready_continuation_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'tests':tests,'scoped_groups':groups,'ready_timings':timings,'ready_solver_diagnostics':solverdiag,'rate_table_quadrature_repeated':False,'production_repeated':False,'new_independent_DB_spots':18,'BDF_calls_in_ready_continuation':0,'full_suite_passed':False,'remaining_frozen_work':'Completed available dependency-safe outputs; required independent BDF validation HOLD','ready_continuation_command':'OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 timeout 25s python code/li_thermal_finish_ready.py > results/laneA/finish_ready.log 2>&1','observed_runtime_model':'UNKNOWN'})
    dump(ROOT/'evidence/LI_THERMAL_EXECUTION.json',evidence)
    print(json.dumps({'status':evidence['status'],'internal_wall_seconds':elapsed,'metrics':metrics,'comparisons':comparisons,'timings':timings,'scoped_groups':groups,'RR_sensitivity':sensitivity}))
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except BaseException as error:
        if not isinstance(error,SystemExit):
            dump(OUT/'ready_continuation_failure.json',{'error_type':type(error).__name__,'error':str(error),'status':'PARTIAL_READY_BDF_REFERENCE_HOLD','no_retry':True})
        raise
