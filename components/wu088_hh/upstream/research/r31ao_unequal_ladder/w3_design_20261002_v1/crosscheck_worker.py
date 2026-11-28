"""Existing endpoint evaluator under the external pinned hard process guard."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
LADDER = HERE.parent
source = LADDER/'production_solver_20261001_v1/endpoint_tasks/planner.py'
if hashlib.sha256(source.read_bytes()).hexdigest()!='53fe8cea32fb24efe9ef2682f480d63595db2bf32525ed57f46df391fe3eb4e6':
    raise ValueError('pinned planner source mismatch')
spec=importlib.util.spec_from_file_location('_w3_crosscheck_planner',source)
p=importlib.util.module_from_spec(spec);sys.modules[spec.name]=p;spec.loader.exec_module(p)
plan=p.read_json(HERE/'runtime/CROSSCHECK_PLAN.json')
if not (plan['window']['l_t']==plan['window']['l_u']=='1/512'
        and plan['window']['T_t']==plan['window']['T_u']
        and plan['window']['T_t'] in [str(1<<n) for n in (32,40,48,56,64)]
        and plan['precision_bits']==128 and plan['caps']['wall_seconds']==30
        and plan['caps']['memory_bytes']==512*1024**2):
    raise ValueError('crosscheck outside fixed campaign contract')
raw=(LADDER/'production_solver_20261001_v1/inputs/FROZEN_INPUTS.npz').read_bytes()
result=p.evaluate_task(plan,0,source_archive_bytes=raw)
p.validate_result(plan,result)
p.write_new(HERE/'runtime/CROSSCHECK_RESULT.json',result)
print(json.dumps({k:result[k] for k in ('status','index','engine_calls','result_sha256')}))
raise SystemExit(0 if result['status']=='CONDITIONAL_TAIL_BOUND' else 2)
