"""Run the exact fixed-input optimized model with cache preload and shared oracle checks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def default_threads():
    count = len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else (os.cpu_count() or 1)
    quota = Path('/sys/fs/cgroup/cpu.max')
    if quota.exists():
        maximum, period = quota.read_text().split()
        if maximum != 'max':
            count = min(count, max(1, int(maximum)//int(period)))
    return max(1, min(8, count))


def positive_integer(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError('threads must be a positive integer')
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--threads', type=positive_integer, default=default_threads())
    parser.add_argument('--label', default='OPTIMIZED')
    parser.add_argument('--binary', type=Path, help='reuse an already built optimized executable')
    parser.add_argument('--runtime', type=Path, help='fresh scratch directory for a reproducible offline build')
    parser.add_argument('--rust-prefix', type=Path, help='installed Rust 1.94.1 prefix; required when building')
    args = parser.parse_args()
    if args.binary is None and (args.runtime is None or args.rust_prefix is None):
        parser.error('provide --binary, or both --runtime and --rust-prefix')
    if not args.label or Path(args.label).name != args.label:
        parser.error('label must be one nonempty filename component')
    baseline = json.loads((HERE/'results/BASELINE_RUN.json').read_text())
    for name in ['inputs/model.json', 'inputs/nodes.csv']:
        data = (HERE.parent/'vigilode_age_transport_20261019'/name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == baseline['identities'][name], name
    binary = args.binary
    if binary is None:
        subprocess.run([sys.executable, str(HERE/'build_variant.py'), '--variant', 'C',
                        '--runtime', str(args.runtime), '--rust-prefix', str(args.rust_prefix)], check=True)
        binary = args.runtime.resolve()/'target_C/release/rei-vigilode-age-transport'
    subprocess.run([sys.executable, str(HERE/'bench.py'), '--label', args.label,
                    '--binary', str(binary), '--threads', str(args.threads),
                    '--preload', '--reuse-oracle'], check=True)


if __name__=='__main__':
    main()
