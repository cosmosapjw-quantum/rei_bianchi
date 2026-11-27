from pathlib import Path
import os, sys, pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import replay_snapshot
INPUT=Path(os.environ.get('WU088_R31X_INPUT',Path(__file__).resolve().parent/'inputs/EXISTING_METRIC_INPUTS.npz'))

def test_stored_full49_and_reduced_extrema_agree_pointwise():
    d=replay_snapshot.compute(INPUT)
    assert d['eta_reduced_point']==pytest.approx(0.6007169417167524,rel=1e-12)
    assert d['eta_full_point']==pytest.approx(0.6007169417167523,rel=1e-12)
    assert abs(d['eta_gap_full_minus_reduced'])<2e-15
    assert d['lambda_full_min']==pytest.approx(-0.4831184527967165,rel=1e-12)
    assert d['lambda_full_max']==pytest.approx(0.6007169417167519,rel=1e-12)

def test_extremal_full_vectors_are_in_retained_subspace_to_roundoff():
    d=replay_snapshot.compute(INPUT)
    p=d['extremal_full_eigenvector_O_projection_residual']
    assert p['negative']<2e-14 and p['positive']<2e-14

def test_reduced_is_not_full_spectral_equivalence():
    d=replay_snapshot.compute(INPUT)
    assert len(d['full_nonzero_generalized_eigenvalues_tol1e-12'])==4
    assert len(d['reduced_nonzero_generalized_eigenvalues_tol1e-12'])==2
    assert d['approx_rank_R']>=4 and d['approx_rank_R_reduced']>=2

def test_witnesses_lift_and_minimum_correction_lower_bound():
    d=replay_snapshot.compute(INPUT)
    pos=d['witnesses']['positive']; neg=d['witnesses']['negative']
    assert pos['ambient_rayleigh_real']==pytest.approx(0.6007169417167527,rel=1e-12)
    assert neg['ambient_rayleigh_real']==pytest.approx(-0.4831184527967168,rel=1e-12)
    assert pos['ambient_relative_eigen_residual']<1e-13
    assert neg['ambient_relative_eigen_residual']<1e-13
    assert d['minimum_whitened_connection_correction_lower_bound_from_reduced']==pytest.approx(0.3003584708583762,rel=1e-12)
    assert d['minimum_whitened_connection_correction_full_point']==pytest.approx(0.3003584708583762,rel=1e-12)

def test_source_is_immutable_and_claim_ceiling_closed():
    d=replay_snapshot.compute(INPUT)
    assert d['source_changed'] is False
    assert d['new_native_evaluations']==0 and d['new_heavy_scientific_nodes']==0 and d['HH_trajectory_runs']==0
    assert d['production_admitted'] is False and d['full_cell_interval_bound'] is False

def test_point_defect_is_cross_block_dominated_for_extremal_witnesses():
    d=replay_snapshot.compute(INPUT)
    pos=d['block_attribution_47_plus_2']['positive']
    neg=d['block_attribution_47_plus_2']['negative']
    assert abs(pos['neutral_neutral_real'])<1e-12
    assert pos['neutral_ionic_cross_real']==pytest.approx(0.6244098017137278,rel=1e-11)
    assert pos['ionic_ionic_real']==pytest.approx(-0.0236928599969749,rel=1e-11)
    assert neg['neutral_ionic_cross_real']==pytest.approx(-0.4640637914925836,rel=1e-11)
    assert neg['ionic_ionic_real']==pytest.approx(-0.01905466130413372,rel=1e-11)
    norms=d['residual_block_norms']
    assert norms['neutral_neutral_2norm']<2e-13
    assert norms['neutral_ionic_2norm']>0.3
    assert norms['ionic_ionic_2norm']<0.02

def test_archived_mixed_block_affine_derivative_compatibility_fails_conditionally():
    d=replay_snapshot.compute(INPUT)['mixed_block_interpolation']
    assert d['secant_slope_minus_endpoint_z0_dotO_2norm']==pytest.approx(0.5495713714162325,rel=1e-11)
    assert d['secant_slope_minus_endpoint_z4_dotO_2norm']==pytest.approx(0.33156843070467085,rel=1e-11)
    assert d['direct_z2_cross_residual_2norm']<2e-15
    assert d['hybrid_cross_residual_2norm']==pytest.approx(0.3649304141812512,rel=1e-11)
    assert d['connection_interpolation_mismatch_term_2norm']>d['derivative_mismatch_term_2norm']
    assert d['decomposition_closure_2norm']<2e-15
    assert d['physical_source_affineness_claim'] is False

def test_extremal_witness_cross_residual_decomposition_closes():
    d=replay_snapshot.compute(INPUT)['mixed_block_interpolation']
    p=d['positive_witness_decomposition']; n=d['negative_witness_decomposition']
    assert p['derivative_mismatch_real']+p['connection_interpolation_mismatch_real']+p['direct_z2_residual_real']==pytest.approx(p['hybrid_cross_real'],abs=2e-14)
    assert n['derivative_mismatch_real']+n['connection_interpolation_mismatch_real']+n['direct_z2_residual_real']==pytest.approx(n['hybrid_cross_real'],abs=2e-14)
    assert p['connection_interpolation_mismatch_real']>1.0
    assert n['connection_interpolation_mismatch_real']<-0.85
