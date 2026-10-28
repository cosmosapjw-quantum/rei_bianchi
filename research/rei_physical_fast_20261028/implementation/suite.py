"""One actual-data non-IVP calibration suite and adapter output pass."""
import csv
import hashlib
import json
import math
from pathlib import Path
import unittest
import calibration as c
from current_entrypoint import resolve_case
import lumina_adapter as lumina

CONTRACT=json.loads((c.UNIT/'theory/PHYSICAL_NEXT_CONTRACT.json').read_text())
RTOL=CONTRACT['numeric_checks']['relative_tolerance'];ATOL=CONTRACT['numeric_checks']['absolute_tolerance']


class CalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data,cls.template=c.load_sources();cls.fit=c.fit_sources()
    def close(self,a,b):self.assertTrue(math.isclose(a,b,rel_tol=RTOL,abs_tol=ATOL),msg=f'{a!r} != {b!r}')

    def test_user_default_and_explicit_override(self):
        result=resolve_case();self.assertEqual(result['resolved_case'],'ON_refined');self.assertFalse(result['solver_invoked'])
        self.assertEqual(result['settings']['rtol'],2e-8);self.assertEqual(result['settings']['scaled_atol'],2e-12)
        off=resolve_case('OFF_base');self.assertEqual(off['settings']['external_source_alpha'],0)
        self.assertEqual(off['settings']['fast_neutron_escape_s-1'],0)
        self.assertEqual(resolve_case('ON_base')['settings']['external_source_alpha'],result['settings']['external_source_alpha'])
        with self.assertRaises(ValueError):resolve_case('renamed_calibrated_toy')

    def test_covariance_scale_spd_and_reconstruction(self):
        covariance=self.data['statistical_covariance_dex2']
        self.close(covariance[0][0],.00218);self.close(covariance[0][1],.00142);self.close(covariance[-1][-1],.00488)
        L=c.cholesky(covariance)
        for i in range(7):
            for j in range(7):self.close(sum(L[i][k]*L[j][k] for k in range(7)),covariance[i][j])
        with self.assertRaises(ValueError):c.cholesky([[1.,2.],[2.,1.]])
        with self.assertRaises(ValueError):c.cholesky([[1.,.2],[.1,1.]])

    def test_independent_two_point_correlated_gls(self):
        covariance=[[1.,.5],[.5,4.]]
        fit=c.fit_log_amplitude([1.,3.],[0.,0.],covariance,[0.,0.])['statistical_only']
        self.close(fit['beta_log10_amplitude'],1.25);self.close(fit['variance_beta_dex2'],.9375)
        residual=[-.25,1.75]
        direct=(4*residual[0]**2-residual[0]*residual[1]+residual[1]**2)/3.75
        self.close(fit['residual_chi2'],direct);self.close(direct,1.)
        diagonal=c.fit_log_amplitude([1.,3.],[0.,0.],[[1.,0.],[0.,4.]],[0.,0.])['statistical_only']
        self.close(diagonal['beta_log10_amplitude'],1.4)
        self.assertGreater(abs(diagonal['beta_log10_amplitude']-fit['beta_log10_amplitude']),.1)

    def test_actual_fit_and_amplitude_equivariance(self):
        fit=self.fit['statistical_only']
        self.assertEqual(fit['degrees_of_freedom'],6)
        self.close(fit['residual_chi2'],fit['profiled_subtraction_identity_chi2'])
        self.assertLessEqual(fit['residual_chi2'],fit['unscaled_template_chi2'])
        shifted=c.fit_log_amplitude(self.data['values'],[x+.3 for x in self.fit['template_log10_Gamma12']],
            self.data['statistical_covariance_dex2'],self.data['slope_nuisance']['response_dex'])['statistical_only']
        self.close(shifted['beta_log10_amplitude'],fit['beta_log10_amplitude']-.3)
        self.close(shifted['residual_chi2'],fit['residual_chi2'])
        source=c.template_moments(3.,self.template);scaled=c.calibrated_moments(3.,fit['beta_log10_amplitude'],self.template)
        for key in c.RATE_FIELDS:self.close(scaled[key]/source[key],fit['amplitude'])

    def test_EOS_box_boundary_and_degeneracy(self):
        interior=c.fit_log_amplitude([1.,2.],[0.,0.],[[1.,0.],[0.,1.]],[1.,-1.])['EOS_box_profile']
        self.close(interior['theta'],.5);self.close(interior['residual_chi2'],0.)
        boundary=c.fit_log_amplitude([0.,4.],[0.,0.],[[1.,0.],[0.,1.]],[1.,-1.])['EOS_box_profile']
        self.close(boundary['theta'],1.);self.close(boundary['residual_chi2'],2.);self.assertTrue(boundary['theta_at_boundary'])
        degenerate=c.fit_log_amplitude([1.,3.],[0.,0.],[[1.,.5],[.5,4.]],[.1,.1])['EOS_box_profile']
        self.assertTrue(degenerate['degenerate_with_amplitude']);self.assertIsNone(degenerate['theta'])
        self.assertEqual(len(degenerate['theta_endpoint_reports']),2)
        self.close(degenerate['theta_endpoint_reports'][0]['chi2'],degenerate['theta_endpoint_reports'][1]['chi2'])
        self.assertLessEqual(self.fit['EOS_box_profile']['residual_chi2'],self.fit['statistical_only']['residual_chi2']+ATOL)

    def test_rate_interpolation_zeros_exact_knots_and_domains(self):
        for row in self.template['rows']:
            actual=c.template_moments(row[0],self.template)
            for key in c.RATE_FIELDS:
                expected=row[self.template['columns'].index(key)]
                if expected==0:self.assertEqual(actual[key],0.)
                else:self.close(actual[key]/expected,1.)
        self.close(c.log_interpolate(.5,[0.,1.],[1.,100.]),10.)
        zero=c.interpolate_rate(0.,[0.,1.],[0.,4.]);self.assertEqual(zero['value'],0.)
        ramp=c.interpolate_rate(.5,[0.,1.],[0.,4.]);self.close(ramp['value'],2.)
        self.assertEqual(ramp['method'],'LINEAR_RATE_ZERO_ENDPOINT')
        with self.assertRaises(ValueError):c.template_moments(20.,self.template)
        with self.assertRaises(ValueError):c.calibrated_moments(6.,0.,self.template)
        with self.assertRaises(ValueError):c.log_interpolate(.5,[0.,1.],[-1.,4.])

    def test_observed_interpolation_and_cross_covariance(self):
        data=self.data;cov=data['statistical_covariance_dex2']
        for j,z in enumerate(data['z']):
            result=c.observed_HI(z,data);self.close(result['log10_Gamma12'],data['values'][j])
            self.close(result['statistical_variance_dex2'],cov[j][j])
        middle=(data['z'][0]+data['z'][1])/2
        result=c.observed_HI(middle,data)
        self.close(result['log10_Gamma12'],sum(data['values'][:2])/2)
        self.close(result['statistical_variance_dex2'],(cov[0][0]+2*cov[0][1]+cov[1][1])/4)
        self.close(c.observed_covariance(middle,data['z'][0],data),(cov[0][0]+cov[1][0])/2)
        self.close(c.observed_covariance(data['z'][0],middle,data),c.observed_covariance(middle,data['z'][0],data))
        with self.assertRaises(ValueError):c.observed_HI(20.,data)

    def test_event_heat_identity_and_missing_fields(self):
        result=c.event_heat_mapping(.5,1e-12,3e-12,13.6,.002)
        self.close(result['events_per_Href_s']/5e-13,1.)
        self.close(result['absorbed_eV_per_Href_s']/result['events_per_Href_s'],16.6)
        self.close(result['events_cm-3_s-1']/1e-15,1.)
        self.assertFalse(result['extra_4pi_or_c_applied'])
        self.assertEqual(c.event_heat_mapping(0.,1e-12,3e-12,13.6,.002)['absorbed_eV_per_Href_s'],0.)
        adapter=c.bath_adapter(3.,self.fit['statistical_only']['beta_log10_amplitude'])
        for key in ('T_K','electron_density_cm-3','Li_photo_rates','MeV_photodisintegration','CR_source_yields',
                    'fast_stopping_escape','inverse_weak_bath','H_s-1','shear','initial_populations'):
            self.assertIsNone(adapter[key])
        self.assertFalse(adapter['old_bath_mutated']);self.assertFalse(adapter['solver_invoked'])

    def test_Lumina_domains_medians_and_zero(self):
        histories=lumina.load_histories()
        self.assertEqual(len(histories['SFRD']['rows_ascending_z']),246)
        self.assertEqual(len(histories['xHeIII_median']['rows_ascending_z']),294)
        initial=histories['SFRD']['rows_ascending_z'][-1]
        self.assertEqual(lumina.history_at('SFRD',initial[0],histories)['value'],0.)
        self.assertEqual(lumina.history_at('xHI_median',3.,histories)['status'],'MISSING_OUTSIDE_SUPPLIED_SUPPORT')
        self.assertEqual(lumina.history_at('xHeIII_median',3.,histories)['status'],'AVAILABLE_MODEL_HISTORY')
        raw=histories['xHeIII_median']['rows_ascending_z'][0]
        self.assertGreater(raw[2],raw[1]);self.assertGreater(raw[1],raw[3]) # header mismatch retained, never sorted
        self.close(lumina.history_at('xHeIII_median',raw[0],histories)['value'],raw[1])
        self.assertIn('UNRESOLVED',histories['xHeIII_median']['quantile_status'])


def write_products(out,fit):
    data,template=c.load_sources()
    fit.update({'status':'COMPLETED_ACTUAL_DATA_CALIBRATION','scientific_admission':'PENDING_ASTRA_REVIEW',
                'full_physical_F4':'PARTIAL','physical_fast_completed':4,'physical_fast_total':7,
                'global_working_completed':33,'global_total':88,'old_runs_mutated':False,'new_IVPs':0})
    (out/'CALIBRATION_RESULT.json').write_text(json.dumps(fit,indent=2,allow_nan=False)+'\n')
    with (out/'CALIBRATION_POINTS.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['z','observed_log10_Gamma12','statistical_sigma_dex','template_log10_Gamma12',
            'stat_fit_log10_Gamma12','EOS_fit_log10_Gamma12','statistical_residual_dex','EOS_residual_dex'])
        for j,z in enumerate(data['z']):
            model=fit['template_log10_Gamma12'][j]
            writer.writerow([z,data['values'][j],math.sqrt(data['statistical_covariance_dex2'][j][j]),model,
                model+fit['statistical_only']['beta_log10_amplitude'],model+fit['EOS_box_profile']['beta_log10_amplitude'],
                fit['residuals_statistical_only'][j],fit['residuals_EOS_profile'][j]])
    with (out/'CALIBRATED_MOMENTS.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['z',*c.RATE_FIELDS,'calibration_case'])
        for case in ('statistical_only','EOS_box_profile'):
            beta=fit[case]['beta_log10_amplitude']
            for k in range(101):
                z=2.4+(4.75-2.4)*k/100;moments=c.calibrated_moments(z,beta,template)
                writer.writerow([z,*[moments[field] for field in c.RATE_FIELDS],case])
    observed=[c.observed_HI(z,data) for z in data['z']]
    (out/'RADIATION_ADAPTER.json').write_text(json.dumps({'conditional_template_bath_at_z3':c.bath_adapter(3.,fit['statistical_only']['beta_log10_amplitude']),
        'observation_only_at_data_knots':observed,'full_logdex_covariance_between_knots':[
            [c.observed_covariance(a,b,data) for b in data['z']] for a in data['z']],
        'missing_fields_are_not_zeros':True,'measured_domain_z':[2.4,4.75],'raw_template_domain_z':[0,15.1]},indent=2,allow_nan=False)+'\n')
    (out/'LUMINA_ADAPTER_REPORT.json').write_text(json.dumps(lumina.domain_report(),indent=2,allow_nan=False)+'\n')
    (out/'DEFAULT_RESOLUTION.json').write_text(json.dumps(resolve_case(),indent=2)+'\n')
    paths=[p for p in (c.UNIT/'sources').rglob('*') if p.is_file()]
    paths += [p for p in (c.UNIT/'implementation').glob('*') if p.is_file()]
    paths += [c.UNIT/'theory/PHYSICAL_NEXT_CONTRACT.json',c.UNIT/'theory/PHYSICAL_NEXT_CONTRACT.md']
    (out/'SOURCE_IDENTITIES.json').write_text(json.dumps({str(p.relative_to(c.UNIT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')


def main():
    out=c.UNIT/'outputs';out.mkdir(exist_ok=True)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(CalibrationTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors),'relative_tolerance':RTOL,'absolute_tolerance':ATOL,
            'IVPs':0,'old_regression_runs':0,'actual_observation_fit_executed':hasattr(CalibrationTests,'fit'),
            'scope':'Conditional HI UVB calibration, partial radiation input and Lumina model-domain adapter'}
    if result.wasSuccessful():write_products(out,CalibrationTests.fit)
    (out/'TEST_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__=='__main__':main()
