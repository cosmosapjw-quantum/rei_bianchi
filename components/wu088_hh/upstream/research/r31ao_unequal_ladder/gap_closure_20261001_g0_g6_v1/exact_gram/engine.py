"""Bounded exact Gram and gap arithmetic for finite represented matrices.

Backend: EXACT_INTEGER_SQRT_RATIONAL_ENCLOSURE. No NumPy/SciPy/native backend,
archived-data loader, producer or comparator is imported or run by this module.
Inputs are exact fractions, never host floating approximations.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt


class ContractError(ValueError):
    """Unsupported/malformed/nonfinite input: no certificate returned."""


class ResourceLimit(ContractError):
    """Predeclared exact-arithmetic work limit exceeded; fail closed."""


@dataclass(frozen=True)
class Limits:
    max_precision: int = 4096
    max_entries: int = 1024
    max_integer_bits: int = 131072
    max_work_bits: int = 270336
    max_operations: int = 100000

    def __post_init__(self):
        for name, value in vars(self).items():
            if type(value) is not int or value <= 0:
                raise ContractError(f'{name} must be a positive integer')


DEFAULT_LIMITS = Limits()


def _q(x):
    if not isinstance(x, Fraction):
        raise ContractError('exact Fraction required; floats/decimal strings are not implicit inputs')
    return x


def _nonnegative(x):
    x = _q(x)
    if x < 0:
        raise ContractError('nonnegative bound required')
    return x


class _Work:
    def __init__(self, limits):
        if not isinstance(limits, Limits):
            raise ContractError('Limits required')
        self.limits = limits
        self.operations = 0

    def tick(self, n=1):
        self.operations += n
        if self.operations > self.limits.max_operations:
            raise ResourceLimit('exact operation budget exhausted')

    def check(self, q):
        q = _q(q)
        if max(q.numerator.bit_length(), q.denominator.bit_length()) > self.limits.max_integer_bits:
            raise ResourceLimit('rational input/intermediate bit limit exceeded')
        return q

    def binary(self, a, b, operation):
        self.check(a)
        self.check(b)
        # Cross products in +,-,*,/ stay below these integer-size bounds.
        if max(a.numerator.bit_length(), a.denominator.bit_length()) + max(b.numerator.bit_length(), b.denominator.bit_length()) + 2 > self.limits.max_work_bits:
            raise ResourceLimit('rational intermediate allocation cap exceeded')
        self.tick()
        if operation == '+':
            c = a+b
        elif operation == '-':
            c = a-b
        elif operation == '*':
            c = a*b
        else:
            raise ContractError('unknown internal exact operation')
        return self.check(c)


@dataclass(frozen=True)
class Interval:
    lo: Fraction
    hi: Fraction

    def __post_init__(self):
        _q(self.lo)
        _q(self.hi)
        if self.lo > self.hi:
            raise ContractError('reversed interval')

    def to_json(self):
        return {'lo': str(self.lo), 'hi': str(self.hi), 'endpoints': 'EXACT_RATIONAL'}


@dataclass(frozen=True)
class ComplexDisk:
    center: tuple
    radius: Fraction

    def __post_init__(self):
        _complex(self.center)
        _nonnegative(self.radius)


def _complex(z):
    if not isinstance(z, tuple) or len(z) != 2:
        raise ContractError('complex exact value must be (Fraction, Fraction)')
    _q(z[0])
    _q(z[1])
    return z


def _matrix(a, work):
    if not isinstance(a, (list, tuple)) or not a:
        raise ContractError('nonempty finite nested row sequence required')
    if not isinstance(a[0], (list, tuple)) or not a[0]:
        raise ContractError('nonempty finite rows required')
    m, n = len(a), len(a[0])
    if m*n > work.limits.max_entries:
        raise ResourceLimit('matrix entry budget exceeded')
    for row in a:
        if not isinstance(row, (list, tuple)) or len(row) != n:
            raise ContractError('ragged matrix')
        for z in row:
            for v in _complex(z):
                work.check(v)
    return m, n


def from_decoded(decoded, *, limits=DEFAULT_LIMITS):
    """Adapter to G2 .shape/.values_c_order; decoder has already ordered axes."""
    shape = decoded.shape
    if not isinstance(shape, (list, tuple)) or len(shape) != 2 or any(type(v) is not int or v <= 0 for v in shape):
        raise ContractError('rank-two positive decoded shape required')
    m, n = shape
    if m*n > limits.max_entries:
        raise ResourceLimit('decoded matrix entry budget exceeded')
    values = decoded.values_c_order
    if not isinstance(values, (list, tuple)) or len(values) != m*n:
        raise ContractError('decoded C-order value length mismatch')
    a = [list(values[i*n:(i+1)*n]) for i in range(m)]
    _matrix(a, _Work(limits))
    return a


def _adjoint(a):
    return [[(a[i][j][0], -a[i][j][1]) for i in range(len(a))] for j in range(len(a[0]))]


def adjoint(a, *, limits=DEFAULT_LIMITS):
    _matrix(a, _Work(limits))
    return _adjoint(a)


def _subtract(a, b, work):
    if _matrix(a, work) != _matrix(b, work):
        raise ContractError('matrix shape mismatch')
    return [[tuple(work.binary(x, y, '-') for x,y in zip(za,zb)) for za,zb in zip(ra,rb)] for ra,rb in zip(a,b)]


def _k(c, r, work):
    m, n = _matrix(c, work)
    if n != 2 or _matrix(r, work) != (2,m):
        raise ContractError('C must be n by 2 and R must be 2 by n')
    difference = _subtract(c, _adjoint(r), work)
    return [[tuple(work.binary(x, Fraction(1,2), '*') for x in z) for z in row] for row in difference]


def construct_k(c, r, *, limits=DEFAULT_LIMITS):
    """Exact K=(C-R†)/2; predictions retain their independently stored K."""
    return _k(c, r, _Work(limits))


def _sqrt(q, precision, work):
    work.check(_nonnegative(q))
    if type(precision) is not int or precision < 1:
        raise ContractError('positive integer sqrt precision required')
    if precision > work.limits.max_precision:
        raise ResourceLimit('sqrt precision cap exceeded')
    work.tick()
    # isqrt's operands and the perfect-square checks also consume the work
    # budget; the exact-root shortcut must not bypass allocation limits.
    if max(q.numerator.bit_length(), q.denominator.bit_length())+1 > work.limits.max_work_bits:
        raise ResourceLimit('sqrt exact-root work-bit cap exceeded')
    # First return exact rational square roots, regardless of dyadic grid size.
    pn, pd = isqrt(q.numerator), isqrt(q.denominator)
    if pn*pn == q.numerator and pd*pd == q.denominator:
        s = Fraction(pn, pd)
        return Interval(s,s)
    if q.numerator.bit_length()+2*precision > work.limits.max_work_bits:
        raise ResourceLimit('sqrt shifted-integer allocation cap exceeded')
    scaled_floor = (q.numerator << (2*precision)) // q.denominator
    k = isqrt(scaled_floor)
    lo = work.check(Fraction(k, 1 << precision))
    hi = work.check(Fraction(k+1, 1 << precision))
    return Interval(lo, hi)


def sqrt_interval(q, *, precision=160, limits=DEFAULT_LIMITS):
    """Outward interval sqrt via integer isqrt; absolute width <=2**(-p)."""
    return _sqrt(q, precision, _Work(limits))


def _gram(a, work):
    m, n = _matrix(a, work)
    if n != 2:
        if m != 2:
            raise ContractError('Gram reduction requires n by 2 or 2 by n')
        a = _adjoint(a)
    aa = dd = br = bi = Fraction(0)
    for (xr,xi),(yr,yi) in a:
        aa = work.binary(aa, work.binary(work.binary(xr,xr,'*'),work.binary(xi,xi,'*'),'+'),'+')
        dd = work.binary(dd, work.binary(work.binary(yr,yr,'*'),work.binary(yi,yi,'*'),'+'),'+')
        br = work.binary(br, work.binary(work.binary(xr,yr,'*'),work.binary(xi,yi,'*'),'+'),'+')
        bi = work.binary(bi, work.binary(work.binary(xr,yi,'*'),work.binary(xi,yr,'*'),'-'),'+')
    return aa, (br,bi), dd


def gram2(a, *, limits=DEFAULT_LIMITS):
    """Return a,b,d of [[a,b],[conj(b),d]] for A†A (AA† for wide A)."""
    return _gram(a, _Work(limits))


def _norm(a, precision, work):
    aa, (br,bi), dd = _gram(a, work)
    delta = work.binary(aa,dd,'-')
    b2 = work.binary(work.binary(br,br,'*'),work.binary(bi,bi,'*'),'+')
    discriminant = work.binary(work.binary(delta,delta,'*'), work.binary(Fraction(4),b2,'*'), '+')
    root = _sqrt(discriminant, precision, work)
    trace = work.binary(aa,dd,'+')
    lo = work.binary(work.binary(trace,root.lo,'+'),Fraction(1,2),'*')
    hi = work.binary(work.binary(trace,root.hi,'+'),Fraction(1,2),'*')
    return Interval(_sqrt(lo,precision,work).lo, _sqrt(hi,precision,work).hi)


def spectral_norm(a, *, precision=160, limits=DEFAULT_LIMITS):
    return _norm(a, precision, _Work(limits))


def interval_max(a, b):
    if not isinstance(a,Interval) or not isinstance(b,Interval):
        raise ContractError('Interval operands required')
    return Interval(max(a.lo,b.lo),max(a.hi,b.hi))


def _errors(prediction, raw_col, raw_row, raw_k, precision, work):
    if not isinstance(prediction,dict) or not {'K','D_col','D_row'} <= prediction.keys():
        raise ContractError('stored K, D_col and D_row prediction fields required')
    c = _norm(_subtract(prediction['D_col'],raw_col,work),precision,work)
    r = _norm(_subtract(prediction['D_row'],raw_row,work),precision,work)
    k = _norm(_subtract(prediction['K'],raw_k,work),precision,work)
    return {'K':k,'D_col':c,'D_row':r,'Dmax':interval_max(c,r)}


def represented_errors(prediction, raw_col, raw_row, *, precision=160, limits=DEFAULT_LIMITS):
    work = _Work(limits)
    return _errors(prediction,raw_col,raw_row,_k(raw_col,raw_row,work),precision,work)


def represented_gaps(models, raw_col, raw_row, *, precision=160, limits=DEFAULT_LIMITS):
    """Gap=other-local; one R31AK computation is reused for both comparisons."""
    if not isinstance(models,dict) or set(models) != {'R31AK','R31Z','R31AD'}:
        raise ContractError('exactly frozen R31AK/R31Z/R31AD models required')
    work = _Work(limits)
    raw_k = _k(raw_col,raw_row,work)
    errors = {name:_errors(models[name],raw_col,raw_row,raw_k,precision,work) for name in ('R31AK','R31Z','R31AD')}
    result = {'model_errors': errors}
    for comparison,other in [('PRIMARY','R31Z'),('SECONDARY','R31AD')]:
        result[comparison] = {metric: Interval(work.binary(errors[other][metric].lo,errors['R31AK'][metric].hi,'-'),work.binary(errors[other][metric].hi,errors['R31AK'][metric].lo,'-')) for metric in ('K','Dmax')}
    return result


def source_error_bound_disk(raw, target, *, precision=160, limits=DEFAULT_LIMITS):
    """Frobenius upper bound from proven target complex disks (no proof admission).

    The caller must separately establish that every disk encloses the prescribed
    continuous target. This function verifies arithmetic only, not provenance.
    """
    work = _Work(limits)
    m,n = _matrix(raw,work)
    if not isinstance(target,(list,tuple)) or len(target)!=m or any(not isinstance(row,(list,tuple)) or len(row)!=n for row in target):
        raise ContractError('target disk shape mismatch')
    total = Fraction(0)
    for row,balls in zip(raw,target):
        for value,ball in zip(row,balls):
            if not isinstance(ball,ComplexDisk):
                raise ContractError('complex disk convention required')
            dr = work.binary(value[0],ball.center[0],'-')
            di = work.binary(value[1],ball.center[1],'-')
            dist = _sqrt(work.binary(work.binary(dr,dr,'*'),work.binary(di,di,'*'),'+'),precision,work).hi
            bound = work.binary(dist,ball.radius,'+')
            total = work.binary(total,work.binary(bound,bound,'*'),'+')
    return _sqrt(total,precision,work).hi


def propagate_epsilon(epsilon_col, epsilon_row, *, limits=DEFAULT_LIMITS):
    """End-to-end D-block errors only; no X0..X8 producer term is added."""
    work = _Work(limits)
    c,r = _nonnegative(epsilon_col),_nonnegative(epsilon_row)
    return {'K':work.binary(work.binary(c,r,'+'),Fraction(1,2),'*'),
            'Dmax':max(c,r)}


def direct_gap_lower(gap, epsilon, *, limits=DEFAULT_LIMITS):
    if not isinstance(gap,Interval):
        raise ContractError('gap interval required')
    work = _Work(limits)
    return work.binary(gap.lo,work.binary(Fraction(2),_nonnegative(epsilon),'*'),'-')


def legacy_eta(ghat, gap, *, limits=DEFAULT_LIMITS):
    if not isinstance(gap,Interval):
        raise ContractError('gap interval required')
    work = _Work(limits)
    return max(abs(work.binary(_q(ghat),gap.lo,'-')),abs(work.binary(ghat,gap.hi,'-')))


def legacy_gap_lower(ghat, eta, epsilon, *, limits=DEFAULT_LIMITS):
    work = _Work(limits)
    return work.binary(work.binary(_q(ghat),_nonnegative(eta),'-'),work.binary(Fraction(2),_nonnegative(epsilon),'*'),'-')


def binary64_value(bits):
    """Exact finite IEEE binary64 value from a 64-bit unsigned integer."""
    if type(bits) is not int or not 0 <= bits < 1<<64:
        raise ContractError('uint64 bit pattern required')
    sign = -1 if bits>>63 else 1
    exponent, fraction = (bits>>52)&0x7ff, bits&((1<<52)-1)
    if exponent == 0x7ff:
        raise ContractError('nonfinite binary64 rejected')
    mantissa = fraction if exponent == 0 else fraction+(1<<52)
    power = -1074 if exponent == 0 else exponent-1023-52
    return Fraction(sign*mantissa*(1<<max(0,power)), 1<<max(0,-power))


TOLERANCE_BITS = 0x3ddb7cdfd9d7bdbb
TOLERANCE = binary64_value(TOLERANCE_BITS)
MATHEMATICAL_TOLERANCE = Fraction(1,10**10)


def _round_integer(n,d):
    k,r = divmod(n,d)
    return k+int(2*r>d or (2*r==d and k%2==1))


def round_binary64(q, *, limits=DEFAULT_LIMITS):
    """Correct round-to-nearest, ties-to-even finite binary64, by integer math.

    Nonfinite overflow is rejected. Exact zero returns +0; sign of a negative
    underflow is preserved. Zero signs do not affect the frozen comparisons.
    """
    work = _Work(limits)
    q = work.check(_q(q))
    sign = (1<<63) if q < 0 else 0
    q = abs(q)
    if q == 0:
        return 0
    n,d = q.numerator,q.denominator
    e = n.bit_length()-d.bit_length()
    if max(n.bit_length()+max(-e,0),d.bit_length()+max(e,0)) > limits.max_work_bits:
        raise ResourceLimit('binary64 exponent alignment work-bit cap exceeded')
    if (n < (d<<e)) if e>=0 else ((n<<(-e)) < d):
        e -= 1
    if e > 1023:
        raise ContractError('binary64 overflow')
    shift = 1074 if e < -1022 else 52-e
    if max(n.bit_length()+max(shift,0),d.bit_length()+max(-shift,0)) > limits.max_work_bits:
        raise ResourceLimit('binary64 rounding shift cap exceeded')
    mantissa = _round_integer(n<<max(0,shift),d<<max(0,-shift))
    if e < -1022:
        return sign | mantissa
    if mantissa == 1<<53:
        mantissa >>= 1
        e += 1
    if e > 1023:
        raise ContractError('rounded binary64 overflow')
    return sign | ((e+1023)<<52) | (mantissa-(1<<52))


def audit_frozen_binary64(local_bits, other_bits, *, comparison='PRIMARY', limits=DEFAULT_LIMITS):
    """Audit only scalar expressions; never execute frozen SVD/comparator.

    Input bits must come from separately authenticated archived scalar outputs
    for an actual replay claim. This pure arithmetic helper does not admit them.
    """
    if not isinstance(local_bits,(tuple,list)) or not isinstance(other_bits,(tuple,list)) or len(local_bits)!=2 or len(other_bits)!=2:
        raise ContractError('exactly two K,Dmax scalar bit patterns required')
    if comparison not in ('PRIMARY','SECONDARY'):
        raise ContractError('explicit PRIMARY or SECONDARY source expression required')
    local = [binary64_value(b) for b in local_bits]
    other = [binary64_value(b) for b in other_bits]
    if any(v<0 for v in local+other):
        raise ContractError('norm-error scalars must be nonnegative')
    work = _Work(limits)
    added = [round_binary64(work.binary(b,TOLERANCE,'+'),limits=limits) for b in other]
    subtracted = [round_binary64(work.binary(b,a,'-'),limits=limits) for a,b in zip(local,other)]
    other_minus_tol = [round_binary64(work.binary(b,TOLERANCE,'-'),limits=limits) for b in other]
    weak = [a<=binary64_value(b) for a,b in zip(local,added)]
    strict = ([binary64_value(b)>TOLERANCE for b in subtracted] if comparison=='PRIMARY'
              else [a<binary64_value(b) for a,b in zip(local,other_minus_tol)])
    gaps = [b-a for a,b in zip(local,other)]
    frozen = all(weak) and any(strict)
    real = all(g>=-TOLERANCE for g in gaps) and any(g>TOLERANCE for g in gaps)
    return {'comparison':comparison,'frozen_binary64_supported':frozen, 'exact_gap_supported':real,
            'rounding_changes_result':frozen!=real,'weak_predicates':weak,'strict_predicates':strict,
            'other_plus_tol_bits':[f'{b:016x}' for b in added],
            'other_minus_local_bits':[f'{b:016x}' for b in subtracted],
            'other_minus_tol_bits':[f'{b:016x}' for b in other_minus_tol],
            'tolerance_bits':f'{TOLERANCE_BITS:016x}',
            'rounding_mode':'ROUND_TO_NEAREST_TIES_TO_EVEN',
            'input_provenance_admitted':False}


def pareto_sufficient(gaps, epsilons, *, tolerance=TOLERANCE, limits=DEFAULT_LIMITS):
    """Real sufficient condition, separated from the archived machine trace.

    No scientific/continuous-target certificate is emitted by this arithmetic
    helper. Missing target/epsilon/identity admission must be checked by caller.
    """
    if not isinstance(gaps,(tuple,list)) or not isinstance(epsilons,(tuple,list)) or len(gaps)!=2 or len(epsilons)!=2:
        raise ContractError('exactly two K,Dmax metric intervals and bounds required')
    tolerance = _nonnegative(tolerance)
    if tolerance not in (TOLERANCE,MATHEMATICAL_TOLERANCE):
        raise ContractError('unapproved tolerance; no tolerance relaxation')
    lower = [direct_gap_lower(g,e,limits=limits) for g,e in zip(gaps,epsilons)]
    supported = all(g>=-tolerance for g in lower) and any(g>tolerance for g in lower)
    return {'status':'CERTIFIED_REAL_PARETO_SUFFICIENT_CONDITION' if supported else 'DECISION_BOUND_UNRESOLVED',
            'lower_gaps':[str(q) for q in lower], 'tolerance':str(tolerance),
            'tolerance_semantics':'EXACT_BINARY64_FROZEN_TOKEN' if tolerance==TOLERANCE else 'EXACT_DECIMAL_MATHEMATICAL',
            'weak_nonworsening':[g>=-tolerance for g in lower], 'strict_improvement':[g>tolerance for g in lower],
            'machine_predicate_certified':False,'continuous_target_certificate':False}
