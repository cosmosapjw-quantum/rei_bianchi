#!/usr/bin/env python3
"""Native-step crossing localization, distinct from trajectory error."""
import argparse,csv,gzip,hashlib,json,time
from pathlib import Path
UNIT=Path(__file__).resolve().parents[1];REPO=UNIT.parents[1]
T1=REPO/'research/rei_ax11_t1_wave_20261116';YEAR=31557600.

def main():
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);out=p.parse_args().output
    if out.exists():raise FileExistsError(out)
    tic=time.monotonic();cpu=time.process_time();out.mkdir()
    data={}
    for case,expected in [('ZERO','40e536713e4cd8d872060a1213e3caaa21af8dab0bb48257bde747aab3e7c2f2'),('PLUS','90d31e9acd3eba8286ad34fcdcd45696c35c0ce41b1500f2d751d0edddf7b91f')]:
        f=T1/f'native_inputs/{case}_sample_brackets.json.gz'
        assert hashlib.sha256(f.read_bytes()).hexdigest()==expected
        data[case]=json.load(gzip.open(f,'rt'))
    with (UNIT/'results_v1/paired_milestone_shifts.csv').open() as f:point={r['x_HII_level']:r for r in csv.DictReader(f)}
    intervals=[]
    for level in ['0.1','0.5','0.9']:
        bounds={}
        for case,d in data.items():
            m=d['milestones'][level];lo,hi=m['rows'];h={k:i for i,k in enumerate(d['headers'])}
            assert m['upper_row']==m['lower_row']+1
            assert lo[h['x_HII']]<float(level)<=hi[h['x_HII']]
            assert lo[h['time_s']]<hi[h['time_s']]
            bounds[case]=(lo[h['time_s']],hi[h['time_s']])
        zlo,zhi=bounds['ZERO'];plo,phi=bounds['PLUS']
        lower=(plo-zhi)/YEAR;upper=(phi-zlo)/YEAR;best=float(point[level]['T1_PLUS_minus_ZERO_years'])
        assert lower<=best<=upper
        intervals.append({'x_HII_level':level,'T1_pair_point_years':best,
            'native_step_pair_lower_years':lower,'native_step_pair_upper_years':upper,
            'interval_width_years':upper-lower,'excludes_zero_on_saved_T1_native_steps':not lower<=0<=upper,
            'T0_pair_point_years':float(point[level]['T0_PLUS_minus_ZERO_years']),
            'D01_pair_point_years':float(point[level]['D01_paired_years']),
            'D01_point_relative_to_T1_pair':float(point[level]['D01_paired_years'])/abs(best),
            'ZERO_native_lower_time_s':zlo,'ZERO_native_upper_time_s':zhi,
            'PLUS_native_lower_time_s':plo,'PLUS_native_upper_time_s':phi})
    with (out/'NATIVE_CROSSING_INTERVALS.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(intervals[0]));w.writeheader();w.writerows(intervals)
    with (UNIT/'results_v1/endpoint_inventory_D01.csv').open() as f:delta={r['quantity']:r for r in csv.DictReader(f)}
    quantities=['x_HII','photo_events_0_per_H','RR_events_0_per_H','photon_n_per_H','photon_u_eV_per_H','escape_U_eV_per_H','temperature_K']
    contrast={k:{'T0_ZERO':float(delta[k]['T0_ZERO']),'T1_ZERO':float(delta[k]['T1_ZERO']),
                 'D01_ZERO':float(delta[k]['D01_ZERO']),
                 'D01_relative_to_T1_ZERO':float(delta[k]['D01_ZERO'])/abs(float(delta[k]['T1_ZERO']))} for k in quantities}
    result={'status':'SOURCE_QUALIFIED_NATIVE_STEP_LOCALIZATION','intervals':intervals,'endpoint_history_contrast':contrast,
      'interpretation':'For each saved T1 trajectory a crossing contained in its native adjacent step has the displayed paired time interval. All signs here are discretized T1 facts, conditional on within-step continuous crossing.',
      'limitations':['Not a rigorous enclosure of the true continuous solution','A first-upward native row pair cannot exclude unresolved intra-step recrossings','T0 native brackets are not in this consumer: no D01 interval fabricated','A few-year D01 change of paired point estimates is not a few-year timing error bound','D12 and separate energy/angular refinements remain absent'],
      'new_evolution':0,'new_completed_nodes':0,'DAG':'10/17;28/88',
      'execution':{'CPU_s':time.process_time()-cpu,'wall_s':time.monotonic()-tic,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    (out/'LOCALIZATION.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':result['status'],'intervals':intervals,'execution':result['execution']}))
if __name__=='__main__':main()
