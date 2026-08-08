#!/usr/bin/env python3
"""Predeclared source-branch and OTS-energy uncertainty policies."""
from __future__ import annotations

from typing import NamedTuple, Mapping
import numpy as np

V_POLICIES=(
    'CELL_LOWER_STRICT',
    'CELL_UPPER_STRICT',
    'ADAPTER_TABLE_LOW_STRICT',
    'ADAPTER_TABLE_HIGH_STRICT',
)
F_ENDPOINTS=(0.1,1.0)
ENERGY_POLICIES=('ENERGY_LOWER','ENERGY_UPPER')

class UncertaintyPolicy(NamedTuple):
    policy_id: str
    v_policy: str
    f_value: float
    energy_policy: str


def _immutable(values: np.ndarray) -> np.ndarray:
    out=np.ascontiguousarray(values,dtype=np.float64)
    out.setflags(write=False)
    return out


def policy_registry() -> tuple[UncertaintyPolicy,...]:
    rows=[]
    for v_policy in V_POLICIES:
        for f_value in F_ENDPOINTS:
            for energy_policy in ENERGY_POLICIES:
                token=f'{v_policy}__F_{str(f_value).replace(".","P")}__{energy_policy}'
                rows.append(UncertaintyPolicy(token,v_policy,float(f_value),energy_policy))
    return tuple(rows)


def _array(envelope: Mapping[str,np.ndarray],key: str) -> np.ndarray:
    if key not in envelope: raise KeyError(key)
    value=np.asarray(envelope[key])
    if value.ndim!=1: raise ValueError(f'{key} must be one-dimensional')
    return value


def build_v_field(policy: str,envelope: Mapping[str,np.ndarray]) -> np.ndarray:
    if policy not in V_POLICIES: raise KeyError(policy)
    lower=np.asarray(_array(envelope,'v_cell_lower'),dtype=np.float64)
    upper=np.asarray(_array(envelope,'v_cell_upper'),dtype=np.float64)
    adapter=np.asarray(_array(envelope,'v_adapter_central'),dtype=np.float64)
    table=np.asarray(_array(envelope,'table_domain'),dtype=bool)
    below=np.asarray(_array(envelope,'below_table'),dtype=bool)
    above=np.asarray(_array(envelope,'above_table'),dtype=bool)
    n=len(lower)
    if any(len(x)!=n for x in (upper,adapter,table,below,above)):
        raise ValueError('branch envelope arrays have inconsistent lengths')
    if np.any(above):
        raise ValueError('above-table source extrapolation is prohibited')
    domain_count=table.astype(np.int8)+below.astype(np.int8)+above.astype(np.int8)
    if np.any(domain_count!=1):
        raise ValueError('each node must have exactly one temperature-domain label')
    if policy=='CELL_LOWER_STRICT':
        out=np.where(table,lower,0.0)
    elif policy=='CELL_UPPER_STRICT':
        out=np.where(table,upper,1.0)
    elif policy=='ADAPTER_TABLE_LOW_STRICT':
        out=np.where(table,adapter,0.0)
    else:
        out=np.where(table,adapter,1.0)
    if np.any(~np.isfinite(out)) or np.any((out<0.0)|(out>1.0)):
        raise ValueError('v field leaves the probability domain')
    return _immutable(out)


def build_f_field(f_value: float,node_count: int) -> np.ndarray:
    value=float(f_value)
    if value not in F_ENDPOINTS: raise ValueError('f must be a predeclared endpoint')
    if int(node_count)<=0: raise ValueError('node_count must be positive')
    return _immutable(np.full(int(node_count),value,dtype=np.float64))


def load_branch_envelope(path) -> dict[str,np.ndarray]:
    with np.load(path,allow_pickle=False) as data:
        required=('v_cell_lower','v_cell_upper','v_adapter_central','table_domain','below_table','above_table')
        return {key:np.array(data[key],copy=True) for key in required}
