"""Scoped native promotion checks. This never promotes full49/trajectory/production physics."""
from __future__ import annotations
import math

TRUSTED_NATIVE_BLOCKED_LOADER_VARS=('LD_PRELOAD','LD_LIBRARY_PATH')

def sanitize_trusted_native_environment(base_env, **updates):
    """Return a child-only environment accepted by trusted native builders."""
    env=dict(base_env)
    for var in TRUSTED_NATIVE_BLOCKED_LOADER_VARS:
        env.pop(var,None)
    env.update({k:str(v) for k,v in updates.items()})
    return env


def validate_science_regression(data: dict, *, profile_sha256: str, build_key: str) -> dict:
    if data.get('schema') != 'WU088_R31M_SCIENCE_RESOLUTION_NATIVE_REGRESSION_V1':
        raise ValueError('unsupported science regression schema')
    if data.get('tuning_profile_sha256') != profile_sha256:
        raise ValueError('tuning profile identity mismatch')
    if data.get('build_key') != build_key:
        raise ValueError('candidate build identity mismatch')
    if data.get('status') != 'PASS_REPRESENTATIVE_NATIVE_EXACTNESS_NOT_PROMOTED' or data.get('all_exact') is not True:
        raise ValueError('science regression exactness gate not passed')
    if data.get('heavy_pair_state_mutation') is not False:
        raise ValueError('science regression mutated heavy pair state')
    if data.get('production_provider_promoted') is not False:
        raise ValueError('input regression must precede provider promotion')
    selected=data.get('selected') or {}
    threads=selected.get('kernel_threads')
    if not isinstance(threads,int) or threads<1:
        raise ValueError('invalid selected kernel thread count')
    rows=data.get('rows') or []
    required={16.0:0,64.0:0}
    seen=set()
    for row in rows:
        z=float(row.get('z'))
        pair=tuple(row.get('pair') or ())
        if z not in required or len(pair)!=2 or (z,pair) in seen:
            raise ValueError('unexpected or duplicate science regression row')
        seen.add((z,pair));required[z]+=1
        if row.get('numerical_array_exact_equal') is not True or float(row.get('max_abs_component_delta',math.inf)) != 0.0:
            raise ValueError('representative science row is not exact')
        if int(row.get('observed_threads',-1)) != threads:
            raise ValueError('representative science row observed wrong thread team')
    if any(n!=3 for n in required.values()) or len(rows)!=6:
        raise ValueError('representative science regression coverage incomplete')
    return {
        'status':'PASS_SCOPED_FOREIGN_KERNEL_PROMOTION_ELIGIBLE',
        'scope':'FOREIGN_KERNEL_HEAVY_H_SOURCE_ONLY',
        'kernel_threads':threads,
        'processes':int(selected.get('processes',0)),
        'use_smt':bool(selected.get('use_smt',False)),
        'rows':len(rows),
        'full49_admitted':False,
        'trajectory_admitted':False,
        'production_admitted':False,
    }
