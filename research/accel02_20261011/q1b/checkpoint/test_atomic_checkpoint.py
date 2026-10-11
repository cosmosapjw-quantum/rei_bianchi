"""New checkpoint capability tests; never import old physical providers."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from atomic_checkpoint import CheckpointError, discover_generations, load_generation, publish_generation
from fixture import identities, make_snapshot, manufactured_validator, split_trial


class AtomicCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.arrays, self.metadata = make_snapshot()
        self.identity = identities()

    def tearDown(self):
        self.tmp.cleanup()

    def publish(self, arrays=None, metadata=None):
        return publish_generation(self.root, 1, arrays or self.arrays,
                                  metadata or self.metadata, self.identity,
                                  manufactured_validator)

    def load(self, identity=None):
        return load_generation(self.root, 1, identity or self.identity,
                               manufactured_validator)

    def test_complete_generation_preserves_all_arrays_and_metadata(self):
        self.publish()
        got = self.load()
        self.assertEqual(got['metadata'], self.metadata)
        for key, value in self.arrays.items():
            np.testing.assert_array_equal(got['arrays'][key], value)
        self.assertEqual(discover_generations(self.root), [1])
        self.assertFalse(got['manifest']['scientific_admission'])
        self.assertFalse(got['manifest']['internal_integrator_state_saved'])

    def test_corruption_missing_and_torn_rejected_and_tmp_excluded(self):
        path = self.publish()
        original = (path / 'arrays.npz').read_bytes()
        (path / 'arrays.npz').write_bytes(original[:-5] + b'wrong')
        with self.assertRaises(CheckpointError): self.load()
        (path / 'arrays.npz').write_bytes(original)
        (path / 'metadata.json').unlink()
        with self.assertRaises(CheckpointError): self.load()
        (self.root / 'gen-00000002').mkdir()
        (self.root / '.tmp-gen-00000003-abandoned').mkdir()
        self.assertEqual(discover_generations(self.root), [])
        with self.assertRaises(CheckpointError):
            load_generation(self.root, 99, self.identity, manufactured_validator)

    def test_stale_identity_or_missing_validator_rejected(self):
        self.publish()
        wrong = dict(self.identity, source='a' * 64)
        with self.assertRaises(CheckpointError): self.load(wrong)
        with self.assertRaises(CheckpointError):
            load_generation(self.root, 1, self.identity, None)
        with self.assertRaises(CheckpointError):
            load_generation(self.root, 1, self.identity, manufactured_validator,
                            expected_manifest_sha256='0'*64)

    def test_malformed_manifest_fails_closed(self):
        path = self.publish()
        for bad in ([], {'schema':'wrong'}, {'schema':'rei.complete_checkpoint.v1','generation':1,'files':[]}):
            (path/'manifest.json').write_text(json.dumps(bad))
            with self.assertRaises(CheckpointError): self.load()
            self.assertEqual(discover_generations(self.root), [])

    def test_mismatched_prefix_or_boundary_rejected_before_publish(self):
        for mutation in ('order', 'omitted_sample', 'future_sample', 'boundary', 'state', 'counter'):
            with self.subTest(mutation=mutation):
                a = {key: value.copy() for key, value in self.arrays.items()}
                m = copy.deepcopy(self.metadata)
                if mutation == 'order': a['prefix_clock'][1] = a['prefix_clock'][0]
                if mutation == 'omitted_sample':
                    a['prefix_clock'] = a['prefix_clock'][1:]
                    a['prefix_state'] = a['prefix_state'][1:]
                if mutation == 'future_sample': a['prefix_clock'][-1] = 0.6
                if mutation == 'boundary': m['current_clock'] = 0.499
                if mutation == 'state': a['state'][0] += 0.01
                if mutation == 'counter': a['counter_origins'][0] = 3.0
                with self.assertRaises(CheckpointError): self.publish(a, m)
                self.assertEqual(discover_generations(self.root), [])

    def test_create_only_collision_preserves_first_generation(self):
        path = self.publish()
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in path.iterdir()}
        with self.assertRaises(CheckpointError): self.publish()
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in path.iterdir()}
        self.assertEqual(before, after)

    def test_same_manifest_hashes_do_not_override_physical_validator(self):
        a = {key: value.copy() for key, value in self.arrays.items()}
        a['accepted_min'][0] = -1.0
        with self.assertRaises(CheckpointError): self.publish(a)

    def test_manufactured_split_matches_fresh_segmented_uninterrupted(self):
        result = split_trial(self.root)
        self.assertTrue(result['all_acceptance'])
        self.assertEqual(result['restart_kind'], 'FRESH_BDF_AT_NATURAL_SEGMENT_BOUNDARY')
        self.assertFalse(result['production_provider_binding'])
        self.assertLess(result['analytic_max_absolute_error'], 2e-10)
        self.assertEqual(result['split_vs_uninterrupted_max_absolute_error'], 0.0)


if __name__ == '__main__': unittest.main(verbosity=2)
