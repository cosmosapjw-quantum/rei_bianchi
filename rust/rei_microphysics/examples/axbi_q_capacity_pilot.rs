//! C4 positive/source-preserving memory-cap feasibility on actual AXBI owner.
use rei_microphysics::axbi_background::{AxbiBackground, BackgroundFamily, Cosmology};
use rei_microphysics::axbi_q_capacity::{cap_packets, CapacityPolicy, TaggedPhoton};
use rei_microphysics::axbi_q_reference::{absorb_frozen_gas, emit_from_axbi_source};
use rei_microphysics::axbi_sources::AxbiSource;
use rei_microphysics::igm_background::{FlatFlrwBackground, FlatFlrwConfig};
use rei_microphysics::GeometrySnapshot;
use std::time::Instant;

fn sum_readouts(
    p: &[TaggedPhoton],
    g: &GeometrySnapshot,
    neutral: [f64; 3],
    dt: f64,
) -> Result<(f64, f64, [f64; 3], f64), rei_microphysics::ForwardError> {
    let mut n = 0.;
    let mut u = 0.;
    let mut event = [0.0; 3];
    let mut heat = 0.;
    for v in p {
        n += v.photon.photons_per_h;
        u += v.photon.photons_per_h * v.photon.energy_at(g)?;
        let r = absorb_frozen_gas(&v.photon, g, neutral, dt)?;
        for k in 0..3 {
            event[k] += r.absorbed_per_h[k];
        }
        heat += r.heat_ev_per_h;
    }
    Ok((n, u, event, heat))
}
fn run() -> Result<(), rei_microphysics::ForwardError> {
    let a_ref: f64 = 1.0 / 21.0;
    let h0 = 67.4e5 / 3.085_677_581_491_367e24;
    let cosmology = Cosmology {
        h0_per_s: h0,
        omega_m: 0.315,
        omega_r: 0.000092,
        omega_lambda: 0.684908,
    };
    let base = FlatFlrwBackground::new(FlatFlrwConfig {
        h0_per_s: h0,
        omega_r: 0.000092,
        omega_m: 0.315,
        omega_b: 0.0224 / 0.674_f64.powi(2),
        omega_lambda: 0.684908,
        helium_mass_fraction: 0.2454,
        tcmb0_k: 2.7255,
        ln_a_min: a_ref.ln(),
        ln_a_max: (1.0 / 5.0_f64).ln(),
        parameter_source: "current selected AXBI conditional source".into(),
    })?;
    let source = AxbiSource::new(base.n_h_comoving_cm3(), 0.2, 16, 8)?;
    let nu = base.at_ln_a(a_ref.ln())?;
    let neutral = [nu.n_h_cm3 * (1. - 0.0002), nu.n_he_cm3, 0.0];
    let dt = 1e8;
    println!("q_ref,n_before,n_after,merges,original_photons_per_H,new_photons_per_H,original_energy_eV_per_H,new_energy_eV_per_H,event_HI_delta,event_HeI_delta,event_HeII_delta,heat_delta_eV_per_H,elapsed_ms,tagged_payload_bytes_before,tagged_payload_bytes_after,baseline_HI_events_per_H,baseline_HeI_events_per_H,baseline_HeII_events_per_H,baseline_heat_eV_per_H");
    for q in [-0.01, 0., 0.01] {
        let bg = AxbiBackground::new(
            cosmology,
            a_ref,
            1.0 / 5.0,
            0.,
            q,
            BackgroundFamily::PhysicalDensityFixed,
            4096,
        )?;
        let now = bg.point_at_scale(a_ref)?.geometry()?;
        let future = bg.point_at_scale(a_ref * 1.00001)?.geometry()?;
        let photons = emit_from_axbi_source(&source, &now, 20.0, dt)?;
        let tagged: Vec<TaggedPhoton> = photons
            .into_iter()
            .enumerate()
            .map(|(i, p)| TaggedPhoton {
                angular_key: i / source.spectral_cells.len(),
                photon: p,
            })
            .collect();
        let before = sum_readouts(&tagged, &now, neutral, dt)?;
        let start = Instant::now();
        let outcome = cap_packets(
            &tagged,
            &now,
            &future,
            CapacityPolicy {
                cap: 256,
                max_events_per_h: [1e-13; 3],
                max_heat_ev_per_h: 1e-11,
                neutral_cm3: neutral,
                duration_s: dt,
            },
        )
        .map_err(|_| rei_microphysics::ForwardError::InvalidInput("C4_CAP_FEASIBILITY_HOLD"))?;
        let elapsed_ms = start.elapsed().as_secs_f64() * 1000.;
        let after = sum_readouts(&outcome.packets, &now, neutral, dt)?;
        let de: [f64; 3] = std::array::from_fn(|k| after.2[k] - before.2[k]);
        println!("{q},{},{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.6},{},{},{:.17e},{:.17e},{:.17e},{:.17e}",
             tagged.len(),outcome.packets.len(),outcome.merges,before.0,after.0,before.1,after.1,
             de[0],de[1],de[2],after.3-before.3,elapsed_ms,
             tagged.len()*std::mem::size_of::<rei_microphysics::axbi_q_capacity::TaggedPhoton>(),
             outcome.packets.len()*std::mem::size_of::<rei_microphysics::axbi_q_capacity::TaggedPhoton>(),before.2[0],before.2[1],before.2[2],before.3);
    }
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("{e}");
        std::process::exit(1);
    }
}
