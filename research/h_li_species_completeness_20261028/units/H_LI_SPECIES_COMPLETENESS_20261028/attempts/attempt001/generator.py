"""Data-only H--Li finite-snapshot coverage generator; imports no solver/source."""
from pathlib import Path
import json,re
ELEMENT={1:'H',2:'He',3:'Li'}
INITIAL=((1,1),(1,2),(1,3),(2,3),(2,4),(3,6),(3,7))
PROCESSES=('CI','RR','DR','CX','CE','PI','radiative_levels')
CEILINGS={'physical_activation':False,'plasma_species_admitted':False,'globalphysicalcompletion':None,'L4':False,'production':'HOLD','canonical_completion_delta':0}
def nkey(z,a,i):return f'nuclear:{z}:{a}:{i}'
def akey(z,a,i,q):return f'atom:{z}:{a}:{i}:q{q}:level'+('BARE' if q==z else 'UNSPECIFIED')
def validate_nucleus(x):
    if any(isinstance(x[k],bool) or not isinstance(x[k],int) for k in ('Z','A','nuclear_state_index')) or x['Z'] not in ELEMENT or x['A']<x['Z'] or x['nuclear_state_index']<0:raise ValueError('INVALID_NUCLEAR_IDENTITY')
    if x.get('physical_activation') or x.get('plasma_species_admitted'):raise ValueError('SOURCE_FREE_PHYSICAL_ADMISSION')
def validate_atom(x):
    validate_nucleus(x)
    if x.get('kind')!='ATOM_REQUEST' or not isinstance(x['charge'],int) or isinstance(x['charge'],bool) or not 0<=x['charge']<=x['Z']:raise ValueError('INVALID_ATOM_CHARGE_OR_MOLECULE_AS_ATOM')
    if x['electron_count']!=x['Z']-x['charge']:raise ValueError('ELECTRON_COUNT')
    if x.get('electronic_state')=='STABLE_HE_MINUS_GROUND':raise ValueError('HE_MINUS_GROUND_CLAIM')
def validate_aliases(items):
    expected={'D':nkey(1,2,0),'T':nkey(1,3,0)}
    if len(items)!=2 or len({k for k,v in items})!=2 or dict(items)!=expected:raise ValueError('DUPLICATE_OR_INVALID_ALIAS')
def negative_reference_check(x):
    if x.get('element')=='He' and (x.get('A')!=4 or x.get('state')!='1s2s2p 4P' or x.get('stable_ground_anion') is not False):raise ValueError('HE_MINUS_GROUND_OR_ISOTOPE_TRANSFER')
def create(unit):
    inputs=unit/'inputs';rows=json.loads((inputs/'NUBASE_H_LI_ROWS.json').read_text());audit=json.loads((inputs/'SOURCE_AUDIT.json').read_text());model=json.loads((inputs/'atomic_model.json').read_text());bindings=json.loads((unit/'INPUT_BINDINGS.json').read_text())
    sources={Path(r['unit_relative_path']).name:{'unit_relative_path':r['unit_relative_path'],'original_path':r['path'],'sha256':r['sha256'],'public':r['public']} for r in bindings['files']}
    catalogs=[];atoms=[]
    for row in rows['rows']:
        z,a,i=row['Z'],row['A'],row['nuclear_state_index'];key=nkey(z,a,i)
        n={'key':key,'element':ELEMENT[z],'Z':z,'A':a,'N':a-z,'nuclear_state_index':i,'nuclear_label':row['label'],'nuclear_classification':row['nuclear_class'],'source_raw':row['source_row'],'source_locator':rows['source_url'],'source_id':'NUBASE_H_LI_ROWS.json','source_identity':{'normalized_full_sha256':rows['source_sha256'],'selected_rows_sha256':sources['NUBASE_H_LI_ROWS.json']['sha256'],'representation':rows['representation']},'discovery_status':row['discovery_status'],'mass_systematics':row['mass_systematics'],'spin_systematics':None,'spin_policy':'Not parsed from normalized token positions; raw source retained','reported_lifetime_numeric':None,'reported_decay_syntax':row['source_row'],'nuclear_stability':row['nuclear_class'],'electronic_stability':None,'pool':'NUCLEAR_CATALOG_RECORD','source_frame_clock':None,'coverage_axes':['nuclear_identity','evaluated_snapshot_entry'],'atomic_bound_existence':None,**CEILINGS}
        validate_nucleus(n);catalogs.append(n)
        for q in range(z+1):
            atom={**n,'key':akey(z,a,i,q),'kind':'ATOM_REQUEST','nuclear_key':key,'charge':q,'electron_count':z-q,'electronic_state':'BARE_NO_BOUND_ELECTRONS' if q==z else 'UNSPECIFIED_RESOLVED_LEVEL_REQUIRED','existence_scope':'FORMAL_CHARGE_PROJECTION_OF_CATALOG_ENTRY','pool':'FORMAL_ATOMIC_COORDINATE_REQUEST','coverage_axes':['nuclide','nuclear_state','charge','electronic_level_required'],'physical_activation':False,'atomic_bound_existence':None}
            validate_atom(atom);atoms.append(atom)
    ground=[x for x in catalogs if x['nuclear_state_index']==0];extra=[x for x in catalogs if x['nuclear_state_index']!=0]
    aliases=[('D',nkey(1,2,0)),('T',nkey(1,3,0))];validate_aliases(aliases)
    adjacent=[{'request':name,'status':status,'primary_row':None,'physicalexistenceinference':None,'included_in_catalog_denominator':False} for name,status in [('He2/diproton','ADJACENT_SOURCE_COVERAGE_GAP'),('H8','POST2020_DISCOVERY_COVERAGE_NOT_ESTABLISHED'),('He11','POST2020_DISCOVERY_COVERAGE_NOT_ESTABLISHED'),('Li14','POST2020_DISCOVERY_COVERAGE_NOT_ESTABLISHED')]]
    nuclides={'catalog':catalogs,'aliases':dict(aliases),'catalog_domain':'Exactly pinned NUBASE2020 normalized-extract Z1,2,3 rows; no A ceiling and no allknown2026 claim','counts':{'ground':len(ground),'extra_nuclear_levels':len(extra),'total':len(catalogs),'new_ground_vs_initial7':len(ground)-7},'initial_nuclear_keys':[nkey(z,a,0) for z,a in INITIAL],'adjacent_requests':adjacent,'sources':sources,**CEILINGS}
    atomout={'requests':atoms,'counts':{'ground_charge_slots':sum(x['Z']+1 for x in ground),'additional_nuclear_state_slots':sum(x['Z']+1 for x in extra),'total':len(atoms)},'scope':'Formal requested coordinates; not 102 physical plasma species','atomic_bound_existence':None,**CEILINGS}
    refs=[]
    for j,x in enumerate(audit['negative_states']):
        z=1 if j<3 else 3 if j==3 else 2;a=(1,2,3,None,4)[j]
        entry={'id':f'negative-reference-{j+1}','element':ELEMENT[z],'Z':z,'A':a,'nuclear_state_index':0 if a else None,'charge':-1,'electron_count':z+1,'state':'1s2s2p 4P' if z==2 else 'SOURCE_QUALIFIED_BOUND_ANION_REFERENCE','J_components':['1/2','3/2','5/2'] if z==2 else None,'stable_ground_anion':False if z==2 else None,'evidence_class':x['status'],'source_citation':x['source'],'source_id':'SOURCE_AUDIT.json','source_selector':f'negative_states[{j}]','source_note':x,'numerical_affinity':None,'kinetic_rates':None,'isotope_transfer_allowed':False,**CEILINGS}
        negative_reference_check(entry);refs.append(entry)
    negatives=[]
    for x in ground:
        cand=[r['id'] for r in refs if r['Z']==x['Z']]
        matches=[r['id'] for r in refs if r['Z']==x['Z'] and r['A']==x['A']]
        negatives.append({'id':x['key']+':negative-state-request','nuclear_key':x['key'],'Z':x['Z'],'A':x['A'],'nuclear_state_index':0,'charge':-1,'electron_count':x['Z']+1,'state':'ISOTOPE_RESOLVED_STATE_REQUIRED','status':'ISOTOPE_STATE_SOURCE_REQUIRED','referencecandidateIDs':cand,'identity_matched_referenceIDs':matches,'numerical_or_isotope_data_copied':False,'kinetics_status':'MISSING_INPUT','kinetics_value':None,'source_id':'NUBASE_H_LI_ROWS.json',**CEILINGS})
    spectra={'H I':(1,0),'He I':(2,0),'He II':(2,1),'Li II':(3,1)}
    levels=[]
    for j,x in enumerate(audit['electronic_level_source_examples']):
        z,q=spectra[x['spectrum']];levels.append({'id':f'electronic-level-reference-{j+1}',**x,'Z':z,'element':ELEMENT[z],'charge':q,'electron_count':z-q,'A':None,'nuclear_state_index':None,'electronic_spin_term':x['term'],'nuclear_spin':None,'isotope_qualification':'PENDING_NOT_TRANSFERRED_TO_ALL_ISOTOPES','source_id':'SOURCE_AUDIT.json','source_selector':f'electronic_level_source_examples[{j}]','source_family':'NIST retrieved finite level example','lifetime':None,'metastability_admitted':False,'collisional_rate':None,**CEILINGS})
    electronic={'negative_reference_group_count':5,'negative_reference_groups':refs,'isotope_negative_requests':negatives,'electronic_level_references':levels,'pending_level_requests':[{'spectrum':'Li III','configuration':'2s','status':'SOURCE_PENDING','numeric_level':None}],'nuclear_and_electronic_state_axes_distinct':True,'He3minus_no_He4_measurement_transfer':True,**CEILINGS}
    configurations=[('H2',[(1,1,2)],0),('HD',[(1,1,1),(1,2,1)],0),('HT',[(1,1,1),(1,3,1)],0),('D2',[(1,2,2)],0),('DT',[(1,2,1),(1,3,1)],0),('T2',[(1,3,2)],0),('Li6H',[(3,6,1),(1,1,1)],0),('Li7H',[(3,7,1),(1,1,1)],0),('He3Hplus',[(2,3,1),(1,1,1)],1),('He4Hplus',[(2,4,1),(1,1,1)],1)]
    molecules=[]
    for name,parts,q in configurations:
        molecules.append({'id':'molecule:'+name,'kind':'MOLECULAR_CANDIDATE','name':name,'isotope_constituents':[{'nuclear_key':nkey(z,a,0),'Z':z,'A':a,'count':count} for z,a,count in parts],'charge':q,'electron_count':sum(z*count for z,a,count in parts)-q,'electronic_label':'UNSPECIFIED','vibrational_label':'UNSPECIFIED','rotational_label':'UNSPECIFIED','nuclear_spin_symmetry':'UNSPECIFIED_ORTHO_PARA_NOT_ATOMIC_CHARGE_OR_NUCLEAR_ISOMER','kinetic_coverage':'PENDING','kinetic_value':None,'separate_existing_HD_evidence':'Previous reviewed REC-HD energy-defect interface only; no source adopted as new kinetics' if name=='HD' else None,'source_id':'FROZEN_CONTRACT.md',**CEILINGS})
    coverage=[]
    for x in atoms:
        for process in PROCESSES:
            na=x['charge']==x['Z'] and process in ('CI','PI','CE')
            coverage.append({'key':x['key']+':process:'+process,'atom_key':x['key'],'process':process,'numerical_value':None,'new_layer_status':'NOT_APPLICABLE_TO_THIS_TARGET_BOUND_ELECTRON_PROCESS' if na else 'MISSING_INPUT','reason':'Bare target has no bound electron to remove or excite' if na else 'Exact isotope/nuclear/electronic-state-qualified source and kinetics required','declared':True,'new_layer_implemented':False,'implemented':False,'executed':False,'admitted':False,'scope':'NEW_EXACT_ISOTOPE_STATE_QUALIFIED_REQUEST_LAYER_ONLY','legacy_provider_implementation_erased':False,'source_id':'FROZEN_CONTRACT.md',**CEILINGS})
    nuclear=[{'nuclear_key':x['key'],'process':'NUCLEAR_DECAY_TRANSMUTATION','source_report':x['source_raw'],'lifetime_numeric':None,'rate_numeric':None,'coverage':'SOURCE_IDENTITY_AND_LITERAL_DECAY_ONLY; QUALIFIED_RATE_BRANCH_DAUGHTER_ENERGY_REQUIRED','conservation':'Baryon sumA and electric charge including charged leptons; isotope may change; daughter may leave Z<=3','Q_energy':None,'energy_owners':'Mass convention, neutrino/photon/recoil unresolved; no Q from A','source_id':'NUBASE_H_LI_ROWS.json',**CEILINGS} for x in catalogs]
    processout={'atomic_process_requests':coverage,'nuclear_decay_requests':nuclear,'scope':'NEW exact isotope/state-qualified layer. Missing here does not mean historical ElementalElectronicEquality provider never implemented.','legacy_implementation_preserved':True,'source_catalog_is_not_rate_table':True,**CEILINGS}
    # Preserve actual historical source order, retaining its conditional provider policy.
    baseline=[];roman={'I':0,'II':1,'III':2,'IV':3}
    for pos,old in enumerate(model['species_order']):
        if old=='n':baseline.append({'position':pos,'legacy_key':old,'kind':'FREE_NEUTRON','new_nuclear_key':None,'new_atom_key':None,'charge':0,'not_H_LI_ion':True});continue
        match=re.fullmatch(r'(H1|D|T|He3|He4|Li6|Li7)(I|II|III|IV)',old);isotope,suffix=match.groups();z,a={'H1':(1,1),'D':(1,2),'T':(1,3),'He3':(2,3),'He4':(2,4),'Li6':(3,6),'Li7':(3,7)}[isotope];q=roman[suffix]
        baseline.append({'position':pos,'legacy_key':old,'kind':'LEGACY_ATOMIC_CHARGE_SLOT','new_nuclear_key':nkey(z,a,0),'new_atom_key':akey(z,a,0,q),'charge':q,'legacy_level_qualification':'Old provider electronic equality, not new resolved-level source admission'})
    legacy={'assumption':'ElementalElectronicEquality','actual_model_policy':model['isotope_rate_policy'],'scope':'Existing initial7 elemental-electronic-equality conditional RR/CI/CX provider evidence remains valid within its own source/owner scope; no isotope/state-resolved source is inferred for new records.','implementation_preserved':True,'provider_reexecuted':False,'no_isotope_specific_fit_claim':True,'source_ids':['atomic_model.json','atomic_network.py','WU_ALL_ISOTOPE_ATOMIC_SOURCE_COVERAGE.json','CR_N5_ATOMIC_ISOTOPE_COVERAGE.json'],'source_view_caution':'atomic_model is a pinned earlier pilot with its own excluded-process list; conditional CI/CX evidence belongs to later owner policies, not an assertion that this earlier file enabled them','historical_model_excluded_processes':model['excluded_processes']}
    baselineout={'historical21':baseline,'historical_species_order':model['species_order'],'counts':{'initial_H_LI_isotopes':7,'atomic_charge_slots':20,'separate_neutron':1,'historical_order_entries':21},'free_electron':'Derived/free-particle charge -1, not another nuclide or extra historical state','legacy_conditional_provider':legacy,'source_id':'atomic_model.json','source_identity':sources['atomic_model.json'],'solver_dimensions_changed':False,**CEILINGS}
    roles={'WU088_HH':('authoritative identities/elementary source/registry','WU_ALL_TARGET_SPECIES_REACTION_REGISTRY.json'),'rec_bianchi':('level populations/emission/absorption; actual historical21 source view','REC-EXP-SPECIES.json'),'BASS_HE':('differential collisions/recoil/birth; initial7 target projection','HE-EXP-SPECIES.json'),'bass_cr':('nonthermal/cascade/stopping; isotope process coverage','CR_N5_ATOMIC_ISOTOPE_COVERAGE.json'),'bass':('fixed existing geometric/chemical assembly; historical21 source view','atomic_model.json'),'vigilode':('mathematical6 chemical variables/reduced30/full33; no102-dimensional replacement','chemical_polynomial.py'),'rei_bianchi':('selected scenario/ledger/owner join; ON_refined17-state source-specific pilot distinct from historical20+n21 and VigilODE6/reduced30/full33','PHYSICAL_NEXT_CONTRACT.json')}
    projections=[]
    for repo,(role,sid) in roles.items():
        projections.append({'repo':repo,'role':role,'source_id':sid,'source_path':sources[sid]['original_path'],'source_sha256':sources[sid]['sha256'],'source_scope':'Role-specific inherited projection; primary source does not mean same dimensions in all repos','inherited_domain':'Initial7 isotope lineage; actual owner-selected source/domain retained','expanded_requested_keys':[x['key'] for x in atoms],'new_exact_layer_missing_process_count':sum(x['new_layer_status']=='MISSING_INPUT' for x in coverage),'new_exact_layer_not_applicable_count':sum(x['new_layer_status'].startswith('NOT_APPLICABLE') for x in coverage),'implemented_scope_unchanged':True,'legacy_conditional_provider':legacy,'unknown_processes_are_not_zero':True,'ownership':role,'dimension_change':False,'scenario_requires_all_future_catalog_species':False,'REI_ON_refined17_source_qualification':'REUSED_OWNER_OBSERVATION_NO_NEW_STATE_ARRAY_PARSE; authority/rei/AUDIT_KO.md, PR248 commit022f2ed85595364f05834d8eb1573434efce92d0 approved17state3cases; PR251 c5ab42c8673db614e7fb16695ad071c65becb81b ON_refined default. Not derived from HLI registry or a new17array parse' if repo=='rei_bianchi' else None,'WU_owner_progress':'Owner R16 33/48 remains separate from canonical28/88' if repo=='WU088_HH' else None,**CEILINGS})
    return {'NUCLIDE_CATALOG.json':nuclides,'ATOMIC_CHARGE_REQUESTS.json':atomout,'ELECTRONIC_REFERENCE_AND_REQUESTS.json':electronic,'MOLECULAR_CANDIDATES.json':{'candidates':molecules,'count':len(molecules),'scope':'Ten configured initial isotopologue requests, not all molecular states/isotopologues',**CEILINGS},'PROCESS_COVERAGE.json':processout,'BASELINE21_MAPPING.json':baselineout,'REPO_PROJECTIONS.json':{'projections':projections,'all_physical_activation_false':True,**CEILINGS}}
