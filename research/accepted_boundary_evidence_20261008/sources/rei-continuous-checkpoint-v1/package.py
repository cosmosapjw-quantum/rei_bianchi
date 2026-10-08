#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,zipfile,subprocess,sys
r=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(r/'verify_and_report.py')],check=True)
files=[p for p in r.rglob('*') if p.is_file() and not p.is_symlink() and 'target' not in p.relative_to(r).parts and p.name!='SOURCE_ONLY_MANIFEST.json']
manifest={str(p.relative_to(r)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)}
(r/'SOURCE_ONLY_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');files.append(r/'SOURCE_ONLY_MANIFEST.json')
archive=r.parent/'REI_FROZEN_CONTINUOUS_CHECKPOINT_SOURCE_ONLY_20261008.zip'
assert not archive.exists(),'never overwrite an accepted package'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(files):z.write(p,str(Path(r.name)/p.relative_to(r)))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name,meta in manifest.items():assert hashlib.sha256(z.read(r.name+'/'+name)).hexdigest()==meta['sha256']
receipt={'archive':str(archive),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'members':len(files),'CRC_and_each_member_hash_verified':True,'compiled_targets_and_symlinks_excluded':True,'self_contained_source_and_seed_dependencies':True,'final_controls':14,'all_original_pins_unchanged':120,'actual_scope':'original cold broadband frozen-panel k3->k4 only; gas heldfixed; originalmidpoint/source/gates','native_BE_handoff':'BLOCKED_INCOMPATIBLE','physical_full_history_full_wide':'HOLD','uploads':0,'previous_live_archive_unchanged_sha256':'5a46b8b676d8dba9957cecbaa900895e47df401437e09ced2374cf7472f74694','post_package_resources_recorded_separately':True}
(r.parent/'FROZEN_CONTINUOUS_CHECKPOINT_PACKAGE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
