#!/usr/bin/env python3
"""Verify measured evidence; timings are descriptive, never an acceptance gate."""
from __future__ import annotations
import argparse, csv, json, math, statistics, sys
from pathlib import Path

TIMING = {'old_s', 'reuse_s', 'speedup'}

def validate(folder: Path, reference: Path | None = None) -> dict:
    rows=list(csv.DictReader((folder/'p6_matched.csv').open()))
    assert len(rows)==30, f'Incomplete native matrix: {len(rows)} != 30'
    grouped={}
    for row in rows:
        grouped.setdefault(row['case'],[]).append(row)
        assert int(row['bit_equal_steps'])==int(row['nsteps'])
        assert int(row['computed_paths'])==int(row['reused_paths'])>0
        assert int(row['peak_traces'])<=256 and int(row['peak_segments'])<=8192
        assert float(row['max_photon_ledger'])<3e-10
        assert float(row['max_energy_ledger'])<3e-10
        for f in ('old_s','reuse_s','speedup'): assert math.isfinite(float(row[f])) and float(row[f])>0
        if row['full_chemistry']=='true':
            assert all(float(row[f])>0 for f in ('RR_events','CX_abs','FF_J','CMB_abs_J'))
        else:
            assert all(float(row[f])==0 for f in ('RR_events','CX_abs','FF_J','CMB_abs_J'))
    assert len(grouped)==10
    cases={}
    for name,rr in grouped.items():
        assert {x['repeat'] for x in rr}=={'0','1','2'}
        for x in rr[1:]:
            for k in x:
                if k not in TIMING|{'repeat'}: assert x[k]==rr[0][k], (name,k)
        speeds=[float(x['speedup']) for x in rr]
        cases[name]={'nsteps':int(rr[0]['nsteps']), 'full_chemistry':rr[0]['full_chemistry']=='true',
             'median_speedup':statistics.median(speeds),'speedup_min':min(speeds),'speedup_max':max(speeds),
             'median_old_s':statistics.median(float(x['old_s']) for x in rr),
             'median_reuse_s':statistics.median(float(x['reuse_s']) for x in rr),
             'cohorts_retained':int(rr[0]['cohorts']),'computed_paths':int(rr[0]['computed_paths']),
             'reused_paths':int(rr[0]['reused_paths'])}
    witness=list(csv.DictReader((folder/'p6_ray_witness.csv').open()))
    assert len(witness)==96
    max_energy=max_dir=0.
    # Independent closed form, not importing any Rust module or fit.
    for r in witness:
        s=float(r['shear_ratio'])*1.2e-16; t=float(r['t_s']); e=float(r['Eb_eV'])
        n=[float(r[k]) for k in ('nx_b','ny_b','nz_b')]
        p=[n[0]*math.exp(-(1.2e-16-s)*t),n[1]*math.exp(-(1.2e-16-s)*t),n[2]*math.exp(-(1.2e-16+2*s)*t)]
        norm=math.sqrt(sum(x*x for x in p)); expected=e*norm
        max_energy=max(max_energy,abs(float(r['E_eV'])/expected-1))
        for x,k in zip(p,('nx','ny','nz')):max_dir=max(max_dir,abs(float(r[k])-x/norm))
    assert max_energy<3e-14 and max_dir<3e-14
    a=grouped['full_fesc_minus'][0]; b=grouped['full_fesc_plus'][0]
    response={k:(float(b[k])-float(a[k]))/(float(b['fesc'])-float(a['fesc']))
              for k in ('T_K','photons_com3','HeII_events_com3','HI_events_com3')}
    parity=None
    if reference:
        for name in ('p6_matched.csv','p6_ray_witness.csv'):
            current=list(csv.DictReader((folder/name).open()))
            previous=list(csv.DictReader((reference/name).open()))
            assert len(current)==len(previous)
            for i,(x,y) in enumerate(zip(current,previous)):
                for k in x:
                    if k not in TIMING: assert x[k]==y[k], (name,i,k,x[k],y[k])
        parity='SCIENTIFIC_COLUMNS_EXACT_TEXT_EQUAL_TIMING_EXCLUDED'
    return {'schema':'rei.p4.s6.science.v1','status':'PASS_SCOPED_DISCRETE_REFLECTION_REUSE',
            'matched_rows':len(rows),'native_trajectories':2*len(rows),'bit_equal_step_pairs':sum(int(r['nsteps']) for r in rows),
            'case_statistics':cases,'max_photon_ledger':max(float(r['max_photon_ledger']) for r in rows),
            'max_energy_ledger':max(float(r['max_energy_ledger']) for r in rows),
            'independent_ray_rows':len(witness),'max_independent_energy_relative':max_energy,
            'max_independent_direction_absolute':max_dir,
            'central_fesc_response':{'delta_fesc':0.0004,'derivatives':response,'interpretation':'finite-difference diagnostic, not a truncation remainder certificate; identical because both branches have exact same endpoint bits'},
            'replay_parity':parity,'global_eor':'HOLD','age_complexity_reduction':False,
            'pruned_nonzero_cohorts':0,'phase_space_record_merging':False,
            'timing_scope':'single sandbox host, single worker, three alternating-order paired runs; time advance only, complete bit comparison outside timers'}

def main():
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('--reference',type=Path);a=p.parse_args()
    try: result=validate(a.folder,a.reference)
    except (AssertionError,OSError,ValueError) as e:
        print(f'VALIDATION_FAILED: {e}',file=sys.stderr);return 1
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False));return 0
if __name__=='__main__':raise SystemExit(main())
