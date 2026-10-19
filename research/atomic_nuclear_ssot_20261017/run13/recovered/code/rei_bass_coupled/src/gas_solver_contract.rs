//! Contract for an externally integrated native gas stage. No callback can own photons.
use crate::HHeModel;
use crate::full_network::{EV_J, FullState, NetworkConfig, NetworkError, NetworkResult};
use crate::isotope_state::IsotopeSpecies as S;
pub fn validate_result(
    s: &FullState,
    c: &NetworkConfig,
    dt: f64,
    r: &NetworkResult,
) -> Result<(), NetworkError> {
    if c.use_photo || !s.photon_bins.is_empty() || !r.state.photon_bins.is_empty() {
        return Err(NetworkError::OwnershipConflict);
    }
    r.state.validate(c)?;
    let n0 = |sp| s.gas.nuclei.density_m3(sp);
    let n1 = |sp| r.state.gas.nuclei.density_m3(sp);
    for family in [
        vec![S::H1Neutral, S::H1Ionized],
        vec![S::DNeutral, S::DIonized],
        vec![S::He4Neutral, S::He4SinglyIonized, S::He4DoublyIonized],
    ] {
        let a = family.iter().map(|&sp| n0(sp)).sum::<f64>();
        let b = family.iter().map(|&sp| n1(sp)).sum::<f64>();
        if (a - b).abs() > 3e-11 * a.abs().max(b.abs()).max(1e-40) {
            return Err(NetworkError::PhysicsLedger);
        }
    }
    let mut dn = [0.; 13];
    let mut apply = |lo: S, hi: S, v: f64| {
        dn[lo as usize] -= v;
        dn[hi as usize] += v;
    };
    for (j, (lo, hi)) in [
        (S::H1Neutral, S::H1Ionized),
        (S::He4Neutral, S::He4SinglyIonized),
        (S::He4SinglyIonized, S::He4DoublyIonized),
        (S::DNeutral, S::DIonized),
    ]
    .into_iter()
    .enumerate()
    {
        apply(lo, hi, r.budget.ci_events_m3[j] - r.budget.rr_events_m3[j]);
    }
    apply(S::He4SinglyIonized, S::He4Neutral, r.budget.dr_hei_m3);
    apply(S::H1Ionized, S::H1Neutral, r.budget.cx_signed_m3);
    apply(S::DNeutral, S::DIonized, r.budget.cx_signed_m3);
    for sp in S::ALL {
        let a = n0(sp);
        let b = n1(sp);
        if (b - a - dn[sp as usize]).abs() > 3e-11 * a.abs().max(b.abs()).max(1e-40) {
            return Err(NetworkError::PhysicsLedger);
        }
    }
    let q = &r.budget;
    let unsigned = q
        .ci_events_m3
        .into_iter()
        .chain(q.rr_events_m3)
        .chain([q.dr_hei_m3, q.freefree_integrated_j_m3]);
    if !unsigned.into_iter().all(|x| x.is_finite() && x >= 0.) || !q.cx_signed_m3.is_finite() {
        return Err(NetworkError::NonFinite);
    }
    if q.photo_events_m3 != [0.; 4] || q.photo_energy_j_m3 != 0. {
        return Err(NetworkError::OwnershipConflict);
    }
    let chi = HHeModel::controlled_fixture().threshold_ev;
    let chemical = EV_J
        * (chi[0] * dn[S::H1Ionized as usize]
            + chi[1] * dn[S::He4SinglyIonized as usize]
            + (chi[1] + chi[2]) * dn[S::He4DoublyIonized as usize]
            + c.deuterium.chi_d_ev() * dn[S::DIonized as usize]);
    let scale = s
        .energy_j_m3(c)
        .abs()
        .max(r.state.energy_j_m3(c).abs())
        .max(1e-40);
    let checks = [
        r.state.energy_j_m3(c) - s.energy_j_m3(c),
        r.state.gas.thermal_j_m3 - s.gas.thermal_j_m3 - q.thermal_change_j_m3,
        r.state.escaped_j_m3 - s.escaped_j_m3 - q.escape_change_j_m3,
        r.state.cmb_reservoir_j_m3 - s.cmb_reservoir_j_m3 - q.cmb_change_j_m3,
        chemical - q.chemical_change_j_m3,
    ];
    if checks
        .into_iter()
        .any(|x| !x.is_finite() || x.abs() > 3e-11 * scale)
    {
        return Err(NetworkError::PhysicsLedger);
    }
    if !dt.is_finite() || dt <= 0. || r.state.elapsed_s != s.elapsed_s + dt {
        return Err(NetworkError::InvalidInput);
    }
    Ok(())
}
