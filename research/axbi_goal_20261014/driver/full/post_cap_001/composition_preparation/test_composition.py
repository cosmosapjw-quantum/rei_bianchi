"""One manufactured boundary/count fixture, never actual cosmological data."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
SCRIPT = Path(__file__).resolve().parents[1] / 'compose_zero_history.py'
s = importlib.util.spec_from_file_location('composer', SCRIPT)
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)

class CompositionFixture(unittest.TestCase):
    def test_boundary_counts_and_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            (p/'prior').write_text('case_id,time_s,a\nZERO,0,0.047619047619047616\nZERO,1,0.06\nZERO,2,0.08\n')
            (p/'segment').write_text('case_id,time_s,a\nZERO,2.0,0.080\nZERO,3,0.1\nZERO,4,0.15\nZERO,5,0.2\n')
            counts = m.join_csv(p/'prior',p/'segment',p/'joined',2)
            self.assertEqual(counts,dict(original_rows=3,segment_rows_after_boundary=3,boundary_rows_removed=1,composed_rows=6))
            (p/'ledger').write_text('case_id,time_s,ledger_name,residual,tolerance,status\nZERO,0,source_N_per_H,2,,VALUE\nZERO,0,photon_count,0,1e-8,PASS\n')
            self.assertEqual(len(list(m.groups(p/'ledger'))[0][1]),2)
            prior=dict(accepted='2',attempts='8',rejections='1',rhs_evaluations='56',wall_s='2')
            final=dict(accepted='5',attempts='17',rejections='1',rhs_evaluations='119',wall_s='5')
            m.check_counters(prior,final,counts)
            self.assertEqual([t for t,_ in m.groups(p/'joined')],[0,1,2,3,4,5])
            (p/'segment').write_text((p/'segment').read_text().replace('0.080','0.081'))
            with self.assertRaisesRegex(m.NotReady,'HOLD_SHARED_BOUNDARY_VALUES'):
                m.join_csv(p/'prior',p/'segment',p/'bad',2)
            with self.assertRaisesRegex(m.NotReady,'HOLD_COUNTER_REBASE'):
                m.check_counters(prior,dict(final,attempts='7'),counts)

if __name__ == '__main__': unittest.main()
