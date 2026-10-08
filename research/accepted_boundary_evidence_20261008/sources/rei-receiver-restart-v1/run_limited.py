#!/usr/bin/env python3
"""Bounded process-group runner. No external inputs are written."""
import argparse, json, os, pathlib, resource, signal, subprocess, time
p=argparse.ArgumentParser(); p.add_argument('name'); p.add_argument('--core',type=int,required=True); p.add_argument('--as-mib',type=int,required=True); p.add_argument('--cpu-slice',type=float,default=25); p.add_argument('--wall-slice',type=float,default=50); p.add_argument('command',nargs=argparse.REMAINDER); a=p.parse_args()
root=pathlib.Path(__file__).resolve().parent; receipt=root/'results'/f'{a.name}.json'
cmd=a.command; cmd=cmd[1:] if cmd and cmd[0]=='--' else cmd
def limits():
 os.setsid(); os.sched_setaffinity(0,{a.core}); resource.setrlimit(resource.RLIMIT_AS,(a.as_mib*1048576,)*2); resource.setrlimit(resource.RLIMIT_CPU,(120,120)); resource.setrlimit(resource.RLIMIT_FSIZE,(64*1048576,)*2)
prior=list((root/'results').glob('*.json')); cpu=wall=0.
for f in prior:
 try:
  j=json.loads(f.read_text()); cpu+=j.get('cpu_s',0.); wall+=j.get('wall_s',0.)
 except (ValueError,OSError): pass
if cpu>=160 or wall>=265: raise SystemExit('aggregate execution budget exhausted')
start=time.monotonic(); before=resource.getrusage(resource.RUSAGE_CHILDREN)
with (root/'logs'/f'{a.name}.stdout').open('w') as out, (root/'logs'/f'{a.name}.stderr').open('w') as err:
 child=subprocess.Popen(cmd,stdout=out,stderr=err,preexec_fn=limits,env={**os.environ,'CARGO_BUILD_JOBS':'1','CARGO_INCREMENTAL':'0','RUSTFLAGS':'-Ccodegen-units=1 -Cdebuginfo=0 -Cllvm-args=-threads=1','RAYON_NUM_THREADS':'1'})
 reason=None; peak_rss=0; peak_cpu=0.
 while child.poll() is None:
  rss=used=0.
  for d in pathlib.Path('/proc').iterdir():
   if not d.name.isdigit(): continue
   try:
    fields=(d/'stat').read_text().rsplit(')',1)[1].split()
    if int(fields[2])==child.pid:
     used+=(int(fields[11])+int(fields[12])+int(fields[13])+int(fields[14]))/os.sysconf('SC_CLK_TCK'); rss+=int(fields[21])*os.sysconf('SC_PAGE_SIZE')
   except (OSError,ValueError,IndexError): pass
  peak_rss=max(peak_rss,int(rss)); peak_cpu=max(peak_cpu,used)
  if cpu+used>=159.5 or used>=a.cpu_slice-.5 or wall+time.monotonic()-start>=264.5 or time.monotonic()-start>=a.wall_slice-.5:
   reason='aggregate watchdog'; os.killpg(child.pid,signal.SIGKILL); break
  if sum(f.stat().st_size for f in root.rglob('*') if f.is_file())>256*1048576:
   reason='disk watchdog'; os.killpg(child.pid,signal.SIGKILL); break
  time.sleep(.05)
 status=child.wait()
after=resource.getrusage(resource.RUSAGE_CHILDREN)
j={'command':cmd,'exit':status,'core':a.core,'as_limit_bytes':a.as_mib*1048576,'per_process_cpu_limit_s':120,'group_cpu_slice_s':a.cpu_slice,'group_wall_slice_s':a.wall_slice,'aggregate_cpu_watchdog_s':160,'aggregate_execution_wall_watchdog_s':265,'cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'wall_s':time.monotonic()-start,'maxrss_kib':after.ru_maxrss,'sampled_group_peak_rss_bytes':peak_rss,'sampled_group_peak_cpu_s':peak_cpu,'reason':reason}
receipt.write_text(json.dumps(j,indent=2)); print(json.dumps(j)); raise SystemExit(status if status>=0 else 1)
