"""Build a frozen benchmark variant in scratch without changing research sources."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
RUST = HERE.parent/'vigilode_age_transport_20261019/rust'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', choices=['baseline', 'A', 'B', 'C'], required=True)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--rust-prefix', type=Path, required=True)
    parser.add_argument('--reference-check', action='store_true')
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    crate = runtime/('source_'+args.variant)
    assert not crate.exists(), 'use a fresh scratch runtime; preserve prior builds'
    crate.mkdir(parents=True)
    shutil.copytree(RUST/'src', crate/'src')
    shutil.copytree(RUST/'.cargo', crate/'.cargo')
    (crate/'vendor').symlink_to(RUST/'vendor', target_is_directory=True)
    shutil.copyfile(RUST/'Cargo.lock', crate/'Cargo.lock')
    cargo_toml = RUST/'Cargo.toml'
    if args.variant in ['baseline', 'A']:
        for name in ['main.rs', 'certified.rs']:
            source = HERE/'baseline_source'/('A_certified.rs' if args.variant=='A' and name=='certified.rs' else 'src/'+name)
            shutil.copyfile(source, crate/'src'/name)
        if args.variant=='baseline':
            cargo_toml = HERE/'baseline_source/Cargo.toml'
    elif args.variant=='B':
        for name in ['main.rs', 'certified.rs']:
            shutil.copyfile(HERE/'baseline_source/B'/name, crate/'src'/name)
        cargo_toml = HERE/'baseline_source/B/Cargo.toml'
    shutil.copyfile(cargo_toml, crate/'Cargo.toml')
    env = dict(os.environ, PATH=str(args.rust_prefix.resolve()/'bin')+os.pathsep+os.environ['PATH'],
               CARGO_HOME=str(runtime/'cargo_home'), CARGO_TARGET_DIR=str(runtime/('target_'+args.variant)))
    command = [str(args.rust_prefix.resolve()/'bin/cargo'), 'build', '--release', '--offline', '--locked', '-j', '2']
    if args.reference_check:
        assert args.variant!='baseline'
        command += ['--features', 'reference-check']
    start = time.monotonic()
    result = subprocess.run(command, cwd=crate, env=env, capture_output=True, text=True, timeout=240)
    (runtime/(args.variant+'_build.stdout')).write_text(result.stdout)
    (runtime/(args.variant+'_build.stderr')).write_text(result.stderr)
    receipt = {'command': command, 'cwd': str(crate), 'exit_code': result.returncode,
               'wall_seconds': time.monotonic()-start,
               'binary': str(runtime/('target_'+args.variant)/'release/rei-vigilode-age-transport')}
    (runtime/(args.variant+'_build.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    assert result.returncode==0, result.stderr


if __name__=='__main__':
    main()
