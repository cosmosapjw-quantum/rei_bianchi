#!/usr/bin/env python3
"""Exactly the root-authorized finite 19-case matrix; final-source N4 reused."""
import hashlib,json,pathlib,time
from run_captured import ROOT,IMPL,capture
BINARY=IMPL/'target/release/rei-vigilode-radau-research'
EXPECTED='358d254f88d196cd1ada4f71283fa3a69a068bbbf25ae28980af287575106905'
if hashlib.sha256(BINARY.read_bytes()).hexdigest()!=EXPECTED:raise SystemExit('Final binary hash mismatch')
rows=[];blocked=set();total=0.;begin=time.monotonic()
for mode,methods in [('fixed',{'radau':[2,4,8,16],'ssprk':[8,16,32]}),('birth',{'radau':[4,8,16],'ssprk':[4,8,16]}),('disabled',{'radau':[4,8,16],'ssprk':[4,8,16]})]:
 for method,levels in methods.items():
  for n in levels:
   family=(mode,method)
   if family in blocked:rows.append({'mode':mode,'method':method,'N':n,'status':'NOT_RUN_FAMILY_BLOCKED'});continue
   if total>=180:rows.append({'mode':mode,'method':method,'N':n,'status':'NOT_RUN_TOTAL_BUDGET'});continue
   reused=mode=='fixed' and method=='radau' and n==4
   label='final_source_n4' if reused else f'matrix_{mode}_{method}_n{n}'
   out=IMPL/'receipts'/label;raw=out/'raw.json'
   if reused:code=0
   else:code=capture(label,[str(BINARY.relative_to(ROOT)),str(raw.relative_to(ROOT)),mode,method,str(n)],40)
   if raw.exists():data=json.loads(raw.read_text());wall=data['wall_s'];calls=data['native_rhs_attempts_including_fd_replay'];complete=data['completed'] and code==0
   else:wall=json.loads((out/'outcome.json').read_text())['wall_s'];calls=None;complete=False
   if not reused:total+=wall
   row={'mode':mode,'method':method,'N':n,'status':'COMPLETED' if complete else 'FAILED_OR_TRUNCATED','reused':reused,'receipt':str(out.relative_to(ROOT)),'native_rhs_attempts':calls,'native_wall_s':wall};rows.append(row)
   if not complete:blocked.add(family)
   payload={'schema':'v16-finite-authorized-matrix-v1','unique_cases_planned':19,'binary_sha256':EXPECTED,'incremental_native_wall_s':total,'elapsed_wall_s':time.monotonic()-begin,'completed':sum(x['status']=='COMPLETED' for x in rows),'failed_or_truncated':sum(x['status']=='FAILED_OR_TRUNCATED' for x in rows),'cases':rows}
   (IMPL/'receipts/MATRIX_RECEIPT.json').write_text(json.dumps(payload,indent=2)+'\n')
print(json.dumps(payload,indent=2))
