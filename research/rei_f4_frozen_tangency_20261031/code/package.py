from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
def sha(b):return hashlib.sha256(b).hexdigest()
def files():return sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name not in ('MANIFEST.json','OUTPUT_SHA256.json') and p.name!='.DS_Store')
def run():
    outputs=sorted(OUT.glob('*'))
    (ROOT/'OUTPUT_SHA256.json').write_text(json.dumps(dict(schema='REI_F4_TANGENCY_OUTPUT_V1',sha256={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in outputs if p.is_file()}),indent=2,sort_keys=True)+'\n')
    (ROOT/'MANIFEST.json').write_text(json.dumps(dict(schema='REI_F4_TANGENCY_FULL_MANIFEST_V1',sha256={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in files()}),indent=2,sort_keys=True)+'\n')
    zippath=ROOT.parent/(ROOT.name+'_FULL.zip')
    with zipfile.ZipFile(zippath,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p in sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'):
            z.write(p, arcname=ROOT.name+'/'+p.relative_to(ROOT).as_posix())
    print('ZIP',zippath,zippath.stat().st_size,sha(zippath.read_bytes()),'N',len(zipfile.ZipFile(zippath).namelist()))
if __name__=='__main__':run()
