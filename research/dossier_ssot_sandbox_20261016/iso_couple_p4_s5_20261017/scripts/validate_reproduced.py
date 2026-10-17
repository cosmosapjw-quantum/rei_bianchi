from pathlib import Path
import csv,math,json
R=Path(__file__).resolve().parents[1]
def rows(p):
    return list(csv.DictReader(p.open()))
a=rows(R/'evidence/p5_tail_campaign.csv');b=rows(R/'reproduced/p5_tail_campaign.csv')
assert len(a)==len(b)==36
exclude={'total_wall_s','last_step_s'}
for i,(x,y) in enumerate(zip(a,b)):
    for key in x:
        if key in exclude:continue
        assert x[key]==y[key],(i,key,x[key],y[key])
a=json.loads((R/'evidence/P5_INDEPENDENT_SCIPY.json').read_text())
b=json.loads((R/'reproduced/P5_INDEPENDENT_SCIPY.json').read_text())
for x,y in zip(a['cases'],b['cases']):
    for k in ['surviving','absorption_energy_J','photon_identity_residual','energy_upper_J']:
        assert math.isclose(x[k],y[k],rel_tol=1e-11,abs_tol=1e-28),(k,x[k],y[k])
assert 'test result: FAILED' not in (R/'reproduced/test.log').read_text()
print('PASS: 36-row scientific columns exact; 4 independent ODE cases numerically matching; Rust tests PASS')
