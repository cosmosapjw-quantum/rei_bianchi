#!/usr/bin/env python3
"""Source-only high-z Puchwein2019 D1 integral, Python standard library.

No IGM initial-value solver. Publication rows are a 13-point transcription,
not the author's original source archive. D1 effective neutral-weighted rates
must not be used as local ionized-bubble rates.
"""
import csv
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
INPUT=ROOT/'data/P19_D1_ORIGINAL_HIGHZ_13.csv'
CHANNELS=('HI','HeI','HeII')
H0=67.9*1000/(1e6*3.085677581491367e16)
OMEGA_M=0.305

def read():
    with INPUT.open(newline='',encoding='utf-8') as stream:
        rows=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(stream)]
    assert len(rows)==13 and rows[2]['z']==6.14 and rows[-2]['z']==9.99
    assert all(b['z']>a['z'] for a,b in zip(rows,rows[1:]))
    assert all(v>0 and math.isfinite(v) for row in rows for k,v in row.items() if k!='z')
    return rows

def H(z):
    return H0*math.sqrt(OMEGA_M*(1+z)**3+1-OMEGA_M)

def quad_key(rows,key):
    # Simpson 512 panels on each of 9 source intervals; log-linear source moments.
    value=0.0
    for left,right in zip(rows[2:-2],rows[3:-1]):
        a,b=left['z'],right['z']
        d=(b-a)/512
        loga,logb=math.log(left[key]),math.log(right[key])
        def f(z):
            src=math.exp(loga+(z-a)/(b-a)*(logb-loga))
            return src/((1+z)*H(z))
        pieces=f(a)+f(b)
        for i in range(1,512):pieces+=(4 if i%2 else 2)*f(a+i*d)
        value+=d*pieces/3
    return value

def calculate():
    rows=read(); out={}
    for sp in CHANNELS:
        gamma=quad_key(rows,'Gamma_'+sp+'_s')
        heat=quad_key(rows,'Heat_'+sp+'_eV_s')
        out[sp]={'source_integrated_photo_event_exposure':gamma,
                 'source_integrated_excess_heat_eV_per_frozen_target':heat,
                 'source_mean_heat_per_event_eV':heat/gamma}
    return out

if __name__=='__main__':
    import json
    print(json.dumps(calculate(),indent=2))
