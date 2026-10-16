"""Frozen Unit7 lane B; evidence-only trace kinetics; no product runner imports."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'): os.environ[key]='1'
import hashlib,json,math,re,signal,sys,time
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import solve_ivp,cumulative_trapezoid
ROOT=Path(__file__).resolve().parents[2]
CONTRACT=json.loads((ROOT/'spec/BE_KINETICS_CONTRACT.json').read_text())
DONOR=ROOT/'inputs/laneB/R5_DONOR_BBN.json'
if not DONOR.exists(): DONOR=Path(CONTRACT['immutable_input']['path'])
sha=hashlib.sha256(DONOR.read_bytes()).hexdigest()
assert sha==CONTRACT['immutable_input']['sha256']
donor=json.loads(DONOR.read_text()); abund=donor['result']['Y_final']; cmap=CONTRACT['cosmology']['element_charge_map']
Ye=sum(cmap[re.match(r'[A-Za-z]+',name).group()]*value for name,value in abund.items())
B=abund['Be7']; directLi=abund['Li7']; nb0=CONTRACT['cosmology']['nb0_cm-3']
c=CONTRACT['constants']; co=CONTRACT['cosmology']; hbar=c['h_planck_J_s']/(2*np.pi)
H0=100*co['h']*1000/c['Mpc_m']; Om=(co['Omega_b_h2']+co['Omega_c_h2'])/co['h']**2
Og=8*np.pi*c['G_m3_kg_s2']/(3*H0**2)*np.pi**2*(c['kB_J_K']*co['T0_K'])**4/(15*hbar**3*c['c_m_s']**5)
Or=Og*(1+7/8*(4/11)**(4/3)*co['Neff']); OL=1-Om-Or
lam=np.log(2)/(106.4*86400)
def rates(z):
    x=1+np.asarray(z); T=co['T0_K']*x; t=T/(10000*16)
    alpha=1e-13*4*5.596*t**(-.6038)/(1+.3436*t**.4479)
    saha=(2*np.pi*c['me_kg']*c['kB_J_K']*T/c['h_planck_J_s']**2)**1.5*np.exp(-217.7*c['eV_J']/(c['kB_J_K']*T))/1e6
    r=nb0*Ye*x**3*alpha; beta=alpha*saha
    H=H0*np.sqrt(Or*x**4+Om*x**3+OL)
    L=r+beta+lam; D=np.sqrt((r-beta-lam)**2+4*r*beta)
    ks=2*r*lam/(L+D); kf=(L+D)/2
    return r,beta,H,D,ks,kf,saha

def midpoint(N,start=100000):
    u=np.linspace(0,np.log((1+start)/10001),N+1); z=(1+start)*np.exp(-u)-1
    zm=(1+start)*np.exp(-(u[1:]+u[:-1])/2)-1
    r,be,H,D,ks,kf,_=rates(zm); dt=np.diff(u)/H
    es=np.exp(-ks*dt); ef=np.exp(-kf*dt); J=es*(-np.expm1(-D*dt))
    E00=((be+lam-ks)*es+(r-ks)*ef)/D; E01=be*J/D
    E10=r*J/D; E11=((r-ks)*es+(be+lam-ks)*ef)/D
    Is=-np.expm1(-ks*dt)/ks; If=-np.expm1(-kf*dt)/kf
    R0=lam*r*(Is-If)/D; R1=lam*((r-ks)*Is+(be+lam-ks)*If)/D
    y=np.zeros((3,N+1)); y[0,0]=1
    for i in range(N):
        a,b,F=y[:,i]
        y[:,i+1]=(E00[i]*a+E01[i]*b,E10[i]*a+E11[i]*b,F+R0[i]*a+R1[i]*b)
    return u,z,y

def reference(start):
    stop=np.log((1+start)/10001)
    def jac(u,y):
        r,b,H,*_=rates((1+start)*np.exp(-u)-1)
        return np.array([[-r,b,0],[r,-b-lam,0],[0,lam,0]])/H
    def fun(u,y): return jac(u,y)@y
    tic=time.perf_counter(); sol=solve_ivp(fun,(0,stop),[1.,0.,0.],method='Radau',jac=jac,rtol=1e-9,atol=1e-12,dense_output=True)
    return sol,time.perf_counter()-tic

def quant(z,F):
    return {f'z{int(100*q)}':float(np.interp(q,F,z)) if F[-1]>=q else None for q in (.1,.5,.9)}

def run():
    start=time.perf_counter(); timings={}; raw=ROOT/'code/laneB/raw'
    def timeout(*_): raise TimeoutError('30-second cumulative numerical budget exhausted')
    signal.signal(signal.SIGALRM,timeout); signal.alarm(30)
    tic=time.perf_counter(); u,z,y=midpoint(32768); timings['production']=time.perf_counter()-tic
    np.savez(raw/'production.npz',u=u,z=z,y=y)
    tic=time.perf_counter(); uc,zc,yc=midpoint(16384); timings['refinement']=time.perf_counter()-tic
    np.savez(raw/'refinement.npz',u=uc,z=zc,y=yc)
    sol,timings['Radau100000']=reference(100000)
    yr=sol.sol(u); np.savez(raw/'reference100000.npz',u=u,z=z,y=yr,internal_u=sol.t,internal_y=sol.y)
    alt,timings['Radau200000']=reference(200000)
    ya=alt.sol(np.log(200001/(1+z))); np.savez(raw/'reference200000.npz',u_common=u,z=z,y=ya,internal_u=alt.t,internal_y=alt.y)
    a,b,F=y; r,be,H,D,ks,kf,saha=rates(z); L=r+be+lam
    Fq=-np.expm1(-cumulative_trapezoid(ks/H,u,initial=0)); F0=-np.expm1(-cumulative_trapezoid(r*lam/L/H,u,initial=0))
    np.savez(raw/'reductions.npz',Fq=Fq,F0=F0)
    dFdz=-lam*b/((1+z)*H); p=-dFdz/(F[-1]-F[0]); pdf=float(-np.trapezoid(p,z))
    q=quant(z,F); qr=quant(z,yr[2]); qc=quant(zc,yc[2]); qa=quant(z,ya[2])
    M=max(float(nb0*Ye*(1+zz)**3/rates(zz)[-1]) for zz in (100000,CONTRACT['immutable_input']['donor_z']))
    dtbound=(100001**-2-(1+CONTRACT['immutable_input']['donor_z'])**-2)/(2*H0*np.sqrt(Or)); tail=M*(1+lam*dtbound)
    referr={'F':float(np.max(abs(yr[2]-F))),'Be3':float(np.max(abs(yr[1]-b))),'quantiles':{k:abs(q[k]-qr[k]) for k in q}}
    coarseerr={'F':float(np.max(abs(yc[2]-F[::2]))),'Be3':float(np.max(abs(yc[1]-b[::2]))),'quantiles':{k:abs(q[k]-qc[k]) for k in q}}
    starterr={'F':float(np.max(abs(ya[2]-yr[2]))),'Be3':float(np.max(abs(ya[1]-yr[1]))),'quantiles':{k:abs(qr[k]-qa[k]) for k in q}}
    # Ledger identities computed from explicit abundance changes; tolerance is tied to B.
    dfree=-B*(b+F); bound=B*b; dnuc=-B*F; dionic=-B*(b+F); neutrino=B*F
    ledger={'ionic_minus_free':float(np.max(abs(dionic-dfree))),'total_electron_plus_neutrino':float(np.max(abs(dfree+bound+neutrino))),'nuclear_plus_neutrino':float(np.max(abs(dnuc+neutrino))),'nucleus_number':float(np.max(abs(B*(a+b+F)-B))),'mass7_baryons':float(np.max(abs(7*B*(a+b+F)-7*B)))}
    inv={'population_min':float(y.min()),'fraction_sum_max_abs':float(np.max(abs(y.sum(axis=0)-1))),'F_min_increment':float(np.min(np.diff(F))),'ledger':ledger}
    checks={'reference_success':bool(sol.success and alt.success),'positivity':y.min()>=-1e-12,'mass7_fraction_sum':inv['fraction_sum_max_abs']<=5e-11,'F_monotone':np.min(np.diff(F))>=-1e-12,'refinement':coarseerr['F']<=5e-6 and coarseerr['Be3']<=5e-6,'reference':referr['F']<=1e-5 and referr['Be3']<=1e-5,'quantiles':max([*referr['quantiles'].values(),*coarseerr['quantiles'].values()])<=2,'conditional_pdf':abs(pdf-1)<=.002,'qss':np.max(abs(Fq-F))<=.001,'alternate_start':starterr['F']<=1e-7,'early_tail_bound':tail<1e-7,'final_survivors':float(a[-1]+b[-1])<=1e-8,'trace_ledger':all(v<=max(1e-25,1e-12*(7*B if k=='mass7_baryons' else B)) for k,v in ledger.items())}
    ratios={}
    for k,zz in q.items():
        rr,bb,hh,dd,*_=rates(zz); ratios[k]={'z':zz,'beta/lambda':float(bb/lam),'r/H':float(rr/hh),'D/H':float(dd/hh)}
    timings['total_numerical']=time.perf_counter()-start; signal.alarm(0)
    result={'authority_requested':'Astra','executor_requested':'gpt-6.1-sol','executor_observed':'UNKNOWN','donor_sha256':sha,'donor_path_used':str(DONOR.relative_to(ROOT)),'donor_path_mapping':{'contract_original':CONTRACT['immutable_input']['path'],'portable_exact_copy':'inputs/laneB/R5_DONOR_BBN.json','sha256':sha},'nb0_cm-3':nb0,'YBe7':B,'YLi7_direct':directLi,'Ye':Ye,'donor_species_count':len(abund),'n_Be7_comoving0_cm-3':nb0*B,'Omega_gamma':Og,'Omega_r':Or,'Omega_m':Om,'Omega_Lambda':OL,'H0_s-1':H0,'lambda_s-1':lam,'F_start':float(F[0]),'F_end':float(F[-1]),'surviving_fraction_end':float(a[-1]+b[-1]),'endpoint_populations':y[:,-1].tolist(),'early_tail_bound':{'M':M,'time_bound_s':dtbound,'F_omitted_bound':lam*M*dtbound,'F_plus_b_bound':tail},**q,'qss_max_F_error':float(np.max(abs(Fq-F))),'simple_closure_max_F_error':float(np.max(abs(F0-F))),'reference_errors':referr,'refinement_errors':coarseerr,'start_test_errors':starterr,'pdf_normalization':pdf,'electron_bath_trace_fraction_bound':B/Ye,'invariant_residuals':inv,'wall_time_s':timings,'rate_ratios_at_quantiles':ratios,'checks':{k:bool(v) for k,v in checks.items()},'versions':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__},'reference_diagnostics':[{'start':100000,'success':sol.success,'message':sol.message,'nfev':sol.nfev,'njev':sol.njev,'nlu':sol.nlu},{'start':200000,'success':alt.success,'message':alt.message,'nfev':alt.nfev,'njev':alt.njev,'nlu':alt.nlu}],'scope':'Specified FLRW; fully ionized frozen donor electron bath; total RR fit; blackbody PI; statistical-hyperfine bound EC; no continuum EC, second-electron or late history; no physical heat/H/NCP output. Numerical errors are within-model, not atomic uncertainty.','status':'NUMERICAL_CHECKS_PASS_REVIEW_PENDING' if all(checks.values()) else 'NUMERICAL_FAILURE_AUTHORITY_REQUIRED'}
    np.savetxt(ROOT/'evidence/be_kinetics_history.csv',np.column_stack((z,u,a,b,F,F,dFdz,p)),delimiter=',',header='z,u,x_Be4,x_Be3,x_Li3,Fdecay,dF_dz,p_z',comments='',fmt='%.17g')
    (ROOT/'evidence/BE_KINETICS_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'checks':result['checks'],'timings':timings,'quantiles':q,'F_end':F[-1],'survivors':a[-1]+b[-1],'reference_errors':referr,'refinement_errors':coarseerr,'start_test':starterr,'tail':tail,'qss':result['qss_max_F_error']},indent=2))
    return result
if __name__=='__main__':
    try: run()
    except BaseException as exc:
        (ROOT/'code/laneB/raw/failure.json').write_text(json.dumps({'error_type':type(exc).__name__,'error':str(exc)},indent=2)+'\n'); raise
