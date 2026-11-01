//! C5 real source-bound fixed-q number/energy-moment Eulerian grid.
use rei_microphysics::axbi_background::{AxbiBackground, BackgroundFamily, Cosmology};
use rei_microphysics::axbi_q_grid::QFixedGrid;
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::AxisymmetricPoint;

fn g(a: f64, b: f64) -> rei_microphysics::GeometrySnapshot {
    AxisymmetricPoint::new(a, b, 1e-16, 0.)
        .unwrap()
        .snapshot()
        .unwrap()
}
fn source(nmu: usize) -> AxbiSource {
    AxbiSource::new(1.9e-7, 0.2, 16, nmu).unwrap()
}
fn close(x: f64, y: f64, tol: f64) {
    assert!(
        (x - y).abs() <= tol * x.abs().max(y.abs()).max(1e-40),
        "{} vs {}",
        x,
        y
    );
}
#[test]
fn grid_rejects_insufficient_support_and_invalid_layout() {
    let refgeo = g(1. / 21., 0.);
    let src = source(8);
    assert!(QFixedGrid::new(&src, refgeo, 128, 100.).is_err());
    assert!(QFixedGrid::new(&src, refgeo, 0, 433.).is_err());
    assert!(QFixedGrid::new(&src, refgeo, 4096, 433.).is_err());
}
#[test]
fn injection_at_ref_preserves_owner_source_number_and_first_energy() {
    let start = g(1. / 21., 0.);
    let src = source(8);
    let mut grid = QFixedGrid::new(&src, start, 128, 433.).unwrap();
    let dt = 1e10;
    let inj = grid.inject(&start, 20., dt, 1).unwrap();
    let original = src.at_redshift(20.).unwrap().per_h_s * dt;
    let expected_e: f64 = src
        .spectral_cells
        .iter()
        .map(|x| x.photon_fraction * x.energy_ev)
        .sum();
    close(inj.added_photons_per_h, original, 5e-12);
    close(inj.added_energy_ev_per_h / original, expected_e, 5e-8);
    let obs = grid.observe(&start).unwrap();
    close(obs.photon_number_per_h, inj.added_photons_per_h, 5e-13);
    close(obs.photon_energy_ev_per_h, inj.added_energy_ev_per_h, 5e-13);
    assert!(grid.buffer_capacity_bytes() < 8 * 1024 * 1024);
}
#[test]
fn source_shear_family_at_z4_is_count_and_energy_conservative() {
    let gref = g(1. / 21., 0.);
    let h0 = 67.4e5 / 3.085_677_581_491_367e24;
    let c = Cosmology {
        h0_per_s: h0,
        omega_m: 0.315,
        omega_r: 0.000092,
        omega_lambda: 0.684908,
    };
    let src = source(32);
    let dt = 1e10;
    for q in [-0.01, 0., 0.01] {
        let bg = AxbiBackground::new(
            c,
            1. / 21.,
            1. / 5.,
            0.,
            q,
            BackgroundFamily::PhysicalDensityFixed,
            4096,
        )
        .unwrap();
        let geo = bg.point_at_scale(1. / 5.).unwrap().geometry().unwrap();
        let mut grid = QFixedGrid::new(&src, gref, 256, 433.).unwrap();
        let inj = grid.inject(&geo, 4., dt, 4).unwrap();
        close(
            inj.added_photons_per_h,
            src.at_redshift(4.).unwrap().per_h_s * dt,
            5e-11,
        );
        let expect_e: f64 = src
            .spectral_cells
            .iter()
            .map(|x| x.energy_ev * x.photon_fraction)
            .sum();
        close(
            inj.added_energy_ev_per_h / inj.added_photons_per_h,
            expect_e,
            1e-7,
        );
        let before = grid.observe(&geo).unwrap();
        close(before.photon_number_per_h, inj.added_photons_per_h, 2e-12);
        close(
            before.photon_energy_ev_per_h,
            inj.added_energy_ev_per_h,
            2e-12,
        );
    }
}
#[test]
fn source_parallel_is_bit_identical_per_cell() {
    let src = source(32);
    let refg = g(1. / 21., 0.);
    let at = g(1. / 8., 0.004);
    let mut x = QFixedGrid::new(&src, refg, 128, 433.).unwrap();
    let mut y = x.clone();
    let a = x.inject(&at, 8., 1e10, 1).unwrap();
    let b = y.inject(&at, 8., 1e10, 4).unwrap();
    close(a.added_photons_per_h, b.added_photons_per_h, 1e-13);
    for (v, w) in x.number().iter().zip(y.number()) {
        assert_eq!(v.to_bits(), w.to_bits());
    }
    for (v, w) in x.ref_energy_moment().iter().zip(y.ref_energy_moment()) {
        assert_eq!(v.to_bits(), w.to_bits());
    }
}
#[test]
fn frozen_gas_ledger_and_geometry_transport() {
    let refg = g(1. / 21., 0.);
    let src = source(8);
    let mut grid = QFixedGrid::new(&src, refg, 128, 433.).unwrap();
    grid.inject(&refg, 20., 1e10, 1).unwrap();
    let before = grid.observe(&refg).unwrap();
    let frozen = grid
        .absorb_frozen(&refg, [2e-5, 2e-6, 1e-7], 1e9, 1)
        .unwrap();
    let after = grid.observe(&refg).unwrap();
    close(
        before.photon_number_per_h,
        after.photon_number_per_h + frozen.absorbed_per_h.iter().sum::<f64>(),
        2e-12,
    );
    close(
        before.photon_energy_ev_per_h,
        after.photon_energy_ev_per_h + frozen.heat_ev_per_h + frozen.binding_ev_per_h,
        2e-12,
    );
    assert!(frozen.heat_ev_per_h > 0.);
    let future = g((1. / 21.) * 1.00001, 0.000001);
    let n_before = grid.observe(&refg).unwrap();
    let prop = grid
        .advance_frozen(&refg, &future, [0.; 3], 1e10, 4, 2)
        .unwrap();
    let n_after = grid.observe(&future).unwrap();
    close(
        n_before.photon_number_per_h,
        n_after.photon_number_per_h,
        2e-13,
    );
    close(
        n_before.photon_energy_ev_per_h,
        n_after.photon_energy_ev_per_h + prop.redshift_work_ev_per_h,
        1e-11,
    );
}
#[test]
fn repeated_source_injection_has_fixed_allocation_and_no_cohort_growth() {
    let reference = g(1. / 21., 0.);
    let src = source(8);
    let mut grid = QFixedGrid::new(&src, reference, 64, 433.).unwrap();
    let bytes = grid.buffer_capacity_bytes();
    let len = grid.cell_count();
    for i in 0..16 {
        let at = g((1. / 21.) * (1.0 + 1e-7 * i as f64), 0.);
        let z = 1. / at.scale_factors[0] - 1.;
        grid.inject(&at, z, 1e8, 1).unwrap();
        assert_eq!(bytes, grid.buffer_capacity_bytes());
        assert_eq!(len, grid.cell_count());
    }
}

#[test]
fn inject_rejects_changed_background_with_reference_support_outside_grid() {
    let reference = g(1.0 / 21.0, 0.0);
    let source = source(8);
    let mut grid = QFixedGrid::new(&source, reference, 64, 433.0).unwrap();
    let original = grid.number().to_vec();
    // Both samples use the same physical source (z20). The artificially
    // contracted geometry shifts emitted reference E below 13.6 eV.
    let outside = g(1.0 / 42.0, 0.0);
    assert!(grid.inject(&outside, 20.0, 1e9, 1).is_err());
    assert_eq!(grid.number(), original);
}

#[test]
fn frozen_reactions_serial_parallel_are_identical_per_cell() {
    let refg = g(1.0 / 21.0, 0.0);
    let src = source(32);
    let mut slow = QFixedGrid::new(&src, refg, 256, 433.0).unwrap();
    slow.inject(&refg, 20.0, 1e10, 1).unwrap();
    let mut fast = slow.clone();
    let s = slow
        .absorb_frozen(&refg, [2e-5, 2e-6, 1e-7], 1e9, 1)
        .unwrap();
    let p = fast
        .absorb_frozen(&refg, [2e-5, 2e-6, 1e-7], 1e9, 4)
        .unwrap();
    for (a, b) in slow.number().iter().zip(fast.number()) {
        assert_eq!(a.to_bits(), b.to_bits());
    }
    for (a, b) in slow
        .ref_energy_moment()
        .iter()
        .zip(fast.ref_energy_moment())
    {
        assert_eq!(a.to_bits(), b.to_bits());
    }
    for i in 0..3 {
        close(s.absorbed_per_h[i], p.absorbed_per_h[i], 5e-14);
    }
    close(s.heat_ev_per_h, p.heat_ev_per_h, 5e-14);
}

#[test]
fn finite_expanding_step_parallel_is_cellwise_reproducible() {
    let refg = g(1.0 / 21.0, 0.0);
    let src = source(32);
    let mut serial = QFixedGrid::new(&src, refg, 128, 433.0).unwrap();
    serial.inject(&refg, 20.0, 1e10, 1).unwrap();
    let mut parallel = serial.clone();
    let next = g((1.0 / 21.0) * 1.00002, 0.0000003);
    let density = [2e-6, 3e-7, 0.0];
    let a = serial
        .advance_frozen(&refg, &next, density, 3e10, 6, 1)
        .unwrap();
    let b = parallel
        .advance_frozen(&refg, &next, density, 3e10, 6, 4)
        .unwrap();
    for (u, v) in serial.number().iter().zip(parallel.number()) {
        assert_eq!(u.to_bits(), v.to_bits());
    }
    for (u, v) in serial
        .ref_energy_moment()
        .iter()
        .zip(parallel.ref_energy_moment())
    {
        assert_eq!(u.to_bits(), v.to_bits());
    }
    close(a.heat_ev_per_h, b.heat_ev_per_h, 5e-12);
    close(a.redshift_work_ev_per_h, b.redshift_work_ev_per_h, 5e-12);
    assert!(serial
        .advance_frozen(&refg, &next, density, 3e10, 6, 5)
        .is_err());
}
