import hashlib,json,pathlib,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
ARCHIVE=ROOT.parent/'REI_F4_LII_2E1_CAUSAL_REDSHIFT_20261030_FULL.zip'

def pack():
    # Exclude local test cache and execution output generated only during verification.
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='MANIFEST.json')
    info={str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
    (ROOT/'MANIFEST.json').write_text(json.dumps({'schema':'REI_F4_LII_2E1_CAUSAL_PACKAGE_MANIFEST_V1','files':info,'payload_count':len(info)},sort_keys=True,indent=2)+'\n')
    with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(files+[ROOT/'MANIFEST.json']):
            # Explicitly not editing bytes; unique names and header CRC verification.
            z.write(p,arcname=ROOT.name+'/'+str(p.relative_to(ROOT)))
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(files)+1
    print(json.dumps({'archive':str(ARCHIVE),'bytes':ARCHIVE.stat().st_size,
          'sha256':hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
          'payload_files':len(files),'zip_entries':len(files)+1},indent=2))
if __name__=='__main__':pack()
