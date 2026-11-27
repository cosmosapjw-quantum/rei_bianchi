#!/usr/bin/env python3
"""Exact rational/exponential-polynomial counterexamples for E13C4.

No floating-point arithmetic or inherited scientific routine is used.
T is a formal exp(-1); its numerical inequalities use a rational Taylor bound.
"""
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import hashlib
import json
import os
import sys
import tempfile


class Expr:
    """Finite Laurent polynomial in the formal symbol T=exp(-1)."""
    def __init__(self, terms=None):
        self.terms = {k: F(v) for k, v in (terms or {}).items() if v}

    @staticmethod
    def wrap(x):
        return x if isinstance(x, Expr) else Expr({0: F(x)})

    def __add__(self, other):
        d = self.terms.copy()
        for k, v in self.wrap(other).terms.items():
            d[k] = d.get(k, F(0)) + v
        return Expr(d)

    __radd__ = __add__

    def __neg__(self):
        return Expr({k: -v for k, v in self.terms.items()})

    def __sub__(self, other):
        return self + (-self.wrap(other))

    def __rsub__(self, other):
        return self.wrap(other) - self

    def __mul__(self, other):
        d = {}
        for k, v in self.terms.items():
            for j, w in self.wrap(other).terms.items():
                d[k+j] = d.get(k+j, F(0)) + v*w
        return Expr(d)

    __rmul__ = __mul__

    def __eq__(self, other):
        return self.terms == self.wrap(other).terms

    def bounds(self, tlo, thi):
        lo, hi = F(0), F(0)
        for k, v in self.terms.items():
            a, b = sorted((tlo**k, thi**k))
            lo += min(v*a, v*b)
            hi += max(v*a, v*b)
        return lo, hi

    def json(self):
        return {str(k): str(v) for k, v in sorted(self.terms.items())}


T = Expr({1: 1})


def integral_power(n, m):
    """Integral_0^1 u^n exp(-m*u) du, closed finite formula."""
    if m == 0:
        return Expr.wrap(F(1, n+1))
    c = F(factorial(n), m**(n+1))
    s = sum((F(m**k, factorial(k)) for k in range(n+1)), F(0))
    return c*(1 - s*Expr({m: 1}))


def integral_power_ibp(n, m):
    """Independent finite integration-by-parts recurrence."""
    if m == 0:
        return Expr.wrap(F(1, n+1))
    x = F(1, m)*(1 - Expr({m: 1}))
    for k in range(1, n+1):
        x = F(k, m)*x - F(1, m)*Expr({m: 1})
    return x


class EP:
    """Exact sum c_(n,m) u^n exp(-m*u)."""
    def __init__(self, terms=None):
        self.terms = {k: F(v) for k, v in (terms or {}).items() if v}

    @staticmethod
    def wrap(x):
        return x if isinstance(x, EP) else EP({(0, 0): F(x)})

    def __add__(self, other):
        d = self.terms.copy()
        for k, v in self.wrap(other).terms.items():
            d[k] = d.get(k, F(0)) + v
        return EP(d)

    __radd__ = __add__

    def __neg__(self):
        return EP({k: -v for k, v in self.terms.items()})

    def __sub__(self, other):
        return self + (-self.wrap(other))

    def __rsub__(self, other):
        return self.wrap(other) - self

    def __mul__(self, other):
        d = {}
        for (n, m), v in self.terms.items():
            for (j, k), w in self.wrap(other).terms.items():
                key = (n+j, m+k)
                d[key] = d.get(key, F(0)) + v*w
        return EP(d)

    __rmul__ = __mul__

    def __eq__(self, other):
        return self.terms == self.wrap(other).terms

    def derivative(self):
        out = EP()
        for (n, m), v in self.terms.items():
            if n:
                out += EP({(n-1, m): n*v})
            out += EP({(n, m): -m*v})
        return out

    def integral(self):
        return sum((v*integral_power(n, m) for (n, m), v in self.terms.items()), Expr())

    def endpoint(self):
        return sum((v*Expr({m: 1}) for (n, m), v in self.terms.items()), Expr())


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name+'.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    checks = []
    def check(name, condition, details=None):
        checks.append({'id': name, 'pass': bool(condition), 'details': details})

    # e=sum 1/k!. For k>=5, successive terms have ratio <=1/6.
    e_lo = sum((F(1, factorial(k)) for k in range(5)), F(0))
    e_hi = e_lo + F(1, factorial(5))/(1-F(1, 6))
    t_lo, t_hi = 1/e_hi, 1/e_lo
    check('EXP_TAYLOR_TAIL_GEOMETRIC_BOUND', F(8, 3) < e_lo < e_hi < 3)
    check('EXP_NEGATIVE_ONE_RANGE', F(1, 3) < t_lo < t_hi < F(3, 8))
    for n in range(5):
        for m in (-2, -1, 0, 1, 2):
            check(f'INTEGRAL_IBP_n{n}_m{m}', integral_power(n, m) == integral_power_ibp(n, m))

    u, decay = EP({(1, 0): 1}), EP({(0, 1): 1})
    e0, chi1, chi2, alpha = F(6), F(1), F(2), F(1, 2)
    energy = e0*decay

    # All constant: Pf=2-exp(-u), qf=L*2=2, Pfa=1.
    pf = 2-decay
    check('ALLCONSTANT_FROZEN_ODE_EXACT', pf.derivative()+pf-2 == 0)
    check('ALLCONSTANT_INCOMING_ZERO_FIRSTVAR_AND_REMAINDER_ZERO', EP() == 0)

    # Two positive rates with opposite variation; total L is constant.
    dlam = alpha*(u-F(1, 2))
    lam1, lam2 = F(1, 2)+dlam, F(1, 2)-dlam
    source = 1+u
    e = u
    check('CANCELLATION_TOTAL_OPACITY_CONSTANT', lam1+lam2 == 1)
    check('CANCELLATION_TRUE_AND_FIRSTVAR_ODE_EXACT', e.derivative()+e-source == 0)
    ra1 = (dlam*e).integral()
    ra2 = ((-dlam)*e).integral()
    rb1 = (energy*dlam*e).integral()
    rb2 = -rb1
    heat1, heat2 = rb1-chi1*ra1, rb2-chi2*ra2
    check('CANCELLATION_SPECIES_COUNT_NONZERO', ra1 == F(1, 24) and ra2 == -F(1, 24))
    check('CANCELLATION_TOTAL_COUNT_AND_ABSORBED_ENERGY_ZERO', ra1+ra2 == 0 and rb1+rb2 == 0)
    check('CANCELLATION_TOTAL_HEAT_NONZERO_BINDING_ENERGY_SPLIT', heat1+heat2 == F(1, 24))
    check('CANCELLATION_POSITIVE_HEAT_WEIGHT_ALL_ACTIVE_SPECIES', e0/e_hi > chi2)
    check('CANCELLATION_SPECIES_COEFFICIENT_DOMAIN', F(1, 2)-alpha/F(2) >= 0)
    check('CANCELLATION_NUMBER_LEDGER_EXACT', e.endpoint()+(e*(lam1+lam2)).integral()-source.integral() == 0)
    check('CANCELLATION_ENERGY_LEDGER_EXACT', e0*T*e.endpoint()+(energy*e*(lam1+lam2)).integral()+(energy*e).integral()-(energy*source).integral() == 0)

    # One positive variable rate; exact true defect e=u, but e1 differs.
    lam = 1+alpha*u
    source2 = 1+u+alpha*u*u
    e1 = u+alpha*(u*u-2*u+2-2*decay)
    remainder = u-e1
    check('VARIABLE_OPACITY_TRUE_ODE_EXACT', u.derivative()+lam*u-source2 == 0)
    check('VARIABLE_OPACITY_FIRSTVAR_ODE_EXACT', e1.derivative()+e1-source2 == 0)
    check('VARIABLE_OPACITY_REMAINDER_ODE_EXACT', remainder.derivative()+remainder+alpha*u*u == 0)
    rcount = (lam*u).integral()-e1.integral()
    renergy = (energy*lam*u).integral()-(energy*e1).integral()
    rred = (energy*remainder).integral()
    effective_count = alpha*T*integral_power(2, -1)
    effective_energy = e0*alpha*F(1, 2)*(integral_power(2, 1)+T*T*integral_power(2, -1))
    check('EFFECTIVE_KERNEL_COUNT_IDENTITY', rcount == effective_count)
    check('EFFECTIVE_KERNEL_ENERGY_IDENTITY', renergy == effective_energy)
    check('EFFECTIVE_KERNEL_HEAT_IDENTITY', renergy-chi1*rcount == effective_energy-chi1*effective_count)
    check('REMAINDER_TOTAL_COUNT_EQUALS_NEGATIVE_ENDPOINT', rcount+remainder.endpoint() == 0)
    check('REMAINDER_FULL_ENERGY_LEDGER_EXACT', e0*T*remainder.endpoint()+renergy+rred == 0)
    s = F(3, 2)+alpha/F(3)
    hh = alpha*T
    endpoint_magnitude = alpha*(1-2*T)
    bound_margin = s*hh-endpoint_magnitude
    check('ENDPOINT_Br_Hh_BOUND_VALID_IN_NONZERO_REMAINDER_TOY', bound_margin.bounds(t_lo, t_hi)[0] > 0)

    # L=0, source variation nonzero: no 1/L division permitted.
    frozen0 = 1+u
    exact0 = frozen0+F(1, 2)*u*u
    e10 = F(1, 2)*u*u
    check('ZERO_L_NONZERO_SOURCE_FROZEN_ODE', frozen0.derivative()-1 == 0)
    check('ZERO_L_NONZERO_SOURCE_TRUE_ODE', exact0.derivative()-(1+u) == 0)
    check('ZERO_L_NONZERO_SOURCE_RESPONSE_EXACT', e10.derivative()-u == 0)
    check('ZERO_L_SOURCE_NUMBER_LEDGER', e10.endpoint()-u.integral() == 0)
    check('ZERO_L_SOURCE_ENERGY_REDSHIFT_LEDGER', e0*T*e10.endpoint()+(energy*e10).integral()-(energy*u).integral() == 0)

    # Missing incoming uncertainty would wrongly return a zero bound.
    eta = F(1, 8)
    incoming = eta*decay
    incoming_count = incoming.integral()
    incoming_energy = (energy*incoming).integral()
    check('INCOMING_CONSTANT_COEFFICIENT_ODE', incoming.derivative()+incoming == 0)
    check('INCOMING_ENDPOINT_REQUIRED_DESPITE_D_Br_ZERO', incoming.endpoint().bounds(t_lo, t_hi)[0] > 0)
    check('INCOMING_COUNT_REQUIRED_DESPITE_D_Br_ZERO', incoming_count == eta*(1-T) and incoming_count.bounds(t_lo, t_hi)[0] > 0)
    check('INCOMING_ENERGY_REQUIRED_DESPITE_D_Br_ZERO', incoming_energy == eta*e0*F(1, 2)*(1-T*T))

    # E0=1, chi=2 violates positive heat weight; KQ(0) is negative.
    negative_kq = F(1, 2)*(1-T*T)-2*(1-T)
    check('THRESHOLD_NEGATIVE_WEIGHT_INVALIDATES_POSITIVE_KERNEL_ASSUMPTION', negative_kq.bounds(t_lo, t_hi)[1] < 0)
    check('INACTIVE_SPECIES_EXACT_ZERO_DESPITE_NEGATIVE_UNUSED_WEIGHT', 0*negative_kq == 0)

    # Per-cell midpoint constant is 1/24, with derivatives in t=u/h.
    n, h = 4, F(3, 2)
    true_quadratic = h*h*h/F(3)
    midpoint_quadratic = h*sum((h*h*F(2*j+1, 2*n)**2 for j in range(n)), F(0))/n
    derivative_t2 = 2*h*h
    error_quadratic = true_quadratic-midpoint_quadratic
    midpoint_bound = sum((h*derivative_t2/F(24*n**3) for _ in range(n)), F(0))
    check('MIDPOINT_FACTOR_24_AND_NORMALIZED_SECOND_DERIVATIVE', error_quadratic == midpoint_bound)
    q4 = sum((F(2*j+1, 2*n)**4 for j in range(n)), F(0))/n
    q4_bound = sum((12*F(j+1, n)**2/F(24*n**3) for j in range(n)), F(0))
    check('MIDPOINT_CELLWISE_SECOND_DERIVATIVE_BOUND_QUARTIC', abs(F(1, 5)-q4) <= q4_bound)
    check('MIDPOINT_ZERO_DURATION_EXACT_ZERO', F(0)*q4_bound == 0)

    # |t-1/2| is not C2 at its interior root. Sampling f''=0 is invalid.
    n_kink = 3
    kink_quad = sum((abs(F(2*j+1, 2*n_kink)-F(1, 2)) for j in range(n_kink)), F(0))/n_kink
    kink_upper = sum((max(abs(F(j, n_kink)-F(1, 2)), abs(F(j+1, n_kink)-F(1, 2))) for j in range(n_kink)), F(0))/n_kink
    check('ABSOLUTE_VALUE_KINK_MIDPOINT_ZERO_CURVATURE_COUNTEREXAMPLE', kink_quad != F(1, 4))
    check('ABSOLUTE_VALUE_KINK_INTERVAL_RIEMANN_BOUND_VALID', kink_upper >= F(1, 4))

    result = {
        'schema': 'bass-he-e13c4-exact-rational-toys-v1',
        'role': 'THEORY_CONTRIBUTOR_NOT_DECISION_REVIEWER',
        'arithmetic': 'fractions.Fraction and formal Laurent polynomials in T=exp(-1); no float evaluations',
        'producer_sha256_as_run': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'contract_sha256_as_run': hashlib.sha256(Path(__file__).with_name('TASK_CONTRACT.json').read_bytes()).hexdigest(),
        'rational_exp_enclosure': {'exp_1_lower': str(e_lo), 'exp_1_upper': str(e_hi), 'exp_minus_1_lower': str(t_lo), 'exp_minus_1_upper': str(t_hi)},
        'specific_counterexamples': {
            'total_opacity_cancellation_species_count_remainder': [ra1.json(), ra2.json()],
            'total_opacity_cancellation_total_heat_remainder_eV': (heat1+heat2).json(),
            'nonzero_total_opacity_endpoint_remainder': remainder.endpoint().json(),
            'incoming_endpoint_missing_if_eta_omitted': incoming.endpoint().json(),
            'negative_heat_kernel_at_v_zero': negative_kq.json(),
            'midpoint_quadratic_error': str(error_quadratic),
            'absolute_kink_true_integral': '1/4',
            'absolute_kink_midpoint_estimate': str(kink_quad),
            'absolute_kink_interval_upper_bound': str(kink_upper)
        },
        'checks': checks,
        'passed': sum(c['pass'] for c in checks),
        'failed': sum(not c['pass'] for c in checks),
        'first_failure': next((c for c in checks if not c['pass']), None),
        'physical_solver_calls': 0,
        'inherited_solver_calls': 0,
        'claim_ceiling': 'Exact toy algebra and theorem-risk checks only; not six-control enclosure verification, not physical adoption.'
    }
    atomic_json(Path(sys.argv[1]), result)
    print(json.dumps({'passed': result['passed'], 'failed': result['failed'], 'first_failure': result['first_failure'], 'producer_sha256_as_run': result['producer_sha256_as_run']}))
    return 0 if result['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
