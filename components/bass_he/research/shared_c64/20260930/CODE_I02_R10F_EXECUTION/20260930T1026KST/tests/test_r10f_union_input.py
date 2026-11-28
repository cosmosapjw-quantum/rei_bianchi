import json

import numpy as np

from r10f_runner import HERE, R10C, plan_queries
from r10f_lanes import input_probabilities_union


def test_complete_union_table_admitted_without_360_pair_alias():
    table=json.loads((HERE/'EXACT_NODE_TABLE.json').read_text())
    frozen=json.loads((R10C/'FROZEN_DELTA0_RECORD.json').read_text())
    nodes=plan_queries()['nodes']
    dynamic,static=input_probabilities_union(table,nodes,np.array((0.5,5.0)),frozen)
    assert dynamic.shape==static.shape==(510,5)
    assert np.all(np.isfinite(dynamic)) and np.all(np.isfinite(static))
    assert np.any(dynamic!=static)
