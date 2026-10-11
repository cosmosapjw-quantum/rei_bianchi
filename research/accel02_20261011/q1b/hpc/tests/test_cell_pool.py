"""Manufactured actor integration tests; no production binary or history maps."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import time
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ordered_cell_pool import Pool,PoolError


ABSORBER = '''
from types import SimpleNamespace
import os,time
import numpy as np
_REFINEMENTS=[]
def pop_refinement_records():
    result=list(_REFINEMENTS);_REFINEMENTS.clear();return result
def prepare_incident(N,U,R,a,b,opacity,orders=(64,128),rtol=1e-7,support_cap_ev=None):
    if N==999:time.sleep(10)
    opacity.sigma(np.array([a,b]))
    _REFINEMENTS.append(dict(marker=N))
    return SimpleNamespace(N=N,U=U,R=R,diagnostics=dict(marker=N,child_pid=opacity.child.pid,order_pair_max_error=0.))
def absorb(p,lower,h):
    if h==13 and p.N==3:raise ArithmeticError('MANUFACTURED_CELL_FAILURE')
    if h==99 and p.N==3:os._exit(17)
    return dict(N=p.N,U=p.U,K0=np.zeros(3),KE=np.zeros(3),photoheat_direct=np.zeros(3),
        number_absorbed_species=np.zeros(3),energy_absorbed_species=np.zeros(3),
        pointwise_pairing_relative_max=0.,diagnostics=dict(marker=p.N))
'''


class ManufacturedOpacity:
    def __init__(self,binary):
        self.native_calls=0;self.energy_evaluations=0
        self.child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(600)'])
    def sigma(self,energy):
        self.native_calls+=1;self.energy_evaluations+=len(energy)
        return np.zeros((len(energy),3))
    def close(self):
        self.child.terminate();self.child.wait(timeout=3.)


def manufactured_opacity(binary):
    return ManufacturedOpacity(binary)


def requests(numbers):
    return [dict(N=float(n),U=15.*n,R=1.,a=10.,b=20.,orders=(64,128),rtol=1e-7,support_cap_ev=None) for n in numbers]


def running(pid):
    try:
        stat=Path(f'/proc/{pid}/stat').read_text()
        return stat.split(') ',1)[1].split()[0] not in ('Z','X')
    except FileNotFoundError:
        return False


class CellPoolIntegration(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/'synthetic_absorption.py'
        self.path.write_text(ABSORBER)
    def tearDown(self):
        self.temp.cleanup()
    def pool(self):
        return Pool(workers=2,timeout_s=10.,absorption_path=self.path,
                    opacity_factory=manufactured_opacity)
    def assert_children_stopped(self,pids):
        deadline=time.monotonic()+2
        while any(running(pid) for pid in pids) and time.monotonic()<deadline:
            time.sleep(.02)
        self.assertFalse(any(running(pid) for pid in pids))

    def test_order_resident_reuse_replacement_and_new_pool_restart(self):
        with self.pool() as pool:
            prep=pool.prepare(requests(range(1,8)))
            children={v['child_pid'] for v in prep}
            self.assertEqual([v['marker'] for v in prep],list(range(1,8)))
            self.assertEqual(pool.pop_refinement_records(),[dict(marker=n) for n in range(1,8)])
            for _ in range(3):
                out=pool.absorb(np.array([1.,0.,0.]),.1)
                self.assertEqual([v['N'] for v in out],list(range(1,8)))
            self.assertEqual(pool.native_calls,7) # no repeated prepare/SIGMA in Newton-like calls
            self.assertEqual(pool.energy_evaluations,14)
            replacement=pool.prepare(requests([10,20,30]))
            self.assertEqual({v['child_pid'] for v in replacement},children)
            self.assertEqual([v['N'] for v in pool.absorb([0.,0.,0.],.1)],[10,20,30])
            self.assertEqual(pool.native_calls,10)
            self.assertEqual(pool.metrics['opacity_binding'],'INJECTED_TEST_OPACITY')
        self.assertTrue(pool.cleanup_receipt['all_actors_stopped'])
        self.assert_children_stopped(children)
        with self.pool() as restarted:
            self.assertEqual([v['marker'] for v in restarted.prepare(requests([8,9]))],[8,9])
            self.assertEqual(restarted.native_calls,2)

    def test_failure_reports_original_cell_and_refuses_reuse(self):
        pool=self.pool()
        prep=pool.prepare(requests(range(1,6)))
        children={v['child_pid'] for v in prep}
        with self.assertRaises(PoolError) as caught:
            pool.absorb([1.,0.,0.],13.)
        receipt=caught.exception.receipt
        self.assertEqual(receipt['failures'][0]['cell_index'],2)
        self.assertIn('MANUFACTURED_CELL_FAILURE',receipt['failures'][0]['message'])
        self.assertEqual(receipt['counter_status'],'EXACT_RECEIVED_ACTOR_COUNTERS')
        with self.assertRaises(PoolError):pool.prepare(requests([1]))
        self.assert_children_stopped(children)

    def test_abrupt_actor_exit_kills_private_provider_and_preserves_unknown_counts(self):
        pool=self.pool()
        prep=pool.prepare(requests(range(1,6)))
        children={v['child_pid'] for v in prep}
        with self.assertRaises(PoolError) as caught:
            pool.absorb([1.,0.,0.],99.)
        self.assertEqual(caught.exception.receipt['unobserved_workers'],[0])
        self.assertEqual(pool.metrics['counter_status'],'PARTIAL_RECEIPTS_ONLY')
        self.assert_children_stopped(children)

    def test_collective_timeout_kills_workers_and_provider_children_without_retry(self):
        pool=self.pool()
        prep=pool.prepare(requests([1,2]))
        children={v['child_pid'] for v in prep}
        pool.timeout_s=.2
        with self.assertRaises(PoolError) as caught:
            pool.prepare(requests([999,2]))
        self.assertEqual(caught.exception.receipt['timed_out_workers'],[0])
        self.assertTrue(caught.exception.receipt['no_retry'])
        self.assert_children_stopped(children)


if __name__=='__main__':unittest.main()
