"""Reconstruct only the scalar absorbed photon-energy total; no B_i inference."""
from __future__ import annotations
import csv,json,sys,os
from pathlib import Path
from fractions import Fraction as F
from e11.observer_alias import f64,load_mode_csv
from e11.budget_observability import reconstruct_total_absorption
MODES=('OFF','KF','GM')


def run(e10:Path,e7:Path,out:Path):
    if out.exists():raise FileExistsError('FRESH_OUTPUT_ONLY')
    out.mkdir(parents=True)
    result={'scope':'scalar photon absorption total only; NOT individual energy moments',
      'comparison_semantics':'source f64 exact rationals; equal within measured roundoff; no inferred missing fields',
      'modes':{},'source_fields_missing':['BH','BY','BZ','bindMicro','thermalMicro'],
      'full_stored_B_vectors_available_in_pinned_E7_but_not_E10_owner_native':True}
    rows=[]
    for m in MODES:
        owner=load_mode_csv(e10/f'full_{m}/OWNER_NATIVE_41.csv',step_column='step_index_unavailable')
        hist=load_mode_csv(e7/f'data/histories/{m}_N384_P512_O4.csv')
        worst=(F(0),-1,F(0),F(0))
        for i,(x,y) in enumerate(zip(owner,hist)):
            v=reconstruct_total_absorption(f64(x['emitted_E']),f64(x['Eactive']),f64(x['out_E']),f64(x['redshift_E']))
            B=sum((f64(y[k]) for k in ('BH','BY','BZ')),F(0))
            diff=v-B
            denom=max(abs(B),F(10)**-60)
            rel=abs(diff)/denom
            if rel>worst[0]:worst=(rel,i,v,B)
            rows.append({'mode':m,'step':i,'Btotal_reconstructed_erg_per_H':str(float(v)),
                         'Bsum_from_E7_stored_erg_per_H':str(float(B)),
                         'stored_float_diff_erg_per_H':str(float(diff)),
                         'difference_relative_to_Bsum':str(float(rel))})
        result['modes'][m]={'worst_relative':float(worst[0]),'step':worst[1],
            'reconstructed_at_worst':float(worst[2]),'stored_Bsum_at_worst':float(worst[3]),
            'last_saved_B_species_erg_per_H':{k:float(f64(hist[-1][k])) for k in ('BH','BY','BZ')},
            'last_bindMicro':float(f64(hist[-1]['bindMicro'])),
            'last_thermalMicro':float(f64(hist[-1]['thermalMicro']))}
    with (out/'B_TOTAL_ONLY.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);f.flush();os.fsync(f.fileno())
    with (out/'BUDGET_RESULT.json').open('x') as f:
        json.dump(result,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    return result

if __name__=='__main__':
    if len(sys.argv)!=4:raise SystemExit('USAGE python -m e11.run_budget E10_DATA E7_DATA FRESH_OUTPUT')
    v=run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
    print(json.dumps(v['modes'],sort_keys=True))
