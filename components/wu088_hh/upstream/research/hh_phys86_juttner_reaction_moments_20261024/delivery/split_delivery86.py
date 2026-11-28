#!/usr/bin/env python3
"""Create byte-exact transport parts from a frozen delivery archive.
Packaging IO only. No extraction, scientific calculation, upload or overwrite.
"""
from pathlib import Path
import argparse,datetime,hashlib,json
PART_BYTES=6*1024*1024
BUFFER_BYTES=256*1024

def split(receipt_path:Path,outdir:Path):
    frozen=json.loads(receipt_path.read_text());source=Path(frozen['archive'])
    expected_size=frozen['archive_bytes'];expected_sha=frozen['archive_sha256']
    count=(expected_size+PART_BYTES-1)//PART_BYTES
    if count<1: raise ValueError('Empty frozen archive')
    outputs=[outdir/(source.name+f'.part{i:03d}') for i in range(1,count+1)]
    manifest_path=outdir/(source.name+'.PARTS_MANIFEST.json')
    if any(p.exists() for p in outputs+[manifest_path]): raise FileExistsError('Create-only destination already exists')
    outdir.mkdir(parents=True,exist_ok=True)
    original_digest=hashlib.sha256();original_count=0;rows=[]
    with source.open('rb') as stream:
        for ordinal,dest in enumerate(outputs,1):
            digest=hashlib.sha256();length=0;offset=original_count
            with dest.open('xb') as output:
                while length<PART_BYTES:
                    block=stream.read(min(BUFFER_BYTES,PART_BYTES-length))
                    if not block: break
                    output.write(block);digest.update(block);original_digest.update(block)
                    length+=len(block);original_count+=len(block)
            rows.append({'ordinal':ordinal,'offset':offset,'length':length,'sha256':digest.hexdigest(),'localpath':str(dest.resolve())})
        extra=stream.read(1)
    if extra or original_count!=expected_size or original_digest.hexdigest()!=expected_sha:
        raise ValueError('Frozen original size/SHA mismatch; created partial outputs preserved for diagnosis')
    joined=hashlib.sha256();joined_count=0
    for row,dest in zip(rows,outputs):
        digest=hashlib.sha256();length=0
        with dest.open('rb') as stream:
            while True:
                block=stream.read(BUFFER_BYTES)
                if not block: break
                digest.update(block);joined.update(block);length+=len(block);joined_count+=len(block)
        if length!=row['length'] or digest.hexdigest()!=row['sha256']:
            raise ValueError('Part readback mismatch; created outputs preserved for diagnosis')
    if joined_count!=expected_size or joined.hexdigest()!=expected_sha:
        raise ValueError('Concatenated size/SHA mismatch; outputs preserved for diagnosis')
    manifest={'schema':'PHYS86_BYTE_EXACT_DELIVERY_PARTS_V1','status':'PARTS_CREATED_CONCATENATION_VERIFIED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':frozen['stage'],'source_pack_receipt':str(receipt_path.resolve()),'originalfilename':source.name,'original_localpath':str(source.resolve()),'original_bytes':expected_size,'original_sha256':expected_sha,'part_chunk_bytes':PART_BYTES,'stream_buffer_bytes':BUFFER_BYTES,'parts':rows,'concatenation_verification':{'bytes':joined_count,'sha256':joined.hexdigest(),'equals_frozen_original':True},'original_modified':False,'archive_extracted':False,'scientific_evaluations':0,'uploads':0,'provider_backup_status':'NOT_ESTABLISHED_BY_LOCAL_PARTS','claim_limit':'Payload-preserving transport change only; no API size limit or prior remote failure inferred.'}
    with manifest_path.open('x',encoding='utf-8') as f: json.dump(manifest,f,indent=2);f.write('\n')
    return {'stage':frozen['stage'],'manifest':str(manifest_path.resolve()),'original_bytes':expected_size,'original_sha256':expected_sha,'parts':rows,'concatenation_verified':True}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pack_receipt',type=Path)
    parser.add_argument('--outdir',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(split(args.pack_receipt,args.outdir)))
if __name__=='__main__': main()
