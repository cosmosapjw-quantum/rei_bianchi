#!/usr/bin/env python3
"""Freeze actually read PHYS30 inputs and source; metadata only, no import/main."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, stat

ROOT = Path(__file__).resolve().parents[1]
def identity(name):
    path = ROOT/name
    assert path.resolve(strict=True) == path.absolute() and path.is_file()
    data = path.read_bytes()
    return {'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
            'mode':format(stat.S_IMODE(path.stat().st_mode),'04o')}
def save(name, obj):
    with (ROOT/name).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(obj,stream,ensure_ascii=False,indent=2);stream.write('\n')

expected = {
 'contributions/numerics/profile_second_order.py':'19232f405f3f8fba77e63c82ffcc2c52f3e0ef8651edfc9cff4fcde77316e859',
 'contributions/numerics/PROTOCOL.json':'74ad883b3bd04d822ed8d0fc5a9bce67509839ce6fad68e4596100f1dae031f2',
 'contributions/theory/DERIVATION_KO.md':'1a334dcf1acc73d2cff227d49a17abfe0612203f7fcfe98c559321bb646c27ef',
 'contributions/theory/THEORY_CLAIMS.json':'cd6db84226092130029e97dfb4b2f259901c895f5db0e88258b819f30d599cb2',
 'PHYSICS_CONTRACT.json':'475ce8957b46ce1440f227cd1a4b8c5fb3979cf237e4c8e52a5e76028cd78a5d',
 'portability/replay_once.py':'fd6f619fa9f3881d2fe506b8f8f3279cd18f0460b5cdf685be1b6b91e65c450f'
}
for path, digest in expected.items():
    assert identity(path)['sha256'] == digest, path
full_reads = [
 'PHYSICS_CONTRACT.json','SOURCE_MANIFEST.json',
 'contributions/theory/DERIVATION_KO.md','contributions/theory/THEORY_CLAIMS.json',
 'contributions/theory/PROVENANCE.json','contributions/theory/PRE_FREEZE_EVENTS.json',
 'contributions/numerics/profile_second_order.py','contributions/numerics/PROTOCOL.json',
 'contributions/numerics/NUMERICS_DESIGN_KO.md','contributions/numerics/PROVENANCE.json',
 'contributions/numerics/PREEXECUTION_CHANGES.json','contributions/numerics/STATIC_CHECKS.json',
 'portability/replay_once.py','portability/REPLAY_PROTOCOL.json',
 'portability/PREPARATION_STATIC_CHECK.json','portability/PREPARATION_READ_MANIFEST.json',
 'owner_tools/first_run.py','evidence/HARNESS_APPLICATION.json'
]
audit = {
 'task':'REI-PHYS30-20261011','recorded_utc':datetime.now(timezone.utc).isoformat(),
 'owner':'/root','classification':'OWNER_INTEGRATION_SELF_REVIEW_NONBLIND',
 'actual_full_semantic_reads':[identity(p) for p in full_reads],
 'code_read_scope':'All718 lines in bounded displayed ranges. Earlier lines1-275 were read before the sole final protocol-SHA literal replacement; final pin at line27 explicitly read and final entire source identity bound.',
 'theory_read_scope':'All666 lines, T30.1-54,19 derived claims and one proposal actually read.',
 'truncation_resolution':'Code main lines650-718 and entire retained porter protocol/source1-240 output were explicitly redisplayed after aggregate truncation; remaining controller source241-end read separately.',
 'assessment':{
   'moments_and_feasible_support':'Product-measure law and fixed common center interval consistent.',
   'envelope_scope':'Hermite/Rolle proof is restricted to the fixed-profile center-mixture class.',
   'implicit_root':'Physical one-sided C2 with exact interior-root premise; stored A-level is distinct.',
   'profile_transfer':'Fixed-W chain rule accounts once for profile curvature and Vsecond; all eleven d contributions retained.',
   'numerator':'Qdd=2(1-mu2), nonzero-A correction retained; exact A1 toy is a falsifiable check because physical A is too small at the frozen scale.',
   'two_algebra_paths':'New six-coefficient triangular quotient recurrence does not call affine update or shared root helper; same physical cache remains shared.',
   'acceptance':'56 preregistered groups with component rows; no sign/order/finite-width acceptance.',
   'execution_boundary':'Only new cached algebra; physical kernel/derivative/root and old programs0. One first and one separate replay at most.'
 },
 'first_controller_prefreeze_change':{'change':'Add -B to interpreter argv to match the preregistered command; no scientific code, input, formula, expected check or tolerance changed.', 'original':identity('owner_tools/versions/first_run_before_B.py'),'final':identity('owner_tools/first_run.py')},
 'timeouts':{'science_protocol_max_seconds':60,'owner_and_replay_stricter_limit_seconds':30,'interpretation':'Both controllers apply the already prepared stricter bound before execution.'},
 'first_main_so_far':0,'replay_so_far':0,'new_physical_kernel_derivative_root_so_far':0,
 'gate':'READY_FOR_ONE_FIRST_MAIN','final_decision':'NOT_YET_EVALUATED_BY_DISTINCT_REVIEWER'
}
save('evidence/OWNER_PREEXECUTION_READ_REVIEW.json',audit)
protocol=json.loads((ROOT/'contributions/numerics/PROTOCOL.json').read_bytes())
names = sorted(set(protocol['required_frozen_paths'] + [
 'SOURCE_MANIFEST.json','contributions/theory/DERIVATION_KO.md',
 'contributions/theory/THEORY_CLAIMS.json','contributions/theory/PROVENANCE.json',
 'evidence/OWNER_PREEXECUTION_READ_REVIEW.json']))
assert [p for p in names if p.endswith('.py')] == [protocol['entrypoint']]
freeze={'task':'REI-PHYS30-20261011','created_utc':datetime.now(timezone.utc).isoformat(),
 'entrypoint':protocol['entrypoint'],'owner_actual_read_gate':'READY_FOR_ONE_FIRST_MAIN',
 'file_count':len(names),'files':[identity(p) for p in names],
 'scope':'Complete new-program execution input closure plus identity-read theory and source metadata. Prior PHYS29 programs are not imported or replayed. Freeze itself is an extra required runtime member, not self-listed.',
 'first_controller':identity('owner_tools/first_run.py'),'replay_controller':identity('portability/replay_once.py'),
 'first_timeout_seconds':30,'sole_first_main_max':1,'separate_replay_max':1,
 'physical_kernel_derivative_root_max':0,'owner_review':'evidence/OWNER_PREEXECUTION_READ_REVIEW.json'}
save('contributions/numerics/PREEXECUTION_FROZEN.json',freeze)
print(json.dumps({'status':'PREFLIGHT_FROZEN_BEFORE_FIRST_MAIN','freeze':identity('contributions/numerics/PREEXECUTION_FROZEN.json'),'file_count':len(names),'scientific_execution':0},ensure_ascii=False))
