#!/usr/bin/env python3
"""Construct 193 real BASS21 source-owned photon inputs for unmodified native REI IGM Rust point RHS.
Avoids new cosmological IVP and keeps all PR295 energy/source identity constraints.
"""
from __future__ import annotations
import csv, hashlib, json, zipfile, io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'source'/'PR295_FULL.zip'
PARENT_SHA='156cad079282f8418530d1b38af8a4cc44e0a8711ed9c9e23367fff4db3fb7e9'
PREFIX='REI_F4_REI_HHE_THERMAL_SOURCE_20261030/results/'
def input_bytes(name):
    if PARENT.is_file():
        assert hashlib.sha256(PARENT.read_bytes()).hexdigest()==PARENT_SHA, 'PR295 immutable source'
        with zipfile.ZipFile(PARENT) as z:return z.read(PREFIX+name)
    return (Path('/mnt/data/rei_f4_common_thermal_20261030/results')/name).read_bytes()
# immutable SHA256 values recorded by PR295, copied without changing source files
EXPECTED={
'HHE_IGM_THERMAL_193.csv':'46127f9bb5ea1e0ef407a1ad85f895a7ffbb46e6f0481200cb2e704e3f80de2f',
'HHE_IGM_EVENTS_579.csv':'a644826a59d9b2a90cae5e34789edd97bb22846bbe0d078f7f09197adb57176d'}
for p,digest in EXPECTED.items():
 assert hashlib.sha256(input_bytes(p)).hexdigest()==digest, f'wrong source {p}'
source=list(csv.DictReader(io.StringIO(input_bytes('HHE_IGM_THERMAL_193.csv').decode())))
events=list(csv.DictReader(io.StringIO(input_bytes('HHE_IGM_EVENTS_579.csv').decode())))
assert len(source)==193 and len(events)==579
FIELDS=['epoch','z','x','proper_elapsed_s','H_s','nHref_cm3','nHe4_cm3','T_K','T_CMB_K',
 'x_HII','x_HeII','x_HeIII', 'Gamma_HI_s','Gamma_HeI_s','Gamma_HeII_s',
 'heat_HI_erg_per_absorber_s','heat_HeI_erg_per_absorber_s','heat_HeII_erg_per_absorber_s',
 'expected_HII_dt_s','expected_HeII_dt_s','expected_HeIII_dt_s',
 'expected_photoevents_cm3_s','expected_photo_input_erg_cm3_s',
 'expected_thermal_erg_cm3_s','expected_binding_erg_cm3_s','expected_escape_erg_cm3_s',
 'expected_CMB_erg_cm3_s','expected_temperature_dt_K_s','expected_dNe_cm3_s',
 'expected_threshold_defect_erg_per_Href_s','ne_other_isotopes_cm3','nHref_over_nb']
rows=[]
for i,rr in enumerate(source):
 ev=events[3*i:3*i+3]
 assert int(rr['epoch'])==i and all(int(j['epoch'])==i for j in ev)
 assert [j['absorber'] for j in ev]==['H_I','He_I','He_II']
 nh=float(rr['nHref_cm3']);nhe=float(rr['nHe4_cm3'])
 ab=[nh*(1-float(rr['HII_fraction'])),
 nhe*(1-float(rr['HeII_fraction'])-float(rr['HeIII_fraction'])),
 nhe*float(rr['HeII_fraction'])]
 assert nh>0 and nhe>0 and all(a>=0 for a in ab)
 gamma=[float(j['source_BASS_native_photo_gamma_s']) for j in ev]
 eheat=[float(j['REI_point_primary_kinetic_erg_per_Href_s'])*nh for j in ev]
 heat=[e/a if a>0 else 0.0 for e,a in zip(eheat,ab)]
 for a,e,h,g in zip(ab,eheat,heat,gamma):
  assert abs(a*h-e)<=1e-50+1e-12*max(abs(e),abs(a*h))
  if g==0:assert h==0
 out=dict(zip(FIELDS,[i,rr['z'],rr['x'],rr['proper_elapsed_s'],rr['H_s'],rr['nHref_cm3'],rr['nHe4_cm3'],rr['T_original_K'],rr['T_CMB_external_K'],rr['HII_fraction'],rr['HeII_fraction'],rr['HeIII_fraction'],*gamma,*heat,
 rr['REI_source_translated_HII_fraction_dt_per_s'],rr['REI_source_translated_HeII_fraction_dt_per_s'],rr['REI_source_translated_HeIII_fraction_dt_per_s'],
 float(rr['REI_HHe_photon_photoevents_per_Href_s'])*nh, float(rr['REI_HHe_photo_input_erg_per_Href_s'])*nh,float(rr['REI_HHe_thermal_micro_erg_per_Href_s'])*nh,
 float(rr['REI_HHe_binding_micro_erg_per_Href_s'])*nh,float(rr['REI_HHe_escape_erg_per_Href_s'])*nh,float(rr['REI_HHe_cmb_exchange_erg_per_Href_s'])*nh,
 rr['REI_HHe_Tdot_point_K_s'],rr['REI_HHe_dNe_cm3_s'],rr['REI_BASS_ionization_threshold_source_defect_erg_per_Href_s'],rr['ne_omitted_isotopes_cm3'],rr['nHref_over_nb']]))
 # independent photon input from gamma and native per-species primary energy, using REI thresholds
 chi=[13.598434599702,24.587389011,54.41776];ev_erg=1.602176634e-12
 inp=sum(a*(h+g*c*ev_erg) for a,h,g,c in zip(ab,heat,gamma,chi))
 if abs(inp-float(out['expected_photo_input_erg_cm3_s']))>5e-8*max(abs(inp),abs(float(out['expected_photo_input_erg_cm3_s'])),1e-60):
  raise AssertionError('photo input huge mismatch epoch='+str(i))
 rows.append(out)
assert len(rows)==193
path=ROOT/'data/native_rei_igm_193_cases.csv';path.parent.mkdir(parents=True,exist_ok=True)
with path.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\n');w.writeheader();w.writerows(rows)
summary={'schema':'REI_F4_NATIVE_RUST_193_CASES_V1','epochs':len(rows),'event_rows':len(events),'source_archive_SHA256':'156cad079282f8418530d1b38af8a4cc44e0a8711ed9c9e23367fff4db3fb7e9',
 'original_source_SHA256':EXPECTED,'new_cases_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
 'H_range_s':[min(float(x['H_s']) for x in rows),max(float(x['H_s']) for x in rows)],'T_range_K':[min(float(x['T_K']) for x in rows),max(float(x['T_K']) for x in rows)],
 'photo_gamma_origin':'original BASS21; photo replaces rather than adds, no free duplicate source','thermal_model':'REI igm Rust source-translated PR295 comparison, pending native Rust CI check',
 'physics_gates':{'F4':'PARTIAL','production':'HOLD','DAG_working':'33/88','DAG_central':'28/88','DAG_fast':'4/7','new_IVP':0}}
(ROOT/'results/INPUT_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'rows':len(rows),'bytes':path.stat().st_size,'sha256':summary['new_cases_sha256'],'T_K':summary['T_range_K']},indent=2))
