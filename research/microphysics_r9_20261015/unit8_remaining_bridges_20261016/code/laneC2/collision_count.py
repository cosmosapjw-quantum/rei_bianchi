"""Frozen Unit8 C2 projected cold KN chain, indexed by collision count."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
import csv,hashlib,json,signal,sys,time
from pathlib import Path
import numpy as np
import scipy
from scipy.special import gammaincc,gammaincinv
ROOT=Path(__file__).resolve().parents[2];CON=json.loads((ROOT/'spec/GAMMA_COLLISION_COUNT_CONTRACT.json').read_text());BASE=json.loads((ROOT/CON['inherits']).read_text());C=BASE['constants'];ME=C['mec2_eV'];E0=BASE['inputs']['E_gamma_eV'];ST=8*np.pi*C['re_cm']**2/3
COUNTS=CON['counts']
def dump(path,obj):(ROOT/path).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def csvout(path,rows):
    with (ROOT/path).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def operator(N,nang):
    E=np.r_[0,np.geomspace(1000,E0,N)];mu,w=np.polynomial.legendre.leggauss(nang);x=E[1:,None]/ME;r=1/(1+x*(1-mu));out=E[1:,None]*r
    ds=w*np.pi*C['re_cm']**2*r**2*(r+1/r-(1-mu*mu));sigma=ds.sum(axis=1);prob=ds/sigma[:,None]
    hi=np.searchsorted(E,out,side='right');lo=hi-1;upper=(out-E[lo])/(E[hi]-E[lo]);P=np.zeros((N+1,N+1));P[0,0]=1
    parent=np.repeat(np.arange(1,N+1),nang)
    np.add.at(P,(lo.ravel(),parent),(prob*(1-upper)).ravel());np.add.at(P,(hi.ravel(),parent),(prob*upper).ravel())
    K=E-E@P;sg=np.r_[ST,sigma];angularK=np.r_[0,np.sum(prob*(E[1:,None]-out),axis=1)]
    residuals={'column_sum_max_abs':float(np.max(abs(P.sum(axis=0)-1))),'parent_energy_relative':float(np.max(abs(E@P+angularK-E)/np.maximum(E,1))),'min_probability':float(P.min()),'upper_triangle_growth_probability':float(np.tril(P,-1).sum()),'parent_K_min_eV':float(K.min())}
    return E,P,sg,K,residuals

def chain(E,P,sigma,K,N):
    p=np.zeros(len(E));p[-1]=1;cum=0.;L=0.;out={};dlog=np.log(E0/1000)/(N-1)
    for n in range(17):
        if n in COUNTS:
            mean=float(np.dot(E,p));var=float(np.dot(E*E,p)-mean*mean);cdf=np.cumsum(p)
            quant={str(q):float(np.interp(q,cdf,E)) for q in (.05,.5,.95)} if n else {str(q):float(E0) for q in (.05,.5,.95)}
            bound=E0/(1+2*n*E0/ME);pbound=bound*np.exp(-n*dlog);occupied=E[p>0]
            out[n]={'p':p.copy(),'mean_E_eV':mean,'standard_deviation_eV':float(np.sqrt(var)),'quantiles_eV':quant,'cumulative_K_eV':float(cum),'waiting_L_cm-2':float(L),'continuous_support_min_eV':float(bound),'projected_support_min_eV':float(pbound),'numerical_occupied_min_eV':float(occupied.min()),'continuous_support_leakage_probability':float(p[E<bound*(1-1e-12)].sum()),'projected_support_leakage_probability':float(p[E<pbound*(1-1e-12)].sum()),'sentinel_probability':float(p[0]),'count_residual_abs':float(abs(p.sum()-1)),'cumulative_energy_relative':float(abs((mean+cum)/E0-1))}
        if n<16:
            cum+=float(np.dot(K,p));L+=float(np.dot(1/sigma,p));p=P@p
    return out

def timing(z,chains,meta):
    z=np.atleast_1d(z);x=1+z;H=meta['H0_s-1']*np.sqrt(meta['Omega_r']*x**4+meta['Omega_m']*x**3+meta['Omega_Lambda']);ne=meta['nb0_cm-3']*meta['Ye']*x**3;rate=ne*C['c_cm_s'];sigma0=chains['sigma0'];Gamma=rate*sigma0;margin=np.log(x/10001)
    result={}
    for n,row in chains['rows'].items():
        t=row['waiting_L_cm-2']/rate
        vals={'mean_elapsed_s':t,'H_mean_elapsed':H*t,'mean_upper_elapsed_s':n/Gamma,'upper99_elapsed_s':gammaincinv(n,.99)/Gamma if n else np.zeros(len(z)),'upper999_elapsed_s':gammaincinv(n,.999)/Gamma if n else np.zeros(len(z))}
        for eps in (.01,.05):
            frozen=gammaincc(n,eps*Gamma/H) if n else np.zeros(len(z));expanding=gammaincc(n,eps*np.exp(-3*eps)*Gamma/H) if n else np.zeros(len(z))
            if n:expanding=np.where(margin<eps,1.,expanding)
            vals[f'frozen_tail_eps{eps}']=frozen;vals[f'expanding_tail_eps{eps}']=expanding;vals[f'endpoint_margin_indicator_eps{eps}']=(margin<eps).astype(float)
        result[n]=vals
    return result

def source_average(z,F,chainobj,meta,stride=1):
    zs=z[::stride];fs=F[::stride];weights=np.diff(fs);mid=np.sqrt((1+zs[:-1])*(1+zs[1:]))-1;values=timing(mid,chainobj,meta);delta=float(F[-1]-F[0])
    return {n:{key:float(np.dot(weights,arr)/delta) for key,arr in row.items()} for n,row in values.items()},float(weights.sum())

def compare(a,b):
    out={}
    for n in COUNTS:
        def rel(k):return abs(a[n][k]/b[n][k]-1) if b[n][k] else abs(a[n][k]-b[n][k])
        out[n]={'mean_relative':rel('mean_E_eV'),'L_relative':rel('waiting_L_cm-2'),'K_over_E0_absolute':abs(a[n]['cumulative_K_eV']-b[n]['cumulative_K_eV'])/E0,'quantile_max_relative':max(abs(a[n]['quantiles_eV'][q]/b[n]['quantiles_eV'][q]-1) for q in b[n]['quantiles_eV'])}
    return out

def run():
    start=time.perf_counter()
    def timeout(*_):raise TimeoutError('C2separate10s cumulative hard ceiling exhausted')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(10)
    inputs={}
    for name in ('history','kinetics','source'):
        p=ROOT/'inputs/laneC'/Path(BASE['inputs'][name]['path']).name;assert hashlib.sha256(p.read_bytes()).hexdigest()==BASE['inputs'][name]['sha256'];inputs[name]=p
    h=np.genfromtxt(inputs['history'],delimiter=',',names=True);meta=json.loads(inputs['kinetics'].read_text());first=json.loads((ROOT/'evidence/GAMMA_TRANSFER_RESULT.json').read_text());delta=float(h['Fdecay'][-1]-h['Fdecay'][0]);N0=meta['nb0_cm-3']*meta['YBe7'];amp=N0*.104*delta
    if np.any(np.diff(h['Fdecay'])<0):raise ValueError('Negative raw source cell count')
    operators={};chains={};raw={}
    for N,na in ((256,128),(512,128),(512,256)):
        label=f'N{N}_A{na}';E,P,sigma,K,err=operator(N,na);rows=chain(E,P,sigma,K,N);operators[label]={'E':E,'P':P,'sigma':sigma,'K':K,'residuals':err};chains[label]=rows
        j,i=np.nonzero(P);raw[label+'_parent']=i;raw[label+'_daughter']=j;raw[label+'_probability']=P[j,i];raw[label+'_E_eV']=E;raw[label+'_sigma0_cm2']=sigma;raw[label+'_K_parent_eV']=K
    fine=chains['N512_A128'];op=operators['N512_A128'];chobj={'rows':fine,'sigma0':float(op['sigma'][-1])}
    averages,rawsum=source_average(h['z'],h['Fdecay'],chobj,meta);coarse,coarsesum=source_average(h['z'],h['Fdecay'],chobj,meta,2)
    source_errors={};sourcepass=True
    for n in COUNTS:
        source_errors[n]={}
        for key,value in averages[n].items():
            diff=abs(value-coarse[n][key]);relative=diff/abs(value) if value else diff;isprob='tail' in key or 'indicator' in key;tiny=isprob and max(abs(value),abs(coarse[n][key]))<=1e-8
            passed=diff<=1e-8 if tiny else relative<=1e-4
            sourcepass=sourcepass and passed;source_errors[n][key]={'absolute':diff,'relative':relative,'comparison':'absolute1e-8 for probability<=1e-8' if tiny else 'relative1e-4'}
    quantile_values={k:timing([meta[k]],chobj,meta) for k in ('z10','z50','z90')};timingrows=[]
    for n in COUNTS:
        timingrows.append({'source':'rawF_weighted_mean','n_collisions':n,'z_source':None,**averages[n]})
        for name,vals in quantile_values.items():timingrows.append({'source':name,'n_collisions':n,'z_source':meta[name],**{k:float(a[0]) for k,a in vals[n].items()}})
    csvout('evidence/gamma_collision_count_timing.csv',timingrows)
    states=[]
    for n,row in fine.items():
        for E,p in zip(op['E'],row['p']):states.append({'n_collisions':n,'E_eV':float(E),'probability':float(p),'cumulative_K_per_gamma_eV':row['cumulative_K_eV'],'source_gamma_count_per_present_comoving_cm3':amp,'photon_count_per_present_comoving_cm3':float(p*amp)})
    csvout('evidence/gamma_collision_count_states.csv',states);np.savez(ROOT/'evidence/gamma_collision_count_kernel.npz',**raw)
    grid=compare(chains['N256_A128'],fine);angular=compare(chains['N512_A256'],fine)
    errs=[o['residuals'] for o in operators.values()];rows=[r for chainrows in chains.values() for r in chainrows.values()];fmeanerr=abs(fine[1]['mean_E_eV']/first['exact_477600eV']['mean_Eout_eV']-1)
    waitsok=all(row['waiting_L_cm-2']<=n/op['sigma'][-1]*(1+1e-12) for n,row in fine.items());timebounds=all(0<=v<=1 for vals in averages.values() for key,v in vals.items() if 'tail' in key or 'indicator' in key)
    checks={'P_positive_stochastic':all(e['min_probability']>=0 and e['column_sum_max_abs']<=2e-12 for e in errs),'parent_energy':max(e['parent_energy_relative'] for e in errs)<=2e-12,'no_positive_energy_growth':all(e['upper_triangle_growth_probability']==0 and e['parent_K_min_eV']>=0 for e in errs),'state_count_energy':all(r['count_residual_abs']<=1e-11 and r['cumulative_energy_relative']<=1e-11 for r in rows),'sentinel_empty':max(r['sentinel_probability'] for r in rows)<=1e-14,'projected_support':max(r['projected_support_leakage_probability'] for r in rows)<=1e-14,'first_mean_vs_C':fmeanerr<=1e-9,'grid_mean_L':max(max(v['mean_relative'],v['L_relative']) for v in grid.values())<=.003,'grid_cumulative_K':max(v['K_over_E0_absolute'] for v in grid.values())<=.001,'grid_quantiles':max(v['quantile_max_relative'] for v in grid.values())<=.03,'angular_mean_L':max(max(v['mean_relative'],v['L_relative']) for v in angular.values())<=.003,'angular_quantiles':max(v['quantile_max_relative'] for v in angular.values())<=.03,'source_refinement':sourcepass,'waiting_upper_bound':waitsok,'probability_bounds':timebounds,'raw_source_amplitude':abs(rawsum/delta-1)<=1e-12 and abs(coarsesum/delta-1)<=1e-12 and abs(amp/first['source_gamma_count_per_present_comoving_cm3']-1)<=1e-12}
    summaries={n:{key:value for key,value in row.items() if key!='p'} for n,row in fine.items()};yieldunits={n:{'per_gamma_eV':row['cumulative_K_eV'],'per_initial_Be7_donor_eV':row['cumulative_K_eV']*.104*delta,'per_cosmic_baryon_eV':row['cumulative_K_eV']*.104*delta*meta['YBe7'],'per_present_comoving_cm3_eV':row['cumulative_K_eV']*amp} for n,row in fine.items()}
    elapsed=time.perf_counter()-start;signal.alarm(0)
    result={'contract_id':CON['contract_id'],'authority_requested':'Astra','executor_requested':'gpt-6.1-sol','executor_observed':'UNKNOWN','source_DeltaF':delta,'source_gamma_count_per_present_comoving_cm3':amp,'fine_states':summaries,'cumulative_electron_K_units':yieldunits,'source_weighted_timing':averages,'source_quantile_timing':{key:{n:{k:float(v[0]) for k,v in vals.items()} for n,vals in rows.items()} for key,rows in quantile_values.items()},'source_refinement_errors':source_errors,'grid_comparison':grid,'angular_comparison':angular,'operator_residuals':{key:o['residuals'] for key,o in operators.items()},'first_mean_vs_C_relative':fmeanerr,'background_variation_bounds':{str(eps):{'density':float(-np.expm1(-3*eps)),'photon_redshift':float(-np.expm1(-eps)),'H':float(-np.expm1(-2*eps))} for eps in (.01,.05)},'quantile_method':'linear interpolation of inclusive discrete CDF on ascending energy nodes; initial delta kept exact','time_quantile_label':'99/99.9% fields are Erlang upper bounds, not exact chain quantiles; weighted fields average those upper bounds over actual rawF source','support_policy':'continuous exact support leakage reported as projection error; acceptance uses amended proven exp(-n*dlogE) projected bound with1e-12 relative energy roundoff','checks':{k:bool(v) for k,v in checks.items()},'wall_time_s':elapsed,'versions':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__},'scope':'Frozen-background collision-number projected cold stationary-electron chain; analytic expansion comparison probability bounds within z>=10000 bath. No time-dependent cosmological cascade, thermal electron operator, deposited heat, H or NCP. C1 was not rerun.','status':'NUMERICAL_CHECKS_PASS_REVIEW_PENDING' if all(checks.values()) else 'NUMERICAL_FAILURE_AUTHORITY_REQUIRED'}
    dump('evidence/GAMMA_COLLISION_COUNT_RESULT.json',result);print(json.dumps(result,indent=2));return result
if __name__=='__main__':
    try:run()
    except BaseException as exc:dump('evidence/GAMMA_COLLISION_COUNT_failure.json',{'error_type':type(exc).__name__,'error':str(exc)});raise
