#!/usr/bin/env python3
"""Back up pending deltas in parallel across providers; never overlap new scientific work."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time,uuid
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'vendor/orchestration')]
from wu088_hh.backup import dual_backup,digest
from heavy_numerics_v2 import RunLease,pending_delta_hashes,record_dual_backup_ack

def main():
    p=argparse.ArgumentParser();p.add_argument('--folder',required=True,type=Path)
    p.add_argument('--drive',default=os.environ.get('GDRIVE_RCLONE_REMOTE'))
    p.add_argument('--dropbox',default=os.environ.get('DROPBOX_RCLONE_REMOTE'))
    p.add_argument('--prefix',default='BASS_DERIVATION_DOSSIERS_20260912/WU088_HH_R31K_B')
    p.add_argument('--receipts',required=True,type=Path);a=p.parse_args()
    if not a.drive or not a.dropbox:p.error('provide existing raw --drive and --dropbox remotes')
    folder=a.folder.resolve();count=0
    with RunLease(folder/'RUN.lock',folder/'RUN_STATE.json',metadata={'phase':'DUAL_BACKUP_NO_COMPUTE'}):
        pending=set(pending_delta_hashes(folder))
        if pending:
            queue=[json.loads(l) for l in (folder/'DURABLE_UPLOAD_QUEUE.jsonl').read_text().splitlines() if l.strip()]
            for row in queue:
                if row['delta_sha256'] not in pending:continue
                source=Path(row['delta_path']).resolve()
                if source.parent!=folder/'durable_deltas':raise ValueError('delta is not in this state\'s durable_deltas directory')
                if digest(source)!=(row['delta_sha256'],row['bytes']):raise ValueError('queued delta source changed')
                def target(remote):
                    return remote.rstrip('/')+('' if remote.endswith(':') else '/')+a.prefix.strip('/')+'/'+folder.name+'/deltas/'+source.name
                dest={'google_drive':target(a.drive),'dropbox':target(a.dropbox)}
                receipt=a.receipts/(row['delta_sha256']+'_'+uuid.uuid4().hex[:10]+'.json')
                r=dual_backup(source,dest,receipt)
                if not r['dual_raw_readback_verified']:
                    print(json.dumps({'status':'BLOCKED_BACKUP_INCOMPLETE','receipt':str(receipt)}));return 74
                rh=hashlib.sha256(receipt.read_bytes()).hexdigest()
                def ref(provider):
                    return dict(id=dest[provider],locator_kind='rclone_remote_path_not_provider_object_id',
                                sha256=row['delta_sha256'],bytes=row['bytes'],raw_readback_receipt_sha256=rh)
                record_dual_backup_ack(folder,row['delta_sha256'],drive=ref('google_drive'),dropbox=ref('dropbox'))
                count+=1;pending.remove(row['delta_sha256'])
    print(json.dumps(dict(status='PENDING_DELTAS_BACKED_UP_AND_ACKED',count=count,pending_after=pending_delta_hashes(folder))))
    return 0
if __name__=='__main__':raise SystemExit(main())
