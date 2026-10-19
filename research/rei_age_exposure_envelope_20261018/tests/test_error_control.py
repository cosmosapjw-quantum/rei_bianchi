import ast
import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np
import scipy
from scipy.integrate._ivp.rk import DOP853

import build_refined_sources
import error_control as control
import run_refinement


class ErrorControlTests(unittest.TestCase):
    def test_padding_old_factor_and_scalar_block_invariance(self):
        for size in (2,144,1152,9234):
            a=np.zeros(size); b=np.zeros(size)
            a[-1]=3.; b[-1]=4.
            analytic=3.**2/math.sqrt(3.**2+.01*4.**2)
            old=control.block_error_norm(a,b,1.,(size,))
            block=control.block_error_norm(a,b,1.,(size-1,1))
            self.assertAlmostEqual(old,analytic/math.sqrt(size),places=14)
            self.assertAlmostEqual(block,analytic,places=14)

    def test_all_in_one_matches_installed_scipy(self):
        rng=np.random.default_rng(2718)
        for size in (2,144):
            original=DOP853.__new__(DOP853)
            variant=control.make_block_dop853((size,)).__new__(control.make_block_dop853((size,)))
            variant.block_sizes=(size,)
            K=rng.normal(size=(len(DOP853.E5),size))
            scale=rng.uniform(.1,2.,size)
            old=original._estimate_error_norm(K,.01,scale)
            new=variant._estimate_error_norm(K,.01,scale)
            self.assertAlmostEqual(new/old,1.,places=14)

    def test_production_partition_complete(self):
        for dimension in (18,19,9234):
            blocks=control.production_blocks(dimension)
            self.assertEqual(sum(blocks),dimension)
            self.assertEqual(blocks[0],4)
            self.assertEqual(blocks[-14:],(1,)*14)
        self.assertEqual(control.production_blocks(18),(4,)+(1,)*14)

    def test_invalid_partition_and_nonfinite_estimates(self):
        for blocks in ((),(0,2),(-1,3),(1,), (True,1), (1.,1)):
            with self.assertRaises(ValueError):
                control.block_error_norm([1.,2.],[0.,0.],1.,blocks)
        for value in (math.inf,math.nan):
            with self.assertRaises(ValueError):
                control.block_error_norm([value],[0.],1.,(1,))
        with self.assertRaises(ValueError):
            control.block_error_norm([1.],[0.],math.inf,(1,))
        self.assertEqual(control.block_error_norm([-1.],[0.],-1.,(1,)),1.)

    def test_large_estimates_avoid_square_overflow(self):
        value=control.block_error_norm([1e200],[1e200],1e-200,(1,))
        self.assertTrue(math.isfinite(value))
        self.assertAlmostEqual(value,1/math.sqrt(1.01),places=14)
        self.assertEqual(control.block_error_norm([0.],[0.],1.,(1,)),0.)

    def test_core_and_interpolation_inherited_unchanged(self):
        cls=control.make_block_dop853((1,1))
        self.assertIs(cls._step_impl,DOP853._step_impl)
        self.assertIs(cls._dense_output_impl,DOP853._dense_output_impl)
        self.assertEqual(control.error_control_identity()['scipy_version'],scipy.__version__)

    def test_standalone_overlay_and_legacy_default(self):
        root=Path(__file__).resolve().parents[1]
        native,solver=build_refined_sources.overlay(
            (root/'donors/pr171/positive_native.rs').read_bytes(),
            (root/'donors/pr171/positive_solver.py').read_bytes())
        ast.parse(solver)
        self.assertIn("choices=('rms','block-max'),default='rms'",solver)
        self.assertIn('def block_error_norm(',solver)
        self.assertNotIn('from error_control import',solver)
        self.assertIn("method='DOP853',rtol=2e-11 if a.tight else 2e-10",solver)
        self.assertIn('abs(er)<=1e-8*eg and abs(nr)<=1e-8*ng',solver)

    def test_reference_flag_and_native_command(self):
        plans=run_refinement.plan()
        args=(Path('/binary'),Path('/solver'),Path('/out'),10.,100)
        legacy=run_refinement.command(plans['age64'],*args)
        block=run_refinement.command(dict(plans['age64'],error_norm='block-max'),*args)
        self.assertEqual(legacy[-2:],['--error-norm','rms'])
        self.assertEqual(block[-2:],['--error-norm','block-max'])
        native=run_refinement.command(dict(plans['time8'],error_norm='block-max'),*args)
        self.assertNotIn('--error-norm',native)

    def test_validate_output_norm_matches_with_historical_rms_default(self):
        config=run_refinement.plan()['age64']
        endpoint=dict(N=1.,U=20.,flat=[],ledgers=[],Gamma_s=[],
                      heat_erg_per_absorber_s=[],cohorts=[])
        result={key:config[key] for key in ('q','birth_panels','n_mu','source_subdivisions','transport_cells')}
        result.update(status='SCOPED_NUMERICAL_EXECUTION_COMPLETE',server_exit=0)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name,value in [('endpoint.json',endpoint),('solver_return.json',result),
                               ('ledgers.json',dict(energy_normalized=0.,photon_normalized=0.))]:
                (root/name).write_text(json.dumps(value))
            run_refinement.validate_outputs(config,root)
            with self.assertRaisesRegex(ValueError,'REFERENCE_ERROR_NORM_MISMATCH'):
                run_refinement.validate_outputs(dict(config,error_norm='block-max'),root)


if __name__ == '__main__':
    unittest.main()
