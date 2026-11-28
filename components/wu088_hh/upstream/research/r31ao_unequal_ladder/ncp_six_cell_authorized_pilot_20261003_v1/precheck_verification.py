"""Pre-dispatch rejection checks only; never calls adapter run/worker/consume."""
from common import *
from execution_entry import static_checks
import ast,subprocess
T=R/'precheck_tests'
T.mkdir(exist_ok=True)
results=[]
def rejected(name,call):
 try:call()
 except (ValueError,OSError) as exc:results.append(dict(check=name,result='REJECTED_BEFORE_DISPATCH',error=str(exc)))
 else:raise AssertionError(name+' did not reject')
q=c.load(PROPOSAL);q['limits']['radius_exp']=-56
if not (T/'changed_policy.json').exists():write(T/'changed_policy.json',q)
assert c.load(T/'changed_policy.json')==q
rejected('invalid_proposal_self_hash',lambda:static_checks(T/'changed_policy.json'))
if not (T/'changed_byte_identity.json').exists():(T/'changed_byte_identity.json').write_bytes(PROPOSAL.read_bytes()+b'\n')
assert (T/'changed_byte_identity.json').read_bytes()==PROPOSAL.read_bytes()+b'\n'
rejected('valid_self_hash_but_changed_file_bytes',lambda:static_checks(T/'changed_byte_identity.json'))
rejected('missing_authorization',lambda:static_checks(authorization_path=T/'ABSENT_AUTHORIZATION.json'))
rejected('consumed_scope_refusal',lambda:assert_unconsumed(dict(scope_consumed=True)))
before=registry_inventory();assert_unconsumed(before)
q,p,m,h,verified=static_checks();write(E/'STATIC_IDENTITY_VERIFICATION.json',verified)
for filename in ('common.py','observe.py','execution_entry.py','precheck_verification.py'):
 ast.parse((R/filename).read_text(),filename=filename)
assert subprocess.run(['/bin/sh','-n',str(R/'namespace_entry.sh')]).returncode==0
after=registry_inventory();assert after==before;assert not (E/'ADAPTER_INVOCATION.json').exists()
write(E/'LAUNCHER_PRECHECK_VERIFICATION.json',dict(negative_checks=results,negative_check_count=4,syntax='PASS',original_adapter_run_worker_consume_test_calls=0,registry_unchanged=True,science_dispatch_count=0,changed_test_document_is_not_science_input=True,launcher_sources=[ref(R/n) for n in ('common.py','observe.py','execution_entry.py','namespace_entry.sh','precheck_verification.py')]))
print(json.dumps(dict(negative_checks=4,syntax='PASS',static='PASS',science_dispatch_count=0,scope_consumed=False)))
