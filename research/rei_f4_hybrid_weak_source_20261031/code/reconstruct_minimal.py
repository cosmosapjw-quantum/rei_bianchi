#!/usr/bin/env python3
"""Compact independent 21-state chemistry source reconstruction from full PR295 ZIP.

Input is the exact parent source archive. No time integration or thermal evolution.
The more complete thermal and plotting implementation is code/hybrid.py in the
full source-inclusive research checkpoint.
"""
import argparse, csv, io, json, zipfile
from pathlib import Path
import numpy as np
PRE295='REI_F4_REI_HHE_THERMAL_SOURCE_20261030/'
PRE293='REI_F4_COMMON_FJ_ELECTRON_THERMAL_CLOCK_20261030/'
U=np.array([1,2,10,11,12],dtype=int)

def npz(data):
    with np.load(io.BytesIO(data),allow_pickle=False) as z:
        return {k:z[k].copy() for k in z.files}

def reconstruct(parent_zip):
    with zipfile.ZipFile(parent_zip) as parent:
        hhe=npz(parent.read(PRE295+'results/REI_HHE_FJ_193.npz'))
        rows=list(csv.DictReader(io.StringIO(parent.read(PRE295+'results/HHE_IGM_THERMAL_193.csv').decode())))
        with zipfile.ZipFile(io.BytesIO(parent.read(PRE295+'source/PR293_FULL.zip'))) as z293:
            bass=npz(z293.read(PRE293+'results/SOURCE_FJ21_193.npz'))
            with zipfile.ZipFile(io.BytesIO(z293.read(PRE293+'source/REI_F4_BASS193_SELFCONSISTENT_20261030_FULL.zip'))) as z278:
                state=npz(z278.read('trajectory.npz'))
                atomic=json.loads(z278.read('source/BASS_ATOMIC_MODEL.json'))
    assert len(rows)==193 and bass['F21_per_baryon_s'].shape==(193,21)
    assert atomic['weak_decay']['maps'][0]=='n -> H1II + e + anti_nu'
    tau=float(atomic['weak_decay']['neutron_mean_lifetime_s'])
    q=bass['q21'];A=bass['A21'];Y=state['Y']
    nb=np.array([float(row['nb_m3']) for row in rows])
    ne=np.array([float(row['ne_all_BASS_cm3'])-float(row['ne_HHe_cm3']) for row in rows])*1e6
    # q4 is positive, index 4 DII is outside H/He replacement; cross J is n_b (M_R X) q4.
    assert q[4]==1 and 4 not in U
    MRX=hhe['J5x21_common'][:,:,4]/nb[:,None]
    F_rei=hhe['F5']+ne[:,None]*MRX
    Fb=bass['F21_per_baryon_s'];Jb=bass['J21_per_s']
    F=Fb.copy();F[:,U]=F_rei
    J=Jb.copy();J[:,U,:]=hhe['J5x21_common']
    wrong=float(np.max(abs(np.einsum('j,ijk->ik',A,J))))
    beta=Jb[:,2,0]
    assert np.allclose(beta,1/tau,rtol=1e-12,atol=0)
    F[:,2]+=beta*Y[:,0]
    J[:,2,0]+=beta
    af=float(np.max(abs(F@A)))
    aj=float(np.max(abs(np.einsum('j,ijk->ik',A,J))))
    assert wrong>1e-4 and af<8e-24 and aj<5e-21
    return {'F':F,'J':J,'q':q,'A':A,'z':state['z']},dict(epochs=193,
           F_entries=F.size,J_entries=J.size,naive_AJ=wrong,repaired_AJ=aj,repaired_AF=af,
           beta_s=float(beta[0]),new_ivps=0)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('pr295_zip');a.add_argument('outdir');v=a.parse_args()
    d,summary=reconstruct(v.pr295_zip);out=Path(v.outdir);out.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(out/'HYBRID_FJ21_MINIMAL.npz',**d)
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
