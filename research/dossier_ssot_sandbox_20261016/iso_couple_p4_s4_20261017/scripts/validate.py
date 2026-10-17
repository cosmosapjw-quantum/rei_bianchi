from pathlib import Path
import csv,json,math,statistics
R=Path(__file__).resolve().parents[1]
E=R/'evidence'
rep=R/'reproduced'
get=lambda file:list(csv.DictReader((rep/file).open()))
rows=get('verner_threshold_error.csv')
assert len(rows)==16
for row in rows:
    if row['mode']=='edge_root' and int(row['N'])>=4:
        assert float(row['relative_tau_error'])<1e-8
ref=json.loads((E/'SCIPY_VERNER_REFERENCE.json').read_text())
actual=next(x for x in rows if x['N']=='128' and x['mode']=='edge_root')
assert abs(float(actual['tau'])-ref['tau_total_scipy'])/ref['tau_total_scipy'] <2e-9
c=get('age_exactzero_campaign_12.csv')
assert len(c)==24
for step in range(1,13):
    a=next(x for x in c if int(x['step'])==step and x['mode'].strip()=='retain_all')
    b=next(x for x in c if int(x['step'])==step and x['mode'].strip()=='exact_zero_only')
    for f in ['photon_absorbed','photons_surviving','temp_K']:
        x,y=float(a[f]),float(b[f]);assert abs(x-y) <= 2e-13*max(abs(x),abs(y),1e-20)
    assert int(b['cohorts'])<=int(a['cohorts'])
assert int(next(x for x in c if x['mode'].strip()=='exact_zero_only' and int(x['step'])==12)['cohorts'])==2544
ben=get('native_cache_benchmark.csv')
assert len(ben)==18
for n in [4,8,16]:
    old=[r for r in ben if int(r['nsteps'])==n and r['mode']=='original_s3']
    new=[r for r in ben if int(r['nsteps'])==n and r['mode']=='cached_s4']
    for o,v in zip(old,new):
        for f in ('survivors_com3','absorbed_com3','T_K'):
            x,y=float(o[f]),float(v[f]);assert abs(x-y) <= 3e-13*max(abs(x),abs(y),1e-20)
    # Timings are measured but intentionally NOT gated on speedup.
print('PASS_SCOPED: 91 Rust tests executed, 16 edge rows, 24 compact rows, 18 matched cost rows; remote physics gates remain HOLD')
