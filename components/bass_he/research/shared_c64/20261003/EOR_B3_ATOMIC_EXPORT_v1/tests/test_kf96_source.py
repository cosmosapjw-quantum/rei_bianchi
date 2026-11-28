"""HE-F1: explicit nominal source, compatibility and rejection semantics."""
import copy
from decimal import Decimal
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import pytest
from bass_he_atomic_export import (
    ContractError, SourceUnavailable, export_packet, validate_packet,
    bundle_packets, write_packet, sources, verify_runtime_bindings,
)

KF = 'KF96_HEIII_HI_RCT_NOMINAL_V1'
GM = 'GM25_W82_RCX_CONSTANT_200_10000_K_V1'
ROOT = Path(__file__).resolve().parents[1]


def req(source=KF, ts=None, unit='m3 s-1', quantity='event_count_coefficients'):
    return dict(schema='bass-he.atomic-request.v1', source_id=source,
                temperature_K=['1000'] if ts is None else ts,
                distribution='MAXWELL_COMMON_T_ZERO_DRIFT', isotope_basis='SOURCE_W82_4HE_H',
                initial_state='H1s', relative_drift_m_s=0,
                radiation_model='SPONTANEOUS_SINGLE_PHOTON',
                acknowledge_source_conflict=True, unit=unit, quantity=quantity)


def kf_core():
    assert importlib.util.find_spec('bass_he_atomic_export._kf96') is not None, 'KF96 implementation absent'
    return importlib.import_module('bass_he_atomic_export._kf96')


def test_registry_preserves_old_order_adds_explicit_alternative():
    r = sources()
    assert r['default_source_id'] is None and not r['automatic_source_ranking']
    ids = [s['source_id'] for s in r['sources']]
    assert ids == [GM, 'WEST82_OPTICAL_REFERENCE_V2', KF]
    assert not r['sources'][1]['thermal_rate_available']
    assert r['alternative_family']['common_comparison_domain_K'] == ['1000', '10000']
    assert r['alternative_family']['sources_are_additive'] is False
    r['sources'][-1]['native_coefficient'] = '0'
    assert sources()['sources'][-1]['native_coefficient'] == '1.00E-14'


@pytest.mark.parametrize('temperature,side', [('1000','right'),('1000.01','two_sided'),('10000','two_sided'),('10000000','left')])
@pytest.mark.parametrize('unit,expected', [('m3 s-1','1.00E-20'),('cm3 s-1','1.00E-14')])
@pytest.mark.parametrize('quantity', ['thermal_rate','event_count_coefficients'])
def test_nominal_rate_boundaries_units_and_counts(temperature,side,unit,expected,quantity):
    p = export_packet(req(ts=[temperature], unit=unit, quantity=quantity)); r=p['records'][0]
    assert p['exporter'] == 'bass-he-atomic-export==0.1.1'
    assert r['rate_token'] == expected and r['rate_binary64'] == float(expected)
    assert r['derivative_side'] == side and r['dk_dT_token'] == '0'
    assert r['reported_domain_K'] == ['1000','10000000']
    assert r['source_id'] == p['source']['source_id'] == KF
    assert r['source_location']['doi'] == '10.1086/192335'
    assert r['fit_error_bound'] is None and r['source_uncertainty'] is None
    for f in ('photon_energy_moment','heat_moment','recoil_moment','inverse_reaction_rate'):
        assert r[f] is None
    assert not r['physical_accuracy_certified'] and not r['conflict_resolved']
    if quantity == 'event_count_coefficients':
        nu = [-1,1,0,1,-1,0]
        assert r['stoichiometry'] == nu and r['photon_number_per_event'] == 1
        assert r['free_electron_delta'] == 0 and r['multiplying_density_pair'] == ['HI','HeIII']
        values=list(map(Decimal,r['species_rate_coefficients']))
        assert values == [Decimal(expected)*n for n in nu]
        for conserved in ([1,1,0,0,0,0],[0,0,1,1,1,0],[0,1,0,1,2,-1]):
            assert sum(v*w for v,w in zip(values,conserved)) == 0
    assert validate_packet(json.loads(json.dumps(p))) is True


def test_source_prescription_and_approximate_lower_marker_retained():
    r = export_packet(req())['records'][0]
    assert r['rate_semantics'] == 'NOMINAL_COMPILATION_PRESCRIPTION_NOT_PRECISE_TOTAL_RATE'
    assert r['table_temperature_token'] == '~1(3)-1(7)'
    assert r['lower_endpoint_is_approximate_in_source'] is True
    assert r['isotope_source_resolved'] is False
    assert r['state_mapping_kind'] == 'EXPLICIT_W82_GROUND_STATE_RCT_SCENARIO'
    assert r['boundary_policy'] == 'STRICT_NUMERIC_WINDOW_NO_CLAMP_OR_EXTRAPOLATION'


@pytest.mark.parametrize('t', ['999.999','10000000.001','0','-1','NaN','Infinity',True,{},'1'*129])
def test_kf_bad_temperature_is_rejected_for_domain_or_type(t):
    core=kf_core()
    kwargs=req(); kwargs.pop('schema'); kwargs.pop('temperature_K');kwargs.pop('quantity')
    with pytest.raises(ContractError): core.rate(t,**kwargs)


@pytest.mark.parametrize('field,value', [
    ('distribution','NONTHERMAL'),('relative_drift_m_s',1),('relative_drift_m_s','NaN'),
    ('isotope_basis','3HE_H'),('initial_state','H2s'),('radiation_model','STIMULATED'),
    ('acknowledge_source_conflict',False),('acknowledge_source_conflict',1),('unit','cm2')])
def test_kf_core_conventions_explicit(field,value):
    core=kf_core(); kwargs=req(); kwargs.pop('schema');kwargs.pop('temperature_K');kwargs.pop('quantity');kwargs[field]=value
    with pytest.raises(ContractError): core.rate('1000',**kwargs)


@pytest.mark.parametrize('source',[None,'AUTO','OFF_DIAGNOSTIC','WEST82_OPTICAL_REFERENCE_V2',[GM,KF],{'source':KF}])
def test_no_automatic_fallback_or_additive_source_list(source):
    with pytest.raises(ContractError): export_packet(req(source=source))


def test_density_geometry_and_missing_convention_refused():
    p=req();p['density_HI']=1
    with pytest.raises(ContractError): export_packet(p)
    p=req();p.pop('isotope_basis')
    with pytest.raises(ContractError): export_packet(p)


@pytest.mark.parametrize('field,value',[('heat_moment',0),('recoil_moment',0),('photon_energy_moment',40.8),('source_uncertainty',0),('conflict_resolved',True)])
def test_tampered_kf_packet_rejected(field,value):
    p=export_packet(req());p['records'][0][field]=value
    with pytest.raises(ContractError):validate_packet(p)


def test_kf_cannot_be_forged_as_legacy_gm_packet():
    p=export_packet(req());p['exporter']='bass-he-atomic-export==0.1.0'
    with pytest.raises(ContractError):validate_packet(p)


def test_alternative_packets_and_rate_count_views_never_add():
    gm=export_packet(req(source=GM));kf=export_packet(req())
    rate=export_packet(req(quantity='thermal_rate'))
    for packets in ([gm,kf],[kf,kf],[kf,rate]):
        with pytest.raises(ContractError, match='DUPLICATE_REACTION_NOT_ADDITIVE'):bundle_packets(packets)
    assert bundle_packets([kf])['packets'] == [kf]


def test_old_gm_packets_migrate_only_exporter_label():
    baseline=json.loads((ROOT/'tests/fixtures/gm25_v010_hashes.json').read_text())
    for case in baseline['packets']:
        new=export_packet(case['request'])
        normalized=copy.deepcopy(new);normalized['exporter']=baseline['exporter']
        encoded=json.dumps(normalized,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
        assert hashlib.sha256(encoded).hexdigest()==case['canonical_packet_sha256']
        assert validate_packet(normalized) is True
    r=verify_runtime_bindings()
    assert r['_rate.py']=='529ae325622718b48292c3b748a7850ccb315733b28bff930388f00915f2d217'
    assert r['_io.py']=='3dd8d8080216d6e4448d66590e411afdab4b6a801abf37a1c1fad47754c3bd88'


def test_common_domain_comparison_not_a_whole_domain_claim():
    for t in ['1000','2000','10000']:
        g=export_packet(req(GM,[t]))['records'][0]
        k=export_packet(req(KF,[t]))['records'][0]
        assert Decimal(g['rate_token']) / Decimal(k['rate_token']) == 17
    assert export_packet(req(GM,['200']))['records'][0]['rate_token']=='1.70E-19'
    with pytest.raises(ContractError):export_packet(req(KF,['200']))
    assert export_packet(req(KF,['10000000']))['records']
    with pytest.raises(ContractError):export_packet(req(GM,['10000000']))


def test_kf_whole_batch_failure_leaves_no_output(tmp_path):
    path=tmp_path/'should_not_exist.json'
    with pytest.raises(ContractError):write_packet(path,req(ts=['1000','999']))
    assert not path.exists()
    path2=tmp_path/'existing.json';path2.write_bytes(b'original\n')
    with pytest.raises(FileExistsError):write_packet(path2,req())
    assert path2.read_bytes() == b'original\n'


def test_kf_cli_and_semantic_validator(tmp_path):
    p=tmp_path/'request.json';out=tmp_path/'packet.json';p.write_text(json.dumps(req()))
    base=[sys.executable,'-W','error','-B','-m','bass_he_atomic_export']
    run=subprocess.run(base+['export',str(p),'--out',str(out)],capture_output=True,text=True)
    assert run.returncode==0,run.stderr
    assert subprocess.run(base+['validate',str(out)],capture_output=True).returncode==0
    assert json.loads(out.read_text())['source']['source_id']==KF
    assert subprocess.run(base+['export',str(p),'--out',str(out)],capture_output=True).returncode==2
