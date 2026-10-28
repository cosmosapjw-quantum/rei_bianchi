"""Byte-only snapshots and Git staging. Never imports or executes science code.

Run only after controller authorization: python delivery/package_checkpoint.py PHASE
PHASE is an immutable checkpoint label. Produces distinct public portable and
private recovery archives; publication is a separate controller-authorized action.
"""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import time
import zipfile
import resource

UNIT = Path(__file__).resolve().parents[1]
OUT = UNIT / 'delivery'
ROOT_PUBLIC = {'UNIT_START.json', 'ADMISSION.json', 'GLOBAL_DAG_STATUS.json',
               'HANDOFF_KO.md', 'REPORT_KO.md', 'GLOBAL_STATUS_KO.md',
               'REPRODUCE.md', 'README.md'}
INTAKE_PUBLIC = {'SOURCE_AUTHORITY.json', 'SURVEY_SYNTHESIS_KO.md',
                 'AGENTS_CURRENT.md', 'REI_SELECTED_DAG_NODES.json',
                 'ROOT_SCOPE_AND_ASSEMBLY_CONTRACT.md',
                 'REI_PROGRAM_CHARTER_KO.md', 'REI_PROGRAM_HANDOFF_KO.md',
                 'WU_PROGRAM_HANDOFF_KO.md'}
PREFIXES_PUBLIC = {'theory', 'implementation', 'review', 'runtime_inputs'}


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def eligible(p):
    return p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.pyc', '.tmp'}


def public_paths():
    result = []
    for p in sorted(UNIT.rglob('*')):
        if not eligible(p):
            continue
        r = p.relative_to(UNIT)
        if ((len(r.parts) == 1 and p.name in ROOT_PUBLIC)
                or r.parts[0] in PREFIXES_PUBLIC
                or (r.parts[0] == 'intake' and p.name in INTAKE_PUBLIC)
                or str(r) in {'progress/STAGE_EVIDENCE.json', 'progress/STAGES_KO.md'}
                or str(r) in {'delivery/package_checkpoint.py', 'delivery/PUBLICATION_PLAN.json'}):
            result.append(p)
    return result


def verify_runtime():
    provenance = json.loads((UNIT/'runtime_inputs/PROVENANCE.json').read_text())
    for name, row in provenance['files'].items():
        assert sha((UNIT/name).read_bytes()) == row['sha256'], name
    auth = UNIT/'implementation/RUN_AUTHORIZATION.json'
    if auth.exists():
        obj = json.loads(auth.read_text())
        for name, expected in obj.get('sha256_bindings', {}).items():
            p = (UNIT/name).resolve()
            assert sha(p.read_bytes()) == expected, name


def archive(path, paths, prefix):
    rows = []
    with zipfile.ZipFile(path, 'x', zipfile.ZIP_DEFLATED, compresslevel=3) as z:
        for p in paths:
            raw = p.read_bytes()
            name = prefix + p.relative_to(UNIT).as_posix()
            z.writestr(name, raw)
            rows.append({'path': name, 'bytes': len(raw), 'sha256': sha(raw)})
        manifest = {'unit': UNIT.name, 'files': rows, 'scientific_evaluations': 0,
                    'extraction': 'No code runs on extraction. Runtime inputs retain unit-relative paths.'}
        z.writestr('MANIFEST.json', encoded(manifest))
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for row in rows:
            assert sha(z.read(row['path'])) == row['sha256']
    return {'path': str(path), 'bytes': path.stat().st_size,
            'sha256': sha(path.read_bytes()), 'payload_members': len(rows),
            'CRC_and_member_hashes': 'PASS'}


def stage(paths, phase):
    plan = json.loads((OUT/'PUBLICATION_PLAN.json').read_text())
    provider = json.loads((UNIT/'runtime_inputs/provider/PROVIDER_MANIFEST.json').read_text())
    reusable = {r['sha256']: r['git_blob'] for r in provider['files']}
    rows, tree = [], []
    for p in paths:
        raw = p.read_bytes()
        rel = p.relative_to(UNIT).as_posix()
        item = {'path': plan['allowed_path']+'/'+rel, 'mode': '100644', 'type': 'blob'}
        row = {'local_path': str(p), 'path': item['path'], 'bytes': len(raw), 'sha256': sha(raw)}
        if sha(raw) in reusable:
            item['sha'] = reusable[sha(raw)]
            row['reused_git_blob'] = item['sha']
        else:
            item['content'] = raw.decode('utf-8')
        tree.append(item)
        rows.append(row)
    (OUT/(phase+'_PUBLIC_MANIFEST.json')).write_bytes(encoded({'files': rows, 'publication': plan}))
    (OUT/(phase+'_GIT_TREE_PAYLOAD.json')).write_bytes(encoded({
        'repository_full_name': plan['repository'], 'base_tree_sha': plan['base_tree'],
        'tree_elements': tree}))


def main():
    phase = sys.argv[1]
    assert phase.replace('_', '').isalnum(), 'Simple phase label required'
    receipt = OUT/(phase+'_PACKAGE_RECEIPT.json')
    assert not receipt.exists(), 'Preserve existing checkpoint'
    c0, w0 = time.process_time(), time.perf_counter()
    # Hard CPU ceiling supplements explicit elapsed checks; no science is imported.
    resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
    prior = json.loads((UNIT/'UNIT_START.json').read_text())['packaging']
    pcpu, pwall = prior['charged_prior_CPU_s'], prior['charged_prior_wall_s']
    for p in OUT.glob('*_PACKAGE_RECEIPT.json'):
        r = json.loads(p.read_text()); pcpu += r['incremental_CPU_s']; pwall += r['incremental_wall_s']
    verify_runtime()
    public = public_paths()
    assert UNIT/'implementation/coupled_collision.py' in public
    stage(public, phase)
    pub = archive(OUT/(phase+'_PUBLIC_PORTABLE.zip'), public, UNIT.name+'/')
    private = [p for p in sorted(UNIT.rglob('*')) if eligible(p) and 'delivery' not in p.relative_to(UNIT).parts]
    private += [p for p in sorted(OUT.glob('*.json')) if 'GIT_TREE_PAYLOAD' not in p.name]
    private += [Path(__file__)]
    backup = archive(OUT/(phase+'_PRIVATE_RECOVERY.zip'), private, UNIT.name+'/')
    cpu, wall = time.process_time()-c0, time.perf_counter()-w0
    r = {'phase': phase, 'public': pub, 'private': backup,
         'incremental_CPU_s': cpu, 'incremental_wall_s': wall,
         'charged_cumulative': {'CPU_s': pcpu+cpu, 'wall_s': pwall+wall},
         'caps': {'CPU_s': 30, 'wall_s': 60}, 'phase_caps': {'CPU_s': 2, 'wall_s': 5},
         'historical_conservative_debit_s': 1, 'scientific_evaluations': 0,
         'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'storage': 'PENDING_BACKUP_AGENT_ACK', 'publication_mutations': 0}
    receipt.write_bytes(encoded(r))
    print(json.dumps(r))
    assert cpu < 2 and wall < 5 and pcpu+cpu < 30 and pwall+wall < 60


if __name__ == '__main__':
    main()
