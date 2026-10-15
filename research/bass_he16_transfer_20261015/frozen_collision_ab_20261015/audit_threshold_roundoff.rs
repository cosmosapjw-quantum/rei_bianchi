//! Diagnose original Native frame energy roundoff at threshold grid nodes.
use rei_microphysics::axbi_driver::{Driver, DriverConfig};
use rei_microphysics::axbi_q_reference::CovariantPhoton;
use rei_microphysics::{Absorber, AtomicProvider, CharacteristicRay};
fn main() {
    println!("q_ref,steps,native_grid_energy,reconstructed_same_frame_energy,reconstructed_minus_native_eV,heii_sigma_from_native_E,heii_sigma_from_packet_E");
    for q in [-0.005_f64, 0., 0.005] {
        let mut c = DriverConfig::baseline();
        c.q_ref = q;
        c.end_zbar = 19.8;
        c.background_panels = 4096;
        let (d, state) = Driver::new(c).unwrap();
        let aref = state.a;
        let af = 1. / 20.8;
        let ri = d.source.angular_cells.len() / 2;
        let mu = d.source.angular_cells[ri].mu;
        let dir = [(1. - mu * mu).sqrt(), 0., mu];
        let gref = d
            .background
            .point_at_scale(aref)
            .unwrap()
            .geometry()
            .unwrap();
        let ray = CharacteristicRay::new(1., dir, 0.).unwrap();
        for steps in [1_usize, 32, 256] {
            let a1 = aref * ((af / aref).ln() / (steps as f64)).exp();
            let am = (aref * a1).sqrt();
            let gm = d.background.point_at_scale(am).unwrap().geometry().unwrap();
            let mdir = ray.pullback(&gref, &gm).unwrap().direction;
            let e = d.energies[32];
            let pk = CovariantPhoton::from_local(&gm, e, mdir, 1e-10).unwrap();
            let reconstructed = pk.energy_at(&gm).unwrap();
            let prov = AtomicProvider::reference();
            let sg = prov.cross_section(Absorber::HeII, e).unwrap();
            let sp = prov.cross_section(Absorber::HeII, reconstructed).unwrap();
            println!(
                "{q},{steps},{e:.17e},{reconstructed:.17e},{:.17e},{sg:.17e},{sp:.17e}",
                reconstructed - e
            );
        }
    }
}
