#![allow(dead_code)]
extern crate self as canonical;
#[path = "../numeric/source/rei-next-nodes/canonical/src/primitives.rs"]
mod core;
pub use core::{Tracked, Wide};
#[path = "../numeric/source/rei-next-nodes/short-hhe-midpoint/src/canonical_owner.rs"]
mod owner;
use rei_microphysics::{
    audit_counts,
    igm_background::{FlatFlrwBackground, FlatFlrwConfig},
    igm_photo::packet_opacity,
    igm_state::IgmGasState,
};

fn main() {
    let a = -2.5644410241282034_f64;
    let b = -2.56443269079487_f64;
    let eta = 0.05244705397124411_f64;
    let f = 3.729103312391377e-306_f64;
    let y = [
        0.007119344345087282,
        0.023998668820863836,
        8.263528632703969e-05,
    ];
    let thermal = 2.1907858161386438e-13_f64;
    let background = FlatFlrwBackground::new(FlatFlrwConfig {
        h0_per_s: 2.2e-18,
        omega_r: 9e-5,
        omega_m: 0.3,
        omega_b: 0.048,
        omega_lambda: 0.69991,
        helium_mass_fraction: 0.24,
        tcmb0_k: 2.7255,
        ln_a_min: -13_f64.ln(),
        ln_a_max: -11_f64.ln(),
        parameter_source: "existing igm_manufactured_z12_to10.cfg".to_string(),
    })
    .unwrap();
    let p = background.at_ln_a((a + b) * 0.5).unwrap();
    let gas = IgmGasState::new(y, thermal).unwrap();
    let energy = (eta - (a + b) * 0.5).exp();
    let rates = packet_opacity(&gas, energy, p.n_h_cm3, p.n_he_cm3)
        .unwrap()
        .map(|x| x / p.hubble_per_s);
    let energy_start = (eta - a).exp();
    let o = owner::kernel(f, 0.0, rates, b - a, energy_start).unwrap();
    for i in 0..3 {
        let coefficient = owner::EPS * owner::CHI[i];
        let threshold_energy = coefficient * o.an[i];
        let heat = o.be[i] - threshold_energy;
        println!(
            "species={i} A={:.17e} B={:.17e} threshold={:.17e} heat={:.17e} bits={:016x}",
            o.an[i], o.be[i], threshold_energy, heat, heat.to_bits()
        );
    }
    println!(
        "N={:.17e} U={:.17e} input={:.17e} rates={rates:?} counts={:?}",
        o.n,
        o.u,
        f,
        audit_counts::read()
    );
    assert_eq!(audit_counts::read(), (0, 3));
}
