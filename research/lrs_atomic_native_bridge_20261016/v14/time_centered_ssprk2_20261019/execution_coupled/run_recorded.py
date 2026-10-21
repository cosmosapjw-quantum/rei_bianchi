#!/usr/bin/env python3
from pathlib import Path
import os,sys,json,time,subprocess,hashlib
w=Path('/workspace/scratch/6af5e9e6c737/v15_work');out=w/'execution_coupled';env=os.environ.copy();env['PATH']=str(w/'toolchain/bin')+':'+env['PATH'];env['CARGO_HOME']=str(w/'cargo_home');env['CARGO_BUILD_JOBS']='2';env['OMP_NUM_THREADS']='2';env['RAYON_NUM_THREADS']='2'
name=sys.argv[1];limit=int(sys.argv[2]);cmd=sys.argv[3:];start=time.monotonic()
(out/(name+'.command.json')).write_text(json.dumps({'cwd':str(w/'native_owner/rust/rei_microphysics'),'argv':cmd,'timeout_s':limit,'environment_overrides':{k:env[k] for k in ['CARGO_HOME','CARGO_BUILD_JOBS','OMP_NUM_THREADS','RAYON_NUM_THREADS']},'toolchain_bin':str(w/'toolchain/bin')},indent=2)+'\n')
with (out/(name+'.stdout')).open('w') as so,(out/(name+'.stderr')).open('w') as se:
 try:r=subprocess.run(cmd,cwd=w/'native_owner/rust/rei_microphysics',env=env,stdout=so,stderr=se,timeout=limit);code=r.returncode
 except subprocess.TimeoutExpired:code=124
elapsed=time.monotonic()-start;(out/(name+'.exit')).write_text(str(code)+'\n');(out/(name+'.timing.json')).write_text(json.dumps({'elapsed_s':elapsed,'exit':code},indent=2)+'\n')
print(name,'exit',code,'elapsed_s',elapsed);print((out/(name+'.stdout')).read_text()[-5000:]);print((out/(name+'.stderr')).read_text()[-5000:]);sys.exit(code)
