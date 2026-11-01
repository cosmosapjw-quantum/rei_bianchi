#!/usr/bin/env python3
"""Stdlib-only integrity + independent algebraic check for the published 3-case evidence.

This tests the small GitHub-published science table. It does NOT validate
physical source rates, prove a Bianchi model, or replace the full 26-state ODE.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys
from pathlib import Path
EXPECTED_SHA256='d9a9986b893114802cdf2a15a3478a0c9388dc9d8e5903a03cbd57b44482f06f'

def verify(path:Path,require_sha:bool=True):
    raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
    if require_sha and digest!=EXPECTED_SHA256:raise ValueError('SOURCE_EVIDENCE_SHA_MISMATCH:'+digest)
    rows=list(csv.DictReader(raw.decode().splitlines()))
    if len(rows)!=3:raise AssertionError('exactly 3 actual model rows required')
    expected={'prehistory_Puchwein','reset_z10_Puchwein','reset_z10_NoUVB'}
    observed={r['case'] for r in rows}
    if observed!=expected:raise AssertionError('case identity mismatch')
    errors={}
    for r in rows:
        name=r.pop('case');v={k:float(z) for k,z in r.items()}
        if not all(math.isfinite(z) for z in v.values()):raise AssertionError('non-finite field')
        nres=v['x_HII_end']-v['x_HII_start']-v['H_photo_per_H']-v['H_CI_per_H']+v['H_recomb_per_H']
        qphot=v['Q_photo_erg_H']-v['Q_photo_heat_erg_H']-v['Q_photo_bind_erg_H']
        qent=v['Q_photo_erg_H']-v['Q_escape_erg_H']+v['Q_CMB_erg_H']-v['Q_ad_erg_H']-v['delta_w_erg_H']-v['delta_Eion_erg_H']
        if abs(nres)>3e-10 or abs(qphot)>4e-19 or abs(qent)>4e-19:raise AssertionError(name+' owner balance failure')
        if v['tau']<=0:raise AssertionError('unphysical non-positive optical depth')
        errors[name]={'H_number_residual':nres,'photo_partition_erg_H':qphot,'total_energy_residual_erg_H':qent,'tau':v['tau']}
    if not(errors['prehistory_Puchwein']['tau']>errors['reset_z10_Puchwein']['tau']):raise AssertionError('source-specific prehistory effect missing')
    return {'status':'PASS_PUBLISHED_3_CASE_MODEL_LEDGER_ONLY','rows':len(rows),'sha256':digest,'checks':errors,
            'canonical_REI':'28/88_UNCHANGED','native_REI_Rust':'NOT_RUN','BASS_BIANCHI':'NOT_RUN'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--file',type=Path,default=Path(__file__).resolve().parent/'PHYSICAL_EVENT_ENERGY_3_CASES.csv')
    p.add_argument('--allow_other_sha',action='store_true');a=p.parse_args()
    print(json.dumps(verify(a.file,not a.allow_other_sha),indent=2))
