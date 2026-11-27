"""HE27 source admission controls; no native chemistry campaign is invoked."""
from pathlib import Path
import sys
import time

import numpy as np
from scipy.integrate import quad

ANALYSIS = Path(__file__).resolve().parents[1] / "analysis"
sys.path.insert(0, str(ANALYSIS))
from source_acceptance import (BIND_EV, FIT_CUTS, X_END, birth_frame_reference,
    check_pinned_sources, donor_moments, he25_raw_moments, he25_panels,
    shell_cut_control, shape, sigma_cm2)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sourcecut import SourceCutModel
from sourcecut import _cut_children
from portable_cut_core import children_of_cell


def test_exact_donor_and_locked_physical_source_bytes():
    identities = check_pinned_sources()
    assert len(set(identities.values())) == 3


def test_immutable_he25_unnormalized_count_exposes_old_bias():
    reference = birth_frame_reference()
    original = he25_raw_moments(4, 4, .005, .37*X_END)
    donor = donor_moments(4, 4, .005, .37*X_END)
    # Model.source's count normalization hides this raw-quadrature bias.
    assert original["photon_modes"] == 256
    assert abs(original["raw_n"]/reference["raw_n"]-1) > 2e-5
    assert abs(donor["raw_n"]/reference["raw_n"]-1) < 1e-13
    assert abs(donor["mean_ev"]-reference["mean_ev"]) < 1e-11


def test_positive_children_partition_moving_thresholds():
    x = .37*X_END
    for q in (-.005, 0., .005):
        for m in (4, 8):
            result = donor_moments(m, 4, q, x)
            assert result["all_positive"] and result["no_cut_straddle"]
            assert result["children"] >= result["parents"]
            assert result["raw_n"] > 0 and result["raw_u_ev"] > 0
            assert min(result["photo_cm2"]) >= 0
            assert min(result["heat_ev_cm2"]) >= 0


def test_species_photo_and_heat_match_scaled_birth_quad():
    reference = birth_frame_reference()
    for q in (-.005, 0., .005):
        got = donor_moments(4, 4, q, .37*X_END)
        np.testing.assert_allclose(got["photo_cm2"], reference["photo_cm2"],
                                   rtol=2e-12, atol=0.)
        np.testing.assert_allclose(got["heat_ev_cm2"], reference["heat_ev_cm2"],
                                   rtol=2e-12, atol=0.)


def test_unscaled_sigma_quad_is_detectable_negative_control():
    reference = birth_frame_reference()
    # The default absolute QUAD tolerance is vastly larger than these cm2
    # integrals.  A strict relative assertion must reject its false reference.
    naive = quad(lambda e: float(shape(e))*float(sigma_cm2(e)[0])
                 * (e-BIND_EV[0]), 13.6, 100.)[0]
    assert abs(naive/reference["heat_ev_cm2"][0]-1) > 1e-11
    donor = donor_moments(4, 4, .005, .37*X_END)
    assert abs(donor["heat_ev_cm2"][0]/reference["heat_ev_cm2"][0]-1) < 2e-12


def test_both_signed_shear_shell_cuts_and_unsplit_negative_control():
    controls = [shell_cut_control(q, float(c)) for q in (-.005, .005)
                for c in FIT_CUTS]
    for control in controls:
        cuts = control["preimages"]
        assert len(cuts) == 4
        assert abs(cuts[1]+cuts[2]) < 1e-14
        assert abs(control["cut_error"]) < 2e-14
    # A global GL32 misses at least one manufactured discontinuity by 0.5%.
    assert max(abs(c["global_error"]) for c in controls) > .005


def test_he25_panel_count_is_stable_transcription():
    panels = list(he25_panels(4, 4, .005))
    assert len(panels) * 4 == he25_raw_moments(4, 4, .005, .37*X_END)["photon_modes"]
    assert all(13.6 <= lo < hi <= 100.01 for _, _, lo, hi in panels)


def test_opt_in_fixed_mode_source_admits_all_physical_moments():
    reference = birth_frame_reference()
    expected = np.array([reference["raw_n"], reference["raw_u_ev"],
                         *reference["photo_cm2"], *reference["heat_ev_cm2"]])
    for q in (-.005, 0., .005):
        model = SourceCutModel(None, m=4, angles=4, q=q)
        t = .37*model.t_end
        raw, report = model.source_moments(t)
        donor = np.array(report["donor_raw"])
        admitted = np.array(report["admitted_raw"])
        assert raw.size == model.K == 256
        assert np.all(np.isfinite(raw)) and np.all(raw >= 0)
        np.testing.assert_allclose(donor, expected, rtol=2e-12, atol=0.)
        np.testing.assert_allclose(admitted, donor, rtol=3e-13, atol=0.)
        assert all(b["min_mode"] >= 0 for b in report["bands"])
        for band in report["bands"]:
            np.testing.assert_allclose(band["admitted"], band["donor"],
                                       rtol=3e-13, atol=3e-27)
        source = model.source(t)
        assert np.all(source >= 0)
        assert abs(float(source.sum())/(model.H(t)*model.source_per_x)-1) < 2e-15
        assert abs(float(np.dot(source, model.geometry(t)[0]))/
                   float(source.sum()) - reference["mean_ev"]) < 2e-11


def test_batched_child_is_he26_exact_gl8_rule():
    for q in (-.005, 0., .005):
        panels = [(lo, hi) for mu, _, lo, hi in he25_panels(4, 4, q)
                  if mu < 0][:16]
        mu = float(np.polynomial.legendre.leggauss(4)[0][0])
        for x in (0., .37*X_END, X_END):
            fast = _cut_children(panels, x, q, mu)
            original = [child for lo, hi in panels for child in
                        children_of_cell(lo, hi, x, q, mu, 1., 13.6, 100.,
                                         FIT_CUTS, BIND_EV, shape, sigma_cm2)]
            assert len(fast) == len(original)
            for new, old in zip(fast, original):
                np.testing.assert_allclose([new['low_ev'], new['high_ev'],
                                            new['n'], new['u_ev']],
                                           [old['low_ev'], old['high_ev'],
                                            old['n'], old['u_ev']],
                                           rtol=2e-14, atol=0.)
                np.testing.assert_allclose(new['photo_cm2'], old['photo_cm2'],
                                           rtol=2e-14, atol=0.)
                np.testing.assert_allclose(new['heat_ev_cm2'], old['heat_ev_cm2'],
                                           rtol=2e-14, atol=0.)


def test_bounded_108_source_admissions_match_birth_frame():
    reference = birth_frame_reference()
    expected = np.array([reference["raw_n"], reference["raw_u_ev"],
                         *reference["photo_cm2"], *reference["heat_ev_cm2"]])
    cases = 0
    started = time.monotonic()
    for q in (-.005, 0., .005):
        for m in (4, 8, 16):
            for angles in (4, 8):
                model = SourceCutModel(None, m=m, angles=angles, q=q)
                for time_fraction in (0., .1, .37, .5, .9, 1.):
                    raw, report = model.source_moments(time_fraction*model.t_end)
                    donor = np.array(report['donor_raw'])
                    admitted = np.array(report['admitted_raw'])
                    assert np.all(np.isfinite(raw)) and np.all(raw >= 0)
                    assert abs(donor[0]/expected[0]-1) < 1e-13
                    assert abs(donor[1]/donor[0]-reference['mean_ev']) < 1e-11
                    np.testing.assert_allclose(donor[2:], expected[2:],
                                               rtol=2e-12, atol=0.)
                    np.testing.assert_allclose(admitted, donor,
                                               rtol=3e-13, atol=0.)
                    cases += 1
    assert cases == 108
    assert time.monotonic()-started < 60., 'SOURCE_ONLY_108_RUNTIME_CAP_60S'
