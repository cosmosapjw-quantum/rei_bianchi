#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--manifest',type=Path,required=True)
p.add_argument('--manifest-sha256',required=True)
p.add_argument('--archive',type=Path,required=True)
p.add_argument('--output-dir',type=Path,required=True)
p.add_argument('--hydrate',action='store_true')
a=p.parse_args()
assert a.hydrate and a.output_dir.name=='E13C9'
assert a.manifest.name=='BASS_HE_E13C9_TRANSFER_MANIFEST.json'
assert a.archive.name=='E13C9_COMPLETE.zip'
assert hashlib.sha256(a.manifest.read_bytes()).hexdigest()==a.manifest_sha256
assert a.archive.read_bytes()==b'E13C9 COMPLETE TINY WIRING FIXTURE ONLY\n'
a.output_dir.mkdir(parents=True,exist_ok=False)
package=a.output_dir/'package/BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1'
package.mkdir(parents=True,exist_ok=False)
r={'schema':'bass-he-e13c9-restore-receipt-v1','status':'PASS_COMPLETE_RESTORE',
'FIXTURE_ONLY':True,'scientific_kernel_calls':0,'MPI_invocations':0,
'NCP_execute_invocations':0,'prior_restore_helper_invocations':1,
'automatic_retries':0,'package_directory':str(package.resolve()),
'hydrated_E13C8':{'returncode':0,'FIXTURE_ONLY':'simulated child status; no real E13C8 helper invoked'},
'actual_fake_child_argv':{'manifest':str(a.manifest),'archive':str(a.archive),'output_dir':str(a.output_dir),'hydrate':a.hydrate}}
(a.output_dir/'RESTORE_RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
print('FIXTURE_FAKE_PREDECESSOR_CALLED_ONCE; ACTUAL_PINNED_PREDECESSOR_CALLS=0')
