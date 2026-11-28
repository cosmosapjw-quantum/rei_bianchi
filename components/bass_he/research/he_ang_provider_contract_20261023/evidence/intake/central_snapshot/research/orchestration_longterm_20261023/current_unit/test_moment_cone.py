"""One bounded fixture invocation. Retains all assertion and exception outcomes."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import copy
from fractions import Fraction as F
import json
from pathlib import Path
import resource
import sys
import time
start_wall, start_cpu = time.monotonic(), time.process_time()
from moment_cone import validate_energy_moments, PASS, FAIL, BOUNDARY
P = Path(__file__).parent

def diag(a,b,c): return [[a,0,0],[0,b,0],[0,0,c]]

def oracle(K,S,axis=None,D=None):
    """Independent explicit 3x3 principal minors, trace and P2 identity."""
    s = [[F(v) for v in r] for r in S]
    a,b,c = s[0]; d,e,f = s[1]; g,h,i = s[2]
    minors = [a,e,i,a*e-b*d,a*i-c*g,e*i-f*h,
              a*e*i+b*f*g+c*d*h-c*e*g-b*d*i-a*f*h]
    result = dict(trace=str(a+e+i), minors=[str(v) for v in minors],
                  trace_equal=a+e+i==F(K), psd=all(v>=0 for v in minors))
    if axis is not None:
        ax = [F(v) for v in axis]
        predicted = (3*sum(ax[j]*s[j][k]*ax[k] for j in range(3) for k in range(3))-F(K))/2
        result.update(D=str(predicted), D_equal=predicted==F(D))
    return result

fixtures = [
 ('isotropic',dict(K=3,S=diag(1,1,1),axis=[0,0,1],D=0),PASS),
 ('parallel',dict(K=3,S=diag(0,0,3),axis=[0,0,1],D=3),PASS),
 ('perpendicular',dict(K=3,S=diag(F(3,2),F(3,2),0),axis=[0,0,1],D=F(-3,2)),PASS),
 ('rational_rotation',dict(K=3,S=[[F(27,25),0,F(36,25)],[0,0,0],[F(36,25),0,F(48,25)]],axis=[F(3,5),0,F(4,5)],D=3),PASS),
 ('finite_mass_endpoint',dict(K=6,S=diag(0,0,6),E=10,I=2,Kp=2,axis=[0,0,1],D=6),PASS),
 ('heavy_limit_false_accept',dict(K=6,S=diag(0,0,6),E=10,I=2,Kp=2,axis=[0,0,1],D=7),FAIL),
 ('nonPSD_norm_not_sufficient',dict(K=3,S=diag(F(-1,10),F(31,20),F(31,20))),FAIL),
 ('zero_nonzero',dict(K=0,S=diag(1,0,0)),FAIL),
 ('zero_exact',dict(K=0,S=diag(0,0,0)),PASS),
 ('trace_error',dict(K=3,S=diag(1,1,2)),FAIL),
 ('negative_count',dict(K=3,S=diag(1,1,1),count=-2),FAIL),
 ('count_not_two',dict(K=3,S=diag(1,1,1),count=1),FAIL),
 ('negative_K',dict(K=-1,S=diag(0,0,0)),FAIL),
 ('mixed_units',dict(K=3,S=diag(1,1,1),units={'K':'J','S':'eV'}),FAIL),
 ('nonunit_axis',dict(K=3,S=diag(1,1,1),axis=[0,0,2],D=0),FAIL),
 ('nan',dict(K=float('nan'),S=diag(1,1,1)),FAIL),
 ('inf_matrix',dict(K=3,S=diag(1,float('inf'),1)),FAIL),
 ('complex',dict(K=3+0j,S=diag(1,1,1)),FAIL),
 ('bool',dict(K=True,S=diag(1,1,1)),FAIL),
 ('shape',dict(K=3,S=[[1,0],[0,1]]),FAIL),
 ('asymmetric',dict(K=3,S=[[1,F(1,10),0],[0,1,0],[0,0,1]]),FAIL),
 ('nearzero_float',dict(K=3.,S=diag(-1e-16,1.5,1.5)),BOUNDARY),
 ('float_negative_exact_input',dict(K=3.,S=diag(-.1,1.55,1.55),mode='exact_input'),FAIL),
 ('cancellation',dict(K=1.,S=diag(0.,0.,1.),E=1e16,I=1e16,Kp=0.),BOUNDARY),
 ('ledger_incompatible',dict(K=6,S=diag(0,0,6),E=10,I=2,Kp=3),FAIL),
 ('missing_ledger_operand',dict(K=3,S=diag(1,1,1),E=10),FAIL),
 ('source_error_retained',dict(K=3.,S=diag(1.,1.,1.),uncertainty={'K':.01,'S':.01}),BOUNDARY),
 ('negative_uncertainty',dict(K=3,S=diag(1,1,1),uncertainty={'K':-.01}),FAIL),
 ('float_represented_interior',dict(K=3.,S=diag(1.,1.,1.)),PASS),
 ('float_represented_boundary',dict(K=3.,S=diag(0.,0.,3.)),PASS),
 ('huge_finite_diagnostics',dict(K=2e200,S=diag(1e200,1e200,0.)),PASS),
 ('largest_finite_diagnostics',dict(K=1e308,S=diag(1e308,0.,0.)),PASS),
]
results=[]
for name,kwargs,expected in fixtures:
    kwargs.setdefault('units','fixture_energy')
    source_rounded={'nearzero_float','cancellation','source_error_retained','float_represented_interior','float_represented_boundary','huge_finite_diagnostics','largest_finite_diagnostics'}
    kwargs.setdefault('mode','source_rounded' if name in source_rounded else 'exact_input')
    before=copy.deepcopy(kwargs)
    result=dict(name=name,expected=expected,input_repr=repr(kwargs))
    try:
        record=validate_energy_moments(**kwargs)
        data=record.as_dict()
        result['diagnostic']=data
        # repr comparisons preserve NaN, raw invalid inputs and matrix values.
        checks=dict(decision=data['decision']==expected,
                    input_unchanged=repr(kwargs)==repr(before),
                    immutable_record=isinstance(record,str),
                    qualification=data.get('represented_input_only') is True and data['source_uncertainty'] in {'not_supplied','supplied','exact_mathematical_fixture'},
                    strict_json=json.loads(json.dumps(data,allow_nan=False))==data)
        if name in {'isotropic','parallel','perpendicular','rational_rotation','finite_mass_endpoint','nonPSD_norm_not_sufficient','zero_exact'}:
            exact=oracle(kwargs['K'],kwargs['S'],kwargs.get('axis'),kwargs.get('D'))
            result['independent_exact_oracle']=exact
            checks['oracle_trace']=exact['trace_equal']
            checks['oracle_psd']=exact['psd']==(name!='nonPSD_norm_not_sufficient')
            if 'D_equal' in exact: checks['oracle_D']=exact['D_equal']
        if name=='nearzero_float':
            checks['negative_eigenvalue_not_clipped']=data['min_eigenvalue']<0
        if name=='cancellation':
            checks['cancellation_flag']=data['cancellation_ratio']==2e16 and any('energy ledger' in v for v in data['boundaries'])
        result.update(checks=checks,passed=all(checks.values()))
    except Exception as e:
        result.update(exception=repr(e),passed=False)
    results.append(result)
# Formula-only illustrative plot; not a new solver run or source calibration.
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig,ax=plt.subplots(1,2,figsize=(9,3.6))
    k=np.linspace(0,8,100)
    ax[0].fill_between(k,-k/2,k,color='#b8d9e8',label='abstract necessary cone')
    ax[0].plot(k,k,color='#176a89');ax[0].plot(k,-k/2,color='#176a89')
    ax[0].scatter([3,3,3],[0,3,-1.5],color='#152d3b',zorder=4)
    ax[0].set(xlabel='electron kinetic energy K [fixture unit]',ylabel='quadrupole moment D [same unit]',title='Inclusive count-two angular moments')
    ax[0].legend(fontsize=8)
    kp=np.linspace(0,8,100)
    ax[1].fill_between(kp,-(8-kp)/2,8-kp,color='#cfe4c3')
    ax[1].axhline(8,color='gray',ls='--',label='heavy-target upper bound')
    ax[1].scatter([2],[6],color='#156c35',label='finite-mass endpoint')
    ax[1].scatter([2],[7],color='#b32a32',marker='x',s=60,label='D=7 rejected')
    ax[1].set(xlabel='outgoing proton Kp [fixture unit]',ylabel='D [same unit]',title='E=10, I=2; K=8-Kp')
    ax[1].legend(fontsize=8)
    fig.suptitle('X1 necessary moment gate; no eventwise momentum sufficiency',fontsize=10)
    fig.tight_layout();fig.savefig(P/'moment_cone.png',dpi=150);plt.close(fig)
    plot=dict(created=True,dependency=matplotlib.__version__)
except Exception as e:
    plot=dict(created=False,exception=repr(e))
wall,cpu=time.monotonic()-start_wall,time.process_time()-start_cpu
receipt=dict(command='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python test_moment_cone.py',
 invocation=1, max_workers=1, old_suite_replays=0, IVPs=0, benchmarks=0,
 wall_seconds=wall,cpu_seconds=cpu,budget=dict(cpu_limit=10,wall_limit=30,within=cpu<=10 and wall<=30),
 requested_model='lower-tier coding agent (controller routing)',observed_model='not exposed by execution runtime',
 results=results,plot=plot,all_passed=all(r['passed'] for r in results),
 dependencies=dict(python=sys.version,numpy=__import__('numpy').__version__),
 local_stage_R='mechanical observed facts only; independent Astra scientific review pending',
 local_stage_C='standalone checker/test receipt prepared; no provider/runtime admission')
(P/'raw_outcomes.json').write_text(json.dumps(receipt,indent=2,allow_nan=False))
print(json.dumps({k:v for k,v in receipt.items() if k!='results'},indent=2))
print(json.dumps([dict(name=r['name'],passed=r['passed'],decision=r.get('diagnostic',{}).get('decision'),exception=r.get('exception')) for r in results],indent=2))
sys.exit(0 if receipt['all_passed'] and receipt['budget']['within'] and plot['created'] else 1)
