//! HeII threshold owner audit: original reference atomic provider and exact null ray.
use rei_microphysics::axbi_driver::{Driver, DriverConfig};
use rei_microphysics::axbi_q_reference::CovariantPhoton;
use rei_microphysics::{Absorber, AtomicProvider};
fn main() {
    println!("q_ref,steps,initial_energy_ev,exact_first_mid_energy_ev,sigma_heii_at_node_cm2,sigma_heii_at_exact_mid_cm2");
    let atom = AtomicProvider::reference();
    for q in [-0.005_f64, 0., 0.005] {
        let mut c = DriverConfig::baseline();
        c.q_ref = q;
        c.end_zbar = 19.8;
        c.background_panels = 4096;
        let (d, st) = Driver::new(c).unwrap();
        let ai = st.a;
        let af = 1.0 / 20.8;
        let gi = d.background.point_at_scale(ai).unwrap().geometry().unwrap();
        let k = d.source.angular_cells.len() / 2;
        let mu = d.source.angular_cells[k].mu;
        let direction = [(1. - mu * mu).sqrt(), 0., mu];
        let e0 = d.energies[32];
        let p = CovariantPhoton::from_local(&gi, e0, direction, 1e-10).unwrap();
        for steps in [1_usize, 32, 256] {
            let a_end = ai * ((af / ai).ln() / steps as f64).exp();
            let am = (ai * a_end).sqrt();
            let gm = d.background.point_at_scale(am).unwrap().geometry().unwrap();
            let e = p.energy_at(&gm).unwrap();
            let sig_grid = atom.cross_section(Absorber::HeII, e0).unwrap();
            let sig_exact = atom.cross_section(Absorber::HeII, e).unwrap();
            assert!(e < 54.42 && sig_exact == 0. && sig_grid > 0.);
            println!("{q},{steps},{e0:.17e},{e:.17e},{sig_grid:.17e},{sig_exact:.17e}");
        }
    }
}
