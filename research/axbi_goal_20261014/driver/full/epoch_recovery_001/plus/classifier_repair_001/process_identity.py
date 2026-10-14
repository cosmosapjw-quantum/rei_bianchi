#!/usr/bin/env python3
"""Execution-position process identities for the AXBI handoff only.

No data operand or shell command string is searched for an executable name.
"""
from dataclasses import dataclass
from pathlib import Path
import re


OWNERS = frozenset({
    'run_campaign.py', 'recover_queue.py', 'post_cap_dispatch.py',
    'post_plus_dispatch.py', 'post_cap_epoch_recovery.py',
    'post_plus_epoch_dispatch.py', 'recover_plus.py',
})
ACTIVE_FLAGS = frozenset({'--run', '--observe', '--start-detached'})
WRAPPERS = frozenset({'time', 'timeout', 'taskset', 'prlimit'})


class IdentityAmbiguous(RuntimeError):
    pass


@dataclass(frozen=True)
class TrackedLauncher:
    pid: int
    pgid: int
    start_boot_s: float
    native_basename: str

    def __post_init__(self):
        if self.pid <= 0 or self.pgid <= 0 or self.pid != self.pgid or not self.native_basename.startswith('axbi_'):
            raise ValueError('INVALID_TRACKED_LAUNCHER')


def _name(value):
    return Path(value).name


def _take_option(argv, index, zero, one, equals):
    value = argv[index]
    if value in zero:
        return index + 1
    if value in one:
        if index + 1 >= len(argv):
            raise IdentityAmbiguous('WRAPPER_OPTION_MISSING_VALUE')
        return index + 2
    if any(value.startswith(prefix) and len(value) > len(prefix) for prefix in equals):
        return index + 1
    raise IdentityAmbiguous('UNRECOGNIZED_WRAPPER_OPTION:' + value)


def _unwrap_one(argv):
    wrapper = _name(argv[0])
    index = 1
    if wrapper == 'time':
        while index < len(argv) and argv[index].startswith('-'):
            if argv[index] == '--':
                index += 1
                break
            index = _take_option(argv, index,
                                 {'-v', '--verbose', '-p', '--portability', '-a', '--append'},
                                 {'-o', '--output', '-f', '--format'},
                                 {'--output=', '--format='})
    elif wrapper == 'timeout':
        while index < len(argv) and argv[index].startswith('-'):
            if argv[index] == '--':
                index += 1
                break
            index = _take_option(argv, index,
                                 {'--foreground', '--preserve-status', '-v', '--verbose'},
                                 {'-s', '--signal', '-k', '--kill-after'},
                                 {'--signal=', '--kill-after='})
        if index >= len(argv) or not re.fullmatch(r'[0-9]+(?:\.[0-9]+)?[smhd]?', argv[index]):
            raise IdentityAmbiguous('TIMEOUT_DURATION_MISSING')
        index += 1
    elif wrapper == 'taskset':
        if index >= len(argv) or argv[index] not in {'-c', '--cpu-list'}:
            raise IdentityAmbiguous('TASKSET_COMMAND_SLOT_UNKNOWN')
        index = _take_option(argv, index, set(), {'-c', '--cpu-list'}, set())
    elif wrapper == 'prlimit':
        while index < len(argv) and argv[index] != '--':
            index = _take_option(argv, index, set(), {'--as', '--fsize'},
                                 {'--as=', '--fsize='})
        if index >= len(argv):
            raise IdentityAmbiguous('PRLIMIT_COMMAND_SEPARATOR_MISSING')
        index += 1
    else:
        return argv
    if index >= len(argv):
        raise IdentityAmbiguous('WRAPPER_COMMAND_MISSING')
    return argv[index:]


def executable_argv(argv):
    """Return the real command slot after only recognized wrapper options."""
    command = list(argv)
    for _ in range(5):
        if not command:
            return []
        if _name(command[0]) not in WRAPPERS:
            return command
        command = _unwrap_one(command)
    raise IdentityAmbiguous('WRAPPER_DEPTH_EXCEEDED')


def _python_script(command):
    if not command:
        return None
    first = _name(command[0])
    if first.endswith('.py'):
        return first, 0
    if not re.fullmatch(r'(?:python|python[23](?:\.[0-9]+)?)', first):
        return None
    index = 1
    no_value = {'-B', '-E', '-I', '-O', '-OO', '-S', '-s', '-u', '-q', '-v'}
    with_value = {'-W', '-X'}
    while index < len(command):
        arg = command[index]
        if arg == '--':
            index += 1
            break
        if arg in {'-c', '-m'} or arg.startswith(('-c', '-m')):
            return None
        if arg in no_value or arg.startswith(('-W', '-X')) and arg not in with_value or arg.startswith('--check-hash-based-pycs='):
            index += 1
            continue
        if arg in with_value:
            if index + 1 >= len(command):
                raise IdentityAmbiguous('PYTHON_OPTION_MISSING_VALUE')
            index += 2
            continue
        if arg.startswith('-'):
            raise IdentityAmbiguous('PYTHON_SCRIPT_SLOT_UNKNOWN:' + arg)
        break
    if index < len(command) and _name(command[index]).endswith('.py'):
        return _name(command[index]), index
    return None


def member_identity(member):
    """(kind, name, active_flag), or None; native identity uses argv[0]."""
    argv = member.get('argv') or []
    command = executable_argv(argv)
    if not command:
        return None
    native = _name(command[0])
    if native.startswith('axbi_'):
        return ('native', native, None)
    script = _python_script(command)
    if script is None:
        return None
    name, index = script
    if name not in OWNERS:
        return None
    active = next((flag for flag in command[index + 1:] if flag in ACTIVE_FLAGS), None)
    return ('owner', name, active) if active else None


def project_groups(groups, tracked=(), allowed_group=None):
    """Project only execution identities into the unchanged historical checks."""
    tracking = {item.pgid: item for item in tracked}
    if len(tracking) != len(tuple(tracked)):
        raise RuntimeError('DUPLICATE_TRACKED_GROUP')
    if allowed_group is not None and allowed_group not in tracking:
        raise RuntimeError('ALLOWED_GROUP_START_IDENTITY_REQUIRED')
    projected = {}
    for pgid, members in groups.items():
        record = tracking.get(pgid)
        if record and members:
            leaders = [m for m in members if m['pid'] == record.pid]
            if leaders and (len(leaders) != 1 or leaders[0].get('start_boot_s') != record.start_boot_s):
                raise RuntimeError('TRACKED_LAUNCHER_START_IDENTITY_CHANGED')
            if not leaders and min(m.get('start_boot_s', -1) for m in members) < record.start_boot_s:
                raise RuntimeError('TRACKED_LAUNCHER_GROUP_IDENTITY_AMBIGUOUS')
        out = []
        for member in members:
            clone = dict(member)
            identity = member_identity(member)
            if identity is None:
                clone['argv'] = [_name(member['argv'][0])] if member.get('argv') else []
            elif identity[0] == 'native':
                clone['argv'] = [identity[1]]
            else:
                clone['argv'] = [identity[1], identity[2]]
            out.append(clone)
        if record and out and not any(m['argv'] and m['argv'][0].startswith('axbi_') for m in out):
            out[0]['argv'] = [record.native_basename]
        projected[pgid] = out
    return projected


def scientific_groups(groups, tracked=()):
    return {pgid for pgid, members in project_groups(groups, tracked).items()
            if any(m['argv'] and m['argv'][0].startswith('axbi_') for m in members)}
