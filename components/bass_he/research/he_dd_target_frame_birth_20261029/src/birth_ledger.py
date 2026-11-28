"""Exact per-event He4 + gamma -> D + D kinematic birth ledger.

Scope: conditional two-body kinematics only; NO physical event rate, cross-section
normalization, radiation history, or deposited heat is computed. Energy units MeV,
(p*c) units MeV, squared-energy invariants MeV^2. Frozen PR104 masses.
"""
from __future__ import annotations
from decimal import Decimal, localcontext
from fractions import Fraction

M = Fraction('3727.3794118')  # M_alpha c^2, MeV
m = Fraction('1875.61294500')  # m_D c^2, MeV
c = 299_792_458  # m s^-1


def exact(value):
    if isinstance(value, (bool, float)) or not isinstance(value, (int, str, Decimal, Fraction)):
        raise TypeError('exact value required; float/bool rejected')
    return Fraction(value)


def threshold():
    return (4*m*m - M*M)/(2*M)


def event_ledger(incident_photon_MeV):
    """Exact fraction-valued invariants, no angular or rate assumptions."""
    e = exact(incident_photon_MeV)
    if e < threshold():
        raise ValueError('below 2D threshold')
    s = M*M + 2*M*e
    q2 = (s - 4*m*m)/4
    splitting2 = e*e*q2/s
    ksum = M+e-2*m
    kbar = ksum/2
    assert q2 >= 0 and splitting2 >= 0 and kbar >= 0
    return {
        'photon_MeV': e, 's_MeV2': s, 'q2_c2_MeV2': q2,
        'splitting_coefficient_squared_MeV2': splitting2,
        'single_D_pair_mean_kinetic_MeV': kbar,
        'pair_kinetic_MeV': ksum,
        'rest_mass_gain_MeV': 2*m-M,
        'photon_energy_debit_MeV': -e,
        'energy_balance_MeV': (2*m-M)+ksum-e,
        'n_D_per_event': 2, 'n_alpha_per_event': -1, 'n_gamma_per_event': -1,
        'baryon_delta': -4+2*2, 'charge_delta': -2+2,
        'R_event': None, 'kappa': None, 'physical_activation': False,
        'L4': False, 'production': 'HOLD',
        'angular_law_required_for_mean': False,
    }


def moment_packet(incident_photon_MeV, angular_atoms):
    """Finite, dimensionless manufactured angular weights (mu,w).

    Every event contributes BOTH daughters. An arbitrary (not necessarily even)
    weight law can be used to validate the unconditional pair-averaged mean.
    No measured angular law, cross section or deposition model is claimed.
    """
    a = event_ledger(incident_photon_MeV)
    atoms = tuple((exact(mu), exact(weight)) for mu, weight in angular_atoms)
    if not atoms:
        raise ValueError('empty angular distribution')
    if any(not -1 <= mu <= 1 or w < 0 for mu, w in atoms):
        raise ValueError('negative weight or out-of-range cosine')
    wsum = sum((w for _,w in atoms), Fraction(0))
    if wsum <= 0:
        raise ValueError('angular weights must have positive sum')
    avgmu = sum((w*mu for mu,w in atoms), Fraction(0))/wsum
    avgmu2 = sum((w*mu*mu for mu,w in atoms), Fraction(0))/wsum
    delta2 = a['splitting_coefficient_squared_MeV2']
    return {
        'mean_cosine':avgmu,
        'mean_cosine_squared':avgmu2,
        'single_D_pair_mean_kinetic_MeV':a['single_D_pair_mean_kinetic_MeV'],
        'single_D_pair_variance_MeV2':delta2*avgmu2,
        'pair_centered_cross_moment_MeV2':-delta2*avgmu2,
        'labelled_D_plus_variance_MeV2':delta2*(avgmu2-avgmu*avgmu),
        'labelled_D_cross_covariance_MeV2':-delta2*(avgmu2-avgmu*avgmu),
        'pair_kinetic_MeV':a['pair_kinetic_MeV'],
        'R_event':None, 'thermal_deposition_rate':None,
        'physical_activation':False, 'production':'HOLD',
        'input_class':'MANUFACTURED_DIMENSIONLESS_ANGULAR_WEIGHTS',
    }


def photon_target_energy_squared(incident_lab_MeV, beta, mu):
    """E'_gamma^2 in the target rest frame, from normal tetrad frame.

    E' = gamma E (1-beta*mu). This is NOT a photon distribution transform;
    it cannot independently evaluate an event rate. beta = v/c is signed
    relative to the chosen photon/tetrad axis. Exactly rational square.
    """
    E,b,u = map(exact,(incident_lab_MeV,beta,mu))
    if E < 0 or abs(b) >= 1 or abs(u) > 1:
        raise ValueError('invalid photon energy, target beta or angular cosine')
    return E*E*(1-b*u)**2/(1-b*b)


def _dec(z: Fraction, digits: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = digits
        return Decimal(z.numerator)/Decimal(z.denominator)


def daughter_lab_sample(incident_photon_MeV, cm_cosine, digits=85):
    """High precision sample with explicit non-certified decimal rounding.

    Computes both daughter four-vectors in alpha target rest tetrad, z along
    incident photon, opposite transverse momenta. Returns string diagnostics.
    """
    if type(digits) is not int or not 40 <= digits <= 180:
        raise ValueError('digits must be an integer from 40 to 180')
    e = exact(incident_photon_MeV)
    mu = exact(cm_cosine)
    if abs(mu) > 1:
        raise ValueError('cosine outside [-1,1]')
    a = event_ledger(e)
    with localcontext() as ctx:
        ctx.prec = digits
        E, Mm, md, uu = [_dec(z,digits) for z in (e,M,m,mu)]
        sqrt_s = _dec(a['s_MeV2'], digits).sqrt()
        q = _dec(a['q2_c2_MeV2'],digits).sqrt()
        gam = (Mm+E)/sqrt_s
        splitting = E*q*uu/sqrt_s
        Eplus = (Mm+E)/2+splitting
        Eminus = (Mm+E)/2-splitting
        pzplus = E/2 + gam*q*uu
        pzminus= E/2 - gam*q*uu
        pt2 = q*q*(1-uu*uu)
        resplus=Eplus*Eplus-pzplus*pzplus-pt2-md*md
        resminus=Eminus*Eminus-pzminus*pzminus-pt2-md*md
        return {
            'Kplus_MeV':str(Eplus-md),'Kminus_MeV':str(Eminus-md),
            'Ksum_MeV':str(Eplus+Eminus-2*md),
            'E_total_residual_MeV':str(Eplus+Eminus-(Mm+E)),
            'pz_total_residual_MeV':str(pzplus+pzminus-E),
            'mass_shell_plus_residual_MeV2':str(resplus),
            'mass_shell_minus_residual_MeV2':str(resminus),
            'rounding_certified':False,'source_class':'KINEMATIC_ONLY',
            'R_event':None,'thermal_deposition_rate':None,
        }
