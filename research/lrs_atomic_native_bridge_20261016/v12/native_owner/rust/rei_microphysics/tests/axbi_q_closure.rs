//! C6 two-moment positive reconstruction and species threshold regression.
use rei_microphysics::axbi_q_closure::{absorb_positive_bin, positive_reconstruct};
use rei_microphysics::axbi_q_grid::QFixedGrid;
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::igm_background::{FlatFlrwBackground, FlatFlrwConfig};
use rei_microphysics::AxisymmetricPoint;

fn owner_source(nmu: usize) -> AxbiSource {
    let ar: f64 = 1.0 / 21.0;
    let h0 = 67.4e5 / 3.085_677_581_491_367e24;
    let flat = FlatFlrwBackground::new(FlatFlrwConfig {
        h0_per_s: h0,
        omega_m: 0.315,
        omega_r: 0.000092,
        omega_lambda: 0.684908,
        omega_b: 0.0224 / 0.674_f64.powi(2),
        helium_mass_fraction: 0.2454,
        tcmb0_k: 2.7255,
        ln_a_min: ar.ln(),
        ln_a_max: (0.2_f64).ln(),
        parameter_source: "selected actual Planck-like source".to_string(),
    })
    .unwrap();
    AxbiSource::new(flat.n_h_comoving_cm3(), 0.2, 16, nmu).unwrap()
}
fn geom() -> rei_microphysics::GeometrySnapshot {
    AxisymmetricPoint::new(1.0 / 21.0, 0.0, 1e-16, 0.0)
        .unwrap()
        .snapshot()
        .unwrap()
}
fn close(a: f64, b: f64, tol: f64) {
    assert!(
        (a - b).abs() <= tol * a.abs().max(b.abs()).max(1e-30),
        "{a} versus {b}"
    );
}
#[test]
fn max_entropy_positive_bin_matches_number_and_first_energy() {
    for eta in [-0.999, -0.80, -0.30, 0.0, 0.5, 0.95, 0.999] {
        let mean = 25.0 + eta * 2.0;
        let r = positive_reconstruct(23.0, 27.0, mean).unwrap();
        close(r.mean_ev(), mean, 3e-11);
        assert!(r.beta.is_finite());
        assert!(r.normalizer > 0.0);
    }
}
#[test]
fn split_threshold_reaction_preserves_photons_and_energy() {
    let input = 1e-9;
    let u = input * 24.6;
    let densities = [1e-4, 5e-5, 1e-5];
    let r = absorb_positive_bin(23.0, 26.0, input, u, 1.0, densities, 1e9).unwrap();
    assert!(r.absorbed_per_h[0] >= 0.0);
    assert!(r.absorbed_per_h[1] > 0.0);
    assert_eq!(r.absorbed_per_h[2], 0.0);
    close(
        input,
        r.surviving_photons_per_h + r.absorbed_per_h.iter().sum::<f64>(),
        3e-13,
    );
    close(
        u,
        r.surviving_energy_moment_ev_per_h + r.binding_ev_per_h + r.heat_ev_per_h,
        3e-13,
    );
}
#[test]
fn real_md14_source_helium_rate_improves_over_centroid() {
    let g = geom();
    let source = owner_source(32);
    let proper_gas = [0.0017575700008892194, 0.0001429214010766023, 0.0];
    let mut grid = QFixedGrid::new(&source, g, 256, 433.0).unwrap();
    grid.inject(&g, 20.0, 1e10, 1).unwrap();
    let prior = grid.clone().absorb_frozen(&g, proper_gas, 1e10, 1).unwrap();
    let result = grid.absorb_reconstructed(&g, proper_gas, 1e10, 1).unwrap();
    let sci_he1 = 1.4281834584030507e-09;
    let old_err = (prior.absorbed_per_h[1] / sci_he1 - 1.0).abs();
    let new_err = (result.absorbed_per_h[1] / sci_he1 - 1.0).abs();
    assert!(old_err > 0.01);
    assert!(new_err < old_err / 2.0, "old={} new={}", old_err, new_err);
    assert!(new_err < 0.004, "new HeI relative error {}", new_err);
    assert!(result.heat_ev_per_h >= 0.0);
}
#[test]
fn reconstruction_refuses_unphysical_moments_and_reaction_inputs() {
    assert!(positive_reconstruct(23.0, 27.0, 28.0).is_err());
    assert!(positive_reconstruct(23.0, 27.0, 20.0).is_err());
    assert!(absorb_positive_bin(23.0, 27.0, 1e-5, 2e-4, 1.0, [1e-4; 3], 1e8).is_err());
    assert!(absorb_positive_bin(23.0, 27.0, 1e-5, 2.5e-4, 1.0, [-1e-4; 3], 1e8).is_err());
}
#[test]
fn manufactured_heii_channel_matches_independent_continuum_reference() {
    let g = geom();
    let src = owner_source(32);
    let mut x = QFixedGrid::new(&src, g, 256, 433.).unwrap();
    x.inject(&g, 20., 1e10, 1).unwrap();
    let out = x.absorb_reconstructed(&g, [0., 0., 2e-5], 1e10, 4).unwrap();
    let truth = 2.5555213060184666e-13;
    let error = (out.absorbed_per_h[2] / truth - 1.).abs();
    eprintln!(
        "C6_HEII_ACTUAL={:.17e} C6_HEII_REFERENCE={:.17e} REL_ERROR={:.17e}",
        out.absorbed_per_h[2], truth, error
    );
    assert!(error < 2e-4, "HeII relative error {}", error);
    close(out.absorbed_per_h[0], 0., 1e-13);
    close(out.absorbed_per_h[1], 0., 1e-13);
    assert!(out.heat_ev_per_h >= 0.);
}
#[test]
fn parallel_reconstruction_is_cellwise_bitwise_identical() {
    let g = geom();
    let src = owner_source(32);
    let mut a = QFixedGrid::new(&src, g, 256, 433.).unwrap();
    a.inject(&g, 20., 1e10, 1).unwrap();
    let mut b = a.clone();
    let gas = [0.0017575700008892194, 0.0001429214010766023, 2e-5];
    let ra = a.absorb_reconstructed(&g, gas, 1e10, 1).unwrap();
    let rb = b.absorb_reconstructed(&g, gas, 1e10, 4).unwrap();
    for (u, v) in a.number().iter().zip(b.number()) {
        assert_eq!(u.to_bits(), v.to_bits());
    }
    for (u, v) in a.ref_energy_moment().iter().zip(b.ref_energy_moment()) {
        assert_eq!(u.to_bits(), v.to_bits());
    }
    for i in 0..3 {
        close(ra.absorbed_per_h[i], rb.absorbed_per_h[i], 2e-12);
    }
    close(ra.heat_ev_per_h, rb.heat_ev_per_h, 2e-12);
}
#[test]
fn repeated_frozen_absorption_stays_positive_and_ledger_closes() {
    let g = geom();
    let src = AxbiSource::new(1.9e-7, 0.2, 16, 8).unwrap();
    let mut q = QFixedGrid::new(&src, g, 128, 433.).unwrap();
    q.inject(&g, 20., 1e10, 1).unwrap();
    let before = q.observe(&g).unwrap();
    let mut events = 0.0;
    let mut heat = 0.0;
    let mut binding = 0.0;
    for _ in 0..5 {
        let step = q
            .absorb_reconstructed(&g, [1e-4, 1e-5, 1e-6], 1e9, 1)
            .unwrap();
        events += step.absorbed_per_h.iter().sum::<f64>();
        heat += step.heat_ev_per_h;
        binding += step.binding_ev_per_h;
        assert!(q.number().iter().all(|x| x.is_finite() && *x >= 0.));
        assert!(q
            .ref_energy_moment()
            .iter()
            .all(|x| x.is_finite() && *x >= 0.));
    }
    let after = q.observe(&g).unwrap();
    close(
        before.photon_number_per_h,
        after.photon_number_per_h + events,
        4e-12,
    );
    close(
        before.photon_energy_ev_per_h,
        after.photon_energy_ev_per_h + heat + binding,
        4e-12,
    );
}
#[test]
fn two_moments_do_not_uniquely_fix_threshold_side_population() {
    // Two positive spectra in the SAME q-bin have N=1 and U=24.55eV.
    // Single delta at 24.55eV is below HeI threshold (24.59),
    // but 50/50 at 24.0 and 25.1 eV contains HeI-ionizing photons.
    let mean = 24.55;
    let p = positive_reconstruct(23.0, 26.0, mean).unwrap();
    close(p.mean_ev(), mean, 5e-12);
    let actual = absorb_positive_bin(23.0, 26.0, 1.0, mean, 1.0, [0.0, 1e-5, 0.0], 1e10).unwrap();
    assert!(actual.absorbed_per_h[1] > 0.0);
    let no_helium_at_centroid = rei_microphysics::AtomicProvider::reference()
        .cross_section(rei_microphysics::Absorber::HeI, mean)
        .unwrap();
    assert_eq!(no_helium_at_centroid, 0.0);
    // Positive reconstruction is a useful numerical closure, not a
    // certificate of arbitrary within-bin support after spectral hardening.
}
