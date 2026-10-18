"""Synthetic CSV plumbing tests; never counted as native or physics histories."""
from pathlib import Path
import csv,math,sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analyze_v14 import analyze,MODES

def fixture(tmp_path):
    fields=['mode','N','step','Xend','T_K','HII','HeII','HeIII','photons_per_H','source_N','source_U',
        'energy_residual_eV_H','photon_residual_H']
    fields += ['photo_'+s for s in ('HI','HeI','HeII')]+['CI_'+s for s in ('HI','HeI','HeII')]
    fields += ['RR_'+s for s in ('HII','HeII','HeIII')]+['DR_HeII']
    fields += ['electrons_per_H','photo_binding_eV_H','photo_heat_eV_H','CE_HI_eV_H','CE_HeI_eV_H','CE_HeII_eV_H','RR_HII_eV_H','RR_HeII_eV_H','RR_HeIII_eV_H','DR_HeII_eV_H','FF_eV_H','CMB_eV_H','thermal_work_eV_H','escape_eV_H']
    rows=[];births=[];n=8;xend=1e-5;h=xend/n
    c=(1-1/math.sqrt(3))/2
    for mode in MODES:
        for step in range(1,9):
            row={k:0 for k in fields};row.update(mode=mode,N=8,step=step,Xend=xend,T_K=15000,HII=.075,HeII=.12,HeIII=.03)
            row['electrons_per_H']=.075+.2454/(4*(1-.2454))*(.12+2*.03)
            rows.append(row)
            points=[] if mode=='source_off' else ([c,1-c] if mode in ('physical_gl2','source_off_gl2') else ([.5,.5] if mode=='common_combined' else [.5]))
            for i,t in enumerate(points):births.append(dict(mode=mode,N=n,step=step,birth=i,a=math.exp((step-1+t)*h)/21.,weight_dln_a=h/len(points),proper_time_weight_s=1.,added_N=0.,added_U=0.))
    path=tmp_path/'SYNTHETIC_NOT_NATIVE.csv'
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    with Path(str(path)+'.births.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(births[0]));w.writeheader();w.writerows(births)
    return path

def test_analyzer_accepts_complete_synthetic_shape(tmp_path):
    p=fixture(tmp_path);r=analyze(p)
    assert r['histories']==7 and r['rows']==56
    assert r['maximum_species_event_residual']==0

def test_missing_birth_sidecar_fails(tmp_path):
    p=fixture(tmp_path);Path(str(p)+'.births.csv').unlink()
    with pytest.raises(ValueError,match='missing actual birth'):analyze(p)

def test_incomplete_run_fails(tmp_path):
    p=fixture(tmp_path);ls=p.read_text().splitlines();p.write_text('\n'.join(ls[:-1])+'\n')
    with pytest.raises(ValueError,match='incomplete history'):analyze(p)

def test_orphan_birth_fails(tmp_path):
    p=fixture(tmp_path);b=Path(str(p)+'.births.csv');b.write_text(b.read_text().replace('physical_gl2,8,','physical_gl2,16,'))
    with pytest.raises(ValueError,match='orphan birth'):analyze(p)
