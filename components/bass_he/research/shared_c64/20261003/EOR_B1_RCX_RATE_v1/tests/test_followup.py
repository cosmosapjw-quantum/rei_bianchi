"""Post-implementation checks, not counted as observed RED/GREEN cases."""
from decimal import Decimal
from fractions import Fraction
import json
import pytest
from bass_he_rcx import SOURCE_ID, ContractError, parse_fit_excerpt, rate, batch, count_coefficients
KW=dict(source_id=SOURCE_ID,distribution='MAXWELL_COMMON_T_ZERO_DRIFT',acknowledge_source_conflict=True)

def test_exact_si_not_cross_section_conversion():
    si=rate(1000,**KW); cgs=rate(1000,**KW,unit='cm3 s-1')
    assert Fraction(si['rate_token'])/Fraction(cgs['rate_token'])==Fraction(1,1000000)
    assert Fraction(si['rate_token'])==Fraction(17,10**20)

def test_source_sentence_cannot_silently_change_coefficient(root):
    text=(root/'source/GM25_fit_excerpt.txt').read_text()
    with pytest.raises(ContractError):parse_fit_excerpt(text.replace('1.70','1.07'))

def test_no_surrogate_derivative_outside_source():
    assert rate(200,**KW)['derivative_side']=='right'
    assert rate(10000,**KW)['derivative_side']=='left'
    with pytest.raises(ContractError):rate('10000.0000000000000000001',**KW)

def test_batch_is_ordered_and_has_no_nan():
    rows=batch([200,250,750,5000,10000],**KW)
    text=json.dumps(rows,allow_nan=False)
    assert len(json.loads(text))==5
    assert all(r['fit_error_bound'] is None for r in rows)

def test_count_coefficients_exact_rational_charge_conservation():
    out=count_coefficients(5000,**KW)
    a=list(map(Fraction,out['species_rate_coefficients']))
    assert a[0]+a[1]==0 and a[2]+a[3]+a[4]==0
    assert a[1]+a[3]+2*a[4]-a[5]==0
    assert a[5]==0 and Fraction(out['photon_count_rate_token'])>0

def test_zero_missing_moment_never_serialized():
    out=count_coefficients(1000,**KW)
    for k in ['photon_energy_moment','heat_moment','recoil_moment','inverse_reaction_rate']:
        assert out[k] is None
    assert out['zero_missing_moment_fill'] is False

def test_empty_sequence_and_scalar_string_rejected():
    for a in ([], '1000', (x for x in [1000])):
        with pytest.raises(ContractError): batch(a,**KW)

def test_literal_precision_and_model_class_preserved():
    out=rate(Decimal('200.0'),**KW)
    assert out['coefficient_native_token']=='1.70E-13'
    assert out['data_kind']=='AUTHOR_REANALYSIS_THERMAL_RATE_FIT'
    assert out['conflict_resolved'] is False and out['raw_sigma_available'] is False
