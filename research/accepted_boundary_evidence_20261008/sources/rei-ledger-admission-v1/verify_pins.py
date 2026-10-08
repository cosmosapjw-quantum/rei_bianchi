import pathlib,json,hashlib
r=pathlib.Path(__file__).resolve().parent;base=r.parent/'rei-species-energy-sidecar-v1';proof=json.loads((base/'evidence/SOURCE_PIN_PROOF.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins=[]
for entry in proof['all_unchanged_files']+proof['planned_hook_changes_only']:
 p=base/entry['path'];h=sha(p);assert h==entry['after'];pins.append({'path':str(p),'sha256':h})
for rel,key in [('vendor/native-detailed/src/species_sidecar.rs','sidecar_sha256'),('tests/controls.rs','controls_sha256')]:
 p=base/rel;h=sha(p);assert h==proof[key];pins.append({'path':str(p),'sha256':h})
archives=[]
for name,expected in [('REI_EXTERNAL_ADAPTER_FIRST_SLICE_SOURCE_ONLY_20261007.zip','bc39ecc15366bb620f45f378a7eacc2b7a8cc0e2e14d2a151a34e48e9577745d'),('REI_SPECIES_ENERGY_SIDECAR_SOURCE_ONLY_20261007.zip','4700d68ffda7204656fbd57d80c56a60278afb9bf0d03d1cd9c697298e0acd3f')]:
 p=r.parent/name;h=sha(p);assert h==expected;archives.append({'path':str(p),'bytes':p.stat().st_size,'sha256':h,'unchanged':True})
assert len(pins)==70;assert sha(r/'src/ledger_sidecar.rs')==sha(r/'evidence/FINAL_GREEN_SOURCE.rs');green=(r/'logs/final-accepted-green.stdout').read_text();assert '15 passed; 0 failed' in green
mutants=json.loads((r/'evidence/MUTANTS.json').read_text());assert len(mutants)==14 and all(x['compiled']and x['assertion_RED']for x in mutants)
result={'archives':archives,'accepted_source_pins_verified':pins,'pin_count':len(pins),'new_source_sha256':sha(r/'src/ledger_sidecar.rs'),'new_tests_sha256':sha(r/'tests/ledger_sidecar.rs'),'restored_GREEN':15,'actual_assertion_RED':14,'new_provider_or_RHS_or_cosmology_evaluations':0,'full_scientific_admission':'HOLD','source_only_package_requires_sibling_species_archive':archives[1]['sha256']}
(r/'evidence/IMMUTABILITY_AND_SOURCE_PROOF.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items()if k!='accepted_source_pins_verified'},indent=2))
