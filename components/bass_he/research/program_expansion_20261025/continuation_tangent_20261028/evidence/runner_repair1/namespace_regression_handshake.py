"""One diagnostic child, no scientific imports/calls. CPU2s/wall5s/AS768MiB."""
import importlib.util
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
UNIT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('runner_under_test',UNIT/'scripts/run_once.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
resource.setrlimit(resource.RLIMIT_CPU,(2,2))
resource.setrlimit(resource.RLIMIT_AS,(768*1024**2,768*1024**2))
os.environ.update({key:'1' for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']})
child_code="import json,os,pathlib,resource,time; print(json.dumps({'local_pid':os.getpid(),'local_pgrp':os.getpgrp(),'proc_self_status':pathlib.Path('/proc/self/status').read_text(),'proc_self_stat':pathlib.Path('/proc/self/stat').read_text(),'own_user_CPU':resource.getrusage(resource.RUSAGE_SELF).ru_utime,'own_system_CPU':resource.getrusage(resource.RUSAGE_SELF).ru_stime}),flush=True);time.sleep(.1)"
command=[sys.executable,'-c',child_code]
start=time.monotonic();base=resource.getrusage(resource.RUSAGE_CHILDREN)
identity_path=HERE/'REGRESSION_MONITOR_IDENTITY.json'
child=subprocess.Popen(command,start_new_session=True,preexec_fn=lambda:runner.write_monitor_identity(identity_path),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
namespace=runner.resolve_host_group(child.pid,identity_path)
observed_group_cpu=runner.group_cpu(namespace['child_host_pgrp'])
out,err=child.communicate(timeout=5)
(HERE/'regression_handshake_child_stdout.log').write_text(out);(HERE/'regression_handshake_child_stderr.log').write_text(err)
raw=json.loads(out)
self_usage=resource.getrusage(resource.RUSAGE_SELF);children_usage=resource.getrusage(resource.RUSAGE_CHILDREN)
wall=time.monotonic()-start
cpu=self_usage.ru_utime+self_usage.ru_stime+children_usage.ru_utime+children_usage.ru_stime-base.ru_utime-base.ru_stime
raw_host_pid=int(raw['proc_self_stat'].split()[0]);fields=raw['proc_self_stat'][raw['proc_self_stat'].rfind(')')+2:].split();raw_host_group=int(fields[2])
passed=child.returncode==0 and not err and raw['local_pid']==child.pid and namespace['child_host_pid']==raw_host_pid and namespace['child_host_pgrp']==raw_host_group and namespace['child_local_pgrp']==namespace['child_local_pid'] and namespace['child_host_pgrp']==namespace['child_host_pid'] and observed_group_cpu<1 and cpu<2 and wall<5
result={'status':'PASS' if passed else 'FAIL','command':command,'entry_command':[sys.executable,str(Path(__file__).resolve())],'namespace':namespace,'child_reported_local_pid':raw['local_pid'],'child_reported_local_pgrp':raw['local_pgrp'],'child_reported_host_pid':raw_host_pid,'child_reported_host_pgrp':raw_host_group,'observed_group_CPU_seconds':observed_group_cpu,'whole_regression_runner_waited_child_CPU_seconds':cpu,'wall_seconds':wall,'exit_code':child.returncode,'limits':{'CPU_seconds':2,'wall_seconds':5,'AS_bytes':768*1024**2,'threads':1},'scientific_imports_calls':0,'diagnostic_child_count':1}
(HERE/'NAMESPACE_REGRESSION_HANDSHAKE.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
sys.exit(0 if passed else 1)
