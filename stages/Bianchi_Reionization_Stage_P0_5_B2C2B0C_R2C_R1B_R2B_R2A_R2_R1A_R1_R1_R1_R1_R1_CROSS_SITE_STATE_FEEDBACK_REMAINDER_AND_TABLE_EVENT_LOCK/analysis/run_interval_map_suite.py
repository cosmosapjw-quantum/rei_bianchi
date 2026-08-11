#!/usr/bin/env python3
"""Reproduce the three-lane map and partition-sensitivity evidence."""
from __future__ import annotations
import importlib.util
import json
import sys
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
STAGE=HERE.parent
REPO=STAGE.parents[1]
LANES=(
    'LOCAL_NEUTRAL_HAZARD_PRIMARY',
    'RECOMBINATION_WEIGHTED_AUDITOR',
    'SCRIPT_SELF_SHIELDING_AUDITOR',
)


def load():
    path=HERE/'interval_discrete_map.py'
    spec=importlib.util.spec_from_file_location('crosssite_interval_suite',path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module


def plain(result,lane,elapsed,partition):
    return {
        'lane':lane,
        'partition':int(partition),
        'elapsed_s':float(elapsed),
        'classification':result.classification,
        'certified':bool(result.certified),
        'widths':result.public_widths,
        'table_event':result.table_event,
        'set_ledgers':result.set_ledgers,
        'diagnostics':result.diagnostics,
    }


def run() -> dict[str, object]:
    m=load()
    t0=time.perf_counter()
    rows=[]
    max_widths={'x_HII':0.0,'x_HeII':0.0,'x_HeIII':0.0,'log_T':0.0}
    for lane in LANES:
        start=time.perf_counter()
        result=m.run_lane(REPO,lane=lane,partition=2048)
        row=plain(result,lane,time.perf_counter()-start,2048)
        rows.append(row)
        for key,value in result.public_widths.items():
            max_widths[key]=max(max_widths[key],float(value))
    three={
        'classification':'THREE_LANE_VALIDATED_DISCRETE_MAP',
        'rows':rows,
        'all_certified':all(r['certified'] for r in rows),
        'max_widths':max_widths,
        'elapsed_s':time.perf_counter()-t0,
    }
    (STAGE/'data/THREE_LANE_INTERVAL_MAP.json').write_text(
        json.dumps(three,indent=2,sort_keys=True)+'\n',encoding='utf-8')

    parts=[]
    for partition in (1024,2048,4096):
        start=time.perf_counter()
        result=m.run_lane(REPO,lane=LANES[0],partition=partition)
        row=plain(result,LANES[0],time.perf_counter()-start,partition)
        row.pop('set_ledgers'); row.pop('lane')
        diagnostics=row.pop('diagnostics')
        row['validated_local_error_bounds']=diagnostics.get('validated_local_error_bounds',{})
        row['maximum_validated_local_error']=diagnostics.get('maximum_validated_local_error')
        row['map_enclosed']=diagnostics.get('map_enclosed',False)
        parts.append(row)
    monotone={key:all(parts[i+1]['widths'][key] < parts[i]['widths'][key]
                      for i in range(len(parts)-1)) for key in max_widths}
    sensitivity={
        'classification':'PARTITION_SENSITIVITY',
        'rows':parts,
        'acceptance_pattern':{str(r['partition']):bool(r['certified']) for r in parts},
        'all_maps_enclosed':all(r['map_enclosed'] for r in parts),
        'load_bearing_partition_2048_pass':bool(next(r for r in parts if r['partition']==2048)['certified']),
        'monotone_widths':monotone,
    }
    (STAGE/'data/PARTITION_SENSITIVITY.json').write_text(
        json.dumps(sensitivity,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return {'three_lane':three,'partition_sensitivity':sensitivity}


if __name__=='__main__':
    result=run()
    print(json.dumps(result,indent=2,sort_keys=True))
    ok=(result['three_lane']['all_certified'] and result['partition_sensitivity']['all_maps_enclosed'] and result['partition_sensitivity']['load_bearing_partition_2048_pass'] and all(result['partition_sensitivity']['monotone_widths'].values()))
    raise SystemExit(0 if ok else 1)
