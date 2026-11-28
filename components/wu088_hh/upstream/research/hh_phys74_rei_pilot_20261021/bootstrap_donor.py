"""Restore only the eight byte-pinned owner files, never execute a scientific job.

Prefer the full PHYS74 recovery (already contains donor/) or DONOR_SOURCE.zip.
Otherwise fetch public immutable raw GitHub paths, checking each SHA before publish.
"""
import argparse,hashlib,json,os,urllib.request,uuid,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--archive',type=Path);a=ap.parse_args(argv)
    lock=json.loads((HERE/'DONOR_LOCK.json').read_text());target=HERE/'donor'
    z=zipfile.ZipFile(a.archive) if a.archive else None
    try:
        for relative,want in lock['files'].items():
            p=target/relative
            if p.exists():
                if hashlib.sha256(p.read_bytes()).hexdigest()!=want:raise ValueError('existing donor mismatch: '+relative)
                continue
            if z is not None:data=z.read(relative)
            else:
                url=f"https://raw.githubusercontent.com/{lock['repo']}/{lock['commit']}/{relative}"
                with urllib.request.urlopen(url,timeout=30) as r:data=r.read()
            if hashlib.sha256(data).hexdigest()!=want:raise ValueError('donor byte identity failed: '+relative)
            p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_name('.'+p.name+'.'+uuid.uuid4().hex)
            try:
                with temp.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
                os.link(temp,p)
            finally:temp.unlink(missing_ok=True)
    finally:
        if z:z.close()
    print('DONOR_BYTES_VERIFIED: 8 immutable files; scientific runs 0')
if __name__=='__main__':main()
