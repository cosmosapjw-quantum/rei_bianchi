"""Positive two-moment reconstruction; no time evolution or atomic policy."""
import math
from decimal import Decimal, localcontext
import numpy as np

C = 29979245800.0
EV = 1.602176634e-12
THRESHOLDS = (13.60, 24.59, 54.42)
CHI = np.array((13.598434599702, 24.587389011, 54.41776))

def dint(k, lo, hi):
    """Decimal closed integral of exp(k*x) dx, including k=0."""
    return hi-lo if k == 0 else ((k*hi).exp()-(k*lo).exp())/k

def dmean(beta, a, b):
    L=(b/a).ln()
    # Anchor at high end for positive slope to avoid positive huge exponent.
    anchor=L if beta>0 else Decimal(0)
    p=beta/L
    return a*(anchor.exp())*dint(p+1,-anchor,L-anchor)/dint(p,-anchor,L-anchor)

class Reconstruction:
    def __init__(self, qlo, qhi, R, N, U):
        if not all(math.isfinite(x) for x in (qlo,qhi,R,N,U)) or qlo<=0 or qhi<=qlo or R<=0 or N<0 or U<0:
            raise ValueError('HOLD_RECONSTRUCTION_REALIZABILITY')
        self.a=qlo; self.b=min(qhi,50000./R); self.R=R; self.N=N; self.U=U
        self.delta=None; self.beta=0.; self.p=0.; self.iterations=0; self.doublings=0
        if self.b<=self.a:
            if N!=0 or U!=0: raise ValueError('HOLD_RECONSTRUCTION_REALIZABILITY')
            self.empty=True; return
        if (N==0)!=(U==0): raise ValueError('HOLD_RECONSTRUCTION_REALIZABILITY')
        self.empty=N==0
        if self.empty:return
        self.Q=U/R; self.mean=self.Q/N
        if not math.isfinite(self.mean) or not self.a<=self.mean<=self.b:
            raise ValueError('HOLD_RECONSTRUCTION_REALIZABILITY')
        if self.mean in (self.a,self.b): self.delta=self.mean; return
        with localcontext() as ctx:
            ctx.prec=80
            a,b,m=map(Decimal.from_float,(self.a,self.b,self.mean))
            low,high=Decimal(-1),Decimal(1)
            while not dmean(low,a,b)<=m<=dmean(high,a,b):
                if self.doublings>=60:raise ValueError('HOLD_RECONSTRUCTION_INVERSION')
                low*=2;high*=2;self.doublings+=1
            for i in range(200):
                beta=(low+high)/2;forward=dmean(beta,a,b);self.iterations=i+1
                if abs(forward-m)/(b-a)<=Decimal('1e-17'): break
                if forward<m:low=beta
                else:high=beta
            else:raise ValueError('HOLD_RECONSTRUCTION_INVERSION')
            self.beta=float(beta);self.p=float(beta/(b/a).ln())
            self.forward_mean=float(dmean(Decimal.from_float(self.beta),a,b))
        if abs(self.forward_mean-self.mean)/(self.b-self.a)>1e-12:
            raise ValueError('HOLD_RECONSTRUCTION_INVERSION')

    def density(self,q):
        q=np.asarray(q,float)
        if self.empty:return np.zeros_like(q)
        if self.delta is not None:raise ValueError('DELTA_HAS_NO_DENSITY')
        if np.any(q<self.a) or np.any(q>self.b):raise ValueError('OUTSIDE_ACTIVE_SUPPORT')
        L=math.log(self.b/self.a);t=np.log(q/self.a)/L;beta=self.beta
        if beta==0:return np.full_like(q,self.N/L)
        if beta>0:return self.N*(beta/L)*np.exp(beta*(t-1))/(-math.expm1(-beta))
        return self.N*(beta/L)*np.exp(beta*t)/math.expm1(beta)

    def oracle_moment(self,r=0.,lo=None,hi=None):
        """Independent Decimal80 closed integral, returning ∫q^r F dlnq."""
        if self.empty:return 0.
        lo=self.a if lo is None else max(self.a,lo)
        hi=self.b if hi is None else min(self.b,hi)
        if self.delta is not None:
            return self.N*self.delta**r if lo<=self.delta<=hi else 0.
        if hi<=lo:return 0.
        with localcontext() as ctx:
            ctx.prec=80
            a,b,l,h=map(Decimal.from_float,(self.a,self.b,lo,hi))
            p=Decimal.from_float(self.p);rr=Decimal.from_float(float(r));anchor=b if p>0 else a
            denom=dint(p,(a/anchor).ln(),(b/anchor).ln())
            num=dint(p+rr,(l/anchor).ln(),(h/anchor).ln())
            return float(Decimal.from_float(self.N)*anchor**rr*num/denom)

def nodes(rec,order,threshold):
    if rec.empty:return np.array([]),np.array([])
    lo=max(rec.a,threshold/rec.R);hi=rec.b
    if rec.delta is not None:
        if rec.delta*rec.R<threshold:return np.array([]),np.array([])
        return np.array([rec.delta]),np.array([rec.N])
    if hi<=lo:return np.array([]),np.array([])
    x,w=np.polynomial.legendre.leggauss(order)
    la,lb=math.log(lo),math.log(hi)
    q=np.exp((la+lb)/2+x*(lb-la)/2)
    if np.any(q<rec.a) or np.any(q>rec.b):raise ValueError('HOLD_ANALYTIC_FIXTURE')
    return q,w*(lb-la)/2*rec.density(q)

def kernels(q,weights,sigma,R,chi):
    k0=C*math.fsum(float(v) for v in weights*sigma)
    k1=C*math.fsum(float(v) for v in weights*sigma*q)
    heat=C*math.fsum(float(v) for v in weights*sigma*(R*q-chi))
    scale=max(abs(R*k1),abs(chi*k0),abs(heat))
    err=abs(heat-(R*k1-chi*k0))
    if (err/scale>1e-12 if scale else err!=0):raise ValueError('HOLD_COMMON_PHOTO_ACCOUNTING')
    return np.array([k0,k1,heat])

def accounting(K,R,V,densities):
    # K shape [absorber, K0/K1/H]; same events supply all particle changes.
    n=np.asarray(densities);Gamma=K[:,0]/V;events=n*Gamma
    heat=EV*float(np.dot(n,K[:,2]/V));binding=EV*float(np.dot(CHI,events))
    absorbed_energy=EV*float(np.dot(n,R*K[:,1]/V))
    scale=max(abs(heat),abs(binding),abs(absorbed_energy));err=abs(heat+binding-absorbed_energy)
    if (err/scale>1e-12 if scale else err!=0):raise ValueError('HOLD_COMMON_PHOTO_ACCOUNTING')
    return {'Gamma':Gamma.tolist(),'events':events.tolist(),'photon_loss_ref':float(np.dot(n,K[:,0])),
            'photon_energy_loss_ref_eV':float(np.dot(n,R*K[:,1])), 'binding_erg':binding,'heat_erg':heat,
            'absorbed_energy_erg':absorbed_energy,'residual_scaled':err/scale if scale else 0.,
            'particle_changes':{'HI':-events[0],'HII':events[0],'HeI':-events[1],
              'HeII':events[1]-events[2],'HeIII':events[2],'electron':float(sum(events))}}

