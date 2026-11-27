"""Build a create-only archival successor; no scientific computation or code execution."""
from pathlib import Path
import csv
import datetime as dt
import hashlib
import html
import io
import json
import re
import shutil
import sqlite3
import tarfile
import zipfile

HERE = Path(__file__).resolve().parent
BASE = HERE / 'base/tree/WU088_HH_LITERATURE_CODE_ARCHIVE_20261001_v1'
NEW = HERE / 'new/payload'
OUT = HERE / 'deliverables'
NAME = 'WU088_HH_LITERATURE_CODE_ARCHIVE_20261001_v2_RECOVERY'
ROOT = OUT / NAME
UTC = dt.datetime.now(dt.timezone.utc).isoformat()
HEAD = '08be330906512eebfe840c40a16b94dc9759e545'
TREE = '58f6042a510eb13abc26842feca45eebd1f14d04'
COLLECTOR = '46a0889ed4b0cd775117541f91d3cad4557dd7e5'
EXPECTED_ORIGINAL = 'ab875d3e4fa771b34bdc1026042c38553b473b98f23e00e809d21c3b367948a9'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def writej(p, data):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def writecsv(p, rows, fields):
    with Path(p).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                        for k, v in row.items()})


def seal(root):
    excluded = ['ARTIFACT_MANIFEST.json', 'MANIFEST.sha256']
    members = [{'path': str(p.relative_to(root)), 'bytes': p.stat().st_size, 'sha256': sha(p)}
               for p in sorted(root.rglob('*')) if p.is_file() and p.name not in excluded]
    writej(root / excluded[0], {'schema': 'WU088_RECOVERY_ARTIFACT_MANIFEST_V2',
                              'self_excluded': excluded, 'files': members})
    (root / excluded[1]).write_text(''.join(x['sha256'] + '  ' + x['path'] + '\n' for x in members))
    return members


def create_zip(root, path, members=None):
    files = sorted(p for p in root.rglob('*') if p.is_file()) if members is None else members
    with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in files:
            z.write(p, str(Path(root.name) / p.relative_to(root)))
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
    return {'filename': path.name, 'bytes': path.stat().st_size, 'sha256': sha(path)}


def reconstruct_report_db():
    recon = OUT / 'WU088_HH_R31AO_LITERATURE_DATABASE_RECONSTRUCTED_20261001_v1'
    recon.mkdir()
    report = (BASE / 'research_report/DEEP_RESEARCH_REPORT.md').read_text()
    sql = re.search(r'### Machine-actionable schema\s+```sql\n(.*?)```', report, re.S).group(1)
    (recon / 'schema.sql').write_text(sql)
    csvs = re.findall(r'```csv\n(.*?)```', report, re.S)
    db = sqlite3.connect(recon / 'wu088_r31ao_literature_RECONSTRUCTED.db')
    db.executescript(sql)
    counts = {}
    for text in csvs:
        rows = list(csv.DictReader(io.StringIO(text)))
        if not rows:
            continue
        table = 'sources' if 'source_id' in rows[0] else 'blockers' if 'blocker_id' in rows[0] else None
        if table is None:
            continue
        fields = list(rows[0]); (recon / (table + '_EXPLICIT_REPORT_EXAMPLES.csv')).write_text(text)
        for row in rows:
            db.execute('INSERT INTO ' + table + '(' + ','.join(fields) + ') VALUES(' +
                       ','.join('?' for _ in fields) + ')', [row[x] for x in fields])
        counts[table] = len(rows)
    db.executescript('CREATE TABLE reconstruction_provenance(key TEXT PRIMARY KEY,value_json TEXT);')
    provenance = {'original_deep_research_db_recovered': False,
                  'original_expected_reported_sha256': EXPECTED_ORIGINAL,
                  'semantic_equivalence_to_lost_database': 'UNVERIFIED_NOT_CLAIMED',
                  'populated_rows': counts,
                  'original_report_claimed_counts': {'sources': 19, 'theorems': 9, 'code_modules': 9,
                                                     'tests': 15, 'artifacts': 7, 'blockers': 8},
                  'unrecoverable_export_rows': 'Original complete rows are unavailable; only explicit CSV examples are inserted.',
                  'all_report_tables_retained_as_markdown': True,
                  'execution_status': 'NOT_EXECUTED', 'report_sha256': sha(BASE / 'research_report/DEEP_RESEARCH_REPORT.md')}
    db.execute('INSERT INTO reconstruction_provenance VALUES(?,?)', ('status', json.dumps(provenance)))
    db.commit(); assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'; db.close()
    shutil.copy2(BASE / 'research_report/DEEP_RESEARCH_REPORT.md', recon / 'RECOVERABLE_ORIGINAL_REPORT.md')
    shutil.copy2(BASE / 'catalog/sources.csv', recon / 'ACQUISITION_SOURCE_CROSSWALK_NOT_ORIGINAL_DB.csv')
    writej(recon / 'RECONSTRUCTION_STATUS.json', provenance)
    (recon / 'README_KO.md').write_text(
        '# 연구 DB의 부분 재구성\n\n원 ZIP bytes를 복원하지 못했다. 이 DB는 원 보고서에 명시된 SQL schema와 '
        'sources 4개·blockers 5개 CSV 예제만 복원한다. 원 보고서가 주장한 전체 19/9/9/15/7/8 record와 '
        '동등하다고 주장하지 않는다. 복구 가능한 전체 보고서·표 및 acquisition catalog crosswalk를 함께 보존한다. '
        '미공개 원 record를 만들어 채우지 않았으며, theorem/module/test/artifact 테이블은 빈 상태다. '
        '원 보고서의 계획과 OPEN blocker는 새 실행 승인이나 현재 과학 판정으로 승격되지 않는다.\n')
    seal(recon)
    identity = create_zip(recon, OUT / (recon.name + '.zip'))
    return recon, identity, provenance


def main():
    OUT.mkdir(exist_ok=True); ROOT.mkdir()
    shutil.copytree(BASE, ROOT / 'previous_v1')
    shutil.copytree(NEW, ROOT / 'recovery')
    (ROOT / 'catalog').mkdir(); (ROOT / 'provenance').mkdir(); (ROOT / 'scripts').mkdir()
    shutil.copy2(HERE / 'collect_recovery.py', ROOT / 'scripts/collect_recovery.py')
    shutil.copy2(Path(__file__), ROOT / 'scripts/build_successor.py')
    shutil.copy2(HERE / 'workflow.yml', ROOT / 'provenance/EXECUTED_ONE_SHOT_WORKFLOW.yml')
    shutil.copy2(HERE / 'new/transport/TRANSPORT.json', ROOT / 'provenance/RECOVERY_TRANSPORT_RECEIPT.json')
    shutil.copy2(HERE / 'evidence_sources.json', ROOT / 'provenance/RETRIEVAL_EVIDENCE.json')
    shutil.copy2(HERE / 'PAYLOAD_INSPECTION.json', ROOT / 'provenance/PAYLOAD_INSPECTION.json')
    shutil.copy2(HERE.parent / 'upload/Pasted text(20260930-214610).txt', ROOT / 'provenance/TASK_CONTRACT.txt')

    originals = json.loads((BASE / 'catalog/sources.json').read_text())
    original_by_id = {s['id']: s for s in originals}
    target_set = [s for s in originals if s['status'] != 'ACQUIRED']
    assert {x['id'] for x in target_set} == {'C11', 'C12', 'P04', 'P06', 'URL10', 'URL11', 'URL24', 'URL25', 'URL26'}
    writej(ROOT / 'catalog/RECOVERY_TARGET_SET.json', target_set)
    results = json.loads((NEW / 'ACQUISITION_RESULTS.json').read_text())
    assert all(r['acquisition_status'] == 'ACQUIRED' for r in results)
    result_by_id = {r['id']: r for r in results}
    recoveries = []
    records = []
    added_assets = []
    equivalence = {'P04_RECOVERY': 'PREPUBLICATION_SAME_WORK',
                   'P06_RECOVERY': 'EXACT_PUBLISHER_VERSION',
                   'C14_CINTE': 'OFFICIAL_SOURCE_BYTES', 'C14_DESCRIPTION': 'OFFICIAL_DOCUMENTATION',
                   'C12_OFFICIAL': 'OFFICIAL_DOCUMENTATION', 'C12_MANUAL': 'OFFICIAL_DOCUMENTATION'}
    record_ids = {'P04_RECOVERY': 'P04-R2', 'P06_RECOVERY': 'P06-R2', 'C14_CINTE': 'C14',
                  'C14_DESCRIPTION': 'C14-DOCS-R2', 'C12_OFFICIAL': 'C12-WEB-R2',
                  'C12_MANUAL': 'C12-MANUAL-R2'}
    titles = {'C14_CINTE': 'Petras cinte: official unversioned PASCAL-XSC source archive',
              'C14_DESCRIPTION': 'Petras cinte official package description',
              'C12_OFFICIAL': 'COSY official registration and source distribution page',
              'C12_MANUAL': "COSY INFINITY 10.2 Programmer's Manual, April 2023"}
    for r in results:
        sid = record_ids[r['id']]; parent = r['parent_id']
        if parent == 'C14_CINTE':
            parent = 'C14'
        old = original_by_id.get(parent, {})
        record = {'id': sid, 'parent_source_id': parent if sid != 'C14' else None,
                  'title': titles.get(r['id'], old.get('title')),
                  'source_type': 'code' if sid == 'C14' else 'paper' if sid.startswith(('P04', 'P06')) else 'documentation_or_metadata',
                  'scope': 'ACQUISITION_RECOVERY', 'status': 'ACQUIRED',
                  'acquisition_status': 'ACQUIRED', 'requested_identity': old.get('doi') or old.get('title') or titles.get(r['id']),
                  'acquired_representation': r['representation'],
                  'representation_equivalence': equivalence[r['id']],
                  'publisher_version_available': False if sid == 'P04-R2' else True if sid == 'P06-R2' else None,
                  'publisher_direct_download_acquired': False,
                  'assets': [], 'attempts': r['attempts'], 'fallback_chain': r['urls'],
                  'retrieved_utc': r['assets'][0]['acquisition_utc'],
                  'remaining_gap': 'Final publisher revision/numbering comparison unavailable' if sid == 'P04-R2' else None,
                  'restore_verified': False, 'backup_object_ids': None,
                  'backup_binding': 'DETACHED_FINAL_RETURN_AND_BACKUP_RECEIPT',
                  'doi': old.get('doi'), 'authors': old.get('authors'), 'year': old.get('year'),
                  'version_or_ref': '10.2' if parent == 'C12' else 'unversioned current official archive' if sid == 'C14' else '',
                  'theorem_authority_automatically_promoted': False,
                  'acquisition_is_scientific_validation': False}
        for i, a in enumerate(r['assets']):
            asset = dict(a, path='recovery/' + a['path'], asset_id=sid + '-A' + str(i+1), source_id=sid,
                         requested_url=a['original_source_url'], retrieved_utc=a['acquisition_utc'],
                         representation=a['acquired_representation'])
            record['assets'].append(asset); added_assets.append(asset)
        if sid == 'P06-R2':
            record['equivalence_evidence'] = 'Author-hosted journal scan: title, both authors, issue/date, pages 1170-1186 (17 pages), section/equation/theorem numbering in the published layout. Publisher-served PDF byte equality NOT verified.'
        if sid == 'P04-R2':
            record['equivalence_evidence'] = 'Institutional software index identifies this as the same titled Petras preprint; PostScript title/author/abstract verified from literal text without execution. 15 pages; TeX source timestamp 2000-12-19. Final article is 2002; substantive and numbering differences unresolved.'
            record['source_format'] = 'postscript_not_pdf'
            record['manuscript_revision_timestamp'] = '2000-12-19T12:49 (TeX timestamp, timezone unavailable)'
        records.append(record)

    def update(parent, child, status, gap=None, assets=None):
        record = next((x for x in records if x['id'] == child), None)
        recoveries.append({'source_id': parent, 'successor_record_id': child,
                           'acquisition_status': status, 'requested_identity': original_by_id.get(parent, {}).get('doi') or original_by_id.get(parent, {}).get('title', child),
                           'acquired_representation': record.get('acquired_representation') if record else 'existing_acquired_equivalent',
                           'representation_equivalence': record.get('representation_equivalence') if record else None,
                           'remaining_gap': gap, 'closed': status.startswith('ACQUIRED'),
                           'asset_paths': [a['path'] for a in (assets if assets is not None else record.get('assets', []) if record else [])]})
    update('P04', 'P04-R2', 'ACQUIRED_AUTHOR_MANUSCRIPT', 'Final publisher comparison remains unresolved; preprint full text acquired.')
    update('P06', 'P06-R2', 'ACQUIRED_INSTITUTIONAL_PUBLISHER_SCAN')
    update('C14', 'C14', 'ACQUIRED_OFFICIAL_UNVERSIONED_SOURCE_ARCHIVE')
    update('C12', 'C12-MANUAL-R2', 'NOT_ACQUIRED_SOURCE_REGISTRATION_REQUIRED_DOCUMENTATION_ACQUIRED',
           'Source requires personal registration and signed licence; no login, registration, signature or purchase performed.')
    c11 = dict(original_by_id['C11'], id='C11-R2', parent_source_id='C11',
               acquisition_status='NOT_ACQUIRED_PERSONAL_PAID_LICENSE_REQUIRED',
               requested_identity='INTLAB 14.1', acquired_representation='metadata_only',
               representation_equivalence='UNRESOLVED', remaining_gap='Personal paid source licence required; official conditions retained as D06.',
               fallback_chain=['https://www.tuhh.de/ti3/rump/intlab/', 'https://www.tuhh.de/ti3/rump/intlab/Obtain_INTLAB.shtml'],
               restore_verified=False, backup_object_ids=None)
    records.append(c11); update('C11', 'C11-R2', 'NOT_ACQUIRED_PERSONAL_PAID_LICENSE_REQUIRED', c11['remaining_gap'])

    for sid, equivalent in {'URL10':'P08', 'URL11':'P06-R2', 'URL24':'P05', 'URL25':'P09', 'URL26':'P04-R2'}.items():
        target = next((x for x in records if x['id'] == equivalent), original_by_id.get(equivalent))
        assets = [dict(a, path='previous_v1/' + a['path']) for a in target['assets']] if equivalent in original_by_id else target['assets']
        x = dict(original_by_id[sid], id=sid+'-R2', parent_source_id=sid,
                 status='ACQUIRED_EQUIVALENT_CONTENT_REFERENCE', acquisition_status='ACQUIRED_EQUIVALENT_CONTENT_REFERENCE',
                 acquired_representation=target.get('acquired_representation', 'existing_full_text'),
                 representation_equivalence='RELATED_CITATION_RESOLVED_TO_SAME_WORK', equivalent_source_id=equivalent,
                 requested_url_snapshot_available=False, assets=[],
                 equivalent_asset_paths=[a['path'] for a in assets],
                 remaining_gap='Exact cited URL snapshot remains unavailable; full-text equivalent is linked without redownload.',
                 restore_verified=False, backup_object_ids=None)
        records.append(x); update(sid, x['id'], x['acquisition_status'], x['remaining_gap'], assets)

    recon, recon_identity, reconstruction = reconstruct_report_db()
    (ROOT / 'reconstructed_database').mkdir()
    shutil.copy2(OUT / recon_identity['filename'], ROOT / 'reconstructed_database' / recon_identity['filename'])
    writej(ROOT / 'reconstructed_database/ORIGINAL_DATABASE_RECOVERY_STATUS.json', reconstruction)

    # Keep the original SQL rows and their record_json unchanged; append versioned records.
    original_db = sqlite3.connect(BASE / 'catalog/acquisition.sqlite')
    db = sqlite3.connect(ROOT / 'catalog/acquisition.sqlite'); original_db.backup(db)
    db.executescript('''
      CREATE TABLE recovery_updates(source_id TEXT PRIMARY KEY, successor_record_id TEXT,
        acquisition_status TEXT, remaining_gap TEXT, closed INTEGER, record_json TEXT NOT NULL);
      CREATE TABLE representation_identity(source_id TEXT PRIMARY KEY, requested_identity TEXT,
        acquired_representation TEXT, representation_equivalence TEXT, publisher_version_available INTEGER,
        fallback_chain TEXT, version_selection_rule TEXT, version_requested TEXT, version_acquired TEXT,
        version_is_latest_stable INTEGER, commit_sha TEXT, tree_sha TEXT, source_sha256 TEXT,
        bytes INTEGER, license TEXT, retrieved_utc TEXT, failure_class TEXT, remaining_gap TEXT,
        backup_object_ids TEXT, restore_verified INTEGER NOT NULL DEFAULT 0);
      CREATE TABLE recovery_artifacts(id TEXT PRIMARY KEY,status TEXT,record_json TEXT);
      CREATE VIEW effective_sources AS SELECT s.id,s.title,s.source_type,
        coalesce(r.acquisition_status,s.status) AS acquisition_status,
        r.successor_record_id,r.remaining_gap FROM sources s
        LEFT JOIN recovery_updates r ON s.id=r.source_id
        WHERE s.id IN (SELECT id FROM sources WHERE scope!='ACQUISITION_RECOVERY') OR s.id='C14';
      CREATE VIEW effective_assets AS SELECT asset_id,source_id,
        CASE WHEN path LIKE 'recovery/%' THEN path ELSE 'previous_v1/'||path END AS package_path,
        bytes,sha256,representation,requested_url,final_url,retrieved_utc FROM assets;
    ''')
    for r in records:
        db.execute('INSERT INTO sources VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                   (r['id'], r['title'], r['source_type'], 'ACQUISITION_RECOVERY', r['status'],
                    r.get('acquisition_status'), r.get('version_or_ref'), None, None,
                    r.get('doi'), r.get('arxiv'), r.get('year'), r.get('authors'), json.dumps(r, ensure_ascii=False)))
        for i, attempt in enumerate(r.get('attempts', [])):
            db.execute('INSERT INTO attempts VALUES(?,?,?)', (r['id'], i+1, json.dumps(attempt)))
        a = r.get('assets', [{}])[0] if r.get('assets') else {}
        db.execute('INSERT INTO representation_identity VALUES('+','.join('?' for _ in range(20))+')',
                   (r['id'], r.get('requested_identity'), r.get('acquired_representation'), r.get('representation_equivalence'),
                    r.get('publisher_version_available'), json.dumps(r.get('fallback_chain', [])),
                    'LATEST_OFFICIAL_DOCUMENTED_STABLE' if r['id'].startswith('C12') else 'OFFICIAL_UNVERSIONED_BYTES' if r['id']=='C14' else None,
                    r.get('version_or_ref'), r.get('version_or_ref'), None, None, None, a.get('sha256'), a.get('bytes'),
                    None, r.get('retrieved_utc'), None, r.get('remaining_gap'), None, 0))
    for a in added_assets:
        db.execute('INSERT INTO assets VALUES(?,?,?,?,?,?,?,?,?,?)',
                   (a['asset_id'], a['source_id'], a['path'], a['bytes'], a['sha256'], a['representation'],
                    a['requested_url'], a['final_url'], a['retrieved_utc'], json.dumps(a)))
    for r in recoveries:
        db.execute('INSERT INTO recovery_updates VALUES(?,?,?,?,?,?)',
                   (r['source_id'], r['successor_record_id'], r['acquisition_status'], r['remaining_gap'], int(r['closed']), json.dumps(r)))
    db.execute('INSERT INTO recovery_artifacts VALUES(?,?,?)', ('ORIGINAL_DEEP_RESEARCH_DB', 'NOT_RECOVERED_REPORT_PARTIALLY_RECONSTRUCTED', json.dumps(reconstruction)))
    db.execute('INSERT INTO metadata VALUES(?,?)',('successor_path_namespace',json.dumps({'legacy_assets_root':'previous_v1/','new_assets_root':'recovery/','path_resolver_view':'effective_assets'})))
    db.commit()
    baseline_rows_unchanged = True
    for table in ['sources','assets','attempts','relations','blocker_map','citation_occurrences','metadata']:
        cols = [x[1] for x in original_db.execute('PRAGMA table_info('+table+')')]
        base_rows = original_db.execute('SELECT * FROM '+table).fetchall()
        for row in base_rows:
            query = 'SELECT 1 FROM '+table+' WHERE '+' AND '.join(c+' IS ?' for c in cols)+' LIMIT 1'
            if db.execute(query,row).fetchone() is None:
                baseline_rows_unchanged = False
    assert baseline_rows_unchanged
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert db.execute('SELECT count(*) FROM effective_sources').fetchone()[0] == 68
    db.close(); original_db.close()

    code_info = []
    for r in originals:
        if r['source_type'] != 'code':
            continue
        a = r.get('assets', [{}])[0] if r.get('assets') else {}
        code_info.append({'source_id': r['id'], 'repository': r.get('repo'), 'release_tag_version': r.get('version_or_ref'),
                          'commit_sha': r.get('resolved_commit'), 'tree_sha': r.get('resolved_tree'),
                          'release_date': None, 'release_date_status':'not independently resolved; acquisition/header timestamps are not release dates',
                          'source_archive_sha256':a.get('sha256'), 'bytes':a.get('bytes'), 'license':None,
                          'license_status':'see retained upstream archive/documents; no inferred licence', 'dependencies':None,
                          'dependencies_status':'not installed or resolved by archival acquisition',
                          'canonical_upstream_url':a.get('requested_url') or r.get('urls'),
                          'acquisition_utc':a.get('retrieved_utc'), 'authority_role':r.get('role',r.get('scope')),
                          'version_selection_rule':'PRESERVE_EXISTING_PIN_OR_ACQUIRED_IDENTITY', 'original_identity_unchanged':True})
    code_info.append({'source_id':'C12','repository':'https://www.bmtdynamics.org/cosy/', 'release_tag_version':'10.2',
                      'commit_sha':None,'tree_sha':None,'release_date':None,'source_archive_sha256':None,'bytes':None,
                      'license':'Personal registered noncommercial licence; commercial licence separately', 'dependencies':None,
                      'canonical_upstream_url':'https://www.bmtdynamics.org/cosy/', 'acquisition_utc':result_by_id['C12_MANUAL']['assets'][0]['acquisition_utc'],
                      'authority_role':'SURVEY_REFERENCE_ONLY_NOT_PROJECT_BACKEND', 'version_selection_rule':'LATEST_OFFICIAL_DOCUMENTED_STABLE_TARGET',
                      'version_requested':'10.2','version_acquired':None,'documentation_version_acquired':'10.2',
                      'version_is_latest_stable':True,'source_acquired':False})
    cinte = result_by_id['C14_CINTE']['assets'][0]
    code_info.append({'source_id':'C14','repository':'https://www2.math.uni-wuppertal.de/wrswt/xsc/pascal-xsc/software/petras/',
                      'release_tag_version':None,'commit_sha':None,'tree_sha':None,'release_date':None,
                      'source_archive_sha256':cinte['sha256'],'bytes':cinte['bytes'],'license':None,
                      'license_status':'No explicit licence file found; official public preservation copy, not public redistribution permission',
                      'dependencies':['PASCAL-XSC compiler and libraries (historical description cites 2.7.2.1)'],
                      'canonical_upstream_url':cinte['original_source_url'],'acquisition_utc':cinte['acquisition_utc'],
                      'authority_role':'HISTORICAL_METHOD_REFERENCE_NOT_COSY_SUBSTITUTE',
                      'version_selection_rule':'NO_OFFICIAL_RELEASE_TAG_OR_GIT_REPOSITORY_IDENTIFIED; CURRENT_OFFICIAL_UNVERSIONED_ARCHIVE_BYTES_PINNED',
                      'version_is_latest_stable':None,'source_acquired':True,'executed':False})
    writej(ROOT/'catalog/CODE_VERSION_POLICY.json',code_info)
    writej(ROOT/'catalog/sources_successor_records.json',records)
    writej(ROOT/'catalog/recovery_updates.json',recoveries)

    remaining = [
        {'source_id':'C11','requested_identity':'INTLAB 14.1 source package','failure_class':'PERSONAL_PAID_LICENSE_REQUIRED',
         'remaining_gap':'Raw code package unavailable through authorized public routes; licence conditions retained.', 'minimum_next_action':'User obtains a personal authorised package and supplies its bytes; no purchase or registration performed.'},
        {'source_id':'C12','requested_identity':'COSY INFINITY 10.2 source package','failure_class':'PERSONAL_REGISTRATION_SIGNED_LICENSE_REQUIRED',
         'remaining_gap':'Latest documented stable target and official 110-page manual acquired; source is restricted to registered users.',
         'minimum_next_action':'User supplies personally licensed source; CINTE does not replace COSY.'},
        {'source_id':'ORIGINAL_DEEP_RESEARCH_DB','requested_identity':'WU088_HH_R31AO_LITERATURE_DATABASE_20261001.zip',
         'failure_class':'ORIGINAL_BYTES_NOT_FOUND_IN_ACCESSIBLE_ARTIFACTS', 'expected_reported_sha256':EXPECTED_ORIGINAL,
         'remaining_gap':'Library exact/short filename searches, Drive search and specified Dropbox folder did not reveal the original ZIP. Partial report/schema reconstruction is explicitly distinct.',
         'minimum_next_action':'If the originating thread still exposes the ZIP, supply it for exact hash verification.'}]
    writej(ROOT/'catalog/missing_sources.json',remaining)
    fields=['source_id','successor_record_id','acquisition_status','requested_identity','acquired_representation','representation_equivalence','remaining_gap','closed','asset_paths']
    writecsv(ROOT/'sources_recovered.csv',[r for r in recoveries if r['closed']],fields)
    writecsv(ROOT/'sources_remaining.csv',remaining,['source_id','requested_identity','failure_class','remaining_gap','minimum_next_action'])
    summary = {'schema':'WU088_ACQUISITION_RECOVERY_V2','created_utc':UTC,'inspected_head':HEAD,'inspected_tree':TREE,
               'collector_commit':COLLECTOR,'collector_tree':'8ff35c2c729191dd097cfcd9e7b45c126600f041',
               'identified_sources_total':69,'canonical_source_records':68,'original_database_artifact_targets':1,
               'baseline_catalog_records':67,'baseline_previously_acquired_reused':58,'baseline_payloads_hash_verified':168,
               'baseline_tree_files_reused':169,'baseline_missing_status_records':9,'recovery_target_total_including_original_db':10,
               'newly_acquired':3,'new_payload_assets':6,'publisher_originals_acquired':0,'arxiv_preprints_acquired':0,
               'author_manuscripts_acquired':1,'institutional_manuscripts_acquired':1,'code_archives_acquired':1,
               'failed_citation_records_resolved_via_full_text':5,'baseline_missing_status_records_closed':7,
               'explicit_pins_preserved':True,'latest_stable_target_selected_where_available':True,
               'latest_stable_used_where_unpinned':False,
               'latest_stable_note':'COSY 10.2 selected, official documentation acquired, source not acquired. CINTE has no identified stable version/tag or Git repository; current official bytes preserved.',
               'original_deep_research_db_recovered':False,'reconstructed_db_created':True,
               'reconstructed_db':recon_identity,'reconstruction_semantic_equivalence':'UNVERIFIED_NOT_CLAIMED',
               'still_missing':remaining,'science_commands':0,'science_producer_commands':0,
               'numerical_certificate_runs':0,'downloaded_code_executions':0,'native_builds':0,
               'science_authority_preserved':{'order_verdict':'B_ORDER_VERDICT_STABLE_OVER_128_160_192',
                                            'source_accuracy':'SOURCE_ACCURACY_BOUND_UNAVAILABLE',
                                            'rigorous_reference':'RIGOROUS_REFERENCE_CERTIFICATION_BLOCKED_BY_MISSING_ERROR_BOUND',
                                            'certified_epsilon':None,'certified_eta':None,'rigorous':False},
               'RESTORE_VERIFIED':False,'local_v1_restore_and_hash_check':True,
               'local_encrypted_transport_decryption_and_hash_check':True,
               'backup_receipt_binding':'DETACHED_FINAL_RETURN_AND_BACKUP_RECEIPT',
               'completion_status':'LITERATURE_ACQUISITION_COMPLETE_WITH_DOCUMENTED_UNOBTAINABLE_ITEMS'}
    writej(ROOT/'acquisition_recovery.json',summary)

    rows=[]; index=['# Complete source index\n','The effective source view overlays versioned recovery records; original records remain unchanged.\n',
                   '| ID | Source | Effective status | Available payloads |','|---|---|---|---|']
    allcanonical=originals+[next(r for r in records if r['id']=='C14')]
    update_by_id={r['source_id']:r for r in recoveries}
    for source in allcanonical:
        u=update_by_id.get(source['id']);status=u['acquisition_status'] if u else source['status']
        paths=u['asset_paths'] if u else ['previous_v1/'+a['path'] for a in source.get('assets',[])]
        links='; '.join('['+Path(p).name+']('+p+')' for p in paths) or 'metadata / documented gap'
        index.append('| '+source['id']+' | '+source['title'].replace('|','/')+' | '+status+' | '+links+' |')
        rows.append('<tr><td>'+html.escape(source['id'])+'</td><td>'+html.escape(source['title'])+'</td><td>'+html.escape(status)+'</td><td>'+
                    ('<br>'.join('<a href="'+html.escape(p)+'">'+html.escape(Path(p).name)+'</a>' for p in paths) or 'metadata / documented gap')+'</td></tr>')
    (ROOT/'COMPLETE_SOURCE_INDEX.md').write_text('\n'.join(index)+'\n')
    (ROOT/'INDEX.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><title>WU088 literature recovery v2</title>'
        '<style>body{font:15px system-ui;max-width:1500px;margin:30px auto}td,th{border:1px solid #bbb;padding:7px}table{border-collapse:collapse}</style>'
        '<h1>WU088 literature recovery v2</h1><p>기존 168 payload 검증·재사용. 원문 2편, 소스 1개 신규 확보. 과학 계산 없음.</p>'
        '<p><a href="ACQUISITION_RECOVERY_REPORT.md">Report</a> · <a href="STILL_MISSING.md">Remaining gaps</a> · '
        '<a href="catalog/acquisition.sqlite">Successor database</a></p><table><tr><th>ID</th><th>Source</th><th>Status</th><th>Payload</th></tr>'+''.join(rows)+'</table></html>')
    still='# Still missing\n\n전체 identified source를 모두 확보한 상태가 아니다. 남은 항목은 다음 3개다.\n\n'
    still+='| ID | Gap | 최소 후속 조치 |\n|---|---|---|\n'+''.join('| '+r['source_id']+' | '+r['remaining_gap']+' | '+r['minimum_next_action']+' |\n' for r in remaining)
    still+='\n기존 실패 웹 URL 5개는 원문 equivalent로 연결했으나 원 URL snapshot bytes가 복원된 것은 아니다. '
    still+='Petras preprint와 2002 final 사이의 정리·식 번호와 substantive 차이는 final을 확보하지 못해 unresolved다. '
    still+='Git history/submodules/signature verification에 관한 v1의 한계도 유지한다.\n'
    (ROOT/'STILL_MISSING.md').write_text(still)
    report=f'''# WU088_HH 문헌 확보 복구 보고서 — 2026-10-01

상태: **LITERATURE_ACQUISITION_COMPLETE_WITH_DOCUMENTED_UNOBTAINABLE_ITEMS**.
기존 acquired 58 source record와 hash 검증된 168 payload를 재사용했다. 원문 2편·소스 1개를 새로 확보했고, 신규 파일은 설명·공식 문서를 포함하여 6개다. 기존 status!=ACQUIRED 9건 중 7건을 원문/동일 논문 reference로 닫았다. INTLAB·COSY raw source와 원 Deep Research DB ZIP은 미확보다.

## 원격·원 archive identity

- inspected HEAD/tree: `{HEAD}` / `{TREE}`.
- archive/infrastructure-only collector HEAD/tree: `{COLLECTOR}` / `8ff35c2c729191dd097cfcd9e7b45c126600f041`.
- v1: 106272651 bytes; SHA256 `df453c892349f622258edd7ee65939338be39f781a22921c6916e7d30876f508`.
- v1의 169 ZIP member 전체를 `previous_v1/`에 보존했다. 원 manifest의 168 payload hash/size가 모두 일치한다. 기존 acquired source를 upstream에서 다시 다운로드하지 않았다.

## 새 원문·코드의 representation

| Work | 확보 형식·경로 | 검증·authority 상태 |
|---|---|---|
| Petras, DOI 10.1016/S0377-0427(01)00586-6 | Wuppertal 공개 author preprint `vipaf.ps`, 15 pages | PostScript magic·제목·저자·abstract literal 및 기관 index 확인. TeX timestamp 2000-12-19. `PREPUBLICATION_SAME_WORK`; 2002 publisher PDF 확보 아님. Final의 정리/식 번호·revision 차이는 unresolved. |
| Gautschi–Varga, DOI 10.1137/0720087 | Purdue 저자 archive의 17-page journal scan `085.pdf` | PDF magic·1983 issue·저자·제목·1170–1186 page range·게재 layout 확인. `institutional_repository`; `EXACT_PUBLISHER_VERSION`은 게재 layout 분류다. Publisher-served PDF와의 byte equality는 미검증이며 publisher direct acquisition count는 0이다. |
| Petras `cinte` | Wuppertal 공식 current unversioned `cinte.tgz` | 13 archive members, 모든 regular member size·압축 읽기 검증. Source snapshot만 보존. Stable version/tag/Git repository 식별 불가; current upstream bytes hash로 pin. COSY 대체 구현으로 취급하지 않는다. |
| COSY INFINITY | 공식 download/registration page 및 10.2 Programmer's Manual, 110 pages, April 2023 | 최신 공식 공개 문서에서 10.2를 선택했다. 개인 등록·서명 licence가 필요한 raw source는 확보하지 않았다. |

R31AO에서 현재 고정된 실제 API authority는 FLINT 3.4.0의 `acb_calc`/`acb_hypgeom` source/documentation이다. 새 Petras/Gautschi 파일은 방법론·문헌 계보를 보존하며, 기존 endpoint theorems A–E나 callback contract의 정리 authority를 자동 교체하지 않는다. 새 manuscript의 theorem/equation 번호를 실행 certificate에 binding하지 않았다. 원문을 읽어 보존했다는 사실과 numerical certificate를 만들었다는 사실은 별개다.

## 실패 citation 5건의 closure

| 기존 ID | 보존한 equivalent |
|---|---|
| URL10, SIAM Accurate Sum and Dot Product | 기존 P08 원문 재사용 |
| URL11, SIAM Gautschi–Varga | P06-R2 저자 archive scan |
| URL24, ResearchGate Taylor Models | 기존 P05 원문 재사용 |
| URL25, ResearchGate Richardson estimate | 기존 P09 원문·코드 재사용 |
| URL26, ScienceDirect Petras | P04-R2 기관 preprint |

원 URL의 실패 evidence와 기존 immutable record는 그대로 유지했다. URL snapshot 확보와 논문 원문 확보를 혼동하지 않는다. Successor DB의 `effective_sources`, `recovery_updates`, `representation_identity`가 새 상태를 제공한다.

## Version 선택

FLINT project pin **3.4.0** 및 기존 NumPy **2.3.5**, MPFR **4.2.2**, GMP **6.3.0**, MPFI **1.5.4**, INTLAB target **14.1**, 기존 resolved commit/tree를 보존했다. FLINT 3.6.0의 기존 shadow archive도 재사용하며 project pin으로 승격하지 않았다. COSY에는 기존 구현 pin이 없어서 공식 10.2 stable document target을 선택했다. raw source는 registration 때문에 미확보이며, 따라서 `latest_stable_used_where_unpinned=false`는 안정판 source를 확보·사용했다고 주장하지 않는다는 뜻이다. `latest_stable_target_selected_where_available=true`. CINTE는 upstream에 release/tag/Git가 식별되지 않아 version/commit/tree/release date를 null로 두고 current official archive bytes만 pin했다. Last-Modified, tar member mtime, PDF creation timestamp를 software release date로 둔갑시키지 않았다. Licence/dependency가 확인되지 않은 필드도 null과 unresolved 사유로 보존했다.

## 원 Deep Research DB

원 ZIP expected reported SHA256: `{EXPECTED_ORIGINAL}`. 접근 가능한 파일의 exact/short title 검색, Drive filename 검색, 지정 Dropbox folder에서 찾지 못했다. `original_deep_research_db_recovered=false`.

`{recon_identity['filename']}`를 별도 생성했다. 원 보고서의 명시적 SQL schema·source CSV 4개·blocker CSV 5개, 전체 보고서/표와 acquisition crosswalk만 복원했다. 원 보고서가 주장한 전체 19 source/9 theorem/9 module/15 test/7 artifact/8 blocker export는 원 record가 없어 재현하지 않았다. Semantic equivalence는 `UNVERIFIED_NOT_CLAIMED`; 재구성본을 원본으로 부르지 않는다.

## 남은 gap과 bounded 종료

INTLAB 14.1은 개인 유료 licence 경로, COSY 10.2는 개인 registration·서명 licence 경로다. 이를 우회하거나 등록·서명·결제를 하지 않았다. 공개 legal fallback 탐색은 성공 경로 또는 명시적 licence wall에서 종료했다. 새로운 동일 URL retry는 1회 이하이고, PDF 오류 HTML을 원문으로 저장하지 않았다. 두 논문에 arXiv 정확 일치본은 검색에서 확인되지 않았으나 기관 원문으로 closure했다. 원 DB는 접근 가능한 bytes가 없어 부분 재구성까지 수행했다. 이것은 환경 때문에 모든 fallback 탐색을 수행 못한 C 상태가 아니라, 원문 회수 작업을 끝내고 3개의 명시적 미확보 항목을 남긴 B 상태다.

## 검증·범위

`science_commands=0`, `science_producer_commands=0`, `numerical_certificate_runs=0`, `downloaded_code_executions=0`, `native_builds=0`.
`B_ORDER_VERDICT_STABLE_OVER_128_160_192`, `SOURCE_ACCURACY_BOUND_UNAVAILABLE`, `RIGOROUS_REFERENCE_CERTIFICATION_BLOCKED_BY_MISSING_ERROR_BOUND`, `certified_epsilon=null`, `certified_eta=null`, `rigorous=false`를 보존한다.
Original DB rows를 그대로 유지하고 child/versioned record만 추가했다. SQLite integrity와 원 row 포함 여부를 확인했다. New PDF 2개 magic/page count, PostScript magic/DSC 15 pages, source tar 13 member integrity를 검사했다. OCR, PS 실행/변환, scientific code 실행은 하지 않았다.

## 봉인·publication·backup binding

이 self-contained 패키지는 provider upload와 최종 Git metadata publication 전에 봉인된다. 실제 upload ACK·object ID·remote parent/path·metadata size/checksum 및 final commit/tree는 detached `RETURN.json`/backup receipt에 기록한다. 이 파일의 수집 completion과 remote backup verification은 분리한다. Content-part ZIP들의 member union은 canonical package tree와 동일하도록 검증한다. 실제 remote download/readback가 없으면 `RESTORE_VERIFIED=false`다. 기존 두 automatic acquisition workflow는 collector commit에서 제거했고, 성공 결과를 보존한 후 새 임시 workflow도 최종 metadata commit에서 제거한다. Public Git에는 원문·third-party archive를 넣지 않는다.
'''
    (ROOT/'ACQUISITION_RECOVERY_REPORT.md').write_text(report)
    (ROOT/'README_KO.md').write_text('# WU088 literature recovery v2\n\n`INDEX.html` 또는 `COMPLETE_SOURCE_INDEX.md`를 열면 offline 원문을 찾을 수 있다. '
        '`previous_v1/`은 기존 archive tree 그대로이며 `recovery/`는 신규 6 asset이다. '
        '현재 상태·세 가지 미확보 gap·representation 차이는 보고서와 `STILL_MISSING.md`를 참조한다. '
        'DB의 원 record는 immutable이며 최신 acquisition 상태는 `effective_sources` view를 조회한다. '
        '이 패키지는 science execution/certification을 승인하거나 수행하지 않는다.\n')
    acceptance = {'schema':'WU088_ACQUISITION_ACCEPTANCE_V2','baseline_168_payloads_reused_and_verified':True,
                  'all_missing_json_ids_have_successor_status':True,'all_status_ne_acquired_ids_in_target_set':True,
                  'author_institutional_fallbacks_acquired':True,'publisher_preprint_distinction_preserved':True,
                  'explicit_pins_preserved':True,'available_latest_stable_target_selected':True,
                  'unversioned_non_git_upstream_exception_documented':True,
                  'new_assets_have_sha256_and_bytes':True,'pdf_magic_verified':True,'postscript_not_mislabeled_pdf':True,
                  'downloaded_code_executions':0,'public_git_third_party_payloads':0,
                  'original_db_vs_partial_reconstruction_distinguished':True,
                  'original_sql_rows_unchanged':baseline_rows_unchanged,
                  'backup_size_verification':'DETACHED_RETURN_AFTER_UPLOAD',
                  'RESTORE_VERIFIED':False,'workflow_cleanup':'TO_BE_BOUND_BY_FINAL_METADATA_COMMIT',
                  'science_commands':0,'numerical_certificate_runs':0,'original_science_gate_mutations':0}
    writej(ROOT/'ACCEPTANCE_TESTS.json',acceptance)
    members=seal(ROOT)
    for x in members:
        assert (ROOT/x['path']).stat().st_size==x['bytes'] and sha(ROOT/x['path'])==x['sha256']
    for x in json.loads((BASE/'MANIFEST.json').read_text())['files']:
        assert sha(ROOT/'previous_v1'/x['path'])==x['sha256']
    archive=create_zip(ROOT,OUT/(NAME+'.zip'))
    # Independent content ZIPs, not a byte-concatenation split.
    partitions=[[],[]];loads=[0,0]
    for p in sorted((p for p in ROOT.rglob('*') if p.is_file()),key=lambda p:(-p.stat().st_size,str(p))):
        i=min(range(2),key=lambda i:loads[i]);partitions[i].append(p);loads[i]+=p.stat().st_size
    parts=[create_zip(ROOT,OUT/(NAME+'_part'+str(i+1).zfill(2)+'.zip'),sorted(ps)) for i,ps in enumerate(partitions)]
    union={};duplicates=[]
    for part in parts:
        assert part['bytes']<100*1024*1024
        with zipfile.ZipFile(OUT/part['filename']) as z:
            for name in z.namelist():
                if name in union:duplicates.append(name)
                data=z.read(name);union[name]=hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(OUT/archive['filename']) as z:
        canonical={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
    assert not duplicates and union==canonical
    partition_proof={'schema':'WU088_CONTENT_PART_UNION_V1','canonical_archive':archive,'parts':parts,
                     'canonical_tree_files':len(canonical),'part_union_files':len(union),'overlap_members':duplicates,
                     'same_path_same_byte_hash_union_equals_canonical':True,'byte_concatenation_split':False,
                     'every_part_independently_extractable':True,'file_manifest':canonical}
    writej(OUT/'CONTENT_PARTS_MANIFEST.json',partition_proof)
    writej(OUT/'PACKAGE_IDENTITY.json',{'archive':archive,'parts':parts,'reconstructed_db':recon_identity,
                                      'manifest_files':len(members),'canonical_tree_files':len(canonical)})
    for name in ['ACQUISITION_RECOVERY_REPORT.md','STILL_MISSING.md','acquisition_recovery.json','sources_recovered.csv','sources_remaining.csv']:
        shutil.copy2(ROOT/name,OUT/name)
    print(json.dumps({'archive':archive,'parts':parts,'reconstructed_db':recon_identity,
                      'manifest_payloads':len(members),'canonical_files':len(canonical),'part_union_verified':True,
                      'previously_acquired_records_reused':58,'new_full_text_or_code_sources':3,
                      'remaining_items':3,'science_commands':0},ensure_ascii=False))


if __name__=='__main__':
    main()
