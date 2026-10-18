//! Reproducible frozen-gas and free-flight numerical pilot on the REAL
//! conditional AXBI source and prescribed signed backgrounds.
//! It does not evolve a coupled H/He reionization history.
use rei_microphysics::axbi_background::{AxbiBackground, BackgroundFamily, Cosmology};
use rei_microphysics::axbi_q_reference::{absorb_frozen_gas, emit_from_axbi_source};
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::igm_background::{FlatFlrwBackground, FlatFlrwConfig};

fn run() -> Result<(), rei_microphysics::ForwardError> {
    let a_start: f64 = 1.0 / 21.0;
    let a_finish: f64 = 1.0 / 5.0;
    let h0 = 67.4 * 1e5 / 3.085_677_581_491_367e24;
    let params = Cosmology {
        h0_per_s: h0,
        omega_m: 0.315,
        omega_r: 0.000_092,
        omega_lambda: 0.684_908,
    };
    let flat = FlatFlrwBackground::new(FlatFlrwConfig {
        h0_per_s: h0,
        omega_m: 0.315,
        omega_r: 0.000_092,
        omega_lambda: 0.684_908,
        omega_b: 0.0224 / 0.674_f64.powi(2),
        helium_mass_fraction: 0.2454,
        tcmb0_k: 2.7255,
        ln_a_min: a_start.ln(),
        ln_a_max: a_finish.ln(),
        parameter_source: "SCENARIO_LOCK PLANCKLIKE MD14 selected".to_string(),
    })?;
    let source = AxbiSource::new(flat.n_h_comoving_cm3(), 0.2, 16, 8)?;
    let densities = flat.at_ln_a(a_start.ln())?;
    let neutral = [densities.n_h_cm3 * (1.0 - 0.0002), densities.n_he_cm3, 0.0];
    let duration = 1e8_f64;
    println!("q_ref,source_photons_per_H,source_energy_eV_per_H,source_absorbed_per_H,source_photoheat_eV_per_H,source_binding_eV_per_H,photon_number_residual_per_H,photon_energy_residual_eV_per_H,freeflight_mean_E_eV,freeflight_above_HeI_per_H,freeflight_above_HeII_per_H,work_eV_per_H");
    for q in [-0.01_f64, 0.0, 0.01] {
        let bg = AxbiBackground::new(
            params,
            a_start,
            a_finish,
            0.0,
            q,
            BackgroundFamily::PhysicalDensityFixed,
            4096,
        )?;
        let start = bg.point_at_scale(a_start)?.geometry()?;
        let finish = bg.point_at_scale(a_finish)?.geometry()?;
        let packets = emit_from_axbi_source(&source, &start, 20.0, duration)?;
        let mut count = 0.;
        let mut before = 0.;
        let mut after = 0.;
        let mut absorbed = 0.;
        let mut heat = 0.;
        let mut binding = 0.;
        let mut remain = 0.;
        let mut remain_energy = 0.;
        let mut hei = 0.;
        let mut heii = 0.;
        for packet in &packets {
            let ei = packet.energy_at(&start)?;
            let ef = packet.energy_at(&finish)?;
            count += packet.photons_per_h;
            before += packet.photons_per_h * ei;
            after += packet.photons_per_h * ef;
            if ef >= 24.59 {
                hei += packet.photons_per_h;
            }
            if ef >= 54.42 {
                heii += packet.photons_per_h;
            }
            let step = absorb_frozen_gas(packet, &start, neutral, duration)?;
            absorbed += step.absorbed_per_h.iter().sum::<f64>();
            remain += step.final_packet.photons_per_h;
            remain_energy += ei * step.final_packet.photons_per_h;
            heat += step.heat_ev_per_h;
            binding += step.binding_ev_per_h;
        }
        let photon_ledger = count - absorbed - remain;
        let energy_ledger = before - heat - binding - remain_energy;
        let mean_energy = after / count;
        let work = before - after;
        println!("{q},{count:.17e},{before:.17e},{absorbed:.17e},{heat:.17e},{binding:.17e},{photon_ledger:.17e},{energy_ledger:.17e},{mean_energy:.17e},{hei:.17e},{heii:.17e},{work:.17e}");
    }
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("{e}");
        std::process::exit(1);
    }
}
