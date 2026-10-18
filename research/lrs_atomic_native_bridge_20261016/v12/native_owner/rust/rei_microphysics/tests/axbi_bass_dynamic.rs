use rei_microphysics::axbi_bass_background::{sha256_bytes, BassBackground, BassSourceIdentity};
use rei_microphysics::axbi_driver::{Driver, DriverConfig};
use std::{
    fs,
    path::{Path, PathBuf},
};

const CSV: &str = "5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133";
const MANIFEST: &str = "98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed";
fn root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../research/bass_source007_20261016/inputs")
}
fn id(case: &str, csv: &str, manifest: &str, grid: usize) -> BassSourceIdentity {
    BassSourceIdentity {
        producer_commit: "3c39bbbf46b6663e7c40277e194fd0ef48118472".into(),
        source_csv_sha256: csv.into(),
        source_manifest_sha256: manifest.into(),
        case: case.into(),
        grid_points: grid,
    }
}
fn bg(case: &str) -> BassBackground {
    BassBackground::from_files(
        &root().join("pr164_121.csv"),
        &root().join("pr164_121.json"),
        id(case, CSV, MANIFEST, 121),
    )
    .unwrap()
}
fn temp() -> PathBuf {
    let p = root()
        .parent()
        .unwrap()
        .join("raw/test_scratch")
        .join(format!(
            "bass-dynamic-test-{}-{:?}",
            std::process::id(),
            std::thread::current().id()
        ));
    fs::create_dir_all(&p).unwrap();
    p
}
fn fail<T: std::fmt::Debug>(r: Result<T, rei_microphysics::ForwardError>, tag: &str) {
    assert!(
        format!("{:?}", r.unwrap_err()).contains(tag),
        "expected {tag}"
    );
}
fn cfg() -> DriverConfig {
    let mut c = DriverConfig::baseline();
    c.end_zbar = 19.99;
    c.transport_cells = 16;
    c.energy_subdivisions = 2;
    c
}

#[test]
fn original_geometry_and_identity() {
    let b = bg("COLD_FLRW");
    assert!(b.max_hamiltonian_normalized < 3e-12);
    assert!(b.max_raychaudhuri_normalized < 1e-9);
    let p = b.point_at_scale(1.0 / 21.0).unwrap();
    assert_eq!(p.b, 0.0);
    assert_eq!(p.sigma, 0.0);
    let x = b.point_at_scale((1.0 / 21.0) * 0.0001_f64.exp()).unwrap();
    assert!(x.time_s > 0.0);
    assert!((b.point_at_time(x.time_s).unwrap().a - x.a).abs() < 1e-13);
    let signed = bg("SIGNED_MINUS").point_at_scale(1.0 / 21.0).unwrap();
    assert!(signed.sigma < 0.0);
}
#[test]
fn changed_csv_and_manifest_are_rejected() {
    let dir = temp();
    let csv = dir.join("a.csv");
    let manifest = dir.join("a.json");
    let mut data = fs::read(root().join("pr164_121.csv")).unwrap();
    data[100] ^= 1;
    fs::write(&csv, data).unwrap();
    fs::copy(root().join("pr164_121.json"), &manifest).unwrap();
    fail(
        BassBackground::from_files(&csv, &manifest, id("COLD_FLRW", CSV, MANIFEST, 121)),
        "BASS_SOURCE_CSV_SHA256",
    );
    fs::copy(root().join("pr164_121.csv"), &csv).unwrap();
    let mut data = fs::read(&manifest).unwrap();
    data[20] ^= 1;
    fs::write(&manifest, data).unwrap();
    fail(
        BassBackground::from_files(&csv, &manifest, id("COLD_FLRW", CSV, MANIFEST, 121)),
        "BASS_SOURCE_MANIFEST_SHA256",
    );
}
fn altered_source(field: &str, new: &str) -> (PathBuf, PathBuf, String, String) {
    let dir = temp();
    let csv = dir.join(format!("{field}.csv"));
    let manifest = dir.join(format!("{field}.json"));
    let old = fs::read_to_string(root().join("pr164_121.csv")).unwrap();
    let mut lines = old.lines().map(str::to_owned).collect::<Vec<_>>();
    let columns = lines[0].split(',').collect::<Vec<_>>();
    let k = columns.iter().position(|c| *c == field).unwrap();
    let mut row = lines[2].split(',').map(str::to_owned).collect::<Vec<_>>();
    row[k] = new.into();
    lines[2] = row.join(",");
    let bytes = format!("{}\n", lines.join("\n")).into_bytes();
    let hash = sha256_bytes(&bytes).unwrap();
    fs::write(&csv, bytes).unwrap();
    let oldmanifest = fs::read_to_string(root().join("pr164_121.json")).unwrap();
    let text = oldmanifest.replace(CSV, &hash);
    let mh = sha256_bytes(text.as_bytes()).unwrap();
    fs::write(&manifest, text).unwrap();
    (csv, manifest, hash, mh)
}
#[test]
fn signed_shear_and_nonmonotone_clock_are_rejected() {
    let (c, m, ch, mh) = altered_source("signed_s_over_H", "0.2");
    fail(
        BassBackground::from_files(&c, &m, id("COLD_FLRW", &ch, &mh, 121)),
        "BASS_SIGNED_SHEAR",
    );
    let (c, m, ch, mh) = altered_source("proper_elapsed_s", "-1.0");
    fail(
        BassBackground::from_files(&c, &m, id("COLD_FLRW", &ch, &mh, 121)),
        "BASS_PROPER_TIME_MONOTONIC",
    );
}
#[test]
fn hamiltonian_row_is_rejected() {
    let (c, m, ch, mh) = altered_source("H_mean_per_s", "1.0e-16");
    fail(
        BassBackground::from_files(&c, &m, id("COLD_FLRW", &ch, &mh, 121)),
        "BASS_HAMILTONIAN",
    );
}
#[test]
fn signed_geometry_redshift_work_uses_physical_inventory() {
    let (driver, mut state) = Driver::new_bass(cfg(), bg("SIGNED_MINUS")).unwrap();
    driver.seed_delta(&mut state, 0, 30.0, 1e-3).unwrap();
    let (n0, u0) = driver.photon_inventory(&state);
    let b0 = driver.geometry_point(state.a).unwrap().b;
    let to = state.a * 0.0001_f64.exp();
    driver.geometry_map(&mut state, to).unwrap();
    let (n1, u1) = driver.photon_inventory(&state);
    let b1 = driver.geometry_point(state.a).unwrap().b;
    assert!(b1 < b0);
    assert!((n1 - n0).abs() < 1e-15);
    assert!(
        (state.ledgers.photon_work - (u0 - u1)).abs() < 1e-15,
        "work={} u0={} u1={} diff={}",
        state.ledgers.photon_work,
        u0,
        u1,
        state.ledgers.photon_work - (u0 - u1)
    );
    assert!(u1 > 0.0);
}
#[test]
fn checkpoint_binding_and_restart() {
    let dir = temp();
    let (driver, mut state) = Driver::new_bass(cfg(), bg("COLD_FLRW")).unwrap();
    driver.fixed_step(&mut state, 1e-4).unwrap();
    let output = dir.join("output.txt");
    fs::write(&output, "first output epoch\n").unwrap();
    let path = dir.join("checkpoint.bass");
    driver
        .save_bass_checkpoint(&path, &state, "epoch1", &output)
        .unwrap();
    let (reader, _) = Driver::new_bass(cfg(), bg("COLD_FLRW")).unwrap();
    let read = reader
        .read_bass_checkpoint(&path, "epoch1", &output)
        .unwrap();
    assert_eq!(read.a, state.a);
    assert_eq!(read.photons, state.photons);
    fail(
        driver.save_bass_checkpoint(&path, &state, "epoch1", &output),
        "BASS_CHECKPOINT_EXISTS",
    );
    fail(
        reader.read_bass_checkpoint(&path, "epoch2", &output),
        "BASS_CHECKPOINT_EPOCH_OUTPUT",
    );
    let mut wrong = cfg();
    wrong.transport_cells = 32;
    let (different, _) = Driver::new_bass(wrong, bg("COLD_FLRW")).unwrap();
    fail(
        different.read_bass_checkpoint(&path, "epoch1", &output),
        "BASS_CHECKPOINT_PROVIDER_SCHEMA",
    );
    let mut changed_workers = cfg();
    changed_workers.transport_threads = 2;
    let (different, _) = Driver::new_bass(changed_workers, bg("COLD_FLRW")).unwrap();
    fail(
        different.read_bass_checkpoint(&path, "epoch1", &output),
        "BASS_CHECKPOINT_CONFIG",
    );
    let (different, _) = Driver::new_bass(cfg(), bg("SIGNED_MINUS")).unwrap();
    fail(
        different.read_bass_checkpoint(&path, "epoch1", &output),
        "BASS_CHECKPOINT_SOURCE_BINDING",
    );
    let saved = fs::read_to_string(&path).unwrap();
    assert!(saved.contains("DONOR_REI=1f8619c27c1d2b7f13e1c05cf3819c9766cd38f3"));
    assert!(saved.contains("CURRENT_PROVIDER=SOURCE007"));
    assert!(!saved.contains("REI_NATIVE_SOURCE=0e258"));
    let mut source_lines = saved.lines().map(str::to_owned).collect::<Vec<_>>();
    source_lines[4] = "0".repeat(64);
    let wrong_source = dir.join("wrong-current-source.bass");
    fs::write(&wrong_source, format!("{}\n", source_lines.join("\n"))).unwrap();
    fail(
        reader.read_bass_checkpoint(&wrong_source, "epoch1", &output),
        "BASS_CHECKPOINT_NATIVE_SOURCE",
    );
    let mut lines = saved.lines().map(str::to_owned).collect::<Vec<_>>();
    lines[8].push_str("|wrong_signed_shear_and_hamiltonian");
    let bad_geometry = dir.join("bad-geometry.bass");
    fs::write(&bad_geometry, format!("{}\n", lines.join("\n"))).unwrap();
    fail(
        reader.read_bass_checkpoint(&bad_geometry, "epoch1", &output),
        "BASS_CHECKPOINT_GEOMETRY_STATE",
    );
    fail(
        reader.save_checkpoint(&dir.join("legacy-write.txt"), &state),
        "BASS_REJECT_LEGACY_CHECKPOINT",
    );
    fs::write(&output, "changed output\n").unwrap();
    fail(
        reader.read_bass_checkpoint(&path, "epoch1", &output),
        "BASS_CHECKPOINT_OUTPUT_SHA256",
    );
    let corrupt = dir.join("truncated.bass");
    fs::write(&corrupt, "BASS_REI_CHECKPOINT_V1\n").unwrap();
    fail(
        reader.read_bass_checkpoint(&corrupt, "epoch1", &output),
        "BASS_CHECKPOINT_TRUNCATED",
    );
    let legacy = dir.join("old-v4.txt");
    fs::write(&legacy, "AXBI_CHECKPOINT_V4\n").unwrap();
    fail(
        reader.read_bass_checkpoint(&legacy, "epoch1", &output),
        "BASS_REJECT_LEGACY_CHECKPOINT",
    );
    fail(
        reader.read_checkpoint(&legacy),
        "BASS_REJECT_LEGACY_CHECKPOINT",
    );
}

#[test]
fn bound_domain_clock_and_config_reject_controls() {
    for case in ["COLD_FLRW", "SIGNED_MINUS"] {
        let b = bg(case);
        assert_eq!(b.grid_points(), 121);
        let start = b.point_at_scale(1.0 / 21.0).unwrap();
        let end = b.point_at_scale(0.2).unwrap();
        assert_eq!(start.time_s, 0.0);
        assert_eq!(b.point_at_time(0.0).unwrap().time_s, 0.0);
        assert_eq!(b.point_at_time(end.time_s).unwrap().a, end.a);
        assert!(end.time_s > 0.0);
        let inc = b.interval_increment(start.a, end.a).unwrap();
        assert_eq!(inc.proper_time_s, end.time_s);
        assert_eq!(inc.delta_b, end.b - start.b);
        assert!(inc.gl4_time_difference_s.is_finite()); // diagnostic, no invented bound
        assert!(inc.gl4_b_difference.is_finite());
        for a in [
            0.0,
            f64::NAN,
            (1.0 / 21.0) * (1.0 - 1e-8),
            0.2 * (1.0 + 1e-8),
        ] {
            fail(b.point_at_scale(a), "BASS_POINT_DOMAIN");
        }
        fail(b.point_at_time(-1.0), "BASS_TIME_DOMAIN");
        fail(
            b.interval_increment(0.1, 1.0 / 21.0),
            "BASS_INTERVAL_DOMAIN",
        );
    }
    let signed = bg("SIGNED_MINUS").point_at_scale(1.0 / 21.0).unwrap();
    assert!((signed.sigma - (-0.009999500037496877)).abs() < 2e-12);
    assert!((3.0_f64.sqrt() * signed.sigma.abs() - 0.017319642115231484).abs() < 2e-12);
    for mode in 0..3 {
        let mut c = cfg();
        match mode {
            0 => c.q_ref = 0.01,
            1 => c.same_h = true,
            _ => c.inactive_hi_split = true,
        }
        fail(
            Driver::new_bass(c, bg("SIGNED_MINUS")),
            "BASS_DRIVER_CONFIG_MODE",
        );
    }
    let (legacy, _) = Driver::new(cfg()).unwrap();
    assert!(legacy.bass_identity().is_none());
    assert!(!legacy.config.parallel_jacobian_columns);
    assert_eq!(
        legacy.geometry_point(1.0 / 21.0).unwrap(),
        legacy.background.point_at_scale(1.0 / 21.0).unwrap()
    );
}

#[test]
fn source006_parallel_jacobian_compatibility_and_charged_denial() {
    let mut c = cfg();
    c.transport_threads = 2;
    let (serial, mut a) = Driver::new_bass(c, bg("SIGNED_MINUS")).unwrap();
    assert!(!serial.config.parallel_jacobian_columns);
    let mut parallel = serial.clone();
    parallel.config.parallel_jacobian_columns = true;
    let mut b = a.clone();
    serial.fixed_step(&mut a, 1e-4).unwrap();
    parallel.fixed_step(&mut b, 1e-4).unwrap();
    assert_eq!(format!("{a:?}"), format!("{b:?}"));
    assert!(a.rhs_evaluations > 4);
    let before = format!("{b:?}");
    parallel.config.max_rhs = b.rhs_evaluations;
    let mut counter = b.rhs_evaluations;
    assert!(parallel.chemical_stage(&mut b, 1e8, &mut counter).is_err());
    assert_eq!(counter, b.rhs_evaluations);
    assert_eq!(format!("{b:?}"), before);
    // Newly ported fixed_step retains source006 accounting on failed work.
    let mut failure_driver = serial.clone();
    let mut failed = a.clone();
    failure_driver.config.max_rhs = failed.rhs_evaluations + 1;
    let old = failed.clone();
    assert!(failure_driver.fixed_step(&mut failed, 1e-4).is_err());
    assert_eq!(failed.attempts, old.attempts + 1);
    assert_eq!(failed.rhs_evaluations, old.rhs_evaluations + 1);
    assert!(failed.rhs_evaluations <= failure_driver.config.max_rhs);
    let mut expected = old;
    expected.attempts = failed.attempts;
    expected.rhs_evaluations = failed.rhs_evaluations;
    assert_eq!(format!("{failed:?}"), format!("{expected:?}"));
    failure_driver.config.max_attempts = failed.attempts;
    let unchanged = format!("{failed:?}");
    assert!(failure_driver.fixed_step(&mut failed, 1e-4).is_err());
    assert_eq!(format!("{failed:?}"), unchanged);
}

#[test]
fn signed_component_preserves_single_instantaneous_energy_owner() {
    use rei_microphysics::{axbi_covariant_transport::PhotonState, axbi_rates::AxbiProvider};
    let (driver, mut state) = Driver::new_bass(cfg(), bg("SIGNED_MINUS")).unwrap();
    driver.fixed_step(&mut state, 1e-4).unwrap();
    let p = driver.geometry_point(state.a).unwrap();
    let nh = driver.n_h0_cm3 / state.a.powi(3);
    let nhe = driver.n_he0_cm3 / state.a.powi(3);
    let g = p.geometry().unwrap();
    let photons = PhotonState {
        number: state.photons.clone(),
        energy_ref: state.photon_energy_ref.clone(),
        support_lo: state.photon_support_lo.clone(),
        support_hi: state.photon_support_hi.clone(),
    };
    let prepared = driver.transport.prepare(&photons, &g).unwrap();
    let [x, y, z] = state.gas.fractions;
    let absorption = driver
        .transport
        .evaluate(
            &prepared,
            [nh * (1.0 - x), nhe * (1.0 - y - z), nhe * y],
            nh,
            0.0,
        )
        .unwrap();
    let rhs = AxbiProvider
        .point(&state.gas, nh, nhe, 0.0, 2.7255 / state.a, absorption.photo)
        .unwrap()
        .rhs;
    let balance = rhs.thermal_micro_erg_cm3_s + rhs.binding_micro_erg_cm3_s + rhs.escape_erg_cm3_s
        - rhs.photo_input_erg_cm3_s
        - rhs.cmb_to_gas_erg_cm3_s;
    let denom = rhs
        .photo_input_erg_cm3_s
        .abs()
        .max(rhs.escape_erg_cm3_s.abs())
        .max(rhs.thermal_micro_erg_cm3_s.abs())
        .max(1e-300);
    assert!(balance.abs() / denom <= 1e-12); // inherited donor owner criterion
    driver.validate(&state, 1e-8).unwrap();
}
