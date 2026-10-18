//! Three read-only full/two-half comparisons of one frozen checkpoint.
use rei_microphysics::axbi_covariant_transport::PhotonState;
use rei_microphysics::axbi_driver::{compiled_identity, Driver, DriverConfig, DriverState};
use rei_microphysics::igm_state::w_erg_per_h_to_ev;
use rei_microphysics::ForwardError;
use std::{error::Error, fs, path::Path, time::Instant};

fn photons(s: &DriverState) -> PhotonState {
    PhotonState {
        number: s.photons.clone(),
        energy_ref: s.photon_energy_ref.clone(),
        support_lo: s.photon_support_lo.clone(),
        support_hi: s.photon_support_hi.clone(),
    }
}
fn tentative(
    d: &Driver,
    old: &DriverState,
    to: f64,
    counter: &mut usize,
    started: Instant,
) -> Result<DriverState, ForwardError> {
    if started.elapsed().as_secs_f64() > 55.0 {
        return Err(ForwardError::InvalidInput("DIAGNOSTIC_WALL_CAP"));
    }
    let mut s = old.clone();
    let mid = (old.a * to).sqrt();
    let dt = d.background.interval_increment(old.a, to)?.proper_time_s;
    d.geometry_map(&mut s, mid)?;
    let geometry = d.background.point_at_scale(mid)?.geometry()?;
    let mut p = photons(&s);
    let added = d.transport.inject(&mut p, &geometry, 1.0 / mid - 1.0, dt)?;
    s.photons = p.number;
    s.photon_energy_ref = p.energy_ref;
    s.photon_support_lo = p.support_lo;
    s.photon_support_hi = p.support_hi;
    s.ledgers.source_n += added.added_photons_per_h;
    s.ledgers.source_u += added.added_energy_ev_per_h;
    d.chemical_stage(&mut s, dt, counter)?;
    d.geometry_map(&mut s, to)?;
    d.validate(&s, 1e-8)?;
    let (n0, u0) = d.residuals(old)?;
    let (n1, u1) = d.residuals(&s)?;
    if (n1 - n0).abs() > 1e-10 * s.ledgers.source_n.max(1.0)
        || (u1 - u0).abs() > 1e-10 * s.ledgers.source_u.max(1.0)
    {
        return Err(ForwardError::InvalidInput("DIAGNOSTIC_STEP_LEDGER"));
    }
    Ok(s)
}
fn cell_json(s: &DriverState, k: usize) -> String {
    format!(
        "{{\"N\":{},\"Uref\":{},\"support_lo\":{},\"support_hi\":{}}}",
        s.photons[k], s.photon_energy_ref[k], s.photon_support_lo[k], s.photon_support_hi[k]
    )
}
fn cut_json(s: &DriverState, k: usize, cuts: [f64; 3]) -> String {
    let flags = cuts.map(|q| s.photon_support_lo[k] < q && q < s.photon_support_hi[k]);
    format!("{flags:?}")
}
fn hi_straddle(d: &Driver, s: &DriverState) -> Result<String, ForwardError> {
    let geometry = d.background.point_at_scale(s.a)?.geometry()?;
    let rays = d.transport.ray_geometry(&geometry)?;
    let cells = d.transport.n_energy();
    for k in 0..s.photons.len() {
        let cut = 13.6 / rays[k / cells].scale;
        if s.photons[k] > 0.0 && s.photon_support_lo[k] < cut && s.photon_support_hi[k] > cut {
            let mut p = d.transport.empty_state();
            p.number[k] = s.photons[k];
            p.energy_ref[k] = s.photon_energy_ref[k];
            p.support_lo[k] = s.photon_support_lo[k];
            p.support_hi[k] = s.photon_support_hi[k];
            let nh = d.n_h0_cm3 / s.a.powi(3);
            let nhe = d.n_he0_cm3 / s.a.powi(3);
            let [x, y, z] = s.gas.fractions;
            let prepared = d.transport.prepare(&p, &geometry)?;
            let out = prepared.evaluate([nh * (1.0 - x), nhe * (1.0 - y - z), nhe * y], nh, 0.0)?;
            return Ok(format!("{{\"cell\":{k},\"q_cut_HI\":{cut},\"moments\":{},\"gamma_s\":{:?},\"heat_erg_per_absorber_s\":{:?},\"quadrature_nodes\":{}}}",
                cell_json(s,k),out.photo.gamma_s,out.photo.heat_erg_per_absorber_s,prepared.node_count()));
        }
    }
    Ok("null".into())
}
fn run(config: &Path, checkpoint: &Path, output: &Path) -> Result<(), Box<dyn Error>> {
    fs::create_dir(output)?;
    let config_text = fs::read_to_string(config)?;
    fs::write(output.join("input_config.cfg"), &config_text)?;
    fs::copy(checkpoint, output.join("input_checkpoint.txt"))?;
    fs::write(output.join("source_identity.txt"), compiled_identity())?;
    fs::write(
        output.join("diagnostic_source.rs"),
        include_str!("axbi_covariant_step_diagnostic.rs"),
    )?;
    let (mut d, _) = Driver::new(DriverConfig::read(&config_text)?)?;
    let old = d.read_checkpoint(checkpoint)?;
    d.config.max_rhs = 10000;
    let mut counter = 0;
    let started = Instant::now();
    let mut records = Vec::new();
    for divisor in [1.0, 2.0, 4.0] {
        let step = old.next_dln_a / divisor;
        let to = old.a * step.exp();
        let mid = (old.a * to).sqrt();
        let before = counter;
        let full = tentative(&d, &old, to, &mut counter, started)?;
        let first = tentative(&d, &old, mid, &mut counter, started)?;
        let half = tentative(&d, &first, to, &mut counter, started)?;
        let fraction_errors: [f64; 3] = std::array::from_fn(|i| {
            (full.gas.fractions[i] - half.gas.fractions[i]).abs()
                / half.gas.fractions[i].abs().max(1e-5)
        });
        let w = w_erg_per_h_to_ev(half.gas.w_erg_per_h)?;
        let thermal = (w_erg_per_h_to_ev(full.gas.w_erg_per_h)? - w).abs() / w.abs().max(1e-6);
        let (n, u) = d.photon_inventory(&half);
        let geometry = d.background.point_at_scale(to)?.geometry()?;
        let rays = d.transport.ray_geometry(&geometry)?;
        let nc = d.transport.n_energy();
        let dn = full
            .photons
            .iter()
            .zip(&half.photons)
            .map(|(a, b)| (a - b).abs())
            .sum::<f64>();
        let du = full
            .photon_energy_ref
            .iter()
            .zip(&half.photon_energy_ref)
            .enumerate()
            .map(|(k, (a, b))| (a - b).abs() * rays[k / nc].scale)
            .sum::<f64>();
        let n_error = dn / n.max(1e-8);
        let u_error = du / u.max(1e-8);
        let native = d.error_metric(&full, &half)?;
        let component_max = fraction_errors
            .iter()
            .copied()
            .fold(thermal, f64::max)
            .max(n_error)
            .max(u_error);
        if (native - component_max).abs() > 8.0 * f64::EPSILON * native.max(1e-30) {
            return Err("diagnostic component metric mismatch".into());
        }
        let mut order: Vec<_> = (0..full.photons.len()).collect();
        let score = |k: usize| {
            (full.photons[k] - half.photons[k]).abs() / n.max(1e-8)
                + (full.photon_energy_ref[k] - half.photon_energy_ref[k]).abs() * rays[k / nc].scale
                    / u.max(1e-8)
        };
        order.sort_by(|&a, &b| score(b).total_cmp(&score(a)));
        let top:Vec<_> = order.into_iter().take(8).map(|k| {
            let cuts = [13.6,24.59,54.42].map(|e| e/rays[k/nc].scale);
            format!("{{\"ray\":{},\"energy_cell\":{},\"q_edges\":[{},{}],\"full\":{},\"half\":{},\"fit_cuts_over_R\":{:?},\"full_straddles\":{},\"half_straddles\":{},\"delta_N\":{},\"delta_Uactual\":{},\"score\":{}}}",
                k/nc,k%nc,d.transport.edges()[k%nc],d.transport.edges()[k%nc+1],cell_json(&full,k),cell_json(&half,k),cuts,
                cut_json(&full,k,cuts),cut_json(&half,k,cuts),full.photons[k]-half.photons[k],
                (full.photon_energy_ref[k]-half.photon_energy_ref[k])*rays[k/nc].scale,score(k))
        }).collect();
        let source_n = [
            full.ledgers.source_n - old.ledgers.source_n,
            half.ledgers.source_n - old.ledgers.source_n,
        ];
        let source_u = [
            full.ledgers.source_u - old.ledgers.source_u,
            half.ledgers.source_u - old.ledgers.source_u,
        ];
        let event_delta: [f64; 3] =
            std::array::from_fn(|j| full.ledgers.photo_events[j] - half.ledgers.photo_events[j]);
        let dt = d.background.interval_increment(old.a, to)?.proper_time_s;
        let old_diag = hi_straddle(&d, &old)?;
        let full_diag = hi_straddle(&d, &full)?;
        let half_diag = hi_straddle(&d, &half)?;
        records.push(format!("{{\"divisor\":{divisor},\"requested_dln_a\":{step},\"actual_dln_a\":{},\"proper_dt_s\":{dt},\"rhs_evaluations\":{},\"gas_fraction_errors\":{:?},\"thermal_error\":{thermal},\"photon_N_L1_error\":{n_error},\"photon_U_L1_error\":{u_error},\"native_error\":{native},\"component_metric_equal\":true,\"source_N_deltas_full_half\":{:?},\"source_U_deltas_full_half\":{:?},\"photo_event_full_minus_half\":{:?},\"top_cells\":[{}],\"first_HI_straddling_old\":{old_diag},\"first_HI_straddling_full\":{full_diag},\"first_HI_straddling_half\":{half_diag}}}",
            ((to-old.a)/old.a).ln_1p(),counter-before,fraction_errors,source_n,source_u,event_delta,top.join(",")));
    }
    fs::write(output.join("diagnostic.json"),format!("{{\"status\":\"COMPLETED_3_COMPARISONS\",\"checkpoint_a\":{},\"checkpoint_accepted\":{},\"stored_next_dln_a\":{},\"tentative_count\":9,\"rhs_evaluations\":{counter},\"wall_s\":{},\"comparisons\":[{}]}}\n",old.a,old.accepted,old.next_dln_a,started.elapsed().as_secs_f64(),records.join(",")))?;
    println!("three frozen-checkpoint comparisons complete; RHS={counter}");
    Ok(())
}
fn main() -> Result<(), Box<dyn Error>> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len() != 3 {
        return Err("usage: axbi_covariant_step_diagnostic CONFIG CHECKPOINT FRESH_OUTPUT".into());
    }
    run(
        Path::new(&args[0]),
        Path::new(&args[1]),
        Path::new(&args[2]),
    )
}
