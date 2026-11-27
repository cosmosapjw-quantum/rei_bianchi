"""Read-only byte identity/intake audit. Never imports research implementations.

Writes this lane's metadata under r12_intake/attachments only. It does not
extract archives, open PDF text, execute science, edit the repository, or
allocate an execution allowance.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import json

ROOT = Path('/workspace/scratch/d813e058ed8f')
REPO = ROOT / 'WU088_HH'
OUT = ROOT / 'r12_intake/attachments'
R11 = REPO / 'research/provider_registry_molecular_r11_20261028'
R10 = REPO / 'research/provider_registry_molecular_r10_20261028'


def timestamp():
    now = datetime.now(timezone.utc)
    return {'UTC': now.isoformat(),
            'KST': now.astimezone(timezone(timedelta(hours=9))).isoformat()}


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            sha.update(chunk)
    return sha.hexdigest()


def identity(path, relative_to=ROOT):
    record = {'path': str(path.relative_to(relative_to)), 'exists': path.is_file()}
    if record['exists']:
        record.update(bytes=path.stat().st_size, sha256=digest(path))
    return record


def manifest_check(items):
    rows = []
    for expected in items:
        row = identity(REPO / expected['path'], REPO)
        row['expected'] = {k: expected[k] for k in ('bytes', 'sha256')}
        row['matches'] = (row.get('bytes') == expected['bytes'] and
                          row.get('sha256') == expected['sha256'])
        rows.append(row)
    return {'count': len(rows), 'matching': sum(r['matches'] for r in rows),
            'missing': [r['path'] for r in rows if not r['exists']],
            'mismatched': [r['path'] for r in rows if r['exists'] and not r['matches']],
            'files': rows}


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    started = timestamp()
    basepath = R10 / 'authority/backup_literature/ATTACHMENT_IDENTITY.json'
    baseline = json.loads(basepath.read_text())
    old = {x['name']: x for x in baseline['files']}
    current_paths = sorted(p for p in (ROOT / 'project_sources').iterdir()
                           if p.is_file() and not p.name.startswith('.'))
    current = []
    for path in current_paths:
        row = identity(path)
        row['name'] = path.name
        previous = old.get(path.name)
        row['baseline_present'] = previous is not None
        row['same_size'] = previous is not None and row['bytes'] == previous['bytes']
        row['same_SHA256'] = previous is not None and row['sha256'] == previous['sha256']
        row['relation'] = ('BYTE_IDENTITY' if row['same_size'] and row['same_SHA256']
                           else 'NEW' if previous is None else 'CHANGED')
        current.append(row)
    names = {x.name for x in current_paths}
    missing = sorted(set(old) - names)
    changed = [r['path'] for r in current if r['relation'] != 'BYTE_IDENTITY']
    attachment_result = {
        'schema': 'WU_R12_ATTACHMENT_IDENTITY_INTAKE_V1',
        'started': started, 'finished': timestamp(),
        'scope': 'Current 20 explicitly supplied local project_sources files; SHA256 and byte sizes only.',
        'baseline': identity(basepath, REPO),
        'baseline_source_commit': 'c92e63787ed7f6b50cbec06dd0b8dd2a00ace518',
        'earlier_baseline_url': baseline['baseline_url'],
        'earlier_baseline_Git_blob': baseline['baseline_Git_blob'],
        'count': len(current), 'total_bytes': sum(r['bytes'] for r in current),
        'matching_names_sizes_SHA256': sum(r['relation'] == 'BYTE_IDENTITY' for r in current),
        'changed_or_new_paths': changed, 'missing_baseline_names': missing,
        'status': 'ALL_BYTE_IDENTICAL_REUSE_PRIOR_INVESTIGATION' if not changed and not missing else 'DELTA_REQUIRES_CONTENT_REVIEW',
        'prior_investigation_reused': {
            'archive_member_metadata': baseline['old_archive_member_metadata_reused'],
            'literature_PDF_texts': baseline['old_literature_PDF_text_reused'],
            'source': str((R10 / 'authority/backup_literature/INTAKE_SUMMARY_KO.md').relative_to(REPO)),
            'new_archive_extractions': 0, 'new_OCR': 0, 'new_content_body_reads': 0,
            'reason': 'Exact attachment bytes match the previously investigated inputs.'},
        'scientific_execution': {'production_imports': 0, 'primary': 0, 'reference': 0, 'CAS': 0, 'ODE': 0},
        'input_inference': 'No changed attachment input is identified. Existing HD reactive array/named physical consumer INPUT_PENDING is reused for this attachment scope; no global absence claim.',
        'files': current}
    write('ATTACHMENT_IDENTITY.json', attachment_result)

    baseline_started = timestamp()
    payload_path = R11 / 'SCIENTIFIC_PAYLOAD_MANIFEST.json'
    payload = json.loads(payload_path.read_text())
    encoded = json.dumps(payload['files'], ensure_ascii=False, sort_keys=True,
                         separators=(',', ':')).encode('utf-8')
    payload_check = manifest_check(payload['files'])
    payload_check['manifest_payload_sha256'] = payload['payload_sha256']
    payload_check['recomputed_payload_sha256'] = hashlib.sha256(encoded).hexdigest()
    payload_check['canonical_digest_match'] = (payload_check['recomputed_payload_sha256'] == payload['payload_sha256'])
    freeze = json.loads((R11 / 'raw/PREEXECUTION_FREEZE.json').read_text())
    inputs = json.loads((R11 / 'authority/INPUT_IDENTITY.json').read_text())
    required = ['REPORT_KO.md', 'HANDOFF_KO.md', 'SCIENTIFIC_ADMISSION.json',
                'SCIENTIFIC_PAYLOAD_MANIFEST.json', 'CONTRACT.json', 'DAG.json',
                'WORKFLOW_RECORD.json', 'EXECUTION_LEDGER.json',
                'reviews/C9_FINAL_REVIEW.json', 'reviews/ADMISSION_DELTA_REVIEW.json',
                'authority/closeout_delta/CLOSEOUT_SUMMARY_KO.md',
                'followup/NEXT_INPUT_CONTRACT.json', 'delivery/PUBLICATION_INDEX.json']
    required_rows = [identity(REPO / 'AGENTS.md', REPO)] + [identity(R11 / x, REPO) for x in required]
    dags = [json.loads((REPO / 'research' / leaf / 'DAG.json').read_text()) for leaf in
            ['provider_registry_molecular_r9_20261028', 'provider_registry_molecular_r10_20261028', 'provider_registry_molecular_r11_20261028']]
    ledger = json.loads((R11 / 'EXECUTION_LEDGER.json').read_text())
    workflow = json.loads((R11 / 'WORKFLOW_RECORD.json').read_text())
    review = json.loads((R11 / 'reviews/C9_FINAL_REVIEW.json').read_text())
    delta = json.loads((R11 / 'reviews/ADMISSION_DELTA_REVIEW.json').read_text())
    next_input = json.loads((R11 / 'followup/NEXT_INPUT_CONTRACT.json').read_text())
    publication = json.loads((R11 / 'delivery/PUBLICATION_INDEX.json').read_text())
    freeze_check, input_check = manifest_check(freeze['files']), manifest_check(inputs['files'])
    missing_all = [r['path'] for r in required_rows if not r['exists']] + payload_check['missing'] + freeze_check['missing'] + input_check['missing']
    local = {
        'schema': 'WU_R12_R11_LOCAL_BASELINE_AVAILABILITY_V1',
        'started': baseline_started, 'finished': timestamp(),
        'scope': 'Read-only local file/JSON/hash and admitted-scope inspection; no science rerun or renewed scientific review.',
        'required_documents': required_rows,
        'payload': payload_check, 'preexecution_freeze': freeze_check,
        'inherited_input_identity': input_check,
        'missing_local_paths': sorted(set(missing_all)),
        'source_recovery_required': bool(missing_all or payload_check['mismatched'] or freeze_check['mismatched'] or input_check['mismatched']),
        'DAG_history': {'R9': dags[0]['counts'], 'R10': dags[1]['counts'], 'R11': dags[2]['counts'],
                        'R9_34_objects_unchanged_in_R10': dags[0]['nodes'] == dags[1]['nodes'][:34],
                        'R10_36_objects_unchanged_in_R11': dags[1]['nodes'] == dags[2]['nodes'][:36]},
        'workflow': {k: workflow[k] for k in ('status','workflow_complete','workflow_total','scientific_DAG')},
        'C9': {'status':review['status'], 'open_material_findings':review['open_material_findings'], 'sha256':digest(R11/'reviews/C9_FINAL_REVIEW.json')},
        'admission_delta': {'status':delta['status'], 'open_material_findings':delta['open_material_findings']},
        'allowances': {'R11':{k:ledger[k]['remaining'] for k in ('primary','reference','CAS')},
                       'old_remaining':ledger['old_remaining'], 'global_remaining':ledger['global_remaining'],
                       'full_historical_CPU_s':ledger['full_historical_CPU_s'],
                       'next_unit_allocated':next_input['candidate_next_unit']['new_execution_allowance_allocated']},
        'publication': {'dual_provider_stages':publication['dual_provider_stages'],
                        'own_FINAL_receipt_location':publication['own_FINAL_receipt_location'],
                        'own_FINAL_receipt_status':publication['FINAL_own_receipt_status'],
                        'external_FINAL_receipt_read_in_this_lane':False},
        'physical_status': next_input['current_physical_status'],
        'read_only_boundary': {'repository_edits':0,'production_imports':0,'scientific_primary_runs':0,
                              'scientific_reference_runs':0,'CAS_calls':0,'ODE_runs':0,'external_writes':0,
                              'new_R12_implementation_authored':False}}
    write('R11_LOCAL_AVAILABILITY.json', local)
    print(json.dumps({'attachments':len(current), 'byte_identical':attachment_result['matching_names_sizes_SHA256'],
                      'changed_or_new':len(changed), 'required_docs_present':sum(r['exists'] for r in required_rows),
                      'required_docs_total':len(required_rows), 'payload_matching':payload_check['matching'],
                      'freeze_matching':freeze_check['matching'], 'inherited_inputs_matching':input_check['matching'],
                      'source_recovery_required':local['source_recovery_required'],
                      'DAG_history':local['DAG_history']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
