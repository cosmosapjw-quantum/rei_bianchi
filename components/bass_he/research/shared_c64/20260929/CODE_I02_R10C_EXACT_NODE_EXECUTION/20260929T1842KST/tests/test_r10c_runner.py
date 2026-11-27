import copy
import json
import math
from pathlib import Path
import numpy as np
import pytest
from bass_he.eq54 import BRANCHES, support_cutoffs
from bass_he.geometry import _canonical
from r10c_runner import (validate_query_rows, contour_key, validate_exact_table,
                         fixed_node_integrate, frozen_geometry_map, probability_ratio)

QUERY = Path('/tmp/BASS_HE_R10B_REVIEW_PACKAGE_20260929/BASS_HE_R10B_Q23_NODE_IDENTITY_20260929/PROPOSED_QUERY_CONTRACT.json')
R10A = Path('/tmp/BASS_HE_R10C_R10A_RESTORE/research/shared_c64/20260929/CODE_I02_R10A_RHO_FREEZE_IMPACT/20260929T1535KST/attempt2')


def test_exact_query_set_and_reject_one_ulp():
    contract = json.loads(QUERY.read_text())
    assert validate_query_rows(contract, BRANCHES, support_cutoffs()) == (105, 360)
    altered = copy.deepcopy(contract)
    x = altered['query_rows'][0]
    x['rho_hex'] = np.nextafter(x['rho'], math.inf).hex()
    with pytest.raises(ValueError, match='QUERY_IDENTITY'):
        validate_query_rows(altered, BRANCHES, support_cutoffs())


def test_cache_key_includes_exact_source_environment_branch_rho_depth_panels():
    b = BRANCHES[0]
    a = contour_key(b, 1.0, 'source-A', ('2.3.5', '3.12.3'))
    variants = [contour_key(b, np.nextafter(1.0, math.inf), 'source-A', ('2.3.5', '3.12.3')),
                contour_key(BRANCHES[1], 1.0, 'source-A', ('2.3.5', '3.12.3')),
                contour_key(b, 1.0, 'source-B', ('2.3.5', '3.12.3')),
                contour_key(b, 1.0, 'source-A', ('2.3.5', '3.13.5')),
                contour_key(b, 1.0, 'source-A', ('2.3.5', '3.12.3'), depth=97),
                contour_key(b, 1.0, 'source-A', ('2.3.5', '3.12.3'), panels=64)]
    assert all(_canonical(a) != _canonical(v) for v in variants)
    assert a['rho_hex'] == 1.0.hex()


def test_original_cache_reuse_requires_exact_identity():
    from bass_he.geometry import EvidenceCache
    c = json.loads((R10A/'RUN_CONTRACT.json').read_text())
    cache = EvidenceCache(R10A/'cache')
    b = BRANCHES[0]
    key = contour_key(b, 0.0, c['source_sha256'], (c['numpy'], c['python']))
    assert cache.get(key)['rho'] == 0.0
    assert cache.get(contour_key(b, np.nextafter(0.0, math.inf), c['source_sha256'],
                                 (c['numpy'], c['python']))) is None
    assert cache.get(contour_key(b, 0.0, c['source_sha256'], (c['numpy'], c['python']),
                                 panels=64)) is None
    assert cache.get(contour_key(b, 0.0, 'different-source', (c['numpy'], c['python']))) is None


def test_exact_table_must_be_complete_and_finite():
    q = [{'branch':'S23','rho':1.0,'rho_hex':1.0.hex()},
         {'branch':'Q23','rho':2.0,'rho_hex':2.0.hex()}]
    rows = [{'branch':r['branch'],'rho':r['rho'],'rho_hex':r['rho_hex'],'delta':0.5} for r in q]
    assert validate_exact_table(q, rows) == 2
    with pytest.raises(ValueError, match='EXACT_TABLE'):
        validate_exact_table(q, rows[:1])
    with pytest.raises(ValueError, match='EXACT_TABLE'):
        validate_exact_table(q, rows+[rows[0]])
    broken=copy.deepcopy(rows);broken[1]['delta']=float('nan')
    with pytest.raises(ValueError, match='EXACT_TABLE'):
        validate_exact_table(q, broken)


def test_fixed_nodes_no_refinement_and_exact_identity():
    cuts=support_cutoffs()
    from bass_he.geometry import _gk15_nodes
    expected={float(x).hex() for a,b in zip(cuts[:-1],cuts[1:]) for x in np.sqrt(_gk15_nodes(a*a,b*b))}
    calls=[]
    def evaluate(rhos):
        calls.append(tuple(float(x).hex() for x in rhos))
        return np.ones((len(rhos),1))
    result=fixed_node_integrate(evaluate,cuts,expected)
    assert result['evaluations']==105 and result['refinements']==0 and result['interval_count']==7
    assert len(calls)==1
    with pytest.raises(ValueError, match='QUERY_IDENTITY'):
        fixed_node_integrate(evaluate,cuts,expected- {next(iter(expected))})


def test_frozen_branch_support_and_delta0_isolation():
    b=BRANCHES[0]
    r=np.array([0., b.support_cutoff, np.nextafter(b.support_cutoff,math.inf)])
    out=frozen_geometry_map([b],r,{b.name:0.75})
    assert out[(b.name,0.)]['delta']==0.75
    assert out[(b.name,float(b.support_cutoff))]['delta']==0.75
    assert (b.name,float(r[-1])) not in out


def test_analytic_probability_ratio():
    d0=0.4;d=0.5;v=2.0
    for factor in (1,2):
        direct=math.exp(-factor*d0/v)/math.exp(-factor*d/v)
        assert probability_ratio(d0,d,v,factor)==pytest.approx(direct,rel=1e-15)
