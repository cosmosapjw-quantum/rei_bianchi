"""Run only the C2g registered read-only analysis under inherited bounded guard."""
from pathlib import Path
import json,os,secrets,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from runtime_support import atomic_create,code_identity,execution_environment,file_identity,GIB,host_preflight
from launch_manufactured import OwnedProcessGuard,monitor_process,OWNER_ENV

def main():
    output=ROOT/'results/analysis/ANALYSIS.json'
    output.parent.mkdir(exist_ok=False)
    report=ROOT/'results/ANALYSIS_RUNTIME.json'
    prereg=json.loads((ROOT/'contract/PHYSICAL_PREREGISTRATION.json').read_text())
    campaign=prereg['campaign'];before=code_identity(ROOT/'code');host=host_preflight()
    if host['effective_cpu_budget']<1:raise RuntimeError('no effective CPU budget')
    if campaign['postprocess_sampled_memory_gib']*GIB>host['memory_available_bytes']:raise RuntimeError('analysis budget exceeds observed available memory')
    env=execution_environment(1,'none');env[OWNER_ENV]=secrets.token_hex(32)
    command=[sys.executable,str(ROOT/'code/analyze_reference.py'),'--manifest',str(ROOT/'contract/PHYSICAL_TASKS.json'),'--review',str(ROOT/'review/PHYSICAL_LAUNCH_REVIEW.json'),'--layout', 'numpy_serial_1x1='+str(ROOT/'results/numpy_serial_1x1.json'),'--layout','native_mpi_2x1='+str(ROOT/'results/native_mpi_2x1.json'),'--output',str(output)]
    with (output.parent/'stdout.txt').open('xb') as stdout,(output.parent/'stderr.txt').open('xb') as stderr:
        proc=subprocess.Popen(command,env=env,cwd=ROOT,stdout=stdout,stderr=stderr,start_new_session=True)
        guard=OwnedProcessGuard(proc,env[OWNER_ENV])
        try:process=monitor_process(proc,guard,campaign['postprocess_wall_seconds'],campaign['postprocess_sampled_memory_gib']*GIB)
        except BaseException:
            guard.stop();raise
        finally:
            guard.close();stdout.flush();os.fsync(stdout.fileno());stderr.flush();os.fsync(stderr.fileno())
    unchanged=code_identity(ROOT/'code')==before
    ok=process['returncode']==0 and process['termination'] is None and unchanged and output.exists()
    atomic_create(report,{'status':'PASS' if ok else 'FAIL','process':process,'source_unchanged':unchanged,'source_identity':before,'host_preflight':host,'command':command,'result':file_identity(output) if output.exists() else None,'physical_eigensolves':0,'helper_identity':file_identity(__file__)})
    print(json.dumps({'status':'PASS' if ok else 'FAIL','result':str(output),'runtime':str(report)}));return 0 if ok else 1
if __name__=='__main__':raise SystemExit(main())
