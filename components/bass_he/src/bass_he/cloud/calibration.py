"""Explicit, hash-bound operator admission for measured worker counts."""
import hashlib
import json
from pathlib import Path


def _digest(body):
    return hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def make_worker_receipt(selected, binding_id, thread_policy, memory_receipt_sha256,
                        observations_sha256=None):
    if not isinstance(selected,int) or selected<1 or not memory_receipt_sha256:
        raise ValueError('invalid calibration selection')
    body={'schema':'bass_he.worker_admission.v1','selected':selected,
          'binding':binding_id,'thread_policy':thread_policy,
          'memory_receipt_sha256':memory_receipt_sha256,
          'observations_sha256':observations_sha256}
    return {**body,'sha256':_digest(body)}


def admit_calibrated_workers(requested, receipt, binding_id, thread_policy,
                             memory_receipt_sha256):
    body={k:v for k,v in receipt.items() if k!='sha256'}
    if receipt.get('sha256')!=_digest(body):raise ValueError('calibration receipt tampered')
    if body.get('schema')!='bass_he.worker_admission.v1' or body.get('binding')!=binding_id:
        raise ValueError('calibration binding mismatch')
    if body.get('thread_policy')!=thread_policy or body.get('memory_receipt_sha256')!=memory_receipt_sha256:
        raise ValueError('calibration environment/memory mismatch')
    if not isinstance(requested,int) or requested<1 or requested>body.get('selected',0):
        raise ValueError('worker count exceeds calibrated selection')
    return True


def verify_sweep_evidence(receipt_path,receipt):
    """Bind admission to the actual three-repeat PERF report beside the receipt."""
    path=Path(receipt_path).parent/'WORKER_SWEEP.json'
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=receipt.get('observations_sha256'):
        raise ValueError('worker sweep evidence changed or missing')
    sweep=json.loads(raw)
    if (sweep.get('binding')!=receipt.get('binding') or
        sweep.get('thread_policy')!=receipt.get('thread_policy') or
        sweep.get('memory_receipt_sha256')!=receipt.get('memory_receipt_sha256') or
        sweep.get('selected')!=receipt.get('selected') or
        sweep.get('namespace')!='PERF_NOT_SCIENCE'):
        raise ValueError('worker sweep binding mismatch')
    selected=sweep['selected']
    rows=[x for x in sweep.get('observations',()) if x.get('workers')==selected]
    if len(rows)!=3 or {x.get('repeat') for x in rows}!={0,1,2} or not all(x.get('valid') for x in rows):
        raise ValueError('selected worker count lacks three valid repeats')
    return True
