from decimal import Decimal
from fractions import Fraction
import math
import pytest
from bass_he_rcx import SOURCE_ID, ContractError, SourceUnavailable, parse_fit_excerpt, rate, batch, count_coefficients, require_moment
KWS=dict(source_id=SOURCE_ID,distribution='MAXWELL_COMMON_T_ZERO_DRIFT',acknowledge_source_conflict=True)

def test_parse_primary_literal(root):
    r=parse_fit_excerpt((root/'source/GM25_fit_excerpt.txt').read_text())
    assert r is not None and r['coefficient_token']=='1.70E-13'
    assert r['Tmin_K']=='200' and r['Tmax_K']=='10000' and r['native_unit']=='cm3 s-1'

@pytest.mark.parametrize('T',[200,300,1000,3000,5000,10000,'200',Decimal('10000')])
def test_author_constant_and_conversion(T):
    r=rate(T,**KWS)
    assert r is not None
    assert Decimal(r['rate_token'])==Decimal('1.70e-19')
    assert r['unit']=='m3 s-1' and r['data_kind']=='AUTHOR_REANALYSIS_THERMAL_RATE_FIT'
    assert r['source_uncertainty'] is None and r['fit_error_bound'] is None
    assert not r['physical_accuracy_certified']

@pytest.mark.parametrize('T',[0,-1,199.999,10000.001,True,float('nan'),float('inf'),'NaN','-Infinity','bad'])
def test_bad_or_outside_temperature(T):
    with pytest.raises(ContractError): rate(T,**KWS)

@pytest.mark.parametrize('change',[
 {'source_id':None},{'source_id':'automatic'}, {'distribution':'monoenergetic'},
 {'distribution':'drifting_maxwell'}, {'acknowledge_source_conflict':False},
 {'acknowledge_source_conflict':'true'}, {'unit':'cm2'}, {'temperature_unit':'eV'},
 {'isotope_basis':'3He'}, {'initial_state':'H2s'}, {'relative_drift_m_s':1.0},
 {'relative_drift_m_s':float('nan')}, {'radiation_model':'stimulated'}])
def test_semantics_refusals(change):
    with pytest.raises(ContractError): rate(1000,**(KWS|change))

def test_native_cgs_and_analytic_derivative():
    r=rate(4000,**KWS,unit='cm3 s-1')
    assert r is not None and r['rate_token']=='1.70E-13'
    assert r['dk_dT_token']=='0' and r['derivative_semantics']=='CONSTANT_FIT_ONLY_NOT_PHYSICAL_SLOPE'

def test_batch_preserves_order_and_types():
    r=batch([1000,200,10000],**KWS)
    assert r is not None and [x['T_K'] for x in r]==['1000','200','10000']

def test_batch_no_partial_success():
    with pytest.raises(ContractError): batch([500,10001,200],**KWS)

def test_stoichiometric_photon_count():
    r=count_coefficients(1000,**KWS)
    assert r is not None and r['species_order']==['HI','HII','HeI','HeII','HeIII','e']
    assert r['stoichiometry']==[-1,1,0,1,-1,0]
    assert r['photon_number_per_event']==1 and r['free_electron_delta']==0
    assert r['photon_energy_moment'] is None and r['heat_moment'] is None
    q=list(map(Decimal,r['species_rate_coefficients']))
    assert q[0]+q[1]==0 and q[2]+q[3]+q[4]==0 and q[1]+q[3]+2*q[4]-q[5]==0

@pytest.mark.parametrize('name',['cross_section','heat','mean_photon_energy','photon_spectrum','recoil','inverse_rate'])
def test_not_infer_missing_moments(name):
    with pytest.raises(SourceUnavailable): require_moment(name,source_id=SOURCE_ID)

def test_source_location_travels_with_rate_packet():
    r=rate(1000,**KWS)
    assert r.get('source_location') == {
        'arxiv':'2511.21966v1','section':'Appendix B.3','pdf_page':9,
        'ancestral_cross_section_doi':'10.1103/PhysRevA.26.3164',
        'original_cross_section_integration_reproduced':False}
