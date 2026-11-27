"""Affected assumptions: changed support mask and restored exact input identity."""
import numpy as np
import pytest
from pathlib import Path
import execute_real_support as r


def test_inside_boundary_and_one_ulp_outside():
    cutoff=.5
    x=[np.nextafter(cutoff,0),cutoff,np.nextafter(cutoff,np.inf)]
    p=r.support_probabilities(np.ones((3,1)),x,[.5,5.],[cutoff])
    assert np.all(p[:4]>0) and np.all(p[4:]==0)


def test_inactive_zero_action_does_not_become_unit_probability():
    p=r.support_probabilities(np.zeros((1,2)),[2.],[.5,5.],[1.,3.])
    assert np.array_equal(p,[[0.,1.],[0.,1.]])


def test_same_support_retains_exact_dynamic_probability():
    delta=np.array([[.1,.2],[.3,.4]])
    p=r.support_probabilities(delta,[.1,.2],[.5,5.],[1.,2.])
    expected=np.exp(-2*np.repeat(delta,2,axis=0)/r.velocity(np.tile([.5,5.],2))[:,None])
    assert np.array_equal(p,expected)


def test_real_mask_is_subset_of_extended():
    real=np.array([b.R.real for b in r.BRANCHES]);ext=np.array([b.support_cutoff for b in r.BRANCHES])
    rho=np.concatenate([real,np.nextafter(real,np.inf),ext])
    a=r.support_probabilities(np.ones((len(rho),5)),rho,[.5,5.],real)
    b=r.support_probabilities(np.ones((len(rho),5)),rho,[.5,5.],ext)
    assert np.all((a>0)<=(b>0))


@pytest.mark.parametrize('bad',[np.nan,-1.,np.inf])
def test_bad_actions_fail(bad):
    with pytest.raises(ValueError):r.support_probabilities([[bad]],[.1],[.5],[.5])


def test_restored_exact_table_and_cache_content_authority():
    bank,eps,files=r.load_bank(Path('/tmp/BASS_HE_R10G_ENDPOINT_RUN_20260930'))
    assert len(bank)==1335 and len(eps)==5 and len(files)==300
    assert all(np.isfinite(float.fromhex(d)) and float.fromhex(d)>=0 for d,_ in bank.values())


def test_no_elastic_identity_tail_in_component_selection():
    rot=np.eye(10)[None,:,:]
    y=r.propagate(np.zeros((1,5)),rot)
    assert np.array_equal(y[:,np.arange(10)!=2],np.zeros((1,9)))


def test_unchanged_tail_panels_reuse_exact_r10f_nodes():
    import json
    q=json.loads((r.HERE/'QUERY_CONTRACT.json').read_text())
    assert q['tail_reuse_count']>0, 'unchanged u=rho^2 GK panels must reuse exact R10F pairs'


def test_prepared_contract_json_roundtrip_can_execute():
    q,_=r.prepare(Path('/tmp/BASS_HE_R10G_ENDPOINT_RUN_20260930'))
    assert q['tail_reuse_count']==540
