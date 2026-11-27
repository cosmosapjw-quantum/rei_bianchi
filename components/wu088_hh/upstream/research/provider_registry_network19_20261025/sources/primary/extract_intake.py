#!/usr/bin/env python3
"""Source transcription only: no rate, cross-section, reverse-rate, or Q evaluation."""
from pathlib import Path
from decimal import Decimal
import hashlib
import html
import json
import re
import shutil

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
R1 = ROOT / 'WU088_HH/research/provider_registry_20261025/registry'
PIN = '9620e1fcc4bdda76e0311206f614234926600381'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, value):
    p = BASE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.open('x', encoding='utf-8').write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def textloc(text, start, end):
    return {'text_char_start': start, 'text_char_end_exclusive': end,
            'text_line_start_1based': len(text[:start].splitlines()) + 1,
            'pdf_page_1based': text[:start].count('\f') + 1}

def extract_between(text, begin, end):
    a = text.index(begin)
    b = text.index(end, a) + len(end)
    return {'literal': text[a:b], **textloc(text, a, b)}

target_path = ROOT/'prior_archive_search/raw/TARGET_NETWORK_19_c9deb93.json'
conditional_path = ROOT/'prior_archive_search/raw/REI18_NUCLEAR_NETWORK_CONTRACT_9620e1f.json'
targets = json.loads(target_path.read_text())
conditional = json.loads(conditional_path.read_text())
families = {x['id']: x for x in conditional['families']}
photo_ids = {4, 5, 6, 7, 8, 11}
rows = []

def row(identifier, family, file, url, source_kind, locator):
    f = families[family]
    p = BASE/file
    r = {'id': identifier, 'record_class': 'PRIMARY_SOURCE_ROW',
         'source_kind': source_kind, 'family_ids': [family],
         'target_ids': f['dossier_ids'], 'direction': 'family_forward',
         'target_directions': {str(i): ('target_reverse' if i in photo_ids else 'target_forward')
                               for i in f['dossier_ids']},
         'source_url': url, 'source_file': file, 'source_SHA256': sha(p),
         'source_bytes': p.stat().st_size, 'locator': locator,
         'raw_values': {}, 'units': {}, 'support': {}, 'uncertainty': None,
         'Q': None, 'branch': {'status': 'CHANNEL_LABEL_ONLY_BRANCH_FRACTIONS_UNRESOLVED',
                              'branch_fraction': None, 'total_photon_multiplicity': None},
         'state_resolution': {'source_isotope_labels': 'EXPLICIT_NUCLIDES',
                              'isomer': 'NOT_RESOLVED_BY_SELECTED_ROW',
                              'ionic_charge': 'NOT_BOUND_TO_PROJECT_POPULATION',
                              'electronic_state': 'NOT_RESOLVED_BY_SELECTED_ROW'},
         'default_active': False, 'new_rate_admission': False, 'new_Q_admission': False,
         'primary_binding_qualification': 'FAMILY_AND_DIRECTION_ONLY; STATE_BRANCH_NOT_BOUND',
         'source_value_evaluated_in_this_intake': False}
    rows.append(r)
    return r

# Native source tables retain the source's printed numeric strings.  Sorting T9 is
# a transcription aid, not interpolation or evaluation of a scientific function.
nt_path = BASE/'derived_text/NACREII_1310.7099.txt'
nt = nt_path.read_text()
numeric = re.compile(r'[+−-]?\d+(?:\.\d*)?(?:E[+−-]?\d+)?\Z')
configs = [
    (2, '3.1', 'p_d_gamma', '0.21', '0.04', '0.04', 'eV b', '5.493',
     'The resulting S(0) = 0.21', 'eV b.', '0.0025', 'PM', '0.1'),
    (3, '3.2', 'd_d_gamma', '5.8', '1.5', '1.0', 'meV b', '23.847',
     'The resulting S(0) = 5.8', 'meV b.', '0.007', 'PM', '0.2'),
    (4, '3.3', 'd_d_n', '55.5', '6.0', '6.0', 'keV b', '3.269',
     'The resulting S(0) = 55.5', 'keV b.', '0.002', 'DWBA', '0.1'),
    (5, '3.4', 'd_d_p', '56.2', '4.7', '4.9', 'keV b', '4.033',
     'The present S(0) = 56.2', 'keV b.', '0.0016', 'DWBA', '0.1'),
    (6, '3.5', 'd_alpha_gamma', '2.2', '1.2', '0.9', 'meV b', '1.474',
     'The present S(0) = 2.2', 'meV b.', '0.07', 'PM', '0.7'),
    (7, '3.6', 'd_t_n', '11', '1', '1', 'MeV b', '17.589',
     'The present S(0) = 11', 'MeV b.', '0.005', 'DWBA', '0.01'),
    (8, '3.7', 't_alpha_gamma', '98', '8', '11', 'eV b', '2.467',
     'The present S(0) = 98', 'eV b.', '0.05', 'PM', None),
    (9, '3.8', 'd_he3_p', '5.9', '0.5', '0.5', 'MeV b', '18.353',
     'The present S(0) = 5.9', 'MeV b.', '0.005', 'DWBA', '0.05'),
    (13, '3.12', 'p_li6_alpha', '3.1', '0.4', '0.4', 'MeV b', '4.020',
     'The present S(0) = 3.1', 'MeV b.', '0.01', 'DWBA', '0.1'),
    (15, '3.14', 'p_li7_alpha', '52', '8', '11', 'keV b', '17.347',
     'The present S(0) = 52', 'keV b.', '0.010', 'DWBA', '0.05'),
]
for table, section, family, central, minus, plus, unit, q, start_s, end_s, data_min, model, split in configs:
    ms = list(re.finditer(r'^\s*Table '+str(table)+r':[^\n]*', nt, re.M))
    assert len(ms) == 1, (table, len(ms))
    a = ms[0].start(); b = nt.index('REV =', a)
    block = nt[a:b]
    points = []
    for n, literal in enumerate(block.splitlines(), 1):
        tokens = literal.split()
        if len(tokens) not in (4, 8) or not all(numeric.fullmatch(x) for x in tokens):
            continue
        for side in range(len(tokens)//4):
            v = tokens[4*side:4*side+4]
            points.append({'T9': v[0], 'adopted': v[1], 'low': v[2], 'high': v[3],
                           'table_text_line_1based': n, 'column_group': side+1,
                           'raw_literal': literal})
    expected = 59 if table in (6, 8) else 60
    assert len(points) == expected, (table, len(points), expected)
    assert len({Decimal(x['T9']) for x in points}) == expected
    points.sort(key=lambda x: Decimal(x['T9']))
    s0 = extract_between(nt, start_s, end_s)
    sec_key = section.replace('.', r'\s*\.\s*')
    qm = re.search(r'^\s*'+sec_key+r'\s+[^\n]*\+\s+'+re.escape(q)+r'[^\n]*', nt, re.M)
    assert qm is not None, section
    r = row('NACREII2013_'+family+'_TABLE'+str(table), family,
            'raw_primary/NACREII_1310.7099.pdf', 'https://arxiv.org/pdf/1310.7099',
            'PRIMARY_PUBLISHED_NUCLEAR_RATE_EVALUATION',
            {'section': section, 'native_rate_table': table, **textloc(nt, a, b),
             'derived_text_file': str(nt_path.relative_to(BASE)), 'derived_text_SHA256': sha(nt_path),
             'S0_locator': {k:v for k,v in s0.items() if k != 'literal'},
             'Q_table': 1, 'Q_locator': textloc(nt, qm.start(), qm.end())})
    r['raw_values'] = {'S0_printed_central': central, 'S0_printed_literal': s0['literal'],
                       'native_rate_table_count': len(points), 'native_rate_table': points,
                       'native_table_literal': block}
    r['units'] = {'S0': unit, 'native_rate': 'cm^3 mol^-1 s^-1',
                  'native_rate_quantity': 'N_A <sigma v>', 'temperature': 'T9 = T/(10^9 K)',
                  'quoted_experimental_minimum_Ecm': 'MeV', 'Q': 'MeV'}
    r['support'] = {'native_T9_min': points[0]['T9'], 'native_T9_max': points[-1]['T9'],
                    'native_table_interpolation_performed': False,
                    'native_grid_overlaps_100_to_10000_K': False,
                    'S0_definition': 'Section3 intro: unless specified otherwise, nominal S(0) is at about0.5–1.0keV',
                    'experimental_data_reach_quoted_in_section_Ecm_min_MeV': data_min,
                    'low_energy_model': model,
                    'model_to_experimental_switch_Ecm_MeV': split,
                    'scope': 'Published model/evaluation and native rate table; not a new low-temperature or ionic-state admission'}
    r['uncertainty'] = {'S0_minus': minus, 'S0_plus': plus, 'unit': unit,
                        'native_rate_bounds': ['low', 'high'], 'covariance': None,
                        'confidence_probability': None,
                        'meaning': 'Published adopted/low/high evaluation boundaries; no99% or Gaussian distribution assigned'}
    r['Q'] = {'printed_value': '+'+q, 'unit': 'MeV', 'raw_literal': qm.group(0),
              'uncertainty': None, 'ionic_mass_convention_qualified': False,
              'status': 'SOURCE_TABLE_VALUE_ONLY_NOT_NEW_Q_ADMISSION'}
    if family == 't_alpha_gamma':
        r['branch'] = {'status': 'INCLUSIVE_GROUND_AND_FIRST_EXCITED_NO_FRACTIONS',
                       'daughter': '7Li', 'branch_fraction': None, 'total_photon_multiplicity': None,
                       'source_statement': 'The transitions to the ground and the first excited states of 7 Li are considered inclusively.'}
        r['support']['model_cross_section_ranges_Ecm_MeV'] = ['below0.3', 'above1.2']
        r['support']['experimental_cross_section_range_Ecm_MeV'] = ['0.3', '1.2']
    if family in ('d_d_p', 'd_d_n'):
        r['selection_status'] = 'INACTIVE_ALTERNATIVE_TO_REI18_VIVIANI_CONSTANT; DO_NOT_SUM'

# Channel-resolved evaluated reference cross sections; averaged columns stay
# separate from monoenergetic points and from the dimensionless g-factor.
jfile = 'raw_primary/JENDL5_He3_T3.html'
jt = (BASE/jfile).read_text()
for mt, family in [(102, 'he3_n_gamma'), (103, 'n_he3_p')]:
    allblocks = re.findall(r'<tr>.*?</tr>', jt, re.S)
    blocks = [x for x in allblocks if re.search(r'<td[^>]*>'+str(mt)+r'</td>', x)]
    assert len(blocks) == 1
    literal = blocks[0]
    cells = [html.unescape(re.sub('<[^>]+>', '', x)).strip()
             for x in re.findall(r'<td[^>]*>(.*?)</td>', literal, re.S)]
    assert len(cells) == 8
    cols = ['MT', 'reaction', 'sigma_0.0253_eV', 'Maxwellian_average', 'g_factor',
            'resonance_integral', 'sigma_14_MeV', 'fission_spectrum_average']
    r = row('JENDL5_He3_MT'+str(mt)+'_REFERENCE_TABLE', family, jfile,
            'https://wwwndc.jaea.go.jp/jendl/j5/elm/Table/z002/T3.html',
            'EVALUATED_LIBRARY_REFERENCE_POINT_TABLE', {'html_row_MT': mt})
    r['raw_values'] = {**dict(zip(cols, cells)), 'raw_literal': literal}
    r['units'] = {'cross_sections': 'nativeSI-prefixed barns as printed in each cell',
                  'g_factor': 'dimensionless', 'energy_reference': 'eV/MeV as labeled'}
    r['support'] = {'source_processing_temperature_K': '300',
                    'native_monoenergetic_points': ['0.0253eV', '14MeV'],
                    'averages_are_not_monoenergetic_points': True,
                    'one_over_v_extrapolation_performed': False,
                    'full_energy_grid_recovered': False,
                    'source_processing': 'JENDL-5 at300K using LINEAR,RECENT,SIGMA1/PREPRO'}

# NCNR reports total absorption.  Project capture/alpha branch assignment is
# carried only as an explicit candidate relation, not source-resolved branching.
nfile = 'raw_primary/NIST_NCNR_neutron_list.html'
nl = (BASE/nfile).read_text().splitlines()
for isotope, family in [('1H', 'p_n_gamma'), ('2H', 'd_n_gamma'), ('6Li', 'n_li6_alpha')]:
    found = [(i+1, x) for i,x in enumerate(nl) if re.match(r'<td>\s*'+isotope+r'\s*<td>', x)]
    assert len(found) == 1, isotope
    ln, literal = found[0]
    cells = [html.unescape(re.sub('<[^>]*>', '', x)).strip() for x in literal.split('<td>')[1:]]
    assert len(cells) == 8, cells
    r = row('NIST_NCNR_'+isotope+'_ABSORPTION_2200MS', family, nfile,
            'https://ncnr.nist.gov/resources/n-lengths/list.html',
            'PROVIDER_TABULATED_TOTAL_ABSORPTION', {'raw_line_1based': ln, 'isotope_label': isotope})
    r['raw_values'] = {'all_native_columns': cells, 'absorption': cells[-1], 'raw_literal': literal}
    r['units'] = {'absorption': 'barn', 'reference_velocity': 'm/s'}
    r['support'] = {'neutron_velocity': '2200', 'channel': 'TOTAL_ABSORPTION',
                    'one_over_v_extrapolation_performed': False,
                    'reaction_family_assignment': 'REI18_CONDITIONAL_CAPTURE_OR_DOMINANT_ALPHA_APPROXIMATION_ONLY',
                    'source_publication': 'NeutronNews,vol3no3,1992,pp29–37'}
    r['branch'] = {'status': 'TOTAL_ABSORPTION_PARTIAL_CHANNEL_ASSIGNMENT_UNRESOLVED',
                   'branch_fraction': None, 'total_photon_multiplicity': None}
    r['uncertainty'] = ({'printed': '(4.)', 'unit': 'barn', 'confidence_probability': None,
                         'meaning': 'Parenthetical source uncertainty retained; source branch uncertainty separate'}
                        if isotope == '6Li' else None)

vtpath = BASE/'derived_text/Viviani2023_DD.txt'
vt = vtpath.read_text()
vex = extract_between(vt, 'Specifically, the d(d, p)', 'keV b].')
for family, value, unc in [('d_d_p', '50.8', '1.9'), ('d_d_n', '51.0', '1.4')]:
    r = row('VIVIANI2023_'+family+'_S0', family, 'raw_primary/Viviani2023_DD.pdf',
            'https://inspirehep.net/files/fc3a3fe08ab5d1beaa365ec51e2c7565',
            'PRIMARY_THEORETICAL_ZERO_ENERGY_ESTIMATE',
            {**{k:v for k,v in vex.items() if k != 'literal'},
             'derived_text_file': str(vtpath.relative_to(BASE)), 'derived_text_SHA256': sha(vtpath)})
    r['raw_values'] = {'S0': value, 'raw_literal': vex['literal']}
    r['units'] = {'S0': 'keV b'}
    r['support'] = {'zero_energy_estimate': True, 'energy_dependent_table_recovered': False,
                    'theory_cutoffs_MeV': ['500', '600'], 'rate_table_supplied': False,
                    'constant_S_continuation_performed': False}
    r['uncertainty'] = {'plus_minus': unc, 'unit': 'keV b',
                        'meaning': 'Preliminary theoretical band from two interaction cutoffs',
                        'covariance': None, 'confidence_probability': None}
    r['selection_status'] = 'HISTORICAL_REI18_NOMINAL_INPUT; NO_NEW_DEFAULT_ACTIVATION'

ptpath = BASE/'derived_text/Dubovichenko2019_pT_1811.04779.txt'
pt = ptpath.read_text()
pex = extract_between(pt, 'S(0) = 0.95(5) eV b.', 'S(0) = 0.95(5) eV b.')
r = row('DUBOVICHENKO2019_p_t_gamma_E1_S0', 'p_t_gamma',
        'raw_primary/Dubovichenko2019_pT_1811.04779.pdf', 'https://arxiv.org/pdf/1811.04779',
        'PRIMARY_E1_CLUSTER_MODEL_ESTIMATE',
        {**{k:v for k,v in pex.items() if k != 'literal'},
         'derived_text_file': str(ptpath.relative_to(BASE)), 'derived_text_SHA256': sha(ptpath)})
r['raw_values'] = {'S0': '0.95', 'raw_literal': pex['literal']}
r['units'] = {'S0': 'eV b'}
r['support'] = {'model_nearly_flat_energy_range_keV': ['1', '3'],
                'multipole_scope': 'E1 model; M1 is zero in this source model, not an empirical all-multipole guarantee',
                'constant_S_continuation_performed': False, 'rate_table_supplied': False}
r['uncertainty'] = {'printed_parenthetical': '(5)', 'plus_minus': '0.05', 'unit': 'eV b',
                    'meaning': 'Source zero-energy versus1keV model-extrapolation estimate',
                    'confidence_probability': None}

lifile = 'raw_primary/Li2015_DDp_1503.08672.html'
litext = (BASE/lifile).read_text()
lm = re.search(r'<math id="S4.SS4.p3.m5".*?</math>', litext, re.S)
assert lm is not None and '56.7' in lm.group(0)
r = row('LI2015_d_d_p_THM_S0', 'd_d_p', lifile,
        'https://ar5iv.labs.arxiv.org/html/1503.08672',
        'PRIMARY_TROJAN_HORSE_EXPERIMENTAL_EXTRAPOLATION',
        {'html_id': 'S4.SS4.p3.m5', 'section': 'IV.4', 'table': 'I,currentwork'})
r['raw_values'] = {'S_bare_0': '56.7', 'raw_literal': lm.group(0)}
r['units'] = {'S_bare_0': 'keV b'}
r['support'] = {'quoted_data_reach': 'about400keV down to severalkeV',
                'zero_energy_polynomial_extrapolation': True,
                'plasma_screening_correction_imported': False, 'rate_table_supplied': False}
r['uncertainty'] = {'plus_minus': '2.0', 'unit': 'keV b', 'covariance': None,
                    'confidence_probability': None}
r['selection_status'] = 'INACTIVE_ALTERNATIVE_TO_REI18_VIVIANI_CONSTANT; DO_NOT_SUM'

assert len(rows) == 19 and len({r['id'] for r in rows}) == len(rows)
assert len({f for r in rows for f in r['family_ids']}) == 16
write('PROVIDER_ROWS.json', {
    'schema': 'WU_TARGET19_PRIMARY_PROVIDER_SOURCE_ROWS_V1',
    'numeric_policy': 'Native printed strings; no unit conversion, interpolation, reverse-rate inference, rate evaluation, or Q computation',
    'scope': '16nonweak conditional-family source links, including3total-absorption assignments; not16channel-resolved empirical rates',
    'primary_source_variants': len(rows),
    'native_NACRE_rate_grid_records': sum(r['raw_values'].get('native_rate_table_count', 0) for r in rows),
    'six_direct_photonuclear_forward_supplier_cells': 'UNRESOLVED_NULL',
    'reused_conditional_outputs': 'REUSED_OUTPUT_RETRIEVAL.json; not included or counted as primary provider rows',
    'rows': rows})

old = json.loads((R1/'providers.json').read_text())['rows']
oldmap = {
    1: {'target_forward': ['VF96_PI_Z1_N1'], 'target_reverse': ['VF96_RR_Z1_N1']},
    2: {'target_forward': ['VF96_PI_Z2_N2'], 'target_reverse': ['VF96_RR_Z2_N2_fit_a', 'VF96_RR_Z2_N2_fit_b']},
    3: {'target_forward': ['VF96_PI_Z2_N1'], 'target_reverse': ['VF96_RR_Z2_N1']},
    7: {'target_reverse': ['PHYS81_COLD_pd_h_gamma']},
    8: {'target_reverse': ['ENDF_B_VIII1_H1_MT102', 'PHYS81_COLD_np_d_gamma']},
    9: {'target_forward': ['NUBASE2020_T_beta_minus', 'LiveChart_ENSDF_T_beta_minus']},
    10: {'target_forward': ['NUBASE2020_n_beta_minus', 'LiveChart_ENSDF_n_beta_minus']},
    12: {'target_forward': ['ENDF_B_VIII1_H1_MT102', 'PHYS81_COLD_np_d_gamma']},
    13: {'target_forward': ['PHYS81_COLD_pd_h_gamma']},
}
mapped = []
for t in targets['reactions']:
    i = t['id']
    links = oldmap.get(i, {})
    assert all(p in old for ps in links.values() for p in ps)
    new = [r for r in rows if i in r['target_ids']]
    m = {'target_id': i, 'equation_as_listed': t['equation_as_listed'],
         'target_declaration_unchanged': True,
         'conditional_family_ids': [f['id'] for f in families.values() if i in f['dossier_ids']],
         'R1_provider_ids_by_target_direction': links,
         'R1_kinematics_only_ids': [p for ps in links.values() for p in ps if p.startswith('PHYS81_COLD_')],
         'new_primary_provider_ids_by_target_direction': {
             d: [r['id'] for r in new if r['target_directions'][str(i)] == d]
             for d in ('target_forward', 'target_reverse')},
         'new_rate_admission': False, 'new_Q_admission': False,
         'state_branch_energy_qualification': 'UNRESOLVED_UNLESS_EXPLICITLY_RETAINED_FROM_R1_SOURCE',
         'direct_photonuclear_sigma_gamma_source': None if i in photo_ids else 'NOT_THIS_TARGET_KIND'}
    if i in photo_ids:
        m['missing_target_forward_provider'] = {
            'status': 'INPUT_DEPENDENCY_UNRESOLVED',
            'need': 'Versioned channel-resolved sigma_gamma(E_gamma), threshold/support, normalization, daughter-state/particle/photon branches and uncertainty; preserve ionic-state mass/Q convention',
            'capture_anchor_is_reverse_evidence_only': True,
            'prior_selected_5_to_60_eV_external_photo_zero_is_not_cross_section_zero': True,
            'source_refs': ['raw_git/research/rei_tritium_production_audit_20261022/NUCLEAR_PROVIDER_INVENTORY.md',
                            'raw_primary/NACREII_1310.7099.pdf'] if i in (6,7,11) else
                           ['raw_git/research/rei_tritium_production_audit_20261022/NUCLEAR_PROVIDER_INVENTORY.md'],
            'primary_reverse_thermal_rate_appendix_is_not_direct_sigma_gamma': True}
    if i <= 3:
        m['qualification'] = 'Elemental fit source with explicit isotope projections; isotope shifts/state response and totalRR cascade photon multiplicity not newly admitted'
    elif i == 9:
        m['qualification'] = 'R1 source alternatives preserved; neutralT spectator projection has a chargedHe3+ daughter plus beta electron and antineutrino. Drawing does not resolve electron-shell branches.'
    elif i == 10:
        m['qualification'] = 'R1 evaluated neutron alternatives preserved; neutron half-life and mean lifetime must not be conflated'
    elif i in (7, 13):
        m['qualification'] = 'R1 cold pD Q is kinematics only; newNACRE-II source supplies forwardcapture native-rate table outside100–10000K'
    mapped.append(m)
write('TARGET19_R1_MAPPING.json', {
    'schema': 'WU_TARGET19_R1_ADDITIVE_SOURCE_MAPPING_V1',
    'target_contract_sha256': sha(target_path), 'conditional_contract_sha256': sha(conditional_path),
    'R1_source_commit': '18a6804d7cbe4879701e83631f7e908bbb84cef1',
    'R1_registry_SHA256': {p.name: sha(p) for p in sorted(R1.glob('*.json'))},
    'authoritative_target_count': 19, 'shared_family_target_pairs': [[7,13], [8,12], [11,19]],
    'conditional_dossier_families': 13, 'conditional_extra_closure_families': 5,
    'direct_photonuclear_forward_missing_target_ids': sorted(photo_ids),
    'R1_nd_capture_is_extra_closure_not_target19_id': True,
    'no_physical_result_counts_inferred_from_source_or_projection_counts': True,
    'rows': mapped})

for source, name in [(target_path, 'TARGET_NETWORK_19.json'), (conditional_path, 'REI18_CONDITIONAL_CONTRACT.json')]:
    dest = BASE/'raw_contracts'/name
    dest.parent.mkdir(exist_ok=True)
    with dest.open('xb') as out:
        out.write(source.read_bytes())
write('INTAKE_SUMMARY.json', {
    'schema': 'WU_TARGET19_SOURCE_INTAKE_SUMMARY_V1',
    'source_variants': len(rows), 'native_NACRE_grid_records': 598,
    'primary_family_links': 16, 'of_which_total_absorption_only': 3,
    'primary_records_are_not_new_physical_approvals': True,
    'target19_coverage': 'All19 mapped; six directphotonuclear forward cells are null; original electronic/weak/ENDF sources remain scoped',
    'publication_integration': 'AdditiveR2 only; no R1 source or compiled output changed',
    'reused_model_output_record_class': 'REUSED_CONDITIONAL_MODEL_OUTPUT',
    'reused_model_artifacts': 'REUSED_OUTPUT_RETRIEVAL.json',
    'reused_model_scope': conditional['mode'],
    'new_rate_Q_or_IVP_executions': 0, 'old249_suite_replays': 0,
    'source_retrieval_and_preparation_CPU_s': None, 'source_retrieval_and_preparation_wall_s': None,
    'unmeasured_is_not_zero': True,
    'remaining_dependencies': [
        'Direct channel-resolved photonuclear sigma_gamma(E) for target4,5,6,7,8,11',
        'NISTtotalabsorption to capture/alpha branch fractions; full neutron-energy support/covariance where required',
        'State-resolved ionic/isomer/daughter branches and nuclearQ conventions, especially neutraltritium shell response and inclusiveLi7capture',
        'Low-temperature neutral/molecular/screening and energetic-product treatment for any future actualconsumer',
        'Finite covariance/confidence or joint alternative-selection contract; never infer99% from printed ranges'],
    'access_outcomes': {
        'NACRE_ar5iv_first_attempt': 'READ_TIMEOUT_PRESERVED_IN_PRIMARY_FETCH_RECEIPTS_01',
        'NACRE_observed_PDF_link_fallback': 'SUCCESS_PRIMARY_FETCH_RECEIPTS_02',
        'direct_photonuclear_payload': 'NO_DIRECT_CHANNEL_PAYLOAD_LINK_FOUND_IN_PINNED_INVENTORY; not claimedinaccessiblebypermission',
        'alternative_primary_crosschecks_not_needed_for_selected_rows': [
            'https://inspirehep.net/literature/276545',
            'https://www.nndc.bnl.gov/endfdocs/ENDF-301.pdf'],
        'controller_decay_source_labels_not_newly_retrieved_as_primary': [
            'LNHB H-3_tables.pdf', 'IAEA sgnucdat/d1.htm', 'PDG2025 neutronmeanlifetime']}})
print(json.dumps({'source_variants': len(rows),
                  'native_NACRE_grid_records': sum(r['raw_values'].get('native_rate_table_count', 0) for r in rows),
                  'target_ids': len(mapped), 'direct_photonuclear_forward_missing': sorted(photo_ids),
                  'provider_rows_SHA256': sha(BASE/'PROVIDER_ROWS.json')}, indent=2))
