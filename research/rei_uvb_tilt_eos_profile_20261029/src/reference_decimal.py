"""Independent Decimal80 Gaussian elimination on original represented binary64 values.

Does not import the production Cholesky code.
"""
from decimal import Decimal,localcontext

def dec(a):return Decimal.from_float(a) if isinstance(a,float) else Decimal(a)
def solve(M,vec):
    n=len(vec);aug=[[dec(t) for t in row]+[dec(vec[i])] for i,row in enumerate(M)]
    for j in range(n):
        pivot=max(range(j,n),key=lambda i:abs(aug[i][j]))
        if aug[pivot][j]==0:raise ValueError('SINGULAR')
        aug[j],aug[pivot]=aug[pivot],aug[j]
        t=aug[j][j]
        for k in range(j,n+1):aug[j][k]/=t
        for i in range(n):
            if i==j:continue
            t=aug[i][j]
            for k in range(j,n+1):aug[i][k]-=t*aug[j][k]
    return [aug[i][-1] for i in range(n)]
def dot(x,y):return sum((a*b for a,b in zip(x,y)),Decimal(0))
def fit(z,d,m,C,v):
    with localcontext() as ctx:
        ctx.prec=80
        N=len(z);z=list(map(dec,z));d=list(map(dec,d));m=list(map(dec,m));v=list(map(dec,v));C=[list(map(dec,row)) for row in C]
        one=[Decimal(1)]*N;x=[zz-dec(3.6) for zz in z];r=[di-mi for di,mi in zip(d,m)]
        w1,wx,wr,wv=[solve(C,s) for s in (one,x,r,v)]
        a,b,c=dot(one,w1),dot(one,wx),dot(x,wx)
        u,zz,uu,vv=dot(one,wr),dot(x,wr),dot(one,wv),dot(x,wv)
        g=[[a,b],[b,c]]
        p0=solve(g,[u,zz]);pv=solve(g,[uu,vv]);co=lambda t:[p0[i]+t*pv[i] for i in range(2)]
        def q2(th):
            y=[r[i]+th*v[i] for i in range(N)];p=co(th);res=[y[i]-p[0]-p[1]*x[i] for i in range(N)]
            beta0=dot(one,solve(C,y))/a;res0=[yi-beta0 for yi in y]
            return dot(res,solve(C,res)),dot(res0,solve(C,res0)),p
        e0=[r[i]-p0[0]-p0[1]*x[i] for i in range(N)];eV=[v[i]-pv[0]-pv[1]*x[i] for i in range(N)]
        curvature=dot(eV,solve(C,eV));lin=dot(e0,solve(C,eV))
        thstar=max(Decimal(-1),min(Decimal(1),-lin/curvature))
        res={str(t):[str(q) for q in q2(t)[:2]]+[list(map(str,q2(t)[2]))] for t in (Decimal(-1),Decimal(0),Decimal(1),thstar)}
        cov=solve(g,[Decimal(1),Decimal(0)]),solve(g,[Decimal(0),Decimal(1)])
        return dict(beta0=str(p0[0]),kappa0=str(p0[1]),betader=str(pv[0]),kappader=str(pv[1]),
                    theta_star=str(thstar),theta_unconstrained=str(-lin/curvature),
                    curvature=str(curvature),lin=str(lin),cov=[[str(cov[0][0]),str(cov[1][0])],[str(cov[0][1]),str(cov[1][1])]],profile_points=res,precision=80)
