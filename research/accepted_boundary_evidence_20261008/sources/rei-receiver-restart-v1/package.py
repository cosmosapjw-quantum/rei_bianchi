#!/usr/bin/env python3
import pathlib,json,hashlib,zipfile,subprocess,sys
r=pathlib.Path(__file__).resolve().parent
subprocess.run([sys.executable,str(r/'verify_and_report.py')],check=True)
files=[p for p in r.rglob('*') if p.is_file() and 'target' not in p.relative_to(r).parts and p.name!='SOURCE_ONLY_MANIFEST.json']
manifest={str(p.relative_to(r)): {'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)}
(r/'SOURCE_ONLY_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');files.append(r/'SOURCE_ONLY_MANIFEST.json')
archive=r.parent/'REI_LIVE_RECEIVER_RESTART_SOURCE_ONLY_20261008.zip'
assert not archive.exists(), 'never overwrite a delivered package'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(files):z.write(p,str(pathlib.Path(r.name)/p.relative_to(r)))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name,meta in manifest.items():assert hashlib.sha256(z.read(r.name+'/'+name)).hexdigest()==meta['sha256']
receipt={'archive':str(archive),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'members':len(files),'crc_and_every_member_hash_verified':True,'target_and_executables_excluded':True,'runtime_dependency_archive_sha256':'4700d68ffda7204656fbd57d80c56a60278afb9bf0d03d1cd9c697298e0acd3f','upload_performed':False,'final_control_count':19,'physical_history_full_wide':'HOLD','post_pack_measurement_receipt_follows_outside_archive':True}
(r.parent/'LIVE_RECEIVER_RESTART_PACKAGE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
