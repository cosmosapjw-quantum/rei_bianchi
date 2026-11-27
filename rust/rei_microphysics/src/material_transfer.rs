//! Fixed-volume proper-cell collision step. The geometry owner supplies the clock.
//! Densities use m^-3, and energy stocks use eV m^-3. No rest-mass energy is evolved.
use crate::igm_state::IgmGasState;
use crate::{ForwardError, HHeModel, IsotopeNumberState, IsotopeSpecies as S};
use std::collections::HashSet;

#[derive(Clone, Debug)]
pub struct Cell {
    pub scenario: String,
    pub proper_s: f64,
    pub nuclei: IsotopeNumberState,
    pub thermal_ev_m3: f64,
    pub photon_ev_m3: f64,
    pub projectile_ev_m3: f64,
    pub secondary_ev_m3: f64,
    pub secondary_electrons_m3: f64,
    pub escaped_ev_m3: f64,
    /// Difference between the projectile stopping convention and the host binding convention.
    pub threshold_offset_ev_m3: f64,
}

/// The atomic threshold convention belongs to the existing REI H/He owner.
#[derive(Clone, Copy, Debug)]
pub enum Target {
    H,
    HeI,
    HeII,
}
impl Target {
    fn ions(self) -> (S, S, usize) {
        match self {
            Self::H => (S::H1Neutral, S::H1Ionized, 0),
            Self::HeI => (S::He4Neutral, S::He4SinglyIonized, 1),
            Self::HeII => (S::He4SinglyIonized, S::He4DoublyIonized, 2),
        }
    }
}
#[derive(Clone, Copy, Debug)]
pub enum Process {
    /// Positive means D I + H II -> D II + H I.
    ChargeExchange {
        net_m3: f64,
    },
    Photo {
        target: Target,
        absorbed_m3: f64,
        energy_ev: f64,
    },
    EscapingLine {
        number_m3: f64,
        energy_ev: f64,
    },
    /// Primary proton ionization. Births are charged nonthermal particles until deposition.
    CosmicRay {
        target: Target,
        births_m3: f64,
        born_kinetic_ev_m3: f64,
        threshold_offset_ev_m3: f64,
    },
}
#[derive(Clone, Debug)]
pub struct Transfer<'a> {
    pub event_id: &'a str,
    pub already_in_host_rhs: bool,
    pub process: Process,
}
fn invalid(reason: &'static str) -> ForwardError {
    ForwardError::InvalidInput(reason)
}
fn nonnegative(x: f64) -> bool {
    x.is_finite() && x >= 0.0
}
fn change_ion(n: &mut [f64; 13], from: S, to: S, value: f64) {
    n[from as usize] -= value;
    n[to as usize] += value;
}
const DELTA_D_EV: f64 = 0.0037;
impl Cell {
    /// Lift the host state at fixed temperature, specifying the additional D reservoir explicitly.
    pub fn from_host(
        scenario: &str,
        proper_s: f64,
        gas: IgmGasState,
        nh_cm3: f64,
        nhe_cm3: f64,
        nd_cm3: f64,
        yd: f64,
    ) -> Result<Self, ForwardError> {
        if !nonnegative(nd_cm3) || !yd.is_finite() || !(0.0..=1.0).contains(&yd) {
            return Err(invalid("D_INVENTORY"));
        }
        let eos = gas.eos(nh_cm3, nhe_cm3)?;
        let [h, he1, he2] = gas.fractions;
        let mut n = [0.0; 13];
        for (s, x) in [
            (S::H1Neutral, nh_cm3 * (1.0 - h)),
            (S::H1Ionized, nh_cm3 * h),
            (S::He4Neutral, nhe_cm3 * (1.0 - (he1 + he2))),
            (S::He4SinglyIonized, nhe_cm3 * he1),
            (S::He4DoublyIonized, nhe_cm3 * he2),
            (S::DNeutral, nd_cm3 * (1.0 - yd)),
            (S::DIonized, nd_cm3 * yd),
        ] {
            n[s as usize] = x * 1e6;
        }
        let nuclei = IsotopeNumberState::new(n)?;
        let model = HHeModel::controlled_fixture();
        let thermal_ev_m3 = 1.5 * model.kb_erg_k / model.ev_erg
            * eos.temperature_k
            * nuclei.thermal_particle_density_all_thermal_m3()?;
        let cell = Self {
            scenario: scenario.into(),
            proper_s,
            nuclei,
            thermal_ev_m3,
            photon_ev_m3: 0.0,
            projectile_ev_m3: 0.0,
            secondary_ev_m3: 0.0,
            secondary_electrons_m3: 0.0,
            escaped_ev_m3: 0.0,
            threshold_offset_ev_m3: 0.0,
        };
        cell.validate()?;
        Ok(cell)
    }
    pub fn electron_thermal_m3(&self) -> Result<f64, ForwardError> {
        let value =
            self.nuclei.moments()?.neutral_free_electron_density_m3 - self.secondary_electrons_m3;
        if nonnegative(value) {
            Ok(value)
        } else {
            Err(invalid("NONTHERMAL_ELECTRON_STOCK"))
        }
    }
    pub fn temperature_k(&self) -> Result<f64, ForwardError> {
        let particles =
            self.nuclei.moments()?.heavy_particle_density_m3 + self.electron_thermal_m3()?;
        let c = HHeModel::controlled_fixture();
        let t = self.thermal_ev_m3 / particles * (2.0 * c.ev_erg / (3.0 * c.kb_erg_k));
        if t > 0.0 && t.is_finite() {
            Ok(t)
        } else {
            Err(invalid("THERMAL_DOMAIN"))
        }
    }
    pub fn ionization_ev_m3(&self) -> f64 {
        let [h, he1, he2] = HHeModel::controlled_fixture().threshold_ev;
        self.nuclei.density_m3(S::H1Ionized) * h
            + self.nuclei.density_m3(S::DIonized) * (h + DELTA_D_EV)
            + self.nuclei.density_m3(S::He4SinglyIonized) * he1
            + self.nuclei.density_m3(S::He4DoublyIonized) * (he1 + he2)
    }
    pub fn total_ev_m3(&self) -> f64 {
        self.thermal_ev_m3
            + self.ionization_ev_m3()
            + self.photon_ev_m3
            + self.projectile_ev_m3
            + self.secondary_ev_m3
            + self.escaped_ev_m3
            + self.threshold_offset_ev_m3
    }
    fn validate(&self) -> Result<(), ForwardError> {
        if self.scenario.is_empty()
            || !self.threshold_offset_ev_m3.is_finite()
            || ![
                self.proper_s,
                self.thermal_ev_m3,
                self.photon_ev_m3,
                self.projectile_ev_m3,
                self.secondary_ev_m3,
                self.secondary_electrons_m3,
                self.escaped_ev_m3,
                self.total_ev_m3(),
            ]
            .into_iter()
            .all(nonnegative)
        {
            return Err(invalid("CELL_DOMAIN"));
        }
        for s in [
            S::Neutron,
            S::TNeutral,
            S::TIonized,
            S::He3Neutral,
            S::He3SinglyIonized,
            S::He3DoublyIonized,
        ] {
            if self.nuclei.density_m3(s) != 0.0 {
                return Err(invalid("CELL_SPECIES_DOMAIN"));
            }
        }
        self.temperature_k()?;
        Ok(())
    }
    /// Transactional: a bad event, epoch, or depleted stock returns without changing the input.
    pub fn advance(
        &self,
        scenario: &str,
        begin_s: f64,
        end_s: f64,
        transfers: &[Transfer],
    ) -> Result<Self, ForwardError> {
        self.validate()?;
        if scenario != self.scenario
            || begin_s != self.proper_s
            || !end_s.is_finite()
            || end_s <= begin_s
        {
            return Err(invalid("SOURCE_FRAME_OR_CLOCK"));
        }
        let thresholds = HHeModel::controlled_fixture().threshold_ev;
        let mut out = self.clone();
        let mut n = S::ALL.map(|s| self.nuclei.density_m3(s));
        let mut seen = HashSet::new();
        for row in transfers {
            if row.event_id.is_empty() || !seen.insert(row.event_id) || row.already_in_host_rhs {
                return Err(invalid("DUPLICATE_EVENT_OWNERSHIP"));
            }
            match row.process {
                Process::ChargeExchange { net_m3: j } if j.is_finite() => {
                    change_ion(&mut n, S::H1Ionized, S::H1Neutral, j);
                    change_ion(&mut n, S::DNeutral, S::DIonized, j);
                    out.thermal_ev_m3 -= DELTA_D_EV * j;
                }
                Process::Photo {
                    target,
                    absorbed_m3: z,
                    energy_ev: e,
                } if nonnegative(z) && e.is_finite() => {
                    let (lo, hi, i) = target.ions();
                    if e < 0.0 || (z > 0.0 && e < [13.60, 24.59, 54.42][i]) {
                        return Err(invalid("SUBTHRESHOLD_PHOTON"));
                    }
                    change_ion(&mut n, lo, hi, z);
                    out.photon_ev_m3 -= e * z;
                    out.thermal_ev_m3 += (e - thresholds[i]) * z;
                }
                Process::EscapingLine {
                    number_m3: z,
                    energy_ev: e,
                } if nonnegative(z) && e.is_finite() && e > 0.0 => {
                    out.photon_ev_m3 -= z * e;
                    out.escaped_ev_m3 += z * e;
                }
                Process::CosmicRay {
                    target,
                    births_m3: z,
                    born_kinetic_ev_m3: w,
                    threshold_offset_ev_m3: d,
                } if nonnegative(z)
                    && nonnegative(w)
                    && d.is_finite()
                    && (z > 0.0 || (w == 0.0 && d == 0.0)) =>
                {
                    let (lo, hi, i) = target.ions();
                    change_ion(&mut n, lo, hi, z);
                    out.secondary_electrons_m3 += z;
                    out.secondary_ev_m3 += w;
                    let ion_cost = thresholds[i] * z + d;
                    if !nonnegative(ion_cost) {
                        return Err(invalid("PROJECTILE_THRESHOLD_DOMAIN"));
                    }
                    out.projectile_ev_m3 -= ion_cost + w;
                    out.threshold_offset_ev_m3 += d;
                }
                _ => return Err(invalid("EVENT_DOMAIN")),
            }
            if !n.into_iter().all(nonnegative)
                || ![out.projectile_ev_m3, out.photon_ev_m3, out.thermal_ev_m3]
                    .into_iter()
                    .all(nonnegative)
            {
                return Err(invalid("DEPLETED_STOCK"));
            }
        }
        out.nuclei = IsotopeNumberState::new(n)?;
        out.proper_s = end_s;
        out.validate()?;
        Ok(out)
    }
}

/// Passive D II update in the accepted gas frame with frozen nH, xHII and T.
/// Original Savin Table 1 is shared by the Python and Rust entry points.
pub fn trace_dii_step(
    y: f64,
    dt_s: f64,
    temperature_k: f64,
    nh_cm3: f64,
    xhii: f64,
) -> Result<f64, ForwardError> {
    use std::sync::OnceLock;
    static TABLE: OnceLock<Result<Vec<(f64, f64, f64)>, ForwardError>> = OnceLock::new();
    let table = TABLE
        .get_or_init(|| {
            let text = include_str!(
                "../../../src/rei_bianchi/microphysics/data/savin2002_charge_exchange.csv"
            );
            text.lines()
                .skip(1)
                .map(|line| {
                    let mut columns = line.split(',');
                    let mut next_number = || {
                        columns
                            .next()
                            .and_then(|s| s.trim().parse::<f64>().ok())
                            .ok_or_else(|| invalid("SAVIN_TABLE"))
                    };
                    Ok((next_number()?, next_number()?, next_number()?))
                })
                .collect()
        })
        .as_ref()
        .map_err(Clone::clone)?;
    if !(0.0..=1.0).contains(&y)
        || !(0.0..=1.0).contains(&xhii)
        || !nonnegative(dt_s)
        || !nonnegative(nh_cm3)
        || !(2.7..=200_000.).contains(&temperature_k)
    {
        return Err(invalid("SAVIN_TRACE_DOMAIN"));
    }
    let i = table.partition_point(|(t, _, _)| *t < temperature_k);
    let &(t1, f1, r1) = table.get(i).ok_or_else(|| invalid("SAVIN_TABLE"))?;
    let (kf, kr) = if t1 == temperature_k {
        (f1, r1)
    } else {
        let &(t0, f0, r0) = table
            .get(i.checked_sub(1).ok_or_else(|| invalid("SAVIN_TABLE"))?)
            .ok_or_else(|| invalid("SAVIN_TABLE"))?;
        let w = (temperature_k / t0).ln() / (t1 / t0).ln();
        (
            ((1. - w) * f0.ln() + w * f1.ln()).exp(),
            ((1. - w) * r0.ln() + w * r1.ln()).exp(),
        )
    };
    let a = kf * xhii;
    let sum = a + kr * (1. - xhii);
    let depth = sum * nh_cm3 * dt_s;
    Ok(y * (-depth).exp() + (a / sum) * (-(-depth).exp_m1()))
}
