"""Universal moment bounds for finite-mass 4He(gamma,dd) pressure trace.

Exact even angular moment m2=E[mu^2] does not fix the laboratory
second momentum flux. Output is conditional on the frozen 330 MeV
He4-target rest-frame, two-body exclusive event and nonnegative
angular law. It is NOT a measured pressure-rate or a thermalization law.
"""
from fractions import Fraction as F
from nonthermal_d_birth import HE4_REST_MEV, D_REST_MEV, GAMMA_MEV, MEV_TO_J, exact

S_MEV2 = HE4_REST_MEV**2 + 2*HE4_REST_MEV*GAMMA_MEV
E0_MEV = (HE4_REST_MEV + GAMMA_MEV)/2
B2_MEV2 = GAMMA_MEV**2*(S_MEV2/4 - D_REST_MEV**2)/S_MEV2
A2_MEV2 = E0_MEV**2
assert 0 < B2_MEV2 < A2_MEV2


def event_pressure_trace_at_mu2(mu2):
    """Sum_d (p_d*c)^2/E_d, in MeV, no rate or distribution claimed."""
    x=exact(mu2)
    if not 0<=x<=1: raise ValueError('mu2 must be in [0,1]')
    return 2*E0_MEV - 2*D_REST_MEV**2*E0_MEV/(A2_MEV2-B2_MEV2*x)


def moment_trace_bounds(m2):
    """Lower/upper exact bounds for E[event pressure trace] in MeV.

    Only E[mu^2]=m2 and |mu|<=1 are assumed; no fixed-polynomial
    angular-family sharpness is asserted. The universal endpoints are
    exact for nonnegative symmetric atomic laws (or limiting smooth laws).
    """
    m=exact(m2)
    if not 0<=m<=1: raise ValueError('second angular moment outside [0,1]')
    # f(x)=1/(E0^2-B2*x) strictly convex on [0,1].
    f_secant=(1-m)/A2_MEV2+m/(A2_MEV2-B2_MEV2)
    f_jensen=1/(A2_MEV2-B2_MEV2*m)
    lower=2*E0_MEV-2*D_REST_MEV**2*E0_MEV*f_secant
    upper=2*E0_MEV-2*D_REST_MEV**2*E0_MEV*f_jensen
    gap=2*D_REST_MEV**2*E0_MEV*B2_MEV2**2*m*(1-m)/(A2_MEV2*(A2_MEV2-B2_MEV2)*(A2_MEV2-B2_MEV2*m))
    assert lower<=upper and upper-lower==gap
    return {'lower_MeV_per_event':lower,'upper_MeV_per_event':upper,
            'gap_MeV_per_event':gap,'m2':m,
            'physical_activation':False,'production':'HOLD'}


def manufactured_pressure_trace_source(rate, m2, *, source_class):
    """MeV pressure-trace per-event enclosure times manufactured R only."""
    if source_class!='MANUFACTURED_TEST_ONLY':
        raise ValueError('physical pressure-trace rate unavailable')
    r=exact(rate)
    if r<0: raise ValueError('negative rate')
    b=moment_trace_bounds(m2)
    return {'lower_J_m3s':r*b['lower_MeV_per_event']*MEV_TO_J,
            'upper_J_m3s':r*b['upper_MeV_per_event']*MEV_TO_J,
            'physical_activation':False}
