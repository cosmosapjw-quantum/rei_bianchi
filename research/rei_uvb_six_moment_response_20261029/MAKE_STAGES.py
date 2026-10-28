"""Create-only retrospective stage capsules from the verified final unit tree.
These are per-stage recovery snapshots, not historical at-stage runtime snapshots.
"""
from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parent
stages=[
('R1','Question, source scope and no-IVP gate','THEORY_KO.md'),
('R2','Primary Puchwein and BB13 source provenance','source/PUCHWEIN2019_13_ROW_PROJECTION.json'),
('R3','Conditional fixed-template claims, redshift and units','THEORY_KO.md'),
('R4','Nonlinear six-moment map and confidence support construction','THEORY_KO.md'),
('R5','Jacobian, Hessian, support and energy ledger derivations','THEORY_KO.md'),
('R6','Different-author scientific review required; same-context CAS only','THEORY_KO.md'),
('R7','Wolfram CAS and new finite numerical cross-checks','results/TESTS_STDERR.txt'),
('R8','Source-rate vs physical tau claim gate and negative cases','REPORT_KO.md'),
('R9','Mathematical-to-code rate/clock/energy contract','THEORY_KO.md'),
('R10','Scoped theory result and resumption handoff','HANDOFF_NEXT_THREAD_KO.md'),
('C1','Frozen source/acceptance and independent local budget','source/FROZEN_BB13_SUPPORT_INPUT.json'),
('C2','Map BB13, P19 and BASS tau source units to code','code/source_response.py'),
('C3','Cholesky GLS, stable log interpolation and exact support','code/source_response.py'),
('C4','Bounded source-rate calculation without old IVP','code/run_once.py'),
('C5','Complete six-moment rate/Jacobian/Hessian/energy implementation','code/source_response.py'),
('C6','Actual 21-test regression execution and negative controls','results/TESTS_STDERR.txt'),
('C7','Finite support witnesses, clock and energy science checks','results/RESULT.json'),
('C8','MP80 clock check, independent QR and resource accounting','results/REPAIR_HISTORY.json'),
('C9','Different-author code review required; same-context checks only','tests/test_source_response.py'),
('C10','Publication, dual backup and copyable handoff','HANDOFF_NEXT_THREAD_KO.md')]
count=0
manifest=[]
for stage,obj,ev in stages:
 status='HOLD_DISTINCT_AUTHOR_REVIEW' if stage in ('R6','C9') else 'OUTPUT_COMPLETE_SCOPED'
 if status.startswith('OUTPUT'):count+=1
 row={'schema':'REI_SOURCE_RESPONSE_STAGE_V1','stage':stage,'objective':obj,
      'status':status,'local_progress':f'{count}/20','original_working_DAG':'33/88',
      'central_last_observed':'28/88','original_DAG_delta':0,
      'evidence_path':ev,'source_sha256':'13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b',
      'source_projection_sha256':'dcd13144072584085f49698e40c9822e074fecc2a6046605dc9d67cfe7cc3eff',
      'native_subagent':'NOT_EXPOSED','new_ivp':0,'F4':'PARTIAL','L4_ready':False,
      'archive_snapshot_semantics':'RECONSTRUCTED_AT_CLOSEOUT_FROM_FINAL_VERIFIED_FILES',
      'remote_backup_receipts':'IN_SEPARATE_DELIVERY_ACK'}
 stagefile=R/'stages'/f'{stage}.json';stagefile.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n')
 files=[f'stages/{stage}.json','source/FROZEN_BB13_SUPPORT_INPUT.json','source/PUCHWEIN2019_13_ROW_PROJECTION.json']
 if stage not in ('R1','R2','R3','R4'):files.append('THEORY_KO.md')
 if stage in ('R8','R9','R10','C6','C7','C8','C9','C10'):files.append('REPORT_KO.md')
 if stage.startswith('C'):files.extend(['code/source_response.py','code/run_once.py'])
 if stage in ('C6','C7','C8','C9','C10'):files.extend(['tests/test_source_response.py','results/RESULT.json','results/TESTS_STDERR.txt','results/TESTS_TIME.txt','results/REPAIR_HISTORY.json'])
 if stage in ('R10','C10'):files.append('HANDOFF_NEXT_THREAD_KO.md')
 archive=R/'delivery'/f'REI_SOURCE_RESPONSE_STAGE_{stage}_20261029.zip'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for f in sorted(set(files)):
   z.write(R/f,f)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  assert all(z.read(f)==(R/f).read_bytes() for f in set(files))
 item={'stage':stage,'progress':f'{count}/20','original_working_DAG':'33/88','central_last_observed':'28/88',
       'status':status,'archive':archive.name,'bytes':archive.stat().st_size,
       'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
       'local_crc_and_member_bytes':'PASS','payload_files':len(set(files)),
       'provider_status':'NOT_YET_SUBMITTED'}
 manifest.append(item)
(R/'delivery/STAGE_ARCHIVE_MANIFEST.json').write_text(json.dumps({'schema':'REI_SOURCE_RESPONSE_STAGE_ARCHIVES_V1','scope':'20 per-stage create-only closeout snapshots, not chronological at-stage state','stages':manifest},ensure_ascii=False,indent=2)+'\n')
print('STAGES',len(manifest),'SCOPED_COMPLETED',count)
for m in manifest:print(m['stage'],m['progress'],m['bytes'],m['sha256'][:12])
