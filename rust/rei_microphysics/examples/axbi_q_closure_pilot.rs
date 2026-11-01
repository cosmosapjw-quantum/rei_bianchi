//! C6 fresh-source and reconstructed two-moment closure species comparison.
use rei_microphysics::axbi_q_grid::QFixedGrid;
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::igm_background::{FlatFlrwBackground, FlatFlrwConfig};
use rei_microphysics::AxisymmetricPoint;
use std::time::Instant;
fn run() -> Result<(), rei_microphysics::ForwardError> {
    let a = 1.0_f64 / 21.0;
    let h0 = 67.4e5 / 3.085_677_581_491_367e24;
    let background = FlatFlrwBackground::new(FlatFlrwConfig {
        h0_per_s: h0,
        omega_m: 0.315,
        omega_r: 0.000092,
        omega_lambda: 0.684908,
        omega_b: 0.0224 / 0.674_f64.powi(2),
        helium_mass_fraction: 0.2454,
        tcmb0_k: 2.7255,
        ln_a_min: a.ln(),
        ln_a_max: (0.2_f64).ln(),
        parameter_source: "selected Planck-like MD14 source".to_string(),
    })?;
    let source = AxbiSource::new(background.n_h_comoving_cm3(), 0.2, 16, 32)?;
    let gas = background.at_ln_a(a.ln())?;
    let neutral = [gas.n_h_cm3 * (1.0 - 0.0002), gas.n_he_cm3, 0.0];
    let g = AxisymmetricPoint::new(a, 0.0, 1e-16, 0.0)?.snapshot()?;
    let dts = 1e10;
    println!("N_E,n_mu,n_photons_per_H,n_state_bytes,centroid_HI,centroid_HeI,centroid_HeII,centroid_heat,reconstructed_HI,reconstructed_HeI,reconstructed_HeII,reconstructed_heat,number_residual_per_H,energy_residual_eV_per_H,serial_ms,parallel_4_ms");
    for ne in [64, 128, 256, 512] {
        let mut grid = QFixedGrid::new(&source, g, ne, 433.0)?;
        let injected = grid.inject(&g, 20.0, dts, 1)?;
        let mut centroid = grid.clone();
        let c = centroid.absorb_frozen(&g, neutral, dts, 1)?;
        let mut reconstructed = grid.clone();
        let measured = reconstructed.absorb_reconstructed(&g, neutral, dts, 1)?;
        let mut timings = Vec::new();
        for threads in [1, 4] {
            let start = Instant::now();
            let mut observed = 0.0;
            for _ in 0..5 {
                let mut scratch = grid.clone();
                let e = scratch.absorb_reconstructed(&g, neutral, dts, threads)?;
                observed += e.heat_ev_per_h;
            }
            std::hint::black_box(observed);
            timings.push(start.elapsed().as_secs_f64() * 1000.0 / 5.0);
        }
        println!("{ne},32,{:.17e},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.6},{:.6}",
   injected.added_photons_per_h,grid.buffer_capacity_bytes(),
   c.absorbed_per_h[0],c.absorbed_per_h[1],c.absorbed_per_h[2],c.heat_ev_per_h,
   measured.absorbed_per_h[0],measured.absorbed_per_h[1],
   measured.absorbed_per_h[2],measured.heat_ev_per_h,
   measured.photon_number_residual_per_h,measured.photon_energy_residual_ev_per_h,
   timings[0],timings[1]);
    }
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("{e}");
        std::process::exit(1);
    }
}
