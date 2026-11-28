"""Read-only, source-bound exact endpoint-birth / paired-defect algebra.

This is a **synthetic scalar constant-opacity BE submodel**, not the coupled
HH/He/Bianchi solver. Fractions preserve the frozen binary64 input values.
No scientific runtime dispatch, state mutation, or source-law replacement.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import math
import re

OWNER_SHA = '8322d79609cc535b046b6000dd27bfdfd8859ddbffb5c3adac90ba396d6d2718'
HH_OWNER_SHA = 'f47958a8e185ab02cd7d6c00cb7760be583eb769147ca4ed04ef7b1404e87830'

class ContractRefused(ValueError):
    """An unsupported source, toy state, clock, or gate was requested."""


@dataclass(frozen=True)
class BirthContract:
    start: Q
    middle: Q
    end: Q
    full: tuple[tuple[Q, Q], ...]
    halves: tuple[tuple[Q, Q], ...]
    amount: Q
    effective_source: Q
    original_rate_binary64: Q
    source_digests: tuple[str, str]


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_birth_contract(folder: Path) -> BirthContract:
    """Compare NCP's recorded discrete measures against actual frozen owner bytes.

    Source-rate and injected weights are two distinct binary64 operations.
    effective_source := observed full birth amount / observed dt is ONLY an
    exact algebraic representation of those stored dyadic weights.
    """
    folder = Path(folder)
    source = folder/'PINNED_paired_runtime.rs'
    hh = folder/'PINNED_hh_paired_extension.rs'
    ids = (_digest(source), _digest(hh))
    if ids != (OWNER_SHA, HH_OWNER_SHA):
        raise ContractRefused('OWNER_SOURCE_IDENTITY_MISMATCH')
    t = source.read_text(encoding='utf-8')
    v = hh.read_text(encoding='utf-8')
    matches = re.search(r'const SOURCE: f64 = ([0-9.eE+-]+);',t)
    tokens_base = (
        'let (weights,wb)=source_weights(c,h,t1)?;let source_n=dt*SOURCE;',
        'let (full,a1,l1)=endpoint(c,h,s,dt,&nodes)?;',
        'let (half,a2,l2)=endpoint(c,h,s,dt/2.0,&nodes)?;',
        'let (two,a3,l3)=endpoint(c,h,&half,dt/2.0,&nodes)?;',
    )
    tokens_hh = (
        'let source_n=dt*SOURCE;',
        'hh_endpoint_state(c,s,dt,&nodes)?;',
        'hh_endpoint_state(c,s,dt/2.0,&nodes)?;',
        'hh_endpoint_state(c,&half,dt/2.0,&nodes)?;',
        'source_hh_events:[e1[0],e2[0],e3[0]]',
    )
    if matches is None or any(k not in t for k in tokens_base) or any(k not in v for k in tokens_hh):
        raise ContractRefused('OWNER_ENDPOINT_SOURCE_SEMANTICS_UNBOUND')
    rate=float(matches.group(1))
    if not math.isfinite(rate) or rate<=0:
        raise ContractRefused('OWNER_SOURCE_RATE_DOMAIN')
    data=json.loads((folder/'NCP_ENERGY06_SOURCE_MEASURE.json').read_text(encoding='utf-8'))
    if (data.get('owner_source_sha256'),data.get('HH_owner_source_sha256')) != ids:
        raise ContractRefused('NCP_SOURCE_PIN_MISMATCH')
    scope=data['input_scope']
    t0=Q(scope['t0']);t1=Q(scope['t1']);t2=Q(scope['t2']);dt=Q(scope['dt'])
    if not (dt>0 and t1-t0 == t2-t1 == dt/2 and t2-t0==dt):
        raise ContractRefused('SOURCE_CLOCK_PARTITION_MISMATCH')
    full=tuple((Q(s),Q(m)) for s,m in data['full'])
    halves=tuple((Q(s),Q(m)) for s,m in data['two_half'])
    if not(len(full)==1 and len(halves)==2 and all(m>=0 for _,m in full+halves)):
        raise ContractRefused('SOURCE_BIRTH_SHAPE')
    # Require exact dyadic interpretations of the actual binary64 products,
    # rather than using the input SOURCE constant as an unrounded exact factor.
    bf=Q.from_float(float(dt)*rate)
    bh=Q.from_float(float(dt/2)*rate)
    if full != ((t2,bf),) or halves != ((t1,bh),(t2,bh)) or bf!=2*bh:
        raise ContractRefused('SOURCE_BINARY64_BIRTH_MISMATCH')
    moment=sum(t*m for t,m in halves)-sum(t*m for t,m in full)
    if moment != Q(data['first_time_moment_half_minus_full_exact']):
        raise ContractRefused('RECORDED_MOMENT_MISMATCH')
    if not data['total_mass_equal'] or data['birth_measures_equal']:
        raise ContractRefused('RECORDED_MEASURE_CLASSIFICATION_MISMATCH')
    return BirthContract(t0,t1,t2,full,halves,bf,bf/dt,Q.from_float(rate),ids)


def _toy_valid(p, w, x):
    if not all(isinstance(z,Q) for z in (p,w,x)) or min(p,w,x)<0:
        raise ContractRefused('TOY_DOMAIN_REQUIRE_NONNEGATIVE_FRACTIONS')


def toy_full(p: Q, w: Q, x: Q) -> Q:
    """One BE step for dP/dt=S-kP: add source before implicit absorption."""
    _toy_valid(p,w,x)
    return (p+w)/(1+x)


def toy_halves(p: Q, w: Q, x: Q) -> Q:
    """Two half BE steps with the same constant source law, distinct birth nodes."""
    _toy_valid(p,w,x)
    a=1/(1+x/2)
    return (p+w/2)*a*a+(w/2)*a


def toy_delta_closed(p: Q, w: Q, x: Q) -> Q:
    """Exact (two half) minus full step, for the scalar constant-opacity law.

    Delta = x*(w-x*p) / (4*(1+x)*(1+x/2)**2).
    In particular distinct birth timestamps DO NOT force nonzero Delta.
    """
    _toy_valid(p,w,x)
    return x*(w-x*p)/(4*(1+x)*(1+x/2)**2)


def _tangent_step(p,dp,w,dw,x,dx):
    # M=1+x ; includes derivative of incoming stock and birth weight AND opacity
    y=(p+w)/(1+x)
    dy=(dp+dw-dx*y)/(1+x)
    return y,dy


def toy_full_tangent(p, dp, w, dw, x, dx) -> tuple[Q,Q]:
    _toy_valid(p,w,x)
    return _tangent_step(p,dp,w,dw,x,dx)


def toy_halves_tangent(p, dp, w, dw, x, dx) -> tuple[Q,Q]:
    _toy_valid(p,w,x)
    a,da=_tangent_step(p,dp,w/2,dw/2,x/2,dx/2)
    return _tangent_step(a,da,w/2,dw/2,x/2,dx/2)


def toy_halves_tangent_closed(p, dp, w, dw, x, dx) -> tuple[Q,Q]:
    """Independent differentiation of explicit rational two-half solution."""
    _toy_valid(p,w,x)
    a=1/(1+x/2)
    a_prime=-a*a*dx/2
    y=p*a*a + w*(a+a*a)/2
    dy=dp*a*a + 2*p*a*a_prime + dw*(a+a*a)/2 + w*a_prime*(1+2*a)/2
    return y,dy


def audit_ncp_science_gates(folder: Path) -> dict:
    """Read-only gate classification. It **never** issues authorizations."""
    folder=Path(folder)
    n=json.loads((folder/'NCP_NCP_MASTER_RETURN.json').read_text(encoding='utf-8'))
    two=json.loads((folder/'NCP_TWO_CELL_NEW_SCOPE_PROPOSAL.json').read_text(encoding='utf-8'))
    proposed=json.loads((folder/'NCP_ENERGY06_SUCCESSOR_PROPOSAL.json').read_text(encoding='utf-8'))
    coverage=n['coverage']
    if (coverage['accepted'],coverage['total'],coverage['missing_unbounded'])!=(24,289,265):
        raise ContractRefused('HISTORIC_COVERAGE_UNEXPECTED')
    if n['new_science_dispatch']!=0 or n['epsilon_C'] is not None or n['epsilon_R'] is not None or n['B22']!='OPEN_UNDETERMINED':
        raise ContractRefused('NCP_SCIENCE_CLAIM_CHANGED')
    if two['authorization_record'] is not None or two['scope_consumed'] or two['dispatch_count'] or two['request_ready']:
        raise ContractRefused('INTEGRATION_SCOPE_AUTHORITY_CONFLICT')
    return {
        'coverage_accepted':coverage['accepted'],
        'missing_unbounded':coverage['missing_unbounded'],
        'authorization_missing':True,
        'executable_science_scope':False,
        'owner_full_paired_admitted':False,
        'new_science_dispatch':0,
        'source_law_is_common':True,
        'discrete_birth_measure_need_not_match':True,
        'two_cell_missing_prerequisites':two['prerequisites'],
        'owner_macro_missing_prerequisites':proposed['next_implementation'],
    }
