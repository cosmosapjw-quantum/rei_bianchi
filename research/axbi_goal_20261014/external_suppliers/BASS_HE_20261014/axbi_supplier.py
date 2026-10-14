#!/usr/bin/env python3
"""Read-only cold AXBI normalization and comparison preparation.

No source/RHS/solver imports; no writes to owner DAG, histories or checkpoints.
Fractions are exact interpretations of the transmitted CSV numbers, not true-IVP
error bounds. A stitched history is NOT a full dynamical checkpoint validator.
"""
from __future__ import annotations
import argparse
import csv
import json
from fractions import Fraction as Q
from pathlib import Path
from typing import Iterable, Mapping

Row = Mapping[str, str]
PHYSICAL_FIELDS = ('time_s','a','zbar','x_HII','x_HeII','x_HeIII',
                   'nH_proper_cm3','ne_proper_cm3','temperature_K')


def number(value: object) -> Q:
    """Reject nonfinite input and avoid an implicit float-to-decimal conversion."""
    if isinstance(value, float):
        return Q.from_float(value)  # preserve the already parsed binary number
    try:
        return Q(value)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError('FINITE_NUMERIC_INPUT_REQUIRED') from exc


def helium_ratio(mass_fraction: object) -> Q:
    y=number(mass_fraction)
    if not 0 < y < 1:
        raise ValueError('HELIUM_MASS_FRACTION_DOMAIN')
    return y/(4*(1-y))


def inspect_row(row: Row, mass_fraction: object, absolute_xe_tolerance: object) -> dict:
    """Check a declared source's element and baryon normalizations, without clipping."""
    x,y,z = (number(row[k]) for k in ('x_HII','x_HeII','x_HeIII'))
    nh,ne,temp = (number(row[k]) for k in ('nH_proper_cm3','ne_proper_cm3','temperature_K'))
    tol=number(absolute_xe_tolerance)
    if not(0<=x<=1 and y>=0 and z>=0 and y+z<=1 and nh>0 and ne>=0 and temp>0 and tol>=0):
        raise ValueError('PHYSICAL_DOMAIN_OR_TOLERANCE')
    f=helium_ratio(mass_fraction); xe=x+f*(y+2*z); nb_nh=1+4*f
    ys=((1-x)/nb_nh,x/nb_nh,f*(1-y-z)/nb_nh,f*y/nb_nh,f*z/nb_nh)
    residual=ne/nh-xe
    return {'pass':abs(residual)<=tol, 'helium_number_ratio':f,'xe':xe,'Ye':xe/nb_nh,
            'Y_species':ys,'observed_xe':ne/nh,'charge_residual_per_H':residual,
            'scope':'stored-row normalization only; no physical or IVP error admission'}


def _ordered(rows: list[Row]) -> None:
    if not rows: raise ValueError('EMPTY_SEGMENT')
    times=[number(r['time_s']) for r in rows]
    if any(b<=a for a,b in zip(times,times[1:])):raise ValueError('NONMONOTONE_OR_DUPLICATED_TIME')


def stitch_segments(prefix: list[Row], segment: list[Row]) -> list[Row]:
    """Count one repeated, physically identical boundary row once.

    The caller must separately verify original source/config/numerics, complete
    photon state and cumulative ledger checkpoint identities before a restart.
    This utility cannot authorize restart or compensate missing state.
    """
    _ordered(prefix);_ordered(segment)
    if any(number(prefix[-1][k])!=number(segment[0][k]) for k in PHYSICAL_FIELDS):
        raise ValueError('SEGMENT_BOUNDARY_CLOCK_OR_STATE_MISMATCH')
    result=list(prefix)+list(segment[1:]);_ordered(result)
    return result


def compare_at(reference: Row,candidate: Row,coordinate: str,coordinate_tolerance: object) -> dict:
    """Compare already aligned rows only. No implicit interpolation/extrapolation."""
    fields={'ZBAR':'zbar','PROPER_TIME':'time_s'}
    if coordinate not in fields:raise ValueError('CHOOSE_ZBAR_OR_PROPER_TIME')
    tol=number(coordinate_tolerance)
    if tol<0:raise ValueError('NEGATIVE_COORDINATE_TOLERANCE')
    key=fields[coordinate]
    if abs(number(reference[key])-number(candidate[key]))>tol:
        raise ValueError('REQUESTED_COORDINATE_NOT_MATCHED')
    return {'coordinate':coordinate,'reference_time_s':number(reference['time_s']),
      'candidate_time_s':number(candidate['time_s']),'reference_zbar':number(reference['zbar']),
      'candidate_zbar':number(candidate['zbar']),
      'delta':{k:number(candidate[k])-number(reference[k]) for k in ('x_HII','x_HeII','x_HeIII','temperature_K')},
      'scope':'matched stored-row difference, not detection or convergence certification'}


def response_resolution(delta: object,numerical_indicator: object|None,absolute_floor: object,
                        relative_budget: object=Q(1,10)) -> str:
    """Apply the declared AXBI empirical budget, never infer a rigorous radius.

    A numerical indicator must come from the owner's actual baseline and at least
    two refinement levels. This function neither creates nor validates that data.
    """
    if numerical_indicator is None:return 'NEED_REFINEMENT_EVIDENCE'
    d=abs(number(delta));e=number(numerical_indicator);f=number(absolute_floor);r=number(relative_budget)
    if e<0 or f<0 or not 0<r<1:raise ValueError('RESOLUTION_BUDGET_DOMAIN')
    if d<=f:return 'BELOW_PREDECLARED_FLOOR'
    return 'RESOLVED_EMPIRICAL_ONLY' if e<=r*d else 'UNRESOLVED_NUMERICAL'


def prep_readiness(owner_node_status: Mapping[str,str]) -> dict:
    """Nonmutating supplier split; owner execution/readiness is NOT rewritten."""
    return {'ZERO_CONVERGENCE_PREP':'READY' if owner_node_status.get('AX07')=='COMPLETED' else 'WAIT_FOR_OWNER_AX07',
      'SIGNED_COMPARISON_INTERFACE':'READY',
      'SIGNED_FAMILY_RESULT':'OWNER_REVIEW_REQUIRED' if owner_node_status.get('AX08')=='COMPLETED' else 'WAIT_FOR_OWNER_AX08',
      'launch_authorized':False,'owner_state_modified':False,'readiness_scope':'BASS_HE supplier preparation only'}


def _encode(value: object) -> object:
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {k:_encode(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [_encode(v) for v in value]
    return value


def inspect_csv(path: Path,mass_fraction: object,tolerance: object) -> dict:
    """Stream a real history without loading its photon spectra or changing files."""
    count=failures=0;max_charge=Q(0);previous=None
    with path.open(newline='') as f:
        reader=csv.DictReader(f)
        if not set(PHYSICAL_FIELDS).issubset(reader.fieldnames or []):
            raise ValueError('HISTORY_SCHEMA_MISSING_REQUIRED_FIELDS')
        for row in reader:
            now=number(row['time_s'])
            if previous is not None and now<=previous:raise ValueError('HISTORY_TIME_ORDER')
            result=inspect_row(row,mass_fraction,tolerance)
            failures+=not result['pass'];count+=1;previous=now
            max_charge=max(max_charge,abs(result['charge_residual_per_H']))
    if not count:raise ValueError('EMPTY_HISTORY')
    return {'rows_checked':count,'normalization_failed_rows':failures,'max_charge_residual_per_H':max_charge,
            'status':'PASS_STORED_NORMALIZATION_ONLY' if failures==0 else 'FAIL_STORED_NORMALIZATION',
            'source_RHS_calls':0,'owner_mutations':0}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('history',type=Path);p.add_argument('--helium-mass-fraction',required=True)
    p.add_argument('--xe-tolerance',required=True,help='Explicit same-source absolute electron/H tolerance')
    a=p.parse_args()
    result=inspect_csv(a.history,a.helium_mass_fraction,a.xe_tolerance)
    print(json.dumps(_encode(result),indent=2))
    raise SystemExit(0 if result['normalization_failed_rows']==0 else 1)
if __name__=='__main__':main()
