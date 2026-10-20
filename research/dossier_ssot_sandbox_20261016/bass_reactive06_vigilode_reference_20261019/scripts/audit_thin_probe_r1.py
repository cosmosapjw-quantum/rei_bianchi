#!/usr/bin/env python3
"""Independent Decimal400 audit of the freshly declared R1 thin probe.

This is a new recovery verifier. The old probe source and exact grid were lost;
the new 22-case run must not be described as a byte-identical old-grid replay.
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
import struct
import time
from decimal_oracles_r1 import phi, point, sha


def ordered_bits(value):
    bits=struct.unpack('>Q',struct.pack('>d',value))[0]
    return (1<<63)-bits if bits>>63 else bits+(1<<63)


def ulps(a,b):
    return abs(ordered_bits(a)-ordered_bits(b))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--csv',type=Path,required=True)
    ap.add_argument('--probe',type=Path,required=True)
    ap.add_argument('--execution',type=Path,required=True)
    ap.add_argument('--source-identity',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter()
    rows=list(csv.DictReader(args.csv.open()))
    if len(rows)!=22:raise ValueError('R1 declared probe must have22rows')
    results=[]
    with localcontext() as ctx:
        ctx.prec=400;ctx.Emin=-999999999999999999;ctx.Emax=999999999999999999
        E0,h,T=point(100.0),point(.05),point(1.0)
        for row in rows:
            if row['status']!='ok':
                results.append({'case':int(row['case']),'status':'RUST_REFUSAL','row':row});continue
            k=point(row['rate']);tau=k*T
            survival=(-tau).exp()
            absorption=tau*phi(tau)
            attenuation=phi((k+h)*T)
            absorbed_energy=k*E0*T*attenuation
            work=-h*E0*T*attenuation
            end_energy=E0*(-h*T).exp()
            survivor_energy=survival*end_energy
            actual={name:point(row[name]) for name in ('survival','HI','HeI','HeII','DI','absorbed_total','absorbed_energy_ev','work_independent_ev','work_ledger_ev','end_energy_ev')}
            count_ulps=ulps(float(actual['HI']),float(absorption))
            count_relative=(actual['HI']-absorption)/absorption if absorption else Decimal(0)
            work_relative=(actual['work_independent_ev']-work)/work
            ledger_relative=(actual['work_ledger_ev']-work)/work
            energy_relative=(actual['absorbed_energy_ev']-absorbed_energy)/absorbed_energy if absorbed_energy else Decimal(0)
            new_energy_residual=actual['survival']*actual['end_energy_ev']+actual['absorbed_energy_ev']-E0-actual['work_independent_ev']
            inactive_zero=all(actual[sp]==0 for sp in ('HeI','HeII','DI'))
            nonnegative=all(actual[key]>=0 for key in ('survival','HI','HeI','HeII','DI','absorbed_total','absorbed_energy_ev','end_energy_ev'))
            flags={key:row[key] for key in ('opacity_underflow','absorption_underflow','HI_underflow','HI_heat_underflow','survival_underflow')}
            # Explicit finite-control acceptance: exact zero; for subnormal
            # absorption, retain its correctly rounded nonzero representation;
            # otherwise relative count/work error below1e-12.
            if absorption==0:
                count_pass=actual['HI']==0
            elif absorption<point(float.fromhex('0x1.0p-1022')):
                count_pass=count_ulps==0
            else:
                count_pass=abs(count_relative)<Decimal('1e-12')
            passed=(count_pass and abs(work_relative)<Decimal('1e-12') and
                    abs(new_energy_residual)/E0<Decimal('1e-12') and inactive_zero and nonnegative and
                    all(value=='false' for value in flags.values()))
            results.append({'case':int(row['case']),'rate_exact_binary64':str(k),'slabs':int(row['slabs']),
                'thin_time_route':row['thin_time_route']=='true','status':'PASS' if passed else 'FAIL',
                'survival_reference_decimal400':str(survival),'absorption_reference_decimal400':str(absorption),
                'absorbed_energy_reference_ev_decimal400':str(absorbed_energy),'work_reference_ev_decimal400':str(work),
                'survivor_energy_reference_ev_decimal400':str(survivor_energy),
                'absorption_ulps_from_correctly_rounded_reference':count_ulps,
                'absorption_relative_error':str(count_relative),'work_relative_error':str(work_relative),
                'ledger_work_relative_error':str(ledger_relative),'absorbed_energy_relative_error':str(energy_relative),
                'independently_recomputed_energy_residual_ev':str(new_energy_residual),
                'inactive_species_exact_zero':inactive_zero,'nonnegative':nonnegative,'flags':flags})
    failures=[r for r in results if r['status']!='PASS']
    successful=[r for r in results if 'work_relative_error' in r]
    receipt={'version':'BR06_THEORY_RECOVERY_R1','historical_pass_inherited':False,
        'status':'PASS_FRESH_R1_DECLARED_THIN_GRID' if not failures else 'FAIL',
        'grid_scope':'New declared R1 22-case grid, not exact restoration of the deleted probe. Same original near-zero-hazard failure mechanisms; no extra nonlinear history.',
        'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':platform.python_version(),
        'decimal_precision':400,'exact_binary64_constants':{'E0_ev':str(point(100.0)),'h_per_s':str(point(.05)),'duration_s':str(point(1.0))},
        'reference_formulas':{'HI':'k*T*Phi(k*T)','work_ev':'-h*E0*T*Phi((k+h)*T)','absorbed_energy_ev':'k*E0*T*Phi((k+h)*T)'},
        'source_sha256':sha(__file__),'decimal_module_sha256':sha(Path(__file__).with_name('decimal_oracles_r1.py')),
        'inputs':{str(p):sha(p) for p in (args.csv,args.probe,args.execution,args.source_identity)},
        'acceptance':'Nonnegative measures; inactive channels zero; exact zero opacity; correctly rounded nonzero subnormal absorption; otherwise count/work relative<1e-12 and energy residual/source<1e-12; represented-underflow flags all false.',
        'cases':len(rows),'passed':len(rows)-len(failures),'thin_route_cases':sum(r.get('thin_time_route',False) for r in results),
        'correctly_rounded_absorption_cases':sum(r.get('absorption_ulps_from_correctly_rounded_reference')==0 for r in results),
        'maximum_absorption_ulps':max(r['absorption_ulps_from_correctly_rounded_reference'] for r in successful),
        'max_work_relative_error':str(max(abs(Decimal(r['work_relative_error'])) for r in successful)),
        'max_ledger_work_relative_error':str(max(abs(Decimal(r['ledger_work_relative_error'])) for r in successful)),
        'results':results,'failures':failures,'wall_s':time.perf_counter()-start}
    out=args.output/'THIN_PROBE_DECIMAL_RECOVERY_R1.json'
    out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','cases','passed','thin_route_cases','correctly_rounded_absorption_cases','maximum_absorption_ulps','max_work_relative_error','wall_s')}|{'output':str(out),'sha256':sha(out)}))
    if failures:raise SystemExit(1)


if __name__=='__main__':main()
