import copy
from dataclasses import replace
from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import adapter as a

class ReadOnlyAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.up = a.upstream()
        cls.packet = cls.up.load_packet()

    def test_actual_stored_point_and_exact_parity(self):
        p = copy.deepcopy(self.packet)
        result = a.readout(p)
        previous = json.loads((a.PACKAGE/'receiver-observed/RECEIVER_OUTPUT.json').read_text())
        self.assertEqual(result['conditional_output'], previous)
        self.assertEqual(p, self.packet)
        self.assertEqual(result['typed_input']['generator_ids'], [])
        self.assertEqual(result['producer_context']['provider_cutoffs_ev'], [13.6,24.59,54.42])
        self.assertEqual(result['extra_provider_calls'], 0)
        self.assertEqual(result['physical'], 'HOLD')

    def test_missing_and_forbidden_owner_representations(self):
        for p in (None, {}, {'total':[1]*13}, {'rates':[1]*3},
                  {'rhs':{'photo':[0]*3}}, {'Gamma':[0]*3},
                  {'Gamma':[0]*3,'incident_Ecal':None}):
            with self.subTest(p=p):
                r=a.readout(p)
                self.assertEqual(r['status'],'MISSING_INSTANTANEOUS_JOINT_MOMENTS')
                self.assertGreater(len(r['required_producer_fields']), 8)

    def test_actual_receiver_exact_epoch_and_state_expectations(self):
        _,_,ctx,_=self.up.typed_input(self.packet)
        for wrong in (replace(ctx,epoch_ln_a=ctx.epoch_ln_a+Fraction(1,2**60)),
                      replace(ctx,bound_state=replace(ctx.bound_state,h=ctx.bound_state.h+Fraction(1,2**60))),
                      replace(ctx,provider_id=ctx.provider_id+'wrong'),
                      replace(ctx,source_id=ctx.source_id+'wrong')):
            with self.subTest(wrong=wrong):
                with self.assertRaisesRegex(ValueError,'CONTEXT_MISMATCH'):
                    a.readout(self.packet,expected_context=wrong)

    def test_units_threshold_provider_clock_species_values(self):
        mutations=[('units','Gamma','cm^-3 s^-1'),('units','incident_Ecal','erg absorber^-1 s^-1'),
                   ('context','gas_epoch_ln_a',-2.0),('context','photo_provider','wrong'),
                   ('context','chi_ev',[13.6,24.59,54.42]),
                   ('context','producer_commit','wrong')]
        for section,key,value in mutations:
            p=copy.deepcopy(self.packet);p[section][key]=value
            with self.subTest(key=key):
                with self.assertRaises(ValueError):a.readout(p)
        p=copy.deepcopy(self.packet);p['Gamma'].reverse()
        with self.assertRaises(ValueError):a.readout(p)

    def test_uncertainty_generators_not_invented(self):
        for field,value in [('generators',[[0]*6]),('generator_ids',['invented']),
                            ('provider_error','PASS'),('physical','PASS')]:
            p=copy.deepcopy(self.packet);p[field]=value
            with self.subTest(field=field):
                with self.assertRaises(ValueError):a.readout(p)

    def test_original_schema_family_and_generator_identity_preserved(self):
        out = a.readout(self.packet)
        for key in ('schema', 'family_id', 'family_kind', 'generators',
                    'generator_ids', 'uncertainty_widths'):
            self.assertEqual(out['producer_moment_identity'][key], self.packet[key])
        for key in ('schema', 'family_id'):
            p = copy.deepcopy(self.packet)
            p[key] = 'wrong'
            with self.assertRaisesRegex(ValueError, 'SCHEMA_FAMILY_ID_REQUIRED'):
                a.readout(p)

    def test_no_observer_provider_or_native_execution(self):
        calls=[]
        def profile(frame,event,arg):
            if event=='call' and frame.f_code.co_name in ('observe','cross_section','igm_point_rhs','advance','spectral_moments'):
                calls.append(frame.f_code.co_name)
        sys.setprofile(profile)
        try:a.readout(self.packet)
        finally:sys.setprofile(None)
        self.assertEqual(calls,[])

if __name__=='__main__':unittest.main()
