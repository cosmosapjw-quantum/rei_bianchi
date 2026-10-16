"""Materialize pinned native source and include_str inputs, without checkout edits."""
import hashlib,io,json,re,subprocess,sys,tarfile
from pathlib import Path
commit='35d9747a0bbedcafdb568467ce7c1e7a25f965b6'
repo=Path(sys.argv[1]).resolve();dest=Path(sys.argv[2]).resolve()
if dest.exists() and any(dest.iterdir()):raise SystemExit('destination must be empty')
dest.mkdir(parents=True,exist_ok=True)
raw=subprocess.check_output(['git','-C',str(repo),'archive',commit,'rust/rei_microphysics'])
with tarfile.open(fileobj=io.BytesIO(raw)) as archive:archive.extractall(dest,filter='data')
for src in (dest/'rust/rei_microphysics/src').glob('*.rs'):
    for name in re.findall(r'include_str!\(\s*"(\.\./[^"\n]+)"\s*\)',src.read_text()):
        path=(src.parent/name).resolve();rel=path.relative_to(dest).as_posix()
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(subprocess.check_output(['git','-C',str(repo),'show',f'{commit}:{rel}']))
rows=[]
for p in sorted(dest.rglob('*')):
    if p.is_file():rows.append(dict(path=p.relative_to(dest).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(dest/'NATIVE_SOURCE_IDENTITY.json').write_text(json.dumps(dict(commit=commit,files=rows),indent=2)+'\n')
print(json.dumps(dict(commit=commit,files=len(rows),destination=str(dest))))
