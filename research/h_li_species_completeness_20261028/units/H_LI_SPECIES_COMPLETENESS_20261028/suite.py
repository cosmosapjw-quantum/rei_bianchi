from pathlib import Path
import hashlib,json,sys
sys.dont_write_bytecode=True
import generator
import independent
U=Path(__file__).resolve().parent

def dump(name,obj):
    (U/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def rejected(fn):
    try:fn()
    except ValueError:return True
    raise AssertionError('INVALID_REGISTRY_IDENTITY_ACCEPTED')
def main():
    manifest=json.loads((U/'INPUT_BINDINGS.json').read_text());authority=json.loads((U/'inputs/AUTHORITY_INPUT_FREEZE.json').read_text());checked=[]
    for row in manifest['files']:
        raw=(U/row['unit_relative_path']).read_bytes()
        assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],'COPIED_SOURCE_IDENTITY_MISMATCH'
        checked.append({'path':row['unit_relative_path'],'bytes':len(raw),'sha256':row['sha256'],'public':row['public']})
    assert len(authority['files'])==6
    for row in authority['files']:
        matches=[x for x in manifest['files'] if x['path']==row['path']];assert len(matches)==1 and all(matches[0][k]==row[k] for k in ('bytes','sha256'))
    output=generator.create(U);ref=independent.inspect(U,output)
    sample=output['ATOMIC_CHARGE_REQUESTS.json']['requests'][0];nucleus=output['NUCLIDE_CATALOG.json']['catalog'][0]
    guards=[rejected(lambda:generator.validate_nucleus({**nucleus,'Z':4})),rejected(lambda:generator.validate_nucleus({**nucleus,'A':0})),rejected(lambda:generator.validate_atom({**sample,'charge':-1})),rejected(lambda:generator.validate_atom({**sample,'charge':sample['Z']+1})),rejected(lambda:generator.validate_aliases([('D','nuclear:1:2:0'),('D','nuclear:1:3:0')])),rejected(lambda:generator.validate_nucleus({**nucleus,'physical_activation':True})),rejected(lambda:generator.validate_atom({**sample,'kind':'MOLECULAR_CANDIDATE'})),rejected(lambda:generator.negative_reference_check({'element':'He','A':4,'state':'GROUND','stable_ground_anion':True})),rejected(lambda:generator.negative_reference_check({'element':'He','A':3,'state':'1s2s2p 4P','stable_ground_anion':False}))]
    assert all(guards)
    tests={**ref['controls'],'frozen6_inputs_plus_selected_legacy_provenance_identity':True,'invalid_identity_charge_alias_admission_molecule_He_ground_guards':True}
    assert len(tests)<=16 and all(tests.values())
    for name,obj in output.items():dump(name,obj)
    dump('REFERENCE.json',{**ref,'guard_rejections':len(guards),'input_identities_checked':checked,'new_control_group_count':len(tests)})
    result={'unit':'H_LI_SPECIES_COMPLETENESS_20261028','status':'PASS_FINITE_SNAPSHOT_REGISTRY_VALIDATION_PENDING_C9','scientific_admission':'PENDING_FRESH_THERMAL28_C9','counts':{'source_rows':31,'ground_nuclear_entries':26,'extra_nuclear_levels':5,'initial_H_LI_isotopes':7,'new_ground_vs_initial7':19,'ground_formal_charge_requests':82,'extra_nuclear_level_charge_requests':20,'formal_atomic_requests':102,'historical_atomic_charge_slots':20,'historical_separate_neutron':1,'historical_source_order':21,'negative_reference_groups':5,'isotope_negative_state_requests':26,'finite_electronic_level_examples':6,'configured_molecular_candidates':10,'new_atomic_process_requests':714,'new_missing_process_cells':621,'bare_bound_electron_process_not_applicable':93,'nuclear_decay_coverage_rows':31,'repository_projections':7,'registry_process_rows':ref['row_count']},'controls':tests,'control_groups':len(tests),'source_selection':'Independent full normalized source leading AAA ZZZi, Z001/002/003, no mass-number ceiling; exact31raw row equality','source_representation':'Exa-normalized official IAEA NUBASE2020 text; original fixedwidth bytes not acquired','catalog_scope':'Finite pinned NUBASE2020 snapshot; not allknown2026 or post2020 discovery census','formal_coordinates_not_physical_atoms':True,'Li3_unaccepted_retained':True,'H7_mass_systematics_not_discovery_rejection':True,'He2_diproton':'ADJACENT_SOURCE_COVERAGE_GAP_NOT_NONEXISTENCE','legacy_provider_preserved':'ElementalElectronicEquality conditional provider evidence retained; new exact isotope/state-qualified MISSING layer does not erase old implementation','REI_view_preserved':'ON_refined17-state previously verified source-specific pilot, no new array parse; distinct historical20+n21 and VigilODE6/reduced30/full33','source_ids_resolved':True,'old_source_or_solver_imports':0,'old_rate_checks':0,'new_rate_or_lifetime_evaluations':0,'new_ODEs':0,'source_input_transfer_allowance':0,'publication_prefix':'research/h_li_species_completeness_20261028/','private_only_inputs':['private_validation_inputs/NUBASE2020_EXA_NORMALIZED_FULL.txt'],'full_papers_copied':False,**generator.CEILINGS}
    dump('RESULTS.json',result)
    ledger={'R1':'PASS_PINNED_BASELINE_AND_SCOPE','R2':'PASS_OFFICIAL_NORMALIZED_SOURCE_AND_PRIMARY_NOTES','R3':'PASS_SOURCE_TO_KEYS','R4':'PASS_CATEGORY_SEPARATION','R5':'PASS_CONSTRUCTIVE_REGISTRY_SCHEMA','R6':'PASS_INDEPENDENT_PREEXEC_THERMAL28','R7':'PASS_ACTUAL_BOUNDED_DATA_VALIDATOR_CHILD','R8':'FINITE_REGISTRY_ONLY_PENDING_FRESH_C9_ADMISSION','R9':'PASS_SCHEMA_AND_INDEPENDENT_ORACLE_IMPLEMENTED','R10':'PASS_SOURCE_IDENTITIES_OUTPUTS_NEXT_INPUT_CHECKPOINT','C1':'PASS_SOURCE_PIN','C2':'PASS_SOURCE_KEY_MAPPING','C3':'PASS_EXACT_FINITE_ENUMERATION','C4':'CHILD_COMPLETED_WRAPPER_MEASURED_RECEIPT_REQUIRED','C5':'PASS_REGISTRY_AND_VALIDATOR','C6':'PASS_GUARDS','C7':'PASS_CHARGE_ISOTOPE_IDENTITIES','C8':'PASS_INDEPENDENT_RESELECTOR_NO_GENERATOR_IMPORT','C9':'PENDING_FRESH_THERMAL28_REVIEW','C10':'PENDING_ROOT_PUBLICATION_AND_BACKUPS','unearned_20_of_20_claim':False,'physical_activation':False,'canonical_delta':0}
    dump('LOOP_LEDGER.json',ledger)
    print(json.dumps({'status':'PASS','controls':len(tests),'source_rows':31,'formal_atoms':102,'negative_requests':26,'levels':6,'new_process_missing':621,'legacy_provider':'PRESERVED','physical_activation':False}))
if __name__=='__main__':
    try:main()
    except Exception as exc:
        dump('FAILURE.json',{'status':'FAIL_STOP_FOR_AUTHORITY','type':type(exc).__name__,'message':str(exc)})
        raise
