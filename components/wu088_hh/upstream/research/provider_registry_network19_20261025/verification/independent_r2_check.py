"""Independent changed-input audit; no project parser or builder imports.

Checks native printed data and new integer projections only. All source rate/Q
numbers remain strings. No interpolation, spectrum fold, rate or Q evaluation.
Run once through the R2 bounded runner after root's authority/input preflight.
"""
from pathlib import Path
from collections import Counter
from decimal import Decimal
import argparse
import hashlib
import html
import json
import re
import time
import traceback

WORK = Path('/workspace/scratch/3ffa3d77ca37')
LEAF = WORK / 'WU088_HH/research/provider_registry_network19_20261025'
R1 = LEAF.parent / 'provider_registry_20261025'
PRIVATE = WORK / 'network19_intake'
PUBLIC = LEAF / 'sources/primary'
PHOTO = LEAF / 'sources/photon_native'
HE4_PRIVATE = WORK / 'he4_photo_supplement'
RESULTS = []
INPUTS = {}
ASSERTIONS = 0


def sha(path):
    path = Path(path)
    value = hashlib.sha256(path.read_bytes()).hexdigest()
    INPUTS[str(path)] = value
    return value


def read(path):
    sha(path)
    return json.loads(Path(path).read_text())


def ck(condition, reason):
    global ASSERTIONS
    ASSERTIONS += 1
    if not condition:
        raise AssertionError(reason)


def group(name, function):
    before = ASSERTIONS
    try:
        detail = function()
        RESULTS.append({'group': name, 'status': 'PASS',
                        'assertions': ASSERTIONS-before, 'detail': detail})
    except Exception as exc:
        RESULTS.append({'group': name, 'status': 'FAIL',
                        'assertions': ASSERTIONS-before,
                        'error': str(exc), 'traceback': traceback.format_exc()})


def manifest(base, name):
    document = read(base / name)
    for item in document['files']:
        p = base / item['path']
        ck(p.stat().st_size == item['bytes'], 'Manifest byte count: '+str(p))
        ck(sha(p) == item['sha256'], 'Manifest hash: '+str(p))
    return len(document['files'])


def pin_and_manifests():
    pins = {
        PRIVATE/'MANIFEST.json': 'f1e1b7c75105efbe5d4a4b78aa7e2025b2ba1eec3f3d34c921dafccb380f6ba7',
        PRIVATE/'PROVIDER_ROWS.json': 'be8a66c04f662c00e779d6aebe1245da72c0d868625264881cb18f6c83e6b39e',
        PUBLIC/'PROVIDER_ROWS.json': '9878f53c509ddaaa0317df2349913040dfd01425bc318d66cca0fd307bed33e3',
        PUBLIC/'PUBLICATION_SUBSET_MANIFEST.json': '8657e0572ba0a759e13771ee1c924b32d774156c34bd367bd430f2e13a89c542',
        PHOTO/'PROVIDER_ROWS.json': 'c0c4c93aa0427e6353ea56e9ff12c78718951f47eb9c7dbc6d6b3e83a5ccf6ae',
        LEAF/'build_network19.py': '96778246c7db1366689da360050dc7c73045668ef08c39324ac7e2e7e34bfdaf',
        R1/'registry_adapter.py': '9a093eed42f9ff5858d7bae11c726988ddbde4feeed38888b1c90fe329be816c',
        LEAF.parent/'rei_chem_ledger_20261025/chem_ledger.py': '60a502895266b6feb96964abc4b24db61c2faed2344db0f7d12f16bb47ed62af',
    }
    for path, expected in pins.items():
        ck(sha(path) == expected, 'Frozen input changed: '+str(path))
    return {'private_manifest_files': manifest(PRIVATE, 'MANIFEST.json'),
            'public_manifest_files': manifest(PUBLIC, 'PUBLICATION_SUBSET_MANIFEST.json'),
            'photon_manifest_files': manifest(PHOTO, 'MANIFEST.json')}


def primary_rows():
    rows = read(PRIVATE/'PROVIDER_ROWS.json')['rows']
    ck(len(rows) == 19 and len({r['id'] for r in rows}) == 19, '19 distinct primary records')
    fams = read(PRIVATE/'raw_contracts/REI18_CONDITIONAL_CONTRACT.json')['families']
    by_fam = {r['id']: r for r in fams}
    for r in rows:
        ck(sha(PRIVATE/r['source_file']) == r['source_SHA256'], 'Primary raw source '+r['id'])
        ck((PRIVATE/r['source_file']).stat().st_size == r['source_bytes'], 'Primary size '+r['id'])
        ck(r['record_class'] == 'PRIMARY_SOURCE_ROW', 'Primary class '+r['id'])
        ck(r['new_rate_admission'] is False and r['new_Q_admission'] is False
           and r['default_active'] is False and r['source_value_evaluated_in_this_intake'] is False,
           'Primary source-only boundary '+r['id'])
        ck(r['direction'] == 'family_forward', 'Primary phase A direction '+r['id'])
        target_ids = set().union(*(set(by_fam[f]['dossier_ids']) for f in r['family_ids']))
        ck(set(r['target_ids']) <= target_ids, 'Family mapping '+r['id'])
        expected = {str(t): 'target_reverse' if t in {4,5,6,7,8,11} else 'target_forward'
                    for t in r['target_ids']}
        ck(r['target_directions'] == expected, 'Direction mapping '+r['id'])
        ck(r['branch']['branch_fraction'] is None and r['branch']['total_photon_multiplicity'] is None,
           'Uninvented branch/multiplicity '+r['id'])
    ck(len(set(f for r in rows for f in r['family_ids'])) == 16, '16 nonweak family links')
    return {'source_variants': 19, 'nonweak_family_links': 16}


def nacre_native_tables():
    source = (PRIVATE/'derived_text/NACREII_1310.7099.txt').read_text()
    pages = source.split('\f')
    rows = [r for r in read(PRIVATE/'PROVIDER_ROWS.json')['rows'] if r['id'].startswith('NACRE')]
    expected = {2: ('0.21','eV b','+5.493',60), 3: ('5.8','meV b','+23.847',60),
                4: ('55.5','keV b','+3.269',60), 5: ('56.2','keV b','+4.033',60),
                6: ('2.2','meV b','+1.474',59), 7: ('11','MeV b','+17.589',60),
                8: ('98','eV b','+2.467',59), 9: ('5.9','MeV b','+18.353',60),
                13: ('3.1','MeV b','+4.020',60), 15: ('52','keV b','+17.347',60)}
    total = 0
    token = re.compile(r'[+−-]?\d+(?:\.\d*)?(?:E[+−-]?\d+)?\Z')
    for r in rows:
        loc, vals = r['locator'], r['raw_values']
        number = loc['native_rate_table']
        page = pages[loc['pdf_page_1based']-1]
        header = re.search(r'(?m)^\s*Table '+str(number)+r':', page)
        ck(header is not None, 'Native PDF table page '+r['id'])
        region = page[header.end():].split('REV =', 1)[0]
        columns = [[], []]
        for line in region.splitlines():
            fields = line.split()
            if len(fields) not in (4, 8) or not all(token.fullmatch(x) for x in fields):
                continue
            columns[0].append(fields[:4])
            if len(fields) == 8:
                columns[1].append(fields[4:])
        independently_parsed = columns[0] + columns[1]
        exported = [[p[k] for k in ('T9','adopted','low','high')] for p in vals['native_rate_table']]
        ck(independently_parsed == exported, 'All native tuples in table '+str(number))
        ck(len(exported) == expected[number][3] == vals['native_rate_table_count'], 'Native count '+r['id'])
        literal = source[loc['text_char_start']:loc['text_char_end_exclusive']]
        ck(literal == vals['native_table_literal'], 'Native table exact locator '+r['id'])
        for p in vals['native_rate_table']:
            line = literal.splitlines()[p['table_text_line_1based']-1]
            ck(line == p['raw_literal'], 'Raw native line '+r['id']+' '+p['T9'])
            start = 4*(p['column_group']-1)
            ck(line.split()[start:start+4] == [p[k] for k in ('T9','adopted','low','high')], 'Native column binding')
            lo, mid, hi = [Decimal(p[k].replace('−','-')) for k in ('low','adopted','high')]
            ck(lo <= mid <= hi, 'Source evaluation ordering '+r['id']+' '+p['T9'])
        s0loc, qloc = loc['S0_locator'], loc['Q_locator']
        ck(source[s0loc['text_char_start']:s0loc['text_char_end_exclusive']] == vals['S0_printed_literal'], 'S0 literal binding')
        ck(source[qloc['text_char_start']:qloc['text_char_end_exclusive']] == r['Q']['raw_literal'], 'Q literal binding')
        ck((vals['S0_printed_central'],r['units']['S0'],r['Q']['printed_value']) == expected[number][:3], 'S0/Q source values and units')
        ck(r['units']['native_rate_quantity'] == 'N_A <sigma v>' and r['units']['native_rate'] == 'cm^3 mol^-1 s^-1', 'Native rate unit')
        ck(r['support']['native_grid_overlaps_100_to_10000_K'] is False and r['support']['native_table_interpolation_performed'] is False, 'Domain/execution separation')
        ck(r['uncertainty']['confidence_probability'] is None and r['uncertainty']['covariance'] is None, 'No invented NACRE covariance/confidence')
        ck(r['Q']['ionic_mass_convention_qualified'] is False and r['Q']['uncertainty'] is None, 'Printed Q not physical admission')
        total += len(exported)
    ck(total == 598, '598 native grid records')
    return {'native_tables': len(rows), 'native_grid_records': total, 'rate_evaluations': 0}


def selected_source_constants():
    rows = read(PRIVATE/'PROVIDER_ROWS.json')['rows']
    count = 0
    for r in rows:
        rid, values = r['id'], r['raw_values']
        if rid.startswith('NACRE'):
            continue
        if rid.startswith('JENDL'):
            source = (PRIVATE/r['source_file']).read_text()
            trs = re.findall(r'<tr\b[^>]*>(.*?)</tr>', source, re.S | re.I)
            all_cells = [[html.unescape(re.sub(r'<[^>]*>', '', cell)).strip()
                          for cell in re.findall(r'<td\b[^>]*>(.*?)</td>', tr, re.S | re.I)] for tr in trs]
            selected = [cells for cells in all_cells if cells and cells[0] == values['MT']]
            keys = ('MT','reaction','sigma_0.0253_eV','Maxwellian_average','g_factor','resonance_integral','sigma_14_MeV','fission_spectrum_average')
            ck(selected == [[values[k] for k in keys]], 'JENDL selected source cells '+rid)
            ck(r['support']['averages_are_not_monoenergetic_points'] is True and r['support']['one_over_v_extrapolation_performed'] is False, 'JENDL observable distinction')
        elif rid.startswith('NIST'):
            source = (PRIVATE/r['source_file']).read_text().splitlines()
            line = source[r['locator']['raw_line_1based']-1]
            cells = [html.unescape(re.sub('<[^>]*>', '', c)).strip() for c in re.split(r'<td>', line)[1:]]
            ck(cells == values['all_native_columns'], 'NIST raw row '+rid)
            ck(cells[-1] == values['absorption'], 'NIST absorption cell')
            ck(r['support']['channel'] == 'TOTAL_ABSORPTION' and r['branch']['status'] == 'TOTAL_ABSORPTION_PARTIAL_CHANNEL_ASSIGNMENT_UNRESOLVED', 'NIST partial channel not inferred')
        elif rid.startswith(('VIVIANI','DUBOVICHENKO')):
            loc = r['locator']; source = (PRIVATE/loc['derived_text_file']).read_text()
            ck(sha(PRIVATE/loc['derived_text_file']) == loc['derived_text_SHA256'], 'Derived text identity')
            ck(source[loc['text_char_start']:loc['text_char_end_exclusive']] == values['raw_literal'], 'Primary S0 exact locator')
            ck(r['uncertainty']['confidence_probability'] is None, 'Model error not empirical confidence')
            if rid.startswith('VIVIANI'):
                ck(r['support']['theory_cutoffs_MeV'] == ['500','600'], 'Viviani cutoff variation')
                ck((values['S0'],r['uncertainty']['plus_minus']) == (('50.8','1.9') if '_d_d_p_' in rid else ('51.0','1.4')), 'Viviani native value')
            else:
                ck(values['S0'] == '0.95' and r['uncertainty']['plus_minus'] == '0.05' and r['units']['S0'] == 'eV b', 'Dubo native value')
        elif rid.startswith('LI2015'):
            source = (PRIVATE/r['source_file']).read_text()
            m = re.search(r'<math\s+id="'+re.escape(r['locator']['html_id'])+r'".*?</math>', source, re.S)
            ck(m is not None and m.group() == values['raw_literal'], 'Li source formula selector')
            ck(values['S_bare_0'] == '56.7' and r['uncertainty']['plus_minus'] == '2.0', 'Li native value')
        else:
            raise AssertionError('Unhandled selected source '+rid)
        count += 1
    return {'selected_non_NACRE_source_rows': count}


def public_derivative():
    private = read(PRIVATE/'PROVIDER_ROWS.json')
    public = read(PUBLIC/'PROVIDER_ROWS.json')
    removed = {'raw_literal','native_table_literal','S0_printed_literal','source_statement'}
    def strip(value):
        if isinstance(value, dict):
            return {k: strip(v) for k,v in value.items() if k not in removed}
        if isinstance(value, list):
            return [strip(v) for v in value]
        return value
    ck(len(public['rows']) == len(private['rows']) == 19, 'Public source count unchanged')
    for old, new in zip(private['rows'], public['rows']):
        reduced = {k:v for k,v in new.items() if k != 'publication_source_availability'}
        ck(reduced == strip(old), 'All public numeric, uncertainty, support and provenance fields unchanged '+old['id'])
        if not (PUBLIC/new['source_file']).exists():
            ck(new['publication_source_availability']['original_bytes_bundled'] is False, 'Explicit full-text omission')
    m = read(PUBLIC/'PUBLICATION_SUBSET_MANIFEST.json')
    public_hashes = {sha(p) for p in PUBLIC.rglob('*') if p.is_file()}
    for excluded in m['excluded_original_files']:
        ck(excluded['sha256'] not in public_hashes, 'Excluded original bytes must not occur anywhere in public subset: '+excluded['path'])
    notice = (PUBLIC/'THIRD_PARTY_NOTICES.md').read_text()
    full_viviani = (PRIVATE/'derived_text/Viviani2023_DD.txt').read_text().split('\f')[0]
    ck('Creative Commons Attribution 3.0' in full_viviani or 'CC BY 3.0' in full_viviani, 'Viviani actual page 1 grant')
    ck('3.0' in notice and 'Viviani' in notice and '2586' in notice, 'CC attribution retained')
    return {'public_primary_rows': 19, 'non_CC_original_hashes_excluded': len(m['excluded_original_files'])}


def recovered_scope_and_reuse():
    target = read(PRIVATE/'raw_contracts/TARGET_NETWORK_19.json')
    conditional = read(PRIVATE/'raw_contracts/REI18_CONDITIONAL_CONTRACT.json')
    ck([r['id'] for r in target['reactions']] == list(range(1,20)), 'All original IDs')
    ck(sum(1+int(r['reversible_arrow_as_listed']) for r in target['reactions']) == 28, 'Original 28 directions')
    fams = conditional['families']
    ck(len(fams) == 18 and sum(bool(f['dossier_ids']) for f in fams) == 13, '13 plus 5 model families')
    mapped = [x for f in fams for x in f['dossier_ids']]
    ck(sorted(mapped) == list(range(4,20)), '16 original nuclear IDs covered once by family aliases')
    mapping = read(PRIVATE/'TARGET19_R1_MAPPING.json')
    ck(mapping['direct_photonuclear_forward_missing_target_ids'] == [4,5,6,7,8,11], 'Preserved phase-A gap observation')
    ck(len(mapping['rows']) == 19, 'Original mapping retains all IDs')
    for name, expected in mapping['R1_registry_SHA256'].items():
        ck(sha(R1/'registry'/name) == expected, 'Unchanged R1 saved registry '+name)
    image = LEAF/'sources/recovered_network/primordial_target_network.png'
    ck(sha(image) == target['source_image']['sha256'] and image.stat().st_size == target['source_image']['bytes'], 'Original image recovered identity')
    reuse = read(PRIVATE/'REUSED_OUTPUT_RETRIEVAL.json')['rows']
    for row in reuse:
        raw = (PRIVATE/row['path']).read_bytes()
        ck(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], 'Reused output hash '+row['path'])
        ck(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob_SHA'], 'Reused actual git blob '+row['path'])
        ck(row['record_class'] == 'REUSED_CONDITIONAL_MODEL_OUTPUT' and row['new_execution'] is False, 'Derived conditional output classification')
    decision = read(PRIVATE/'raw_git/research/rei_tritium_production_audit_20261022/review/NUCLEAR_NETWORK_DECISION.json')
    ck('PASS_SCOPED' in json.dumps(decision), 'Existing conditional independent review located')
    return {'original_targets':19,'directions':28,'conditional_families':18,'reused_artifacts':len(reuse),'historical_science_replays':0}


def endf_fields(line):
    return [line[i:i+11].strip() for i in range(0,66,11)]


def verify_tab1(lines, table, mat, mf, mt):
    h = table['header_line_1based']-1
    native = endf_fields(lines[h])
    ck(native == table['header_fields'], 'ENDF TAB1 header identity')
    nr, np = int(native[4]), int(native[5])
    ck((nr,np) == (table['NR'],table['NP']) and np == len(table['rows']), 'ENDF NR/NP')
    packed_interpolation = []
    for k in range(h+1,h+1+(2*nr+5)//6):
        packed_interpolation += endf_fields(lines[k])
    independently_interpolation = [{'NBT':int(packed_interpolation[i]),'INT':int(packed_interpolation[i+1])} for i in range(0,2*nr,2)]
    ck(independently_interpolation == table['interpolation'], 'Native interpolation regions')
    first_data = h+1+(2*nr+5)//6
    for i,row in enumerate(table['rows']):
        line_no = first_data+i//3
        fx = 2*(i%3)
        actual = endf_fields(lines[line_no])
        ck((int(lines[line_no][66:70]),int(lines[line_no][70:72]),int(lines[line_no][72:75])) == (mat,mf,mt), 'ENDF MAT MF MT')
        ck(row == {'x':actual[fx],'y':actual[fx+1], 'source_line_1based':line_no+1,
                   'x_field_1based':fx+1,'y_field_1based':fx+2}, 'Native field/line selector')
    last_exclusive = first_data+(2*np+5)//6
    ck(table['last_source_line_1based'] == last_exclusive, 'Native last TAB1 line')
    return last_exclusive


def photon_native():
    packet = read(PHOTO/'PROVIDER_ROWS.json')
    specs = {128:(50,35,2,4,'EXCLUSIVE_NATIVE_CHANNEL'),
             225:(5,42,3,121,'FACTORIZED_EXCLUSIVE_CANDIDATE'),
             328:(5,169,11,1652,'INCLUSIVE_ONLY')}
    tally = []
    for row in packet['rows']:
        mat = row['locator']['MAT'];mt,np,nk,ny,coverage = specs[mat]
        path = PHOTO/row['source_file']; ck(sha(path) == row['source_SHA256'], 'Photon source SHA')
        ck(path.stat().st_size == row['source_bytes'], 'Photon source bytes')
        lines = path.read_text().splitlines()
        cross = row['raw_values']['cross_section_TAB1']
        last = verify_tab1(lines,cross,mat,3,mt)
        ck(cross['NP'] == np and last == row['locator']['cross_section']['line_end_1based'], 'Cross-section native range')
        production = row['raw_values']['production_yield_TAB1s']
        section_indices = [i for i,l in enumerate(lines) if len(l)>=75 and l[70:72].strip()=='6' and l[72:75].strip()==str(mt)]
        cursor = section_indices[0]
        ck(endf_fields(lines[cursor]) == production['header_fields'], 'MF6 section header')
        ck(production['NK'] == nk == len(production['products']), 'MF6 product count')
        cursor += 1
        for product in production['products']:
            tab = product['yield_TAB1']
            ck(cursor+1 == tab['header_line_1based'], 'Full MF6 product traversal selector')
            fields = endf_fields(lines[cursor])
            ck((product['ZAP'],product['AWP'],product['LIP'],product['LAW']) == (fields[0],fields[1],int(fields[2]),int(fields[3])), 'MF6 product identity/state/law')
            cursor = verify_tab1(lines,tab,mat,6,mt)
            law = int(fields[3])
            if law in (1,2):
                cont = endf_fields(lines[cursor]);nr,ne = int(cont[4]),int(cont[5])
                cursor += 1+(2*nr+5)//6
                for _ in range(ne):
                    npl = int(endf_fields(lines[cursor])[4])
                    cursor += 1+(npl+5)//6
            elif law in (0,3,4):
                pass
            elif law == 6:
                cursor += 1
            else:
                raise AssertionError('Unsupported actual MF6 law '+str(law))
        ck(cursor == section_indices[-1]+1 and production['end_consumed_exactly'] is True, 'All MF6 LAW payloads traversed to exact section end')
        ck(sum(p['yield_TAB1']['NP'] for p in production['products']) == ny, 'Native yield knot count')
        ck(row['source_coverage'] == coverage and row['exclusive_channel_binding'] is (mat==128), 'Physical photon classification')
        ck(row['new_cross_section_products_evaluated'] == 0 and row['new_rate_evaluations'] == 0 and row['new_Q_admission'] is False and row['activation'] is False, 'No photon arithmetic admission')
        ck(row['Q']['Q_admitted'] is False and row['Q']['new_Q_computation'] is False, 'Raw Q source-only')
        if mat == 128:
            ck(row['Q']['value'] == row['Q']['mass_difference_field'] == '-2.224600+6', 'H2 actual negative source Q fields')
        else:
            ck(row['Q']['value'] is None and row['Q']['mass_difference_field'] is None, 'MT5 zero is not exclusive Q')
        if mat == 225:
            header = '\n'.join(l[:66] for l in lines if len(l)>=75 and l[70:75]==' 1451')
            ck(re.search(r'Deuteron production cross section:\s*\n\s*He-3\(g,p\)D cross section',header) is not None, 'He3 factorization supported by actual MF1 comment')
        ck(not any(l[70:72].strip() in {'31','32','33','34','35','40'} for l in lines if len(l)>=75), 'Covariance absence from recovered ENDF file')
        tally.append({'MAT':mat,'MF3_knots':np,'MF6_products':nk,'MF6_yield_knots':ny,'coverage':coverage})
    ck(len(tally) == 3, 'Three actual photon source records')
    return tally


def he4_native(packet_path):
    packet_path = Path(packet_path)
    packet = read(packet_path)
    manifest_count = manifest(packet_path.parent, 'MANIFEST.json')
    first_packet = read(HE4_PRIVATE/'public/PROVIDER_ROWS.json')
    prior_by_id = {r['id']:r for r in first_packet['rows']}
    ck(packet['source_record_count'] == 4 and packet['native_selected_measurements'] == 20, 'He4 actual source counts')
    total = 0
    for row in packet['rows']:
        raw = HE4_PRIVATE/row['source_file']
        ck(sha(raw) == row['source_SHA256'] and raw.stat().st_size == row['source_bytes'], 'He4 private source identity')
        source_name = 'Shima2005_nucl-ex0509017' if row['id'].startswith('Shima') else 'Murata2023_2307.01474'
        textpath = HE4_PRIVATE/'private_text'/f'{source_name}.txt'
        ck(sha(textpath) == row['locator']['private_derived_text_SHA256'], 'He4 private text identity')
        text = textpath.read_text(); start = row['locator']['table_text_char_start'];block = text[start:].split('\f',1)[0]
        ck(text[:start].count('\f')+1 == row['locator']['pdf_page_1based'], 'He4 actual PDF table page')
        points = row['raw_values']['measurements']
        ck(all(row[k] == prior_by_id[row['id']][k] for k in ('raw_values','uncertainty','Q','units')),
           'He4 response-weight correction preserves all original numbers/uncertainties')
        response = row['support']['response_and_energy_definition']
        ck(response['simple_beam_only_average'] is False and response['source_model_reconstruction_performed'] is False,
           'He4 response-weight distinction and no model replay')
        if row['id'].startswith('Shima'):
            ck(response['observable_definition_source_equation'] == '2'
               and response['mean_energy_definition_source_equation'] == '3'
               and 'epsilon' in response['cross_section_latex']
               and 'sigma' in response['mean_energy_latex'], 'Shima efficiency and reaction weighted source definitions')
        else:
            ck(response['unit_integral_photon_profile'] is False
               and response['mean_energy_source_equation'] == '9'
               and response['published_total_observable_source_equations'] == ['10','11','12'],
               'Murata photon-count normalization and model/acceptance correction')
        is_n = row['target_ids'] == [4]
        for p in points:
            line = block.splitlines()[p['source_table_text_line_1based']-1]
            numbers = re.findall(r'\d+(?:\.\d+)?',line)
            if row['id'].startswith('Shima'):
                k = 4 if is_n else 1
                expected = [numbers[0],numbers[k],numbers[k+1],numbers[k+2],numbers[k+2]]
                ck(p['beam_maximum_photon_energy_MeV'] == ['22.3','25','28','32'][p['source_row_1based']-1], 'Shima actual Emax settings')
            else:
                k = 2 if is_n else 7
                expected = numbers[k:k+5]
                ck(p['beam_index_k_source'] == numbers[0] and p['beam_maximum_photon_energy_MeV'] == numbers[1], 'Murata native beam index/Emax')
            ck([p[key] for key in ('mean_photon_energy_MeV','spectrum_averaged_sigma_mb','statistical_plus_minus_mb','systematic_plus_mb','systematic_minus_mb')] == expected, 'He4 native energy/value/statistical/asymmetric-systematic tuple')
        ck(len(points) == row['raw_values']['native_measurement_count'], 'He4 row count')
        ck(row['source_coverage'] == 'EXCLUSIVE_SPECTRUM_AVERAGED_MEASUREMENT' and row['exclusive_channel_binding'] is False, 'He4 measured channel vs pointwise binding')
        ck(row['new_rate_admission'] is False and row['new_Q_admission'] is False and row['default_active'] is False, 'He4 source-only')
        ck(row['publication_source_availability']['original_bytes_bundled'] is False and not (packet_path.parent/row['source_file']).exists(), 'Non-CC He4 paper excluded')
        total += len(points)
    ck(total == 20 and packet['target6_direct_numeric_supplier'] is None, 'He4 target6 explicit dependency')
    return {'source_records':4,'native_channel_measurements':20,'target6_numeric_supplier':None,'manifest_files':manifest_count}


def new_output_projection():
    registry = LEAF/'registry'
    species = read(registry/'species.json')['rows']
    events = read(registry/'events.json')['rows']
    compiled = {r['event_id']:r for r in read(registry/'compiled.json')['rows']}
    ck(len(events) == len(compiled) == 24 and len(species) == 9, '24 new columns and nine reused coordinates')
    r1species = read(R1/'registry/species.json')['rows']
    for sid,s in species.items():
        ck(s == r1species[sid], 'Exact R1 species identity reuse')
    for event in events:
        nu = Counter()
        for side,sign in (('reactants',-1),('products',1)):
            for sid,count in event[side]:
                ck(type(count) is int and count > 0, 'Positive integer stoichiometry')
                nu[sid] += sign*count
        nu = {sid:n for sid,n in nu.items() if n}
        b=q=le=0
        for sid,n in nu.items():
            s = species[sid]['compiler_record']
            baryon = sum(c['A']*c['count'] for c in s['composition'])
            proton = sum(c['Z']*c['count'] for c in s['composition'])
            b += baryon*n; q += s['charge']*n; le += (proton-s['charge'])*n
        for key,sign in (('external_reactants',-1),('external_products',1)):
            for particle,n in event[key]:
                label = particle.split(':',1)[0]
                ck(label in {'gamma','antinu_e','nu_e'}, 'Explicit external particle identity')
                le += sign*n*({'gamma':0,'antinu_e':-1,'nu_e':1}[label])
        ck((b,q,le) == (0,0,0), 'Independent B/q/Le ledger '+event['id'])
        checked = compiled[event['id']]
        ck(checked['stoichiometry'] == nu and (checked['baryon_delta'],checked['charge_delta'],checked['electron_lepton_delta']) == (b,q,le), 'Compiled exact number column '+event['id'])
        ck(checked['energy_status'] == 'UNQUALIFIED:ENERGY' and checked['Q_approved'] is False and checked['native_rate_evaluated'] is False and checked['activation'] is False, 'Compiled physics boundary')
        ck(event['native_Q_record'] is None and event['physical_total_photon_count'] is None and event['rate_normalization_bound'] is False and event['reverse_rate_inferred'] is False, 'Event Q/radiation/normalization boundary')
    families = {r['id']:r for r in read(PRIVATE/'raw_contracts/REI18_CONDITIONAL_CONTRACT.json')['families']}
    symbol_to_AZ = {'n':(1,0),'p':(1,1),'H1':(1,1),'D':(2,1),'T':(3,1),'He3':(3,2),'He4':(4,2),'Li6':(6,3),'Li7':(7,3)}
    def material_signature(side):
        out = Counter()
        for sid,n in side:
            s = species[sid]['compiler_record']
            if not s['composition']:
                continue
            ck(len(s['composition']) == 1 and s['composition'][0]['count'] == 1, 'One nucleus per coordinate')
            c=s['composition'][0]; ck(s['charge'] == c['Z'] and c['isomer']=='ground', 'Declared bare ground coordinate')
            out[(c['A'],c['Z'])] += n
        return out
    for event in events:
        if event['family_id']:
            original=families[event['family_id']]
        else:
            target=next(r for r in read(PRIVATE/'raw_contracts/TARGET_NETWORK_19.json')['reactions'] if r['id']==event['target_id'])
            original=target['nuclear_stoichiometry']
        for side in ('reactants','products'):
            expected=Counter()
            for name,n in original[side].items(): expected[symbol_to_AZ[name]] += n
            ck(material_signature(event[side]) == expected, 'Actual declaration/model side binding '+event['id']+' '+side)
    return {'new_compiled_columns':24,'independent_B_q_Le_zero':24,'reused_coordinate_identities':9,'no_rate_Q_evaluation':True}


def output_sources_and_coverage(packet_path):
    registry=LEAF/'registry'
    rows=read(registry/'primary_providers.json')['rows']
    source_rows = read(PUBLIC/'PROVIDER_ROWS.json')['rows']+read(PHOTO/'PROVIDER_ROWS.json')['rows']+read(packet_path)['rows']
    ck(len(rows) == len(source_rows) == 26, '26 actual new provider variants')
    for raw in source_rows:
        row=rows[raw['id']]
        ck(row['native_record'] == raw, 'Entire native source record preserved '+raw['id'])
        canonical=json.dumps(raw,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
        ck(row['record_sha256'] == hashlib.sha256(canonical).hexdigest(), 'Provider canonical identity')
    targets=read(registry/'targets.json')['rows']
    ck([r['id'] for r in targets] == list(range(1,20)), '19 target rows preserved')
    ck(sum(len(r['directions']) for r in targets) == 28, '28 original direction rows preserved')
    for r in targets:
        for d in r['directions']:
            ck(d['selected_rate_provider'] is None and d['physical_Q'] is None and d['physical_rate_admission'] is False and d['physical_Q_admission'] is False and d['activation'] is False, 'Target physical admission false')
    photo_status={r['id']:next(d for d in r['directions'] if d['direction']=='target_forward')['supplier_status'] for r in targets if r['id'] in {4,5,6,7,8,11}}
    ck(photo_status == {4:'EXCLUSIVE_SPECTRUM_AVERAGED_MEASUREMENT_POINTWISE_BINDING_UNRESOLVED',5:'EXCLUSIVE_SPECTRUM_AVERAGED_MEASUREMENT_POINTWISE_BINDING_UNRESOLVED',6:'TARGET_DECLARED_PRIMARY_SUPPLIER_MISSING',7:'FACTORIZED_EXCLUSIVE_CANDIDATE_UNEVALUATED',8:'EXCLUSIVE_NATIVE_CHANNEL_SOURCE_REFERENCE_PRESENT',11:'INCLUSIVE_SOURCE_ONLY_EXCLUSIVE_TARGET_UNRESOLVED'}, 'Current photo source classes')
    coverage=read(registry/'coverage.json')
    p=coverage['direct_photonuclear_source_coverage']
    ck((p['exclusive_native_channel_source_count'],p['factorized_exclusive_candidate_count'],p['inclusive_only_source_count'],p['beam_averaged_measurement_direction_count']) == (1,1,1,2), 'Photo class count closure')
    ck(p['no_primary_source_record_reference'] == ['TARGET19:06:target_forward'], 'Actual remaining source dependency')
    ck(len(p['exclusive_source_binding_gaps']) == 5, 'Remaining exclusive native bindings')
    reused=read(registry/'reused_r1_evidence.json')
    ck(reused['recompiled_count'] == 0 and len(reused['rows']) == 24, '24 R1 references without replay')
    saved_events={r['id']:r for r in read(R1/'registry/events.json')['rows']}
    saved_compiled={r['event_id']:r for r in read(R1/'registry/compiled.json')['rows']}
    for eid,r in reused['rows'].items():
        ck(r['recompiled'] is False and r['source_commit']=='18a6804d7cbe4879701e83631f7e908bbb84cef1', 'R1 reused status')
        for key,saved in [('event_record_sha256',saved_events[eid]),('compiled_record_sha256',saved_compiled[eid])]:
            raw=json.dumps(saved,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
            ck(r[key] == hashlib.sha256(raw).hexdigest(), 'R1 saved evidence identity')
    return {'new_provider_rows':26,'photo_source_classes':photo_status,'R1_references_without_recompile':24}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--he4-packet',type=Path,required=True)
    parser.add_argument('--he4-sha256',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise ValueError('Append-only result exists; do not replay')
    cpu=time.process_time();wall=time.monotonic()
    ck(sha(args.he4_packet)==args.he4_sha256,'Explicit final He4 packet identity')
    for name,func in [('frozen_sources_and_manifests',pin_and_manifests),
                      ('primary_rows_and_family_directions',primary_rows),
                      ('all_598_native_NACRE_grid_records',nacre_native_tables),
                      ('other_native_source_rows',selected_source_constants),
                      ('public_numeric_derivative_and_redistribution',public_derivative),
                      ('original_scope_and_saved_results_reuse',recovered_scope_and_reuse),
                      ('native_ENDF_TAB1_and_MF6_fields',photon_native),
                      ('native_He4_measured_tables',lambda:he4_native(args.he4_packet)),
                      ('new_integer_projection_independent_B_q_Le',new_output_projection),
                      ('output_sources_and_current_coverage',lambda:output_sources_and_coverage(args.he4_packet))]:
        group(name,func)
    failed=[r['group'] for r in RESULTS if r['status']=='FAIL']
    report={'schema':'WU_TARGET19_R2_INDEPENDENT_CHANGED_INPUT_CHECK_V1',
            'reviewer':'/root/authority_survey','status':'PASS_SCOPED' if not failed else 'FAIL',
            'scope':'Native source transcription, source class/direction identity, public facts preservation and only 24 new finite integer projections',
            'checker_sha256':sha(Path(__file__)), 'checks':RESULTS,'check_groups':len(RESULTS),
            'assertions':ASSERTIONS,'failed_groups':failed,'input_sha256':INPUTS,
            'CPU_s':time.process_time()-cpu,'wall_s':time.monotonic()-wall,
            'new_rate_evaluations':0,'new_Q_evaluations':0,'native_cross_section_products':0,
            'new_IVPs':0,'old_249_replays':0,'R1_full_suite_replays':0,'PHYS91_or_REI_background_replays':0,
            'physical_admission':False,'global_completion':False}
    with args.output.open('x') as out:
        json.dump(report,out,ensure_ascii=False,indent=2);out.write('\n')
    print(json.dumps({'status':report['status'],'groups':len(RESULTS),'assertions':ASSERTIONS,'failed':failed,'output':str(args.output)},indent=2))
    raise SystemExit(bool(failed))


if __name__=='__main__':
    main()
