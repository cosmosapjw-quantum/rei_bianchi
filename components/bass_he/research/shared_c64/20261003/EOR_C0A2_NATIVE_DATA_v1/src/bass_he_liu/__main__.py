"""Command line interface. All values remain source-native unless explicitly converted."""
import argparse
import json
import sys
from pathlib import Path
from .native import ContractError, load_dataset, strict_json
from .products import audit, write_json_create_only


def main(argv=None):
    parser=argparse.ArgumentParser(prog='bass-he-liu')
    parser.add_argument('--root',required=True,type=Path,help='Unpacked, source-bound C0A2 bundle root')
    commands=parser.add_subparsers(dest='command',required=True)
    for name in ('export','audit'):
        p=commands.add_parser(name);p.add_argument('--out',type=Path)
    query=commands.add_parser('sample')
    query.add_argument('channel_id');query.add_argument('energy')
    query.add_argument('--scope',choices=('paper_domain','payload_domain'),default='paper_domain')
    query.add_argument('--unit',choices=('source_native','cm2','m2'),default='source_native')
    query.add_argument('--accept-contextual-unit',action='store_true');query.add_argument('--out',type=Path)
    args=parser.parse_args(argv)
    try:
        ds=load_dataset(args.root/'raw',args.root/'provenance/INPUT_LOCK.json')
        if args.command=='sample':
            out=ds.sample(args.channel_id,args.energy,scope=args.scope,unit=args.unit,
                          accept_contextual_unit=args.accept_contextual_unit)
        elif args.command=='export':out=ds.to_dict()
        else:
            catalog=strict_json((args.root/'provenance/parent_CHANNEL_ENERGY_COVERAGE.json').read_text(encoding='utf-8'))
            out=audit(ds,catalog)
        if args.out:write_json_create_only(args.out,out)
        else:print(json.dumps(out,ensure_ascii=False,allow_nan=False,indent=2))
        return 0
    except FileExistsError:
        print('OUTPUT_EXISTS: no existing file was replaced',file=sys.stderr);return 2
    except (ContractError,OSError,UnicodeError) as exc:
        print(f'{type(exc).__name__}: {exc}',file=sys.stderr);return 2


if __name__=='__main__':
    raise SystemExit(main())
