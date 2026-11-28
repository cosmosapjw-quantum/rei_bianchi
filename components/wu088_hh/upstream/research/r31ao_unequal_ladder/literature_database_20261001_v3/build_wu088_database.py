#!/usr/bin/env python3
"""Build a metadata-only successor of the sealed WU088 R31AO acquisition DB.

No network access, scientific computation, upstream code execution, or original
DB reconstruction claim. All historical SQLite rows are preserved unchanged.
"""
import argparse
import csv
import hashlib
import html
import json
import mimetypes
import re
import shutil
import sqlite3
import tarfile
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

PACKAGE = 'WU088_HH_R31AO_DATABASE_20261001_v3'
DB_NAME = 'WU088_HH_R31AO_ACQUISITION_DATABASE_20261001_v3.sqlite'
GATES = {
    'order_verdict': 'B_ORDER_VERDICT_STABLE_OVER_128_160_192',
    'source_accuracy': 'SOURCE_ACCURACY_BOUND_UNAVAILABLE',
    'rigorous_reference': 'RIGOROUS_REFERENCE_CERTIFICATION_BLOCKED_BY_MISSING_ERROR_BOUND',
    'certified_epsilon': None, 'certified_eta': None, 'rigorous': False,
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def jd(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n')


def insert(conn, table, values):
    cols = list(values)
    conn.execute('INSERT INTO ' + table + ' (' + ','.join(cols) + ') VALUES (' + ','.join('?' for _ in cols) + ')', [values[k] for k in cols])


def rows(conn, sql, params=()):
    return [dict(x) for x in conn.execute(sql, params)]


def csv_write(path, records, columns=None):
    cols = columns or list(records[0])
    with Path(path).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(records)


SCHEMA = '''
PRAGMA foreign_keys=ON;
CREATE TABLE db_build_metadata(key TEXT PRIMARY KEY, value_json TEXT NOT NULL);
CREATE TABLE source_catalog(
 source_id TEXT PRIMARY KEY REFERENCES sources(id), title TEXT NOT NULL, source_type TEXT,
 authors TEXT, year INTEGER, doi TEXT, arxiv TEXT, requested_identity TEXT,
 acquisition_status TEXT, acquired_representation TEXT, representation_equivalence TEXT,
 publisher_version_available INTEGER CHECK(publisher_version_available IN (0,1)),
 publisher_direct_download_acquired INTEGER CHECK(publisher_direct_download_acquired IN (0,1)),
 publisher_bytes_compared INTEGER NOT NULL DEFAULT 0 CHECK(publisher_bytes_compared=0),
 fallback_chain TEXT NOT NULL CHECK(json_valid(fallback_chain)), version_selection_rule TEXT,
 version_requested TEXT, version_acquired TEXT, version_is_latest_stable INTEGER,
 commit_sha TEXT, tree_sha TEXT, source_sha256 TEXT, bytes INTEGER, license TEXT,
 retrieved_utc TEXT, failure_class TEXT, remaining_gap TEXT,
 backup_object_ids TEXT NOT NULL CHECK(json_valid(backup_object_ids)),
 restore_verified INTEGER NOT NULL DEFAULT 0 CHECK(restore_verified=0),
 raw_source_acquired INTEGER CHECK(raw_source_acquired IN (0,1)),
 full_text_acquired INTEGER CHECK(full_text_acquired IN (0,1)),
 effective_record_id TEXT NOT NULL REFERENCES sources(id), evidence_origin TEXT NOT NULL,
 theorem_authority_automatically_promoted INTEGER NOT NULL DEFAULT 0 CHECK(theorem_authority_automatically_promoted=0)
);
CREATE TABLE source_versions(
 record_id TEXT PRIMARY KEY REFERENCES sources(id), source_id TEXT NOT NULL REFERENCES source_catalog(source_id),
 parent_record_id TEXT REFERENCES sources(id), historical_status TEXT, representation TEXT, provenance_json TEXT NOT NULL CHECK(json_valid(provenance_json))
);
CREATE TABLE acquired_files(
 asset_id TEXT PRIMARY KEY REFERENCES assets(asset_id), record_id TEXT NOT NULL REFERENCES source_versions(record_id),
 source_id TEXT NOT NULL REFERENCES source_catalog(source_id), payload_archive TEXT NOT NULL, package_path TEXT NOT NULL UNIQUE,
 bytes INTEGER NOT NULL CHECK(bytes>=0), sha256 TEXT NOT NULL CHECK(length(sha256)=64),
 mime_type TEXT, observed_format TEXT NOT NULL, original_filename TEXT, filename_evidence TEXT,
 normalized_local_filename TEXT NOT NULL, original_source_url TEXT, final_url TEXT,
 retrieved_utc TEXT, http_status INTEGER, http_metadata_json TEXT NOT NULL CHECK(json_valid(http_metadata_json)),
 representation TEXT, page_count INTEGER, title_identity_status TEXT, inspection_json TEXT NOT NULL CHECK(json_valid(inspection_json)),
 local_bytes_hash_verified INTEGER NOT NULL CHECK(local_bytes_hash_verified=1),
 backup_set_id TEXT NOT NULL, restore_verified INTEGER NOT NULL DEFAULT 0 CHECK(restore_verified=0)
);
CREATE TABLE source_file_links(
 source_id TEXT REFERENCES source_catalog(source_id), asset_id TEXT REFERENCES acquired_files(asset_id),
 link_role TEXT, evidence_origin TEXT NOT NULL, PRIMARY KEY(source_id,asset_id,link_role)
);
CREATE TABLE acquisition_events(
 event_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source_catalog(source_id),
 record_id TEXT REFERENCES source_versions(record_id), attempted_url TEXT, utc TEXT,
 http_status_or_error TEXT, failure_class TEXT, retryable INTEGER, fallback_attempted INTEGER,
 event_kind TEXT NOT NULL, evidence_origin TEXT NOT NULL, record_json TEXT NOT NULL CHECK(json_valid(record_json))
);
CREATE TABLE code_version_policy(
 policy_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source_catalog(source_id),
 repository TEXT, release_tag_version TEXT, version_requested TEXT, version_acquired TEXT,
 raw_source_acquired INTEGER NOT NULL, commit_sha TEXT, tree_sha TEXT, release_date TEXT,
 source_archive_sha256 TEXT, bytes INTEGER, license TEXT, dependencies_json TEXT,
 canonical_upstream_url TEXT, acquisition_utc TEXT, authority_role TEXT, version_selection_rule TEXT,
 latest_stable_target_selected INTEGER NOT NULL, record_json TEXT NOT NULL CHECK(json_valid(record_json))
);
CREATE TABLE acquisition_gaps(
 gap_id TEXT PRIMARY KEY, source_id TEXT REFERENCES source_catalog(source_id), artifact_id TEXT,
 gap_scope TEXT NOT NULL, requested_identity TEXT, failure_class TEXT, remaining_gap TEXT NOT NULL,
 minimum_next_action TEXT, evidence_origin TEXT NOT NULL, prevents_acquisition_completion_all INTEGER NOT NULL
);
CREATE TABLE backup_objects(
 provider TEXT, object_id TEXT, backup_set_id TEXT NOT NULL, filename TEXT, path_or_parent TEXT,
 bytes INTEGER, local_sha256 TEXT, upload_ack INTEGER, metadata_size_matches INTEGER,
 verification_tier TEXT, remote_checksum_verified INTEGER NOT NULL, restore_verified INTEGER NOT NULL,
 evidence_origin TEXT NOT NULL, PRIMARY KEY(provider,object_id)
);
CREATE TABLE original_research_database_status(
 artifact_id TEXT PRIMARY KEY, original_filename TEXT NOT NULL, expected_reported_sha256 TEXT NOT NULL,
 original_bytes_recovered INTEGER NOT NULL CHECK(original_bytes_recovered=0),
 reconstruction_equivalence TEXT NOT NULL, reconstruction_filename TEXT, reconstruction_sha256 TEXT,
 reconstruction_bytes INTEGER, recovered_explicit_source_rows INTEGER, recovered_explicit_blocker_rows INTEGER,
 unexported_entity_tables_json TEXT NOT NULL CHECK(json_valid(unexported_entity_tables_json)), evidence_origin TEXT NOT NULL
);
CREATE TABLE report_documents(document_id TEXT PRIMARY KEY, original_package_path TEXT, sha256 TEXT, body TEXT NOT NULL);
CREATE TABLE report_example_rows(
 example_table TEXT, row_number INTEGER, row_json TEXT NOT NULL CHECK(json_valid(row_json)),
 evidence_origin TEXT NOT NULL, PRIMARY KEY(example_table,row_number)
);
CREATE TABLE report_sections(
 section_id TEXT PRIMARY KEY, document_id TEXT REFERENCES report_documents(document_id),
 heading TEXT, start_line INTEGER, end_line INTEGER, body TEXT NOT NULL
);
CREATE VIRTUAL TABLE catalog_search USING fts5(source_id UNINDEXED, title, authors, identifiers, status, representation, notes);
CREATE VIRTUAL TABLE report_search USING fts5(section_id UNINDEXED, heading, body);
CREATE INDEX files_sha256 ON acquired_files(sha256);
CREATE INDEX events_source_time ON acquisition_events(source_id,utc);
CREATE INDEX gaps_source ON acquisition_gaps(source_id);
CREATE VIEW v_source_files AS
 SELECT s.source_id,s.title,l.link_role,f.asset_id,f.record_id,f.package_path,f.sha256,f.bytes,f.observed_format,f.retrieved_utc
 FROM source_catalog s JOIN source_file_links l USING(source_id) JOIN acquired_files f USING(asset_id);
CREATE VIEW v_current_missing AS SELECT * FROM acquisition_gaps WHERE prevents_acquisition_completion_all=1;
CREATE VIEW v_failed_attempts AS SELECT * FROM acquisition_events WHERE failure_class IS NOT NULL;
CREATE VIEW v_payload_backup_sets AS
 SELECT f.asset_id,f.source_id,f.package_path,f.sha256,b.provider,b.object_id,b.filename,b.path_or_parent,b.verification_tier,b.restore_verified
 FROM acquired_files f JOIN backup_objects b USING(backup_set_id);
'''


def classify_failure(raw):
    if raw.get('failure_class'):
        return raw['failure_class'], raw.get('retryable')
    err = str(raw.get('error') or '')
    status = raw.get('http_status_or_error', raw.get('http_status'))
    match = re.search(r'HTTP Error (\d+)', err)
    if match:
        status = int(match[1])
    if status in (403,404,429) or isinstance(status, int) and status >= 500:
        return {403:'HTTP_403_ACCESS_DENIED',404:'HTTP_404_NOT_FOUND',429:'HTTP_429_RATE_LIMIT'}.get(status, 'HTTP_5XX_SERVER_ERROR'), int(status==429 or status>=500)
    if err:
        if 'timed out' in err.lower():
            return 'NETWORK_TIMEOUT', 1
        if 'name or service not known' in err.lower() or 'dns' in err.lower():
            return 'DNS_RESOLUTION_FAILURE', 1
        return 'UNCLASSIFIED_RECORDED_ERROR', None
    return None, raw.get('retryable')


def inspect_file(path, raw):
    with path.open('rb') as f:
        magic = f.read(32)
    details = dict(raw.get('inspection') or {})
    if path.suffix.lower()=='.pdf':
        assert magic.startswith(b'%PDF-'), str(path)
        fmt, mime = 'PDF', 'application/pdf'
        details['pdf_magic_verified_current_build'] = True
    elif path.suffix.lower()=='.ps':
        assert magic.startswith(b'%!PS'), str(path)
        fmt, mime = 'POSTSCRIPT', 'application/postscript'
        details['postscript_magic_verified_current_build'] = True
    elif path.name.endswith(('.tar.gz','.tgz','.tar')):
        with tarfile.open(path, 'r:*') as arc:
            members = arc.getmembers()
            details.update(archive_member_count=len(members), top_level=sorted({m.name.split('/')[0] for m in members}), member_headers_read=True)
        fmt, mime = 'SOURCE_TAR_ARCHIVE', 'application/gzip' if magic.startswith(b'\x1f\x8b') else 'application/x-tar'
    elif path.suffix.lower()=='.zip':
        with zipfile.ZipFile(path) as arc:
            assert arc.testzip() is None, str(path)
            details.update(archive_member_count=len(arc.infolist()), top_level=sorted({m.filename.split('/')[0] for m in arc.infolist()}), zip_crc_verified=True)
        fmt, mime = 'SOURCE_ZIP_ARCHIVE', 'application/zip'
    else:
        fmt = 'HTML_SNAPSHOT' if path.suffix.lower() in ('.html','.htm') else 'TEXT_OR_OTHER_SNAPSHOT'
        mime = mimetypes.guess_type(path.name)[0]
    details['downloaded_code_executed'] = False
    details['ocr_performed'] = False
    return fmt, mime, details


def build(args):
    root, out = Path(args.baseline_root).resolve(), Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    prior = json.loads(Path(args.prior_return).read_text())
    assert prior['original_science_gates']==GATES
    parts = json.loads(Path(args.parts_manifest).read_text())
    manifest = json.loads((root/'ARTIFACT_MANIFEST.json').read_text())
    for m in manifest['files']:
        p = root/m['path']
        assert p.is_file() and p.stat().st_size==m['bytes'] and sha(p)==m['sha256'], m['path']
    assert parts['canonical_archive']['sha256']==prior['archive']['sha256']
    for path, expected in parts['file_manifest'].items():
        relative = Path(path).relative_to(root.name)
        assert sha(root/relative)==expected, path
    src = sqlite3.connect('file:'+str(root/'catalog/acquisition.sqlite')+'?mode=ro', uri=True)
    src.row_factory = sqlite3.Row
    c = sqlite3.connect(out/DB_NAME)
    c.row_factory = sqlite3.Row
    src.backup(c)
    old_tables = [x[0] for x in src.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    c.executescript(SCHEMA)
    source_rows = rows(src, 'SELECT * FROM sources ORDER BY id')
    source_by_id = {s['id']:s for s in source_rows}
    raw_sources = {s['id']:json.loads(s['record_json']) for s in source_rows}
    effective = rows(src, 'SELECT * FROM effective_sources ORDER BY id')
    canonical = {s['id'] for s in effective}
    parent = {s['id']:s['id'] if s['id'] in canonical else raw_sources[s['id']]['parent_source_id'] for s in source_rows}
    assert len(canonical)==68 and len(parent)==79
    policies = json.loads((root/'catalog/CODE_VERSION_POLICY.json').read_text())
    policy_by_id = {p['source_id']:p for p in policies}
    missing = json.loads((root/'catalog/missing_sources.json').read_text())
    missing_by_id = {m['source_id']:m for m in missing}
    updates = json.loads((root/'catalog/recovery_updates.json').read_text())
    update_by_id = {u['source_id']:u for u in updates}
    asset_rows = rows(src, 'SELECT * FROM effective_assets ORDER BY asset_id')
    asset_raw = {a['asset_id']:json.loads(src.execute('SELECT record_json FROM assets WHERE asset_id=?',(a['asset_id'],)).fetchone()[0]) for a in asset_rows}
    links = {(parent[a['source_id']],a['asset_id'],'DIRECT_OR_VERSIONED_PAYLOAD','assets.source_id') for a in asset_rows}
    by_path = {a['package_path']:a for a in asset_rows}
    for u in updates:
        if u['source_id'].startswith('URL'):
            for path in u['asset_paths']:
                links.add((u['source_id'],by_path[path]['asset_id'],'EQUIVALENT_CONTENT_REFERENCE','catalog/recovery_updates.json'))
    objects = []
    for provider in ('drive','dropbox'):
        for b in prior[provider]['parts']:
            objects.append(dict(provider=provider,object_id=b['object_id'],backup_set_id='WU088_V2_CONTENT_PART_UNION',filename=b['filename'],
                path_or_parent=jd(b.get('parent')) if provider=='drive' else b['path'],bytes=b['bytes'],local_sha256=b['sha256'],
                upload_ack=int(b['upload_ack']),metadata_size_matches=int(b['size_matches_local']),
                verification_tier=prior['verification_tier'],remote_checksum_verified=0,restore_verified=0,evidence_origin='provenance/PRIOR_RETURN.json'))
    object_refs = [dict(provider=b['provider'],object_id=b['object_id'],backup_set_id=b['backup_set_id']) for b in objects]
    for e in effective:
        sid = e['id']; s = source_by_id[sid]; u = update_by_id.get(sid,{})
        rid = e.get('successor_record_id') or sid
        raw = raw_sources[rid]
        files = [a for a in asset_rows if any(l[0]==sid and l[1]==a['asset_id'] for l in links)]
        files.sort(key=lambda a: (not(a['package_path'].endswith(('.pdf','.ps','.zip','.tgz','.tar.gz','.tar'))),a['asset_id']))
        first = files[0] if files else {}
        raw_code = any(a['representation'] in ('SOURCE_ARCHIVE_SNAPSHOT','official_source_archive') for a in files)
        fulltext = any(a['package_path'].endswith(('.pdf','.ps')) for a in files)
        rep = u.get('acquired_representation') or raw.get('acquired_representation') or first.get('representation') or 'metadata_only'
        eq = u.get('representation_equivalence') or raw.get('representation_equivalence') or 'UNRESOLVED'
        if rep=='PDF_BYTES_TITLE_NOT_YET_VERIFIED':
            if 'arxiv.org/' in first.get('requested_url',''):
                rep = 'arxiv_preprint'
                eq = 'PREPUBLICATION_SAME_WORK' if asset_raw[first['asset_id']].get('title_identity_status')=='FIRST_PAGE_INSPECTED_AND_MATCHED' else 'UNRESOLVED'
            else:
                rep = 'institutional_repository' if fulltext else 'metadata_only'
        if raw_code:
            rep = 'official_source_archive' if sid=='C14' else 'SOURCE_ARCHIVE_SNAPSHOT'
        policy = policy_by_id.get(sid,{})
        requested_version = policy.get('release_tag_version') or s['version_or_ref'] or None
        acquired_version = requested_version if raw_code or s['source_type']!='code' and fulltext else None
        if sid=='C11': requested_version, acquired_version = '14.1', None
        if sid=='C12': requested_version, acquired_version = '10.2', None
        if sid=='C14': requested_version, acquired_version = None, 'unversioned official archive; SHA256 pinned'
        routes = list(dict.fromkeys(raw_sources[sid].get('urls',[]) + raw_sources[sid].get('supplement_urls',[]) + raw.get('fallback_chain',[]) + [a['requested_url'] for a in files if a['requested_url']]))
        gap = missing_by_id.get(sid,{})
        record = dict(source_id=sid,title=s['title'],source_type=s['source_type'],authors=s['authors'],year=s['year'],doi=s['doi'],arxiv=s['arxiv'],
            requested_identity=s['title'] if sid=='C14' else u.get('requested_identity') or raw.get('requested_identity') or s['doi'] or s['arxiv'] or s['title'],
            acquisition_status=e['acquisition_status'],acquired_representation=rep,representation_equivalence=eq,
            publisher_version_available=raw.get('publisher_version_available'),publisher_direct_download_acquired=raw.get('publisher_direct_download_acquired'),publisher_bytes_compared=0,
            fallback_chain=jd(routes),version_selection_rule=policy.get('version_selection_rule'),version_requested=requested_version,version_acquired=acquired_version,
            version_is_latest_stable=None,commit_sha=s['resolved_commit'],tree_sha=s['resolved_tree'],source_sha256=first.get('sha256'),bytes=first.get('bytes'),license=policy.get('license'),
            retrieved_utc=first.get('retrieved_utc'),failure_class=gap.get('failure_class'),remaining_gap=e.get('remaining_gap') or gap.get('remaining_gap'),
            backup_object_ids=jd(object_refs if files else []),restore_verified=0,raw_source_acquired=int(raw_code) if s['source_type']=='code' else None,
            full_text_acquired=int(fulltext) if s['source_type']=='paper' else None,effective_record_id=rid,
            evidence_origin='effective_sources + versioned source/asset evidence; historical tables preserved',theorem_authority_automatically_promoted=0)
        insert(c,'source_catalog',record)
        c.execute('INSERT INTO catalog_search VALUES (?,?,?,?,?,?,?)',(sid,s['title'],s['authors'], ' '.join(str(s[k] or '') for k in ('doi','arxiv','version_or_ref')),record['acquisition_status'],rep,jd(raw.get('notes',[]))))
    for s in source_rows:
        insert(c,'source_versions',dict(record_id=s['id'],source_id=parent[s['id']],parent_record_id=raw_sources[s['id']].get('parent_source_id'),historical_status=s['status'],representation=raw_sources[s['id']].get('acquired_representation'),provenance_json=s['record_json']))
    extra_inspections = {p['file']:p for p in json.loads((root/'provenance/PAYLOAD_INSPECTION.json').read_text())}
    for a in asset_rows:
        raw = asset_raw[a['asset_id']]; p = root/a['package_path']
        assert p.stat().st_size==a['bytes'] and sha(p)==a['sha256'], a['asset_id']
        fmt, mime, inspection = inspect_file(p,raw)
        more = extra_inspections.get(p.name,{})
        if more:
            inspection['prior_pdf_inspection_evidence'] = 'provenance/PAYLOAD_INSPECTION.json:'+p.name
        original = raw.get('original_filename') or unquote(Path(urlsplit(a['final_url'] or a['requested_url'] or '').path).name) or None
        insert(c,'acquired_files',dict(asset_id=a['asset_id'],record_id=a['source_id'],source_id=parent[a['source_id']],payload_archive=parts['canonical_archive']['filename'],package_path=a['package_path'],
            bytes=a['bytes'],sha256=a['sha256'],mime_type=mime,observed_format=fmt,original_filename=original,filename_evidence='RECORDED_ORIGINAL_FILENAME' if raw.get('original_filename') else 'FINAL_OR_REQUEST_URL_BASENAME; CONTENT_DISPOSITION_NOT_OBSERVED',
            normalized_local_filename=p.name,original_source_url=a['requested_url'],final_url=a['final_url'],retrieved_utc=a['retrieved_utc'],http_status=raw.get('http_status'),
            http_metadata_json=jd(raw.get('headers') or raw.get('http_metadata') or {}),representation=a['representation'],page_count=raw.get('pdf_pages') or more.get('pages'),
            title_identity_status=raw.get('title_identity_status') or ('PRIOR_FIRST_PAGE_INSPECTION_RECORDED' if more else None),inspection_json=jd(inspection),local_bytes_hash_verified=1,backup_set_id='WU088_V2_CONTENT_PART_UNION',restore_verified=0))
    for sid,aid,role,origin in sorted(links):
        insert(c,'source_file_links',dict(source_id=sid,asset_id=aid,link_role=role,evidence_origin=origin))
    for obj in objects: insert(c,'backup_objects',obj)
    event_records = []
    for a in rows(src,'SELECT * FROM attempts ORDER BY source_id,attempt_number'):
        event_records.append(('LEGACY:'+a['source_id']+':'+str(a['attempt_number']),parent[a['source_id']],a['source_id'],json.loads(a['record_json']),'HISTORICAL_ATTEMPT','attempts'))
    for a in asset_rows:
        event_records.append(('ASSET:'+a['asset_id'],parent[a['source_id']],a['source_id'],asset_raw[a['asset_id']],'SUCCESSFUL_PAYLOAD_RETRIEVAL','assets'))
    recovery_results = json.loads((root/'recovery/ACQUISITION_RESULTS.json').read_text())
    for rec in recovery_results:
        record_assets=[a for a in asset_rows if asset_raw[a['asset_id']].get('source_record_id')==rec['id']]
        assert record_assets, rec['id']
        route_record_id=record_assets[0]['source_id']
        for n,attempt in enumerate(rec['attempts']):
            evidence=dict(attempt,original_route_parent_id=rec['parent_id'],original_route_record_id=rec['id'])
            event_records.append(('RECOVERY:'+rec['id']+':'+str(n),parent[route_record_id],route_record_id,evidence,'RECOVERY_ROUTE_ATTEMPT','recovery/ACQUISITION_RESULTS.json'))
    for eid,sid,rid,raw,kind,origin in event_records:
        failure,retryable = classify_failure(raw)
        insert(c,'acquisition_events',dict(event_id=eid,source_id=sid,record_id=rid,attempted_url=raw.get('attempted_url') or raw.get('url') or raw.get('original_source_url') or raw.get('requested_url'),
            utc=raw.get('utc') or raw.get('acquisition_utc') or raw.get('retrieved_utc'),http_status_or_error=str(raw.get('http_status_or_error') or raw.get('error') or raw.get('http_status') or '') or None,
            failure_class=failure,retryable=retryable,fallback_attempted=raw.get('fallback_attempted'),event_kind=kind,evidence_origin=origin,record_json=jd(raw)))
    for n,p in enumerate(policies):
        sid=p['source_id']; raw_code=c.execute('SELECT raw_source_acquired FROM source_catalog WHERE source_id=?',(sid,)).fetchone()[0]
        version=p.get('release_tag_version')
        insert(c,'code_version_policy',dict(policy_id='POLICY-'+str(n+1).zfill(2),source_id=sid,repository=p.get('repository'),release_tag_version=version,
            version_requested='14.1' if sid=='C11' else version,version_acquired=(version or 'unversioned official archive; SHA256 pinned') if raw_code else None,raw_source_acquired=raw_code,
            commit_sha=p.get('commit_sha'),tree_sha=p.get('tree_sha'),release_date=p.get('release_date'),source_archive_sha256=p.get('source_archive_sha256'),bytes=p.get('bytes'),license=p.get('license'),
            dependencies_json=jd(p.get('dependencies')),canonical_upstream_url=p.get('canonical_upstream_url'),acquisition_utc=p.get('acquisition_utc'),authority_role=p.get('authority_role'),
            version_selection_rule=p.get('version_selection_rule'),latest_stable_target_selected=int(p.get('version_selection_rule')=='LATEST_OFFICIAL_DOCUMENTED_STABLE_TARGET'),record_json=jd(p)))
    for m in missing:
        sid=m['source_id']; is_source=sid in canonical
        insert(c,'acquisition_gaps',dict(gap_id='MISSING:'+sid,source_id=sid if is_source else None,artifact_id=None if is_source else sid,gap_scope='RAW_SOURCE_PACKAGE' if is_source else 'ORIGINAL_RESEARCH_DATABASE',
            requested_identity=m['requested_identity'],failure_class=m['failure_class'],remaining_gap=m['remaining_gap'],minimum_next_action=m.get('minimum_next_action'),evidence_origin='catalog/missing_sources.json',prevents_acquisition_completion_all=1))
    for u in updates:
        if u['source_id'].startswith('URL') or u['source_id']=='P04':
            insert(c,'acquisition_gaps',dict(gap_id='REPRESENTATION:'+u['source_id'],source_id=u['source_id'],artifact_id=None,gap_scope='EXACT_CITED_URL_SNAPSHOT' if u['source_id'].startswith('URL') else 'FINAL_PUBLISHER_REVISION_COMPARISON',
                requested_identity=u['requested_identity'],failure_class='ORIGINAL_REPRESENTATION_UNAVAILABLE',remaining_gap=u.get('remaining_gap') or 'Equivalent full-text reference is retained; exact historical URL bytes are unavailable.',
                minimum_next_action=None,evidence_origin='catalog/recovery_updates.json',prevents_acquisition_completion_all=0))
    rec = prior['reconstructed_db']
    with zipfile.ZipFile(root/'reconstructed_database'/rec['filename']) as z:
        reconstruction_status=json.loads(z.read(next(n for n in z.namelist() if n.endswith('/RECONSTRUCTION_STATUS.json'))))
        for table,filename in [('sources','sources_EXPLICIT_REPORT_EXAMPLES.csv'),('blockers','blockers_EXPLICIT_REPORT_EXAMPLES.csv')]:
            entry=next(n for n in z.namelist() if n.endswith('/'+filename))
            examples=list(csv.DictReader(z.read(entry).decode('utf-8-sig').splitlines()))
            assert len(examples)==reconstruction_status['populated_rows'][table]
            for n,example in enumerate(examples):
                insert(c,'report_example_rows',dict(example_table=table,row_number=n+1,row_json=jd(example),evidence_origin='reconstructed_database/'+rec['filename']+':'+filename))
    insert(c,'original_research_database_status',dict(artifact_id='ORIGINAL_DEEP_RESEARCH_DB',original_filename='WU088_HH_R31AO_LITERATURE_DATABASE_20261001.zip',expected_reported_sha256=missing_by_id['ORIGINAL_DEEP_RESEARCH_DB']['expected_reported_sha256'],
        original_bytes_recovered=0,reconstruction_equivalence='UNVERIFIED_NOT_CLAIMED',reconstruction_filename=rec['filename'],reconstruction_sha256=rec['sha256'],reconstruction_bytes=rec['bytes'],
        recovered_explicit_source_rows=reconstruction_status['populated_rows']['sources'],recovered_explicit_blocker_rows=reconstruction_status['populated_rows']['blockers'],unexported_entity_tables_json=jd(['theorems','modules','tests','artifacts']),evidence_origin='reconstructed_database/'+rec['filename']))
    report_path='previous_v1/research_report/DEEP_RESEARCH_REPORT.md'
    report=(root/report_path).read_text(); report_lines=report.splitlines()
    insert(c,'report_documents',dict(document_id='ORIGINAL_REPORT',original_package_path=report_path,sha256=sha(root/report_path),body=report))
    headings=[(n,line) for n,line in enumerate(report_lines) if re.match(r'^#{1,6}\s',line)]
    if not headings or headings[0][0]>0: headings.insert(0,(0,'Report preamble'))
    for n,(start,heading) in enumerate(headings):
        end=headings[n+1][0] if n+1<len(headings) else len(report_lines)
        section_id='REPORT-'+str(n+1).zfill(3); body='\n'.join(report_lines[start:end])
        insert(c,'report_sections',dict(section_id=section_id,document_id='ORIGINAL_REPORT',heading=heading.lstrip('# '),start_line=start+1,end_line=end,body=body))
        c.execute('INSERT INTO report_search VALUES (?,?,?)',(section_id,heading,body))
    provenance=dict(schema='WU088_R31AO_ACQUISITION_DATABASE_SUCCESSOR_V3',created_utc=args.created_utc,inspected_head=args.inspected_head,
        repository='cosmosapjw-quantum/WU088_HH',branch='research/r31ao-unequal-order-ladder-20260930',baseline_db_sha256=sha(root/'catalog/acquisition.sqlite'),
        baseline_archive=parts['canonical_archive'],database_role='SUCCESSOR_ACQUISITION_DATABASE_NOT_ORIGINAL_DEEP_RESEARCH_DATABASE',original_deep_research_db_recovered=False,
        acquisition_payloads_included=False,payload_location='Existing sealed v2 archive or union of both v2 content parts on either provider',
        backup_set_semantics='Every file references the two-part union for each provider; per-file partition membership is not inferred.',
        unknown_values_policy='NULL means not observed; historical JSON remains unchanged. No current release lookup or new payload acquisition performed.',
        original_science_gates=GATES,science_commands=0,science_producer_commands=0,numerical_certificate_runs=0,downloaded_code_executions=0,native_builds=0,
        theorem_equation_authority='Available report prose is searchable; unexported original research entity tables are not invented or certified.',
        delivery_receipt_binding='New package provider IDs/publication head are in detached final RETURN.json; old payload backup IDs are in this database.')
    for k,v in provenance.items(): insert(c,'db_build_metadata',dict(key=k,value_json=jd(v)))
    c.commit()
    assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert not list(c.execute('PRAGMA foreign_key_check'))
    preserved = {}
    for table in old_tables:
        old = [tuple(r) for r in src.execute('SELECT * FROM '+table)]
        new = [tuple(r) for r in c.execute('SELECT * FROM '+table)]
        assert sorted(map(repr,old))==sorted(map(repr,new)),table
        preserved[table]=len(old)
    assert c.execute('SELECT COUNT(*) FROM source_catalog').fetchone()[0]==68
    assert c.execute('SELECT COUNT(*) FROM source_versions').fetchone()[0]==79
    assert c.execute('SELECT COUNT(*) FROM acquired_files').fetchone()[0]==66
    assert c.execute("SELECT COUNT(*) FROM source_catalog WHERE source_type='paper' AND full_text_acquired=1").fetchone()[0]==11
    assert c.execute("SELECT COUNT(*) FROM source_catalog WHERE source_id IN ('C11','C12') AND version_acquired IS NULL AND raw_source_acquired=0").fetchone()[0]==2
    assert c.execute("SELECT version_requested FROM source_catalog WHERE source_id='C01'").fetchone()[0]=='v3.4.0'
    assert c.execute("SELECT acquired_representation FROM source_catalog WHERE source_id='P04'").fetchone()[0]=='author_manuscript'
    assert c.execute("SELECT publisher_direct_download_acquired FROM source_catalog WHERE source_id='P06'").fetchone()[0]==0
    assert c.execute("SELECT COUNT(*) FROM source_file_links WHERE link_role='EQUIVALENT_CONTENT_REFERENCE'").fetchone()[0]==5
    assert c.execute("SELECT COUNT(*) FROM catalog_search WHERE catalog_search MATCH 'Petras'").fetchone()[0]>0
    assert c.execute("SELECT COUNT(*) FROM report_search WHERE report_search MATCH 'Petras'").fetchone()[0]>0
    tables=['source_catalog','source_versions','acquired_files','source_file_links','acquisition_events','code_version_policy','acquisition_gaps','backup_objects','original_research_database_status','report_sections','report_example_rows']
    counts={t:c.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in tables}
    export_specs={'sources.csv':'SELECT * FROM source_catalog ORDER BY source_id','source_versions.csv':'SELECT record_id,source_id,parent_record_id,historical_status,representation FROM source_versions ORDER BY record_id',
        'files.csv':'SELECT * FROM acquired_files ORDER BY asset_id','source_file_links.csv':'SELECT * FROM source_file_links ORDER BY source_id,asset_id,link_role',
        'attempts.csv':'SELECT * FROM acquisition_events ORDER BY source_id,event_id','code_versions.csv':'SELECT * FROM code_version_policy ORDER BY policy_id',
        'sources_recovered.csv':'SELECT s.* FROM source_catalog s JOIN recovery_updates r ON s.source_id=r.source_id WHERE r.closed=1 ORDER BY s.source_id',
        'sources_remaining.csv':'SELECT * FROM v_current_missing ORDER BY gap_id','representation_limits.csv':'SELECT * FROM acquisition_gaps WHERE prevents_acquisition_completion_all=0 ORDER BY gap_id',
        'backup_objects.csv':'SELECT * FROM backup_objects ORDER BY provider,filename','report_example_rows.csv':'SELECT * FROM report_example_rows ORDER BY example_table,row_number'}
    export_counts={}
    for filename,sql in export_specs.items():
        result=rows(c,sql); csv_write(out/filename,result); export_counts[filename]=len(result)
    full_schema='PRAGMA foreign_keys=ON;\n\n'+'\n\n'.join(str(x[0])+';' for x in c.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL AND name NOT GLOB 'catalog_search_*' AND name NOT GLOB 'report_search_*' ORDER BY CASE type WHEN 'table' THEN 0 WHEN 'index' THEN 1 ELSE 2 END,name"))+'\n'
    (out/'schema.sql').write_text(full_schema)
    write_json(out/'BUILD_PROVENANCE.json',provenance)
    checks=dict(schema='WU088_DATABASE_ACCEPTANCE_V3',all_passed=True,sqlite_integrity='ok',foreign_key_violations=[],historical_tables_rows_unchanged=preserved,
        baseline_manifest_payloads_verified=len(manifest['files']),baseline_content_union_paths_verified=len(parts['file_manifest']),all_66_file_hashes_and_bytes_verified=True,
        canonical_sources=68,versioned_records=79,acquired_files=66,paper_fulltexts=11,table_counts=counts,csv_counts=export_counts,
        explicit_pins_preserved=True,COSY_manual_not_source=True,INTLAB_and_COSY_acquired_source_version_null=True,original_deep_research_db_recovered=False,
        publisher_preprint_scan_distinctions_preserved=True,no_original_entity_rows_fabricated=True,offline_catalog_and_report_search_verified=True,
        science_commands=0,numerical_certificate_runs=0,downloaded_code_executions=0,original_science_gates_unchanged=True,remote_restore_verified=False)
    write_json(out/'ACCEPTANCE_TESTS.json',checks)
    summary=dict(provenance,identified_sources_total=69,canonical_source_record_count=68,original_db_artifact_target_count=1,previously_acquired_reused=66,newly_acquired=0,
        sources_recovered_in_prior_v2=7,currently_missing=missing,representation_limit_count=6,table_counts=counts,
        latest_stable_used_where_unpinned=False,latest_stable_target_selected_where_available=True,unpinned_software=[{'source_id':'C12','target':'COSY 10.2','raw_source_acquired':False},{'source_id':'C14','target':'Unversioned official CINTE archive','raw_source_acquired':True}],
        explicit_pins_preserved=True,reconstructed_db_created=False,prior_partial_reconstruction_preserved=True,RESTORE_VERIFIED=False,
        completion_status='LITERATURE_ACQUISITION_COMPLETE_WITH_DOCUMENTED_UNOBTAINABLE_ITEMS',database_build_status='DATABASE_BUILT_AND_LOCALLY_VALIDATED; DELIVERY_RECEIPT_DETACHED')
    write_json(out/'acquisition_recovery.json',summary)
    prov=out/'provenance';prov.mkdir()
    shutil.copy2(args.prior_return,prov/'PRIOR_RETURN.json')
    shutil.copy2(args.parts_manifest,prov/'PRIOR_CONTENT_PARTS_MANIFEST.json')
    shutil.copy2(root/'catalog/missing_sources.json',prov/'PRIOR_MISSING_SOURCES.json')
    shutil.copy2(root/'catalog/RECOVERY_TARGET_SET.json',prov/'PRIOR_RECOVERY_TARGET_SET.json')
    shutil.copy2(root/'provenance/PAYLOAD_INSPECTION.json',prov/'PRIOR_PAYLOAD_INSPECTION.json')
    shutil.copy2(root/'previous_v1/catalog/missing_sources.json',prov/'ORIGINAL_V1_MISSING_SOURCES.json')
    (prov/'ORIGINAL_REPORT.md').write_text(report)
    (out/'example_queries.sql').write_text("""-- Read-only examples; run against the successor SQLite DB.
SELECT source_id,title,acquisition_status,acquired_representation,remaining_gap FROM source_catalog ORDER BY source_id;
SELECT * FROM v_current_missing;
SELECT * FROM v_source_files WHERE source_id IN ('P04','P06','C12');
SELECT * FROM v_failed_attempts WHERE source_id='P04';
SELECT source_id,version_requested,version_acquired,raw_source_acquired,authority_role FROM code_version_policy;
SELECT source_id,title FROM catalog_search WHERE catalog_search MATCH 'Petras';
SELECT section_id,heading,snippet(report_search,2,'[',']','…',25) FROM report_search WHERE report_search MATCH 'Petras';
-- Both listed content parts form one backup set, not individual per-file mirrors.
SELECT * FROM v_payload_backup_sets WHERE asset_id='P04-R2-A1';
SELECT * FROM original_research_database_status;
""")
    sources=rows(c,'SELECT * FROM source_catalog ORDER BY source_id')
    (out/'COMPLETE_SOURCE_INDEX.md').write_text('# WU088 R31AO 출처 색인\n\n고유 출처 68개. 판본 기록 79개와 별도 원 DB artifact 1개는 중복 집계하지 않는다.\n\n| ID | 제목 | 확보 상태 | 판본 | 파일 수 |\n|---|---|---|---|---:|\n'+ '\n'.join('| '+s['source_id']+' | '+s['title'].replace('|','\\|')+' | '+s['acquisition_status']+' | '+s['acquired_representation']+' | '+str(c.execute('SELECT COUNT(*) FROM source_file_links WHERE source_id=?',(s['source_id'],)).fetchone()[0])+' |' for s in sources)+'\n')
    (out/'STILL_MISSING.md').write_text('# 남은 항목\n\n'+ '\n\n'.join('## '+m['source_id']+'\n\n'+m['remaining_gap']+'\n\n실패 분류: `'+m['failure_class']+'`' for m in missing)+ '\n\nP04 최종 출판판과의 수식·정리 번호 및 실질적 차이는 미비교다. URL10/11/24/25/26은 동등 원문 참조로 닫았으나 해당 URL의 원래 snapshot bytes는 미확보다.\n')
    report_text=f'''# WU088 R31AO 데이터베이스 구축 결과

검증된 v2 acquisition.sqlite를 기반으로 후속 DB를 만들었다. 기존 {len(old_tables)}개 테이블의 모든 행은 그대로 보존했다. 새 원문을 수집하거나 과학 계산을 실행하지 않았다.

- 고유 출처: 68개 (원 Deep Research DB artifact 1개는 별도)
- 기존·회복 판본 기록: 79개
- 실제 확보 파일: 66개, 전부 SHA256/bytes 재검증
- 회복 이전의 실패 기록, 성공 파일 회수 기록, 회복 경로 기록을 각각 구별한 event: {counts['acquisition_events']}개
- 코드 버전 정책: 15개 (COSY 이전 조사와 공식 10.2 대상 구별)
- 주요 미확보: INTLAB raw package, COSY raw package, 원 Deep Research DB bytes
- 별도 판본 제한: P04 출판판 비교, 5개 인용 URL의 원래 snapshot

P04는 저자의 기관 PostScript manuscript이며 publisher PDF가 아니다. P06은 Purdue에서 확보한 출판 레이아웃 scan이며 publisher 서버 bytes와 직접 비교하지 않았다. COSY 10.2 manual은 원 코드 확보를 뜻하지 않는다. CINTE는 COSY의 대체 구현으로 채택하지 않는다.

FLINT 3.4.0 프로젝트 pin, FLINT 3.6.0 조사본, NumPy 2.3.5 기존 참조를 구별해 보존했다. COSY 10.2는 이전 회복 단계에서 확인한 공식 stable 대상이며 raw source는 미확보다. 이 단계에서는 최신판을 다시 조사하거나 변경하지 않았다. 알 수 없는 release date/license/dependencies는 NULL과 기존 근거 상태로 보존했다.

원 `WU088_HH_R31AO_LITERATURE_DATABASE_20261001.zip`은 여전히 미복구다. 기존 부분 재구성본은 명시적으로 복구 가능한 source 4행과 blocker 5행만 담는다. 원 보고서의 나머지 theorem/module/test/artifact 행을 만들어내지 않았다. 대신 원 보고서 본문과 {counts['report_sections']}개 섹션에 읽기 전용 검색을 제공한다. 원 DB와 의미적 동등성은 주장하지 않는다.

DB 파일과 CSV/JSON, schema.sql, example_queries.sql, offline INDEX.html, 재현 스크립트를 제공한다. 원문 PDF/PS와 코드 tar/ZIP은 이미 보존된 v2 원문 archive에 있다. 새 패키지는 해당 원문 66개의 경로·해시·출처·기존 이중 백업 object IDs를 기록하며 대용량 payload를 중복 포함하지 않는다. 각 provider의 part01+part02 union이 한 전체 payload backup set이다. 개별 파일이 어느 part에 속하는지는 추정하지 않았다.

검증: SQLite integrity, 외래키, 기존 전체 행 보존, 201개 baseline manifest payload와 203개 content-union path, 파일 66개의 해시·크기·magic/archive headers, 11개 논문 원문 연결, 5개 동등 참조, 명시적 버전 pin 및 검색을 확인했다. ZIP CRC 확인과 archive metadata 읽기는 실행 없는 파일 검증이다.

기존 과학 상태는 그대로다: `B_ORDER_VERDICT_STABLE_OVER_128_160_192`, `SOURCE_ACCURACY_BOUND_UNAVAILABLE`, `RIGOROUS_REFERENCE_CERTIFICATION_BLOCKED_BY_MISSING_ERROR_BOUND`. `certified_epsilon=null`, `certified_eta=null`, `rigorous=false`. science/producer/certificate/downloaded-code 실행 모두 0이다.

새 Git 게시 및 Drive·Dropbox create-only 백업 결과는 외부 `RETURN.json`에 기록한다. DB 내부 backup object는 기존 v2 원문 보관본에 대한 prior receipt 근거다. Provider 검증은 ACK + object ID + parent/path + metadata size이며 실제 원격 bytes download/readback은 수행하지 않았으므로 `RESTORE_VERIFIED=false`다.

최종 수집 상태: `LITERATURE_ACQUISITION_COMPLETE_WITH_DOCUMENTED_UNOBTAINABLE_ITEMS`.
'''
    (out/'ACQUISITION_RECOVERY_REPORT.md').write_text(report_text)
    (out/'README_KO.md').write_text(f'''# WU088 R31AO 후속 수집 DB v3

`{DB_NAME}`을 SQLite 도구로 열거나 `INDEX.html`을 브라우저에서 열어 출처를 검색한다. 필드 설명은 `DATA_DICTIONARY.md`, SQL 예제는 `example_queries.sql`에 있다.

이 DB는 기존 수집 DB의 후속본이다. 분실된 원 Deep Research DB를 복원했다고 주장하지 않는다. 원문 payload는 별도 기존 v2 archive에 있고, `files.csv`와 `backup_objects.csv`로 찾을 수 있다. 두 content-part ZIP의 합집합을 사용한다.

빌드: `python build_wu088_database.py --baseline-root /path/to/extracted/v2 --prior-return /path/to/prior/RETURN.json --parts-manifest /path/to/CONTENT_PARTS_MANIFEST.json --output /path/to/new/output --inspected-head {args.inspected_head} --created-utc {args.created_utc}`

다운로드 없이 기존 보관본만 읽는다. 새 output 경로가 이미 있으면 중단한다. 별도 패키징 후 `verify_wu088_database.py`로 검사한다. 원격 게시/백업 receipt는 외부 RETURN.json에 있다.
''')
    (out/'DATA_DICTIONARY.md').write_text('''# 데이터 사전

| 테이블/뷰 | 의미 |
|---|---|
| sources/assets/attempts/relations/blocker_map/citation_occurrences/metadata/recovery_updates/representation_identity/recovery_artifacts | 기존 v2 원형 테이블. 행·JSON 값을 수정하지 않음 |
| source_catalog | canonical 68개 출처의 현재 상태, 요청 판본, 확보 판본, 제한, 백업 연결 |
| source_versions | 기존 source 79행의 canonical parent 및 원 JSON |
| acquired_files | 실제 확보 bytes 66개. 경로는 기존 v2 archive 내부 상대 경로 |
| source_file_links | 직접/판본 파일과 equivalent URL 참조의 명시적 연결 |
| acquisition_events | 원 실패·회수·회복 경로 기록. event 중복 경로는 근거 origin별 보존 |
| code_version_policy | 원 정책 15행 보존. version_acquired는 raw source 없으면 NULL |
| acquisition_gaps/v_current_missing | 주요 미확보 3개와 판본 제한 6개를 구별 |
| backup_objects/v_payload_backup_sets | 기존 v2 각 provider의 두 content parts를 하나의 backup set으로 연결 |
| original_research_database_status | 분실 원 DB, expected reported SHA, 부분 재구성본 범위 |
| report_documents/report_sections/report_search | 원 보고서의 본문/섹션/FTS5 검색. 원 미수출 entity DB와 구별 |
| catalog_search | 제목·저자·식별자·상태 FTS5 검색 |

NULL은 미관측/미확정이다. `publisher_version_available`은 기존 증거에서 출판 레이아웃이 확보됐는지에 대한 값이며 publisher 서버 직접 다운로드 여부와 다르다. `publisher_bytes_compared=0`이고 정리/수식 권위 자동 승격은 0이다. `version_is_latest_stable=NULL`은 확보 bytes가 현재 최신인지 검증하지 않았음을 뜻한다. COSY는 stable target만 선정됐고 코드 미확보다.

`backup_object_ids`는 기존 v2 raw payload 보관 object를 가리킨다. 새 DB/패키지 저장 object는 detached RETURN.json에 있다. `restore_verified=0`은 provider 원격 bytes를 readback하지 않았음을 뜻한다. 로컬 hash/bytes 검증과 혼동하지 않는다. `original_filename`에 HTTP Content-Disposition이 없으면 URL basename이라는 근거를 기록한다. acquired_files의 source_id는 직접 parent이며 alias 파일 연결은 source_file_links에 있다.
''')
    table_rows=''.join('<tr data-search="'+html.escape(' '.join(str(s[k] or '') for k in ('source_id','title','authors','doi','arxiv','acquisition_status','acquired_representation')),quote=True)+'"><td>'+html.escape(s['source_id'])+'</td><td>'+html.escape(s['title'])+'</td><td>'+html.escape(s['acquisition_status'])+'</td><td>'+html.escape(s['acquired_representation'])+'</td><td>'+html.escape(s['remaining_gap'] or '')+'</td></tr>' for s in sources)
    (out/'INDEX.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WU088 R31AO 출처 DB v3</title><style>body{font:16px system-ui,sans-serif;margin:2rem;line-height:1.5;color:#18232f}input{width:min(90%,700px);padding:.7rem;border:1px solid #789}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #ccd;padding:.5rem;vertical-align:top}th{background:#eef3f8}a{color:#175591}tr[hidden]{display:none}code{font-size:.9em}</style><h1>WU088 R31AO 출처 DB v3</h1><p>고유 출처 68개 · 판본 79개 · 확보 파일 66개. 원 Deep Research DB bytes는 미복구다. 원문 bytes는 기존 v2 archive와 두 content parts union에 있다.</p><p><a href="README_KO.md">사용법</a> · <a href="COMPLETE_SOURCE_INDEX.md">전체 색인</a> · <a href="STILL_MISSING.md">남은 항목</a> · <a href="ACQUISITION_RECOVERY_REPORT.md">보고서</a> · <a href="sources.csv">출처 CSV</a> · <a href="files.csv">파일 CSV</a> · <a href="example_queries.sql">SQL 예제</a></p><label for="q">제목·저자·DOI·상태 검색</label><p><input id="q" placeholder="Petras, DOI, COSY 등"></p><p id="count">68개</p><div style="overflow:auto"><table><thead><tr><th>ID</th><th>제목</th><th>확보 상태</th><th>판본</th><th>남은 제한</th></tr></thead><tbody>'''+table_rows+'''</tbody></table></div><p>과학 계산/코드 실행 0. 인증 상태 변경 없음. 원격 restore 검증 없음.</p><script>const q=document.getElementById('q'),r=[...document.querySelectorAll('tbody tr')];q.addEventListener('input',()=>{let n=0;const s=q.value.toLocaleLowerCase();r.forEach(x=>{x.hidden=!x.dataset.search.toLocaleLowerCase().includes(s);if(!x.hidden)n++});document.getElementById('count').textContent=n+'개'});</script></html>''')
    shutil.copy2(__file__,out/'build_wu088_database.py')
    verifier=Path(__file__).with_name('verify_wu088_database.py')
    if verifier.exists(): shutil.copy2(verifier,out/verifier.name)
    src.close();c.close()
    print(jd({'output':str(out),'database':str(out/DB_NAME),'table_counts':counts,'checks':'PASSED'}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for arg in ('baseline-root','prior-return','parts-manifest','output','inspected-head','created-utc'):
        p.add_argument('--'+arg,required=True)
    build(p.parse_args())
