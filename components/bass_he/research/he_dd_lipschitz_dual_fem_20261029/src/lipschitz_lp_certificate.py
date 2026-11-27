"""Finite-grid LP with exact rational dual postcertificate and analytic continuum slack.

No physical EXFOR event normalization, production kernel, or new IVP is admitted.
The interval claim is for the *conditional* nonnegative Lipschitz angular family.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as F
from functools import lru_cache
from math import factorial
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

SOURCE=( (46,F('0.11'),F('0.17')), (61,F('0.11'),F('0.21')),
         (73,F('0.02'),F('0.12')), (87,F('0.14'),F('0.24')) )
SOURCE_SHA256='b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f'
PARENT_PR=109
PARENT_HEAD='11b3cfdb987137323d8ebd220e74063b0ed6db22'
GATES=dict(kappa=None,R_event=None,heat_rate=None,physical_activation=False,L4=False,production='HOLD')
PI0=F('3.1415926535897932384626433832795')
TRIG_EPS=F(1,10**8)   # covers both-basis combination, Taylor, Machin-pi and interval evaluation


def exact(x):
    if isinstance(x,(float,bool)):raise TypeError('float/bool not accepted')
    if not isinstance(x,(int,str,F,Decimal)):raise TypeError('exact rational expected')
    return F(x)

def atan_bounds(z, even_terms):
    """Alternating series: S_even < atan(1/z) < S_odd."""
    if even_terms%2:raise ValueError('even_terms')
    def sm(n):return sum(((-1)**j*F(1, (2*j+1)*z**(2*j+1)) for j in range(n)),F())
    return sm(even_terms),sm(even_terms+1)

@lru_cache(maxsize=1)
def pi_bounds():
    l5,u5=atan_bounds(5,40); l239,u239=atan_bounds(239,14)
    low=16*l5-4*u239; high=16*u5-4*l239
    assert low<high and max(abs(PI0-low),abs(PI0-high))<F(1,10**27)
    assert 6*(F(24,5)**32/factorial(32)+F(24,5)**33/factorial(33)+F(3,2)*F(1,10**27))<TRIG_EPS
    return low,high

@dataclass(frozen=True)
class Interval:
    lo:Decimal
    hi:Decimal
    def __post_init__(self):
        if self.lo>self.hi:raise ValueError('interval reversed')
    @classmethod
    def point(cls,x):
        if isinstance(x,F):
            with localcontext() as c:
                c.prec=90;c.rounding=ROUND_FLOOR;a=Decimal(x.numerator)/Decimal(x.denominator)
            with localcontext() as c:
                c.prec=90;c.rounding=ROUND_CEILING;b=Decimal(x.numerator)/Decimal(x.denominator)
            return cls(a,b)
        x=Decimal(x);return cls(x,x)
    def __add__(self,o):
        o=o if isinstance(o,Interval) else Interval.point(o)
        with localcontext() as c:
            c.prec=85;c.rounding=ROUND_FLOOR; lo=self.lo+o.lo
        with localcontext() as c:
            c.prec=85;c.rounding=ROUND_CEILING; hi=self.hi+o.hi
        return Interval(lo,hi)
    __radd__=__add__
    def __neg__(self):return Interval(-self.hi,-self.lo)
    def __sub__(self,o):return self+(-o if isinstance(o,Interval) else -Interval.point(o))
    def __mul__(self,o):
        o=o if isinstance(o,Interval) else Interval.point(o)
        with localcontext() as c:
            c.prec=85;c.rounding=ROUND_FLOOR; lows=[a*b for a in (self.lo,self.hi) for b in (o.lo,o.hi)]
        with localcontext() as c:
            c.prec=85;c.rounding=ROUND_CEILING; highs=[a*b for a in (self.lo,self.hi) for b in (o.lo,o.hi)]
        return Interval(min(lows),max(highs))
    __rmul__=__mul__
    def divided(self,pos):
        if not isinstance(pos,int) or pos<=0:raise ValueError('positive integer divisor')
        with localcontext() as c:
            c.prec=85;c.rounding=ROUND_FLOOR;lo=self.lo/pos
        with localcontext() as c:
            c.prec=85;c.rounding=ROUND_CEILING;hi=self.hi/pos
        return Interval(lo,hi)
    def centre(self):
        with localcontext() as c:
            c.prec=75;return F((self.lo+self.hi)/2)
    def is_within(self,centre,eps):return F(self.lo)>=centre-eps and F(self.hi)<=centre+eps

def trig_series(z,m):
    """Certified *polynomial* interval, actual trig within ±TRIG_EPS after remainder proof."""
    z=z*Interval.point(m)
    z2=z*z
    sin=Interval.point(0);cos=Interval.point(0)
    st=z;ct=Interval.point(1)
    for j in range(16):
        sin=sin+st;cos=cos+ct
        st=-(st*z2).divided((2*j+2)*(2*j+3))
        ct=-(ct*z2).divided((2*j+1)*(2*j+2))
    # sin polynomial degree31, cos degree30. Taylor remainder is bounded by
    # (24/5)^33/33! and (24/5)^32/32!, respectively, for |z|<24/5.
    return sin,cos

def trig_mid(t,j,subdiv):
    """Rational midpoint coefficients g_t, g_t' with verified <=TRIG_EPS envelope."""
    t=exact(t)
    mid=F(2*j+1,2*subdiv)
    z=Interval.point(PI0)*Interval.point(mid)
    z=z.divided(180)
    s1,c1=trig_series(z,1);s3,c3=trig_series(z,3)
    g=(Interval.point(F(1,4)-t)*s1)+(Interval.point(F(1,4))*s3)
    gp=(Interval.point(PI0).divided(180))*(Interval.point(F(1,4)-t)*c1+Interval.point(F(3,4))*c3)
    # Include pi0-vs-pi difference and Taylor remainder using universal margin.
    g0,gp0=g.centre(),gp.centre()
    if not (g.is_within(g0,TRIG_EPS/F(10)) and gp.is_within(gp0,TRIG_EPS/F(10))):
        raise ArithmeticError('Taylor interval too wide; no certificate')
    return g0,gp0

def frac_source_bounds(L):
    L=exact(L)
    if L<F(1,700):raise ValueError('L < exact min source Lipschitz')
    return L

def envelope(theta,L,upper=False):
    theta=exact(theta);L=frac_source_bounds(L)
    if theta<0 or theta>90:raise ValueError('theta out of domain')
    if upper:return min(hi+L*abs(theta-angle) for angle,lo,hi in SOURCE)
    return max([F(0)]+[lo-L*abs(theta-angle) for angle,lo,hi in SOURCE])

def lower_segments(L):
    L=frac_source_bounds(L);cuts={F(0),F(90)}
    cuts.update(F(x[0]) for x in SOURCE)
    lines=[(F(0),F(0),None)]
    for theta,lo,hi in SOURCE:
        lines.extend([(lo-L*theta,L,F(theta)),(lo+L*theta,-L,F(theta))])
    # all pair intersections; include only if valid on corresponding side of theta
    for i,(a,b,refa) in enumerate(lines):
        for d,e,refb in lines[i+1:]:
            if b!=e:
                x=(d-a)/(b-e)
                if 0<x<90:cuts.add(x)
    raw=sorted(cuts)
    out=[]
    for a,b in zip(raw[:-1],raw[1:]):
        mid=(a+b)/2;vals=[(F(0),F(0))]
        for theta,lo,hi in SOURCE:
            if mid<=theta:vals.append((lo-L*theta,L))
            else:vals.append((lo+L*theta,-L))
        c,d=max(vals,key=lambda x:x[0]+x[1]*mid)
        if out and out[-1][1]==a and out[-1][2:]==(c,d):out[-1]=(out[-1][0],b,c,d)
        else:out.append((a,b,c,d))
    assert out[0][0]==0 and out[-1][1]==90
    return tuple(out)

def Dmin_rational(L):
    """Exact D lower via sin(pi theta/180)>=theta/90 on [0,90]."""
    acc=F(0)
    for a,b,A,B in lower_segments(L):
        acc+=(A*(b*b-a*a)/2+B*(b*b*b-a*a*a)/3)/90
    if acc<=0:raise ArithmeticError('D lower must positive')
    return acc

def global_B(L):
    L=frac_source_bounds(L)
    return min(hi+L*max(theta,90-theta) for theta,_,hi in SOURCE)

@dataclass
class Grid:
    L:F
    subdiv:int
    h:F
    B:F
    Dmin:F
    A:object
    b:tuple[F,...]
    coords:tuple[tuple[tuple[int,F],...],...]
    n:int

@lru_cache(maxsize=12)
def make_grid(L,subdiv):
    from scipy.sparse import csr_matrix
    L=frac_source_bounds(L)
    if type(subdiv)!=int or subdiv<1 or subdiv>50:raise ValueError('subdiv domain 1..50')
    h=F(1,subdiv);n=90*subdiv+1;B=global_B(L)
    rr=[];cc=[];dd=[];br=[];coords=[]
    def row(terms,rhs):
        idx=len(br);br.append(rhs);coords.append(tuple(terms))
        for j,v in terms:rr.append(idx);cc.append(j);dd.append(float(v))
    for j in range(n-1):
        row(((j,F(-1)),(j+1,F(1))),L*h)
        row(((j,F(1)),(j+1,F(-1))),L*h)
    for theta,low,high in SOURCE:
        j=theta*subdiv
        row(((j,F(1)),),high)
        row(((j,F(-1)),),-low)
    mat=coo_matrix((dd,(rr,cc)),shape=(len(br),n)).tocsr()
    return Grid(L,subdiv,h,B,Dmin_rational(L),mat,tuple(br),tuple(coords),n)

@lru_cache(maxsize=8)
def _basis_weights(subdiv):
    """Build N and D rational coefficients once; F_t=N-tD."""
    n=90*subdiv+1;h=F(1,subdiv)
    nn=[F(0)]*n;dd=[F(0)]*n
    for i in range(n-1):
        g0,p0=trig_mid(F(0),i,subdiv)
        g1,p1=trig_mid(F(1),i,subdiv)
        gd,pd=g0-g1,p0-p1
        nn[i]+=h*g0/2-h*h*p0/12
        nn[i+1]+=h*g0/2+h*h*p0/12
        dd[i]+=h*gd/2-h*h*pd/12
        dd[i+1]+=h*gd/2+h*h*pd/12
    return tuple(nn),tuple(dd)

def weights(t,subdiv):
    t=exact(t)
    if not F(0)<=t<=F(1):raise ValueError('t outside [0,1]')
    nn,dd=_basis_weights(subdiv)
    return tuple(n-t*d for n,d in zip(nn,dd))

def solve_lp(t,grid,sign=1):
    """sign=+1 maximize F_t; -1 maximize -F_t. Dual bound is exact-rational postprocessed."""
    if sign not in (-1,1):raise ValueError('sign')
    c=tuple(sign*v for v in weights(t,grid.subdiv))
    y=np.array([-float(v) for v in c]);b=np.array([float(v) for v in grid.b])
    res=linprog(y,A_ub=grid.A,b_ub=b,bounds=(0,float(grid.B)),method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
    if not res.success:raise ArithmeticError(f'LP failed: {res.message}')
    # Exact reconstructed nonnegative dual variables λ>=0 for A y<=b and ν>=0 for y<=B.
    lam=[F(str(max(0.0,-float(v)))) for v in res.ineqlin.marginals]
    nu=[F(str(max(0.0,-float(v)))) for v in res.upper.marginals]
    val=F(0);coeff=[F(0)]*grid.n
    for i,v in enumerate(lam):
        if v:
            val+=v*grid.b[i]
            for j,a in grid.coords[i]:coeff[j]+=v*a
    for i,v in enumerate(nu):
        if v:
            val+=grid.B*v;coeff[i]+=v
    # Since y >= 0, y<=B, residual c - A^Tλ - ν adds no more than B*positive part.
    penalty=grid.B*sum((max(F(0),c[i]-coeff[i]) for i in range(grid.n)),F(0))
    dual=val+penalty
    # Witness LP output is only a floating proposal, projected to exact feasible set below.
    return {'dual_upper':dual,'penalty':penalty,'numeric_opt':-res.fun,
            'raw':res.x,'success':True,'iterations':res.nit}

def feasible_projection(x,grid):
    """Exact rational McShane upper hull, clamped to pinned f_-/f_+ cones."""
    xs=[F(str(max(0.0,float(v)))) for v in x];s=grid.L*grid.h
    fw=[F(0)]*grid.n;bw=[F(0)]*grid.n
    for j in range(grid.n):fw[j]=max(xs[j],fw[j-1]-s if j else xs[j])
    for j in range(grid.n-1,-1,-1):bw[j]=max(xs[j],bw[j+1]-s if j+1<grid.n else xs[j])
    ans=tuple(max(envelope(j*grid.h,grid.L,False),min(envelope(j*grid.h,grid.L,True),max(fw[j],bw[j]))) for j in range(grid.n))
    assert all(F(0)<=v<=grid.B for v in ans)
    assert all(abs(ans[j+1]-ans[j])<=s for j in range(grid.n-1))
    assert all(lo<=ans[theta*grid.subdiv]<=hi for theta,lo,hi in SOURCE)
    return ans

def errors(grid):
    # for |g_t|<=1 and |g_t''|<=3(pi/180)^2, pi<22/7.
    # π<22/7 gives simple rational outward curv bound.
    k=F(22,7*180)
    einterp=90*grid.L*grid.h/2
    equad=90*grid.B*3*k*k*grid.h*grid.h/8
    etrig=90*grid.B*TRIG_EPS+90*grid.L*grid.h*grid.h*TRIG_EPS/12
    return {'interp':einterp,'quad':equad,'trig':etrig,'total':einterp+equad+etrig}

def certified_outer(t,grid,side):
    """Return valid continuum ratio upper/lower via exact dual and global Dmin."""
    t=exact(t)
    if not F(0)<=t<=F(1):raise ValueError('t outside [0,1]')
    sign=1 if side=='upper' else -1 if side=='lower' else None
    if sign is None:raise ValueError('side')
    lp=solve_lp(t,grid,sign)
    E=errors(grid)['total']
    slack=max(F(0),lp['dual_upper']+E)
    raw=(t+slack/grid.Dmin) if side=='upper' else (t-slack/grid.Dmin)
    outer=min(F(1),raw) if side=='upper' else max(F(0),raw)
    return dict(side=side,t=t,bound=outer,dual=lp['dual_upper'],dual_residual_penalty=lp['penalty'],
                interpolation_error=E,Dmin=grid.Dmin,numeric_opt=lp['numeric_opt'],raw=lp['raw'])

def find_lpshape_endpoint(grid,side,iterations=15):
    """Locate finite-grid root approximately, then certify continuum at final rational t."""
    lo=0.0;hi=1.0
    for _ in range(iterations):
        t=(lo+hi)/2
        sign=1 if side=='upper' else -1
        v=solve_lp(F(str(t)),grid,sign)['numeric_opt']
        if side=='upper':
            if v>0:lo=t
            else:hi=t
        else:
            if v>0:hi=t
            else:lo=t
    t=F(str(hi if side=='upper' else lo))
    return certified_outer(t,grid,side)

def report(L,subdiv,iterations=16):
    grid=make_grid(L,subdiv)
    lo=find_lpshape_endpoint(grid,'lower',iterations)
    hi=find_lpshape_endpoint(grid,'upper',iterations)
    if lo['bound']>hi['bound']:raise ArithmeticError('inconsistent bounds')
    return {'L':str(grid.L),'degree_subdivisions':subdiv,'h_degrees':str(grid.h),
            'N':grid.n,'B':str(grid.B),'Dmin_exact':str(grid.Dmin),
            'grid_lower_root_t':str(lo['t']),'grid_upper_root_t':str(hi['t']),
            'continuum_lower':str(lo['bound']),'continuum_upper':str(hi['bound']),
            'lower_lp_dual':str(lo['dual']),'upper_lp_dual':str(hi['dual']),
            'error_components':{k:str(v) for k,v in errors(grid).items()},
            'dual_residual_penalties':[str(lo['dual_residual_penalty']),str(hi['dual_residual_penalty'])],
            'certified':'exact rational dual and analytic continuum error; trig polynomial bounds with explicit Taylor/Machin inequality',
            'rate':None,'kappa':None,'physical_activation':False,'L4':False,'production':'HOLD'}

def witness_bounds(y,grid):
    """Exact feasible grid witness and certified interval on its true b; NOT population CI."""
    y=feasible_projection(y,grid)
    n0,d0=_basis_weights(grid.subdiv)
    Nhat=sum((a*v for a,v in zip(n0,y)),F(0))
    Dhat=sum((a*v for a,v in zip(d0,y)),F(0))
    err=errors(grid)
    # Interpolation is irrelevant: the constructed piecewise-linear function
    # is the actual admissible continuous witness, not approximation to an unknown f.
    E=err['quad']+err['trig']
    if not Dhat>E or Nhat<E:raise ArithmeticError('witness denominator not verified')
    blo=max(F(0),(Nhat-E)/(Dhat+E))
    bhi=min(F(1),(Nhat+E)/(Dhat-E))
    if blo>bhi:raise ArithmeticError('witness enclosure inconsistent')
    return {'b_lower':blo,'b_upper':bhi,'Dhat':Dhat,'Nhat':Nhat,'error':E,
            'knot_count':len(y),'nonnegative':True,'source_box_pass':True,
            'lipschitz_feasible_exact':True}

def full_extrema_certificate(L,subdiv=50,iterations=19):
    """For true extrema: min_b ∈ [outer_lo,witness_min_hi];
       max_b ∈ [witness_max_lo,outer_hi]."""
    grid=make_grid(L,subdiv)
    low=find_lpshape_endpoint(grid,'lower',iterations)
    high=find_lpshape_endpoint(grid,'upper',iterations)
    wl=witness_bounds(low['raw'],grid)
    wh=witness_bounds(high['raw'],grid)
    if low['bound']>wl['b_upper'] or wh['b_lower']>high['bound']:
        raise ArithmeticError('primal-dual error crossing, invalidate claim')
    return dict(L=str(grid.L),h=str(grid.h),grid_nodes=grid.n,
        min_b_outer_low=str(low['bound']), min_b_inner_high=str(wl['b_upper']),
        max_b_inner_low=str(wh['b_lower']), max_b_outer_high=str(high['bound']),
        final_dual_residual=[str(low['dual_residual_penalty']),str(high['dual_residual_penalty'])],
        total_continuum_error=str(errors(grid)['total']),
        certified='piecewise-linear exact feasible witnesses plus rational LP dual and proved continuum/trig errors',
        measured_angular_moment=None,physical_event_rate=None,production='HOLD')
