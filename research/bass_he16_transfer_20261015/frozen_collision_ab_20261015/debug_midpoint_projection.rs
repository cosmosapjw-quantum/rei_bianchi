//! Diagnosis only: observe actual projected spectrum before frozen absorption.
use rei_microphysics::axbi_driver::{Driver, DriverConfig};
use rei_microphysics::{Absorber, AtomicProvider};
fn main() {
    for q in [-0.005_f64, 0., 0.005] {
        let mut cfg = DriverConfig::baseline();
        cfg.q_ref = q;
        cfg.end_zbar = 19.8;
        cfg.background_panels = 4096;
        let (d, mut st) = Driver::new(cfg).unwrap();
        let ai = st.a;
        let ae = 1. / 20.8;
        let am = (ai * ae).sqrt();
        let ray = d.source.angular_cells.len() / 2;
        let ne = d.energies.len();
        st.photons[ray * ne + 32] = 1e-10;
        d.geometry_map(&mut st, am).unwrap();
        println!(
            "q={q} originE={}, grid31={},grid32={},grid33={}, after midpoint total={}",
            d.energies[32],
            d.energies[31],
            d.energies[32],
            d.energies[33],
            st.photons.iter().sum::<f64>()
        );
        for j in 29..=34 {
            let n = st.photons[ray * ne + j];
            let sig = AtomicProvider::reference()
                .cross_section(Absorber::HeII, d.energies[j])
                .unwrap();
            println!(
                " eidx {j}, E={:.17e}, nfrac={:.17e},sigmaHeII={:.17e}",
                d.energies[j],
                n / 1e-10,
                sig
            );
        }
    }
}
