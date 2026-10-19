"""Reproduce the bounded fixed-opacity study without touching existing lanes."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--rust-prefix', type=Path, required=True)
    parser.add_argument('--native-input-dir', type=Path)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--repo', type=Path)
    parser.add_argument('--fetch-missing', action='store_true')
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--reuse-export', type=Path)
    parser.add_argument('--bundled-inputs', action='store_true')
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    runtime.mkdir(parents=True, exist_ok=True)
    results = HERE/'results'
    results.mkdir(exist_ok=True)
    commands = []

    def run(name, command, budget=240, env=None, stdout_file=None):
        started = time.monotonic()
        completed = subprocess.run(command, env=env, input='', text=True,
                                   capture_output=True, timeout=budget,
                                   cwd=HERE/'rust' if name.startswith('cargo_') or name=='fixed_data_study' else None)
        stdout = stdout_file or results/(name+'.stdout')
        stdout.write_text(completed.stdout)
        (results/(name+'.stderr')).write_text(completed.stderr)
        receipt = {'name':name, 'command':command, 'exit_code':completed.returncode,
                   'wall_seconds':time.monotonic()-started, 'budget_seconds':budget}
        commands.append(receipt)
        (results/'RUN_COMMANDS.json').write_text(json.dumps(commands, indent=2)+'\n')
        if completed.returncode:
            raise RuntimeError(completed.stderr)
        return completed

    export = (HERE/'inputs' if args.bundled_inputs else
              args.reuse_export.resolve() if args.reuse_export else runtime/'vigilode_native_probe/export')
    if args.reuse_export or args.bundled_inputs:
        receipt = json.loads((export/'EXPORT_RECEIPT.json').read_text())
        assert receipt['exit_code'] == 0
        assert all(receipt['archived_source_exact_comparisons'].values())
        for name, expected in receipt['files'].items():
            assert digest(export/name) == expected, name
    else:
        command = [sys.executable, str(HERE/'prepare_export.py'), '--runtime',
                   str(runtime/'vigilode_native_probe'), '--rust-prefix',str(args.rust_prefix)]
        if not any([args.native_input_dir,args.archive,args.repo,args.fetch_missing]):
            restored = HERE.parent/'intake/native_original_35d9747'
            donor = HERE.parent/'donors/REI_POSITIVE_NATIVE_C9_20261016_v1.zip'
            if restored.is_dir():
                args.native_input_dir = restored
            elif donor.is_file():
                args.archive = donor
            else:
                args.fetch_missing = True
        for name in ['native_input_dir','archive','repo']:
            value = getattr(args,name)
            if value:
                command += ['--'+name.replace('_','-'),str(value)]
        if args.fetch_missing:
            command += ['--fetch-missing']
        run('native_export',command,budget=140)
    inputs=HERE/'inputs'
    inputs.mkdir(exist_ok=True)
    for name in ['nodes.csv','model.json','native_setup.json','EXPORT_RECEIPT.json','command.stdout','command.stderr']:
        if (export/name).resolve() != (inputs/name).resolve():
            shutil.copyfile(export/name,inputs/name)
    env = dict(os.environ)
    env['PATH'] = str(args.rust_prefix/'bin')+os.pathsep+env['PATH']
    env['CARGO_HOME'] = str(runtime/'vigilode_cargo_home')
    env['CARGO_TARGET_DIR'] = str(runtime/'vigilode_target')
    cargo=[str(args.rust_prefix/'bin/cargo')]
    common=['--release','--locked','-j','2','--manifest-path',str(HERE/'rust/Cargo.toml')]
    if args.offline:
        common += ['--offline']
    run('cargo_test',cargo+['test']+common,env=env)
    run('fixed_data_study',cargo+['run']+common+['--',str(inputs),str(results/'STUDY.json')],env=env)
    binary=runtime/'vigilode_target/release/rei-vigilode-age-transport'
    run('exp_fixtures',[str(binary),'--exp-fixtures'],stdout_file=results/'EXP_FIXTURES.json')
    run('independent_verification',[sys.executable,str(HERE/'verify.py')])
    run('summarize',[sys.executable,str(HERE/'summarize.py')])
    print((results/'STUDY.json').read_text()[:400])


if __name__=='__main__':
    main()
