"""Create a public text subset or a complete private research archive."""
import argparse,hashlib,io,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from validate_contract import atomic_create

def dump(path,obj):atomic_create(path,(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode())
def files():
    return [p for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pending')]
def public():
    namespace='research/shared_c64/20261002/C2E_DOMAIN_TARGET_v1'
    blocked={'provenance/USER_CONTRACT_ORIGINAL.txt','provenance/A2_ASYMPTOTIC_DERIVATION_KO.md','provenance/C2D_NEXT_HANDOFF_KO.md','provenance/PARENT_RESEARCH_DAG.json'}
    selected=[]
    for p in files():
        rel=str(p.relative_to(ROOT))
        if rel in blocked or (rel.startswith('source_notes/domain_inputs/') and p.name!='INPUT_MANIFEST.json'):continue
        if p.suffix not in ('.py','.json','.md','.txt','.csv'):continue
        if p.is_symlink():raise ValueError('symlink rejected')
        selected.append(p)
    elements=[];expected={}
    for p in selected:
        raw=p.read_bytes();path=namespace+'/'+str(p.relative_to(ROOT))
        elements.append({'path':path,'mode':'100644','type':'blob','content':raw.decode('utf-8')})
        expected[path]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'git_blob_sha':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()}
    payload=json.dumps(elements,ensure_ascii=True,separators=(',',':')).encode()
    atomic_create(ROOT.parent/'C2E_PUBLIC_TREE_PAYLOAD.json',payload)
    dump(ROOT/'provenance/PUBLIC_EXPECTED.json',expected)
    print(json.dumps({'files':len(elements),'payload_bytes':len(payload),'namespace':namespace}))
def archive():
    paths=files()
    if any(p.name=='MANIFEST.json' or p.is_symlink() for p in paths):raise ValueError('existing manifest or symlink')
    records={str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths}
    dump(ROOT/'MANIFEST.json',{'schema':1,'scope':'all archive payload except manifest','files':records});paths.append(ROOT/'MANIFEST.json')
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in paths:z.writestr(ROOT.name+'/'+str(p.relative_to(ROOT)),p.read_bytes())
    target=ROOT.with_suffix('.zip');atomic_create(target,buffer.getvalue())
    sha=hashlib.sha256(target.read_bytes()).hexdigest()
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None and len(z.namelist())==len(records)+1
        assert len(set(z.namelist()))==len(z.namelist())
        for name,v in records.items():
            raw=z.read(ROOT.name+'/'+name);assert len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['sha256']
    atomic_create(target.with_suffix('.zip.sha256'),(sha+'  '+target.name+'\n').encode())
    result={'archive_path':str(target),'bytes':target.stat().st_size,'sha256':sha,'crc':'PASS','all_manifest_payloads':'PASS','payload_count':len(records),'member_count':len(records)+1,'scope':'local artifact validation; no external restore claimed'}
    dump(ROOT.parent/'C2E_ARTIFACT_VALIDATION.json',result);print(json.dumps(result))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['public','archive']);a=p.parse_args()
    (public if a.mode=='public' else archive)()
