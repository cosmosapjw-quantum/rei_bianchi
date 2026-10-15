//! C5 runnable source-bound fixed-q grid: injection, frozen gas, short geometry.
use rei_microphysics::axbi_background::{AxbiBackground, BackgroundFamily, Cosmology};
use rei_microphysics::axbi_q_grid::QFixedGrid;
use rei_microphysics::axbi_q_reference::{absorb_frozen_gas, emit_from_axbi_source};
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::igm_background::{FlatFlrwBackground, FlatFlrwConfig};
use rei_microphysics::GeometrySnapshot;
use std::time::Instant;

fn baseline_source(
    c: Cosmology,
) -> Result<(FlatFlrwBackground, AxbiSource), rei_microphysics::ForwardError> {
    let a_ref: f64 = 1. / 21.;
    let base = FlatFlrwBackground::new(FlatFlrwConfig {
        h0_per_s: c.h0_per_s,
        omega_m: c.omega_m,
        omega_r: c.omega_r,
        omega_lambda: c.omega_lambda,
        omega_b: 0.0224 / 0.674_f64.powi(2),
        helium_mass_fraction: 0.2454,
        tcmb0_k: 2.7255,
        ln_a_min: a_ref.ln(),
        ln_a_max: (1.0_f64 / 5.0).ln(),
        parameter_source: "selected AXBI conditional source, unchanged".to_string(),
    })?;
    let source = AxbiSource::new(base.n_h_comoving_cm3(), 0.2, 16, 32)?;
    Ok((base, source))
}
fn neutral_gas(
    base: &FlatFlrwBackground,
    a: f64,
) -> Result<[f64; 3], rei_microphysics::ForwardError> {
    let physical = base.at_ln_a(a.ln())?;
    Ok([physical.n_h_cm3 * (1.0 - 0.0002), physical.n_he_cm3, 0.])
}
fn cohort_reference(
    source: &AxbiSource,
    g: &GeometrySnapshot,
    n: [f64; 3],
    dt: f64,
) -> Result<(f64, f64), rei_microphysics::ForwardError> {
    let packets = emit_from_axbi_source(source, g, 20., dt)?;
    let (mut lost, mut heat) = (0., 0.);
    for p in &packets {
        let e = absorb_frozen_gas(p, g, n, dt)?;
        lost += e.absorbed_per_h.iter().sum::<f64>();
        heat += e.heat_ev_per_h;
    }
    Ok((lost, heat))
}
fn run() -> Result<(), rei_microphysics::ForwardError> {
    let cosmology = Cosmology {
        h0_per_s: 67.4e5 / 3.085_677_581_491_367e24,
        omega_m: 0.315,
        omega_r: 0.000092,
        omega_lambda: 0.684908,
    };
    let (base, source) = baseline_source(cosmology)?;
    let a0: f64 = 1. / 21.;
    let at_z20 = AxbiBackground::new(
        cosmology,
        a0,
        1. / 5.,
        0.,
        0.,
        BackgroundFamily::PhysicalDensityFixed,
        4096,
    )?;
    let g0 = at_z20.point_at_scale(a0)?.geometry()?;
    let g0_neutral = neutral_gas(&base, a0)?;
    let dt = 1e10;
    let ref_cohort = cohort_reference(&source, &g0, g0_neutral, dt)?;
    println!("SHORT_GRID,q_ref,n_energy,n_mu,created_per_H,emit_mean_eV,one_source_abs_per_H,one_source_heat_eV_per_H,HI_abs_per_H,HeI_abs_per_H,HeII_abs_per_H,one_source_binding_eV_per_H,cohort_abs_per_H,cohort_heat_eV_per_H,complete_cells,working_arrays_bytes,source_ms,absorb_ms,two_source_final_photons_per_H,two_source_final_physical_energy_eV_per_H,total_two_source_number_residual_per_H,total_two_source_energy_residual_eV_per_H");
    for q in [-0.01, 0., 0.01] {
        let bg = AxbiBackground::new(
            cosmology,
            a0,
            1. / 5.,
            0.,
            q,
            BackgroundFamily::PhysicalDensityFixed,
            4096,
        )?;
        let g1a = bg.point_at_scale(a0 * 1.000002)?;
        let g2a = bg.point_at_scale(a0 * 1.000004)?;
        let g1 = g1a.geometry()?;
        let g2 = g2a.geometry()?;
        let t1 = g1a.time_s;
        let t2 = g2a.time_s;
        for n_energy in [64, 128, 256, 512] {
            let mut grid = QFixedGrid::new(&source, g0, n_energy, 433.)?;
            let bench = Instant::now();
            let first = grid.inject(&g0, 20., dt, 4)?;
            let source_ms = bench.elapsed().as_secs_f64() * 1000.;
            let work_start = Instant::now();
            let first_gas = grid.absorb_frozen(&g0, g0_neutral, dt, 2)?;
            let absorb_ms = work_start.elapsed().as_secs_f64() * 1000.;
            // The second short pilot starts from a CLEAN source state, so its
            // physical gas/energy ledger doesn't double count the first diagnostic.
            let mut two = QFixedGrid::new(&source, g0, n_energy, 433.)?;
            let d0 = two.inject(&g0, 20., t1, 4)?;
            let p1 = two.advance_frozen(&g0, &g1, g0_neutral, t1, 6, 1)?;
            let z1 = 1. / g1a.a - 1.;
            let d1 = two.inject(&g1, z1, t2 - t1, 4)?;
            let p2 = two.advance_frozen(&g1, &g2, neutral_gas(&base, g1a.a)?, t2 - t1, 6, 1)?;
            let final_mom = two.observe(&g2)?;
            let all_abs =
                p1.absorbed_per_h.iter().sum::<f64>() + p2.absorbed_per_h.iter().sum::<f64>();
            let injected = d0.added_photons_per_h + d1.added_photons_per_h;
            let e_injected = d0.added_energy_ev_per_h + d1.added_energy_ev_per_h;
            let final_energy_plus_losses = final_mom.photon_energy_ev_per_h
                + p1.binding_ev_per_h
                + p2.binding_ev_per_h
                + p1.heat_ev_per_h
                + p2.heat_ev_per_h
                + p1.redshift_work_ev_per_h
                + p2.redshift_work_ev_per_h;
            println!("SHORT_GRID,{q},{n_energy},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{},{},{:.6},{:.6},{:.17e},{:.17e},{:.17e},{:.17e}",
                source.angular_cells.len(),first.added_photons_per_h,
                first.added_energy_ev_per_h/first.added_photons_per_h,
                first_gas.absorbed_per_h.iter().sum::<f64>(),first_gas.heat_ev_per_h,
                first_gas.absorbed_per_h[0],first_gas.absorbed_per_h[1],first_gas.absorbed_per_h[2],
                first_gas.binding_ev_per_h,ref_cohort.0,ref_cohort.1,grid.cell_count(),grid.buffer_capacity_bytes(),
                source_ms,absorb_ms,final_mom.photon_number_per_h,final_mom.photon_energy_ev_per_h,
                injected-final_mom.photon_number_per_h-all_abs,
                e_injected-final_energy_plus_losses);
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
