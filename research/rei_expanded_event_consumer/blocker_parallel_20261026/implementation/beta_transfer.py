"""Exact constant-source parent transfer in a declared count basis.

Rates are explicit inverse proper seconds; h is proper seconds. This module
does not supply empirical rates, spectra, heat or charge-state qualification.
The returned Jacobian holds source-independent rates and the clock fixed.
"""
import math

STATE = ('n', 'p', 'T', 'He3', 'e_minus', 'antinue')
BETA_STOICHIOMETRY = ((-1,1,0,0,1,1), (0,0,-1,1,1,1))
INVARIANT_ROWS = ((1,1,3,3,0,0), (0,1,1,2,-1,0), (0,0,0,0,1,-1))
OUTPUT_ORDER = ('parent', 'integrated_parent', 'beta_events', 'competing_removals')


def _nonnegative(value, name):
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(name + '_MUST_BE_EXPLICIT_FINITE_NONNEGATIVE') from exc
    if not math.isfinite(value) or value < 0:
        raise ValueError(name + '_MUST_BE_EXPLICIT_FINITE_NONNEGATIVE')
    return value


def beta_transfer(parent, source, beta_rate, competing_rate, h):
    """Return exact P1,I,B,R and d(P1,I,B,R)/d(parent,source).

Counts are per fixed reference or comoving counts. Competing removals are
explicit counters with no unspecified daughter assignment. Continuum beta
daughter, electron and antineutrino counters each receive beta_events.
"""
    parent = _nonnegative(parent, 'PARENT')
    source = _nonnegative(source, 'SOURCE')
    beta_rate = _nonnegative(beta_rate, 'BETA_RATE')
    competing_rate = _nonnegative(competing_rate, 'COMPETING_RATE')
    h = _nonnegative(h, 'DURATION')
    k = beta_rate + competing_rate
    if not math.isfinite(k):
        raise ValueError('NONFINITE_TOTAL_RATE')
    x = k*h
    if not math.isfinite(x):
        raise ValueError('NONFINITE_RATE_DURATION')
    if h == 0:
        E, A, C = 1., 0., 0.
    else:
        E = math.exp(-x)
        if x <= .1:
            term1, term2 = 1., .5
            phi1, phi2 = term1, term2
            for j in range(1,11):
                term1 *= -x/(j+1)
                term2 *= -x/(j+2)
                phi1 += term1
                phi2 += term2
        else:
            m = -math.expm1(-x)
            phi1 = m/x
            phi2 = (1-m/x)/x
        A = h*phi1
        C = h*(h*phi2)
    if not all(math.isfinite(v) and v >= 0 for v in (E,A,C)):
        raise ValueError('NONFINITE_OR_NEGATIVE_TRANSFER_COEFFICIENT')
    integrated = A*parent+C*source
    outputs = (E*parent+A*source, integrated, beta_rate*integrated, competing_rate*integrated)
    jacobian = ((E,A),(A,C),(beta_rate*A,beta_rate*C),(competing_rate*A,competing_rate*C))
    if not all(math.isfinite(v) and v >= 0 for v in outputs):
        raise ValueError('NONFINITE_OR_NEGATIVE_TRANSFER_OUTPUT')
    if not all(math.isfinite(v) and v >= 0 for row in jacobian for v in row):
        raise ValueError('NONFINITE_OR_NEGATIVE_TRANSFER_JACOBIAN')
    return dict(zip(OUTPUT_ORDER,outputs), jacobian_parent_source=jacobian,
                beta_product_increments={'daughter':outputs[2],'continuum_electron':outputs[2],
                                         'antineutrino':outputs[2]},
                thermal_heat=None, empirical_rate_admitted=False,
                basis='fixed_reference_or_comoving_counts_continuum_beta_branch')
