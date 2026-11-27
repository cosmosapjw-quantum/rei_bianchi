"""Conditional equal-sharing arithmetic; never admits a physical provider.

Quadratics are nonnegative (mantissa, exponent) pairs. Component sums are
scaled before addition, then squared directly, preserving tiny coherent
remainders even when an unrelated raw component has a huge magnitude.
"""
import math
from decimal import Decimal, InvalidOperation


class ContractError(ValueError):
    pass


def _real(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise ContractError('finite real number required')
    try:
        y = float(x)
    except (ValueError, OverflowError) as exc:
        raise ContractError('finite binary64 input required') from exc
    if not math.isfinite(y):
        raise ContractError('nonfinite input')
    return y


def _nonnegative(x):
    x = _real(x)
    if x < 0:
        raise ContractError('negative density or radius')
    return x


def _complex(z):
    if isinstance(z, complex):
        return (_real(z.real), _real(z.imag))
    if isinstance(z, (list, tuple)) and len(z) == 2:
        return (_real(z[0]), _real(z[1]))
    raise ContractError('complex value must be complex or [real, imaginary]')


def _spin(spin):
    if type(spin) is not int or spin not in (0, 1):
        raise ContractError('spin must be integer 0 or 1')
    return 1 if spin == 0 else -1


def _sum(values):
    """Signed linear sum of scaled mantissa/exponent pairs."""
    values = [(m, e) for m, e in values if m]
    if not values:
        return (0.0, 0)
    exponent = max(e for _, e in values)
    m = math.fsum(math.ldexp(m, e-exponent) for m, e in values)
    if not m:
        return (0.0, 0)
    m, shift = math.frexp(m)
    return (m, exponent+shift)


def _norm2(components):
    components = [(m, e) for m, e in components if m]
    if not components:
        return (0.0, 0)
    exponent = max(e for _, e in components)
    q = math.fsum(math.ldexp(m, e-exponent)**2 for m, e in components)
    m, shift = math.frexp(q)
    return (m, 2*exponent+shift)


def _sqrt(q):
    m, e = q
    if e % 2:
        m *= 2
        e -= 1
    sm, shift = math.frexp(math.sqrt(m))
    return (sm, e//2+shift)


def _times(q, weight):
    m, e = q
    wm, shift = math.frexp(m*weight)
    return (wm, e+shift) if wm else (0.0, 0)


def _packed(q):
    m, e = q
    if m < 0:
        raise ContractError('negative quadratic')
    try:
        value = math.ldexp(m, e)
    except OverflowError:
        value = None
    if value is None or not math.isfinite(value):
        status, value = 'OVERFLOW', None
    elif m and value == 0:
        status, value = 'UNDERFLOW', None
    elif m == 0:
        status = 'ZERO'
    else:
        status = 'REPRESENTABLE'
    return {'mantissa': m, 'exponent': e, 'float': value, 'status': status}


def _unpack(q):
    return (q['mantissa'], q['exponent'])


def raw_pair_diagnostics(a, b, spin):
    sign = _spin(spin)
    ar, ai = _complex(a)
    br, bi = _complex(b)
    # frexp gives a common power-of-two scale without squaring raw magnitudes.
    p = [math.frexp(x) for x in (ar, ai, br, bi)]
    u = _norm2(p)
    c = _norm2([_sum([p[0], _times(p[2], sign)]),
                 _sum([p[1], _times(p[3], sign)])])
    d = _norm2([_sum([p[0], _times(p[2], -sign)]),
                 _sum([p[1], _times(p[3], -sign)])])
    eta = None if not u[0] else math.ldexp(d[0]/(2*u[0]), d[1]-u[1])
    return {'U': _packed(u), 'C': _packed(c), 'D': _packed(d),
            'eta': eta, 'spin': spin, 'physical_provider_admitted': False}


def phase_intensity_interval(A, B):
    A, B = _nonnegative(A), _nonnegative(B)
    sa, sb = math.sqrt(A), math.sqrt(B)
    total = sa+sb
    # Rationalized difference avoids cancellation in nearby square roots.
    difference = abs(A-B)/total if total else 0.0
    return {'lower': _packed(_norm2([math.frexp(difference)])),
            'upper': _packed(_norm2([math.frexp(total)])),
            'kind': 'EXACT_FREE_RELATIVE_PHASE_RANGE', 'C': None,
            'physical_provider_admitted': False}


def coherent_disk_interval(a, b, spin, error_a, error_b):
    diagnostic = raw_pair_diagnostics(a, b, spin)
    radius = _sum([math.frexp(_nonnegative(error_a)),
                   math.frexp(_nonnegative(error_b))])
    center = _sqrt(_unpack(diagnostic['C']))
    lower = _sum([center, _times(radius, -1)])
    if lower[0] < 0:
        lower = (0.0, 0)
    upper = _sum([center, radius])
    return {'lower': _packed(_norm2([lower])), 'upper': _packed(_norm2([upper])),
            'kind': 'DETERMINISTIC_COMPLEX_DISC_ENCLOSURE',
            'sharp_if_errors_fill_independent_discs': True,
            'physical_provider_admitted': False}


def _text(record, key):
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ContractError(key+' must be a nonempty identifier')
    return value


def _energy(record):
    energy = record.get('outgoing_energies')
    if not isinstance(energy, dict) or energy.get('kind') != 'point_exact':
        raise ContractError('exact equal-energy point metadata required')
    unit = _text(energy, 'unit')
    values = energy.get('values')
    if not isinstance(values, list) or len(values) != 2 or any(not isinstance(x, str) for x in values):
        raise ContractError('two exact decimal energy strings required')
    try:
        a, b = [Decimal(x) for x in values]
    except InvalidOperation as exc:
        raise ContractError('invalid exact energy') from exc
    if not (a.is_finite() and b.is_finite()) or a < 0 or b < 0 or a != b:
        raise ContractError('equal finite nonnegative outgoing energies required; no near-sharing tolerance')
    digits = ''.join(str(d) for d in a.as_tuple().digits)
    exponent = a.as_tuple().exponent
    if not a:
        canonical = '0'
    else:
        while digits.endswith('0'):
            digits, exponent = digits[:-1], exponent+1
        canonical = digits+'e'+str(exponent)
    return {'value': canonical, 'unit': unit, 'kind': 'point_exact'}


def admit_equal_sharing_record(record):
    if not isinstance(record, dict):
        raise ContractError('record must be an object')
    if record.get('source_profile') != 'CCC_RAW_EQUAL_SHARING':
        raise ContractError('unsupported source profile')
    spin = record.get('spin')
    _spin(spin)
    source_id = _text(record, 'source_id')
    identity = {key: _text(record, key) for key in ('producer_family', 'kinematics_id', 'preparation_id')}
    units, measure = _text(record, 'density_unit'), _text(record, 'differential_measure')
    energy = _energy(record)
    weighted = record.get('spin_weight_applied')
    if type(weighted) is not bool:
        raise ContractError('explicit spin_weight_applied boolean required')
    tag = record.get('representation')
    result = {'representation': tag, 'source_id': source_id, 'spin': spin,
              'density_unit': units, 'differential_measure': measure,
              'outgoing_energy': energy, 'spin_weight_applied': weighted, **identity,
              'physical_provider_admitted': False, 'status': 'CONDITIONAL_ARITHMETIC_ONLY'}
    if tag == 'raw_amplitudes':
        phase = record.get('phase_provenance')
        if weighted:
            raise ContractError('raw amplitudes must be unweighted')
        if not isinstance(phase, dict) or phase.get('source_id') != source_id or phase.get('relative_phase_preserved') is not True:
            raise ContractError('same-source common relative-phase provenance required')
        _text(phase, 'common_convention')
        diag = raw_pair_diagnostics(record.get('a'), record.get('b'), spin)
        result.update({k: diag[k] for k in ('U', 'C', 'D', 'eta')})
        result['interval'] = {'lower': diag['C'], 'upper': diag['C']}
    elif tag == 'coherent_density':
        density = _packed(math.frexp(_nonnegative(record.get('density'))))
        result.update(C=density, U=None, D=None, eta=None,
                      interval={'lower': density, 'upper': density})
    elif tag == 'incoherent_intensities':
        if weighted:
            raise ContractError('intensity pair must be unweighted')
        interval = phase_intensity_interval(record.get('A'), record.get('B'))
        result.update(C=None, U=None, D=None, eta=None,
                      interval={k: interval[k] for k in ('lower', 'upper')})
    else:
        raise ContractError('unknown representation')
    return result


def spin_average(records):
    if not isinstance(records, (list, tuple)) or len(records) != 2:
        raise ContractError('exactly one singlet and one triplet required')
    channels = [admit_equal_sharing_record(r) for r in records]
    if {c['spin'] for c in channels} != {0, 1}:
        raise ContractError('duplicate/missing spin channel')
    for key in ('source_id', 'producer_family', 'kinematics_id', 'preparation_id', 'density_unit', 'differential_measure', 'outgoing_energy'):
        if channels[0][key] != channels[1][key]:
            raise ContractError('spin channels disagree on '+key)
    def weight(c):
        return 1.0 if c['spin_weight_applied'] else (0.25 if c['spin'] == 0 else 0.75)
    def combine(key):
        return _packed(_sum([_times(_unpack(c['interval'][key]), weight(c)) for c in channels]))
    interval = {key: combine(key) for key in ('lower', 'upper')}
    result = {key: channels[0][key] for key in ('source_id', 'producer_family', 'kinematics_id', 'preparation_id', 'density_unit', 'differential_measure', 'outgoing_energy')}
    result.update(interval=interval, C=interval['lower'] if all(c['C'] is not None for c in channels) else None,
                  physical_provider_admitted=False, status='CONDITIONAL_ARITHMETIC_ONLY',
                  weighting='unpolarized spin weights applied exactly once')
    if all(c['U'] is not None for c in channels):
        for key in ('U', 'D'):
            result[key] = _packed(_sum([_times(_unpack(c[key]), weight(c)) for c in channels]))
    return result
