"""Create-only moving-threshold experiment, independent Decimal step oracle."""
import argparse
from decimal import Decimal,localcontext
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
from threshold_positive import fit_threshold_positive
from positive_entry import fit_positive,attenuate
from reconstruction import reconstruct
from opacity_native import NativeOpacity,THRESHOLDS_EV,CHEMICAL_CHI_EV,C_CM_S
from provider import HistoryProvider

UNIT=Path(__file__).resolve().parent;BASE=UNIT.parent;ROOT=UNIT.parents[2]
RESULT={'unit':'Q1B9_MOVING_THRESHOLD_POSITIVE_QUADRATURE01','checks':[],'fixtures':[],
 'execution':{'native_processes':0,'SIGMA':0,'SIGMA_energies':0,'positive_absorption_maps':0,'fresh_IC':0,'source_integration':0,'CELL_RHS':0,'gas_update':0,'history':0,'build':0},
 'executor':'controller_direct_owner_authorized','observed_runtime_model':'NOT_INDEPENDENTLY_OBSERVED','global_admission':'HOLD'}
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path,value):
    def convert(x):
        if isinstance(x,np.ndarray):return x.tolist()
        if isinstance(x,np.generic):return x.item()
        raise TypeError(type(x).__name__)
    with path.open('x') as f:json.dump(value,f,indent=2,allow_nan=False,default=convert)
def need(ok,label):
    if not ok:raise AssertionError(label)
def check(label,actual,expected,tol,scale=None):
    a,b=np.asarray(actual,float),np.asarray(expected,float)
    s=abs(b) if scale is None else np.broadcast_to(np.asarray(scale,float),a.shape)
    diff=abs(a-b);err=np.divide(diff,s,out=np.zeros_like(diff),where=s!=0)
    ok=bool(np.isfinite(a).all() and np.isfinite(b).all() and np.all(err<=tol) and np.all(diff[s==0]==0))
    RESULT['checks'].append({'label':label,'maximum':float(np.max(err)),'tolerance':tol,'pass':ok})
    need(ok,'HOLD_'+label)
def relative(a,b):
    a,b=np.asarray(a),np.asarray(b)
    return {'difference':a-b,'relative':np.divide(abs(a-b),abs(b),out=np.zeros_like(b),where=b!=0),
            'exact_zero_mask':b==0,'nonzero_over_zero_mask':(b==0)&(a!=0)}
def decimal_step(cell,E,chi):
    """Direct truncated exp integrals in log(q/a), no quadrature/CDF reuse."""
    with localcontext() as ctx:
        ctx.prec=80
        D=Decimal.from_float;a,b,R,N,p=map(D,(cell.a,cell.b,cell.R,cell.N,cell.p))
        lower=max(a,D(float(E))/R)
        if lower>=b:return np.zeros(3)
        L=(b/a).ln();l=(lower/a).ln()
        def integral(power,left):
            if power==0:return L-left
            return ((power*L).exp()-(power*left).exp())/power
        norm=integral(p,Decimal(0));k0=N*integral(p,l)/norm
        ke=N*R*a*integral(p+1,l)/norm
        return np.array([float(k0),float(ke),float(ke-D(float(chi))*k0)])
def moments(q,p,R,sigma):
    E=R*q;cross=C_CM_S*sigma
    return np.stack([np.sum(cross*p[:,None],axis=0),np.sum(E[:,None]*cross*p[:,None],axis=0),
                     np.sum((E[:,None]-CHEMICAL_CHI_EV)*cross*p[:,None],axis=0)])
def absorption(q,p,R,sigma,T,N,U):
    RESULT['execution']['positive_absorption_maps']+=1
    need(RESULT['execution']['positive_absorption_maps']<=36,'MAP_CAP')
    E=R*q;cross=C_CM_S*sigma;lower=np.array([1e-3*.8,8e-5*.6,8e-5*.3])
    survive,absorb=attenuate(p,cross*lower,T)
    count=absorb.sum(axis=0);binding=CHEMICAL_CHI_EV*count
    heat=np.sum((E[:,None]-CHEMICAL_CHI_EV)*absorb,axis=0)
    nextn=math.fsum(survive);nextu=math.fsum(E*survive)
    check('pointwise_pairing',survive+absorb.sum(axis=1),p,1e-12)
    check('stored_number_pairing',nextn+math.fsum(count),N,1e-12)
    check('stored_energy_pairing',nextu+math.fsum(binding)+math.fsum(heat),U,1e-12)
    need(np.all(heat>=0) and np.all(count>=0) and nextn>=0 and nextu>=0,'ABSORPTION_POSITIVITY')
    mean=nextu/R/nextn if nextn else None
    need(mean is not None and q.min()<mean<q.max(),'SURVIVING_CONE')
    return {'N':nextn,'U_eV':nextu,'count':count,'binding_eV':binding,'heat_eV':heat,
            'moments':moments(q,survive,R,sigma),'q':q,'p':p,'survive':survive,'absorbed':absorb}
def run():
    bindpath=BASE/'q1b_selective_native_bind03/evidence/attempt1/RESULT.json'
    need(digest(bindpath)=='482d800301726ae01a713f4dfc06db9a3227f38abf15fe7a3ee06a5042b08593','B3_IDENTITY')
    bind=json.loads(bindpath.read_text());pins=bind['input_sha256'].copy()
    additions={'q1b_selective_native_bind03/GRID_SELECTIVE_C02.json':'78110050b83a91bd59ceb35f8f65887b66e0a6a83feea2698fa4747a5fcf6769',
      'q1b_source_entry04/positive_entry.py':'5f23ccfa306c4e9aae1ce08765ab5f23d9a2c0ea20454b08b7a4f626cdf23623',
      'q1b_coupled_refinement08/evidence/attempt1/RESULT.json':'dad0e0b0fcc50d56b25f8d8e4ad9acbf39d419b74a27069e71dde6caea5a9a4a'}
    for p,s in additions.items():pins[str((BASE/p).relative_to(ROOT))]=s
    need(all(digest(ROOT/p)==s for p,s in pins.items()),'FROZEN_INPUT_IDENTITY');RESULT['input_sha256']=pins
    grid=json.loads((BASE/'q1b_selective_native_bind03/GRID_SELECTIVE_C02.json').read_text());edges=np.array(grid['q_edges_eV'])
    need(hashlib.sha256(edges.astype('<f8').tobytes()).hexdigest()=='a750fdc7338f3e7a4a3e315f39dfb35aa9a990878c5f65f530456d4a2642f26e','EDGES_IDENTITY')
    for N,U,R,a,b in [(0.,0.,1.,1.,2.),(0.,0.,1.,1.,1.)]:
        q,p,fit=fit_threshold_positive(N,U,R,a,b,64);need(q.size==p.size==0 and fit['empty'],'EMPTY_EXACT')
    rejected=[]
    for U in [1.,2.]:
        try:fit_threshold_positive(1.,U,1.,1.,2.,64)
        except ValueError as exc:
            need(str(exc)=='ENTRY_STRICT_CONE_REQUIRED','WEAK_LIMIT_TYPED');rejected.append(str(exc))
        else:raise AssertionError('WEAK_LIMIT_ACCEPTED')
    RESULT['boundary_regressions']={'empty':2,'weak_rejections':rejected}
    provider=HistoryProvider(r=0.);T=2827462976819.2324
    RESULT['fixture_definition']='Saved actualIC moments transformed by collisionless redshift; nophysicaltrajectory'
    RESULT['provider_identity']=provider.identity
    native=NativeOpacity();RESULT['execution']['native_processes']=1;original=native.sigma
    def sigma(energy):
        c=RESULT['execution'];need(c['SIGMA']<128 and c['SIGMA_energies']+len(energy)<=24576,'SIGMA_CAP')
        c['SIGMA']+=1;c['SIGMA_energies']+=len(energy)
        return original(energy)
    native.sigma=sigma
    try:
        for t in [0.,T/2,T]:
            R=1/provider.geometry(t)['a_rel']
            for j in range(2):
                for i in [12,17,34]:
                    a,b=edges[i:i+2];initial=bind['initial_cells'][j*88+i];N=initial[3];U=R*initial[4]
                    cell=reconstruct(N,U,R,a,b)
                    row={'t_s':t,'angle':j,'cell':i,'N':N,'U_eV':U,'R':R,'support':[a,b],'p':cell.p,'orders':[]}
                    RESULT['fixtures'].append(row)
                    reference=native.moments(cell,orders=(64,128),rtol=1e-7);row['native_reference']=reference
                    ref=np.array([reference['K0'],reference['KE'],reference['heat_eV']])
                    target_index=[12,17,34].index(i);oracle=decimal_step(cell,THRESHOLDS_EV[target_index],CHEMICAL_CHI_EV[target_index]);row['step_oracle']=oracle
                    for order in [64,128]:
                        q,p,fit=fit_threshold_positive(N,U,R,a,b,order)
                        E=R*q;sig=sigma(E);raw=moments(q,p,R,sig)
                        step=np.array([math.fsum(p[E>=THRESHOLDS_EV[target_index]]),math.fsum((E*p)[E>=THRESHOLDS_EV[target_index]]),math.fsum(((E-CHEMICAL_CHI_EV[target_index])*p)[E>=THRESHOLDS_EV[target_index]])])
                        sample={'order':order,'fit':fit,'native_moments':raw,'step_moments':step}
                        row['orders'].append(sample)
                        check('step_Decimal80',step,oracle,1e-7)
                        check('native_split_reference',raw,ref,1e-7)
                        sample['absorption']=absorption(q,p,R,sig,T,N,U)
                    coarse,fine=row['orders'];check('native_GL64_128',coarse['native_moments'],fine['native_moments'],1e-7)
                    for field in ['N','U_eV','count','binding_eV','heat_eV','moments']:
                        check('absorption_GL64_128_'+field,coarse['absorption'][field],fine['absorption'][field],1e-7)
                    uq,up,uf=fit_positive(N,U,R,a,b,128);us=sigma(R*uq);raw=moments(uq,up,R,us)
                    row['unsplit_diagnostic']={'order':128,'fit':uf,'raw':raw,'versus_split_reference':relative(raw,ref),'acceptance_oracle':False}
    finally:native.close()
    need(len(RESULT['fixtures'])==18,'FIXTURE_COUNT')
    need(all(digest(ROOT/p)==s for p,s in pins.items()),'FROZEN_INPUT_CHANGED')
    RESULT['outcome']='PASS_MOVING_THRESHOLD_POSITIVE_QUADRATURE_SCOPED'
    RESULT['next']='Astra fullC02 onesubstep trialcontract for sameN1lane'
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.output.resolve()
    if a.worker:
        t=time.monotonic();status=0
        try:run()
        except Exception as exc:traceback.print_exc();RESULT['outcome']='HOLD_THRESHOLD_POSITIVE09_FIRST_FAILURE';RESULT['first_failure']={'type':type(exc).__name__,'message':str(exc)};status=1
        RESULT['wall_s']=time.monotonic()-t;dump(out/'RESULT.json',RESULT);print(json.dumps({'outcome':RESULT['outcome'],'execution':RESULT['execution']}));return status
    out.mkdir(parents=True,exist_ok=False)
    cmd=['env','OMP_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','MKL_NUM_THREADS=1','timeout','--signal=TERM','--kill-after=5s','120s','prlimit','--as=2147483648','--cpu=120','--fsize=33554432','/usr/bin/python3','-B',str(Path(__file__).resolve()),'--worker','--output',str(out)]
    dump(out/'STARTED.json',{'command':cmd,'cwd':str(ROOT),'implementation_sha256':{p.name:digest(p) for p in UNIT.iterdir() if p.is_file()},'prior_cumulative':json.loads((UNIT/'CONTRACT.json').read_text())['prior_cumulative']})
    t=time.monotonic();c0=resource.getrusage(resource.RUSAGE_CHILDREN)
    with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:r=subprocess.run(cmd,cwd=ROOT,stdout=stdout,stderr=stderr)
    c1=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={'exit':r.returncode,'wall_s':time.monotonic()-t,'child_CPU_s':c1.ru_utime+c1.ru_stime-c0.ru_utime-c0.ru_stime,'CPU_limit_semantics':'perprocess, measuredchildCPUseparate','files':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in out.iterdir() if p.is_file()}}
    receipt['output_cap_pass']=sum(x['bytes'] for x in receipt['files'].values())<=33554432;dump(out/'EXECUTION_RECEIPT.json',receipt);print(json.dumps(receipt,indent=2));return r.returncode
if __name__=='__main__':raise SystemExit(main())
