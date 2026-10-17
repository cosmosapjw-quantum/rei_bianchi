#!/usr/bin/env python3
"""Typed scientific gates for the selected P4/S2 bounded Rust reference."""
from pathlib import Path
import csv, json, subprocess, hashlib, math, sys
ROOT=Path(__file__).resolve().parents[1]
READ=lambda name:list(csv.DictReader((ROOT/name).open()))
rows=READ('evidence/p4_birth_clock_campaign.csv')
assert len(rows)==32, len(rows)
ref=READ('inputs/P3_POSITIVE_CAMPAIGN_32_ROWS.csv')
assert len(ref)==32, len(ref)
expected={(name,n,r) for name in ['flrw','bi_plus','bi_minus','bi_plus_fesc025']
          for n in ['8','16','32','64'] for r in ['p3_full_exposure','p4_positive_birth_phi']}
assert {(x['case'],x['nsteps'],x['representation']) for x in rows}==expected
cols=['T_final_K','survivors_com_m3','emitted_com_m3','absorbed_com_m3','HI_events_com3','HeI_events_com3','HeII_events_com3','D_events_com3']
for r in rows:
    for c in cols:
        assert math.isfinite(float(r[c])) and float(r[c])>=0,(r['case'],c)
    assert abs(float(r['survivors_com_m3'])+float(r['absorbed_com_m3'])-float(r['emitted_com_m3']))<=3e-10*float(r['emitted_com_m3'])
    assert float(r['max_energy_residual'])<3e-10
    assert int(r['cohorts'])==int(r['nsteps'])*384
old=[r for r in rows if r['representation']=='p3_full_exposure']
pairs=[]
for x in old:
    other=x['case'].replace('bi_plus_fesc025','bi_fesc025')
    y=next((r for r in ref if r['case']==other and r['nsteps']==x['nsteps'] and r['representation']=='positive_384'),None)
    assert y is not None
    for a,b in [('T_final_K','T_final_K'),('survivors_com_m3','photons_com_m3'),('emitted_com_m3','emitted_com_m3'),('absorbed_com_m3','absorbed_com_m3')]:
        z=float(x[a]);v=float(y[b]);pairs.append(abs(z-v)/max(abs(z),abs(v),1e-50))
assert max(pairs)<2e-14,max(pairs)
for case in {x['case'] for x in rows}:
    for n in ['8','16','32','64']:
        a=next(x for x in rows if x['case']==case and x['nsteps']==n and x['representation']=='p3_full_exposure')
        b=next(x for x in rows if x['case']==case and x['nsteps']==n and x['representation']=='p4_positive_birth_phi')
        assert float(b['survivors_com_m3'])>float(a['survivors_com_m3'])
        assert float(b['absorbed_com_m3'])<float(a['absorbed_com_m3'])
oracle=READ('evidence/p4_constant_opacity_oracle.csv')
assert len(oracle)==7
assert [int(x['nsteps']) for x in oracle]==[2,4,8,16,32,64,128]
errors=[]
for r in oracle:
    assert float(r['new_survivor_rel_error'])<5e-14
    assert float(r['old_number_relative_residual'])<3e-14
    assert float(r['new_number_relative_residual'])<3e-14
    errors.append(float(r['old_survivor_rel_error']))
assert all(a>b>0 for a,b in zip(errors,errors[1:])),errors
source=json.loads((ROOT/'inputs/P3_OWNER_SOURCE_IDENTITY.json').read_text())
src=ROOT/'rust/rei_iso_couple_p4_s2/owner_src'
for filename,blob in source['owner_blobs'].items():
    p=src/filename
    got=subprocess.check_output(['git','hash-object',str(p)],text=True).strip()
    assert got==blob,(filename,got,blob)
original=ROOT/'rust/rei_iso_couple_p4_s2/src/positive_age.rs'
assert hashlib.sha256(original.read_bytes()).hexdigest()=='4c377bb568d4483eff5c73127f825e15e4f0cf6663e32e6e4ec4bb5eabe1252a'
summary={
 'verdict':'PASS_SCOPED_P4_S2_POSITIVE_BIRTH_CLOCK',
 'test_scope':'Rust P3 + P4 inherited/new unit tests and 32 source-native matched rows',
 'total_rows':len(rows),'constant_opacity_rows':len(oracle),
 'native_owner_git_blob_verified':len(source['owner_blobs']),
 'p3_original_native_result_max_rel_difference':max(pairs),
 'max_photon_relative_ledger':max(abs(float(x['survivors_com_m3'])+float(x['absorbed_com_m3'])-float(x['emitted_com_m3']))/float(x['emitted_com_m3']) for x in rows),
 'max_energy_relative_ledger':max(float(x['max_energy_residual']) for x in rows),
 'newborn_constant_opacity_relative_error_max':max(float(x['new_survivor_rel_error']) for x in oracle),
 'full_EoR_claim':'HOLD', 'global_coupled_second_order_claim':'NOT_ADMITTED',
}
print(json.dumps(summary,indent=2))
