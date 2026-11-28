"""Create-only PHYS84 application. No computation on a verified resume.

Persistence is separate from its callback so tests use mock callbacks exclusively.
Existing incomplete/corrupt directories are always refused and retained.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

from source_adapter import SavedSource, UNIT, PARENT, PINS, CONTRACT_SHA, ROUTES, sha

LEASE_REL = 'source/vendor/phys78_run_pilot.py'
LEASE_SHA = '76ff57ba687fd9830b84c3fcff69eb8ed0e9f6ceab4551e61c67c84d3ea65124'


def encoded(obj):
    return (json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def write_new(path, data):
    with Path(path).open('xb') as stream:
        stream.write(data)


def build_identity():
    if sha((UNIT/'CONTRACT.json').read_bytes()) != CONTRACT_SHA:
        raise ValueError('ADAPTER_CONTRACT_PIN_MISMATCH')
    for name, pin in PINS.items():
        if sha((PARENT/name).read_bytes()) != pin:
            raise ValueError('PARENT_INPUT_PIN_MISMATCH:'+name)
    if sha((PARENT/LEASE_REL).read_bytes()) != LEASE_SHA:
        raise ValueError('LEASE_SOURCE_PIN_MISMATCH')
    code = {p.name:sha(p.read_bytes()) for p in sorted((UNIT/'source').glob('*.py'))}
    return {'schema':'PHYS84_APPLICATION_IDENTITY_V1','adapter_contract_SHA256':CONTRACT_SHA,
            'code_SHA256':code,'fixture_SHA256':sha((UNIT/'source/fixtures.json').read_bytes()),
            'parent_input_SHA256':PINS,'lease_source_SHA256':LEASE_SHA,
            'dependency_pins':{'libraries':'stdlib only; binary64 Python float and math.fsum'},
            'constructed_states':8,'routes_per_state':2,'expected_rows':16,
            'old_scientific_callbacks':0,'new_rate_evaluations':0,'new_population_solves':0,'new_ODE':0}


def persist(output, identity, callback, *, resume=False, allow_new=False):
    output = Path(output)
    ident_bytes = encoded(identity)
    if output.exists():
        if not resume:
            raise FileExistsError('CREATE_ONLY_OUTPUT_EXISTS')
        expected_files = {'IDENTITY.json','source_rows.json','COMPLETE.json'}
        if {p.name for p in output.iterdir()} != expected_files:
            raise ValueError('INCOMPLETE_OR_EXTRA_OUTPUT_FILES')
        ib = (output/'IDENTITY.json').read_bytes()
        rb = (output/'source_rows.json').read_bytes()
        complete_bytes = (output/'COMPLETE.json').read_bytes()
        complete = json.loads(complete_bytes)
        expected = {'schema':'PHYS84_COMPLETE_V1','status':'COMPLETE',
                    'identity_SHA256':sha(ident_bytes),'result_SHA256':sha(rb),
                    'result_bytes':len(rb),'row_count':16}
        rows = json.loads(rb)
        if ib != ident_bytes or complete != expected or encoded(complete) != complete_bytes or not isinstance(rows,list) or len(rows)!=16:
            raise ValueError('CORRUPTED_OR_MISMATCHED_COMPLETION')
        # Canonical byte representation prevents semantically similar byte edits.
        if encoded(rows) != rb:
            raise ValueError('RESULT_BYTES_NOT_CANONICAL')
        return {'status':'VERIFIED_COMPLETED_SKIP','callback_calls':0,'result_SHA256':sha(rb)}
    if resume:
        raise FileNotFoundError('RESUME_REQUIRES_EXISTING_COMPLETION')
    if not allow_new:
        raise ValueError('EXPLICIT_NEW_APPLICATION_AUTHORIZATION_REQUIRED')
    output.mkdir(parents=False,exist_ok=False)
    write_new(output/'IDENTITY.json',ident_bytes)
    rows = callback()
    if not isinstance(rows,list) or len(rows)!=16:
        raise ValueError('EXPECTED_16_CALLBACK_ROWS')
    result = encoded(rows)
    write_new(output/'source_rows.json',result)
    complete = {'schema':'PHYS84_COMPLETE_V1','status':'COMPLETE',
                'identity_SHA256':sha(ident_bytes),'result_SHA256':sha(result),
                'result_bytes':len(result),'row_count':len(rows)}
    write_new(output/'COMPLETE.json',encoded(complete))
    return {'status':'NEW_APPLICATION_COMPLETE','callback_calls':1,'rows':len(rows),'result_SHA256':sha(result)}


def real_callback():
    source = SavedSource()
    fixtures = json.loads((UNIT/'source/fixtures.json').read_bytes())
    if fixtures != source.contract['application']['fixtures']:
        raise ValueError('FIXTURE_CONTRACT_MISMATCH')
    rows = []
    for fixture in fixtures:
        state = {k:v for k,v in fixture.items() if k!='id'}
        for route in ROUTES:
            row = source.evaluate(state,radiation_route=route,
                radiative_owner='detached_own_spontaneous',excited_state_owner='explicit_1S_2S_2P',
                native_radiative_owner_active=False)
            row['fixture_id'] = fixture['id']
            row['application_identity_SHA256'] = sha(encoded(build_identity()))
            rows.append(row)
    return rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--authorize-new-16row-application',action='store_true')
    args=parser.parse_args()
    if args.resume and args.authorize_new_16row_application:
        raise ValueError('NEW_AND_RESUME_ARE_MUTUALLY_EXCLUSIVE')
    identity=build_identity()
    result=persist(args.output,identity,real_callback,resume=args.resume,
                   allow_new=args.authorize_new_16row_application)
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    main()
