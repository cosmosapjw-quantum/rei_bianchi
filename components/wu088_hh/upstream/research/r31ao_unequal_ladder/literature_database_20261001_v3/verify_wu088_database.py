#!/usr/bin/env python3
"""Verify a WU088 database delivery and optionally its sealed ZIP, without network."""
import argparse
import csv
import hashlib
import json
import sqlite3
import zipfile
from pathlib import Path


def digest(p):
    with Path(p).open('rb') as f:
        h=hashlib.file_digest(f,'sha256')
    return h.hexdigest()


def verify(package, baseline, archive=None):
    package=Path(package).resolve();baseline=Path(baseline).resolve()
    db=next(package.glob('*.sqlite'))
    new=sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True)
    old=sqlite3.connect('file:'+str(baseline/'catalog/acquisition.sqlite')+'?mode=ro',uri=True)
    new.row_factory=sqlite3.Row;old.row_factory=sqlite3.Row
    assert new.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert not list(new.execute('PRAGMA foreign_key_check'))
    preserved={}
    for r in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        table=r[0]
        actual=sorted(repr(tuple(row)) for row in new.execute('SELECT * FROM '+table))
        expected=sorted(repr(tuple(row)) for row in old.execute('SELECT * FROM '+table))
        assert actual==expected,table
        preserved[table]=len(expected)
    for row in new.execute('SELECT * FROM acquired_files'):
        path=baseline/row['package_path']
        assert path.is_file() and path.stat().st_size==row['bytes'] and digest(path)==row['sha256'],row['asset_id']
        original=old.execute('SELECT * FROM effective_assets WHERE asset_id=?',(row['asset_id'],)).fetchone()
        for col in ('package_path','bytes','sha256','retrieved_utc'):
            assert row[col]==original[col],(row['asset_id'],col)
        if row['observed_format']=='PDF':
            with path.open('rb') as f: assert f.read(5)==b'%PDF-'
    canonical={r[0] for r in old.execute('SELECT id FROM effective_sources')}
    assert canonical=={r[0] for r in new.execute('SELECT source_id FROM source_catalog')}
    assert new.execute('SELECT COUNT(*) FROM source_versions').fetchone()[0]==79
    assert new.execute('SELECT COUNT(*) FROM acquired_files').fetchone()[0]==66
    assert new.execute('SELECT COUNT(*) FROM code_version_policy').fetchone()[0]==15
    assert new.execute('SELECT COUNT(*) FROM v_current_missing').fetchone()[0]==3
    assert new.execute('SELECT COUNT(*) FROM acquisition_gaps').fetchone()[0]==9
    for row in new.execute("SELECT * FROM source_catalog WHERE source_id IN ('C11','C12')"):
        assert row['raw_source_acquired']==0 and row['version_acquired'] is None
    for sid,version in [('C01','v3.4.0'),('C02','v3.6.0'),('C04','v2.3.5')]:
        row=new.execute('SELECT * FROM source_catalog WHERE source_id=?',(sid,)).fetchone()
        assert row['version_acquired']==version and row['commit_sha']==old.execute('SELECT resolved_commit FROM sources WHERE id=?',(sid,)).fetchone()[0]
    p04=new.execute("SELECT * FROM source_catalog WHERE source_id='P04'").fetchone()
    assert p04['representation_equivalence']=='PREPUBLICATION_SAME_WORK' and p04['publisher_direct_download_acquired']==0
    p06=new.execute("SELECT * FROM source_catalog WHERE source_id='P06'").fetchone()
    assert p06['acquired_representation']=='institutional_repository' and p06['publisher_bytes_compared']==0 and p06['publisher_direct_download_acquired']==0
    for sid,path in [('URL10','previous_v1/acquired/papers/P08.pdf'),('URL11','recovery/files/P06_RECOVERY.pdf'),('URL24','previous_v1/supplement/papers/P05.pdf'),('URL25','previous_v1/acquired/papers/P09.pdf'),('URL26','recovery/files/P04_RECOVERY.ps')]:
        paths=[r[0] for r in new.execute('SELECT package_path FROM v_source_files WHERE source_id=?',(sid,))]
        assert path in paths,(sid,paths)
    rec=new.execute('SELECT * FROM original_research_database_status').fetchone()
    assert rec['original_bytes_recovered']==0 and rec['reconstruction_equivalence']=='UNVERIFIED_NOT_CLAIMED'
    assert rec['recovered_explicit_source_rows']==4 and rec['recovered_explicit_blocker_rows']==5
    assert new.execute('SELECT COUNT(*) FROM report_example_rows').fetchone()[0]==9
    prior=json.loads((package/'provenance/PRIOR_RETURN.json').read_text())
    provenance=json.loads((package/'BUILD_PROVENANCE.json').read_text())
    assert prior['original_science_gates']==provenance['original_science_gates']
    for key in ('science_commands','science_producer_commands','numerical_certificate_runs','downloaded_code_executions','native_builds'):
        assert provenance[key]==0
    for row in new.execute('SELECT * FROM backup_objects'):
        assert row['restore_verified']==0 and row['remote_checksum_verified']==0 and row['upload_ack']==1 and row['metadata_size_matches']==1
    assert new.execute('SELECT COUNT(*) FROM catalog_search WHERE catalog_search MATCH ?',('Petras',)).fetchone()[0]>0
    assert new.execute('SELECT COUNT(*) FROM report_search WHERE report_search MATCH ?',('Petras',)).fetchone()[0]>0
    checks=json.loads((package/'ACCEPTANCE_TESTS.json').read_text())
    for filename,count in checks['csv_counts'].items():
        with (package/filename).open(newline='',encoding='utf-8') as f:
            assert len(list(csv.DictReader(f)))==count,filename
    fresh=sqlite3.connect(':memory:')
    fresh.executescript((package/'schema.sql').read_text())
    assert fresh.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='source_catalog'").fetchone()[0]==1
    fresh.close()
    html=(package/'INDEX.html').read_text()
    assert html.count('<tr data-search=')==68
    assert (package/'verify_wu088_database.py').is_file() and (package/'build_wu088_database.py').is_file()
    manifest=package/'ARTIFACT_MANIFEST.json'
    sealed_files=None
    if manifest.exists():
        manifest=json.loads(manifest.read_text());sealed_files=manifest['files']
        for entry in sealed_files:
            p=package/entry['path']
            assert p.is_file() and p.stat().st_size==entry['bytes'] and digest(p)==entry['sha256'],entry['path']
        listed={m['path'] for m in sealed_files}
        actual={str(p.relative_to(package)) for p in package.rglob('*') if p.is_file()}-set(manifest['self_excluded'])
        assert listed==actual
        for line in (package/'MANIFEST.sha256').read_text().splitlines():
            hash_,rel=line.split('  ',1)
            assert digest(package/rel)==hash_,rel
    if archive:
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            local={package.name+'/'+str(p.relative_to(package)) for p in package.rglob('*') if p.is_file()}
            assert set(z.namelist())==local and len(set(z.namelist()))==len(z.infolist())
            for info in z.infolist():
                path=package/Path(info.filename).relative_to(package.name)
                assert hashlib.sha256(z.read(info)).hexdigest()==digest(path),info.filename
    new.close();old.close()
    return {'schema':'WU088_DATABASE_INDEPENDENT_FILE_VALIDATION_V3','all_passed':True,'baseline_rows_preserved':preserved,
        'canonical_sources':68,'versioned_records':79,'payload_hashes_verified':66,'main_missing_targets':3,'representation_limits':6,
        'schema_executable':True,'original_db_recovered':False,'source_references_and_aliases_verified':True,
        'manifest_entries_verified':len(sealed_files) if sealed_files else None,'zip_crc_and_members_verified':bool(archive),
        'database_sha256':digest(db),'database_bytes':db.stat().st_size,'remote_restore_verified':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package',required=True);p.add_argument('--baseline-root',required=True);p.add_argument('--archive')
    p.add_argument('--report')
    a=p.parse_args();result=verify(a.package,a.baseline_root,a.archive)
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.report:Path(a.report).write_text(text)
    print(text)
