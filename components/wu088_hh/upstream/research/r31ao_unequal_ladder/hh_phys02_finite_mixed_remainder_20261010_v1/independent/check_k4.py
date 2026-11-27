"""Exact polynomial checks of HH-PHYS02 K4 identities; no ODE integration.

This is a nonphysical algebra fixture. All arithmetic is rational. A direct
time/parameter power-series recurrence is compared with a separate first/second
state derivative evaluation of the claimed fourth mixed coefficient.
"""
from fractions import Fraction as R
from pathlib import Path
import json

NVAR = 5  # x, a dummy nonphoto gas coordinate, w, P1, P2
CHI, A1, A2, G1, G2 = R(7, 2), R(2), R(3), R(1, 3), R(2, 5)
Z0 = tuple(map(R, (0, 0, 0, 0, 0)))
Z0 = (R(1, 5), R(1, 7), R(11, 4), R(1, 11), R(1, 13))


class Poly:
    # keys are powers of (time, epsilon_lambda, epsilon_S)
    def __init__(self, d=0):
        self.d = {k: R(v) for k, v in d.items() if v} if isinstance(d, dict) else ({(0, 0, 0): R(d)} if d else {})
    @staticmethod
    def cast(x): return x if isinstance(x, Poly) else Poly(x)
    def __add__(self, other):
        d = dict(self.d)
        for k, v in self.cast(other).d.items(): d[k] = d.get(k, R(0)) + v
        return Poly(d)
    __radd__ = __add__
    def __neg__(self): return Poly({k: -v for k, v in self.d.items()})
    def __sub__(self, other): return self + (-self.cast(other))
    def __rsub__(self, other): return self.cast(other) - self
    def __mul__(self, other):
        d = {}
        for a, av in self.d.items():
            for b, bv in self.cast(other).d.items():
                k = tuple(a[i] + b[i] for i in range(3))
                if k[0] <= 4 and k[1] <= 1 and k[2] <= 1:
                    d[k] = d.get(k, R(0)) + av * bv
        return Poly(d)
    __rmul__ = __mul__
    def __pow__(self, n):
        v = Poly(1)
        for _ in range(n): v *= self
        return v


class D2:
    def __init__(self, v, g=None, h=None):
        self.v = R(v)
        self.g = list(g) if g is not None else [R(0)] * NVAR
        self.h = [list(r) for r in h] if h is not None else [[R(0)] * NVAR for _ in range(NVAR)]
    @staticmethod
    def cast(x): return x if isinstance(x, D2) else D2(x)
    @staticmethod
    def variable(v, i):
        out = D2(v)
        out.g[i] = R(1)
        return out
    def __add__(self, other):
        b = self.cast(other)
        return D2(self.v+b.v, [self.g[i]+b.g[i] for i in range(NVAR)], [[self.h[i][j]+b.h[i][j] for j in range(NVAR)] for i in range(NVAR)])
    __radd__ = __add__
    def __neg__(self): return D2(-self.v, [-v for v in self.g], [[-v for v in row] for row in self.h])
    def __sub__(self, other): return self + (-self.cast(other))
    def __rsub__(self, other): return self.cast(other) - self
    def __mul__(self, other):
        b = self.cast(other)
        return D2(self.v*b.v,
                  [self.g[i]*b.v+self.v*b.g[i] for i in range(NVAR)],
                  [[self.h[i][j]*b.v+self.g[i]*b.g[j]+self.g[j]*b.g[i]+self.v*b.h[i][j] for j in range(NVAR)] for i in range(NVAR)])
    __rmul__ = __mul__
    def __pow__(self, n):
        v = D2(1)
        for _ in range(n): v *= self
        return v


def field(z, lam, src):
    x, y, w, p1, p2 = z
    u = 1-x
    # Nonphoto vector field is intentionally nonlinear in all gas coordinates.
    n = (R(1, 7)+x*y-R(2, 9)*w*w,
         x*x-y*w+R(1, 3)*y,
         R(2, 5)*x*w+y*y-R(1, 4)*w)
    q = u*u*(1+w*w+x*y)
    m = A1*p1+A2*p2
    heat = A1*G1*p1+A2*G2*p2
    return (n[0]+u*m+lam*q, n[1], n[2]+u*heat-lam*CHI*q,
            -A1*u*p1, -A2*u*p2+src)


def add(*vecs): return [sum(v[i] for v in vecs) for i in range(NVAR)]
def mul(a, v): return [a*x for x in v]
def dot(a, b): return sum(x*y for x, y in zip(a, b))


def direct_coefficient(lam, src):
    z = [Poly(v) for v in Z0]
    lp = Poly(lam)+Poly({(0, 1, 0): 1})
    sp = Poly(src)+Poly({(0, 0, 1): 1})
    for n in range(1, 5):
        f = field(z, lp, sp)
        for i in range(NVAR):
            update = {(n, a, b): f[i].d.get((n-1, a, b), R(0))/n
                      for a in range(2) for b in range(2)}
            z[i] = z[i] + Poly(update)
    return [24 * p.d.get((4, 1, 1), R(0)) for p in z]


def formula(lam, src):
    zj = [D2.variable(v, i) for i, v in enumerate(Z0)]
    jets = field(zj, lam, src)
    f = [v.v for v in jets]
    qj = (1-zj[0])**2*(1+zj[2]**2+zj[0]*zj[1])
    h = [R(1), R(0), -CHI, R(0), R(0)]
    b = [R(0), R(0), R(0), R(0), R(1)]
    hh = mul(qj.v, h)
    j = lambda v: [dot(d.g, v) for d in jets]
    q = lambda v, w: [sum(d.h[i][k]*v[i]*w[k] for i in range(NVAR) for k in range(NVAR)) for d in jets]
    hp = lambda v: mul(dot(qj.g, v), h)
    hpp = lambda v, w: mul(sum(qj.h[i][k]*v[i]*w[k] for i in range(NVAR) for k in range(NVAR)), h)
    c = j(b)
    k3 = add(hp(c), mul(2, q(hh, b)))
    k4 = add(j(k3), mul(3, q(b, add(j(hh), hp(f)))), mul(3, q(hh, c)),
             hp(add(j(c), mul(2, q(f, b)))), mul(3, hpp(f, c)))
    d = [R(1), R(0), G2, R(0), -R(1)]
    qd, qh = dot(qj.g, d), dot(qj.g, h)
    qhd = sum(qj.h[i][k]*h[i]*d[k] for i in range(NVAR) for k in range(NVAR))
    k41 = add(mul(A2*(2*(1-Z0[0])*qd*qh-4*qj.v*qd+6*(1-Z0[0])*qj.v*qhd), h),
              mul(-6*A2*qj.v*qh, d))
    return k4, k41


def main():
    cases = []
    k40, k41 = formula(R(0), R(0))
    for lam in (R(0), R(1, 3), R(1)):
        for src in (R(0), R(2, 7)):
            direct = direct_coefficient(lam, src)
            proposed, linear = formula(lam, src)
            affine = add(k40, mul(lam, k41))
            assert direct == proposed == affine
            assert linear == k41
            cases.append({'lambda': str(lam), 'S': str(src), 'direct_series_equals_K4': True, 'S_independent_lambda_affine': True})
    result = {
        'status': 'PASS_ALGEBRA_FIXTURE_ONLY',
        'arithmetic': 'fractions.Fraction exact rational',
        'source': 'nonphysical 3 gas + 2 photon polynomial fixture',
        'ivp_or_native_dispatch': False,
        'checks': cases,
        'K40_x': str(k40[0]), 'K41_x': str(k41[0]),
        'physical_coefficient_evaluated': False,
    }
    out = Path(__file__).with_name('K4_EXACT_CHECK.json')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'cases': len(cases), 'output': str(out)}))


if __name__ == '__main__': main()
