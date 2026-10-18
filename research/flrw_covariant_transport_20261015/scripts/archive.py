#!/usr/bin/env python3
"""Archive the immutable first pilot and produce a compact terminal extraction.
No upload, Library operation, git action, numerical execution or source edit.
"""
import argparse,csv,hashlib,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
TASK=ROOT/'research/flrw_covariant_transport_20261015'
RAW=TASK/'raw'
NAME='REI_COVARIANT_PILOT_20261015_ATTEMPT1.zip'
def digest(data):return hashlib.sha256(data).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def main(output):
 if output.exists():raise RuntimeError('Archive already exists; verify/reuse it instead of overwriting.')
 run=RAW/'q128_attempt1';receipt=RAW/'q128_attempt1_receipt.json';diag=RAW/'q128_step_diagnostic_001'
 result=json.loads(receipt.read_text())
 if result.get('status')=='RUNNING' or not (run/'RETURN.txt').exists():raise RuntimeError('Terminal first pilot required')
 compact=RAW/'q128_attempt1_terminal_compact'
 if compact.exists():raise RuntimeError('Compact extraction exists; verify/reuse it instead of overwriting.')
 compact.mkdir()
 copies=['checkpoint.txt','RETURN.txt','source_identity.txt','config.cfg','metadata.txt','case_id.txt','feedback_summary.txt']
 for name in copies:shutil.copy2(run/name,compact/name)
 shutil.copy2(receipt,compact/'execution_receipt.json')
 for name in ['q128_attempt1.log','q128_step_diagnostic_001.log','q128_step_diagnostic_001.receipt.json']:
  shutil.copy2(RAW/name,compact/name)
 shutil.copytree(diag,compact/'diagnostic')
 # Terminal rows are explicit extracts, never replacements for full raw CSVs.
 last_ledger={}
 with (run/'ledgers.csv').open() as stream:
  for row in csv.DictReader(stream):last_ledger[row['ledger_name']]=row
 dump(compact/'final_ledgers.json',last_ledger)
 with (run/'history.csv').open() as stream:
  final=None
  for row in csv.DictReader(stream):final=row
 dump(compact/'endpoint_history.json',final)
 selection={'schema':'rei.covariant.terminal_extraction.v1','full_raw_retained':True,'full_raw_path':str(run.relative_to(ROOT)),'direct_terminal_copies':copies,'derived_terminal_extracts':{'final_ledgers.json':'last row per ledger_name from original ledgers.csv','endpoint_history.json':'last row from original history.csv'},'full_csvs_not_in_compact':['abundances.csv','history.csv','ledgers.csv','spectra.csv','feedback.csv'],'reason':'Full raw stays immutable and is included in external archive; compact preserves terminal checkpoint, identity, config, receipt and final metrics for git review.'}
 dump(compact/'EXTRACTION.json',selection)
 chosen=[]
 for folder in [run,diag,compact]:chosen.extend(f for f in folder.rglob('*') if f.is_file())
 for name in ['q128_attempt1_receipt.json','q128_attempt1.log','q128_step_diagnostic_001.log','q128_step_diagnostic_001.receipt.json','build_attempt1.json','build_attempt1.log']:
  chosen.append(RAW/name)
 for name in ['NATIVE_CONTRACT.md','PILOT_FIRST_FAILURE.md','PILOT_STATUS.json','PILOT_COMPARISON.json','PILOT_TIME_ERROR_DIAGNOSIS.json','PILOT_TIME_ERROR_DIAGNOSIS.md']:
  chosen.append(TASK/name)
 chosen.extend([TASK/'configs/pilot_z20_19p8_q128.cfg',Path(__file__).resolve(),TASK/'scripts/pilot.py'])
 chosen=sorted(set(chosen),key=lambda f:str(f.relative_to(ROOT)))
 entries={str(f.relative_to(ROOT)):f.read_bytes() for f in chosen}
 # Reconstruct the exact original compiled source dependency payload rather
 # than substituting a later on-disk driver/diagnostic edit.
 source=(run/'source_identity.txt').read_text();parts=source.split('\nAXBI_SOURCE_BOUNDARY\n')
 bound=result['source_inputs_sha256']
 if len(parts)!=len(bound):raise RuntimeError('Compiled identity dependency shape mismatch')
 for (path,expected),text in zip(bound.items(),parts):
  data=text.encode()
  if digest(data)!=expected:raise RuntimeError(f'Original source chunk hash mismatch: {path}')
  entries['source_at_pilot/'+path]=data
 manifest={'schema':'rei.covariant.pilot_backup.v1','scope':'Full immutable q128 attempt1 and its bounded diagnosis, exact original source dependencies, terminal compact extraction; no build cache','raw_pilot_result':result['native_return']['result'],'entries':[{'path':name,'bytes':len(data),'sha256':digest(data)} for name,data in sorted(entries.items())]}
 manifest_bytes=(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n').encode();entries['ARCHIVE_MANIFEST.json']=manifest_bytes
 output.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
  for name,data in sorted(entries.items()):
   info=zipfile.ZipInfo(name,date_time=(2026,10,15,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
   z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
 with zipfile.ZipFile(output) as z:
  if z.testzip() is not None:raise RuntimeError('ZIP CRC failure')
  for name,data in entries.items():
   if digest(z.read(name))!=digest(data):raise RuntimeError(f'Archive readback mismatch: {name}')
 # Check all selected original files remained unchanged during assembly.
 for f in chosen:
  if f.read_bytes()!=entries[str(f.relative_to(ROOT))]:raise RuntimeError(f'Input changed during archive assembly: {f}')
 raw_bytes=sum(f.stat().st_size for f in run.rglob('*') if f.is_file())
 record={'schema':'rei.covariant.pilot_backup_receipt.v1','archive_path':str(output),'archive_bytes':output.stat().st_size,'archive_sha256':digest(output.read_bytes()),'archive_entries':len(entries),'uncompressed_payload_bytes':sum(map(len,entries.values())),'full_raw_pilot_bytes':raw_bytes,'compact_path':str(compact.relative_to(ROOT)),'compact_bytes':sum(f.stat().st_size for f in compact.rglob('*') if f.is_file()),'manifest_sha256':digest(manifest_bytes),'original_source_chunks_verified':len(bound),'zip_crc_and_member_sha_readback':'PASS','original_inputs_unchanged':'PASS','uploads':0,'git_mutations':0,'library_operations':0,'repeatability':'Sorted members, fixed timestamp/mode, explicit compression level and exact input hashes; no cache included'}
 dump(TASK/'PILOT_ARCHIVE_RECEIPT.json',record)
 print(json.dumps(record,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT.parents[1]/NAME);args=ap.parse_args();main(args.output.resolve())
