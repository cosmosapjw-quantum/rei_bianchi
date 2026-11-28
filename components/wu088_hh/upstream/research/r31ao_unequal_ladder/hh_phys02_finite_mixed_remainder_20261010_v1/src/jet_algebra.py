"""Truncated time series over hyperdual Arb balls; no trajectory solver.

Hyperdual order is (value, d_lambda, d_s, d_lambda_d_s).
Time coefficients are derivatives divided by factorials.
"""
from flint import arb


class HD:
    __slots__ = ('c',)

    def __init__(self, value=0, dl=0, ds=0, dls=0):
        self.c = tuple(v if isinstance(v, arb) else arb(v)
                       for v in (value, dl, ds, dls))

    @staticmethod
    def lift(v):
        return v if isinstance(v, HD) else HD(v)

    def __add__(self, other):
        if isinstance(other, Jet):
            return NotImplemented
        b = HD.lift(other)
        return HD(*(a + d for a, d in zip(self.c, b.c)))

    __radd__ = __add__

    def __neg__(self):
        return HD(*(-a for a in self.c))

    def __sub__(self, other):
        return self + (-HD.lift(other))

    def __rsub__(self, other):
        return HD.lift(other) + (-self)

    def __mul__(self, other):
        if isinstance(other, Jet):
            return NotImplemented
        b = HD.lift(other).c
        a = self.c
        return HD(a[0]*b[0], a[1]*b[0]+a[0]*b[1],
                  a[2]*b[0]+a[0]*b[2],
                  a[3]*b[0]+a[1]*b[2]+a[2]*b[1]+a[0]*b[3])

    __rmul__ = __mul__

    def inv(self):
        a, u, v, w = self.c
        if a.contains(0):
            raise ValueError('hyperdual reciprocal spans zero')
        b = 1/a
        return HD(b, -u*b*b, -v*b*b, 2*u*v*b*b*b-w*b*b)

    def __truediv__(self, other):
        if isinstance(other, Jet):
            return NotImplemented
        return self * HD.lift(other).inv()

    def __rtruediv__(self, other):
        return HD.lift(other) * self.inv()

    def exp(self):
        a, u, v, w = self.c
        b = a.exp()
        return HD(b, b*u, b*v, b*(w+u*v))

    def log(self):
        a, u, v, w = self.c
        if not a > 0:
            raise ValueError('hyperdual logarithm not positive')
        return HD(a.log(), u/a, v/a, w/a-u*v/(a*a))

    def __pow__(self, power):
        if isinstance(power, int) and power >= 0:
            r = HD(1)
            for _ in range(power):
                r = r*self
            return r
        return (self.log()*power).exp()


class Jet:
    __slots__ = ('a', 'n')

    def __init__(self, coefficients, order=None):
        self.n = len(coefficients)-1 if order is None else order
        if len(coefficients) > self.n+1:
            raise ValueError('too many time coefficients')
        self.a = [HD.lift(v) for v in coefficients]
        self.a += [HD(0) for _ in range(self.n+1-len(self.a))]

    def lift(self, v):
        if isinstance(v, Jet):
            if v.n != self.n:
                raise ValueError('time truncation orders differ')
            return v
        return Jet([v], self.n)

    def __add__(self, v):
        b = self.lift(v)
        return Jet([x+y for x, y in zip(self.a, b.a)])

    __radd__ = __add__

    def __neg__(self):
        return Jet([-x for x in self.a])

    def __sub__(self, v):
        return self + (-self.lift(v))

    def __rsub__(self, v):
        return self.lift(v) + (-self)

    def __mul__(self, v):
        b = self.lift(v)
        return Jet([sum((self.a[k]*b.a[j-k] for k in range(j+1)), HD(0))
                    for j in range(self.n+1)])

    __rmul__ = __mul__

    def inv(self):
        b = [self.a[0].inv()]
        for j in range(1, self.n+1):
            b.append(-b[0]*sum((self.a[k]*b[j-k] for k in range(1, j+1)), HD(0)))
        return Jet(b)

    def __truediv__(self, v):
        return self*self.lift(v).inv()

    def __rtruediv__(self, v):
        return self.lift(v)*self.inv()

    def exp(self):
        b = [self.a[0].exp()]
        for j in range(1, self.n+1):
            b.append(sum((k*self.a[k]*b[j-k] for k in range(1, j+1)), HD(0))/j)
        return Jet(b)

    def log(self):
        reciprocal = self.inv().a
        b = [self.a[0].log()]
        for j in range(1, self.n+1):
            b.append(sum((k*self.a[k]*reciprocal[j-k] for k in range(1, j+1)), HD(0))/j)
        return Jet(b)

    def __pow__(self, power):
        if isinstance(power, int) and power >= 0:
            r = self.lift(1)
            for _ in range(power):
                r = r*self
            return r
        return (self.log()*power).exp()


def flow_jet(field, initial_hd, lam, source, order=4):
    """Taylor recurrence at one abstract point; no step is advanced."""
    z = [Jet([v], order) for v in initial_hd]
    for n in range(order):
        f = field(z, Jet([lam], order), Jet([source], order))
        for j in range(len(z)):
            z[j].a[n+1] = f[j].a[n]/(n+1)
    return z
