"""Runtime-only extension of the frozen C11 controller; no numerical retuning."""
from __future__ import annotations
import copy
TARGET_TIME_S=4.011926941800233e16
TOTAL_ATTEMPTS=105
TOTAL_ACCEPTED_MACROS=103
RUNTIME_KEYS={'max_attempts','max_accepted_macros','bounded_run_request'}

def require(ok,message):
    if not ok:raise ValueError(message)

def assert_runtime_only_controls(old,new,cursor):
    """Allow precisely the declared full-target runtime cap/start/end changes."""
    require(set(old)==set(new),'FORBIDDEN_CONTROL_CHANGE:keys')
    for key in old.keys()-RUNTIME_KEYS:
        require(old[key]==new[key],'FORBIDDEN_CONTROL_CHANGE:'+key)
    old_req=old['bounded_run_request'];new_req=new['bounded_run_request']
    require(set(old_req)==set(new_req),'FORBIDDEN_CONTROL_CHANGE:bounded_run_keys')
    for key in old_req.keys()-{'start_s','end_s'}:
        require(old_req[key]==new_req[key],'FORBIDDEN_CONTROL_CHANGE:bounded_run_'+key)
    require(new_req['start_s']==cursor['accepted_clock_s'] and new_req['end_s']==TARGET_TIME_S,'FORBIDDEN_RUNTIME_INTERVAL')
    require(type(new['max_attempts']) is int and new['max_attempts']==TOTAL_ATTEMPTS and
            type(new['max_accepted_macros']) is int and new['max_accepted_macros']==TOTAL_ACCEPTED_MACROS,
            'FORBIDDEN_RUNTIME_ALLOCATION')
    require(cursor['attempts']==5 and cursor['accepted_macros']==3 and cursor['rejected_macros']==2 and
            cursor['accepted_boundaries']==6,'PARENT_CURSOR_ALLOCATION_ORIGIN')
    return True

def production_controls(old,cursor):
    new=copy.deepcopy(old)
    new['max_attempts']=TOTAL_ATTEMPTS
    new['max_accepted_macros']=TOTAL_ACCEPTED_MACROS
    new['bounded_run_request'].update(start_s=cursor['accepted_clock_s'],end_s=TARGET_TIME_S)
    assert_runtime_only_controls(old,new,cursor)
    return new
