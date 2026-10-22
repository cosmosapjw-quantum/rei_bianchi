#!/usr/bin/env python3
"""Additive clean-empty bootstrap for the frozen PR219 atomic pilot (POSIX)."""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE = HERE.parents[1] / 'rei_isotope_quotient_pilot_20261022'
ATTEMPT_LIMIT, CPU_LIMIT, WALL_LIMIT = 90, 2400., 900.
HISTORICAL_RUNNER = '1d1cad1484b113ea767eb07bc1dc617c994e551f8c05f4606081686753d82586'
RECOVERED_RUNNER = '2b3332936a3e9012d435876206b0fb006fcbeb7da9ee61d6f4b3299754831513'
SOURCE_FILES = ['INHERITED_PHYSICAL_CONTRACT.md', 'PHYSICS_CONTRACT.md',
                'pilot/code/run.py', 'pilot/code/atomic_quotient.py',
                'pilot/code/compact_transport.py', 'pilot/evidence/BASELINE_MANIFEST.json',
                'pilot/data/verner_photo_Z1_Z2_Z3.dat',
                'pilot/data/verner_ferland_rr_table1_original.dat']


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text())


def write(p, value, replace=False):
    p = Path(p)
    if p.exists() and not replace:
        raise FileExistsError(p)
    tmp = p.with_name(p.name + '.tmp')
    with tmp.open('w') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)


def prepare(source, workspace):
    """Copy only immutable inputs; no NumPy/SciPy import or output dependency."""
    source, workspace = Path(source).resolve(), Path(workspace).resolve()
    if workspace == source or workspace in source.parents or source in workspace.parents:
        raise ValueError('workspace must be separate from source tree')
    if workspace.exists() and any(workspace.iterdir()):
        raise FileExistsError('prepare requires a new or empty explicit workspace')
    baseline = read(source / 'pilot/evidence/BASELINE_MANIFEST.json')
    files = SOURCE_FILES + ['pilot/' + p for p in baseline['files']]
    if (source / 'pilot/vendor/LICENSE').exists():
        files.append('pilot/vendor/LICENSE')
    recovery = read(HERE / 'SOURCE_IDENTITY.json')
    for relative in files:
        expected = (recovery or {}).get('current_files', {}).get(relative, {}).get('sha256')
        if expected and digest(source / relative) != expected:
            raise RuntimeError('source identity mismatch: ' + relative)
        if relative.startswith('pilot/vendor/'):
            expected = baseline['files'].get(relative.removeprefix('pilot/'))
            if expected and digest(source / relative) != expected:
                raise RuntimeError('vendor identity mismatch: ' + relative)
    if digest(source / 'pilot/code/run.py') != RECOVERED_RUNNER:
        raise RuntimeError('requires disclosed recovered PR219 runner')
    workspace.mkdir(parents=True, exist_ok=True)
    identities = {}
    for relative in files:
        target = workspace / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, target)
        identities[relative] = digest(target)
    (workspace / 'pilot/results').mkdir()
    manifest = dict(schema='rei.bootstrap.source.v1', files=identities,
                    requested_historical_commit='215d5c33',
                    controller_observed_commit='5a1e5220',
                    local_git_identity='unavailable in restored scratch tree',
                    source_provenance='recovered runtime; original historical runner bytes unavailable',
                    historical_expected_runner_sha256=HISTORICAL_RUNNER,
                    recovered_runner_sha256=RECOVERED_RUNNER)
    write(workspace / 'BOOTSTRAP_SOURCE.json', manifest)
    return dict(status='PREPARED_SOURCE_ONLY', workspace=str(workspace), files=len(files),
                new_ivps=0, results=[])


def verify_workspace(workspace):
    manifest = read(Path(workspace) / 'BOOTSTRAP_SOURCE.json')
    for relative, expected in manifest['files'].items():
        if digest(Path(workspace) / relative) != expected:
            raise RuntimeError('prepared immutable source changed: ' + relative)


def load_runner(workspace):
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(Path(workspace) / 'pilot/code'))
    # Each real command uses one workspace per process; avoid accidental module reuse.
    if 'run' in sys.modules:
        raise RuntimeError('runner already loaded; use a new process per workspace')
    runner = importlib.import_module('run')
    runner.verify_sources()
    return runner


def plan(workspace):
    verify_workspace(workspace)
    return dict(status='PLANNED', workspace=str(Path(workspace).resolve()), new_ivps=0,
                stages=['source/import', 'point_checks_v2', 'profile_quotient',
                        'profile_full18_reference', 'profile_pair', 'profile_reanalysis',
                        'strong_and_cancellation_plus_3_L24_controls',
                        'remaining_79_nominal', 'fresh_numeric_summary'],
                cases=dict(nominal=79, controls=3, reference=1, total=83),
                limits=dict(attempts=90, cpu_s=2400, wall_s=900, max_workers=4),
                execution_workers=1, scientific_admission='PENDING_INDEPENDENT_REVIEW')


class RealExecutor:
    """No solver/check/render function is called by inventory or complete reuse."""
    def __init__(self, workspace):
        self.workspace = Path(workspace)
        self.r = load_runner(workspace)
        self.cases, self.controls = self.r.case_configurations()
        self.reference = dict(sigma=0., am=0., ar=0., reference=True)
        self.configs = self.cases + self.controls + [self.reference]
        self.out = self.workspace / 'pilot/results'
        self.sequence = 0

    def name(self, config):
        return self.r.case_id(self.r.Coupled(**config))

    def receipts(self):
        records = []
        for config in self.configs:
            name = self.name(config)
            receipt, raw = self.out / (name + '.json'), self.out / (name + '.npz')
            if receipt.exists() != raw.exists():
                raise RuntimeError('partial or failed case retained: ' + name)
            if receipt.exists():
                records.append(self.r.verify_existing_case(config))
        return records

    def complete(self):
        if (self.workspace / 'pilot/summary.json').exists() and len(self.receipts()) == 83:
            # Existing strict numeric summary is read-only evidence, never reissued.
            return self.r.saved_inventory(require_complete=True)
        return None

    def present(self, stage, config=None):
        if stage == 'case':
            path = self.out / (self.name(config) + '.json')
            if path.exists():
                self.r.verify_existing_case(config)
                return True
            if (self.out / (self.name(config) + '.npz')).exists():
                raise RuntimeError('partial raw case retained: ' + self.name(config))
            return False
        paths = {'checks': self.out / 'point_checks_v2.json',
                 'pair': self.out / 'profile_pair.json',
                 'reanalysis': self.out / 'profile_existing_reanalysis.json',
                 'summary': self.workspace / 'pilot/summary.json'}
        path = paths[stage]
        if not path.exists():
            return False
        value = read(path)
        passed = value.get('passed') is True if stage == 'checks' else value.get('status') == 'PASS'
        if stage == 'summary':
            # A saved historical summary may omit status; only complete() validates it.
            raise RuntimeError('incomplete workspace has an existing summary; preserve and use a new workspace')
        if not passed:
            raise RuntimeError('failed prerequisite retained: ' + str(path))
        return True

    def execute(self, stage, config, remaining_cpu, remaining_wall):
        logs = self.workspace / 'bootstrap_logs'
        logs.mkdir(exist_ok=True)
        self.sequence = len(list(logs.glob('*.command.json'))) + 1
        prefix = logs / f'{self.sequence:04d}_{stage}'
        command = [sys.executable, str(Path(__file__).resolve()), '_worker',
                   '--workspace', str(self.workspace), '--stage', stage,
                   '--config', json.dumps(config), '--cpu-bound', str(remaining_cpu)]
        write(prefix.with_suffix('.command.json'), dict(command=command, stage=stage,
                                                      config=config, remaining_wall_s=remaining_wall))
        start, cpu = time.monotonic(), resource.getrusage(resource.RUSAGE_CHILDREN)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
                   OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
        error = None
        with prefix.with_suffix('.stdout').open('wb') as out, prefix.with_suffix('.stderr').open('wb') as err:
            try:
                completed = subprocess.run(command, stdout=out, stderr=err, env=env,
                                           timeout=remaining_wall, check=False)
                code = completed.returncode
            except subprocess.TimeoutExpired:
                code, error = 124, 'cumulative wall limit'
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        result = dict(status='PASS' if code == 0 else 'FAILED', exit_code=code,
                      wall_s=time.monotonic() - start,
                      cpu_s=after.ru_utime + after.ru_stime - cpu.ru_utime - cpu.ru_stime,
                      log_prefix=str(prefix), error=error)
        write(prefix.with_suffix('.outcome.json'), result)
        return result


class Engine:
    """Serial execution is intentional: cumulative limits include every stage/restart."""
    def __init__(self, workspace, executor, workers=4):
        if workers not in range(1, 5):
            raise ValueError('workers must be 1..4 (current serial executor uses one)')
        self.workspace, self.ex = Path(workspace), executor
        self.state_path = self.workspace / 'BOOTSTRAP_STATE.json'
        self.started, self.cpu_started = time.monotonic(), time.process_time()
        self.state = read(self.state_path) if self.state_path.exists() else dict(
            schema='rei.bootstrap.state.v1', attempts=0, cpu_s=0., wall_s=0., events=[],
            status='READY', active=None, limits=dict(attempts=90,cpu_s=2400,wall_s=900),
            requested_max_workers=workers, actual_workers=1, ncp_allocation='UNCHANGED')
        if self.state['active']:
            # Lost process measurement cannot be reset or guessed into a success.
            self.state['status'] = 'INTERRUPTED_REQUIRES_DIAGNOSIS'
            self.save()
            raise RuntimeError('unfinished launch retained; inspect logs/state, do not reset budget')

    def save(self):
        write(self.state_path, self.state, replace=True)

    def meter(self):
        now, cpu = time.monotonic(), time.process_time()
        self.state['wall_s'] += now - self.started
        self.state['cpu_s'] += cpu - self.cpu_started
        self.started, self.cpu_started = now, cpu

    def run_one(self, stage, config=None):
        if self.ex.present(stage, config):
            return
        self.meter()
        if (stage == 'case' and self.state['attempts'] >= ATTEMPT_LIMIT) or self.state['cpu_s'] >= CPU_LIMIT - 1 or self.state['wall_s'] >= WALL_LIMIT:
            self.state['status'] = 'RESOURCE_LIMIT'
            self.save()
            raise RuntimeError('cumulative resource limit; no launch')
        if stage == 'case':
            self.state['attempts'] += 1
        self.state['active'] = dict(stage=stage, config=config, launched_epoch=time.time())
        self.save()  # Case reservation and active stage survive any interruption.
        try:
            result = self.ex.execute(stage, config, CPU_LIMIT-self.state['cpu_s'], WALL_LIMIT-self.state['wall_s'])
        except Exception as exc:
            # Unknown subprocess usage remains explicit; automatic restart is blocked.
            self.state['status'] = 'EXECUTOR_EXCEPTION_REQUIRES_DIAGNOSIS'
            self.state['events'].append(dict(stage=stage, config=config, error=str(exc)))
            self.save()
            raise
        self.meter()  # Parent wall already includes child duration, never double count it.
        self.state['cpu_s'] += result['cpu_s']
        self.state['events'].append(dict(stage=stage, config=config, result=result))
        self.state['active'] = None
        if result['status'] != 'PASS':
            self.state['status'] = 'FAILED'
            self.save()
            raise RuntimeError('stage failed; retained evidence: ' + stage)
        if self.state['cpu_s'] >= CPU_LIMIT or self.state['wall_s'] >= WALL_LIMIT:
            self.state['status'] = 'RESOURCE_LIMIT'
            self.save()
            raise RuntimeError('cumulative resource limit after stage')
        self.state['status'] = 'RUNNING'
        self.save()

    def run(self):
        if self.state['status'] in ('FAILED', 'RESOURCE_LIMIT', 'EXECUTOR_EXCEPTION_REQUIRES_DIAGNOSIS', 'INTERRUPTED_REQUIRES_DIAGNOSIS'):
            raise RuntimeError('prior stop retained; inspect state/logs; no automatic retry')
        records = self.ex.receipts()
        if not self.state_path.exists():
            # Partial saved evidence consumes prior case allowance and measured CPU;
            # sum of case wall times is a conservative historical elapsed bound.
            self.state['attempts'] = len(records)
            self.state['cpu_s'] += sum(v['cpu_s'] for v in records)
            self.state['wall_s'] += sum(v['wall_s'] for v in records)
        complete = self.ex.complete()
        if complete:
            return dict(complete, bootstrap_status='COMPLETE_NO_WORK', new_ivps=0)
        self.run_one('checks')
        self.run_one('case', self.ex.cases[7])
        self.run_one('case', self.ex.reference)
        self.run_one('pair')
        self.run_one('reanalysis')
        strong = next(c for c in self.ex.cases if c['sigma'] == .6 and c['am'] == 1.6 and c['ar'] == -.8)
        for config in [strong, self.ex.cases[75], *self.ex.controls]:
            self.run_one('case', config)
        for config in self.ex.cases:
            self.run_one('case', config)
        self.run_one('summary')
        complete = self.ex.complete()
        if not complete:
            raise RuntimeError('summary completion validation failed')
        self.meter()
        self.state['status'] = 'COMPLETE_NUMERICAL_PENDING_REVIEW'
        self.save()
        return dict(complete, bootstrap_status=self.state['status'],
                    attempts_total=self.state['attempts'], limits_consumed=self.state)


def profile_pair(r):
    import numpy as np
    names = ['quotient_L16_S0_Am0_Ar0', 'reference_L16_S0_Am0_Ar0']
    receipts = [read(r.OUT / (n+'.json')) for n in names]
    with np.load(r.OUT / (names[0]+'.npz')) as a, np.load(r.OUT / (names[1]+'.npz')) as b:
        fq, fr = a['conditional'], b['state'][:,39:-1]
        target = np.concatenate([fq[:,:2],fq[:,:2],fq[:,2:5],fq[:,2:5],fq[:,5:],fq[:,5:]],axis=1)
        fraction = float(np.max(abs(target-fr)))
        axes = {k:float(np.max(abs(a['diagnostics'][:,a['diagnostic_names'].tolist().index(k)] -
                b['diagnostics'][:,b['diagnostic_names'].tolist().index(k)])))
                for k in ('signed_Sigma','P_m','P_r','tau_T')}
    wall, cpu = sum(v['wall_s'] for v in receipts), sum(v['cpu_s'] for v in receipts)
    passed = max(fraction, *axes.values()) <= 2e-7 and wall <= 120 and cpu <= 240
    result = dict(status='PASS' if passed else 'FAILED', max_charge_difference=fraction,
                  axes_difference=axes, pair_wall_s=wall, pair_cpu_s=cpu,
                  reduced_receipt=names[0]+'.json', reference_receipt=names[1]+'.json',
                  provenance='fresh pair comparison from current raw outputs')
    write(r.OUT / 'profile_pair.json', result)
    return result


def fresh_summary(r):
    """Derive every reported value from new/reused receipts and arrays, not old summary."""
    import numpy as np
    cases, controls = r.case_configurations()
    records = [r.verify_existing_case(c) for c in cases+controls]
    r.verify_existing_case(dict(sigma=0.,am=0.,ar=0.,reference=True))
    checks, pair, reanalysis = [read(r.OUT / name) for name in
        ('point_checks_v2.json','profile_pair.json','profile_existing_reanalysis.json')]
    comparisons = {}
    for config in controls:
        name = r.case_id(r.Coupled(**config))
        low = r.case_id(r.Coupled(**dict(config,ellmax=16,rtol=r.RTOL,atol=r.ATOL)))
        with np.load(r.OUT/(name+'.npz')) as hi, np.load(r.OUT/(low+'.npz')) as lo:
            if not np.array_equal(hi['x'],lo['x']):
                raise RuntimeError('control grids differ: '+name)
            fraction = float(np.max(abs(hi['conditional']-lo['conditional'])))
            axes = {k:float(np.max(abs(hi['diagnostics'][:,hi['diagnostic_names'].tolist().index(k)] -
                lo['diagnostics'][:,lo['diagnostic_names'].tolist().index(k)]))) for k in ('signed_Sigma','P_m','P_r')}
        comparisons[name] = dict(reference=low, fraction=fraction, axes=axes,
                                 passed=max(fraction,*axes.values()) <= 2e-5)
    maxima = dict(max_testfluid_energy_over_background=0., max_electron_closure_relative=0.,
                  max_baryon_sum_residual=0., max_isotope_sum_residual=0.,
                  max_massive_number_relative_drift=0.)
    minima = dict(min_populated_charge_fraction=float('inf'), min_sampled_angular_brightness=float('inf'))
    atomic = r.AtomicQuotient(r.source())
    mass = np.array([a for _,a,z in r.ISOTOPES for q in range(z+1)])
    for config, receipt in zip(cases+controls,records):
        name = r.case_id(r.Coupled(**config))
        with np.load(r.OUT/(name+'.npz')) as raw:
            d, names = raw['diagnostics'], raw['diagnostic_names'].tolist()
            col = lambda key: d[:,names.index(key)]
            expected_ne = col('nB_m3') * (raw['conditional'] @ (atomic.w_element*atomic.q))
            closure = np.max(abs(expected_ne-col('ne_m3'))/np.maximum(abs(expected_ne),1e-300))
            maxima['max_electron_closure_relative'] = max(maxima['max_electron_closure_relative'],float(closure))
            maxima['max_baryon_sum_residual'] = max(maxima['max_baryon_sum_residual'],float(np.max(abs(raw['census']@mass-1))))
            maxima['max_testfluid_energy_over_background'] = max(maxima['max_testfluid_energy_over_background'],float(np.max(
                (col('U_thermal_J_m3')+col('U_binding_J_m3')+col('U_UV_J_m3'))/col('background_J_m3'))))
            minima['min_populated_charge_fraction'] = min(minima['min_populated_charge_fraction'],float(np.min(raw['conditional'])))
        maxima['max_isotope_sum_residual'] = max(maxima['max_isotope_sum_residual'],max(receipt['isotope_sum_errors'].values()))
        maxima['max_massive_number_relative_drift'] = max(maxima['max_massive_number_relative_drift'],receipt['massive_number_drift'])
        minima['min_sampled_angular_brightness'] = min(minima['min_sampled_angular_brightness'],receipt['min_brightness'])
    passed = checks['passed'] is True and pair['status'] == reanalysis['status'] == 'PASS' and all(v['passed'] for v in comparisons.values())
    summary = dict(status='PASS' if passed else 'FAILED', completed=len(records),expected=82,
                   controls=comparisons,point_checks_v2_pass=checks['passed'],
                   all_82_and_3_controls_scoped_numerical_pass=passed,
                   ivp_attempts_including_full18_reference=83,
                   scientific_admission='PENDING_INDEPENDENT_REVIEW',
                   summary_provenance='fresh raw-array and receipt aggregation; historical admission not copied',
                   energy_ratio_definition='(U_thermal+U_binding+prescribed U_UV)/(3 H^2/K), critical-equivalent',
                   figures=[],**maxima,**minima)
    write(r.ROOT/'summary.json',summary)
    return summary


def worker(args):
    # Bound total child CPU, including import/check/summary overhead.
    bound = max(1, int(math.floor(args.cpu_bound)))
    resource.setrlimit(resource.RLIMIT_CPU, (bound,bound))
    r = load_runner(args.workspace)
    config = json.loads(args.config)
    if args.stage == 'checks':
        result = r.point_checks()
        good = result['passed'] is True
    elif args.stage == 'case':
        result = r.run_case(r.Coupled(**config,deadline=120.), output=r.OUT)
        good = result['status'] == 'PASS'
    elif args.stage == 'pair':
        result = profile_pair(r)
        good = result['status'] == 'PASS'
    elif args.stage == 'reanalysis':
        result = r.reanalyze_existing_profile()
        good = result['status'] == 'PASS'
    else:
        result = fresh_summary(r)
        good = result['status'] == 'PASS'
    print(json.dumps(result,indent=2,allow_nan=False))
    return 0 if good else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','plan','resume','fresh-reproduce','reuse-existing','_worker'])
    parser.add_argument('--workspace',type=Path)
    parser.add_argument('--source',type=Path,default=DEFAULT_SOURCE)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--stage',choices=['checks','case','pair','reanalysis','summary'])
    parser.add_argument('--config',default='null')
    parser.add_argument('--cpu-bound',type=float,default=2400.)
    args = parser.parse_args()
    if args.action == '_worker':
        return worker(args)
    if args.action == 'reuse-existing':
        # Deliberately read-only: no workspace/state is created and no check/solve/render.
        r = load_runner(args.source)
        result = r.saved_inventory(require_complete=True)
    else:
        if args.workspace is None:
            parser.error('--workspace is required and must be a new separate directory')
        args.workspace = args.workspace.resolve()
        if args.action in ('prepare','fresh-reproduce'):
            result = prepare(args.source,args.workspace)
        if args.action == 'plan':
            result = plan(args.workspace)
        elif args.action in ('resume','fresh-reproduce'):
            verify_workspace(args.workspace)
            started, cpu_started = time.monotonic(), time.process_time()
            executor = RealExecutor(args.workspace)
            engine = Engine(args.workspace,executor,args.workers)
            engine.state['wall_s'] += time.monotonic()-started
            engine.state['cpu_s'] += time.process_time()-cpu_started
            result = engine.run()
    print(json.dumps(result,indent=2,allow_nan=False))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(f'{type(exc).__name__}: {exc}',file=sys.stderr)
        sys.exit(1)
