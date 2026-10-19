//! Synchronous line protocol for independent SciPy time integration of the
//! source-native instantaneous gas equations. Shared RHS, independent integrator.
#[path = "../tests/common/mod.rs"]
mod common;
use common::fixture;
use rei_iso_couple_reference::{
    deuterium_thermal_coupling::CxOwnership, isotope_state::IsotopeNumberState, midpoint_gas,
    positive_spectral::SpectralMode,
};
use std::io::{self, BufRead, Write};
fn main() {
    let (_, _, mut cfg, initial) = fixture(0., true, 0.2, SpectralMode::OriginalCellMean, 2, 4);
    cfg.use_photo = false;
    cfg.owner = CxOwnership::AtomicRhs;
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut out = stdout.lock();
    for line in stdin.lock().lines() {
        let line = line.unwrap();
        if line == "quit" {
            break;
        }
        let input: Vec<f64> = line
            .split_whitespace()
            .map(|x| x.parse::<f64>().unwrap())
            .collect();
        if input.len() != 16 {
            writeln!(out, "ERROR length").unwrap();
            out.flush().unwrap();
            continue;
        }
        let mut s = initial.clone();
        s.gas.nuclei = IsotopeNumberState::new(std::array::from_fn(|i| input[i])).unwrap();
        s.gas.thermal_j_m3 = input[13];
        s.escaped_j_m3 = input[14];
        s.cmb_reservoir_j_m3 = input[15];
        match midpoint_gas::rhs(&s, &cfg) {
            Ok(k) => {
                for x in k.nuclei_per_s {
                    write!(out, "{x:.17e} ").unwrap();
                }
                writeln!(
                    out,
                    "{:.17e} {:.17e} {:.17e}",
                    k.budget_per_s.thermal_change_j_m3,
                    k.budget_per_s.escape_change_j_m3,
                    k.budget_per_s.cmb_change_j_m3
                )
                .unwrap();
            }
            Err(e) => {
                writeln!(out, "ERROR {e:?}").unwrap();
            }
        }
        out.flush().unwrap();
    }
}
