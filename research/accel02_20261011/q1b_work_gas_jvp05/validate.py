"""Single bounded work/JVP validation. Existing sources and evidence are read-only."""
import argparse
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
from adapter import work_split, absorption_map, domain, FIELDS, BASE
from positive_entry import fit_positive
from opacity_native import EV_ERG, C_CM_S, CHEMICAL_CHI_EV, NativeOpacity
sys.path.insert(0,str(BASE/'q1b_selective_native_bind03'))
from caller import Caller
from provider import HistoryProvider

UNIT=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
DECIMAL_ACTUAL=False
RESULT={'unit':'Q1B5_WORK_SPLIT_GAS_ABSORPTION_JVP01','checks':[],'work':[],'derivatives':[],
        'execution':{'native_processes':0,'CELL_RHS_V1':0,'SIGMA':0,'SIGMA_energies':0,'gas_map_evaluations':0,
                     'source_integrations':0,'new_steps':0,'build':0,'gas_solve':0,'history_ODE':0},
        'executor':'controller_direct_owner_authorized','observed_runtime_model':'NOT_INDEPENDENTLY_OBSERVED',
        'global_admission':'HOLD','fields':FIELDS}

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,obj):
    def convert(v):
        if isinstance(v,np.ndarray):return v.tolist()
        if isinstance(v,np.generic):return v.item()
        raise TypeError(type(v).__name__)
    with Path(p).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False,default=convert)
def need(ok,label):
    if not ok:raise AssertionError(label)
def errors(a,b,scale):
    a,b=np.broadcast_arrays(np.asarray(a,float),np.asarray(b,float));s=np.broadcast_to(np.asarray(scale,float),a.shape)
    need(np.isfinite(a).all() and np.isfinite(b).all() and np.isfinite(s).all() and np.all(s>=0),'NONFINITE_COMPARISON')
    d=abs(a-b)
    need(np.all(d[s==0]==0),'NONZERO_ON_EXACT_ZERO_SCALE')
    return np.divide(d,s,out=np.zeros_like(d),where=s!=0)
def check(label,a,b,tol,scale=None):
    err=errors(a,b,abs(np.asarray(b)) if scale is None else scale);maximum=float(np.max(err))
    RESULT['checks'].append({'label':label,'maximum':maximum,'tolerance':tol,'pass':maximum<=tol})
    need(maximum<=tol,'HOLD_'+label);return maximum
def gas_at_temperature(g,x,T):
    x=np.asarray(x);ratio=g['nHe']/g['nH']
    w=1.5*1.380649e-16*T*(1+ratio+x[0]+ratio*(x[1]+2*x[2]))/EV_ERG
    return np.r_[x,w]

def run_work(caller,provider,entry):
    T=entry['T_s'];g=provider.geometry(T);gas=provider.initial_gas.copy();step=entry['actual_runs'][0]['steps'][0]
    R=math.exp(-math.log1p(provider.background._relative_volume_increment(T))/3)
    mu=entry['cell']['mu'];cells=[]
    for i in range(2):
        v=step['orders'][i][1];lam=g['H']+g['s']*(3*mu[i]**2-1)
        cells.append([mu[i],R,lam,v['N'],v['U_eV'],0.,0.,*v['K0'],*v['KE']])
    fixtures=[('saved_entry_endpoint',g,gas,np.array(cells),T)]
    fixed={'a_rel':1.3,'b':0.,'H':2e-18,'s':.2*2e-18,'nH':1e-3,'nHe':8e-5,'Tcmb_K':46.}
    gas=gas_at_temperature(fixed,[.2,.3,.1],5000.)
    beam=np.zeros((3,13));beam[:,0]=[0.,.6,1.];beam[:,1]=1/1.3
    beam[:,3]=np.array([1.,2.,3.])*1e-8;beam[:,4]=beam[:,3]*[80.,100.,120.]
    for label in ['base','zero_H_s','empty','double_w','double_U','negative_s']:
        gg=fixed.copy();yy=gas.copy();cc=beam.copy()
        if label=='zero_H_s':gg['H']=gg['s']=0.
        if label=='empty':cc[:,3:]=0.
        if label=='double_w':yy[3]*=2
        if label=='double_U':cc[:,4]*=2
        if label=='negative_s':gg['s']=-.2*gg['H']
        cc[:,2]=gg['H']+gg['s']*(3*cc[:,0]**2-1)
        fixtures.append((label,gg,yy,cc,0.))
    for label,g,gas,cells,t in fixtures:
        need(caller.counts['CELL_RHS_V1']<7,'CELL_CAP')
        out=caller.submit(t,g,gas,cells);work=work_split(g,gas,cells,out)
        scale=work['termwise_scale']
        check('ABI_work_'+label,work['radiation_work_rate']+work['gas_work_rate'],out[5],2e-11,scale)
        check('pressure_work_'+label,work['radiation_work_rate'],work['pressure_form_radiation'],1e-12,scale)
        check('native_residual_'+label,out[12:14],0.,1e-12,1.)
        RESULT['work'].append({'fixture':label,'geometry':g,'gas':gas,'cells':cells,'native':out,'split':work})
    w={row['fixture']:row['split'] for row in RESULT['work']};base=w['base'];scale=base['termwise_scale']
    need(w['zero_H_s']['abi_combined_work_rate']==w['zero_H_s']['radiation_work_rate']==w['zero_H_s']['gas_work_rate']==0.,'ZERO_WORK')
    for label,rad,thermal in [('empty',0.,base['gas_work_rate']),('double_w',base['radiation_work_rate'],2*base['gas_work_rate']),('double_U',2*base['radiation_work_rate'],base['gas_work_rate'])]:
        check('variant_'+label,[w[label]['radiation_work_rate'],w[label]['gas_work_rate']],[rad,thermal],1e-12,scale)
    shear=EV_ERG*fixed['s']*sum((3*beam[:,0]**2-1)*beam[:,4])
    check('negative_s_difference',w['negative_s']['radiation_work_rate']-base['radiation_work_rate'],-2*shear,1e-12,scale)

def evaluate(q,p,R,h,sigma,g,gas,directions=()):
    # Domain is checked before admission to the map; no clipped trial enters.
    domain(gas);need(RESULT['execution']['gas_map_evaluations']<(4 if DECIMAL_ACTUAL else 128),'MAP_CAP')
    RESULT['execution']['gas_map_evaluations']+=1
    return absorption_map(q,p,R,h,sigma,g,gas,directions)

def decimal_values(*args,**kwargs):
    from decimal_oracle import values
    count=RESULT['execution'].setdefault('Decimal80_map_evaluations',0)
    need(count<76,'DECIMAL_MAP_CAP');RESULT['execution']['Decimal80_map_evaluations']+=1
    return values(*args,**kwargs)

class RepairSigmaOnly:
    def __init__(self):
        self.opacity=NativeOpacity();self.counts={'native_processes':1,'SIGMA':0,'SIGMA_energies':0,'CELL_RHS_V1':0}
        sigma=self.opacity.sigma
        def bounded(energy):
            need(self.counts['SIGMA']<4 and self.counts['SIGMA_energies']+len(energy)<=384,'REPAIR_SIGMA_CAP')
            self.counts['SIGMA']+=1;self.counts['SIGMA_energies']+=len(energy);return sigma(energy)
        self.opacity.sigma=bounded
    def close(self):self.opacity.close()

def fixture(caller,label,params,g,gas,directions,modes,h=None):
    N,U,R,a,b=params;nodes=[]
    for order in [64,128]:
        q,p,fit=fit_positive(N,U,R,a,b,order)
        need(caller.counts['SIGMA']<16 and caller.counts['SIGMA_energies']+len(q)<=2048,'SIGMA_CAP')
        sigma=caller.opacity.sigma(R*q);nodes.append((order,q,p,fit,sigma))
    if h is None:
        lower=[g['nH']*(1-gas[0]),g['nHe']*(1-gas[1]-gas[2]),g['nHe']*gas[1]]
        h=1/np.max((C_CM_S*nodes[1][4]*lower).sum(axis=1))
    pair=[]
    for order,q,p,fit,sigma in nodes:
        val,jvp,scales,pairs=evaluate(q,p,R,h,sigma,g,gas,directions)
        need(np.all(val[:23]>=0),'POSITIVE_FUNCTIONALS')
        check(label+'_value_number',val[0]+sum(val[2:5]),N,1e-12)
        check(label+'_value_energy',val[1]+sum(val[5:11]),U,1e-12)
        row={'fixture':label,'order':order,'params':params,'geometry':g,'gas':gas,'h':h,'fit':fit,
             'values':val,'jvp':jvp,'scales':scales,'directions':directions,'FD':[]};RESULT['derivatives'].append(row)
        if DECIMAL_ACTUAL:
            row['raw_nodes']={'q':q,'P':p,'sigma':sigma,'R':R,'h':h}
            dbaseline=decimal_values(q,p,R,h,sigma,g,gas)
            row['Decimal80_baseline']=[str(z) for z in dbaseline]
            check(label+'_Decimal80_baseline_link',val,[float(z) for z in dbaseline],1e-12)
        for d,(direction,mode,pairing) in enumerate(zip(directions,modes,pairs)):
            check(label+'_node_derivative_pair',pairing['node_residual'],0.,1e-12,pairing['node_scale'])
            check(label+'_energy_derivative_pair',pairing['energy_residual'],0.,1e-12,pairing['energy_scale'])
            check(label+'_number_JVP_pair',jvp[d,0]+sum(jvp[d,2:5]),0.,1e-12,scales[d,0]+sum(scales[d,2:5]))
            check(label+'_energy_JVP_pair',jvp[d,1]+sum(jvp[d,5:11]),0.,1e-12,scales[d,1]+sum(scales[d,5:11]))
            need(jvp[d,24]==0.,'RADIATION_WORK_GAS_JVP_ZERO')
            if mode=='thermal':
                need(np.all(jvp[d,:23]==0.) and np.all(scales[d,:23]==0.),'THERMAL_PHOTON_JVP_ZERO')
                # The adapter has no w dependence except the explicit gas work term.
                for eps in [2.**-8,2.**-9,2.**-10]:
                    gg=gas+eps*direction;domain(gg)
                    exact=2*g['H']*EV_ERG*g['nH']*g['a_rel']**3*direction[3]
                    check(label+'_thermal_work_JVP',jvp[d,23],exact,1e-12,abs(exact))
                row['FD'].append({'direction':d,'mode':'EXACT_THERMAL_ZERO_NO_PHOTON_FD','order':'ORDER_NOT_RESOLVED'})
                continue
            selected=np.arange(2,11) if label.startswith('actual') else np.arange(25)
            fdrows=[]
            fdrecord={'direction':d,'mode':mode,'rows':fdrows,'order':'NOT_YET_EVALUATED'}
            row['FD'].append(fdrecord)
            for eps in [2.**-8,2.**-9,2.**-10]:
                fdrow={'epsilon':eps,'selected_fields':[FIELDS[i] for i in selected]};fdrows.append(fdrow)
                if DECIMAL_ACTUAL:
                    from decimal_oracle import difference
                    plus=decimal_values(q,p,R,h,sigma,g,gas,direction,eps)
                    other=decimal_values(q,p,R,h,sigma,g,gas,direction,2*eps if mode=='right' else -eps)
                    dfd=difference(dbaseline,plus,other,eps,mode)
                    fdrow.update({'Decimal80_plus':[str(z) for z in plus],
                                  'Decimal80_plus2' if mode=='right' else 'Decimal80_minus':[str(z) for z in other],
                                  'Decimal80_FD':[str(z) for z in dfd]})
                    fd=np.array([float(z) for z in dfd])
                else:
                    plus=evaluate(q,p,R,h,sigma,g,gas+eps*direction)[0]
                    if mode=='right':
                        plus2=evaluate(q,p,R,h,sigma,g,gas+2*eps*direction)[0];fd=(-3*val+4*plus-plus2)/(2*eps)
                    else:
                        minus=evaluate(q,p,R,h,sigma,g,gas-eps*direction)[0];fd=(plus-minus)/(2*eps)
                fdrow['FD']=fd[selected];fdrow['scale']=scales[d,selected]
                err=errors(fd[selected],jvp[d,selected],scales[d,selected])
                fdrow.update({'scaled_errors':err,'maximum':float(max(err))})
            check(label+'_finest_FD',fdrows[-1]['FD'],jvp[d,selected],1e-7,scales[d,selected])
            for c,f in zip(fdrows[:-1],fdrows[1:]):
                ce,fe=np.array(c['scaled_errors']),np.array(f['scaled_errors'])
                need(np.all(fe[ce>1e-9]<=ce[ce>1e-9]),'FD_REFINEMENT_WORSENED')
            fdrecord['order']='ORDER_NOT_RESOLVED' if fdrows[0]['maximum']<=1e-9 else 'REFINEMENT_NONWORSENING'
        pair.append((val,jvp,scales))
    check(label+'_GL_value',pair[0][0],pair[1][0],1e-7)
    check(label+'_GL_JVP',pair[0][1],pair[1][1],1e-7,pair[1][2])

def run():
    entrypath=BASE/'q1b_source_entry04/evidence/attempt1/RESULT.json'
    need(digest(entrypath)=='6dffb2891b0146ddb7f5774da238f2f38c864780cd4f72ee71782e6b9ef8b418','ENTRY_IDENTITY')
    entry=json.loads(entrypath.read_text());pins=entry['input_sha256'].copy()
    pins.update({str((BASE/'q1b_source_entry04/positive_entry.py').relative_to(ROOT)):'5f23ccfa306c4e9aae1ce08765ab5f23d9a2c0ea20454b08b7a4f626cdf23623',
                 str((BASE/'q1b_selective_native_bind03/caller.py').relative_to(ROOT)):'a78c05c12133f05bda80251b2e8d339bfc3afeb97f4f228a7c5af1d60ea057df',
                 str((BASE/'q1b/native/src/main.rs').relative_to(ROOT)):'147884bf5ed60024a265803896a7c76d50e4db9f28f4b24b69a4572e9634a2f6'})
    need(all(digest(ROOT/p)==s for p,s in pins.items()),'SOURCE_IDENTITY')
    review=json.loads((BASE/'q1b_source_entry04/INDEPENDENT_REVIEW.json').read_text())
    need(review['decision']=='PASS_SOURCE_ENTRY_FIXED_BATH_SCOPED','ENTRY_REVIEW_REQUIRED')
    RESULT['input_sha256']=pins;RESULT['entry_RESULT_sha256']=digest(entrypath)
    for bad in [[-1.,0.,0.,1.],[.2,.7,.4,1.],[.2,.3,.1,0.]]:
        try:domain(np.array(bad))
        except ValueError:pass
        else:raise AssertionError('OUTSIDE_DOMAIN_ACCEPTED')
    if DECIMAL_ACTUAL:
        reused={'evidence/attempt1/RESULT.json':'9b5f1d4190f67207b72df3e59d869c0dd07b86f47793336d38b850201f6731f1',
                'evidence/manufactured01/RESULT.json':'a386062ed13415e2c919ee751a5f86fd356b074e85d53553aef993ac972dc37e',
                'adapter.py':'c7f1cac3ecbb4a8dc8edfc62f1c7458fff77e9ff6633cadb0cfb1c8e4c15f3c5'}
        need(all(digest(UNIT/p)==s for p,s in reused.items()),'REPAIR_REUSE_IDENTITY')
        RESULT['reuse_sha256']=reused;RESULT['repair']='ACTUAL_ONLY_DECIMAL80_VALUE_FD_ORACLE'
    provider=HistoryProvider(r=0.);caller=RepairSigmaOnly() if DECIMAL_ACTUAL else Caller()
    try:
        if not DECIMAL_ACTUAL:run_work(caller,provider,entry);print('WORK_SPLIT_7_NATIVE_CALLS_PASS',flush=True)
        T=entry['T_s'];g=provider.geometry(T);gas=provider.initial_gas.copy();R=math.exp(-math.log1p(provider.background._relative_volume_increment(T))/3)
        step=entry['actual_runs'][0]['steps'][0]
        directions=np.array([[1e-4,0,0,0],[0,1e-3,0,0],[0,0,1e-3,0],[0,0,0,.1*gas[3]]])
        for j in range(2):
            fixture(caller,'actual_angle'+str(j),(step['incident_N'][j],step['incident_U_eV'][j],R,50000.,50000./R),g,gas,directions,['central','right','right','thermal'],T)
        if not DECIMAL_ACTUAL:
            g={'a_rel':1.3,'b':0.,'H':2e-18,'s':.2*2e-18,'nH':1e-3,'nHe':8e-5,'Tcmb_K':46.}
            gas=gas_at_temperature(g,[.2,.3,.1],5000.)
            directions=np.array([[.1,0,0,0],[0,.1,0,0],[0,0,.1,0],[0,0,0,.1*gas[3]],[.1,-.08,.03,.1*gas[3]]])
            fixture(caller,'manufactured_tau_order_one',(1e-8,90e-8,1.,60.,120.),g,gas,directions,['central','central','central','thermal','central'])
    finally:
        RESULT['execution'].update(caller.counts);caller.close()
    need(all(digest(ROOT/p)==s for p,s in pins.items()),'SOURCE_CHANGED')
    RESULT['outcome']='PASS_ACTUAL_ABSORPTION_JVP_DECIMAL80_SCOPED' if DECIMAL_ACTUAL else 'PASS_WORK_SPLIT_GAS_ABSORPTION_JVP_SCOPED'
    RESULT['next']='Bounded single-endpoint four-gas residual evaluator and admissible trial line-search contract'
    RESULT['claim_ceiling']='Fixed-node photo functional derivative only; not full gas RHS Jacobian, nonlinear solve, channel-relative time convergence or history admission'

def worker(out):
    t=time.monotonic();status=0
    try:run()
    except Exception as exc:
        traceback.print_exc();RESULT['outcome']='HOLD_WORK_GAS_JVP05_FIRST_FAILURE';RESULT['first_failure']={'type':type(exc).__name__,'message':str(exc)};status=1
    RESULT['wall_s']=time.monotonic()-t;dump(out/'RESULT.json',RESULT)
    print(json.dumps({'outcome':RESULT['outcome'],'execution':RESULT['execution']}),flush=True);return status

def main():
    global DECIMAL_ACTUAL
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--worker',action='store_true');parser.add_argument('--decimal-actual',action='store_true');args=parser.parse_args();out=args.output.resolve();DECIMAL_ACTUAL=args.decimal_actual
    if args.worker:return worker(out)
    out.mkdir(parents=True,exist_ok=False)
    cmd=['env','OMP_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','MKL_NUM_THREADS=1','NUMEXPR_NUM_THREADS=1','timeout','--signal=TERM','--kill-after=5s','120s','prlimit','--as=2147483648','--cpu=120','--fsize=16777216','/usr/bin/python3','-B',str(Path(__file__).resolve()),'--worker','--output',str(out)]
    if DECIMAL_ACTUAL:cmd.append('--decimal-actual')
    contract=json.loads((UNIT/('PRECISION_ORACLE_ADDENDUM01.json' if DECIMAL_ACTUAL else 'CONTRACT.json')).read_text())
    dump(out/'STARTED.json',{'command':cmd,'cwd':str(ROOT),'source_sha256':{p.name:digest(p) for p in UNIT.iterdir() if p.is_file()},'prior_cumulative':contract['prior_cumulative']})
    t=time.monotonic();c0=resource.getrusage(resource.RUSAGE_CHILDREN)
    with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:p=subprocess.run(cmd,cwd=ROOT,stdout=stdout,stderr=stderr)
    c1=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={'exit':p.returncode,'wall_s':time.monotonic()-t,'child_CPU_s':c1.ru_utime+c1.ru_stime-c0.ru_utime-c0.ru_stime,'CPU_limit_semantics':'per process; child CPU measured separately','files':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in out.iterdir() if p.is_file()}}
    receipt['output_cap_pass']=sum(v['bytes'] for v in receipt['files'].values())<=16777216
    dump(out/'EXECUTION_RECEIPT.json',receipt);print(json.dumps(receipt,indent=2));return p.returncode

if __name__=='__main__':raise SystemExit(main())
