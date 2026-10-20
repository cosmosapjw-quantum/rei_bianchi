"""Create-only command receipt for bounded native development; no IVP driver."""
import argparse, datetime, hashlib, json, os, pathlib, subprocess, time
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True)
p.add_argument('--cwd',type=pathlib.Path,required=True);p.add_argument('--timeout',type=float,default=60)
p.add_argument('argv',nargs=argparse.REMAINDER);a=p.parse_args()
argv=a.argv[1:] if a.argv[:1]==['--'] else a.argv
if not argv:raise SystemExit('command required')
a.output.mkdir(parents=True,exist_ok=False)
prefix=pathlib.Path('/tmp/rei_run19_runtime/prefix')
env=os.environ.copy();env['PATH']=str(prefix/'bin')+':'+env.get('PATH','')
env['LD_LIBRARY_PATH']=str(prefix/'lib');env['CARGO_HOME']='/tmp/rei_run19_runtime/cargo_home'
env['CARGO_NET_OFFLINE']='true';env['RUSTFLAGS']='';env.pop('CARGO_ENCODED_RUSTFLAGS',None)
env['RUSTC']=str(prefix/'bin/rustc');env['RUSTDOC']=str(prefix/'bin/rustdoc')
t=time.perf_counter();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
try:
    r=subprocess.run(argv,cwd=a.cwd,env=env,capture_output=True,timeout=a.timeout)
    code=r.returncode;stdout=r.stdout;stderr=r.stderr;timed_out=False
except subprocess.TimeoutExpired as e:
    code=None;stdout=e.stdout or b'';stderr=e.stderr or b'';timed_out=True
(a.output/'stdout.txt').write_bytes(stdout);(a.output/'stderr.txt').write_bytes(stderr)
receipt={'schema':'REI_RUN19_COMMAND_V1','utc':utc,'argv':argv,'cwd':str(a.cwd),
    'wall_seconds':time.perf_counter()-t,'exit_code':code,'timed_out':timed_out,
    'environment_overrides':{k:env[k] for k in ['LD_LIBRARY_PATH','CARGO_HOME','CARGO_NET_OFFLINE','RUSTFLAGS','RUSTC','RUSTDOC']},
    'logs':[{'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        for name,data in [('stdout.txt',stdout),('stderr.txt',stderr)]]}
(a.output/'COMMAND.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2));print(stdout.decode(errors='replace')[-10000:]);print(stderr.decode(errors='replace')[-5000:])
