"""Audit actual canonical cell weak moments and failed shifted/affine admission."""
import numpy as np,json
from pathlib import Path
from dg import centers
D=Path(__file__).resolve().parent
def run():
 a=json.loads((D/'ACTUAL_DG.json').read_text())['rows'];b=json.loads((D/'DIRECT_DG.json').read_text())['rows'];assert len(a)==len(b)==3
 out={}
 for v,w in zip(a,b):
  label=v['label'];assert label==w['label'] and w['status']=='SCOPED_LOCAL_STEP'
  z=np.load(D/(label+'_direct.npz'));r=np.load(D/(label+'_dg.npz'));d=r['d'];q=centers(z['edges'])
  N,V=z['increment_N'],z['increment_V'];U=(V+q*N)*d[:,None]
  nerr=float(abs(N.sum())/np.sum(abs(N)));uerr=float(abs(U.sum())/np.sum(abs(U)))
  assert max(nerr,uerr)<1e-12 and w['min_ratio_updated']>0
  # Validate physically tiny signed increment separate from rounded full state.
  fN,fV=z['fine_increment_N'],z['fine_increment_V'];errN=float(np.sum(abs(fN-N))/np.sum(abs(fN)));errV=float(np.sum(abs(fV-V))/np.sum(abs(fV)))
  assert abs(errN-w['quadrature_N'])<1e-10 and abs(errV-w['quadrature_V'])<1e-10
  out[label]=dict(N_closure=nerr,U_closure=uerr,dg_shift_N=v['N_roundtrip'],dg_shift_V=v['geometric_V_roundtrip'],bad_full_affine=v['bad_full_affine'],min_sampled_ratio=w['min_ratio_updated'],quadrature_N=errN,quadrature_V=errV,fullhalf_N=w['fullhalf_N'],fullhalf_V=w['fullhalf_V'])
 p=json.loads((D/'COLLECTIVE.json').read_text())['rows'];warnings=sum(q['warnings'] for v in p for a in [v['disp'],v['fixed_pole']] for q in a.values())
 z=dict(rows=out,collective_warnings=warnings,scope='direct canonical local weak collision with positive sampled analytic reference, no native live admission; exact affine full state fails in 512-bin tail, shifted overlap projection not uniformly convergent')
 (D/'AUDIT.json').write_text(json.dumps(z,indent=2)+'\n');print(z,flush=True)
if __name__=='__main__':run()
