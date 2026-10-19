#!/usr/bin/env python3
"""Create a fresh sparse RUN17 workspace from the observed RUN16 remote SHA."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import platform
import subprocess
import sys

OUT = Path(__file__).resolve().parent
REPO = Path('/tmp/rei_run17_repo')
OLD = Path('/tmp/rei_run16_repo')
SHA = '45ee7192b9d405214ec2650185aeaaa635e0fa13'
TREE = 'e33b14edd675b31e50526be27d77a83bf11a301d'
SCOPES = [f'research/atomic_nuclear_ssot_20261017/run{n}' for n in (10, 13, 15, 16)]
ENV_OVERRIDES = {'GIT_OPTIONAL_LOCKS': '0', 'GIT_TERMINAL_PROMPT': '0',
                 'PYTHONDONTWRITEBYTECODE': '1'}
ENV = dict(os.environ, **ENV_OVERRIDES)
commands = []

def identity(b):
    return {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def write_new(p, b):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb') as f:
        f.write(b)

def dump_new(p, d):
    write_new(p, (json.dumps(d, ensure_ascii=False, indent=2)+'\n').encode())

def call(name, argv, cwd=REPO):
    r = subprocess.run(argv, cwd=cwd, env=ENV, capture_output=True)
    paths = {}
    for key in ('stdout', 'stderr'):
        b = getattr(r, key)
        rel = f'git_logs/{name}.{key}.txt'
        write_new(OUT/rel, b)
        paths[key] = {'path': rel, **identity(b)}
    commands.append({'name': name, 'argv': argv, 'cwd': str(cwd),
                     'exit_code': r.returncode, 'env_overrides': ENV_OVERRIDES, **paths})
    if r.returncode:
        raise RuntimeError(f'{name} exited {r.returncode}: '+r.stderr.decode(errors='replace')[:2000])
    return r.stdout

def old_state():
    r = subprocess.run(['git','rev-parse','HEAD'],cwd=OLD,env=ENV,capture_output=True,check=True)
    run16 = OLD/'research/atomic_nuclear_ssot_20261017/run16'
    files = [{'path':p.relative_to(run16).as_posix(), **identity(p.read_bytes())}
             for p in sorted(run16.rglob('*')) if p.is_file()]
    return {'HEAD':r.stdout.decode().strip(), 'index': identity((OLD/'.git/index').read_bytes()),
            'run16_files': files}

def main():
    if REPO.exists():
        raise SystemExit('Refusing to alter existing RUN17 path')
    before = old_state()
    dump_new(OUT/'PRESERVED_RUN16_BEFORE.json', before)
    REPO.mkdir()
    try:
        call('01_init',['git','init',str(REPO)],OUT)
        call('02_remote',['git','remote','add','origin','https://github.com/cosmosapjw-quantum/rei_bianchi.git'])
        call('03_sparse_init',['git','sparse-checkout','init','--cone'])
        call('04_sparse_scopes',['git','sparse-checkout','set',*SCOPES])
        call('05_fetch',['git','fetch','--depth=1','--filter=blob:none','--no-tags','origin',SHA])
        call('06_checkout',['git','checkout','--detach','FETCH_HEAD'])
        head=call('07_head',['git','rev-parse','HEAD']).decode().strip()
        tree=call('08_tree',['git','rev-parse','HEAD^{tree}']).decode().strip()
        if head!=SHA or tree!=TREE:
            raise ValueError('HEAD/tree differs from observed remote')
        tree_paths=call('09_tree_paths',['git','ls-tree','-r','--name-only','HEAD']).decode().splitlines()
        agent_paths=[p for p in tree_paths if p=='AGENTS.md' or p.endswith('/AGENTS.md')]
        relevant_agents=[p for p in agent_paths if p=='AGENTS.md' or any(
            s.startswith(p.rsplit('/',1)[0]+'/') or p.startswith(s+'/') for s in SCOPES)]
        for i,p in enumerate(relevant_agents):
            b=call(f'10_agent_{i:02d}',['git','show',f'HEAD:{p}'])
            write_new(OUT/'agents'/p,b)
        after=old_state()
        dump_new(OUT/'PRESERVED_RUN16_AFTER.json',after)
        if before!=after:
            raise ValueError('The protected previous canonical state changed concurrently')
        receipt={'status':'ISOLATED_REMOTE_CHECKOUT_PREPARED','remote_commit':head,
                 'remote_tree':tree,'checkout':str(REPO),'sparse_scopes':SCOPES,
                 'observed_all_AGENTS_paths':agent_paths,'applicable_AGENTS_paths':relevant_agents,
                 'old_canonical_HEAD_preserved':before['HEAD'],'old_canonical_index_and_run16_preserved':True,
                 'canonical_existing_untracked_RUN16_not_migrated_or_overwritten':True,
                 'branch_state':'detached at observed RUN16 commit; no RUN17 remote mutation',
                 'native_IVP_runs':0,'tests_run':0,'science_recomputations':0,
                 'source_mutations':0,'remote_mutations':0}
    except Exception as e:
        receipt={'status':'BLOCKED','error_type':type(e).__name__,'error':str(e),
                 'remote_commit':SHA,'no_retry':True}
    receipt.update({'created_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
                    'exact_command':[sys.executable,'-B',str(Path(__file__).resolve())],
                    'environment':{'python':platform.python_version(),'platform':platform.platform()},
                    'commands':commands,'script':identity(Path(__file__).read_bytes())})
    dump_new(OUT/'CHECKOUT_RECEIPT.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k!='commands'},ensure_ascii=False))
    return 0 if receipt['status']=='ISOLATED_REMOTE_CHECKOUT_PREPARED' else 1

if __name__=='__main__':
    raise SystemExit(main())
