#!/usr/bin/env python3
"""One authority-authorized plumbing retry from saved outputs; no integration."""
import json
import os
import sys
import time
from pathlib import Path
import li_photo_driver as d

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/laneA'

def main():
    started=time.perf_counter()
    p=json.loads((OUT/'provider_reconstruction.json').read_text())
    # Exact saved arrays were parsed from immutable provider bytes in the first pass.
    d.PH1=p['PH1']; d.PH2=p['PH2_2s']
    raw={}
    for r in d.readcsv(OUT/'li_photo_response.csv'):
        raw[r['species'],int(r['n']),int(r['quadrature_nodes']),r['band'],r['shell']]=[float(r[f]) for f in d.FIELDS]
    moments=d.readcsv(OUT/'li_photo_source_moments.csv')
    for r in moments:
        for f in ['quadrature_nodes','n']: r[f]=int(r[f])
        for f in ['Delta_eV','P_2s','photon_count','energy_eV','saved_reservoir_eV','P_Delta_eV']: r[f]=float(r[f])
    cross=d.readcsv(OUT/'li_photo_cross_sections.csv')
    for r in cross:
        for f in ['E_eV','sigma_Mb','Decimal_reference_Mb']: r[f]=float(r[f])
    convergence=d.readcsv(OUT/'li_photo_quadrature.csv')
    for r in convergence: r['relative_128_256']=float(r['relative_128_256'])
    comparisons=d.readcsv(OUT/'li_photo_comparison.csv')
    for r in comparisons: r['relative_difference']=float(r['relative_difference'])
    independent=json.loads((OUT/'li_photo_independent.json').read_text())['species']
    mixtures=json.loads((ROOT/'inputs/laneA/cascade_mixture.json').read_text())['mixture_moments']
    delta=json.loads((OUT/'li_photo_summary.json').read_text())['species_Delta_eV']
    sys.path.insert(0,str(ROOT/'tests'))
    from test_li_photo_validation import validate
    tests=validate(raw,moments,cross,convergence,comparisons,independent,mixtures,delta)
    tests['validation_passes']=1
    tests['failed_prior_invocation']='module-state import exception before focused validation completed; raw traceback retained'
    d.dump(OUT/'li_photo_tests.json',tests)
    elapsed=time.perf_counter()-started
    evidence=json.loads((ROOT/'evidence/LI_PHOTO_EXECUTION.json').read_text())
    evidence['initial_status']=evidence['status']
    evidence['status']='PASS_PENDING_INDEPENDENT_AUTHORITY_REVIEW' if tests['passed'] else 'FAIL_RETURN_TO_AUTHORITY'
    evidence['tests']=tests
    evidence['repairs_executed']=1
    evidence['repair']={'classification':'TEST_PLUMBING','authority':'Independent Astra via controller /root',
        'authorization':'Register initialized __main__ module alias before test import for future direct execution; for validation-only repair load provider rows from exact saved provider_reconstruction.json and saved outputs, then run focused validation once without quadrature rerun. Preserve first traceback; no model/tolerance changes.',
        'command':'OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 30s python code/li_photo_validate_saved.py > results/laneA/li_photo_validation_retry.log 2>&1',
        'wall_seconds':elapsed,'quadrature_rerun':False,
        'thread_environment':{k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']}}
    evidence['initial_command_plus_retry_validation_seconds']=evidence['command_wall_seconds']+elapsed
    d.dump(ROOT/'evidence/LI_PHOTO_EXECUTION.json',evidence)
    print(json.dumps({'status':evidence['status'],'validation_retry_wall_seconds':elapsed,'tests':tests}))
    return 0 if tests['passed'] else 1

if __name__=='__main__': sys.exit(main())
