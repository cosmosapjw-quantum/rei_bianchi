"""Independent accepted-row gas energy ledger and cutoff comparison."""
import json,numpy as np,hashlib,sys
from pathlib import Path
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'r118c3g_spectral_cutoff'))
from spectral_coupling import H,P,G,abundance_from_clock
from inventory import cv,binding
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 r=np.genfromtxt(H,names=True,delimiter=',');st=np.genfromtxt(P,names=True,delimiter=',');Y=abundance_from_clock(r)
 f=np.stack([r[k] for k in ['xHII','xHeII','xHeIII']],axis=1);c=cv(f,Y);B=binding(f,Y);w0=c[0]*r['T'][0]
 results={}
 for label in ['funded4096','funded8192','calibrated4096','calibrated8192']:
  data=json.loads((D/(label+'.json')).read_text());v=np.load(D/(label+'.npz'));a,T,w,b,Q,C,F,Wg,Wr,res=v['rows'].T
  assert np.array_equal(a,r['a'][1:]) and np.max(abs(w-c[1:]*T))<1e-14 and np.max(abs(b-B[1:]))<1e-14
  wprev=np.r_[w0,w[:-1]];bprev=B[:-1];expectedwork=wprev*(1-(r['a'][:-1]/a)**2)
  gas=w-wprev+b-bprev+expectedwork-Q+C+F
  U=st['BB1'][-1]*15/np.pi**4*(v['x']@v['delta'])
  total=w[-1]-w0+b[-1]-B[0]+U+Wg.sum()+Wr.sum()-Q.sum()
  assert np.max(abs(gas))<1e-14 and np.max(abs(expectedwork-Wg))<1e-14 and abs(total)<1e-12
  assert abs(total-data['total_residual'])<1e-15
  for p in (H,P,G):assert data['source_hashes'][str(p)]==sha(p)
  results[label]=dict(max_gas=float(np.max(abs(gas))),global_total=float(total),work_mismatch=float(np.max(abs(expectedwork-Wg))))
 full=np.load(D/'nested_full.npz')['edges'];cut=[]
 for label in ['nested_full','nested_cut6','nested_cut3']:
  v=np.load(D/(label+'.npz'));data=json.loads((D/(label+'.json')).read_text());e=v['edges'];assert np.array_equal(e,full[-len(e):])
  cut.append(dict(xmin=float(e[0]),n=len(e)-1,ff_number=data['ff_number'],ff_energy=data['freefree'],compton=data['compton']))
 slope=np.diff([a['ff_number'] for a in cut])/np.diff(np.log([a['xmin'] for a in cut]))
 # The earlier FF table computed Z2 fraction with approximate Y; quantify discrepancy, no redefinition of locked table.
 mid=(f[:-1]+f[1:])/2;phys=4*Y*mid[:,2]/(mid[:,0]+Y*mid[:,1]+4*Y*mid[:,2])
 d=dict(results=results,cutoffs=cut,number_slope_per_log=slope.tolist(),ff_Z2_fraction_max_abs_discrepancy=float(np.max(abs(phys-st['z2frac']))),scope='actual pinned stage inputs, arithmetic audit; earlier approximate helium mixture in locked Gaunt table not silently replaced; not autonomous chemistry')
 (D/'LEDGER_AUDIT.json').write_text(json.dumps(d,indent=2)+'\n');print(d)
if __name__=='__main__':main()
