#!/usr/bin/env python3
"""Small adversarial checks of assembly integrity, not science tests."""
import copy,importlib.util,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('assemble',ROOT/'assembly/assemble.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
d=json.loads((ROOT/'assembly/DAG.json').read_text());results={'unchanged_authority':not m.validate(d,ROOT)}
for case in ['cycle','missing_source','claim_leap','duplicate_id']:
 x=copy.deepcopy(d)
 if case=='cycle':x['nodes'][0]['local_dependencies']=[x['nodes'][0]['id']]
 if case=='missing_source':x['nodes'][0]['authority']='absent_source.json'
 if case=='claim_leap':x['nodes'][0]['contract']['status']='UNSCOPED_ADMITTED'
 if case=='duplicate_id':x['nodes'].append(copy.deepcopy(x['nodes'][0]))
 results[case]=bool(m.validate(x,ROOT))
print(json.dumps(results));assert all(results.values())
