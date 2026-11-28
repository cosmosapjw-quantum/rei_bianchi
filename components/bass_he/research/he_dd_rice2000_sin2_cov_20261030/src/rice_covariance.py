"""Rice-2000 P0+P2 endpoint-constrained DD daughter correlation: CONDITIONAL physics.

No source-owned photon history, per-energy cross section, transport or heat is supplied.
All energies are physical MeV in the stationary bare-alpha target rest frame.
Read notes/THEORY_KO.md before using these results outside this bounded model.
"""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path

M_ALPHA = 3727.3794118  # MeV, bare alpha rest energy, pinned PR126 CODATA2022
M_D = 1875.61294500     # MeV, bare D rest energy, pinned PR126 CODATA2022
Q = 2 * M_D - M_ALPHA
A_P2 = 1.0 / 5.0
BIN_SPECS = ((150.0, 190.0, 8.29, 1.32), (190.0, 250.0, 4.34, 0.69))
TAIL_THRESHOLDS_MEV = (60.0, 80.0, 100.0, 120.0, 140.0)


def delta(e: float) -> float:
    """Exact two-body alpha-rest kinetic splitting coefficient (MeV)."""
    if not (math.isfinite(e) and e > Q):
        raise ValueError('requires finite E_gamma strictly above gamma+alpha -> dd threshold')
    s = M_ALPHA**2 + 2.0 * M_ALPHA * e  # MeV**2
    return e / 2.0 * math.sqrt(1.0 - 4.0 * M_D**2 / s)


def angular_density(mu: float) -> float:
    """Conditional P2-constrained unpolarized per-event cos(theta*) density."""
    if not -1.0 <= mu <= 1.0:
        raise ValueError('mu outside [-1,1]')
    return 0.75 * (1.0 - mu**2)


def daughters(e: float, mu: float) -> tuple[float, float]:
    if not -1.0 <= mu <= 1.0:
        raise ValueError('mu outside [-1,1]')
    half = (e - Q) / 2.0
    gap = delta(e) * mu
    return half + gap, half - gap


def daughter_pdf(e: float, k: float) -> float:
    """Probability density (MeV^-1) for ONE randomly selected daughter."""
    d = delta(e)
    x = (k - (e - Q)/2.0) / d
    if not (-1.0 < x < 1.0):
        return 0.0
    return 0.75 * (1.0 - x*x) / d


def tail_probability(e: float, threshold: float) -> float:
    """P(K_D >= threshold) for one daughter, given monochromatic E (not measured)."""
    d = delta(e)
    x = (threshold - (e-Q)/2.0)/d
    if x <= -1.0:
        return 1.0
    if x >= 1.0:
        return 0.0
    return 0.5 - 0.75*x + 0.25*x*x*x


def monotonic_split_upper(a: float, b: float) -> float:
    """Analytic conservative bound on max Delta'(E) on [a,b], per PR126."""
    if not (Q < a < b):
        raise ValueError('invalid photon bin')
    def s(e:float)->float:return M_ALPHA*M_ALPHA+2*M_ALPHA*e
    def r(e:float)->float:return math.sqrt(1-4*M_D*M_D/s(e))
    return 0.5*(r(b) + 4*M_D*M_D*M_ALPHA*b/(s(a)**2*r(a)))


def covariance_from_discrete(energies: list[float], weights: list[float], a2moment: float=A_P2) -> float:
    """Exact conditional daughter K+ K- covariance for event-weighted E distribution.

    For each E, E[mu|E]=0 and E[mu**2|E]=a2moment, no other E-mu
    correlation. weights are nonnegative normalized event probabilities.
    """
    if len(energies) != len(weights) or not energies:
        raise ValueError('nonempty matching energy/weight lists required')
    if not 0 <= a2moment <= 1 or any((not math.isfinite(w) or w < 0) for w in weights):
        raise ValueError('invalid probabilities or angular second moment')
    tot=math.fsum(weights)
    if tot <= 0:raise ValueError('zero event weight')
    if any(not math.isfinite(e) or e<=Q for e in energies):
        raise ValueError('bad energy')
    w=[x/tot for x in weights]
    mean=math.fsum(e*wi for e,wi in zip(energies,w))
    var=math.fsum(wi*(e-mean)**2 for e,wi in zip(energies,w))
    split=math.fsum(wi*delta(e)**2 for e,wi in zip(energies,w))
    return var/4.0 - a2moment*split


def bound_for_bin(a: float, b: float, a2moment: float=A_P2) -> dict:
    """Sharp maximum of Cov(K+,K-) among all gamma E distributions on [a,b].

    Valid if cos(theta) conditional on each E has mean zero and fixed second
    moment a2moment. Convexity of g(E)=E^2/4 -a2moment*Delta(E)^2
    gives endpoint-mixture extremizer. No measured photon event weights needed.
    """
    if not (Q < a < b and 0 <= a2moment <= 1):
        raise ValueError('bad energy domain or angular second moment')
    d0,d1=delta(a),delta(b)
    c=(b-a)**2/4.0
    v0,v1=(a2moment*d0*d0,a2moment*d1*d1)
    pstar = min(1.,max(0.,0.5*(1.0-(v1-v0)/c)))
    cov_ub=c*pstar*(1.0-pstar) -(1.0-pstar)*v0-pstar*v1
    crit=(b-a)**2/(4.0*(d0+d1)**2)
    return {
        'E_gamma_bin_MeV':[a,b],
        'D_kinetic_mean_endpoint_MeV':[(a-Q)/2,(b-Q)/2],
        'Delta_endpoint_MeV':[d0,d1],
        'conditional_single_D_variance_endpoint_MeV2':[v0,v1],
        'conditional_single_D_rms_endpoint_MeV':[math.sqrt(v0), math.sqrt(v1)],
        'angular_second_moment_P2':a2moment,
        'a_critical_for_forced_negative_pair_covariance':crit,
        'max_covariance_upper_MeV2':cov_ub,
        'sharp_extremizer_probability_at_Emax':pstar,
        'holds_for_all_nonnegative_event_weight_E_distributions': True,
        'covariance_strict_negative_in_this_model':cov_ub<0,
        'monotonic_delta_prime_conservative_upper':monotonic_split_upper(a,b),
    }


def build_results() -> dict:
    bins=[];tails=[]
    for a,b,sig,a0 in BIN_SPECS:
        row=bound_for_bin(a,b)
        row.update({
            'source_bin_fit':'Rice2000 constrained P0+P2 endpoint-zero fit (not point-E sigma)',
            'source_sigma_total_binfit_nb':sig,
            'source_A0_binfit_nb_per_sr':a0,
            'sigma_total_author_fit_consistency_nb':2*math.pi*a0,
            'event_weight_photon_spectrum':None,
            'event_rate':None,'heat_rate':None,
        })
        bins.append(row)
        for t in TAIL_THRESHOLDS_MEV:
            mn,mx=tail_probability(a,t),tail_probability(b,t)
            assert -1e-13 <= mn <= mx + 1e-12 <= 1+1e-12, (a,b,t,mn,mx)
            tails.append({'E_gamma_bin_MeV':[a,b], 'D_kinetic_threshold_MeV':t,
                          'fraction_above_threshold_min':mn,
                          'fraction_above_threshold_max':mx,
                          'number_fast_D_per_event_min':2*mn,
                          'number_fast_D_per_event_max':2*mx})
    return {'schema':'BASS_HE_RICE2000_SIN2_CONDITIONAL_PAIR_CORRELATION_V1',
            'source_experiment_count':1,'source_author_fit_rows_reused':2,
            'source_2000_data_not_new_measurements':True,
            'model':'per-photon-energy P0+P2 endpoint-zero, angular density 3(1-mu²)/4; NOT demonstrated by binned Rice measurements at every E',
            'target_epoch_He_rest_photon_history':None,
            'gamma_angular_covariance':None,
            'reaction_event_rate':None,'heat_rate':None,
            'central_DAG':'28/88','HE_physical_DAG':'14/18','physical_delta':0,
            'units':{'energy':'MeV','covariance':'MeV^2','sigma_total':'nb'},
            'bins':bins,'tails':tails}


def export(root: Path) -> None:
    result=build_results(); dest=root/'results';dest.mkdir(exist_ok=True)
    (dest/'CONDITIONAL_PAIR_CORRELATION.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
    with (dest/'PAIR_COVARIANCE_2BINS.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f,lineterminator="\n");writer.writerow(['Emin_MeV','Emax_MeV','sigma_event_fit_nb','delta_min_MeV','delta_max_MeV','Acrit','max_Cov_MeV2','pstar','monotonic_delta_prime_bound'])
        for z in result['bins']:
            a,b=z['E_gamma_bin_MeV'];writer.writerow([a,b,z['source_sigma_total_binfit_nb'],*z['Delta_endpoint_MeV'],z['a_critical_for_forced_negative_pair_covariance'],z['max_covariance_upper_MeV2'],z['sharp_extremizer_probability_at_Emax'],z['monotonic_delta_prime_conservative_upper']])
    with (dest/'DFAST_TAIL_10.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f,lineterminator="\n");writer.writerow(['Emin_MeV','Emax_MeV','K_threshold_MeV','fraction_min','fraction_max','N_D_above_min_per_event','N_D_above_max_per_event'])
        for z in result['tails']:
            writer.writerow([*z['E_gamma_bin_MeV'],z['D_kinetic_threshold_MeV'],z['fraction_above_threshold_min'],z['fraction_above_threshold_max'],z['number_fast_D_per_event_min'],z['number_fast_D_per_event_max']])


if __name__=='__main__':
    export(Path(__file__).resolve().parents[1])
