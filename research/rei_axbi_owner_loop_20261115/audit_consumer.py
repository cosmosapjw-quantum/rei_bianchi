#!/usr/bin/env python3
"""Same-author adversarial audit, independent scalar reader/interpolator.

Does not import the production reducer. Keeps source-evolution accuracy open.
"""
from array import array
from bisect import bisect_right
import argparse
import csv
import gzip
import json
import math
from pathlib import Path
import time

import mpmath as mp

HERE=Path(__file__).resolve().parent
FHE=.2454/(4*(1-.2454))
CS=29979245800.0*6.6524587051e-25
YEAR=31557600.
FIELDS=['x_HI','x_HII','x_HeI','x_HeII','x_HeIII','xe_per_H','temperature_K']


def need(condition, message):
    if not condition:raise RuntimeError(message)


def scalar_interp(x,xs,ys):
    need(xs[0] <= x <= xs[-1], 'AUDIT_EXTRAPOLATION')
    if x==xs[-1]:return ys[-1]
    j=max(0,bisect_right(xs,x)-1)
    f=(x-xs[j])/(xs[j+1]-xs[j])
    return (1-f)*ys[j]+f*ys[j+1]


def read_actual(path):
    names=['ln_a','time_s','ne_proper_cm3']+FIELDS
    out={k:array('d') for k in names};mil={};prev=None;charge=0.;tau_terms=[]
    with Path(path).open(newline='') as f:
        for i,row in enumerate(csv.DictReader(f)):
            values={k:float(row[k]) for k in FIELDS if k!='xe_per_H'}
            t=float(row['time_s']);a=float(row['a']);ne=float(row['ne_proper_cm3']);nh=float(row['nH_proper_cm3'])
            values.update(ln_a=math.log(a),time_s=t,ne_proper_cm3=ne,xe_per_H=ne/nh)
            e=values['x_HII']+FHE*(values['x_HeII']+2*values['x_HeIII'])
            charge=max(charge,abs(ne/nh-e))
            if prev is not None:
                need(t>prev['time_s'] and values['ln_a']>prev['ln_a'],'AUDIT_NATIVE_ORDER')
                tau_terms.append(CS*(ne+prev['ne_proper_cm3'])*(t-prev['time_s'])/2)
                for level in (.1,.5,.9):
                    if level not in mil and prev['x_HII']<level<=values['x_HII']:
                        frac=(level-prev['x_HII'])/(values['x_HII']-prev['x_HII'])
                        ll=(1-frac)*prev['ln_a']+frac*values['ln_a']
                        tt=(1-frac)*prev['time_s']+frac*t
                        mil[level]={'lower_row':i-1,'time_s':tt,'zbar':math.exp(-ll)-1}
            for k in names:out[k].append(values[k])
            prev=values
    need(charge<=1e-12,'AUDIT_CHARGE')
    return out,mil,math.fsum(tau_terms),charge


def high_precision_clock(q,a):
    mp.mp.dps=60
    ai=mp.mpf(1)/21;h0=mp.mpf('67.4')*100000/mp.mpf('3.0856775814913673e24')
    om,orr=mp.mpf('.315'),mp.mpf('.000092');ol=1-om-orr
    def h(aa):return h0*mp.sqrt(orr/aa**4+om/aa**3+ol)
    qi=mp.mpf(str(q));hi=h(ai)
    def difference(u):
        aa=mp.exp(u);hf=h(aa);s=qi*hi*(ai/aa)**3
        # Deliberately independent expression: high-precision reciprocal subtraction.
        return 1/mp.sqrt(hf*hf+s*s)-1/hf
    return mp.quad(difference,[mp.log(ai),mp.log(mp.mpf(str(a)))])


def main(root):
    started=time.monotonic()
    manifest=json.loads((HERE/'INPUT_MANIFEST.json').read_text())
    summary=json.loads((HERE/'results/SUMMARY.json').read_text())
    originals={};milestones={};tau={};charge={}
    for spec in manifest['cases']:
        case=spec['id']
        originals[case],milestones[case],tau[case],charge[case]=read_actual(Path(root)/spec['relative_input'])
        need(len(originals[case]['time_s'])==spec['rows'],'AUDIT_ROW_COUNT')
    milestone_errors={'time_s':0.,'zbar':0.}
    with (HERE/'results/milestones.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            own=milestones[r['case']][float(r['x_HII_level'])]
            need(own['lower_row']==int(r['lower_row']),'AUDIT_FIRST_CROSSING_BRACKET')
            for k in milestone_errors:milestone_errors[k]=max(milestone_errors[k],abs(own[k]-float(r[k])))
    need(milestone_errors['time_s']<=32 and milestone_errors['zbar']<1e-12,'AUDIT_MILESTONE_DIFFERENCE')
    errors={k:0. for k in FIELDS};rows_checked=0;coordinate_error=0.
    ref=originals['ZERO']
    with gzip.open(HERE/'results/comparison_time.csv.gz','rt',newline='') as f:
        for r in csv.DictReader(f):
            case=originals[r['case']];t=float(r['elapsed_time_s'])
            lu=scalar_interp(t,case['time_s'],case['ln_a'])
            lr=scalar_interp(t,ref['time_s'],ref['ln_a'])
            coordinate_error=max(coordinate_error,abs(math.exp(lu)-float(r['candidate_a'])),
                                 abs(math.exp(lr)-float(r['reference_a'])))
            for k in FIELDS:
                x=scalar_interp(lu,case['ln_a'],case[k]);y=scalar_interp(lr,ref['ln_a'],ref[k])
                ya=scalar_interp(lu,ref['ln_a'],ref[k])
                for suffix,v in [('candidate',x),('reference',y),('delta_at_fixed_t',x-y),
                                 ('fixed_a_at_candidate_a',x-ya),('clock_displacement',ya-y)]:
                    errors[k]=max(errors[k],abs(v-float(r[k+'_'+suffix])))
            rows_checked+=1
    for k,error in errors.items():need(error<(2e-8 if k=='temperature_K' else 2e-12),'AUDIT_EQUAL_TIME_'+k)
    need(coordinate_error<1e-14,'AUDIT_COORDINATE_MAP')
    tau_error=max(abs(tau[k]-summary['rec_segment_consumer'][k]['tau_z20_to_z4']) for k in tau)
    need(tau_error<2e-14,'AUDIT_THOMSON_PROPER_TIME')
    clock_results=[]
    with (HERE/'results/clock_check.csv').open(newline='') as f:clock_rows=list(csv.DictReader(f))
    for q in (-.01,.005):
        independent=high_precision_clock(q,.2)
        row=next(r for r in clock_rows if float(r['q_ref'])==q and float(r['a'])==.2)
        discrepancy=abs(float(independent)-float(row['independent_offset_s']))
        need(discrepancy<.002,'AUDIT_HIGH_PRECISION_CLOCK')
        clock_results.append({'q_ref':q,'a':.2,'offset_s_60_digits':str(independent),
                              'difference_from_stable_double_integral_s':discrepancy})
    result={'status':'PASS_SCOPED_SAVED_MODEL_CONSUMER','author_independence':False,
        'method_independence':'stdlib CSV + scalar bisect interpolation; 60-digit reciprocal subtraction integral',
        'full_rows_read':sum(len(d['time_s']) for d in originals.values()),
        'equal_time_comparison_rows_checked':rows_checked,'coordinate_max_abs_error':coordinate_error,
        'equal_time_max_abs_error_by_observable':errors,
        'first_upward_milestone_max_difference':milestone_errors,
        'proper_electron_charge_max_residual':charge,
        'proper_time_Thomson_max_difference':tau_error,'high_precision_clock':clock_results,
        'reused_evidence':['original PR129 full species census and parity','source hashes verified by reducer_002'],
        'unresolved':['AX08 +0.01 full case','AX11 evolution refinements','AX12 source/IC robustness',
                      'full observer tail','source/interpolation sensitivity is not a rigorous evolution bound'],
        'subagents':0,'central_completed':28,'central_total':88,'wall_s':time.monotonic()-started}
    (HERE/'results/ADVERSARIAL_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inputs',required=True)
    main(p.parse_args().inputs)
