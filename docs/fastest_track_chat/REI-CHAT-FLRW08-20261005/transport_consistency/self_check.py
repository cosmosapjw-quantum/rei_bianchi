"""Finite numerical and exact-rational checks; no native or trajectory replay."""
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.linalg import expm
from transport_core import (energy_nodes, number_generator, energy_generator,
    projection, original_hat_map, projected_number_map, projected_energy_map,
    cfl_linear_map, local_defect_bound, column_norm)

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]
OUT=ROOT/'.cuh/fastest-track/REI-CHAT-FLRW08/transport-consistency/outputs'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    checks=[]
    def check(name,ok,detail=None):
        checks.append({'name':name,'status':'PASS' if bool(ok) else 'FAIL','detail':detail})
    E=energy_nodes(); B=number_generator(E); C=energy_generator(E)
    w=np.r_[E[1:],1.]; lam=E[1:]/np.diff(E); L=float(max(lam))
    ef=[Fraction(float(x)) for x in E]
    lf=[ef[j]/(ef[j]-ef[j-1]) for j in range(1,len(E))]
    exact=max(lf)
    check('exact rational all number column sums zero',all(-l+l==0 for l in lf))
    check('exact rational all energy moment columns -weight',all(-l*ef[j]+l*ef[j-1]==-ef[j] for j,l in enumerate(lf,1)))
    check('exact rational number induced l1 norm',max(2*l for l in lf)==2*exact)
    check('exact rational weighted-energy induced l1 norm',max([l+l*ef[j-1]/ef[j] for j,l in enumerate(lf,1)]+[Fraction(1)])==2*exact-1)
    check('numeric generator number norm',abs(column_norm(B)-2*L)<1e-10)
    check('numeric generator weighted energy norm',abs(column_norm(C,w)-(2*L-1))<1e-10)
    P=projection(E)
    check('P idempotent numerical matrix',np.array_equal(P@P,P))
    for r in [1.,math.exp(-1e-8),math.exp(-1.25e-5),math.exp(-2e-5),.5,.01]:
        M=original_hat_map(E,r)
        check(f'P M = P M P all columns r={r}',column_norm(P@M-P@M@P)<1e-12)
        K=projected_number_map(E,r); U=projected_energy_map(E,r)
        check(f'all-state number positivity and conservation r={r}',K.min()>=0 and max(abs(K.sum(axis=0)-1))<3e-15)
        check(f'all-state weighted energy positivity and moment r={r}',U.min()>=0 and max(abs(w@U-r*w))<1e-13)
        check(f'all-state number contractivity r={r}',column_norm(K)<=1+3e-15)
        check(f'all-state energy contractivity r={r}',column_norm(U,w)<=r+3e-15)
    for s in [1e-8,1e-6,6.25e-6,1.25e-5]:
        r=math.exp(-s); x=1-r
        K=projected_number_map(E,r); U=projected_energy_map(E,r)
        check(f'CFL satisfied s={s}',x*L<1)
        check(f'CFL number identity all basis columns s={s}',np.max(abs(K-cfl_linear_map(E,r)))<1e-9)
        check(f'CFL energy identity all basis columns s={s}',np.max(abs(U-cfl_linear_map(E,r,True)))<1e-8)
        TN=expm(s*B); TE=expm(s*C)
        check(f'exact semigroup numeric number moment s={s}',max(abs(TN.sum(axis=0)-1))<3e-14)
        check(f'exact semigroup numeric energy moment s={s}',max(abs(w@TE-math.exp(-s)*w))<5e-13)
        for name,A,T,norm,ww in [('number',K,TN,2*L,None),('energy',U,TE,2*L-1,w)]:
            defect=column_norm(A-T,ww); bound=local_defect_bound(norm,s)
            check(f'all-state {name} operator defect s={s}',defect<=bound+2e-9,
                  {'operator_column_norm':defect,'real_arithmetic_bound':bound,'numeric_check_slack':2e-9})
    r=math.exp(-2e-5)
    check('non-CFL chosen step',(1-r)*L>1)
    linear=np.eye(len(E))+(1-r)*B
    check('non-CFL linear expression has negative column entry',linear.min()<0)
    check('non-CFL hat differs from linear expression',column_norm(projected_number_map(E,r)-linear)>0.1)
    rejected=False
    try:cfl_linear_map(E,r)
    except ValueError as e:rejected='non-CFL' in str(e)
    check('non-CFL linear API explicitly rejected',rejected)
    # Unprojected map retains transient lowest node before the second transport.
    M1=original_hat_map(E,math.exp(-6.25e-6));M2=original_hat_map(E,math.exp(-1.25e-5))
    check('unprojected lowest-node transient exists',M1[0,1]>0)
    check('projected original composition all full basis columns',column_norm(P@M2@M1-P@M2@P@M1@P)<2e-13)
    rng=np.random.default_rng(20261005)
    for i in range(8):
        v=rng.random(len(E)+2);v[-1]=.5*E[0]*v[-2]
        check(f'projected composition dense original cone {i}',max(abs(P@M2@M1@v-P@M2@P@M1@P@v))<1e-12)
    source=ROOT/'rust/rei_microphysics/src/paired_runtime.rs'
    extraction=json.loads((OUT/'prefix_extraction.json').read_text()); src=source.read_bytes()
    a,b=extraction['original_prefix_body_span_bytes']; module=(OUT/'original_transport_prefix.rs').read_bytes()
    body=src[a:b]
    check('prefix source body SHA and verbatim extraction',hashlib.sha256(body).hexdigest()==extraction['original_prefix_body_sha256'] and body in module)
    check('generated module identity',sha(OUT/'original_transport_prefix.rs')==extraction['generated_module_sha256'])
    check('prefix stops before source injection',b==src.index(b'    let (weights,wb)=source_weights(c,h,t1)?;',a))
    check('prefix body has no chemistry/source calls',b'source_weights(' not in body and b'primary_stage_' not in body)
    intent=json.loads((OUT.parent/'intent.json').read_text())
    for path,h in intent['inputs'].items():
        check('frozen input '+path,sha(ROOT/path)==h)
    result=json.loads((HERE/'RESULTS.json').read_text())
    native=json.loads((OUT/'native.json').read_text())
    check('native cases>=64',len(native['cases'])>=64)
    check('native all-state representative maximum normalized error',result['native_prefix_max_scaled_error']<=1e-9,result['native_prefix_worst_case'])
    check('native includes occupied lowest and guard and dense states',set(x['kind'] for x in native['cases'])==set(range(35)))
    check('native exact geometries and times',set(x['geometry'] for x in native['cases'])=={'BI','FLRW'} and set(x['t0'] for x in native['cases'])=={0,5e12})
    check('native execution count one',result['native_prefix_executions_total']==1)
    for path,h in result['included_source_sha256'].items():
        check('preserved compiled source '+path,sha(ROOT/path)==h)
    check('scientific ceiling',result['scientific_admission']=='HOLD' and result['continuum_time_error_certificate']=='NOT_ESTABLISHED' and result['coupled_stability_status']=='CONDITIONAL_NOT_CERTIFIED')
    check('no new coupled/full campaigns',result['new_coupled_trajectory_executions']==0 and result['new_full_campaign_executions']==0)
    passed=all(x['status']=='PASS' for x in checks)
    result['basis_operator_bounds_status']='PASS' if passed else 'FAIL'
    result['non_cfl_linear_formula_rejected']=rejected
    (HERE/'RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    validation={'status':'PASS' if passed else 'FAIL','scope':'candidate self-check; not independent review or scientific admission',
        'scientific_admission':'HOLD','check_count':len(checks),'checks':checks,
        'results_sha256':sha(HERE/'RESULTS.json'),'native_output_sha256':sha(OUT/'native.json'),
        'floating_point_rigorous_envelope':False}
    (HERE/'VALIDATION.json').write_text(json.dumps(validation,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':validation['status'],'checks':len(checks),'failed':[x['name'] for x in checks if x['status']=='FAIL']}))
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
