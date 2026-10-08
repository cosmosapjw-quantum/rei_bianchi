//! Single owner for primary photo events and packet losses, in erg and photons/H.
use crate::{
    coupled_primary::PrimaryPacket, igm_state::IgmGasState, igm_thermal::IgmPhotoInput,
    ForwardError,
};
#[derive(Clone, Debug, Default)]
pub struct IgmPhotoRates {
    pub input: IgmPhotoInput,
    pub packet_owner_per_h_s: Vec<[f64; 3]>,
    pub owner_per_h_s: [f64; 3],
    pub absorbed_erg_per_h_s: f64,
    /// Conservative lost-rate bounds from explicitly identified IEEE underflow.
    pub underflow_count_per_h_s: f64,
    pub underflow_energy_erg_per_h_s: f64,
}

use crate::{Absorber, AtomicProvider, HHeModel};
fn invalid() -> ForwardError {
    ForwardError::InvalidInput("IGM_PHOTO_DOMAIN_OR_ARITHMETIC")
}
fn valid(x: f64) -> bool {
    x.is_finite() && x >= 0.0
}
pub fn packet_opacity(
    gas: &IgmGasState,
    energy: f64,
    nh: f64,
    nhe: f64,
) -> Result<[f64; 3], ForwardError> {
    packet_opacity_impl(gas, energy, None, nh, nhe)
}
/// Disable specified absorber channels without changing the photon energy.
/// Active channels retain the atomic provider's original support convention.
pub fn packet_opacity_masked(
    gas: &IgmGasState,
    energy: f64,
    active: [bool; 3],
    nh: f64,
    nhe: f64,
) -> Result<[f64; 3], ForwardError> {
    packet_opacity_impl(gas, energy, Some(active), nh, nhe)
}
fn packet_opacity_impl(
    gas: &IgmGasState,
    energy: f64,
    active: Option<[bool; 3]>,
    nh: f64,
    nhe: f64,
) -> Result<[f64; 3], ForwardError> {
    gas.eos(nh, nhe)?;
    if !energy.is_normal() || energy <= 0.0 {
        return Err(invalid());
    }
    let [x, y, z] = gas.fractions;
    let n = [nh * (1.0 - x), nhe * (1.0 - (y + z)), nhe * y];
    let mut out = [0.0; 3];
    let c = HHeModel::controlled_fixture();
    for (i, a) in [Absorber::HI, Absorber::HeI, Absorber::HeII]
        .iter()
        .enumerate()
    {
        if active.is_some_and(|mask| !mask[i]) {
            continue;
        }
        let sigma = AtomicProvider::reference().cross_section(*a, energy)?;
        out[i] = c.c_cm_s * n[i] * sigma;
        if !valid(out[i]) || (n[i] > 0.0 && sigma > 0.0 && !out[i].is_normal()) {
            return Err(invalid());
        }
    }
    Ok(out)
}
pub fn igm_photo_rates(
    gas: &IgmGasState,
    packets: &[PrimaryPacket],
    nh: f64,
    nhe: f64,
) -> Result<IgmPhotoRates, ForwardError> {
    igm_photo_rates_impl(gas, packets, None, nh, nhe)
}
/// Per-packet, per-absorber support masks shared by gamma, heat and photon owners.
pub fn igm_photo_rates_masked(
    gas: &IgmGasState,
    packets: &[PrimaryPacket],
    masks: &[[bool; 3]],
    nh: f64,
    nhe: f64,
) -> Result<IgmPhotoRates, ForwardError> {
    igm_photo_rates_impl(gas, packets, Some(masks), nh, nhe)
}
fn igm_photo_rates_impl(
    gas: &IgmGasState,
    packets: &[PrimaryPacket],
    masks: Option<&[[bool; 3]]>,
    nh: f64,
    nhe: f64,
) -> Result<IgmPhotoRates, ForwardError> {
    if masks.is_some_and(|m| m.len() != packets.len()) {
        return Err(invalid());
    }
    gas.eos(nh, nhe)?;
    let c = HHeModel::controlled_fixture();
    let mut out = IgmPhotoRates::default();
    for (j, p) in packets.iter().enumerate() {
        if !valid(p.per_h) {
            return Err(invalid());
        }
        let active = masks.map(|m| m[j]);
        let opacity = packet_opacity_impl(gas, p.energy_ev, active, nh, nhe)?;
        let mut owners = [0.0; 3];
        for (i, a) in [Absorber::HI, Absorber::HeI, Absorber::HeII]
            .iter()
            .enumerate()
        {
            if active.is_some_and(|mask| !mask[i]) {
                continue;
            }
            let sigma = AtomicProvider::reference().cross_section(*a, p.energy_ev)?;
            if sigma == 0.0 || p.per_h == 0.0 {
                continue;
            }
            let gamma = c.c_cm_s * nh * sigma * p.per_h;
            let heat = gamma * (p.energy_ev - c.threshold_ev[i]) * c.ev_erg;
            owners[i] = opacity[i] * p.per_h;
            if !valid(gamma) || !valid(heat) || !valid(owners[i]) {
                return Err(invalid());
            }
            let ratio = [
                1.0 - gas.fractions[0],
                nhe / nh * (1.0 - (gas.fractions[1] + gas.fractions[2])),
                nhe / nh * gas.fractions[1],
            ][i];
            if !gamma.is_normal() {
                out.underflow_count_per_h_s += ratio * f64::MIN_POSITIVE;
                out.underflow_energy_erg_per_h_s +=
                    ratio * f64::MIN_POSITIVE * p.energy_ev * c.ev_erg;
            }
            if !heat.is_normal() {
                out.underflow_energy_erg_per_h_s += ratio * f64::MIN_POSITIVE;
            }
            if opacity[i] > 0.0 && !owners[i].is_normal() {
                out.underflow_count_per_h_s += f64::MIN_POSITIVE;
                out.underflow_energy_erg_per_h_s += f64::MIN_POSITIVE * p.energy_ev * c.ev_erg;
            }
            out.input.gamma_s[i] += gamma;
            out.input.heat_erg_per_absorber_s[i] += heat;
            out.owner_per_h_s[i] += owners[i];
            out.absorbed_erg_per_h_s += owners[i] * p.energy_ev * c.ev_erg;
        }
        out.packet_owner_per_h_s.push(owners);
    }
    // Strict point-provider admission is unchanged. Quantities whose entire
    // contribution lies below normal arithmetic are rounded only at this numeric
    // boundary, with dimensional error bounds; packet log weights are retained.
    let abs = [
        nh * (1.0 - gas.fractions[0]),
        nhe * (1.0 - (gas.fractions[1] + gas.fractions[2])),
        nhe * gas.fractions[1],
    ];
    for i in 0..3 {
        let gamma = out.input.gamma_s[i];
        let heat = out.input.heat_erg_per_absorber_s[i];
        let ratio = abs[i] / nh;
        let gamma_bad = gamma > 0.0
            && (!gamma.is_normal()
                || (abs[i] > 0.0 && !(abs[i] * gamma * c.threshold_ev[i] * c.ev_erg).is_normal()));
        let heat_bad =
            heat > 0.0 && (!heat.is_normal() || (abs[i] > 0.0 && !(abs[i] * heat).is_normal()));
        if gamma_bad {
            out.underflow_count_per_h_s += ratio * gamma + f64::MIN_POSITIVE;
            out.underflow_energy_erg_per_h_s +=
                ratio * (gamma * c.threshold_ev[i] * c.ev_erg + heat) + f64::MIN_POSITIVE;
            out.input.gamma_s[i] = 0.0;
            out.input.heat_erg_per_absorber_s[i] = 0.0;
        } else if heat_bad {
            out.underflow_energy_erg_per_h_s += ratio * heat + f64::MIN_POSITIVE;
            out.input.heat_erg_per_absorber_s[i] = 0.0;
        }
    }
    for v in out
        .input
        .gamma_s
        .iter()
        .chain(out.input.heat_erg_per_absorber_s.iter())
        .chain(out.owner_per_h_s.iter())
        .chain(std::iter::once(&out.absorbed_erg_per_h_s))
    {
        if !valid(*v) {
            return Err(invalid());
        }
    }
    Ok(out)
}
