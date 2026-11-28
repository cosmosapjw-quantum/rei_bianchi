"""Independent source and exact-integer audit; no imports of assembly/scientific kernels.

The adapter is imported only for deliberate black-box rejection/key tests after
independent recomputation of all saved event columns from the exported records.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import argparse,csv,gzip,hashlib,importlib.util,json,sys,time,resource

p=argparse.ArgumentParser()
p.add_argument('--registry-root',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args(); base=a.registry_root
if a.output.exists(): raise SystemExit('INDEPENDENT_OUTPUT_EXISTS_NO_REPLAY')
start=time.monotonic(); cpu0=time.process_time();checks=[];failures=[]
def rb(path):
 path=Path(path)
 return path.read_bytes() if path.exists() else gzip.decompress(Path(str(path)+'.gz').read_bytes())
def rj(path):return json.loads(rb(path))
def hs(b):return hashlib.sha256(b).hexdigest()
def dh(obj):return hs(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def check(category,name,condition,detail=None):
 row={'category':category,'name':name,'passed':bool(condition)}
 if detail is not None:row['detail']=detail
 checks.append(row)
 if not condition:failures.append(row)
def unchanged_manifest():
 paths=[base/'registry'/f for f in ('species.json','providers.json','events.json','compiled.json','coverage.json')]+[base/'registry_adapter.py',base/'build_registry.py',base/'CONTRACT.json',base.parent/'rei_chem_ledger_20261025/chem_ledger.py']
 return {str(x.relative_to(base.parent)):hs(x.read_bytes()) for x in paths}
initial=unchanged_manifest()
compiler=base.parent/'rei_chem_ledger_20261025/chem_ledger.py'
check('immutable_reuse','compiler_source_sha',hs(compiler.read_bytes())=='60a502895266b6feb96964abc4b24db61c2faed2344db0f7d12f16bb47ed62af')
reg=base/'registry';sp=rj(reg/'species.json');prov=rj(reg/'providers.json');ev=rj(reg/'events.json')['rows'];co=rj(reg/'compiled.json')['rows'];cv=rj(reg/'coverage.json')
species=sp['rows'];providers=prov['rows'];compiled={r['event_id']:r for r in co};byevent={r['id']:r for r in ev}
check('identity','unique_event_and_compiled_ids',len(ev)==len(byevent)==len(co)==len(compiled) and set(compiled)==set(byevent))
check('identity','unique_material_species_keys',len({dh(v['compiler_record']) for v in species.values()})==len(species))
check('phase_counts','historical21_not_extended_material_count',len(sp['historical_view'])==21 and cv['historical_population_count']==21 and len(species)>21)
check('phase_counts','historical39_and_missing_CI10',len(cv['historical_direction_cells'])==39 and cv['historical_directions_with_source']==29 and len(cv['missing_CI_source_directions'])==10)
check('phase_counts','no_activation_or_global_completion',cv['active_new_rates']==0 and cv['new_physical_Q_approvals']==0 and cv['old_249_checks_replayed']==0 and cv['global_physical_completion'] is None and cv['HH_R10']=='OFF' and cv['production']=='NOT_ISSUED')
# Resolve exact source rows independently using the new structured selector.
for pid,r in providers.items():
 ref=r['payload_ref'];doc=rj(base/ref['file']);container=ref['container']
 rows=doc if container is None else doc[container]
 if container is None: selected=rows
 else:
  matches=[v for v in rows if all(v.get(k)==v0 for k,v0 in ref['match'].items())]
  check('source_locator',pid,len(matches)==1)
  if len(matches)!=1:continue
  selected=matches[0]
 raw=r['native_record']
 same=raw==selected or raw.get('row')==selected or raw.get('stored_result')==selected
 if pid=='LEIDEN_LiH_PD':same=raw=={k:v for k,v in selected.items() if k!='points'}
 check('source_identity',pid,same and dh(raw)==r['record_sha256'] and r['new_empirical_rate_admission'] is False and r['new_nuclear_Q_admission'] is False)
# Every saved column recomputed without the frozen compiler or its adapter.
external={'gamma:incident':(0,0,0),'gamma:escaping':(0,0,0),'nu_e:escaping':(0,0,1),'antinu_e:escaping':(0,0,-1),'cosmic_ray_field':(0,0,0),'CR_induced_UV_field':(0,0,0)}
for e in ev:
 n=Counter();valid=True
 for sign,side in ((-1,e['reactants']),(1,e['products'])):
  for sid,k in side:
   valid &= sid in species and type(k) is int and k>0
   n[sid]+=sign*k
 n={sid:k for sid,k in n.items() if k}
 isotopes=Counter();b=q=l=0
 for sid,k in n.items():
  s=species[sid]['compiler_record'];zsum=0
  for c in s['composition']:
   key=(c['Z'],c['A'],c['isomer']);isotopes[key]+=k*c['count'];b+=k*c['A']*c['count'];zsum+=c['Z']*c['count']
  q+=k*s['charge'];l+=k*(zsum-s['charge'])
 for sign,side in ((-1,e['external_reactants']),(1,e['external_products'])):
  for label,k in side:
   valid &= label in external and type(k) is int and k>0
   xb,xq,xl=external[label];b+=sign*k*xb;q+=sign*k*xq;l+=sign*k*xl
 stored=compiled[e['id']]
 expected_iso={str(k):v for k,v in sorted(isotopes.items())}
 invariant=not(b or q or l) and (e['kind']=='nuclear' or not any(isotopes.values()))
 identities=(stored['stoichiometry']==n and stored['isotope_delta']==expected_iso and stored['baryon_delta']==b and stored['charge_delta']==q and stored['electron_lepton_delta']==l)
 limits=(e['activation'] is False and e['empirical_rate_admitted'] is False and e['nuclear_Q_admitted'] is False and e['rate_normalization_bound'] is False and e['consumer_ACK'] is None and stored['energy_status']=='UNQUALIFIED:ENERGY' and stored['Q_approved'] is False and stored['native_rate_evaluated'] is False and stored['reverse_rate_inferred'] is False)
 sourceok=(e['source_id'] in providers and e['source_identity']==providers[e['source_id']]['record_sha256'])
 check('independent_event_columns',e['id'],valid and invariant and identities and limits and sourceok,{'baryon':b,'charge':q,'electron_lepton':l,'nuclear_isotope_changes':{k:v for k,v in expected_iso.items() if v} if e['kind']=='nuclear' else None})
# Source row inventory, not inferred from emitted counts.
src=base/'sources';atomic=rj(src/'atomic_nuclear/provider_rows.json');correction=rj(src/'atomic_nuclear_correction/CORRECTION_V1.json');umist=rj(src/'molecular/umist_light_provider_rows.json');hd=rj(src/'molecular/hd_provider_rows.json');lih=rj(src/'molecular/lih_photoprocess_provider.json');cold=rj(src/'atomic_nuclear/reused_cold_kinematic_rows.json');v97=rj(src/'voronov1997/SELECTED_ROWS.json')
expected=set(r['id'] for r in atomic['rows'] if r['id']!='VF96_RR_Z2_N2')|set(r['id'] for r in correction['corrected_source_rows'])|set('PHYS81_COLD_'+r['reaction'] for r in cold['rows'])|set('UMIST22_'+r['provider_row_id'] for r in umist['rows'])|{'LEIDEN_LiH_PD'}|set('LAMDA_HD_A_'+str(r['transition_id']) for r in hd['radiative_lines'])|set('LAMDA_HD_C_'+str(r['collider_id'])+'_'+str(r['transition_id']) for r in hd['collisions'])|set(r['id'] for r in v97['rows'])
check('phase_counts','provider_set_equals_source_rows',set(providers)==expected,{'expected_count':len(expected),'observed':len(providers),'missing':sorted(expected-set(providers)),'extra':sorted(set(providers)-expected)})
check('phase_counts','coverage_phase_counters_match_actual',cv['provider_variant_count']==len(providers) and cv['compiled_projection_count']==len(ev))
# The six source coefficients represent thirteen explicit isotope-blind model
# projections. The historical ten missing admissions remain missing admissions.
vraw=rb(src/'voronov1997/cfit.dat');vlines=vraw.decode().splitlines();vdoc=rb(src/'voronov1997/cfit.txt');vfortran=rb(src/'voronov1997/cfit.f').decode().lower()
for row in v97['rows']:
 line=vlines[row['source_line1']-1];z=int(line[6:8]);nel=int(line[9:11]);domain=row['native_temperature_domain']
 coeff={key:line[lo:hi].strip() for key,lo,hi in [('dE',12,19),('P',20,21),('A',22,31),('X',32,38),('K',39,43)]}
 exact=(row['raw_row']==line and row['raw_row_sha256_without_newline']==hs(line.encode()) and row['Z']==z and row['bound_electrons_lower_ion']==nel and row['charge_lower']==z-nel and row['coefficients']==coeff and row['source_sha256']==hs(vraw) and row['format_sha256']==hs(vdoc))
 semantics=(domain['Tmin']==line[44:48].strip() and domain['Tmin_unit']=='eV' and domain['Tmax']==line[49:53].strip() and domain['Tmax_unit']=='keV' and domain['variable']=='electron_temperature_as_energy_kB_T' and row['coefficient_units']['A']=='cm^3 s^-1' and row['dE_is_approved_chemical_Q'] is False and row['physical_admission'] is False and row['new_rate_evaluations']==0 and row['parameter_covariance'] is None)
 check('Voronov_raw',row['id'],exact and semantics)
v_events=[e for e in ev if e['source_id'].startswith('V97_CI_')]
check('Voronov_scope','six_elemental_rows_thirteen_inactive_projections',len(vlines)==v97['source_total_rows']==406 and len(v97['rows'])==cv['additional_CI_source_variants']==6 and len(v_events)==cv['additional_CI_candidate_projections']==13 and {(r['Z'],r['bound_electrons_lower_ion']) for r in v97['rows']}=={(1,1),(2,2),(2,1),(3,3),(3,2),(3,1)} and all('EXPLICIT_ISOTOPE_BLIND_CANDIDATE' in e['projection_qualification'] and e['native_Q_record']['chemical_Q_admission'] is False for e in v_events))
check('Voronov_scope','native_Fortran_cutoff_described_not_executed','te=t*8.617385e-05' in vfortran and 'if(u.gt.80.0)return' in vfortran and all(r['source_Fortran']['u_greater_80_returns_zero'] is True and r['source_Fortran']['cutoff_qualification']=='legacy numerical return rule, not measured physical zero' for r in v97['rows']))
check('Voronov_scope','all39_have_source_candidate_without_old_admission_rewrite',cv['historical_directions_with_any_sourced_candidate']==39 and cv['missing_any_sourced_candidate_directions']==[] and all(c.get('additional_source_candidates') and c['physical_full_rate_admission']=='NOT_ISSUED' for c in cv['historical_direction_cells'] if c['process']=='CI') and cv['historical_directions_with_source']==29 and len(cv['missing_CI_source_directions'])==10)
# Verify every recovered pinned Git input against its captured byte SHA.
for r in rj(src/'atomic_nuclear/GITHUB_INPUT_MANIFEST.json'):
 b0=rb(src/'atomic_nuclear'/r['local_path'])
 check('raw_github_file',r['path'],len(b0)==r['bytes'] and hs(b0)==r['sha256'])
# He I variants and scientific error meaning.
rr=rb(src/'atomic_nuclear_correction/rec_table1.dat').decode().splitlines()
for suffix,line,top,rms in [('a',2,'1000000','2.5'),('b',3,'10000000000','4.7')]:
 r=providers['VF96_RR_Z2_N2_fit_'+suffix]['native_record'];domain=r['temperature_fit_domain_K']
 check('HeI_variants',suffix,r['raw_row']==rr[line-1] and domain['lower']=='3' and domain['upper']==top and domain['lower_inclusive'] is False and domain['upper_inclusive'] is False and r['fit_residual_rms_percent']==rms and r['radiation_count']['total_emitted_photons_per_capture'] is None)
check('HeI_variants','legacy_alias_is_b',prov['aliases']['VF96_RR_Z2_N2']=='VF96_RR_Z2_N2_fit_b')
for nuc in ('He3','He4'):
 x,y=[compiled['VF96_RR_Z2_N2_fit_'+s+':'+nuc] for s in ('a','b')]
 check('ownership','HeI_alternatives_'+nuc,x['ownership_group_sha256']==y['ownership_group_sha256'])
rrcells=[x for x in cv['historical_direction_cells'] if x['process']=='RR']
check('RR_count','13_total_RR_directions_remain_unresolved',len(rrcells)==13 and all('gamma:escaping' not in c['products'] and c['total_photon_count'] is None for c in rrcells))
check('RR_count','compiled_total_RR_no_escape_count',all(not e['external_products'] and 'UNRESOLVED' in e['radiation_count_qualification'] for e in ev if e['source_id'].startswith('VF96_RR_')))
# UMIST exact rows and declared source conventions.
umraw=rb(src/'molecular/raw/rate22_final.rates').splitlines(keepends=True)
for row in umist['rows']:
 b0=umraw[row['provider_line']-1];parts=next(csv.reader([b0.decode()],delimiter=':',quotechar='"'));nfit=int(parts[8]);stored=row['fits_original_decimal_strings']
 expect=[dict(zip(('alpha','beta','gamma','Tmin_K','Tmax_K','method','accuracy_code','original_reference','notes'),parts[9+9*i:18+9*i])) for i in range(nfit)]
 check('UMIST_raw',row['provider_row_id'],b0.decode()==row['raw_row_utf8'] and hs(b0)==row['raw_row_sha256'] and expect==stored and row['rate_admission'] is False and row['Q_value'] is None)
r74=next(x for x in umist['rows'] if x['provider_row_id']=='74')
check('UMIST_domain','reaction74_unfilled_temperature_gap',[(x['Tmin_K'],x['Tmax_K']) for x in r74['fits_original_decimal_strings']]==[('10','100'),('101','3000')])
check('UMIST_source','isotope_specificity_not_inferred',all('elemental labels' in r['isotope_source_labels'] for r in umist['rows']) and all('NO_ISOTOPE_RATE_TRANSFER' in e['projection_qualification'] for e in ev if e['source_id'].startswith('UMIST22_')))
check('UMIST_source','gamma_not_Q_and_drivers_preserved',all(r['gamma_is_Q'] is False for r in umist['rows']) and any(e['external_reactants']==[['cosmic_ray_field',1]] for e in ev))
# HD exact retained line/collider source rows.
hdraw=rb(src/'molecular/raw/lamda_hd_20261025.dat').decode().splitlines()
for kind in ('levels','radiative_lines','collisions'):
 check('HD_raw',kind,all(hdraw[r['source_line']-1]==r['raw_line_utf8'] for r in hd[kind]),{'rows':len(hd[kind])})
check('HD_coverage','nine_levels_eight_lines_eighteen_pairs',len(hd['levels'])==9 and len(hd['radiative_lines'])==8 and len(hd['collisions'])==18)
for j in range(1,10):
 e2=byevent['LAMDA_HD_C_2_'+str(j)];e3=byevent['LAMDA_HD_C_3_'+str(j)]
 def catalyst(e):return set(s for s,n in e['reactants']) & set(s for s,n in e['products'])
 c2,c3=catalyst(e2),catalyst(e3)
 check('HD_spin','pair_'+str(j),len(c2)==len(c3)==1 and c2!=c3 and 'para_H2' in species[next(iter(c2))]['compiler_record']['state'] and 'ortho_H2' in species[next(iter(c3))]['compiler_record']['state'] and e2['native_rate_record']['T_K']==['50.0','100.0','200.0'])
# LiH actual samples preserved, no summary support extrapolation.
li_lines=rb(src/'molecular/raw/LiH.txt').splitlines(keepends=True)
liok=all(li_lines[r['source_line']-1].decode()==r['raw_line_utf8'] and hs(li_lines[r['source_line']-1])==r['raw_row_sha256'] and li_lines[r['source_line']-1].decode().split()==[r['wavelength_nm'],r['photoabsorption_cm2'],r['photodissociation_cm2'],r['photoionisation_cm2']] for r in lih['points'])
check('LiH_source','1562_exact_sample_rows',liok and len(lih['points'])==1562)
check('LiH_source','summary_threshold_and_sample_support_separate',lih['source_support_nm']==['91.2000000','351.1000000'] and lih['source_discrepancy']['summary_pd_threshold_nm']=='579' and lih['isotope']['Li'] is None and lih['isotope']['H'] is None and lih['Q_value'] is None)
# Independent full fixed-width catalogue binding; no mass/Q arithmetic.
nu_lines=rb(src/'atomic_nuclear/raw_external/nubase_4.mas20.txt').decode().splitlines();cat=[json.loads(line) for line in rb(src/'atomic_nuclear/nuclear_catalogue.jsonl').decode().splitlines()];data=[(i,s) for i,s in enumerate(nu_lines,1) if s and not s.startswith('#')]
cat_ok=len(cat)==len(data)
for r,(i,line) in zip(cat,data):
 cat_ok &= (r['raw_row']==line and r['source_line1']==i and r['A']==int(line[:3]) and r['Z']==int(line[4:7]) and r['provider_state_index']==int(line[7:8]) and r['provider_state_symbol']==line[16:17].strip() and r['mass_excess_keV']==line[18:31].strip() and r['mass_excess_uncertainty_keV']==line[31:42].strip() and r['branch_or_abundance_literal']==(line[119:209].strip() or None))
check('NUBASE_catalogue','all5843_fixed_width_rows',cat_ok and len(cat)==5843,{'ground':sum(r['provider_state_index']==0 for r in cat),'non_ground':sum(r['provider_state_index']!=0 for r in cat)})
check('NUBASE_catalogue','catalogue_not_active_network',cv['nuclear_catalogue_is_active_network'] is False and cv['all_non_ground_are_isomers'] is False and cv['all_configured_network_reactions_known'] is False)
for nuc in ('n','T'):
 e1=byevent['NUBASE2020_'+nuc+'_beta_minus'];e2=byevent['LiveChart_ENSDF_'+nuc+'_beta_minus']
 check('weak_alternatives',nuc,compiled[e1['id']]['ownership_group_sha256']==compiled[e2['id']]['ownership_group_sha256'] and ['antinu_e:escaping',1] in e1['external_products'] and e1['activation'] is False and e2['activation'] is False)
weakn=[providers['NUBASE2020_n_beta_minus']['native_record'],providers['LiveChart_ENSDF_n_beta_minus']['native_record']]
check('weak_source','neutron_lifetime_alternatives_not_averaged',[r['half_life_literal'] for r in weakn]==['609.8','613.9'])
for nuc in ('n','T'):
 r=providers['LiveChart_ENSDF_'+nuc+'_beta_minus']['native_record'];columns=r['beta_radiation_row_columns']
 check('weak_source','duplicate_uncertainty_columns_'+nuc,sum(x['name']=='unc_me' for x in columns)==2 and r['Q_standard_uncertainty_keV_literal']!=next(x['literal'] for x in columns if x['name']=='unc_q') and 'atomic ground-state mass difference' in r['Q_convention'])
endf=byevent['ENDF_B_VIII1_H1_MT102']
check('nuclear_Q_boundary','native_MT102_not_bare_Q',endf['native_Q_record']['atomic_to_bare_map']=='UNRESOLVED' and endf['nuclear_Q_admitted'] is False and compiled[endf['id']]['energy_status']=='UNQUALIFIED:ENERGY')
# Black-box tests: each is a new-input semantic control, not old synthetic suite.
sys.path.insert(0,str(base));import registry_adapter as adapter
mutations=[]
def rejection(name,event,expected):
 try:adapter.compile_event(event,species)
 except Exception as err:
  ok=expected in str(err);check('blackbox_rejection',name,ok,{'observed':type(err).__name__+':'+str(err),'expected_contains':expected})
 else:check('blackbox_rejection',name,False,{'observed':'ACCEPTED','expected_contains':expected})
n=deepcopy(byevent['NUBASE2020_n_beta_minus']);n['external_products']=[];rejection('weak_missing_antineutrino',n,'ELECTRON_LEPTON_NUMBER_NOT_CONSERVED')
n=deepcopy(byevent['NUBASE2020_n_beta_minus']);n['external_products']=[['nu_e:escaping',1]];rejection('weak_wrong_neutrino_sign',n,'ELECTRON_LEPTON_NUMBER_NOT_CONSERVED')
n=deepcopy(ev[0]);n['products'].append(['unknown_actual_species',1]);rejection('unknown_actual_species',n,'UNKNOWN_SPECIES')
n=deepcopy(ev[0]);n['activation']=True;rejection('attempted_activation',n,'CANNOT_ACTIVATE')
n=deepcopy(ev[0]);n['nuclear_Q_admitted']=True;rejection('attempted_Q_promotion',n,'CANNOT_ISSUE_PHYSICAL_ADMISSION')
n=deepcopy(byevent['CHIANTI_A_2s_two_photon_per_s']);same=deepcopy(n);same['external_products']=[['gamma:escaping',1],['gamma:escaping',1]]
x,y=adapter.compile_event(n,species),adapter.compile_event(same,species)
check('blackbox_identity','external_photon_split_representation',x['physical_event_key_sha256']==y['physical_event_key_sha256'] and x['ownership_group_sha256']==y['ownership_group_sha256'])
n=deepcopy(ev[0]);changed=deepcopy(n);changed['branch_id']='different_actual_branch'
check('blackbox_identity','branch_changes_identity',adapter.compile_event(n,species)['ownership_group_sha256']!=adapter.compile_event(changed,species)['ownership_group_sha256'])
for label,ids in [('He4_a_b',['VF96_RR_Z2_N2_fit_a:He4','VF96_RR_Z2_N2_fit_b:He4']),('neutron_evaluations',['NUBASE2020_n_beta_minus','LiveChart_ENSDF_n_beta_minus'])]:
 es=[deepcopy(byevent[s]) for s in ids]
 for e in es:e['activation']=True
 try:adapter.verify_active_ownership(es,co)
 except ValueError as err:check('blackbox_owner',label,'OWNER_OVERLAP_UNRESOLVED' in str(err),str(err))
 else:check('blackbox_owner',label,False,'two active alternatives accepted')
check('blackbox_domain','UMIST74_gap_100_5K_rejected',adapter.within_native_intervals('100.5',[('10','100'),('101','3000')]) is False)
check('frozen_inputs','unchanged_after_independent_review',initial==unchanged_manifest())
summary={'schema':'WU_SOURCE_REGISTRY_INDEPENDENT_C9_CHECK_V1','decision':'PASS_SCOPED_SOURCE_ROWS_AND_INTEGER_PROJECTIONS' if not failures else 'CHANGES_REQUIRED','checker_sha256':hs(Path(__file__).read_bytes()),'frozen_source_manifest':initial,'independent_method':'Direct raw-file/row/column parsing and integer ledgers; saved production output compared without importing assembler/core; adapter imported only for new-input rejection and key controls','counts':{'provider_variants':len(providers),'candidate_events':len(ev),'species_identities':len(species),'historical_configured_populations':len(sp['historical_view']),'nuclear_source_rows':len(cat),'checks':len(checks),'failed':len(failures),'checks_by_category':dict(Counter(r['category'] for r in checks))},'science_execution':{'rates':0,'Q_evaluations':0,'IVPs':0,'old249_replay':0,'new_exact_saved_columns':len(ev)},'cpu_s':time.process_time()-cpu0,'wall_s':time.monotonic()-start,'peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'checks':checks,'failures':failures,'admission_limit':'Actual source-row transcription and structural number projection only. No source statistical validation, physical rate/Q, source atomic-to-bare mapping or consumer adoption.'}
a.output.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ('decision','counts','cpu_s','wall_s','peak_RSS_KiB')},ensure_ascii=False))
if failures:print(json.dumps(failures,ensure_ascii=False));raise SystemExit(1)
