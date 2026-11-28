"""Bounded, source-only 4He + gamma -> D_fast + D_fast ledger.

This module has NO physical cross-section, photon bath, rate, distribution,
thermalization, or IVP. Its manufactured-rate path is an algebraic regression,
not a physical 330 MeV photodisintegration provider. All energies are exact MeV
at the 4He target-rest frame; SI source units are explicit in output names.
"""
from fractions import Fraction as F

# Frozen pair-count15 mass/incident-energy convention, not a fresh mass evaluation.
HE4_REST_MEV = F('3727.3794118')
D_REST_MEV = F('1875.61294500')
GAMMA_MEV = F(330)
C_M_S = F(299792458)
MEV_TO_J = F(1602176634, 10**28) * 10**6
K0_MEV = (HE4_REST_MEV + GAMMA_MEV) / 2 - D_REST_MEV
REQUIRED_FRAME = 'HE4_TARGET_REST'
REQUIRED_CLASS = 'MANUFACTURED_TEST_ONLY'
POOL_ID = 'D_FAST_FROM_HE4_GAMMA_2D_CONDITIONAL'


def exact(x):
    """Preserve decimal/rational provenance; reject rounded float and boolean."""
    if isinstance(x, (float, bool)):
        raise ValueError('fraction/decimal text/integer required, not float/bool')
    return F(x)


def birth_source(rate_m3_s=None, *, source_class=None,
                 frame=REQUIRED_FRAME, photon_direction=None):
    """Source contribution ONLY, not the full cosmological RHS.

    R is manufactured exclusive events/(m^3 s) in proper target-rest time.
    A missing rate returns unresolved sources and never chooses R=0.
    Direction, when present, must be an exact Euclidean unit vector.
    Individual daughter momentum, stress and fast-to-thermal transfer are open.
    """
    base = dict(pool_id=POOL_ID, physical_pool_admitted=False,
                physical_activation=False, production='HOLD', L4=False,
                source_class=source_class, frame=frame,
                source_time='target_proper_time',
                event_rate_m3_s=None, he4_count_m3_s=None,
                fast_D_count_m3_s=None, photon_count_m3_s=None,
                fast_D_kinetic_J_m3_s=None, he4_rest_J_m3_s=None,
                fast_D_rest_J_m3_s=None, photon_J_m3_s=None,
                event_energy_residual_J_m3_s=None,
                fast_D_total_momentum_N_m3=None,
                photon_momentum_N_m3=None,
                event_momentum_residual_N_m3=None,
                daughter_pressure_tensor=None, collision_stopping=None,
                thermal_deposition_J_m3_s=None, Gamma_thermal=None,
                Cv=None, coupled_population_RHS=None)
    if frame != REQUIRED_FRAME:
        raise ValueError('TARGET_REST_FRAME_REQUIRED')
    if rate_m3_s is None:
        if source_class not in (None, 'MISSING'):
            raise ValueError('rate absent but source class supplied')
        return base
    if source_class != REQUIRED_CLASS:
        raise ValueError('no qualified physical exclusive-rate provider is connected')
    r = exact(rate_m3_s)
    if r < 0:
        raise ValueError('negative event rate')
    if photon_direction is None:
        n = None  # Unknown net momentum is not zero momentum.
    else:
        if len(photon_direction) != 3:
            raise ValueError('direction must contain three components')
        n = tuple(exact(x) for x in photon_direction)
        if sum(x*x for x in n) != 1:
            raise ValueError('photon direction must have exact unit norm')

    he_rest = -r * HE4_REST_MEV * MEV_TO_J
    d_rest = 2*r * D_REST_MEV * MEV_TO_J
    fast_kinetic = 2*r * K0_MEV * MEV_TO_J
    photon = -r * GAMMA_MEV * MEV_TO_J
    energy_residual = he_rest + d_rest + fast_kinetic + photon
    assert energy_residual == 0  # Algebraic source invariant.
    base.update(event_rate_m3_s=r, he4_count_m3_s=-r,
                fast_D_count_m3_s=2*r, photon_count_m3_s=-r,
                fast_D_kinetic_J_m3_s=fast_kinetic,
                he4_rest_J_m3_s=he_rest,
                fast_D_rest_J_m3_s=d_rest,
                photon_J_m3_s=photon,
                event_energy_residual_J_m3_s=energy_residual,
                baryon_number_residual_m3_s=4*(-r)+2*(2*r),
                charge_residual_m3_s=2*(-r)+1*(2*r))
    if n is not None:
        p = tuple(r * GAMMA_MEV * MEV_TO_J * x / C_M_S for x in n)
        # N m^-3 = kg m^-2 s^-2 : momentum/(volume*time).
        base.update(fast_D_total_momentum_N_m3=p,
                    photon_momentum_N_m3=tuple(-x for x in p),
                    event_momentum_residual_N_m3=tuple(x-x for x in p))
    return base
