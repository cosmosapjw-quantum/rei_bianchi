import sys,json,subprocess,hashlib,os
from pathlib import Path
import numpy as np
sys.path.insert(0,'/root/BASS_HE_HE22_NATIVE_20261016/research/he22_casea_native_handoff_20261016/src')
from he22_coupled import run_coupled
from he21_photo import N_H_Z20,Y_HE
out=Path(__file__).parent
class StopFirstPoint(Exception):pass
def factory(a,x):
 def capture(g,gr,power):
  argv=['/root/HE22_NCP_20261016/build/he22_owner_point',*[format(float(v),'.17e') for v in (a,*g,*gr,*power)]]
  p=subprocess.run(argv,capture_output=True)
  (out/'native_stdout.bin').write_bytes(p.stdout);(out/'native_stderr.bin').write_bytes(p.stderr)
  fields={r.split('\t')[0]:r.split('\t')[1:] for r in p.stdout.decode().splitlines()[1:]}
  nh=float(fields['NH_CM3'][0]);nhe=float(fields['NHE_CM3'][0]);expected=N_H_Z20*np.exp(-3*x)
  record=dict(purpose='single first-point boundary diagnostic, not pilot retry or acceptance',argv=argv,returncode=p.returncode,a=a,x=x,expected_nh=float(expected),native_nh=nh,relative_nh_mismatch=nh/expected-1,expected_Y_HE=Y_HE,native_Y_HE=nhe/nh,density_tolerance=1e-9,raw_stdout_sha256=hashlib.sha256(p.stdout).hexdigest())
  tmp=out/'FIRST_POINT.json.partial'
  with tmp.open('w') as f:json.dump(record,f,indent=2);f.flush();os.fsync(f.fileno())
  tmp.replace(out/'FIRST_POINT.json')
  raise StopFirstPoint()
 return capture
try:run_coupled(factory,m=4,steps=2,q=0.)
except StopFirstPoint:pass
