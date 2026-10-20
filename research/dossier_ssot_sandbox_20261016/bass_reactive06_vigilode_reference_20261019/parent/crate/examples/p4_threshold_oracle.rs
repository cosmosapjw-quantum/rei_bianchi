//! Verner H/D two-threshold crossing, exact native Killing propagation;
//! compare unsplit midpoint vs root-split using the same original provider.
use rei_iso_couple_reference::{
    Absorber, AtomicProvider, HHeModel,
    bianchi_i::{AxisymmetricPoint, ConstantAxisymmetricBackground, GeometryBackground},
    deuterium_atomic::DAtomicProvider,
    source_age::Cohort,
    threshold_roots::split_by_thresholds,
};
fn main() {
    let h = 1.2e-16;
    let dt = 5e12;
    let en0 = 13.605;
    let geom = ConstantAxisymmetricBackground::new(
        0.,
        AxisymmetricPoint::new(1. / 21., 0., h, 0.).unwrap(),
        [0., dt],
    )
    .unwrap();
    let co = Cohort {
        birth_time_s: 0.,
        birth_geometry: geom.snapshot(0.).unwrap(),
        energy_at_birth_ev: en0,
        direction_at_birth: [0.8, 0., 0.6],
        n_comoving_m3: 1.,
        spectral_index: 0,
        angular_index: 0,
    };
    let chi = HHeModel::controlled_fixture().threshold_ev[0];
    let dd = chi + 0.0037;
    let provider = DAtomicProvider::new(chi, dd, "MANUFACTURED_D_H_DELTA_CHI").unwrap();
    let original = AtomicProvider::reference();
    let rate = |t: f64| -> f64 {
        let en = co.ray_at(&geom.snapshot(t).unwrap()).unwrap().energy_ev;
        let hsig = original.cross_section(Absorber::HI, en).unwrap() * 1e-4 * 0.03;
        let dsig = provider.cross_section_m2(en).unwrap() * 0.03;
        (hsig + dsig) * 299_792_458.0
    };
    let integrate = |n: usize, split: bool| -> (f64, usize) {
        let mut tau = 0.;
        let mut crossings = 0;
        for j in 0..n {
            let a = dt * j as f64 / n as f64;
            let b = dt * (j + 1) as f64 / n as f64;
            let points = if split {
                split_by_thresholds(
                    &geom,
                    &co,
                    a,
                    b,
                    &geom.snapshot(a).unwrap(),
                    &geom.snapshot(b).unwrap(),
                    dd,
                )
                .unwrap()
            } else {
                vec![a, b]
            };
            crossings += points.len() - 2;
            for pair in points.windows(2) {
                tau += rate(0.5 * (pair[0] + pair[1])) * (pair[1] - pair[0]);
            }
        }
        (tau, crossings)
    };
    let (tau_ref, _) = integrate(131072, true);
    println!("N,mode,tau,relative_tau_error,survivor,crossings");
    for n in [1, 2, 4, 8, 16, 32, 64, 128] {
        for (name, splitted) in [("unsplit", false), ("edge_root", true)] {
            let (tau, ncross) = integrate(n, splitted);
            println!(
                "{n},{name},{tau:.16e},{:.16e},{:.16e},{ncross}",
                (tau - tau_ref).abs() / tau_ref,
                tau.neg_exp()
            );
        }
    }
}
trait Decay {
    fn neg_exp(self) -> f64;
}
impl Decay for f64 {
    fn neg_exp(self) -> f64 {
        (-self).exp()
    }
}
