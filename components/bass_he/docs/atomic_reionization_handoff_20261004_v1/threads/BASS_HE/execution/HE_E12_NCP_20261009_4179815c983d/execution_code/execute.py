import os,pathlib,json,subprocess,time,uuid,datetime
R=pathlib.Path(__file__).parent
def write(name,obj):
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True);t=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
 with t.open('x') as f:json.dump(obj,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(t,p)
def run(tag,cmd,cwd=None):
 d=R/'logs'/tag;d.mkdir(parents=True,exist_ok=False);start=time.monotonic();env=os.environ.copy()
 env['PATH']='/root/BASS_HE_runtime/toolchain/cargo-1.94.1-x86_64-unknown-linux-gnu/cargo/bin:/root/WU088_HH_ON02_20261005/toolchain/prefix/bin:'+env['PATH']
 env['RUST_PREFIX']='/root/WU088_HH_ON02_20261005/toolchain/prefix';env['CARGO_HOME']=str(R/'cargo_home');env.pop('CARGO_TARGET_DIR',None)
 with (d/'stdout').open('xb') as out,(d/'stderr').open('xb') as err:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=out,stderr=err);write('logs/'+tag+'/PROCESS.json',{'pid':p.pid,'command':cmd,'cwd':str(cwd),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});code=p.wait();out.flush();os.fsync(out.fileno());err.flush();os.fsync(err.fileno())
 rec={'tag':tag,'command':cmd,'cwd':str(cwd),'exit':code,'elapsed_s':time.monotonic()-start};write('logs/'+tag+'/EXIT.json',rec)
 with (R/'EXECUTION_LEDGER.jsonl').open('a') as f:f.write(json.dumps(rec)+'\n');f.flush();os.fsync(f.fileno())
 print(json.dumps(rec),flush=True);return code
if __name__=='__main__':
 import sys
 sys.exit(run(sys.argv[1],sys.argv[3:],sys.argv[2]))
