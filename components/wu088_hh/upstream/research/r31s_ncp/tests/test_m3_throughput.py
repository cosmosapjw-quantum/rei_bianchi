import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location('m3_throughput', ROOT/'m3_throughput.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pair_set_spans_cost_quantiles_and_is_unique():
    m = load()
    costs = {(i, 0): float(i+1) for i in range(20)}
    pairs = m.select_pairs(costs, count=12)
    assert len(pairs) == len(set(pairs)) == 12
    assert pairs[0] == (0, 0)
    assert pairs[-1] == (19, 0)
    assert (10, 0) in pairs or (9, 0) in pairs


def test_layout_and_memory_gate():
    m = load()
    assert m.affinity_groups(list(range(64)), 30, 2) == [list(range(i*2, i*2+2)) for i in range(30)]
    assert m.memory_safe(60, 100, 12000)
    assert not m.memory_safe(60, 101, 12000)
    try:
        m.affinity_groups(list(range(64)), 64, 2)
    except ValueError:
        pass
    else:
        raise AssertionError('oversubscribed layout accepted')


def test_measured_batch_feeds_high_outer_parallelism():
    m = load()
    assert m.measured_task_count(64) >= 128
    assert m.measured_task_count(60) >= 120
