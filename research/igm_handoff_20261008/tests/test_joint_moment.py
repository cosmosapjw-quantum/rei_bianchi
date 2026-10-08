"""Independent rational vertex oracle and fail-closed contract checks."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bridge.joint_moment import (
    CLOCK, ContractError, FixedContext, JointMomentFamily, MissingPremise,
    Moments, State, conditional_joint_enclosure,
)

CHI = (F(13), F(24), F(54))


def state(**changes):
    values = dict(h=F(1,4), y=F(1,5), z=F(1,10), w_erg_h=F(50),
                  n_h=F(10), n_he=F(1), hubble_s=F(2), kb_erg_k=F(3),
                  ev_erg=F(5), c_thomson_cm3_s=F(7))
    values.update(changes)
    return State(**values)


def context(s, chi=CHI):
    return FixedContext("synthetic-exact-source", "test-clock", "test-state",
                        "test-provider", s, F(-2), chi)


def moment(gamma, excess=(F(0),)*3):
    return Moments(tuple(gamma), tuple(c*g+e for c,g,e in zip(CHI,gamma,excess)))


def family(s=None, center=None, generators=()):
    s = state() if s is None else s
    if center is None:
        center = moment((F(4),F(3),F(2)), (F(8),F(8),F(8)))
    return JointMomentFamily(center, tuple(generators), context(s),
                             "synthetic-family", "supplied_uncertainty",
                             tuple("synthetic-u-"+str(i) for i in range(len(generators))))


def enclosure(f, premises=("Synthetic exact family supplied as a premise.",)):
    return conditional_joint_enclosure(f.context.bound_state, CHI, f,
                                       context=f.context, premises=premises)


def independent_formula(s, rates, energy):
    """Direct equations; never invokes project(), thermal_response() or bounds()."""
    helium = s.n_he / s.n_h
    electron_fraction = s.h + helium * (s.y + 2*s.z)
    particles = 1 + helium + electron_fraction
    absorbers = (1-s.h, helium*(1-s.y-s.z), helium*s.y)
    electron = sum((a*g for a,g in zip(absorbers,rates)), F(0))
    absorbed = s.ev_erg * sum((a*e for a,e in zip(absorbers,energy)), F(0))
    binding = s.ev_erg * sum((a*c*g for a,c,g in zip(absorbers,CHI,rates)), F(0))
    heat = absorbed - binding
    heat_temperature = 2*heat / (3*s.kb_erg_k*particles)
    particle_temperature = -2*s.w_erg_h*electron / (3*s.kb_erg_k*particles**2)
    return {
        "h_dt_s": (1-s.h)*rates[0],
        "heii_dt_s": (1-s.y-s.z)*rates[1]-s.y*rates[2],
        "heiii_dt_s": s.y*rates[2],
        "electron_dt_per_h_s": electron,
        "heat_erg_h_s": heat,
        "binding_erg_h_s": binding,
        "absorbed_erg_h_s": absorbed,
        "temperature_dt_k_s": heat_temperature+particle_temperature,
        "heating_temperature_dt_k_s": heat_temperature,
        "particle_temperature_dt_k_s": particle_temperature,
        "photo_q_ell_source": s.c_thomson_cm3_s*s.n_h*electron/s.hubble_s**2,
    }


class JointMomentTests(unittest.TestCase):
    def test_exact_extrema_equal_independent_64_vertex_oracle(self):
        generators = []
        for j in range(6):
            rates = tuple(F((-1)**(i+j)*(i+1), 20+j) for i in range(3))
            excess = tuple(F((-1)**j*(i+1), 13+j) for i in range(3))
            generators.append(moment(rates, excess))
        f = family(generators=generators)
        result = enclosure(f)
        vertices = []
        for signs in product((-1,1), repeat=6):
            rates = tuple(f.center.gamma[i] + sum(
                (u*g.gamma[i] for u,g in zip(signs,generators)), F(0)) for i in range(3))
            energy = tuple(f.center.energy_ev_s[i] + sum(
                (u*g.energy_ev_s[i] for u,g in zip(signs,generators)), F(0)) for i in range(3))
            vertices.append(independent_formula(f.context.bound_state,rates,energy))
        for key, bounds in result.bounds_native.items():
            self.assertEqual(bounds, (min(v[key] for v in vertices), max(v[key] for v in vertices)), key)
        self.assertEqual(result.physical_status, "HOLD")
        self.assertFalse(result.history_integrated)
        self.assertIn("UNVERIFIED", result.uncertainty_truth)

    def test_shared_generator_preserves_zero_heat_width(self):
        center = moment((F(4),F(0),F(0)))
        generator = moment((F(1),F(0),F(0)))
        f = family(center=center, generators=(generator,))
        result = enclosure(f)
        self.assertEqual(result.bounds_native["heat_erg_h_s"], (F(0),F(0)))
        # Independentized Gamma/Ecal boxes choose opposite extrema and give a
        # spurious nonzero heat radius, which this exact test must reject.
        independent_box_radius = 2*f.context.bound_state.ev_erg*(1-f.context.bound_state.h)*CHI[0]
        self.assertGreater(independent_box_radius, 0)
        self.assertNotEqual(result.bounds_native["heat_erg_h_s"],
                            (-independent_box_radius,independent_box_radius))

    def test_positive_heating_can_have_negative_temperature_response(self):
        s = state(h=F(0),y=F(0),z=F(0),n_he=F(0),w_erg_h=F(100))
        f = family(s, moment((F(1),F(0),F(0)), (F(1,10),F(0),F(0))))
        result = enclosure(f)
        self.assertGreater(result.center_native["heat_erg_h_s"],0)
        self.assertLess(result.center_native["temperature_dt_k_s"],0)
        self.assertEqual(result.center_native["temperature_dt_k_s"],
                         F(2,3)/(s.kb_erg_k)*(F(1,2)-F(100)))
        self.assertNotEqual(result.center_native["temperature_dt_k_s"],
                            result.center_native["heating_temperature_dt_k_s"])
        # A signed generator is a difference, not an absolute physical source:
        # negative heat does not force negative temperature change either.
        g = moment((F(-1),F(0),F(0)), (F(-1,10),F(0),F(0)))
        with_difference = enclosure(family(s,
            moment((F(4),F(0),F(0)),(F(2),F(0),F(0))), (g,)))
        self.assertLess(with_difference.generators_native[0]["heat_erg_h_s"],0)
        self.assertGreater(with_difference.generators_native[0]["temperature_dt_k_s"],0)

    def test_pure_h_neutral_and_zero_absorber_limits(self):
        s = state(h=F(0),y=F(0),z=F(0),n_he=F(0))
        r = enclosure(family(s, moment((F(2),F(0),F(0)))))
        self.assertEqual(r.center_native["h_dt_s"], F(2))
        self.assertEqual(r.center_native["electron_dt_per_h_s"], F(2))
        self.assertEqual(r.center_native["heii_dt_s"], F(0))
        self.assertEqual(r.center_native["heiii_dt_s"], F(0))
        self.assertEqual(r.center_native["heat_erg_h_s"], F(0))
        full = state(h=F(1),y=F(0),z=F(1))
        self.assertTrue(all(v == 0 for v in enclosure(family(full)).center_native.values()))
        neutral = state(h=F(0),y=F(0),z=F(0))
        zero = enclosure(family(neutral,moment((F(0),)*3)))
        self.assertTrue(all(v == 0 for v in zero.center_native.values()))

    def test_dt_to_dln_a_has_exactly_one_h_and_q_has_no_extra_h(self):
        f = family()
        r = enclosure(f)
        h = f.context.bound_state.hubble_s
        self.assertNotEqual(h,1)
        self.assertEqual(r.bounds_dln_a["h_dln_a"], tuple(v/h for v in r.bounds_native["h_dt_s"]))
        self.assertEqual(r.bounds_dln_a["heat_erg_h_dln_a"], tuple(v/h for v in r.bounds_native["heat_erg_h_s"]))
        self.assertEqual(r.bounds_dln_a["photo_q_ell_source"],r.bounds_native["photo_q_ell_source"])
        self.assertNotEqual(r.bounds_dln_a["photo_q_ell_source"],
                            tuple(v/h for v in r.bounds_native["photo_q_ell_source"]))

    def test_entire_family_domain_and_zero_rate_energy(self):
        for bad in (
            family(center=moment((F(1),F(1),F(1))),
                   generators=(moment((F(2),F(0),F(0))),)),
            family(center=moment((F(1),)*3,(F(1),)*3),
                   generators=(moment((F(0),)*3,(F(2),F(0),F(0))),)),
            family(center=moment((F(0),F(1),F(1)),(F(1),F(0),F(0)))),
            family(center=moment((F(1),F(1),F(1)),(F(1),F(0),F(0))),
                   generators=(moment((F(1),F(0),F(0))),)),
        ):
            with self.subTest(center=bad.center, generators=bad.generators):
                with self.assertRaises(ContractError): enclosure(bad)

    def test_context_epoch_state_units_clock_and_record_kind_fail_closed(self):
        f = family()
        for changed_context in (
            replace(f.context,source_id="another-source"),
            replace(f.context,clock_id="another-clock"),
            replace(f.context,state_id="another-state"),
            replace(f.context,provider_id="another-provider"),
            replace(f.context,epoch_ln_a=F(-3)),
            replace(f.context,bound_state=state(h=F(1,3))),
        ):
            with self.subTest(context=changed_context):
                with self.assertRaises(ContractError):
                    conditional_joint_enclosure(f.context.bound_state,CHI,f,
                        context=changed_context,premises=("explicit",))
        with self.assertRaises(ContractError):
            conditional_joint_enclosure(state(h=F(1,3)),CHI,f,context=f.context,premises=("explicit",))
        for changes in (
            {"gamma_unit":"photons/H"}, {"energy_unit":"erg/H"},
            {"energy_unit":"erg absorber^-1 s^-1"},
            {"input_kind":"integrated_owner_record"},
            {"family_kind":"true-error-certified"}, {"family_id":" "},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ContractError): replace(f,**changes)
        for changes in ({"clock":"t=seconds"},{"epoch_ln_a":-2.0},{"source_id":""}):
            with self.subTest(changes=changes):
                with self.assertRaises(ContractError): replace(f.context,**changes)
        with self.assertRaises(ContractError): state(hubble_s=F(0))

    def test_missing_premises_family_and_inexact_values_rejected(self):
        f=family()
        for p in (None,(),[],("",),"not a list"):
            with self.subTest(premises=p):
                with self.assertRaises(MissingPremise): enclosure(f,p)
        for bad_family in (None,{},f.center):
            with self.subTest(family=bad_family):
                with self.assertRaises(ContractError):
                    conditional_joint_enclosure(f.context.bound_state,CHI,bad_family,
                        context=f.context,premises=("explicit",))
        with self.assertRaises(ContractError): Moments((1.0,F(0),F(0)),(F(0),)*3)
        with self.assertRaises(ContractError): replace(f,generators=(f.center,)*7)
        with self.assertRaises(ContractError):
            conditional_joint_enclosure(f.context.bound_state,(13.0,F(24),F(54)),f,
                context=f.context,premises=("explicit",))

    def test_serialization_retains_context_family_and_exact_rationals(self):
        f=replace(family(),family_kind="finite_rule_envelope")
        document=json.loads(json.dumps(enclosure(f).as_json()))
        self.assertEqual(document["family_kind"],"finite_rule_envelope")
        self.assertEqual(document["context"]["epoch_ln_a"],"-2/1")
        self.assertEqual(document["context"]["chi_ev"],["13/1","24/1","54/1"])
        self.assertEqual(document["physical_status"],"HOLD")
        self.assertIn("NOT_ESTABLISHED",document["common_spectrum_realizability"])
        self.assertEqual(F(document["bounds_native"]["h_dt_s"][0]),F(3))

    def test_independently_derived_theory_vectors(self):
        # Separate theory author supplied these exact expected values without
        # importing the vendor or this implementation; source lives in inputs.
        document=json.loads((Path(__file__).resolve().parents[1]/"inputs"/"TOY_VECTORS.json").read_text())
        s=State(**{k:F(v) for k,v in document["state"].items()})
        chi=tuple(F(v) for v in document["chi_ev"])
        def unpack(values):
            return Moments(tuple(F(v) for v in values[:3]),tuple(F(v) for v in values[3:]))
        for case in document["cases"]:
            with self.subTest(case=case["id"]):
                f=JointMomentFamily(unpack(case["center"]),
                    tuple(unpack(g) for g in case["generators"]),context(s,chi),
                    case["id"],"supplied_uncertainty",
                    tuple(case["id"]+"-u-"+str(i) for i in range(len(case["generators"]))))
                if not case["admission_expected"]:
                    with self.assertRaises(ContractError):
                        conditional_joint_enclosure(s,chi,f,context=f.context,premises=("Synthetic oracle family.",))
                else:
                    r=conditional_joint_enclosure(s,chi,f,context=f.context,premises=("Synthetic oracle family.",))
                    self.assertEqual(r.center_native,{k:F(v) for k,v in case["output_center"].items()})
                    self.assertEqual(r.bounds_native,{k:tuple(F(v) for v in b) for k,b in case["joint_extrema"].items()})

    def test_thresholds_are_bound_to_fixed_context(self):
        f=family()
        different=(CHI[0]+F(1,100),CHI[1],CHI[2])
        with self.assertRaisesRegex(ContractError,"FIXED_CONTEXT_THRESHOLD_MISMATCH"):
            conditional_joint_enclosure(f.context.bound_state,different,f,
                context=f.context,premises=("explicit",))
        with self.assertRaisesRegex(ContractError,"CONTEXT_MISMATCH"):
            conditional_joint_enclosure(f.context.bound_state,different,f,
                context=replace(f.context,chi_ev=different),premises=("explicit",))
        for bad in ((F(13),F(24)),(13.0,F(24),F(54)),(F(-1),F(24),F(54)),list(CHI)):
            with self.subTest(thresholds=bad):
                with self.assertRaises(ContractError): replace(f.context,chi_ev=bad)

    def test_generator_ids_are_required_unique_and_retained(self):
        g0=moment((F(1),F(0),F(0)))
        g1=moment((F(0),F(1),F(0)))
        f=family(generators=(g0,g1))
        for bad in ((),("one",),("same","same"),("valid"," "),("valid",None),["u0","u1"]):
            with self.subTest(ids=bad):
                with self.assertRaises(ContractError): replace(f,generator_ids=bad)
        ids=("shared-spectrum-normalization","shared-spectrum-shape")
        r=enclosure(replace(f,generator_ids=ids))
        self.assertEqual(r.generator_ids,ids)
        self.assertEqual(r.as_json()["generator_ids"],list(ids))
        self.assertEqual(len(r.generators_native),len(ids))
        self.assertEqual(r.generators_native[0]["h_dt_s"],F(3,4))
        self.assertEqual(r.generators_native[1]["h_dt_s"],F(0))


if __name__ == "__main__":
    unittest.main()
