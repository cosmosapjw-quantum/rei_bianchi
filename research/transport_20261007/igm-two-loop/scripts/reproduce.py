"""Portable offline replay. Python standard library and Rust are sufficient.

Compile and numerical phases are measured separately. Existing evidence is never
overwritten: the requested output directory must be new. Read the scope in README.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

p = argparse.ArgumentParser()
p.add_argument('--output', type=Path, required=True)
p.add_argument('--loop', choices=['1', 'all'], default='all')
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
root = Path(__file__).resolve().parents[1]
env = dict(os.environ, CARGO_TARGET_DIR=str(out / 'target'), RUST_TEST_THREADS='1')
records = []
def source_identity():
    paths = [root / 'Cargo.toml', root / 'CONTRACT.json']
    for directory in ['src', 'tests', 'scripts', 'examples']:
        paths.extend(x for x in (root / directory).glob('**/*') if x.is_file() and '__pycache__' not in x.parts)
    return {str(x.relative_to(root)): hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(paths)}
identity = source_identity()
(out / 'INPUT_SOURCE_SHA256.json').write_text(json.dumps(identity, indent=2) + '\n')

def run(label, cmd, compile=False, stdout=None):
    begin = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU, (120, 120))
        if not compile:
            resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2, 512 * 1024**2))
    with (stdout or out / (label + '.stdout')).open('w') as so, (out / (label + '.stderr')).open('w') as se:
        try:
            rc = subprocess.run(cmd, cwd=root, env=env, stdout=so, stderr=se,
                                timeout=180, preexec_fn=limits).returncode
        except subprocess.TimeoutExpired:
            rc = 124
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    records.append({'label': label, 'phase': 'compile' if compile else 'numerical',
                    'command': [str(x) for x in cmd], 'exit_code': rc,
                    'wall_seconds': time.monotonic() - begin,
                    'cpu_seconds': after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
                    'children_high_water_rss_KiB': after.ru_maxrss})
    (out / 'RESOURCE_RECEIPT.json').write_text(json.dumps(records, indent=2) + '\n')
    if rc:
        raise SystemExit(f'{label} failed ({rc}); preserved stdout/stderr in {out}')

rustc = shutil.which('rustc')
cargo = shutil.which('cargo')
if not rustc or not cargo:
    raise SystemExit('Set PATH to a working Rust toolchain (tested Rust 1.94.1).')
run('cargo_build_tests', [cargo, 'test', '--offline', '--no-run'], compile=True)
run('cargo_tests', [cargo, 'test', '--offline'])
for kind in ['panel', 'tail']:
    binary = out / (kind + '_probe')
    run(kind + '_compile', [rustc, '--edition=2021', '-O', str(root / 'scripts' / (kind + '_probe.rs')), '-o', str(binary)], compile=True)
    if kind == 'panel':
        data = out / (kind + '.csv')
        run(kind + '_probe', [str(binary)], stdout=data)
        run(kind + '_oracle', [sys.executable, str(root / 'scripts/check_panel.py'),
                              '--input', str(data), '--output', str(out / 'panel_oracle.json')])
    else:
        run('tail_oracle', [sys.executable, str(root / 'scripts/check_tail.py'),
                           '--probe', str(binary), '--output', str(out / 'tail_oracle')])
if a.loop == 'all':
    binary=out / 'tail_anchor_probe'
    run('tail_anchor_compile',[rustc,'--edition=2021','-O',str(root / 'scripts/tail_anchor_probe.rs'),'-o',str(binary)],compile=True)
    run('tail_anchor_oracle',[sys.executable,str(root / 'scripts/check_tail_anchor.py'),'--probe',str(binary),'--output',str(out / 'tail_anchor_oracle')])
    run('loop2_compile', [cargo, 'build', '--offline', '--release', '--example', 'loop2'], compile=True)
    run('loop2_candidate', [str(out / 'target/release/examples/loop2')], stdout=out / 'loop2.csv')
    run('loop2_oracle', [sys.executable, str(root / 'scripts/check_loop2.py'), '--input', str(out / 'loop2.csv'), '--output', str(out / 'loop2_oracle.json')])
if source_identity() != identity:
    raise SystemExit('Source changed during replay; outputs retained but not a final-source certificate.')
print(f'Replay passed; raw evidence and measured resource receipts: {out}')
