"""Local sandbox execution: preflight success is a mandatory launch dependency.

The no-binding exception is local only; launch_ncp defaults remain core-bound.
No physics settings or memory thresholds are altered here.
"""
import argparse,json,os,signal,subprocess,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from mpi_batch import atomic_create,json_bytes
ap=argparse.ArgumentParser()
ap.add_argument('--manifest',required=True)
ap.add_argument('--output-dir',required=True)
ap.add_argument('--mpirun',required=True)
ap.add_argument('--ranks',required=True,type=int)
ap.add_argument('--wall-cap',required=True,type=int)
args=ap.parse_args()
out=ROOT/args.output_dir
preflight=out.with_name(out.name+'_PREFLIGHT.json')
receipt=out.with_name(out.name+'_LAUNCH.json')
log=out.with_name(out.name+'_LOG.txt')
if any(p.exists() for p in (out,preflight,receipt,log)):
    raise FileExistsError('create-only output required')
command=[sys.executable,str(ROOT/'code/launch_ncp.py'),'--manifest',args.manifest,
         '--output-dir',args.output_dir,'--backend','native','--ranks',str(args.ranks),
         '--threads','1','--mpirun',args.mpirun]
# A failing preflight raises here. No execution command is constructed on failure.
try:
    checked=subprocess.run(command,cwd=ROOT,check=True,capture_output=True,text=True)
except subprocess.CalledProcessError as error:
    atomic_create(receipt,json_bytes({'status':'PREFLIGHT_REJECTED_NOT_LAUNCHED',
        'preflight_returncode':error.returncode,'stdout':error.stdout,'stderr':error.stderr},
        ))
    raise
atomic_create(preflight,checked.stdout.encode())
record=json.loads(checked.stdout)
assert record['action']=='COMMAND_ONLY_NOT_EXECUTED'
launch=record['command_argv'];i=launch.index('--bind-to')
assert launch[i+1]=='core'
launch[i+1]='none'
start=time.perf_counter()
timed_out=False
with log.open('x') as stream:
    process=subprocess.Popen(launch,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,
                             start_new_session=True)
    try:
        returncode=process.wait(timeout=args.wall_cap)
    except subprocess.TimeoutExpired:
        timed_out=True
        try: os.killpg(process.pid,signal.SIGTERM)
        except ProcessLookupError: pass
        try: process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try: os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError: pass
            process.wait()
        returncode=124
atomic_create(receipt,json_bytes({'preflight_returncode':0,'command_argv':launch,
    'local_binding_exception':'none; observed sandbox hwloc restriction',
    'returncode':returncode,'timed_out':timed_out,'elapsed_seconds':time.perf_counter()-start,
    'wall_cap_seconds':args.wall_cap}))
raise SystemExit(returncode)
