"""New split-map boundary adapter tests; no old checkpoint suite is replayed."""
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from entry_checkpoint import (COUNTERS, CheckpointError, entry_identity,
                              make_entry_snapshot, pack_entry_state,
                              unpack_entry_state, write_entry_checkpoint,
                              load_entry_checkpoint)


def example():
    # Static neutral gas, two stored boundaries, one incident cell. The
    # manufactured sink immediately escapes, so gas chemistry is unchanged.
    gas = np.array([0., 0., 0., 1.5 * 8.617333262e-5 * 1.08 * 20.])
    counters = dict.fromkeys(COUNTERS, 0.)
    first = pack_entry_state(gas, np.array([1.]), np.array([2.]), counters)
    counters.update(Nsource=.4, Nabs=.1, Esource_eV=.8, Eescape_eV=.2)
    last = pack_entry_state(gas, np.array([1.3]), np.array([2.6]), counters)
    a, m = make_entry_snapshot(
        clocks=np.array([0., 1.]), states=np.array([first, last]),
        R=np.ones((2,1)), support=np.array([[[1.,3.]], [[1.,3.]]]),
        all_boundary_clocks=np.array([0.,1.,2.]), nH_ref=1., nHe_ref=.08,
        scales=np.ones(first.size),
        physical_binding='MANUFACTURED_SPLIT_RADIATIVE_ESCAPE')
    return a, m


class TestEntryCheckpoint(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.identity_files = {}
        for name in ('source','grid','binary','control','physics_contract'):
            p = self.root / (name+'.txt')
            p.write_text('new checkpoint fixture '+name+'\n')
            self.identity_files[name] = p
        self.identity = entry_identity(**self.identity_files)

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_boundary_roundtrip_and_explicit_restart_kind(self):
        arrays, meta = example()
        path = write_entry_checkpoint(self.root/'generations', 0, arrays, meta, self.identity)
        got = load_entry_checkpoint(self.root/'generations', 0, self.identity)
        for k, v in arrays.items():
            self.assertTrue(np.array_equal(got['arrays'][k], v), k)
        self.assertEqual(got['metadata'], meta)
        self.assertEqual(got['metadata']['restart_kind'], 'FRESH_SPLIT_STEP_AT_NATURAL_SEGMENT_BOUNDARY')
        self.assertEqual(got['current_validation']['scope'], 'MANUFACTURED_SPLIT_RADIATIVE_ESCAPE')
        self.assertFalse(got['manifest']['scientific_admission'])
        self.assertTrue(path.is_dir())

    def test_missing_prefix_counter_and_identity_are_rejected(self):
        arrays, meta = example()
        for change in ('prefix', 'counter', 'identity'):
            a, m, ident = copy.deepcopy(arrays), copy.deepcopy(meta), dict(self.identity)
            if change == 'prefix': a['prefix_clock'] = np.array([1.])
            if change == 'counter': a['counter_origins'][0] = 1.
            if change == 'identity': ident.pop('grid')
            with self.subTest(change=change), self.assertRaises(CheckpointError):
                write_entry_checkpoint(self.root/change, 0, a, m, ident)

    def test_physics_not_saved_flags_controls_acceptance(self):
        arrays, meta = example()
        for change in ('gas', 'cone', 'support', 'ledger', 'restart'):
            a, m = copy.deepcopy(arrays), copy.deepcopy(meta)
            if change == 'gas':
                a['state'][0] = 1.1
                a['prefix_state'][-1,0] = 1.1
                a['accepted_max'][0] = 1.1
            if change == 'cone':
                a['state'][5] = 20.
                a['prefix_state'][-1,5] = 20.
                a['accepted_max'][5] = 20.
            if change == 'support': m['prefix_support'][1][0][0] = 2.5
            if change == 'ledger':
                a['state'][6] += .01
                a['prefix_state'][-1,6] += .01
                a['accepted_max'][6] += .01
            if change == 'restart': m['restart_kind'] = 'IMAGINARY_INTERNAL_STATE_RESTORE'
            with self.subTest(change=change), self.assertRaises(CheckpointError):
                write_entry_checkpoint(self.root/change, 0, a, m, self.identity)

    def test_load_checks_expected_identity(self):
        arrays, meta = example()
        write_entry_checkpoint(self.root/'generations', 0, arrays, meta, self.identity)
        stale = dict(self.identity, grid='0'*64)
        with self.assertRaisesRegex(CheckpointError, 'Stale'):
            load_entry_checkpoint(self.root/'generations', 0, stale)

    def test_signed_CMB_counter_is_valid_but_loss_counters_cannot_decrease(self):
        arrays, meta = example()
        # Zero net signed bath exchange is already covered by example. An
        # equal negative CMB and smaller gas thermal energy is valid.
        j = 6 + COUNTERS.index('ECMB_eV')
        arrays['state'][j] = -.001
        arrays['state'][3] -= .001
        arrays['prefix_state'][-1] = arrays['state']
        arrays['accepted_min'] = arrays['prefix_state'].min(axis=0)
        arrays['accepted_max'] = arrays['prefix_state'].max(axis=0)
        write_entry_checkpoint(self.root/'signed', 0, arrays, meta, self.identity)

    def test_new_split_source_absorption_restart_is_exact(self):
        from source_entry import integrate_source, advance_source
        from positive_absorption import prepare_incident, absorb, C_CM_S

        class Birth:
            def source(self, t):
                R = math.exp(-.3*t)
                sn = np.array([[2.*.3*t]])
                sq = np.array([[10.*math.expm1(.3*t)]])
                return dict(N=sn,Q_eV=sq,U_eV=R*sq,R=np.array([R]))

        def sigma(E):
            out = np.zeros((len(E),3))
            out[:,0] = 1./C_CM_S
            return out

        clocks = np.array([0.,.25,.5,.75,1.])
        gas = np.array([0.,0.,0.,1.5*8.617333262e-5*1.08*20.])
        initial = pack_entry_state(gas,np.array([0.]),np.array([0.]),dict.fromkeys(COUNTERS,0.))

        def advance(state,j):
            p = unpack_entry_state(state,1)
            t0,t1 = clocks[j:j+2]
            result = integrate_source(Birth(),t0,t1)
            incident = advance_source(p['N'].reshape(1,1),p['U_eV'].reshape(1,1),result)
            R = math.exp(-.3*t1)
            measure = prepare_incident(incident['N'].item(),incident['U_eV'].item(),
                                       R,5.,5.*math.exp(.3*t1),sigma)
            survived = absorb(measure,np.array([1.7,0.,0.]),t1-t0)
            counter = p['counters']
            counter['Nsource'] += result['dN'].item()
            counter['Nabs'] += float(sum(survived['number_absorbed_species']))
            counter['Esource_eV'] += result['injected_energy_eV'].item()
            counter['Eescape_eV'] += float(sum(survived['energy_absorbed_species']))
            counter['Wrad_eV'] += incident['radiation_work_eV'].item()
            return pack_entry_state(p['gas'],np.array([survived['N']]),
                                    np.array([survived['U']]),counter)

        def snapshot(history):
            times = clocks[:len(history)]
            Rs = np.exp(-.3*times)[:,None]
            support = np.array([[[5.,5.*math.exp(.3*t)]] for t in times])
            return make_entry_snapshot(clocks=times,states=np.array(history),R=Rs,
                support=support,all_boundary_clocks=clocks,nH_ref=1.,nHe_ref=.08,
                scales=np.ones(len(initial)),
                physical_binding='MANUFACTURED_SPLIT_RADIATIVE_ESCAPE')

        uninterrupted = [initial]
        for j in range(4): uninterrupted.append(advance(uninterrupted[-1],j))
        split = [initial]
        for j in range(2): split.append(advance(split[-1],j))
        arrays,meta = snapshot(split)
        directory = self.root/'split-generations'
        first = write_entry_checkpoint(directory,0,arrays,meta,self.identity)
        restored = load_entry_checkpoint(directory,0,self.identity,
            expected_manifest_sha256=hashlib.sha256((first/'manifest.json').read_bytes()).hexdigest())
        split = list(restored['arrays']['prefix_state'])
        for j in range(2,4): split.append(advance(split[-1],j))
        final_a,final_m = snapshot(split)
        expected_a,expected_m = snapshot(uninterrupted)
        write_entry_checkpoint(directory,1,final_a,final_m,self.identity)
        for name in final_a:
            self.assertTrue(np.array_equal(final_a[name],expected_a[name]),name)
        self.assertEqual(final_m,expected_m)
        for value in final_m['ledger_max'].values(): self.assertLess(value,1e-9)
        evidence = os.environ.get('CHECKPOINT_ENTRY_EVIDENCE_DIR')
        if evidence:
            dest = Path(evidence)
            shutil.copytree(directory,dest)
            report = dict(schema='rei.q1b.entry_checkpoint_restart.v1',status='PASS',
                new_split_map='actual source_entry + positive_absorption functions',
                closure='MANUFACTURED_IMMEDIATE_RADIATIVE_ESCAPE_FIXED_GAS',
                boundary_clock=.5,final_clock=1.,accepted_boundaries=5,
                complete_prefix_state_difference_max=0.,arrays_bitwise_equal=True,
                metadata_exact_equal=True,ledger_max=final_m['ledger_max'],
                native_calls=0,physical_gas_driver_binding='NOT_EVALUATED',
                scientific_admission=False)
            (dest.parent/'CHECKPOINT_ENTRY_RESTART.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
