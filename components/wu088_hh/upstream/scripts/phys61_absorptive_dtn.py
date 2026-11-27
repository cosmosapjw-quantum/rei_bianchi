#!/usr/bin/env python3
"""Source SHA-guarded PHYS61 R5 science producer; standard library only."""
import argparse,json
from pathlib import Path
from wu088_hh.phys61_absorptive_dtn import certified_contract
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);args=p.parse_args()
r=certified_contract(args.source)
Path(args.out).parent.mkdir(parents=True,exist_ok=True)
Path(args.out).write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
print('PHYS61_R5_RATIONAL_PASS '+str(r['science']['dtn_difference_norm_upper']))
