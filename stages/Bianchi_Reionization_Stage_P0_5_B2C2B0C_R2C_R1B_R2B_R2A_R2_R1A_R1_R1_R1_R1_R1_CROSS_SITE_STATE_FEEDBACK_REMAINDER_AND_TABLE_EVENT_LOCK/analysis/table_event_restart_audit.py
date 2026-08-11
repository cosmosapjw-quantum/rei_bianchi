#!/usr/bin/env python3
"""Synthetic and inherited audits for table-knot detection/restart semantics."""
from __future__ import annotations
import importlib.util
import json
import math
import sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
STAGE=HERE.parent


def load():
    path=HERE/'cross_site_discrete_map.py'
    spec=importlib.util.spec_from_file_location('table_event_primitives',path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module


def run() -> dict[str, object]:
    m=load()
    knots=np.log(10.0**np.arange(4.0,5.0000001,0.25))
    safe=m.detect_path_table_events(
        m.IntervalVector(np.array([knots[1]+1e-3]),np.array([knots[1]+2e-3])),
        m.IntervalVector(np.array([knots[1]+3e-3]),np.array([knots[1]+4e-3])),
    )
    between=m.detect_path_table_events(
        m.IntervalVector(np.array([knots[2]-2e-4]),np.array([knots[2]-1e-4])),
        m.IntervalVector(np.array([knots[2]+1e-4]),np.array([knots[2]+2e-4])),
    )
    state=b'accepted-state-sha-locked'
    ledger=b'accepted-ledger-sha-locked'
    t_cross=0.375
    inc=m.localize_monotone_table_event(
        t0=0.0,t1=1.0,knot=float(knots[2]),
        value_at=lambda t:float(knots[2])+0.4*(float(t)-t_cross),
        parent_state_bytes=state,parent_ledger_bytes=ledger,
        time_tolerance=2.0**-40,
    )
    dec=m.localize_monotone_table_event(
        t0=0.0,t1=1.0,knot=float(knots[3]),
        value_at=lambda t:float(knots[3])-0.7*(float(t)-0.625),
        parent_state_bytes=state,parent_ledger_bytes=ledger,
        time_tolerance=2.0**-40,
    )
    result={
        'classification':'TABLE_EVENT_DETECTION_AND_TRANSACTIONAL_RESTART_AUDIT',
        'safe_path_event':safe.any_event,
        'between_site_crossing_detected':between.any_event,
        'between_site_node_indices':between.node_indices.tolist(),
        'between_site_knot_indices':between.knot_indices.tolist(),
        'increasing_localization':{
            'certified':inc.certified,'t_lower':inc.t_lower,'t_upper':inc.t_upper,
            'contains_exact_crossing':inc.t_lower<=t_cross<=inc.t_upper,
            'width':inc.t_upper-inc.t_lower,'iterations':inc.iterations,
            'parent_unchanged':inc.parent_unchanged,
        },
        'decreasing_localization':{
            'certified':dec.certified,'t_lower':dec.t_lower,'t_upper':dec.t_upper,
            'contains_exact_crossing':dec.t_lower<=0.625<=dec.t_upper,
            'width':dec.t_upper-dec.t_lower,'iterations':dec.iterations,
            'parent_unchanged':dec.parent_unchanged,
        },
    }
    result['passed']=bool(
        not result['safe_path_event'] and result['between_site_crossing_detected']
        and result['increasing_localization']['certified']
        and result['increasing_localization']['contains_exact_crossing']
        and result['increasing_localization']['parent_unchanged']
        and result['decreasing_localization']['certified']
        and result['decreasing_localization']['contains_exact_crossing']
        and result['decreasing_localization']['parent_unchanged']
    )
    target=STAGE/'data/TABLE_EVENT_RESTART_AUDIT.json'
    target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    result=run()
    print(json.dumps(result,indent=2,sort_keys=True))
    raise SystemExit(0 if result['passed'] else 1)
