"""PHYS48: exact rational Coulomb centrifugal forbidden-region ACTION enclosures.

Source-locked original H(1s)+H(1s) h=-Delta/2-1/r-(1+1/s)e^-2s,
R=kappa=7/10. For the CENTRAL reference radial Coulomb equation only:
  q_l(r)=kappa²+2/r-l(l+1)/r²
  Vbar_l(r)=-q_l(r), turning root q_l(rt)=0,
  A_l(20)=integral_20^rt sqrt(Vbar_l(r)) dr, when rt>20.

An EXACT monotone rational Riemann enclosure A_lo<=A_l<=A_hi
follows because Vbar>0 and decreases on [20,rt].
This is a rigorously calculated WKB ACTION INTEGRAL, **not** a
verified transmission amplitude or infinite-l Coulomb Green estimate.
No extra physical source, no artificial physical channel cutoff.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from math import isqrt
from multiprocessing import get_context
from pathlib import Path
from time import perf_counter
import hashlib

SOURCE_SHA="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
K=F(7,10)
K2=K*K
B=F(20)
SCHEMA="WU088_HH_PHYS48_COULOMB_BARRIER_RATIONAL_ACTION_V1"


def sqrt_floor(x:F, digits:int=18)->F:
    """Exact positive square root floor to fixed decimal digits."""
    if not isinstance(x,F) or x<0 or type(digits) is not int or not 8<=digits<=28:
        raise ValueError("nonnegative rational and 8..28 digits")
    fac=10**digits
    return F(isqrt(x.numerator*fac*fac//x.denominator),fac)


def sqrt_ceil(x:F,digits:int=18)->F:
    lo=sqrt_floor(x,digits)
    if lo*lo==x:return lo
    return lo+F(1,10**digits)


def outward_decimal(x:F,digits:int=18,above:bool=True)->str:
    if not isinstance(x,F) or x<0 or not 8<=digits<=28:
        raise ValueError("nonnegative Fraction and precision")
    scaled=x*10**digits
    k=scaled.numerator//scaled.denominator
    if above and F(k,1)!=scaled:k+=1
    return f"{k//10**digits}.{k%10**digits:0{digits}d}"


def barrier(x:F,ell:int)->F:
    if not isinstance(x,F) or x<=0 or type(ell) is not int or ell<0:
        raise ValueError("positive Bohr radius and nonnegative integer ell")
    L=ell*(ell+1)
    return F(L,x*x)-2/x-K2


def turning_bracket(ell:int,digits:int=20)->tuple[F,F]:
    """Exact rational bracket for the positive Coulomb turning point."""
    if type(ell) is not int or ell<0 or ell>2000:
        raise ValueError("physical nonnegative bounded angular momentum")
    root_arg=1+K2*ell*(ell+1)
    lo=(sqrt_floor(root_arg,digits)-1)/K2
    hi=(sqrt_ceil(root_arg,digits)-1)/K2
    assert lo<=hi
    if ell:
        assert barrier(hi,ell)<=0
        assert barrier(lo,ell)>=0
    return lo,hi


def mesh(Ba:F,last:F,n:int,grading:str)->list[F]:
    """Exact endpoints; graded mesh clusters toward the turning radius."""
    if n<4 or n>4096 or Ba>last or grading not in ("uniform","quadratic","cubic"):
        raise ValueError("invalid rational partition")
    p={"uniform":1,"quadratic":2,"cubic":3}[grading]
    return [Ba+(last-Ba)*(1-(1-F(i,n))**p) for i in range(n+1)]


def _candidate(job:tuple)->dict:
    ell,n,grading,digits=job
    begin=perf_counter()
    low_turn,high_turn=turning_bracket(ell,digits+2)
    if high_turn<=B:
        return {"ell":ell,"turning_lo":str(low_turn),"turning_hi":str(high_turn),
                "barrier_at_B_exact":str(barrier(B,ell)),
                "integration_last":str(B),"mesh":grading,"subintervals":n,
                "action_lower":"0.0","action_upper":"0.0",
                "interval_width":"0.0","maximum_partition_leaf_gap":"0.0",
                "barrier_exists_at_B":False,
                "_low":F(0),"_high":F(0),"elapsed_s":perf_counter()-begin}
    if low_turn<=B:
        raise ArithmeticError("turning point straddles original boundary; refine precision")
    if not barrier(B,ell)>0:
        raise ArithmeticError("positive centrifugal barrier must occur at original B")
    # A coarse integer cut leaves an unnecessarily wide uncertified
    # turning-point sliver, particularly when r_turn is near an integer.
    # Take the exact rational decimal floor of the rigorously enclosed
    # turning point instead. No floating approximation enters the proof.
    endpoint_scale=10**8
    scaled=low_turn*endpoint_scale
    last=F(scaled.numerator//scaled.denominator,endpoint_scale)
    if last<B:last=B
    if last>low_turn:
        raise ArithmeticError("turning point lower irrational bound violated")
    if grading=="adaptive":
        low,hi,worst_leaf=adaptive_action(ell,last,n,digits)
        remaining_root=sqrt_ceil(barrier(last,ell),digits)
    else:
        r=mesh(B,last,n,grading)
        vals=[barrier(x,ell) for x in r]
        if any(x<0 for x in vals) or any(a<b for a,b in zip(vals,vals[1:])):
            raise ArithmeticError("barrier real, nonnegative and decreasing requirement fails")
        floor_root=[sqrt_floor(x,digits) for x in vals]
        ceil_root=[(u if u*u==v else u+F(1,10**digits))
                   for u,v in zip(floor_root,vals)]
        low=sum(((b-a)*rv for a,b,rv in zip(r,r[1:],floor_root[1:])),F(0))
        hi=sum(((b-a)*rv for a,b,rv in zip(r,r[1:],ceil_root[:-1])),F(0))
        worst_leaf=max(((b-a)*(aa-bb) for (a,b),aa,bb in
                        zip(zip(r,r[1:]),ceil_root[:-1],floor_root[1:])),default=F(0))
        remaining_root=ceil_root[-1]
    # Until exact irrational rt, barrier decreases to zero.
    hi+=(high_turn-last)*remaining_root
    if not 0<=low<=hi:
        raise ArithmeticError("nonsensical certified forbidden action ordering")
    return {
        "ell":ell,"turning_lo":str(low_turn),"turning_hi":str(high_turn),
        "turning_radius_lo":outward_decimal(low_turn,14,False),
        "turning_radius_hi":outward_decimal(high_turn,14,True),
        "barrier_at_B_exact":str(barrier(B,ell)),
        "integration_last":str(last),"mesh":grading,"subintervals":n,
        "action_lower":outward_decimal(low,14,False),
        "action_upper":outward_decimal(hi,14,True),
        "interval_width":outward_decimal(hi-low,14,True),
        "maximum_partition_leaf_gap":outward_decimal(worst_leaf,14,True),
        "barrier_exists_at_B":True,
        "_low":low,"_high":hi,"elapsed_s":perf_counter()-begin,
    }


def source_barrier_actions(frozen:str|Path,
         ells:tuple[int,...]=(14,15,20,21,24,28,33,41,61,80,120),
         n:int=256,grading:str="quadratic",digits:int=18,
         workers:int=1)->dict:
    """Prove turning radius and forbidden ACTION, without wave amplitude promotion."""
    frozen=Path(frozen)
    original=hashlib.sha256(frozen.read_bytes()).hexdigest()
    if original!=SOURCE_SHA:
        raise ValueError("wrong immutable original H-H frozen source SHA256")
    if not ells or len(set(ells))!=len(ells) or any(
        type(ell) is not int or ell<0 or ell>2000 for ell in ells):
        raise ValueError("distinct angular-momentum channels in 0..2000")
    if not 4<=n<=4096 or grading not in ("uniform","quadratic","cubic","adaptive"):
        raise ValueError("supported exact rational quadrature")
    if not 12<=digits<=24 or workers not in (1,2,3,4):
        raise ValueError("precision and multiprocessing bounds")
    started=perf_counter()
    jobs=[(ell,n,grading,digits) for ell in ells]
    if workers==1:
        rows=list(map(_candidate,jobs))
    else:
        with ProcessPoolExecutor(max_workers=workers,mp_context=get_context("forkserver")) as pool:
            rows=list(pool.map(_candidate,jobs))
    certified=[{k:v for k,v in row.items() if not k.startswith("_") and k!="elapsed_s"}
               for row in rows]
    # The ACTION interval itself is from exact monotone integrand inequalities,
    # not from a WKB approximation. Relation to actual H_l is only diagnostic.
    return {
        "schema":SCHEMA,
        "original_source_sha256":original,
        "fixed_reference":"k=7/10, central Coulomb -1/r with physical original R=7/10",
        "physical_domain":"forbidden interval [B=20,r_turn(ell)] if q_ell(20)<0",
        "centrifugal_barrier":"ell(ell+1)/r²-2/r-49/100",
        "turning_radius_formula":"r_turn=(sqrt(1+(49/100)ell(ell+1))-1)/(49/100)",
        "barrier_action":"integral_20^rturn sqrt(ell(ell+1)/r²-2/r-49/100)dr",
        "rigorous_interval_method":"decreasing positive barrier; exact right-rectangle lower and left-rectangle upper plus bounded turning-point sliver; outward isqrt and exact Fraction partitions; adaptive selects largest exact leaf gap with proof-preserving midpoint split",
        "ell_values":list(ells),"mesh_type":grading,"subintervals":n,
        "sqrt_fixed_decimal_digits":digits,
        "action_enclosures":certified,
        "workers":workers,"elapsed_s":perf_counter()-started,
        "claim_status":"CERTIFIED_CENTRAL_COULOMB_FORBIDDEN_ACTION_ONLY",
        "not_certified":[
            "physical large-l outgoing Coulomb Green operator/infinite-dimensional Volterra contraction",
            "WKB barrier penetration probability or actual Coulomb H amplitude from action alone",
            "screened noncentral propagated angular tail or full outgoing DtN",
            "original driven xi=F*y-phi source and origin, incoming adjoint",
            "physical sigma(E), Maxwellian H-H rate k(T), rei_bianchi HH_R10",
        ],
    }


def adaptive_action(ell:int,last:F,n:int,digits:int=18)->tuple[F,F,F]:
    """Certified true-child-gap priority bisection of monotone sqrt barrier.

    A child refines its parent's lower/upper bound. The heap priority
    is the *actual exact rational* cell interval width, not a float proxy.
    This reuses the true-child positive-envelope scheduling pattern from
    bass_cr PR71, with no atomic/REI physical data imported.
    """
    from heapq import heappop,heappush
    if not 4<=n<=4096 or last<B:raise ValueError("adaptive finite mesh")
    if last==B:return F(0),F(0),F(0)
    cache={}
    def roots(r):
        if r not in cache:
            z=barrier(r,ell)
            if z<0:raise ArithmeticError("adaptive probe outside centrifugal barrier")
            down=sqrt_floor(z,digits)
            up=down if down*down==z else down+F(1,10**digits)
            cache[r]=(down,up)
        return cache[r]
    def cell(a,b):
        ra,rb=roots(a),roots(b)
        low=(b-a)*rb[0]
        high=(b-a)*ra[1]
        if low>high:raise ArithmeticError("inverted child envelope")
        return (low,high,high-low)
    total_lo,total_hi,_=cell(B,last)
    heap=[]
    ident=0
    def put(a,b):
        nonlocal ident
        lo,hi,width=cell(a,b)
        heappush(heap,(-width,ident,a,b,lo,hi))
        ident+=1
    put(B,last)
    while len(heap)<n:
        negwidth,_,a,b,old_lo,old_hi=heappop(heap)
        mid=(a+b)/2
        if not a<mid<b:raise ArithmeticError("nonpositive rational split")
        lc=cell(a,mid)
        rc=cell(mid,b)
        total_lo+=lc[0]+rc[0]-old_lo
        total_hi+=lc[1]+rc[1]-old_hi
        put(a,mid)
        put(mid,b)
        if not 0<=total_lo<=total_hi:raise ArithmeticError("adaptive certified bound lost")
    # Recheck exact complete union rather than assuming the heap contains
    # the original coverage. It cannot create physical derivative jumps.
    intervals=sorted((a,b) for _,_,a,b,_,_ in heap)
    if intervals[0][0]!=B or intervals[-1][1]!=last or any(
         b!=c for (_,b),(c,_) in zip(intervals,intervals[1:])):
        raise ArithmeticError("missing adaptive interval coverage")
    chk_lo=chk_hi=F(0)
    for _,_,a,b,low,hi in heap:
        chk_lo+=low
        chk_hi+=hi
    if chk_lo!=total_lo or chk_hi!=total_hi:
        raise ArithmeticError("heap/source accumulator differs")
    return total_lo,total_hi,max(-row[0] for row in heap)
