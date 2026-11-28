import math, json, shutil
import numpy as np
import pytest
from bass_he_west82 import ContractError, NumericalFailure, solve_partial_wave
from bass_he_west82.source import load_resonances, optical_point, paper_k2, radial_input_point


def test_table_is_resonance_labels_not_sigma(root):
    t=load_resonances(root/'data/WEST82_TABLE_I.json',root/'source/PhysRevA.26.3164.pdf')
    assert t is not None and len(t['rows'])==25
    assert sum(x['ell']>32 for x in t['rows'])==16
    assert t['rows'][14]['E_cm_eV_token']=='0.121' and t['rows'][14]['ell']==38
    assert all(x['sigma'] is None and x['width'] is None for x in t['rows'])


def test_modified_table_fails(root,tmp_path):
    p=tmp_path/'bad.json'
    p.write_text((root/'data/WEST82_TABLE_I.json').read_text().replace('0.121','0.122'))
    with pytest.raises(ContractError):load_resonances(p,root/'source/PhysRevA.26.3164.pdf')


def test_modified_pdf_fails(root,tmp_path):
    p=tmp_path/'bad.pdf';p.write_bytes((root/'source/PhysRevA.26.3164.pdf').read_bytes()+b'\n')
    with pytest.raises(ContractError):load_resonances(root/'data/WEST82_TABLE_I.json',p)


def test_west_unit_adapter_hartree_ry_agrees():
    # Declared manufactured electronic inputs, not molecular data.
    h=optical_point(4.,-.8,-1.6,[.1,.2,0],energy_unit='Hartree',c_atomic=100.)
    r=optical_point(4.,-1.6,-3.2,[.1,.2,0],energy_unit='Ry',c_atomic=100.)
    assert h is not None and h==r
    assert h['V_hartree']==pytest.approx(.2)
    assert h['A_atomic']==pytest.approx(4/3/100**3*.8**3*.05)
    assert h['Gamma_hartree']==h['A_atomic']
    assert h['photon_energy_moment'] is None and not h['physical_source_admitted']


def test_dipole_phase_invariance():
    a=optical_point(2.,-.4,-1.,[1j,2.,0.],energy_unit='Hartree',c_atomic=100.)
    b=optical_point(2.,-.4,-1.,[-1.,2j,0.],energy_unit='Hartree',c_atomic=100.)
    assert a is not None and a['A_atomic']==b['A_atomic']


def test_paper_k2_preserves_historical_13_602():
    x=paper_k2('0.121','1000')
    assert x is not None and x['k2_bohr_inverse_squared']==pytest.approx(1000*.121/13.602)
    assert x['conversion']=='WEST1982_EQ11_13.602_NOT_MODERN_CONSTANT'


def test_radial_scale_factor_two():
    x=radial_input_point(1.,-.1,.01,1000.)
    assert x is not None and x['energy_over_E0']==2000
    assert x['potential_over_E0']==-200 and x['width_over_E0']==20

@pytest.mark.parametrize('ell',[33,38,48,64])
def test_high_l_free(ell):
    o=solve_partial_wave(1.,ell,[0.,ell+3.],[0.],[[0.]])
    assert o['loss_probability']==0.
    assert abs(complex(*o['S'])-1)<2e-10
    assert not o['physical_source_admitted']

@pytest.mark.parametrize('ell',[33,48,64])
def test_high_l_weak_absorber_is_positive(ell):
    o=solve_partial_wave(1.,ell,[0.,ell+3.],[0.],[[1e-22]])
    assert o['loss_probability']>0
    assert o['loss_formula']=='positive_flux_integral'


def test_small_first_cell_not_absolute_power_failure():
    # l32 is already supported by parent, but a^(l+1) normalization fails.
    edges=np.r_[0.,np.geomspace(1e-5,35.,81)]
    o=solve_partial_wave(1.,32,edges,[0.]*(len(edges)-1),[[0.]]*(len(edges)-1))
    assert abs(complex(*o['S'])-1)<2e-8

@pytest.mark.parametrize('bad',[65,True,-1,1.5])
def test_invalid_ell_kept_fail_closed(bad):
    with pytest.raises(ContractError):solve_partial_wave(1.,bad,[0.,1.],[0.],[[0.]])

@pytest.mark.parametrize('kw',[dict(energy_unit='eV',c_atomic=100.),dict(energy_unit='Hartree',c_atomic=0.),dict(energy_unit='Hartree',c_atomic=float('nan'))])
def test_undeclared_or_invalid_units_refused(kw):
    with pytest.raises(ContractError):optical_point(4.,-.8,-1.6,[.1,.2,0],**kw)


def test_rate_namespace_not_shadowed():
    import bass_he_west82
    assert 'bass_he_west82' in bass_he_west82.__file__
