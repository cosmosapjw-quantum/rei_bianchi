"""Lossless source-row intake only: no rate evaluation or scientific solver."""
from pathlib import Path
import ast, csv, hashlib, json, re, time

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'raw'
EXT = ROOT / 'raw_external'
PIN = '34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad'
P78='research/hh_phys78_sandbox_nuclide_20261021/'
P81='research/hh_phys81_atomic_nuclear_source_contract_20261023/'
P83='research/hh_phys83_ce_completion_20261023/'
P87='research/hh_phys87_endf_np_native_moments_20261024/'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p): return json.loads((RAW/p).read_text())
def ref(p, locator):
    return {'repository':'cosmosapjw-quantum/WU088_HH','commit':PIN,'path':p,
            'local_path':'raw/'+p,'sha256':sha(RAW/p),'locator':locator,
            'url':f'https://github.com/cosmosapjw-quantum/WU088_HH/blob/{PIN}/{p}'}
def extref(name, locator):
    receipt=next(x for x in json.loads((EXT/'RECEIPTS.json').read_text()) if x['name']==name)
    return {'url':receipt['url'],'local_path':'raw_external/'+name,'sha256':sha(EXT/name),
            'locator':locator,'retrieval_date':'2026-10-25','source_representation':'original HTTP bytes'}
def write(name,obj): (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def base_row(identifier,process,reactants,products,source):
    return {'id':identifier,'process':process,'reactants':reactants,'products':products,'source':source,
            'energy_qualification':'PROVIDER_SOURCE_ROW_NOT_EVENT_ENERGY_ADMISSION',
            'empirical_rate_admitted_by_this_intake':False,'nuclear_Q_admitted_by_this_intake':False,
            'new_scientific_evaluation':False}
def csv_columns(name):
    ls=list(csv.reader((EXT/name).read_text().splitlines()))
    head,row=ls[0],ls[1]
    assert len(head)==len(row)
    return [{'index0':i,'name':h,'literal':v} for i,(h,v) in enumerate(zip(head,row))]

def main():
    t0=time.process_time(); w0=time.monotonic()
    src=ast.parse((RAW/(P78+'source/atomic_network.py')).read_text())
    lit={}
    for node in src.body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in ('_ISOTOPE_DATA','ELEMENT_IONS'):
                    lit[target.id]=ast.literal_eval(node.value)
    isotopes=[('n',1,0)]+list(lit['_ISOTOPE_DATA'])
    species=[]
    for name,a,z in isotopes:
        for q in range(z+1):
            species.append({'label':f'{name}:{q}','nuclide':name,'Z':z,'A':a,'isomer':'ground',
                 'charge':q,'electronic_state':'bare_nucleus' if q==z else 'charge_population_aggregate',
                 'composition':{f'{z}:{a}:ground':1},'pool':'thermal_material',
                 'state_resolution':'actual historical population; electronic substate unresolved unless bare',
                 'source':ref(P78+'source/atomic_network.py','_ISOTOPE_DATA; SPECIES comprehension; n slot')})
    write('configured_targets.json',{'scope':'historical explicitly configured populations only; future source catalogue is separate',
        'nuclides':[i[0] for i in isotopes],'species':species,'population_count':len(species),
        'original_nuclear_network_status':'NOT_RECOVERED_NOT_READ; no stable locator supplied by pinned contract',
        'all_future_target_set_known':False})
    rows=[]; coverage=[]
    photo_path=P78+'vendor/atomic/photo.dat'; rr_path=P78+'vendor/atomic/rec_table1.dat'
    photo={}; rr={}
    for i,line in enumerate((RAW/photo_path).read_text().splitlines(),1):
        w=line.split()
        if len(w)==11: photo[tuple(map(int,w[:2]))]=(i,line,w[2:])
    for i,line in enumerate((RAW/rr_path).read_text().splitlines(),1):
        try: key=(int(line[9:11]),int(line[12:14]))
        except ValueError: continue
        rr[key]=(i,line,[line[a:b].strip() for a,b in ((16,25),(27,33),(35,44),(46,55))])
    for key in lit['ELEMENT_IONS']:
        z,nel=key; q=z-nel
        for kind,data,path,names,units in [
          ('PI',photo,photo_path,['Eth','Emax','E0','sigma0','ya','P','yw','y0','y1'],['eV','eV','eV','Mb','1','1','1','1','1']),
          ('RR',rr,rr_path,['A','b','T0','T1'],['cm^3 s^-1','1','K','K'])]:
            no,raw,vals=data[key]
            rows.append({'id':f'VF96_{kind}_Z{z}_N{nel}','process':kind,'Z':z,'bound_electrons_lower_ion':nel,
             'charge_lower':q,'source':ref(path,f'line {no}'),'raw_row':raw,
             'coefficients':dict(zip(names,vals)),'coefficient_units':dict(zip(names,units)),
             'isotope_qualification':'elemental electronic row; no isotope-specific certification',
             'state_qualification':'ground target photoionization fit' if kind=='PI' else 'total Case A radiative recombination toward charge state; captures/cascades not state-resolved',
             'parameter_uncertainty':None,'uncertainty_status':'not supplied in selected coefficient row',
             'inherited_admission':'EXPLORATORY_ISOTROPIC_PI_RR_ISOTOPE_BLIND_CASE_A',
             'empirical_rate_admitted_by_this_intake':False,'new_scientific_evaluation':False})
    ci=rd(P81+'source_data/ADMITTED_FINITE_CI_REGISTRY.json')
    ci_samples=list(csv.DictReader((RAW/(P81+'source_data/PHYS81_CI_FINITE_WINDOW_LITERAL_DATA.csv')).read_text().splitlines()))
    cim={x['project_label']:x for x in ci['source_curves']}
    for name,a,z in isotopes:
        for q in range(z):
            for kind in ('CI','PI','RR'):
                provider=f'VF96_{kind}_Z{z}_N{z-q}' if kind in ('PI','RR') else (f'PHYS81_CI_{name}' if name in cim and q==0 else None)
                if kind=='CI': left={f'{name}:{q}':1,'e:thermal':1};right={f'{name}:{q+1}':1,'e:thermal':2}
                elif kind=='PI':left={f'{name}:{q}':1,'gamma:incident':1};right={f'{name}:{q+1}':1,'e:thermal':1}
                else:left={f'{name}:{q+1}':1,'e:thermal':1};right={f'{name}:{q}':1,'gamma:escaping':1}
                coverage.append({'id':f'{kind}:{name}:{q}','process':kind,'nuclide':name,'charge_lower':q,
                  'reactants':left,'products':right,'provider_id':provider,
                  'status':'SOURCE_ROW_AVAILABLE_FINITE_OPERATOR' if kind=='CI' and provider else ('SOURCE_ROW_AVAILABLE_ISOTOPE_BLIND_MODEL' if provider else 'MISSING_PROVIDER_NULL'),
                  'state_mapping':'ground CI branch in finite window' if kind=='CI' and provider else 'ground photo fit / charge aggregate Case A RR; isotope-blind explicit model',
                  'rate_value':None,'physical_full_rate_admission':'NOT_ISSUED',
                  'missing_is_not_zero':True})
    for i,c in enumerate(ci['source_curves']):
        n=c['project_label'];r=base_row(f'PHYS81_CI_{n}','CI',{f'{n}:0:ground':1,'e:thermal':1},{f'{n}:1:ground':1,'e:thermal':2},ref(P81+'source_data/ADMITTED_FINITE_CI_REGISTRY.json',f'/source_curves/{i}'))
        r.update({'provider_row':c,'chemical_defect_eV':c['chemical_I_eV'],'chemical_defect_uncertainty_eV':c['chemical_I_uncertainty_eV'],
          'support_eV':c['allowed_window_eV'],'frame':'stationary target incident electron; electron-mass Maxwell average in inherited finite operator',
          'branch':'ground residual ion only within selected finite support','branch_probability':None,
          'cross_section_uncertainty':None,'source_accuracy_domain':None,'numerical_T_K':ci['numerical_temperature_domain_K'],
          'inherited_admission':ci['status'],'full_rate_admission':ci['physical_full_rate_admission'],
          'literal_sample_source':ref(P81+'source_data/PHYS81_CI_FINITE_WINDOW_LITERAL_DATA.csv',f'rows project_nuclide_label={n}'),
          'raw_sample_rows':[x for x in ci_samples if x['project_nuclide_label']==n]})
        rows.append(r)
    ce=rd(P83+'source_data/HI_CE_SOURCE_CONTRACT.json')
    for pair,member in [('1s_to_2s','2S.1S'),('1s_to_2p','2P.1S'),('2s_to_1s','1S.2S'),('2p_to_1s','1S.2P')]:
        low,high=pair.split('_to_');r=base_row('PHYS83_CE_'+pair,'CE',{f'H1:0:{low}':1,'e:thermal':1},{f'H1:0:{high}':1,'e:thermal':1},ref(P83+'source_data/HI_CE_SOURCE_CONTRACT.json','/selected_raw_members/'+member))
        r.update({'raw_member':member,'raw_member_sha256':ce['selected_raw_members'][member]['sha256'],
          'raw_source':ref(P83+'source_data/CCC_'+member,'complete selected CCC member; first two header lines preserve direction and units'),
          'native_gap_eV':'10.2043500','gap_uncertainty':None,'gap_status':'native finite LS model literal, not isotope/fine-structure mass energy',
          'support_eV':ce['channel_convention']['excitation_support_eV'] if low=='1s' else ce['channel_convention']['reverse_source_support_eV'],
          'cross_section_unit':'a0^2','statistical_weights':ce['channel_convention']['state_degeneracies'],
          'physical_uncertainty':None,'inherited_source_status':ce['status'],'interpolation_contract':ce['allowed_computational_contract'],
          'raw_parse_result':ce['source_parse_and_reciprocity'][member]})
        rows.append(r)
    radiative=ce['radiative_data']
    for k,upper,nph,line1 in [('A_2s_two_photon_per_s','2s',2,2),('A_2p1_2_to_ground_per_s','2p_J1_2',1,3),('A_2p3_2_to_ground_per_s','2p_J3_2',1,4),('also_listed_2s_M1_per_s','2s',1,1)]:
        r=base_row('CHIANTI_'+k,'radiative_decay',{f'H1:0:{upper}':1},{'H1:0:1s':1,'gamma:escaping':nph},ref(P83+'source_data/HI_CE_SOURCE_CONTRACT.json','/radiative_data/'+k))
        raw_line=(RAW/(P83+'source_data/h_1.wgfa')).read_text().splitlines()[line1-1]
        r.update({'rate_literal':raw_line.split()[4],'rate_unit':'s^-1','rate_uncertainty':None,'branch_probability':None,
          'raw_source':ref(P83+'source_data/h_1.wgfa',f'line {line1}'),'raw_provider_row':raw_line,
          'branch_status':'absolute A, not a normalized branching ratio','source_ion_version':radiative['page_ion_version'],
          'two_photon_spectral_shape':'NOT_SUPPLIED' if nph==2 else 'NOT_APPLICABLE',
          'mapping_to_LS_model':'requires same native Delta accounting contract; retain observed fine-level metadata separately'})
        rows.append(r)
    nuc=rd(P87+'source_data/SOURCE_TABLE.json')
    r=base_row('ENDF_B_VIII1_H1_MT102','nuclear_capture',{'n:0':1,'H1:1':1},{'D:1':1,'gamma:escaping':1},ref(P87+'source_data/SOURCE_TABLE.json','/MF3_MT102;/MF6_MT102;/rows'))
    r.update({'stoichiometry_qualification':'bare nuclear schematic projection ONLY; actual source atomic-to-bare event map unresolved',
      'native_target':nuc['target'],'native_projectile':nuc['projectile'],'native_Q_eV':nuc['MF3_MT102']['QI_eV'],
      'native_Q_uncertainty':None,'frame':nuc['incident_energy_frame'],'secondary_angle_frame':nuc['secondary_angle_frame'],
      'native_mass_and_product_data':{'MF3':nuc['MF3_MT102'],'MF6':nuc['MF6_MT102']},
      'source_support_eV':[nuc['rows'][0]['En_eV'],nuc['rows'][-1]['En_eV']],
      'nominal_knots':len(nuc['rows']),'nominal_cells':len(nuc['rows'])-1,'cross_section_unit':'barn',
      'covariance_groups':153,'covariance_boundaries':154,'covariance_status':'PHYS91 B1 OPEN; no source confidence interval or repair admitted',
      'atomic_to_bare_map':'UNRESOLVED','native_Q_physical_event_admission':'NOT_ISSUED',
      'raw_endf_sha256':nuc['source_sha256'],'raw_endf_url':nuc['source_url'],
      'raw_endf':ref(P87+'source_data/n-001_H_001.endf','MF3/MT102; MF6/MT102; MF33/MT102'),
      'raw_table':nuc['rows']})
    rows.append(r)
    cold=rd(P81+'verification/nuclear/COLD_ROWS_FROM_RECEIPT.json')
    write('reused_cold_kinematic_rows.json',{'source':ref(P81+'verification/nuclear/COLD_ROWS_FROM_RECEIPT.json','/rows'),
      'rows':cold['rows'],'operation':'copied stored evaluated strings; no reaction or thermal re-evaluation',
      'uncertainty':None,'uncertainty_reason':'joint CODATA covariance not supplied in parent mass deck',
      'admission_boundary':'cold isolated bare-nucleus kinematics; no physical rate or source atomic-to-bare mapping'})
    catalog=[]
    for no,line in enumerate((EXT/'nubase_4.mas20.txt').read_text().splitlines(),1):
        if not line or line.startswith('#'):continue
        a=int(line[0:3]);z=int(line[4:7]);i=int(line[7:8]);s=line[16:17].strip()
        catalog.append({'Z':z,'A':a,'provider_state_index':i,'provider_state_symbol':s,
          'state_class':'ground' if i==0 else 'isomer' if s in ('m','n') else 'provider_non_ground_level_or_isomer_or_resonance_or_IAS',
          'nuclide_label':line[11:16].strip(),'mass_excess_keV':line[18:31].strip(),'mass_excess_uncertainty_keV':line[31:42].strip(),
          'excitation_keV':line[42:54].strip() or None,'excitation_uncertainty_keV':line[54:65].strip() or None,
          'excitation_origin':line[65:67].strip() or None,'ordering_uncertainty_marker':line[67:68].strip() or None,'ordering_inversion_marker':line[68:69].strip() or None,
          'half_life_literal':line[69:78].strip(),'half_life_unit':line[78:80].strip() or None,'half_life_uncertainty_literal':line[81:88].strip() or None,
          'spin_parity_literal':line[88:102].strip(),'branch_or_abundance_literal':line[119:209].strip() or None,
          'source_line1':no,'raw_row':line})
    keys=[(r['Z'],r['A'],r['provider_state_index']) for r in catalog]
    assert len(set(keys))==len(keys)
    with (ROOT/'nuclear_catalogue.jsonl').open('w') as f:
        for r in catalog:f.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
    selected=[r for r in catalog if (r['Z'],r['A']) in {(z,a) for _,a,z in isotopes} and r['provider_state_index']==0]
    write('nuclear_catalogue_manifest.json',{'source':extref('nubase_4.mas20.txt','header column definitions; all5843 data records'),
      'catalogue_rows':len(catalog),'ground_rows':sum(r['provider_state_index']==0 for r in catalog),
      'non_ground_rows':sum(r['provider_state_index']!=0 for r in catalog),'selected_configured_ground_rows':selected,
      'nuclide_catalogue_is_not_population_network':True,'charge_state':'not assigned by nuclear catalogue',
      'mass_convention':'mass excess of neutral atoms per evaluated nuclear mass convention, neutron exception; not bare masses',
      'systematics_marker_policy':'literal # retained; no estimated datum promoted to measured',
      'branch_parse_policy':'raw decay modes and intensities preserved; IS= denotes isotopic abundance, not a decay branch',
      'all_non_ground_are_isomers':False})
    for name in ('n','T'):
        stem='1n' if name=='n' else '3h';gs=csv_columns('livechart_'+stem+'.csv');br=csv_columns('livechart_'+stem+'_beta.csv');gd={x['name']:x['literal'] for x in gs}
        for evaluation in ('NUBASE2020','LiveChart_ENSDF'):
            target=next(r for r in selected if (r['Z'],r['A'])==((0,1) if name=='n' else (1,3)))
            left={'n:0':1} if name=='n' else {'T:0:neutral_ground':1}
            right={'H1:1':1,'e:beta':1,'antinu_e:escaping':1} if name=='n' else {'He3:1:one_bound_electron_unresolved':1,'e:beta':1,'antinu_e:escaping':1}
            source=extref('nubase_4.mas20.txt','line '+str(target['source_line1'])) if evaluation=='NUBASE2020' else extref('livechart_'+stem+'.csv','CSV record1; exact duplicate-column-preserving packet for beta file separately')
            r=base_row(f'{evaluation}_{name}_beta_minus','weak_beta_minus',left,right,source)
            r.update({'provider_evaluation':evaluation,'half_life_literal':target['half_life_literal'] if evaluation=='NUBASE2020' else gd['half_life'],
              'half_life_unit':target['half_life_unit'] if evaluation=='NUBASE2020' else gd['unit_hl'],
              'half_life_uncertainty_literal':target['half_life_uncertainty_literal'] if evaluation=='NUBASE2020' else gd['unc_hl'],
              'half_life_uncertainty_notation':'NUBASE explicit uncertainty same unit' if evaluation=='NUBASE2020' else 'ENSDF last-digit uncertainty raw; use explicit half_life_sec/unc_hls fields for SI',
              'half_life_seconds_literal':None if evaluation=='NUBASE2020' else gd['half_life_sec'],
              'half_life_uncertainty_seconds_literal':None if evaluation=='NUBASE2020' else gd['unc_hls'],
              'branch_literal':target['branch_or_abundance_literal'] if evaluation=='NUBASE2020' else gd['decay_1']+'='+gd['decay_1_%'],
              'branch_fraction_literal':'1','branch_uncertainty':None,
              'Q_keV_literal':None if evaluation=='NUBASE2020' else gd['qbm'],
              'Q_standard_uncertainty_keV_literal':None if evaluation=='NUBASE2020' else gd['unc_qb'],
              'Q_convention':'atomic ground-state mass difference from AME; not automatically beta kinetic endpoint or bare-nuclear Q',
              'electronic_state_transfer':'neutral T has one spectator bound electron; daughter He3+ manifold and shake-up/shake-off branches unresolved' if name=='T' else 'free neutron->bare proton; atomic-mass Q requires explicit electron binding/rest-mass conversion',
              'lepton_number_ledger':{'electron':1,'electron_antineutrino':-1,'sum':0},
              'electromagnetic_charge_residual':0,'baryon_residual':0,'rate_value':None,
              'source_conflict':'NUBASE T1/2=609.8(0.6)s versus LiveChart ENSDF2005 T1/2=613.9(0.6)s; preserve alternatives, no default activation' if name=='n' else None,
              'execution_activation':False,
              'raw_provider_row':target['raw_row'] if evaluation=='NUBASE2020' else gs})
            if evaluation=='LiveChart_ENSDF':r.update({'beta_radiation_row_columns':br,'beta_radiation_source':extref('livechart_'+stem+'_beta.csv','CSV record1, positional columns'),
                 'beta_uncertainty_issue':'duplicate unc_me column labels are retained positionally; beta-rad q uncertainty literal500 remains unresolved and is not substituted for ground-state unc_qb'})
            rows.append(r)
    write('provider_rows.json',{'schema':'WU_SOURCE_PROVIDER_ROW_EXTRACTION_V1','source_pin':PIN,
       'scope':'actual provider coefficients, cross-section/state/branch metadata, evaluated mass/decay rows; no empirical or nuclear-Q admission from registry intake',
       'rows':rows,'historical39_direction_coverage':coverage,'configured_population_source':'configured_targets.json',
       'nuclear_catalogue_source':'nuclear_catalogue_manifest.json','new_rate_evaluations':0,'new_IVP':0,
       'input_dependency_unknowns':['original nuclear network figure and its full target list','additional configured daughters/isomers without explicit source assignment','state-specific molecular/negative-ion provider handled by separate intake','source-approved MT102 nominal/full-precision covariance/formatter and actual atomic-to-bare kernel','named thermal/fast/radiation consumer ownership ACK']})
    manifest=[]
    for p in sorted(RAW.rglob('*')):
        if p.is_file():manifest.append({'local_path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p),'repository':'cosmosapjw-quantum/WU088_HH','commit':PIN,'path':str(p.relative_to(RAW))})
    write('GITHUB_INPUT_MANIFEST.json',manifest)
    write('EXTRACTION_RECEIPT.json',{'classification':'mechanical source parsing and transcription; no scientific evaluator',
        'provider_rows':len(rows),'historic_direction_coverage_rows':len(coverage),'configured_populations':len(species),
        'nuclear_catalogue_rows':len(catalog),'zero_physics_evaluation':True,'cpu_seconds':time.process_time()-t0,
        'wall_seconds':time.monotonic()-w0,'inherited_PHYS91_budget_debit':0,'exit_status':0})
    print(json.dumps({'provider_rows':len(rows),'coverage':len(coverage),'species':len(species),'nuclear_catalogue':len(catalog)}))

if __name__=='__main__':main()
