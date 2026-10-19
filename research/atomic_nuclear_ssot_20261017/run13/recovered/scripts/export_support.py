"""Export ONE native support; no atomic/source normalization is changed."""
from pathlib import Path
import sys,os,json,subprocess,hashlib,numpy as np
R=Path(__file__).resolve().parents[1]
def export_support(r:int):
 if not 1<=r<=8:raise ValueError('run09 campaign contract allows r=1..8')
 dest=R/'inputs'/'refined';dest.mkdir(exist_ok=True)
 out=dest/f'r{r}.json';bits=dest/f'r{r}.tuple.bin'
 env=os.environ.copy();env['RUN08_PACKET_BITS']=str(bits)
 cmd=[str(R/'code/rei_bass_coupled/target/release/examples/source_support_server'),'SIGNED_MINUS',str(r)]
 p=subprocess.run(cmd,input='INIT\nQUIT\n',text=True,capture_output=True,env=env,timeout=20)
 if p.returncode:raise RuntimeError(p.stderr)
 packet=json.loads(p.stdout);out.write_text(p.stdout)
 parent=json.loads((R/'inputs/FINITE_BIRTH_PACKET.json').read_text())
 for k in ['case','x0','x1','a0','t0_s','t1_s','tau_seed','state','chi_eV','columns']:assert packet[k]==parent[k],k
 a=np.asarray(packet['cohorts']);a0=np.asarray(parent['cohorts']);n=48*8
 assert len(a)==r*len(a0) and len(a)%n==0
 assert np.isfinite(a).all() and (a[:,6]>0).all()
 times=a[::n,1];assert np.all(np.diff(times)>0)
 assert np.all((times>packet['t0_s'])&(times<packet['t1_s']))
 # Do not match only totals: preserve every spectral/angular source label at every birth.
 for rows in a.reshape(-1,n,9):
  assert np.array_equal(rows[:,[4,5,7,8]],a0[:n,[4,5,7,8]])
  assert (rows[:,1]==rows[0,1]).all()
 if r==1:assert packet==parent,'r1 must exactly replay parent physical packet'
 vals=np.column_stack([a[:,1],a[:,4],a[:,5],a[:,6]*packet['a0']**3]).astype('<f8')
 # Native binary is authoritative; reconstruction through a^3 can round, so do not assert byte identity to it.
 raw=bits.read_bytes();assert len(raw)==32*len(a)
 rec={'subdivisions':r,'native_command':cmd,'status':'EXPORTED_NATIVE_VALIDATED','packet_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'tuple_sha256':hashlib.sha256(raw).hexdigest(),'tuple_bytes':len(raw),'physical_cohorts':len(a),'birth_times':len(times),'source_fields_preserved':True,'r1_exact_parent_object':r==1,'panels':packet['panels'],'tau_seed':packet['tau_seed'],'born_com3':float(a[:,6].sum()*packet['a0']**3),'max_birth_gap_s':float(np.diff(np.r_[packet['t0_s'],times,packet['t1_s']]).max()),'no_post_normalization':True}
 (dest/f'r{r}.identity.json').write_text(json.dumps(rec,indent=2)+'\n')
 print(json.dumps(rec,indent=2));return rec
if __name__=='__main__':export_support(int(sys.argv[1]))
