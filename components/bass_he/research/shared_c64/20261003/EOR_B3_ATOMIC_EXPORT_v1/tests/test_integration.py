"""Narrow parity tests for migrated code, not a rerun of parent scientific suites."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from fractions import Fraction
import pytest
import bass_he_atomic_export as api


def original(root):
    spec=importlib.util.spec_from_file_location('rate_reference_for_test',root/'provenance/rate_core_original.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('quantity',['thermal_rate','event_count_coefficients'])
@pytest.mark.parametrize('unit',['m3 s-1','cm3 s-1'])
def test_migrated_parity(root,request_data,quantity,unit):
    ref=original(root);request_data.update(quantity=quantity,unit=unit)
    request_data['temperature_K']=['200','201','299.999','1000','9999.9','10000']
    kw={k:request_data[k] for k in ('source_id','distribution','isotope_basis','initial_state',
        'relative_drift_m_s','radiation_model','acknowledge_source_conflict','unit')}
    fn=ref.rate if quantity=='thermal_rate' else ref.count_coefficients
    expect=[fn(t,**kw) for t in request_data['temperature_K']]
    assert api.export_packet(request_data)['records']==expect


def test_exact_inherited_bytes(root):
    import importlib.resources as r
    for new,old in [('_rate.py','rate_core_original.py'),('_io.py','rate_io_original.py')]:
        assert r.files('bass_he_atomic_export').joinpath(new).read_bytes()==(root/'provenance'/old).read_bytes()
    assert len(api.verify_runtime_bindings())==2


def test_endpoint_derivative_is_fit_only(request_data):
    p=api.export_packet(request_data)
    assert [r['derivative_side'] for r in p['records']]==['right','two_sided','left']
    assert all(r['derivative_semantics']=='CONSTANT_FIT_ONLY_NOT_PHYSICAL_SLOPE' for r in p['records'])


def test_duplicate_temperatures_preserved_not_summed(request_data):
    request_data['temperature_K']=['1000','1000']
    p=api.export_packet(request_data)
    assert len(p['records'])==2
    assert p['records'][0]['rate_token']=='1.70E-19'


def test_rate_and_count_views_not_additive(request_data):
    a=api.export_packet(request_data);request_data['quantity']='thermal_rate';b=api.export_packet(request_data)
    with pytest.raises(api.ContractError,match='DUPLICATE_REACTION'):api.bundle_packets([a,b])


@pytest.mark.parametrize('text',['{"a":1e999}',b'\xff','[1,2', '[NaN]'])
def test_json_invalid(text):
    with pytest.raises(api.ContractError):api.loads_strict(text)


def test_json_length_budget():
    with pytest.raises(api.ContractError,match='BUDGET'):api.loads_strict('"abc"',max_bytes=4)


def test_whole_batch_failure_is_before_write(request_data,tmp_path):
    request_data['temperature_K']=['1000','199']
    with pytest.raises(api.ContractError):api.write_packet(tmp_path/'no.json',request_data)
    assert not (tmp_path/'no.json').exists()


def test_write_refuses_symlink(request_data,tmp_path):
    old=tmp_path/'old';old.write_text('unchanged')
    out=tmp_path/'out';out.symlink_to(old)
    with pytest.raises(FileExistsError):api.write_packet(out,request_data)
    assert old.read_text()=='unchanged'


def test_write_and_read_canonical_packet(request_data,tmp_path):
    out=tmp_path/'out';p=api.write_packet(out,request_data)
    assert api.loads_strict(out.read_bytes())==p
    assert api.validate_packet(p)


def test_preserve_unknown_flags(request_data):
    p=api.export_packet(request_data)
    for r in p['records']:
        for k in ['photon_energy_moment','heat_moment','recoil_moment','inverse_reaction_rate','source_uncertainty','fit_error_bound']:
            assert r[k] is None
        assert r['source_location']['original_cross_section_integration_reproduced'] is False


def test_boolean_not_numeric_packet_equal(request_data):
    p=api.export_packet(request_data);p['records'][0]['conflict_resolved']=0
    with pytest.raises(api.ContractError):api.validate_packet(p)


def test_extra_consumer_fields_not_smuggled(request_data):
    p=api.export_packet(request_data);p['gamma_bulk']=1.
    with pytest.raises(api.ContractError):api.validate_packet(p)


def test_rate_import_no_optical_dependency(root):
    env=os.environ.copy();env['PYTHONPATH']=env.get('B3_TEST_INSTALLED',str(root/'src'))
    code="import sys;import bass_he_atomic_export as a;a.sources();assert 'numpy' not in sys.modules;assert 'scipy' not in sys.modules;assert 'bass_he_rcx' not in sys.modules"
    r=subprocess.run([sys.executable,'-B','-S','-c',code],env=env,capture_output=True,text=True,timeout=15)
    assert r.returncode==0,r.stderr


def test_selected_batch_4096_boundary(request_data):
    request_data['temperature_K']=['1000']*4096
    assert len(api.export_packet(request_data)['records'])==4096
    request_data['temperature_K'].append('1000')
    with pytest.raises(api.ContractError):api.export_packet(request_data)
