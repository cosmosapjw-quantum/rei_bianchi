"""Two bounded interface probes by the nonauthor reviewer; no suite replay."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, platform, resource, sys, time, traceback

ROOT = Path('/tmp/he38_review')
COMPONENT = Path('/tmp/he38_implementation')

def write_json(name, value):
    path = ROOT/name
    temporary = path.with_suffix(path.suffix+'.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)

start = datetime.now(timezone.utc).isoformat()
wall = time.perf_counter()
cpu = time.process_time()
write_json('PROBE_START.json', {
    'started_utc': start,
    'command': 'PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python /tmp/he38_review/probe_interface.py',
    'python': sys.version, 'platform': platform.platform(),
    'scope': 'tiny diagonal STF nested adapter representation and fully ionized zero-reactant boundary only',
    'input_sha256': {str(p.relative_to(COMPONENT)):hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted((COMPONENT/'h1_finite_mass').rglob('*.py'))},
    'reviewer_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'old_suites_replayed': 0, 'old_IVPs_replayed': 0, 'new_IVPs': 0,
    'benchmark_runs': 0, 'science_renders': 0,
})
code = 0
try:
    import numpy as np
    sys.path.insert(0, str(COMPONENT))
    import h1_finite_mass as h
    scopes = dict(thermal_inventory_scope=h.ALL_RETAINED_THERMAL,
                  charge_census_scope=h.NEUTRAL_21_STATE_CENSUS)
    temperature = 20000.
    nb = 1e6
    y = np.zeros(21); y[1] = .6; y[2] = .4
    pe = np.diag([1., -1., 0.]) * (1e-40 * nb * y[2] * h.KB_J_K * temperature)
    zero = np.zeros((3,3))
    source = h.h1_ci_source(temperature, y, nb, pe, zero, **scopes)
    direct = source.J
    nested = source.event_tensor_source.J
    expected = -float(source.species.evaluation.kappa2_m3_s[0])*nb*y[1]*h.ZETA*pe
    scale = np.max(np.abs(expected))
    direct_error = float(np.max(np.abs(direct/scale-expected/scale)))
    assert direct_error < 1e-14
    assert np.count_nonzero(direct) == 2
    tiny = dict(
        input_diagonal_Pa=np.diag(pe).tolist(),
        direct_diagonal_Pa_s=np.diag(direct).tolist(),
        nested_legacy_diagonal_Pa_s=np.diag(nested).tolist(),
        direct_relative_error=direct_error,
        nested_equals_direct=bool(np.array_equal(nested,direct)),
        direct_STF_preserved=True,
        interpretation='Public wrapper J follows direct new coefficients; nested legacy field is a trace-projected diagnostic and is not a small-STF accuracy oracle.',
    )
    ionized = np.zeros(21); ionized[2] = 1.
    pe_boundary = np.diag([1.,-1.,0.]) * (1e-4*nb*h.KB_J_K*temperature)
    source_boundary = h.h1_ci_source(temperature,ionized,nb,pe_boundary,zero,**scopes)
    assert source_boundary.volumetric_event_rate == 0
    assert np.count_nonzero(source_boundary.J) == 0
    assert source_boundary.physical_abundance_jacobian_s[2,1] > 0
    assert source_boundary.dot_T_reaction_K_s == 0
    boundary = dict(
        rate=source_boundary.volumetric_event_rate,
        direct_STF_nonzero_entries=int(np.count_nonzero(source_boundary.J)),
        activated_dYp_dYH_s=float(source_boundary.physical_abundance_jacobian_s[2,1]),
        temperature_source_K_s=source_boundary.dot_T_reaction_K_s,
        interpretation='Source vanishes while the abundance derivative toward a populated neutral state remains active.',
    )
    result = dict(status='PASS_SCOPED', probe_count=2,
                  tiny_STF=tiny, fully_ionized_boundary=boundary)
except Exception as error:
    code = 1
    result = dict(status='FAIL', exception=repr(error), traceback=traceback.format_exc())
result.update(completed_utc=datetime.now(timezone.utc).isoformat(),
              wall_seconds=time.perf_counter()-wall, cpu_seconds=time.process_time()-cpu,
              max_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              exit_code=code)
write_json('PROBE_RESULT.json', result)
print(json.dumps(result,indent=2))
sys.exit(code)
