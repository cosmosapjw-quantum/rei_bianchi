"""Stable local gas energy increment derivative and source ledger tangent from actual native stage rate increments."""
from pathlib import Path
import numpy as np,json
D=Path(__file__).resolve().parent;ld=np.longdouble
j=json.loads((D/'STAGE_JACOBIAN.json').read_text());f=ld('.2454')/(4*(1-ld('.2454')));cov=np.array([ld('13.598434599702'),f*ld('24.587389011'),f*(ld('24.587389011')+ld('54.41776')),ld(1)],ld);rows=[]
for r in j['rows']:
 if r['status']!='COMPLETE':continue
 columns={}
 for l in (D/(r['tag']+'.log')).read_text().splitlines():
  if l.startswith('C4H_STAGE,col,'):
   a=l.split(',')
   if int(a[2])==r['stage'] and int(a[4])==1:columns[int(a[3])]=np.array(a[6:12],ld)
 assert len(columns)==4
 A=np.column_stack([columns[k] for k in range(4)]);J=np.eye(4,dtype=ld)-A[:4]
 # The local inverse may be close to identity; avoid subtracting identity for energy increments.
 X=np.array(r['inverse'],ld);stable=cov@A[:4]@X;subtractive=cov@(X-np.eye(4,dtype=ld));L=A[4:]@X;implied=stable+L[1]-L[0]
 resid=J@X-np.eye(4,dtype=ld);assert max(abs(resid).ravel())<1e-14
 row=dict(tag=r['tag'],stage=r['stage'],gas_increment_stable=stable.astype(float).tolist(),gas_increment_subtractive=subtractive.astype(float).tolist(),gas_increment_cancellation_gap=float(np.linalg.norm(stable-subtractive)),CMB_input=L[0].astype(float).tolist(),escape=L[1].astype(float).tolist(),net_absorbed_energy_implied=implied.astype(float).tolist(),inverse_abs_residual=float(max(abs(resid).ravel())),scope='fixed-prepared-input local gas chemical substage; implied net absorption is energy-balance diagnostic not separately measured photon-energy derivative')
 rows.append(row);print(row,flush=True)
(D/'STABLE_STAGE_ENERGY.json').write_text(json.dumps(dict(rows=rows,scope='actual native rate increment derivatives and inverse; (J^-1-I)=A J^-1 with A=dt Df; no derivative of geometry, prepared radiation, outer adaptive branch or whole work ledger'),indent=2)+'\n')

