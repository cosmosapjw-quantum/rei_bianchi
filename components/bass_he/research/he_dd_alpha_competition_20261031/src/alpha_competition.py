"""Source-conditional He-4 photonuclear competition under frozen FLRW conditions.

Inherited PR132 exact Planck Breit-Wheeler rate; free-electron KN scattering and
high-E bare nuclear BH. Adds 2003 Cyburt-Ellis-Fields-Olive fits for He4
(gamma,p)T, He4(gamma,n)He3, He4(gamma,np)D, and optionally He4(gamma,DD).
The inherited Rice2000 150--250MeV wide-bin DD angular-fit SURROGATE is the
baseline; the Cyburt2003 DD function is ONLY an outside-fit-range extrapolation
alternative and is not a replacement high-energy measurement.

Energy-conserving all-order *photon-only* KN regeneration above 150 MeV:
BW/BH pair creation are terminal (no electron-positron secondary photons),
other nuclear reactions terminate into nonthermal nuclei, and photons below
150 MeV exit the modeled window, NOT become heat.  No BASS-native emissivity.
"""
from __future__ import annotations
import sys, math
from pathlib import Path
from functools import lru_cache
import numpy as np
from scipy import constants as c

# Archived self-contained copy and real GitHub branch share this tree layout.
ROOT = Path(__file__).resolve().parents[2]
PREV = ROOT / "he_dd_flrw_firstcollision_20261031" / "src"
if not PREV.is_dir():
    raise RuntimeError("Need pinned PR132 original source tree")
sys.path.insert(0, str(PREV))
from physics_pr131 import state, Q_MEV, ELECTRON_MEV, he_dd_rate_per_photon
from transport import four_channel_rates, sigma_kn

C_CM_S = c.c * 100
RE_CM = c.physical_constants["classical electron radius"][0]*100
E_MIN = 150.
E_MAX = 250.
# Cyburt, Ellis, Fields, Olive PRD 67 (2003) 103521 Appendix A items 6-9.
# A[mb], Q[MeV], exponent of (Q/E), exponent of (1-Q/E)
SOURCES = {
    'pT': (19.5, 19.813852, 3.5, 1.0),
    'nHe3': (17.1, 20.577615, 3.5, 1.0),
    'npD': (21.7, 26.0711, 4.0, 3.0),
    'dd_cyburt_extrap': (10.7, 23.846527, 10.2, 3.4),
}
Q = {'pT':19.813852, 'nHe3':20.577615, 'npD':26.0711, 'dd':Q_MEV}


def sigma_cyburt_cm2(E_MeV: float, key: str) -> float:
    """Published 2003 analytic nuclear fits. HIGH E 150-250 IS EXTRAPOLATION."""
    A, q, power_q, power_k = SOURCES[key]
    if E_MeV<=q:return 0.
    return 1e-27*A * (q/E_MeV)**power_q * (1.-q/E_MeV)**power_k


def sigma_rice_dd_cm2(E_MeV: float) -> float:
    if not (150<=E_MeV<=250):raise ValueError('Rice surrogate only E=150..250')
    return (8.29 if E_MeV < 190 else 4.34)*1e-33


@lru_cache(maxsize=2048)
def rates(E_MeV:float,z:float,dd_mode:str='rice'):
    if not (E_MIN<=E_MeV<E_MAX):raise ValueError('E outside 150<=E<250MeV')
    if dd_mode not in ('rice','cyburt_extrap'):
        raise ValueError('dd_mode rice|cyburt_extrap only')
    inherited=four_channel_rates(float(E_MeV),float(z))
    na = state(z)['n_alpha_cm3']
    result={k:inherited[k] for k in ('bw','kn','bh')}
    result.update({key:na*C_CM_S*sigma_cyburt_cm2(E_MeV,key) for key in ('pT','nHe3','npD')})
    result['dd'] = (inherited['dd'] if dd_mode=='rice' else na*C_CM_S*sigma_cyburt_cm2(E_MeV,'dd_cyburt_extrap'))
    return result


@lru_cache(maxsize=4)
def quadrature(n:int=96):return np.polynomial.legendre.leggauss(n)


def kn_daughter_weights(E, t0, t1, nquad=96):
    """Normalized dP/d[ln(E/E')]; cold-electron differential Klein-Nishina."""
    if t1<=t0:return np.empty(0),np.empty(0)
    u,w=quadrature(nquad)
    t=(t0+t1)*.5 + (t1-t0)*.5*u
    x=E/ELECTRON_MEV
    daughter=E*np.exp(-t)
    q=np.exp(-t)
    cos_th=1.-np.expm1(t)/x
    dsig_dt=np.pi*RE_CM**2 * q*q*(q+1./q-(1.-cos_th*cos_th))*np.exp(t)/x
    return daughter,dsig_dt*(t1-t0)*.5*w/sigma_kn(E)


def solve_cascade(z:float, dd_mode:str='rice',delta_E=2.,nquad=96):
    """Positivity-preserving triangular Volterra solution of KN recycling.

    Results for ONE injected gamma. Not time-resolved, no e+e- cascade,
    no nuclear daughter transport. Source-qualified model prediction only.
    """
    if delta_E<=0 or abs(100/delta_E-round(100/delta_E))>1e-11:
        raise ValueError('delta_E must evenly divide 100MeV')
    grid=np.arange(E_MIN,E_MAX,delta_E,dtype=float)  # inherited Rice source exact E=250 endpoint not supported
    m=len(grid)
    channels=('bw','bh','pT','nHe3','npD','dd','escape')
    ledgers=('E_bw','E_bh','E_pT_K','E_nHe3_K','E_npD_K','E_dd_K',
             'E_pT_Q','E_nHe3_Q','E_npD_Q','E_dd_Q','E_escape','E_KN_e')
    vals={key:np.zeros(m) for key in channels+ledgers}
    max_pdf_error=0.
    for i,E in enumerate(grid):
        r=rates(float(E),float(z),dd_mode)
        total=sum(r.values()); p={k:r[k]/total for k in r}
        t_cut=math.log(E/E_MIN)
        tmax=math.log1p(2*E/ELECTRON_MEV)
        e_hi, w_hi=kn_daughter_weights(E,0.,t_cut,nquad)
        e_lo, w_lo=kn_daughter_weights(E,t_cut,tmax,nquad)
        max_pdf_error=max(max_pdf_error,abs(sum(w_hi)+sum(w_lo)-1.))
        # Piecewise-linear destination interpolation, including one-bin self hit.
        W=np.zeros(i+1)
        for ep,w in zip(e_hi,w_hi):
            lo=min(i-1,max(0,np.searchsorted(grid[:i+1],ep,side='right')-1)) if i else 0
            if lo==i:W[i]+=w
            else:
                f=(ep-grid[lo])/(grid[lo+1]-grid[lo]);W[lo]+=w*(1.-f);W[lo+1]+=w*f
        direct={k:p[k] for k in channels[:-1]}
        direct['escape']=p['kn']*sum(w_lo)
        direct['E_bw']=p['bw']*E
        direct['E_bh']=p['bh']*E
        for key in ('pT','nHe3','npD','dd'):
            direct[f'E_{key}_K']=p[key]*(E-Q[key])
            direct[f'E_{key}_Q']=p[key]*Q[key]
        direct['E_escape']=p['kn']*float(w_lo@e_lo)
        direct['E_KN_e']=p['kn']*(float(w_lo@(E-e_lo))+float(w_hi@(E-e_hi)))
        den=1.-p['kn']*W[i]
        if den <=0:raise ArithmeticError('invalid KN self-scattering denominator')
        for key in vals:
            vals[key][i]=(direct[key]+p['kn']*float(W[:i]@vals[key][:i]))/den
    output=[]
    for i,E in enumerate(grid):
        P=sum(vals[k][i] for k in channels)
        ledger=sum(vals[k][i] for k in ledgers)
        entry={
           'E_inj_MeV':float(E),'z':float(z),'DD_source_mode':dd_mode,
           **{f'P_{k}':float(vals[k][i]) for k in channels},
           'P_alpha_photo_total':float(sum(vals[k][i] for k in ('pT','nHe3','npD','dd'))),
           'N_D_birth_per_gamma':float(2*vals['dd'][i]+vals['npD'][i]),
           'N_T_birth_per_gamma':float(vals['pT'][i]),
           'N_He3_birth_per_gamma':float(vals['nHe3'][i]),
           'N_n_from_alpha_per_gamma':float(vals['nHe3'][i]+vals['npD'][i]),
           'N_p_from_alpha_per_gamma':float(vals['pT'][i]+vals['npD'][i]),
           'K_DD_pair_birth_MeV_per_gamma':float(vals['E_dd_K'][i]),
           'E_nuclear_Q_MeV_per_gamma':float(sum(vals[f'E_{k}_Q'][i] for k in ('pT','nHe3','npD','dd'))),
           'E_alpha_products_K_MeV_per_gamma':float(sum(vals[f'E_{k}_K'][i] for k in ('pT','nHe3','npD','dd'))),
           'E_KN_e_recoil_MeV_per_gamma':float(vals['E_KN_e'][i]),
           'E_BW_pair_channel_MeV_per_gamma':float(vals['E_bw'][i]),
           'E_BH_pair_channel_MeV_per_gamma':float(vals['E_bh'][i]),
           'E_low_gamma_escape_MeV_per_gamma':float(vals['E_escape'][i]),
           'P_total':float(P),'E_ledger_MeV':float(ledger),
           'P_normalization_abs_error':float(abs(P-1)),
           'E_ledger_rel_error':float(abs(ledger-E)/E),
           'KN_pdf_max_normalization_abs_error':float(max_pdf_error),
           'model':'fixed_z_cold_KN_all_orders_bw_bh_terminal_alpha_Cyburt2003_highE_extrap_dd_Rice_or_Cyburt',
           'production_admissible':False,
        }
        output.append(entry)
    return output
