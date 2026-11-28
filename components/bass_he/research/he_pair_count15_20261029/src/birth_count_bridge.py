"""Exact conditional 4He(gamma,d)d marked-count covariance.

No event normalization, photon bath, named physical pool or thermalization provider
is inferred. Accepts published HE-BIRTH-MOMENT15 rows without rerunning producer.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

A = Q('3727.3794118')     # MeV, frozen predecessor mass convention
M = Q('1875.61294500')   # MeV, deuteron mass
E = Q('330')             # MeV, incident photon in target-rest frame
S = A*A + 2*A*E
B2 = E*E * (S / 4 - M*M) / S
K0 = (A + E) / 2 - M
assert B2 > 0 and K0 > 0 and K0*K0 > B2
EV_TO_J = Q(1602176634, 10**28)  # EXACT: 1 eV = 1.602176634e-19 J
MEV_TO_J = EV_TO_J * 10**6
BIRTH_RESULT_SHA256 = '1fb9f1479863ecffd072a4b7c762de8d5c8e80b18d6571dfb417d42c945e5264'
SOURCE_COMMIT = 'de6bcbd95d25f9686997ad7eadbd62ea4e917d59'


def q(x):
    if type(x) in (bool, float):
        raise ValueError('exact Fraction/text required; binary float disallowed')
    return Q(x)


def frozen_full_witness():
    """Exact v from saved predecessor FULL fixed witness, not a new angular run."""
    return dict(sample='fixed_witness', aperture='FULL',
        daughter_count_per_event=2,
        daughter_mean_MeV=str(K0),
        daughter_variance_MeV2=['62574503954512379344012665/48306809029441085611817']*2,
        daughter_covariance_MeV2=['-62574503954512379344012665/48306809029441085611817']*2,
        pair_kinetic_total_MeV=str(2*K0),
        pair_kinetic_total_variance_MeV2='0')


def read_pinned_birth_result(path):
    path = Path(path)
    blob = path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != BIRTH_RESULT_SHA256:
        raise ValueError('SOURCE_IDENTITY_MISMATCH: original HE-BIRTH-MOMENT15 required')
    original=json.loads(blob)
    if len(original['rows']) != 15 or not original['exact_checks_pass']:
        raise ValueError('FROZEN_15_ROW_SHAPE')
    return original['rows']


def parse_row(row):
    if row.get('daughter_count_per_event') != 2:
        raise ValueError('not a two-daughter event')
    if q(row['daughter_mean_MeV']) != K0 or q(row['pair_kinetic_total_MeV']) != 2*K0:
        raise ValueError('mean/pair energy identity mismatch')
    lo,hi=map(q,row['daughter_variance_MeV2'])
    clo,chi=map(q,row['daughter_covariance_MeV2'])
    if lo < 0 or hi < lo or hi > B2:
        raise ValueError('variance outside exact kinematic range')
    if clo != -hi or chi != -lo or q(row['pair_kinetic_total_variance_MeV2']) != 0:
        raise ValueError('same-event covariance identity mismatch')
    return lo,hi


def conditional_count_moments(var_interval, mean_count, variance_count):
    """E[sum marks]=E[N] mu; Cov(sum marks)=E[N] Sigma+Var[N] mu mu^T.

    Pure mathematical count moments. The pair is *not* necessarily realizable
    by a physical event-count distribution; that is an external source duty.
    """
    lo,hi=map(q,var_interval)
    n=q(mean_count); f=q(variance_count)
    if min(lo,n,f)<0 or hi<lo or hi>B2:
        raise ValueError('invalid variance/count domain')
    if n==0 and f!=0:
        raise ValueError('nonnegative count cannot have variance with mean zero')
    main=f*K0*K0
    diag=(main+n*lo,main+n*hi)
    cross=(main-n*hi,main-n*lo)
    pair_total_variance=4*main
    daughter_diff_variance=(4*n*lo,4*n*hi)
    return dict(mean_daughters=(n*K0,n*K0),mean_pair_kinetic_MeV=2*n*K0,
        diagonal_variance_MeV2=diag,cross_covariance_MeV2=cross,
        pair_total_variance_MeV2=pair_total_variance,
        daughter_difference_variance_MeV2=daughter_diff_variance,
        eigen_sum=2*main,eigen_difference=(2*n*lo,2*n*hi),
        count_fano=None if n==0 else f/n,
        cross_sign_threshold_fano=(lo/(K0*K0),hi/(K0*K0)))


def poisson_from_mean(var_interval, mean_count):
    """Only when the independent iid-mark Poisson-count model is stipulated."""
    return conditional_count_moments(var_interval,mean_count,mean_count)


def no_physical_activation(row):
    """The event rate and pool are not supplied by the predecessor evidence."""
    lo,hi=parse_row(row)
    return {'sample':row.get('sample'),'aperture':row.get('aperture'),
        'per_event_variance_bounds_MeV2':list(map(str,(lo,hi))),
        'per_event_covariance_bounds_MeV2':list(map(str,(-hi,-lo))),
        'kinetic_pair_mean_MeV':str(2*K0),
        'event_rate_m3s':None,'incident_photon_flux':None,
        'named_physical_D_pool':None,'electron_charge_birth_state':None,
        'event_source_multiplicity':'UNQUALIFIED',
        'D_count_source_m3s':None,'D_kinetic_energy_source_J_m3s':None,
        'D_thermal_deposition_J_m3s':None,'Gamma_thermal':None,'Cv':None,
        'independent_binding_RHS':None,'activation':False,'L4':False,
        'physical_completion':None}


def diagnostic_manufactured_event_rate(rate, source_class):
    """Regression-only manufactured scalar, never an admitted physical source."""
    if source_class != 'MANUFACTURED_TEST_ONLY':
        raise ValueError('not an accepted physical event normalization')
    R=q(rate)
    if R < 0:
        raise ValueError('negative event rate')
    return {'manufactured_D_count_m3s':2*R,
            'manufactured_pair_kinetic_J_m3s':R*2*K0*MEV_TO_J,
            'physical_activation':False}
