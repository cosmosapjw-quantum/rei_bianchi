import pytest

from bass_he.channel_semantics import (
    upper_shell_correlation_rows,
    branch_destination_semantics,
    appendix_a_nmax3_alias_oracle,
    require_disjoint_physical_labels,
)


def test_nmax3_united_upper_shell_correlates_entirely_to_bound_separated_states():
    rows=upper_shell_correlation_rows(3)
    assert len(rows)==6
    assert all(r['is_bound_correlation'] for r in rows)
    assert all(r['separated_center']=='Z2' for r in rows)
    assert sorted(r['separated_n'] for r in rows)==[2,3,3,3,3,3]


def test_q23_destination_is_united_upper_shell_but_separated_n2():
    rows={r['branch']:r for r in branch_destination_semantics(3)}
    q23=rows['Q23']
    assert q23['united_Nmax_member'] is True
    assert q23['separated_n']==2
    assert q23['separated_n_equals_Nmax'] is False
    for name in ('S23','Qother','Qm1'):
        assert rows[name]['united_Nmax_member'] is True
        assert rows[name]['separated_n']==3
        assert rows[name]['separated_n_equals_Nmax'] is True


def test_appendix_a_reports_n3_capture_equal_to_ionization_at_both_energies():
    o=appendix_a_nmax3_alias_oracle()
    assert o['exact_equalities'] is True
    assert o['rows'][0.5]['capture_n3']==o['rows'][0.5]['ionization']
    assert o['rows'][5.0]['capture_n3']==o['rows'][5.0]['ionization']


def test_overlapping_source_labels_cannot_be_promoted_as_disjoint_physical_channels():
    with pytest.raises(ValueError,match='overlap'):
        require_disjoint_physical_labels(uses_upper_shell_as_sink=True,also_exports_bound_correlations=True)
    require_disjoint_physical_labels(uses_upper_shell_as_sink=False,also_exports_bound_correlations=True)


def test_absorbing_double_pass_differs_from_reversible_final_population_by_p_squared():
    from bass_he.channel_semantics import (
        absorbing_double_pass_sink_probability,
        reversible_phase_averaged_double_pass_probability,
        absorbing_vs_reversible_bias,
    )
    for p in (0.0,1e-6,0.1,0.5,0.9,1.0):
        sink=absorbing_double_pass_sink_probability(p)
        rev=reversible_phase_averaged_double_pass_probability(p)
        assert sink == pytest.approx(p*(2-p))
        assert rev == pytest.approx(2*p*(1-p))
        assert absorbing_vs_reversible_bias(p) == pytest.approx(p*p)
    assert absorbing_double_pass_sink_probability(1.0)==1.0
    assert reversible_phase_averaged_double_pass_probability(1.0)==0.0


def test_current_q23_absorbing_event_reproduces_one_way_sink_not_reversible_population():
    import numpy as np
    from bass_he.transport import apply_eq50
    from arseny_reimpl.eq50_scoped import ordered_scoped_branches, branch_state_indices
    from arseny_reimpl.state_index import state_index
    from bass_he.channel_semantics import absorbing_double_pass_sink_probability
    branches=ordered_scoped_branches();events=[]
    for b in branches:
        i,j=branch_state_indices(b);events.append((i-1,j-1,b.state_b[0]==3))
    dim=state_index(3,2,2)
    initial=np.zeros((dim,1));initial[state_index(2,1,0)-1,0]=1
    prot=np.eye(dim)[None,:,:]
    q23_idx=[i for i,b in enumerate(branches) if b.name=='Q23'][0]
    sink_idx=state_index(3,2,0)-1
    for p in (0.01,0.2,0.5,0.9,1.0):
        probs=np.zeros((1,len(branches)));probs[0,q23_idx]=p
        y=apply_eq50(probs,events,prot,initial)[0,:,0]
        assert y[sink_idx] == pytest.approx(absorbing_double_pass_sink_probability(p),abs=2e-15)
