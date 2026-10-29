from pathlib import Path
import hashlib,json,zipfile
UNIT=Path(__file__).resolve().parents[1]
WORKTREE=UNIT.parents[1]
STAGEDIR=UNIT/'delivery/stage_capsules';STAGEDIR.mkdir(parents=True,exist_ok=True)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def writezip(path,files):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for name,src in sorted(files.items()):
            zi=zipfile.ZipInfo(name,date_time=(2026,10,29,0,0,0))
            zi.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(zi,src.read_bytes())
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert all(z.read(n)==files[n].read_bytes() for n in files)

ledger=json.loads((UNIT/'STAGE_LEDGER.json').read_text())
receipts=[]
for stage in ledger['stages']:
    code=stage['stage'];p=UNIT/stage['file'];rec=json.loads(p.read_text());e=UNIT/rec['evidence_file']
    files={'stage.json':p,'evidence/'+e.name:e,'SOURCE_RECONCILIATION.json':UNIT/'SOURCE_RECONCILIATION.json','CONTRACT.json':UNIT/'CONTRACT.json'}
    dest=STAGEDIR/f'REI_SAVED17_STAGE_{code}_20261029.zip'
    writezip(dest,files)
    receipts.append({'stage':code,'name':dest.name,'bytes':dest.stat().st_size,'sha256':sha(dest),'members':len(files),'CRC':'PASS'})
manifest={'schema':'REI_SAVED17_20_STAGE_ARCHIVE_MANIFEST_V1','snapshot_semantics':'CLOSEOUT_RECONSTRUCTED','stages':receipts,'total':20,'independent_cloud_stage_uploads':False}
(UNIT/'delivery/STAGE_ARCHIVE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
files={}
for p in UNIT.rglob('*'):
    if not p.is_file() or p.suffix=='.pyc' or p.name in ('source17_cpp_reference','PACKAGE_RECEIPT.txt') or '__pycache__' in p.parts:continue
    files[str(p.relative_to(WORKTREE))]=p
for p in (WORKTREE/'research/rei_uvb_six_moment_response_20261029').rglob('*'):
    if p.is_file():files[str(p.relative_to(WORKTREE))]=p
out=Path('/mnt/data/REI_SAVED17_UVB_SOURCE_TANGENT_20261029_FULL.zip')
writezip(out,files)
with zipfile.ZipFile(out) as z:
    for x in receipts:
        n=f'research/rei_uvb_saved_state_source_tangent_20261029/delivery/stage_capsules/{x["name"]}'
        assert hashlib.sha256(z.read(n)).hexdigest()==x['sha256']
print(json.dumps({'master':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'members':len(files),'stage_capsules':len(receipts),'CRC':'PASS'},indent=2))
