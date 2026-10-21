"""Manufactured output mutations, NOT new native/physical trajectories."""
import csv, sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analyze_v14 import analyze
from test_native_analysis import fixture

def augmented(tmp_path):
    p=fixture(tmp_path)
    rows=list(csv.DictReader(p.open()))
    y=.2454/(4*(1-.2454))
    for r in rows:
        r['electrons_per_H']=.075+y*(.12+2*.03)
        for k in ('photo_binding_eV_H','photo_heat_eV_H','CE_HI_eV_H','CE_HeI_eV_H',
                  'CE_HeII_eV_H','RR_HII_eV_H','RR_HeII_eV_H','RR_HeIII_eV_H',
                  'DR_HeII_eV_H','FF_eV_H','CMB_eV_H','thermal_work_eV_H','escape_eV_H'):
            r[k]=0.
    write(p,rows)
    return p

def write(p,rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def test_closed_zero_event_fixture(tmp_path):
    assert analyze(augmented(tmp_path))['rows']==56

@pytest.mark.parametrize('field,value',[
    ('CE_HI_eV_H',1e-4),('RR_HeII_eV_H',1e-4),('FF_eV_H',1e-4),
    ('CMB_eV_H',1e-4),('thermal_work_eV_H',1e-4),('escape_eV_H',1e-4),
    ('photo_binding_eV_H',1e-4),('electrons_per_H',.5)])
def test_independent_account_rejects_changed_channel(tmp_path,field,value):
    p=augmented(tmp_path);rows=list(csv.DictReader(p.open()));rows[-1][field]=value;write(p,rows)
    # Native recorded residual remains zero: reconstruct from output primitives.
    with pytest.raises(ValueError,match='independent'):
        analyze(p)

@pytest.mark.parametrize('seed',range(16))
def test_nonzero_mixed_channels_and_signed_cmb(seed):
    # Independent construction of a cumulative event budget, no ODE integration.
    import random
    from math import fsum
    from event_energy_audit import audit_row,CHI,KB_ERG_K,EV_ERG,HE_PER_H,IC,T0
    rng=random.Random(seed)
    P=[rng.uniform(0,1e-5) for _ in range(3)]
    C=[rng.uniform(0,1e-5) for _ in range(3)]
    R=[rng.uniform(0,1e-5) for _ in range(3)]
    D=rng.uniform(0,1e-5)
    net=[P[i]+C[i]-R[i] for i in range(3)];net[1]-=D
    f=[IC[0]+net[0],IC[1]+(net[1]-net[2])/HE_PER_H,IC[2]+net[2]/HE_PER_H]
    e0=IC[0]+HE_PER_H*(IC[1]+2*IC[2]);e=f[0]+HE_PER_H*(f[1]+2*f[2])
    r=dict(zip(('HII','HeII','HeIII'),f));r['electrons_per_H']=e
    for label,v in [('photo',P),('CI',C),('RR',R)]:
        species=('HII','HeII','HeIII') if label=='RR' else ('HI','HeI','HeII')
        r.update({label+'_'+k:x for k,x in zip(species,v)})
    r['DR_HeII']=D
    cooling=('RR_HII_eV_H','RR_HeII_eV_H','RR_HeIII_eV_H','DR_HeII_eV_H',
             'CE_HI_eV_H','CE_HeI_eV_H','CE_HeII_eV_H','FF_eV_H')
    for name in cooling:r[name]=rng.uniform(0,1e-5)
    r['photo_binding_eV_H']=sum(x*y for x,y in zip(CHI,P))
    r['photo_heat_eV_H']=rng.uniform(0,1e-4)
    r['CMB_eV_H']=rng.uniform(-1e-5,1e-5)
    r['thermal_work_eV_H']=rng.uniform(0,1e-4)
    r['escape_eV_H']=sum(r[k] for k in cooling)+sum(x*y for x,y in zip(CHI,R))+CHI[1]*D
    w0=1.5*KB_ERG_K/EV_ERG*T0*(1+HE_PER_H+e0)
    w=w0+r['photo_heat_eV_H']+r['CMB_eV_H']-r['thermal_work_eV_H']-sum(r[k] for k in cooling)-sum(x*y for x,y in zip(CHI,C))
    r['T_K']=w/(1.5*KB_ERG_K/EV_ERG*(1+HE_PER_H+e))
    assert max(abs(v) for v in audit_row(r).values())<2e-15
    # DR shares the HeII binding energy, not HeIII; wrong substitution is caught.
    r['escape_eV_H']+=(CHI[2]-CHI[1])*D
    if D>1e-8:
        with pytest.raises(ValueError,match='independent escaped'):audit_row(r)
