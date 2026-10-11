"""Only new C12 attempt42 source-repair checks; no native gas/maps or old scans."""
from pathlib import Path
import hashlib,json,sys,unittest
import numpy as np
HERE=Path(__file__).resolve().parent;Q1B=HERE.parents[2];REPO=Q1B.parents[2]
for d in (HERE,Q1B,Q1B.parent/'n1',Q1B/'c11/precision'):sys.path.insert(0,str(d))
from source_precision_v2 import StableCellSource,integrate_source,provider_event_times
from source_precision import StableCellSource as OldStable, _old
from provider import HistoryProvider
from source_cells import CellSource
from grid_cells import load_grid

class NewSourceRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request=json.loads((Q1B/'c12/evidence/C2_FULL001/RUN/ATTEMPTS/attempt-00000042/MAP_01_REQUEST.json').read_text())
        for key,digest in cls.request['dependency_closure'].items():
            assert hashlib.sha256((REPO/key.removeprefix('dependency:')).read_bytes()).hexdigest()==digest
        cls.source=CellSource(HistoryProvider(r=0.),load_grid(Q1B/'GRID_C2.json'))
    def test_exact_failed_endpoint_positive_moment_assembly(self):
        t=self.request['t1_s'];raw=OldStable(self.source).source(t)
        self.assertLess(raw['Q_eV'][0,158],self.source.edges[158]*raw['N'][0,158])
        source=StableCellSource(self.source);v=source.source(t)
        n,q=v['N'],v['Q_eV'];a,b=self.source.edges[:-1],self.source.edges[1:]
        self.assertTrue(np.all(q>=a*n));self.assertTrue(np.all(q<=b*n))
        self.assertTrue(np.array_equal(n,raw['N']))
        self.assertTrue(np.array_equal(v['D_eV'],raw['D_eV']))
        self.assertTrue(np.array_equal(v['R'],raw['R']))
        self.assertGreater(n[0,158],0.)
        self.assertEqual(q[0,158],a[158]*n[0,158])
        _old._snapshot(source,t)
        (HERE/'ENDPOINT_REPAIR_RESULT.json').write_text(json.dumps(dict(
            N=float(n[0,158]),Q_raw=float(raw['Q_eV'][0,158]),Q_reassembled=float(q[0,158]),D=float(v['D_eV'][0,158]),
            tiny_positive_source_preserved=True,exact_snapshot_cone=True,assembly=v['moment_assembly'],native_calls=0),indent=2)+'\n')
    def test_new_failed_interval_original_quadrature_and_pairing(self):
        t0,t1=self.request['t0_s'],self.request['t1_s']
        source=StableCellSource(self.source);events=provider_event_times(source,t0,t1)
        result=integrate_source(source,t0,t1,event_times=events)
        self.assertTrue(result['diagnostics']['pass'])
        self.assertLessEqual(max(result['diagnostics']['per_cell_fine_scale_max_errors'].values()),1e-10)
        self.assertLessEqual(result['diagnostics']['source_pairing_max_relative'],1e-12)
        out=dict(result['diagnostics'],native_calls=0,old_completed_replays=0,t0_s=t0,t1_s=t1,
            newly_failed_interval_repair_only=True,dN_born_cell=float(result['dN'][0,158]))
        (HERE/'INTERVAL_SOURCE_RESULT.json').write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__':unittest.main(verbosity=2)
