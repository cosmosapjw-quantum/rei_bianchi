PRAGMA foreign_keys=ON;

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

CREATE TABLE acquisition_events(
 event_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source_catalog(source_id),
 record_id TEXT REFERENCES source_versions(record_id), attempted_url TEXT, utc TEXT,
 http_status_or_error TEXT, failure_class TEXT, retryable INTEGER, fallback_attempted INTEGER,
 event_kind TEXT NOT NULL, evidence_origin TEXT NOT NULL, record_json TEXT NOT NULL CHECK(json_valid(record_json))
);

CREATE TABLE acquisition_gaps(
 gap_id TEXT PRIMARY KEY, source_id TEXT REFERENCES source_catalog(source_id), artifact_id TEXT,
 gap_scope TEXT NOT NULL, requested_identity TEXT, failure_class TEXT, remaining_gap TEXT NOT NULL,
 minimum_next_action TEXT, evidence_origin TEXT NOT NULL, prevents_acquisition_completion_all INTEGER NOT NULL
);

CREATE TABLE assets(asset_id TEXT PRIMARY KEY,source_id TEXT REFERENCES sources(id),path TEXT,bytes INTEGER,sha256 TEXT,representation TEXT,requested_url TEXT,final_url TEXT,retrieved_utc TEXT,record_json TEXT);

CREATE TABLE attempts(source_id TEXT REFERENCES sources(id),attempt_number INTEGER,record_json TEXT,PRIMARY KEY(source_id,attempt_number));

CREATE TABLE backup_objects(
 provider TEXT, object_id TEXT, backup_set_id TEXT NOT NULL, filename TEXT, path_or_parent TEXT,
 bytes INTEGER, local_sha256 TEXT, upload_ack INTEGER, metadata_size_matches INTEGER,
 verification_tier TEXT, remote_checksum_verified INTEGER NOT NULL, restore_verified INTEGER NOT NULL,
 evidence_origin TEXT NOT NULL, PRIMARY KEY(provider,object_id)
);

CREATE TABLE blocker_map(source_id TEXT REFERENCES sources(id),blocker TEXT,PRIMARY KEY(source_id,blocker));

CREATE VIRTUAL TABLE catalog_search USING fts5(source_id UNINDEXED, title, authors, identifiers, status, representation, notes);

CREATE TABLE citation_occurrences(id INTEGER PRIMARY KEY,start_idx INTEGER,end_idx INTEGER,original_token TEXT,urls_json TEXT);

CREATE TABLE code_version_policy(
 policy_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source_catalog(source_id),
 repository TEXT, release_tag_version TEXT, version_requested TEXT, version_acquired TEXT,
 raw_source_acquired INTEGER NOT NULL, commit_sha TEXT, tree_sha TEXT, release_date TEXT,
 source_archive_sha256 TEXT, bytes INTEGER, license TEXT, dependencies_json TEXT,
 canonical_upstream_url TEXT, acquisition_utc TEXT, authority_role TEXT, version_selection_rule TEXT,
 latest_stable_target_selected INTEGER NOT NULL, record_json TEXT NOT NULL CHECK(json_valid(record_json))
);

CREATE TABLE db_build_metadata(key TEXT PRIMARY KEY, value_json TEXT NOT NULL);

CREATE TABLE metadata(key TEXT PRIMARY KEY,value_json TEXT);

CREATE TABLE original_research_database_status(
 artifact_id TEXT PRIMARY KEY, original_filename TEXT NOT NULL, expected_reported_sha256 TEXT NOT NULL,
 original_bytes_recovered INTEGER NOT NULL CHECK(original_bytes_recovered=0),
 reconstruction_equivalence TEXT NOT NULL, reconstruction_filename TEXT, reconstruction_sha256 TEXT,
 reconstruction_bytes INTEGER, recovered_explicit_source_rows INTEGER, recovered_explicit_blocker_rows INTEGER,
 unexported_entity_tables_json TEXT NOT NULL CHECK(json_valid(unexported_entity_tables_json)), evidence_origin TEXT NOT NULL
);

CREATE TABLE recovery_artifacts(id TEXT PRIMARY KEY,status TEXT,record_json TEXT);

CREATE TABLE recovery_updates(source_id TEXT PRIMARY KEY, successor_record_id TEXT,
        acquisition_status TEXT, remaining_gap TEXT, closed INTEGER, record_json TEXT NOT NULL);

CREATE TABLE relations(source_id TEXT REFERENCES sources(id),related_id TEXT REFERENCES sources(id),relation TEXT,PRIMARY KEY(source_id,related_id,relation));

CREATE TABLE report_documents(document_id TEXT PRIMARY KEY, original_package_path TEXT, sha256 TEXT, body TEXT NOT NULL);

CREATE TABLE report_example_rows(
 example_table TEXT, row_number INTEGER, row_json TEXT NOT NULL CHECK(json_valid(row_json)),
 evidence_origin TEXT NOT NULL, PRIMARY KEY(example_table,row_number)
);

CREATE VIRTUAL TABLE report_search USING fts5(section_id UNINDEXED, heading, body);

CREATE TABLE report_sections(
 section_id TEXT PRIMARY KEY, document_id TEXT REFERENCES report_documents(document_id),
 heading TEXT, start_line INTEGER, end_line INTEGER, body TEXT NOT NULL
);

CREATE TABLE representation_identity(source_id TEXT PRIMARY KEY, requested_identity TEXT,
        acquired_representation TEXT, representation_equivalence TEXT, publisher_version_available INTEGER,
        fallback_chain TEXT, version_selection_rule TEXT, version_requested TEXT, version_acquired TEXT,
        version_is_latest_stable INTEGER, commit_sha TEXT, tree_sha TEXT, source_sha256 TEXT,
        bytes INTEGER, license TEXT, retrieved_utc TEXT, failure_class TEXT, remaining_gap TEXT,
        backup_object_ids TEXT, restore_verified INTEGER NOT NULL DEFAULT 0);

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

CREATE TABLE source_file_links(
 source_id TEXT REFERENCES source_catalog(source_id), asset_id TEXT REFERENCES acquired_files(asset_id),
 link_role TEXT, evidence_origin TEXT NOT NULL, PRIMARY KEY(source_id,asset_id,link_role)
);

CREATE TABLE source_versions(
 record_id TEXT PRIMARY KEY REFERENCES sources(id), source_id TEXT NOT NULL REFERENCES source_catalog(source_id),
 parent_record_id TEXT REFERENCES sources(id), historical_status TEXT, representation TEXT, provenance_json TEXT NOT NULL CHECK(json_valid(provenance_json))
);

CREATE TABLE sources(id TEXT PRIMARY KEY,title TEXT,source_type TEXT,scope TEXT,status TEXT,coverage TEXT,version_or_ref TEXT,resolved_commit TEXT,resolved_tree TEXT,doi TEXT,arxiv TEXT,year INTEGER,authors TEXT,record_json TEXT NOT NULL);

CREATE INDEX asset_hash_index ON assets(sha256);

CREATE INDEX events_source_time ON acquisition_events(source_id,utc);

CREATE INDEX files_sha256 ON acquired_files(sha256);

CREATE INDEX gaps_source ON acquisition_gaps(source_id);

CREATE VIEW effective_assets AS SELECT asset_id,source_id,
        CASE WHEN path LIKE 'recovery/%' THEN path ELSE 'previous_v1/'||path END AS package_path,
        bytes,sha256,representation,requested_url,final_url,retrieved_utc FROM assets;

CREATE VIEW effective_sources AS SELECT s.id,s.title,s.source_type,
        coalesce(r.acquisition_status,s.status) AS acquisition_status,
        r.successor_record_id,r.remaining_gap FROM sources s
        LEFT JOIN recovery_updates r ON s.id=r.source_id
        WHERE s.id IN (SELECT id FROM sources WHERE scope!='ACQUISITION_RECOVERY') OR s.id='C14';

CREATE VIEW v_current_missing AS SELECT * FROM acquisition_gaps WHERE prevents_acquisition_completion_all=1;

CREATE VIEW v_failed_attempts AS SELECT * FROM acquisition_events WHERE failure_class IS NOT NULL;

CREATE VIEW v_payload_backup_sets AS
 SELECT f.asset_id,f.source_id,f.package_path,f.sha256,b.provider,b.object_id,b.filename,b.path_or_parent,b.verification_tier,b.restore_verified
 FROM acquired_files f JOIN backup_objects b USING(backup_set_id);

CREATE VIEW v_source_files AS
 SELECT s.source_id,s.title,l.link_role,f.asset_id,f.record_id,f.package_path,f.sha256,f.bytes,f.observed_format,f.retrieved_utc
 FROM source_catalog s JOIN source_file_links l USING(source_id) JOIN acquired_files f USING(asset_id);
