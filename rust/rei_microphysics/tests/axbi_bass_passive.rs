use rei_microphysics::axbi_bass_background::{
    enclose_hermite_derivative, BassBackground, BassMonotonicityStatus, BassSourceIdentity,
};
use rei_microphysics::axbi_covariant_transport::PhotonState;
use rei_microphysics::axbi_driver::{Driver, DriverConfig, DriverState};
use std::{
    fs,
    path::{Path, PathBuf},
};
const CSV: &str = "5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133";
const RECEIPT: &str = "98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed";
fn base() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../research/bass_source007_20261016/inputs")
}
fn scratch() -> PathBuf {
    let p = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../research/bass_source008_20261016/raw/test_scratch")
        .join(format!(
            "{}-{:?}",
            std::process::id(),
            std::thread::current().id()
        ));
    fs::create_dir_all(&p).unwrap();
    p
}
fn background(case: &str) -> BassBackground {
    BassBackground::from_files(
        &base().join("pr164_121.csv"),
        &base().join("pr164_121.json"),
        BassSourceIdentity {
            producer_commit: "3c39bbbf46b6663e7c40277e194fd0ef48118472".into(),
            source_csv_sha256: CSV.into(),
            source_manifest_sha256: RECEIPT.into(),
            case: case.into(),
            grid_points: 121,
        },
    )
    .unwrap()
}
fn config(split: bool) -> DriverConfig {
    let mut c = DriverConfig::baseline();
    c.end_zbar = 19.8;
    c.background_panels = 64;
    c.transport_cells = 32;
    c.energy_subdivisions = 2;
    c.inactive_hi_split = split;
    c
}
fn driver(case: &str, split: bool) -> (Driver, DriverState) {
    Driver::new_bass(config(split), background(case)).unwrap()
}
fn seed_all(d: &Driver, s: &mut DriverState, q: f64, n: f64) {
    for (k, cell) in d.source.angular_cells.iter().enumerate() {
        d.seed_delta(s, k, q, n * cell.count_fraction).unwrap();
    }
    s.ledgers.source_n += n;
    s.ledgers.source_u += n * q;
}
fn photon(s: &DriverState) -> PhotonState {
    PhotonState {
        number: s.photons.clone(),
        energy_ref: s.photon_energy_ref.clone(),
        support_lo: s.photon_support_lo.clone(),
        support_hi: s.photon_support_hi.clone(),
    }
}
fn close_n(a: f64, b: f64, scale: f64) {
    assert!(
        (a - b).abs() <= 64.0 * f64::EPSILON * scale,
        "number {a} {b}"
    );
}
fn close_u(a: f64, b: f64, scale: f64) {
    assert!(
        (a - b).abs() <= 128.0 * f64::EPSILON * scale,
        "energy {a} {b}"
    );
}
#[test]
fn all_selected_segments_are_enclosed_and_actual_rays_redshift() {
    for case in ["COLD_FLRW", "SIGNED_MINUS"] {
        let bg = background(case);
        let report = bg.passive_monotonicity();
        assert_eq!(report.status, BassMonotonicityStatus::Established);
        assert_eq!(report.segments.len(), 120);
        for segment in &report.segments {
            for control in segment.controls {
                let v = control.unwrap();
                assert!(v.lo > -0.5 && v.hi < 1.0);
            }
        }
        fs::write(
            scratch().join(format!("{case}_all_segment_enclosures.txt")),
            format!("{report:#?}\n"),
        )
        .unwrap();
        let (d, _) = driver(case, true);
        // Actual knot and midpoint rays are compatibility controls; the
        // all-segment proof above, rather than samples, licenses the mode.
        let rows = fs::read_to_string(base().join("pr164_121.csv")).unwrap();
        let scales: Vec<f64> = rows
            .lines()
            .skip(1)
            .filter_map(|line| {
                let row: Vec<_> = line.split(',').collect();
                (row[0] == case).then(|| row[2].parse().unwrap())
            })
            .collect();
        let mut previous = d
            .transport
            .ray_geometry(&bg.point_at_scale(scales[0]).unwrap().geometry().unwrap())
            .unwrap();
        for pair in scales.windows(2) {
            for a in [(pair[0] * pair[1]).sqrt(), pair[1]] {
                let rays = d
                    .transport
                    .ray_geometry(&bg.point_at_scale(a).unwrap().geometry().unwrap())
                    .unwrap();
                assert!(previous
                    .iter()
                    .zip(&rays)
                    .all(|(old, new)| new.scale <= old.scale));
                previous = rays;
            }
        }
        let meta = d.transport_mode_metadata();
        assert!(meta.contains("background_provider=BASS_SELECTED_SOURCE008"));
        assert!(meta.contains("selected_BASS_certified_forward_ray_monotone_only"));
        assert!(!meta.contains("q0_forward_monotonic_only"));
    }
}
#[test]
fn unsafe_interior_boundary_and_nonfinite_controls_retain_typed_failure() {
    // Endpoint derivatives are zero, but the middle Bernstein control is3,
    // and the actual Hermite derivative at u=1/2 is1.5 (>1).
    let unsafe_segment = enclose_hermite_derivative([0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0]);
    assert_eq!(
        unsafe_segment.status,
        BassMonotonicityStatus::MonotonicityNotEstablished
    );
    assert!(unsafe_segment.controls[0].unwrap().hi < 1.0);
    assert!(unsafe_segment.controls[2].unwrap().hi < 1.0);
    assert!(unsafe_segment.controls[1].unwrap().lo > 1.0);
    for inputs in [
        [0.0, 1.0, 0.0, 0.0, -0.5, 1.0, 0.0, 1.0],
        [0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0],
        [0.0, f64::NAN, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0],
    ] {
        let result = enclose_hermite_derivative(inputs);
        assert_eq!(result.status.code(), "MONOTONICITY_NOT_ESTABLISHED");
        assert_eq!(result.inputs.map(f64::to_bits), inputs.map(f64::to_bits));
    }
    fs::write(
        scratch().join("manufactured_unsafe_enclosure.txt"),
        format!("{unsafe_segment:#?}\n"),
    )
    .unwrap();
}
#[test]
fn nonselected_identity_analytic_knobs_and_reverse_domain_reject_without_mutation() {
    for mut bg in [background("WARM_ISOTROPIC"), background("SIGNED_MINUS")] {
        if bg.identity.case == "SIGNED_MINUS" {
            bg.identity.producer_commit = "0".repeat(40);
        }
        let report = bg.passive_monotonicity();
        assert_eq!(report.status.code(), "MONOTONICITY_NOT_ESTABLISHED");
        assert_eq!(report.reason, "NONSELECTED_SOURCE_IDENTITY");
        assert!(
            format!("{:?}", Driver::new_bass(config(true), bg).unwrap_err())
                .contains("BASS_MONOTONICITY_NOT_ESTABLISHED")
        );
    }
    for q in [-0.01, 0.01] {
        let mut c = config(true);
        c.q_ref = q;
        assert!(Driver::new(c.clone()).is_err());
        assert!(Driver::new_bass(c, background("SIGNED_MINUS")).is_err());
    }
    let mut c = config(true);
    c.same_h = true;
    assert!(Driver::new_bass(c, background("SIGNED_MINUS")).is_err());
    let (d, mut s) = driver("SIGNED_MINUS", true);
    seed_all(&d, &mut s, 13.6, 1e-6);
    let to = s.a * 0.0002_f64.exp();
    d.geometry_map(&mut s, to).unwrap();
    for to in [s.a * 0.9999, 0.0, f64::NAN, 0.2000001] {
        let before = format!("{s:?}");
        assert!(d.geometry_map(&mut s, to).is_err());
        assert_eq!(format!("{s:?}"), before);
    }
}
#[test]
fn actual_ray_hi_equality_active_just_below_passive_and_mu_crossings_differ() {
    let (d, mut s) = driver("SIGNED_MINUS", true);
    d.seed_delta(&mut s, 0, 13.6, 1e-6).unwrap();
    let geometry = d.geometry_point(s.a).unwrap().geometry().unwrap();
    let p = d
        .transport
        .partition_below_hi(&photon(&s), &geometry)
        .unwrap();
    assert_eq!(p.active.number.iter().sum::<f64>(), 1e-6);
    assert_eq!(p.inactive_number.iter().sum::<f64>(), 0.0);
    // At a later actual ray the reference cutoff is inside the source grid.
    let (d, mut below) = driver("SIGNED_MINUS", true);
    let to = below.a * 0.0001_f64.exp();
    d.geometry_map(&mut below, to).unwrap();
    let g = d.geometry_point(below.a).unwrap().geometry().unwrap();
    let ray = d.transport.ray_geometry(&g).unwrap()[0];
    let mut q = 13.6 / ray.scale;
    while q * ray.scale >= 13.6 {
        q = q.next_down();
    }
    d.seed_delta(&mut below, 0, q, 1e-6).unwrap();
    let p = d.transport.partition_below_hi(&photon(&below), &g).unwrap();
    assert_eq!(p.active.number.iter().sum::<f64>(), 0.0);
    assert_eq!(p.inactive_number.iter().sum::<f64>(), 1e-6);
    let (d, mut s) = driver("SIGNED_MINUS", true);
    let to = s.a * 0.0001_f64.exp();
    let g = d.geometry_point(to).unwrap().geometry().unwrap();
    let rays = d.transport.ray_geometry(&g).unwrap();
    let lo = rays.iter().map(|r| r.scale).fold(f64::INFINITY, f64::min);
    let hi = rays.iter().map(|r| r.scale).fold(0.0, f64::max);
    assert!(hi > lo);
    let q = 13.6 / ((lo + hi) / 2.0);
    seed_all(&d, &mut s, q, 1e-6);
    d.geometry_map(&mut s, to).unwrap();
    assert!(
        s.photons.iter().sum::<f64>() > 0.0 && s.photon_inactive_number.iter().sum::<f64>() > 0.0
    );
    for (k, ray) in rays.iter().enumerate() {
        let range = k * d.energies.len()..(k + 1) * d.energies.len();
        let active = s.photons[range.clone()].iter().sum::<f64>();
        let passive = s.photon_inactive_number[range].iter().sum::<f64>();
        if q * ray.scale < 13.6 {
            assert_eq!(active, 0.0);
            assert!(passive > 0.0);
        } else {
            assert!(active > 0.0);
            assert_eq!(passive, 0.0);
        }
    }
}
#[test]
fn repeated_transfer_preserves_moments_work_and_has_no_false_events() {
    for case in ["COLD_FLRW", "SIGNED_MINUS"] {
        let (d, mut s) = driver(case, true);
        seed_all(&d, &mut s, 13.6, 1e-6);
        let (n0, u0) = d.photon_inventory(&s);
        let a0 = s.a;
        for x in [0.0001_f64, 0.0002, 0.0003] {
            d.geometry_map(&mut s, a0 * x.exp()).unwrap();
        }
        assert_eq!(s.photons.iter().sum::<f64>(), 0.0);
        let pn = s.photon_inactive_number.clone();
        let pu = s.photon_inactive_energy_ref.clone();
        d.geometry_map(&mut s, a0 * 0.0004_f64.exp()).unwrap();
        assert_eq!(s.photon_inactive_number, pn);
        assert_eq!(s.photon_inactive_energy_ref, pu);
        let (n, u) = d.photon_inventory(&s);
        close_n(n, n0, n0);
        close_u(u + s.ledgers.photon_work, u0, u0);
        close_u(d.moments(&s).unwrap()[0], u, u0);
        assert_eq!(s.ledgers.photo_events, [0.0; 3]);
        assert_eq!(s.ledgers.absorbed_n, 0.0);
        d.validate(&s, 1e-8).unwrap();
    }
}
#[test]
fn actual_source_and_chemistry_absorb_only_active_while_passive_moments_remain() {
    let (d, mut with) = driver("SIGNED_MINUS", true);
    let (_, mut without) = driver("SIGNED_MINUS", true);
    seed_all(&d, &mut with, 13.6, 1e-6);
    let to = with.a * 0.0002_f64.exp();
    d.geometry_map(&mut with, to).unwrap();
    d.geometry_map(&mut without, to).unwrap();
    let pn = with.photon_inactive_number.clone();
    let pu = with.photon_inactive_energy_ref.clone();
    d.fixed_step(&mut with, 1e-4).unwrap();
    d.fixed_step(&mut without, 1e-4).unwrap();
    assert!(with.ledgers.source_n > 1e-6 && with.ledgers.absorbed_n > 0.0);
    assert_eq!(format!("{:?}", with.gas), format!("{:?}", without.gas));
    assert_eq!(with.photons, without.photons);
    assert_eq!(with.photon_energy_ref, without.photon_energy_ref);
    assert_eq!(with.ledgers.photo_events, without.ledgers.photo_events);
    for i in 0..pn.len() {
        close_n(
            with.photon_inactive_number[i] - without.photon_inactive_number[i],
            pn[i],
            1e-6,
        );
        close_u(
            with.photon_inactive_energy_ref[i] - without.photon_inactive_energy_ref[i],
            pu[i],
            13.6e-6,
        );
    }
    d.validate(&with, 1e-8).unwrap();
    d.validate(&without, 1e-8).unwrap();
}
#[test]
fn nonzero_passive_checkpoint_binds_mode_six_arrays_and_new_compiled_source() {
    let (d, mut s) = driver("SIGNED_MINUS", true);
    seed_all(&d, &mut s, 13.6, 1e-6);
    let to = s.a * 0.0002_f64.exp();
    d.geometry_map(&mut s, to).unwrap();
    assert!(s.photon_inactive_number.iter().sum::<f64>() > 0.0);
    let dir = scratch();
    let output = dir.join("output.txt");
    fs::write(&output, "source008 passive epoch\n").unwrap();
    let path = dir.join("checkpoint.bass-v1");
    d.save_bass_checkpoint(&path, &s, "source008", &output)
        .unwrap();
    let loaded = d.read_bass_checkpoint(&path, "source008", &output).unwrap();
    assert_eq!(format!("{loaded:?}"), format!("{s:?}"));
    let text = fs::read_to_string(&path).unwrap();
    assert!(text.contains("CURRENT_PROVIDER=SOURCE008"));
    assert!(text.contains("inactive_hi_split=true"));
    let (_, body) = text.split_once("\nAXBI_CHECKPOINT_V4\n").unwrap();
    assert_eq!(body.lines().count(), 10);
    let (off, _) = driver("SIGNED_MINUS", false);
    let e = off
        .read_bass_checkpoint(&path, "source008", &output)
        .unwrap_err();
    assert!(format!("{e:?}").contains("BASS_CHECKPOINT_PROVIDER_SCHEMA"));
    let mut lines = text.lines().map(str::to_owned).collect::<Vec<_>>();
    lines[4] = "7a085a77634c39e65cf39150532a43d288233a9349c77803475479866b0e8f3e".into();
    let old = dir.join("old-source007.bass");
    fs::write(&old, format!("{}\n", lines.join("\n"))).unwrap();
    assert!(format!(
        "{:?}",
        d.read_bass_checkpoint(&old, "source008", &output)
            .unwrap_err()
    )
    .contains("BASS_CHECKPOINT_NATIVE_SOURCE"));
}
