import hashlib, json, pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main(which):
    doc=json.loads((ROOT/('MANIFEST.json' if which=='manifest' else 'OUTPUT_SHA256.json')).read_text())
    for fn,expected in doc['sha256'].items():
        f=ROOT/fn
        if not f.is_file() or digest(f)!=expected:raise SystemExit('MISMATCH '+str(fn))
    print(which.upper(),len(doc['sha256']),'/',len(doc['sha256']),'PASS')
if __name__=='__main__':main(sys.argv[1])
