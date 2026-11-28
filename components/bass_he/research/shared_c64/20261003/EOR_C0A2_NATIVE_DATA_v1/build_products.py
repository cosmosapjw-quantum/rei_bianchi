"""Rebuild products into an explicitly new output directory."""
import argparse,json,sys
from pathlib import Path
from bass_he_liu import load_dataset
from bass_he_liu.products import audit,write_json_create_only,write_long_csv_create_only

p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=False)
d=load_dataset(a.root/'raw',a.root/'provenance/INPUT_LOCK.json')
catalog=json.loads((a.root/'provenance/parent_CHANNEL_ENERGY_COVERAGE.json').read_text())
r=audit(d,catalog)
write_json_create_only(a.out/'LIU2024_NATIVE_DATA.json',d.to_dict())
write_json_create_only(a.out/'NATIVE_DATA_AUDIT.json',r)
write_json_create_only(a.out/'CHANNEL_ENERGY_COVERAGE.json',r['catalog_coverage'])
write_long_csv_create_only(a.out/'LIU2024_NATIVE_SAMPLES.csv',d)
derived=[]
for x in r['catalog_coverage']:
 if x['status']=='DERIVED_EXACT_SUM':
  derived.append({'id':x['id'],'source_kind':'DERIVED_NOT_ORIGINAL_COLUMN',
                  'samples':[d.sample(x['id'],e,scope='payload_domain') for e in d.available_energies(x['id'])]})
write_json_create_only(a.out/'DERIVED_SHELL_SUMS.json',derived)
print(json.dumps({'status':'BUILT_SOURCE_NATIVE_PRODUCTS','values':r['native_values'],
 'channels':r['raw_channels'],'missing':r['explicit_missing_values'],'physical_certificate':False}))
