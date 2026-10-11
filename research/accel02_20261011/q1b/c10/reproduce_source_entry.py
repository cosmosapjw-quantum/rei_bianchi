#!/usr/bin/env python3
"""Reconstruct the executed C10 source diagnostics in a fresh output directory.

This script was reconstructed AFTER the original inline executions. It is not
their archived original command text and has not itself run those diagnostics.
It preserves their scientific operations, input hashes and acceptance metrics.
Publication of this script does not request or authorize replay of older runs.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np

HERE = Path(__file__).resolve().parent
Q1B = HERE.parent
sys.path[:0] = [str(HERE),str(Q1B),str(Q1B.parent/'n1')]
from source_entry import SourceEntryError, integrate_source, advance_source, provider_event_times
from source_cells import CellSource
from grid_cells import load_grid
from provider import HistoryProvider

EXPECTED_INPUTS = {
    'c10/source_entry.py':'56ed274e76e4cea832d70271764534ba54b89c3d37365a0ae83e4f9ddc20db64',
    'c10/test_source_entry.py':'706504580a09343daf3a412aa6ba2beb17d000751046121d2f741e98c4986257',
    'GRID_C2.json':'409a584cc4ee863dee97cd5fba60486abfd50be63a9c0955a258aeae755bffa0',
    'source_cells.py':'1200e88036d6af443d6f350d896d790953f0a04f24caa4d893b420abeb10f631',
    'evidence/SOURCE_C2.npz':'bd0fc845407010dbd80f3561e37fb57d523d308a5ef899ecd44b909f38f7960a',
}
EXPECTED_PROVIDER = {
    'background.py':'b80f1d2ca8b4ab251d93447ff746428e6230130bee9b87500b7960bbc3a0076d',
    'hm12_data.py':'ede512206bd6f5acc85b1c6b90fda4edc256b4dd8a70c42f9726932b6bff5121',
    'sources/emissivity.out':'88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b',
    'sources/UVB.out':'a708586ead551202c068b049d48afa87b96695c5a5d12253e9b9bbb74efd75dc',
}
EXPECTED_PATTERN = [True,False,False,True,True,True]


def write_json(path, value):
    with path.open('x') as handle:
        json.dump(value,handle,indent=2,allow_nan=False)
        handle.write('\n')


def own_fine_error(coarse,fine):
    relative = np.zeros_like(fine)
    np.divide(abs(coarse-fine),abs(fine),out=relative,where=fine != 0)
    if np.any((fine == 0) & (coarse != fine)):
        return None
    return float(relative.max())


def run(output_dir):
    # Validate before constructing providers or creating result directories.
    actual = {name:hashlib.sha256((Q1B/name).read_bytes()).hexdigest()
              for name in EXPECTED_INPUTS}
    if actual != EXPECTED_INPUTS:
        raise ValueError('SOURCE_ENTRY_REPRO_INPUT_IDENTITY_MISMATCH')
    provider = HistoryProvider(r=0.)
    if provider.identity != EXPECTED_PROVIDER:
        raise ValueError('SOURCE_ENTRY_REPRO_PROVIDER_IDENTITY_MISMATCH')
    source = CellSource(provider,load_grid(Q1B/'GRID_C2.json'))
    output_dir.mkdir(parents=True,exist_ok=False)
    write_json(output_dir/'REPRODUCTION_CONTRACT.json',{
        'status':'REPRODUCTION_RUNNING','started_utc':datetime.now(timezone.utc).isoformat(),
        'script_provenance':'Reconstructed after original execution; not original inline source text',
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'input_sha256':actual,'provider_sha256':provider.identity,
        'scope':'New C10 source-only diagnostics; no old RUN002/EVENT003/Q0 or native/gas calculation',
        'expected_interval_pass_pattern':EXPECTED_PATTERN,
        'gates':{'time_quadrature_per_cell_own_fine':1e-10,'pairing':1e-12,
                 'semigroup_per_cell_own_fine':1e-10},
    })
    start = time.monotonic()
    attempts = []
    with (output_dir/'SOURCE_ENTRY_INTERVALS.jsonl').open('x') as log:
        for h in (1e10,5e9,2.5e9,1e11,5e10,2.5e10):
            try:
                result = integrate_source(source,0.,h,
                    event_times=provider_event_times(source,0.,h))
                record = {'h':h,'pass':True,'diagnostics':result['diagnostics']}
            except SourceEntryError as error:
                record = {'h':h,'pass':False,'error':str(error),
                          'diagnostics':error.diagnostics}
            attempts.append(record)
            log.write(json.dumps(record,allow_nan=False)+'\n')
            log.flush()
            print(json.dumps({'interval_s':h,'pass':record['pass']}),flush=True)
    with np.load(Q1B/'evidence/SOURCE_C2.npz') as saved:
        N0,U0 = saved['initial_N'].copy(),saved['initial_U_eV'].copy()
    born = int(np.flatnonzero(source.edges[:-1] == 50000.)[0])
    histories,final = {},{}
    local_pass = True
    with (output_dir/'SOURCE_ENTRY_SEMIGROUP.jsonl').open('x') as log:
        for steps in (1,2,4):
            N,U = N0.copy(),U0.copy()
            work,injected = np.zeros_like(N),np.zeros_like(N)
            details = []
            for j in range(steps):
                t0,t1 = j*1e11/steps,(j+1)*1e11/steps
                try:
                    result = integrate_source(source,t0,t1,
                        event_times=provider_event_times(source,t0,t1))
                    out = advance_source(N,U,result)
                except SourceEntryError as error:
                    details.append({'t0':t0,'t1':t1,'error':str(error),
                                    'diagnostics':error.diagnostics})
                    local_pass = False
                    break
                N,U = out['N'],out['U_eV']
                work += out['radiation_work_eV']
                injected += result['injected_energy_eV']
                details.append({'t0':t0,'t1':t1,'time_quad':result['diagnostics'],
                                'advance_pairing':out['diagnostics']})
            if len(details) == steps and 'error' not in details[-1]:
                residual = U-U0+work-injected
                scale = np.maximum.reduce([abs(U),abs(U0),abs(work),abs(injected)])
                relative = np.zeros_like(scale)
                np.divide(abs(residual),scale,out=relative,where=scale > 0)
                pairing = float(relative.max())
                # The original fixture has no nonzero residual at zero scale.
                if np.any((scale == 0) & (residual != 0)):
                    raise ValueError('SOURCE_ENTRY_ZERO_SCALE_NONZERO_PAIRING')
                R1 = result['R1']
                mean = U[:,born]/(R1*N[:,born])
                width = 50000./R1-50000.
                item = {'pass':pairing <= 1e-12,'steps':details,
                    'accumulated_pairing_max_relative':pairing,
                    'birth':{'cell_index':born,'q_left_eV':50000.,
                        'N_per_angle':N[:,born].tolist(),
                        'Q_per_angle':(U[:,born]/R1).tolist(),
                        'mean_q_eV':mean.tolist(),'reachable_width_eV':width.tolist(),
                        'fraction_of_reachable_width':((mean-50000.)/width).tolist(),
                        'initial_N_exact_zero':bool(np.all(N0[:,born] == 0)),
                        'mean_is_integrated_not_seeded':True}}
                final[steps] = (N,U,work,injected)
                local_pass &= item['pass']
            else:
                item = {'pass':False,'steps':details}
            histories[str(steps)] = item
            log.write(json.dumps({'steps':steps,**item},allow_nan=False)+'\n')
            log.flush()
            print(json.dumps({'semigroup_steps':steps,'pass':item['pass']}),flush=True)
    comparisons = {}
    if len(final) == 3:
        for coarse in (1,2):
            comparisons[str(coarse)+'_vs_4'] = {
                name:own_fine_error(a,b) for name,a,b in
                zip(('N','U','work','injected'),final[coarse],final[4])}
        local_pass &= all(value is not None and value <= 1e-10
                         for row in comparisons.values() for value in row.values())
    else:
        local_pass = False
    with (output_dir/'SOURCE_ENTRY_SEMIGROUP_ARRAYS.npz').open('xb') as handle:
        np.savez_compressed(handle,**{f'{name}_{steps}':array
            for steps,arrays in final.items()
            for name,array in zip(('N','U','work','injected'),arrays)})
    pattern_matches = [item['pass'] for item in attempts] == EXPECTED_PATTERN
    report = {'schema':'rei.q1b.c10.source_entry_reproduction.v1',
        'status':'LOCAL_SOURCE_REDSHIFT_MAP_ONLY','model_identity':'UNKNOWN',
        'reproduction_pass':bool(local_pass and pattern_matches),
        'expected_interval_pattern_matches':pattern_matches,
        'pass_local_semigroup':bool(local_pass),'source_only_interval_attempts':attempts,
        'common_endpoint_s':1e11,'common_endpoint_runs':histories,
        'common_endpoint_comparisons':comparisons,'elapsed_s':time.monotonic()-start,
        'input_sha256':actual,'provider_identity':provider.identity,
        'expected_original_observation':{
            'semigroup_max_own_fine':7.012775437112667e-12,
            'newborn_N_per_angle_1step':9.426024685299062e-21,
            'newborn_mean_q_eV_1step':50000.143910086,
            'comparison_policy':'Frozen gates and interval pass pattern; binary-identical results are not required'},
        'claim_ceiling':'Source-only quadrature/paired work; not native absorption, gas, temporal splitting or history admission',
    }
    write_json(output_dir/'SOURCE_ENTRY_REPRODUCTION.json',report)
    print(json.dumps({'reproduction_pass':report['reproduction_pass'],
                      'comparisons':comparisons}),flush=True)
    return 0 if report['reproduction_pass'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True,
                        help='Fresh directory; existing directory is refused')
    args = parser.parse_args()
    raise SystemExit(run(args.output_dir.resolve()))
