from pathlib import Path
import hashlib,importlib.util,json,resource,sys,time
sys.dont_write_bytecode=True
U=Path(__file__).resolve().parent
if (U/'RUN_INPUT.json').exists():raise SystemExit('Initial attempt recorded; no automatic replay')
manifest=json.loads((U/'INPUT_BINDINGS.json').read_text())
for row in manifest['files']:
    for path in (Path(row['path']),U/row['unit_relative_path']):
        raw=path.read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],'PREEXEC_INPUT_IDENTITY_CHANGE'
spec=importlib.util.spec_from_file_location('bounded_child',U.parents[1]/'helpers/bounded_child.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
config={'argv':[sys.executable,str(U/'suite.py')],'cwd':str(U),'timeout_seconds':30,'cpu_seconds':8,'address_space_bytes':256*1024**2,'output_prefix':str(U/'RUN')}
ip=U/'RUN_INPUT.json';ip.write_text(json.dumps(config,indent=2)+'\n');start=time.monotonic();before=resource.getrusage(resource.RUSAGE_SELF);rc=runner.run(ip);after=resource.getrusage(resource.RUSAGE_SELF)
r=json.loads((U/'RUN.receipt.json').read_text());r['runner_parent_overhead']={'user_seconds':after.ru_utime-before.ru_utime,'system_seconds':after.ru_stime-before.ru_stime,'wall_minus_child_seconds':time.monotonic()-start-r['wall_seconds']};r['host_global_overhead']='UNKNOWN_NOT_ZERO';r['ledger']='NEW_H_LI_REGISTRY_8CPU_30WALL_256MiB_NO_OLD_ALLOWANCE_TRANSFER';r['worker_count']=1;r['attempt']=1
(U/'RUN_RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
raise SystemExit(rc)
