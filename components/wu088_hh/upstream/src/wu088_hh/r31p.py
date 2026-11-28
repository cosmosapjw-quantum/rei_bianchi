"""R31P direct midpoint preregistration and planning.

This module records the already-frozen R31J midpoint/interpolation contract.
It does not evaluate interpolation or admit trajectory/production physics.
"""
from __future__ import annotations
import hashlib
import math
import os
from pathlib import Path
import stat
import struct

MIDPOINTS=(4,12,24,40,56)
H_ORDERS=(160,192)
CP4_REUSED_IONIC=frozenset({4,12,24})
CP4_IONIC_EXECUTABLE_SHA256={
    'duffy_polar_double':'16bdcd528c53193ed53bfe371e74b804644c1b3491e014ac6f088f2d3667bf75',
    'duffy_polar':'36ed3a81c76ce6fe95bb7fbde43d3931d5e817ed66951ba3ac2ff0aed8d8fb0f',
    'diagonal':'9df0b914fca2d3df26681d3476aec5d878eae199684e580eb9544177d03ff560',
    'half_hermite':'dfbc2b434beecdfe4354fb18dca28ee3172c6f8e3957050464f4809c48de99ff',
}

def ensure_cp4_ionic_executables(cp4_root)->dict:
    """Restore owner execute permission only for provenance-bound CP4 ELF bytes."""
    base=Path(cp4_root)/'completion/ionic'
    rows={}
    for name,expected in CP4_IONIC_EXECUTABLE_SHA256.items():
        p=base/name
        if not p.is_file(): raise FileNotFoundError(p)
        data=p.read_bytes()
        got=hashlib.sha256(data).hexdigest()
        if got!=expected: raise ValueError(f'CP4 ionic executable hash mismatch: {name}')
        if not data.startswith(b'\x7fELF'): raise ValueError(f'CP4 ionic executable is not ELF: {name}')
        before=stat.S_IMODE(p.stat().st_mode)
        p.chmod(before|stat.S_IXUSR)
        after=stat.S_IMODE(p.stat().st_mode)
        if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
            raise RuntimeError(f'CP4 ionic executable bytes changed during mode repair: {name}')
        if not os.access(p,os.X_OK):
            raise PermissionError(f'CP4 ionic executable remains non-executable: {name}')
        rows[name]={'sha256':expected,'mode_before':oct(before),'mode_after':oct(after),'owner_execute_restored':not bool(before&stat.S_IXUSR)}
    return {'status':'CP4_IONIC_EXECUTABLE_MODES_VERIFIED','executables':rows}


def interpolation_contract()->dict:
    return {
        'method':'piecewise_linear_only_after_midpoint_validation',
        'H_midpoint_max_abs_Eh':2e-7,
        'whitened_independent_generator_relative_error':2e-12,
        'interpolated_raw_gates_must_also_pass':True,
        'adaptive_rule':'bisect_only_failing_intervals',
        'minimum_interval_width_a0':1.0,
        'on_failure':'STOP_INTERPOLATION_RESOLUTION_UNRESOLVED',
    }


def h_folder_name(n:int,z:float,g:int=80,scale:str='unit')->str:
    if n not in H_ORDERS or g!=80 or scale!='unit':
        raise ValueError('R31P H source uses only frozen B160/B192 g80 unit-scale contract')
    z=float(z)
    if not math.isfinite(z) or z not in MIDPOINTS:
        raise ValueError('z is not a preregistered R31P midpoint')
    return f'B{n}_g{g}_s{scale}_z{struct.pack(">d",z).hex()}'


def midpoint_plan(*,existing_ionic_nodes)->dict:
    existing={int(z) for z in existing_ionic_nodes}
    if existing != set(CP4_REUSED_IONIC):
        raise ValueError('ionic reuse set must be exactly preregistered CP4 midpoint nodes 4,12,24')
    return {
        'schema':'WU088_R31P_MIDPOINT_DIRECT_PLAN_V1',
        'midpoints':list(MIDPOINTS),
        'h_orders':list(H_ORDERS),
        'od_z':list(MIDPOINTS),
        'jvp_z':list(MIDPOINTS),
        'ionic_reuse':sorted(CP4_REUSED_IONIC),
        'ionic_compute':[z for z in MIDPOINTS if z not in CP4_REUSED_IONIC],
        'interpolation_contract':interpolation_contract(),
        'interpolation_evaluated':False,
        'trajectory_runs':0,
        'trajectory_admitted':False,
        'production_admitted':False,
    }
