"""New binding tests only; no native map or old scientific trajectory replay."""
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from production_schedule import build_schedule, schedule_window, build_real_schedule


class ToyProvider:
    r = 0.
    end_time_s = 128.
    photon_band_eV = (1., 4.)
    identity = {'toy': 'analytic r(t)=1/(1+t), z(t)=128-t'}
    def __init__(self):
        self.tables = {'emissivity': SimpleNamespace(
            energies_eV=np.array([1., 2., 3., 4.]),
            redshifts=np.array([128., 64., 0.]))}
        self.background = SimpleNamespace(time_of_redshift=lambda z: 128.-z)
    def geometry(self, t):
        if not 0. <= t <= 128.:
            raise ValueError('time')
        return {'z': 128.-t}
    def ray(self, q, mu, t):
        r = np.ones(len(mu))/(1.+t)
        return np.asarray(q)*r, np.asarray(mu), r


def fixture():
    provider = ToyProvider()
    source = SimpleNamespace(provider=provider, edges=np.array([1., 4., 8.]),
                             mu=np.array([-.5, .5]))
    values = list(map(float, range(129)))
    epochs = {'time_s': values, 'time_s_hex': [x.hex() for x in values],
              'shared65_indices': list(range(0, 129, 2))}
    return source, epochs


class ProductionScheduleTests(unittest.TestCase):
    def test_band_z_output_classification_and_duplicate_labels(self):
        source, epochs = fixture()
        result = build_schedule(source, epochs)
        self.assertEqual(result['output_epochs_s'], epochs['time_s'])
        self.assertEqual(result['shared65_indices'], epochs['shared65_indices'])
        # q=8/E=2 is an internal energy kink at t=3: never classify it
        # as a hard source event. t=3 IS hard from q=4/E=1 and OUTPUT.
        physical = [r for r in result['hard_event_records']
                    if any(x['kind']=='SOURCE_BAND_CELL_EDGE' for x in r['labels'])]
        self.assertEqual(len(physical), 3)
        for actual, expected in zip(sorted(r['time_s'] for r in physical), [1.,3.,7.]):
            self.assertLessEqual(abs(actual-expected), 1.e-4)
        at3 = next(r for r in result['hard_event_records'] if r['time_s']==3.)
        self.assertFalse(any(x.get('energy_eV')==2. for x in at3['labels']))
        self.assertTrue(any(x['kind']=='OUTPUT' for x in at3['labels']))
        self.assertEqual(len(result['hard_events_s']), len(set(result['hard_events_s'])))
        self.assertEqual(result['physical_hard_events_s'][-2:], [64., 128.])
        at64 = next(r for r in result['hard_event_records'] if r['time_s']==64.)
        self.assertEqual({x['kind'] for x in at64['labels']}, {'OUTPUT','EMISSIVITY_REDSHIFT_KNOT'})
        self.assertEqual(result['hard_events_s'][0], 1.)
        self.assertTrue(any(x['kind']=='OUTPUT' for x in result['initial_boundary_labels']))
        self.assertEqual(result['hard_events_s'][-1], 128.)

    def test_h0_open_interval_and_invalid_time(self):
        source, epochs = fixture()
        result = build_schedule(source, epochs)
        self.assertEqual(schedule_window(result, 1., 1.), ())
        window = schedule_window(result, 1., 4.)
        self.assertTrue(all(1.<t<4. for t in window))
        self.assertTrue({2.,3.}.issubset(window))
        for t0,t1 in ((-1., 1.), (5., 4.), (0., float('inf')), (0., 129.)):
            with self.assertRaises(ValueError):
                schedule_window(result, t0, t1)

    def test_exact_epochs_and_nonzero_shear_refused(self):
        source, epochs = fixture()
        for mutate in ('hex', 'duplicate', 'subset', 'endpoint'):
            bad = copy.deepcopy(epochs)
            if mutate == 'hex': bad['time_s_hex'][1] = float(2.).hex()
            if mutate == 'duplicate': bad['time_s'][1] = 0.
            if mutate == 'subset': bad['shared65_indices'][1] = 3
            if mutate == 'endpoint': bad['time_s'][-1] = 127.5
            with self.assertRaises(ValueError): build_schedule(source, bad)
        source.provider.r = .001
        with self.assertRaisesRegex(ValueError, 'FLRW'):
            build_schedule(source, epochs)

    def test_real_pinned_epoch_binding_without_native_or_source_scan(self):
        q1b = HERE.parents[2]
        sys.path[:0] = [str(q1b), str(q1b.parent/'n1')]
        from provider import HistoryProvider
        from grid_cells import load_grid
        from source_cells import CellSource
        source = CellSource(HistoryProvider(r=0.), load_grid(q1b/'GRID_C2.json'))
        result = build_real_schedule(source)
        saved = json.loads((HERE.parent/'production_design/OUTPUT_EPOCHS.json').read_text())
        self.assertEqual(result['output_epochs_s'], saved['time_s'])
        self.assertEqual([float(x).hex() for x in result['output_epochs_s']], saved['time_s_hex'])
        self.assertEqual(result['end_time_s'], source.provider.end_time_s)
        self.assertEqual(result['internal_source_quadrature']['global_materialized'], False)
        self.assertTrue(all(0. <= t <= source.provider.end_time_s for t in result['hard_events_s']))
        self.assertEqual(set(result['output_epochs_s'][1:])-set(result['hard_events_s']), set())
        self.assertTrue(all(label['kind'] in {'OUTPUT','SOURCE_BAND_CELL_EDGE','EMISSIVITY_REDSHIFT_KNOT'}
                        for record in result['hard_event_records'] for label in record['labels']))

if __name__ == '__main__': unittest.main()
