from pathlib import Path
import hashlib,importlib.util,json,resource,sys,time
sys.dont_write_bytecode=True
U=Path(__file__).resolve().parent
if (U/'REPAIR_INPUT.json').exists():raise SystemExit('Targeted retry already recorded; stop')
for row in json.loads((U/'INPUT_BINDINGS.json').read_text())['files']:
    for path in (Path(row['path']),U/row['unit_relative_path']):
        raw=path.read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],'REPAIR_PREEXEC_SOURCE_CHANGE'
first=json.loads((U/'attempts/attempt001/RUN_RECEIPT.json').read_text());used=first['user_seconds']+first['system_seconds']
spec=importlib.util.spec_from_file_location('bounded_child',U.parents[1]/'helpers/bounded_child.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
config={'argv':[sys.executable,str(U/'suite.py')],'cwd':str(U),'timeout_seconds':30-first['wall_seconds'],'cpu_seconds':int(8-used),'address_space_bytes':256*1024**2,'output_prefix':str(U/'REPAIR_RUN')}
ip=U/'REPAIR_INPUT.json';ip.write_text(json.dumps(config,indent=2)+'\n');start=time.monotonic();before=resource.getrusage(resource.RUSAGE_SELF);rc=runner.run(ip);after=resource.getrusage(resource.RUSAGE_SELF);retry=json.loads((U/'REPAIR_RUN.receipt.json').read_text())
result={'unit':'H_LI_SPECIES_COMPLETENESS_20261028','attempts':2,'targeted_repairs':1,'initial_exit':first['returncode'],'final_exit':rc,'first_attempt_receipt':'attempts/attempt001/RUN_RECEIPT.json','retry':retry,'cumulative_child_cpu_seconds':used+retry['user_seconds']+retry['system_seconds'],'cumulative_child_wall_seconds':first['wall_seconds']+retry['wall_seconds'],'peak_child_RSS_KiB':max(first['maxrss_native'],retry['maxrss_native']),'original_caps':{'cpu_seconds':8,'wall_seconds':30,'address_space_bytes':256*1024**2},'retry_parent_overhead':{'user_seconds':after.ru_utime-before.ru_utime,'system_seconds':after.ru_stime-before.ru_stime,'wall_minus_child_seconds':time.monotonic()-start-retry['wall_seconds']},'first_parent_overhead':first['runner_parent_overhead'],'host_global_overhead':'UNKNOWN_NOT_ZERO','diagnostic_source_diff_overhead':'Read-only source inspection outside scientific child; unmeasured parent/global, not zero','historical_allowance_transfer':0}
(U/'CUMULATIVE_RUN_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
if result['cumulative_child_cpu_seconds']>8 or result['cumulative_child_wall_seconds']>30:raise SystemExit('CUMULATIVE_RESOURCE_STOP')
raise SystemExit(rc)
