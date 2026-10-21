"""Only reviewer-found plotting status/hash risk; no IVP or original gate replay."""
import sys,time,tempfile,json
from pathlib import Path
sys.dont_write_bytecode=True
begin=time.monotonic()
sys.path.insert(0,str(Path(__file__).resolve().parent))
import plot_extension as p
import numpy as np
checks={};root=p.u.ROOT
with tempfile.TemporaryDirectory(prefix='rei_plot_gate_') as temporary:
    p.u.ROOT=Path(temporary);c={'id':'synthetic','config':{'P_m_i':.0003}};folder=p.u.ROOT/'z2_extension/results/cases/synthetic';folder.mkdir(parents=True);raw=folder/'raw.npz';receipt=folder/'RESULT.json'
    checks['missing_receipt_masks']=p.verified_plot_path(c,2) is None
    np.savez(raw,x=np.array([]),raw_y=np.empty((40,0)))
    r={'id':c['id'],'config':c['config'],'status':'FAILED','raw_sha256':p.u.sha(raw)};receipt.write_text(json.dumps(r))
    checks['failed_partial_raw_masks']=p.read(c,2) is None
    r['status']='COMPLETED';receipt.write_text(json.dumps(r));checks['completed_hash_verified']=p.verified_plot_path(c,2)==raw
    try:p.read(c,2);checks['empty_completed_raw_rejected']=False
    except ValueError as e:checks['empty_completed_raw_rejected']='SHAPE_MISMATCH' in str(e)
    r['id']='wrong';receipt.write_text(json.dumps(r))
    try:p.verified_plot_path(c,2);checks['receipt_identity_rejected']=False
    except ValueError as e:checks['receipt_identity_rejected']='IDENTITY_MISMATCH' in str(e)
    r['id']=c['id'];receipt.write_text(json.dumps(r));raw.write_bytes(b'tampered')
    try:p.verified_plot_path(c,2);checks['tampered_raw_rejected']=False
    except ValueError as e:checks['tampered_raw_rejected']='HASH_MISMATCH' in str(e)
p.u.ROOT=root
result={'checks':checks,'pass':all(checks.values()),'elapsed_s':time.monotonic()-begin,'no_IVP_calls':True,'prior_mechanical_s':.205+.7569442020030692,'plot_source_sha256':p.u.sha(p.__file__),'finding':'plot reader formerly admitted existing failed/unverified raw'}
p.u.atomic_json(root/'components/PLOT_GATE_MECHANICAL.json',result)
print(json.dumps(result,indent=2));sys.exit(0 if result['pass'] else 1)
