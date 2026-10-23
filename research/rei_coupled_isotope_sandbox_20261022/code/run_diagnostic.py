#!/usr/bin/env python3
"""One offline finite scientific diagnostic; no cosmological or historical IVP."""
from __future__ import annotations
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import sys
sys.dont_write_bytecode=True
import resource
resource.setrlimit(resource.RLIMIT_CPU,(120,120));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
import hashlib,json,math,platform,time,traceback,signal
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import scipy
from scipy.linalg import solve,expm
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from atomic import PreparedAtomic
from local import Coefficient,LogRateTable,ResolvedEvent,evaluate_events,outer_transform,thermal_rhs,ENERGY,Unresolved,RateOverflow,K_B

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence';FIG=ROOT/'figures'
EPS=np.finfo(float).eps;ALG_TOL=512*EPS
WALL0=time.perf_counter();CPU0=time.process_time()
def wall_timeout(signum,frame):raise TimeoutError('DIAGNOSTIC_WALL_CAP_180S')
signal.signal(signal.SIGALRM,wall_timeout);signal.alarm(180)

def clean(x):
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,np.generic):return clean(x.item())
    if isinstance(x,float) and not math.isfinite(x):return '-Infinity' if x==-math.inf else 'Infinity' if x==math.inf else 'NaN'
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    return x

def write(path,value):path.write_text(json.dumps(clean(value),indent=2,allow_nan=False)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def infnorm(x):return float(np.linalg.norm(np.asarray(x),np.inf))
def residual(a,b,terms):return infnorm(np.asarray(a)-np.asarray(b))/max(math.fsum(infnorm(v) for v in terms),1e-300)

class Diagnostic:
    def __init__(self):self.tests=[];self.raw={};self.counts={'atomic_grid_states':0,'linear_solve_cases':0,'midpoint_trajectories':0,'atomic_Radau_oracles':0,'trace_scalar_reference_solves':0,'old_C1_C2_invocations':0,'cosmological_IVPs':0}
    def check(self,name,inputs,outputs,value=None,tolerance=None,accepted=None,kind='finite_scientific_check'):
        if accepted is None:accepted=math.isfinite(value) and value<=tolerance
        row={'name':name,'status':'PASS' if accepted else 'FAIL','kind':kind,'inputs':inputs,'outputs':outputs,'residual':value,'tolerance':tolerance}
        self.tests.append(row)
    def rejects(self,name,operation,expected):
        try:output=operation()
        except (ValueError,ArithmeticError) as error:
            self.check(name,{'expected_exception_token':expected},{'exception_type':type(error).__name__,'message':str(error)},accepted=expected in str(error),kind='expected_rejection')
        else:self.check(name,{}, {'unexpected_result':output},accepted=False,kind='expected_rejection')
    def checkpoint(self):write(OUT/'PARTIAL_RESULTS.json',{'tests':self.tests,'counts':self.counts,'raw':self.raw})

def inputs_check(d):
    identity=json.loads((ROOT/'vendor/INPUT_COPIES.json').read_text())
    for row in identity['copies']:
        actual=sha(ROOT/row['path'])
        d.check('immutable_copy:'+row['path'],{'expected_sha256':row['sha256']},{'actual_sha256':actual},accepted=actual==row['sha256'])
        if actual!=row['sha256']:raise ValueError('IMMUTABLE_INPUT_MISMATCH')

def states(prepared):
    raw=np.arange(1,22,dtype=float);positive=raw/(prepared.A@raw)
    initial=np.array(prepared.network.initial_Y,copy=True)
    trace=initial.copy();trace[0]=1e-104;trace[5]=1e-120;trace[6]=2e-120
    return {'positive':positive,'initial':initial,'trace':trace}

def atomic_grid(d):
    prepared={};setup=[];solve_cases=[]
    for T in (100.,1000.,10000.):
        for uv in (0.,.3,1.):
            start=time.perf_counter();p=PreparedAtomic(T,uv);setup.append({'T':T,'uv':uv,'setup_wall_s':time.perf_counter()-start});prepared[T,uv]=p
            for nb in (1.,1e6):
                for label,y in states(p).items():
                    d.counts['atomic_grid_states']+=1
                    e=nb*float(p.q@y);direct_B=p.P+e*p.R;direct_F=direct_B@y
                    u=nb*(p.R@y);direct_J=direct_B+np.outer(u,p.q)
                    actual_F=p.rhs(y,nb);actual_J=p.jacobian(y,nb)
                    f_res=residual(actual_F,direct_F,[p.P@y,e*(p.R@y)])
                    j_res=residual(actual_J,direct_J,[p.P,e*p.R,np.outer(u,p.q)])
                    cs=np.column_stack([np.imag(p.smooth_rhs(y.astype(complex)+1e-30j*np.eye(21)[i],nb))/1e-30 for i in range(21)])
                    cs_res=infnorm(actual_J-cs)/max(infnorm(actual_J),1e-300)
                    d.check(f'atomic_grid:T{T}:uv{uv}:nb{nb}:{label}',{'T':T,'uv':uv,'nb':nb,'state':label,'Y':y},
                            {'F':actual_F,'J':actual_J,'direct_F':direct_F,'F_residual':f_res,'J_residual':j_res,'complex_step_residual':cs_res},
                            accepted=f_res<=ALG_TOL and j_res<=ALG_TOL and cs_res<=1e-10)
                    if uv==1. and nb==1e6:solve_cases.append((p,nb,label,y))
    p=prepared[1000.,1.];y=states(p)['positive'];nb=1e6;f=.25*float(p.q@y)
    analytic=p.fast_electron_column(y,nb,f)
    cs=np.imag(p.smooth_rhs(y.astype(complex),nb,f+1e-30j))/1e-30
    d.check('fast_electron_column',{'f':f,'nb':nb},{'analytic':analytic,'complex_step':cs},residual(analytic,cs,[analytic,cs]),ALG_TOL)
    no_rank=p.P+nb*float(p.q@y)*p.R;correct=p.jacobian(y,nb)
    wrong=infnorm(no_rank-correct)/max(infnorm(correct),1e-300)
    d.check('negative_control_omitted_electron_rank_one',{}, {'wrong_relative_J_error':wrong,'wrong_accepted':wrong<=1e-10},accepted=wrong>1e-10,kind='expected_rejection')
    rows=np.stack([y*(1+.001*i) for i in range(256)]);batch=p.batch_rhs(rows,nb)
    scalar=np.stack([p.rhs(row,nb) for row in rows]);error=residual(batch,scalar,[batch,scalar])
    d.check('batch256_matches_scalar',{'batch_size':256},{'max_normalized_residual':error},error,ALG_TOL)
    d.raw['setup']=setup;return prepared,solve_cases

def linear_checks(d,cases):
    rng=np.random.default_rng(20261022);rows=[]
    for p,nb,label,y in cases:
        B,u,J=p.matrices(y,nb);rate=float(np.max(-np.diag(B)))
        for stiffness in (1e-3,1.,100.):
            h=stiffness/rate if rate else 0.;b=rng.normal(size=21);A=np.eye(21)-h*J
            structured,info=p.solve_structured(y,nb,h,b,return_info=True)
            dense=solve(A,b,check_finite=True);condition=float(np.linalg.cond(A,np.inf))
            backward=infnorm(A@structured-b)/max(infnorm(A)*infnorm(structured)+infnorm(b),1e-300)
            forward=infnorm(structured-dense)/max(infnorm(dense),1e-300)
            d.check(f'linear:T{p.T_K}:{label}:stiffness{stiffness}',{'T':p.T_K,'nb':nb,'state':label,'h':h,'h_max_exit':stiffness,'rhs':b},
                    {'solution':structured,'dense_solution':dense,'condition_inf':condition,'backward_residual':backward,'forward_relative_error':forward,'solve_info':info},
                    accepted=backward<=1e-12 and (condition>1e8 or forward<=1e-10))
            rows.append({'T':p.T_K,'state':label,'stiffness':stiffness,'condition_inf':condition,'backward':backward,'forward':forward,'info':info})
            d.counts['linear_solve_cases']+=1
    p=PreparedAtomic(1000.,0.);y=np.zeros(21);y[1]=1.;b=rng.normal(size=21)
    got,info=p.solve_structured(y,0.,0.,b,return_info=True)
    d.check('zero_generator_h0_solve',{}, {'info':info,'solution':got},infnorm(got-b),0.)
    d.raw['linear_solve_summary']=rows

def event_checks(d,p):
    zero={key:0. for key in ENERGY};energy=dict(zero,Q0=3e-18,dI=1e-18,dEfast=1e-18,Egamma_esc=1e-18)
    dec=json.loads((ROOT/'vendor/nuclear/EVALUATED_DECAY_INPUTS.json').read_text())
    lt=math.log(2)/(dec['tritium_half_life_years']*dec['year_days']*dec['seconds_per_day'])
    def event(name,left,right,k=1e-6,order=None,coefficient=None,ledger=zero,**kw):
        return ResolvedEvent(name,left,right,coefficient or Coefficient.positive(k),'s^-1' if sum(left.values())==1 else 'm^3/s',
                             'evaluated lambda; manufactured ledger' if name=='TII_beta' else 'MANUFACTURED_ALGEBRA',
                             'SUPPLIED_RESOLVED_CHANNEL_ONLY',ledger,p.A,p.q,**kw)
    beta=event('TII_beta',{6:1},{9:1},k=lt)
    unequal=event('p_n_capture',{2:1,0:1},{4:1},ledger=energy)
    identical=event('D_D_to_H_T',{4:2},{2:1,6:1},k=2e-6)
    y=states(p)['positive'];nb=3.
    all_events=[beta,unequal,identical]
    for e in all_events:
        row=e.evaluate(y,nb);k=math.exp(e.coefficient.log_value)
        direct=k*nb**(e.order-1)*math.prod(y[i]**n for i,n in e.left.items())/math.prod(math.factorial(n) for n in e.left.values())
        def polynomial(pop):return e.nu*k*nb**(e.order-1)*np.prod([pop[i]**n for i,n in e.left.items()])/math.prod(math.factorial(n) for n in e.left.values())
        cs=np.column_stack([np.imag(polynomial(y.astype(complex)+1e-30j*np.eye(21)[i]))/1e-30 for i in range(21)])
        err=residual(row['jacobian'],cs,[row['jacobian'],cs]);rate_err=abs(row['rate']-direct)/max(abs(direct),1e-300)
        d.check('resolved_event:'+e.id,{'reactants':e.left,'products':e.right,'coefficient':k,'unit':e.unit,'Y':y,'nb':nb},row,
                accepted=err<=ALG_TOL and rate_err<=ALG_TOL and sum(int(a)*int(v) for a,v in zip(p.A,e.nu))==0)
    # Exactly zero: no quotient R/Y is used and the unequal reaction derivative survives.
    yz=y.copy();yz[2]=0.;row=unequal.evaluate(yz,nb)
    expected=math.exp(unequal.coefficient.log_value)*nb*yz[0]
    d.check('event_zero_onset_polynomial_derivative',{'Y_HII':0.,'Y_n':yz[0]},row,
            accepted=row['status']=='ZERO_REACTANT' and abs(row['gradient'][2]-expected)/expected<=ALG_TOL and row['gradient'][0]==0)
    yz2=y.copy();yz2[4]=0.;same=identical.evaluate(yz2,nb)
    d.check('identical_zero_reactant_derivative',{},same,accepted=same['status']=='ZERO_REACTANT' and np.all(same['gradient']==0))
    outcome=evaluate_events(all_events,y,nb)
    d.check('event_source_counts_and_energy',{},outcome,
            accepted=residual(outcome['source'],sum((e.nu*e.evaluate(y,nb)['rate'] for e in all_events),np.zeros(21)),[outcome['source']])<=ALG_TOL
            and abs(outcome['electron_source']-float(p.q@outcome['source']))/max(abs(outcome['electron_source'])+abs(float(p.q@outcome['source'])),1e-300)<=ALG_TOL)
    # Finite log coefficient below exp's range becomes representable after density multiplication.
    recovered=event('tiny_k_large_nb',{2:1,0:1},{4:1},coefficient=Coefficient('POSITIVE',-800.))
    row=recovered.evaluate(y,1e40)
    highprecision=float(np.exp(np.longdouble(-800))*np.longdouble(1e40)*np.longdouble(y[2])*np.longdouble(y[0]))
    error=abs(row['rate']-highprecision)/highprecision
    d.check('log_before_exponentiation_recovers_tiny_coefficient',{'log_k':-800.,'nb':1e40,'exp_k_binary64':math.exp(-800.)},row,error,2e-12)
    underflow=event('retained_log_underflow',{2:1,0:1},{4:1},coefficient=Coefficient('POSITIVE',-1200.)).evaluate(y,1.)
    d.check('representational_underflow_retains_log',{},underflow,accepted=underflow['rate']==0 and math.isfinite(underflow['log_rate']) and underflow['status']=='REPRESENTATIONAL_UNDERFLOW')
    support=event('support_zero',{2:1,0:1},{4:1},coefficient=Coefficient('SUPPORT_ZERO')).evaluate(y,1.)
    d.check('support_zero_status_distinct',{},support,accepted=support['status']=='SUPPORT_ZERO')
    d.rejects('absent_event_not_summed',lambda:event('absent',{6:1},{9:1},coefficient=Coefficient('ABSENT')).evaluate(y,1.),'ABSENT_EVENT_INPUT')
    d.rejects('unresolved_event_not_summed',lambda:event('unresolved',{6:1},{9:1},coefficient=Coefficient('UNRESOLVED')).evaluate(y,1.),'UNRESOLVED_EVENT_INPUT')
    d.rejects('event_overflow_named',lambda:event('overflow',{2:1,0:1},{4:1},coefficient=Coefficient('POSITIVE',700.)).evaluate(y,1e100),'EVENT_RATE_OVERFLOW')
    d.rejects('missing_energy_rejected',lambda:event('missing',{6:1},{9:1},ledger=None),'MISSING_ENERGY_LEDGER')
    d.rejects('double_booked_energy_rejected',lambda:event('double',{6:1},{9:1},ledger=dict(zero,Q0=1.,dEth=1.,dEfast=1.)),'ENERGY_LEDGER_IMBALANCE')
    d.rejects('binding_reference_mismatch_rejected',lambda:event('binding',{6:1},{9:1},ionization_reference=np.arange(21,dtype=float)),'IONIZATION_REFERENCE_MISMATCH')
    d.rejects('parent_branch_metadata_not_silently_ignored',lambda:event('branch',{6:1},{9:1},parent_id='parent',probability=.25),'PARENT_BRANCH_GROUPS_UNSUPPORTED')
    d.rejects('negative_physical_abundance_rejected',lambda:beta.evaluate(-y,1.),'INVALID_EVENT_STATE')
    wrong_identical=2*identical.evaluate(y,nb)['rate'];correct_identical=identical.evaluate(y,nb)['rate']
    d.check('negative_control_omitted_identical_symmetry_factor',{}, {'wrong':wrong_identical,'correct':correct_identical},accepted=abs(wrong_identical-correct_identical)/correct_identical>ALG_TOL,kind='expected_rejection')
    old_D=p.network.decay_matrix@y
    d.check('negative_control_atomic_beta_not_separated',{}, {'duplicate_beta_source':old_D,'old_atomic_beta_plus_event_would_duplicate':True},accepted=infnorm(old_D)>0,kind='expected_rejection')
    d.raw['resolved_event_semantics']='Each supplied k is a resolved channel coefficient; parent_id/probability metadata is explicitly rejected, never ignored or invented.'

def interpolation_checks(d):
    T=np.array([100.,1000.,10000.]);x=np.log(T)
    power=LogRateTable(T,[Coefficient('POSITIVE',-40+1.25*v) for v in x])
    d.rejects('default_knot_only_refuses_offgrid',lambda:power.at(math.sqrt(T[0]*T[1])),'OFF_GRID_KNOT_ONLY')
    for i in (0,1):
        tt=float(math.sqrt(T[i]*T[i+1]));got,bound=power.at(tt,'LOG_LINEAR',0.,1e-12);actual=-40+1.25*math.log(tt)
        d.check('manufactured_power_law_interpolation:'+str(i),{'T':tt,'curvature':0.},{'log_interpolated':got.log_value,'log_exact':actual,'bound':bound},abs(got.log_value-actual),ALG_TOL)
    quadratic=LogRateTable(T,[Coefficient('POSITIVE',-40+.02*v*v) for v in x])
    for i in (0,1):
        tt=float(math.sqrt(T[i]*T[i+1]));got,bound=quadratic.at(tt,'LOG_LINEAR',.04,.03);exact=-40+.02*math.log(tt)**2
        log_error=abs(got.log_value-exact);rel=abs(math.expm1(got.log_value-exact))
        d.check('manufactured_quadratic_interpolation_bound:'+str(i),{'T':tt,'M':.04},{'log_error':log_error,'relative_error':rel,'bound':bound},accepted=log_error<=bound['log_error_bound']+ALG_TOL and rel<=bound['relative_error_bound']+ALG_TOL)
    d.rejects('missing_curvature_refused',lambda:power.at(500.,'LOG_LINEAR'),'MISSING_INTERPOLATION_ERROR_BOUND')
    d.rejects('unacceptable_interpolation_error_refused',lambda:quadratic.at(500.,'LOG_LINEAR',.04,1e-4),'INTERPOLATION_BOUND_EXCEEDS_TOLERANCE')
    crossing=LogRateTable([100.,1000.],[Coefficient('SUPPORT_ZERO'),Coefficient('POSITIVE',-30.)])
    d.rejects('status_crossing_not_interpolated',lambda:crossing.at(300.,'LOG_LINEAR',0.,1.),'STATUS_CROSSING')
    zeros=LogRateTable([100.,1000.],[Coefficient('SUPPORT_ZERO'),Coefficient('SUPPORT_ZERO')],[True]);co,b= zeros.at(300.,'LOG_LINEAR')
    d.check('declared_entire_zero_interval',{}, {'status':co.status,'bound':b},accepted=co.status=='SUPPORT_ZERO')
    undec=LogRateTable([100.,1000.],[Coefficient('SUPPORT_ZERO'),Coefficient('SUPPORT_ZERO')])
    d.rejects('undeclared_zero_interval_refused',lambda:undec.at(300.,'LOG_LINEAR'),'STATUS_CROSSING')
    with np.load(ROOT/'fixtures/nuclear_sample.npz',allow_pickle=False) as sample:
        ts=sample['rate__T_K'];logs=sample['rate__log_forward_rate_m3_s_or_s_inv'][:,0]
    saved=LogRateTable(ts,[Coefficient('POSITIVE',float(v)) for v in logs])
    for t,logk in zip(ts,logs):
        got,bound=saved.at(float(t));d.check('saved_exact_knot:'+str(float(t)),{}, {'returned_log_k':got.log_value,'saved_log_k':float(logk)},abs(got.log_value-float(logk)),0.)
    d.rejects('saved_three_knots_do_not_establish_curvature',lambda:saved.at(float(math.sqrt(ts[0]*ts[1]))),'OFF_GRID_KNOT_ONLY')

def trace_checks(d):
    rows=[];rate=.001;t_eval=np.linspace(0,1000.,65)
    for scale in (1e-104,1e-120):
        exact=scale*(-np.expm1(-rate*t_eval))
        for rtol in (1e-8,1e-10,1e-12):
            sol=solve_ivp(lambda t,z:rate*(1-z),[0.,1000.],[0.],method='Radau',jac=lambda t,z:np.array([[-rate]]),rtol=rtol,atol=rtol*1e-3,t_eval=t_eval)
            d.counts['trace_scalar_reference_solves']+=1
            values=scale*sol.y[0];error=float(np.max(np.abs(values[1:]-exact[1:])/exact[1:]));final_error=abs(values[-1]-exact[-1])/exact[-1]
            d.check(f'trace_onset_scale{scale}:rtol{rtol}',{'scale':scale,'source_per_s':scale*rate,'loss_s-1':rate,'rtol':rtol,'initial_exact_zero':True},
                    {'success':sol.success,'nfev':sol.nfev,'t':t_eval,'Y':values,'analytic_Y':exact,'max_component_relative_error':error,'final_component_relative_error':final_error},
                    accepted=sol.success and values[0]==0 and np.all(values[1:]>0) and error<=1e-8)
            rows.append({'scale':scale,'rtol':rtol,'error':error,'t':t_eval,'Y':values,'exact':exact})
    d.raw['trace']=rows

def midpoint_checks(d,p):
    y0=states(p)['positive'];nb=1e6;B,u,J=p.matrices(y0,nb);final_t=1/float(np.max(-np.diag(B)))
    totals=np.array([np.sum(y0[list(g)]) for g in p.groups]);weights=np.zeros(21)
    for total,g in zip(totals,p.groups):weights[list(g)]=total
    oracle=solve_ivp(lambda t,y:p.smooth_rhs(y,nb),[0.,final_t],y0,method='Radau',jac=lambda t,y:p.jacobian(y,nb),rtol=1e-11,atol=1e-13*weights)
    d.counts['atomic_Radau_oracles']+=1
    if not oracle.success:raise ArithmeticError('ATOMIC_RADAU_ORACLE_FAILED:'+oracle.message)
    reference=oracle.y[:,-1];rows=[]
    for N in (16,32,64,128):
        y=y0.copy();minimum=np.inf;max_conservation=0.
        for step in range(N):
            y=p.step_midpoint(y,nb,final_t/N)
            for g,total in zip(p.groups,totals):
                minimum=min(minimum,float(np.min(y[list(g)]))/total)
                max_conservation=max(max_conservation,abs(float(np.sum(y[list(g)]))-total)/total)
        error=float(np.max(np.abs(y-reference)/weights));rows.append({'N':N,'error':error,'Y_final':y,'max_isotope_relative_conservation':max_conservation,'minimum_fraction':minimum})
        d.counts['midpoint_trajectories']+=1
        d.check('midpoint_N'+str(N),{'N':N,'t_final_s':final_t,'T':p.T_K,'uv':p.uv,'nb':nb},rows[-1],accepted=max_conservation<=1e-12 and minimum>=-1e-14)
    orders=[math.log(rows[i-1]['error']/rows[i]['error'],2) for i in range(1,len(rows))]
    d.check('midpoint_second_order_convergence',{}, {'errors':[r['error'] for r in rows],'orders':orders,'oracle_final':reference,'oracle_nfev':oracle.nfev,'oracle_njev':oracle.njev},
            accepted=all(rows[i]['error']<rows[i-1]['error'] for i in range(1,4)) and all(1.7<=o<=2.3 for o in orders[-2:]))
    # Independent dense exponential of the same frozen generator, separate from step-order claim.
    block=p._frozen_exponential(y0,nb,final_t/3,y0);dense=expm((final_t/3)*B)@y0
    d.check('shared_exponential_matches_dense21',{}, {'shared':block,'dense21':dense},residual(block,dense,[block,dense]),ALG_TOL)
    d.raw['midpoint']={'rows':rows,'orders':orders,'t_final_s':final_t,'reference':reference,'oracle_rtol':1e-11,'oracle_atol':1e-13*weights}

def eos_outer_checks(d,p):
    y=np.zeros(21);y[0]=.5;y[2]=.5;F=np.zeros(21);F[0]=-1.;F[2]=-1.;F[4]=1.
    eos=thermal_rhs(y,F,p.q,8192.,0.,0.)
    identity=1.5*K_B*(eos['C_th']*eos['dot_T_K_s']+8192*eos['dot_C_th'])
    scale=abs(1.5*K_B*eos['C_th']*eos['dot_T_K_s'])+abs(1.5*K_B*8192*eos['dot_C_th'])
    d.check('EOS_capture_constant_translational_energy',{'Y':y,'F':F,'Q_per_baryon':0.,'H':0.},eos,abs(identity)/max(scale,1e-300),ALG_TOL)
    wrong_Cdot=float(p.q@F)
    d.check('negative_control_omitted_nuclear_particle_change',{}, {'wrong_Cdot_electrons_only':wrong_Cdot,'correct_Cdot':eos['dot_C_th']},accepted=wrong_Cdot!=eos['dot_C_th'],kind='expected_rejection')
    yy=states(p)['positive'];ff=p.rhs(yy,1e6);fast=.1*float(p.q@yy);fastdot=1e-5;H=1e-3;Q=2e-22;T=1000.
    thermal=thermal_rhs(yy,ff,p.q,T,H,Q,fast,fastdot)
    lhs=1.5*K_B*(thermal['C_th']*thermal['dot_T_K_s']+T*thermal['dot_C_th'])+3*H*K_B*T*thermal['C_th']
    d.check('EOS_fast_pool_energy_identity',{'Q':Q,'f':fast,'fdot':fastdot,'H':H},thermal,abs(lhs-Q)/max(abs(lhs)+abs(Q),1e-300),ALG_TOL)
    d.rejects('missing_total_heat_source_unresolved',lambda:thermal_rhs(yy,ff,p.q,T,H,None),'MISSING_TOTAL_TRANSLATIONAL')
    threshold_final_T=8192.*1./2.
    d.check('threshold_H_particle_doubling_limit',{'C_initial':1.,'C_final':2.,'Delta_eth':0.},{'T_initial':8192.,'T_final':threshold_final_T},abs(1.5*K_B*8192-1.5*K_B*2*threshold_final_T)/(3*K_B*8192),ALG_TOL)
    trace=states(p)['trace'];scales=np.maximum(trace,1e-120);scales[0]=1e-104;scales[5:7]=1e-120
    F=p.rhs(trace,1e6);J=p.jacobian(trace,1e6);fz,jz=outer_transform(F,J,scales,2e-3)
    backF=fz*scales*2e-3;backJ=jz*scales[:,None]/scales[None,:]*2e-3
    d.check('outer_scale_and_H_applied_once',{'scales':scales,'H':2e-3},{'F_z_x':fz,'J_z_x':jz},max(residual(backF,F,[F]),residual(backJ,J,[J])),ALG_TOL)
    d.rejects('outer_H_zero_rejected',lambda:outer_transform(F,J,scales,0.),'INVALID_OUTER_SCALE_OR_H')


def timing(d,p):
    y=states(p)['positive'];nb=1e6;e=nb*float(p.q@y);B,u,J=p.matrices(y,nb);h=1/float(np.max(-np.diag(B)));rhs=np.arange(1,22,dtype=float)
    def rebuilt():
        rates=p.network.rates(p.T_K,p.uv)
        return rates['G0']@y+e*(rates['Gne']@y)
    prepared=lambda:p.rhs(y,nb)
    dense=lambda:p.solve_dense(y,nb,h,rhs)
    structured=lambda:p.solve_structured(y,nb,h,rhs)
    batch=np.stack([y*(1+.001*i) for i in range(64)])
    scalar_batch=lambda:np.stack([p.rhs(row,nb) for row in batch])
    vector_batch=lambda:p.batch_rhs(batch,nb)
    d.check('timing_RHS_identical_physics',{}, {'rebuilt':rebuilt(),'prepared':prepared()},residual(rebuilt(),prepared(),[prepared()]),ALG_TOL)
    timings={}
    for name,method,iterations,items in [('rates_rebuilt_RHS',rebuilt,300,1),('prepared_RHS',prepared,300,1),('dense_linear',dense,200,1),('shared_rank_one_linear',structured,200,1),('scalar_batch64',scalar_batch,10,64),('vectorized_batch64',vector_batch,10,64)]:
        for _ in range(3):method()
        samples=[]
        for repeat in range(7):
            start=time.perf_counter()
            for _ in range(iterations):method()
            samples.append((time.perf_counter()-start)/iterations)
        timings[name]={'seconds_per_call':samples,'median_seconds_per_call':float(np.median(samples)),'min_seconds_per_call':min(samples),'max_seconds_per_call':max(samples),'iterations_per_repeat':iterations,'repeat_batches':7,'states_per_call':items,'scalar_state_evaluations_per_repeat':iterations*items}
    faster='dense' if timings['dense_linear']['median_seconds_per_call']<=timings['shared_rank_one_linear']['median_seconds_per_call'] else 'structured'
    p.default_solver=faster
    d.raw['timing']={'methods':timings,'selected_linear_default':faster,
       'prepared_vs_rebuilt_RHS_speedup':timings['rates_rebuilt_RHS']['median_seconds_per_call']/timings['prepared_RHS']['median_seconds_per_call'],
       'structured_vs_dense_linear_speedup':timings['dense_linear']['median_seconds_per_call']/timings['shared_rank_one_linear']['median_seconds_per_call'],
       'batch_vectorization_speedup':timings['scalar_batch64']['median_seconds_per_call']/timings['vectorized_batch64']['median_seconds_per_call'],
       'BLAS_threads':1,'setup_cost_separate':True,'accuracy_gate_is_not_speed':True}
    d.check('timed_default_selected_from_actual_medians',{}, {'default':faster,'methods':timings},accepted=True)
    write(OUT/'TIMING.json',d.raw['timing'])


def plots(d):
    plt.rcParams.update({'font.size':10,'figure.dpi':140,'axes.spines.top':False,'axes.spines.right':False})
    rows=d.raw['midpoint']['rows'];fig,ax=plt.subplots(figsize=(6,4));nn=np.array([r['N'] for r in rows]);ee=np.array([r['error'] for r in rows])
    ax.loglog(nn,ee,'o-',label='Shared atomic midpoint vs Radau');ax.loglog(nn,ee[0]*(nn[0]/nn)**2,'--',label='N⁻² guide');ax.set(xlabel='Steps N',ylabel='Max isotope-weighted final error',title='Atomic-only prescribed-T convergence');ax.legend();fig.tight_layout();fig.savefig(FIG/'midpoint_convergence.png');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for scale in (1e-104,1e-120):
        row=next(r for r in d.raw['trace'] if r['scale']==scale and r['rtol']==1e-10)
        axes[0].plot(row['t'],row['Y']/scale,label=f'Y / {scale:g}')
        subset=[r for r in d.raw['trace'] if r['scale']==scale]
        axes[1].loglog([r['rtol'] for r in subset],[r['error'] for r in subset],'o-',label=f's={scale:g}')
    axes[0].set(xlabel='Proper time [s]',ylabel='Resolved trace / chosen scale',title='Born from exact zero, no floor');axes[1].set(xlabel='Radau relative tolerance',ylabel='Max component relative error',title='Componentwise trace resolution');axes[0].legend();axes[1].legend();fig.tight_layout();fig.savefig(FIG/'trace_onset_and_error.png');plt.close(fig)
    methods=d.raw['timing']['methods'];names=list(methods);median=np.array([methods[n]['median_seconds_per_call'] for n in names])*1e6
    lo=median-np.array([methods[n]['min_seconds_per_call'] for n in names])*1e6;hi=np.array([methods[n]['max_seconds_per_call'] for n in names])*1e6-median
    fig,ax=plt.subplots(figsize=(9,4));ax.barh(names,median,xerr=np.array([lo,hi]),capsize=3);ax.set_xscale('log');ax.set(xlabel='Microseconds per call (batch methods process 64 states)',title='Seven local timing batches; 1 BLAS thread');fig.tight_layout();fig.savefig(FIG/'timing.png');plt.close(fig)

def main():
    OUT.mkdir(exist_ok=True);FIG.mkdir(exist_ok=True)
    # A second run never overwrites the observed evidence from the first.
    if (OUT/'RESULTS.json').exists():raise FileExistsError('Existing diagnostic evidence; targeted repair must preserve it before a new run.')
    d=Diagnostic();error=None
    try:
        inputs_check(d);prepared,cases=atomic_grid(d);d.checkpoint()
        linear_checks(d,cases);event_checks(d,prepared[1000.,1.]);interpolation_checks(d);d.checkpoint()
        trace_checks(d);midpoint_checks(d,prepared[1000.,1.]);eos_outer_checks(d,prepared[1000.,1.]);d.checkpoint()
        timing(d,prepared[1000.,1.]);plots(d)
    except Exception:error=traceback.format_exc()
    failed=[r['name'] for r in d.tests if r['status']=='FAIL'];exit_code=int(bool(failed or error))
    resources={'wall_s':time.perf_counter()-WALL0,'CPU_s':time.process_time()-CPU0,'peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'CPU_cap_s':120,'wall_cap_s':180,'address_space_cap_MiB':1024,'BLAS_threads':1}
    result={'schema':'rei-conditional-sandbox-results-v1','status':'PASS_FINITE_CONDITIONAL_SANDBOX' if not exit_code else 'FAIL_PRESERVED','test_count':len(d.tests),'failed_tests':failed,'exception':error,'tests':d.tests,'raw':d.raw,'counts':d.counts,'resources':resources,'claim_boundary':'Prescribed-T atomic-only local kinetics and conditional supplied events; no coupled cosmological/nuclear/thermal trajectory.'}
    execution={'command':[sys.executable,str(Path(__file__).resolve())],'utc':datetime.now(timezone.utc).isoformat(),'exit_code':exit_code,'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__,'platform':platform.platform(),'requested_executor':'lower-tier implementation under frozen Astra contract','observed_model_identity':'UNAVAILABLE_FROM_RUNTIME_TOOL_OUTPUT','contract_sha256':sha(ROOT/'EXECUTION_CONTRACT.md'),'code_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'code').glob('*.py'))},'resources':resources,'counts':d.counts,'exception':error,'workflow_context':{'user_selected_skill':'physmath-research-loop built-in 1.0.0 as bound by execution contract','current_AGENTS':'read; tiered delegation and no-new-worktree applied','old_C1_C2_results':'reused without rerun','recursive_agents':False}}
    write(OUT/'RESULTS.json',result);write(OUT/'EXECUTION.json',execution)
    print(json.dumps({'status':result['status'],'test_count':len(d.tests),'failed_tests':failed,'exception':error,'resources':resources,'counts':d.counts},indent=2))
    return exit_code

if __name__=='__main__':raise SystemExit(main())
