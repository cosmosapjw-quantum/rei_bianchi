"""One create-only fixed-bath source-entry attempt, with bounded child runner."""
import argparse
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback
import numpy as np
from scipy.optimize import brentq
from positive_entry import source_integrals, incident, fit_positive, attenuate
from source_cells import table_cell_moments
from opacity_native import NativeOpacity, CHEMICAL_CHI_EV, C_CM_S, EV_ERG
from provider import HistoryProvider, EXPECTED

UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[2];BASE=UNIT.parent
RESULT={'unit':'SOURCE_ENTRY_POSITIVE_STEP_V1/FIXED_BATH01','checks':[],'actual_runs':[],
        'execution':{'native_processes':0,'SIGMA':0,'SIGMA_energies':0,'source_evaluations':0,
                     'actual_substeps':0,'manufactured_grey_substeps':0,'event_panels':0,
                     'CELL_RHS':0,'build':0,'gas_update':0,'history_ODE':0},
        'executor':'controller_direct_owner_authorized','observed_runtime_model':'NOT_INDEPENDENTLY_OBSERVED',
        'global_admission':'HOLD'}

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,value):
    def convert(x):
        if isinstance(x,np.ndarray):return x.tolist()
        if isinstance(x,np.generic):return x.item()
        raise TypeError(type(x).__name__)
    with Path(path).open('x') as f:json.dump(value,f,indent=2,allow_nan=False,default=convert)
def need(ok,label):
    if not ok:raise AssertionError(label)
def check(label,actual,expected,tol,scale=None):
    a,b=np.asarray(actual,float),np.asarray(expected,float)
    s=abs(b) if scale is None else np.broadcast_to(np.asarray(scale,float),a.shape)
    diff=abs(a-b);err=np.divide(diff,s,out=np.zeros_like(diff),where=s!=0)
    ok=bool(np.isfinite(a).all() and np.isfinite(b).all() and np.all(err<=tol) and np.all(diff[s==0]==0))
    RESULT['checks'].append({'label':label,'maximum':float(np.max(err)),'tolerance':tol,'pass':ok})
    need(ok,'HOLD_'+label)
def source_count():
    RESULT['execution']['source_evaluations']+=1
    need(RESULT['execution']['source_evaluations']<=2048,'SOURCE_CALL_CAP')

def manufactured():
    def source(t):
        source_count();return np.array([[t,math.expm1(t)]])
    rows=[]
    for h in [2.**-8,2.**-9,2.**-10]:
        val=source_integrals(source,lambda t:-t,0.,h,[0.,h],32)[0]
        with localcontext() as ctx:
            ctx.prec=80;d=Decimal.from_float(h);one=Decimal(1)
            refs=[d*d/2,d.exp()-one-d,d+(-d).exp()-one,d-2+(2+d)*(-d).exp()]
        check('manufactured_source_birth',val,np.array([float(x) for x in refs]),1e-10)
        n,u,w=incident(np.zeros(1),np.zeros(1),0.,-h,val[None,:])
        q,p,fit=fit_positive(n[0],u[0],math.exp(-h),1.,math.exp(h),128)
        check('fitted_constant',[sum(p)],n,1e-12)
        check('fitted_affine',np.dot(p,(q-1)/(math.exp(h)-1))/n[0],
              (u[0]/math.exp(-h)/n[0]-1)/(math.exp(h)-1),1e-7)
        rows.append({'h':h,'integrals':val,'mean_fraction':fit['target_cell_fraction'],'fit':fit})
    def zero_source(t):
        source_count();return np.zeros((2,2))
    zero=source_integrals(zero_source,lambda t:-t,0.,.1,[0.,.1],32)
    need(np.array_equal(zero,np.zeros((2,4))),'ZERO_SOURCE_INTEGRAL')
    zn,zu,zw=incident(np.zeros(2),np.zeros(2),0.,-.1,zero)
    need(np.all(zn==0) and np.all(zu==0) and np.all(zw==0),'ZERO_SOURCE_STATE')
    q,p,_=fit_positive(0.,0.,1.,1.,2.,128)
    survive,absorb=attenuate(p,np.zeros((0,3)),1.)
    need(survive.size==absorb.size==0,'ZERO_SOURCE_ABSORPTION')
    for tau in [0.,1e-6,1.,1e6,1e12]:
        p=np.array([.2,.3,.5]);q=np.array([1.,2.,3.]);k=np.zeros((3,3));k[:,0]=tau
        sp,ap=attenuate(p,k,1.)
        check('grey_survival_'+str(tau),sp,p/(1+tau),1e-12)
        check('grey_absorption_'+str(tau),ap[:,0],p*tau/(1+tau),1e-12)
        check('grey_energy_pairing_'+str(tau),np.dot(q,sp)+np.sum(q[:,None]*ap),np.dot(q,p),1e-12)
    oracle=json.loads((BASE/'q1b/theory/SOURCE_ENTRY_ALGORITHM_DECISION.json').read_text())['analytic_check']
    errors=[];grey=[]
    for partition,saved in zip([16,32,64],oracle['rows']):
        n=u=0.;h=1./partition
        for j in range(partition):
            ta=j*h;tb=(j+1)*h;ra,rb=math.exp(-ta),math.exp(-tb)
            dn=(tb*tb-ta*ta)/2;dq=math.exp(ta)*math.expm1(h)-h
            injected=h+rb-ra
            increments=np.array([[dn,dq,injected,injected-rb*dq]])
            nn,uu,_=incident([n],[u],-ta,-tb,increments)
            q,p,_=fit_positive(nn[0],uu[0],rb,1.,math.exp(tb),128)
            k=np.zeros((len(p),3));k[:,0]=3.
            sp,ap=attenuate(p,k,h)
            n=math.fsum(sp);u=rb*math.fsum(q*sp)
            RESULT['execution']['manufactured_grey_substeps']+=1
        final=np.array([n,u/math.exp(-1.)]);reference=np.array([float(saved['N']),float(saved['Q'])])
        check('new_positive_grey_vs_saved_'+str(partition),final,reference,1e-10)
        err=abs(final-np.array([float(oracle['N_exact']),float(oracle['Q_exact'])]));errors.append(err)
        grey.append({'partition':partition,'N_Q':final,'error':err})
    ratios=[errors[i]/errors[i+1] for i in range(2)]
    need(all(np.all((r>=1.8)&(r<=2.2)) for r in ratios),'MANUFACTURED_GREY_ORDER')
    RESULT['manufactured']={'birth':rows,'grey':grey,'grey_error_ratios':ratios,'zero_source':'PASS'}

def run():
    bind=BASE/'q1b_selective_native_bind03/evidence/attempt1/RESULT.json'
    need(digest(bind)=='482d800301726ae01a713f4dfc06db9a3227f38abf15fe7a3ee06a5042b08593','BINDING_INPUT_HASH')
    proposal=BASE/'q1b/theory/SOURCE_ENTRY_NEXT.md'
    need(digest(proposal)=='43955350b287f55a3cc6881c166716773c2406a789e1e04ed694f0b931b0a9cc','PROPOSAL_HASH')
    previous=json.loads(bind.read_text());pins=previous['input_sha256']
    need(all(digest(ROOT/p)==s for p,s in pins.items()),'INPUT_SOURCE_HASH')
    RESULT['input_sha256']=pins;RESULT['binding_RESULT_sha256']=digest(bind);RESULT['proposal_sha256']=digest(proposal)
    grid=json.loads((BASE/'q1b_selective_native_bind03/GRID_SELECTIVE_C02.json').read_text())
    edges=np.array(grid['q_edges_eV']);mu=np.array(grid['initial_mu']);weights=np.array(grid['angular_weights'])
    need(hashlib.sha256(edges.astype('<f8').tobytes()).hexdigest()=='a750fdc7338f3e7a4a3e315f39dfb35aa9a990878c5f65f530456d4a2642f26e','GRID_HASH')
    i=int(np.flatnonzero(edges==50000.)[0]);a,b=edges[i:i+2]
    need(a==50000. and b==50049.62945859662,'BIRTH_CELL_IDENTITY')
    RESULT['cell']={'index':i,'edges':[a,b],'mu':mu,'weights':weights}
    manufactured()
    print('MANUFACTURED_POSITIVE_ENTRY_PASS',flush=True)
    provider=HistoryProvider(r=0.);bg=provider.background;table=provider.tables['emissivity']
    RESULT['provider_identity']=provider.identity
    T=2.**-12/provider.geometry(0.)['H'];RESULT['T_s']=T
    def logR(t):return -math.log1p(bg._relative_volume_increment(t))/3
    def r(t):return math.exp(logR(t))
    need(50000./r(T)<b,'ENTRY_REACHES_NEXT_CELL_BOUNDARY')
    event_times=[]
    z0,zT=provider.geometry(0.)['z'],provider.geometry(T)['z']
    for z in table.redshifts:
        if zT<z<z0:event_times.append(bg.time_of_redshift(float(z)))
    for e in np.unique(table.energies_eV):
        if a*r(T)<e<a:event_times.append(brentq(lambda t:a*r(t)-e,0.,T,xtol=1e-4,rtol=4*np.finfo(float).eps))
    event_times=sorted(set(event_times));RESULT['event_times_s']=event_times
    def source(t):
        source_count();g=provider.geometry(t)
        v=table_cell_moments(table,g['z'],[a,b],np.full(2,r(t)),weights)
        return np.stack([v['N'][:,0],v['Q_eV'][:,0]],axis=1)
    native=NativeOpacity();RESULT['execution']['native_processes']=1
    original=native.sigma
    def sigma(energy):
        count=RESULT['execution'];need(count['SIGMA']<256 and count['SIGMA_energies']+len(energy)<=32768,'NATIVE_CALL_CAP')
        count['SIGMA']+=1;count['SIGMA_energies']+=len(energy)
        return original(energy)
    native.sigma=sigma
    def absorbed_step(n,u,rb,cap,h,lower,order):
        q,p,fit=fit_positive(n,u,rb,a,cap,order)
        energy=rb*q;need(np.all(energy<=50000.) and np.all(energy>0),'PHYSICAL_ENERGY_DOMAIN')
        s=native.sigma(energy);cross=C_CM_S*s
        survive,absorbed=attenuate(p,cross*lower,h)
        nextn=math.fsum(survive);nextu=math.fsum(energy*survive)
        count=absorbed.sum(axis=0);binding=CHEMICAL_CHI_EV*count
        heat=np.sum((energy[:,None]-CHEMICAL_CHI_EV)*absorbed,axis=0)
        K0=np.sum(cross*survive[:,None],axis=0);KE=np.sum(energy[:,None]*cross*survive[:,None],axis=0)
        check('point_energy_pair',np.sum(energy*(survive+absorbed.sum(axis=1))),np.dot(energy,p),1e-12)
        check('stored_number_pair',nextn+sum(count),n,1e-12)
        check('stored_energy_pair',nextu+sum(binding)+sum(heat),u,1e-12)
        need(nextn>0 and a<(nextu/nextn)/rb<cap and np.all(heat>=0),'ABSORBED_STATE_CONE')
        return {'N':nextn,'U_eV':nextu,'count':count,'binding_eV':binding,'heat_eV':heat,
                'K0':K0,'KE':KE,'kernel_heat_eV':KE-CHEMICAL_CHI_EV*K0,'fit':fit}
    try:
        for partition in [1,2,4]:
            N=np.zeros(2);U=np.zeros(2);counters=np.zeros(10);steps=[]
            row={'partitions':partition,'steps':steps};RESULT['actual_runs'].append(row)
            # counters: injected N, injected eV, work eV, three absorbed counts,
            # three heat eV and total binding eV.
            for k in range(partition):
                RESULT['execution']['actual_substeps']+=1
                ta,tb=T*k/partition,T*(k+1)/partition
                panels=[ta]+[t for t in event_times if ta<t<tb]+[tb]
                RESULT['execution']['event_panels']+=len(panels)-1
                need(RESULT['execution']['event_panels']<=16,'EVENT_PANEL_CAP')
                coarse=source_integrals(source,logR,ta,tb,panels,16)
                fine=source_integrals(source,logR,ta,tb,panels,32)
                step={'ta':ta,'tb':tb,'source_GL16':coarse,'source_GL32':fine};steps.append(step)
                check('source_time_GL16_32',coarse,fine,1e-10)
                nn,uu,work=incident(N,U,logR(ta),logR(tb),fine)
                check('source_energy_work_pair',uu-U+work,fine[:,2],1e-12)
                rb=r(tb);cap=50000./rb;need(cap<b,'NEXT_CELL_BOUNDARY')
                g=provider.geometry(tb);lower=np.array([g['nH']*(1-2e-4),g['nHe'],0.])
                pairs=[]
                for angle in range(2):
                    values=[absorbed_step(nn[angle],uu[angle],rb,cap,tb-ta,lower,o) for o in [64,128]]
                    for field in ['K0','KE','kernel_heat_eV','N','U_eV','count','heat_eV']:
                        check('opacity_GL64_128_'+field,values[0][field],values[1][field],1e-7)
                    pairs.append(values);v=values[1];N[angle]=v['N'];U[angle]=v['U_eV']
                    counters[3:6]+=v['count'];counters[6:9]+=v['heat_eV'];counters[9]+=sum(v['binding_eV'])
                counters[0]+=fine[:,0].sum();counters[1]+=fine[:,2].sum();counters[2]+=work.sum()
                step.update({'incident_N':nn,'incident_U_eV':uu,'work_eV':work,'orders':pairs,'accepted_N':N.copy(),'accepted_U_eV':U.copy()})
            row.update({'N':N.copy(),'U_eV':U.copy(),'counters':counters.copy(),
                        'energy_unit_note':'Internal counters in eV/reference cm3; multiply by EV_ERG for erg',
                        'injected_energy_erg':counters[1]*EV_ERG,'work_erg':counters[2]*EV_ERG})
            check('cumulative_number',sum(N)+sum(counters[3:6]),counters[0],1e-12)
            check('cumulative_energy',sum(U)+counters[2]+sum(counters[6:9])+counters[9],counters[1],1e-12)
        for co,fi in zip(RESULT['actual_runs'][:-1],RESULT['actual_runs'][1:]):
            c,f=np.array(co['counters']),np.array(fi['counters'])
            check('temporal_number_'+str(fi['partitions']),np.r_[co['N'],c[3:6]],np.r_[fi['N'],f[3:6]],2e-6,scale=f[0])
            check('temporal_energy_'+str(fi['partitions']),np.r_[co['U_eV'],c[2],c[6:10]],np.r_[fi['U_eV'],f[2],f[6:10]],2e-6,scale=f[1])
    finally:native.close()
    need(all(digest(ROOT/p)==s for p,s in pins.items()),'SOURCE_CHANGED')
    RESULT['outcome']='PASS_SOURCE_ENTRY_FIXED_BATH_SCOPED'
    RESULT['next']='Work ownership and gas-direction absorption derivative contract; no full gas solve/history admission'

def worker(out):
    start=time.monotonic();status=0
    try:run()
    except Exception as exc:
        traceback.print_exc();RESULT['outcome']='HOLD_SOURCE_ENTRY04_FIRST_FAILURE'
        RESULT['first_failure']={'type':type(exc).__name__,'message':str(exc)};status=1
    RESULT['wall_s']=time.monotonic()-start
    dump(out/'RESULT.json',RESULT)
    print(json.dumps({'outcome':RESULT['outcome'],'execution':RESULT['execution']}),flush=True)
    return status

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--worker',action='store_true');args=parser.parse_args()
    out=args.output.resolve()
    if args.worker:return worker(out)
    out.mkdir(parents=True,exist_ok=False)
    cmd=['env','OMP_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','MKL_NUM_THREADS=1','NUMEXPR_NUM_THREADS=1',
         'timeout','--signal=TERM','--kill-after=5s','180s','prlimit','--as=2147483648','--cpu=180','--fsize=33554432',
         '/usr/bin/python3','-B',str(Path(__file__).resolve()),'--worker','--output',str(out)]
    dump(out/'STARTED.json',{'command':cmd,'cwd':str(ROOT),'source_sha256':{p.name:digest(p) for p in UNIT.iterdir() if p.is_file()},
                          'prior_cumulative':json.loads((UNIT/'CONTRACT.json').read_text())['prior_cumulative']})
    start=time.monotonic();cpu0=resource.getrusage(resource.RUSAGE_CHILDREN)
    with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:
        p=subprocess.run(cmd,cwd=ROOT,stdout=stdout,stderr=stderr)
    cpu1=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={'exit':p.returncode,'wall_s':time.monotonic()-start,'child_CPU_s':cpu1.ru_utime+cpu1.ru_stime-cpu0.ru_utime-cpu0.ru_stime,
             'CPU_limit_semantics':'per process; measured child CPU separately','files':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in out.iterdir() if p.is_file()}}
    receipt['output_cap_pass']=sum(v['bytes'] for v in receipt['files'].values())<=33554432
    dump(out/'EXECUTION_RECEIPT.json',receipt);print(json.dumps(receipt,indent=2))
    return p.returncode

if __name__=='__main__':raise SystemExit(main())
