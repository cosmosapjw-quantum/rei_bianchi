"""R9 exact-rational passive current-column to finite-bin reference.

No ODE, upstream module import, network access, or production mutation.
All input decimals are exact rational leaves, not calibrated physical constants.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

Interval = tuple[F, F]
SOURCE_SIGMA_M2 = F('6.6524587051e-29')
BASS_SIGMA_M2 = F('6.6524587e-29')
C_M_S = F(299792458)
V0_M3 = F(1257522545067581081, 1250000000000000000)
BH_EV = F(7659328181264345, 562949953421312)
SOURCE_COMMIT = 'cc3249947a1fc93f2bacf2190604371dfde2f42f'


def interval(value) -> Interval:
    """Parse two exact leaves; reject floats rather than infer their intention."""
    if len(value) != 2 or any(isinstance(x, (float, bool)) for x in value):
        raise TypeError('two exact strings, integers, or Fractions required')
    lo, hi = map(F, value)
    if hi < lo:
        raise ValueError('reversed interval')
    return lo, hi


def nonnegative(value) -> Interval:
    ans = interval(value)
    if ans[0] < 0:
        raise ValueError('nonnegative interval required')
    return ans


def scale(value: Interval, factor: F) -> Interval:
    if not isinstance(factor, F):
        factor = F(factor)
    if factor < 0:
        raise ValueError('positive scaling only')
    return value[0] * factor, value[1] * factor


def product(a: Interval, b: Interval) -> Interval:
    a, b = nonnegative(a), nonnegative(b)
    return a[0] * b[0], a[1] * b[1]


def exp_minus(x: F, digits: int = 100) -> Interval:
    """Enclose exp(-x) by alternating series plus exact range reduction.

    At x/2**m <= 1 the odd/even Taylor sums bracket exp(-x/2**m).
    Positive interval squaring preserves enclosure. Per-square rounding is
    outward to a rational decimal grid, keeping integer sizes bounded.
    This reference supports 0 <= x <= 1024 and 20 <= digits <= 200.
    """
    if not isinstance(x, F):
        raise TypeError('exact Fraction required')
    if not 0 <= x <= 1024 or not 20 <= digits <= 200:
        raise ValueError('outside bounded reference domain')
    if x == 0:
        return F(1), F(1)
    y, squares = x, 0
    while y > 1:
        y /= 2
        squares += 1
    grid = 10 ** (digits + 12)
    tolerance = F(1, grid)
    term = total = F(1)
    lo, hi = F(0), F(1)
    for n in range(1, 2049):
        term *= -y / n
        total += term
        if n % 2:
            lo = total
        else:
            hi = total
        if n >= 2 and hi - lo <= tolerance:
            break
    else:
        raise ArithmeticError('alternating series did not close')
    for _ in range(squares):
        ll, hh = lo * lo * grid, hi * hi * grid
        lo = F(ll.numerator // ll.denominator, grid)
        hi = F(-((-hh.numerator) // hh.denominator), grid)
    return lo, hi


def conditional_probability(depth: Interval) -> Interval:
    """1-exp(-B), conditional on survival from near edge to observer."""
    lo, hi = nonnegative(depth)
    return 1 - exp_minus(lo)[1], 1 - exp_minus(hi)[0]


def bin_probability(depth: Interval, foreground: Interval | None) -> Interval | None:
    """Observer probability with an explicit common near-edge optical tail.

    None stays unknown. It is never silently replaced with zero foreground.
    Correlated boxes yield a valid outer enclosure, not attainable extrema.
    """
    nonnegative(depth)
    if foreground is None:
        return None
    tl, th = nonnegative(foreground)
    return product((exp_minus(th)[0], exp_minus(tl)[1]),
                   conditional_probability(depth))


def positive_probability_excess(baseline: Interval, excess: Interval) -> Interval:
    """exp(-B0)*(1-exp(-deltaB)); same-source positive paired difference."""
    bl, bh = nonnegative(baseline)
    return product((exp_minus(bh)[0], exp_minus(bl)[1]),
                   conditional_probability(nonnegative(excess)))


@dataclass(frozen=True)
class ElectronColumn:
    """Cross-section-free column and one fixed supplier coverage, in m^-2."""
    full_m2_inv: Interval
    baseline_m2_inv: Interval
    ion_excess_m2_inv: Interval
    reference_m2_inv: Interval
    radius_m2_inv: F
    coverage_s: tuple[F, F]
    source_sha256: str
    source_commit: str = SOURCE_COMMIT

    def depth(self, sigma_m2: F, coverage_s=None) -> Interval:
        if not isinstance(sigma_m2, F) or sigma_m2 <= 0:
            raise ValueError('positive exact cross-section in m^2 required')
        if coverage_s is not None and tuple(map(F, coverage_s)) != self.coverage_s:
            raise ValueError('supplier certifies only its complete stored interval')
        return scale(self.full_m2_inv, sigma_m2)


def load_cr53(input_dir: Path, *, expected_certificate_sha256: str,
              expected_contract_sha256: str) -> ElectronColumn:
    """Bind the actual CR53 center and radius together; no static fallback."""
    cp, kp = input_dir / 'CR53_CERTIFICATE.json', input_dir / 'CR53_CONTRACT.json'
    for path, expected in [(cp, expected_certificate_sha256), (kp, expected_contract_sha256)]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('source identity mismatch: ' + path.name)
    j, contract = json.loads(cp.read_text()), json.loads(kp.read_text())
    if j['unit'] != 'NT_GEOMETRY_IONIZATION_RESTORE' or contract['h_s'] != 100000:
        raise ValueError('different source family or horizon')
    if tuple(map(F, contract['geometry_H_s-1'])) != (F('2e-15'), F('4e-15'), F('6e-15')):
        raise ValueError('different source geometry')
    if contract['clock'] != 'proper seconds' or contract['signature'] != '(-,+,+,+)':
        raise ValueError('different clock or metric convention')
    h = F(100000)
    bi = interval(j['B_integral_eV_s'])[1]
    bii = interval(j['B_double_integral_eV_s2'])[1]
    work = interval(j['integrated_total_energy_difference_upper_eV_s'])[1]
    cu = interval(j['residual_polynomial']['adiabatic_heat_lift_defect']['coefficient'])[1]
    if work < F('1.2e-14') * bii + cu * h**3 / 6:
        raise ValueError('work bound assembly failed')
    radius = interval(j['tau_radius_energy_quotient'])[1]
    if radius < C_M_S * SOURCE_SIGMA_M2 * (bi + work) / (2 * V0_M3 * BH_EV):
        raise ValueError('radius is smaller than bound assembly')
    full, ref = interval(j['tau_full_endpoint']), interval(j['tau_reference'])
    if not (full[0] <= ref[0] - radius and full[1] >= ref[1] + radius):
        raise ValueError('center/radius pairing failed')
    base = interval(j['tau_initial_census'])
    inc = interval(j['tau_reference_ion_increment'])
    excess = inc[0] - radius, inc[1] + radius
    if excess[0] <= 0 or not j['branch_closed']:
        raise ValueError('required scoped source evidence missing')
    inv = 1 / SOURCE_SIGMA_M2
    return ElectronColumn(scale(full, inv), scale(base, inv), scale(excess, inv),
                          scale(ref, inv), radius * inv, (F(0), h),
                          expected_certificate_sha256)


def augmented_saltation(reset_jacobian, f_minus, f_plus, reset_time,
                        guard_x, guard_time, ell_minus: F, ell_plus: F):
    """First-order saltation for (state, continuous optical accumulator).

    Input vector fields and ell must use the same clock. The accumulator
    reset is identity and has no singular physical impulse.
    """
    n = len(f_minus)
    if not (len(f_plus) == len(reset_time) == len(guard_x) == n
            and len(reset_jacobian) == n and all(len(row) == n for row in reset_jacobian)):
        raise ValueError('dimension mismatch')
    den = guard_time + sum(guard_x[i] * f_minus[i] for i in range(n))
    if den == 0:
        raise ValueError('transversality required')
    b = [f_plus[i] - sum(reset_jacobian[i][j]*f_minus[j] for j in range(n))
         - reset_time[i] for i in range(n)]
    top = [[reset_jacobian[i][j] + b[i]*guard_x[j]/den for j in range(n)]
           + [F(0)] for i in range(n)]
    return top + [[(ell_plus-ell_minus)*g/den for g in guard_x] + [F(1)]]
