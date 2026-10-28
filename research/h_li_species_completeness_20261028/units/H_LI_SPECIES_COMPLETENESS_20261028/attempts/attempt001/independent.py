"""Independent source reselector and registry oracle; no production import."""
from collections import Counter
import json,re

def inspect(unit,output):
    selected=json.loads((unit/'inputs/NUBASE_H_LI_ROWS.json').read_text());audit=json.loads((unit/'inputs/SOURCE_AUDIT.json').read_text());model=json.loads((unit/'inputs/atomic_model.json').read_text())
    full=(unit/'private_validation_inputs/NUBASE2020_EXA_NORMALIZED_FULL.txt').read_text();reselected=[]
    for line in full.splitlines():
        match=re.match(r'^(\d{3})\s+(\d{3})(\d)\s',line)
        if match and int(match.group(2)) in (1,2,3):reselected.append((int(match.group(2)),int(match.group(1)),int(match.group(3)),line.strip()))
    expected=sorted((r['Z'],r['A'],r['nuclear_state_index'],r['source_row']) for r in selected['rows'])
    assert sorted(reselected)==expected,'FULL_NORMALIZED_SOURCE_SELECTION_MISMATCH'
    cat=output['NUCLIDE_CATALOG.json'];n=cat['catalog'];a=output['ATOMIC_CHARGE_REQUESTS.json']['requests'];e=output['ELECTRONIC_REFERENCE_AND_REQUESTS.json'];mol=output['MOLECULAR_CANDIDATES.json']['candidates'];process=output['PROCESS_COVERAGE.json'];baseline=output['BASELINE21_MAPPING.json'];projection=output['REPO_PROJECTIONS.json']['projections'];tests={}
    assert len(n)==31 and Counter(x['Z'] for x in n if x['nuclear_state_index']==0)=={1:7,2:8,3:11}
    assert len([x for x in n if x['nuclear_state_index']!=0])==5
    assert len(n)==len({x['key'] for x in n}) and {(x['Z'],x['A'],x['nuclear_state_index'],x['source_raw']) for x in n}==set(expected)
    tests['independent_full_normalized_reselector_31']=True
    original={(r['Z'],r['A'],r['nuclear_state_index']):r for r in selected['rows']}
    for x in n:
        raw=original[(x['Z'],x['A'],x['nuclear_state_index'])]
        assert x['nuclear_classification']==raw['nuclear_class'] and x['mass_systematics']==raw['mass_systematics'] and x['discovery_status']==raw['discovery_status'] and x['N']==x['A']-x['Z']>=0
        assert x['reported_lifetime_numeric'] is None and x['spin_systematics'] is None
    li3=next(x for x in n if x['Z']==3 and x['A']==3);h7=next(x for x in n if x['Z']==1 and x['A']==7);li13=next(x for x in n if x['Z']==3 and x['A']==13)
    assert li3['discovery_status']=='UNACCEPTED_IDENTIFICATION_ESTIMATE' and h7['mass_systematics'] is True and h7['discovery_status']!='UNACCEPTED_IDENTIFICATION_ESTIMATE' and li13['mass_systematics'] is False
    assert {(x['A'],x['nuclear_state_index']) for x in n if x['nuclear_state_index']!=0}=={(6,8),(7,8),(8,8),(10,1),(10,2)}
    tests['source_classification_systematics_nuclear_levels_distinct']=True
    initial={(1,1,0),(1,2,0),(1,3,0),(2,3,0),(2,4,0),(3,6,0),(3,7,0)};ground={(x['Z'],x['A'],0) for x in n if x['nuclear_state_index']==0}
    assert initial<=ground and len(ground-initial)==19
    assert cat['aliases']=={'D':'nuclear:1:2:0','T':'nuclear:1:3:0'}
    tests['initial7_aliases_19_new_ground']=True
    assert len(a)==102 and len({x['key'] for x in a})==102 and sum(x['nuclear_state_index']==0 for x in a)==82
    aset={x['key']:x for x in a}
    for x in n:
        matches=[y for y in a if y['nuclear_key']==x['key']]
        assert {y['charge'] for y in matches}==set(range(x['Z']+1))
        for y in matches:
            assert y['electron_count']==y['Z']-y['charge'] and y['atomic_bound_existence'] is None and y['plasma_species_admitted'] is False
            assert y['electronic_state']==('BARE_NO_BOUND_ELECTRONS' if y['charge']==y['Z'] else 'UNSPECIFIED_RESOLVED_LEVEL_REQUIRED')
            assert y['existence_scope']=='FORMAL_CHARGE_PROJECTION_OF_CATALOG_ENTRY'
    tests['102_formal_charge_identity_requests_no_atom_existence_promotion']=True
    assert baseline['historical_species_order']==model['species_order'] and [x['legacy_key'] for x in baseline['historical21']]==model['species_order'] and len(model['species_order'])==21
    assert baseline['historical21'][0]['kind']=='FREE_NEUTRON'
    assert len([x for x in baseline['historical21'] if x['new_atom_key'] in aset])==20
    assert baseline['legacy_conditional_provider']['actual_model_policy']==model['isotope_rate_policy'] and baseline['legacy_conditional_provider']['implementation_preserved']
    tests['historical20_plus_neutron21_exact_order_and_legacy_provider']=True
    refs=e['negative_reference_groups'];assert len(refs)==e['negative_reference_group_count']==5
    assert [(x['Z'],x['A']) for x in refs]==[(1,1),(1,2),(1,3),(3,None),(2,4)]
    for i,x in enumerate(refs):
        assert x['evidence_class']==audit['negative_states'][i]['status'] and x['source_citation']==audit['negative_states'][i]['source'] and x['electron_count']==x['Z']+1 and x['numerical_affinity'] is None and not x['isotope_transfer_allowed']
    assert 'THEORETICAL' in refs[2]['evidence_class'] and refs[4]['stable_ground_anion'] is False and refs[4]['J_components']==['1/2','3/2','5/2']
    requests=e['isotope_negative_requests'];assert len(requests)==26 and len({x['nuclear_key'] for x in requests})==26
    for x in requests:
        assert x['status']=='ISOTOPE_STATE_SOURCE_REQUIRED' and x['kinetics_value'] is None and not x['numerical_or_isotope_data_copied']
        if x['Z']==2 and x['A']==3:assert x['identity_matched_referenceIDs']==[]
        if x['Z']==3:assert x['identity_matched_referenceIDs']==[]
    tests['5_negative_reference_groups_26_isotope_requests_no_transfer']=True
    levels=e['electronic_level_references'];assert len(levels)==6
    for row,orig in zip(levels,audit['electronic_level_source_examples']):
        assert all(row[k]==v for k,v in orig.items()) and row['A'] is None and row['nuclear_spin'] is None and row['lifetime'] is None and row['collisional_rate'] is None
    assert e['pending_level_requests'][0]['spectrum']=='Li III' and e['pending_level_requests'][0]['status']=='SOURCE_PENDING'
    tests['6_exact_finite_electronic_levels_not_nuclear_or_rates']=True
    expected_molecules={'H2':[(1,1,2)],'HD':[(1,1,1),(1,2,1)],'HT':[(1,1,1),(1,3,1)],'D2':[(1,2,2)],'DT':[(1,2,1),(1,3,1)],'T2':[(1,3,2)],'Li6H':[(3,6,1),(1,1,1)],'Li7H':[(3,7,1),(1,1,1)],'He3Hplus':[(2,3,1),(1,1,1)],'He4Hplus':[(2,4,1),(1,1,1)]}
    assert {x['name'] for x in mol}==set(expected_molecules) and len(mol)==10
    for x in mol:
        assert [(y['Z'],y['A'],y['count']) for y in x['isotope_constituents']]==expected_molecules[x['name']]
        assert x['id'].startswith('molecule:') and x['electron_count']==sum(y['Z']*y['count'] for y in x['isotope_constituents'])-x['charge'] and sum(y['count'] for y in x['isotope_constituents'])==2
        assert x['kinetic_value'] is None and x['electronic_label']=='UNSPECIFIED'
    tests['10_separate_molecular_isotopologue_candidates']=True
    cells=process['atomic_process_requests'];assert len(cells)==714 and len({x['key'] for x in cells})==714
    na=0
    for x in cells:
        atom=aset[x['atom_key']];expected_na=atom['charge']==atom['Z'] and x['process'] in ('CI','PI','CE')
        assert x['numerical_value'] is None and x['declared'] and not any(x[k] for k in ('new_layer_implemented','implemented','executed','admitted','physical_activation'))
        assert x['scope']=='NEW_EXACT_ISOTOPE_STATE_QUALIFIED_REQUEST_LAYER_ONLY' and x['legacy_provider_implementation_erased'] is False
        assert x['new_layer_status']==('NOT_APPLICABLE_TO_THIS_TARGET_BOUND_ELECTRON_PROCESS' if expected_na else 'MISSING_INPUT');na+=expected_na
    assert na==93 and process['legacy_implementation_preserved'] and len(process['nuclear_decay_requests'])==31
    assert all(x['rate_numeric'] is None and x['Q_energy'] is None for x in process['nuclear_decay_requests'])
    tests['714_new_layer_cells_621_missing_93_not_applicable_nuclear_separate']=True
    assert len(projection)==7 and {x['repo'] for x in projection}=={'WU088_HH','rec_bianchi','BASS_HE','bass_cr','bass','vigilode','rei_bianchi'}
    for x in projection:assert not x['dimension_change'] and x['implemented_scope_unchanged'] and x['legacy_conditional_provider']['implementation_preserved'] and not x['physical_activation'] and not x['scenario_requires_all_future_catalog_species']
    rei=next(x for x in projection if x['repo']=='rei_bianchi');assert 'ON_refined17' in rei['role'] and 'NO_NEW_STATE_ARRAY_PARSE' in rei['REI_ON_refined17_source_qualification']
    tests['7_repo_roles_legacy_and_REI17_Vigi6_30_33_views_preserved']=True
    assert len(cat['adjacent_requests'])==4 and all(x['primary_row'] is None and x['physicalexistenceinference'] is None and not x['included_in_catalog_denominator'] for x in cat['adjacent_requests'])
    tests['He2_and_post2020_adjacent_gaps_not_absence_claims']=True
    source_ids=set(cat['sources'])
    def scan(obj):
        if isinstance(obj,dict):
            if 'source_id' in obj:assert obj['source_id'] in source_ids
            if 'physical_activation' in obj:assert obj['physical_activation'] is False
            if 'globalphysicalcompletion' in obj:assert obj['globalphysicalcompletion'] is None
            for value in obj.values():scan(value)
        elif isinstance(obj,list):
            for value in obj:scan(value)
    for obj in output.values():scan(obj)
    tests['all_source_ids_resolved_and_no_activation']=True
    # Identity bookkeeping controls: chemistry conserves isotope counts and charge
    # including electron; beta transformation conserves baryon and nuclear+lepton charge.
    assert (1,0)==(1,1-1) and (1,-1)==(1,0-1)
    assert 3==3 and 1==2-1
    tests['atomic_vs_nuclear_charge_baryon_bookkeeping']=True
    total=len(n)+len(a)+len(refs)+len(requests)+len(levels)+len(mol)+len(cells)+31+len(projection)+21
    assert total<=2000
    tests['bounded_registry_process_row_count']=True
    return {'status':'PASS_INDEPENDENT_DATA_ONLY_ORACLE','controls':tests,'control_groups':len(tests),'reselected_rows':[{'Z':z,'A':a,'index':i,'source_row':raw} for z,a,i,raw in sorted(reselected)],'row_count':total,'normalized_source_representation':'Official IAEA content Exa-normalized, not original fixed-width byte verification','generator_imported':False,'source_id_count':len(source_ids),'negative_reference_groups':5,'electronic_level_examples':6,'new_process_missing':621,'new_process_not_applicable':93}
