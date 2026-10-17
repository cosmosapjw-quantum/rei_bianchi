#!/usr/bin/env python3
import csv,math,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
for name,expect in [('REPLAY_POSITIVE_CAMPAIGN.csv','p3_positive_campaign_matched.csv'),('REPLAY_GEOMETRY.csv','p3_geometric_age.csv')]:
    a=(P/'evidence'/name).read_bytes();b=(P/'evidence'/expect).read_bytes()
    if a!=b:
        # preserve strict byte identity as one witness, before any looser numeric comparison
        raise SystemExit('REPLAY_BYTE_MISMATCH_'+name)
rows=list(csv.DictReader((P/'evidence/REPLAY_POSITIVE_CAMPAIGN.csv').open()))
assert len(rows)==32
for row in rows:
    em=float(row['emitted_com_m3']); n=float(row['photons_com_m3']);absn=float(row['absorbed_com_m3'])
    assert abs(em-absn-n)/em<4e-11
    assert float(row['max_step_energy_error'])<3e-10
print('PASS_RESTORED_CSV_BYTE_PARITY',len(rows))
