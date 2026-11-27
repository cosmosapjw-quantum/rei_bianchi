#!/usr/bin/env python3
"""Transcribe printed measured photonuclear table facts; do not evaluate rates."""
from pathlib import Path
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
PUBLIC = BASE/'public'
PUBLIC.mkdir(exist_ok=False)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, value):
    (PUBLIC/name).open('x', encoding='utf-8').write(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

receipts = json.loads((BASE/'FETCH_RECEIPT_01.json').read_text())['rows']
rows = []
parse_checks = []

def make(source, target, family, channel, points, text, pos, page, eqs):
    source_rec = next(x for x in receipts if source in x['path'])
    r = {
        'id': source+'_He4_gamma_'+channel+'_TABLE_II',
        'record_class': 'PRIMARY_SOURCE_ROW',
        'source_kind': 'DIRECT_EXPERIMENTAL_PHOTONUCLEAR_MEASUREMENT',
        'source_coverage': 'EXCLUSIVE_SPECTRUM_AVERAGED_MEASUREMENT',
        'source_is_named_exclusive_channel': True,
        'exclusive_channel_binding': False,
        'family_ids': [family], 'target_ids': [target],
        'direction': 'family_reverse', 'target_directions': {str(target): 'target_forward'},
        'source_url': source_rec['url'], 'source_file': source_rec['path'],
        'source_SHA256': source_rec['sha256'], 'source_bytes': source_rec['bytes'],
        'locator': {'table': 'II', 'pdf_page_1based': page,
                    'private_derived_text_SHA256': source_rec['text_sha256'],
                    'table_text_char_start': pos,
                    'column': 'He4(gamma,'+channel+')',
                    'averaging_definitions': eqs},
        'raw_values': {'native_measurement_count': len(points), 'measurements': points},
        'units': {'mean_photon_energy': 'MeV', 'maximum_photon_energy': 'MeV',
                  'spectrum_averaged_cross_section': 'mb', 'cross_section_uncertainty': 'mb'},
        'support': {
            'incident_beam': 'quasi-monoenergetic laser-Compton-scattering photons',
            'target': 'He4 gas active target time-projection chamber',
            'observable': 'source-published beam-spectrum-averaged channel cross section',
            'mean_energy_is_not_delta_function_photon_energy': True,
            'native_beam_maximums_MeV': [x['beam_maximum_photon_energy_MeV'] for x in points],
            'native_mean_photon_energies_MeV': [x['mean_photon_energy_MeV'] for x in points],
            'numeric_beam_spectrum_payload': None,
            'beam_spectrum_source': 'Full beam-profile definitions in the cited source; no digitization or numerical profile reconstruction performed',
            'monoenergetic_sigma_E_grid_supplied': False,
            'interpolation_or_extrapolation_performed': False,
            'fit_or_cross_dataset_average_performed': False,
            'inverse_capture_inference_performed': False},
        'uncertainty': {
            'statistical': 'Per-native-row symmetric magnitude retained',
            'systematic': 'Per-native-row plus and minus magnitudes retained separately',
            'joint_covariance': None, 'confidence_probability': None,
            'between_dataset_discrepancy': 'Shima2005 and Murata2023 are separate inactive alternatives; neither is selected or averaged here'},
        'branch': {'observed_channel': 'He4(gamma,'+channel+')'+('He3' if target==4 else 'T'),
                   'branch_fraction': None, 'total_absorption_branch_normalization': None,
                   'total_photon_multiplicity': None},
        'Q': None,
        'state_resolution': {'isotopes': 'source explicitly identifiesHe4 andHe3/T plusn/p',
                             'nuclear_isomer': 'NOT_SEPARATELY_QUALIFIED',
                             'electronic_daughter_state': 'UNRESOLVED',
                             'ionic_population_binding': 'UNRESOLVED'},
        'selection_status': 'INDEPENDENT_INACTIVE_SOURCE_ALTERNATIVE',
        'default_active': False, 'new_rate_admission': False, 'new_Q_admission': False,
        'source_value_evaluated_in_this_intake': False,
        'publication_source_availability': {
            'original_bytes_bundled': False,
            'reason': 'No general full-paper redistribution grant established; public packet contains only numerical facts/locators/identities',
            'restore': 'Fetch exactsourceURL and verifyoriginalSHA256; no scientific recomputation'}}
    rows.append(r)
    return r

s = (BASE/'private_text/Shima2005_nucl-ex0509017.txt').read_text()
a = s.index('TABLE II:')
block = s[a:].split('\f',1)[0]
pat = re.compile(r'^\s*(\d+\.\d+)\s+(\d+\.\d+)±(\d+\.\d+)±(\d+\.\d+)\s+(\d+\.\d+)±(\d+\.\d+)±(\d+\.\d+)')
matched = [(n,pat.match(line)) for n,line in enumerate(block.splitlines(),1) if pat.match(line)]
assert len(matched)==4
energies = ['21.8','24.3','26.5','29.8']
maxima = ['22.3','25','28','32']
for target,family,channel,offset in [(4,'he3_n_gamma','n',4),(5,'p_t_gamma','p',1)]:
    pts=[]
    for i,(line_no,m) in enumerate(matched):
        v=m.groups();assert v[0]==energies[i]
        pts.append({'source_row_1based':i+1,'source_table_text_line_1based':line_no,
                    'beam_index_k_source':str(i),
                    'beam_maximum_photon_energy_MeV':maxima[i],
                    'mean_photon_energy_MeV':v[0],
                    'spectrum_averaged_sigma_mb':v[offset],
                    'statistical_plus_minus_mb':v[offset+1],
                    'systematic_plus_mb':v[offset+2],
                    'systematic_minus_mb':v[offset+2]})
    r=make('Shima2005',target,family,channel,pts,s,a,15,'sourceEqs2–3 and6; beammaxima inSecII.B andEq6')
    r['support']['beam_half_width_at_maximum_32MeV_MeV']='2.5'
    r['support']['maximum_energy_calibration_accuracy']='betterthan1percent, asreported'
    r['support']['same_reported_mean_energies_for_n_and_p']='source approximates their difference as within100keV'
    r['Q']={'source_printed_value_MeV':'-20.58' if target==4 else '-19.81',
            'source_table':'I','source_pdf_page_1based':7,'uncertainty':None,
            'status':'SOURCE_TABLE_Q_ONLY_NOT_NEW_IONIC_Q_ADMISSION',
            'ionic_mass_convention_qualified':False}
parse_checks.append({'source':'Shima2005','status':'PASS','source_table_rows':4,
                     'selected_channel_measurements':8,'regex_fields_bound':True})

s=(BASE/'private_text/Murata2023_2307.01474.txt').read_text()
a=s.index('TABLE II.')
block=s[a:].split('\f',1)[0]
matched=[]
for n,line in enumerate(block.splitlines(),1):
    if not re.match(r'^\s*[1-6]\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+±',line):
        continue
    v=re.findall(r'\d+(?:\.\d+)?',line)
    assert len(v)==12,(len(v),line)
    matched.append((n,v))
assert len(matched)==6 and [x[1][0] for x in matched]==['1','2','3','4','5','6']
for target,family,channel,offset in [(4,'he3_n_gamma','n',2),(5,'p_t_gamma','p',7)]:
    pts=[]
    for line_no,v in matched:
        pts.append({'source_row_1based':int(v[0]),'source_table_text_line_1based':line_no,
                    'beam_index_k_source':v[0], 'beam_maximum_photon_energy_MeV':v[1],
                    'mean_photon_energy_MeV':v[offset],
                    'spectrum_averaged_sigma_mb':v[offset+1],
                    'statistical_plus_minus_mb':v[offset+2],
                    'systematic_plus_mb':v[offset+3],
                    'systematic_minus_mb':v[offset+4]})
    r=make('Murata2023',target,family,channel,pts,s,a,9,'sourceEqs3–12, especially meanenergy Eq9; beamsettingsTableI')
    r['support']['native_beam_profile_domain']='Source f_k(E) is normalized over0..Emax,k; exactprofile is not tabulated in this packet'
    r['support']['angular_acceptance_correction']='SourceEq10–12 model-dependent correction to4pi; statistical and systematic uncertainties retained separately'
    r['support']['channel_dependent_mean_energies_preserved']=True
parse_checks.append({'source':'Murata2023','status':'PASS','source_table_rows':6,
                     'selected_channel_measurements':12,'separate_n_p_mean_energies':True,
                     'asymmetric_systematic_fields_separate':True})

assert len(rows)==4 and sum(r['raw_values']['native_measurement_count'] for r in rows)==20
write('PROVIDER_ROWS.json',{
    'schema':'WU_HE4_DIRECT_PHOTONUCLEAR_MEASUREMENTS_V1',
    'source_record_count':4,'native_selected_measurements':20,
    'coverage':'Direct named-channel measured spectrumaverages for originaltarget4 and5; no monoenergetic runtimebinding',
    'target6_direct_numeric_supplier':None,
    'no_new_rate_Q_or_reverse_calculation':True,
    'rows':rows})

write('SOURCE_CHAIN_AND_LICENSE.json',{
    'schema':'WU_HE4_PHOTON_SOURCE_CHAIN_V1',
    'connected_sources':[
      {'from':'Dubovichenko2019 arXiv1811.04779 reference11',
       'from_original_SHA256':'693da7cd228bd4189a31ab6007174cdb18931598a85ea83fc3ca4792184378fc',
       'to':'Shima2005 PhysRevC72,044004; arXivnucl-ex/0509017',
       'direction':'EXPLICIT_REFERENCE_IN_PREVIOUSLY_RECOVERED_PRIMARY_SOURCE'},
      {'from':'Murata2023 PhysRevC107,064317; arXiv2307.01474',
       'reference':32,'to':'Shima2005 PhysRevC72,044004',
       'direction':'NEW_PRIMARY_COMPARISON_SOURCE_EXPLICITLY_CITES_RECOVERED_SHIMA'}],
    'full_papers_in_public_packet':False,
    'observed_licenses':[
      {'source':'Shima2005','metadata_url':'https://arxiv.org/abs/nucl-ex/0509017',
       'view_license_target':'https://arxiv.org/licenses/assumed-1991-2003/license.html',
       'grant_scope':'Observed arXiv-assumed nonexclusive distribution, no generalCC grant asserted'},
      {'source':'Murata2023','metadata_url':'https://arxiv.org/abs/2307.01474',
       'view_license_target':'https://arxiv.org/licenses/nonexclusive-distrib/1.0/license.html',
       'grant_scope':'arXiv nonexclusive distribution, no generalCC grant asserted'}],
    'originals':[{'source_url':r['url'],'original_SHA256':r['sha256'],'original_bytes':r['bytes'],
                  'original_text_SHA256':r['text_sha256'],'original_bytes_bundled':False} for r in receipts]})

write('TARGET6_DEPENDENCY.json',{
    'schema':'WU_HE4_GAMMA_DD_BOUNDED_DEPENDENCY_V1','target_id':6,
    'equation':'He4 + gamma -> D + D','direct_numeric_provider':None,
    'status':'INPUT_DEPENDENCY_UNRESOLVED_AFTER_BOUNDED_DIRECT_SOURCE_CHECK',
    'observations':[
      {'source':'Shima2005','locator':'SecIII.A(iii), PDFpp7–8',
       'finding':'No candidate event is reported for this channel; no usable quantified upperlimit with confidence/exposure is provided in the selected statement',
       'numeric_zero_assigned':False,'upper_limit_assigned':False,
       'secondary_peak_mention':'About3.2microbarn near29MeV is cited toref37; not imported as a primary measurement'},
      {'source':'Shima2005 reference37','items':[
         'Weller andLehman, AnnualReviewNuclearParticleScience38,563(1988)',
         'Bluge,Assenbaum,Langanke,PhysRevC36,21(1987)',
         'Assenbaum,Langanke,PhysRevC36,17(1987)',
         'Wachter,Mertelmeier,Hofmann,PhysLettB200,246(1988)'],
       'finding':'Reference is a review/theory group, including inverse radiativecapture model papers; no retrieved primary gamma,dd numerical table'},
      {'source_url':'https://journals.aps.org/prc/abstract/10.1103/PhysRevC.36.21',
       'observed_title':'Potential model analysis of low energy2H(d,gamma)4He fusiondata',
       'access':'Abstract accessible; fulltext authorizationrequired','direct_gamma_data_imported':False},
      {'source_url':'https://journals.aps.org/prc/abstract/10.1103/PhysRevC.36.17',
       'observed_title':'Low-energy2H(d,gamma)4He reaction andD-state admixture',
       'access':'Abstract accessible; fulltext authorizationrequired','direct_gamma_data_imported':False},
      {'source_url':'https://journals.aps.org/prc/abstract/10.1103/PhysRevC.61.064612',
       'observed_title':'Two-deuteron photodisintegration of4He at150–250MeV',
       'available_metadata':{'photon_energy_bins_MeV':[['150','190'],['190','250']],'angles':6},
       'access':'Direct experimental paper identified; public abstract has no numericalcrosssections; fulltext authorizationrequired',
       'direct_numeric_rows_recovered':0},
      {'source':'OfficialEXFOR andHokkaido mirror','receipt':'EXFOR_INTERFACE_RECEIPT.json',
       'finding':'IAEA landingpage200 but linked normalform scripts403; Hokkaido interface503. No EXFORentry rows retrieved; this is access evidence, not absenceofdata'}],
    'needed_next':'Exact primary numericalgamma,dd data with units/support/angularorenergyaveraging/uncertainty or authenticated providerexport; do not infer from inversecapture or graphs',
    'figure_digitizations':0,'inverse_inferences':0,'new_rate_Q_admission':False})

for name in ['FETCH_RECEIPT_01.json','EXFOR_INTERFACE_RECEIPT.json','EXFOR_SCRIPT_RECEIPT.json']:
    (PUBLIC/name).open('xb').write((BASE/name).read_bytes())
(PUBLIC/'extract_public.py').open('xb').write(Path(__file__).read_bytes())
write('TRANSCRIPTION_CHECK.json',{'schema':'WU_HE4_PRINTED_TABLE_TRANSCRIPTION_CHECK_V1',
    'status':'PASS','checks':parse_checks,'source_records':4,'native_measurements':20,
    'full_private_source_hashes_verified':[sha(BASE/r['path'])==r['sha256'] for r in receipts],
    'rate_Q_IVP_executions':0,'old_validation_suite_replays':0,
    'source_retrieval_preparation_CPU_s':None,'unmeasured_is_not_zero':True})
files=[{'path':str(p.relative_to(PUBLIC)),'bytes':p.stat().st_size,'sha256':sha(p)}
       for p in sorted(PUBLIC.rglob('*')) if p.is_file()]
write('MANIFEST.json',{'schema':'WU_HE4_PHOTON_PUBLIC_SUPPLEMENT_MANIFEST_V1',
    'frozen':True,'files':files,'file_count_excluding_manifest':len(files),
    'source_count':4,'measurement_count':20,
    'PROVIDER_ROWS_sha256':sha(PUBLIC/'PROVIDER_ROWS.json'),
    'private_full_papers_excluded':True,
    'prior_R1_and_frozen_primary_packets_unchanged':True})
print(json.dumps({'PROVIDER_ROWS_sha256':sha(PUBLIC/'PROVIDER_ROWS.json'),
                  'MANIFEST_sha256':sha(PUBLIC/'MANIFEST.json'),
                  'source_records':4,'native_measurements':20,
                  'target6_direct_numeric_supplier':None},indent=2))
