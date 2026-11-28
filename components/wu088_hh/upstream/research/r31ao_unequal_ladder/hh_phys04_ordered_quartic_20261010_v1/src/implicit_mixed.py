"""Regular reduced-BE equality sensitivities; no nonlinear root solver.

The caller supplies the endpoint candidate and the incoming state/derivative
family. This arithmetic reference does not issue a native root certificate.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as Q


@dataclass(frozen=True)
class D2:
    v: object
    a: object = 0
    b: object = 0
    ab: object = 0

    @staticmethod
    def coerce(x):
        return x if isinstance(x, D2) else D2(x)

    def __add__(self, other):
        y=self.coerce(other)
        return D2(self.v+y.v,self.a+y.a,self.b+y.b,self.ab+y.ab)

    __radd__=__add__

    def __neg__(self):
        return D2(-self.v,-self.a,-self.b,-self.ab)

    def __sub__(self, other):
        return self+(-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other)-self

    def __mul__(self, other):
        y=self.coerce(other)
        return D2(self.v*y.v,self.a*y.v+self.v*y.a,
                  self.b*y.v+self.v*y.b,
                  self.ab*y.v+self.a*y.b+self.b*y.a+self.v*y.ab)

    __rmul__=__mul__

    def unary(self, value, first, second):
        return D2(value,first*self.a,first*self.b,
                  first*self.ab+second*self.a*self.b)

    def reciprocal(self):
        if self.v==0:
            raise ZeroDivisionError("zero primal denominator")
        return self.unary(1/self.v,-1/(self.v*self.v),2/(self.v**3))

    def __truediv__(self, other):
        return self*self.coerce(other).reciprocal()

    def __rtruediv__(self, other):
        return self.coerce(other)*self.reciprocal()

    def __pow__(self, power):
        if not isinstance(power,int):
            raise TypeError("use unary(value, first, second) for noninteger powers")
        if power<0:
            return (self.reciprocal())**(-power)
        result=D2(1)
        for _ in range(power):
            result=result*self
        return result


def strip(x):
    return D2.coerce(x).v


def solve_linear(matrix, rhs):
    """Exact Gaussian elimination for Fraction; generic scalar reference."""
    n=len(rhs)
    if len(matrix)!=n or any(len(row)!=n for row in matrix):
        raise ValueError("linear shape")
    a=[list(row)+[rhs[i]] for i,row in enumerate(matrix)]
    for k in range(n):
        pivot=next((i for i in range(k,n) if a[i][k]!=0),None)
        if pivot is None:
            raise ValueError("singular equality Jacobian")
        if pivot!=k:
            a[k],a[pivot]=a[pivot],a[k]
        denom=a[k][k]
        a[k]=[x/denom for x in a[k]]
        for i in range(n):
            if i==k:
                continue
            factor=a[i][k]
            a[i]=[x-factor*y for x,y in zip(a[i],a[k])]
    return [row[-1] for row in a]


def reduced_photons(gas, incoming, dt, density, speed_c, f_he, sigma):
    x,y1,y2,_=gas
    low=[1-x,f_he*(1-y1-y2),f_he*y1]
    result=[]
    for stock,sig in zip(incoming,sigma):
        opacity=sum((speed_c*density*l*s for l,s in zip(low,sig)),D2(0))
        denominator=1+dt*opacity
        if strip(denominator)<=0:
            raise ValueError("nonpositive BE photon denominator")
        result.append(stock/denominator)
    return result


def make_reduced_residual(dt,density,speed_c,f_he,energies,sigma,chi,
                          nonphoto,hh_rate):
    """F callbacks preserve all gas chemistry/heat; lambda scales HH only.

    residual(gas, old_gas, incoming_photons, lambda) returns gas residual.
    Source b enters through incoming photons/old gas derivatives.
    """
    if not (len(energies)==len(sigma)) or any(len(s)!=3 for s in sigma):
        raise ValueError("packet layout")
    if f_he<=0 or dt<=0 or density<=0 or speed_c<=0:
        raise ValueError("positive physical scales required")
    if len(chi)!=3:
        raise ValueError("threshold layout")
    for e,row in zip(energies,sigma):
        if any(s<0 for s in row) or any(s>0 and e<cut for s,cut in zip(row,chi)):
            raise ValueError("sigma/threshold domain")

    def residual(gas,old,incoming,lam):
        if len(gas)!=4 or len(old)!=4 or len(incoming)!=len(energies):
            raise ValueError("state layout")
        gas=list(map(D2.coerce,gas))
        old=list(map(D2.coerce,old))
        incoming=list(map(D2.coerce,incoming))
        lam=D2.coerce(lam)
        deriv=list(nonphoto(gas))
        if len(deriv)!=4:
            raise ValueError("nonphoto shape")
        deriv=list(map(D2.coerce,deriv))
        q=hh_rate(gas)
        deriv[0]+=lam*q
        deriv[3]-=chi[0]*lam*q
        photons=reduced_photons(gas,incoming,dt,density,speed_c,f_he,sigma)
        x,y1,y2,_=gas
        low=[1-x,f_he*(1-y1-y2),f_he*y1]
        for e,sig,photon in zip(energies,sigma,photons):
            rates=[speed_c*density*l*s*photon for l,s in zip(low,sig)]
            deriv[0]+=rates[0]
            deriv[1]+=(rates[1]-rates[2])/f_he
            deriv[2]+=rates[2]/f_he
            deriv[3]+=sum((r*(e-cut) for r,cut in zip(rates,chi)),D2(0))
        return [y-x-dt*f for y,x,f in zip(gas,old,deriv)]
    return residual


def mixed_at_candidate(residual,candidate,old_gas,incoming_photons,lam):
    """Compute A, U, V, W from a supplied regular endpoint candidate.

    Does not test a physical tube, issue a root identity, call BE, or find a root.
    Signed derivatives at zero photon stock are retained without stock division.
    """
    n=len(candidate)
    old=list(map(D2.coerce,old_gas))
    photons=list(map(D2.coerce,incoming_photons))
    lam=D2.coerce(lam)
    base_old=[D2(z.v) for z in old]
    base_ph=[D2(z.v) for z in photons]
    base_lam=D2(lam.v)
    matrix=[[0 for _ in range(n)] for _ in range(n)]
    for col in range(n):
        g=[D2(v,1 if j==col else 0) for j,v in enumerate(candidate)]
        r=residual(g,base_old,base_ph,base_lam)
        for row in range(n):
            matrix[row][col]=r[row].a
    parameter=residual([D2(v) for v in candidate],old,photons,lam)
    u=solve_linear(matrix,[-r.a for r in parameter])
    v=solve_linear(matrix,[-r.b for r in parameter])
    pre_mixed=residual([D2(z,a,b,0) for z,a,b in zip(candidate,u,v)],
                       old,photons,lam)
    w=solve_linear(matrix,[-r.ab for r in pre_mixed])
    final=residual([D2(z,a,b,c) for z,a,b,c in zip(candidate,u,v,w)],
                   old,photons,lam)
    return {"matrix":matrix,"U":u,"V":v,"W":w,
            "primal_residual":[r.v for r in final],
            "first_a_residual":[r.a for r in final],
            "first_b_residual":[r.b for r in final],
            "mixed_residual":[r.ab for r in final],
            "native_root_certificate":False}
