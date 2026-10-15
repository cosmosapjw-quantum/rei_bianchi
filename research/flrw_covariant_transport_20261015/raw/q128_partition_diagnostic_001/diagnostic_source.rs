//! Bounded experimental active/passive wrapper; not a production resume.
use rei_microphysics::axbi_covariant_transport::PhotonState;
use rei_microphysics::axbi_driver::{compiled_identity, Driver, DriverConfig, DriverState};
use rei_microphysics::axbi_rates::AxbiProvider;
use rei_microphysics::igm_state::w_erg_per_h_to_ev;
use std::{error::Error, fs, path::Path, time::Instant};
const BENEFIT_BOUND: f64 = 7.926958298838388e-7;
#[derive(Clone)]
struct Wrapped {
    active: DriverState,
    pn: Vec<f64>,
    pu: Vec<f64>,
    passive_work: f64,
    nodes: usize,
}
fn photons(s: &DriverState) -> PhotonState {
    PhotonState {
        number: s.photons.clone(),
        energy_ref: s.photon_energy_ref.clone(),
        support_lo: s.photon_support_lo.clone(),
        support_hi: s.photon_support_hi.clone(),
    }
}
fn set(s: &mut DriverState, p: PhotonState) {
    s.photons = p.number;
    s.photon_energy_ref = p.energy_ref;
    s.photon_support_lo = p.support_lo;
    s.photon_support_hi = p.support_hi;
}
fn restrict(d: &Driver, s: &mut Wrapped) -> Result<(), Box<dyn Error>> {
    let g = d.background.point_at_scale(s.active.a)?.geometry()?;
    let p = d.transport.partition_below_hi(&photons(&s.active), &g)?;
    s.nodes += p.quadrature_nodes;
    for k in 0..s.pn.len() {
        s.pn[k] += p.inactive_number[k];
        s.pu[k] += p.inactive_energy_ref[k];
    }
    set(&mut s.active, p.active);
    Ok(())
}
fn augmented_residual(d: &Driver, s: &Wrapped) -> Result<(f64, f64), Box<dyn Error>> {
    let (n, u) = d.residuals(&s.active)?;
    let g = d.background.point_at_scale(s.active.a)?.geometry()?;
    let rays = d.transport.ray_geometry(&g)?;
    let pu =
        s.pu.iter()
            .enumerate()
            .map(|(k, q)| q * rays[k / d.transport.n_energy()].scale)
            .sum::<f64>();
    Ok((n + s.pn.iter().sum::<f64>(), u + pu))
}
fn validate(d: &Driver, s: &Wrapped) -> Result<(), Box<dyn Error>> {
    d.transport.validate_state(&photons(&s.active))?;
    if !s.pn.iter().chain(&s.pu).all(|v| v.is_finite() && *v >= 0.0) {
        return Err("nonpositive passive domain".into());
    }
    let eos = s.active.gas.eos(
        d.n_h0_cm3 / s.active.a.powi(3),
        d.n_he0_cm3 / s.active.a.powi(3),
    )?;
    AxbiProvider.rates(eos.temperature_k)?;
    let (n, u) = augmented_residual(d, s)?;
    if n.abs() > 1e-8 * s.active.ledgers.source_n.max(1.0)
        || u.abs() > 1e-8 * s.active.ledgers.source_u.max(1.0)
    {
        return Err("augmented cumulative ledger".into());
    }
    let g = d.background.point_at_scale(s.active.a)?.geometry()?;
    let rays = d.transport.ray_geometry(&g)?;
    let cells = d.transport.n_energy();
    let mut energy = 0.0;
    let mut dipole = 0.0;
    for k in 0..s.pu.len() {
        let u = (s.active.photon_energy_ref[k] + s.pu[k]) * rays[k / cells].scale;
        energy += u;
        dipole += u * rays[k / cells].mu;
    }
    if dipole.abs() > 1e-12 * energy.max(1e-30) {
        return Err("augmented parity".into());
    }
    Ok(())
}
fn geometry(d: &Driver, s: &mut Wrapped, to: f64) -> Result<(), Box<dyn Error>> {
    let g0 = d.background.point_at_scale(s.active.a)?.geometry()?;
    let g1 = d.background.point_at_scale(to)?.geometry()?;
    let r0 = d.transport.ray_geometry(&g0)?;
    let r1 = d.transport.ray_geometry(&g1)?;
    if r0.iter().zip(&r1).any(|(a, b)| b.scale > a.scale) {
        return Err("nonmonotonic ray scale".into());
    }
    let dw =
        s.pu.iter()
            .enumerate()
            .map(|(k, q)| {
                (r0[k / d.transport.n_energy()].scale - r1[k / d.transport.n_energy()].scale) * q
            })
            .sum::<f64>();
    d.geometry_map(&mut s.active, to)?;
    s.active.ledgers.photon_work += dw;
    s.passive_work += dw;
    restrict(d, s)?;
    Ok(())
}
fn tentative(
    d: &Driver,
    old: &Wrapped,
    to: f64,
    counter: &mut usize,
    started: Instant,
) -> Result<Wrapped, Box<dyn Error>> {
    if started.elapsed().as_secs_f64() > 55.0 {
        return Err("diagnostic wall cap".into());
    }
    let mut s = old.clone();
    let mid = (old.active.a * to).sqrt();
    let dt = d
        .background
        .interval_increment(old.active.a, to)?
        .proper_time_s;
    geometry(d, &mut s, mid)?;
    let g = d.background.point_at_scale(mid)?.geometry()?;
    let mut p = photons(&s.active);
    let added = d.transport.inject(&mut p, &g, 1.0 / mid - 1.0, dt)?;
    set(&mut s.active, p);
    s.active.ledgers.source_n += added.added_photons_per_h;
    s.active.ledgers.source_u += added.added_energy_ev_per_h;
    d.chemical_stage(&mut s.active, dt, counter)?;
    geometry(d, &mut s, to)?;
    validate(d, &s)?;
    let (n0, u0) = augmented_residual(d, old)?;
    let (n1, u1) = augmented_residual(d, &s)?;
    if (n1 - n0).abs() > 1e-10 * s.active.ledgers.source_n.max(1.0)
        || (u1 - u0).abs() > 1e-10 * s.active.ledgers.source_u.max(1.0)
    {
        return Err("augmented step ledger".into());
    }
    Ok(s)
}
fn run(cfg: &Path, checkpoint: &Path, baseline: &Path, out: &Path) -> Result<(), Box<dyn Error>> {
    fs::create_dir(out)?;
    let text = fs::read_to_string(cfg)?;
    fs::write(out.join("input_config.cfg"), &text)?;
    fs::copy(checkpoint, out.join("input_checkpoint.txt"))?;
    fs::copy(baseline, out.join("reused_baseline_diagnostic.json"))?;
    fs::write(out.join("source_identity.txt"), compiled_identity())?;
    fs::write(
        out.join("diagnostic_source.rs"),
        include_str!("axbi_covariant_partition_diagnostic.rs"),
    )?;
    let (mut d, _) = Driver::new(DriverConfig::read(&text)?)?;
    if d.config.q_ref != 0.0 || d.config.same_h {
        return Err("diagnostic is monotonic q0 FLRW only".into());
    }
    let original = d.read_checkpoint(checkpoint)?;
    d.config.max_rhs = 10000;
    let original_res = d.residuals(&original)?;
    let mut old = Wrapped {
        active: original,
        pn: vec![0.0; d.transport.cell_count()],
        pu: vec![0.0; d.transport.cell_count()],
        passive_work: 0.0,
        nodes: 0,
    };
    let started = Instant::now();
    restrict(&d, &mut old)?;
    validate(&d, &old)?;
    let initial_res = augmented_residual(&d, &old)?;
    let initial_nodes = old.nodes;
    let mut counter = 0;
    let mut records = Vec::new();
    let mut passes = false;
    for divisor in [1.0, 2.0, 4.0] {
        let h = old.active.next_dln_a / divisor;
        let to = old.active.a * h.exp();
        let mid = (old.active.a * to).sqrt();
        let before = counter;
        let full = tentative(&d, &old, to, &mut counter, started)?;
        let first = tentative(&d, &old, mid, &mut counter, started)?;
        let half = tentative(&d, &first, to, &mut counter, started)?;
        let g = d.background.point_at_scale(to)?.geometry()?;
        let rays = d.transport.ray_geometry(&g)?;
        let nc = d.transport.n_energy();
        let mut n = 0.0;
        let mut u = 0.0;
        let (mut dn, mut du, mut sn, mut su) = (0.0, 0.0, 0.0, 0.0);
        for k in 0..full.pn.len() {
            let r = rays[k / nc].scale;
            n += half.active.photons[k] + half.pn[k];
            u += (half.active.photon_energy_ref[k] + half.pu[k]) * r;
            dn += ((full.active.photons[k] + full.pn[k]) - (half.active.photons[k] + half.pn[k]))
                .abs();
            du += ((full.active.photon_energy_ref[k] + full.pu[k])
                - (half.active.photon_energy_ref[k] + half.pu[k]))
                .abs()
                * r;
            sn += (full.active.photons[k] - half.active.photons[k]).abs()
                + (full.pn[k] - half.pn[k]).abs();
            su += ((full.active.photon_energy_ref[k] - half.active.photon_energy_ref[k]).abs()
                + (full.pu[k] - half.pu[k]).abs())
                * r;
        }
        let (tn, tu, split_n, split_u) = (
            dn / n.max(1e-8),
            du / u.max(1e-8),
            sn / n.max(1e-8),
            su / u.max(1e-8),
        );
        let fractions: [f64; 3] = std::array::from_fn(|j| {
            (full.active.gas.fractions[j] - half.active.gas.fractions[j]).abs()
                / half.active.gas.fractions[j].abs().max(1e-5)
        });
        let w = w_erg_per_h_to_ev(half.active.gas.w_erg_per_h)?;
        let thermal =
            (w_erg_per_h_to_ev(full.active.gas.w_erg_per_h)? - w).abs() / w.abs().max(1e-6);
        let gasmax = fractions.iter().copied().fold(thermal, f64::max);
        let total = gasmax.max(tn).max(tu);
        let strong = gasmax.max(split_n).max(split_u);
        if divisor == 1.0 {
            passes = total <= BENEFIT_BOUND && strong <= BENEFIT_BOUND;
        }
        let active_only = d.error_metric(&full.active, &half.active)?;
        let eosf = full
            .active
            .gas
            .eos(d.n_h0_cm3 / to.powi(3), d.n_he0_cm3 / to.powi(3))?;
        let eosh = half
            .active
            .gas
            .eos(d.n_h0_cm3 / to.powi(3), d.n_he0_cm3 / to.powi(3))?;
        let event_delta: [f64; 3] = std::array::from_fn(|j| {
            full.active.ledgers.photo_events[j] - half.active.ledgers.photo_events[j]
        });
        let fres = augmented_residual(&d, &full)?;
        let hres = augmented_residual(&d, &half)?;
        let source_n = [
            full.active.ledgers.source_n - old.active.ledgers.source_n,
            half.active.ledgers.source_n - old.active.ledgers.source_n,
        ];
        let source_u = [
            full.active.ledgers.source_u - old.active.ledgers.source_u,
            half.active.ledgers.source_u - old.active.ledgers.source_u,
        ];
        records.push(format!("{{\"divisor\":{divisor},\"requested_dln_a\":{h},\"proper_dt_s\":{},\"rhs_evaluations\":{},\"gas_fraction_errors\":{:?},\"thermal_error\":{thermal},\"temperature_full_half_k\":[{},{}],\"total_N_L1_error\":{tn},\"total_U_L1_error\":{tu},\"strong_split_N_L1_error\":{split_n},\"strong_split_U_L1_error\":{split_u},\"total_error\":{total},\"strong_split_error\":{strong},\"active_only_metric\":{active_only},\"source_N_deltas_full_half\":{:?},\"source_U_deltas_full_half\":{:?},\"photo_event_full_minus_half\":{:?},\"passive_N_full_half\":[{},{}],\"passive_Q_full_half\":[{},{}],\"passive_work_full_half\":[{},{}],\"partition_nodes_full_half\":[{},{}],\"augmented_residual_full\":[{},{}],\"augmented_residual_half\":[{},{}]}}",
            d.background.interval_increment(old.active.a,to)?.proper_time_s,counter-before,fractions,eosf.temperature_k,eosh.temperature_k,source_n,source_u,event_delta,
            full.pn.iter().sum::<f64>(),half.pn.iter().sum::<f64>(),full.pu.iter().sum::<f64>(),half.pu.iter().sum::<f64>(),full.passive_work,half.passive_work,
            full.nodes-initial_nodes,half.nodes-initial_nodes,fres.0,fres.1,hres.0,hres.1));
    }
    fs::write(out.join("diagnostic.json"),format!("{{\"status\":\"COMPLETED_3_COMPARISONS\",\"checkpoint_use\":\"EXPERIMENT_INITIALSTATE_NOT_PRODUCTION_RESUME\",\"candidate\":\"monotonic_FLRW_active_passive_boundary_partition\",\"baseline_h_native_error\":3.963479149419194e-6,\"preselected_benefit_bound\":{BENEFIT_BOUND},\"h_total_and_strong_benefit_pass\":{passes},\"original_checkpoint_residual\":[{},{}],\"initial_partition_augmented_residual\":[{},{}],\"initial_partition_nodes\":{initial_nodes},\"initial_passive_N\":{},\"initial_passive_Q\":{},\"tentative_count\":9,\"rhs_evaluations\":{counter},\"wall_s\":{},\"comparisons\":[{}]}}\n",original_res.0,original_res.1,initial_res.0,initial_res.1,old.pn.iter().sum::<f64>(),old.pu.iter().sum::<f64>(),started.elapsed().as_secs_f64(),records.join(",")))?;
    println!("three experimental passive-compartment comparisons complete; RHS={counter}; benefit={passes}");
    Ok(())
}
fn main() -> Result<(), Box<dyn Error>> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len() != 4 {
        return Err("usage: axbi_covariant_partition_diagnostic CONFIG CHECKPOINT BASELINE_JSON FRESH_OUTPUT".into());
    }
    run(
        Path::new(&args[0]),
        Path::new(&args[1]),
        Path::new(&args[2]),
        Path::new(&args[3]),
    )
}
