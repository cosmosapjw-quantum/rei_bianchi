PRAGMA foreign_keys=ON;
CREATE TABLE w3_meta(key TEXT PRIMARY KEY,value_json TEXT NOT NULL CHECK(json_valid(value_json)));
CREATE TABLE w3_artifacts(
 artifact_id TEXT PRIMARY KEY,namespace TEXT NOT NULL,relative_path TEXT NOT NULL,
 bytes INTEGER NOT NULL CHECK(bytes>=0),sha256 TEXT NOT NULL CHECK(length(sha256)=64),
 UNIQUE(namespace,relative_path));
CREATE TABLE w3_execution_records(
 record_id TEXT PRIMARY KEY,kind TEXT NOT NULL CHECK(kind IN('ACTUAL_ENDPOINT_SELECTION','ACTUAL_ENDPOINT_CROSSCHECK')),
 primitive_index INTEGER NOT NULL CHECK(primitive_index=0),
 accepted INTEGER NOT NULL CHECK(accepted IN(0,1)),status TEXT NOT NULL,
 native_integration_invocations INTEGER NOT NULL CHECK(native_integration_invocations=0),
 candidate_polynomial_evaluations INTEGER NOT NULL CHECK(candidate_polynomial_evaluations>=0),
 receipt_artifact TEXT NOT NULL UNIQUE REFERENCES w3_artifacts,
 receipt_sha256 TEXT NOT NULL UNIQUE,output_artifact TEXT NOT NULL UNIQUE REFERENCES w3_artifacts,
 output_sha256 TEXT NOT NULL UNIQUE,declared_record_json TEXT NOT NULL CHECK(json_valid(declared_record_json)));
CREATE TABLE w3_host_events(
 event_index INTEGER PRIMARY KEY,event_json TEXT NOT NULL CHECK(json_valid(event_json)));
CREATE TABLE w3_stage_delta(
 stage_id TEXT PRIMARY KEY CHECK(stage_id IN('G0','G1','G2','G3','G4','G5','G6','G7','G8','G9')),
 prior_status TEXT NOT NULL,current_status TEXT NOT NULL,scope TEXT NOT NULL,
 remaining_gates_json TEXT NOT NULL CHECK(json_valid(remaining_gates_json)),
 source_artifact TEXT NOT NULL REFERENCES w3_artifacts,
 prior_source_artifact TEXT NOT NULL REFERENCES w3_artifacts);
CREATE TABLE w3_stage_evidence(
 stage_id TEXT NOT NULL REFERENCES w3_stage_delta,
 source_artifact TEXT NOT NULL REFERENCES w3_artifacts,
 declared_sha256 TEXT NOT NULL,PRIMARY KEY(stage_id,source_artifact));
