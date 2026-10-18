"""Preparation-only positive SSP Heun reference. No subprocess/native launcher.

A future authorized runner may supply an RHS callback backed by the RHS-only
protocol. This module itself never starts a helper, queries setup, or performs
physical work. Constraints are necessary affine checks; native checks remain
authoritative. Controller error is diagnostic, not an observable certificate.
"""
from dataclasses import dataclass
import math


class DomainReject(Exception):
    pass


class Hold(Exception):
    pass


class HelperFailure(Exception):
    pass


@dataclass
class Counters:
    attempts: int = 0
    rhs: int = 0
    accepted: int = 0
    rejected_domain: int = 0
    rejected_error: int = 0
    failed_helper: int = 0
    births: int = 0


@dataclass(frozen=True)
class Domain:
    f: float
    kb_ev: float
    # (number index, reference-energy index, fixed support lower, upper)
    supports: tuple = ()

    def __post_init__(self):
        if not (math.isfinite(self.f) and self.f >= 0 and
                math.isfinite(self.kb_ev) and self.kb_ev > 0):
            raise ValueError('invalid EOS constants')
        for i, j, lo, hi in self.supports:
            if i < 4 or j < 4 or i == j or not all(map(math.isfinite, (lo, hi))) or lo < 0 or hi < lo:
                raise ValueError('invalid fixed support')

    def affine(self, v):
        """Exact affine g(v)>=0 checks, with no invented physical tolerance."""
        h, y, z, w = v[:4]
        d = 1 + self.f + h + self.f * (y + 2*z)
        tlo = 1.5*self.kb_ev
        gs = [h, 1-h, y, z, 1-y-z, w-tlo*d, tlo*1e6*d-w]
        for i, j, lo, hi in self.supports:
            gs.extend((v[i], v[j]-lo*v[i], hi*v[i]-v[j]))
        return gs

    def slopes(self, dv):
        h, y, z, w = dv[:4]
        dd = h + self.f * (y + 2*z)
        tlo = 1.5*self.kb_ev
        gs = [h, -h, y, z, -y-z, w-tlo*dd, tlo*1e6*dd-w]
        for i, j, lo, hi in self.supports:
            gs.extend((dv[i], dv[j]-lo*dv[i], hi*dv[i]-dv[j]))
        return gs

    def validate(self, v):
        if len(v) < 4 or not all(map(math.isfinite, v)):
            raise DomainReject('nonfinite or short state')
        if any(g < 0 or not math.isfinite(g) for g in self.affine(v)):
            raise DomainReject('simplex/cone/EOS')
        for i, j, lo, hi in self.supports:
            if v[i] == 0 and v[j] != 0:
                raise DomainReject('zero number requires zero energy')
            if lo == hi and v[j] != lo*v[i]:
                raise DomainReject('degenerate support exact mean')

    def euler_bound(self, v, dv):
        bounds = []
        for g, slope in zip(self.affine(v), self.slopes(dv)):
            if not math.isfinite(slope):
                raise DomainReject('nonfinite slope')
            if slope < 0:
                if g == 0:
                    raise Hold('DOMAIN_HOLD: boundary outward slope')
                bound = g / -slope
                if math.isfinite(bound) and bound > 0:
                    bounds.append(bound)
                elif bound == 0:
                    raise Hold('STEP_UNDERFLOW_HOLD: affine bound')
        return .9*min(bounds) if bounds else math.inf


def _rhs(rhs, x, v, counts):
    counts.rhs += 1  # actual callback launch, including a failing launch
    try:
        dv = tuple(rhs(x, tuple(v)))
    except Exception as exc:
        counts.failed_helper += 1
        raise HelperFailure('native/helper callback failure') from exc
    if len(dv) != len(v) or not all(map(math.isfinite, dv)):
        counts.failed_helper += 1
        raise HelperFailure('native/helper invalid RHS record')
    return dv


def heun(rhs, x, v, h, domain, counts, *, endpoint=None):
    """No RHS at algebraic B (which represents two Euler substeps)."""
    endpoint = x+h if endpoint is None else endpoint
    if not math.isfinite(endpoint) or not endpoint > x:
        raise Hold('STEP_UNDERFLOW_HOLD: Heun endpoint')
    domain.validate(v)
    f0 = _rhs(rhs, x, v, counts)
    if h > domain.euler_bound(v, f0):
        raise DomainReject('first Euler step exceeds affine bound')
    a = tuple(vi+h*fi for vi, fi in zip(v, f0))
    domain.validate(a)  # before F1
    f1 = _rhs(rhs, endpoint, a, counts)
    if h > domain.euler_bound(a, f1):
        raise DomainReject('second Euler step exceeds affine bound')
    b = tuple(ai+h*fi for ai, fi in zip(a, f1))
    domain.validate(b)  # algebraic validation only, no F(x+2h,B)
    result = tuple(.5*vi+.5*bi for vi, bi in zip(v, b))
    domain.validate(result)
    return result


def transaction(rhs, x, v, h, domain, counts, *, endpoint=None):
    """Returns fine accepted candidate/error; never changes the caller's state."""
    endpoint = x+h if endpoint is None else endpoint
    midpoint = x+h/2
    if h <= 0 or not math.isfinite(h) or not math.isfinite(endpoint) or not x < midpoint < endpoint:
        raise Hold('STEP_UNDERFLOW_HOLD')
    counts.attempts += 1
    coarse = heun(rhs, x, v, h, domain, counts, endpoint=endpoint)
    mid = heun(rhs, x, v, h/2, domain, counts, endpoint=midpoint)
    fine = heun(rhs, midpoint, mid, h/2, domain, counts, endpoint=endpoint)
    e = max(abs(a-b)/(3*((2e-13 if i < 3 else 2e-12 if i == 3 else 1e-15)
                   + 2e-9*max(abs(old), abs(a))))
            for i, (a,b,old) in enumerate(zip(fine,coarse,v)))
    if not math.isfinite(e):
        raise DomainReject('nonfinite controller estimate')
    return fine, e


def integrate(rhs, initial, domain, mesh, births=(), inject=(), initial_h=1e-4, counts=None):
    """Walk exact provided mesh; inject only at matching reached birth knots.

    `inject[j]` is a complete state-sized increment for birth j, with four
    leading gas zeros. Setup decoding expands each native cohort vector to
    this form. No inventory interpolation is performed.
    """
    counts = counts if counts is not None else Counters()
    mesh = tuple(mesh); births = tuple(births)
    if len(mesh) < 2 or any(not math.isfinite(x) for x in mesh) or any(a >= b for a,b in zip(mesh,mesh[1:])):
        raise ValueError('strict finite common mesh including x0 and x1 required')
    if len(births) != len(inject) or any(a >= b for a,b in zip(births,births[1:])) or any(b not in mesh for b in births):
        raise ValueError('births must be unique ordered common mesh knots')
    if not math.isfinite(initial_h) or initial_h <= 0:
        raise ValueError('positive initial step required')
    for inc in inject:
        if len(inc) != len(initial) or any(inc[:4]) or not all(map(math.isfinite,inc)):
            raise ValueError('invalid birth increment')
    v = tuple(initial); domain.validate(v)
    x = mesh[0]; h = initial_h; cursor = 0; saved = [(x,v)]
    for target in mesh:
        while x < target:
            step = min(h, target-x)
            endpoint = target if step == target-x else x+step
            try:
                fine, e = transaction(rhs,x,v,step,domain,counts,endpoint=endpoint)
            except DomainReject:
                counts.rejected_domain += 1
                h = step/2
                if x+h == x:
                    raise Hold('STEP_UNDERFLOW_HOLD after domain rejection')
                continue
            if e > 1:
                counts.rejected_error += 1
                h = step/2
                if x+h == x:
                    raise Hold('STEP_UNDERFLOW_HOLD after error rejection')
                continue
            x = endpoint
            v = fine; counts.accepted += 1
            saved.append((x,v))
            h = step*(2 if e == 0 else min(2,max(.2,.9*e**(-1/3))))
        if cursor < len(births) and target == births[cursor]:
            candidate = tuple(a+b for a,b in zip(v,inject[cursor]))
            domain.validate(candidate)
            v = candidate; counts.births += 1; cursor += 1
            saved.append((x,v))
    return {'x':x,'state':v,'saved':saved,'counts':counts}


def schedule(a0, a1, n):
    if n not in (8,16,32) or not (0 < a0 < a1):
        raise ValueError('selected discrete schedule only')
    x0, x1 = math.log(a0), math.log(a1)
    width = x1-x0
    return tuple(x0+width*(i+.5)/n for i in range(n)), width/n


def common_mesh(a0, a1):
    # Equivalent union for common_mesh(a0,a1,&[8,16,32],1), including x0 for
    # this integrator API. The native setup's exact serialized mesh is used
    # by decode_setup in any future authorized physical run.
    x0, x1 = math.log(a0), math.log(a1)
    return tuple(sorted({x0,x1,*[x for n in (8,16,32) for x in schedule(a0,a1,n)[0]]}))


def decode_setup(record):
    """Decode a supplied protocol record; does not obtain it or spawn anything."""
    if record['protocol'] != 'SOURCE012_RHS_ONLY_V1' or record['q'] != -.1 or record['birth_count'] not in (8,16,32):
        raise ValueError('wrong setup binding')
    if record['native_base'] != '35d9747a0bbedcafdb568467ce7c1e7a25f965b6' or record['overlay'] != '553ce556d9f8662290c000ec675c7e6007c9d895':
        raise ValueError('wrong setup source identity')
    n, cells = record['birth_count'], record['cells']
    if not isinstance(cells,int) or cells <= 0:
        raise ValueError('invalid cells')
    size = 4+2*cells*n
    if len(record['initial']) != size or any(record['initial'][4:]):
        raise ValueError('unborn moments must be zero')
    if len(record['births']) != n or len(record['inject']) != n or len(record['support_lo']) != n or len(record['support_hi']) != n:
        raise ValueError('setup cohort shape')
    supports=[]; injections=[]
    for j in range(n):
        lo,hi,inc = record['support_lo'][j],record['support_hi'][j],record['inject'][j]
        if len(lo)!=cells or len(hi)!=cells or len(inc)!=2*cells:
            raise ValueError('setup cell shape')
        off=4+2*cells*j
        supports.extend((off+k,off+cells+k,lo[k],hi[k]) for k in range(cells))
        full=[0.]*size;full[off:off+2*cells]=inc;injections.append(tuple(full))
    domain=Domain(record['f'],record['kb_eV_K'],tuple(supports))
    domain.validate(record['initial'])
    for inc in injections:
        domain.validate(tuple(a+b for a,b in zip(record['initial'],inc)))
    mesh=tuple(sorted({record['x0'],*record['mesh']}))
    if mesh[-1] != record['x1'] or any(b not in mesh for b in record['births']):
        raise ValueError('birth/common mesh alignment')
    return domain,tuple(record['initial']),mesh,tuple(record['births']),tuple(injections)
