#!/usr/bin/env python3
"""Apply PHYS16 endpoint-remainder theorems to the archived run01 enclosure.

Pure exact rational interval arithmetic. No physical source, root, or history
routine is imported or invoked. All scalar fits remain inherited data.
"""
from dataclasses import dataclass
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as F
import argparse
import hashlib
import json
from pathlib import Path
import resource
import struct
import time


@dataclass(frozen=True)
class I:
    lo: F
    hi: F = None

    def __post_init__(self):
        object.__setattr__(self,'lo',F(self.lo))
        object.__setattr__(self,'hi',self.lo if self.hi is None else F(self.hi))
        assert self.lo <= self.hi

    def __add__(self,x):
        x=iv(x);return I(self.lo+x.lo,self.hi+x.hi)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,x):return self+-iv(x)
    def __rsub__(self,x):return iv(x)+-self
    def __mul__(self,x):
        x=iv(x);v=[self.lo*x.lo,self.lo*x.hi,self.hi*x.lo,self.hi*x.hi];return I(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self,x):
        x=iv(x);assert not x.lo<=0<=x.hi
        return self*I(1/x.hi,1/x.lo)
    def __rtruediv__(self,x):return iv(x)/self
    def __pow__(self,n):
        assert isinstance(n,int) and n>=0
        if not n:return I(1)
        if n%2==0:
            out=I(0 if self.lo<=0<=self.hi else min(self.lo**2,self.hi**2),max(self.lo**2,self.hi**2))
            return out**(n//2) if n>2 else out
        return self*(self**(n-1))
    def mag(self):return max(abs(self.lo),abs(self.hi))
    def meet(self,x):
        x=iv(x);return I(max(self.lo,x.lo),min(self.hi,x.hi))


def iv(x):return x if isinstance(x,I) else I(x)
def bits(s):return F.from_float(struct.unpack('>d',bytes.fromhex(s))[0])
def raw(x):
    if 'exact' in x:
        e=x['exact'];return I(F(*map(int,e['lo'])),F(*map(int,e['hi'])))
    return I(bits(x['lo_bits']),bits(x['hi_bits']))
def dot(a,b):return sum((x*y for x,y in zip(a,b)),I(0))
def mv(A,v):return [dot(row,v) for row in A]
def mm(A,B):return [[dot(row,[r[j] for r in B]) for j in range(len(B[0]))] for row in A]
def rowmat(v,A):return [dot(v,[r[j] for r in A]) for j in range(len(A[0]))]
def plus(A,B):return [[a+b for a,b in zip(ar,br)] for ar,br in zip(A,B)]


def dec(x,rounding):
    with localcontext() as c:
        c.prec=16;c.rounding=rounding
        return str(Decimal(x.numerator)/Decimal(x.denominator))
def enc(x):
    if isinstance(x,F):x=I(x)
    if isinstance(x,I):return {'exact':{'lo':[str(x.lo.numerator),str(x.lo.denominator)],'hi':[str(x.hi.numerator),str(x.hi.denominator)]},
                              'outward_decimal':[dec(x.lo,ROUND_FLOOR),dec(x.hi,ROUND_CEILING)],
                              'sign':'STRICT_POSITIVE' if x.lo>0 else 'STRICT_NEGATIVE' if x.hi<0 else 'ZERO' if x.lo==x.hi==0 else 'CONTAINS_ZERO'}
    if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [enc(v) for v in x]
    return x
def short(x):
    if isinstance(x,(F,I)):return enc(x)['outward_decimal']
    if isinstance(x,dict):return {k:short(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [short(v) for v in x]
    return x
def identity(p):
    b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--phys15',type=Path,required=True)
    ap.add_argument('--application',type=Path,required=True)
    ap.add_argument('--hessian',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();start=time.perf_counter()
    paths={'application':args.application,'hessian':args.hessian,
      'source':args.phys15/'inputs/phys14/inputs/ncp07/results/full/SOURCE_BOX.json',
      'centre':args.phys15/'inputs/phys14/inputs/ncp07/results/full/SOURCE_CENTRE.json',
      'preconditioner':args.phys15/'inputs/ncp07_additions/results/full/UNIFORM_ARITHMETIC.json',
      'constants':args.phys15/'inputs/phys14/inputs/ncp07/results/full/NATIVE_CONSTANT_LEAVES.json'}
    data={k:json.loads(p.read_text()) for k,p in paths.items()}
    app,hs,src,ctr,pre,cs=[data[k] for k in ['application','hessian','source','centre','preconditioner','constants']]
    C=[[I(F.from_float(v)) for v in row] for row in pre['fixed_C']]
    S=[F.from_float(v) for v in pre['radius']]
    B=[[raw(v).hi for v in row] for row in pre['B']]
    q=bits(pre['q']['hi_bits']);kappa=1/(1-q)
    L=F(*map(int,hs['L_H']['exact']))
    d=[raw(v) for v in app['endpoint']['d']]
    a=max(v.mag()/s for v,s in zip(d,S))
    y=[raw(v) for v in app['root_boxes']['g2']]
    center=[I(F.from_float(v)) for v in pre['center']]
    diff=[yi-ci for yi,ci in zip(y,center)]
    Hess=[[[raw(v) for v in row] for row in mat] for mat in src['G_gg']]
    J=[[ (raw(ctr['A_Gg'][i][j])+sum((Hess[i][k][j]*diff[k] for k in range(4)),I(0))).meet(raw(src['A_Gg'][i][j]))
         for j in range(4)] for i in range(4)]
    CJ=mm(C,J)
    M=[[(I(i==j)-CJ[i][j]).meet(I(-B[i][j],B[i][j])) for j in range(4)] for i in range(4)]
    assert max(sum(M[i][j].mag()*S[j]/S[i] for j in range(4)) for i in range(4))<=q
    CT=F(2)*bits(cs['ev_erg_bits'])/(3*bits(cs['kb_bits']))
    f=bits(src['nHe_stored_bits'])/bits(src['nH_bits'])
    le=[I(1),I(f),I(2*f),I(0)]
    Pi2=raw(app['endpoint']['Pi2']);PiF=raw(app['endpoint']['PiF'])
    T2=CT*y[3]/Pi2
    nt=[CT*I(i==3)-T2*le[i] for i in range(4)]
    bT=sum(v.mag()*s for v,s in zip(nt,S))
    Id=[[I(i==j) for j in range(4)] for i in range(4)]
    P=plus(plus(Id,M),mm(M,M));m=2;psum=1+q+q*q
    r=[raw(v) for v in app['residual']]
    Cr=mv(C,r);vm=mv(P,Cr)
    z=rowmat(rowmat(nt,P),C)
    eps=q**(m+1)*a+L*a*a*psum/2
    d_refined=[di.meet(vi+I(-si*eps,si*eps)) for di,vi,si in zip(d,vm,S)]
    a_refined=max(v.mag()/s for v,s in zip(d_refined,S))
    n_approx=dot(z,r).meet(dot(nt,vm))
    n_cert=n_approx+I(-bT*eps,bT*eps)
    dt_endpoint=(n_cert/PiF).meet(raw(app['endpoint']['DeltaT_K']))
    c_norm=max(sum(C[i][j].mag()*S[j]/S[i] for j in range(4)) for i in range(4))
    zrow_error=kappa*c_norm*bT*(q**(m+1)+L*a*psum/2)
    zmean=[zi+I(-zrow_error/si,zrow_error/si) for zi,si in zip(z,S)]
    sectors={}
    for name,rs0 in app['residual_sectors'].items():
        rs=[raw(v) for v in rs0];csval=max(v.mag()/si for v,si in zip(mv(C,rs),S))
        er=kappa*csval*bT*(q**(m+1)+L*a*psum/2)
        approx=dot(z,rs);cert=approx+I(-er,er)
        linked=(cert/PiF).meet(raw(app['sector_attribution']['sectors'][name]['temperature_K']))
        margin=I(-cert.hi) if cert.hi<0 else I(cert.lo) if cert.lo>0 else I(0)
        sectors[name]={'c_s':csval,'approximate_numerator':approx,'error_upper_K':er,
                      'certified_numerator':cert,'strict_sign_margin_K':margin,
                      'temperature_K_after_intersection':linked}
    # Preserve exact b factor in the two birth sectors. The averaged adjoint
    # components, not direct forcing, decide their actual endpoint sign.
    nH=bits(src['nH_bits']);cc=bits(cs['c_bits']);h=F(625000000)
    sig=[bits(row[0]) for row in src['sigma_bits']]
    heat=[bits(row[0]) for row in src['heat_bits']]
    E=[bits(v) for v in src['energy_bits']]
    rho=raw(app['linked_factors']['rho']);birth=raw(app['linked_factors']['M'])
    alpha24=(1-rho)*E[24]/(E[24]-E[23])
    eta=h*cc*nH*(1-y[0]);s23,s24=sig[23],sig[24]
    D23,D24=1+eta*s23,1+eta*s24
    dbeta=eta*(s23-s24)*(1-eta**2*s23*s24)/(D23**2*D24**2)
    aa,bb=heat[23]*s23,heat[24]*s24
    # All three polynomial coefficients are strictly negative on this leaf.
    assert aa-bb<0 and aa*s24-bb*s23<0 and aa*s24*s24-bb*s23*s23<0
    dheat=eta*((aa-bb)+2*eta*(aa*s24-bb*s23)+eta**2*(aa*s24*s24-bb*s23*s23))/(D23**2*D24**2)
    assert dbeta.lo>0 and dheat.hi<0
    assert zmean[0].hi<0 and zmean[3].lo>0
    br_per_b=birth*alpha24*(dbeta*zmean[0]+dheat*zmean[3])/PiF
    tau24=eta*s24;C1=tau24/((1+tau24)**2*(1+2*tau24))
    znu24=zmean[0]+heat[24]*zmean[3]
    assert znu24.hi<0
    be_per_b=-birth*C1*znu24/PiF
    assert br_per_b.hi<0 and be_per_b.lo>0
    birth_signed={'scope':'For b>0; at b=0 both exact sectors vanish',
                  'zbar_numerator':zmean,'zbar_dot_nu24':znu24,
                  'beta23_minus_beta24':dbeta,'heat_beta23_minus_heat_beta24':dheat,
                  'birth_redshift_DeltaT_over_b_K':br_per_b,
                  'birth_backward_euler_DeltaT_over_b_K':be_per_b,
                  'birth_redshift_all_b_0_1_K':I(br_per_b.lo,0),
                  'birth_backward_euler_all_b_0_1_K':I(0,be_per_b.hi)}
    result={'schema':'WU088_HH_PHYS16_ENDPOINT_REMAINDER_APPLICATION_V1',
       'status':'CANDIDATE_COMPUTED','input_status':'PHYS16 application run01 awaiting independent science review',
       'inputs':{k:identity(p) for k,p in paths.items()},
       'method':'exact Fraction interval arithmetic; endpoint centre-Hessian inclusion and finite m=2 Neumann; no source kernel',
       'a_from_actual_D':a,'a_after_endpoint_intersection':a_refined,'q':q,'L_H':L,'m':m,
       'kappa':kappa,'b_T_upper_K':bT,'C_scaled_inf_norm':c_norm,
       'linear_tail':q**3*a,'quadratic_tail':L*a*a*psum/2,'epsilon_m':eps,
       'endpoint_newton_error_upper':kappa*L*a*a/2,
       'temperature_numerator_error_upper_K':bT*eps,
       'temperature_error_from_same_denominator_upper_K':bT*eps/PiF.lo,
       'endpoint_J_inclusion':J,'M_inclusion':M,'Neumann_prediction':vm,
       'endpoint_d_intersection':d_refined,'numerator_covector':nt,
       'endpoint_adjoint_m2':z,'averaged_adjoint_weighted_row_error_upper_K':zrow_error,
       'averaged_adjoint_numerator_inclusion':zmean,
       'temperature_numerator':n_cert,'DeltaT_K_after_endpoint_intersection':dt_endpoint,
       'sectors':sectors,'birth_signed_factorization':birth_signed,
       'physical_source_calls':0,'root_solves':0,'history_replays':0,
       'elapsed_seconds':time.perf_counter()-start,
       'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(enc(result),ensure_ascii=False,indent=2)+'\n')
    summary={k:result[k] for k in ['status','a_from_actual_D','endpoint_newton_error_upper','epsilon_m','temperature_error_from_same_denominator_upper_K','DeltaT_K_after_endpoint_intersection','birth_signed_factorization','elapsed_seconds','peak_rss_kib']}
    print(json.dumps(short(summary),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
