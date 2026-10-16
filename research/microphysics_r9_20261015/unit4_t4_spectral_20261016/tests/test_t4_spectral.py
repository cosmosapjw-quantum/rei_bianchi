"""Independent dense-Hermitian diagnostics and cheap supervision; no PySCF."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
import numpy as np

SCRIPT = Path(__file__).resolve().parents[1] / 'code/t4_spectral.py'
spec = importlib.util.spec_from_file_location('t4_spectral', SCRIPT)
t4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t4)


class DenseTests(unittest.TestCase):
    def exact_fixture(self):
        H = np.diag([0., .7, 1.3, 2.8, 4.2, 8.])
        g = np.eye(6)[:, 0]
        u = np.array([0., 1., 2., .5, .2, 1.])
        u /= np.linalg.norm(u)
        return H, g, u, .43

    def test_exact_ground_known_measure_and_resolvent(self):
        H, g, u, W = self.exact_fixture()
        result, spectral = t4.krylov_chain(lambda x: t4.project(H@t4.project(x, g), g), g, u, W)
        self.assertTrue(result['invariant_subspace'])
        self.assertFalse(result['refinement_met'])  # Exact subspace is a distinct termination.
        self.assertTrue(result['milestones'][-1]['passed'])
        expected = W*abs(u[1:])**2
        np.testing.assert_allclose(spectral['nodes'], np.diag(H)[1:], atol=1e-12)
        np.testing.assert_allclose(spectral['weights'], expected, atol=1e-12)
        for index, eta in enumerate(t4.ETAS):
            for grid_index in (0, 70, 200, 800, 2000):
                z = t4.GRID[grid_index] + eta*1j
                exact = -W*np.vdot(u, np.linalg.solve(z*np.eye(6)-H, u)).imag/np.pi
                self.assertAlmostEqual(spectral['spectra'][index, grid_index], exact, places=11)
        self.assertLess(max(row['residual_Eh'] for row in result['milestones'][-1]['ritz_largest_weights']), 1e-11)

    def test_approximate_ground_nonzero_ground_rayleigh_residual_bounds(self):
        H = np.diag([0., 1., 3., 9.])
        g = np.array([np.cos(.1), np.sin(.1), 0., 0.])
        i = np.array([.6, .2, .5, .1])
        i /= np.linalg.norm(i)
        q = t4.project(i, g)
        W, P = float(np.vdot(q,q)), float(abs(np.vdot(g,i))**2)
        u = q/np.sqrt(W)
        E0 = 0.
        epsilon = np.linalg.norm(H@g)
        bounds = t4.scalar_bounds(P, W, E0, float(i@H@i), float((H@i)@(H@i)), epsilon)
        Q = np.eye(4)-np.outer(g,g)
        K = Q@H@Q
        nodes, vectors = np.linalg.eigh(K)
        weights = W*abs(vectors.T@u)**2
        mean = float(np.dot(weights,nodes)/W)
        second = float(np.dot(weights,nodes**2)/W)
        variance = second-mean**2
        for actual, interval in [(mean,bounds['conditional_mean_interval_Eh']),
                                  (second,bounds['conditional_second_interval_Eh2']),
                                  (variance,bounds['conditional_variance_interval_Eh2'])]:
            self.assertLessEqual(interval[0], actual+1e-12)
            self.assertGreaterEqual(interval[1], actual-1e-12)
        self.assertGreater(float(g@H@g),0)
        self.assertGreater(epsilon,0)
        for row in bounds['cantelli']:
            if row['condition_cut_above_mean_upper']:
                actual_tail = float(sum(weights[nodes>=row['cut_Eh']]))
                self.assertLessEqual(actual_tail,row['unconditional_upper_probability']+1e-12)
        action = lambda x:t4.project(H@t4.project(x,g),g)
        np.testing.assert_allclose(action(g),0,atol=1e-15)
        self.assertLess(abs(np.vdot(g,action(i))),1e-14)
        result,spectral=t4.krylov_chain(action,g,u,W)
        self.assertTrue(result['invariant_subspace'])
        self.assertAlmostEqual(result['direct_moments'][1]/W,mean,places=12)

    def test_repeated_eigenvalues_happy_breakdown(self):
        H=np.diag([0.,1.,1.,2.,2.])
        g=np.eye(5)[:,0]
        u=np.array([0.,1.,2.,3.,4.]);u/=np.linalg.norm(u)
        result,spectral=t4.krylov_chain(lambda x:H@x,g,u,.5)
        self.assertTrue(result['invariant_subspace'])
        self.assertEqual(result['last_length'],2)
        np.testing.assert_allclose(spectral['nodes'],[1.,2.],atol=1e-12)
        np.testing.assert_allclose(spectral['weights'],[.5*5/30,.5*25/30],atol=1e-12)
        self.assertTrue(result['milestones'][-1]['invariant_subspace_certificate'])

    def test_rotated_complex_basis_invariance(self):
        H,g,u,W=self.exact_fixture()
        rng=np.random.default_rng(94)
        rotation,_=np.linalg.qr(rng.normal(size=H.shape)+1j*rng.normal(size=H.shape))
        rotated=rotation@H@rotation.conj().T
        r1,s1=t4.krylov_chain(lambda x:H@x,g,u,W)
        r2,s2=t4.krylov_chain(lambda x:rotated@x,rotation@g,rotation@u,W)
        np.testing.assert_allclose(s1['nodes'],s2['nodes'],atol=1e-11)
        np.testing.assert_allclose(s1['weights'],s2['weights'],atol=1e-11)
        np.testing.assert_allclose(s1['spectra'],s2['spectra'],atol=1e-10)
        np.testing.assert_allclose(r1['direct_moments'],r2['direct_moments'],atol=1e-11)

    def test_nested_milestones_checkpoint_and_full_dense_moments(self):
        size=80
        H=np.diag(np.linspace(0,19,size))
        g=np.eye(size)[:,0]
        u=np.ones(size);u[0]=0;u/=np.linalg.norm(u)
        W=.4
        with tempfile.TemporaryDirectory() as temp:
            result,spectral=t4.krylov_chain(lambda x:H@x,g,u,W,out=Path(temp),identities={'fixture':'dense80'})
            lengths=[m['length'] for m in result['milestones']]
            self.assertEqual(lengths[:3],[16,32,64])
            for m in result['milestones']:
                self.assertTrue(m['passed'])
                np.testing.assert_allclose(m['unconditional_moments'],[W,W*float(u@H@u),W*float((H@u)@(H@u))],atol=1e-9)
            with np.load(Path(temp)/'checkpoint.npz',allow_pickle=False) as checkpoint:
                self.assertEqual(checkpoint['V'].shape[1],result['last_length'])
                meta=json.loads(str(checkpoint['metadata_json']))
                self.assertFalse(meta['resume_implemented'])
            self.assertTrue((Path(temp)/'spectra.npz').exists())
            for index in (1,2):
                self.assertEqual(result['milestones'][index]['refinement_pair'],[lengths[index-1],lengths[index]])

    def test_failed_reconstruction_stops_gate_with_measured_defect(self):
        H,g,u,W=self.exact_fixture()
        i=np.sqrt(1-W)*g+np.sqrt(W)*u
        checks=t4.reconstruction_checks(lambda x:H@x,i,g,u,.1,float(i@H@i),float((H@i)@(H@i)),0.)
        self.assertFalse(checks['passed'])
        failed=[x['name'] for x in checks['gates'] if not x['pass']]
        self.assertIn('ground_residual_Eh',failed)
        self.assertIn('ground_energy_difference_Eh',failed)

    def test_parser_missing_array_and_wrong_shape(self):
        receipt={'retained_ao_rank':3,'ao_rank':3}
        with self.assertRaisesRegex(ValueError,'missing required'):
            t4.prepare_arrays(receipt,{},False)
        arrays={k:np.zeros((3,3)) for k in ('CI_parent','CI_daughter_ground','CI_complement','common_orbital_matrix','rdm1_parent','rdm1_daughter')}
        arrays['AO_overlap_eigenvalues']=np.ones(2)
        with self.assertRaisesRegex(ValueError,'shape mismatch'):
            t4.prepare_arrays(receipt,arrays,False)

    def test_refinement_not_inferred_from_moments_and_tails_retained(self):
        a=t4.lorentzian_spectra(np.array([1.,5.]),np.array([.2,.2]))
        b=t4.lorentzian_spectra(np.array([2.,4.]),np.array([.2,.2]))
        self.assertFalse(t4.refinement(a,b,.4)['passed'])
        self.assertTrue(t4.refinement(a,a,.4)['passed'])
        for row in a['masses']:
            self.assertGreater(row['below_0'],0)
            self.assertGreater(row['above_20'],0)
            self.assertAlmostEqual(row['below_0']+row['inside_0_20']+row['above_20'],.4,places=14)

    def test_action_limit_and_supervisor_timeout_preserve_partial_output(self):
        budget=t4.ActionBudget(time.monotonic()+10,maximum=1,headroom_gib=0)
        budget.apply(lambda x:x,np.array([1.]))
        with self.assertRaisesRegex(t4.Deferred,'action_limit'):
            budget.apply(lambda x:x,np.array([1.]))
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            fixture="from pathlib import Path; import time; Path("+repr(str(out/'checkpoint.npz'))+").write_bytes(b'fixture partial'); print('before sleep',flush=True); time.sleep(5)"
            result=t4.supervise([sys.executable,'-c',fixture],out,.2,1.,headroom_gib=0)
            self.assertEqual(result['status'],'partial')
            self.assertEqual(result['supervisor_stop_reason'],'wall_limit')
            self.assertFalse(result['numerical_passed'])
            self.assertEqual((out/'checkpoint.npz').read_bytes(),b'fixture partial')
            self.assertIn('before sleep',(out/'stdout.log').read_text())


if __name__=='__main__':
    unittest.main(verbosity=2)
