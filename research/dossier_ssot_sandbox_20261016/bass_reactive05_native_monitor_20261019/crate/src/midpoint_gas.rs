//! P4/S8 explicit midpoint gas reference, fixed proper volume, no photon owner.
//! Original full_network remains byte unchanged. Collision source expressions
//! below are transcribed from its collision_step with dt=1 second, not obtained
//! by differencing two nearby states. CX uses original DAtomicRhs channels4/5.
//! This opt-in path requires AtomicRhs CX ownership and never calls thermal CX
//! substeps. Every stage is validated; positivity is NOT unconditional or SSP.
use crate::HHeModel;
use crate::deuterium_atomic::{DChargeExchange, d_atomic_rhs};
use crate::deuterium_thermal_coupling::CxOwnership;
use crate::full_network::{
    EV_J, EventBudget, FullState, NetworkConfig, NetworkError, NetworkResult,
};
use crate::igm_rates::igm_rates;
use crate::isotope_state::{IsotopeNumberState, IsotopeSpecies as S};
use crate::mixture_eos::MixtureState;
const CGS_POWER_TO_SI: f64 = 0.1;
#[derive(Clone, Debug)]
pub struct GasRhs {
    pub nuclei_per_s: [f64; 13],
    pub budget_per_s: EventBudget,
}
fn atomic_values(s: &MixtureState) -> [f64; 13] {
    std::array::from_fn(|i| s.nuclei.density_m3(S::ALL[i]))
}
fn coefficient_rates_m3s(ne: f64, absorber: f64, ion: f64, ci: f64, rr: f64) -> (f64, f64) {
    let ne_cm = ne * 1e-6;
    (ne_cm * absorber * ci, ne_cm * ion * rr)
}
fn chemistry_deltas(a: &mut [f64; 13], j: usize, x: f64) {
    let (lo, hi) = [
        (S::H1Neutral, S::H1Ionized),
        (S::He4Neutral, S::He4SinglyIonized),
        (S::He4SinglyIonized, S::He4DoublyIonized),
        (S::DNeutral, S::DIonized),
    ][j];
    a[lo as usize] -= x;
    a[hi as usize] += x;
}
fn contract(s: &FullState, c: &NetworkConfig) -> Result<(), NetworkError> {
    s.validate(c)?;
    if c.use_photo || !s.photon_bins.is_empty() {
        return Err(NetworkError::OwnershipConflict);
    }
    if c.use_cx && c.owner != CxOwnership::AtomicRhs {
        return Err(NetworkError::OwnershipConflict);
    }
    Ok(())
}
pub fn rhs(s: &FullState, c: &NetworkConfig) -> Result<GasRhs, NetworkError> {
    contract(s, c)?;
    let dt = 1.0; // Unit exposure for powers/event rates, never a finite-difference RHS.
    let eos = s.gas.eos()?;
    let t = eos.temperature_k;
    let n = atomic_values(&s.gas);
    let ne = eos.free_electrons_m3;
    let mut d_net = 0.0;
    let mut d_ci = 0.0;
    let mut d_rr = 0.0;
    let mut ci = [0.0; 4];
    let mut rr = [0.0; 4];
    let mut dr = 0.0;
    let mut heat = 0.0;
    let mut chem = 0.0;
    let mut esc = 0.0;
    let mut ff = 0.0;
    let kbase = HHeModel::controlled_fixture().threshold_ev;
    let r = igm_rates(t).map_err(|_| NetworkError::TemperatureOutsideSource)?;
    if c.use_collisions {
        // The original D RHS sees the entire mixture n_e; CX disabled here.
        let no_d_photo = c
            .deuterium
            .photo_input_from_bound_rates(0.0, 0.0, c.photon_source)
            .map_err(|_| NetworkError::SourceMismatch)?;
        let d = d_atomic_rhs(
            c.deuterium,
            &s.gas.nuclei,
            t,
            &no_d_photo,
            DChargeExchange::Disabled,
        )
        .map_err(|_| NetworkError::InputOutsideDomain)?;
        d_net = d.species_m3_s[S::DIonized as usize];
        d_ci = d.ci_events_m3_s;
        d_rr = d.rr_events_m3_s;
        let d_ledger = d.energy;
        if d.energy.residual().abs()
            > 1e-13
                * d.energy
                    .thermal
                    .abs()
                    .max(d.energy.chemical.abs())
                    .max(d.energy.escape.abs())
                    .max(1e-30)
        {
            return Err(NetworkError::PhysicsLedger);
        }
        let low = [
            n[S::H1Neutral as usize],
            n[S::He4Neutral as usize],
            n[S::He4SinglyIonized as usize],
        ];
        let high = [
            n[S::H1Ionized as usize],
            n[S::He4SinglyIonized as usize],
            n[S::He4DoublyIonized as usize],
        ];
        for j in 0..3 {
            let (cij, rrj) =
                coefficient_rates_m3s(ne, low[j], high[j], r.ci_cm3_s[j], r.rr_cm3_s[j]);
            ci[j] = cij;
            rr[j] = rrj;
            let chi = kbase[j] * EV_J;
            chem += (cij - rrj) * chi * dt;
            heat -= cij * chi * dt;
            esc += rrj * chi * dt;
            // Kinetic recombination cooling only, not the binding energy again.
            let rr_kin = ne * 1e-6 * high[j] * 1e-6 * r.rr_cooling_erg_cm3_s[j] * CGS_POWER_TO_SI;
            heat -= rr_kin * dt;
            esc += rr_kin * dt;
        }
        // HeII -> HeI dielectronic branch from original Grackle, once.
        dr = coefficient_rates_m3s(ne, 0.0, n[S::He4SinglyIonized as usize], 0.0, r.dr_cm3_s).1;
        let chi1 = kbase[1] * EV_J;
        chem -= dr * chi1 * dt;
        esc += dr * chi1 * dt;
        let dr_kin = ne
            * 1e-6
            * n[S::He4SinglyIonized as usize]
            * 1e-6
            * r.dr_cooling_erg_cm3_s
            * CGS_POWER_TO_SI;
        heat -= dr_kin * dt;
        esc += dr_kin * dt;
        // Three CE channels, original HeI metastable has ne^2*n(HeII).
        let ne_cm = ne * 1e-6;
        let ce0 = ne_cm * (low[0] * 1e-6) * r.ce_erg[0] * CGS_POWER_TO_SI;
        let ce1 = ne_cm.powi(2)
            * (n[S::He4SinglyIonized as usize] * 1e-6)
            * r.ce_erg[1]
            * CGS_POWER_TO_SI;
        let ce2 = ne_cm * (n[S::He4SinglyIonized as usize] * 1e-6) * r.ce_erg[2] * CGS_POWER_TO_SI;
        let ces = ce0 + ce1 + ce2;
        heat -= ces * dt;
        esc += ces * dt;
        // Free-free global owner. Include all charged spectator ions, not only D/H/He4.
        let z2: f64 = S::ALL
            .into_iter()
            .map(|sp| {
                let q = f64::from(sp.charge());
                q * q * n[sp as usize]
            })
            .sum();
        ff = ne_cm * (z2 * 1e-6) * r.freefree_erg_cm3_s * CGS_POWER_TO_SI;
        heat -= ff * dt;
        esc += ff * dt;
        // D provider independently owns its CI/RR/CE binding and escape.
        heat += d_ledger.thermal * dt;
        chem += d_ledger.chemical * dt;
        esc += d_ledger.escape * dt;
    }
    // Exactly one global CMB owner based on *total* electrons, including D and spectators.
    let mut cmb = 0.0;
    if c.use_cmb {
        const SIGMA_T_CM2: f64 = 6.652_458_705_1e-25;
        const ME_G: f64 = 9.109_383_713_9e-28;
        const PLANCK_ERG_S: f64 = 6.626_070_15e-27;
        let hc = HHeModel::controlled_fixture();
        let arad = 8.0 * std::f64::consts::PI.powi(5) * hc.kb_erg_k.powi(4)
            / (15.0 * PLANCK_ERG_S.powi(3) * hc.c_cm_s.powi(3));
        let coeff = 4.0 * SIGMA_T_CM2 * arad * hc.kb_erg_k / (ME_G * hc.c_cm_s);
        cmb = coeff
            * (ne * 1e-6)
            * c.cmb_temperature_k.powi(4)
            * (c.cmb_temperature_k - t)
            * CGS_POWER_TO_SI;
        heat += cmb * dt;
    }

    let mut dn = [0.; 13];
    for j in 0..3 {
        chemistry_deltas(&mut dn, j, ci[j] - rr[j]);
    }
    chemistry_deltas(&mut dn, 1, -dr);
    chemistry_deltas(&mut dn, 3, d_net);
    let mut cx = 0.;
    if c.use_cx {
        let none = c
            .deuterium
            .photo_input_from_bound_rates(0., 0., c.photon_source)
            .map_err(|_| NetworkError::SourceMismatch)?;
        let d = d_atomic_rhs(
            c.deuterium,
            &s.gas.nuclei,
            t,
            &none,
            DChargeExchange::Savin2002,
        )
        .map_err(|_| NetworkError::InputOutsideDomain)?;
        cx = d.cx_forward_events_m3_s - d.cx_reverse_events_m3_s;
        dn[S::H1Neutral as usize] += cx;
        dn[S::H1Ionized as usize] -= cx;
        dn[S::DNeutral as usize] -= cx;
        dn[S::DIonized as usize] += cx;
        heat += d.channel_energy[4].thermal + d.channel_energy[5].thermal;
        chem += d.channel_energy[4].chemical + d.channel_energy[5].chemical;
    }
    ci[3] = d_ci;
    rr[3] = d_rr;
    let budget = EventBudget {
        ci_events_m3: ci,
        rr_events_m3: rr,
        dr_hei_m3: dr,
        cx_signed_m3: cx,
        thermal_change_j_m3: heat,
        chemical_change_j_m3: chem,
        escape_change_j_m3: esc,
        cmb_change_j_m3: -cmb,
        freefree_integrated_j_m3: ff,
        d_electron_integrated_m3: d_net,
        ..EventBudget::default()
    };
    if !dn.iter().all(|v| v.is_finite())
        || ![heat, chem, esc, cmb, ff, cx].iter().all(|v| v.is_finite())
    {
        return Err(NetworkError::NonFinite);
    }
    let scale = heat
        .abs()
        .max(chem.abs())
        .max(esc.abs())
        .max(cmb.abs())
        .max(1e-80);
    if (heat + chem + esc - cmb).abs() > 2e-12 * scale {
        return Err(NetworkError::PhysicsLedger);
    }
    Ok(GasRhs {
        nuclei_per_s: dn,
        budget_per_s: budget,
    })
}
pub fn scale_budget(mut b: EventBudget, h: f64) -> EventBudget {
    for v in [
        &mut b.photo_events_m3,
        &mut b.ci_events_m3,
        &mut b.rr_events_m3,
    ] {
        for x in v {
            *x *= h;
        }
    }
    b.dr_hei_m3 *= h;
    b.cx_signed_m3 *= h;
    b.photo_energy_j_m3 *= h;
    b.thermal_change_j_m3 *= h;
    b.chemical_change_j_m3 *= h;
    b.escape_change_j_m3 *= h;
    b.cmb_change_j_m3 *= h;
    b.freefree_integrated_j_m3 *= h;
    b.d_electron_integrated_m3 *= h;
    b
}
/// Apply one event-rate vector to a distinct, already photo-updated state.
/// The caller owns the evaluation time; no clipping, no extra CX or photon step.
pub fn apply(
    s: &FullState,
    c: &NetworkConfig,
    r: &GasRhs,
    h: f64,
) -> Result<NetworkResult, NetworkError> {
    contract(s, c)?;
    if !h.is_finite() || h < 0. {
        return Err(NetworkError::InvalidInput);
    }
    let mut out = s.clone();
    let budget = scale_budget(r.budget_per_s, h);
    let mut n = atomic_values(&out.gas);
    for (x, dx) in n.iter_mut().zip(r.nuclei_per_s) {
        *x += h * dx;
    }
    out.gas.nuclei = IsotopeNumberState::new(n).map_err(|_| NetworkError::NegativePopulation)?;
    out.gas.thermal_j_m3 += budget.thermal_change_j_m3;
    out.escaped_j_m3 += budget.escape_change_j_m3;
    out.cmb_reservoir_j_m3 += budget.cmb_change_j_m3;
    out.elapsed_s += h;
    out.validate(c)?;
    let en = s.energy_j_m3(c);
    let ef = out.energy_j_m3(c);
    if !ef.is_finite() || (ef - en).abs() > 3e-11 * en.abs().max(ef.abs()).max(1e-50) {
        return Err(NetworkError::PhysicsLedger);
    }
    Ok(NetworkResult {
        state: out,
        budget,
        attempts: 1,
        accepted: 1,
        rejected: 0,
    })
}
/// Two-stage explicit midpoint RK2. Rejection is transactional.
pub fn step(s: &FullState, c: &NetworkConfig, h: f64) -> Result<NetworkResult, NetworkError> {
    contract(s, c)?;
    if !h.is_finite() || h < 0. {
        return Err(NetworkError::InvalidInput);
    }
    if h == 0. {
        return Ok(NetworkResult {
            state: s.clone(),
            budget: EventBudget::default(),
            attempts: 1,
            accepted: 1,
            rejected: 0,
        });
    }
    let k1 = rhs(s, c)?;
    let mid = apply(s, c, &k1, 0.5 * h)?.state;
    let k2 = rhs(&mid, c)?;
    apply(s, c, &k2, h)
}

/// Add process-owned budgets without any reapplication of their state changes.
pub fn add_budget(mut a: EventBudget, b: EventBudget) -> EventBudget {
    for j in 0..4 {
        a.photo_events_m3[j] += b.photo_events_m3[j];
        a.ci_events_m3[j] += b.ci_events_m3[j];
        a.rr_events_m3[j] += b.rr_events_m3[j];
    }
    a.dr_hei_m3 += b.dr_hei_m3;
    a.cx_signed_m3 += b.cx_signed_m3;
    a.photo_energy_j_m3 += b.photo_energy_j_m3;
    a.thermal_change_j_m3 += b.thermal_change_j_m3;
    a.chemical_change_j_m3 += b.chemical_change_j_m3;
    a.escape_change_j_m3 += b.escape_change_j_m3;
    a.cmb_change_j_m3 += b.cmb_change_j_m3;
    a.freefree_integrated_j_m3 += b.freefree_integrated_j_m3;
    a.d_electron_integrated_m3 += b.d_electron_integrated_m3;
    a
}
/// Native temperature-dependent CX-only flow. Does NOT advance the global clock.
/// Its local integration duration is an operator exposure, not extra cosmic time.
pub fn cx_flow(s: &FullState, c: &NetworkConfig, h: f64) -> Result<NetworkResult, NetworkError> {
    s.validate(c)?;
    if c.use_photo || !s.photon_bins.is_empty() || !h.is_finite() || h < 0. {
        return Err(NetworkError::InvalidInput);
    }
    let mut out = s.clone();
    let mut budget = EventBudget::default();
    if c.use_cx {
        if c.owner != CxOwnership::ThermalSubstep {
            return Err(NetworkError::OwnershipConflict);
        }
        let r = crate::mixture_coupling::MixtureCxComponent::new(c.deuterium, c.owner)
            .advance_cx_only(s.gas, h, c.cx_controls)
            .map_err(NetworkError::Cx)?;
        out.gas = r.final_state;
        budget.cx_signed_m3 = r.extent_m3;
        budget.thermal_change_j_m3 = r.delta_thermal_j_m3;
        budget.chemical_change_j_m3 = r.delta_chemical_j_m3;
    }
    out.validate(c)?;
    Ok(NetworkResult {
        state: out,
        budget,
        attempts: 1,
        accepted: 1,
        rejected: 0,
    })
}
/// Symmetric CX(h/2) -> collision/CMB RK2(h) -> CX(h/2).
/// The middle integrator is genuinely RK2; wrapping Euler would remain first order.
/// CX uses the original adaptive thermal solver, not an exact T-frozen surrogate.
pub fn step_strang(
    s: &FullState,
    c: &NetworkConfig,
    h: f64,
) -> Result<NetworkResult, NetworkError> {
    if c.use_photo || !h.is_finite() || h < 0. {
        return Err(NetworkError::InvalidInput);
    }
    let a = cx_flow(s, c, h * 0.5)?;
    let mut nc = *c;
    nc.use_cx = false;
    let b = step(&a.state, &nc, h)?;
    let d = cx_flow(&b.state, c, h * 0.5)?;
    let budget = add_budget(add_budget(a.budget, b.budget), d.budget);
    let en = s.energy_j_m3(c);
    let ef = d.state.energy_j_m3(c);
    if (ef - en).abs() > 3e-11 * en.abs().max(ef.abs()).max(1e-50) {
        return Err(NetworkError::PhysicsLedger);
    }
    Ok(NetworkResult {
        state: d.state,
        budget,
        attempts: 1,
        accepted: 1,
        rejected: 0,
    })
}
