"""Equations (1)-(9), THEORY_KO.md: dimensionless fixed-centre direct CBA.

The generic eta is independent of lambda. matched_overlap accepts Delta directly,
so small-transfer input never comes from adding two nearly opposite vectors.
Outputs describe a labelled direct channel, without exchange or finite-M recoil.
"""
import cmath
import math
import numbers
from scipy.special import loggamma


def _real(value, name):
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise ValueError(name + ' must be a finite real scalar')
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(name + ' must be finite')
    return value


def _vector(values, name):
    if not isinstance(values, (list, tuple)) or len(values) != 3:
        raise ValueError(name + ' must be a real length-three list or tuple')
    return tuple(_real(x, name) for x in values)


def _dot(a, b):
    result = math.fsum(x*y for x, y in zip(a, b))
    if not math.isfinite(result):
        raise ValueError('nonfinite derived dot product')
    return result


def _inputs(lam, qvec, pvec, eta):
    lam, eta = _real(lam, 'lambda'), _real(eta, 'eta')
    qvec, pvec = _vector(qvec, 'qvec'), _vector(pvec, 'pvec')
    p = math.hypot(*pvec)
    if lam <= 0 or p <= 0 or eta < 0:
        raise ValueError('require lambda>0, |pvec|>0, eta>=0')
    A = _dot(qvec, qvec) + lam*lam
    Bc = complex(A + 2*_dot(qvec, pvec), -2*lam*p)
    if not math.isfinite(A) or not math.isfinite(Bc.real) or not math.isfinite(Bc.imag) or Bc.imag >= 0:
        raise ValueError('unrepresentable derived shell/branch input')
    return lam, qvec, pvec, eta, p, A, Bc


def _phase(A, Bc, eta):
    return cmath.exp(1j*eta*(math.log(A)-cmath.log(Bc)))


def nordsieck_i(lam, qvec, pvec, eta):
    """Eq1, the integral WITH 1/r. Principal Log(Bc), Im(Bc)<0."""
    lam, qvec, pvec, eta, p, A, Bc = _inputs(lam, qvec, pvec, eta)
    return 4*math.pi*_phase(A, Bc, eta)/A


def overlap_k(lam, qvec, pvec, eta):
    """Eq2, -dI/dlambda at FIXED eta,pvec,qvec; integral without 1/r."""
    lam, qvec, pvec, eta, p, A, Bc = _inputs(lam, qvec, pvec, eta)
    I = 4*math.pi*_phase(A, Bc, eta)/A
    return 2*I*((1-1j*eta)*lam/A+1j*eta*(lam-1j*p)/Bc)


def matched_overlap(lam, delta, pvec):
    """Eq5 for eta=lambda/p, evaluated from the supplied Delta polynomial."""
    lam = _real(lam, 'lambda')
    delta, pvec = _vector(delta, 'delta'), _vector(pvec, 'pvec')
    p = math.hypot(*pvec)
    if lam <= 0 or p <= 0:
        raise ValueError('require lambda>0, |pvec|>0')
    if delta == (0.0, 0.0, 0.0):
        return 0j
    eta = lam/p
    qvec = tuple(d-v for d, v in zip(delta, pvec))
    A = _dot(qvec, qvec)+lam*lam
    delta2 = _dot(delta, delta)
    Bc = delta2+complex(lam, -p)**2
    if not math.isfinite(A) or not math.isfinite(Bc.real) or not math.isfinite(Bc.imag) or Bc.imag >= 0:
        raise ValueError('unrepresentable derived matched input')
    numerator = delta2-(1+1j*eta)*_dot(delta, pvec)
    return 16*math.pi*lam*_phase(A, Bc, eta)*numerator/(A*A*Bc)


def sommerfeld_strength(eta):
    """Eq8, positive expm1 form; eta0 is its continuous limit."""
    eta = _real(eta, 'eta')
    if eta < 0:
        raise ValueError('require eta>=0')
    if eta == 0:
        return 1.0
    result = 2*math.pi*eta/(-math.expm1(-2*math.pi*eta))
    if not math.isfinite(result):
        raise ValueError('unrepresentable Sommerfeld strength')
    return result


def coulomb_normalizer(eta):
    """Eq7 complex delta-state Nc, with explicitly selected SciPy loggamma."""
    eta = _real(eta, 'eta')
    if eta < 0:
        raise ValueError('require eta>=0')
    exponent = math.pi*eta/2+complex(loggamma(complex(1, -eta)))-1.5*math.log(2*math.pi)
    result = cmath.exp(exponent)
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise ValueError('unrepresentable Coulomb normalization')
    return result


def normalized_form_factor(delta, pvec, lam=1.0, eta=None):
    """Eq7. eta=None selects matched stable Eq5 and exact nuclear zero.

    Explicit eta selects the generic fixed-eta model and retains both terms,
    including the nonzero nuclear subtraction in the eta0 plane-wave control.
    """
    delta, pvec = _vector(delta, 'delta'), _vector(pvec, 'pvec')
    lam = _real(lam, 'lambda')
    if lam <= 0 or math.hypot(*pvec) <= 0:
        raise ValueError('require lambda>0, |pvec|>0')
    if eta is None:
        eta = lam/math.hypot(*pvec)
        difference = matched_overlap(lam, delta, pvec)
    else:
        eta = _real(eta, 'eta')
        qvec = tuple(d-v for d, v in zip(delta, pvec))
        difference = overlap_k(lam, qvec, pvec, eta)-overlap_k(lam, tuple(-v for v in pvec), pvec, eta)
    return coulomb_normalizer(eta)*math.sqrt(lam**3/math.pi)*difference


def _direction(values, name):
    values = _vector(values, name)
    norm = math.hypot(*values)
    # Normalize a declared direction; no physical energy or transfer is clipped.
    if norm <= 0:
        raise ValueError(name + ' must be nonzero')
    return tuple(v/norm for v in values)


def direct_tdcs(incident_energy, ejected_energy, incident_direction,
                scattered_direction, ejected_direction, model='cba'):
    """Eq9 hydrogen lambda1/B=.5; energies E_h, output a0^2/E_h.

    model='cba' selects eta1/p and stable matched K; 'plane' selects eta0
    with nuclear subtraction. Directions are normalized real nonzero vectors.
    """
    Ei, EB = _real(incident_energy, 'Ei'), _real(ejected_energy, 'EB')
    Ef = Ei-0.5-EB
    if Ei <= 0 or EB <= 0 or Ef <= 0:
        raise ValueError('require EB>0 and Ef=Ei-.5-EB>0')
    if model not in ('cba', 'plane'):
        raise ValueError('model must be cba or plane')
    ni = _direction(incident_direction, 'incident_direction')
    nf = _direction(scattered_direction, 'scattered_direction')
    nb = _direction(ejected_direction, 'ejected_direction')
    pi_momentum, pf, p = math.sqrt(2*Ei), math.sqrt(2*Ef), math.sqrt(2*EB)
    delta = tuple(pi_momentum*a-pf*b for a, b in zip(ni, nf))
    delta2 = _dot(delta, delta)
    if delta2 <= 0:
        raise ValueError('zero transfer is outside the TDCS API')
    pvec = tuple(p*a for a in nb)
    F = normalized_form_factor(delta, pvec, eta=None if model == 'cba' else 0.0)
    f = 2*F/delta2
    T_delta = (4*math.pi/delta2)/(2*math.pi)**3*F
    tdcs = pf*p/pi_momentum*abs(f)**2
    return {'model':model, 'Ei':Ei, 'EB':EB, 'Ef':Ef, 'delta':delta,
            'pvec':pvec, 'eta':1/p if model == 'cba' else 0.0,
            'F':F, 'f_direct':f, 'T_delta':T_delta, 'tdcs_au':tdcs,
            'units':'a0^2/E_h', 'count':'labelled direct, spin factor1, exchange absent'}
