"""Registered physical-overlap continuation, no eigensolves or basis interpolation."""
import sys,json,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for sub in ('code','reference','math'):sys.path.insert(0,str(ROOT/sub))
from state_io import load_pair
from continuation import pair_overlap,refinement_audit
from mpi_batch import atomic_create,json_bytes

def main():
 c=json.loads((ROOT/'CONTRACT.json').read_text());rs=c['continuation_grid'];out=ROOT/'evidence/CONTINUATION';out.mkdir(exist_ok=False);states={};inputs={};phases=[1,1];rows=[];start=time.monotonic()
 for R in rs:
  p=ROOT/'evidence/PROLATE_MPI'/(f'R{R:g}_base'.replace('.','p'))/'STATE.npz'
  meta=json.loads(p.with_name('RESULT.json').read_text());digest=hashlib.sha256(p.read_bytes()).hexdigest()
  if meta['status']!='PASS' or meta['parameters']['R']!=R or meta['state_file']!=p.name or meta['state_bytes']!=p.stat().st_size or meta['state_sha256']!=digest:raise ValueError('STATE_ARCHIVE_IDENTITY_MISMATCH')
  inputs[str(p.relative_to(ROOT))]=digest;states[R]=load_pair(p)
 for a,b in zip(rs,rs[1:]):
  for m in (0,1):
   if time.monotonic()-start>900:raise TimeoutError('bounded overlap audit wall cap900s')
   records={q:pair_overlap(states[a][m],states[b][m],q) for q in (24,32)}
   audit=refinement_audit(records[24],records[32])
   if not audit['transport_pass']:
    records[48]=pair_overlap(states[a][m],states[b][m],48);audit=refinement_audit(records[32],records[48])
   previous=phases[m]
   phase=previous*audit['phase_factor'] if previous is not None and audit['transport_pass'] else None
   phases[m]=phase
   last=records[max(records)]
   row={'R_left':a,'R_right':b,'m':m,'orders':records,'audit':audit,'transport_phase_left':previous,'transport_phase_right':phase,'transported_overlap':previous*phase*last['normalized_overlap'] if phase is not None else None,'phase_applied_to':'coefficient multiplier in transported-state representation; original archived coefficients immutable'}
   atomic_create(out/f'edge_{len(rows):02d}.json',json_bytes(row));rows.append(row)
   print(json.dumps({'R':b,'m':m,'order':max(records),'overlap':last['normalized_overlap'],'delta':audit['quadrature_increment_abs'],'pass':audit['transport_pass']}),flush=True)
 result={'status':'PASS_FIXED_M_CONTINUATION' if all(r['audit']['transport_pass'] for r in rows) else 'STATE_TRACKING_AMBIGUOUS','rows':rows,'state_sha256':inputs,'math_code_sha256':hashlib.sha256((ROOT/'math/continuation.py').read_bytes()).hexdigest(),'elapsed_seconds':time.monotonic()-start,'rank5_cluster':'NOT_VERIFIED','claim_scope':'common-O physical overlap between lowest fixed-m states; no eigenvalue-gap certification'}
 atomic_create(ROOT/'evidence/CONTINUATION_AUDIT.json',json_bytes(result))
if __name__=='__main__':main()
