#!/usr/bin/env python3
"""Actually execute lightweight independent time-quadrature controls."""
import math,json,csv,platform
from pathlib import Path
import numpy as np
from scipy.integrate import quad,solve_ivp
from birth_reference import linear_history,nonlinear_history
ROOT=Path(__file__).resolve().parent;E=ROOT/'evidence';E.mkdir(exist_ok=True)
rows=[]
for k in (0.,2.,20.):
    for rule in ('midpoint','gl2','common_halves'):
        last=None
        truthN=quad(lambda x:(1+.3*x)*math.exp(-k*(1-x)),0,1,epsabs=1e-14)[0]
        truthU=quad(lambda x:80*(1+.3*x)*math.exp(-(k+1)*(1-x)),0,1,epsabs=1e-12)[0]
        for n in (2,4,8,16,32,64):
            r=linear_history(rule,n,1,k,lambda x:1+.3*x);err=abs(r['U']-truthU)
            p=math.log2(last/err) if last and err>1e-12 else None
            rows.append(dict(case=f'linear_k{k}',rule=rule,steps=n,error_N=abs(r['N']-truthN),error_U_eV_H=err,observed_p_U=p,**r))
            last=err
nonlinear=[]
for label,k in [('affine',lambda x:1+.2*x),('curved',lambda x:1+.2*x+.3*x*x)]:
    def rhs(x,y):
        q=k(x)*y[0]*y[1];return [.3+.1*x-q,-q,q]
    truth=solve_ivp(rhs,(0,1),[.2,1,0],method='Radau',rtol=1e-12,atol=1e-14).y[:,-1]
    for rule in ('midpoint','gl2'):
        last=None
        for n in (8,16,32,64):
            r=nonlinear_history(rule,n,1,lambda x:.3+.1*x,k)
            err=max(abs(np.array([r['N'],r['M'],r['events']])-truth))
            nonlinear.append(dict(case=label,rule=rule,steps=n,error=float(err),observed_p=math.log2(last/err) if last and err else None,**r))
            last=err
stiff=[]
for n in (1,2,8,32,128,512):
    r=linear_history('gl2',n,1,1000,lambda x:1.)
    stiff.append({'N':n,'tau_segment_macro':1000/n,'survivors':r['N'],'relative_error':abs(r['N']-.001)/.001})
result={'schema':'rei.v14.manufactured.1','actual_python':platform.python_version(),'linear_rows':rows,'nonlinear_rows':nonlinear,'stiff_rows':stiff,
        'native_Rust_compile':'NOT_RUN','linear_p4_does_not_certify_native_order':True,
        'special_affine_order':'Observed ~4 for this special nonlinear test; not a general nonlinear order claim',
        'new_lightweight_rows':len(rows)+len(nonlinear)+len(stiff)}
(E/'REFERENCE_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
for r in rows:
    if r['steps']==64 and r['case']=='linear_k2.0':print('LINEAR',r['rule'],r['error_U_eV_H'],r['observed_p_U'])
for r in nonlinear:
    if r['steps']==64:print('NONLINEAR',r['case'],r['rule'],r['error'],r['observed_p'])
print('STIFF',stiff)
print('ROWS',result['new_lightweight_rows'])
