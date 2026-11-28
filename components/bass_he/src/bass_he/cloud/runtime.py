"""Runtime source/environment admission and binding."""
import hashlib, json, os, platform, subprocess, sys
from importlib import metadata
from pathlib import Path
from .contracts import ExecutionBinding
from .backend import THREAD_POLICY

# Explicit numerical dependency closure; runner/store/docs are execution binding only.
SCIENCE_FILES=(
    'scripts/replay_dr11e.py',
    'src/bass_he/replay_contract.py',
    'src/bass_he/spectral.py',
    'src/bass_he/sturm_anchor.py',
    'src/bass_he/sturm_geometry.py',
    'src/bass_he/geometry.py',
    'src/arseny_reimpl/term_complex.py',
    'src/arseny_reimpl/term_real.py',
    'src/bass_he/cloud/adapter.py',
    'src/bass_he/cloud/backend.py',
)

def science_hashes(repo:Path):
    return {name:hashlib.sha256((repo/name).read_bytes()).hexdigest() for name in SCIENCE_FILES}

def scientific_source_identity(repo:Path):
    return hashlib.sha256(json.dumps(science_hashes(repo),sort_keys=True,separators=(',',':')).encode()).hexdigest()

def record_provenance():
    result={}
    for name in ('numpy','scipy','threadpoolctl'):
        record=metadata.distribution(name).read_text('RECORD')
        if not record:raise RuntimeError(f'BLOCKED_ENV_PROVENANCE: {name} RECORD unavailable')
        result[name]={'version':metadata.version(name),'record_sha256':hashlib.sha256(record.encode()).hexdigest()}
    return result

def binding(repo:Path):
    import numpy, scipy, threadpoolctl
    src=repo/'src'; hashes={str(p.relative_to(src)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(src.rglob('*.py'))}
    hashes['scripts/replay_dr11e.py']=hashlib.sha256((repo/'scripts/replay_dr11e.py').read_bytes()).hexdigest()
    git=lambda arg:subprocess.check_output(['git','rev-parse',arg],cwd=repo,text=True).strip()
    plan='4e775fdb61e72fd75f956fe0a83064e37e0522da'
    transfer = repo / 'provenance' / 'DR11E_PLAN_TRANSFER.json'
    if transfer.is_file():
        # The owner repository has its own Git history. Bind replay reuse to the
        # exact numerical dependency closure verified on the donor plan descendant.
        raw = transfer.read_bytes()
        if hashlib.sha256(raw).hexdigest() != 'cc98397fe9a1e8be0d8404c5a7bbf938aa60d8d224e1b890a8155f669282afbe':
            raise RuntimeError('DR11E plan transfer receipt changed')
        if science_hashes(repo) != json.loads(raw)['science_sha256']:
            raise RuntimeError('DR11E source differs from the transferred plan closure')
    else:
        if git(plan+'^{tree}') != '6cd022714a4c3579ce1b2b68ac27f69968c0782d':
            raise RuntimeError('plan tree mismatch')
        if subprocess.run(['git','merge-base','--is-ancestor',plan,'HEAD'],cwd=repo).returncode != 0:
            raise RuntimeError('checkout is not derived from approved plan commit')
    cpuinfo=Path('/proc/cpuinfo').read_text() if Path('/proc/cpuinfo').exists() else ''
    flags=next((line.partition(':')[2].strip() for line in cpuinfo.splitlines() if line.startswith(('flags','Features'))),'UNKNOWN')
    blas=[{k:pool.get(k) for k in ('internal_api','version','filepath','threading_layer')} for pool in threadpoolctl.threadpool_info()]
    return ExecutionBinding(git('HEAD'),git('HEAD^{tree}'),hashlib.sha256(str(sorted(hashes.items())).encode()).hexdigest(),sys.version,{'numpy':numpy.__version__,'scipy':scipy.__version__,'threadpoolctl':threadpoolctl.__version__,'blas':blas,'hashes':hashes,'distribution_records':record_provenance()},platform.platform()+' '+platform.processor()+' flags_sha256='+hashlib.sha256(flags.encode()).hexdigest(),THREAD_POLICY,scientific_source_id=scientific_source_identity(repo))
