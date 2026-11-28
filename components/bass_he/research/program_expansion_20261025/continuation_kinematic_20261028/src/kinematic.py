"""Exact declared-mass Lorentz aperture certificates for continuous measures.

Only rational arithmetic and exact signs of quadratic surds enter certificates.
Mass measurement uncertainty, empirical rates and thermal deposition are absent.
"""
from dataclasses import dataclass
from fractions import Fraction
import importlib.util
from pathlib import Path
import sys

_PARENT = Path(__file__).resolve().parents[2] / "continuation_aperture_20261027/src/aperture.py"
_SPEC = importlib.util.spec_from_file_location("_kinematic08_inherited_aperture", _PARENT)
_API = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _API
_SPEC.loader.exec_module(_API)
ContractError = _API.ContractError
UnsupportedMeasureError = _API.UnsupportedMeasureError
StoppedDirectionError = _API.StoppedDirectionError
BernsteinDensity = _API.BernsteinDensity
SetBounds = _API.SetBounds
IntegralBounds = _API.IntegralBounds
rational, cosine, sign = _API.rational, _API.cosine, _API.sign
FULL = _API.FULL


def sign_surds(p, q, R):
    """Return sign(p + q sqrt(R)) exactly, including rational cancellation."""
    p, q, R = rational(p, "p"), rational(q, "q"), rational(R, "R")
    if R < 0:
        raise ContractError("negative radicand")
    if not R or not q:
        return sign(p)
    if not p:
        return sign(q)
    if sign(p) == sign(q):
        return sign(p)
    return sign(p) * sign(p*p - q*q*R)


@dataclass(frozen=True)
class PhysicalPreimage:
    sets: SetBounds
    delta: Fraction
    root_brackets: tuple
    fold_bracket: tuple | None

    @property
    def inner(self):
        return self.sets.inner

    @property
    def outer(self):
        return self.sets.outer

    @property
    def uncertainty_length(self):
        return _API.length(self.sets.uncertain)

    @property
    def uncertainty_length_bound(self):
        return 5*self.delta


class PhysicalAngularMap:
    """Declared rest energies A,M and incident energy e in MeV."""

    def __init__(self, A, M, e, *, measure_kind="CONTINUOUS", kappa=None):
        _API.require_continuous(measure_kind, kappa)
        self.A, self.M, self.e = (rational(x, n) for x, n in ((A,"A"),(M,"M"),(e,"e")))
        if not (self.M > 0 and 0 < self.A < 2*self.M and self.e > 0):
            raise ContractError("require M>0, 0<A<2M, e>0")
        self.s = self.A*self.A + 2*self.A*self.e
        self.H = self.s - 4*self.M*self.M
        if self.H < 0:
            raise ContractError("closed channel H<0")
        if self.H == 0:
            raise UnsupportedMeasureError("H=0 threshold atom")
        self.G = self.A + self.e
        self.R = self.H/self.s
        self.K = self.e*self.e - self.G*self.G*self.R
        self.topology = "increasing" if self.K < 0 else "stopped" if self.K == 0 else "fold"
        self.operations = {"comparisons": 0, "boundary_bisections": 0, "fold_bisections": 0}

    def compare(self, mu, nu):
        return self._compare(mu, nu, auxiliary_stopped_limit=False)

    def _compare(self, mu, nu, *, auxiliary_stopped_limit):
        mu, nu = cosine(mu,"mu"), cosine(nu,"nu")
        self.operations["comparisons"] += 1
        sx = sign_surds(self.e, self.G*mu, self.R)
        T = self.H*(1-mu*mu)
        if sx == 0 and T == 0:
            if auxiliary_stopped_limit:
                return -sign(nu)
            raise StoppedDirectionError("stopped daughter has no direction")
        sn = sign(nu)
        if sx != sn:
            return sign(sx-sn)
        if sx == 0:
            return 0
        P = (1-nu*nu)*(self.e*self.e+self.G*self.G*mu*mu*self.R)-nu*nu*T
        Q = 2*self.e*self.G*mu*(1-nu*nu)
        return sx*sign_surds(P,Q,self.R)

    def _bracket(self, nu, lo, hi, increasing, delta):
        orientation = 1 if increasing else -1
        def predicate(mu):
            return orientation*self._compare(mu,nu,auxiliary_stopped_limit=True)
        if predicate(lo) >= 0:
            return lo,lo
        if predicate(hi) <= 0:
            return hi,hi
        while hi-lo > delta:
            self.operations["boundary_bisections"] += 1
            mid = (lo+hi)/2
            value = predicate(mid)
            if value == 0:
                return mid,mid
            if value < 0:
                lo = mid
            else:
                hi = mid
        return lo,hi

    def _fold(self, delta):
        lo,hi = Fraction(-1),Fraction(0)
        while hi-lo > delta:
            self.operations["fold_bisections"] += 1
            mid = (lo+hi)/2
            value = sign_surds(mid,self.G/self.e,self.R)
            if value == 0:
                return mid,mid
            if value < 0:
                lo = mid
            else:
                hi = mid
        return lo,hi

    def preimage(self, window, delta):
        low,high = _API.lab_window(window)
        delta = _API.checked_delta(delta)
        if low == high:
            return PhysicalPreimage(SetBounds((),()),delta,(),None)
        if (low,high) == (-1,1):
            return PhysicalPreimage(SetBounds(FULL,FULL),delta,(),None)
        branches = [(Fraction(-1),Fraction(1),True)]
        fold = None
        if self.K > 0:
            fold = self._fold(delta)
            branches = [(Fraction(-1),fold[0],False),(fold[1],Fraction(1),True)]
        inner,outer,brackets = [],[],[]
        for lo,hi,increasing in branches:
            left,right = (low,high) if increasing else (high,low)
            l0,u0 = self._bracket(left,lo,hi,increasing,delta)
            l1,u1 = self._bracket(right,lo,hi,increasing,delta)
            brackets.extend(((l0,u0),(l1,u1)))
            if u0 < l1:
                inner.append((u0,l1))
            if l0 < u1:
                outer.append((l0,u1))
        if fold is not None and fold[0] < fold[1]:
            outer.append(fold)
        result = PhysicalPreimage(SetBounds(tuple(inner),tuple(outer)),delta,tuple(brackets),fold)
        if result.uncertainty_length > result.uncertainty_length_bound:
            raise ContractError("preimage uncertainty exceeds 5 delta")
        return result


def default_delta(density):
    return Fraction(1) if density.maximum == 0 else density.sigma/(20*density.maximum*2**40)


def _inputs(model,density,delta):
    if not isinstance(model,PhysicalAngularMap) or not isinstance(density,BernsteinDensity):
        raise ContractError("PhysicalAngularMap and BernsteinDensity required")
    return _API.checked_delta(default_delta(density) if delta is None else delta)


def physical_aperture_integral(model,density,window,delta=None,w0=1,w1=0):
    delta = _inputs(model,density,delta)
    window = _API.lab_window(window)
    w0,w1 = rational(w0,"w0"),rational(w1,"w1")
    if density.maximum == 0:
        return {"delta":delta,"preimage":None,"integral":IntegralBounds(Fraction(0),Fraction(0),Fraction(0),Fraction(0)),"zero_density_short_circuit":True}
    preimage = model.preimage(window,delta)
    return {"delta":delta,"preimage":preimage,"integral":density.bounds(preimage.sets,w0,w1)}


def physical_pair_response(model,density,windowA,windowB,delta=None):
    delta = _inputs(model,density,delta)
    if not density.symmetric:
        raise ContractError("paired event API requires an even Bernstein density")
    wa,wb = _API.lab_window(windowA),_API.lab_window(windowB)
    if _API.intersection(_API.normalize((wa,)),_API.normalize((wb,))):
        raise ContractError("paired detector windows must not overlap with positive width")
    if density.maximum == 0:
        zero = IntegralBounds(Fraction(0),Fraction(0),Fraction(0),Fraction(0))
        result = {key:zero for key in ("coincidence","hit_a","hit_b","inclusive_a","inclusive_b","coincidence_daughters","pair_energy_MeV","selected_plus_energy_MeV","selected_minus_energy_MeV")}
        result.update({key:None for key in ("preimage_a","preimage_b","coincidence_sets","hit_a_sets","hit_b_sets")})
        result.update(delta=delta,window_a=wa,window_b=wb,zero_density_short_circuit=True)
        return result
    pa,pb = model.preimage(wa,delta),model.preimage(wb,delta)
    a,b = pa.sets,pb.sets
    ra,rb = a.reflected(),b.reflected()
    coincidence = a.intersection(rb).union(b.intersection(ra))
    hit_a,hit_b = a.union(ra),b.union(rb)
    y = density.bounds(coincidence)
    if y.uncertainty_length > 20*delta:
        raise ContractError("pair uncertainty exceeds 20 delta")
    return {"delta":delta,"window_a":wa,"window_b":wb,"preimage_a":pa,"preimage_b":pb,
            "coincidence_sets":coincidence,"hit_a_sets":hit_a,"hit_b_sets":hit_b,
            "coincidence":y,"hit_a":density.bounds(hit_a),"hit_b":density.bounds(hit_b),
            "inclusive_a":density.bounds(a).added(density.bounds(ra)),
            "inclusive_b":density.bounds(b).added(density.bounds(rb)),
            "coincidence_daughters":y.scaled(2),"pair_energy_MeV":y.scaled(model.G),
            "selected_plus_energy_MeV":y.scaled(model.G/2),
            "selected_minus_energy_MeV":y.scaled(model.G/2)}
