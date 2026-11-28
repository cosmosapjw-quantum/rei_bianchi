"""New DR11 tests only. Synthetic probabilities test bookkeeping, not ionization."""
import importlib.util
from pathlib import Path
import numpy as np
import pytest
from bass_he.transport import apply_eq50


def api():
    path=Path(__file__).parents[1]/'src/bass_he/nmax_migration.py'
    assert path.is_file(), 'DR11 first-hit migration implementation is missing'
    from bass_he import nmax_migration
    return nmax_migration


def toy(p=.7,q=.2):
    return np.array([[q,p]]),[(1,2,True),(0,1,False)],np.eye(3)[None],np.array([[1.],[0.],[0.]])


def test_missing_return_is_restored_by_first_hit_ledger():
    a=api();p=.7;q=.2
    r=a.tagged_eq50(*toy(p,q),shells=[2,3,4],threshold=3)
    b=a.migration_budget(r,shells=[2,3,4],old_threshold=3,new_threshold=4)
    assert b['returned_below_old'][0,0]==pytest.approx(p*p*(1-q)**2)
    assert b['resolved_old_to_new'][0,0]==pytest.approx(p*(1-p)*(1+(1-q)**2))
    assert b['new_unresolved'][0,0]==pytest.approx(p*q*(2-q))
    assert b['ever_hit'][0,0]==pytest.approx(p*(2-p))
    assert abs(b['closure_defect'][0,0])<1e-14


def test_complete_swap_returns_entire_old_sink():
    a=api();r=a.tagged_eq50(*toy(1.,0.),shells=[2,3,4],threshold=3)
    np.testing.assert_array_equal(r['hit'][0,:,0],[1.,0.,0.])
    np.testing.assert_array_equal(r['never_hit'],0)


def test_sparse_marginal_matches_exact_current_eq50_1000_draws():
    a=api();rng=np.random.default_rng(20260927)
    p=rng.random((1000,6));events=[(0,1,False),(1,2,False),(2,3,True),(0,2,False),(1,4,True),(3,4,False)]
    rot=rng.random((1000,5,5));rot/=rot.sum(axis=1,keepdims=True)
    initial=np.eye(5)
    result=a.tagged_eq50(p,events,rot,initial,shells=[1,2,3,4,4],threshold=3)
    np.testing.assert_allclose(result['total'],apply_eq50(p,events,rot,initial),atol=5e-15,rtol=0)
    np.testing.assert_allclose(result['hit'].sum(axis=1),result['first_hit_flux'].sum(axis=1),atol=3e-15,rtol=0)


def test_independent_path_enumeration_counts_first_visits():
    a=api();p,events,rot,initial=toy(.43,.67)
    # Independent path tree: explicitly branch each path; no lifted-operator code.
    histories=[(0,False,1.)]
    for k in [1,0,0,1]:
        i,j,sink=events[k];q=p[0,k];new=[]
        for state,hit,weight in histories:
            if state==i:choices=[(i,1-q),(j,q)]
            elif state==j and not sink:choices=[(j,1-q),(i,q)]
            else:choices=[(state,1.)]
            for dest,w in choices:new.append((dest,hit or dest>=1,weight*w))
        histories=new
    expected=np.zeros((2,3))
    for state,hit,weight in histories:expected[int(hit),state]+=weight
    result=a.tagged_eq50(p,events,rot,initial,shells=[2,3,4],threshold=3)
    np.testing.assert_allclose(result['never_hit'][0,:,0],expected[0],atol=1e-15)
    np.testing.assert_allclose(result['hit'][0,:,0],expected[1],atol=1e-15)


def test_tagged_total_equals_absorbing_first_hit_reference():
    a=api();rng=np.random.default_rng(4096)
    # Same event history, but freeze all columns in the marked region for the oracle.
    p=rng.random((23,4));ev=[(0,1,False),(1,2,False),(2,3,False),(3,4,True)]
    rot=np.broadcast_to(np.eye(5),(23,5,5)).copy();initial=np.eye(5)[:,:2]
    result=a.tagged_eq50(p,ev,rot,initial,shells=[1,2,3,4,5],threshold=3)
    y=np.broadcast_to(initial,(23,5,2)).copy()
    for k in [3,2,1,0,0,1,2,3]:
        i,j,sink=ev[k]
        mats=np.broadcast_to(np.eye(5),(23,5,5)).copy();q=p[:,k]
        mats[:,i,i]=1-q;mats[:,j,i]=q
        if not sink:mats[:,i,j]=q;mats[:,j,j]=1-q
        mats[:,:,2:]=np.eye(5)[None,:,2:]
        y=mats@y
    np.testing.assert_allclose(result['hit'].sum(1),y[:,2:].sum(1),atol=3e-15)


def test_initially_high_population_is_tagged_at_step_zero():
    a=api();r=a.tagged_eq50(np.empty((1,0)),[],np.eye(2)[None],np.eye(2),shells=[2,3],threshold=3)
    np.testing.assert_array_equal(r['first_hit_flux'][:,0,:],[[0.,1.]])
    np.testing.assert_array_equal(r['hit'][0],[[0.,0.],[0.,1.]])


def test_rotation_can_produce_first_hit():
    a=api();rot=np.array([[[0.,1.],[1.,0.]]])
    r=a.tagged_eq50(np.empty((1,0)),[],rot,np.array([[1.],[0.]]),shells=[2,3],threshold=3)
    assert r['hit'][0,1,0]==1.
    assert r['first_hit_flux'][0,1,0]==1.


def test_inputs_are_not_mutated():
    a=api();parts=toy();before=[x.copy() if hasattr(x,'copy') else list(x) for x in parts]
    a.tagged_eq50(*parts,shells=[2,3,4],threshold=3)
    for x,y in zip(parts,before):np.testing.assert_equal(x,y)


@pytest.mark.parametrize('bad',[-.1,float('nan'),1.1])
def test_bad_probability_rejected(bad):
    a=api();p,ev,rot,init=toy();p[0,0]=bad
    with pytest.raises(ValueError):a.tagged_eq50(p,ev,rot,init,shells=[2,3,4],threshold=3)


def test_invalid_state_indices_and_thresholds_rejected():
    a=api();p,ev,rot,init=toy();ev[0]=(1,3,True)
    with pytest.raises(ValueError):a.tagged_eq50(p,ev,rot,init,shells=[2,3,4],threshold=3)
    with pytest.raises(ValueError):a.tagged_eq50(*toy(),shells=[2,3,4],threshold=3.5)
    with pytest.raises(ValueError):a.tagged_eq50(*toy(),shells=[2,3],threshold=3)


def test_boundary_and_resolved_partition_are_disjoint():
    a=api();rows=a.correlation_rows(4)
    assert len(rows)==20
    assert sum(r['kind']=='unresolved' for r in rows)==10
    assert all(r['physical_channel'] is None for r in rows if r['kind']=='unresolved')
    assert all(r['formal_asymptote']['energy_hartree']<0 for r in rows)
    pop=np.zeros(20);pop[-1]=1.
    ledger=a.channel_ledger(pop,4)
    assert ledger['unresolved']==1.
    assert ledger['capture_Z2']==ledger['excitation_Z1']==ledger['survival_Z1_1s']==0.
    assert ledger['ionization_available'] is False


def test_promoted_3d_sigma_is_heplus_n2_not_n4():
    a=api();r=next(x for x in a.correlation_rows(4) if x['united']==[3,2,0])
    assert r['kind']=='resolved_bound_model'
    assert r['formal_asymptote']['center']=='Z2'
    assert r['formal_asymptote']['n']==2
    assert r['formal_asymptote']['energy_hartree']==-.5


def test_nmax_4_boundary_contains_both_atomic_centers():
    a=api();rows=[r for r in a.correlation_rows(4) if r['kind']=='unresolved']
    assert {r['formal_asymptote']['center'] for r in rows}=={'Z1','Z2'}


@pytest.mark.parametrize('n,d,b',[(3,10,6),(4,20,10),(5,35,15)])
def test_channel_dimensions_follow_eq49(n,d,b):
    a=api();rows=a.correlation_rows(n)
    assert len(rows)==d
    assert sum(r['kind']=='unresolved' for r in rows)==b


def test_small_sink_alone_does_not_certify_physical_convergence():
    a=api();pop=np.zeros(10);pop[0]=1.;ledger=a.channel_ledger(pop,3)
    assert ledger['unresolved']==0.
    assert not ledger['ionization_available']
    assert not ledger['physical_convergence_certified']


def test_shell_coverage_api_exists():
    assert hasattr(api(),'shell_coverage'), 'fixed separated-shell coverage audit is missing'


def test_hydrogen_n2_requires_nmax6_to_be_fully_resolved():
    a=api();assert hasattr(a,'shell_coverage'), 'fixed separated-shell coverage audit is missing'
    r=a.shell_coverage('Z1',2,5)
    assert (r['resolved_count'],r['boundary_count'],r['outside_count'])==(2,1,0)
    assert r['minimum_Nmax_for_resolved_shell']==6
    assert a.shell_coverage('Z1',2,6)['complete_resolved_shell']


def test_heplus_n2_completeness_changes_at_nmax4():
    a=api();assert hasattr(a,'shell_coverage'), 'fixed separated-shell coverage audit is missing'
    assert a.shell_coverage('Z2',2,3)['resolved_count']==2
    assert not a.shell_coverage('Z2',2,3)['complete_resolved_shell']
    assert a.shell_coverage('Z2',2,4)['complete_resolved_shell']


def test_hydrogen_source_eq17_yields_N_equals_2n_plus_n2():
    a=api();assert hasattr(a,'shell_coverage'), 'fixed separated-shell coverage audit is missing'
    for n in range(1,8):
        r=a.shell_coverage('Z1',n,3*n)
        assert r['minimum_Nmax_for_resolved_shell']==3*n
        assert all(x['united'][0]==2*n+x['separated']['n2'] for x in r['states'])
