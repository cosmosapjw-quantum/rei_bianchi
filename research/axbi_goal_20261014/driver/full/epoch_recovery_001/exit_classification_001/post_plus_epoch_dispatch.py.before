#!/usr/bin/env python3
"""Existing reviewed PLUS execution glue, exact historical inputs, new handoff."""
import argparse
import json
import os
import pathlib
import sys
sys.dont_write_bytecode = True
import importlib.util
HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('epoch_recovery_for_plus', HERE/'post_cap_epoch_recovery.py')
EPOCH = importlib.util.module_from_spec(spec); spec.loader.exec_module(EPOCH)
PLUS = EPOCH.load(HERE/'post_plus_dispatch.py','epoch_plus_existing_glue')
# No old files are modified. Historical SHA relation is exactly two known paths.
PLUS.digest = EPOCH.historical_digest
_original_validate = PLUS.validate
PLUS.RECOVER.frozen_module = lambda: type('HistoricalPlan', (), {'frozen_plan': staticmethod(EPOCH.frozen_plan)})()
PLUS.OWN = EPOCH.AREA/'plus'
PLUS.RUNTIME = PLUS.OWN/'runtime_001'


def validate():
    EPOCH.validate()
    return _original_validate()


def carried_receipt(receipt):
    if receipt.get('status') != 'COMPLETED_EPOCH_RECOVERY' or receipt.get('remaining_signed_queue') != []:
        raise RuntimeError('RECOVERED_CLASSIFIED_TERMINAL_REQUIRED')
    if [receipt.get(k) for k in ['original_actual_starts','continuation_actual_starts','total_full_starts','prior_pilot_starts','prior_and_current_starts']] != [5,1,6,3,9]:
        raise RuntimeError('RECOVERED_CARRIED_COUNTS_UNKNOWN')
    if {r.get('case') for r in receipt.get('original_results',[])} != {'ZERO','SHEAR_PLUS','SHEAR_MINUS','SHEAR_HALF_PLUS','SHEAR_HALF_MINUS'}:
        raise RuntimeError('RECOVERED_ORIGINAL_OUTCOMES_UNKNOWN')
    for result in receipt['original_results']:
        if not ((result.get('status') == 'COMPLETE_EXIT_0' and result.get('exit_code') == 0) or (result.get('typed_stop') == 'ACCEPTED_STEP_CAP' and result.get('exit_code') == 101)):
            raise RuntimeError('RECOVERED_OUTCOME_UNCLASSIFIED')
    if receipt.get('zero_result',{}).get('status') != 'SUCCESS' or receipt['zero_result'].get('exit_code') != 0:
        raise RuntimeError('RECOVERED_ZERO_UNKNOWN')
    return dict(original_actual_starts=5, ZERO_actual_starts=1, PLUS_attempted_starts=0, total_full_starts=6, prior_pilot_starts=3, all_history_starts=9, start_ceilings=dict(original=5,ZERO=1,PLUS=1,full=7,all_history=10), preserved_old_receipt=receipt)


def fresh_handoff(allowed_group=None, allowed_parent=None):
    groups=EPOCH.RECOVER.process_groups()
    # The only permitted parent is this adapter's detached startup command.
    filtered={}
    for pgid,members in groups.items():
        filtered[pgid]=[m for m in members if not (m['pid']==allowed_parent and '--start-detached' in m['argv'] and any(pathlib.Path(arg).name=='post_plus_epoch_dispatch.py' for arg in m['argv']))]
    EPOCH.handoff(filtered,allowed_group=allowed_group)
    saved=json.loads(EPOCH.RECEIPT.read_text())
    original,cases=EPOCH.validate()
    actual=EPOCH.reconcile(original,cases,require_half=True,allowed_group=allowed_group,groups=filtered)
    # Existing PLUS group is allowed during streaming; revalidation is otherwise
    # identical and terminal artifacts/old chain remain exact.
    if saved != actual:
        raise RuntimeError('RECOVERED_RECEIPT_CHAIN_CHANGED')
    if saved['preserved_stale_receipt_sha256'] != EPOCH.digest(EPOCH.OLD_RECEIPT):
        raise RuntimeError('STALE_RECEIPT_CHANGED')
    carried=carried_receipt(saved)
    carried['old_receipt_sha256']=EPOCH.digest(EPOCH.RECEIPT)
    # Old PLUS reservation/output and new reservation both block duplicate launch.
    if PLUS.OWN != EPOCH.HERE/'post_plus_001/dispatch' and (EPOCH.HERE/'post_plus_001/dispatch/runtime_001').exists():
        raise RuntimeError('OLD_PLUS_ALREADY_RESERVED')
    return carried,groups


PLUS.validate=validate
PLUS.fresh_handoff=fresh_handoff
# The retained detached function invokes the original module __file__; supply
# this adapter entrypoint only for spawning, after historical validation.

def detached():
    validate(); fresh_handoff()
    if PLUS.RUNTIME.exists(): raise RuntimeError('PLUS_ALREADY_RESERVED')
    PLUS.OWN.mkdir(parents=True,exist_ok=True)
    with (PLUS.OWN/'observer.stdout').open('xb') as out,(PLUS.OWN/'observer.stderr').open('xb') as err:
        proc=PLUS.subprocess.Popen([sys.executable,str(__file__),'--observe'],cwd=EPOCH.ROOT,stdin=PLUS.subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True,close_fds=True)
    PLUS.save(PLUS.OWN/'DETACHED_START.json',dict(pid=proc.pid,status='OBSERVER_STARTED_NOT_SCIENCE_ACKNOWLEDGEMENT'))
    print(proc.pid)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); actions=parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--start-detached',action='store_true'); actions.add_argument('--observe',action='store_true')
    args=parser.parse_args()
    if args.start_detached: detached()
    else: raise SystemExit(PLUS.observe())
