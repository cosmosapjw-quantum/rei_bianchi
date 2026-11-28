"""Source-pinned, *conditional* 4He(gamma,d)d DA/SIG compatibility bridge.

Only mathematical sensitivity analysis. Does not infer a measured 330 MeV SIG,
resolve identical-deuteron counting, or activate a physical event rate.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from decimal import Decimal, localcontext
from hashlib import sha256, sha1
from pathlib import Path

EXFOR_COMMIT = '939a14d7bba1ddce51975cb5e8711ce96b3b0871'
EXFOR_SHA256 = 'b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f'
EXFOR_BLOB = 'c49433293921dbb012d7f1b0387745732a598efa'
PR105_HEAD = '88a85c859744a0930b1cb776b4d9e8fa0794976d'
E0_MEV = F(330)


def rational(x):
    if isinstance(x, (bool, float)) or type(x) not in (int, str, F, Decimal):
        raise TypeError('exact rational/decimal text only; float and bool forbidden')
    return F(x)


def decimal(x):
    if isinstance(x, (bool, float)) or type(x) not in (int, str, F, Decimal):
        raise TypeError('decimal string/Fraction required')
    if type(x) is F:
        return Decimal(x.numerator) / Decimal(x.denominator)
    z = Decimal(str(x))
    if not z.is_finite():
        raise ValueError('nonfinite decimal')
    return z


@dataclass(frozen=True)
class TotalRow:
    energy_mev: F
    sigma_nb: F
    err_stat_nb: F

    @property
    def lo(self):
        return max(F(0), self.sigma_nb - self.err_stat_nb)

    @property
    def hi(self):
        return self.sigma_nb + self.err_stat_nb


def source_rows(path):
    raw = Path(path).read_bytes()
    if sha256(raw).hexdigest() != EXFOR_SHA256:
        raise ValueError('EXFOR source SHA256 mismatch')
    if sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != EXFOR_BLOB:
        raise ValueError('EXFOR source Git blob mismatch')
    text = raw.decode('ascii')
    if '(2-HE-4(G,D)1-H-2,,SIG)' not in text or 'ERR-ANALYS (ERR-S)' not in text:
        raise ValueError('wrong source or ERR-S semantics')
    sec = text.split('SUBENT        M0475003', 1)[1].split('ENDSUBENT', 1)[0]
    if 'EN         DATA       ERR-S\nMEV        NB         NB' not in sec:
        raise ValueError('wrong source units')
    block = sec.split('MEV        NB         NB\n', 1)[1].split('ENDDATA', 1)[0]
    rows = []
    for line in block.splitlines():
        fields = line.split()
        if not fields:
            continue
        if len(fields) != 3:
            raise ValueError('SIG row width')
        e, v, d = (rational(s) for s in fields)
        if e < 0 or v < 0 or d < 0:
            raise ValueError('negative source field')
        rows.append(TotalRow(e, v, d))
    if len(rows) != 6 or len({r.energy_mev for r in rows}) != 6:
        raise ValueError('unexpected SIG rows')
    if any(r.energy_mev == E0_MEV for r in rows):
        raise ValueError('source unexpectedly contains 330 MeV SIG')
    return tuple(sorted(rows, key=lambda r: r.energy_mev))


def min_energy_L(rows):
    """Exact smallest global K [nb/MeV] allowing all coordinate intervals."""
    if not rows or len({r.energy_mev for r in rows}) != len(rows):
        raise ValueError("nonempty unique-energy source rows required")
    return max([F(0)] + [max(F(0), a.lo - b.hi) / abs(a.energy_mev - b.energy_mev)
            for a in rows for b in rows if a.energy_mev != b.energy_mev])


def energy_interval(rows, K, E=E0_MEV):
    K = rational(K)
    E = rational(E)
    if K < min_energy_L(rows):
        raise ValueError('K below six-row feasibility threshold')
    lo = max([F(0)] + [r.lo - K * abs(E - r.energy_mev) for r in rows])
    hi = min(r.hi + K * abs(E - r.energy_mev) for r in rows)
    if lo > hi:
        raise ArithmeticError('source intervals inconsistent')
    return lo, hi


def _dec_fraction(x):
    return Decimal(x.numerator) / Decimal(x.denominator)


def angular_interval(Ilo, Ihi, kappa, precision=80):
    """Read high-precision *approximate* PR105 I bounds; not certified rounding."""
    if type(precision) is not int or precision < 40 or precision > 200:
        raise ValueError('precision')
    if type(kappa) is not int or kappa not in (1, 2):
        raise ValueError('explicit hypothetical multiplicity kappa=1 or 2')
    with localcontext() as ctx:
        ctx.prec = precision
        a, b = decimal(Ilo), decimal(Ihi)
        if a < 0 or a > b:
            raise ValueError('angular interval')
        return a / kappa, b / kappa


def joint_interval(rows, K, Ilo, Ihi, kappa, precision=80):
    """Sharp conditional support intersection; decimal endpoints are approximations.

    K: assumed total SIG energy Lipschitz bound [nb/MeV].
    Ilo,Ihi: PR105 full-sphere angular integral endpoints [nb].
    kappa: hypothetical I=kappa*sigma_event, NOT EXFOR-confirmed.
    """
    siglo, sighi = energy_interval(rows, K)
    with localcontext() as ctx:
        ctx.prec = precision
        alo, ahi = angular_interval(Ilo, Ihi, kappa, precision)
        lo = max(_dec_fraction(siglo), alo)
        hi = min(_dec_fraction(sighi), ahi)
        return dict(compatible=lo <= hi, sigma330_lower_nb=str(lo) if lo <= hi else None,
                    sigma330_upper_nb=str(hi) if lo <= hi else None,
                    SIG_energy_interval_nb=[str(siglo), str(sighi)],
                    angular_interval_nb=[str(alo), str(ahi)],
                    K_nb_per_MeV=str(rational(K)), kappa=kappa,
                    physical_event_rate=None, source_event_semantics='UNRESOLVED',
                    physical_activation=False, L4=False, production='HOLD',
                    uncertainty='coordinatewise_ERR-S_sensitivity_NOT_joint_CI',
                    numeric_rounding_certified=False)


def critical_energy_L(rows, Ilo, Ihi, kappa, precision=80):
    """Numerical Kcrit from exact theorem; source terms exact, angular decimal approximate."""
    with localcontext() as ctx:
        ctx.prec = precision
        alo, ahi = angular_interval(Ilo, Ihi, kappa, precision)
        k0 = _dec_fraction(min_energy_L(rows))
        constraints = [k0]
        for r in rows:
            d = _dec_fraction(abs(E0_MEV - r.energy_mev))
            constraints.append(max(Decimal(0), _dec_fraction(r.lo) - ahi) / d)
            constraints.append(max(Decimal(0), alo - _dec_fraction(r.hi)) / d)
        return str(max(constraints))


def energy_witness(rows, K, sigma330, E):
    """Pointwise K-Lipschitz constructive witness via midpoint of extremal extensions.
    sigma330 is a *manufactured* feasible event value [nb].
    """
    K, s, E = rational(K), rational(sigma330), rational(E)
    a, b = energy_interval(rows, K)
    if not a <= s <= b:
        raise ValueError('330 witness not in source-compatible interval')
    lower = max([F(0), s - K * abs(E - E0_MEV)] +
                [r.lo - K * abs(E - r.energy_mev) for r in rows])
    upper = min([s + K * abs(E - E0_MEV)] +
                [r.hi + K * abs(E - r.energy_mev) for r in rows])
    if lower > upper:
        raise ArithmeticError('witness infeasible')
    return (lower + upper) / 2
