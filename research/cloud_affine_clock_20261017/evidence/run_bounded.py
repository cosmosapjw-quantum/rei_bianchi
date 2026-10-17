import subprocess,time,resource,json,os,sys,pathlib,hashlib
root=pathlib.Path(__file__).resolve().parents[1]; ledger=root/'evidence/COMMAND_LEDGER.json'
a=json.loads(ledger.read_text()) if ledger.exists() else []
wall_left=300-sum(r['wall_seconds'] for r in a); cpu_left=600-sum(r['child_cpu_seconds'] for r in a)
if min(wall_left,cpu_left)<=0: raise SystemExit('BUDGET_EXHAUSTED')
env=os.environ.copy();env['PATH']=(env['RUST_TOOLCHAIN_BIN']+os.pathsep if env.get('RUST_TOOLCHAIN_BIN') else '')+env['PATH'];env['CARGO_BUILD_JOBS']='1';env['CARGO_INCREMENTAL']='0';env['CARGO_HOME']=str(root/'cargo_home');env['CARGO_TARGET_DIR']=str(root/'target')
cmd=sys.argv[2:]; label=sys.argv[1]; start=time.time(); before=resource.getrusage(resource.RUSAGE_CHILDREN); timeout=False
try:
 r=subprocess.run(cmd,cwd=root/'crate',env=env,capture_output=True,timeout=min(wall_left,120)); code=r.returncode; out=r.stdout;err=r.stderr
except subprocess.TimeoutExpired as e: code=124;out=e.stdout or b'';err=e.stderr or b'';timeout=True
after=resource.getrusage(resource.RUSAGE_CHILDREN); wall=time.time()-start;cpu=(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime)
(root/'evidence'/f'{label}.stdout').write_bytes(out);(root/'evidence'/f'{label}.stderr').write_bytes(err)
a.append(dict(label=label,command=cmd,start_unix=start,wall_seconds=wall,child_cpu_seconds=cpu,exit_code=code,timeout=timeout,stdout_sha256=hashlib.sha256(out).hexdigest(),stderr_sha256=hashlib.sha256(err).hexdigest()))
ledger.write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a[-1]));print(out.decode()[-4000:]);print(err.decode()[-2500:]);sys.exit(code)
