"""Signed represented DR fits: Decimal outward enclosures, not fit uncertainty."""
import hashlib
import json
from decimal import (Decimal as D, Context, localcontext, ROUND_FLOOR,
                     ROUND_CEILING, ROUND_HALF_EVEN, Underflow, Subnormal)
from fractions import Fraction

SOURCE_SHA256 = '38397e6b560f463f09a5923eaa5902a24312e5246abc158694451c631cd4d6bc'


def number(x):
    """int/Decimal mean exact values; float means its exact binary64 image."""
    if type(x) is float:
        x = D.from_float(x)
    elif type(x) is int:
        x = D(x)
    elif type(x) is not D:
        raise TypeError('explicit int, Decimal or binary64 float required')
    if not x.is_finite():
        raise ValueError('finite value required')
    return x


class Arithmetic:
    def __init__(self, precision=60):
        if type(precision) is not int or precision < 50:
            raise ValueError('precision >=50 required')
        self.context = Context(prec=precision, Emin=-999999, Emax=999999)
        self.context.traps[Underflow] = True
        self.context.traps[Subnormal] = True

    def op(self, name, x, y, rounding):
        with localcontext(self.context) as c:
            c.rounding = rounding
            return getattr(c, name)(x, y)

    def interval(self, lo, hi=None):
        lo = number(lo); hi = lo if hi is None else number(hi)
        if lo > hi:
            raise ValueError('reversed interval')
        return Interval(self, lo, hi)


class Interval:
    def __init__(self, arithmetic, lo, hi):
        self.a, self.lo, self.hi = arithmetic, lo, hi

    def coerce(self, x):
        if isinstance(x, Interval):
            if x.a is not self.a:
                raise ValueError('mixed arithmetic contexts')
            return x
        return self.a.interval(x)

    def __add__(self, other):
        y = self.coerce(other)
        return Interval(self.a, self.a.op('add', self.lo, y.lo, ROUND_FLOOR),
                        self.a.op('add', self.hi, y.hi, ROUND_CEILING))
    __radd__ = __add__

    def __neg__(self):
        return Interval(self.a, self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other):
        return self + -self.coerce(other)

    def __rsub__(self, other):
        return self.coerce(other) + -self

    def __mul__(self, other):
        y = self.coerce(other)
        pairs = [(x, z) for x in (self.lo, self.hi) for z in (y.lo, y.hi)]
        return Interval(self.a, min(self.a.op('multiply', x, z, ROUND_FLOOR) for x, z in pairs),
                        max(self.a.op('multiply', x, z, ROUND_CEILING) for x, z in pairs))
    __rmul__ = __mul__

    def __truediv__(self, other):
        y = self.coerce(other)
        if y.lo <= 0 <= y.hi:
            raise ValueError('division interval contains zero')
        reciprocal = Interval(self.a, self.a.op('divide', D(1), y.hi, ROUND_FLOOR),
                              self.a.op('divide', D(1), y.lo, ROUND_CEILING))
        return self * reciprocal

    def transcend(self, method):
        # exp/ln/sqrt are correctly rounded HALF_EVEN, not directed operations.
        with localcontext(self.a.context) as c:
            c.rounding = ROUND_HALF_EVEN
            lo = getattr(c, method)(self.lo)
            hi = getattr(c, method)(self.hi)
            return Interval(self.a, lo.next_minus(c), hi.next_plus(c))

    def magnitude(self):
        return max(self.lo.copy_abs(), self.hi.copy_abs())

    def wire(self):
        return {'lo': str(self.lo), 'hi': str(self.hi)}


def load_source(path, expected_sha256=SOURCE_SHA256):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError('source SHA256 mismatch')
    data = json.loads(raw)
    if set(data['dr']) != {'2:1', '3:1', '3:2'}:
        raise ValueError('unexpected DR row set')
    return data


def parameter_images(data):
    def image(x):
        f = float(x); n, d = f.as_integer_ratio()
        return {'hex': f.hex(), 'num': str(n), 'den': str(d),
                'exact_decimal': str(D.from_float(f))}
    return {'s': image(1e-6), 'k': image(1.380649e-23),
            'rows': {key: {name: [image(x) for x in row[name]]
                          for name in ('c_cm3_s_K32', 'E_K')}
                     for key, row in data['dr'].items()}}


class DRModel:
    def __init__(self, data, precision=60):
        self.data, self.a = data, Arithmetic(precision)
        self.s, self.k = number(1e-6), number(1.380649e-23)

    def row(self, key):
        if type(key) is not str or key not in self.data['rr']:
            raise ValueError('unknown retained species key')
        row = self.data['dr'].get(key)
        if row is None:
            return None
        cs = tuple(number(float(x)) for x in row['c_cm3_s_K32'])
        es = tuple(number(float(x)) for x in row['E_K'])
        if len(cs) != 3 or len(es) != 3 or any(e <= 0 for e in es):
            raise ValueError('unsupported source row')
        return cs, es

    def domain(self, lo, hi=None):
        t = self.a.interval(lo, hi)
        if t.lo < 100 or t.hi > 1000000:
            raise ValueError('outside runtime temperature domain')
        return t

    def kernel(self, energy, temperature):
        e = self.a.interval(energy)
        return (-e/temperature).transcend('exp') / (temperature * temperature.transcend('sqrt'))

    def term_range(self, energy, interval):
        left = self.kernel(energy, self.a.interval(interval.lo))
        right = self.kernel(energy, self.a.interval(interval.hi))
        values = [left, right]
        # Fraction comparisons avoid accidental context rounding of peak tests.
        e = Fraction(energy)
        if 3*Fraction(interval.lo) <= 2*e <= 3*Fraction(interval.hi):
            peak = self.a.interval(energy)*2/3
            values.append(self.kernel(energy, peak))
        return Interval(self.a, min(left.lo, right.lo), max(x.hi for x in values))

    def positivity(self, key, loss=False):
        row = self.row(key)
        if row is None:
            return {'structural_absence': True, 'strict_positive': False}
        cs, es = row
        weights = [Fraction(c)* (Fraction(e) if loss else 1) for c, e in zip(cs, es)]
        if all(w > 0 for w in weights):
            return {'structural_absence': False, 'strict_positive': True, 'basis': 'all_positive'}
        margin = weights[0] - abs(weights[2])
        if not (weights[0] > 0 and weights[1] > 0 and weights[2] < 0 and es[2] >= es[0] and margin > 0):
            raise ValueError('actual-row positivity certificate unavailable')
        return {'structural_absence': False, 'strict_positive': True,
                'basis': 'rewritten_positive_weights',
                'margin': {'num': str(margin.numerator), 'den': str(margin.denominator)}}

    def weights(self, cs, es, loss):
        return [self.a.interval(self.s)*c*(self.a.interval(self.k)*e if loss else 1)
                for c, e in zip(cs, es)]

    def range(self, key, lo, hi, loss=False):
        t = self.domain(lo, hi); row = self.row(key)
        if row is None:
            return self.a.interval(0)
        cs, es = row; self.positivity(key, loss)
        kernels = [self.term_range(e, t) for e in es]
        result = sum((w*g for w, g in zip(self.weights(cs, es, loss), kernels)), self.a.interval(0))
        if cs[2] < 0:
            # Interval subtraction/multiplication retain exact represented factors.
            base = [self.a.interval(c)*(self.a.interval(e) if loss else 1) for c,e in zip(cs,es)]
            positive = (base[0]+base[2])*kernels[0]+base[1]*kernels[1]
            positive = positive*self.s*(self.k if loss else 1)
        else:
            positive = result
        lower = max(result.lo, positive.lo)
        if lower <= 0:
            raise ArithmeticError('arithmetic failed to preserve strict support')
        return Interval(self.a, lower, result.hi)

    def first_log_derivative(self, key, temperature, loss=False):
        t = self.domain(temperature); row = self.row(key)
        if row is None:
            return self.a.interval(0)
        cs, es = row
        return sum((w*self.kernel(e,t)*(self.a.interval(e)/t-D('1.5'))
                    for w,e in zip(self.weights(cs,es,loss),es)), self.a.interval(0))

    def second_bound(self, key, lo, hi, loss=False):
        t = self.domain(lo,hi); row = self.row(key)
        if row is None:
            return self.a.interval(0)
        cs,es=row; total=self.a.interval(0)
        for w,e in zip(self.weights(cs,es,loss),es):
            x=self.a.interval(e)/t
            candidates=[self.a.interval(x.lo),self.a.interval(x.hi)]
            if x.lo <= 2 <= x.hi:
                candidates.append(self.a.interval(2))
            q=max((v*v-4*v+D('2.25')).magnitude() for v in candidates)
            total=total+self.a.interval(w.magnitude())*self.term_range(e,t).hi*q
        return Interval(self.a,D(0),total.hi)

    def taylor(self,key,lo,hi,t0,target,loss=False):
        domain=self.domain(lo,hi); center=self.domain(t0); point=self.domain(target)
        if not (domain.lo<=center.lo<=domain.hi and domain.lo<=point.lo<=domain.hi):
            raise ValueError('Taylor endpoints outside interval')
        f0=self.range(key,t0,t0,loss)
        d0=self.first_log_derivative(key,t0,loss)
        if point.lo == center.lo:
            return {'enclosure':f0,'h':self.a.interval(0),'f0':f0,'d0':d0,'radius':D(0)}
        h=(point/center).transcend('ln')
        radius=(self.second_bound(key,lo,hi,loss)*h.magnitude()*h.magnitude()/2).hi
        linear=f0+d0*h
        enclosure=linear+Interval(self.a,radius.copy_negate(),radius)
        return {'enclosure':enclosure,'h':h,'f0':f0,'d0':d0,'radius':radius}
