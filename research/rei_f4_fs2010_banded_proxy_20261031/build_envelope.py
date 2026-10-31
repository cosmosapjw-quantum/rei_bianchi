#!/usr/bin/env python3
"""Frozen BASS193 x FS2010 (21cmFAST mirror) band-support energy deposition envelope.

This computes a scientifically scoped PROJECTION, not a native multi-species cascade.
No new cosmological IVP; no forced modification of parent or sibling source owner.
"""
from __future__ import annotations
import argparse, io, json, hashlib, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
DEFAULT_PARENT=(HERE/'inputs'/'PR302_ORIGINAL_FULL193_ARRIVAL_192.csv') if (HERE/'inputs'/'PR302_ORIGINAL_FULL193_ARRIVAL_192.csv').exists() else (HERE.parent/'rei_f4_fs2010_full193_threshold_20261031'/'results'/'FS2010_FULL193_ARRIVAL_192.csv')
DEFAULT_303=(HERE/'inputs'/'PR303_ORIGINAL_SPECIES_COMPAT_192.csv') if (HERE/'inputs'/'PR303_ORIGINAL_SPECIES_COMPAT_192.csv').exists() else (HERE.parent/'rei_f4_fs2010_species_compat_20261031'/'results'/'BASS193_FS2010_SPECIES_COMPAT_192.csv')
ORIGINAL_PARENT_CSV_SHA='155c70c1c4363d75db46b6898eca6bbf9496bc3cdd586b6cf0994fa2384df6df'
ORIGINAL_PR303_CSV_SHA='dd0b2ba58effb6ee5929a7091b4b2a91fa172e2d26df7a85dc858ff53f7c1a09'
SOURCE_SHA='603b7eaacec1e8f0e3afe17c5c37ea9c4aee23890e969b1f121bf2b6f4f77192'
PR303_SHA='5b904c0019109d21ef88ff1610057010cd1b5bd6e446f9ac13188f60fb9fadd6'
CATS=['H_I','He_I','He_II','Li_I']
BANDS=['e0_10p2','e10p2_13p6','e13p6_24p59','e24p59_54p42','e54p42_plus']
CHANNELS=['heat','ion','exc']

def sha(path):
    with open(path,'rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def source_data(parent:Path,prev:Path):
    if parent.suffix=='.csv':
        if sha(parent)!=ORIGINAL_PARENT_CSV_SHA:raise AssertionError('PR302_ORIGINAL_CSV_SHA_MISMATCH')
        parent_df=pd.read_csv(parent)
    else:
        if sha(parent)!=SOURCE_SHA:raise AssertionError('PR302_PRIVATE_MASTER_SHA_MISMATCH')
        with zipfile.ZipFile(parent) as z:
            assert z.testzip() is None
            p='REI_F4_FS2010_FULL193_THRESHOLD_20261031/results/FS2010_FULL193_ARRIVAL_192.csv'
            raw=z.read(p)
            assert hashlib.sha256(raw).hexdigest()==ORIGINAL_PARENT_CSV_SHA
            parent_df=pd.read_csv(io.BytesIO(raw))
    if prev.suffix=='.csv':
        if sha(prev)!=ORIGINAL_PR303_CSV_SHA:raise AssertionError('PR303_ORIGINAL_CSV_SHA_MISMATCH')
        compat=pd.read_csv(prev)
    else:
        if sha(prev)!=PR303_SHA:raise AssertionError('PR303_PRIVATE_MASTER_SHA_MISMATCH')
        with zipfile.ZipFile(prev) as z:
            assert z.testzip() is None
            p='REI_F4_FS2010_SPECIES_COMPAT_20261031/results/BASS193_FS2010_SPECIES_COMPAT_192.csv'
            raw=z.read(p)
            assert hashlib.sha256(raw).hexdigest()==ORIGINAL_PR303_CSV_SHA
            compat=pd.read_csv(io.BytesIO(raw))
    assert len(parent_df)==len(compat)==192
    assert np.array_equal(parent_df.arrival_interval.to_numpy(),compat.arrival_interval.to_numpy())
    assert np.max(abs(parent_df.z_high-compat.z_start))<1e-12
    assert np.max(abs(parent_df.z_low-compat.z_end))<1e-12
    return parent_df,compat

def bracket(x,grid,bands):
    # Only a projected single-x_i value is assigned. Out-of-domain values are explicitly flagged.
    val=float(np.clip(x,grid[0],grid[-1]))
    idx=int(np.searchsorted(grid,val,side='right')-1)
    idx=min(idx,len(grid)-2)
    t=(val-grid[idx])/(grid[idx+1]-grid[idx])
    return ((1-t)*bands[idx]+t*bands[idx+1]), bool(x>=grid[0] and x<=grid[-1]),val

def make(parent:Path,prev:Path):
    parent_df,compat=source_data(parent,prev)
    t=json.loads((HERE/'fst_model_envelope_mirror.json').read_text())
    grid=np.array(t['xi'],dtype=float); bminmax=np.array(t['bands'],dtype=float)
    assert bminmax.shape==(14,4,6)
    assert np.all(np.diff(grid)>0) and np.all(bminmax[:,:,::2]<=bminmax[:,:,1::2])
    # Four energy-resolved band tensors, already first-flight source weighted, from immutable PR302.
    energies=np.array([[sum(float(row[f'{s}_{b}_primary_e_eV_per_b']) for s in CATS) for b in BANDS] for _,row in parent_df.iterrows()])
    counts=np.array([[sum(float(row[f'{s}_{b}_counts_per_b']) for s in CATS) for b in BANDS] for _,row in parent_df.iterrows()])
    E=energies.sum(axis=1)
    Eref=parent_df.total_primary_e_eV_per_b.to_numpy()
    Eterm=parent_df.FS_low_e_heat_kinematic_eV_per_b.to_numpy()
    np.testing.assert_allclose(E,Eref,rtol=2e-12,atol=2e-24)
    np.testing.assert_allclose(energies[:,0],Eterm,rtol=2e-12,atol=2e-24)
    assert np.all(energies>=-1e-24) and np.all(counts>=-1e-24)
    assert abs(float(E.sum())-6.749242464433259e-11)<1e-22
    assert abs(float(Eterm.sum())-8.581099847924098e-12)<1e-22
    rows=[]
    summary={'source':{'PR302_SHA256':SOURCE_SHA,'PR303_SHA256':PR303_SHA,'FS_mirror_commit':t['source'],'UCLA_TAR':'NOT_ACQUIRED','FS_MIRROR_BLOB_SHA1':t['github_blobs']},'model':'FS2010_BANDED_SINGLE_XI_PROJECTED_ENCLOSURE_NOT_NATIVE_SPECIES_CASCADE','E_line_eV':t['E_singlet_eV'],'E_primary_eV_per_b':float(E.sum()),'E_sub10p2_eV_per_b':float(Eterm.sum()),'E_above10p2_eV_per_b':float((E-Eterm).sum()),'scenarios':{}}
    for j,(_,src) in enumerate(parent_df.iterrows()):
        d=compat.iloc[j]
        yhe=float(d.helium_per_H_ref)
        xh=float(d.xHII_end)
        xe=(xh+yhe*(float(d.xHeII_end)+2*float(d.xHeIII_end)))/(1+yhe)
        row={'arrival_interval':j,'z_start':float(d.z_start),'z_end':float(d.z_end),'primary_eV_per_b':float(E[j]),'terminal_eV_per_b':float(Eterm[j]),'high_E_eV_per_b':float(E[j]-Eterm[j]),'xHII_saved_endpoint':xh,'xHeII_saved_endpoint':float(d.xHeII_end),'xHeIII_saved_endpoint':float(d.xHeIII_end),'projected_x_electron_equal':xe}
        for label,xx in [('xHII',xh),('electron_matched',xe)]:
            env,inside,clip=bracket(xx,grid,bminmax)
            row[label+'_in_xgrid']=inside
            row[label+'_xi_clipped']=clip
            for c,chan in enumerate(CHANNELS):
                lo=Eterm[j] if chan=='heat' else 0.0
                hi=lo
                # Not applying FS2010 to below 10.2 eV. It is terminal as convention.
                for bi in range(1,5):
                    ee=energies[j,bi]
                    lo+=ee*env[bi-1,2*c]
                    hi+=ee*env[bi-1,2*c+1]
                assert lo>=-1e-24 and hi+1e-24>=lo
                row[label+'_'+chan+'_lo_eV_per_b']=float(lo)
                row[label+'_'+chan+'_hi_eV_per_b']=float(hi)
        rows.append(row)
    out=pd.DataFrame(rows)
    for label in ['xHII','electron_matched']:
        area={'in_grid_arrival_intervals':int(out[label+'_in_xgrid'].sum()),'out_of_grid_arrival_intervals':int((~out[label+'_in_xgrid']).sum()),
              'out_of_grid_energy_fraction':float(out.loc[~out[label+'_in_xgrid'],'primary_eV_per_b'].sum()/E.sum())}
        for chan in CHANNELS:
            a=out[label+'_'+chan+'_lo_eV_per_b'];b=out[label+'_'+chan+'_hi_eV_per_b']
            area[chan+'_lo_eV_per_b']=float(a.sum())
            area[chan+'_hi_eV_per_b']=float(b.sum())
            area[chan+'_lo_fraction_of_primary']=float(a.sum()/E.sum())
            area[chan+'_hi_fraction_of_primary']=float(b.sum()/E.sum())
        # Do not silently extrapolate beyond the original ionized-fraction grid.
        # The below-10.2 eV terminal convention is independent of xi.
        valid=out[label+'_in_xgrid'].to_numpy(dtype=bool)
        high_out=float(out.loc[~valid,'high_E_eV_per_b'].sum())
        area['above10p2_out_of_grid_unassigned_eV_per_b']=high_out
        area['heat_lo_strict_xsupport_eV_per_b']=float(Eterm.sum()+sum(out.loc[valid,label+'_heat_lo_eV_per_b']-out.loc[valid,'terminal_eV_per_b']))
        area['heat_hi_strict_xsupport_eV_per_b']=float(Eterm.sum()+sum(out.loc[valid,label+'_heat_hi_eV_per_b']-out.loc[valid,'terminal_eV_per_b'])+high_out)
        area['ion_hi_strict_xsupport_eV_per_b']=float(out.loc[valid,label+'_ion_hi_eV_per_b'].sum()+high_out)
        area['exc_hi_strict_xsupport_eV_per_b']=float(out.loc[valid,label+'_exc_hi_eV_per_b'].sum()+high_out)
        summary['scenarios'][label]=area
    lo_all=sum(out[f'xHII_{ch}_lo_eV_per_b'].sum() for ch in CHANNELS)
    hi_all=sum(out[f'xHII_{ch}_hi_eV_per_b'].sum() for ch in CHANNELS)
    assert lo_all<=E.sum()*(1+5e-5)
    assert hi_all>=E.sum()*(1-5e-5)
    summary['caveat']='Min/max intervals hold for piecewise linear FS mirror table and chosen one-xi projections. They do NOT bound the actual native multispecies BASS193 cascade. Clipped out-of-grid x values are extrapolation conventions, not source-owned predictions. The components cannot be simultaneously at their interval extremes.'
    summary['gates']={'WORKING_DAG':'33/88','CENTRAL_DAG':'28/88','F4_FAST_DAG':'4/7','CANONICAL_DELTA':0,'AUXILIARY':'1/1_SCOPED','L4_READY':False,'PRODUCTION':'HOLD','NEW_IVPS':0,'NO_MERGE':True,'NO_FORCE_PUSH':True,'AUTO_NEXT_NODE':False}
    out.to_csv(HERE/'BASS193_FS2010_BAND_DEPOSITION_ENVELOPE_192.csv',index=False,float_format='%.17g')
    (HERE/'SCIENTIFIC_RESULT.json').write_text(json.dumps(summary,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
    return out,summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,default=DEFAULT_PARENT);p.add_argument('--prev',type=Path,default=DEFAULT_303)
    x=p.parse_args()
    out,r=make(x.parent,x.prev)
    print('OUTPUT_ROWS',len(out));print(json.dumps(r,indent=2,ensure_ascii=False))
