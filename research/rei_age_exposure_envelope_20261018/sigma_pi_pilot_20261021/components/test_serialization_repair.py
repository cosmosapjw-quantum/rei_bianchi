"""One no-IVP regression for bool serialization, deadline and explicit rebind."""
import sys,time,json,tempfile,contextlib,io
from pathlib import Path
sys.dont_write_bytecode=True
begin=time.monotonic();sys.path.insert(0,str(Path(__file__).resolve().parent))
import unified_pilot as u
import numpy as np
base=u.ROOT/'z2_extension/results';manifest=json.loads((base/'MANIFEST.json').read_text());c=manifest['cases'][0];d=base/'cases'/c['id']
with np.load(d/'raw.npz') as f:raw={k:f[k] for k in f.files}
with np.load(d/'tail.npz') as f:tail={k:f[k] for k in f.files}
with np.load(u.ROOT/c['prefix_relative']/'raw.npz') as f:prefix={k:f[k] for k in f.files}
checks=u.tail_validate(c['config'],u.SimpleNamespace(t=raw['x'],y=raw['raw_y'],success=True),{k:v for k,v in raw.items() if k not in ('x','raw_y')},prefix,u.SimpleNamespace(t=tail['x'],y=tail['raw_y']))
results={'native_join_bool':type(checks['exact_join_x']) is bool,'checks_json_serializable':bool(json.dumps(checks))}
with tempfile.TemporaryDirectory(prefix='rei_explicit_rebind_') as temp:
 f=Path(temp)/'RESUME_CODE_IDENTITY.json';f.write_bytes((base/'RESUME_CODE_IDENTITY.json').read_bytes());before=u.sha(f);identity=u.bind_execution_identity(Path(temp))
 results['original_identity_preserved']=u.sha(f)==before
 results['explicit_new_identity_sidecar']=(Path(temp)/'RESUME_CODE_IDENTITY.OPERATIONAL_REPAIR.json').exists() and identity['sha256']['components/unified_pilot.py']==u.sha(u.__file__)
# Exercise main's exact CLI validation without launching a worker/controller.
observed={};old_run=u.run
u.run=lambda output,profile,requested,resume,approval:observed.update(deadline=u.LIMITS[profile]['case_s'],workers=requested) or {'states':{},'cumulative_child_charged_wall_s':0.,'controller_elapsed_s':0.,'stop_reason':'NO_WORKER_TEST','exit':0}
sys.argv=[__file__,'run','--phase','b2','--max-workers','2','--case-deadline','10','--review-approval','not_read_in_no_worker_test']
with contextlib.redirect_stdout(io.StringIO()):u.main()
results['actual_cli_10s_two_workers']=observed=={'deadline':10.,'workers':2}
results['reservation_fits_unchanged120']=90.08237553801882+2*observed['deadline']<=120. and 90.08237553801882+30.>120.
sys.argv=[__file__,'run','--phase','b2','--case-deadline','31']
try:
 with contextlib.redirect_stderr(io.StringIO()):u.main()
 results['deadline_above_contract_rejected']=False
except SystemExit as e:results['deadline_above_contract_rejected']=e.code==2
u.run=old_run
r={'checks':results,'pass':all(results.values()),'elapsed_s':time.monotonic()-begin,'no_IVP_calls':True,'no_worker_launches':True,'runner_sha256':u.sha(u.__file__)}
u.atomic_json(u.ROOT/'components/SERIALIZATION_REPAIR_MECHANICAL.json',r)
print(json.dumps(r,indent=2));sys.exit(0 if r['pass'] else 1)
