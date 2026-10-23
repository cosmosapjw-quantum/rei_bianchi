"""Bounded one-thread invocation and cumulative exact/debited usage."""
from pathlib import Path
import argparse,json,os,resource,subprocess,sys,time
BASE=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('script');p.add_argument('args',nargs='*');a=p.parse_args()
    R=BASE/'results';R.mkdir(parents=True,exist_ok=True);rp=R/'cost_receipts.json'
    state=json.loads(rp.read_text()) if rp.exists() else {'limits':{'CPU_s':120.,'wall_s':180.,'child_CPU_s':60.,'child_wall_s':90.,'memory_bytes':1073741824,'threads':1},'invocations':[]}
    if any(x['name']==a.name for x in state['invocations']):raise RuntimeError('INVOCATION_ALREADY_RECORDED')
    cpu=min(60,int(120-sum(x['CPU_charge_s'] for x in state['invocations'])));wall=min(90.,180-sum(x['wall_charge_s'] for x in state['invocations']))
    if cpu<1 or wall<1:raise RuntimeError('CUMULATIVE_BUDGET_EXHAUSTED')
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',MPLCONFIGDIR=str(R/'mplconfig'))
    def lim():
        inherited=resource.getrlimit(resource.RLIMIT_CPU)[1]
        cap=min(cpu,inherited) if inherited!=resource.RLIM_INFINITY else cpu
        resource.setrlimit(resource.RLIMIT_CPU,(cap,cap));resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824))
    st=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN);tout=False
    with (R/(a.name+'_stdout.log')).open('w') as out,(R/(a.name+'_stderr.log')).open('w') as err:
        try:rc=subprocess.run([sys.executable,str(BASE/'code'/a.script),*a.args],cwd=BASE,env=env,stdout=out,stderr=err,timeout=wall,preexec_fn=lim).returncode
        except subprocess.TimeoutExpired:tout=True;rc=124
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    item={'name':a.name,'command':[a.script,*a.args],'exit_code':rc,'timed_out':tout,'CPU_charge_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'wall_charge_s':time.monotonic()-st,'measurement_status':'MEASURED','maxrss_children_KiB':after.ru_maxrss,'CPU_cap_s':cpu,'wall_cap_s':wall,'requested_worker':'gpt-6.1-sol/high','observed_runtime_identity':'not exposed by tools'}
    state['invocations'].append(item);state['CPU_charge_s']=sum(x['CPU_charge_s'] for x in state['invocations']);state['wall_charge_s']=sum(x['wall_charge_s'] for x in state['invocations'])
    measured=[x for x in state['invocations'] if x.get('measurement_status')=='MEASURED'];state['measured_CPU_s']=sum(x['CPU_charge_s'] for x in measured);state['measured_wall_s']=sum(x['wall_charge_s'] for x in measured)
    rp.write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(item,indent=2));return rc
if __name__=='__main__':raise SystemExit(main())

