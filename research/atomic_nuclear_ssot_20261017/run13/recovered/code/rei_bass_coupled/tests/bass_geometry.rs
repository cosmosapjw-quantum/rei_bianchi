use rei_iso_couple_reference::bass_geometry::monotone_lrs_bounds;
#[test]
fn accepted_expanding_lrs_interval_has_exact_slope_range() {
    let (lo, hi) = monotone_lrs_bounds(0.0, 0.01, 0.01, 0.01, 1.0)
        .expect("valid expanding Hermite interval must be accepted");
    assert!((lo - 0.01).abs() < 1e-15 && (hi - 0.01).abs() < 1e-15);
}
#[test]
fn endpoint_expansion_does_not_hide_interior_contraction() {
    assert!(monotone_lrs_bounds(0.0, 0.8, 0.0, 0.0, 1.0).is_err());
}

#[path = "../examples/common/mod.rs"]
mod common;
use rei_iso_couple_reference::{
    bass_geometry::{BassGeometry, partition_at_photo_events},
    source_age::Cohort,
};
#[test]
fn original_donor_clock_and_signed_expansion() {
    for case in ["COLD_FLRW", "WARM_ISOTROPIC", "SIGNED_PLUS", "SIGNED_MINUS"] {
        let g = common::load(case, 121);
        assert!(g.slope_min > -0.5 && g.slope_max < 1.0);
        assert!(g.point_at_x(0.).unwrap().h > g.point_at_x(1.4).unwrap().h);
        for x in [0., 1e-8, 0.001, 0.7, 1.4, g.x_max()] {
            let p = g.point_at_x(x).unwrap();
            let back = g.x_at_time(p.time_s).unwrap();
            assert!((x - back).abs() < 4e-15, "{case} {x} {back}");
        }
        if case == "SIGNED_PLUS" {
            assert!(g.point_at_x(0.).unwrap().s > 0.0);
        }
        if case == "SIGNED_MINUS" {
            assert!(g.point_at_x(0.).unwrap().s < 0.0);
        }
    }
}
#[test]
fn exact_flrw_analytic_two_threshold_roots() {
    let g = common::load("COLD_FLRW", 121);
    let p = g.point_at_x(0.7).unwrap();
    let end = g.point_at_x(0.701).unwrap();
    let co = Cohort {
        birth_time_s: p.time_s,
        birth_geometry: p.snapshot().unwrap(),
        energy_at_birth_ev: 13.604,
        direction_at_birth: [0.6, 0., 0.8],
        n_comoving_m3: 1.,
        spectral_index: 0,
        angular_index: 0,
    };
    let segments =
        partition_at_photo_events(&co, &g, p.time_s, end.time_s, 13.602134599702).unwrap();
    assert_eq!(segments.len(), 3);
    for (i, edge) in [13.602134599702, 13.6].into_iter().enumerate() {
        let x = g.x_at_time(segments[i].1).unwrap();
        let exact = 0.7 + (13.604_f64 / edge).ln();
        assert!((x - exact).abs() < 2e-14, "root {x} {exact}");
        let e = co
            .ray_at(&g.point_at_x(x).unwrap().snapshot().unwrap())
            .unwrap()
            .energy_ev;
        assert!((e - edge).abs() < 4e-13);
    }
}
#[test]
fn donor_hash_and_time_domain_fail_closed() {
    let g = common::load("SIGNED_MINUS", 121);
    assert!(g.point_at_time(f64::NAN).is_err());
    assert!(g.point_at_time(-1.).is_err());
    assert!(g.point_at_time(g.time_max() * 1.001).is_err());
    assert!(g.point_at_x(f64::INFINITY).is_err());
    let root = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../inputs/bass164");
    let mut id = g.identity.clone();
    id.csv_sha256 = "0".repeat(64);
    assert!(
        BassGeometry::from_files(
            &root.join("PROPOSED_REI_BACKGROUND.csv"),
            &root.join("PRODUCER_RECEIPT.json"),
            id
        )
        .is_err()
    );
}
#[test]
fn midpoint_clock_is_not_manufactured_affine_h() {
    let g = common::load("MASS3_A_PLUS", 121);
    let t0 = g.point_at_x(0.5).unwrap().time_s;
    let t1 = g.point_at_x(0.9).unwrap().time_s;
    let mid = g.point_at_time((t0 + t1) * 0.5).unwrap();
    let ha = g.point_at_time(t0).unwrap().h;
    let hb = g.point_at_time(t1).unwrap().h;
    assert!((mid.h / ((ha + hb) * 0.5) - 1.).abs() > 1e-3);
}
