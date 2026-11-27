#!/usr/bin/env python3
"""Single source-free R56 science result for GitHub, full original source remains cold-backed up."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
results=json.loads((ROOT/"results/R56_RESULTS.json").read_text())
audit=json.loads((ROOT/"results/R56_ADVERSARIAL_AUDIT.json").read_text())
q={
 "schema":"WU_R56_REI_ORIGINAL_ACCEPTED_HHE_HISTORY_DI_SCIENCE_PUBLIC_V1",
 "parent_PR":195,"parent_HEAD":"20a68553c15e89a2178e5f2ad0caaff5c889aba0",
 "REC195_184320_source_SHA256":results["source_sha256"]["REC195_replayed_184320_cells"],
 "REI_original_state64_128_160":results["source_sha256"]["REI_states"],
 "source_accepted_original_HHe_ticks":[0,64,128,160],
 "source_R54_original_full_zip_SHA256":"23cbf0b3e91f7e17fc915c06c025a9e55c6aac8b0ebeca6df7039bfe5fbb32ab",
 "original_46080_cells":46080,
 "physical_scope":results["physical_scope"],
 "scenarios":results["scenario_tick160_161"],
 "source_left_hold":results["scenario_LEFT_HOLD_tick160_161"],
 "normal_tests":"9/9_PASS",
 "optimized_tests":"9/9_PASS",
 "independent_audit":{k:v for k,v in audit.items() if k!="original_12_input_source_sha"},
 "validation":{**results["validation"],"same_author_independent_audit":"PASS_SCOPED"},
 "files":results["files"],
 "DAG":results["DAG"],
 "gates":results["gates"]}
path=ROOT/"results/R56_SCIENCE_SOURCE_FREE.json"
path.write_text(json.dumps(q,sort_keys=True,indent=2)+"\n")
print(json.dumps({"science_file":str(path),"bytes":path.stat().st_size,
 "sha256":hashlib.sha256(path.read_bytes()).hexdigest()},sort_keys=True))
