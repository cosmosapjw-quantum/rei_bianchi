#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from heavy_numerics_v2 import record_dual_backup_ack, pending_delta_hashes


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--folder',type=Path,required=True)
    ap.add_argument('--delta-sha256',required=True)
    ap.add_argument('--drive-id',required=True)
    ap.add_argument('--dropbox-id',required=True)
    a=ap.parse_args()
    record_dual_backup_ack(a.folder,a.delta_sha256,drive={'id':a.drive_id},dropbox={'id':a.dropbox_id})
    print(json.dumps({'status':'DUAL_BACKUP_ACK_RECORDED','delta_sha256':a.delta_sha256,'pending_after':pending_delta_hashes(a.folder)},indent=2,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
