"""Instantaneous scalar ledger conditional on supplied moments; no transport closure."""
import math
import sys
from fractions import Fraction

OWNERS = ('gas', 'binding', 'excitation', 'radiation', 'nonthermal', 'neutrino',
          'nuclear_rest', 'emitter')
ROUND_FACTOR = 64 * sys.float_info.epsilon


def _finite(**values):
    for name, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f'{name} must be finite')


def allocation(*, external_power=0, **sources):
    """Unique named owners; external power is accounted for separately."""
    if set(sources) - set(OWNERS):
        raise ValueError('unknown owner')
    _finite(external_power=external_power, **sources)
    return {**dict.fromkeys(OWNERS, 0), **sources, 'external_power': external_power}


def exchange_residual(record):
    if set(record) - set(OWNERS) - {'external_power'}:
        raise ValueError('unknown owner')
    _finite(**record)
    return sum(record.get(owner, 0) for owner in OWNERS) - record.get('external_power', 0)


def particle_sources(stoichiometric_sources, cumulative_thresholds, charges):
    """For fully thermalized atomic populations only (not nuclear/fast pools)."""
    sources, thresholds, qs = map(list, (stoichiometric_sources, cumulative_thresholds, charges))
    if not len(sources) == len(thresholds) == len(qs):
        raise ValueError('population lengths differ')
    for source, threshold, charge in zip(sources, thresholds, qs):
        _finite(source=source, threshold=threshold, charge=charge)
    return dict(S_heavy=sum(sources), S_e=sum(q*s for q, s in zip(qs, sources)),
                Q_B=sum(i*s for i, s in zip(thresholds, sources)))


def gas_rhs(n_part, T, H, S_heavy, S_e, Q_kin, k_B):
    _finite(n_part=n_part, T=T, H=H, S_heavy=S_heavy, S_e=S_e, Q_kin=Q_kin, k_B=k_B)
    if n_part <= 0 or T < 0 or k_B <= 0:
        raise ValueError('require n_part>0, T>=0, k_B>0')
    source = S_heavy + S_e
    U = 3*k_B*n_part*T/2
    return dict(U=U, P=k_B*n_part*T, S_part=source,
                dot_n=source-3*H*n_part, dot_U=Q_kin-5*H*U,
                dot_T=-2*H*T-T*source/n_part+2*Q_kin/(3*k_B*n_part))


def photo_event(R, A, chi, thermal_fraction=1):
    _finite(R=R, A=A, chi=chi, thermal_fraction=thermal_fraction)
    if min(R, A, chi) < 0 or not 0 <= thermal_fraction <= 1:
        raise ValueError('invalid rate, energy, threshold or thermal fraction')
    if R == 0 and A != 0:
        raise ValueError('zero photo rate requires zero absorbed moment')
    threshold = chi*R
    excess = A-threshold
    # Integers/Fractions have exact threshold semantics. Other numeric inputs
    # allow only 64 eps * max(|A|, |chi R|), with no dimensionless floor.
    exact = all(isinstance(x, (int, Fraction)) for x in (R, A, chi))
    allowance = 0 if exact else ROUND_FACTOR*max(abs(A), abs(threshold))
    if excess < -allowance:
        raise ValueError('materially subthreshold absorbed energy')
    if excess < 0:
        excess = 0
    return allocation(gas=thermal_fraction*excess, binding=threshold, radiation=-A,
                      nonthermal=(1-thermal_fraction)*excess)


def rr_event(R, C, chi):
    """Bolometric complete prompt cascade; no spectrum or photon count implied."""
    _finite(R=R, C=C, chi=chi)
    if min(R, C, chi) < 0:
        raise ValueError('negative rate, kinetic energy or threshold')
    if R == 0 and C != 0:
        raise ValueError('zero capture rate requires zero kinetic moment')
    return allocation(gas=-C, binding=-chi*R, radiation=C+chi*R)


def band_rhs(N, U, p_radiation, H, s, C_N, C_E, F_N, F_E):
    """Evaluate supplied moments, retaining signed interface flux and amplitude."""
    _finite(N=N, U=U, p_radiation=p_radiation, H=H, s=s,
            C_N=C_N, C_E=C_E, F_N=F_N, F_E=F_E)
    return dict(dot_N=C_N-3*H*N-F_N,
                dot_U=C_E-4*H*U-6*s*p_radiation-F_E)


def component_work(epsilon, P, p_component, H, s):
    """Separate component work; caller retains matter/radiation ownership."""
    _finite(epsilon=epsilon, P=P, p_component=p_component, H=H, s=s)
    return 3*H*(epsilon+P)+6*s*p_component
