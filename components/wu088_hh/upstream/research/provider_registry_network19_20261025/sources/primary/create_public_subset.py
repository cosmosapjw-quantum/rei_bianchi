#!/usr/bin/env python3
"""Produce a publication derivative without altering the frozen source intake."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent
SRC = ROOT/'network19_intake'
DEST = ROOT/'network19_publication_subset'
DEST.mkdir(exist_ok=False)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def wr(name, value):
    p = DEST/name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.open('x', encoding='utf-8').write(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

source_manifest_sha = sha(SRC/'MANIFEST.json')
manifest = json.loads((SRC/'MANIFEST.json').read_text())
excluded = {
    'raw_primary/NACREII_1310.7099.pdf': 'arXiv nonexclusive distribution grant to arXiv; no general CC grant established',
    'derived_text/NACREII_1310.7099.txt': 'Full text of source without established redistribution grant',
    'raw_primary/Dubovichenko2019_pT_1811.04779.pdf': 'arXiv nonexclusive distribution grant to arXiv; no general CC grant established',
    'derived_text/Dubovichenko2019_pT_1811.04779.txt': 'Full text of source without established redistribution grant',
    'raw_primary/Li2015_DDp_1503.08672.html': 'Full paper HTML; arXiv nonexclusive grant is not a general CC grant',
    'raw_primary/JENDL5_He3_T3.html': 'Selected numerical facts retained; explicit full webpage redistribution license not established',
    'raw_primary/NIST_NCNR_neutron_list.html': 'Selected numerical facts retained; source cites externally published NeutronNews data',
    'PROVIDER_ROWS.json': 'Replaced by public numerical-facts derivative; original hash retained',
    'raw_preparation/extract01/PROVIDER_ROWS_FIRST.json': 'Private original contains verbatim/raw formatted duplicate excerpts; hash preserved in frozen manifest',
}

license_rows = [{
    'source': 'raw_primary/Viviani2023_DD.pdf', 'status': 'CC_BY_3_0_EXPLICIT',
    'source_sha256': sha(SRC/'raw_primary/Viviani2023_DD.pdf'),
    'evidence_location': 'PDFpage1 footer; derived_text/Viviani2023_DD.txt',
    'grant_excerpt': 'Content from this work may be used under the terms of the Creative Commons Attribution 3.0 licence.',
    'attribution_required': ['authors', 'worktitle', 'journalcitation', 'DOI', 'licenseURL'],
    'license_url': 'https://creativecommons.org/licenses/by/3.0/',
    'source_url': 'https://inspirehep.net/files/fc3a3fe08ab5d1beaa365ec51e2c7565'}]
for source, arxiv in [('NACREII_1310.7099.pdf', '1310.7099'),
                      ('Dubovichenko2019_pT_1811.04779.pdf', '1811.04779'),
                      ('Li2015_DDp_1503.08672.html', '1503.08672')]:
    license_rows.append({
        'source': source, 'status': 'ARXIV_NONEXCLUSIVE_DISTRIBUTION_ONLY',
        'source_metadata_url': 'https://arxiv.org/abs/'+arxiv,
        'observed_view_license_target': 'https://arxiv.org/licenses/nonexclusive-distrib/1.0/',
        'resolved_license_url': 'https://arxiv.org/licenses/nonexclusive-distrib/1.0/license.html',
        'interpretation': 'Observed distribution grant is to arXiv; no general CC redistribution grant asserted',
        'full_paper_or_full_text_in_public_subset': False})

wr('LICENSE_OBSERVATIONS.json', {
    'schema': 'WU_SOURCE_REDISTRIBUTION_OBSERVATIONS_V1',
    'observed_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'frozen_packet_manifest_sha256': source_manifest_sha,
    'license_evidence': license_rows,
    'numerical_records': 'Keep numerical strings, units, uncertainty facts, exact original-source hashes and locators; remove verbatim prose and duplicate formatted tables',
    'identity_rule': 'Frozen source_file/source_SHA256 identify original bytes, not newly generated excerpts; excluded originals are explicitly marked absent',
    'frozen_packet_edited': False})

original = json.loads((SRC/'PROVIDER_ROWS.json').read_text())
public = copy.deepcopy(original)
removed_paths = []

def strip_excerpts(value, path=''):
    if isinstance(value, dict):
        for key in list(value):
            p = path+'.'+key
            if key in ('raw_literal', 'native_table_literal', 'S0_printed_literal', 'source_statement'):
                removed_paths.append(p)
                del value[key]
            else:
                strip_excerpts(value[key], p)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            strip_excerpts(child, path+'['+str(i)+']')

strip_excerpts(public)
for r in public['rows']:
    r['publication_source_availability'] = {
        'original_bytes_bundled': r['source_file'] not in excluded,
        'original_source_SHA256': r['source_SHA256'],
        'retained_content': 'Numerical facts and source locators; no full-paper excerpt replacement',
        'binding_before_public_filter': 'SOURCE_PARSE_CHECK.json',
        'restore_instruction': 'Fetch source_url and verify original source_SHA256 before source replay'}
    if r['id'].startswith('NACREII'):
        r['support']['S0_definition'] = 'Source section3 usually labels a value near0.5–1.0keV as S0; this is not a new exactzero-energy admission.'
    if r['family_ids'] == ['t_alpha_gamma']:
        r['branch']['inclusive_daughter_states'] = ['ground', 'first_excited']

public['publication_derivative'] = {
    'schema': 'WU_NUMERICAL_FACTS_PUBLIC_DERIVATIVE_V1',
    'original_PROVIDER_ROWS_sha256': sha(SRC/'PROVIDER_ROWS.json'),
    'original_private_packet_manifest_sha256': source_manifest_sha,
    'removed_field_count': len(removed_paths),
    'removed_field_names': ['raw_literal', 'native_table_literal', 'S0_printed_literal', 'source_statement'],
    'numerical_values_unchanged': True,
    'original_source_sha_values_unchanged': True,
    'full_non_CC_papers_excluded': True}
wr('PROVIDER_ROWS.json', public)

for rec in manifest['files']:
    rel = rec['path']
    if rel in excluded:
        continue
    source = SRC/rel
    assert sha(source) == rec['sha256']
    target = DEST/rel
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as out:
        out.write(source.read_bytes())

# The original full-packet inventory is retained as provenance, with a different
# name so it cannot be mistaken for this public bundle's membership list.
(DEST/'PRIVATE_PACKET_MANIFEST.json').open('xb').write((SRC/'MANIFEST.json').read_bytes())

source_bindings = []
for file in sorted({r['source_file'] for r in public['rows']}):
    r = next(r for r in public['rows'] if r['source_file'] == file)
    source_bindings.append({
        'original_source_file': file, 'original_source_SHA256': r['source_SHA256'],
        'original_source_url': r['source_url'], 'original_bytes_bundled': file not in excluded,
        'reason': excluded.get(file, 'Explicit CC BY3.0 license with required attribution'),
        'retained_facts_file': 'PROVIDER_ROWS.json',
        'retained_provider_ids': [x['id'] for x in public['rows'] if x['source_file'] == file]})
wr('SOURCE_REDISTRIBUTION.json', {
    'schema': 'WU_PUBLIC_SOURCE_ORIGINAL_FACTS_BINDING_V1', 'originals': source_bindings,
    'new_rate_admission': False, 'new_Q_admission': False})

notice = '''# Third-party source attribution

The full paper `raw_primary/Viviani2023_DD.pdf` is redistributed under Creative Commons Attribution 3.0 Unported.

M. Viviani, L. Girlanda, A. Kievsky, D. Logoteta and L. E. Marcucci, “Study of the d(d,p)3H and d(d,n)3He processes at low energies,” Journal of Physics: Conference Series 2586 (2023), 012076. DOI: https://doi.org/10.1088/1742-6596/2586/1/012076.

License: https://creativecommons.org/licenses/by/3.0/. Source: https://inspirehep.net/files/fc3a3fe08ab5d1beaa365ec51e2c7565. The PDF bytes are unchanged. `derived_text/Viviani2023_DD.txt` is an automated text extraction. Selected numerical facts are transcribed in `PROVIDER_ROWS.json`. The authors and publisher do not endorse this project through this attribution.

Full NACRE-II and Dubovichenko papers, their full text extracts, and the full Li manuscript HTML are excluded. The public provider file retains numerical facts, original retrieval hashes, source URLs and precise locators. Full JENDL/NIST webpages are also omitted under this conservative publication subset; their selected numerical facts remain. See `LICENSE_OBSERVATIONS.json` and `SOURCE_REDISTRIBUTION.json`.

`PRIVATE_PACKET_MANIFEST.json` inventories the frozen original intake, including excluded originals. It is provenance, not a claim that every original file is bundled publicly. `PUBLICATION_SUBSET_MANIFEST.json` defines this public subset.
'''
(DEST/'THIRD_PARTY_NOTICES.md').open('x').write(notice)

# Preserve the first metadata preparation failure; the rejected command did not
# execute any Python statements or scientific functions.
wr('PUBLIC_FILTER_PREPARATION.json', {
    'schema': 'WU_PUBLIC_FILTER_PREPARATION_V1',
    'first_attempt': {'status': 'PYTHON_PARSE_FAILURE_BEFORE_EXECUTION',
                      'message': "SyntaxError: closing parenthesis '}' does not match opening parenthesis '[' on line18",
                      'files_written': 0, 'scientific_executions': 0},
    'correction': 'Use a standalone script with explicit license_rows construction',
    'successful_transformation': 'Source curation and metadata only',
    'old_suite_replays': 0, 'rate_Q_IVP_evaluations': 0,
    'removed_paths': removed_paths})

# Verify all scientific numeric fields and original identities survived exactly.
for before, after in zip(original['rows'], public['rows']):
    assert before['id'] == after['id']
    assert before['source_SHA256'] == after['source_SHA256']
    expected = copy.deepcopy(before['raw_values'])
    def clean(v):
        if isinstance(v, dict):
            return {k:clean(x) for k,x in v.items() if k not in ('raw_literal', 'native_table_literal', 'S0_printed_literal', 'source_statement')}
        if isinstance(v, list):
            return [clean(x) for x in v]
        return v
    assert clean(expected) == after['raw_values']
    assert before['uncertainty'] == after['uncertainty']
    assert clean(before['Q']) == after['Q']
assert sha(SRC/'MANIFEST.json') == source_manifest_sha

(DEST/'create_public_subset.py').open('xb').write(Path(__file__).read_bytes())
files = [{'path': str(p.relative_to(DEST)), 'bytes': p.stat().st_size, 'sha256': sha(p)}
         for p in sorted(DEST.rglob('*')) if p.is_file()]
wr('PUBLICATION_SUBSET_MANIFEST.json', {
    'schema': 'WU_TARGET19_PUBLICATION_SUBSET_MANIFEST_V2',
    'original_private_packet_manifest_SHA256': source_manifest_sha,
    'original_packet_unchanged': True,
    'public_PROVIDER_ROWS_sha256': sha(DEST/'PROVIDER_ROWS.json'),
    'source_original_identities_unchanged': True,
    'numeric_data_and_uncertainty_unchanged': True,
    'excluded_original_files': [{'path': p, 'sha256': sha(SRC/p), 'reason': why} for p,why in excluded.items()],
    'file_count_excluding_manifest': len(files),
    'total_bytes_excluding_manifest': sum(x['bytes'] for x in files), 'files': files,
    'rate_Q_IVP_evaluations': 0, 'old_suite_replays': 0})
print(json.dumps({'public_PROVIDER_ROWS_sha256': sha(DEST/'PROVIDER_ROWS.json'),
                  'publication_manifest_sha256': sha(DEST/'PUBLICATION_SUBSET_MANIFEST.json'),
                  'file_count_excluding_manifest': len(files),
                  'total_bytes_excluding_manifest': sum(x['bytes'] for x in files),
                  'private_packet_unchanged': True}, indent=2))
