from pathlib import Path
import tarfile,json,hashlib
w=Path('/root/HE23_NCP_DENSITY_20261016');results=[]
for provider,name in [('dropbox','DROPBOX_V2_READBACK.tar.gz'),('google_drive','DRIVE_V2_READBACK.tar.gz')]:
 p=w/name;digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest=='e65a431bfb304f842b05a23463e1680758ff7f24cac8dcc071a11007bd513596'
 dest=w/('RESTORED_'+provider);dest.mkdir(exist_ok=False)
 with tarfile.open(p) as t:t.extractall(dest,filter='data')
 root=dest/'compact_restoration';manifest=json.loads((root/'RESTORE.json').read_text())
 for row in manifest['contents']:assert hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256']
 package=dest/'package';source=dest/'owner_source';package.mkdir();source.mkdir()
 with tarfile.open(root/'HE23_COMMITTED_PACKAGE.tar.gz') as t:t.extractall(package,filter='data')
 with tarfile.open(root/'ORIGINAL_REI_SOURCE_f7830e2f.tar.gz') as t:t.extractall(source,filter='data')
 b=package/'research/he23_density_contract_20261016'
 records=json.loads((b/'SHA256_MANIFEST.json').read_text())
 for row in records:assert hashlib.sha256((b/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
 src=json.loads((b/'results/logs/owner_source_sha256.json').read_text())
 for row in src:assert hashlib.sha256((source/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
 with tarfile.open(b/'results/NATIVE_RAW_AND_FIRST_FAILURES.tar.gz') as t:
  members=t.getmembers();assert any(x.name=='refinement/FIRST_FAILURE_m4_n8.json' for x in members)
  # Decompress and read every member, rather than merely checking headers.
  for member in members:
   if member.isfile():assert len(t.extractfile(member).read())==member.size
 results.append({'provider':provider,'archive_sha256':digest,'archive_bytes':p.stat().st_size,'package_sha_files_checked':len(records),'original_owner_files_checked':len(src),'raw_archive_members_read':len(members),'status':'FULL_DOWNLOAD_EXTRACT_AND_HASH_VERIFIED'})
(w/'RESTORATION_VERIFICATION.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
