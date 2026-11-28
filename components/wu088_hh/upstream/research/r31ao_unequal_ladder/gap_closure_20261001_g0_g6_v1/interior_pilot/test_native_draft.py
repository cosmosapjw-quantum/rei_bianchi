"""Structural contract checks only; NOT a C++ compiler or runtime oracle."""
from pathlib import Path
import unittest

HERE=Path(__file__).parent


class NativeDraftStructure(unittest.TestCase):
    def source(self,name):
        self.assertTrue((HERE/name).is_file(),'native wrapper implementation is absent')
        return (HERE/name).read_text()

    def test_real_integrator_call_and_initialized_limits(self):
        s=self.source('petras_host.cpp')
        for token in ('acb_calc_integrate(', 'acb_calc_integrate_opt_init(', 'options->eval_limit',
                      'options->depth_limit','options->deg_limit','options->use_heap'):
            self.assertIn(token,s)

    def test_full_outer_box_no_midpoint_accessor(self):
        s=self.source('petras_host.cpp')
        self.assertIn('acb_set(context.outer_box.value, outer_box)',s)
        self.assertIn('slice.outer_box = outer_box',s)
        self.assertNotIn('arb_midref(',s)
        self.assertNotIn('arf_get_d(',s)

    def test_achieved_radius_and_nonfinite_refusal(self):
        s=self.source('petras_host.cpp')
        for token in ('arb_radref(acb_realref(out))','arb_radref(acb_imagref(out))',
                      'acb_is_finite(out)','acb_indeterminate(out)','ARB_CALC_SUCCESS'):
            self.assertIn(token,s)

    def test_shared_counted_budget_and_single_thread(self):
        s=self.source('petras_host.cpp')
        for token in ('dispatched_evaluations >=','callback_entries','integration_calls >=',
                      'flint_get_num_threads() != 1','budget.stopped'):
            self.assertIn(token,s)

    def test_uniform_and_point_policies_remain_separate(self):
        s=self.source('petras_host.cpp')
        for token in ('uniform_inner','point_inner','joint_holomorphy_proved',
                      'outer_order == 1 || inner_order == 1'):
            self.assertIn(token,s)

    def test_native_fixture_is_synthetic_and_refusal_focused(self):
        s=self.source('native_petras_synthetic.cpp')
        for token in ('1, 3','1, 6','midpoint_only','max_dispatched_evaluations = 1',
                      'synthetic_only','flint_set_num_threads(1)'):
            self.assertIn(token,s)
        self.assertNotIn('FROZEN_INPUTS',s)
        self.assertNotIn('ASSEMBLED_OD',s)

    def test_build_script_does_not_execute_binary(self):
        s=self.source('build_petras_host.sh')
        self.assertIn('3.4.0',s)
        self.assertIn('verify_build_inputs.py',s)
        self.assertIn('Built only',s)
        self.assertNotIn('\n"$WU088_PETRAS_BUILD_OUT/native_petras_synthetic"\n',s)

    def test_nested_analytic_trial_refusal_is_not_global_failure(self):
        s=self.source('petras_host.cpp')
        self.assertIn('c.speculative_parameter_trial',s)
        self.assertIn('outer_analytic_trial_domain_refusal',s)
        self.assertIn('outer_order==1',s)
        self.assertIn('order==1 && !context.budget->stopped',s)

    def test_uniform_fixture_uses_exact_rational_corners(self):
        s=self.source('native_petras_synthetic.cpp')
        self.assertIn('arb_contains_fmpq(acb_realref(out.value)',s)
        self.assertIn('arb_contains_fmpq(acb_imagref(out.value)',s)
        self.assertNotIn('acb_contains(out.value,image.value)',s)

    def test_too_wide_diagnostic_preserves_returned_radius(self):
        s=self.source('petras_host.cpp')
        h=self.source('petras_host.hpp')
        self.assertIn('mag_dump_str(',s)
        self.assertIn('real_radius_dump',h)
        self.assertIn('imag_radius_dump',h)


if __name__=='__main__': unittest.main()
