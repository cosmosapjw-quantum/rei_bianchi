import importlib
import numpy as np
import pytest
from arseny_reimpl.transition import transition_block,ordered_probability_matrix


def api():
    assert importlib.util.find_spec('bass_he.transport') is not None,'sparse/finite-observable transport missing'
    return importlib.import_module('bass_he.transport')


def test_sparse_batch_matches_nonsymmetric_dense_product():
    mod=api(); rng=np.random.default_rng(771); dim=10
    # Genuine order sensitivity: asymmetric column-stochastic P_rot and absorbing event.
    rot=rng.random((4,dim,dim));rot/=rot.sum(-2,keepdims=True)
    p=rng.random((4,3)); events=[(0,1,False),(1,4,True),(3,6,True)]
    y0=np.eye(dim)[:,[0,3]]
    out=mod.apply_eq50(p,events,rot,y0)
    for b in range(4):
        ms=[transition_block(dim,i+1,j+1,p[b,k],absorbing_j=sink) for k,(i,j,sink) in enumerate(events)]
        dense=ordered_probability_matrix(dim,ms,rot[b])@y0
        np.testing.assert_allclose(out[b],dense,atol=5e-16)


def test_identity_tail_is_not_a_cross_section():
    mod=api(); nodes=np.linspace(0,100,201); P=np.broadcast_to(np.eye(3),(len(nodes),3,3)).copy()
    out=mod.integrate_transitions(nodes,P)
    np.testing.assert_array_equal(out['offdiagonal_area_a0sq'],np.zeros((3,3)))
    np.testing.assert_array_equal(out['reaction_loss_area_a0sq'],np.zeros(3))
    assert out['elastic_cross_section_available'] is False


def test_offdiagonal_loss_identity_and_simple_integral():
    mod=api(); r=np.linspace(0,2,2001); P=np.broadcast_to(np.eye(2),(len(r),2,2)).copy()
    P[:,0,0]=.7; P[:,1,0]=.3
    out=mod.integrate_transitions(r,P)
    assert abs(out['offdiagonal_area_a0sq'][1,0]-1.2*np.pi)<1e-12
    np.testing.assert_allclose(out['offdiagonal_area_a0sq'].sum(0),out['reaction_loss_area_a0sq'],atol=2e-14)


def test_exponent_policy_is_explicit():
    mod=api()
    a=mod.transition_probabilities([0.,.5,20],[.2],exponent_factor=1)
    b=mod.transition_probabilities([0.,.5,20],[.2],exponent_factor=2)
    np.testing.assert_allclose(b,a*a,rtol=2e-15)
    with pytest.raises(ValueError):mod.transition_probabilities([np.nan],[.2],exponent_factor=1)


def test_top_shell_is_not_counted_as_bound_capture_and_sink():
    mod=api(); labels=[{'kind':'bound','n':1},{'kind':'bound','n':2},{'kind':'sink','n':None}]
    out=mod.channel_partition(np.array([.2,.3,.5]),labels)
    assert out['bound_total']==.5 and out['sink_total']==.5
    assert out['bound_total']+out['sink_total']==1


def test_exact_swap_does_not_erase_a_tiny_positive_channel():
    mod=api(); initial=np.array([[1.],[1e-80]])
    y=mod.apply_eq50(np.array([[1.]]),[(0,1,False)],np.eye(2)[None],initial)
    # Two exact swaps must restore both channels, not round the rare one to zero.
    np.testing.assert_array_equal(y[0],initial)
