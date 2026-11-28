"""Explicit source-selected atomic packets, no density or transport evolution."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from .api import (ContractError, export_packet, loads_strict, validate_packet,
                  verify_runtime_bindings, write_packet)
from .registry import sources
from ._io import write_json_create_only


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(prog='bass-he-atomic-export')
    sub=parser.add_subparsers(dest='command',required=True)
    s=sub.add_parser('sources'); s.add_argument('--out',type=Path)
    e=sub.add_parser('export');e.add_argument('request',type=Path);e.add_argument('--out',type=Path,required=True)
    v=sub.add_parser('validate');v.add_argument('packet',type=Path)
    args=parser.parse_args(argv)
    try:
        verify_runtime_bindings()
        if args.command=='sources':
            result=sources()
            if args.out: write_json_create_only(args.out,result)
        elif args.command=='export':
            request=loads_strict(args.request.read_bytes())
            packet=write_packet(args.out,request)
            result={'written':str(args.out),'records':len(packet['records']),
                    'schema':packet['schema'],'physical_accuracy_certified':False}
        else:
            validate_packet(loads_strict(args.packet.read_bytes()))
            result={'packet_consistency_verified':True,'physical_accuracy_certified':False,
                    'verification_semantics':'selected supplier replay; not independent scientific review'}
        if args.command!='sources' or not args.out:
            print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
        return 0
    except FileExistsError:
        print('OUTPUT_EXISTS: existing file preserved',file=sys.stderr);return 2
    except (ContractError,OSError,UnicodeError) as exc:
        print(f'{type(exc).__name__}: {exc}',file=sys.stderr);return 2


if __name__=='__main__':
    raise SystemExit(main())
