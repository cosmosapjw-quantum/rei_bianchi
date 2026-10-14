#!/usr/bin/env python3
"""Runtime-only classifier bridge for the historical PLUS/EPOCH adapter.

The old validators, receipts, solver observer and terminal logic remain loaded
from their exact files. Only process-identity projections replace handoff scans.
This module never launches a science process.
"""
import importlib.util
import os
from pathlib import Path

from process_identity import TrackedLauncher, member_identity, project_groups, scientific_groups

HERE = Path(__file__).resolve().parent
FULL = HERE.parents[2]
OLD_ADAPTER = FULL / 'post_plus_epoch_dispatch.py'


def _refuse_foreign_owners(groups, allowed_parent, detached_parent_script):
    """Apply the complete execution-position owner set before legacy projection."""
    for members in groups.values():
        for member in members:
            if member['pid'] == os.getpid():
                continue
            identity = member_identity(member)
            if identity is None or identity[0] != 'owner':
                continue
            if (member['pid'] == allowed_parent and
                    identity == ('owner', detached_parent_script, '--start-detached')):
                continue
            raise RuntimeError('OWNER_LIFECYCLE_HOLD')


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install(tracked_launchers):
    """Return the old adapter with classification only projected at runtime.

    The caller supplies acknowledged (leader PID, PGID, start_boot_s, native
    solver basename) records. A permitted group has to match that record.
    """
    tracked = tuple(tracked_launchers)
    if not all(isinstance(item, TrackedLauncher) for item in tracked):
        raise TypeError('TRACKED_LAUNCHER_RECORD_REQUIRED')
    adapter = _load(OLD_ADAPTER, 'plus_classifier_repair_old_adapter')
    old_epoch_handoff = adapter.EPOCH.handoff
    old_plus_handoff = adapter.PLUS.handoff

    def epoch_handoff(groups, allowed_group=None, allowed_parent=None):
        _refuse_foreign_owners(groups, allowed_parent, 'post_cap_epoch_recovery.py')
        projected = project_groups(groups, tracked, allowed_group)
        return old_epoch_handoff(projected, allowed_group=allowed_group,
                                 allowed_parent=allowed_parent)

    def plus_handoff(receipt, groups, allowed_group=None, allowed_parent=None):
        _refuse_foreign_owners(groups, allowed_parent, 'post_plus_dispatch.py')
        projected = project_groups(groups, tracked, allowed_group)
        return old_plus_handoff(receipt, projected, allowed_group=allowed_group,
                                allowed_parent=allowed_parent)

    adapter.EPOCH.handoff = epoch_handoff
    adapter.PLUS.handoff = plus_handoff
    adapter.PLUS.scientific_groups = lambda groups: scientific_groups(groups, tracked)
    adapter.classifier_tracking = tracked
    return adapter
