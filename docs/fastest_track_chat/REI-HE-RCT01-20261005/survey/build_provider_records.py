"""Build explicit thermal-rate views using pinned supplier code; no cosmology run."""
from pathlib import Path
import copy, hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
HE = ROOT / 'survey/sources/BASS_HE'
SRC = HE / 'research/shared_c64/20261003/EOR_B3_ATOMIC_EXPORT_v1/src'
sys.path.insert(0, str(SRC))
from bass_he_atomic_export import export_packet, validate_packet

SCHEMA_PATH = ROOT / 'survey/sources/rei_bianchi/docs/atomic_reionization_handoff_20261004_v1/common/PROVIDER_CONTRACT.schema.json'
SCHEMA = json.loads(SCHEMA_PATH.read_text())
KNOWN = {'$schema', 'title', 'type', 'required', 'properties', 'enum', 'minLength', 'additionalProperties', '$comment'}

def validate(value, schema, path='$'):
    """All assertion keywords present in this exact small schema; fail unknown."""
    unknown = set(schema) - KNOWN
    if unknown:
        raise ValueError(f'UNSUPPORTED_SCHEMA_KEYWORDS {unknown}')
    if 'type' in schema:
        allowed = schema['type'] if isinstance(schema['type'], list) else [schema['type']]
        kinds = {'object': isinstance(value, dict), 'array': isinstance(value, list),
                 'string': isinstance(value, str), 'number': isinstance(value, (int,float)) and not isinstance(value,bool),
                 'boolean': isinstance(value,bool), 'null': value is None}
        if not any(kinds[t] for t in allowed):
            raise ValueError(f'TYPE {path}')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(f'ENUM {path}')
    if 'minLength' in schema and len(value) < schema['minLength']:
        raise ValueError(f'MIN_LENGTH {path}')
    if isinstance(value,dict):
        for key in schema.get('required',[]):
            if key not in value: raise ValueError(f'REQUIRED {path}.{key}')
        for key, val in value.items():
            if key in schema.get('properties',{}): validate(val,schema['properties'][key],path+'.'+key)
            elif schema.get('additionalProperties',True) is False: raise ValueError(f'ADDITIONAL {path}.{key}')
    return True

outdir = ROOT / 'publication'
outdir.mkdir(exist_ok=True)
views = ROOT / 'survey/thermal_rate_views'
views.mkdir(exist_ok=True)
records=[]
for short in ['KF96','GM25']:
    count_path=HE/f'docs/atomic_reionization_handoff_20261004_v1/threads/BASS_HE/runs/HE-F1_20261004/data/{short}_PACKET.json'
    req=copy.deepcopy(json.loads(count_path.read_text())['request'])
    req['quantity']='thermal_rate'
    packet=export_packet(req)
    assert validate_packet(packet)
    (views/f'{short}_THERMAL_RATE_PACKET.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
    src=packet['source']; rate=packet['records'][0]
    record={
      'provider_id':src['source_id'], 'process_id':packet['reaction_id'],
      'observable_kind':'thermal_rate',
      'source_identity':{'url':src.get('rate_source_url','https://doi.org/'+src.get('rate_source_doi','')),
        'version':src['source_id'],'read_status':'PINNED_SUPPLIER_THERMAL_RATE_VIEW_EXECUTED',
        'sha256':src['core_sha256'],'sha256_kind':'supplier_code_not_paper',
        'supplier_commit':'21d5b8075429903d195d6e0e0c24a10c00b21063',
        'source_packet_path':f'survey/thermal_rate_views/{short}_THERMAL_RATE_PACKET.json'},
      'units':'cm3 s-1','frame':'local_gas_rest_frame',
      'particle_distribution':'MAXWELL_COMMON_T_ZERO_DRIFT',
      'domain':{'variable':'temperature','units':'K','minimum':int(src['domain_K'][0]),'maximum':int(src['domain_K'][1]),
        'status':'source_supported','status_ceiling':'reported nominal prescription or fitted window; no true-rate certificate'},
      'species_in':{'HI':1,'HeIII':1},'species_out':{'HII':1,'HeII':1},
      'density_prefactor':'n_HI_proper_cm^-3 * n_HeIII_proper_cm^-3',
      'branches_and_floors':[{'outside_domain':'ERROR_NO_CLAMP_NO_EXTRAPOLATION','source_off':'NOT_EVALUATED_NOT_PHYSICAL_ZERO'}],
      'uncertainty':{'kind':'unresolved_source_and_energy_moment','rigorous_physical_bound':None,'fit_error_bound':None,'source_uncertainty':None,
        'source_spread_is_statistical_uncertainty':False},
      'energy_photon_closure':{'status':'unresolved','owner':'rei_bianchi',
        'code_contract':'conditional escape closure requires explicitly supplied escaped mean photon energy for each instantiated run',
        'source_photon_energy_moment_eV':None,'source_heat_moment_eV':None,'source_recoil_moment_eV':None,'source_spectrum':None,
        'consumer_escaped_mean_energy_eV':None,'consumer_thermal_remainder_eV':'Q_binding_eV - consumer_escaped_mean_energy_eV',
        'consumer_recoil_closure':'omitted only in the explicitly declared limited escape model; source moment remains unresolved',
        'primary_photon_injection':'none in escape closure','single_photon_birth':'conditional W82 ground-state spontaneous RCT scenario'},
      'implementation_status':'THERMAL_RATE_VIEW_EXECUTED; native adapter evidence must be read from coding/NATIVE_IMPLEMENTATION_STATUS.json',
      'consumer_admission':False,'closure_id':'EXPLICIT_CONDITIONAL_ESCAPE_MEAN_ENERGY_V1',
      'runtime_admission_scope':'explicit opt-in diagnostic/RHS instance only after complete input contract; baseline remains OFF',
      'coefficient':{'token':src['native_coefficient'],'native_unit':src['native_unit'],
        'si_token':rate['rate_token'],'si_unit':rate['unit'],'cgs_to_si_exact_factor':'1E-6'},
      'source_selected_role':'primary bounded code profile due to wider nominal temperature call window; no physical superiority claim' if short=='KF96' else 'optional alternative for paired sensitivity only in common temperature window',
      'pair_common_domain_K':[1000,10000],'alternatives_are_additive':False,
      'baseline_global_rct_enabled':False,'physical_accuracy_certified':False,
      'rate_record_does_not_relabel_count_packet':True,
      'separate_event_stoichiometry':{'species_order':['HI','HII','HeI','HeII','HeIII','e'],'nu':[-1,1,0,1,-1,0],'density_applied':False}
    }
    assert validate(record,SCHEMA)
    records.append(record)

negative=0
for record in records:
    for missing in SCHEMA['required']:
        mutant=copy.deepcopy(record);del mutant[missing]
        try: validate(mutant,SCHEMA)
        except ValueError: negative+=1
        else: raise AssertionError('missing required field accepted')
    for key,val in [('observable_kind','event_count_coefficients'),('consumer_admission','true'),('provider_id','')]:
        mutant=copy.deepcopy(record);mutant[key]=val
        try: validate(mutant,SCHEMA)
        except ValueError: negative+=1
        else: raise AssertionError('invalid field accepted')
envelope={'schema':'rei.he-rct-provider-selection-records.v1',
 'selection_policy':{'default':'OFF','primary_opt_in':'KF96_HEIII_HI_RCT_NOMINAL_V1','optional_alternative':'GM25_W82_RCX_CONSTANT_200_10000_K_V1',
   'reason':'KF96 nominal code profile supports broader temperature call window; source accuracy ranking not established',
   'legacy_ft03_temperature_guard_inherited':False,'mutual_exclusion':True,'same_reaction_sum_forbidden':True},
 'records':records,
 'validation':{'status':'PASS_FOR_ALL_ASSERTION_KEYWORDS_USED_BY_PINNED_SCHEMA','validator':'local restricted recursive validator, not full JSON Schema implementation',
   'schema_sha256':hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest(),'schema_git_blob':'13d35113dd3a4f4967e0e9574842973720a7c72c',
   'positive_records':2,'negative_controls_rejected':negative,'supplier_thermal_rate_exports':2,'supplier_self_consistency_replays':2,
   'script':'survey/build_provider_records.py','schema_success_is_physical_admission':False}}
(outdir/'PROVIDER_SELECTION_RECORDS.json').write_text(json.dumps(envelope,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(envelope['validation']))
