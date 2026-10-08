import pathlib,json,hashlib
r=pathlib.Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=r.parent/'rei-ledger-admission-v1';proof=json.loads((old/'evidence/IMMUTABILITY_AND_SOURCE_PROOF.json').read_text());out=[]
for x in proof['accepted_source_pins_verified']:
 p=pathlib.Path(x['path']);h=sha(p);assert h==x['sha256'];out.append({'path':str(p),'sha256':h})
for rel,key in [('src/ledger_sidecar.rs','new_source_sha256'),('tests/ledger_sidecar.rs','new_tests_sha256')]:
 p=old/rel;h=sha(p);assert h==proof[key];out.append({'path':str(p),'sha256':h})
archives=[]
for name,expected in [('REI_EXTERNAL_ADAPTER_FIRST_SLICE_SOURCE_ONLY_20261007.zip','bc39ecc15366bb620f45f378a7eacc2b7a8cc0e2e14d2a151a34e48e9577745d'),('REI_SPECIES_ENERGY_SIDECAR_SOURCE_ONLY_20261007.zip','4700d68ffda7204656fbd57d80c56a60278afb9bf0d03d1cd9c697298e0acd3f'),('REI_CANONICAL_LEDGER_ADMISSION_SOURCE_ONLY_20261008.zip','74330ac71267f00afb05c21c4ea7d9a9dc9138b11dd2d0c82c7368960cc28aaf')]:
 p=r.parent/name;h=sha(p);assert h==expected;archives.append({'path':str(p),'sha256':h,'bytes':p.stat().st_size,'unchanged':True})
assert '1 passed; 0 failed'in(r/'logs/real-native-caller-green.stdout').read_text();counts=json.loads((r/'evidence/REAL_NATIVE_RECEIVER_REPORT.json').read_text());assert counts['real_native_trials']==2 and counts['total_actual_rhs']==72 and counts['total_actual_provider_calls']==234 and counts['added_caller_rhs']==0 and counts['added_caller_provider_calls']==0
receipt={'unchanged_dependency_pins':out,'pin_count':len(out),'unchanged_archives':archives,'new_caller_sha256':sha(r/'src/lib.rs'),'new_test_sha256':sha(r/'tests/real_native_receiver.rs'),'real_trial_test_GREEN':1,'earlier_15_controls_rerun':False,'actual_native_counts':counts,'production_receiver_adoption':False,'physical_admission':'HOLD'}
(r/'evidence/IMMUTABILITY_AND_REAL_CALLER_PROOF.json').write_text(json.dumps(receipt,indent=2));print(json.dumps({k:v for k,v in receipt.items()if k!='unchanged_dependency_pins'},indent=2))
