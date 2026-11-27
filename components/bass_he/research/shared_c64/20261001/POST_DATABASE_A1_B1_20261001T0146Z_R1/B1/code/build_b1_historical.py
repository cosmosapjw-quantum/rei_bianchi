from pathlib import Path
import csv,json,hashlib,shutil,re,datetime
from decimal import Decimal
ROOT=Path('/workspace/scratch/0b54847633d9'); R=ROOT/'BASS_HE_PRIMARY_SOURCE_ARCHIVE_20261001_v3'; W=ROOT/'b1_work'; O=ROOT/'BASS_HE_POST_DATABASE_A1_B1_20261001_v1/B1'; O.mkdir(parents=True,exist_ok=True)
P={x['id']:x for x in json.load(open(R/'PAPERS.json'))}; D={x['id']:x for x in json.load(open(R/'DATASETS.json'))}
now=datetime.datetime.now(datetime.timezone.utc).isoformat(); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,d): (O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def writecsv(n,rows,cols=None):
 cols=cols or list(dict.fromkeys(k for row in rows for k in row))
 with open(O/n,'w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
source_ids=['P01','P03','P04','P07','P08','P09','P10','P22']+list(D)
manifest=[]
for id in source_ids:
 x=P.get(id,D.get(id));path=R/x['path'];actual=sha(path);assert actual==x['sha256']
 manifest.append({'id':id,'path_relative_to_immutable_v3':x['path'],'sha256':actual,'bytes':path.stat().st_size,'doi':x.get('doi',x.get('dataset_doi',x.get('related_paper_doi'))),'source_class':x['status']})
manifest.append({'id':'v3_NUMERICAL_MATERIAL_GAPS','path_relative_to_immutable_v3':'NUMERICAL_MATERIAL_GAPS.json','sha256':sha(R/'NUMERICAL_MATERIAL_GAPS.json'),'bytes':(R/'NUMERICAL_MATERIAL_GAPS.json').stat().st_size})
dump('SOURCE_MANIFEST.json',{'immutable_archive_zip_sha256':'0f9dc51cc013aa0b91e7f3ff560bbca5afd1ee1551b67c8bb33278c445b1cd84','archive_check_author':'root; CRC and252manifest entries verified','source_file_hash_checks':'executed in B1','files':manifest})
cells=[]
def add(id,**kw):
 x=P.get(id,D.get(id));base={'source_id':id,'doi':x.get('doi',x.get('dataset_doi','')),'source_path':x['path'],'source_sha256':x['sha256'],'pdf_page':'','printed_page':'','table':'','source_row':'','source_column':'','energy_token':'','energy_unit':'','velocity_token':'','velocity_unit':'','energy_frame':'UNRESOLVED','isotope':'NOT_EXPLICITLY_ASSIGNED','projectile':'He2+','target_initial_state':'H(1s)','final_state':'','observable':'electron_capture_cross_section','value_token':'','cross_section_unit':'','method':'','uncertainty_token':'','uncertainty_kind':'NOT_REPORTED_PER_CELL','evidence_status':'LITERATURE_SUPPORTED','transcription_status':'VERIFIED_SOURCE_NATIVE','benchmark_admission':'SOURCE_NATIVE_CELL_ONLY;G1_NOT_AUTHORIZED','interpolation':'NOT_RUN','frame_conversion':'NOT_RUN','new_shell_sum':'NOT_RUN'};base.update(kw);cells.append(base)
# P03: source-authored HSCC column only. Other table columns are secondary quotations and deliberately omitted.
for e,v in [('20','7.1[-9]'),('50','8.0[-5]'),('100','3.4[-2]'),('200','2.4[-1]'),('600','1.74'),('1000','4.42'),('1600','7.56'),('2000','9.86'),('4000','16.2')]:
 add('P03',pdf_page=9,printed_page='052705-9',table='II',source_row=e,source_column='HSCC',energy_token=e,energy_unit='eV',energy_frame='center_of_mass;PDF8 SectionIV',final_state='He+(n=2);four-channel model native charge-transfer total',value_token=v,cross_section_unit='10^-16 cm^2',method='HSCC;fully quantum nuclear dynamics;four asymptotic channels',uncertainty_kind='NO_PER_CELL_UNCERTAINTY;finite-channel convergence not demonstrated by table',transcription_status='VISUAL_TABLE_TRANSCRIPTION;PDF9')
# P09: 6 complete native velocity tables, all300 value+convergence pairs cross-parser verified.
for t in range(25,31):
 d=json.load(open(W/f'P09_table{t}.json'))
 for row in d['rows']:
  for c in row['cells']:
   add('P09',pdf_page=d['pdf_page'],printed_page=d['pdf_page'],table=str(t),source_row=row['velocity_token'],source_column=c['final_subshell'],velocity_token=row['velocity_token'],velocity_unit='atomic_unit_of_velocity',energy_frame='relative_projectile_target_velocity;target-rest electronic representation;no_energy_adapter',target_initial_state='H(1s)' if t<28 else 'H(2s)',final_state='He+('+c['final_subshell']+')',value_token=c['value_token'],cross_section_unit='10^-16 cm^2',method='AOCC;author average of B1/B2 GTO bases',uncertainty_token=c['source_convergence_token'],uncertainty_kind='epsilon=abs(sigma_B1-sigma_B2)/sigma_average;dimensionless convergence diagnostic;not Gaussian uncertainty',transcription_status='PDF10_11_VISUAL_PLUS_TWO_TEXT_PARSERS_ALL_TOKENS_MATCH',benchmark_admission='NATIVE_VELOCITY_ONLY;NO_EXACT_KEVU_ROW_ASSERTED;G1_NOT_AUTHORIZED')
# P04: complete original Appendix A3, blanks omitted rather than replaced by zero.
a3=json.load(open(W/'metadata_review/P04_A3_verified_cells.json'))
for row in a3['rows']:
 label=row['row_label_native']
 for method,v in row['values'].items():
  if v is None:continue
  if label.startswith('sigma'):final=label+';'+a3['native_total_semantics'][label]
  elif ',' in label:
   n,l=label.split(',');final=f'He+(n={n},l={l});source-native subshell'
  else:final=f'He+(n={label});source-native shell'
  add('P04',pdf_page=8,printed_page=7,table='A3',source_row=label,source_column=method,energy_token='5',energy_unit='keV/u',energy_frame='incident_projectile_energy_per_mass_unit;frame/isotope detail in matrix;no_conversion',final_state=final,value_token=v,cross_section_unit='cm^2',method=method,transcription_status='ALL_A3_NONBLANK_CELLS_VISUALLY_VERIFIED',uncertainty_kind='NO_TABLE_A3_PER_CELL_ERROR_COLUMN;method_difference_not_statistical_error')
# ScienceDB: complete literal nonblank cells; each dependent series uses its own energy column.
gridchecks=[]
for id,x in D.items():
 if not id.startswith('D-LIU24'):continue
 rows=list(csv.reader((R/x['path']).read_text(encoding='utf-8-sig').splitlines()));header=rows[0]
 for group in x['energy_grid_groups']:
  ec=group['energy_column_index_zero_based'];tokens=[]
  for lineno,row in enumerate(rows[1:],2):
   e=row[ec] if ec<len(row) else ''
   if not e:continue
   Decimal(e);tokens.append(e)
   for col in group['observable_column_indices_zero_based']:
    val=row[col] if col<len(row) else ''
    if not val:continue
    Decimal(val)
    add(id,table='RAW_CSV',source_row=lineno,source_column=f'{col+1}:{header[col]}',energy_token=e,energy_unit=x['energy_units'],energy_frame='NOT_EXPLICIT_IN_RAW_CSV;NO_FRAME_CONVERSION',target_initial_state=x['target_initial_state'],final_state=x['final_center']+':'+header[col],observable=x['observable_definition'],value_token=val,cross_section_unit='UNRESOLVED_NOT_EXPLICIT_IN_RAW_METADATA',method='Liu2024 AOCC;3-basis mean in paperEq9;raw file no basis columns',uncertainty_kind='NO_UNCERTAINTY_COLUMN_IN_RAW_CSV',transcription_status='ALL_LITERAL_NONBLANK_RAW_CSV_CELLS_AND_ASSOCIATED_ENERGY_COLUMNS_VERIFIED',benchmark_admission='BLOCKED_UNIT_AND_FRAME_SEMANTICS;G1_NOT_AUTHORIZED')
  gridchecks.append({'source_id':id,'energy_column_zero_based':ec,'observable_columns_zero_based':group['observable_column_indices_zero_based'],'native_tokens':tokens,'exact_decimal_5_present':any(Decimal(e)==Decimal('5.0') for e in tokens),'exact_decimal_0_5_present':any(Decimal(e)==Decimal('0.5') for e in tokens)})
assert all(not d['exact_decimal_5_present'] and not d['exact_decimal_0_5_present'] for d in gridchecks)
dump('SCIENCEDB_EXACT_GRID_CHECK.json',{'status':'IMPLEMENTATION_VERIFIED','comparison':'Decimal equality within same printed keV/u unit; no interpolation or frame conversion','grids':gridchecks,'historical_R10N':'NEW_AUTHORITY_NOT_COMPARABLE remains valid specifically for ScienceDB H1s capture exact5keV/u request'})
# Supplemental verified native P08 table cells are merged when available; numeric values remain native20keV.
extra=W/'metadata_review/p07p08/P08_verified_cells.json'
if extra.exists():
 data=json.load(open(extra));dump('P08_VERIFIED_NATIVE_CELLS.json',data)
writecsv('EXACT_SOURCE_CELLS.csv',cells)
dump('CELL_COUNTS.json',{'total':len(cells),'by_source':{i:sum(c['source_id']==i for c in cells) for i in sorted(set(c['source_id'] for c in cells))},'cross_section_calculation':'NOT_RUN;source transcription only'})
# Rich source-method descriptions retain unresolved fields rather than guessing.
matrix=[]
def mr(id,**k):
 x=P.get(id,D.get(id));b={'source_id':id,'doi':x.get('doi',x.get('dataset_doi','')),'source_sha256':x['sha256'],'source_class':x['status'],'projectile':'He2+','isotope':'UNRESOLVED_NOT_EXPLICIT','target_initial_state':'H(1s)','final_shell_subshell':'','native_axis':'','energy_frame':'UNRESOLVED','method':'','basis_channel_count':'','continuum':'','trajectory':'','reported_uncertainty':'','exact_5_keV_u':'UNRESOLVED','exact_0_5_keV_u':'UNRESOLVED','table_page_evidence':'','machine_readable_status':'','benchmark_admission':'SCOPED_AUTHORITY_ONLY;G1_NOT_AUTHORIZED','unresolved':''};b.update(k);matrix.append(b)
mr('P03',final_shell_subshell='native n2 charge-transfer total;no n1 column',native_axis='Ec.m.(eV):20,50,100,200,600,1000,1600,2000,4000',energy_frame='center_of_mass',method='HSCC fully quantum three-body coordinates',basis_channel_count='four asymptotic channels:incoming H1s + three He+(n2) channels',continuum='not included in four-channel calculation',trajectory='quantum nuclear partial waves;no prescribed classical trajectory',reported_uncertainty='none per TableII cell;higher-energy channel expansion identified by authors as future convergence test',exact_5_keV_u='NO_NATIVE_KEVU_ROW;4000eV_c.m. not admitted as exact5keV/u',exact_0_5_keV_u='NO_NATIVE_KEVU_ROW;no frame/mass conversion performed',table_page_evidence='TableII PDF9/printed052705-9;SectionIV PDF8',machine_readable_status='9_HSCC_CELLS_VERIFIED',unresolved='isotope/mass adapter;channel-truncated n2 result must not stand for n1/complete-total capture')
mr('P09',target_initial_state='H1s,H2s extracted;other initial states remain in PDF',final_shell_subshell='native He+1s..5g in Tables25-30;no new shell sums',native_axis='v(a.u.)=0.2,0.4,0.6,0.8,1,1.2,1.4,1.6,1.8,2',energy_frame='relative impact velocity;target-rest representation;native tables are velocity not energy',method='two-center AOCC;source mean of two GTO basis calculations',basis_channel_count='B1=15s12p9d6f3g;B2=16s13p10d7f4g;bound n<=5;all eigenstates below2a.u.',continuum='120–200 pseudo-continuum states depending on system/basis;both centers',trajectory='straight line R=b+vt;PDF2',reported_uncertainty='epsilon=abs(sigma_B1-sigma_B2)/sigma_average Eq9;dimensionless convergence estimate,not SD',exact_5_keV_u='NO_NATIVE_ENERGY_TOKEN;velocity-to-keV/u adapter NOT_RUN',exact_0_5_keV_u='NO_NATIVE_ENERGY_TOKEN;velocity-to-keV/u adapter NOT_RUN',table_page_evidence='Tables25-26 PDF10;Tables27-30 PDF11;methods Eq8/9 and TableA PDF3',machine_readable_status='300_VALUE_CELLS_PLUS300_CONVERGENCE_TOKENS_VERIFIED;remaining108tables NOT_TRANSCRIBED',unresolved='complete114table extraction not done;isotope not assigned;nativevelocity retained;IAEA proton files excluded from He2+ authority')
for id,x in D.items():
 if id.startswith('D-LIU24'):
  mr(id,target_initial_state=x['target_initial_state'],final_shell_subshell=json.dumps(x['final_shell_subshell_resolution'],ensure_ascii=False),native_axis='keV/u;separate source-native grids per SCIENCEDB_EXACT_GRID_CHECK',energy_frame='UNRESOLVED_NOT_EXPLICIT_IN_RAW_CSV',method='AOCC;related P01 Eq9 averages3 GTO bases',basis_channel_count='P01 B1=17s14p11d8f5g/B2=18s15p12d9f6g/B3=19s16p13d10f7g;554/624/693 totalreactionchannels',continuum='P01 L2 GTO pseudostates bothcenters;200–300 described in paperPDF3',trajectory='P01 straight line R=b+vt PDF2',reported_uncertainty='no raw uncertainty columns;no Gaussian error assigned',exact_5_keV_u='ABSENT_ALL_RELEVANT_NATIVE_ENERGY_COLUMNS',exact_0_5_keV_u='ABSENT_ALL_RELEVANT_NATIVE_ENERGY_COLUMNS',table_page_evidence='rawCSV exactline/column preserved in cellCSV;P01 PDF2–4 method only',machine_readable_status='ALL_NONBLANK_CELLS_TRANSCRIBED_LITERAL;UNITS_AND_FRAME_UNRESOLVED',benchmark_admission='BLOCKED_UNIT_AND_FRAME_SEMANTICS;requested_rows_absent',unresolved='sigma units absent in rawCSV/distribution metadata;no inference from plotted scale')
 else:
  mr(id,projectile='H+;not He2+',target_initial_state=x['target_initial_state'],final_shell_subshell=str(x['final_shell_subshell_resolution']),native_axis='eV/u:1000,4000,9000,16000,25000,36000,49000,64000,81000,100000',energy_frame='not explicit in curator raw metadata',method='curator AOCC data for proton collision',basis_channel_count='see relatedP09;not a He2+ source',continuum='see relatedP09;not evaluated here',trajectory='see relatedP09',reported_uncertainty='curator sigma:uncertainty;basis convergence estimate',exact_5_keV_u='ABSENT;WRONG_PROJECTILE',exact_0_5_keV_u='ABSENT;WRONG_PROJECTILE',table_page_evidence=x['path'],machine_readable_status='RAW_ALREADY_RECOVERED;NOT_IMPORTED_AS_HE2_CELLS',benchmark_admission='EXCLUDED_WRONG_PROJECTILE',unresolved='not relevant to He2+ benchmark')
# Later append independent metadata review rows without losing provenance.
dump('_MATRIX_BASE.json',matrix)
writecsv('BENCHMARK_MATRIX.csv',matrix)
err={'schema':'B1_SOURCE_RECOVERY_ERRATA_v1','source_id':'P04','classification':'IMPLEMENTATION_ERROR_TABLE_HEADER_INDEX_FALSE_NEGATIVE','supersedes_archive_sha256':'0f9dc51cc013aa0b91e7f3ff560bbca5afd1ee1551b67c8bb33278c445b1cd84','supersedes_file':'NUMERICAL_MATERIAL_GAPS.json','supersedes_entry_id':'P04_NUMERICAL_MATERIAL','prior_statement':json.load(open(R/'NUMERICAL_MATERIAL_GAPS.json'))[0],'correction':'Published PDF contains Appendix Tables A1–A12;TableA3 explicitly supplies 5keV/u capture cells. Absence of detected numbered headers did not establish absence of tables. Letter-prefixed Appendix labels were missed in the previous indexing.','established_now':{'embedded_tables':'PRESENT','table_A3_cells':'VERIFIED','standalone_author_raw_file':'NOT_ACQUIRED;unchanged','complete_A1_A12_transcription':'NOT_RUN;onlyA3 is fully transcribed here'},'preservation':'Immutable v3 untouched;old statement preserved here and in v3','claim_withdrawn':'Any reading of old numerical-material gap as no published numeric table/5keV/u authority','scientific_gate_change':'NONE'}
dump('SOURCE_RECOVERY_ERRATA.json',err)
dump('CONTRACT.json',{'node':'B1 PRIMARY_NUMERIC_AUTHORITY_COMPLETION','precise_question':'Which recovered primary sources contain exact native 5.0keV/u and0.5keV/u numeric cells, with unambiguous observable and numerical-authority metadata?','bounded_scope':['P03','P04','P07','P08','P09','P10','P22','4 ScienceDB raw files','2 IAEA proton exports exclusion check'],'not_permitted':['interpolation','curve digitization','unstated frame/isotope conversion','new subshell sums','solver tuning','cross-section calculation','production change'],'completeness_definition':'Source availability/metadata matrix may contain unresolved fields. No claim of global benchmark-authority closure until gaps and required cells reviewed.','host_model':'GPT-6','model_specific_harness':'NOT_LOADED;genericGPT6 absent from canonical router','governing_contract':'user supplied bounded research-loop instructions'})
dump('CONVENTIONS.json',{'metric':'not applicable to source transcription','units':'source-native percell;no automatic conversions','exponent_brackets':'P03 a[b] means a*10^b as source caption states','zero_vs_missing':'blank source cell omitted from numericCSV,not zero','source_shell_totals':'only source printed shell/total rows;no new sums','uncertainty':'source-convergence diagnostics separate from statistical sigma and method spread','native_velocity':'P09 v(a.u.) retained;never relabelled keV/u','energy_equivalence':'requires explicit source-supported adapter and mass/isotope convention;not silently applied'})
dump('EQUATION_MANIFEST.json',[{'id':'P09_Eq8','pdf_page':3,'equation':'sigma_avg=(sigma_B1+sigma_B2)/2','status':'LITERATURE_SUPPORTED;author definition,not recomputed'},{'id':'P09_Eq9','pdf_page':3,'equation':'epsilon=abs(sigma_B1-sigma_B2)/sigma_avg','status':'LITERATURE_SUPPORTED;not a statistical standard deviation'},{'id':'P01_Eq9','pdf_page':4,'equation':'sigma_present=(sigma_B1+sigma_B2+sigma_B3)/3','status':'LITERATURE_SUPPORTED;no new basis averaging executed'}])
dump('NOT_RUN.json',{'scientific':['cross_section_solver','Eq55','fit','benchmark discriminationG1','interpolation','plot digitization','shell aggregation','unstatedframe conversion','velocity-energy conversion','theory numerical error estimation'],'data':['full P09 114table extraction','fullP04 A1-A12 extraction','new network source recovery','ScienceDB source-author unit clarification'],'production':['default change','gate promotion','Gitmutation','cloudmutation']})
(O/'evidence').mkdir(exist_ok=True)
for f in [W/'P09_cross_parser_check.json',W/'metadata_review/P04_A3_verified_cells.json']+[W/f'P09_table{t}.json' for t in range(25,31)]:shutil.copyfile(f,O/'evidence'/f.name)
for f in [W/'P03_p9.png',W/'P09_p10.png',W/'P09_p11.png',W/'metadata_review/P04_page8.png',W/'metadata_review/P04_page11.png']:
 shutil.copyfile(f,O/'evidence'/f.name)
dump('CODE_IDENTITY.json',{'script':'build_b1.py','sha256':sha(Path(__file__)),'execution_kind':'source extraction and metadata packaging only;not physical simulation'})
print(json.dumps({'output':str(O),'cells':len(cells),'matrix_base_rows':len(matrix),'source_hashes_verified':len(source_ids)}))
