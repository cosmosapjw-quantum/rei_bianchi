"""Hostile contract probes against imported repository functions, not copied logic.
No production patch, global monkey patch, cloud job, or geometry-action replay.
Only the first anchor is replaced by an observing sentinel in each probe.
Run with BASS_AUDIT_EVIDENCE=<new-directory> to preserve the attack matrix.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
from decimal import Decimal
from fractions import Fraction

import numpy as np
import pytest

import bass_he.spectral as sp
import bass_he.sturm_geometry as sg
from bass_he.geometry import jsonable, unjsonable

SEED = 1.2125718090356707 + 1.363814370435508j


class AnchorReached(RuntimeError):
    pass


@pytest.fixture(scope='module')
def genuine():
    # A real published constructor supplies membership evidence.
    return sp.find_exceptional_point((1, 0, 0), (2, 1, 0), SEED, depth=64)


@pytest.fixture(scope='module')
def ledger():
    rows = []
    yield rows
    dest = os.environ.get('BASS_AUDIT_EVIDENCE')
    if dest:
        p = Path(dest) / 'ATTACK_MATRIX.json'
        with p.open('x', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.write('\n'); f.flush(); os.fsync(f.fileno())


def inspect_case(ep, monkeypatch, ledger, name):
    before = copy.deepcopy(ep)
    try:
        sp.validate_pair_membership_certificate(ep)
        validator = 'ACCEPTED'
    except Exception as exc:
        validator = type(exc).__name__
    calls = []
    def anchor(*args, **kwargs):
        calls.append(1)
        raise AnchorReached('first real-anchor boundary reached')
    monkeypatch.setattr(sg, 'bound_pair', anchor)
    try:
        sg.contour_geometry(ep, 0.0, panels=8)
        geometry = 'UNEXPECTED_RETURN'
    except AnchorReached:
        geometry = 'ANCHOR_REACHED'
    except Exception as exc:
        geometry = type(exc).__name__
    cert = ep.get('pair_membership', {})
    binding = cert.get('binding')
    try:
        actual_binding_digest = sp._binding_sha256(binding)
    except Exception:
        actual_binding_digest = None
    row = {'case': name, 'validator': validator, 'geometry': geometry,
           'anchor_calls': len(calls),
           'recorded_binding_sha256': cert.get('binding_sha256'),
           'actual_payload_binding_sha256': actual_binding_digest,
           'passed_repr': repr(cert.get('passed')),
           'matching_error_repr': repr(cert.get('max_scaled_matching_error'))}
    ledger.append(row)
    return row


def blocked(row):
    assert row['validator'] == 'ValueError' and row['geometry'] == 'ValueError' and row['anchor_calls'] == 0, row


def allowed(row):
    assert row['validator'] == 'ACCEPTED' and row['geometry'] == 'ANCHOR_REACHED', row


# INTEGER IDENTITY: apply attacks to every label coordinate, not only N.
@pytest.mark.parametrize('field,index,value', [
    ('state_a', 0, 1.5), ('state_a', 0, 1.0), ('state_a', 0, True),
    ('state_a', 0, np.bool_(True)), ('state_a', 0, np.float64(1.0)),
    ('state_a', 1, 0.5), ('state_a', 1, False), ('state_a', 2, 0.5),
    ('state_b', 0, 2.5), ('state_b', 1, 1.5), ('state_b', 2, False),
    ('state_a', 0, '1'), ('state_a', 0, Decimal('1')), ('state_a', 0, Fraction(1,1)),
    ('state_a', 0, complex(1)), ('state_a', 0, np.array(1)),
    ('depth', None, 64.5), ('depth', None, 64.0), ('depth', None, True),
    ('depth', None, np.bool_(True)), ('depth', None, '64'), ('depth', None, np.array(64)),
])
def test_discrete_identity_blocks_before_anchor(genuine,monkeypatch,ledger,field,index,value):
    ep=copy.deepcopy(genuine)
    if index is None: ep[field]=value
    else:
        v=list(ep[field]);v[index]=value;ep[field]=tuple(v)
    blocked(inspect_case(ep,monkeypatch,ledger,f'discrete:{field}[{index}]={repr(value)}'))


@pytest.mark.parametrize('field', ['R','p','lam','Z1','Z2'])
def test_one_ulp_endpoint_change_is_not_rounded_away(genuine,monkeypatch,ledger,field):
    ep=copy.deepcopy(genuine); value=ep[field]
    if np.iscomplexobj(value): ep[field]=complex(np.nextafter(value.real,np.inf),value.imag)
    else: ep[field]=float(np.nextafter(value,np.inf))
    blocked(inspect_case(ep,monkeypatch,ledger,f'one_ulp:{field}'))


@pytest.mark.parametrize('field', ['R','p','lam','Z1','Z2'])
def test_nonfinite_endpoint_blocks(genuine,monkeypatch,ledger,field):
    ep=copy.deepcopy(genuine);ep[field]=float('nan')
    blocked(inspect_case(ep,monkeypatch,ledger,f'nonfinite_endpoint:{field}'))


@pytest.mark.parametrize('field,value', [
    ('tolerance',float('nan')),('probe_scale',float('nan')),
    ('tolerance',1e-5),('probe_scale',2e-4),
    ('binding_sha256','0'*64),('binding_sha256',None),
    ('claim','STALE'),('permutation',[False,True]),('permutation',[0.,1.]),
    ('permutation',[0,0]),('permutation',[0]),('permutation',['0','1']),
    ('permutation',[np.bool_(False),np.bool_(True)]),('permutation',(0,1)),
    ('passed',False),('max_scaled_matching_error',1e-2),
    ('max_scaled_matching_error',float('inf')),
])
def test_known_invalid_certificate_fields_block(genuine,monkeypatch,ledger,field,value):
    ep=copy.deepcopy(genuine);ep['pair_membership'][field]=value
    blocked(inspect_case(ep,monkeypatch,ledger,f'bad_cert:{field}={repr(value)}'))


@pytest.mark.parametrize('value', [float('nan'),float('-inf'),-1.0,'nan'])
def test_matching_error_must_be_finite_nonnegative(genuine,monkeypatch,ledger,value):
    ep=copy.deepcopy(genuine);ep['pair_membership']['max_scaled_matching_error']=value
    blocked(inspect_case(ep,monkeypatch,ledger,f'matching_error:{repr(value)}'))


@pytest.mark.parametrize('value', ['False','0',1])
def test_pass_flag_must_not_use_truthy_nonboolean(genuine,monkeypatch,ledger,value):
    ep=copy.deepcopy(genuine);ep['pair_membership']['passed']=value
    blocked(inspect_case(ep,monkeypatch,ledger,f'passed:{repr(value)}'))


@pytest.mark.parametrize('mode', ['state_bool','state_float','depth_float'])
def test_stored_binding_digest_must_match_actual_payload(genuine,monkeypatch,ledger,mode):
    ep=copy.deepcopy(genuine);c=ep['pair_membership']
    if mode=='state_bool': c['binding']['state_a'][0]=True
    elif mode=='state_float': c['binding']['state_a'][0]=1.0
    else: c['binding']['depth']=64.0
    # No digest recomputation or endpoint alteration. Python equality is insufficient.
    assert sp._binding_sha256(c['binding']) != c['binding_sha256']
    blocked(inspect_case(ep,monkeypatch,ledger,f'binding_payload:{mode}'))


@pytest.mark.parametrize('mode', ['original','numpy_int64','numpy_uint64','json_roundtrip','permutation_reversed'])
def test_intact_semantic_identity_still_reaches_anchor(genuine,monkeypatch,ledger,mode):
    ep=copy.deepcopy(genuine)
    if mode.startswith('numpy_'):
        t=np.int64 if mode=='numpy_int64' else np.uint64
        ep['state_a']=tuple(t(x) for x in ep['state_a'])
        ep['state_b']=tuple(t(x) for x in ep['state_b'])
        ep['depth']=t(ep['depth'])
    elif mode=='json_roundtrip':
        ep=unjsonable(json.loads(json.dumps(jsonable(ep),allow_nan=False)))
    elif mode=='permutation_reversed':
        ep['pair_membership']['permutation']=ep['pair_membership']['permutation'][::-1]
    allowed(inspect_case(ep,monkeypatch,ledger,f'valid_control:{mode}'))
