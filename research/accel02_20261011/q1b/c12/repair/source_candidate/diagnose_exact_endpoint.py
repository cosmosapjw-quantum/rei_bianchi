from pathlib import Path
import sys,json,hashlib,math
import numpy as np
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[5]
Q1B=REPO/'research/accel02_20261011/q1b'
ATT=Q1B/'c12/evidence/C2_FULL001/RUN/ATTEMPTS/attempt-00000042'
request=json.loads((ATT/'MAP_01_REQUEST.json').read_text())
for key,expected in request['dependency_closure'].items():
    p=REPO/key.removeprefix('dependency:')
    assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,key
for p in (Q1B,Q1B.parent/'n1',Q1B/'c11/precision'):sys.path.insert(0,str(p))
from provider import HistoryProvider
from source_cells import CellSource
from grid_cells import load_grid
from source_precision import StableCellSource,log_ray,_log_ratio
provider=HistoryProvider(r=0.)
original=CellSource(provider,load_grid(Q1B/'GRID_C2.json'))
source=StableCellSource(original)
t=request['t1_s'];v=source.source(t)
n,q=v['N'],v['Q_eV']
fail=np.argwhere((q<source.edges[:-1]*n)|(q>source.edges[1:]*n))
lr=log_ray(provider.background,t)
rows=[]
for k,j in fail:
    a,b=source.edges[j:j+2]
    lower=max(0.,_log_ratio(10.,a)-lr);upper=min(source.cell_width[j],_log_ratio(50000.,a)-lr)
    rows.append(dict(angle=int(k),cell=int(j),a=float(a),b=float(b),N=float(n[k,j]),Q=float(q[k,j]),
        aN=float(a*n[k,j]),bN=float(b*n[k,j]),mean=float(q[k,j]/n[k,j]),D=float(v['D_eV'][k,j]),
        lower=lower,upper=upper,logray=lr,mean_minus_a=float(q[k,j]/n[k,j]-a),
        Qminus_aN=float(q[k,j]-a*n[k,j]),Qminus_bN=float(q[k,j]-b*n[k,j]),
        physical_a=math.exp(lr)*a,physical_b=math.exp(lr)*b))
result=dict(t0_s=request['t0_s'],t1_s=t,verified_dependencies=len(request['dependency_closure']),
       fail_count=len(rows),failures=rows,native_calls=0,old_tests_run=0,
       source_kernel='immutable C11 StableCellSource',source_evaluations=1)
(HERE/'EXACT_ENDPOINT_DIAGNOSIS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
