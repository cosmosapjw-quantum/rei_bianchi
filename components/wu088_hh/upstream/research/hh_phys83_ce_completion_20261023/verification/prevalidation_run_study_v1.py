"""One create-only PHYS83 finite H I study; completed bytes resume with zero callbacks.

Identity includes physics, frozen inputs and implementation bytes, excluding
runtime versions. Imports of the scientific implementation occur only after
exclusive identity admission. Failed/incomplete attempts are never replayed
implicitly. This module has no ODE solver, benchmarking, old-science callback,
nuclear rate or stopping callback.
"""
from __future__ import annotations
import argparse
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import sys
import traceback

UNIT = Path(__file__).resolve().parents[1]
CORE = ('CONTRACT.json', 'source/run_study.py', 'source/matched_ce.py',
        'source/frozen_star.py', 'source/vendor/ci_finite_c22d.py')
RAW = ('CCC_1S.2S','CCC_1S.2P','CCC_2S.1S','CCC_2P.1S',
       'HI_CE_SOURCE_CONTRACT.json','h_1.elvlc','h_1.wgfa')
EXPECTED = {'paired_rate_calls':132,'steady_calls':324,'transient_calls':732}
TMAX = 25370.66308424773


def utc(): return datetime.now(timezone.utc).isoformat()
def digest(b): return hashlib.sha256(b).hexdigest()
def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def write_new(path, obj):
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

def replace_owned_json(path,obj):
    """Atomic update of this attempt's own journal pointer, never another claim."""
    path=Path(path);tmp=path.with_name(path.name+'.pending')
    with tmp.open('x',encoding='utf-8') as f:
        json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
        f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def scientific_identity(unit=UNIT):
    paths=list(CORE)+['source_data/'+x for x in RAW]
    hashes={p:digest((unit/p).read_bytes()) for p in paths}
    payload={'schema':'PHYS83_CE_IDENTITY_V1','input_SHA256':hashes,
             'parent_final_PHYS82':'ca9d53983459ea08f9992a8a24663e46b7180344',
             'actual_PHYS83_S0':'09289300ec2e500806aa2cb82365f00329e41c8c',
             'scope':'finite matched H I LS star; frozen T/ne; optically thin escape',
             'expected_callbacks':EXPECTED,'runtime_version_in_identity':False,
             'HH_R10':'OFF','production_admission':'NOT_ISSUED'}
    return {'scientific_identity':digest(canonical(payload)),'payload':payload}

def validate_complete(output, identity):
    output=Path(output)
    complete=json.loads((output/'COMPLETE.json').read_text())
    if complete.get('scientific_identity')!=identity or complete.get('status')!='COMPLETED':
        raise ValueError('COMPLETE_IDENTITY_OR_STATUS_MISMATCH')
    for rel,meta in complete['files'].items():
        p=output/rel
        if p.parent!=output or not p.is_file():raise ValueError('INVALID_COMPLETION_PAYLOAD')
        b=p.read_bytes()
        if len(b)!=meta['bytes'] or digest(b)!=meta['SHA256']:
            raise ValueError('COMPLETED_RESULT_CORRUPTED:'+rel)
    return complete

def execute_new_or_skip(identity_doc,output,registry,callback):
    """Generic admission tested with mocks; callback is not touched on resume."""
    output=Path(output);registry=Path(registry)
    identity=identity_doc['scientific_identity']
    registry.mkdir(parents=True,exist_ok=True)
    claim=registry/(identity+'.json')
    if claim.exists():
        old=json.loads(claim.read_text())
        if old.get('scientific_identity')!=identity:raise ValueError('CLAIM_IDENTITY_MISMATCH')
        # Existing complete bytes can repair an interrupted metadata commit,
        # but never trigger scientific work. Output location is caller supplied
        # so a byte-for-byte restored directory remains portable.
        if (output/'COMPLETE.json').exists():
            complete=validate_complete(output,identity)
            if old.get('status')!='COMPLETED':
                replace_owned_json(claim,{**old,'status':'COMPLETED','metadata_recovery_utc':utc()})
            return {'status':'SKIP_COMPLETED_IDENTITY','scientific_identity':identity,
                    'science_callbacks':0,'verified_payload_files':len(complete['files'])}
        raise RuntimeError('CLAIM_EXISTS_WITHOUT_VERIFIED_COMPLETION; inspect preserved attempt; no automatic replay')
    if output.exists():raise FileExistsError('OUTPUT_EXISTS_WITHOUT_CLAIM; no overwrite or automatic replay')
    admission={'scientific_identity':identity,'status':'ADMITTED','admitted_utc':utc(),
               'output_directory_name':output.name,'runtime_is_not_a_replay_trigger':True}
    write_new(claim,admission) # O_EXCL is the concurrency gate.
    try:
        output.mkdir(parents=True,exist_ok=False)
        write_new(output/'SCIENCE_IDENTITY.json',identity_doc)
        result=callback(output)
        files={}
        for p in sorted(output.iterdir()):
            if p.is_file():
                b=p.read_bytes();files[p.name]={'bytes':len(b),'SHA256':digest(b)}
        complete={'schema':'PHYS83_CE_COMPLETION_V1','status':'COMPLETED',
                  'scientific_identity':identity,'completed_utc':utc(),
                  'files':files,'execution':result}
        write_new(output/'COMPLETE.json',complete)
        validate_complete(output,identity)
        replace_owned_json(claim,{**admission,'status':'COMPLETED','completed_utc':complete['completed_utc']})
        return {'status':'COMPLETED_NEW_IDENTITY','scientific_identity':identity,
                'execution':result,'verified_payload_files':len(files)}
    except BaseException as exc:
        failure={**admission,'status':'FAILED_PRESERVED','failed_utc':utc(),
                 'error':type(exc).__name__+': '+str(exc),'traceback':traceback.format_exc()}
        if output.exists() and not (output/'FAILED.json').exists():write_new(output/'FAILED.json',failure)
        replace_owned_json(claim,failure)
        raise

def write_rows(path,rows):
    if not rows:raise ValueError('NO_ROWS')
    with path.open('x',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)
        f.flush();os.fsync(f.fileno())

def calculate(output):
    # This is the only entry to science; all source/kernel imports follow admission.
    import numpy as np
    from matched_ce import load_channels
    from frozen_star import FrozenHIStar
    counters={k:0 for k in EXPECTED}
    journal=(output/'execution_events.jsonl').open('x',encoding='utf-8')
    def event(kind,**data):
        journal.write(json.dumps({'utc':utc(),'event':kind,**data})+'\n');journal.flush()
    thread_names=('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS')
    if any(os.environ.get(k)!='1' for k in thread_names):raise RuntimeError('EXPLICIT_SINGLE_THREAD_REQUIRED')
    write_new(output/'ENVIRONMENT.json',{'python':platform.python_version(),'platform':platform.platform(),
        'packages':{p:importlib.metadata.version(p) for p in ('numpy','scipy','mpmath')},
        'thread_environment':{k:os.environ.get(k) for k in thread_names},'workers':1,
        'runtime_version_change_alone_triggers_replay':False})
    event('SCIENCE_STARTED')
    channels=load_channels()
    temperatures=sorted(set(float(x) for x in np.geomspace(255.,50000.,61))|{1000.,3000.,5000.,10000.,TMAX})
    if len(temperatures)!=66:raise ArithmeticError('CONTRACT_TEMPERATURE_COUNT')
    cache={};rates=[]
    for T in temperatures:
        cache[T]={}
        for level in ('2S','2P'):
            r=channels[level].evaluate(T);counters['paired_rate_calls']+=1
            cache[T][level]=r;rates.append(asdict(r))
    write_rows(output/'rate_grid.csv',rates);event('RATE_GRID_SAVED',rows=len(rates),callbacks=dict(counters))
    steady=[]
    for T in (5000.,10000.,TMAX,50000.):
        for ne in np.geomspace(1e-8,1e18,81):
            row=asdict(FrozenHIStar(cache[T]['2S'],cache[T]['2P'],float(ne)).steady())
            counters['steady_calls']+=1;steady.append(row)
    write_rows(output/'steady_grid.csv',steady);event('STEADY_GRID_SAVED',rows=len(steady),callbacks=dict(counters))
    transient=[]
    times=[0.]+[float(x) for x in np.geomspace(1e-12,1e3,121)]
    for T in (10000.,TMAX):
        for ne in (1.,1e8,1e12):
            model=FrozenHIStar(cache[T]['2S'],cache[T]['2P'],ne)
            for t in times:
                row=asdict(model.step(t));counters['transient_calls']+=1
                transient.append({'temperature_K':T,'electron_density_cm3':ne,**row})
            event('TRANSIENT_PROFILE_COMPLETED',temperature_K=T,ne_cm3=ne,rows=len(times))
    write_rows(output/'transient_grid.csv',transient)
    if counters!=EXPECTED:raise ArithmeticError('CALLBACK_BUDGET_MISMATCH:'+str(counters))
    max_energy=max(abs(r['normalized_raw_energy_residual']) for r in transient)
    max_nuclei=max(abs(r['nuclei_residual']) for r in transient)
    min_population=min(r[k] for r in transient for k in ('population_ground','population_2s','population_2p'))
    if max_energy>2e-11 or max_nuclei>2e-13 or min_population<0:
        raise ArithmeticError('SAMPLED_SCIENTIFIC_LEDGER_GATE')
    diagnostics={'max_abs_normalized_raw_energy_residual':max_energy,
                 'max_abs_nuclei_residual':max_nuclei,'minimum_sampled_population':min_population,
                 'numerical_branches':sorted(set(r['numerical_branch'] for r in transient)),
                 'negative_clipping_used':False,'finite_sample_is_continuum_certificate':False}
    summary={'status':'COMPLETED_SCOPED','callback_counts':counters,'rate_temperatures':len(temperatures),
        'transient_profiles':6,'diagnostics':diagnostics,'covered_channels':[channels[x].coverage() for x in ('2S','2P')],
        'new_cosmological_ODE':0,'benchmarks':0,'completed_identity_reexecutions':0,
        'nuclear_rates':0,'fast_product_stopping':0,'HH_R10':'OFF','production_admission':'NOT_ISSUED',
        'interpretation':'Finite source-native H I star at fixed T/ne. Conditional model diagnostics, not a source uncertainty interval or coupled thermal history.'}
    write_new(output/'SCIENCE_SUMMARY.json',summary)
    event('SCIENCE_COMPLETED',callbacks=counters,diagnostics=diagnostics);journal.close()
    return summary

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true')
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    if args.receipt.exists():raise FileExistsError('INVOCATION_RECEIPT_EXISTS')
    identity=scientific_identity()
    if not args.execute:
        result={'status':'IDENTITY_ONLY_NO_CALLBACKS',**identity}
    else:
        result=execute_new_or_skip(identity,UNIT/'results',UNIT/'delivery/scientific_claims',calculate)
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    write_new(args.receipt,{'utc':utc(),**result})
    print(json.dumps(result,ensure_ascii=False,allow_nan=False))
    return 0

if __name__=='__main__':raise SystemExit(main())
