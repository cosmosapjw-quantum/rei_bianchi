"""Independent Decimal80 linear equations: no production import or Cholesky."""
from decimal import Decimal,localcontext

def dec(x):
    if isinstance(x,float):return Decimal.from_float(x)
    return Decimal(x)

def solve(M,b):
    a=[list(map(dec,row))+[dec(rhs)] for row,rhs in zip(M,b)]
    n=len(a)
    for k in range(n):
        p=max(range(k,n),key=lambda i:abs(a[i][k]))
        if a[p][k]==0:raise ValueError('SINGULAR')
        a[k],a[p]=a[p],a[k]
        pivot=a[k][k]
        for j in range(k,n+1):a[k][j]/=pivot
        for i in range(n):
            if i==k:continue
            w=a[i][k]
            for j in range(k,n+1):a[i][j]-=w*a[k][j]
    return [a[i][n] for i in range(n)]

def dot(a,b):return sum((x*y for x,y in zip(a,b)),Decimal(0))

def fit(z,d,m,C,z0=3.6):
    with localcontext() as ctx:
        ctx.prec=80
        n=len(z);Z=dec(z0)
        x=[dec(v)-Z for v in z]
        r=[dec(v)-dec(w) for v,w in zip(d,m)]
        one=[Decimal(1)]*n
        w1=solve(C,one);wx=solve(C,x);wr=solve(C,r)
        A=dot(one,w1);B=dot(one,wx);D=dot(x,wx)
        U=dot(one,wr);V=dot(x,wr)
        det=A*D-B*B
        theta=solve([[A,B],[B,D]],[U,V]); beta,kappa=theta
        centered=[ri-beta-kappa*xi for ri,xi in zip(r,x)]
        Q2=dot(centered,solve(C,centered))
        beta0=U/A; q0res=[ri-beta0 for ri in r]
        Q0=dot(q0res,solve(C,q0res))
        cov=[[D/det,-B/det],[-B/det,A/det]]
        return dict(beta=str(+beta),kappa=str(+kappa),Q0=str(+Q0),Q2=str(+Q2),DeltaQ=str(+(Q0-Q2)),
                    cov=[[str(+v) for v in row] for row in cov],precision_digits=ctx.prec)
