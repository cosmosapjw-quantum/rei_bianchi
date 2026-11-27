import copy,json
from decimal import Decimal
import pytest
import bass_he_atomic_export as api

def get(name):
    fn=getattr(api,name,None)
    assert callable(fn),f'B3 behavior not implemented: {name}'
    return fn

def test_registry_requires_explicit_source():
    r=get('sources')()
    assert r['default_source_id'] is None
    assert len(r['sources'])==3
    assert r['sources'][2]['source_id']=='KF96_HEIII_HI_RCT_NOMINAL_V1'
    assert r['sources'][0]['availability']=='LITERATURE_FIT_OPT_IN'
    assert r['sources'][1]['thermal_rate_available'] is False

def test_roundtrip_keeps_source_meaning(request_data):
    p=get('export_packet')(request_data)
    assert p['schema']=='bass-he.atomic-export.v1'
    assert len(p['records'])==3
    assert p['production_admission']=='NOT_GRANTED_BY_EXPORTER'
    assert p['source']['origin_commit']=='9e3d54bf13045b01b3d7a493db78fa3289d3da9d'
    assert p['records'][1]['rate_token']=='1.70E-19'
    assert p['records'][1]['photon_energy_moment'] is None
    assert p['records'][1]['conflict_resolved'] is False
    assert get('validate_packet')(json.loads(json.dumps(p))) is True

@pytest.mark.parametrize('field',['source_id','distribution','isotope_basis','initial_state',
 'relative_drift_m_s','radiation_model','acknowledge_source_conflict','unit','quantity','schema'])
def test_missing_conventions_rejected(request_data,field):
    fn=get('export_packet');request_data.pop(field)
    with pytest.raises(ValueError):fn(request_data)

@pytest.mark.parametrize('key,value',[
 ('source_id','WEST82_OPTICAL_REFERENCE_V2'),('source_id','KF96_UNKNOWN'),
 ('temperature_K',['199.9']),('temperature_K',['10000.01']),('temperature_K',[True]),
 ('temperature_K',['NaN']),('temperature_K',[]),('temperature_K','1000'),
 ('relative_drift_m_s','1'),('isotope_basis','3HE_H'),('initial_state','H2s'),
 ('distribution','NONTHERMAL'),('radiation_model','STIMULATED'),
 ('acknowledge_source_conflict',False),('acknowledge_source_conflict',1),
 ('unit','cm2'),('quantity','heat'),('quantity','cross_section'),
 ('Hubble',1),('density_HI',1),('production_admission',True)])
def test_bad_or_out_of_scope_input_rejected(request_data,key,value):
    fn=get('export_packet');request_data[key]=value
    with pytest.raises(ValueError):fn(request_data)

@pytest.mark.parametrize('field,value',[
 ('heat_moment',0),('photon_energy_moment',40.8),('source_uncertainty',0),
 ('conflict_resolved',True),('rate_token','1.70E-18')])
def test_packet_tampering_rejected(request_data,field,value):
    ex=get('export_packet');va=get('validate_packet')
    p=ex(request_data);p['records'][0][field]=value
    with pytest.raises(ValueError):va(p)

def test_count_invariants_exact_and_unit_scaling(request_data):
    ex=get('export_packet');si=ex(request_data)
    request_data['unit']='cm3 s-1';cgs=ex(request_data)
    for a,b in zip(si['records'],cgs['records']):
        vals=list(map(Decimal,a['species_rate_coefficients']))
        for weights in ([1,1,0,0,0,0],[0,0,1,1,1,0],[0,1,0,1,2,-1]):
            assert sum(v*w for v,w in zip(vals,weights))==0
        assert a['free_electron_delta']==0 and a['photon_number_per_event']==1
        assert Decimal(a['rate_token'])==Decimal(b['rate_token'])*Decimal('1E-6')

def test_input_and_registry_ownership(request_data):
    fn=get('export_packet');original=copy.deepcopy(request_data);p=fn(request_data)
    assert request_data==original
    request_data['temperature_K'][0]='777'
    assert p['request']['temperature_K'][0]=='200'
    r=get('sources')();r['sources'][0]['availability']='CERTIFIED'
    assert get('sources')()['sources'][0]['availability']=='LITERATURE_FIT_OPT_IN'

def test_duplicate_reaction_bundle_rejected(request_data):
    p=get('export_packet')(request_data);fn=get('bundle_packets')
    with pytest.raises(ValueError):fn([p,p])

def test_one_packet_bundle_exact_preservation(request_data):
    p=get('export_packet')(request_data)
    b=get('bundle_packets')([p]);assert b['packets']==[p] and b['additive_reactions_checked']

@pytest.mark.parametrize('raw',['{"schema":1,"schema":2}','{"T":NaN}','{"T":Infinity}'])
def test_strict_json_rejects_ambiguous(raw):
    fn=get('loads_strict')
    with pytest.raises(ValueError):fn(raw)
