#!/usr/bin/env python3
"""Exact-rational, source-bounded EOS response audit of a saved REI UVB tilt.

No network/IVP/new Puchwein rate calculation. Input covariance is the literal
binary64 image of a source projection, not physical observational uncertainty.
This is an audit supplement; it does not perform the required independent C9.
"""
import json,hashlib,sys,os,resource,platform
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'source/FROZEN_INPUT.json'
EXPECTED_SOURCE_SHA='3cd87261e719751228f463c1d5ba71162d0eb4e33620a12176fa56429a6902bf'
EOS_V=('0.084','0.086','0.083','0.077','0.071','0.066','0.064')

# Fraction.from_float is exact for JSON-decoded binary64 source values.
def f(x):
    if isinstance(x,float): return F.from_float(x)
    if isinstance(x,int): return F(x)
    return F(x)

def dot(v,w):
    return sum((a*b for a,b in zip(v,w)),F(0))

def solve(M,y):
    n=len(y)
    if any(len(row)!=n for row in M): raise ValueError('square matrix only')
    a=[list(map(f,row))+[f(y[i])] for i,row in enumerate(M)]
    for k in range(n):
        sel=next((j for j in range(k,n) if a[j][k]),None)
        if sel is None:raise ValueError('singular system')
        a[k],a[sel]=a[sel],a[k]
        inv=F(1)/a[k][k]
        for j in range(k,n+1):a[k][j]*=inv
        for i in range(n):
            if i==k:continue
            coef=a[i][k]
            for j in range(k,n+1):a[i][j]-=coef*a[k][j]
    return [a[i][-1] for i in range(n)]

def representation(q,digits=56):
    with localcontext() as c:
        c.prec=digits
        return str(+(Decimal(q.numerator)/Decimal(q.denominator)))

def calculate():
    raw=SRC.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
    if sha!=EXPECTED_SOURCE_SHA:raise RuntimeError('frozen source projection SHA changed: '+sha)
    old=json.loads(raw)
    if old['unit']!='REI_UVB_ONE_TILT_IDENTIFIABILITY_NEXT' or old['fixed_EOS_theta']!=0:
        raise ValueError('wrong original frozen subject')
    z=[f(i) for i in old['z']];x=[i-f(3.6) for i in z]
    d=[f(i) for i in old['observed_dex']];m=[f(i) for i in old['template_dex']]
    C=[[f(t) for t in row] for row in old['statistical_covariance_dex2']]
    r=[a-b for a,b in zip(d,m)]
    # EOS response from the original BB13 2013 gamma_TDR source; theta=(gamma-1.4)/0.2.
    # These seven decimal literals are source-reported physical-nuisance response vectors.
    v=[f(s) for s in EOS_V]
    n=len(z);one=[F(1)]*n
    if n!=7 or z[0]!=f(2.4) or z[-1]!=f(4.75) or any(z[i]>=z[i+1] for i in range(n-1)):
        raise ValueError('outside frozen seven observed points')
    for i in range(n):
        if any(C[i][j]!=C[j][i] for j in range(n)):raise ValueError('covariance not identical symmetric real')
    w1=solve(C,one);wx=solve(C,x);wr=solve(C,r);wv=solve(C,v)
    A=dot(one,w1);B=dot(one,wx);D=dot(x,wx)
    M=[[A,B],[B,D]]
    determinant=A*D-B*B
    if A<=0 or determinant<=0:raise AssertionError('information not SPD')
    theta0=solve(M,[dot(one,wr),dot(x,wr)])
    sens=solve(M,[dot(one,wv),dot(x,wv)])
    rx=[r[i]-theta0[0]-theta0[1]*x[i] for i in range(n)]
    vx=[v[i]-sens[0]-sens[1]*x[i] for i in range(n)]
    wx_r=solve(C,rx);wx_v=solve(C,vx)
    Q0=dot(rx,wx_r)
    lin=2*dot(rx,wx_v)
    quad=dot(vx,wx_v)
    if Q0<0 or quad<0:raise AssertionError('PSD violation')
    beta0=dot(one,wr)/A
    full0=[r[i]-beta0 for i in range(n)]
    Qamplitude=dot(full0,solve(C,full0))
    slopeGain=(dot(x,wr)-B*dot(one,wr)/A)**2/(D-B*B/A)
    if Qamplitude-Q0!=slopeGain:raise AssertionError('exact rational nested loss identity failed')
    # Exact affine movement of GLS coefficients and quadratic residual under EOS theta.
    eps=[F(-1),F(0),F(1)]
    curves=[]
    for t in eps:
        bs=[theta0[j]+t*sens[j] for j in (0,1)]
        re=[r[i]+t*v[i]-bs[0]-bs[1]*x[i] for i in range(n)]
        direct=dot(re,solve(C,re))
        polynomial=Q0+t*lin+t*t*quad
        if direct!=polynomial:raise AssertionError('exact polynomial response failed')
        curves.append({'theta_EOS':int(t),'gamma_TDR':representation(F(14,10)+t*F(2,10),20),
                       'beta_dex':representation(bs[0]),'kappa_dex_per_z':representation(bs[1]),
                       'residual_chi2':representation(direct)})
    if not (theta0[1]-sens[1]>0 and theta0[1]+sens[1]>0):raise AssertionError('restricted slope changes sign')
    if not (lin-2*quad<0 and lin+2*quad<0):raise AssertionError('restricted Q not monotone')
    # Comparison against the previous, separately authored, saved beta/kappa/Q numbers;
    # same source and host, not a different-agent review.
    expected={'beta':-0.045918743031444754,'kappa':0.06866173948059069,'Q0':19.381736839571925,'Q2':11.34783520897078,
              'gain':8.033901630601145}
    now={'beta':theta0[0],'kappa':theta0[1],'Q0':Qamplitude,'Q2':Q0,'gain':slopeGain}
    comparisons=[]
    for key,val in expected.items():
        err=abs(float(now[key])-val)
        accepted=err<=1e-12+1e-10*abs(val)
        comparisons.append({'key':key,'saved_float':val,'exact_rational_real_decimal':representation(now[key]),
                            'difference_as_float':err,'passed':accepted})
    if not all(i['passed'] for i in comparisons):raise AssertionError('previous source mismatch')
    # Constant redshift error shift cannot change kappa (exact identity).
    shifted=[ri+F(37,100) for ri in r]
    wc=solve(C,shifted)
    t2=solve(M,[dot(one,wc),dot(x,wc)])
    if t2[1]!=theta0[1] or t2[0]!=theta0[0]+F(37,100):
        raise AssertionError('common-amplitude equivariance failed')
    with localcontext() as c:
        c.prec=60
        root=-F(lin,2*quad) if quad else None
    return {'schema':'REI_UVB_EOS_SENSITIVITY_EXACT_RATIONAL_AUDIT_V1',
            'status':'MATHEMATICAL_AND_EXECUTION_CHECKED_NO_INDEPENDENT_REVIEW',
            'parent_source_projection_SHA256':sha,
            'full_input_original_git_blobs':{'BB13':old['source_observation_git_blob'],
                'saved_Puchwein_points':old['source_model_git_blob'],
                'full_Puchwein_table':old['source_template_git_blob']},
            'input_EOS_source_literal':{'theta_definition':'(gamma_TDR-1.4)/0.2',
                'v_response_dex':list(EOS_V),'not_in_frozen_fixed_EOS_primary_model':True},
            'exact_binary64_source_model':True,
            'model':'d(theta)=d+theta*v, r(theta)=d(theta)-m; beta,kappa fitted with fixed C and X=[1,z-3.6]',
            'coefficients_theta0':{'beta':representation(theta0[0]),'kappa':representation(theta0[1])},
            'coefficient_direction_per_theta':{'beta':representation(sens[0]),'kappa':representation(sens[1])},
            'chi2_polynomial':{'constant':representation(Q0),'linear':representation(lin),'quadratic':representation(quad)},
            'restricted_theta':[-1,1], 'endpoints':curves,
            'stationary_Q_theta':representation(-lin/(2*quad)) if quad else None,
            'restricted_kappa_positive':True,
            'restricted_Q2_monotonically_decreasing':True,
            'nested_Q_amplitude_only_theta0':representation(Qamplitude),
            'nested_improvement_theta0':representation(slopeGain),
            'comparison_to_previous_saved_numeric':comparisons,
            'exact_tests':{'SPD_info_minor':True,'exact_nested_gain':True,'exact_EOS_affine_response':3,
                           'constant_amplitude_equivariance':True,'restricted_sign_positivity':True,
                           'bounded_Q_monotonicity':True},
            'claim_holds':['Not an independent Astra-tier native R6/C9',
                           'Not a new cosmological Bianchi global tilt',
                           'No Jeans/thermal/source-model systematic posterior',
                           'Not validation on held-out observations',
                           'No chemical/thermal/radiation source-coupling certification'],
            'node_progress':{'parent_one_tilt':'18/20','R6':'PENDING_DISTINCT_AUTHOR_REVIEW',
                             'C9':'PENDING_DISTINCT_AUTHOR_REVIEW','original_working':'33/88',
                             'central_last_observed':'28/88','delta':0},
            'native_subagent':'NOT_EXPOSED', 'IVPs':0}

if __name__=='__main__':
    d=calculate()
    json.dump(d,sys.stdout,indent=2,ensure_ascii=False)
    sys.stdout.write('\n')
