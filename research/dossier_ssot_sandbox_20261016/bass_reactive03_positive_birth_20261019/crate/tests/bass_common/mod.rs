#![allow(dead_code)]
#[path = "../common/mod.rs"]
pub mod common;
use rei_iso_couple_reference::{
    bass_reactive::{BindingBridge, BoundSourceAgeBridge, GeometryChoice},
    donor::BassSourceIdentity,
    full_network::{FullState, NetworkConfig},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    midpoint_coupled::Centering,
    positive_spectral::SpectralMode,
    qualified_table::QualifiedTable,
    reflection_pool::PoolLimits,
};
use std::path::Path;
pub fn geometry(case: &str, n: usize, capacity: usize) -> GeometryChoice {
    let (rows, cb, mb, cs, ms) = match n {
        121 => (
            968,
            "f9f0bfd3",
            "ccf05824",
            "5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133",
            "98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed",
        ),
        241 => (
            1928,
            "2a9e5a6e",
            "eaa6fd54",
            "30a9abf166005f3c2f4073eb532b0ffd35891827562ed9f0d6816329c625b6c9",
            "9abb74b98a2896a1aee50b373981d2cf3c0c5ba0b65bb7c8437245643c2a90bd",
        ),
        481 => (
            3848,
            "5f26b954",
            "904d399a",
            "1104845a34658b7c99ba4d7731a955c11457cf5c9ab92b1cf49117de462b663f",
            "32b9690e3842c5eeeb64e453fabc1895ab6bf5e27678975521e9f945dc5cc67e",
        ),
        _ => panic!("grid not source locked"),
    };
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../donor_input/donor");
    GeometryChoice::table(
        QualifiedTable::load(
            &root.join(format!("background_{rows}rows_{cb}.csv")),
            &root.join(format!("manifest_{rows}_{mb}.json")),
            BassSourceIdentity {
                producer_commit: "3c39bbbf46b6663e7c40277e194fd0ef48118472".into(),
                source_csv_sha256: cs.into(),
                source_manifest_sha256: ms.into(),
                case: case.into(),
                grid_points: n,
            },
        )
        .unwrap(),
        capacity,
    )
    .unwrap()
}
pub fn fixture(
    case: &str,
    n: usize,
    t0: f64,
    split: bool,
    capacity: usize,
) -> (BindingBridge, NetworkConfig, FullState) {
    let (old, ctr, mut c, mut gas) = common::fixture(
        0.06,
        true,
        0.2,
        if split {
            SpectralMode::SplitPositiveGauss3
        } else {
            SpectralMode::OriginalCellMean
        },
        if split { 4 } else { 2 },
        4,
    );
    c.cx_controls.rtol = 1e-12;
    c.cx_controls.atol_normalized = 1e-14;
    c.cx_controls.max_attempts = 20000;
    c.cx_controls.max_rate_calls = 2500000;
    let g = geometry(case, n, capacity);
    let v0 = g.snapshot(0.).unwrap().volume_factor().unwrap();
    let v = g.snapshot(t0).unwrap().volume_factor().unwrap();
    let mut arr = [0.; 13];
    for sp in S::ALL {
        arr[sp as usize] = gas.gas.nuclei.density_m3(sp) * v0 / v;
    }
    gas.gas.nuclei = IsotopeNumberState::new(arr).unwrap();
    gas.gas.thermal_j_m3 *= v0 / v;
    gas.elapsed_s = t0;
    (
        BindingBridge(
            BoundSourceAgeBridge::new(old.source, g).unwrap(),
            ctr,
            PoolLimits::default(),
            Centering::JointCxSplit,
        ),
        c,
        gas,
    )
}
