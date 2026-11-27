"""Bounded exact-rational PHYS03 checker: algebra only, no IVP/native/BE/NCP.

Direct time/parameter power-series recurrence is compared with an independently
differentiated sparse polynomial vector field and the claimed tensor formulas.
The fixtures are nonphysical and supply no cosmological/atomic history.
"""
from fractions import Fraction as R
from pathlib import Path
import json
import traceback
from decimal import Decimal, localcontext

DIM = 5  # x, dummy nonphoto gas coordinate, w, P1, P2
Z0 = (R(1, 5), R(1, 7), R(11, 4), R(1, 11), R(1, 13))
CHI = R(7, 2)
ETA = (R(1), R(0), -CHI, R(0), R(0))


class MP:
    """Exact sparse polynomials; no truncation and no calculus of time jets."""
    nv = DIM + 1  # explicit time plus state
    def __init__(self, value=0):
        self.p = ({k: R(v) for k, v in value.items() if v}
                  if isinstance(value, dict) else
                  ({(0,) * self.nv: R(value)} if value else {}))
    @classmethod
    def var(cls, i):
        key = [0] * cls.nv
        key[i] = 1
        return cls({tuple(key): R(1)})
    @classmethod
    def cast(cls, x): return x if isinstance(x, cls) else cls(x)
    def __add__(self, other):
        p = dict(self.p)
        for key, value in self.cast(other).p.items():
            p[key] = p.get(key, R(0)) + value
        return MP(p)
    __radd__ = __add__
    def __neg__(self): return MP({key: -value for key, value in self.p.items()})
    def __sub__(self, other): return self + (-self.cast(other))
    def __rsub__(self, other): return self.cast(other) - self
    def __mul__(self, other):
        p = {}
        for ka, a in self.p.items():
            for kb, b in self.cast(other).p.items():
                key = tuple(ka[i] + kb[i] for i in range(self.nv))
                p[key] = p.get(key, R(0)) + a*b
        return MP(p)
    __rmul__ = __mul__
    def __pow__(self, n):
        result = MP(1)
        for _ in range(n): result *= self
        return result
    def diff(self, *indices):
        result = self
        for index in indices:
            p = {}
            for key, value in result.p.items():
                if key[index]:
                    new = list(key)
                    new[index] -= 1
                    new = tuple(new)
                    p[new] = p.get(new, R(0)) + key[index]*value
            result = MP(p)
        return result
    def at(self, point):
        result = R(0)
        for key, value in self.p.items():
            for x, n in zip(point, key): value *= x**n
            result += value
        return result


class TJ:
    """Truncated time/parameter series: t<=5, e_lambda<=1, e_S<=1."""
    def __init__(self, value=0):
        self.p = ({k: R(v) for k, v in value.items() if v}
                  if isinstance(value, dict) else
                  ({(0, 0, 0): R(value)} if value else {}))
    @classmethod
    def cast(cls, x): return x if isinstance(x, cls) else cls(x)
    def __add__(self, other):
        p = dict(self.p)
        for key, value in self.cast(other).p.items():
            p[key] = p.get(key, R(0)) + value
        return TJ(p)
    __radd__ = __add__
    def __neg__(self): return TJ({key: -value for key, value in self.p.items()})
    def __sub__(self, other): return self + (-self.cast(other))
    def __rsub__(self, other): return self.cast(other) - self
    def __mul__(self, other):
        p = {}
        for ka, a in self.p.items():
            for kb, b in self.cast(other).p.items():
                key = tuple(ka[i] + kb[i] for i in range(3))
                if key[0] <= 5 and key[1] <= 1 and key[2] <= 1:
                    p[key] = p.get(key, R(0)) + a*b
        return TJ(p)
    __rmul__ = __mul__
    def __pow__(self, n):
        result = TJ(1)
        for _ in range(n): result *= self
        return result


def fields(t, z, mode):
    x, y, w, p1, p2 = z
    zero = 0*t
    tp = t if mode in ('all', 'photo') else zero
    th = t if mode in ('all', 'hh') else zero
    tb = t if mode in ('all', 'birth') else zero
    tn = t if mode in ('all', 'nonphoto') else zero
    ta = t if mode == 'additive_drift' else zero
    n = (
        R(1, 7)+x*y-R(2, 9)*w*w+tn*(R(1, 3)*x*x+y*w)+ta*R(2, 3),
        x*x-y*w+R(1, 3)*y+tn*x*w+ta*R(3, 7),
        R(2, 5)*x*w+y*y-R(1, 4)*w+tn*(x*y+w*w)+ta*R(5, 11),
    )
    a1 = 2*(1+R(1, 4)*tp)
    a2 = 3*(1-R(1, 5)*tp)
    g1, g2 = R(1, 3)+R(1, 9)*tp, R(2, 5)-R(1, 11)*tp
    neutral = 1-x
    q = neutral*neutral*(1+w*w+x*y)*(1+R(2, 7)*th+R(1, 13)*th*th)
    base = (
        n[0]+neutral*(a1*p1+a2*p2),
        n[1],
        n[2]+neutral*(a1*g1*p1+a2*g2*p2),
        -a1*neutral*p1,
        -a2*neutral*p2,
    )
    hh = (q, zero, -CHI*q, zero, zero)
    birth = (zero, zero, zero, R(1, 5)*tb, 1+R(1, 3)*tb+R(1, 7)*tb*tb)
    return base, hh, birth


def field(t, z, lam, src, mode):
    f0, h, birth = fields(t, z, mode)
    return [f0[i]+lam*h[i]+src*birth[i] for i in range(DIM)]


def va(*args): return [sum(v[i] for v in args) for i in range(DIM)]
def vm(a, v): return [a*x for x in v]
def matrix_apply(matrix, v): return [sum(a*b for a, b in zip(row, v)) for row in matrix]
def tensor_apply(tensor, v, w):
    return [sum(row[i][j]*v[i]*w[j] for i in range(DIM) for j in range(DIM)) for row in tensor]


def tensors(t0, lam, src, mode):
    vars_ = [MP.var(i) for i in range(DIM+1)]
    t, z = vars_[0], vars_[1:]
    fp = field(t, z, lam, src, mode)
    _, hp, bp = fields(t, z, mode)
    point = (t0,)+Z0
    value = lambda polys: [MP.cast(p).at(point) for p in polys]
    first = lambda polys: [[MP.cast(p).diff(i+1).at(point) for i in range(DIM)] for p in polys]
    second = lambda polys: [[[MP.cast(p).diff(i+1,j+1).at(point) for j in range(DIM)] for i in range(DIM)] for p in polys]
    ft, ht, bt = ([MP.cast(p).diff(0) for p in ps] for ps in (fp, hp, bp))
    f, h, birth = map(value, (fp, hp, bp))
    h_t, b_t = map(value, (ht, bt))
    j, hp1, jt, htz = map(first, (fp, hp, ft, ht))
    q, hp2, qt = map(second, (fp, hp, ft))
    J = lambda v: matrix_apply(j, v)
    HP = lambda v: matrix_apply(hp1, v)
    JT = lambda v: matrix_apply(jt, v)
    HTZ = lambda v: matrix_apply(htz, v)
    Q = lambda v,w: tensor_apply(q, v, w)
    HPP = lambda v,w: tensor_apply(hp2, v, w)
    QT = lambda v,w: tensor_apply(qt, v, w)
    c = J(birth)
    k3 = va(HP(c), vm(2,Q(h,birth)))
    frozen4 = va(J(k3), vm(3,Q(birth,va(J(h),HP(f)))), vm(3,Q(h,c)),
                 HP(va(J(c),vm(2,Q(f,birth)))), vm(3,HPP(f,c)))
    drift4 = va(vm(3,Q(h_t,birth)), vm(3,Q(h,b_t)), vm(6,QT(h,birth)),
                HP(va(J(b_t),vm(2,JT(birth)))), vm(3,HTZ(c)))
    return k3, frozen4, drift4


def series(t0, lam, src, mode, order=4, freeze=False):
    t = TJ(t0) if freeze else TJ(t0)+TJ({(1,0,0):1})
    z = [TJ(v) for v in Z0]
    lp, sp = TJ(lam)+TJ({(0,1,0):1}), TJ(src)+TJ({(0,0,1):1})
    for n in range(1,order+1):
        f = field(t,z,lp,sp,mode)
        for i in range(DIM):
            z[i] += TJ({(n,a,b): f[i].p.get((n-1,a,b),R(0))/n
                        for a in range(2) for b in range(2)})
    fact = 1
    results = {}
    for n in range(order+1):
        if n: fact *= n
        results[n] = [fact*p.p.get((n,1,1),R(0)) for p in z]
    return results


def check_series():
    checks = []
    for mode in ('all','birth','hh','photo','nonphoto','additive_drift'):
        # Six joint parameter points include exact axes and finite lambda.
        t0 = R(1, 17) if mode == 'all' else R(0)
        k40 = va(*tensors(t0,R(0),R(0),mode)[1:])
        k41 = va(va(*tensors(t0,R(1),R(0),mode)[1:]),vm(-1,k40))
        for lam in (R(0),R(1,3),R(1)):
            for src in (R(0),R(2,7)):
                direct = series(t0,lam,src,mode)
                frozen = series(t0,lam,src,mode,freeze=True)
                k3, f4, d4 = tensors(t0,lam,src,mode)
                assert direct[0] == direct[1] == direct[2] == [0]*DIM
                assert direct[3] == frozen[3] == k3
                assert direct[4] == va(f4,d4)
                assert frozen[4] == f4
                assert va(direct[4],vm(-1,frozen[4])) == d4
                assert direct[4] == va(k40,vm(lam,k41))
                if mode in ('nonphoto','additive_drift'):
                    assert d4 == [0]*DIM
                checks.append({'mode':mode,'lambda':str(lam),'S':str(src),
                               'cubic_unchanged':True,'quartic_formula':True,
                               'quartic_S_independent_lambda_affine':True})
    a = series(R(0),R(1,3),R(0),'additive_drift',order=5)
    f = series(R(0),R(1,3),R(0),'additive_drift',order=5,freeze=True)
    assert a[3] == f[3] and a[4] == f[4] and a[5][0] != f[5][0]
    return checks, {'first_differing_mixed_x_order':5,
                    'delta_fifth_derivative_x':str(a[5][0]-f[5][0])}


def poly_integral(coeffs, upper):
    return sum(c*upper**(n+1)/R(n+1) for n,c in enumerate(coeffs))


def check_birth_kernel():
    # Independent scalar kernel checks; arbitrary rational diagnostic constants.
    a, q, xi, end = R(2,7),R(3,11),R(5,13),R(7,3)
    hc, d = -a*q*(2+xi), -a*q
    # K(s) = hc*(end-s)^2/2 + d*(end^2-s^2)/2.
    coefficients = ((hc+d)*end*end/2, -hc*end, (hc-d)/2)
    uniform = poly_integral(coefficients,end)
    linear_profile = poly_integral((R(0),)+coefficients,end)
    assert uniform == -a*q*(4+xi)*end**3/6
    assert linear_profile == -a*q*(5+xi)*end**4/24
    initial = coefficients[0]
    terminal = sum(c*end**n for n,c in enumerate(coefficients))
    assert initial == -a*q*(3+xi)*end**2/2 and terminal == 0
    samples = []
    previous = None
    for f in (R(0),R(1,4),R(1,2),R(3,4),R(1)):
        birth = f*end
        correct = sum(c*birth**n for n,c in enumerate(coefficients))
        incorrectly_reset = (hc+d)*(end-birth)**2/2
        memory = birth*(end-birth)*d
        assert correct-incorrectly_reset == memory
        if previous is not None: assert correct > previous
        previous = correct
        samples.append({'birth_fraction':str(f),'kernel_x':str(correct),
                        'prebirth_HH_memory':str(memory)})
    return {'uniform_integral_matches_cubic':True,
            'linear_profile_matches_birth_quartic':True,
            'initial_impulse_matches':True,'terminal_impulse_zero':True,
            'prebirth_memory_identity':True,'samples':samples}


def check_formal_be_ladders():
    """Formal implicit-series substitution only; no numerical BE root exists here."""
    qpoly = (1-MP.var(1))**2*(1+MP.var(3)**2+MP.var(1)*MP.var(2))
    point = (R(0),)+Z0
    q0 = qpoly.at(point)
    qgrad = [qpoly.diff(i+1).at(point) for i in range(DIM)]
    birth = [R(0),R(0),R(0),R(0),R(1)]
    d = [R(1),R(0),R(2,5),R(0),-R(1)]
    c = vm(3*(1-Z0[0]),d)
    X = vm(sum(a*b for a,b in zip(qgrad,c)),ETA)
    D = vm(-3*q0,d)
    xi_effective = -(1-Z0[0])*sum(a*b for a,b in zip(qgrad,d))/q0-2
    results = []
    for m in (1,2,3,5,8):
        alpha = R((m+1)*(m+2),6*m*m)
        beta = R((m+1)*(2*m+1),6*m*m)
        target = va(vm(alpha,X),vm(beta,D))
        cm = (4+xi_effective)/6+(3+xi_effective)/R(2*m)+(5+2*xi_effective)/R(6*m*m)
        assert target[0] == -3*q0*cm
        for lam0 in (R(0),R(1,3)):
            lam = TJ(lam0)+TJ({(0,1,0):1})
            src = TJ({(0,0,1):1})
            dt = TJ({(1,0,0):R(1,m)})
            z = [TJ(value) for value in Z0]
            for _step in range(m):
                old = z
                constant = [old[i]+dt*src*birth[i] for i in range(DIM)]
                guess = constant
                # Multiplication by dt raises the unknown coefficient order.
                # Three substitutions determine every coefficient through h^3 exactly.
                for _order in range(3):
                    rhs = field(TJ(0),guess,lam,R(0),'none')
                    guess = [constant[i]+dt*rhs[i] for i in range(DIM)]
                z = guess
            measured = [value.p.get((3,1,1),R(0)) for value in z]
            assert measured == target
            results.append({'m':m,'lambda_base':str(lam0),'alpha_X':str(alpha),
                            'beta_D':str(beta),'all_state_coefficients_equal':True})
    return {'status':'PASS_FORMAL_IMPLICIT_SERIES_ONLY','cases':results,
            'physical_BE_roots_solved':0,'nonlinear_BE_iterations':0,
            'polynomial_substitutions_per_step':3,
            'comment':'No state trajectory or finite-step BE solution is produced.'}


def source_profile_diagnostics(root):
    source = root/'SOURCE_PROFILE_INPUT.json'
    if not source.exists():
        return {'status':'NOT_RUN_OPTIONAL_SOURCE_INPUT_ABSENT'}
    data = json.loads(source.read_text())
    with localcontext() as context:
        context.prec = 70
        xi = Decimal(data['Xi0'])
        scale = Decimal(data['AqSstar_Delta3'])
        factors = {
            'uniform_continuous':-(4+xi)/6,
            'initial_impulse_continuous':-(3+xi)/2,
            'terminal_impulse_continuous':Decimal(0),
            'birth_plus_one_frozen_BE_map':-(3+xi),
        }
        assert factors['birth_plus_one_frozen_BE_map'] == 2*factors['initial_impulse_continuous']
        return {
            'status':'LEADING_COEFFICIENT_DIAGNOSTICS_ONLY',
            'source_provenance':data['provenance'],
            'normalization':'I_x/(lambda*M*Aq*Delta^2), M=Sstar*Delta',
            'dimensionless_factors':{k:str(v) for k,v in factors.items()},
            'leading_mixed_x_at_inherited_scale':{k:str(v*scale) for k,v in factors.items()},
            'initial_to_uniform_ratio':str(factors['initial_impulse_continuous']/factors['uniform_continuous']),
            'BE_map_to_uniform_ratio':str(factors['birth_plus_one_frozen_BE_map']/factors['uniform_continuous']),
            'BE_map_to_initial_impulse_ratio':'2',
            'repeated_birth_BE_ladder_dimensionless_Cm':{
                str(m):str((4+xi)/6+(3+xi)/(2*m)+(5+2*xi)/(6*m*m))
                for m in (1,2,4,8,16,64)},
            'repeated_birth_BE_ladder_limit_Cinf':str((4+xi)/6),
            'native_or_actual_finite_error':False,
            'new_physical_background_or_history':False,
            'numeric_precision_digits':70,
            'outward_interval_certificate':False,
        }


def main():
    out = Path(__file__).resolve().parent
    result_path = out/'NONAUTONOMOUS_EXACT_CHECK.json'
    try:
        checks, additive = check_series()
        kernel = check_birth_kernel()
        be_ladders = check_formal_be_ladders()
        diagnostics = source_profile_diagnostics(out)
        result = {
            'status':'PASS_EXACT_NONPHYSICAL_ALGEBRA_FIXTURES',
            'arithmetic':'Python standard-library fractions.Fraction',
            'time_series_order_max':5,'gas_coordinates':3,'photon_coordinates':2,
            'cubic_quartic_cases':checks,'additive_time_drift_fixture':additive,
            'birth_kernel_checks':kernel,
            'formal_BE_ladder_checks':be_ladders,
            'source_profile_diagnostics':diagnostics,
            'physical_history_evaluated_in_this_checker':False,
            'actual_background_availability':'Parent source survey reports an explicit hybrid owner background; this checker does not bind or evaluate it.',
            'actual_parameter_family_connection':'unresolved',
            'physical_numerical_certificate':False,
            'scientific_IVP_or_native_or_BE_root_or_NCP_runs':0,
            'first_failure_path':str(out/'FIRST_FAILURE.json') if (out/'FIRST_FAILURE.json').exists() else None,
        }
        result_path.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'status':result['status'],'cases':len(checks),'output':str(result_path)}))
    except Exception:
        failure = {'status':'FAIL_ALGEBRA_FIXTURE','traceback':traceback.format_exc(),
                   'scientific_IVP_or_native_or_BE_root_or_NCP_runs':0}
        try:
            with (out/'FIRST_FAILURE.json').open('x') as stream:
                json.dump(failure,stream,indent=2)
                stream.write('\n')
        except FileExistsError:
            pass
        result_path.write_text(json.dumps(failure,indent=2)+'\n')
        raise


if __name__ == '__main__':
    main()
