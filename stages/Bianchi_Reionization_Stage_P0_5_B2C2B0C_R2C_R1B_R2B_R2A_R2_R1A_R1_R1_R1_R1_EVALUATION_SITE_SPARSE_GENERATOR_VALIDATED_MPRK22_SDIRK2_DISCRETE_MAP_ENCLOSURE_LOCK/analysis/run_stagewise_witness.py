#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parent;REPO=STAGE.parents[1]
prior=next(REPO.glob('stages/*SPARSE_LOCAL_GENERATOR_AFFINE_TAYLOR_MODEL_ENCLOSURE_LOCK'))
s=importlib.util.spec_from_file_location('evalsite_temporal_witness',prior/'analysis/temporal_control_audit.py')
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
lanes=('LOCAL_NEUTRAL_HAZARD_PRIMARY','RECOMBINATION_WEIGHTED_AUDITOR','SCRIPT_SELF_SHIELDING_AUDITOR')
started=time.perf_counter();rows=[m.run_temporal_control_audit(REPO,lane=x).to_dict() for x in lanes]
result={'classification':'FRESH_STAGEWISE_SWITCH_WITNESS_REPLAY','rows':rows,
 'all_hard_gates_pass':all(r['all_trial_hard_gates_pass'] for r in rows),
 'all_escape_static_hull':all(r['outside_node_count']>0 for r in rows),
 'max_outside_absolute':max(r['maximum_outside_absolute'] for r in rows),
 'max_outside_fraction_of_static_width':max(r['maximum_outside_fraction_of_static_width'] for r in rows),
 'elapsed_s':time.perf_counter()-started}
(STAGE/'data/STAGEWISE_WITNESS_REPLAY.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({'all_hard_gates_pass':result['all_hard_gates_pass'],'all_escape_static_hull':result['all_escape_static_hull'],'max_outside_absolute':result['max_outside_absolute'],'max_fraction':result['max_outside_fraction_of_static_width'],'elapsed_s':result['elapsed_s']},indent=2))
