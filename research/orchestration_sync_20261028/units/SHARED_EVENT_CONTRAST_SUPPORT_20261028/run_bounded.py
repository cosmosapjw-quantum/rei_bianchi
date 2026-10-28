from pathlib import Path
import hashlib,importlib.util,json,resource,sys,time
sys.dont_write_bytecode=True
U=Path(__file__).resolve().parent
if (U/'RUN_INPUT.json').exists():raise SystemExit('Attempt recorded; no automatic replay')
manifest=json.loads((U/'INPUT_BINDINGS.json').read_text())
for row in manifest['files']:
    assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256'],'PRECHILD_SOURCE_BYTE_CHANGE'
spec=importlib.util.spec_from_file_location('bounded_child',U.parents[1]/'helpers/bounded_child.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
config={'argv':[sys.executable,str(U/'suite.py')],'cwd':str(U),'timeout_seconds':29,'cpu_seconds':14,'address_space_bytes':512*1024**2,'output_prefix':str(U/'SCIENCE')}
ip=U/'RUN_INPUT.json';ip.write_text(json.dumps(config,indent=2)+'\n');start=time.monotonic();before=resource.getrusage(resource.RUSAGE_SELF);rc=runner.run(ip);science=json.loads((U/'SCIENCE.receipt.json').read_text());render=None
if not rc:
    remaining_cpu=15-science['user_seconds']-science['system_seconds'];remaining_wall=30-science['wall_seconds']
    config={'argv':['/usr/bin/inkscape',str(U/'correlation_gaps.svg'),'--export-type=png','--export-filename='+str(U/'correlation_gaps.png')],'cwd':str(U),'timeout_seconds':remaining_wall,'cpu_seconds':max(1,int(remaining_cpu)),'address_space_bytes':512*1024**2,'output_prefix':str(U/'RENDER')}
    ip=U/'RENDER_INPUT.json';ip.write_text(json.dumps(config,indent=2)+'\n');rc=runner.run(ip);render=json.loads((U/'RENDER.receipt.json').read_text())
after=resource.getrusage(resource.RUSAGE_SELF);receipts=[science]+([render] if render else [])
r={'schema':'shared-event-composition-aggregate-resource-v1','returncode':rc,'science':science,'render':render,'sum_child_cpu_seconds':sum(x['user_seconds']+x['system_seconds'] for x in receipts),'sum_child_wall_seconds':sum(x['wall_seconds'] for x in receipts),'maximum_child_peak_rss_KiB':max(x['maxrss_native'] for x in receipts),'caps':{'total_cpu_seconds':15,'total_wall_seconds':30,'perchild_address_space_bytes':512*1024**2,'science_workers':1},'runner_parent_overhead':{'user_seconds':after.ru_utime-before.ru_utime,'system_seconds':after.ru_stime-before.ru_stime,'wrapper_wall_seconds':time.monotonic()-start,'wall_minus_children_seconds':time.monotonic()-start-sum(x['wall_seconds'] for x in receipts)},'host_global_overhead':'UNKNOWN_NOT_ZERO','ledger':'NEW_INDEPENDENT_SYNTHESIS_UNIT_NO_OWNER_DEBIT_TRANSFER','science_attempts':1}
(U/'RUN_RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
if r['sum_child_cpu_seconds']>15 or r['sum_child_wall_seconds']>30:raise SystemExit('RESOURCE_CAP_STOP')
raise SystemExit(rc)
