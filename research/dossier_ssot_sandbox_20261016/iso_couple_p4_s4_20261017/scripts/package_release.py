from pathlib import Path
import hashlib,zipfile,os
R=Path(__file__).resolve().parents[1]
name=R.name
archive=R.parent/(name+'_FULL.zip')
excluded={'target','__pycache__','reproduced','.git','scratch'}
files=sorted(p for p in R.rglob('*') if p.is_file() and not excluded.intersection(p.relative_to(R).parts) and p.name!='manifest.sha256')
manifest='\n'.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.relative_to(R).as_posix() for f in files)+'\n'
(R/'manifest.sha256').write_text(manifest)
files.append(R/'manifest.sha256')
files.sort()
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
    for f in files:
        rel=f.relative_to(R).as_posix()
        info=zipfile.ZipInfo(name+'/'+rel,date_time=(2026,10,17,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=(0o755 if os.access(f,os.X_OK) else 0o644)<<16
        z.writestr(info,f.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=8)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    lines=z.read(name+'/manifest.sha256').decode().splitlines()
    for line in lines:
        h,path=line.split('  ',1)
        assert hashlib.sha256(z.read(name+'/'+path)).hexdigest()==h,path
checksum=hashlib.sha256(archive.read_bytes()).hexdigest()
(Path(str(archive)+'.sha256')).write_text(f'{checksum}  {archive.name}\n')
print(f'ARCHIVE={archive} BYTES={archive.stat().st_size} SHA256={checksum} MEMBERS={len(files)} VERIFIED={len(lines)}')
