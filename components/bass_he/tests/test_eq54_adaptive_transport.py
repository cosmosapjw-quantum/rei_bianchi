import numpy as np

from bass_he.eq54 import support_cutoffs, assemble_initial_column_batch, component_labels, decode_component_integral
from arseny_reimpl.eq50_scoped import ordered_scoped_branches


def synthetic_geometry(rhos):
    out={}
    for rho in rhos:
        for k,b in enumerate(ordered_scoped_branches()):
            if rho<=b.support_cutoff:
                out[(b.name,float(rho))]={'delta':0.15+0.02*k+0.01*rho}
    return out


def test_support_cutoffs_include_rotation_boundaries_and_branch_jumps():
    c=support_cutoffs(rotation_cut_scale=1.0)
    assert c[0]==0.0
    assert np.all(np.diff(c)>0)
    for b in ordered_scoped_branches():
        assert b.support_cutoff in c
    scaled=support_cutoffs(rotation_cut_scale=1.1)
    # Branch cutoffs stay fixed while the two rotational matching boundaries move.
    assert scaled[-1]==c[-1]
    assert scaled!=c


def test_dual_exponent_assembly_is_stochastic_and_packable():
    rhos=np.array([0.3,7.0]);energies=np.array([0.5,5.0]);factors=(1,2)
    out=assemble_initial_column_batch(synthetic_geometry(rhos),energies,rhos,exponent_factors=factors,rotation_steps=16)
    assert out['probabilities'].shape==(2,2,2,10)
    np.testing.assert_allclose(out['probabilities'].sum(-1),1.0,atol=2e-13)
    assert out['components'].shape==(2,2*2*9)
    labels=component_labels(energies,factors)
    assert len(labels)==36
    assert all(x['final_state_index']!=3 for x in labels)


def test_component_integral_decodes_into_disjoint_lanes():
    energies=np.array([0.5,5.0]);factors=(1,2)
    labels=component_labels(energies,factors)
    vec=np.arange(1,len(labels)+1,dtype=float)
    out=decode_component_integral(vec,energies,factors)
    assert set(out)=={'1','2'}
    for factor in ('1','2'):
        assert set(out[factor])=={'0.5','5.0'}
        for energy in ('0.5','5.0'):
            lane=out[factor][energy]
            assert len(lane['indexed_transition_areas_a0sq'])==9
            assert lane['reaction_loss_area_a0sq']==sum(lane['indexed_transition_areas_a0sq'].values())
