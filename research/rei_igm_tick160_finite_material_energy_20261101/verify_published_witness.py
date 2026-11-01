#!/usr/bin/env python3
"""Verify published original-source nine-node finite energy witness (stdlib).

This checks 9 published source-derived rows and the historical scope only.
For a 46,080-node source-authentic proof run `original_tick160.py` with both
sha-locked GitHub Actions source ZIP inputs included in the master artifact.
"""
import csv,hashlib,json,math
from pathlib import Path
SOURCE_GIT_BLOB='2002d5bd4a5843a2061cb292aa6559f822c2ac09'
CASE_IDS=(0,1,2000,5000,15000,30000,40959,43519,46079)

def git_blob_sha(content):
    return hashlib.sha1(b'blob '+str(len(content)).encode()+b'\x00'+content).hexdigest()

def check(path):
    raw=Path(path).read_bytes()
    if git_blob_sha(raw)!=SOURCE_GIT_BLOB:raise ValueError('REPORTED_WITNESS_BYTE_IDENTITY_MISMATCH')
    data=list(csv.DictReader(raw.decode('utf-8').splitlines()))
    if tuple(int(r['node']) for r in data)!=CASE_IDS:raise ValueError('NINE_NODE_SOURCE_IDENTITY_MISMATCH')
    physical=[]
    for r in data:
        d={k:float(x) for k,x in r.items() if k!='node'}
        if not all(map(math.isfinite,d.values())):raise ValueError('NONFINITE_SOURCE_ROW')
        if d['delta_Uth_hi_eV_H']>=0 or d['delta_Umat_hi_eV_H']>=0:
            raise ValueError('SOURCE_WITNESS_STRICT_MATERIAL_OR_THERMAL_LOSS_FAIL')
        if not(d['delta_Uth_lo_eV_H']<=d['delta_Uth_hi_eV_H'] and
               d['delta_Uion_lo_eV_H']<=d['delta_Uion_hi_eV_H'] and
               d['delta_Umat_lo_eV_H']<=d['delta_Umat_hi_eV_H']):
            raise ValueError('SOURCE_INTERVAL_ORDER_VIOLATION')
        if d['delta_Uth_lo_eV_H']+d['delta_Uion_lo_eV_H']>d['delta_Umat_lo_eV_H']+1e-14:
            raise ValueError('SOURCE_MATTER_ENERGY_LOWER_INTERVAL_NOT_CONSERVATIVE')
        if d['delta_Uth_hi_eV_H']+d['delta_Uion_hi_eV_H']<d['delta_Umat_hi_eV_H']-1e-14:
            raise ValueError('SOURCE_MATTER_ENERGY_UPPER_INTERVAL_NOT_CONSERVATIVE')
        if d['dT_representative_K']>0 and d['dXe_representative_per_H']>=0:
            raise ValueError('REPRESENTATIVE_T_RISE_REQUIRES_ELECTRON_DECLINE')
        physical.append(d)
    return {'sha1_blob':SOURCE_GIT_BLOB,'rows':len(data),
            'all_9_thermal_loss':True,'all_9_material_loss':True,
            'representative_T_rise_in_9':sum(d['dT_representative_K']>0 for d in physical),
            'interpretation':'9 source-derived finite-interval snapshots, not the full 46k verified theorem',
            'REI_central_DAG':'28/88','first_canonical_interval':'BLOCKED_AT_TICK160'}
if __name__=='__main__':
    import sys
    f=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent/'ACTUAL_SOURCE_9_WITNESS_NODES.csv'
    print(json.dumps(check(f),indent=2))
