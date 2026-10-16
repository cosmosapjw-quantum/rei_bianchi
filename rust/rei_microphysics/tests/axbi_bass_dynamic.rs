use rei_microphysics::axbi_bass_background::{sha256_bytes, BassBackground, BassSourceIdentity};
use rei_microphysics::axbi_driver::{Driver, DriverConfig};
use std::{
    fs,
    path::{Path, PathBuf},
};

const CSV: &str = "5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133";
const MANIFEST: &str = "98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed";
fn root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../research/bass_dynamic_20261016/source_grids")
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
    let p = std::env::temp_dir().join(format!(
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
    assert!((state.ledgers.photon_work - (u0 - u1)).abs() < 1e-15,"work={} u0={} u1={} diff={}",state.ledgers.photon_work,u0,u1,state.ledgers.photon_work-(u0-u1));
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
    let grid = &root().join("matched_n121_241_481_retry/n0241");
    let b = BassBackground::from_files(
        &grid.join("PROPOSED_REI_BACKGROUND.csv"),
        &grid.join("PRODUCER_RECEIPT.json"),
        id(
            "COLD_FLRW",
            "30a9abf166005f3c2f4073eb532b0ffd35891827562ed9f0d6816329c625b6c9",
            "9abb74b98a2896a1aee50b373981d2cf3c0c5ba0b65bb7c8437245643c2a90bd",
            241,
        ),
    )
    .unwrap();
    let (different, _) = Driver::new_bass(cfg(), b).unwrap();
    fail(
        different.read_bass_checkpoint(&path, "epoch1", &output),
        "BASS_CHECKPOINT_SOURCE_BINDING",
    );
    let saved = fs::read_to_string(&path).unwrap();
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
