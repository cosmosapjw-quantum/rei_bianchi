#[path = "../tests/common/mod.rs"]
mod common;
use common::fixture;
use rei_iso_couple_reference::{
    deuterium_thermal_coupling::CxOwnership, full_network, isotope_state::IsotopeSpecies as S,
    midpoint_gas, positive_spectral::SpectralMode,
};
fn main() {
    println!(
        "mode,nsteps,initial_T,span_s,T_K,energy_residual,n0,n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11,n12,thermal_J_m3,escape_J_m3,cmb_J_m3"
    );
    for t in [10000., 40000.] {
        let span = if t == 10000. { 8e10 } else { 1e10 };
        for n in [8, 16, 32, 64, 128, 256, 512] {
            for mode in [
                "legacy",
                "midpoint",
                "strang",
                "strang_tight",
                "legacy_tight",
            ] {
                let (_, _, mut c, mut s) =
                    fixture(0., true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
                s.gas.thermal_j_m3 *= t / 1e4;
                c.use_photo = false;
                if mode == "strang_tight" || mode == "legacy_tight" {
                    c.cx_controls.rtol = 1e-12;
                    c.cx_controls.atol_normalized = 1e-15;
                }
                if mode == "midpoint" {
                    c.owner = CxOwnership::AtomicRhs;
                }
                let e0 = s.energy_j_m3(&c);
                for _ in 0..n {
                    s = if mode.starts_with("legacy") {
                        full_network::step(&s, &c, span / n as f64).unwrap().state
                    } else if mode.starts_with("strang") {
                        midpoint_gas::step_strang(&s, &c, span / n as f64)
                            .unwrap()
                            .state
                    } else {
                        midpoint_gas::step(&s, &c, span / n as f64).unwrap().state
                    };
                }
                print!(
                    "{mode},{n},{t:.17e},{span:.17e},{:.17e},{:.17e}",
                    s.gas.eos().unwrap().temperature_k,
                    (s.energy_j_m3(&c) - e0).abs() / e0
                );
                for sp in S::ALL {
                    print!(",{:.17e}", s.gas.nuclei.density_m3(sp));
                }
                println!(
                    ",{:.17e},{:.17e},{:.17e}",
                    s.gas.thermal_j_m3, s.escaped_j_m3, s.cmb_reservoir_j_m3
                );
            }
        }
    }
}
