"""Exact-rational GLS image of published BB13 per-bin EOS/Jeans correction boxes.

Conditional deterministic outer-support study, not a marginalized uncertainty or
physical UVB source posterior.  No rate callback, ODE, spectrum or network.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'source/FROZEN_BB13_SUPPORT_INPUT.json'
SOURCE_EXPECTED='13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b'

def exact(x):
    if isinstance(x,bool):raise TypeError('bool not a numeric field')
    if isinstance(x,int):return F(x)
    return F.from_float(float(x))

def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))

def solve(M,y):
    """Exact Gaussian elimination with partial row pivots and exact divisions."""
    n=len(y);a=[list(row)+[right] for row,right in zip(M,y)]
    assert len(a)==n and all(len(row)==n+1 for row in a)
    for k in range(n):
        pivot=max(range(k,n),key=lambda i:abs(a[i][k]))
        if a[pivot][k]==0:raise ValueError('singular exact matrix')
        a[k],a[pivot]=a[pivot],a[k]
        for i in range(k+1,n):
            q=a[i][k]/a[k][k]
            for j in range(k+1,n+1):a[i][j]-=q*a[k][j]
            a[i][k]=F(0)
    out=[F(0)]*n
    for i in range(n-1,-1,-1):out[i]=(a[i][n]-dot(a[i][i+1:n],out[i+1:]))/a[i][i]
    return out

def ldl_positive(C):
    """Positive exact LDL pivots witness SPD of pinned represented-real covariance."""
    n=len(C)
    if any(C[i][j]!=C[j][i] for i in range(n) for j in range(n)):
        raise ValueError('not symmetric')
    L=[[F(int(i==j)) for j in range(n)] for i in range(n)]
    piv=[]
    for k in range(n):
        d=C[k][k]-sum((L[k][s]*L[k][s]*piv[s] for s in range(k)),F(0))
        if d<=0:raise ValueError('C not SPD')
        piv.append(d)
        for i in range(k+1,n):
            L[i][k]=(C[i][k]-sum((L[i][s]*L[k][s]*piv[s] for s in range(k)),F(0)))/d
    return piv

def choose_endpoint(a,low,high,maximize):
    return high if (a>0)==maximize else low

def compute():
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_EXPECTED:raise RuntimeError('SOURCE_SHA_CHANGE')
    data=json.loads(raw)
    z=list(map(exact,data['z']));n=len(z)
    assert n==7 and data['eos_theta_bounds']==[-1,1]
    y=list(map(exact,data['observed_dex'])); m=list(map(exact,data['template_dex']))
    v=list(map(exact,data['eos_response_dex']));lo=list(map(exact,data['jeans_smoothing_lower_dex']));hi=list(map(exact,data['jeans_smoothing_upper_dex']))
    assert all(l<=h for l,h in zip(lo,hi))
    C=[list(map(exact,row)) for row in data['covariance_dex_squared']]
    assert all(len(row)==n for row in C)
    piv=ldl_positive(C)
    x=[a-exact(3.6) for a in z];one=[F(1)]*n
    invC1=solve(C,one);invCx=solve(C,x)
    info=[[dot(one,invC1),dot(one,invCx)],[dot(x,invC1),dot(x,invCx)]]
    det=info[0][0]*info[1][1]-info[0][1]*info[1][0]
    if det<=0:raise ValueError('rank-deficient GLS design')
    def lin(b0,b1):
        return [(info[1][1]*b0-info[0][1]*b1)/det,
                (-info[1][0]*b0+info[0][0]*b1)/det]
    A=[[],[]]
    for a,b in zip(invC1,invCx):
        q=lin(a,b);A[0].append(q[0]);A[1].append(q[1])
    assert dot(A[0],one)==1 and dot(A[1],one)==0
    assert dot(A[0],x)==0 and dot(A[1],x)==1
    r=[a-b for a,b in zip(y,m)]
    t0=[dot(A[i],r) for i in (0,1)]
    dv=[dot(A[i],v) for i in (0,1)]
    jc=[(l+h)/2 for l,h in zip(lo,hi)]
    jh=[(h-l)/2 for l,h in zip(lo,hi)]
    center=[t0[i]+dot(A[i],jc) for i in (0,1)]
    half=[abs(dv[i])+sum(abs(a)*w for a,w in zip(A[i],jh)) for i in (0,1)]
    bmin,bmax=center[0]-half[0],center[0]+half[0]
    kmin,kmax=center[1]-half[1],center[1]+half[1]
    def evalparams(theta,j):
        return [t0[i]+dv[i]*theta+dot(A[i],j) for i in (0,1)]
    def witness(i,maximum):
        theta=F(1 if ((dv[i]>0)==maximum) else -1)
        j=[choose_endpoint(a,l,h,maximum) for a,l,h in zip(A[i],lo,hi)]
        return theta,j,evalparams(theta,j)[i]
    wmin=witness(1,False);wmax=witness(1,True)
    assert wmin[2]==kmin and wmax[2]==kmax
    # Exhaustively enumerate all 2^8 outer-box corners without new source or IVP.
    vertices=[]
    for theta in (F(-1),F(1)):
        for bits in product((0,1),repeat=7):
            j=[hi[i] if bits[i] else lo[i] for i in range(n)]
            vertices.append((theta,bits,evalparams(theta,j)))
    assert len(vertices)==256
    assert min(row[2][0] for row in vertices)==bmin
    assert max(row[2][0] for row in vertices)==bmax
    assert min(row[2][1] for row in vertices)==kmin
    assert max(row[2][1] for row in vertices)==kmax
    # Every nested amplitude-only vs 2-parameter slope improvement is >=0 under SPD.
    W=[solve(C,[F(int(i==k)) for i in range(n)]) for k in range(n)]
    def quadratic(q):
        t=[dot(column,q) for column in W]
        return dot(q,t)
    beta0weight=[w/info[0][0] for w in invC1]
    for theta,bits,_ in vertices:
        j=[hi[i] if bits[i] else lo[i] for i in range(n)]
        q=[r[i]+theta*v[i]+j[i] for i in range(n)]
        beta0=dot(beta0weight,q)
        q0=quadratic([u-beta0 for u in q])
        param=evalparams(theta,j)
        q2=quadratic([u-param[0]-param[1]*x[i] for i,u in enumerate(q)])
        assert q0>=q2 and q2>=0
    def s(a):return format(float(a),'.17g')
    def e(a):return f'{a.numerator}/{a.denominator}'
    def tx(i,lower_or_upper):
        theta,j,_=witness(i,lower_or_upper)
        return {'theta':int(theta),'gamma_TDR':float(F(7,5)+theta/F(5)),
                'j':list(map(s,j)),'value':s(evalparams(theta,j)[i])}
    report={
      'schema':'REI_UVB_EOS_JEANS_EXACT_SUPPORT_V1','success':True,
      'source_sha256':hashlib.sha256(raw).hexdigest(),
      'exact_arithmetic':'Fraction.from_float(binary64 source images)',
      'n_gls':7,'n_nuisance':8,'corner_count':len(vertices),
      'reused_amplitude_tilt':{'beta0':s(t0[0]),'kappa0':s(t0[1])},
      'eos_direction_dtheta':{'dbeta':s(dv[0]),'dkappa':s(dv[1])},
      'info_determinant_positive':det>0,'covariance_LDL_exact_pivots_positive':len(piv),
      'projection_checks':{'A1_one':True,'Ak_one':True,'A1_x':True,'Ak_x':True},
      'GLS_parameter_covariance_conditional':{'beta_sigma':s((info[1][1]/det)**F(1,2)) if False else None,'var_kappa':s(info[0][0]/det)},
      'jeans_only_kappa':{'min':s(t0[1]+dot(A[1],jc)-sum(abs(a)*w for a,w in zip(A[1],jh))),
                          'max':s(t0[1]+dot(A[1],jc)+sum(abs(a)*w for a,w in zip(A[1],jh)))},
      'nuisance_support':{
       'beta_min':s(bmin),'beta_max':s(bmax),
       'kappa_min':s(kmin),'kappa_max':s(kmax),
       'kappa_zero_excluded_under_this_box':kmin>0,
       'kappa_min_exact_sha256':hashlib.sha256(e(kmin).encode()).hexdigest(),
       'kappa_max_exact_sha256':hashlib.sha256(e(kmax).encode()).hexdigest(),
       'kappa_center':s(center[1]),'kappa_halfwidth':s(half[1]),
       'kappa_central_Jeans_center_shift':s(dot(A[1],jc)),
       'kappa_Jeans_halfwidth':s(sum(abs(a)*w for a,w in zip(A[1],jh))),
       'kappa_EOS_halfwidth':s(abs(dv[1])),
       'kappa_min_witness':tx(1,False),'kappa_max_witness':tx(1,True),
       'beta_min_witness':tx(0,False),'beta_max_witness':tx(0,True),
       'kappa_weights_d_perbin':list(map(s,A[1]))},
      'controls':{'exact_C_SPD':True,'rank2':True,'exact_affine_projection':True,
                  '256_corner_support_extrema':True,'all_256_nested_chi2':True},
      'claim':'CONDITIONAL_DETERMINISTIC_OUTER_BOX_NOT_STATISTICAL_INDEPENDENCE',
      'physical_F4':'PARTIAL','L4_ready':False,'actual_REI_T':None,'physical_radii':None,
      'new_IVP':0,'original_DAG_working':'33/88','central_last_observed':'28/88',
      'native_independent_reviewer':'NOT_RUN'}
    return report

if __name__=='__main__':
    obj=compute();p=ROOT/'results/EXACT_SUPPORT.json';p.write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps({'support':obj['nuisance_support'],'controls':obj['controls']},indent=2))
