"""REI-L0 standalone exploratory algebra, NOT a promoted repository module.

Clock: proper seconds. Energy: eV per conserved reference H nucleus (Href).
There are no rate fits, ODE solvers, quadratures, implicit heating prescriptions,
abundance floors or projections. Exact int/Fraction operands remain exact.
The five-sector PI map is conditional on the selected immediate-heat closure;
physical nonthermal deposition requires a separate, source-qualified owner.
"""
from __future__ import annotations
from fractions import Fraction
import math
from typing import Iterable, Mapping, Sequence

Number = int | float | Fraction
SECTORS = ('gas_thermal', 'binding', 'uv_radiation',
           'dynamic_escape_radiation', 'source_reservoir')
EV_TO_J = Fraction(1602176634, 10**28)
TOLERANCE = 2e-12

class DomainError(ValueError):
    """An input contradicts the declared mathematical or physical domain."""
class MissingInput(ValueError):
    """Required information is absent, not physically zero."""
class OwnershipError(ValueError):
    """A physical event or energy appears under multiple active owners."""
class NumericalRangeError(ArithmeticError):
    """The declared finite binary64 representation cannot hold a result."""


def _number(value: Number, name: str) -> Number:
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
        raise DomainError(f'{name}: finite real int, float or Fraction required')
    if isinstance(value, float) and not math.isfinite(value):
        raise DomainError(f'{name}: nonfinite operand')
    return value


def _add(*values: Number) -> Number:
    if all(isinstance(v, (int, Fraction)) for v in values):
        return sum(values)
    try:
        result = math.fsum(float(v) for v in values)
    except (OverflowError, ValueError) as exc:
        raise NumericalRangeError('binary64 sum not representable') from exc
    if not math.isfinite(result):
        raise NumericalRangeError('binary64 sum not finite')
    return result


def _poly_sum(constants: Sequence[Number] = (),
              products: Sequence[tuple[Number, Number]] = ()) -> Number:
    """Evaluate a short source polynomial on the represented operands.

    Form products and sums exactly, then round once for a float-containing
    expression. This prevents product rounding from erasing a trace source.
    Exact rational inputs stay exact. This small reference kernel makes no
    throughput claim; it does not repair uncertainty already in the inputs.
    """
    vals = tuple(constants) + tuple(v for pair in products for v in pair)
    exact = sum((Fraction(v) for v in constants), Fraction(0))
    exact += sum((Fraction(a)*Fraction(b) for a,b in products), Fraction(0))
    if not any(isinstance(v, float) for v in vals):
        return exact
    try:
        result = float(exact)
    except OverflowError as exc:
        raise NumericalRangeError('source polynomial outside binary64 range') from exc
    if not math.isfinite(result):
        raise NumericalRangeError('source polynomial not finite')
    return result


def _finite_output(values: Iterable[Number]) -> tuple[Number, ...]:
    out = tuple(values)
    if any(isinstance(v, float) and not math.isfinite(v) for v in out):
        raise NumericalRangeError('binary64 output overflow')
    return out


def _third(value: Number) -> Number:
    return Fraction(value)/3 if isinstance(value, (int, Fraction)) else value/3


def _five(values: Sequence[Number], name: str) -> tuple[Number, ...]:
    if len(values) != 5:
        raise DomainError(name+': exactly five components required')
    return tuple(_number(v, f'{name}[{i}]') for i, v in enumerate(values))


def _validate_moments(chi: Number, m: Sequence[Number], availability: str) -> tuple[Number, ...]:
    if availability == 'missing':
        raise MissingInput('source moments have not been supplied')
    if availability not in ('available', 'structural_zero'):
        raise DomainError('unknown source availability')
    _number(chi, 'chi')
    if chi < 0:
        raise DomainError('nonnegative ionization threshold required')
    a,p,r,k,j = _five(m, 'moments')
    if min(a,p,r,k,j) < 0:
        raise DomainError('selected PI/RR/feed moments must be nonnegative')
    if availability == 'structural_zero' and any(v != 0 for v in m):
        raise DomainError('structural zero contradicts nonzero moments')
    if a == 0 and p != 0:
        raise DomainError('absorbed power without an absorption event')
    if r == 0 and k != 0:
        raise DomainError('captured kinetic power without an RR event')
    if Fraction(p) < Fraction(chi)*Fraction(a):
        raise DomainError('absorbed photon energy below ionization threshold')
    return a,p,r,k,j


def energy_source(chi: Number, moments: Sequence[Number], feed_mode: str = 'finite',
                  availability: str = 'available') -> tuple[Number, ...]:
    """Return five proper-time energy derivatives without mean-energy division.

    In external mode the last sector is inactive and sum(q)=J, not zero.
    Availability labels describe input, not an instruction to manufacture zeros.
    """
    a,p,r,k,j = _validate_moments(chi, moments, availability)
    if feed_mode not in ('finite', 'external'):
        raise DomainError('feed_mode must be finite or external')
    return _finite_output((_poly_sum((p,-k), ((-chi,a),)),
                           _poly_sum((), ((chi,a),(-chi,r))), _poly_sum((j,-p)),
                           _poly_sum((k,), ((chi,r),)),
                           -j if feed_mode == 'finite' else 0))


def source_jvp(chi: Number, moments: Sequence[Number], direction: Sequence[Number],
               dchi: Number = 0, feed_mode: str = 'finite') -> tuple[Number, ...]:
    """Full analytic directional derivative B dm + (dB)m.

    Signed directions are allowed. Callers supply d(P_K)=K dR+R dK,
    including K dR when R=0. A balanced but wrong dm is not detected by
    column conservation alone; independent componentwise checks are required.
    """
    a,p,r,k,j = _validate_moments(chi, moments, 'available')
    da,dp,dr,dk,dj = _five(direction, 'direction')
    _number(dchi, 'dchi')
    if feed_mode not in ('finite', 'external'):
        raise DomainError('unknown feed mode')
    return _finite_output((_poly_sum((dp,-dk), ((-chi,da),(-a,dchi))),
                           _poly_sum((), ((chi,da),(-chi,dr),(a,dchi),(-r,dchi))),
                           _poly_sum((dj,-dp)), _poly_sum((dk,), ((chi,dr),(r,dchi))),
                           -dj if feed_mode == 'finite' else 0))


def scaled_balance(terms: Sequence[Number], external: Number = 0) -> float:
    """Dimensionless |sum(q)-external|/sum(|contributions|), no unit floor.

    Exact operands are summed exactly. Float operands are rescaled before
    summation so a large or trace-valued problem does not lose its norm.
    """
    vals = tuple(_number(v,'balance') for v in terms)+(-_number(external,'external'),)
    if all(isinstance(v,(int,Fraction)) for v in vals):
        denom=sum(abs(v) for v in vals)
        return float(abs(sum(vals))/denom) if denom else 0.0
    scale=max(abs(float(v)) for v in vals)
    if scale == 0:
        return 0.0
    scaled=[float(v)/scale for v in vals]
    return abs(math.fsum(scaled))/math.fsum(abs(v) for v in scaled)


def particle_column(process: str, rr_channel: str | None = None,
                    photon_yield: Number | None = None) -> tuple[Number, ...]:
    """(lower ion, upper ion, free electron, UV photon, emitted photon).

    The explicit yield may be a branch-averaged nonnegative number. Bolometric
    RR energy does not determine cascade photon multiplicity or its spectrum.
    """
    if process == 'PI':
        if rr_channel is not None or photon_yield is not None:
            raise DomainError('RR-only options supplied to PI')
        return -1,1,1,-1,0
    if process != 'RR':
        raise DomainError('only adjacent one-electron PI and RR are supported')
    if rr_channel == 'direct_one_photon':
        if photon_yield is not None and photon_yield != 1:
            raise DomainError('direct one-photon channel has yield one')
        return 1,-1,-1,0,1
    if rr_channel == 'cascade':
        if photon_yield is None:
            raise MissingInput('cascade photon yield is not determined by bolometric energy')
        _number(photon_yield,'photon_yield')
        if photon_yield < 0:
            raise DomainError('negative photon yield')
        return 1,-1,-1,0,photon_yield
    raise MissingInput('declare direct_one_photon or a source-qualified cascade')


def lrs_moments(U: Number, Q: Number, role: str = 'state') -> dict:
    """LRS pressure and signed STF, per Href, with no projection or clipping.

    Cone admission is exact on the represented input. It is a necessary
    angular moment condition, not calibration of a source distribution.
    A sink checks positivity of the distribution being REMOVED. General
    signed net rates have no positive-state cone requirement.
    """
    _number(U,'U');_number(Q,'Q')
    if role not in ('state','gain','sink','net'):
        raise DomainError('unknown moment role')
    if role != 'net':
        eu,eq = (-U,-Q) if role == 'sink' else (U,Q)
        # Fractions certify signs of represented floats without rounded bounds.
        u,q=Fraction(eu),Fraction(eq)
        if u < 0 or q < -u/2 or q > u:
            raise DomainError('LRS positive pressure cone violated')
    u3,q3=_third(U),_third(Q)
    pressure=_finite_output((_add(u3,-q3),_add(u3,-q3),_add(u3,2*q3)))
    stf=_finite_output((-q3,-q3,2*q3))
    norm=math.hypot(*(float(v) for v in stf))
    if not math.isfinite(norm):
        raise NumericalRangeError('STF norm not representable')
    return {'pressure_diag':pressure,'stf_diag':stf,'frobenius':norm,
            'role':role,'projection_applied':False}


def sum_stress(diagonals: Iterable[Sequence[Number]]) -> dict:
    vectors=[tuple(v) for v in diagonals]
    if any(len(v)!=3 for v in vectors):
        raise DomainError('three diagonal components required')
    for v in vectors:
        for x in v: _number(x,'stress')
    total=tuple(_add(*(v[i] for v in vectors)) for i in range(3))
    norm=math.hypot(*(float(x) for x in total))
    if not math.isfinite(norm):
        raise NumericalRangeError('summed stress norm not representable')
    return {'diag':total,'frobenius':norm}


def shear_contraction(shear_rate: Number, Q: Number) -> Number:
    _number(shear_rate,'shear_rate');_number(Q,'Q')
    return _finite_output((2*shear_rate*Q,))[0]


def proper_to_eta(proper_derivative: Sequence[Number], H: Number) -> tuple[Number, ...]:
    _number(H,'H')
    if H <= 0:
        raise DomainError('eta=ln(a) adapter requires H>0')
    vals=tuple(_number(v,'proper_derivative') for v in proper_derivative)
    if isinstance(H,(int,Fraction)) and all(isinstance(v,(int,Fraction)) for v in vals):
        return tuple(Fraction(v)/H for v in vals)
    return _finite_output(v/H for v in vals)


def physical_stress(per_href: Sequence[Number], n_href_m3: Number) -> tuple[Number, ...]:
    """Return SI energy-density/pressure components, in J/m^3 = Pa."""
    _number(n_href_m3,'n_href_m3')
    if n_href_m3 < 0: raise DomainError('negative reference density')
    return _finite_output(_number(v,'per_href')*n_href_m3*EV_TO_J for v in per_href)


def register_owners(entries: Sequence[tuple[str, tuple[str,...]]]) -> dict:
    """One active updater per canonical physical event, regardless of alias."""
    seen={}
    for owner,event in entries:
        if not owner or len(event)!=7 or not all(isinstance(s,str) and s for s in event):
            raise DomainError('owner and seven-part canonical event key required')
        if event in seen:
            raise OwnershipError(f'event already owned by {seen[event]}; duplicate {owner}')
        seen[event]=owner
    return seen


def energy_total(sectors: Mapping[str,Number]) -> Number:
    """Sum ONLY physical sectors supplied by the caller, never the tally L."""
    allowed={'u','i','r','e','s'}
    if set(sectors)-allowed:
        raise OwnershipError('diagnostic or unrecognized owner in physical energy total')
    return _add(*(_number(v,'sector') for v in sectors.values()))


def add_geometry(q: Sequence[Number], *, u: Number,r: Number,e: Number,H: Number,
                 shear_rate: Number,Q_uv: Number,Q_escape: Number,
                 p_source: Number,Q_source: Number) -> tuple[tuple[Number,...],Number]:
    """Instantaneous balances plus independently computed work, no integration.

    Source pressure is mandatory: setting it to zero is a declared model choice.
    Binding is a nonrelativistic internal energy with zero pressure. Nonbaryonic
    massive matter is NOT relabelled as this gas or binding sector.
    """
    q=_five(q,'q')
    for name,value in locals().copy().items():
        if name not in ('q',): _number(value,name)
    if min(u,r,e,H) < 0: raise DomainError('nonnegative selected energies and H required')
    losses=(2*H*u,0,_add(H*r,2*shear_rate*Q_uv),
            _add(H*e,2*shear_rate*Q_escape),
            _add(3*H*p_source,2*shear_rate*Q_source))
    derivative=tuple(_add(a,-b) for a,b in zip(q,losses))
    return _finite_output(derivative),_add(*losses)


def escape_constant_source(*, H: float,source_power: float,time_s: float) -> dict[str,float]:
    """Analytic manufactured constant-H, isotropic escape model, zero IC.

    e'=S-H e; L'=S; W'=H e. No numerical ODE or quadrature is used.
    Computing W=(S/H)(x+expm1(-x)) loses its small-x leading term; use a
    bounded Taylor series for W/L instead. No S/H overflow is introduced.
    """
    for name,value in [('H',H),('S',source_power),('t',time_s)]:
        _number(value,name)
        if value < 0: raise DomainError('nonnegative H, S, t required')
    H,S,t=float(H),float(source_power),float(time_s)
    L=S*t
    if not math.isfinite(L): raise NumericalRangeError('tally overflow')
    if H == 0 or t == 0:
        return {'dynamic':L,'work':0.,'tally':L}
    x=H*t
    if x == 0 or not math.isfinite(x):
        raise NumericalRangeError('Ht underflow or overflow')
    if x < 1e-3:
        term=x/2
        terms=[term]
        for n in range(1,12):
            term *= -x/(n+2)
            terms.append(term)
        work_fraction=math.fsum(terms)
        photon_fraction=1-work_fraction
    else:
        photon_fraction=-math.expm1(-x)/x
        work_fraction=(x+math.expm1(-x))/x
    return {'dynamic':L*photon_fraction,'work':L*work_fraction,'tally':L}
