"""Once-only saved-cell mean diagnostic; no provider or native execution."""
import argparse
import ast
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

HERE=Path(__file__).resolve().parent
UNIT=HERE.parent
BASE=UNIT.parent
ROOT=UNIT.parents[2]
sys.path.insert(0,str(BASE/'q1b_threshold_positive09'))
import numpy as np
import threshold_positive as inherited
from reconstruction import reconstruct, _quadrature

RESULT={'unit':'Q1B10_NUMERICAL_ADDENDUM02_PRETILT_MEAN_DIAGNOSTIC',
 'checks':[],'raw_rules':[],'candidates':[],
 'execution':{'launches':1,'unique_cells':1,'reconstruct':0,'raw_rules':0,'candidate_fits':0,'Decimal_direct_integrals':0,
              'native':0,'SIGMA':0,'CELL':0,'source':0,'absorption_map':0,'gas':0,'history':0,'build':0},
 'actual_executor':'controller_direct_owner_authorized','runtime_backend':'NOT_INDEPENDENTLY_OBSERVED','global_admission':'HOLD'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,obj):
    def default(x):
        if isinstance(x,np.ndarray):return x.tolist()
        if isinstance(x,np.generic):return x.item()
        raise TypeError(type(x).__name__)
    with p.open('x') as f:json.dump(obj,f,indent=2,allow_nan=False,default=default)
def need(ok,label):
    if not ok:raise AssertionError(label)
def check(label,value,tol):
    ok=bool(math.isfinite(value) and abs(value)<=tol)
    RESULT['checks'].append({'label':label,'value':value,'tolerance':tol,'pass':ok})
    need(ok,label)

def diagnostic_fit():
    """Reuse exact inherited tail, not edit the approved function on disk."""
    source=(BASE/'q1b_threshold_positive09/threshold_positive.py').read_text()
    tree=ast.parse(source)
    f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='fit_threshold_positive')
    assignments=[(i,n.targets[0].id) for i,n in enumerate(f.body)
                 if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)]
    indices={name:i for i,name in assignments}
    need(indices['cell']==0 and ast.unparse(f.body[0].value)=='reconstruct(N, U, R, a, b)','FIT_AST_CELL_PREFIX')
    need(ast.unparse(f.body[indices['guard']].value)==
         'opacity_moments(cell, lambda q: np.ones_like(q), orders=(64, 128), rtol=1e-07)','FIT_AST_GUARD_PREFIX')
    f.args.args += [ast.arg(arg='cell'),ast.arg(arg='guard')]
    f.body=[n for i,n in enumerate(f.body) if i not in (indices['cell'],indices['guard'])]
    module=ast.fix_missing_locations(ast.Module(body=[f],type_ignores=[]))
    scope=dict(vars(inherited));exec(compile(module,'<diagnostic_only_inherited_tail>','exec'),scope)
    RESULT['diagnostic_transformation']={'removed_assignments':['cell=reconstruct(...)','guard=opacity_moments(...)'],
      'replacement':'Supplied single reconstructed cell and coordinate-only metadata; legacy pretilt failure separately retained',
      'unchanged':'Entire remaining inherited function AST; original source file unchanged',
      'function_AST_sha256':hashlib.sha256(ast.dump(module,include_attributes=False).encode()).hexdigest()}
    return scope['fit_threshold_positive']

def run():
    contract=json.loads((HERE/'CONTRACT.json').read_text())
    need(all(sha(HERE/p)==h for p,h in contract['input_sha256'].items()),'INPUT_IDENTITY')
    RESULT['input_sha256']=contract['input_sha256']
    saved=json.loads((UNIT/'evidence/attempt1/RESULT.json').read_text())
    fixed=saved['fixed'];grid=json.loads((BASE/'q1b_selective_native_bind03/GRID_SELECTIVE_C02.json').read_text())
    N,U,R=fixed['incident_N'][33],fixed['incident_U_eV'][33],fixed['R']
    a,b=grid['q_edges_eV'][33],fixed['active_caps'][33]
    need([N,U,R,a,b]==[1.43398528843739e-15,7.796822278962681e-14,.9997559338349717,54.37903440052643,54.42],'ROW33_IDENTITY')
    need(fixed['incident_N'][121]==N and fixed['incident_U_eV'][121]==U,'ROW121_IDENTICAL_REUSED')
    cell=reconstruct(N,U,R,a,b);RESULT['execution']['reconstruct']=1
    need(cell.status=='INTERIOR','SAVED_INTERIOR')
    coordinate=32*math.ulp(b)/min(cell.mean_q-a,b-cell.mean_q)
    check('coordinate_indicator',coordinate,1e-7)
    RESULT['fixed']={'row':33,'row121_reused':True,'N':N,'U':U,'R':R,'a':a,'b':b,'p':cell.p,'FP64_mean':cell.mean_q,'coordinate_indicator':coordinate}
    with localcontext() as ctx:
        ctx.prec=80;D=Decimal.from_float
        ad,bd,pd,nd,ud,rd=map(D,(a,b,cell.p,N,U,R))
        L=(bd/ad).ln()
        def integral(k):
            RESULT['execution']['Decimal_direct_integrals']+=1
            v=pd+Decimal(k)
            return L if v==0 else ((v*L).exp()-Decimal(1))/v
        Z0,Z1=integral(0),integral(1)
        oracle=ad*Z1/Z0;exact_saved=ud/(nd*rd);frozen=D(cell.mean_q)
        width=bd-ad;near=min(frozen-ad,bd-frozen)
        def errors(value,target):
            delta=value-target
            return {'difference':str(delta),'nearer_endpoint_normalized':float(delta/near),'width_normalized':float(delta/width)}
        root_vs_frozen=errors(oracle,frozen);root_vs_saved=errors(oracle,exact_saved)
        RESULT['Decimal80']={'L':str(L),'Z0':str(Z0),'Z1':str(Z1),'powerlaw_mean':str(oracle),
             'exact_saved_U_over_NR':str(exact_saved),'frozen_FP64_mean':str(frozen),
             'nearer_endpoint_denominator':str(near),'width_denominator':str(width),
             'root_vs_frozen':root_vs_frozen,'root_vs_exact_saved':root_vs_saved}
        for target,err in [('frozen',root_vs_frozen),('exact_saved',root_vs_saved)]:
            for norm in ['nearer_endpoint_normalized','width_normalized']:
                check('root_oracle_'+target+'_'+norm,err[norm],1e-7)
        fit=diagnostic_fit()
        for order in (64,128):
            raw=_quadrature(cell,lambda q:np.ones_like(q),[],order);RESULT['execution']['raw_rules']+=1
            x,w=inherited.gauss(order);v=(x+1)/2;logq=cell.quantile_log(v);dq=a*np.expm1(logq);q=a+dq;provisional=w/2
            rawmean=sum((D(float(qi))*D(float(wi)) for qi,wi in zip(q,provisional)),Decimal(0))/sum(map(lambda wi:D(float(wi)),provisional),Decimal(0))
            RESULT['raw_rules'].append({'order':order,'raw':raw,'q':q,'provisional_weights':provisional,
              'Decimal_mean':str(rawmean),'versus_oracle':errors(rawmean,oracle),
              'legacy_nearer_endpoint_residual':raw['quadrature_mean_cell_relative_residual'],
              'legacy_gate_pass':abs(raw['quadrature_mean_cell_relative_residual'])<=1e-7})
            q,p,info=fit(N,U,R,a,b,order,cell,{'float_q_coordinate_indicator':coordinate})
            RESULT['execution']['candidate_fits']+=1
            fitted=sum((D(float(qi))*D(float(pi)) for qi,pi in zip(q,p)),Decimal(0))/sum(map(lambda pi:D(float(pi)),p),Decimal(0))
            error=errors(fitted,oracle)
            RESULT['candidates'].append({'order':order,'q':q,'fitted_weights':p,'fit':info,'Decimal_fitted_mean':str(fitted),'versus_oracle':error})
            check('fit_N_'+str(order),info['N_residual'],1e-12)
            check('fit_Q_'+str(order),info['Q_residual'],1e-12)
            check('fit_cell_mean_'+str(order),info['cell_mean_residual'],1e-7)
            for norm in ['nearer_endpoint_normalized','width_normalized']:
                check('fit_oracle_'+str(order)+'_'+norm,error[norm],1e-7)
    need(RESULT['execution']['Decimal_direct_integrals']==2,'DECIMAL_CAP')
    need(any(not row['legacy_gate_pass'] for row in RESULT['raw_rules']),'FIRST_FAILURE_REPRODUCED')
    need(all(sha(HERE/p)==h for p,h in contract['input_sha256'].items()),'INPUT_UNCHANGED')
    RESULT['original_failure']='UNCHANGED_HOLD_INHERITED_PRETILT_MEAN_QUADRATURE'
    RESULT['outcome']='PRETILT_GATE_VERSUS_POSTFIT_MEAN_SEPARATED_SCOPED'
    RESULT['next']='Independent decision then explicit planner continuation contract; no automatic full retry'

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--worker',action='store_true');args=p.parse_args();out=args.output.resolve()
    if args.worker:
        t=time.monotonic();status=0
        try:run()
        except Exception as exc:traceback.print_exc();RESULT['outcome']='HOLD_DIAGNOSTIC02_FIRST_FAILURE';RESULT['first_failure']={'type':type(exc).__name__,'message':str(exc)};status=1
        RESULT['wall_s']=time.monotonic()-t;dump(out/'RESULT.json',RESULT);return status
    out.mkdir(parents=True,exist_ok=False)
    cmd=['env','OPENBLAS_NUM_THREADS=1','OMP_NUM_THREADS=1','MKL_NUM_THREADS=1','timeout','--signal=TERM','--kill-after=5s','60s','prlimit','--as=2147483648','--cpu=60','--fsize=8388608','/usr/bin/python3','-B',str(Path(__file__).resolve()),'--worker','--output',str(out)]
    dump(out/'STARTED.json',{'command':cmd,'cwd':str(ROOT),'implementation_sha256':{p.name:sha(p) for p in HERE.iterdir() if p.is_file()}})
    t=time.monotonic();c0=resource.getrusage(resource.RUSAGE_CHILDREN)
    with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:r=subprocess.run(cmd,cwd=ROOT,stdout=stdout,stderr=stderr)
    c1=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={'exit':r.returncode,'wall_s':time.monotonic()-t,'child_CPU_s':c1.ru_utime+c1.ru_stime-c0.ru_utime-c0.ru_stime,
      'files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in out.iterdir() if p.is_file()}}
    receipt['output_cap_pass']=sum(p['bytes'] for p in receipt['files'].values())<=8388608
    dump(out/'EXECUTION_RECEIPT.json',receipt);print(json.dumps(receipt,indent=2));return r.returncode
if __name__=='__main__':raise SystemExit(main())
