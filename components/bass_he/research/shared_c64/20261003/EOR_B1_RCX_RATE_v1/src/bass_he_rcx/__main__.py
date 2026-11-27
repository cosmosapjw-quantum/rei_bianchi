"""Standalone atomic rate/count adapter; no Bianchi or fluid integration."""
import argparse
import json
import sys
from pathlib import Path
from .core import SOURCE_ID, DISTRIBUTION, ContractError, rate, batch, count_coefficients
from .io import write_json_create_only


def main(argv=None):
    parser = argparse.ArgumentParser(prog='bass-he-rcx')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('rate', 'counts', 'batch'):
        p = commands.add_parser(name)
        p.add_argument('temperature', nargs='+' if name == 'batch' else None)
        p.add_argument('--source-id', required=True, choices=[SOURCE_ID])
        p.add_argument('--distribution', required=True, choices=[DISTRIBUTION])
        p.add_argument('--acknowledge-source-conflict', action='store_true')
        p.add_argument('--unit', choices=['m3 s-1', 'cm3 s-1'], default='m3 s-1')
        p.add_argument('--out', type=Path)
    args = parser.parse_args(argv)
    try:
        kw = {'source_id': args.source_id, 'distribution': args.distribution,
              'acknowledge_source_conflict': args.acknowledge_source_conflict, 'unit': args.unit}
        function = {'rate': rate, 'counts': count_coefficients, 'batch': batch}[args.command]
        result = function(args.temperature, **kw)
        if args.out:
            write_json_create_only(args.out, result)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except FileExistsError:
        print('OUTPUT_EXISTS: original bytes retained', file=sys.stderr)
        return 2
    except (ContractError, OSError, UnicodeError) as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
