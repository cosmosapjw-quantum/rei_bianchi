from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'rust'/'rei_iso_couple_p2'/'owner_src'
OWNER={
'atomic_provider.rs':'62211d8910cd332fffa8f94c6989cae77128916e',
'igm_rates.rs':'dc3cc028a41ac852d94835372ce13545389d1c3a',
'rate_table.rs':'8bdbe9ec651c4a3560cf9078856bb790a8e47a6b',
'isotope_state.rs':'a47927cea7d060f89ea28e9731608dd89b5ae7b3',
'deuterium_charge_exchange.rs':'dd0a8c9b96ef3e53b8eef0fd08961045779f20b7',
'deuterium_thermal_charge_exchange.rs':'07f8922f93aaf70f727c396621b5e02eb7479223',
'deuterium_atomic.rs':'9d64984fe091b7e0ed1f13e63ce411b4d6ac5632',
'deuterium_thermal_coupling.rs':'75275a7b1a90cc412f7076093745d39cfbc711b8',
'hhe_events.rs':'57a63eee1e9d8c4aa2b5ed663dbea15619359f71',
'igm_thermal.rs':'5bde309d28c21567769a80575d929dd70c42f597'}
results=[]
for name,expected in OWNER.items():
 raw=(P/name).read_bytes();actual=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
 results.append({'name':name,'git_blob':actual,'expected':expected,'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw),'passed':actual==expected})
print(json.dumps({'schema':'rei.iso.p2.owner10.v1','repo':'cosmosapjw-quantum/rei_bianchi','owner_sha':'da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7','status':'PASS' if all(x['passed'] for x in results) else 'FAIL','results':results},indent=2))
if not all(x['passed'] for x in results):sys.exit(2)
