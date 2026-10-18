//! Actual selected Bianchi-I signed-q, two-epoch MD14 source and frozen-gas test.
//! Source-age support is tracked in q, old centroid-free C6 and C7 compared.
use rei_microphysics::axbi_background::{AxbiBackground, BackgroundFamily, Cosmology};
use rei_microphysics::axbi_q_grid::QFixedGrid;
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::igm_background::{FlatFlrwBackground, FlatFlrwConfig};
use std::time::Instant;
fn run() -> Result<(), rei_microphysics::ForwardError> {
    let ar = 1.0_f64 / 21.0;
    let af = 0.2_f64;
    let h0 = 67.4e5 / 3.085_677_581_491_367e24;
    let cosmology = Cosmology {
        h0_per_s: h0,
        omega_m: 0.315,
        omega_r: 0.000092,
        omega_lambda: 0.684908,
    };
    let flrw = FlatFlrwBackground::new(FlatFlrwConfig {
        h0_per_s: h0,
        omega_m: 0.315,
        omega_r: 0.000092,
        omega_lambda: 0.684908,
        omega_b: 0.0224 / 0.674_f64.powi(2),
        helium_mass_fraction: 0.2454,
        tcmb0_k: 2.7255,
        ln_a_min: ar.ln(),
        ln_a_max: af.ln(),
        parameter_source: "selected MD14 two-age scientific test".into(),
    })?;
    let source = AxbiSource::new(flrw.n_h_comoving_cm3(), 0.2, 16, 32)?;
    let n0 = source.at_redshift(20.)?.per_h_s;
    let n4 = source.at_redshift(4.)?.per_h_s;
    let dt0 = 1e10;
    let dt4 = dt0 * n0 / n4;
    let gas = flrw.at_ln_a(af.ln())?;
    let neutral = [gas.n_h_cm3 * (1.0 - 0.0002), gas.n_he_cm3, 0.0];
    let absorption_dt = 1e10;
    println!("q_ref,nE,nmu,created_old_per_H,created_late_per_H,old_rep_HI,old_rep_HeI,old_rep_heat,support_rep_HI,support_rep_HeI,support_rep_heat,old_rep_ms,support_rep_ms,reference_state_bytes,clipped_populated_cells,count_residual,energy_residual,two_age_HI,two_age_HeI,two_age_heat,two_age_ms,two_age_payload_bytes");
    for q in [-0.01_f64, 0.0, 0.01] {
        let b = AxbiBackground::new(
            cosmology,
            ar,
            af,
            0.,
            q,
            BackgroundFamily::PhysicalDensityFixed,
            4096,
        )?;
        let g0 = b.point_at_scale(ar)?.geometry()?;
        let gf = b.point_at_scale(af)?.geometry()?;
        for nenergy in [64, 128, 256, 512] {
            let mut source_grid = QFixedGrid::new(&source, g0, nenergy, 433.)?;
            let old = source_grid.inject(&g0, 20., dt0, 1)?;
            let late = source_grid.inject(&gf, 4., dt4, 4)?;
            let mut old_age = QFixedGrid::new(&source, g0, nenergy, 433.)?;
            let mut late_age = QFixedGrid::new(&source, g0, nenergy, 433.)?;
            old_age.inject(&g0, 20., dt0, 1)?;
            late_age.inject(&gf, 4., dt4, 1)?;
            let t_age = Instant::now();
            let old_reaction =
                old_age.absorb_reconstructed_support(&gf, neutral, absorption_dt, 4)?;
            let fresh_reaction =
                late_age.absorb_reconstructed_support(&gf, neutral, absorption_dt, 4)?;
            let age_elapsed_ms = t_age.elapsed().as_secs_f64() * 1000.;
            let age_hi = old_reaction.absorbed_per_h[0] + fresh_reaction.absorbed_per_h[0];
            let age_hei = old_reaction.absorbed_per_h[1] + fresh_reaction.absorbed_per_h[1];
            let age_heat = old_reaction.heat_ev_per_h + fresh_reaction.heat_ev_per_h;
            let age_bytes = old_age.buffer_capacity_bytes() + late_age.buffer_capacity_bytes();
            let mut original = source_grid.clone();
            let mut bounded = source_grid.clone();
            let t0 = Instant::now();
            let orig = original.absorb_reconstructed(&gf, neutral, absorption_dt, 4)?;
            let old_ms = t0.elapsed().as_secs_f64() * 1000.;
            let start = Instant::now();
            let closed = bounded.absorb_reconstructed_support(&gf, neutral, absorption_dt, 4)?;
            let new_ms = start.elapsed().as_secs_f64() * 1000.;
            let before = source_grid.observe(&gf)?;
            let after = bounded.observe(&gf)?;
            let count_res = before.photon_number_per_h
                - after.photon_number_per_h
                - closed.absorbed_per_h.iter().sum::<f64>();
            let energy_res = before.photon_energy_ev_per_h
                - after.photon_energy_ev_per_h
                - closed.heat_ev_per_h
                - closed.binding_ev_per_h;
            let edges: Vec<f64> = (0..=nenergy)
                .map(|i| 13.6_f64 * ((433.0_f64 / 13.6_f64).ln() * i as f64 / nenergy as f64).exp())
                .collect();
            let (lo, hi) = source_grid.support_bounds();
            let clipped = (0..source_grid.cell_count())
                .filter(|idx| {
                    if source_grid.number()[*idx] == 0.0 {
                        return false;
                    }
                    let col = idx % nenergy;
                    lo[*idx] > edges[col] * (1.0 + 1e-10)
                        || hi[*idx] < edges[col + 1] * (1.0 - 1e-10)
                })
                .count();
            println!("{q},{nenergy},32,{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.6},{:.6},{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.6},{}",
    old.added_photons_per_h,late.added_photons_per_h,orig.absorbed_per_h[0],orig.absorbed_per_h[1],orig.heat_ev_per_h,
    closed.absorbed_per_h[0],closed.absorbed_per_h[1],closed.heat_ev_per_h,old_ms,new_ms,source_grid.buffer_capacity_bytes(),clipped,count_res,energy_res,age_hi,age_hei,age_heat,age_elapsed_ms,age_bytes);
        }
    }
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("{e}");
        std::process::exit(1);
    }
}
