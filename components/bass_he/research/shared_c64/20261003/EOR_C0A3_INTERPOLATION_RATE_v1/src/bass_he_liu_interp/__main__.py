"""Atomic-data-only CLI. Output paths are create-only; no network or runtime launch."""
import argparse
import json
from pathlib import Path
import sys
from bass_he_liu import load_dataset, ContractError
from bass_he_liu.native import strict_json
from bass_he_liu.products import write_json_create_only
from .core import Interpolator, KinematicBinding


def main(argv=None):
    p = argparse.ArgumentParser(prog='bass-he-liu-interp')
    p.add_argument('--root', type=Path, required=True)
    subs = p.add_subparsers(dest='command', required=True)
    q = subs.add_parser('interpolate')
    q.add_argument('channel_id'); q.add_argument('energy')
    q.add_argument('--method', choices=('linear_E','loglog'), required=True)
    for name in ('functional','partial-rate'):
        q = subs.add_parser(name)
        q.add_argument('channel_id'); q.add_argument('lo'); q.add_argument('hi')
        if name == 'functional':
            q.add_argument('--theta-native', type=float, required=True)
        else:
            q.add_argument('--theta-J', type=float, required=True)
            q.add_argument('--binding', type=Path, required=True)
    for q in subs.choices.values():
        q.add_argument('--scope', choices=('paper_domain','payload_domain'), default='paper_domain')
        if q.prog.endswith(('interpolate','functional')):
            q.add_argument('--unit', choices=('source_native','cm2','m2'), default='source_native')
        q.add_argument('--accept-contextual-unit', action='store_true')
        q.add_argument('--out', type=Path)
    args = p.parse_args(argv)
    try:
        d = load_dataset(args.root/'raw', args.root/'provenance/INPUT_LOCK.json')
        obj = Interpolator(d, method=getattr(args,'method','linear_E'), scope=args.scope)
        if args.command == 'interpolate':
            result = obj.evaluate(args.channel_id, args.energy, unit=args.unit,
                                  accept_contextual_unit=args.accept_contextual_unit)
        elif args.command == 'functional':
            result = obj.maxwell_functional(args.channel_id, args.lo, args.hi,
                       theta_native=args.theta_native, unit=args.unit,
                       accept_contextual_unit=args.accept_contextual_unit)
        else:
            data = strict_json(args.binding.read_text(encoding='utf-8'))
            expected = {'energy_scale_J_per_native','reduced_mass_kg','authority'}
            if not isinstance(data,dict) or set(data) != expected:
                raise ContractError('EXACT_BINDING_FIELDS_REQUIRED')
            result = obj.maxwell_partial_rate(args.channel_id, args.lo, args.hi,
                       theta_J=args.theta_J, binding=KinematicBinding(**data),
                       accept_contextual_unit=args.accept_contextual_unit)
        if args.out:
            write_json_create_only(args.out, result)
        else:
            print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
        return 0
    except FileExistsError:
        print('OUTPUT_EXISTS: no file was overwritten', file=sys.stderr)
        return 2
    except (ContractError, OSError, UnicodeError, OverflowError) as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
