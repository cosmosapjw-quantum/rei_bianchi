"""Frozen one-redshift-tilt 7-point GLS using complete correlated BB13 C.

Statistical-only diagnostics with predeclared x=z-3.6. Does not profile EOS,
modify template rates, or provide physical inverse transfer/causal evidence.
"""
import math


def dot(a,b):
    if len(a)!=len(b):raise ValueError('dot dimensions')
    return math.fsum(x*y for x,y in zip(a,b))


def cholesky(C):
    n=len(C)
    if n<2 or any(len(row)!=n for row in C):raise ValueError('DIMENSION')
    if not all(isinstance(y,(float,int)) and math.isfinite(y) for row in C for y in row):
        raise ValueError('NONFINITE')
    if any(C[i][j]!=C[j][i] for i in range(n) for j in range(n)):
        raise ValueError('NONSYMMETRIC')
    L=[[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            residual=C[i][j]-math.fsum(L[i][k]*L[j][k] for k in range(j))
            if i==j:
                if residual<=0 or not math.isfinite(residual):raise ValueError('NOT_SPD')
                L[i][j]=math.sqrt(residual)
            else:L[i][j]=residual/L[j][j]
    return L


def solve(L,b):
    n=len(L)
    if len(b)!=n or not all(math.isfinite(x) for x in b):raise ValueError('RHS')
    y=[0.0]*n
    for i in range(n):
        y[i]=(b[i]-math.fsum(L[i][j]*y[j] for j in range(i)))/L[i][i]
    x=[0.0]*n
    for i in range(n-1,-1,-1):
        x[i]=(y[i]-math.fsum(L[j][i]*x[j] for j in range(i+1,n)))/L[i][i]
    return x


def fit(z,d,m,C,z0=3.6):
    n=len(z)
    if n!=7 or len(d)!=n or len(m)!=n or len(C)!=n:raise ValueError('FROZEN_SEVEN_POINTS')
    if any(not math.isfinite(float(x)) for x in (*z,*d,*m)) or z0!=3.6:
        raise ValueError('FROZEN_DATA_OR_CENTER')
    if len(set(z))!=n:raise ValueError('REDUNDANT_REDSHIFT')
    x=[zi-z0 for zi in z]
    ones=[1.0]*n
    r=[di-mi for di,mi in zip(d,m)]
    L=cholesky(C)
    W1=solve(L,ones);Wx=solve(L,x);Wr=solve(L,r)
    a=dot(ones,W1); b=dot(ones,Wx); c=dot(x,Wx)
    u=dot(ones,Wr);v=dot(x,Wr)
    det=a*c-b*b
    if a<=0 or det<=0 or not math.isfinite(det):raise ValueError('INFORMATION_NOT_SPD')
    beta=(c*u-b*v)/det
    kappa=(a*v-b*u)/det
    cov00=c/det;cov01=-b/det;cov11=a/det
    beta0=u/a;res0=[ri-beta0 for ri in r]
    Q0=dot(res0,solve(L,res0))
    res2=[ri-beta-kappa*xi for ri,xi in zip(r,x)]
    Q2=dot(res2,solve(L,res2))
    dq=Q0-Q2
    # Identity: extra one-column profiled quadratic.
    residual_slope_info=c-b*b/a
    extra= (v-b*u/a)**2/residual_slope_info
    if min(Q0,Q2)<-1e-12 or extra<0:raise ValueError('INVALID_QUADRATIC')
    return {'z':list(z),'x':x,'r':r,'beta':beta,'kappa':kappa,'covariance':[[cov00,cov01],[cov01,cov11]],
            'info':[[a,b],[b,c]],'det_information':det,'beta0':beta0,'Q0':Q0,'Q2':Q2,'DeltaQ':dq,
            'delta_from_slope_identity':extra,'dof0':6,'dof2':5,
            'residual0':res0,'residual2':res2,'fixed_EOS_theta':0,
            'model_scope':'CONDITIONAL_CORRELATED_STATISTICAL_ONLY'}
