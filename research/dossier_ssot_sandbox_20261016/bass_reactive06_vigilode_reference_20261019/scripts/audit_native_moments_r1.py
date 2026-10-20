#!/usr/bin/env python3
"""R1 independent native scalar interval and source-identity audit.

The native wrapper is a new recovery revision. All scalar CSV input points are
interpreted as exact binary64 numbers, and its new raw-age interval columns
are checked separately from survivor mass. Variable opacity is outside scope.
"""
from __future__ import annotations
import argparse
import csv
import datetime
from decimal import Decimal, localcontext
import json
import math
from pathlib import Path
import platform
import time
import numpy as np
from decimal_oracles_r1 import j_jk, point
from independent_birth_reference import Fixture, gauss, sha


def relative(a, b):
    return (a-b)/b if b else (0.0 if a == b else math.inf)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--parent',type=Path,required=True)
    ap.add_argument('--csv',type=Path,required=True)
    ap.add_argument('--adapter',type=Path,required=True)
    ap.add_argument('--wrapper',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter()
    rows=list(csv.DictReader(args.csv.open()))
    if len(rows)!=48 or len({r['spectral'] for r in rows})!=48:
        raise ValueError('expected48 unique native spectral rows')
    cases={r['case'] for r in rows}
    if len(cases)!=1:raise ValueError('mixed case CSV')
    f=Fixture(args.parent,next(iter(cases)))
    q,w=gauss(128)
    ratios=f.source_ratio(q)
    endpoint_ratios=f.source_ratio(np.array([0.,1.]))
    rules={int(r['rule_id']):r for r in f.rules}
    template_rates={}
    for row in f.templates:
        template_rates.setdefault(int(row['spectral_index']),[]).append(float(row['midpoint_rate_com3_s']))
    identity_checks=[]
    scalar_checks=[]
    source_checks=[]
    with localcontext() as ctx:
        ctx.prec=110
        ctx.Emin=-999999999999999999
        ctx.Emax=999999999999999999
        total_constant=total_linear=Decimal(0)
        total_const_lo=total_const_hi=total_lin_lo=total_lin_hi=Decimal(0)
        total_actual8=total_actual16=total_independent_source=0.0
        for row in rows:
            spectral=int(row['spectral'])
            dt,tau,jmid,left,right=map(point,(row['dt_s'],row['tau'],row['j_mid_com3_s'],row['j_left_com3_s'],row['j_right_com3_s']))
            m00,m10,m20,m01=(j_jk(tau,j,k) for j,k in ((0,0),(1,0),(2,0),(0,1)))
            exact={'J00':m00,'J10':m10,'J20':m20,
                   'constant_mass':jmid*dt*m00,
                   'constant_age1':jmid*dt*dt*m10,
                   'constant_age2':jmid*dt*dt*dt*m20,
                   'linear_mass':dt*(left*m10+right*m01)}
            suffix={'constant_age1':'_s','constant_age2':'_s2'}
            for key,value in exact.items():
                unit=suffix.get(key,'')
                lo,hi=point(row[key+'_lo'+unit]),point(row[key+'_hi'+unit])
                scalar_checks.append({'spectral':spectral,'quantity':key,'reference_decimal110':str(value),
                    'lo_exact_binary64':str(lo),'hi_exact_binary64':str(hi),
                    'enclosed':0<=lo<=value<=hi,'relative_width':str((hi-lo)/value) if value else '0'})
            total_constant+=exact['constant_mass'];total_linear+=exact['linear_mass']
            total_const_lo+=point(row['constant_mass_lo']);total_const_hi+=point(row['constant_mass_hi'])
            total_lin_lo+=point(row['linear_mass_lo']);total_lin_hi+=point(row['linear_mass_hi'])
            rule=rules[spectral]
            expected_kappa=math.fsum(float(rule['k_'+sp+'_per_s']) for sp in ('HI','HeI','HeII','DI'))
            expected_jmid=math.fsum(template_rates[spectral])
            identity_checks.append({'spectral':spectral,
                'energy_relative':relative(float(row['energy_ev']),float(rule['energy_ev'])),
                'kappa_relative':relative(float(row['kappa_per_s']),expected_kappa),
                'j_mid_relative':relative(float(jmid),expected_jmid),
                'left_ratio_relative':relative(float(left/jmid),float(endpoint_ratios[0])),
                'right_ratio_relative':relative(float(right/jmid),float(endpoint_ratios[1])),
                'duration_equal':float(dt)==f.dt,
                'tau_equals_binary64_kappa_times_duration':float(tau)==float(row['kappa_per_s'])*float(dt)})
            independent=float(jmid)*float(dt)*float(np.sum(w*ratios*np.exp(-float(tau)*(1-q))))
            actual8,actual16=float(row['actual_source_gl8']),float(row['actual_source_gl16'])
            source_checks.append({'spectral':spectral,'independent_actual_source_gl128':independent,
                'native_actual_source_gl8':actual8,'native_actual_source_gl16':actual16,
                'native_gl8_to_gl16_relative':relative(actual8,actual16),
                'native_gl16_vs_independent_source_relative':relative(actual16,independent),
                'linear_source_vs_independent_actual_relative':relative(float(exact['linear_mass']),independent)})
            total_actual8+=actual8;total_actual16+=actual16;total_independent_source+=independent
        totals={'constant_exact_binary64_decimal110':str(total_constant),
                'constant_interval_sum_lo_decimal110':str(total_const_lo),'constant_interval_sum_hi_decimal110':str(total_const_hi),
                'linear_exact_binary64_decimal110':str(total_linear),
                'linear_interval_sum_lo_decimal110':str(total_lin_lo),'linear_interval_sum_hi_decimal110':str(total_lin_hi),
                'native_actual_source_gl8':total_actual8,'native_actual_source_gl16':total_actual16,
                'independent_actual_source_gl128':total_independent_source,
                'native_gl16_vs_independent_relative':relative(total_actual16,total_independent_source),
                'linear_source_vs_actual_relative':relative(float(total_linear),total_independent_source)}
    failures=[r for r in scalar_checks if not r['enclosed']]
    identity_failures=[r for r in identity_checks if not r['duration_equal'] or not r['tau_equals_binary64_kappa_times_duration'] or
        max(abs(r[k]) for k in ('energy_relative','kappa_relative','j_mid_relative','left_ratio_relative','right_ratio_relative'))>2e-13]
    receipt={'version':'BR06_THEORY_RECOVERY_R1','historical_pass_inherited':False,
       'status':'PASS_FRESH_NATIVE_SCALAR_CONTAINMENT_AND_INPUT_BINDING' if not failures and not identity_failures else 'FAIL',
       'scope':'48 original energy labels, seven scalar quantities per label. Raw age is unnormalized source-weighted dt^2*J10 and dt^3*J20. Variable geometry/opacity is outside interval enclosure.',
       'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':platform.python_version(),
       'precision_decimal_digits':110,'source_sha256':sha(__file__),
       'modules':{str(p):sha(p) for p in (Path(__file__).with_name('decimal_oracles_r1.py'),Path(__file__).with_name('independent_birth_reference.py'))},
       'inputs':{str(p):sha(p) for p in (args.csv,args.adapter,args.wrapper,*f.files.values())},
       'rows':len(rows),'checks':len(scalar_checks),'enclosed':len(scalar_checks)-len(failures),
       'max_relative_width':str(max(Decimal(r['relative_width']) for r in scalar_checks)),
       'scalar_failures':failures,'identity_failures':identity_failures,'identity_checks':identity_checks,
       'scalar_checks':scalar_checks,'actual_source_checks':source_checks,'totals':totals,
       'source_interpolation_scope':'Linear-source interval is exact for its exported endpoints. Its difference from actual MD14 time dependence is a separate approximation error, not a containment failure.',
       'wall_s':time.perf_counter()-start}
    out=args.output/'NATIVE_MOMENTS_DECIMAL_RECOVERY_R1.json'
    out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','rows','checks','enclosed','max_relative_width','totals','wall_s')}|{'output':str(out),'sha256':sha(out)}))
    if receipt['status']=='FAIL':raise SystemExit(1)


if __name__=='__main__':main()
