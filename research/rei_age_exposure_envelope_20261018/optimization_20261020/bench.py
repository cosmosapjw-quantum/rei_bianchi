"""Bounded, sequential benchmark of the unchanged fixed-input research model."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import time

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent / 'vigilode_age_transport_20261019'
RESULTS = HERE / 'results'


def mode_activation_failures(study, preload=False, reuse_oracle=False, reference_parity=False):
    """Check observed execution modes separately from numerical agreement."""
    actual=study.get('optimization', {})
    failures=[]
    for name,requested in [('preload',preload),('reuse_oracle',reuse_oracle)]:
        if bool(actual.get(name,False)) != requested:
            failures.append({'mode':name,'requested':requested,'actual':actual.get(name)})
    if preload and actual.get('preloaded_exp_evaluations') != study['certified_exp_evaluations']:
        failures.append({'mode':'preloaded_exp_evaluations','expected':study['certified_exp_evaluations'],
                         'actual':actual.get('preloaded_exp_evaluations')})
    if reuse_oracle:
        for pair in study['paired_bounds']:
            group=pair['grouped_affine']; audit=group.get('optimization',{})
            expected={'reuse_oracle':True,'canonical_thread_count':1,'all_prefix_thread_parity':True,
                      'oracle_recurrences':group['groups'],'oracle_prefix_checks':group['total_leaves'],
                      'thread_prefix_bit_comparisons':2*(group['groups']+group['total_leaves'])}
            for key,value in expected.items():
                if audit.get(key) != value:
                    failures.append({'mode':'grouped_'+key,'coarse':pair['coarse'],
                                     'expected':value,'actual':audit.get(key)})
    if reference_parity:
        expected=study['certified_exp_evaluations']+sum(len(p['leaf_gain_upper']) for p in study['paired_bounds'])
        if actual.get('reference_exp_endpoint_checks') != expected:
            failures.append({'mode':'reference_exp_endpoint_checks','expected':expected,
                             'actual':actual.get('reference_exp_endpoint_checks')})
    return failures


def numeric_differences(a, b, path=''):
    if isinstance(a, dict) and isinstance(b, dict):
        keys = (a.keys() | b.keys()) - {'wall_seconds', 'optimization'}
        return [d for k in sorted(keys) for d in numeric_differences(a.get(k), b.get(k), path+'/'+k)]
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return [d for k, (x, y) in enumerate(zip(a, b)) for d in numeric_differences(x, y, path+'/'+str(k))]
    # JSON serialization round-trips binary64 values exactly with float_roundtrip.
    if type(a) is float and type(b) is float:
        import struct
        equal = struct.pack('>d', a) == struct.pack('>d', b)
    else:
        equal = type(a) is type(b) and a == b
    return [] if equal else [{'path': path, 'reference': a, 'candidate': b}]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label', required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--threads', type=int, default=2)
    parser.add_argument('--source', choices=['baseline', 'A', 'B', 'current'], default='current')
    parser.add_argument('--preload', action='store_true')
    parser.add_argument('--reference-parity', action='store_true')
    parser.add_argument('--reuse-oracle', action='store_true')
    args = parser.parse_args()
    assert args.threads > 0
    assert not (RESULTS/(args.label+'_RUN.json')).exists(), 'preserve completed run receipts'
    prior = sum(json.loads(p.read_text())['wall_seconds'] for p in RESULTS.glob('*_RUN.json'))
    assert prior < 600, prior
    result = RESULTS / (args.label+'_STUDY.json')
    cmd = [str(args.binary.resolve()), str(STUDY/'inputs'), str(result)]
    env = dict(os.environ, RAYON_NUM_THREADS=str(args.threads))
    for k in ['REI_PRELOAD', 'REI_EXP_REFERENCE_PARITY', 'REI_REUSE_ORACLE']:
        env.pop(k, None)
    if args.preload:
        env['REI_PRELOAD'] = '1'
    if args.reference_parity:
        env['REI_EXP_REFERENCE_PARITY'] = '1'
    if args.reuse_oracle:
        env['REI_REUSE_ORACLE'] = '1'
    source = {str(p.relative_to(STUDY)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [STUDY/'rust/src/main.rs', STUDY/'rust/src/certified.rs',
                        STUDY/'rust/Cargo.lock', STUDY/'inputs/model.json', STUDY/'inputs/nodes.csv']}
    if args.source != 'current':
        for name in ['main.rs', 'certified.rs']:
            frozen = (HERE/'baseline_source/B'/name if args.source=='B' else
                      HERE/'baseline_source'/('A_certified.rs' if args.source=='A' and name=='certified.rs' else 'src/'+name))
            source['rust/src/'+name] = hashlib.sha256(frozen.read_bytes()).hexdigest()
    started = time.monotonic()
    try:
        completed = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=min(240, 600-prior))
        code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as exc:
        code, stdout, stderr = 124, exc.stdout or b'', exc.stderr or b''
        stdout = stdout.decode() if isinstance(stdout, bytes) else stdout
        stderr = stderr.decode() if isinstance(stderr, bytes) else stderr
    wall = time.monotonic()-started
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    (RESULTS/(args.label+'.stdout')).write_text(stdout)
    (RESULTS/(args.label+'.stderr')).write_text(stderr)
    receipt = {'command': cmd, 'exit_code': code, 'wall_seconds': wall,
               'user_cpu_seconds': usage.ru_utime, 'system_cpu_seconds': usage.ru_stime,
               'peak_rss_kb': usage.ru_maxrss, 'RAYON_NUM_THREADS': args.threads,
               'preload': args.preload, 'reference_parity': args.reference_parity,
               'reuse_oracle': args.reuse_oracle,
               'source_variant': args.source,
               'source_identities': source, 'binary_sha256': hashlib.sha256(args.binary.read_bytes()).hexdigest(),
               'cumulative_measurement_wall_seconds': prior+wall,
               'PRODUCTION_SCIENTIFIC_ADMISSION': 'NOT_ISSUED'}
    if code == 0:
        study=json.loads(result.read_text())
        differences = numeric_differences(json.loads((RESULTS/'BASELINE_STUDY.json').read_text()), study)
        receipt['numeric_byte_parity'] = not differences
        receipt['differences'] = differences
        failures=mode_activation_failures(study,args.preload,args.reuse_oracle,args.reference_parity)
        receipt['mode_activation_pass']=not failures
        receipt['mode_activation_failures']=failures
        if failures:
            receipt['failure_category']='MODE_NOT_ACTIVATED'
    (RESULTS/(args.label+'_RUN.json')).write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))
    if not (code == 0 and receipt['numeric_byte_parity'] and receipt['mode_activation_pass']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
