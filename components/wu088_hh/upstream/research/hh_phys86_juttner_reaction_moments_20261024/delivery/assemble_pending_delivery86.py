#!/usr/bin/env python3
"""Assemble a concrete Dropbox-restored final delivery with Drive honestly incomplete.

Preparation has no side effects. Execution requires an actual FINAL pack and
Dropbox ACK, single full GET and restore receipts. CLI: --request FILE --output FILE.
Request keys: repo,head,tree,base,stage,branch,pull_request (or pr),
evidence_identity_path,status_path,pack_receipt_path,
dropbox_upload_receipt_path,dropbox_download_receipt_path,
dropbox_restore_receipt_path,drive_observation_paths,stage_history_paths,
freeze_check_paths,provenance_paths. Lists contain explicit existing JSON paths.
The sibling strict assemble_final86.py supplies parsing/redaction helpers only;
its strict dual-provider assembly path remains unchanged.
"""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import sys
import zipfile
from assemble_final86 import (BASE,require,read_json,sha,regular,hash_file,scrub,
                              nested_values,select_upload,parse)

NAME='PHYS86_FINAL_DELIVERY_20261024.json'
DRIVE_STATUS='INCOMPLETE_UNKNOWN_ACK_OR_NOT_DISPATCHED'

def completed_ack(value,filename,size):
    """Match filename, explicit size and provider id in one completed ACK record."""
    if isinstance(value,dict):
        if value.get('status')=='completed' or value.get('success') is True or value.get('upload_success') is True:
            names=nested_values(value,{'name','file_name','title'})
            sizes=nested_values(value,{'size','file_size_bytes'})
            ids=nested_values(value,{'id','file_id'})
            if filename in names and sizes and all(v==size for v in sizes) and any(isinstance(v,str) and v for v in ids):
                return True
        return any(completed_ack(v,filename,size) for v in value.values())
    return isinstance(value,list) and any(completed_ack(v,filename,size) for v in value)

def assemble(args):
    _,request_raw,cfg=read_json(args.request,allow_request=True)
    output=Path(args.output).absolute()
    require(output.name==NAME,'immutable external filename must be '+NAME)
    require(not output.exists(),'create-only output already exists')
    required={'repo','head','tree','base','stage','branch','evidence_identity_path','status_path','pack_receipt_path',
              'dropbox_upload_receipt_path','dropbox_download_receipt_path','dropbox_restore_receipt_path',
              'drive_observation_paths','stage_history_paths','freeze_check_paths','provenance_paths'}
    require(required<=set(cfg),'required concrete receipt keys missing')
    require(cfg['base']==BASE and cfg['stage']=='FINAL','fixed base / FINAL stage mismatch')
    repo=Path(cfg['repo']).resolve()
    def git(*items): return subprocess.check_output(['git','-C',str(repo),*items],text=True).strip()
    require(git('rev-parse','HEAD')==cfg['head'],'actual Git HEAD mismatch')
    require(git('rev-parse',cfg['head']+'^{tree}')==cfg['tree'],'actual Git tree mismatch')
    require(git('branch','--show-current')==cfg['branch'],'actual branch mismatch')
    subprocess.run(['git','-C',str(repo),'merge-base','--is-ancestor',BASE,cfg['head']],check=True)
    parents=git('show','-s','--format=%P',cfg['head']).split()
    sources=[];payload={}
    def attachment(path,role,public=True):
        p,raw,obj=read_json(path)
        require(p!=output and output.name not in str(p),'future external JSON self-reference forbidden')
        if public and p.is_relative_to(repo):
            member='repo/'+p.relative_to(repo).as_posix()
            require(member in payload,'public receipt absent from final manifest: '+member)
            require((len(raw),sha(raw))==(payload[member]['bytes'],payload[member]['sha256']),'public receipt differs from final pack: '+member)
        removed=[];clean=scrub(obj,redactions=removed)
        provenance={'role':role,'source_path':str(p),'bytes':len(raw),'sha256':sha(raw),'redacted_field_paths':removed}
        sources.append(provenance)
        return obj,{'provenance':provenance,'receipt':clean}
    pack,pack_doc=attachment(cfg['pack_receipt_path'],'final_pack',False)
    require(pack.get('status')=='PACK_CREATED','actual final pack receipt required')
    for key in ['commit','tree','base','stage']:
        require(pack.get(key)==cfg['head' if key=='commit' else key],'pack identity mismatch: '+key)
    size,digest=pack['archive_bytes'],pack['archive_sha256'];archive=regular(pack['archive'])
    require(hash_file(archive)==(size,digest),'frozen original FINAL ZIP mismatch')
    upload,upload_doc=attachment(cfg['dropbox_upload_receipt_path'],'Dropbox_upload',False)
    require(completed_ack(select_upload(upload,'Dropbox'),archive.name,size),'completed Dropbox ACK filename/size/id mismatch')
    download,download_doc=attachment(cfg['dropbox_download_receipt_path'],'Dropbox_single_full_GET',False)
    require(download.get('status')=='PASS_SINGLE_FULL_GET_REOPENED_BYTES','actual Dropbox full GET not PASS')
    require(download.get('operation')=='download' and download.get('get_attempts')==1 and download.get('automatic_retries')==0,'exactly one GET without automatic retries required')
    require(download.get('http_status')==200 and download.get('complete_response_read') is True,'full HTTP200 response required')
    for key in ['expected_bytes','actual_bytes','bytes_received','bytes_written']:
        require(download.get(key)==size,'download byte mismatch: '+key)
    require(download.get('expected_sha256')==download.get('actual_sha256')==digest,'download SHA mismatch')
    restored,restore_doc=attachment(cfg['dropbox_restore_receipt_path'],'Dropbox_actual_full_restore',False)
    require(restored.get('status')=='RESTORE_VERIFIED' and restored.get('operation')=='restore','actual Dropbox restore not verified')
    for key in ['commit','tree','base','stage']:
        require(restored.get(key)==pack.get(key),'restore identity mismatch: '+key)
    require((restored.get('archive_bytes'),restored.get('archive_sha256'))==(size,digest),'restored ZIP identity mismatch')
    downloaded=regular(download['output_path']).resolve()
    require(downloaded==Path(restored['archive']).resolve(),'GET and restored file differ')
    require(not downloaded.samefile(archive),'downloaded ZIP must be distinct from original ZIP')
    require(hash_file(downloaded)==(size,digest),'actual downloaded bytes no longer match')
    pc=pack['counts'];rc=restored['counts']
    expected={'whole_zip_sha256_checked':1,'member_crc_checked':pc['members_including_manifest'],
              'payload_sha256_checked':pc['payload_members'],'git_blob_sha1_checked':pc['repository_blobs'],
              'extracted_members_rehashed':pc['members_including_manifest'],
              'historical_dependency_whole_bytes_checked':pc['historical_dependencies'],'nested_historical_restore_executions':0}
    require(all(rc.get(k)==v for k,v in expected.items()),'actual restore CRC/payload/blob/extract/dependency counts differ')
    manifest_raw=regular(Path(restored['extracted_directory'])/'MANIFEST.json').read_bytes()
    require(sha(manifest_raw)==pack['manifest_sha256'],'extracted manifest SHA differs')
    with zipfile.ZipFile(archive) as z:
        require(z.read('MANIFEST.json')==manifest_raw,'original ZIP and actual restored manifest differ')
    manifest=parse(manifest_raw)
    for key in ['commit','tree','base','stage']:
        require(manifest.get(key)==pack.get(key),'full manifest identity mismatch: '+key)
    payload.update({row['path']:row for row in manifest['payload']})
    identity,identity_doc=attachment(cfg['evidence_identity_path'],'controller_evidence_identity')
    status,status_doc=attachment(cfg['status_path'],'root_conditional_science_status')
    require(isinstance(identity.get('descriptor'),dict),'controller evidence descriptor absent')
    canonical=json.dumps(identity['descriptor'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
    require(sha(canonical)==identity.get('evidence_identity_SHA256'),'controller canonical evidence binding differs')
    require(identity['descriptor'].get('status')==status,'controller descriptor and exact RESULT_STATUS differ')
    require(status.get('HH_R10')=='OFF' and status.get('production_admission')=='NOT_ISSUED','root sentinels differ')
    require(status.get('scientific_completion_scope')=='conditional reference unit only','conditional scientific completion scope required')
    freezes=[]
    require(cfg['freeze_check_paths'],'byte preservation receipt required')
    for path in cfg['freeze_check_paths']:
        obj,doc=attachment(path,'final_byte_freeze')
        require(str(obj.get('status','')).startswith('PASS') and obj.get('mismatches')==[],'byte freeze must PASS with mismatches=[]')
        freezes.append(doc)
    require(cfg['drive_observation_paths'],'actual pending/unknown Drive observations required')
    require(cfg['stage_history_paths'],'actual stage history required')
    drive_docs=[attachment(p,'Drive_observation')[1] for p in cfg['drive_observation_paths']]
    stage_docs=[attachment(p,'stage_history')[1] for p in cfg['stage_history_paths']]
    provenance_docs=[attachment(p,'provenance')[1] for p in cfg['provenance_paths']]
    document={'schema':'PHYS86_FINAL_DELIVERY_DRIVE_INCOMPLETE_V1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'repository':'cosmosapjw-quantum/WU088_HH','branch':cfg['branch'],'pull_request':cfg.get('pull_request',cfg.get('pr')),
      'identity':{'final_HEAD':cfg['head'],'tree':cfg['tree'],'parents':parents,'PHYS85_base_HEAD':BASE,
                  'evidence_identity_SHA256':identity['evidence_identity_SHA256'],'identity_kind':identity['descriptor'].get('identity_kind'),
                  'completed_science_identity':status.get('completed_science_identity')},
      'root_conditional_science_status':status_doc,'controller_evidence_identity':identity_doc,
      'final_zip':{'filename':archive.name,'bytes':size,'sha256':digest,'payload_counts':pc,'pack_receipt':pack_doc,
                   'full_manifest':manifest,'manifest_sha256':pack['manifest_sha256'],
                   'Dropbox':{'status':'FINAL_FULL_GET_AND_RESTORE_VERIFIED','upload':upload_doc,'single_full_GET':download_doc,'actual_full_restore':restore_doc},
                   'Drive':{'status':DRIVE_STATUS,'final_Drive_ZIP_restore':'NOT_RUN','observations':drive_docs,
                            'interpretation':'UNKNOWN acknowledgements and root-interrupted waits are retained; no remote failure or cancellation inferred.'}},
      'stage_history':stage_docs,'final_freeze_checks':freezes,'provenance':provenance_docs,'input_receipt_manifest':sources,
      'assembly_provenance':{'request_bytes':len(request_raw),'request_sha256':sha(request_raw),'helper_sha256':sha(Path(__file__).read_bytes()),
                             'scientific_executions':0,'network_operations':0,'scope':'Metadata assembly from actual final Git/ZIP/Dropbox GET+restore and unchanged controller science evidence.'},
      'Drive_status':DRIVE_STATUS,'final_Drive_ZIP_restore':'NOT_RUN','dual_backup_completion':False,
      'delivery_status':'DROPBOX_FINAL_FULL_RESTORE_VERIFIED_DRIVE_INCOMPLETE',
      'completed_science_identity':status.get('completed_science_identity'),'scientific_completion_claim':status.get('scientific_completion_claim'),
      'scientific_completion_scope':status.get('scientific_completion_scope'),'HH_R10':'OFF','production_admission':'NOT_ISSUED',
      'json_self_reference_policy':'This immutable external JSON excludes its own future hash, provider IDs, upload acknowledgements and readback claims.',
      'redaction_policy':'Original receipt hashes retained; URLs, transport request fields and secrets redacted using the existing delivery helper.'}
    encoded=(json.dumps(scrub(document),ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode('utf-8')
    with output.open('xb') as f: f.write(encoded)
    return {'status':'PENDING_DRIVE_DELIVERY_JSON_CREATED','output':str(output),'bytes':len(encoded),'sha256':sha(encoded),
            'delivery_status':document['delivery_status'],'dual_backup_completion':False,'external_json_upload_or_readback':'NOT_PERFORMED_BY_ASSEMBLER'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--request',required=True);p.add_argument('--output',required=True);args=p.parse_args()
    try:
        print(json.dumps(assemble(args),indent=2));return 0
    except Exception as exc:
        print(json.dumps({'status':'ASSEMBLY_FAILED','error_type':type(exc).__name__,
                          'reason':str(exc) if isinstance(exc,ValueError) else 'Inspect actual receipt paths; no existing output overwritten.'}));return 1
if __name__=='__main__': sys.exit(main())
