"""Run each delegated exact unit once with per-process and cumulative receipts."""
import os,sys,json,time,math,resource,signal,pathlib,hashlib

ROOT=pathlib.Path(__file__).resolve().parent
UNITS=['WU_CUBIC_RATIONAL_DOUBLE_ROOT_PREPROCESS_V1','CR_SAME_BIN_HL_CORRECTED_JOINT_FACET_V1']

def run_unit(name):
    unit=ROOT/name;total=0.;results=[];self_start=resource.getrusage(resource.RUSAGE_SELF);unit_start=time.monotonic()
    for mode,target in [('primary','PRIMARY.json'),('independent','REFERENCE.json')]:
        if (unit/target).exists() or (unit/(mode+'.resource.json')).exists():raise RuntimeError('create-only attempt already present')
        command=[sys.executable,str(unit/(mode+'.py')),'--input',str(unit/'INPUTS.json')]
        if mode=='independent':command+=['--primary',str(unit/'PRIMARY.json')]
        command+=['--output',str(unit/target)]
        remaining=10-total
        if remaining<=0:raise RuntimeError('no remaining science child CPU')
        started=time.monotonic();pid=os.fork()
        if pid==0:
            os.setsid();resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2));lim=max(1,math.ceil(remaining));resource.setrlimit(resource.RLIMIT_CPU,(lim,lim))
            for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
            for fd,label in [(1,'stdout'),(2,'stderr')]:
                f=os.open(str(unit/(mode+'.'+label+'.log')),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.dup2(f,fd);os.close(f)
            os.execv(sys.executable,command)
        timeout=False
        while True:
            done,status,usage=os.wait4(pid,os.WNOHANG)
            if done:break
            if time.monotonic()-started>20:
                os.killpg(pid,signal.SIGKILL);done,status,usage=os.wait4(pid,0);timeout=True;break
            time.sleep(.005)
        cpu=usage.ru_utime+usage.ru_stime;total+=cpu
        receipt={'command':command,'exit_status':os.waitstatus_to_exitcode(status),'wall_seconds':time.monotonic()-started,'cpu_user_seconds':usage.ru_utime,'cpu_system_seconds':usage.ru_stime,'cpu_seconds':cpu,'maxrss_KiB':usage.ru_maxrss,'cumulative_science_child_cpu_seconds':total,'allowance_cpu_seconds':10,'wall_limit_seconds':20,'address_space_limit_bytes':256*1024**2,'workers':1,'thread_env':1,'timeout':timeout,'pass':os.waitstatus_to_exitcode(status)==0 and not timeout and total<=10}
        (unit/(mode+'.resource.json')).write_text(json.dumps(receipt,indent=2)+'\n');results.append(receipt)
        if not receipt['pass']:break
    end=resource.getrusage(resource.RUSAGE_SELF)
    summary={'science_children_cpu_seconds':total,'runner_self_cpu_seconds':(end.ru_utime-self_start.ru_utime)+(end.ru_stime-self_start.ru_stime),'runner_wall_seconds':time.monotonic()-unit_start,'host_overhead':'UNKNOWN_NOT_MEASURED','historical_budget':'SEPARATE_NO_TRANSFER','attempts':len(results),'all_child_checks_pass':len(results)==2 and all(x['pass'] for x in results),'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in unit.glob('*.py')}}
    (unit/'RESOURCE_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(name,json.dumps(summary),flush=True)

if __name__=='__main__':
    for name in UNITS:run_unit(name)
