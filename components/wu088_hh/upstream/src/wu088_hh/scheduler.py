"""Measured-cost ordering; timing interpolation never interpolates scientific data."""
from __future__ import annotations
import math
from typing import Iterable, Mapping


def order_tasks(tasks: Iterable[tuple], costs: Mapping[tuple[int, int], float]) -> list[tuple]:
    tasks = list(tasks)
    keys = [(int(t[0]), int(t[1])) for t in tasks]
    if len(keys) != len(set(keys)):
        raise ValueError('duplicate pending pair')
    for key in keys:
        c = costs.get(key)
        if c is None or not math.isfinite(c) or c <= 0:
            raise ValueError(f'missing or invalid pair cost: {key}')
    return sorted(tasks, key=lambda t: (-costs[int(t[0]), int(t[1])], int(t[0]), int(t[1])))


def verify_profile(profile: dict, *, driver_sha: str, model_sha: str, g: int, gamma_scale: str) -> None:
    expected = dict(schema='WU088_PAIR_COST_PROFILE_V1',scientific_driver_sha256=driver_sha,
                    model_sha256=model_sha,g=g,gamma_scale=gamma_scale)
    for k,v in expected.items():
        if profile.get(k) != v:
            raise ValueError(f'cost profile {k} mismatch')


def predict_costs(profile: dict, *, n: int, z: float) -> tuple[dict, dict]:
    if n not in (160,192) or not math.isfinite(z):
        raise ValueError('unsupported n or nonfinite z')
    states = profile.get('states', [])
    if not states:
        raise ValueError('empty timing profile')
    parsed = {}
    complete = {(i,j) for i in range(12) for j in range(12)}
    for s in states:
        sn,sz = int(s['n']),float(s['z'])
        if sn not in (160,192) or not math.isfinite(sz) or (sn,sz) in parsed:
            raise ValueError('invalid or duplicate timing state')
        costs={}
        for i,j,c in s['costs']:
            k=(int(i),int(j)); c=float(c)
            if k in costs or k not in complete or not math.isfinite(c) or c<=0:
                raise ValueError('invalid timing sample')
            costs[k]=c
        if set(costs)!=complete:
            raise ValueError('incomplete timing state')
        parsed[sn,sz]=costs
    available_n=sorted({sn for sn,_ in parsed})
    source_n=n if n in available_n else min(available_n,key=lambda sn:abs(n-sn))
    zs=sorted(sz for sn,sz in parsed if sn==source_n)
    target=abs(z)  # performance-only use; this does not admit negative-z science.
    if not zs[0]<=target<=zs[-1]:
        raise ValueError('target geometry outside timing profile')
    lo=max(zz for zz in zs if zz<=target); hi=min(zz for zz in zs if zz>=target)
    w=0 if hi==lo else (target-lo)/(hi-lo)
    scale=(n/source_n)**2
    costs={k:scale*((1-w)*parsed[source_n,lo][k]+w*parsed[source_n,hi][k]) for k in sorted(complete)}
    return costs,dict(source_n=source_n,source_z=[lo,hi],n_scaling=scale,
        costs_are_performance_predictions_only=True,scientific_interpolation=False)
