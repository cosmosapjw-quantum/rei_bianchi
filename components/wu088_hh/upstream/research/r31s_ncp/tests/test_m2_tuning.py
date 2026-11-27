import importlib


def module():
    return importlib.import_module('research.r31s_ncp.m2_tuning')


def test_full_and_half_budget_candidates_are_bounded():
    rows = module().legal_configurations(64)
    assert rows == [(64, 1), (32, 2), (16, 4), (8, 8), (4, 16),
                    (2, 32), (1, 64), (32, 1), (16, 2), (8, 4),
                    (4, 8), (2, 16), (1, 32)]
    assert all(p*t <= 64 for p, t in rows)


def test_small_budget_never_overcommits():
    assert module().legal_configurations(3) == [(2, 1), (1, 2), (1, 1)]


def test_reads_linux_smaps_rss_pss_when_available():
    result = module()._smaps()
    assert result['rss_bytes'] is not None and result['rss_bytes'] > 0
    assert result['pss_bytes'] is not None and result['pss_bytes'] > 0


def test_spawn_barrier_is_passed_through_initializer():
    m = module()
    ctx = m.mp.get_context('spawn')
    barrier = ctx.Barrier(2)
    with m.ProcessPoolExecutor(max_workers=2, mp_context=ctx,
                               initializer=m.init_barrier, initargs=(barrier,)) as pool:
        assert sorted(pool.map(m.barrier_probe, range(2))) == [0, 1]


def test_pilot_memory_gate_keeps_headroom():
    m = module()
    assert m.memory_safe(64, 100_000_000, 20_000_000_000)
    assert not m.memory_safe(64, 100_000_000, 10_000_000_000)
