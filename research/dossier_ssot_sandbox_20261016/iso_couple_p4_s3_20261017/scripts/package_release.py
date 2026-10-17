import hashlib,os,zipfile,pathlib,stat,sys
root=pathlib.Path(__file__).resolve().parents[1]; archive=pathlib.Path('/mnt/data/REI_ISO_COUPLE_P4_S3_20261017_FULL.zip')
root_prefix=root.name
eligible=[]
for f in root.rglob('*'):
    if not f.is_file():continue
    if any(p in ('target','__pycache__','reproduced') for p in f.relative_to(root).parts):continue
    if f.name=='manifest.sha256':continue
    eligible.append(f)
manifest=[]
for f in sorted(eligible):
    rel=f.relative_to(root).as_posix()
    manifest.append(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {rel}')
(root/'manifest.sha256').write_text('\n'.join(manifest)+'\n')
files=sorted(eligible+[root/'manifest.sha256'])
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8,allowZip64=True) as z:
    for f in files:
        rel=f.relative_to(root).as_posix()
        info=zipfile.ZipInfo(root_prefix+'/'+rel, date_time=(2026,10,17,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=(0o755 if os.access(f,os.X_OK) else 0o644)<<16
        z.writestr(info,f.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=8)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for line in z.read(root_prefix+'/manifest.sha256').decode().splitlines():
        digest,rel=line.split('  ',1)
        data=z.read(root_prefix+'/'+rel)
        assert hashlib.sha256(data).hexdigest()==digest,rel
p=pathlib.Path(str(archive)+'.sha256'); sha=hashlib.sha256(archive.read_bytes()).hexdigest();p.write_text(f'{sha}  {archive.name}\n')
print('ARCHIVE',archive,'BYTES',archive.stat().st_size,'SHA256',sha,'MEMBERS',len(files),'MEMBERS_HASHED',len(eligible))
