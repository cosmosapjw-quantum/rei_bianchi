"""Verify literal transcription identity only; no physics solve, unit conversion or sums.
Usage: python verify_source_cells.py --source-root /path/to/immutable_v3
Prints a JSON record to stdout; redirect to a new evidence file if desired.
PDF cells are compared with preserved visual/two-parser transcription records, not
claimed to be independently re-extracted by this verifier.
"""
from pathlib import Path
import argparse,csv,json,hashlib,collections
from decimal import Decimal

def readj(p):return json.loads(p.read_text())
def check(condition,message):
 if not condition:raise ValueError(message)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-root',required=True,type=Path);args=ap.parse_args()
 b=Path(__file__).resolve().parents[1];sources=readj(b/'SOURCE_MANIFEST.json')['files']
 for s in sources:
  data=(args.source_root/s['path_relative_to_immutable_v3']).read_bytes()
  check(hashlib.sha256(data).hexdigest()==s['sha256'],'source hash '+s['id'])
  check(len(data)==s['bytes'],'source bytes '+s['id'])
 sm={s['id']:s for s in sources};rows=list(csv.DictReader((b/'EXACT_SOURCE_CELLS.csv').open(encoding='utf-8-sig')))
 matrix=list(csv.DictReader((b/'BENCHMARK_MATRIX.csv').open(encoding='utf-8-sig')))
 check(len(matrix)==13 and len({r['source_id'] for r in matrix})==13,'matrixcount/uniqueness')
 check((b/'BENCHMARK_MATRIX.csv').read_bytes()==(b.parent/'BASS_HE_BENCHMARK_MATRIX.csv').read_bytes(),'rootmatrixcopy')
 expected_counts={'D-LIU24-1':195,'D-LIU24-2':134,'D-LIU24-3':232,'D-LIU24-4':182,'P03':9,'P04':63,'P08':16,'P09':300}
 check(dict(collections.Counter(r['source_id'] for r in rows))==expected_counts,'cell counts')
 keys=set();grids=readj(b/'SCIENCEDB_EXACT_GRID_CHECK.json')['grids'];raw={}
 for sid in expected_counts:
  if sid.startswith('D-LIU'):
   raw[sid]=list(csv.reader((args.source_root/sm[sid]['path_relative_to_immutable_v3']).open(encoding='utf-8-sig')))
 p03=readj(b/'evidence/P03_verified_cells.json')['rows']
 p04={(r['row_label_native'],c):v for r in readj(b/'evidence/P04_A3_verified_cells.json')['rows'] for c,v in r['values'].items() if v is not None}
 p08={(r['E_alpha_keV']+'keV;'+str(r['basis_states'])+'states',c):r[c] for r in readj(b/'evidence/P08_verified_cells.json')['native_rows'] for c in ['1s','2s','2p','3s','3p','3d','beyond_3d','All']}
 p09={}
 for t in range(25,31):
  for rr in readj(b/f'evidence/P09_table{t}.json')['rows']:
   for c in rr['cells']:p09[(str(t),rr['velocity_token'],c['final_subshell'])]=(c['value_token'],c['source_convergence_token'])
 for r in rows:
  sid=r['source_id'];key=tuple(r[x] for x in ['source_id','table','source_row','source_column']);check(key not in keys,'duplicatecell');keys.add(key)
  check(r['source_sha256']==sm[sid]['sha256'],'cell sourcehash')
  check(r['source_path']==sm[sid]['path_relative_to_immutable_v3'],'cell sourcepath')
  check(all(r[k]=='NOT_RUN' for k in ['interpolation','frame_conversion','new_shell_sum']),'forbiddenoperation')
  check(r['value_token']!='','blanknotnumeric')
  if sid.startswith('D-LIU'):
   line=int(r['source_row'])-1;col=int(r['source_column'].split(':')[0])-1
   ec=next(g['energy_column_zero_based'] for g in grids if g['source_id']==sid and col in g['observable_columns_zero_based'])
   check(raw[sid][line][col].strip()==r['value_token'],'rawvalue')
   check(raw[sid][line][ec].strip()==r['energy_token'],'rawenergy')
   check(Decimal(r['energy_token']) not in [Decimal('5'),Decimal('0.5')],'unexpectedrequestedenergy')
   check('UNRESOLVED' in r['cross_section_unit'],'unresolvedunits')
  elif sid=='P03':check(p03[r['energy_token']]==r['value_token'] and r['energy_unit']=='eV','P03record')
  elif sid=='P04':
   check(p04[(r['source_row'],r['source_column'])]==r['value_token'],'P04record')
   check(r['energy_token']=='5' and r['energy_unit']=='keV/u','P04nativeenergy')
   check('NOT_EXPLICIT' in r['energy_frame'] and 'cross-reference' in r['target_initial_state'],'P04claimceiling')
  elif sid=='P08':
   check(p08[(r['source_row'],r['source_column'])]==r['value_token'],'P08record')
   check(r['energy_token']=='20' and r['energy_unit']=='keV','P08nativeenergy')
  elif sid=='P09':check(p09[(r['table'],r['velocity_token'],r['source_column'])]==(r['value_token'],r['uncertainty_token']),'P09record')
 for g in grids:
  tokens=[]
  for r in raw[g['source_id']][1:]:
   k=g['energy_column_zero_based']
   if len(r)>k and r[k].strip():tokens.append(r[k].strip())
  check(tokens==g['native_tokens'],'grididentity')
 check(not any(r['source_id'].startswith('D-IAEA') for r in rows),'wrongprojectile')
 print(json.dumps({'status':'PASS','scope':'transcription integration and source bytes;not physics or independent PDF re-extraction','source_files_verified':len(sources),'cross_section_value_cells':len(rows),'by_source':expected_counts,'P09_convergence_tokens':300,'matrix_rows':len(matrix),'source_native_tokens_preserved':True,'no_new_cross_sections_computed':True,'no_interpolation_or_new_sums':True,'global_authority_closed':False},indent=2))
if __name__=='__main__':main()
