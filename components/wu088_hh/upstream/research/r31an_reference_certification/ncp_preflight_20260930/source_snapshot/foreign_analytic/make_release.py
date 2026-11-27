"""Create-only release of this evidence delta; does not run scientific kernels."""
from pathlib import Path
import hashlib,json,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 decision=json.loads((HERE/'review/FINAL_DECISION.json').read_text())
 freeze=json.loads((HERE/'CANDIDATE_FREEZE.json').read_text())
 for name,digest in freeze['sha256'].items():
  if sha((HERE/name).read_bytes())!=digest:raise RuntimeError('frozen evidence changed: '+name)
 dest=ROOT/'delivery/WU088_HH_R10_EVEN_ODD_FOREIGN_20260923_v1.zip'
 if dest.exists():raise FileExistsError(dest)
 excluded={'CHECKPOINT_MANIFEST.json','RELEASE_MANIFEST.json'}
 files=[p for p in sorted(HERE.rglob('*'))if p.is_file()and '__pycache__'not in p.parts and p.name not in excluded and not p.name.endswith(('.tmp','.lock'))]
 blobs={str(p.relative_to(ROOT)):p.read_bytes()for p in files}
 manifest={'schema':1,'kind':'FOREIGN_EVEN_ODD_DELTA','parent_identity':'foreign_analytic/PARENT_RELEASES.json','review_decision_file':'foreign_analytic/review/FINAL_DECISION.json','review_decision_sha256':sha((HERE/'review/FINAL_DECISION.json').read_bytes()),'scope':'Scoped component evidence. FullH and physical production remain HOLD.','files':[{'path':name,'bytes':len(data),'sha256':sha(data)}for name,data in blobs.items()]}
 mf=HERE/'RELEASE_MANIFEST.json';mf.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
 blobs[str(mf.relative_to(ROOT))]=mf.read_bytes()
 dest.parent.mkdir(exist_ok=True)
 with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=5)as z:
  for name,data in blobs.items():z.writestr(name,data)
 with zipfile.ZipFile(dest)as z:
  if z.testzip()is not None:raise RuntimeError('zip CRC failure')
  if set(z.namelist())!=set(blobs):raise RuntimeError('archive path mismatch')
  for name,data in blobs.items():
   if sha(z.read(name))!=sha(data):raise RuntimeError('archive bytes mismatch: '+name)
 receipt={'path':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest.read_bytes()),'file_count':len(blobs),'zip_crc_PASS':True,'all_archived_sha256_PASS':True,'frozen_candidate_and_author_results_unchanged':True,'remote_restore_performed':False}
 (ROOT/'delivery/foreign_release_local_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
