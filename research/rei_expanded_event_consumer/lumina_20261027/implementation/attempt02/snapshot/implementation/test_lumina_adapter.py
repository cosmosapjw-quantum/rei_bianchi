"""Bounded deterministic contract tests; no IVP, quadrature, or network."""
from dataclasses import replace
from decimal import Decimal
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import unittest

from lumina_adapter import (ROOT, DomainError, EV_TO_ERG, TRUE_C_CM_S, IncidentPhotonExposure,
                            LEFT_VECTORS, STOICHIOMETRY, benchmark_panels,
                            energy_opacity_cm2,
                            exposure_from_proper_energy_density,
                            helium_electron_projection, hii_complement,
                            kinetic_support, load_moments, load_public_series,
                            moment_operator, parse_series, photo_heating, reaction_source)


class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.series = load_public_series()
        cls.rows = load_moments()

    def exposure(self, regime="early", phi=None, z=None):
        chosen = tuple(r for r in self.rows if r.regime == regime)
        return IncidentPhotonExposure(tuple(phi if phi is not None else (0.0,)*len(chosen)),
            "photon cm^-2 s^-1", "proper", regime, z if z is not None else (5.0 if regime == "early" else 4.75),
            tuple(r.template for r in chosen), "transport_reduced_0.2c", (0.0, 30.0),
            "fixture:single-test", "fixture:instant")

    def test_actual_count_endpoint_grid_and_identity(self):
        specs = {"HI": (258, 29.428494, 4.774995, -1),
                 "HeIII": (294, 29.428494, 2.992408, -1),
                 "SFRD": (246, 27.433528, 2.991495, -1),
                 "tau": (981, 0., 49., 1)}
        for name, (count, first, last, sign) in specs.items():
            s = self.series[name]
            self.assertEqual(len(s.rows), count)
            self.assertEqual((s.rows[0][0], s.rows[-1][0]), (first,last))
            self.assertTrue(all(sign*(b[0]-a[0])>0 for a,b in zip(s.rows,s.rows[1:])))
            self.assertEqual(s.source_sha256, sha256((ROOT/"data"/("tau_cmb_vs_z_lumina.txt" if name=="tau" else ("sfrd_lumina.txt" if name=="SFRD" else name+"_reion_lumina.txt"))).read_bytes()).hexdigest())
        self.assertEqual(self.series["tau"].rows[-1][1], .0543742529)

    def test_raw_quantile_flags_and_HII_order(self):
        hi, he = self.series["HI"], self.series["HeIII"]
        self.assertIn("valid_declared_quantiles", hi.validation_flags)
        self.assertIn("invalid_quantile_order:203", he.validation_flags)
        out = hii_complement(hi)
        r, x = hi.rows[-1], out.rows[-1]
        self.assertEqual(x[2], 1-r[3]); self.assertEqual(x[3], 1-r[2])
        self.assertEqual(x[6], 1-r[7]); self.assertEqual(x[7], 1-r[6])
        self.assertEqual(out.redshift_domain, hi.redshift_domain)
        self.assertEqual(hi.raw_column_names[1], "xHI_median")
        self.assertEqual(he.raw_column_names[-1], "xHeIII_max")

    def test_panels_native_grid_and_scope(self):
        p = benchmark_panels(self.series)
        self.assertEqual([len(p[k]["z"]) for k in ("HI_and_HII","HeIII","SFRD","tau")], [258,294,246,981])
        self.assertEqual(p["HeIII"]["median_only"][-1], .993331657)
        self.assertNotIn("mass_weighted_xe", p)
        self.assertEqual(p["tau"]["paper_reported_Planck_reference_constraint"]["sigma"], .007)

    def test_parser_bad_input(self):
        raw = (ROOT/"data/HI_reion_lumina.txt").read_bytes()
        url = self.series["HI"].source_url
        bad = [raw.replace(b"29.428494",b"nan",1), raw.replace(b"29.428494",b"-1.000000",1),
               raw.replace(b"28.967040",b"31.000000",1), raw.replace(b"9.99999000e-01",b"1.50000000e+00",1)]
        for value in bad:
            with self.assertRaises(DomainError):
                parse_series(value, source_url=url, expected_sha256=sha256(value).hexdigest(), quantity="HI")
        with self.assertRaises(DomainError):
            parse_series(raw, source_url=url, expected_sha256="0"*64, quantity="HI")

    def test_stoichiometry_exact_and_reaction(self):
        for left in LEFT_VECTORS:
            self.assertEqual(tuple(sum(left[i]*STOICHIOMETRY[i][j] for i in range(6)) for j in range(3)), (0,0,0))
            self.assertEqual(sum(x*y for x,y in zip(left,reaction_source((2.,-3.,4.)))), 0)

    def test_helium_projection_and_invalid_guesses(self):
        self.assertAlmostEqual(helium_electron_projection(1,0,0,1),22/19,places=14)
        self.assertAlmostEqual(helium_electron_projection(0,1,0,0),0)
        with self.assertRaises(DomainError):
            helium_electron_projection(1e-6,1-(1e-6-1.26666667e-5)-1.26666667e-5,
                                       1e-6-1.26666667e-5,1.26666667e-5)

    def test_seven_moments_and_zero_flux(self):
        self.assertEqual((len(self.rows),sum(r.regime=="early" for r in self.rows)),(7,6))
        for regime in ("early","late"):
            r=moment_operator(self.exposure(regime),self.rows)
            for s in r.active_species:
                j=("HI","HeI","HeII").index(s)
                self.assertEqual((r.gamma_s[j],r.heat_erg_s_target[j],r.absorbed_erg_s_target[j]),(0,0,0))

    def test_single_bin_decimal_independence(self):
        phi=(0,0,Decimal("2.5e8"),0,0,0)
        x=self.exposure(phi=tuple(map(float,phi)))
        r=moment_operator(x,self.rows)
        for j in range(3):
            sigma=Decimal(str(self.rows[2].sigma[j])); excess=Decimal(str(self.rows[2].excess[j]))
            gamma=float(phi[2]*sigma)
            heat=float(phi[2]*sigma*excess*Decimal("1.602176634e-12"))
            self.assertTrue(math.isclose(r.gamma_s[j],gamma,rel_tol=1e-12,abs_tol=1e-30))
            self.assertTrue(math.isclose(r.heat_erg_s_target[j],heat,rel_tol=1e-12,abs_tol=1e-30))
            self.assertTrue(math.isclose(r.absorbed_erg_s_target[j],r.gamma_s[j]*((13.6,24.59,54.42)[j])*EV_TO_ERG+r.heat_erg_s_target[j],rel_tol=1e-12,abs_tol=1e-30))

    def test_superposition_and_volume_heat(self):
        a=self.exposure(phi=(1e9,0,0,0,0,0)); b=self.exposure(phi=(0,2e9,0,0,0,0))
        c=self.exposure(phi=(1e9,2e9,0,0,0,0))
        ra,rb,rc=(moment_operator(v,self.rows) for v in (a,b,c))
        for quantities in ("gamma_s","heat_erg_s_target","absorbed_erg_s_target"):
            for u,v,w in zip(getattr(ra,quantities),getattr(rb,quantities),getattr(rc,quantities)):
                self.assertTrue(math.isclose(u+v,w,rel_tol=1e-12,abs_tol=1e-30))
        self.assertTrue(math.isclose(photo_heating(rc,{"HI":1.2,"HeI":.1,"HeII":.03}),sum(n*h for n,h in zip((1.2,.1,.03),rc.heat_erg_s_target)),rel_tol=1e-12,abs_tol=1e-30))

    def test_transition_and_inactive_routes(self):
        late=self.exposure("late",(1e9,),4.75)
        r=moment_operator(late,self.rows)
        self.assertEqual(r.active_species,("HeII",))
        self.assertIsNone(r.gamma_s[0]); self.assertIsNone(r.heat_erg_s_target[1]); self.assertIsNone(r.absorbed_erg_s_target[0])
        self.assertEqual(r.gamma_s[2],1e9*self.rows[-1].sigma[2])
        with self.assertRaises(DomainError): moment_operator(replace(late,regime="early"),self.rows)
        with self.assertRaises(DomainError): photo_heating(r,{"HI":1.,"HeII":1.})

    def test_exposure_validation(self):
        base=self.exposure()
        variants=(replace(base,phi=(-1,0,0,0,0,0)), replace(base,phi=(float("nan"),0,0,0,0,0)),
                  replace(base,units="photon m^-2 s^-1"), replace(base,frame="comoving"),
                  replace(base,spectral_template_identity=("arbitrary",)*6),replace(base,speed_convention=""),
                  replace(base,source_identity=""),replace(base,temporal_trace_identity=""),
                  replace(base,validity_domain=(0,4.9)),replace(base,z=-1))
        for x in variants:
            with self.assertRaises(DomainError): moment_operator(x,self.rows)

    def test_explicit_energy_density_conversion(self):
        e=self.exposure("late",(1e9,))
        u=(1e9*self.rows[-1].mean*EV_TO_ERG/TRUE_C_CM_S,)
        metadata=dict(energy_density_units="erg cm^-3",energy_density_frame="proper",
            regime="late",z=e.z,spectral_template_identity=e.spectral_template_identity,
            speed_convention="true_c",validity_domain=e.validity_domain,
            source_identity="fixture:u",temporal_trace_identity="fixture:t")
        derived=exposure_from_proper_energy_density(u,TRUE_C_CM_S,metadata=metadata,rows=self.rows)
        self.assertTrue(math.isclose(derived.phi[0],1e9,rel_tol=1e-12))
        expected_energy_sink=TRUE_C_CM_S*u[0]*energy_opacity_cm2(self.rows[-1],"HeII")
        self.assertTrue(math.isclose(expected_energy_sink,moment_operator(derived,self.rows).absorbed_erg_s_target[2],rel_tol=1e-12,abs_tol=1e-30))
        self.assertIsNone(energy_opacity_cm2(self.rows[-1],"HI"))
        with self.assertRaises(DomainError):
            exposure_from_proper_energy_density(u,TRUE_C_CM_S,metadata=dict(metadata,energy_density_frame="comoving"),rows=self.rows)
        with self.assertRaises(DomainError):
            exposure_from_proper_energy_density(u,3e10,metadata=metadata,rows=self.rows)

    def test_support_edges(self):
        early=self.exposure(phi=(0,0,0,1e9,0,0))
        for species in ("HI","HeI"):
            with self.assertRaisesRegex(DomainError,"row 3 "+species+" upper support"):
                kinetic_support(early,self.rows,species)
        self.assertTrue(math.isclose(kinetic_support(early,self.rows,"HeII")[0][1],145.58,abs_tol=1e-12))
        with self.assertRaisesRegex(DomainError,"1945.58"):
            kinetic_support(self.exposure("late",(1e9,)),self.rows,"HeII")
        with self.assertRaises(DomainError): kinetic_support(self.exposure("late",(1e9,)),self.rows,"HI")


if __name__ == "__main__":
    result = unittest.main(exit=False).result
    output = os.environ.get("LUMINA_OUTPUT_DIR")
    if output:
        dest = Path(output)
        (dest/"TEST_RESULTS.json").write_text(json.dumps({
            "run": result.testsRun, "failures": len(result.failures),
            "errors": len(result.errors), "successful": result.wasSuccessful(),
            "kind": "bounded deterministic contract tests; no IVP or quadrature"
        },indent=2)+"\n")
        if result.wasSuccessful():
            (dest/"BENCHMARK_PANELS.json").write_text(json.dumps(benchmark_panels(AdapterTests.series),
                                                              separators=(",",":"),allow_nan=False)+"\n")
    if not result.wasSuccessful():
        raise SystemExit(1)
