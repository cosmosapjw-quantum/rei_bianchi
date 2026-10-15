#!/usr/bin/env python3
"""Positive multi-opacity moment matching and independent gas-state holdout."""
import json,sys,time
from pathlib import Path
base=Path(__file__).resolve().parents[1]/'source07_c8_age_compression_20261015/experiment.py'
ns={'__file__':str(base),'__name__':'c8_math'}
exec(compile(base.read_text().split('\nresults=[]\n')[0],str(base),'exec'),ns)
import numpy as np
from scipy.optimize import linprog
model=ns['model'];vector=ns['vector'];nh=ns['nh'];nhe=ns['nhe']
ages=np.geomspace(model.ar,.2,36)
train=[(nh,nhe,0.),(.6*nh,1.3*nhe,0.),(1.4*nh,.7*nhe,0.)]
holdouts=[(.8*nh,1.1*nhe,0.),(1.2*nh,.9*nhe,0.),(.4*nh,1.5*nhe,0.)]
output=[]
for q in (-.01,0.,.01):
 start=time.perf_counter()
 tensors=np.array([[vector(a,q,g) for a in ages] for g in train+holdouts]) # gas, age, feature
 allA=tensors.transpose(0,2,1)
 initial=np.ones(36)/36
 designs={}
 for nstates in (1,3):
  # 1 norm row plus 5 observables per training gas, normalize by row maximum.
  raw=np.concatenate([np.ones((1,36))]+[allA[i] for i in range(nstates)],axis=0)
  norm=np.maximum(np.max(np.abs(raw),axis=1),1e-30)
  matrix=raw/norm[:,None];rhs=matrix@initial
  lp=linprog(np.linspace(0,1,36),A_eq=matrix,b_eq=rhs,bounds=(0,None),method='highs')
  assert lp.success,lp.message
  w=lp.x
  train_err=[float(np.max(np.abs(allA[i]@w-allA[i]@initial)/np.maximum(np.abs(allA[i]@initial),1e-30))) for i in range(nstates)]
  hold_err=[(np.abs(allA[j]@w-allA[j]@initial)/np.maximum(np.abs(allA[j]@initial),1e-30)).tolist() for j in range(3,6)]
  assert np.all(w>=-1e-12) and abs(w.sum()-1)<1e-9
  designs[str(nstates)]={'retained':int(np.sum(w>1e-9)),'train_error_max':max(train_err),'holdout_errors':hold_err,'weights':[(int(k),float(w[k])) for k in np.where(w>1e-9)[0]]}
 output.append({'q':q,'designs':designs,'seconds':time.perf_counter()-start})
 print(q,[(i,designs[i]['retained'],max(v[-1] for v in designs[i]['holdout_errors'])) for i in ('1','3')],flush=True)
Path(__file__).with_name('results.json').write_text(json.dumps(output,indent=2)+'\n')
