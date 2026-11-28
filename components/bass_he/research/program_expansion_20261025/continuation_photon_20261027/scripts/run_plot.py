"""One bounded plot process reading only saved validation data."""
import datetime,hashlib,json,os,pathlib,resource,signal,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1];out=ROOT/'evidence/plot';start=out/'START.json';finish=out/'FINISH.json';source=ROOT/'evidence/validation/SAVED_PLOT_DATA.json'
if not source.exists():raise RuntimeError('Measured saved data required')
out.mkdir(parents=True,exist_ok=True)
if start.exists():raise RuntimeError('Existing plot start; stop and diagnose')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,d):
 tmp=p.with_suffix('.tmp')
 with tmp.open('x') as f:json.dump(d,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 tmp.replace(p)
def limits():resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912));resource.setrlimit(resource.RLIMIT_CPU,(3,3))
command=[sys.executable,'-B',str(ROOT/'scripts/plot_saved.py')];save(start,{'status':'STARTED','time_utc':now(),'command':command,'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cpu_cap_s':4,'wall_cap_s':15,'memory_bytes':536870912,'threads':1,'scientific_function_calls':0})
env=os.environ.copy()
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[key]='1'
env['PYTHONDONTWRITEBYTECODE']='1';t=time.monotonic();cpu=time.process_time();ch=resource.getrusage(resource.RUSAGE_CHILDREN);timed=False;error=None;rc=None;stdout=stderr=b''
try:
 child=subprocess.Popen(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,preexec_fn=limits)
 try:stdout,stderr=child.communicate(timeout=10)
 except subprocess.TimeoutExpired:timed=True;os.killpg(child.pid,signal.SIGKILL);stdout,stderr=child.communicate()
 rc=child.returncode
except (OSError,subprocess.SubprocessError) as e:error=repr(e)
ch2=resource.getrusage(resource.RUSAGE_CHILDREN);child_cpu=ch2.ru_utime+ch2.ru_stime-ch.ru_utime-ch.ru_stime;parent_cpu=time.process_time()-cpu;wall=time.monotonic()-t;(out/'stdout.txt').write_bytes(stdout);(out/'stderr.txt').write_bytes(stderr);ok=rc==0 and not timed and not error and child_cpu+parent_cpu<=4 and wall<=15
save(finish,{'status':'PASS' if ok else 'FAIL','end_utc':now(),'returncode':rc,'timed_out':timed,'launch_error':error,'child_cpu_s':child_cpu,'runner_cpu_s':parent_cpu,'cumulative_cpu_s':child_cpu+parent_cpu,'wall_s':wall,'scientific_function_calls':0});raise SystemExit(0 if ok else 1)
