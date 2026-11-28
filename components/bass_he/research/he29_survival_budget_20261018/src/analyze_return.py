"""Read completed HE28 native records; zero solver calls and no result mutation."""
from pathlib import Path
import json,math,hashlib

ROOT=Path(__file__).resolve().parents[1]

def load_records(root):
    root=Path(root); records={}
    for p in sorted((root/'study').glob('*/RESULT.json')):
        d=json.loads(p.read_text());r=d['results']['transport']
        if d['status']!='SCOPED_NATIVE_COMPLETED':raise ValueError('HE29_INCOMPLETE_PARENT')
        ident=json.loads((p.parent/'IDENTITY.json').read_text())
        s=ident['spec'];key=(s['strips'],ident['n'])
        if key in records or s['m']!=8 or s['angles']!=4 or s['q']!=0 or ident['source_table_nodes']!=512:
            raise ValueError('HE29_PARENT_DESIGN')
        if not all(math.isfinite(x) for x in (r['temperature_K'],r['number_defect'],r['energy_defect_ev'])):
            raise ValueError('HE29_NONFINITE_PARENT')
        records[key]={'T':r['temperature_K'],'record':d,'identity':ident,
                      'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    if set(records)!={(r,n) for r in (2,4,8) for n in (32,64)}:raise ValueError('HE29_MISSING_CASE')
    return records

def audit(root=ROOT/'inputs'):
    rr=load_records(root)
    for r in (2,4,8):
        if rr[r,32]['record']['source_table_sha256']!=rr[r,64]['record']['source_table_sha256']:
            raise ValueError('HE29_TABLE_CHANGED_WITH_TIME')
    time={str(r):rr[r,64]['T']-rr[r,32]['T'] for r in (2,4,8)}
    spectral=[]
    for a,b in ((2,4),(4,8)):
        d32=rr[b,32]['T']-rr[a,32]['T'];d64=rr[b,64]['T']-rr[a,64]['T']
        spectral.append({'r_from':a,'r_to':b,'delta_T_n32_K':d32,'delta_T_n64_K':d64,
          'mixed_difference_K':d64-d32,'sign_changes':d32*d64<0,
          'interpretation':'finite mixed sensitivity, not an error bound or observed order'})
    pilot=json.loads((Path(root)/'pilot/m4_r2_n16/RESULT.json').read_text())['results']
    relative=max(abs(a-b)/max(abs(b),1e-300) for a,b in zip(pilot['transport']['gas_final'][:3],pilot['Radau']['gas_final'][:3]))
    absolute=max(abs(a-b) for a,b in zip(pilot['transport']['gas_final'][:3],pilot['Radau']['gas_final'][:3]))
    return {'schema':'he29.native_return_audit.v1','native_calls_this_audit':0,
      'completed_parent_study_cases':len(rr),'time_T_n64_minus_n32_K':time,
      'spectral_mixed_differences':spectral,'pilot_fraction_error_absolute':absolute,
      'pilot_fraction_error_max_relative':relative,
      'fraction_label_note':'parent report says relative; stored gate compares absolute fractions; no tolerance changed',
      'max_number_defect_per_H':max(abs(x['record']['results']['transport']['number_defect']) for x in rr.values()),
      'max_energy_defect_eV_per_H':max(abs(x['record']['results']['transport']['energy_defect_ev']) for x in rr.values()),
      'new_reference_required':'same-r/same-table Radau-DOP853 at m8,r2/4/8; old m4,r2 pilot is not a cross-r error estimate',
      'spectral_convergence':'HOLD','parent_files_sha256':{f'r{r}_n{n}':v['sha256'] for (r,n),v in rr.items()}}
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--input-root',default=str(ROOT/'inputs'));a=ap.parse_args()
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(audit(a.input_root),f,indent=2,allow_nan=False)
    print(p.read_text())
