import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import subprocess,json,numpy as np,hashlib
from retarded_integrator import ROOT,RetardedModel,GasServer,EV_J
m=RetardedModel();rows=[];inputs=[];expected=[]
with GasServer() as g:
 m.server=g
 for k,z in enumerate([.2,.55,.9,1.]):
  y=m.y0.copy();y[1:5]*=1+.03*k;y[10:13]*=1-.02*k;y[13]*=1+.01*k;y[27:m.p]=np.linspace(0,.8,m.m)
  active=int(np.searchsorted(m.birth,z,side='right'));q=m.raw_rhs(z,y,active)
  vals=np.r_[m.x0+m.dx*z,active,y[:14]*m.gscale[:14],y[27:m.p]]
  inputs.append('RHS '+' '.join(format(v,'.17e')for v in vals))
  expected.append(q)
p=subprocess.run([str(ROOT/'code/rei_bass_coupled/target/release/examples/retarded_joint_server')],input='\n'.join(inputs+['QUIT'])+'\n',capture_output=True,text=True,timeout=15,check=True)
lines=p.stdout.strip().splitlines();assert len(lines)==4,p.stdout[:500]
scale=np.r_[m.gscale,np.ones(m.m),np.full(4,m.nh),np.full(6,m.nh*EV_J)]
for k,(line,q) in enumerate(zip(lines,expected)):
 assert line.startswith('OK '),line
 raw=np.fromstring(line[3:],sep=' ');assert len(raw)==m.dim
 ref=raw*m.dx/scale
 # Norm is max componentwise discrepancy scaled by largest derivative in each
 # physical block, not an ill-conditioned relative ratio of near-zero components.
 blocks=[(0,13),(13,16),(16,26),(26,27),(27,m.p),(m.p,m.p+4),(m.p+4,m.p+8),(m.p+8,m.p+10)]
 errors=[float(max(abs(ref[a:b]-q[a:b]))/max(max(abs(ref[a:b])),1e-50)) for a,b in blocks]
 assert max(errors)<3e-11,errors
 rows.append({'state':k,'derivative_values':len(ref),'block_relative_max':errors,'max':max(errors)})
o={'scope':'full native retarded RHS vs separate Python vectorized photo+native gas, four positive states','m':m.m,'rows':rows,'maximum_block_scaled_error':max(x['max']for x in rows),'request_sha256':hashlib.sha256(('\n'.join(inputs)).encode()).hexdigest(),'native_stdout_sha256':hashlib.sha256(p.stdout.encode()).hexdigest()}
(ROOT/'evidence/NATIVE_PYTHON_PARITY.json').write_text(json.dumps(o,indent=2));print(json.dumps(o,indent=2))
