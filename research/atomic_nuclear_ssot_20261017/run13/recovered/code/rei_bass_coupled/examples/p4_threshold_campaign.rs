//! Actual original Verner HI and H-equality DI provider matched at a moving
//! FLRW threshold. Manufactured gas density/geometry, single initial photon
//! cohort: a microphysical/geometry oracle, NOT source-on cosmic EoR.
use rei_iso_couple_reference::bianchi_i::{ConstantHubbleBackground, GeometryBackground};
use rei_iso_couple_reference::source_age::Cohort;
use rei_iso_couple_reference::threshold_events::partition_at_photo_events;
use rei_iso_couple_reference::{Absorber, AtomicProvider};

const C: f64 = 299_792_458.;
const H: f64 = 1e-12; // s^-1 manufactured
const E0: f64 = 13.604; // eV, crosses D and HI edges
const D_EDGE: f64 = 13.602134599702; // eV, inherited manufactured D binding
const H_BIND: f64 = 13.598434599702; // eV original HHeModel fixture
const NHI0: f64 = 8.0e3; // m^-3, manufactured
const NDI0: f64 = 1.6e3; // m^-3, artificially large D stress test
const DT: f64 = 5.0e8; // seconds

fn run(m: usize, split: bool) -> (f64, f64, f64, usize, f64) {
    let bg = ConstantHubbleBackground::new([1., 1., 1.], [H, H, H]).unwrap();
    let co = Cohort {
        birth_time_s: 0.,
        birth_geometry: bg.snapshot(0.).unwrap(),
        energy_at_birth_ev: E0,
        direction_at_birth: [0., 0., 1.],
        n_comoving_m3: 1.,
        spectral_index: 0,
        angular_index: 0,
    };
    let p = AtomicProvider::reference();
    let mut n = 1.;
    let mut hi = 0.;
    let mut di = 0.;
    let mut count = 0;
    let mut absorbed_energy_ev = 0.;
    for k in 0..m {
        let a = DT * k as f64 / m as f64;
        let b = DT * (k + 1) as f64 / m as f64;
        let segs = if split {
            partition_at_photo_events(&co, &bg, a, b, D_EDGE).unwrap()
        } else {
            vec![(a, b)]
        };
        count += segs.len() - 1;
        for (sa, sb) in segs {
            let t = 0.5 * (sa + sb);
            let e = co.ray_at(&bg.snapshot(t).unwrap()).unwrap().energy_ev;
            let sigma = p.cross_section(Absorber::HI, e).unwrap() * 1e-4;
            let nscale = (-3.0 * H * t).exp();
            let k_hi = C * NHI0 * nscale * sigma;
            let k_di = if e >= D_EDGE {
                C * NDI0 * nscale * sigma
            } else {
                0.
            };
            let kappa = k_hi + k_di;
            let absorbed = n * -(-kappa * (sb - sa)).exp_m1();
            if kappa > 0. {
                hi += absorbed * k_hi / kappa;
                di += absorbed * k_di / kappa;
            }
            absorbed_energy_ev += absorbed * e;
            n -= absorbed;
        }
    }
    assert!((1. - n - hi - di).abs() < 4e-15);
    assert!(absorbed_energy_ev >= hi * H_BIND + di * D_EDGE - 2e-14);
    (n, hi, di, count, absorbed_energy_ev)
}
fn main() {
    println!("m,event_split,photon_surv,HI_abs,DI_abs,event_cuts,absorbed_energy_ev");
    for m in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512] {
        for mode in [false, true] {
            let (n, a, b, c, e) = run(m, mode);
            println!("{m},{mode},{n:.16e},{a:.16e},{b:.16e},{c},{e:.16e}");
        }
    }
}
