"""Atomic internal-state moments only. No heat, stopping, full rate or cosmology."""
import argparse
import json
from pathlib import Path
import sys
from bass_he_liu import ContractError, SourceUnavailable
from bass_he_liu.products import write_json_create_only
from .core import MODEL_ID, MomentProvider
from .products import load_at_root, write_products


def main(argv=None):
    p=argparse.ArgumentParser(prog='bass-he-atomic-moments')
    p.add_argument('--root',type=Path,required=True)
    commands=p.add_subparsers(dest='command',required=True)
    binding=commands.add_parser('provider');binding.add_argument('--out',type=Path)
    export=commands.add_parser('export');export.add_argument('--out',type=Path,required=True)
    export.add_argument('--energy-model',required=True,choices=[MODEL_ID])
    for name in ('sample','functional','heat'):
        q=commands.add_parser(name);q.add_argument('channels',help='One ID or comma-separated nonoverlapping IDs')
        if name=='functional':
            q.add_argument('lo');q.add_argument('hi');q.add_argument('--theta-native',required=True,type=float)
            q.add_argument('--full',action='store_true')
        else:q.add_argument('energy')
        q.add_argument('--energy-model',required=True,choices=[MODEL_ID])
        q.add_argument('--method',choices=['linear_E','loglog'])
        q.add_argument('--scope',choices=['paper_domain','payload_domain'],default='paper_domain')
        q.add_argument('--unit',choices=['source_native','cm2','m2'],default='source_native')
        q.add_argument('--accept-contextual-unit',action='store_true');q.add_argument('--out',type=Path)
    args=p.parse_args(argv)
    try:
        if args.command=='heat':raise SourceUnavailable('HEATING_REQUIRES_RECOIL_AND_ENERGY_RESERVOIR_MODEL')
        if args.command=='export':
            names=write_products(args.root,args.out)
            print(json.dumps({'created':names,'physical_certificate':False}));return 0
        data,provider_binding=load_at_root(args.root)
        if args.command=='provider':out=provider_binding
        else:
            provider=MomentProvider(data,model_id=args.energy_model,method=args.method,scope=args.scope)
            ids=args.channels.split(',')
            kws={'unit':args.unit,'accept_contextual_unit':args.accept_contextual_unit}
            if args.command=='functional':
                out=provider.functional(ids,args.lo,args.hi,theta_native=args.theta_native,require_full=args.full,**kws)
            elif len(ids)==1:out=provider.sample(ids[0],args.energy,**kws)
            else:out=provider.aggregate(ids,args.energy,**kws)
        if args.out:write_json_create_only(args.out,out)
        else:print(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False))
        return 0
    except FileExistsError:
        print('OUTPUT_EXISTS: existing bytes preserved',file=sys.stderr);return 2
    except (ContractError,OSError,UnicodeError) as e:
        print(f'{type(e).__name__}: {e}',file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
