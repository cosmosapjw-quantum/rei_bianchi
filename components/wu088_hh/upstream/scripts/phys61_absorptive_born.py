#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from wu088_hh.phys61_absorptive_born import science_packet
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);a=p.parse_args()
d=science_packet(a.source)
Path(a.out).parent.mkdir(parents=True,exist_ok=True)
Path(a.out).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
print('PHYS61_C5C8_PASS '+str(d['numerical_scoped_born']))
