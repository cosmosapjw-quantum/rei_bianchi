#!/usr/bin/env python3
"""PHYS04 order-four formal BE maps. Standard library only.

This is a finite formal-polynomial calculation, never a nonlinear BE solver.
Candidate: explicit tensor Taylor coefficients and map-composition derivatives.
Oracle: four predetermined substitutions in a truncated time-series ring.
Shared: rational algebraic fixture and fractions.Fraction. Candidate derivative
and time-series recurrences are different; neither establishes native physics.
"""
from fractions import Fraction as Q
from itertools import product
from math import factorial
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time
import traceback

N = 6
ORDER = 4

class SF:
    """Commuting square-free dual ring; bit 0=lambda, bit 1=b."""
    __slots__ = ("c",)
    def __init__(self, value=0):
        if isinstance(value, SF):
            self.c = value.c.copy()
        elif isinstance(value, dict):
            self.c = {k: Q(v) for k, v in value.items() if v}
        else:
            self.c = {0: Q(value)} if value else {}
    @staticmethod
    def co(v):
        return v if isinstance(v, SF) else SF(v)
    def __add__(self, other):
        other = SF.co(other); out = self.c.copy()
        for k, v in other.c.items():
            out[k] = out.get(k, Q(0)) + v
        return SF(out)
    __radd__ = __add__
    def __neg__(self):
        return SF({k: -v for k, v in self.c.items()})
    def __sub__(self, other):
        return self + (-SF.co(other))
    def __rsub__(self, other):
        return SF.co(other) - self
    def __mul__(self, other):
        other = SF.co(other); out = {}
        for i, a in self.c.items():
            for j, b in other.c.items():
                if not i & j:
                    k = i | j
                    out[k] = out.get(k, Q(0)) + a*b
        return SF(out)
    __rmul__ = __mul__
    def __truediv__(self, other):
        return self * (Q(1)/Q(other))
    def __pow__(self, n):
        ans = SF(1); x = self
        while n:
            if n & 1: ans = ans*x
            n //= 2
            if n: x = x*x
        return ans
    def __eq__(self, other):
        return self.c == SF.co(other).c
    def coefficient(self, mask):
        return self.c.get(mask, Q(0))
    def __bool__(self):
        return bool(self.c)

class Poly:
    """Sparse exact polynomial in (t,z0,...,z5,lambda)."""
    NV = N+2
    __slots__ = ("c",)
    def __init__(self, value=0):
        if isinstance(value, Poly): self.c = value.c.copy()
        elif isinstance(value, dict): self.c = {k: Q(v) for k,v in value.items() if v}
        else: self.c = {(0,)*self.NV: Q(value)} if value else {}
    @staticmethod
    def var(i):
        e=[0]*Poly.NV; e[i]=1
        return Poly({tuple(e): Q(1)})
    @staticmethod
    def co(x):
        return x if isinstance(x, Poly) else Poly(x)
    def __add__(self, other):
        other=Poly.co(other); out=self.c.copy()
        for e,v in other.c.items(): out[e]=out.get(e,Q(0))+v
        return Poly(out)
    __radd__=__add__
    def __neg__(self): return Poly({e:-v for e,v in self.c.items()})
    def __sub__(self,o): return self+(-Poly.co(o))
    def __rsub__(self,o): return Poly.co(o)-self
    def __mul__(self,o):
        o=Poly.co(o); out={}
        for a,ca in self.c.items():
            for b,cb in o.c.items():
                e=tuple(x+y for x,y in zip(a,b))
                out[e]=out.get(e,Q(0))+ca*cb
        return Poly(out)
    __rmul__=__mul__
    def __truediv__(self,o): return self*(Q(1)/Q(o))
    def __pow__(self,n):
        ans=Poly(1)
        for _ in range(n): ans=ans*self
        return ans
    def derivative(self,i):
        out={}
        for e,c in self.c.items():
            if e[i]:
                q=list(e); q[i]-=1
                out[tuple(q)]=c*e[i]
        return Poly(out)
    def evaluate(self,vals):
        ans=SF(0)
        powers={}
        for e,c in self.c.items():
            p=SF(c)
            for i,k in enumerate(e):
                if k:
                    key=(i,k)
                    if key not in powers: powers[key]=vals[i]**k
                    p=p*powers[key]
                    if not p: break
            ans=ans+p
        return ans

class TS:
    """Truncated h-series with SF coefficients, independent convolution path."""
    __slots__=("a",)
    def __init__(self,x=0):
        if isinstance(x,TS): self.a=x.a.copy()
        elif isinstance(x,list):
            self.a=[SF.co(v) for v in x[:ORDER+1]]
            self.a += [SF(0)]*(ORDER+1-len(self.a))
        else: self.a=[SF.co(x)]+[SF(0)]*ORDER
    @staticmethod
    def co(x): return x if isinstance(x,TS) else TS(x)
    @staticmethod
    def h(scale=1): return TS([0,scale])
    def __add__(self,o):
        o=TS.co(o); return TS([a+b for a,b in zip(self.a,o.a)])
    __radd__=__add__
    def __neg__(self): return TS([-a for a in self.a])
    def __sub__(self,o): return self+(-TS.co(o))
    def __rsub__(self,o): return TS.co(o)-self
    def __mul__(self,o):
        o=TS.co(o); out=[SF(0) for _ in range(ORDER+1)]
        for i in range(ORDER+1):
            for j in range(ORDER+1-i):
                out[i+j]=out[i+j]+self.a[i]*o.a[j]
        return TS(out)
    __rmul__=__mul__
    def __truediv__(self,o): return self*(Q(1)/Q(o))
    def __pow__(self,n):
        ans=TS(1)
        for _ in range(n): ans=ans*self
        return ans

def add(*vectors):
    return [sum(v[i] for v in vectors) for i in range(len(vectors[0]))]
def scale(a,v): return [a*x for x in v]
def zeros(): return [SF(0) for _ in range(N)]

class Fixture:
    """Dimensionless algebraic H/He/thermal and two-photon fixture, not a dataset."""
    def __init__(self, density_drift=0, transport=1, profile=0, nonphoto=1,
                 transport_clock=0):
        self.d=Q(density_drift)
        self.transport=Q(transport)
        self.profile=Q(profile)
        self.nonphoto=Q(nonphoto)
        self.transport_clock=Q(transport_clock)
        vs=[Poly.var(i) for i in range(Poly.NV)]
        self.fpoly=self.rhs(vs[0],vs[1:N+1],vs[-1])
        self.hpoly=[f.derivative(N+1) for f in self.fpoly]
        self.derivative_cache={():self.fpoly}
    def density(self,t):
        # Third-order jet of n(t)=exp(-d*t); exact polynomial fixture.
        return 1-self.d*t+self.d**2*t**2/2-self.d**3*t**3/6
    def rhs(self,t,z,lam):
        x,y,v,w,p0,p1=z
        r=Q(1,5); u=1-x; he0=1-y-v; el=x+r*(y+2*v)
        dens=self.density(t)
        # Polynomial temperature/particle-number surrogate; state dependent,
        # includes nonzero third derivatives. Actual k_LCS is not approximated here.
        thermal=1+w/7+w*w/29+y/13+v/17
        q=dens*u*u*thermal
        n=self.nonphoto
        fx=n*dens*(Q(2,11)*u*el-Q(3,17)*x*el)+lam*q
        fy=n*dens*(Q(1,19)*he0*el-Q(2,23)*y*el-Q(3,31)*y*el+Q(1,37)*v*el)
        fv=n*dens*(Q(3,31)*y*el-Q(1,37)*v*el)
        fw=n*(-(Q(1,41)+self.d*t/47)*w+dens*(x*v/43-w*el/53-w*w/59))-lam*Q(7,3)*q
        out=[fx,fy,fv,fw,0*p0,0*p1]
        channels=[(Q(2,3),Q(1,7),Q(1,11),Q(5,2),Q(7,3),Q(11,4)),
                  (Q(5,7),Q(3,13),Q(2,17),Q(9,4),Q(13,5),Q(17,6))]
        for j,p in enumerate((p0,p1)):
            sH,s0,s1,eH,e0,e1=channels[j]
            Hion=dens*sH*u*p
            HeI=dens*s0*he0*p
            HeII=dens*s1*y*p
            out[0]=out[0]+Hion
            out[1]=out[1]+HeI-HeII
            out[2]=out[2]+HeII
            out[3]=out[3]+eH*Hion+r*e0*HeI+r*e1*HeII
            out[4+j]=out[4+j]-Hion-r*HeI-r*HeII
        return out
    def B(self,t):
        p=self.profile
        return [0*t,0*t,0*t,0*t,1+p*t/7,Q(1,3)+p*t*t/11]
    def Bderiv(self,t,k):
        p=self.profile
        if k==0: return self.B(t)
        if k==1: return [0*t,0*t,0*t,0*t,p/7+0*t,2*p*t/11]
        if k==2: return [0*t,0*t,0*t,0*t,0*t,2*p/11+0*t]
        return [0*t for _ in range(N)]
    def Laction(self,t,z):
        # One-way redshift on active quotient, lowest active bin leaks out.
        ell=self.transport*(1+self.transport_clock*t)
        return [0*z[0],0*z[1],0*z[2],0*z[3],
                ell*(-Q(2,5)*z[4]+Q(3,7)*z[5]),
                -ell*Q(3,7)*z[5]]
    def Rcoeff_action(self,t,z,k):
        # R_delta=I+s(delta)L(t), s=(1-exp(-gamma*delta))/gamma.
        # Deliberately not exp(delta L).
        gamma=Q(1,9)
        return scale((-gamma)**(k-1)/factorial(k),self.Laction(t,z))
    def Dpoly(self,indices):
        key=tuple(sorted(indices))
        if key not in self.derivative_cache:
            prior=self.Dpoly(key[:-1])
            self.derivative_cache[key]=[p.derivative(key[-1]) for p in prior]
        return self.derivative_cache[key]
    def f_tensors(self,point,lam):
        vals=list(point)+[lam]; cache={}
        def ev(indices=()):
            key=tuple(sorted(indices))
            if key not in cache:
                cache[key]=[p.evaluate(vals) for p in self.Dpoly(key)]
            return cache[key]
        def tensor(*vectors):
            out=zeros()
            # Ordered index tuples; no symmetry factor is hidden.
            for inds in product(range(N+1),repeat=len(vectors)):
                polys=self.Dpoly(inds)
                if not any(p.c for p in polys): continue
                factor=SF(1)
                for j,k in enumerate(inds):
                    factor=factor*vectors[j][k]
                    if not factor: break
                if factor:
                    out=add(out,scale(factor,ev(inds)))
            return out
        return ev,tensor

def coefficients(model,point,lam,b,max_order=4):
    """Explicit candidate one-step coefficients, F derivatives at (t,z)."""
    t,z=point[0],point[1:]
    ev,D=model.f_tensors(point,lam)
    dk={k:add(model.Rcoeff_action(t,z,k),
              scale(b/Q(factorial(k-1)),model.Bderiv(t,k-1)))
        for k in range(1,max_order+1)}
    a1=add(dk[1],ev())
    out=[None,a1]
    if max_order>=2:
        v1=[SF(1)]+a1
        a2=add(dk[2],D(v1)); out.append(a2)
    if max_order>=3:
        v2=[SF(0)]+a2
        a3=add(dk[3],D(v2),scale(Q(1,2),D(v1,v1)))
        out.append(a3)
    if max_order>=4:
        v3=[SF(0)]+a3
        a4=add(dk[4],D(v3),D(v1,v2),scale(Q(1,6),D(v1,v1,v1)))
        out.append(a4)
    return out

def directional(fn,point,vectors,extra=()):
    """Exact directional derivative by fresh commuting nilpotents."""
    used=0
    for item in list(point)+[y for v in vectors for y in v]+list(extra):
        for m in SF.co(item).c: used |= m
    start=used.bit_length()
    flags=[1<<(start+i) for i in range(len(vectors))]
    pert=list(point)
    for flag,v in zip(flags,vectors):
        pert=[x+SF({flag:Q(1)})*a for x,a in zip(pert,v)]
    value=fn(pert); mask=sum(flags)
    return [SF({m^mask:c for m,c in item.c.items() if (m&mask)==mask})
            for item in value]

def full_and_two_half_coefficients(model,point,lam,b):
    aa=coefficients(model,point,lam,b)
    G={1:[SF(1)]+aa[1]}
    for k in (2,3,4): G[k]=[SF(0)]+aa[k]
    def dg(k,*vectors):
        def fn(q):
            ak=coefficients(model,q,lam,b,k)[k]
            return [SF(1 if k==1 else 0)]+ak
        return directional(fn,point,list(vectors),(lam,b))
    c1=G[1]
    c2=scale(Q(1,4),add(scale(2,G[2]),dg(1,G[1])))
    c3=scale(Q(1,8),add(scale(2,G[3]),dg(1,G[2]),dg(2,G[1]),
                           scale(Q(1,2),dg(1,G[1],G[1]))))
    c4=scale(Q(1,16),add(
        scale(2,G[4]),dg(1,G[3]),dg(2,G[2]),dg(3,G[1]),
        dg(1,G[1],G[2]),scale(Q(1,2),dg(2,G[1],G[1])),
        scale(Q(1,6),dg(1,G[1],G[1],G[1]))))
    return aa[1:], [c1[1:],c2[1:],c3[1:],c4[1:]]

def formal_step(model,start,z_in,delta,lam,b):
    """Four fixed substitutions in a formal ring; no root or tolerance."""
    end=start+delta
    pre=list(z_in)
    for k in range(1,ORDER+1):
        pre=add(pre,scale(delta**k,model.Rcoeff_action(start,z_in,k)))
    pre=add(pre,scale(b*delta,model.B(end)))
    z=list(pre)
    for _ in range(ORDER):
        z=add(pre,scale(delta,model.rhs(end,z,lam)))
    residual=add(z,scale(-1,pre),scale(-delta,model.rhs(end,z,lam)))
    for j in range(N):
        for k in range(ORDER+1):
            if residual[j].a[k] != 0:
                raise AssertionError("formal implicit residual nonzero",j,k)
    return z

def oracle(model,point,lam,b,m):
    start=TS(point[0]); z=[TS(a) for a in point[1:]]
    d=TS.h(Q(1,m))
    for _ in range(m):
        z=formal_step(model,start,z,d,TS(lam),TS(b))
        start=start+d
    return [[z[j].a[k] for j in range(N)] for k in range(1,ORDER+1)]

def initial(old=False,zero_photons=False,lam0=Q(0),b0=Q(0)):
    state=[Q(1,5),Q(1,7),Q(1,11),Q(3,2),Q(1,13),Q(1,17)]
    if zero_photons: state[-2:]=[Q(0),Q(0)]
    if old:
        U=[Q((-1)**j,j+31) for j in range(N)]
        V=[Q((-1)**(j+1),j+43) for j in range(N)]
        W=[Q(1,j+59) for j in range(N)]
    else:
        U=V=W=[Q(0)]*N
    zs=[SF({0:z,1:u,2:v,3:w}) for z,u,v,w in zip(state,U,V,W)]
    return [SF(Q(2,9))]+zs,SF({0:lam0,1:1}),SF({0:b0,2:1})

def frac(q): return str(q.numerator)+"/"+str(q.denominator)
def vector_slot(v,mask=3): return [frac(SF.co(x).coefficient(mask)) for x in v]
def compare(candidate,reference,label):
    count=0
    for k in range(ORDER):
        for j in range(N):
            if candidate[k][j] != reference[k][j]:
                raise AssertionError(label,k+1,j,
                                     candidate[k][j].c,reference[k][j].c)
            count += 4
    return count

def zero_photon_L_prediction(model,point,lam,b):
    # This expression is the mixed derivative at a control base point but
    # contains H=F_lambda explicitly, no lambda/b nilpotent extraction needed.
    base=[SF(x.coefficient(0)) for x in point]
    lam_base=SF(lam.coefficient(0))
    vals=base+[lam_base]
    H=[p.evaluate(vals) for p in model.hpoly]
    ev,D=model.f_tensors(base,lam_base)
    B=[SF(x) for x in model.B(base[0])]
    LB=[SF(x) for x in model.Laction(base[0],B)]
    JLB=D([SF(0)]+LB)
    YLB=D([SF(0)]+H,[SF(0)]+LB)
    Y=D([SF(0)]+H,[SF(0)]+B)
    HX=zeros()
    for j in range(N):
        for k in range(N):
            HX[j]=HX[j]+model.hpoly[j].derivative(k+1).evaluate(vals)*JLB[k]
    return scale(Q(1,16),add(HX,scale(2,YLB),model.Laction(base[0],Y)))

def frozen_cubic_prediction(model,point,lam,m):
    base=[SF(x.coefficient(0)) for x in point]
    vals=base+[SF(lam.coefficient(0))]
    ev,D=model.f_tensors(base,vals[-1])
    H=[p.evaluate(vals) for p in model.hpoly]
    B=[SF(x) for x in model.B(base[0])]
    JB=D([SF(0)]+B)
    Y=D([SF(0)]+H,[SF(0)]+B)
    X=zeros()
    for j in range(N):
        for k in range(N):
            X[j]=X[j]+model.hpoly[j].derivative(k+1).evaluate(vals)*JB[k]
    alpha=Q((m+1)*(m+2),6*m*m)
    beta=Q((m+1)*(2*m+1),6*m*m)
    return add(scale(alpha,X),scale(beta,Y))

def run(outdir):
    outdir.mkdir(parents=True,exist_ok=False)
    started=time.time()
    specs=[
      ("frozen_nonzero_photons",0,1,0,1,0,False,False,Q(0),Q(0)),
      ("density_and_profile_drift",Q(1,7),1,1,1,0,False,False,Q(1,3),Q(2,5)),
      ("transport_clock_and_density",Q(2,9),1,0,1,Q(1,6),False,False,Q(0),Q(2,5)),
      ("inherited_UVW_all_nonzero",Q(1,7),1,1,1,Q(1,6),True,False,Q(1,3),Q(2,5)),
      ("zero_photons_frozen",0,1,0,1,0,False,True,Q(0),Q(0)),
      ("zero_photons_frozen_lambda_base",0,1,0,1,0,False,True,Q(1,3),Q(2,5)),
    ]
    results=[]; scalar_slots=0
    for name,d,tr,pr,np,tc,old,zp,l0,b0 in specs:
        model=Fixture(d,tr,pr,np,tc)
        point,lam,b=initial(old,zp,l0,b0)
        full,half=full_and_two_half_coefficients(model,point,lam,b)
        direct1=oracle(model,point,lam,b,1)
        direct2=oracle(model,point,lam,b,2)
        scalar_slots += compare(full,direct1,name+"/full")
        scalar_slots += compare(half,direct2,name+"/two-half")
        row={"test_id":name,"status":"PASS","old_UVW_nonzero":old,
             "zero_initial_photons":zp,"lambda_base":frac(l0),"b_base":frac(b0),
             "all_state_components":N,"checked_orders":[1,2,3,4],
             "checked_control_slots":["primal","U","V","W"],
             "full_mixed_cubic":vector_slot(full[2]),
             "full_mixed_quartic":vector_slot(full[3]),
             "two_half_mixed_cubic":vector_slot(half[2]),
             "two_half_mixed_quartic":vector_slot(half[3]),
             "quartic_two_half_minus_full":vector_slot(add(half[3],scale(-1,full[3])))}
        if not old:
            # PHYS03 cubic is only an inherited lower-order consistency limit.
            for m,actual in ((1,full[2]),(2,half[2])):
                pred=frozen_cubic_prediction(model,point,lam,m)
                if any(actual[j].coefficient(3)!=pred[j].coefficient(0) for j in range(N)):
                    raise AssertionError(name,"inherited cubic limit",m)
            row["inherited_cubic_limit"]="PASS"
        if zp:
            noL=Fixture(d,0,pr,np,tc)
            f0,h0=full_and_two_half_coefficients(noL,point,lam,b)
            predicted=zero_photon_L_prediction(model,point,lam,b)
            full_diff=add(full[3],scale(-1,f0[3]))
            half_diff=add(half[3],scale(-1,h0[3]))
            if any(x.coefficient(3) for x in full_diff):
                raise AssertionError(name,"zero-photon full L dependence")
            if any(half_diff[j].coefficient(3)!=predicted[j].coefficient(0)
                   for j in range(N)):
                raise AssertionError(name,"zero-photon L quartic",
                    vector_slot(half_diff),vector_slot(predicted,0))
            row["zero_photon_remap_specialization"]="PASS"
            row["L_dependent_two_half_quartic"]=vector_slot(half_diff)
            row["L_specialization_prediction"]=vector_slot(predicted,0)
        results.append(row)
        print(json.dumps({"test_id":name,"status":"PASS"},ensure_ascii=False),flush=True)
    result={
      "schema":"HH_PHYS04_ORDERED_BE_QUARTIC_EXACT_CHECK_v1",
      "status":"PASS","cases":results,
      "case_count":len(results),"exact_scalar_slots_compared":scalar_slots,
      "formal_residual_order":ORDER,"state_dimension":N,
      "native_calls":0,"ivp_calls":0,"nonlinear_BE_root_calls":0,"NCP_calls":0,
      "legacy_or_parent_suite_reruns":0,
      "coefficient_normalization":"raw h^k coefficients, not kth derivatives",
      "oracle":"four predetermined formal substitutions per stage, independent time convolution",
      "candidate":"explicit F tensor a1..a4 and extended-time two-step composition",
      "shared_dependencies":["fractions.Fraction","dimensionless fixture rhs definition"],
      "independent_final_decision":False,
      "actual_native_finite_time_claim":"UNRESOLVED",
      "elapsed_seconds":time.time()-started
    }
    (outdir/"EXACT_CHECK.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    out=Path(args.output)
    try:
        result=run(out)
        print(json.dumps({"status":result["status"],"case_count":result["case_count"],
                          "exact_scalar_slots_compared":result["exact_scalar_slots_compared"]},
                         ensure_ascii=False),flush=True)
        return 0
    except Exception:
        details={"classification":"UNCLASSIFIED_CHECK_FAILURE",
                 "traceback":traceback.format_exc(),
                 "scientific_promotion":False}
        # Preserve the initial scientific/check failure, never overwrite it.
        fail=Path(__file__).resolve().parent/"FIRST_CHECK_FAILURE.json"
        try:
            with fail.open("x") as f: json.dump(details,f,indent=2)
        except FileExistsError: pass
        traceback.print_exc()
        return 1

if __name__=="__main__":
    sys.exit(main())

