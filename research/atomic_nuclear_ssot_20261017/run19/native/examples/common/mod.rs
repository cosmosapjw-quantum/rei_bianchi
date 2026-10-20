use rei_iso_couple_reference::{
    HHeModel,
    axbi_sources::{AxbiSource, SOURCE_ID},
    bass_geometry::{BassGeometry, SourceIdentity},
    deuterium_atomic::DAtomicProvider,
    full_network::{FullState, NetworkConfig},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::{KB_J_K, MixtureState},
};
use std::path::PathBuf;
pub fn load(case: &str, grid: usize) -> BassGeometry {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../inputs");
    let (folder, csv_sha, manifest_sha) = match grid {
        121 => (
            "bass164",
            "5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133",
            "98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed",
        ),
        241 => (
            "bass241",
            "30a9abf166005f3c2f4073eb532b0ffd35891827562ed9f0d6816329c625b6c9",
            "9abb74b98a2896a1aee50b373981d2cf3c0c5ba0b65bb7c8437245643c2a90bd",
        ),
        _ => panic!("unsupported retained donor grid"),
    };
    BassGeometry::from_files(
        &root.join(folder).join("PROPOSED_REI_BACKGROUND.csv"),
        &root.join(folder).join("PRODUCER_RECEIPT.json"),
        SourceIdentity {
            csv_sha256: csv_sha.into(),
            manifest_sha256: manifest_sha.into(),
            case: case.into(),
            points: grid,
        },
    )
    .expect("source-locked original BASS donor")
}
/// Explicit test chemistry: baryon count normalized to donor Omega_b rho_crit,
/// A*m_u mass convention, Y_He=.245 and D/H=2.5e-5. Charge/T not REC output.
#[allow(dead_code)] // Shared fixture is used by coupled examples, not geometry-only probes.
pub fn fixture(g: &BassGeometry, x: f64) -> (FullState, NetworkConfig, AxbiSource) {
    let point = g.point_at_x(x).unwrap();
    let h0 = 2.1842852410855026e-18_f64;
    let nb0 = 0.049309230511847414 * 3.0 * h0 * h0
        / (8.0 * std::f64::consts::PI * 6.67430e-11 * 1.66053906892e-27);
    let d_over_h = 2.5e-5;
    let yhe = 0.245;
    let he_over_h = yhe * (1.0 + 2.0 * d_over_h) / (4.0 * (1.0 - yhe));
    let nh0 = nb0 / (1.0 + 2.0 * d_over_h + 4.0 * he_over_h);
    let nh = nh0 / point.a.powi(3);
    let nd = nh * d_over_h;
    let nhe = nh * he_over_h;
    let mut n = [0.0; 13];
    n[S::H1Neutral as usize] = 0.9 * nh;
    n[S::H1Ionized as usize] = 0.1 * nh;
    n[S::DNeutral as usize] = 0.9 * nd;
    n[S::DIonized as usize] = 0.1 * nd;
    n[S::He4Neutral as usize] = 0.8 * nhe;
    n[S::He4SinglyIonized as usize] = 0.15 * nhe;
    n[S::He4DoublyIonized as usize] = 0.05 * nhe;
    let nuclei = IsotopeNumberState::new(n).unwrap();
    let u = 1.5 * KB_J_K * nuclei.thermal_particle_density_all_thermal_m3().unwrap() * 1.0e4;
    let full = FullState {
        gas: MixtureState {
            nuclei,
            thermal_j_m3: u,
        },
        photon_bins: vec![],
        escaped_j_m3: 0.0,
        cmb_reservoir_j_m3: 0.0,
        elapsed_s: point.time_s,
    };
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let conf = NetworkConfig::source_bound(
        DAtomicProvider::new(chi, chi + 0.0037, "MANUFACTURED_D_H_DELTA_CHI").unwrap(),
        SOURCE_ID,
    );
    let source = AxbiSource::new(nh0 / 1.0e6, 0.2, 16, 8).unwrap();
    (full, conf, source)
}
