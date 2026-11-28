"""Exact, frozen-coefficient 1s/2s/2p star and separate event/energy ledgers.

Per initial H I atom, proper seconds, cm^-3 and eV.  The bath is prescribed;
this module does not update temperature, ionization, geometry or photon spectra.
The two eigenvalues replace a time-stepped stiff IVP.  Source and scope are
fixed in CONTRACT.json and the inherited PHYS83 derivation.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Real

import numpy as np
from scipy.special import gammainc

from matched_ce import RatePair, KB_EV_K

GAP_EV = 10.20435
A_2GAMMA = 8.229
A_M1 = 2.496e-6
A_E1 = 626000000.0
A_S = A_2GAMMA + A_M1
RADIATIVE_OWNER = "detached_own_spontaneous"
NE_MAX = 1e18
TIME_MAX_S = 1e3


def _real(value, name, low, high):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise ValueError(name + "_MUST_BE_REAL_NONBOOL_SCALAR")
    ans = float(value)
    if not math.isfinite(ans) or not low <= ans <= high:
        raise ValueError(name + "_OUTSIDE_DECLARED_DOMAIN")
    return ans


def _phi_minus(order, x):
    """phi_order(-x), order 1 or 2, for finite nonnegative x.

    The small-x alternating series has monotonically decreasing terms;
    stopping uses its next-term bound.  No subtraction of t-h at small t.
    """
    if order not in (1, 2) or not math.isfinite(x) or x < 0:
        raise ValueError("INVALID_PHI_ARGUMENT")
    if x <= 0.5:
        term = 1.0 / math.factorial(order)
        terms = [term]
        for n in range(1, 40):
            term *= -x / (n + order)
            terms.append(term)
            if abs(term) <= 1e-18 * abs(math.fsum(terms)):
                return math.fsum(terms)
        raise ArithmeticError("PHI_SERIES_DID_NOT_CONVERGE")
    if order == 1:
        return -math.expm1(-x) / x
    return (1.0 + math.expm1(-x) / x) / x


def _divided_integrals(slow, fast, gap, t):
    """Return h_fast, G_fast, H2, H3 of the inherited exact solution.

    H2 = (h_slow-h_fast)/(fast-slow), H3 = (G_slow-G_fast)/(fast-slow).
    Tiny times use bivariate entire series. Near-coincident positive roots
    use a positive-moment expansion in gap/slow, including the exact limit.
    The direct branch is only used with well-separated roots and arguments.
    """
    if t == 0:
        return 0.0, 0.0, 0.0, 0.0, "zero_time"
    xs, xf = slow*t, fast*t
    hf, gf = t*_phi_minus(1, xf), t*t*_phi_minus(2, xf)
    if xf <= 0.5:
        # h_n(xs,xf) = sum(xs^j xf^(n-j)); no root subtraction.
        homog = power_s = 1.0
        h2_terms, h3_terms = [0.5], [1.0/6.0]
        for n in range(1, 40):
            power_s *= xs
            homog = xf*homog + power_s
            term2 = (-1.0 if n % 2 else 1.0)*homog/math.factorial(n+2)
            term3 = (-1.0 if n % 2 else 1.0)*homog/math.factorial(n+3)
            h2_terms.append(term2); h3_terms.append(term3)
            if max(abs(term2), abs(term3)) <= 1e-18*min(abs(math.fsum(h2_terms)), abs(math.fsum(h3_terms))):
                break
        else:
            raise ArithmeticError("BIVARIATE_SERIES_DID_NOT_CONVERGE")
        return hf, gf, t*t*math.fsum(h2_terms), t*t*t*math.fsum(h3_terms), "small_time_series"
    if slow > 0 and gap/slow <= 0.25:
        rho = gap/slow
        # Integrating u^(n+1)exp(-slow*u) cancels (n+1)! exactly.
        h2_terms, h3_terms = [], []
        rn = 1.0
        for n in range(128):
            p2, p3 = float(gammainc(n+2, xs)), float(gammainc(n+3, xs))
            bracket = xs*p2 - (n+2)*p3
            if bracket < 0:
                raise ArithmeticError("NEGATIVE_INTEGRATED_POSITIVE_MOMENT")
            term2, term3 = rn*p2, rn*bracket
            h2_terms.append(term2); h3_terms.append(term3)
            # Ratios are at most rho; the geometric tail bound is explicit.
            if n >= 1 and max(abs(term2), abs(term3))*rho/(1-rho) <= 1e-18*min(abs(math.fsum(h2_terms)), abs(math.fsum(h3_terms))):
                break
            rn *= -rho
        else:
            raise ArithmeticError("NEAR_ROOT_SERIES_DID_NOT_CONVERGE")
        return hf, gf, math.fsum(h2_terms)/slow**2, math.fsum(h3_terms)/slow**3, "near_root_moments"
    if gap <= 0:
        raise ArithmeticError("ROOT_GAP_NOT_POSITIVE")
    hs, gs = t*_phi_minus(1, xs), t*t*_phi_minus(2, xs)
    return hf, gf, (hs-hf)/gap, (gs-gf)/gap, "separated_roots"


def _spectral_data(a_s, a_p, d_s, d_p):
    """Positive roots and cancellation-free values d_other-lambda_slow."""
    trace = d_s+d_p+a_s+a_p
    disc = math.hypot((d_s+a_s)-(d_p+a_p), 2*math.sqrt(a_s)*math.sqrt(a_p))
    fast = 0.5*(trace+disc)
    det = math.fsum((d_s*d_p, a_s*d_p, a_p*d_s))
    if fast <= 0 or det <= 0:
        raise ArithmeticError("NONPOSITIVE_DECAY_SPECTRUM")
    slow = det/fast
    if d_s <= d_p:
        span, denom = d_p-d_s, fast-d_s
        shift = a_s*span/denom if denom else 0.0
        coef_s, coef_p = span-shift, -shift
    else:
        span, denom = d_s-d_p, fast-d_p
        shift = a_p*span/denom if denom else 0.0
        coef_s, coef_p = -shift, span-shift
    return slow, fast, disc, coef_s, coef_p


@dataclass(frozen=True)
class StepResult:
    time_s: float
    population_ground: float
    population_2s: float
    population_2p: float
    integral_ground_s: float
    integral_2s_s: float
    integral_2p_s: float
    excitation_2s_events: float
    excitation_2p_events: float
    deexcitation_2s_events: float
    deexcitation_2p_events: float
    two_photon_events: float
    M1_events: float
    E1_events: float
    emitted_photons: float
    atomic_excitation_eV: float
    escaped_radiation_eV: float
    thermal_change_eV: float
    heat_withdrawal_eV: float
    raw_event_thermal_change_eV: float
    raw_energy_residual_eV: float
    gross_energy_scale_eV: float
    normalized_raw_energy_residual: float
    event_balance_2s: float
    event_balance_2p: float
    nuclei_residual: float
    numerical_branch: str
    finite_star_only: bool = True
    prescribed_bath: bool = True


@dataclass(frozen=True)
class SteadyResult:
    temperature_K: float
    electron_density_cm3: float
    population_ground: float
    population_2s: float
    population_2p: float
    critical_density_2s_cm3: float
    critical_density_2p_cm3: float
    radiative_events_2s_per_s: float
    radiative_events_2p_per_s: float
    escaped_power_eV_per_s: float
    emitted_photons_per_s: float
    coronal_reference_power_eV_per_s: float
    exact_to_coronal_2s: float
    exact_to_coronal_2p: float
    coronal_relative_overestimate_2s: float
    coronal_relative_overestimate_2p: float
    slow_decay_per_s: float
    fast_decay_per_s: float
    ground_depletion_ratio: float
    finite_star_only: bool = True


@dataclass(frozen=True, init=False)
class FrozenHIStar:
    rate_s: RatePair
    rate_p: RatePair
    electron_density_cm3: float
    a_s: float
    a_p: float
    c_s: float
    c_p: float
    d_s: float
    d_p: float

    def __init__(self, rate_s, rate_p, electron_density_cm3, *,
                 radiative_owner=RADIATIVE_OWNER, native_radiative_owner=False):
        if not isinstance(native_radiative_owner, (bool, np.bool_)):
            raise ValueError("OWNER_FLAG_MUST_BE_BOOL")
        if native_radiative_owner or radiative_owner != RADIATIVE_OWNER:
            raise ValueError("RADIATIVE_OWNER_CONFLICT")
        if not isinstance(rate_s, RatePair) or not isinstance(rate_p, RatePair):
            raise ValueError("PINNED_RATE_PAIRS_REQUIRED")
        if rate_s.upper_level != "2S" or rate_p.upper_level != "2P":
            raise ValueError("RATE_CHANNEL_ORDER")
        if rate_s.temperature_K != rate_p.temperature_K:
            raise ValueError("COMMON_T_REQUIRED")
        ne = _real(electron_density_cm3, "ELECTRON_DENSITY", 0.0, NE_MAX)
        for r, weight in ((rate_s,1.0),(rate_p,3.0)):
            for k in (r.q_up_cm3_s, r.q_down_cm3_s):
                if not math.isfinite(k) or k < 0:
                    raise ValueError("NONNEGATIVE_FINITE_RATES_REQUIRED")
            if r.q_down_cm3_s <= 0:
                raise ValueError("POSITIVE_DOWN_RATE_REQUIRED")
            if abs((r.log_q_up_cm3_s-r.log_q_down_cm3_s) - (math.log(weight)-GAP_EV/(KB_EV_K*r.temperature_K))) > 2e-12:
                raise ValueError("MATCHED_DETAILED_BALANCE_REQUIRED")
        for n,v in (("rate_s",rate_s),("rate_p",rate_p),("electron_density_cm3",ne),
                    ("a_s",ne*rate_s.q_up_cm3_s),("a_p",ne*rate_p.q_up_cm3_s),
                    ("c_s",ne*rate_s.q_down_cm3_s),("c_p",ne*rate_p.q_down_cm3_s),
                    ("d_s",ne*rate_s.q_down_cm3_s+A_S),("d_p",ne*rate_p.q_down_cm3_s+A_E1)):
            object.__setattr__(self,n,v)

    def steady(self):
        rs, rp = self.a_s/self.d_s, self.a_p/self.d_p
        R = rs+rp
        pg = 1.0/(1.0+R); ps,pp = rs*pg,rp*pg
        etas, etap = self.c_s/A_S,self.c_p/A_E1
        ratio_s,ratio_p = 1.0/((1.0+etas)*(1.0+R)),1.0/((1.0+etap)*(1.0+R))
        slow,fast,_,_,_ = _spectral_data(self.a_s,self.a_p,self.d_s,self.d_p)
        return SteadyResult(self.rate_s.temperature_K,self.electron_density_cm3,pg,ps,pp,
            A_S/self.rate_s.q_down_cm3_s,A_E1/self.rate_p.q_down_cm3_s,
            A_S*ps,A_E1*pp,GAP_EV*(A_S*ps+A_E1*pp),
            (2*A_2GAMMA+A_M1)*ps+A_E1*pp,GAP_EV*(self.a_s+self.a_p),
            ratio_s,ratio_p,etas+R+etas*R,etap+R+etap*R,slow,fast,R)

    def step(self, time_s):
        t = _real(time_s,"PROPER_TIME",0.0,TIME_MAX_S)
        slow,fast,gap,coef_s,coef_p = _spectral_data(self.a_s,self.a_p,self.d_s,self.d_p)
        hf,gf,H2,H3,branch = _divided_integrals(slow,fast,gap,t)
        ps = self.a_s*math.fsum((hf,coef_s*H2))
        pp = self.a_p*math.fsum((hf,coef_p*H2))
        js = self.a_s*math.fsum((gf,coef_s*H3))
        jp = self.a_p*math.fsum((gf,coef_p*H3))
        pg, jg = 1.0-ps-pp, t-js-jp
        if not all(math.isfinite(v) for v in (pg,ps,pp,jg,js,jp)):
            raise ArithmeticError("NONFINITE_POPULATION_OR_INTEGRAL")
        if min(pg,ps,pp,jg,js,jp)<0:
            raise ArithmeticError("NEGATIVE_POPULATION_OR_INTEGRAL_NO_CLIPPING")
        up_s,up_p = self.a_s*jg,self.a_p*jg
        down_s,down_p = self.c_s*js,self.c_p*jp
        two,m1,e1 = A_2GAMMA*js,A_M1*js,A_E1*jp
        uatom = GAP_EV*(ps+pp)
        eradiation = GAP_EV*math.fsum((two,m1,e1))
        heat = math.fsum((uatom,eradiation))
        raw = -GAP_EV*math.fsum((up_s,up_p,-down_s,-down_p))
        residual = math.fsum((raw,uatom,eradiation))
        gross = GAP_EV*math.fsum((up_s,up_p,down_s,down_p,two,m1,e1,ps,pp))
        norm = residual/gross if gross else 0.0
        return StepResult(t,pg,ps,pp,jg,js,jp,up_s,up_p,down_s,down_p,two,m1,e1,
            2*two+m1+e1,uatom,eradiation,-heat,heat,raw,residual,gross,norm,
            math.fsum((up_s,-down_s,-two,-m1,-ps)),
            math.fsum((up_p,-down_p,-e1,-pp)),math.fsum((pg,ps,pp))-1.0,branch)

    def coverage(self):
        return {"species":"H I", "levels":["1s","2s","2p"],
            "initial_population":[1.0,0.0,0.0],"temperature_K":self.rate_s.temperature_K,
            "electron_density_cm3":self.electron_density_cm3,"time_domain_s":[0.0,TIME_MAX_S],
            "gap_eV":GAP_EV,"radiative_owner":RADIATIVE_OWNER,
            "optical_boundary":"optically thin immediate escape",
            "thermal_sign":"thermal_change_eV = -heat_withdrawal_eV",
            "two_photon_energy":"pair total gap; no spectrum assigned",
            "source_mixing_and_high_density_completeness":"OPEN",
            "coupled_temperature_charge_geometry":"NOT_IMPLEMENTED",
            "HH_R10":"OFF","production_admission":"NOT_ISSUED"}
