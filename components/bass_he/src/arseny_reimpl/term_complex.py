from __future__ import annotations
from dataclasses import dataclass
import cmath, math
import numpy as np
from .term_real import trace_real_curve

State = tuple[int,int,int]

@dataclass(frozen=True)
class ComplexTermPoint:
    N:int; l:int; m:int; R:complex; Z1:float; Z2:float
    p:complex; separation_lambda:complex; energy_hartree:complex
    residual_radial:complex; residual_angular:complex
    iterations:int; cf_depth:int
    @property
    def max_residual(self)->float:
        return max(abs(self.residual_radial),abs(self.residual_angular))

@dataclass(frozen=True)
class BranchPointSolution:
    state_a:State; state_b:State; series:str; R:complex
    p_a:complex; lambda_a:complex; p_b:complex; lambda_b:complex
    energy_a:complex; energy_b:complex; spectral_residual_norm:float
    energy_split:complex; iterations:int; cf_depth:int
    @property
    def coalescence_error(self)->float:
        return max(self.spectral_residual_norm,abs(self.energy_split))

def _validate_state(state:State)->None:
    N,l,m=state
    if N<1 or not(0<=l<N) or not(0<=m<=l):
        raise ValueError("invalid united-atom state")

def classify_branch_pair(a:State,b:State)->str:
    _validate_state(a); _validate_state(b)
    N,l,m=a
    if b==(N+1,l,m): return "S"
    if b==(N+1,l+1,m): return "Q"
    return "GENERIC"

def complex_energy_from_p(p:complex,R:complex)->complex:
    if abs(R)==0: raise ValueError("R must be nonzero")
    return -2*p*p/(R*R)

def _radial_coefficients(s,p,lam,*,Z1,Z2,R,m):
    if abs(p)==0: raise ValueError("p must be nonzero")
    a=(Z1+Z2)*R
    sigma=a/(2*p)-m-1
    alpha=(s+1)*(s+m+1)
    beta=2*s*(s+2*p-sigma)-(m+sigma)*(m+1)-2*p*sigma+lam
    gamma=(s-1-sigma)*(s-1-m-sigma)
    return complex(alpha),beta,gamma

def _angular_coefficients(s,p,lam,*,Z1,Z2,R,m):
    if abs(p)==0: raise ValueError("p must be nonzero")
    b=(Z2-Z1)*R
    rho=(s+2*m+1)*(b-2*p*(s+m+1))/(2*(s+m)+3)
    chi=(s+m)*(s+m+1)-lam
    delta=0j if s==0 else s*(b+2*p*(s+m))/(2*(s+m)-1)
    return rho,chi,delta

def _matched_cf_residual(n0,coeff_fn,p,lam,*,Z1,Z2,R,m,depth=96):
    if depth<=n0+4: raise ValueError("continued-fraction depth too small")
    def c(s): return coeff_fn(s,p,lam,Z1=Z1,Z2=Z2,R=R,m=m)
    _,low,_=c(0); tiny=1e-280
    for s in range(1,n0+1):
        Aprev,_,_=c(s-1); _,B,C=c(s)
        if abs(low)<tiny: raise FloatingPointError("finite CF pole")
        low=B-C*Aprev/low
    _,high,_=c(depth)
    for s in range(depth-1,n0,-1):
        A,B,_=c(s); _,_,Cnext=c(s+1)
        if abs(high)<tiny: raise FloatingPointError("tail CF pole")
        high=B-A*Cnext/high
    A0,_,_=c(n0); _,_,Cnext=c(n0+1)
    if abs(high)<tiny: raise FloatingPointError("tail CF pole")
    return low-A0*Cnext/high

def complex_term_residuals(state,R,p,lam,*,Z1=1.,Z2=2.,depth=96):
    _validate_state(state)
    if Z1==Z2: raise NotImplementedError("symmetric angular recurrence outside DR4")
    N,l,m=state
    return np.array([
        _matched_cf_residual(N-l-1,_radial_coefficients,p,lam,Z1=Z1,Z2=Z2,R=R,m=m,depth=depth),
        _matched_cf_residual(l-m,_angular_coefficients,p,lam,Z1=Z1,Z2=Z2,R=R,m=m,depth=depth)
    ],dtype=complex)

def _complex_jacobian(fun,z,rel_step=1e-6):
    f0=np.asarray(fun(z),dtype=complex)
    J=np.empty((len(f0),len(z)),dtype=complex)
    for j in range(len(z)):
        h=rel_step*max(abs(z[j]),1.0)
        zp=z.copy(); zm=z.copy(); zp[j]+=h; zm[j]-=h
        J[:,j]=(fun(zp)-fun(zm))/(2*h)
    return J

def solve_complex_term(state,R,*,Z1=1.,Z2=2.,p0,lam0,depth=96,tol=1e-10,max_iterations=80):
    _validate_state(state)
    if abs(R)==0: raise ValueError("R must be nonzero")
    x=np.array([complex(p0),complex(lam0)],dtype=complex)
    def fun(xx): return complex_term_residuals(state,R,xx[0],xx[1],Z1=Z1,Z2=Z2,depth=depth)
    for it in range(1,max_iterations+1):
        f=fun(x); fn=float(np.max(np.abs(f)))
        if not math.isfinite(fn): raise RuntimeError("non-finite complex TERM residual")
        if fn<=tol:
            N,l,m=state
            return ComplexTermPoint(N,l,m,R,Z1,Z2,x[0],x[1],complex_energy_from_p(x[0],R),f[0],f[1],it,depth)
        J=_complex_jacobian(fun,x)
        try: dx=np.linalg.solve(J,-f)
        except np.linalg.LinAlgError as exc: raise RuntimeError("singular complex TERM Jacobian") from exc
        alpha=1.; accepted=False
        for _ in range(40):
            xn=x+alpha*dx
            try: fn2=float(np.max(np.abs(fun(xn))))
            except Exception: fn2=float("inf")
            if math.isfinite(fn2) and fn2<fn:
                x=xn; accepted=True; break
            alpha*=0.5
        if not accepted: raise RuntimeError(f"complex TERM failed at R={R!r}, state={state}, residual={fn:.3e}")
    raise RuntimeError(f"complex TERM did not converge at R={R!r}, state={state}")

def _real_anchor_grid(R_anchor):
    if R_anchor<=0: raise ValueError("real anchor must be positive")
    if R_anchor<=0.01: return [R_anchor]
    n=max(2,int(math.ceil((R_anchor-0.01)/0.15))+1)
    return list(np.linspace(0.01,R_anchor,n))

def continue_complex_from_real(state,R_target,*,Z1=1.,Z2=2.,depth=96,tol=1e-9,max_complex_step=0.05):
    _validate_state(state); Rt=complex(R_target)
    if Rt.real<=0: raise ValueError("requires Re(R)>0")
    real_pts=trace_real_curve(*state,_real_anchor_grid(Rt.real),Z1=Z1,Z2=Z2,depth=depth,tol=max(tol,1e-9))
    anchor=real_pts[-1]
    if abs(Rt.imag)==0:
        return ComplexTermPoint(*state,Rt,Z1,Z2,complex(anchor.p),complex(anchor.separation_lambda),
            complex(anchor.energy_hartree),complex(anchor.residual_radial),complex(anchor.residual_angular),
            anchor.iterations,depth)
    nsteps=max(1,int(math.ceil(abs(Rt.imag)/max_complex_step)))
    hist=[]
    Rprev=complex(anchor.R); pprev=complex(anchor.p); lprev=complex(anchor.separation_lambda)
    for k in range(1,nsteps+1):
        R=complex(Rt.real,Rt.imag*k/nsteps)
        if len(hist)>=2:
            Ra,pa,la=hist[-2]; Rb,pb,lb=hist[-1]
            f=(R-Rb)/(Rb-Ra); pg=pb+f*(pb-pa); lg=lb+f*(lb-la)
        elif len(hist)==1:
            Rb,pb,lb=hist[-1]; pg=pb*R/Rb; lg=lb
        else:
            pg=pprev*R/Rprev; lg=lprev
        pt=solve_complex_term(state,R,Z1=Z1,Z2=Z2,p0=pg,lam0=lg,depth=depth,tol=tol,max_iterations=100)
        hist.append((R,pt.p,pt.separation_lambda))
        Rprev,pprev,lprev=R,pt.p,pt.separation_lambda
    return pt

def _branch_system(z,a,b,*,Z1,Z2,depth):
    pa,la,pb,lb,R=z
    fa=complex_term_residuals(a,R,pa,la,Z1=Z1,Z2=Z2,depth=depth)
    fb=complex_term_residuals(b,R,pb,lb,Z1=Z1,Z2=Z2,depth=depth)
    return np.array([fa[0],fa[1],fb[0],fb[1],pa*pa-pb*pb],dtype=complex)

def solve_branch_point(state_a,state_b,R0,*,Z1=1.,Z2=2.,depth=96,tol=1e-9,max_iterations=50):
    _validate_state(state_a); _validate_state(state_b); R0=complex(R0)
    a0=continue_complex_from_real(state_a,R0,Z1=Z1,Z2=Z2,depth=depth,tol=max(tol,1e-9))
    b0=continue_complex_from_real(state_b,R0,Z1=Z1,Z2=Z2,depth=depth,tol=max(tol,1e-9))
    z=np.array([a0.p,a0.separation_lambda,b0.p,b0.separation_lambda,R0],dtype=complex)
    def fun(zz): return _branch_system(zz,state_a,state_b,Z1=Z1,Z2=Z2,depth=depth)
    for it in range(1,max_iterations+1):
        f=fun(z); fn=float(np.max(np.abs(f)))
        if fn<=tol:
            pa,la,pb,lb,R=z
            Ea=complex_energy_from_p(pa,R); Eb=complex_energy_from_p(pb,R)
            return BranchPointSolution(state_a,state_b,classify_branch_pair(state_a,state_b),R,pa,la,pb,lb,Ea,Eb,fn,Ea-Eb,it,depth)
        J=_complex_jacobian(fun,z)
        try: dz=np.linalg.solve(J,-f)
        except np.linalg.LinAlgError as exc: raise RuntimeError("singular branch-point Jacobian") from exc
        alpha=1.; accepted=False
        for _ in range(40):
            zn=z+alpha*dz
            try: fn2=float(np.max(np.abs(fun(zn))))
            except Exception: fn2=float("inf")
            if math.isfinite(fn2) and fn2<fn:
                z=zn; accepted=True; break
            alpha*=0.5
        if not accepted: raise RuntimeError(f"branch-point Newton failed for {state_a}<->{state_b}")
    raise RuntimeError(f"branch-point solve did not converge for {state_a}<->{state_b}")

def s_series_limit_point(l,m,*,Z1=1.,Z2=2.,upper=True):
    if l<0 or m<0 or m>l: raise ValueError("invalid l,m")
    re=(l+0.5)**2-0.5*(m+1)**2
    im=(m+1)*math.sqrt(2*(l+0.5)**2-0.25*(m+1)**2)
    return complex(re,im if upper else -im)/(Z1+Z2)

def s_series_initial_guess(l,m,*,Z1=1.,Z2=2.,upper=True):
    if l<0 or m<0 or m>l: raise ValueError("invalid l,m")
    phase=math.pi*(m+1)/(2*l+1)
    if not upper: phase=-phase
    return ((l+0.5)**2/(Z1+Z2))*cmath.exp(1j*phase)
