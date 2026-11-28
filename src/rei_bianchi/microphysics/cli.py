"""Command line for the REI-owned microphysics components."""
import argparse
import json

from . import cr
from .experiment import consume_live, late_cell


def main(argv=None):
    parser=argparse.ArgumentParser(prog='rei-igm',description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    phys=sub.add_parser('electron-births',help='integrate the source-qualified PHYS02 electron spectrum')
    phys.add_argument('--start-s',type=float,default=0.);phys.add_argument('--stop-s',type=float,default=1e10)
    live=sub.add_parser('live-history',help='consume native BASS/REC/REI history and UV exchange ledgers')
    live.add_argument('history');live.add_argument('exchange')
    cell=sub.add_parser('cell',help='apply D/H and optional CR sources at a published gas snapshot')
    cell.add_argument('--native',required=True,help='path to the REI material_exchange executable')
    cell.add_argument('--case',choices=sorted(cr.axbi_snapshots()['rows']),default='SHEAR_PLUS');cell.add_argument('--duration-s',type=float,default=1e10)
    cell.add_argument('--d-over-h',type=float,default=2.5e-5);cell.add_argument('--initial-dii',type=float,default=0.)
    cell.add_argument('--cr-off',action='store_true')
    args=parser.parse_args(argv)
    try:
        if args.command == 'cell':
            result = late_cell(args.native, args.case, args.duration_s, args.d_over_h,
                               args.initial_dii, not args.cr_off)
        elif args.command == 'live-history':
            result = consume_live(args.history, args.exchange)
        else:
            result = cr.integrate_phys02(args.start_s, args.stop_s)
    except (ValueError, OSError, OverflowError) as exc:
        parser.error(str(exc))
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__': main()
