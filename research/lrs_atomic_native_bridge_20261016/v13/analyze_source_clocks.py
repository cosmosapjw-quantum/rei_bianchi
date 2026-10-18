#!/usr/bin/env python3
"""Inspect actual native V13 rows. Self differences are not a continuum reference.

Uses Python standard library only. No implicit claim based on cancellation,
positivity, conservation, or a short observed convergence slope.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
from collections import defaultdict

OBSERVABLES=('T_K','photons_per_H','photo_HI','photo_HeI','photo_HeII','photo_heat_eV_H')

def analyze(path:Path)->dict:
    rows=list(csv.DictReader(path.open(newline='')))
    if not rows: raise ValueError('EMPTY_NATIVE_CSV')
    grouped=defaultdict(list)
    for row in rows:
        numeric={k:float(v) for k,v in row.items() if k!='mode'}
        if not all(math.isfinite(v) for v in numeric.values()): raise ValueError('NONFINITE_ROW')
        x,y,z=numeric['HII'],numeric['HeII'],numeric['HeIII']
        if not(0<=x<=1 and y>=0 and z>=0 and y+z<=1 and numeric['T_K']>0):
            raise ValueError('NONPHYSICAL_NATIVE_ROW')
        if abs(numeric['photon_residual_H'])>1e-16: raise ValueError('PHOTON_LEDGER')
        if abs(numeric['energy_residual_eV_H'])>1e-9: raise ValueError('ENERGY_LEDGER')
        if numeric['photons_per_H']<0 or min(numeric[k] for k in ('photo_HI','photo_HeI','photo_HeII'))<0:
            raise ValueError('NEGATIVE_PHOTON_EVENT')
        grouped[(row['mode'],int(row['N']))].append(row)
    ends=defaultdict(list)
    for (mode,n),block in grouped.items():
        if [int(r['step']) for r in block]!=list(range(1,n+1)):raise ValueError('INCOMPLETE_OR_DUPLICATE_RUN')
        ends[mode].append(block[-1])
    modes={}
    for mode,points in ends.items():
        points.sort(key=lambda r:int(r['N']))
        entry={'N':[int(r['N']) for r in points], 'observables':{}}
        for key in OBSERVABLES:
            values=[float(r[key]) for r in points]
            signed=[a-b for a,b in zip(values,values[1:])]
            magnitude=list(map(abs,signed))
            orders=[math.log2(a/b) if a>0 and b>0 else None for a,b in zip(magnitude,magnitude[1:])]
            entry['observables'][key]={'endpoints':values,'signed_self_difference':signed,
                'absolute_self_difference':magnitude,'self_difference_order':orders,
                'difference_sign_changes':sum(a*b<0 for a,b in zip(signed,signed[1:]))}
        modes[mode]=entry
    return {'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'completed_histories':len(grouped),'checked_rows':len(rows),'cells':int(rows[0]['cells']),
        'Xend':float(rows[0]['Xend']),
        'maximum_energy_residual_eV_H':max(abs(float(r['energy_residual_eV_H'])) for r in rows),
        'maximum_photon_residual_H':max(abs(float(r['photon_residual_H'])) for r in rows),
        'maximum_newton_residual':max(float(r['max_newton_residual']) for r in rows),
        'recorded_history_wall_sum_s':sum(float(v[-1]['wall_s']) for v in grouped.values()),
        'modes':modes}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('csv',nargs='+',type=Path);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();results=[analyze(p) for p in args.csv]
    payload={'schema':'rei.v13.native.analysis.1','status':'FINITE_SOURCEON_EXPERIMENT_SCOPED',
       'continuum_sourceon_reference':'NOT_RUN','global_sourceon_second_order':'HOLD',
       'warnings':['Self-difference slopes can be dominated by cancellation, nonlinear tolerance or spectral closure.',
                   'Common-midpoint source halves are not retarded GL2 source-age quadrature.',
                   'These are modified native Rust experiments in sandbox, not NCP.'],
       'results':results}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    for r in results:
        print(r['file'],r['completed_histories'],'histories',r['checked_rows'],'rows')
        for mode in ('be_control','combined','source_off'):
            o=r['modes'][mode]['observables'];print(mode,'p_T=',o['T_K']['self_difference_order'],
                'p_N=',o['photons_per_H']['self_difference_order'])
    print('TOTAL',sum(r['completed_histories'] for r in results),'histories',sum(r['checked_rows'] for r in results),'rows')
