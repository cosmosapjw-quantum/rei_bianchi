PRAGMA foreign_keys=ON;
CREATE TABLE meta(key TEXT PRIMARY KEY,value_json TEXT NOT NULL CHECK(json_valid(value_json)));
CREATE TABLE artifacts(
 artifact_id TEXT PRIMARY KEY,namespace TEXT NOT NULL,relative_path TEXT NOT NULL,
 bytes INTEGER NOT NULL CHECK(bytes>=0),sha256 TEXT NOT NULL CHECK(length(sha256)=64),
 UNIQUE(namespace,relative_path));
CREATE TABLE source_links(
 link_id TEXT PRIMARY KEY,from_artifact TEXT NOT NULL REFERENCES artifacts,
 to_artifact TEXT REFERENCES artifacts,relation TEXT NOT NULL,json_pointer TEXT,
 declared_sha256 TEXT CHECK(declared_sha256 IS NULL OR length(declared_sha256)=64),
 verification TEXT NOT NULL);
CREATE TABLE run_records(
 run_id TEXT PRIMARY KEY,source_artifact TEXT NOT NULL REFERENCES artifacts,
 component TEXT NOT NULL,source_schema TEXT,reported_status TEXT,
 reported_exit_code INTEGER,reported_scope TEXT,
 facts_json TEXT NOT NULL CHECK(json_valid(facts_json)));
CREATE TABLE stage_delta(
 delta_id TEXT PRIMARY KEY,stage_id TEXT NOT NULL,status TEXT NOT NULL,
 scope TEXT NOT NULL,source_artifact TEXT NOT NULL REFERENCES artifacts,
 run_id TEXT REFERENCES run_records,claim_limit TEXT NOT NULL);
CREATE INDEX source_links_target ON source_links(to_artifact);
CREATE INDEX run_records_component ON run_records(component);
CREATE INDEX stage_delta_stage ON stage_delta(stage_id);
