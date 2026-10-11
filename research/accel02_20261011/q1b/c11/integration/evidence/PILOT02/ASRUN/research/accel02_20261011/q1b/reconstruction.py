"""Q1B local positive two-moment closure; production/native binding NOT_IMPLEMENTED.

N is reference-volume photon number, U is photon energy (eV/reference cm^3),
E=R*q.  The caller supplies the current active support [a,b]; this module does
not infer a source cap or erase sub-10-eV photons.  A monotone source-entry cap
requires the separate geometry contract.  Only strict-interior Jacobians are
implemented.  Empty/endpoint handling is explicit and is NOT a BDF start rule.

Opacity kernel is kappa(q)=c*sigma(R*q) at fixed time. Temporary probability-
coordinate Gauss quadrature integrates both depletion moments and their
covariances. Its two declared orders provide a local diagnostic, not a rigorous
error bound or a physical opacity/closure accuracy certificate.
"""
from dataclasses import dataclass
import math
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.optimize import brentq

NATIVE_BINDING = "NOT_IMPLEMENTED"


class InvalidCone(ValueError):
    pass


class UndefinedJacobian(ValueError):
    pass


class TraceRequired(ValueError):
    pass


class QuadratureNotConverged(ArithmeticError):
    pass


def _log_integral(t, L):
    """log integral_0^L exp(t*x) dx, including t=0 explicitly."""
    z = t*L
    if t == 0:
        return math.log(L)
    if abs(z) < 1e-5:
        return math.log(L)+math.log1p(z/2+z*z/6+z**3/24+z**4/120)
    if z > 0:
        return z+math.log(-math.expm1(-z))-math.log(t)
    return math.log(-math.expm1(z))-math.log(-t)


def _log_mean_power(p, k, a, b):
    """log E[q**k], avoiding subtraction of two huge log normalizers."""
    if k == 0:
        return 0.
    L = math.log1p((b-a)/a)
    if p > 0 and p+k > 0 and min(p,p+k)*L > 0.01:
        return (k*math.log(b)+math.log1p(-k/(p+k))
                +math.log(-math.expm1(-(p+k)*L))
                -math.log(-math.expm1(-p*L)))
    if p < 0 and p+k < 0 and min(-p,-p-k)*L > 0.01:
        return (k*math.log(a)+math.log1p(-k/(p+k))
                +math.log(-math.expm1((p+k)*L))
                -math.log(-math.expm1(p*L)))
    # This branch includes p=0 and p=-k, each using the exact t=0 limit.
    return k*math.log(a)+_log_integral(p+k,L)-_log_integral(p,L)


def _unit_moments(t,count):
    """E[y**k] for exp(t*y) on [0,1], bounded stable series/recurrence."""
    if abs(t)<=1.:
        terms=[t**n/math.factorial(n) for n in range(40)]
        norm=math.fsum(term/(n+1) for n,term in enumerate(terms))
        return [math.fsum(term/(n+k+1) for n,term in enumerate(terms))/norm
                for k in range(count+1)]
    A=(1./(-math.expm1(-t)) if t>0 else math.exp(t)/math.expm1(t))
    moments=[1.]
    for k in range(1,count+1):
        moments.append(A-k/t*moments[-1])
    return moments


def _mean_cell_fraction(t,L,a,b):
    """(E[q]-a)/(b-a); retains cell-relative information for thin support.

    Here t=p*L. For L<=0.01, expand expm1(L*y)/expm1(L) through
    y**7. The omitted numerator term is <=exp(.01)*.01**7/8!.
    This is a numerical evaluation, not a change of reconstruction closure.
    """
    if L<=0.01:
        moments=_unit_moments(t,7)
        numerator=math.fsum(L**(k-1)/math.factorial(k)*moments[k] for k in range(1,8))
        return numerator/(math.expm1(L)/L)
    return math.expm1(_log_mean_power(t/L,1.,a,b)-math.log(a))/math.expm1(L)


@dataclass(frozen=True)
class CellSpectrum:
    N: float
    U: float
    R: float
    a: float
    b: float
    mean_q: float | None
    p: float | None
    status: str
    jacobian_status: str

    def moment(self, k):
        """Exact closure integral q**k F dlnq (floating analytic evaluation)."""
        if self.status in ("EMPTY","ZERO_WIDTH_EMPTY"):
            return 0.
        if not math.isfinite(k):
            raise ValueError("Nonfinite moment power")
        if k == 0:
            return self.N
        if k == 1:
            return self.U/self.R
        if self.p is None:
            return self.N*self.mean_q**k
        return self.N*math.exp(_log_mean_power(self.p,k,self.a,self.b))

    def cdf(self, q):
        if self.status != "INTERIOR":
            raise ValueError("CDF requires strict interior closure")
        if q <= self.a:
            return 0.
        if q >= self.b:
            return 1.
        x,L,p=math.log1p((q-self.a)/self.a),math.log1p((self.b-self.a)/self.a),self.p
        if p == 0:
            return x/L
        if p > 0:
            return math.exp(p*(x-L))*(-math.expm1(-p*x))/(-math.expm1(-p*L))
        return math.expm1(p*x)/math.expm1(p*L)

    def quantile_log(self, v):
        """log(q/a) for strictly interior probability coordinates."""
        v=np.asarray(v,dtype=float)
        if np.any((v<=0)|(v>=1)):
            raise ValueError("Quadrature probabilities must be strictly interior")
        L,p=math.log1p((self.b-self.a)/self.a),self.p
        if p == 0:
            return L*v
        if p > 0:
            return L+np.logaddexp(np.log1p(-v)-p*L,np.log(v))/p
        return np.log1p(v*np.expm1(p*L))/p


def reconstruct(N,U,R,a,b):
    """Construct exact empty/weak-limit or unique interior power-law closure.

    No clipping, density floor, arbitrary empty seed, or huge-p endpoint proxy.
    At a=b only an exactly empty continuous-source cell is admitted.
    """
    N,U,R,a,b=map(float,(N,U,R,a,b))
    if not all(math.isfinite(v) for v in (N,U,R,a,b)):
        raise InvalidCone("Nonfinite state or support")
    if R<=0 or a<=0 or b<a or N<0 or U<0:
        raise InvalidCone("Invalid support, geometry, or negative moment")
    if N == 0:
        if U != 0:
            raise InvalidCone("N=0 requires U=0")
        status="ZERO_WIDTH_EMPTY" if a==b else "EMPTY"
        jacstatus="NO_JAC_AT_ZERO_WIDTH" if a==b else "NO_JAC_AT_EMPTY"
        return CellSpectrum(N,U,R,a,b,None,None,status,jacstatus)
    if a == b:
        raise InvalidCone("Nonzero zero-width support is not a continuous-source cell")
    m=(U/N)/R
    if not math.isfinite(m) or not a<=m<=b:
        raise InvalidCone("Mean covector lies outside supplied active support")
    if m == a or m == b:
        status="LOWER_WEAK_LIMIT" if m==a else "UPPER_WEAK_LIMIT"
        return CellSpectrum(N,U,R,a,b,m,None,status,"NO_JAC_AT_ENDPOINT")
    L=math.log1p((b-a)/a)
    target=(m-a)/(b-a)
    def f(t):
        return _mean_cell_fraction(t,L,a,b)-target
    lo,hi=-1.,1.
    for _ in range(80):
        if f(lo)<=0<=f(hi):
            break
        lo*=2
        hi*=2
    else:
        raise ArithmeticError("Interior mean inversion could not be bracketed")
    p=brentq(f,lo,hi,xtol=2e-13,rtol=1e-14,maxiter=160)/L
    return CellSpectrum(N,U,R,a,b,m,p,"INTERIOR","INTERIOR_COVARIANCE")


def _quadrature(cell,kernel,splits,order):
    nodes,weights=leggauss(order)
    edges=[0.]+[cell.cdf(q) for q in splits]+[1.]
    allx,allw=[],[]
    for lo,hi in zip(edges[:-1],edges[1:]):
        if hi==lo:
            continue
        v=lo+(hi-lo)*(nodes+1)/2
        allx.append(cell.quantile_log(v))
        allw.append((hi-lo)*weights/2)
    x,w=np.concatenate(allx),np.concatenate(allw)
    dq=cell.a*np.expm1(x)
    q=cell.a+dq
    kappa=np.broadcast_to(np.asarray(kernel(q),dtype=float),q.shape)
    if np.any(~np.isfinite(kappa)) or np.any(kappa<0):
        raise ValueError("Opacity kernel must return finite nonnegative values")
    sw=float(w.sum())
    if abs(sw-1)>8*np.finfo(float).eps:
        raise ArithmeticError("Positive quadrature lost probability normalization")
    # All covariance terms use the same positive measure; no denominator floor.
    xbar=float(w@x)
    dqbar=float(w@dq)
    qbar=cell.a+dqbar
    covq=float(w@((dq-dqbar)*(x-xbar)))
    if not math.isfinite(covq) or covq<=0:
        raise QuadratureNotConverged("Unresolved positive interior covariance")
    # Integrate the constant anchor analytically. In particular a constant
    # kernel has exactly zero covariance, not a roundoff-sized false column.
    delta0=kappa-kappa[0]
    mean_delta0=float(w@delta0)
    energy_kernel=cell.R*q*kappa
    deltaE=energy_kernel-energy_kernel[0]
    mean_deltaE=float(w@deltaE)
    B0=float(kappa[0]+mean_delta0)
    BE=float(energy_kernel[0]+mean_deltaE)
    cov0=float(w@((delta0-mean_delta0)*(x-xbar)))
    covE=float(w@((deltaE-mean_deltaE)*(x-xbar)))
    ratio0,ratioE=cov0/covq,covE/covq
    jac=np.array([[B0-cell.mean_q*ratio0,ratio0/cell.R],
                  [BE-cell.mean_q*ratioE,ratioE/cell.R]])
    K0,KE=cell.N*B0,cell.N*BE
    if not np.all(np.isfinite([K0,KE,*jac.ravel()])):
        raise ArithmeticError("Nonfinite opacity moments or interior Jacobian")
    # Each component has its own scale. The N derivatives use their two
    # cancellation terms; a large Jacobian cannot hide a small K0/KE error.
    response=np.array([B0,BE,jac[0,0],jac[0,1],jac[1,0],jac[1,1]])
    response_scales=np.array([abs(B0),abs(BE),max(abs(B0),abs(cell.mean_q*ratio0)),
                              abs(ratio0/cell.R),max(abs(BE),abs(cell.mean_q*ratioE)),
                              abs(ratioE/cell.R)])
    mean_scale=min(cell.mean_q-cell.a,cell.b-cell.mean_q)
    return {"K0":K0,"KE":KE,"jacobian_N_U":jac.tolist(),
            "quadrature_number_relative_residual":sw-1.,
            "quadrature_mean_relative_residual":qbar/cell.mean_q-1.,
            "quadrature_mean_cell_relative_residual":(dqbar-(cell.mean_q-cell.a))/mean_scale,
            "cov_q_logq":covq,"response":response,"response_scales":response_scales}


def opacity_moments(cell,kernel,*,split_points=(),orders=(64,128),rtol=1e-7,
                    require_jacobian=True,endpoint_trace=None):
    """Common positive moment/Jacobian quadrature, with a bounded order check.

    K0=c integral sigma F, KE=c integral (R*q) sigma F; K1=KE/R.
    ``endpoint_trace=(side,value)`` is a caller-certified interior trace of
    kappa, not a sample at the endpoint. Smooth and discontinuous endpoints
    both require it because this module cannot infer kernel continuity.
    ``rtol`` is an additional local numerical criterion, not any global gate.
    """
    if not math.isfinite(rtol) or rtol<=0:
        raise ValueError("A positive finite local quadrature tolerance is required")
    if cell.status in ("EMPTY","ZERO_WIDTH_EMPTY"):
        if require_jacobian:
            raise UndefinedJacobian(cell.jacobian_status+": source entry start rule is unresolved")
        return {"K0":0.,"KE":0.,"K1":0.,"jacobian_N_U":None,
                "status":"EMPTY_EXACT_ZERO","jacobian_status":cell.jacobian_status}
    if cell.status!="INTERIOR":
        side="right" if cell.status=="LOWER_WEAK_LIMIT" else "left"
        if (not isinstance(endpoint_trace,tuple) or len(endpoint_trace)!=2
                or endpoint_trace[0]!=side):
            raise TraceRequired("Explicit "+side+" interior kernel trace required")
        value=float(endpoint_trace[1])
        if not math.isfinite(value) or value<0:
            raise ValueError("Invalid one-sided opacity trace")
        if require_jacobian:
            raise UndefinedJacobian("NO_JAC_AT_ENDPOINT: no threshold/endpoint Jacobian supplied")
        return {"K0":cell.N*value,"KE":cell.U*value,"K1":cell.U/cell.R*value,
                "jacobian_N_U":None,"status":"WEAK_LIMIT_WITH_EXPLICIT_TRACE",
                "trace_side":side,"trace_value":value,
                "jacobian_status":cell.jacobian_status}
    if (len(orders)!=2 or any(type(n) is not int or n<2 for n in orders)
            or orders[0]>=orders[1]):
        raise ValueError("Exactly two increasing positive quadrature orders required")
    # An arbitrary caller kernel receives binary64 q, not exact subcell offsets.
    # Close support/endpoints can amplify a q ULP enormously (e.g. affine
    # (q-a)/(b-a)). This conservative admission indicator rejects states where
    # even coordinate resolution cannot support the requested local accuracy.
    # It is not a rigorous arbitrary-kernel error bound or a photon/state floor.
    coordinate_indicator=32*math.ulp(cell.b)/min(cell.mean_q-cell.a,cell.b-cell.mean_q)
    if coordinate_indicator>rtol:
        raise QuadratureNotConverged(
            f"FLOAT_Q_COORDINATE_UNRESOLVED: indicator={coordinate_indicator}, rtol={rtol}; no clipping or startup seed")
    splits=sorted(float(v) for v in split_points)
    if any(not math.isfinite(v) or not cell.a<v<cell.b for v in splits):
        raise ValueError("Splits must lie strictly inside supplied active support")
    if len(set(splits))!=len(splits):
        raise ValueError("Duplicate opacity split")
    coarse=_quadrature(cell,kernel,splits,orders[0])
    fine=_quadrature(cell,kernel,splits,orders[1])
    scales=np.maximum(coarse["response_scales"],fine["response_scales"])
    differences=abs(fine["response"]-coarse["response"])
    component_errors=np.divide(differences,scales,out=np.zeros_like(differences),where=scales>0)
    if np.any((scales==0)&(differences!=0)):
        raise QuadratureNotConverged("Nonzero difference in an exactly zero component")
    error=float(np.max(component_errors))
    residual=max(abs(coarse["quadrature_mean_cell_relative_residual"]),
                 abs(fine["quadrature_mean_cell_relative_residual"]))
    if error>rtol or residual>rtol:
        raise QuadratureNotConverged(
            f"Declared orders {orders} unresolved: response error={error}, mean residual={residual}, rtol={rtol}")
    fine.pop("response")
    fine.pop("response_scales")
    fine.update({"K1":fine["KE"]/cell.R,"status":"INTERIOR_LOCAL_QUADRATURE_CHECKED",
                 "jacobian_status":cell.jacobian_status,"orders":list(orders),
                 "order_pair_response_scaled_error":error,"local_rtol":rtol,
                 "order_pair_component_errors":dict(zip(
                     ["K0","KE","J_K0_N","J_K0_U","J_KE_N","J_KE_U"],component_errors.tolist())),
                 "float_q_coordinate_indicator":coordinate_indicator,
                 "jacobian_error_scaling":"per_component_with_separate_cancellation_terms",
                 "closure_moments":{"N":cell.N,"U":cell.U},
                 "native_binding":NATIVE_BINDING,
                 "claim":"LOCAL_NUMERICAL_FIXTURE_ONLY_NOT_ODE_ADMISSION"})
    return fine
