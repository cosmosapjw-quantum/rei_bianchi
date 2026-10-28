"""Fixed-template statistical shape diagnostics; standard-library binary64 only."""
import math


def dot(x,y): return math.fsum(a*b for a,b in zip(x,y))
def validate(C,r):
    n=len(r)
    if n<2 or len(C)!=n or any(len(row)!=n for row in C):raise ValueError('DIMENSIONS')
    if not all(math.isfinite(x) for x in r) or not all(math.isfinite(x) for row in C for x in row):raise ValueError('NONFINITE')
    if any(C[i][j]!=C[j][i] for i in range(n) for j in range(n)):raise ValueError('NONSYMMETRIC')

def cholesky(C):
    n=len(C);L=[[0.]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            s=C[i][j]-math.fsum(L[i][k]*L[j][k] for k in range(j))
            if i==j:
                if not math.isfinite(s) or s<=0:raise ValueError('NOT_SPD')
                L[i][j]=math.sqrt(s)
            else:L[i][j]=s/L[j][j]
    return L

def solve(L,v):
    n=len(v);y=[0.]*n;x=[0.]*n
    for i in range(n):y[i]=(v[i]-math.fsum(L[i][k]*y[k] for k in range(i)))/L[i][i]
    for i in reversed(range(n)):x[i]=(y[i]-math.fsum(L[k][i]*x[k] for k in range(i+1,n)))/L[i][i]
    return x

def diagnostic(C,r):
    validate(C,r);n=len(r);L=cholesky(C);one=[1.]*n
    t=solve(L,one);h=solve(L,r);den=dot(one,t);beta=dot(one,h)/den
    res=[x-beta for x in r];Q=dot(res,solve(L,res));loo=[]
    for i in range(n):
        J=[j for j in range(n) if j!=i];B=[[C[j][k] for k in J] for j in J];cc=[C[j][i] for j in J];rj=[r[j] for j in J];u=[1.]*(n-1);lb=cholesky(B)
        t=solve(lb,u);h=solve(lb,rj);g=solve(lb,cc);denj=dot(u,t);bm=dot(u,h)/denj;a=1-dot(cc,t);s0=C[i][i]-dot(cc,g)
        if s0<=0 or denj<=0:raise ValueError('NONPOSITIVE_CONDITIONAL_VARIANCE')
        pred=dot(cc,h)+a*bm;e=r[i]-pred;s=s0+a*a/denj
        if not math.isfinite(s) or s<=0:raise ValueError('NONPOSITIVE_PREDICTIVE_VARIANCE')
        resj=[x-bm for x in rj];deleted=dot(resj,solve(lb,resj))
        loo.append({'index':i,'e':e,'s':s,'Z':e/math.sqrt(s),'beta_minus':bm,'variance_beta_minus':1/denj,'predicted_residual':pred,'deleted_chi2':deleted,'innovation_chi2':e*e/s,'Q_minus_deleted':Q-deleted,'beta_full_minus_beta_minus':beta-bm,'block_beta_shift':a*e/(denj*s0+a*a),'a':a,'s0':s0})
    D=[[-1. if k==j else 1. if k==j+1 else 0. for k in range(n)] for j in range(n-1)]
    delta=[r[j+1]-r[j] for j in range(n-1)]
    S=[[C[i+1][j+1]-C[i+1][j]-C[i][j+1]+C[i][j] for j in range(n-1)] for i in range(n-1)]
    ls=cholesky(S);cq=dot(delta,solve(ls,delta))
    return {'beta_full':beta,'variance_beta_full':1/den,'Q':Q,'D':D,'Delta':delta,'S':S,'contrast_Q':cq,'leave_one_out':loo,'covariance_cholesky_pivots':[L[i][i]**2 for i in range(n)],'contrast_cholesky_pivots':[ls[i][i]**2 for i in range(n-1)]}
