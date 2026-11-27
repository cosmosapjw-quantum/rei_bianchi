"""Research-only checks. No HH native integration or trajectory."""
import importlib.util
import os
from pathlib import Path
import numpy as np
import pytest
from scipy import linalg as la

HERE=Path(__file__).resolve().parent
INPUT=Path(os.environ.get('WU088_R31Y_INPUT',HERE/'inputs/EXISTING_METRIC_INPUTS.npz'))

def api():
    spec=importlib.util.spec_from_file_location('r31y_api',HERE/'lowrank.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def sample():
    rng=np.random.default_rng(31929)
    a=rng.normal(size=(7,7))+1j*rng.normal(size=(7,7));o=a@a.conj().T+np.eye(7)
    b=rng.normal(size=(5,2))+1j*rng.normal(size=(5,2))
    f=np.array([[1,1j],[-1j,-2]],complex)
    r=np.block([[np.zeros((5,5)),b],[b.conj().T,f]])
    return o,r

def test_synthetic_complete_nonzero_spectrum_and_inertia():
    o,r=sample();d=api().analyze(o,r,5)
    assert d['small_dimension']==4
    assert d['small_positive_negative_counts']==[2,2]
    assert d['small_vs_auxiliary_spectral_gap']<1e-12
    assert d['small_vs_raw_spectral_gap']<1e-12
    assert d['lifted_max_relative_residual_auxiliary']<1e-12

def test_nonzero_neutral_remainder_is_preserved_not_screened():
    o,r=sample();r[:5,:5]=np.diag([1e-5,0,0,0,0]);raw=r.tobytes()
    d=api().analyze(o,r,5)
    assert d['raw_minus_auxiliary_norm']>=1e-5*(1-1e-12)
    assert d['whitened_remainder_norm']>0
    assert r.tobytes()==raw
    assert d['certified'] is False

def test_time_unit_scaling():
    o,r=sample();a=api().analyze(o,r,5);b=api().analyze(o,7*r,5)
    assert np.allclose(b['small_eigenvalues_real'],7*np.array(a['small_eigenvalues_real']),rtol=1e-12)

def test_overlap_rescaling():
    o,r=sample();a=api().analyze(o,r,5);b=api().analyze(3*o,r,5)
    assert np.allclose(b['small_eigenvalues_real'],np.array(a['small_eigenvalues_real'])/3,rtol=1e-12)

@pytest.mark.parametrize('bad',['nan','nonsquare','bad_split','bool_split','indefinite','nonhermitian','zeroB','rankdefB'])
def test_invalid_prerequisites(bad):
    o,r=sample();n=5
    if bad=='nan':o[0,0]=np.nan
    elif bad=='nonsquare':o=o[:,:-1]
    elif bad=='bad_split':n=0
    elif bad=='bool_split':n=True
    elif bad=='indefinite':o=-np.eye(7)
    elif bad=='nonhermitian':r[0,1]=1
    elif bad=='zeroB':r[:5,5:]=0;r[5:,:5]=0
    elif bad=='rankdefB':r[:5,6]=r[:5,5];r[6,:5]=r[5,:5]
    with pytest.raises(ValueError):api().analyze(o,r,n)

def test_small_antihermiticity_is_exposed_not_silently_projected():
    o,r=sample();r[0,0]=1e-14j;before=r.tobytes()
    d=api().analyze(o,r,5)
    assert d['raw_residual_hermiticity_gap']>=2e-14
    assert d['general_eigensolver_used'] is True
    assert d['raw_minus_auxiliary_norm']>0 and r.tobytes()==before

def test_generic_complement_is_not_mistaken_for_invariant_sector():
    o,r=sample();q=np.eye(7)[:,:4]
    d=api().sector_diagnostic(o,r,q)
    assert d['O_cross_norm']>.1 and d['R_cross_norm']>.1

def test_Q_must_be_orthonormal_for_reported_involution():
    o,r=sample()
    with pytest.raises(ValueError):api().sector_diagnostic(o,r,2*np.eye(7)[:,:4])

@pytest.fixture(scope='module')
def stored():return api().replay(INPUT)

def test_stored_four_mode_core(stored):
    d=stored['lowrank']
    assert np.allclose(d['small_eigenvalues_real'],[-.4831184527967165,-.11540262422575817,.17743965987509827,.6007169417167519],atol=3e-13,rtol=0)
    assert d['small_vs_raw_spectral_gap']<3e-13
    assert d['whitened_remainder_norm']<1e-12
    assert d['small_positive_negative_counts']==[2,2]

def test_stored_algebraic_complement_contains_inner_pair(stored):
    d=stored['sectors']
    assert d['dimensions']==[25,24]
    assert d['O_cross_norm']<1e-13 and d['R_cross_norm']<1e-13
    assert np.allclose(d['complement_nonzero_real'],[-.11540262422575817,.17743965987509827],atol=3e-13,rtol=0)
    assert d['physical_sector_labels_assigned'] is False

def test_no_authority_promotion_or_source_mutation(stored):
    assert stored['input_unchanged'] is True
    assert stored['full_cell_bound'] is False and stored['production_admitted'] is False
    assert stored['native_evaluations']==0
    assert stored['Q_authority']=='Q_AUTHORITY_BLOCKED'

def test_tampered_snapshot_rejected(tmp_path):
    p=tmp_path/'bad.npz';p.write_bytes(b'bad')
    with pytest.raises(ValueError,match='SHA-256'):api().replay(p)

def test_create_only_output_fails_before_input_read(tmp_path):
    p=tmp_path/'keep.json';p.write_text('preserve')
    with pytest.raises(FileExistsError):api().main(['--input',str(tmp_path/'absent'),'--out',str(p)])
    assert p.read_text()=='preserve'
