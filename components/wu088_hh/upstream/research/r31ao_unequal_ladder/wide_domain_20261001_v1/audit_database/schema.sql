PRAGMA foreign_keys=ON;
CREATE TABLE meta(key TEXT PRIMARY KEY,value_json TEXT NOT NULL CHECK(json_valid(value_json)));
CREATE TABLE artifacts(
 artifact_id TEXT PRIMARY KEY,namespace TEXT NOT NULL,relative_path TEXT NOT NULL,
 bytes INTEGER NOT NULL CHECK(bytes>=0),sha256 TEXT NOT NULL CHECK(length(sha256)=64),
 UNIQUE(namespace,relative_path));
CREATE TABLE prior_artifact_records(
 prior_artifact_id TEXT PRIMARY KEY,namespace TEXT NOT NULL,relative_path TEXT NOT NULL,
 bytes INTEGER NOT NULL CHECK(bytes>=0),sha256 TEXT NOT NULL CHECK(length(sha256)=64),
 provenance_artifact TEXT NOT NULL REFERENCES artifacts);
CREATE TABLE source_links(
 link_id TEXT PRIMARY KEY,from_artifact TEXT NOT NULL REFERENCES artifacts,
 to_artifact TEXT REFERENCES artifacts,to_prior_record TEXT REFERENCES prior_artifact_records,
 relation TEXT NOT NULL,json_pointer TEXT,declared_sha256 TEXT,
 verification TEXT NOT NULL,
 CHECK(to_artifact IS NULL OR to_prior_record IS NULL));
CREATE TABLE run_records(
 run_id TEXT PRIMARY KEY,source_artifact TEXT NOT NULL REFERENCES artifacts,
 json_pointer TEXT NOT NULL,component TEXT NOT NULL,
 status_fields_json TEXT NOT NULL CHECK(json_valid(status_fields_json)),
 exit_fields_json TEXT NOT NULL CHECK(json_valid(exit_fields_json)),
 scalar_fields_json TEXT NOT NULL CHECK(json_valid(scalar_fields_json)),
 UNIQUE(source_artifact,json_pointer));
CREATE TABLE stage_delta(
 stage_id TEXT PRIMARY KEY CHECK(stage_id IN('G0','G1','G2','G3','G4','G5','G6','G7','G8','G9')),
 prior_status TEXT NOT NULL,current_status TEXT NOT NULL,scope TEXT NOT NULL,
 remaining_gates_json TEXT NOT NULL CHECK(json_valid(remaining_gates_json)),
 source_artifact TEXT NOT NULL REFERENCES artifacts,
 prior_source_artifact TEXT NOT NULL REFERENCES artifacts);
CREATE TABLE stage_evidence(
 stage_id TEXT NOT NULL REFERENCES stage_delta,source_artifact TEXT NOT NULL REFERENCES artifacts,
 declared_sha256 TEXT NOT NULL,PRIMARY KEY(stage_id,source_artifact));
