"""Compare interpolated V5 rates and cgs point terms with actual PR150 Rust."""
from __future__ import annotations
import csv
import json
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'donor'))
from native_interface import point_terms
from rate_table import CaseARates, COLUMNS
from study_v5 import GAS, H0, N_STAR, T0, rays


def relative(a,b):
    return abs(a-b)/max(abs(b),1e-300)


def run(crate:Path):
    provider=CaseARates()
    native=crate/'target/release/examples'
    rate_csv=HERE/'native_owner_heldout_121.csv'
    with rate_csv.open('w') as f:
        subprocess.run([native/'lrs_v5_native_rates','--loggrid','10000','24000','121'],
                       check=True,stdout=f)
    deviations=[]
    with rate_csv.open() as f:
        for row in csv.DictReader(f):
            got=provider(float(row['T_K']))
            deviations.extend(relative(float(a),float(row[key]))
                              for a,key in zip(got,COLUMNS))
    point=point_terms(rays(0.),GAS,.02,N_STAR,H0,T0,provider)
    args=[point['nh_cm3'],point['nhe_cm3'],H0,T0,
          *point['gamma_s'],*point['heat_erg_per_absorber_s']]
    raw=subprocess.run([native/'lrs_v5_native_point',*(f'{v:.17e}' for v in args)],
                       capture_output=True,text=True,check=True)
    (HERE/'native_point_stdout.csv').write_text(raw.stdout)
    output={r[0]:tuple(map(float,r[1:])) for r in csv.reader(raw.stdout.splitlines())}
    expected={'photo':point['photo_events_cm3_s'],
              'rr':point['rr_events_cm3_s'],
              'dr':(point['dr_HeII_events_cm3_s'],),
              'rr_cool':point['rr_cooling_erg_cm3_s'],
              'dr_cool':(point['dr_HeII_cooling_erg_cm3_s'],),
              'photo_input':(point['photo_input_erg_cm3_s'],),
              'selected_thermal':(point['selected_thermal_micro_erg_cm3_s'],),
              'selected_binding':(point['selected_binding_micro_erg_cm3_s'],),
              'selected_escape':(point['selected_escape_erg_cm3_s'],)}
    diffs={k:max(relative(a,b) for a,b in zip(output[k],values))
           for k,values in expected.items()}
    report={'owner_rate_grid_points':121,'owner_rate_values_compared':len(deviations),
            'max_rate_relative_error':max(deviations),
            'max_point_relative_errors':diffs,'point_x':.02,
            'point_T_K':T0,'point_n_star_cm3':N_STAR,
            'point_H_s':H0,'native_raw':str(native)}
    (HERE/'native_comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    if max(deviations)>2e-7 or max(diffs.values())>2e-7:
        raise AssertionError(report)
    return report


if __name__=='__main__':
    print(json.dumps(run(Path(sys.argv[1]).resolve()),indent=2))
