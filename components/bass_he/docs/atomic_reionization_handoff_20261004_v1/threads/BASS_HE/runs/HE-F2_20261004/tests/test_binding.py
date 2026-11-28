"""HE-F2 record adaptation and actual consumer exclusion, not a physics suite."""
from pathlib import Path
from fractions import Fraction
import copy
import json
import subprocess
import sys
import pytest
import he_f2_binding as target
from bass_he_atomic_export import export_packet

ROOT=Path(__file__).resolve().parents[1]

def fn(name):
    f=getattr(target,name,None)
    assert callable(f),f'HE-F2 implementation absent: {name}'
    return f

def packet(which='KF96', quantity='thermal_rate'):
    r=json.loads((ROOT/'inputs'/f'{which}_REQUEST.json').read_text())
    r['unit']='cm3 s-1';r['quantity']=quantity
    return export_packet(r)

def policy():
    return json.loads((ROOT/'inputs/rei_ft03/MODEL_POLICY.json').read_text())

@pytest.mark.parametrize('which,k',[('GM25','1.70E-13'),('KF96','1.00E-14')])
def test_candidates_match_actual_research_schema_without_admission(which,k):
    import jsonschema
    p=packet(which)
    x=fn('provider_candidate')(p)
    schema=json.loads((ROOT/'inputs/rei_ft03/PROVIDER_CONTRACT.schema.json').read_text())
    jsonschema.Draft202012Validator(schema).validate(x)
    assert x['provider_id']==p['source']['source_id']
    assert x['observable_kind']=='thermal_rate' and x['units']=='cm3 s-1'
    assert x['coefficient']['token']==k
    assert x['consumer_admission'] is False
    assert x['closure_id']=='UNRESOLVED_RCT_CLOSURE_NOT_SELECTED'
    assert x['energy_photon_closure']['status']=='unresolved'
    assert x['density_already_applied'] is False
    assert x['b3_packet']==p
    assert x['uncertainty']['rigorous_physical_bound'] is None

@pytest.mark.parametrize('quantity',['event_count_coefficients'])
def test_count_view_not_mislabelled_as_thermal_provider(quantity):
    with pytest.raises(ValueError,match='THERMAL_RATE_VIEW_REQUIRED'):
        fn('provider_candidate')(packet(quantity=quantity))

@pytest.mark.parametrize('field,value',[('heat_moment',0),('rate_token','0'),('source_uncertainty',0)])
def test_tampered_packet_cannot_be_adapted(field,value):
    p=packet();p['records'][0][field]=value
    with pytest.raises(ValueError):fn('provider_candidate')(p)

@pytest.mark.parametrize('a,b,want',[
    ([200,10000],[30000,110000],None),
    ([1000,10000000],[30000,110000],['30000','110000']),
    ([200,10000],[1000,10000000],['1000','10000']),
    ([200,10000],[10000,30000],['10000','10000'])])
def test_closed_interval_intersection_exact(a,b,want):
    assert fn('intersection')(a,b)==want

@pytest.mark.parametrize('a',[[True,2],[3,2],['NaN',4],[0,'Infinity'],[1]])
def test_malformed_domain_is_not_missing_or_zero(a):
    with pytest.raises(ValueError):fn('intersection')(a,[1,10])

@pytest.mark.parametrize('which,covered',[('GM25',False),('KF96',True)])
def test_actual_ft03_exclusion_is_not_source_zero(which,covered):
    x=fn('assess_consumer')(fn('provider_candidate')(packet(which)),policy())
    assert x['process_policy']=='EXPLICITLY_DISABLED_IN_CURRENT_CONSUMER'
    assert x['source_domain_covers_consumer_guard'] is covered
    assert x['action']=='NO_INJECTION'
    assert x['consumer_admission'] is False and x['replacement_rate'] is None
    assert 'RCT_CLOSURE_NOT_SELECTED' in x['blockers']

@pytest.mark.parametrize('f',['0.083','0.2','1'])
def test_normalization_keeps_electron_and_nuclei_invariants(f):
    x=fn('reaction_ledger')(f,{'HI':'13.598434599702','HeI':'24.587389011','HeII':'54.41776'})
    h,he2,he3=map(Fraction,x['fraction_pushforward_per_event_per_H'])
    assert h+Fraction(f)*(he2+2*he3)==0
    assert x['stoichiometry']==[-1,1,0,1,-1,0]
    assert x['conservation_dots']=={'H':0,'He':0,'charge':0}
    assert x['chemical_energy_change_eV']=='-40.819325400298'
    assert x['photon_energy_eV'] is None and x['prompt_heat_eV'] is None
    assert x['density_multiplication_owner']=='rei_bianchi'

@pytest.mark.parametrize('f',['0','-0.1','NaN'])
def test_invalid_he_abundance_rejected(f):
    with pytest.raises(ValueError):fn('reaction_ledger')(f,{'HI':'13','HeI':'24','HeII':'54'})


def test_complete_products_are_blocked_not_fake_consumer_acceptance(tmp_path):
    ps=fn('build_products')(ROOT)
    assert set(ps)=={'PROVIDER_CANDIDATES.json','REACTION_BINDING.json','CONSUMER_LEDGER_ACCEPTANCE.json','SOURCE_DOMAIN_ASSESSMENT.json'}
    a=ps['CONSUMER_LEDGER_ACCEPTANCE.json']
    assert a['state']=='BLOCKED_CONSUMER_CONTRACT'
    assert a['consumer_acceptance_issued'] is False
    assert a['baseline_may_continue'] is True
    assert a['paired_campaign_ready'] is False
    assert ps['SOURCE_DOMAIN_ASSESSMENT.json']['paired_intersection_with_current_consumer_K'] is None
    assert ps['REACTION_BINDING.json']['consumer_enabled'] is False
    assert a['external_dependencies']['REI_PROVIDER_CONTRACT']['resolved'] is False


def test_current_policy_mutation_needs_new_provenance(tmp_path):
    import shutil
    for sub in ['inputs','vendor']:
        shutil.copytree(ROOT/sub,tmp_path/sub)
    shutil.copy(ROOT/'INPUT_LOCK.json',tmp_path/'INPUT_LOCK.json')
    p=tmp_path/'inputs/rei_ft03/MODEL_POLICY.json'
    p.write_text(p.read_text().replace('charge_exchange','not_CX'))
    with pytest.raises(ValueError,match='INPUT_IDENTITY_MISMATCH'):
        fn('build_products')(tmp_path)


def test_create_only_is_not_consumer_enablement(tmp_path):
    out=tmp_path/'new'
    fn('write_products')(ROOT,out)
    before={p.name:p.read_bytes() for p in out.iterdir()}
    with pytest.raises(FileExistsError):fn('write_products')(ROOT,out)
    assert before=={p.name:p.read_bytes() for p in out.iterdir()}


def test_cli_reports_blocked_as_status_not_crash(tmp_path):
    assert callable(getattr(target,'build_products',None)),'HE-F2 implementation absent'
    p=subprocess.run([sys.executable,'-B',str(ROOT/'he_f2_binding.py'),'--root',str(ROOT),'--out',str(tmp_path/'out')],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    assert 'BLOCKED_CONSUMER_CONTRACT' in p.stdout
    assert json.loads((tmp_path/'out/CONSUMER_LEDGER_ACCEPTANCE.json').read_text())['consumer_acceptance_issued'] is False
