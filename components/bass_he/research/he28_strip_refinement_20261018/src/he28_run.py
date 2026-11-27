"""HE28 complete opt-in native runner. Does not claim a native run until executed."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import sys
import time
import traceback

from refined_source import GridSpec,RefinedSourceModel,RESEARCH
from native import NativeOwner,SOURCE_COMMIT
from transport import solve_transport
from reference import solve_reference
from execution import atomic_json,digest,manifest,verify_manifest,run_process

ROOT=Path(__file__).resolve().parents[1]
REPO=RESEARCH.parent

THREAD_ENV_NAMES=('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',
                  'NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS')


def pin_numerical_threads():
    """Allow only case-level concurrency; avoid nested library pools."""
    for name in THREAD_ENV_NAMES:
        os.environ[name]='1'
    os.environ.update(OMP_DYNAMIC='FALSE',OMP_PLACES='cores',OMP_PROC_BIND='close')


def numerical_thread_environment():
    names=(*THREAD_ENV_NAMES,'OMP_DYNAMIC','OMP_PLACES','OMP_PROC_BIND')
    env={name:os.environ.get(name) for name in names}
    if any(env[name]!='1' for name in THREAD_ENV_NAMES):
        raise ValueError('HE28_NUMERICAL_THREAD_ENVIRONMENT')
    return env


def build_identity(binary,receipt):
    d=json.loads(Path(receipt).read_text())
    if d.get('owner_source')!=SOURCE_COMMIT or d.get('binary_sha256')!=digest(binary):
        raise ValueError('HE28_NATIVE_BUILD_IDENTITY')
    expected=json.loads((ROOT/'provenance/PARENT_SHA256.json').read_text())
    verify_manifest(expected,REPO)
    return {'parent_sources':expected,'binary_sha256':digest(binary),
            'owner_source':SOURCE_COMMIT,'build_receipt':d,
            'python':sys.version,
            'numerical_thread_environment':numerical_thread_environment(),
            'he28_sources':manifest(sorted((ROOT/'src').glob('*.py')),ROOT)}


def check_result(r):
    numeric=[r['number_defect'],r['energy_defect_ev'],r['min_photon'],r['temperature_K'],*r['species_defect'],*r['gas_final']]
    if not all(math.isfinite(x) for x in numeric):
        raise AssertionError('HE28_NONFINITE_SCIENTIFIC_RESULT')
    if (abs(r['number_defect'])>3e-15 or abs(r['energy_defect_ev'])>3e-12
        or max(abs(x) for x in r['species_defect'])>3e-12
        or not r['gas_positive'] or r['min_photon']<0):
        raise AssertionError('HE28_NATIVE_LEDGER_OR_POSITIVITY')


def case(args):
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    identity=build_identity(args.binary,args.build_receipt)
    spec=GridSpec(m=args.m,angles=args.angles,q=args.q,strips=args.strips)
    identity.update(spec=asdict(spec),n=args.n,source_table_nodes=args.table_nodes)
    atomic_json(out/'IDENTITY.json',identity)
    started=time.monotonic()
    try:
        with NativeOwner(args.binary,evidence_path=out/'native.jsonl.gz',
                         expected_binary_sha256=identity['binary_sha256']) as owner:
            model=RefinedSourceModel(owner,spec=spec,tabulate=True,
                source_table_nodes=args.table_nodes,
                max_table_bytes=args.table_mb*1024**2,
                max_table_wall_s=args.table_wall_s)
            atomic_json(out/'TABLE.json',dict(diagnostics=model.source_table_diagnostics,
                source_table_sha256=model.source_table_sha256))
            before=owner.calls
            result=solve_transport(model,n=args.n)
            check_result(result)
            outputs={'transport':result,'transport_native_calls':owner.calls-before}
            if args.reference:
                for method in ('Radau','DOP853'):
                    before=owner.calls
                    ref=solve_reference(model,rtol=1e-10,atol=1e-12,method=method)
                    check_result(ref)
                    outputs[method]=ref;outputs[method+'_native_calls']=owner.calls-before
                outputs['reference_delta_temperature_K']=abs(outputs['Radau']['temperature_K']-outputs['DOP853']['temperature_K'])
                outputs['transport_reference_error_K']=abs(result['temperature_K']-outputs['Radau']['temperature_K'])
                outputs['reference_stable']=outputs['reference_delta_temperature_K']<=1e-9
                outputs['transport_reference_fraction_error']=max(abs(a-b) for a,b in zip(result['gas_final'][:3],outputs['Radau']['gas_final'][:3]))
                outputs['pilot_accuracy_pass']=(outputs['reference_stable'] and outputs['transport_reference_error_K']<=1e-8 and outputs['transport_reference_fraction_error']<=1e-11)
                # No automatic inference of temporal/spectral convergence from one case.
            outputs['total_native_calls']=owner.calls
        atomic_json(out/'RESULT.json',dict(status='SCOPED_NATIVE_COMPLETED',results=outputs,
            source_table_sha256=model.source_table_sha256,wall_s=time.monotonic()-started,
            full_EoR='HOLD',continuous_spectrum='HOLD'))
    except BaseException as exc:
        atomic_json(out/'FAILURE.json',{'status':'HOLD_FIRST_FAILURE','error':repr(exc),
            'traceback':traceback.format_exc(),'wall_s':time.monotonic()-started})
        raise


def campaign(args):
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    build_identity(args.binary,args.build_receipt)
    # Stage-specific bounded jobs; no full Cartesian-product campaign.
    jobs=[(4,2,16,True)] if args.stage=='pilot' else [
        (8,2,32,False),(8,4,32,False),(8,8,32,False),
        (8,2,64,False),(8,4,64,False),(8,8,64,False)]
    if args.stage=='study':
        if not args.pilot_result:raise ValueError('HE28_PILOT_REQUIRED')
        pr=json.loads(Path(args.pilot_result).read_text())
        ident=json.loads((Path(args.pilot_result).parent/'IDENTITY.json').read_text())
        if pr.get('status')!='SCOPED_NATIVE_COMPLETED' or pr['results'].get('pilot_accuracy_pass') is not True:
            raise ValueError('HE28_PILOT_NOT_ADMITTED')
        now=build_identity(args.binary,args.build_receipt)
        if (ident['he28_sources']!=now['he28_sources']
            or ident['binary_sha256']!=now['binary_sha256']
            or ident.get('owner_source')!=now['owner_source']
            or ident.get('parent_sources')!=now['parent_sources']):
            raise ValueError('HE28_PILOT_SOURCE_CHANGED')
        if ident.get('numerical_thread_environment')!=now['numerical_thread_environment']:
            raise ValueError('HE28_PILOT_THREAD_ENVIRONMENT_CHANGED')
        # A table discretization is part of the admitted model, not just a cost knob.
        # Study m/r/n change by design; changing table resolution needs a new pilot.
        if ident.get('source_table_nodes') != args.table_nodes:
            raise ValueError('HE28_PILOT_TABLE_RESOLUTION_CHANGED')
        if (ident.get('spec') != {'m':4,'strips':2,'angles':4,'q':0.}
            or ident.get('n') != 16):
            raise ValueError('HE28_PILOT_DESIGN_CHANGED')
        table_path=Path(args.pilot_result).parent/'TABLE.json'
        if not table_path.is_file():
            raise ValueError('HE28_PILOT_TABLE_MISSING')
        table=json.loads(table_path.read_text())
        table_hash=pr.get('source_table_sha256')
        diagnostics=table.get('diagnostics',{})
        if (not isinstance(table_hash,str) or not table_hash
            or table.get('source_table_sha256')!=table_hash
            or diagnostics.get('nodes_per_long_interval')!=args.table_nodes
            or diagnostics.get('spec')!=ident.get('spec')):
            raise ValueError('HE28_PILOT_TABLE_IDENTITY')
    atomic_json(out/'DESIGN.json',{'jobs':jobs,'scope':'finite strip/time comparison; no automatic global PASS',
                 'source_table_nodes':args.table_nodes,'per_case_wall_s':args.case_wall_s})
    def execute(job):
        m,r,n,reference=job
        name=f'm{m}_r{r}_n{n}'
        cmd=[sys.executable,str(Path(__file__).resolve()),'case','--binary',str(Path(args.binary).resolve()),
             '--build-receipt',str(Path(args.build_receipt).resolve()),'--out',str(out/name),
             '--m',str(m),'--strips',str(r),'--n',str(n),
             '--table-nodes',str(args.table_nodes),'--table-mb',str(args.table_mb),
             '--table-wall-s',str(args.table_wall_s)]
        if reference:cmd.append('--reference')
        rec=run_process(cmd,out/(name+'_process'),args.case_wall_s)
        if rec['returncode']==0 and reference:
            complete=json.loads((out/name/'RESULT.json').read_text())
            rec['pilot_accuracy_pass']=complete['results'].get('pilot_accuracy_pass') is True
        return dict(case=name,**rec)

    workers=getattr(args,'workers',1)
    if type(workers) is not int or not 1 <= workers <= len(jobs):
        raise ValueError('HE28_STUDY_WORKER_DOMAIN')
    # Cases have independent native-owner processes and immutable output roots.
    # Keep each case's BLAS/OpenMP policy at one thread; parallelism is only across
    # the six pre-authorized study cases, never across floating-point reductions.
    records_by_name={}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures={pool.submit(execute,job):f'm{job[0]}_r{job[1]}_n{job[2]}' for job in jobs}
        for future in as_completed(futures):
            name=futures[future]
            try:
                records_by_name[name]=future.result()
            except BaseException as exc:
                records_by_name[name]={'case':name,'returncode':-1,'runner_error':repr(exc)}
    records=[records_by_name.get(f'm{m}_r{r}_n{n}',
             {'case':f'm{m}_r{r}_n{n}','returncode':-1,'runner_error':'not executed'})
             for m,r,n,_ in jobs]
    summary={'executed':len(records),'requested':len(jobs),'records':records,
             'workers':workers,
             'all_processes_pass':len(records)==len(jobs) and all(r['returncode']==0 for r in records),
             'pilot_accuracy_pass':records[0].get('pilot_accuracy_pass') if args.stage=='pilot' else None,
             'stage':args.stage,'continuous_spectral_convergence':'HOLD','full_EoR':'HOLD'}
    atomic_json(out/'SUMMARY.json',summary)
    print(json.dumps(summary,indent=2))
    if not summary['all_processes_pass'] or summary['pilot_accuracy_pass'] is False:raise SystemExit(1)


def main():
    pin_numerical_threads()
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['case','campaign','preflight'])
    ap.add_argument('--out',required=True);ap.add_argument('--binary');ap.add_argument('--build-receipt')
    ap.add_argument('--m',type=int,default=4);ap.add_argument('--strips',type=int,default=2)
    ap.add_argument('--n',type=int,choices=[16,32,64,128,256],default=16)
    ap.add_argument('--angles',type=int,default=4);ap.add_argument('--q',type=float,default=0.)
    ap.add_argument('--reference',action='store_true');ap.add_argument('--table-nodes',type=int,default=512)
    ap.add_argument('--table-mb',type=int,default=2048);ap.add_argument('--table-wall-s',type=float,default=600.)
    ap.add_argument('--case-wall-s',type=float,default=3600.);ap.add_argument('--stage',choices=['pilot','study'],default='pilot')
    ap.add_argument('--pilot-result')
    ap.add_argument('--workers',type=int,default=1,
                    help='bounded process-level concurrency for the six independent study cases')
    args=ap.parse_args()
    if args.mode=='preflight':
        model=RefinedSourceModel(None,GridSpec(args.m,args.angles,args.q,args.strips),tabulate=False,
                                 source_table_nodes=args.table_nodes)
        atomic_json(Path(args.out)/'PREFLIGHT.json',model.source_table_diagnostics)
    else:
        if not args.binary or not args.build_receipt:ap.error('native binary and build receipt required')
        if args.mode=='case':case(args)
        else:campaign(args)

if __name__=='__main__':main()
