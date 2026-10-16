#!/usr/bin/env python3
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
checks={
 'atomic_provider.rs':'62211d8910cd332fffa8f94c6989cae77128916e',
 'igm_rates.rs':'dc3cc028a41ac852d94835372ce13545389d1c3a',
 'rate_table.rs':'8bdbe9ec651c4a3560cf9078856bb790a8e47a6b',
 'deuterium_atomic.rs':'9d64984fe091b7e0ed1f13e63ce411b4d6ac5632',
 'deuterium_charge_exchange.rs':'dd0a8c9b96ef3e53b8eef0fd08961045779f20b7',
 'deuterium_thermal_charge_exchange.rs':'07f8922f93aaf70f727c396621b5e02eb7479223',
 'deuterium_thermal_coupling.rs':'75275a7b1a90cc412f7076093745d39cfbc711b8',
 'isotope_state.rs':'a47927cea7d060f89ea28e9731608dd89b5ae7b3'
}
for name,expected in checks.items():
 p=ROOT/'rust/rei_iso_couple_reference/owner_src'/name
 a=p.read_bytes()
 git=hashlib.sha1(f'blob {len(a)}\0'.encode()+a).hexdigest()
 assert git==expected, f'OWNER_SOURCE_BLOB_MISMATCH {name} {git} != {expected}'
print('PASS_EIGHT_GIT_BLOBS_MATCH_PR150',len(checks))
