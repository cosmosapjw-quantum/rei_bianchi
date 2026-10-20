"""Retrieve only observed original-author URLs; preserve raw bytes and metadata."""
from pathlib import Path
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import datetime

OUT = Path(__file__).resolve().parent / 'data'
URLS = {
    'photo.dat': 'https://www.pa.uky.edu/~verner/dima/photo//photo.dat',
    'photo.txt': 'https://www.pa.uky.edu/~verner/dima/photo//photo.txt',
    'phfit2.f': 'https://www.pa.uky.edu/~verner/dima/photo//phfit2.f',
    'cfit.dat': 'https://www.pa.uky.edu/~verner/dima/col//cfit.dat',
    'cfit.txt': 'https://www.pa.uky.edu/~verner/dima/col//cfit.txt',
    'cfit.f': 'https://www.pa.uky.edu/~verner/dima/col//cfit.f',
    'rec_table.txt': 'https://www.pa.uky.edu/~verner/dima/rec//table.txt',
    'rec_table1.dat': 'https://www.pa.uky.edu/~verner/dima/rec//table1.dat',
    'author_info.html': 'https://www.pa.uky.edu/~verner/info.html',
}

def fetch(item):
    name, url = item
    try:
        with urlopen(url, timeout=25) as response:
            data = response.read()
            headers = dict(response.headers)
        (OUT / name).write_bytes(data)
        row = dict(path=name, url=url, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                   retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   http_headers=headers, status='RAW_BYTES_DOWNLOADED')
    except Exception as exc:
        row = dict(path=name, url=url, status='DOWNLOAD_FAILED', error=f'{type(exc).__name__}: {exc}')
    print({k:v for k,v in row.items() if k in ('path','bytes','sha256','status','error')}, flush=True)
    return row

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    old = OUT / 'PROVENANCE.json'
    if old.exists():
        (OUT / 'PROVENANCE_PREVIOUS_ATTEMPT.json').write_bytes(old.read_bytes())
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(fetch, URLS.items()))
    old.write_text(json.dumps(rows, indent=2) + '\n')
    if any(row['status'] != 'RAW_BYTES_DOWNLOADED' for row in rows):
        raise SystemExit(1)
