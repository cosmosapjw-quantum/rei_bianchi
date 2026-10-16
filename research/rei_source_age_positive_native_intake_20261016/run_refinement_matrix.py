"""Bounded serial matrix. Completed exact inputs are reused; raw never overwritten."""
import argparse,json,os,signal,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('binary',type=Path);p.add_argument('out',type=Path);p.add_argument('--cases',default='age16,age32,angular16,transport32,source16,angular32,transport64');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);here=Path(__file__).resolve().parent
configs=dict(age8=[0,8,8,8,16],age16=[0,16,8,8,16],age32=[0,32,8,8,16],qplus_base=[.1,8,8,8,16],angular16=[.1,8,16,8,16],angular32=[.1,8,32,8,16],transport32=[.1,8,8,8,32],transport64=[.1,8,8,8,64],source16=[.1,8,8,16,16])
start=time.monotonic();record=[]
def run(command,name,cap):
 if time.monotonic()-start>1800:raise RuntimeError('30min matrix cap')
 with (a.out/(name+'.stdout')).open('w')as stdout,(a.out/(name+'.stderr')).open('w')as stderr:
  before=time.monotonic();child=subprocess.Popen(command,stdout=stdout,stderr=stderr,start_new_session=True)
  try:code=child.wait(timeout=min(cap,1800-(time.monotonic()-start)))
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGTERM);child.wait(timeout=20);code=124
 record.append(dict(name=name,command=command,exit_code=code,wall_s=time.monotonic()-before))
 (a.out/'MATRIX_EXECUTION.json').write_text(json.dumps(record,indent=2)+'\n')
 if code:raise RuntimeError(f'{name} exit {code}; raw retained')
for name in a.cases.split(','):
 q,births,mu,source,cells=configs[name];dest=a.out/name
 if (dest/'solver_return.json').exists():
  prior=json.loads((dest/'solver_return.json').read_text());assert prior['status']=='SCOPED_NUMERICAL_EXECUTION_COMPLETE'
  setup=json.loads((dest/'setup.json').read_text());assert [setup.get('birth_count',8),setup.get('n_mu',8),setup.get('source_subdivisions',8),setup.get('transport_cells',16)]==[births,mu,source,cells]
  record.append(dict(name=name,status='EXACT_COMPLETED_INPUT_REUSED'))
 else:
  command=['/usr/bin/time','-v','-o',str(a.out/(name+'.time')),'python3',str(here/'positive_solver.py'),str(a.binary),str(dest),'--q',str(q),'--birth-panels',str(births),'--n-mu',str(mu),'--source-subdivisions',str(source),'--transport-cells',str(cells)]
  run(command,name,600)
 native=a.out/(name+'_native')
 if not(native/'endpoint.json').exists():run(['/usr/bin/time','-v','-o',str(a.out/(name+'_native.time')),str(a.binary),'matrix_native',str(q),str(native),str(births),str(mu),str(source),str(cells)],name+'_native',300)
 mesh=(native/'common_mesh_ln_a.json').read_bytes();known=a.out/'FROZEN_COMMON_MESH_LN_A.json'
 if known.exists():assert known.read_bytes()==mesh,'matrix chemistry mesh differs'
 else:known.write_bytes(mesh)
(a.out/'MATRIX_EXECUTION.json').write_text(json.dumps(record,indent=2)+'\n')
