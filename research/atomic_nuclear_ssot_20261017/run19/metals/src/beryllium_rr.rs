//! Verner & Ferland (1996), Eq. (4), selected total-RR coefficients forming
//! Be II, Be III and Be IV. The labels identify the formed ion, not the parent.
//! Source: https://www.pa.uky.edu/~verner/rec.html ; astro-ph/9509083.
//! This low-Z fit is used only for 3 K <= T <= 1e9 K. The fit's physical
//! approximation error is separate from interpolation/numerical error.
//!
//! Missing Be I formation is not a structural zero. The number operator below
//! is only the contribution of three selected electronic channels, with no
//! thermal, photo, dielectronic, ionization, nuclear or abundance closure.
use crate::{EvaluatorBinding, ForwardError, rate_table::LogRateGrid};
use crate::lithium_rates::IsotopeRatePolicy;
use std::sync::Arc;

pub const BE_RR_MIN_K: f64 = 3.0;
pub const BE_RR_MAX_K: f64 = 1e9;
pub const BE_RR_DEFAULT_NODES: usize = 8193;
pub const BE_RR_SOURCE_ID: &str = "VF1996_BE_RR_ROWS_0792b2794c4a4d996c02537cb2e83f6b7855b58daba6e89c9675cf97e2cd2570";
pub const BE_RR_SCOPE: &str = "SELECTED_TOTAL_RR_NUMBER_CONTRIBUTIONS_ONLY";
const RAW_ROWS: &str = include_str!("../data/vf1996_be_rr_rows.dat");

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum BeRrError {
    InvalidInput, InvalidCharge, TemperatureDomain, MissingSource,
    SourceData, Arithmetic, Table, BindingMismatch,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct BeRrRecord {
    pub formed_ion: &'static str,
    pub atomic_number: u8,
    pub formed_electron_count: u8,
    pub initial_charge: u8,
    pub final_charge: u8,
    pub a_cm3_s: f64,
    pub b: f64,
    pub t0_k: f64,
    pub t1_k: f64,
    pub minimum_k: f64,
    pub maximum_k: f64,
}

#[derive(Clone, Debug)]
pub struct BeRrProvider { records: [BeRrRecord; 3] }

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct BeRrRates {
    temperature_k: f64,
    alpha_cm3_s: [f64; 3],
}

impl BeRrRates {
    pub fn temperature_k(&self) -> f64 { self.temperature_k }
    /// Order: q=2->1 (BeII), q=3->2 (BeIII), q=4->3 (BeIV).
    pub fn alpha_cm3_s(&self) -> [f64; 3] { self.alpha_cm3_s }
    pub fn source_id(&self) -> &'static str { BE_RR_SOURCE_ID }
}

fn check_temperature(t: f64) -> Result<(), BeRrError> {
    if !t.is_finite() || !(BE_RR_MIN_K..=BE_RR_MAX_K).contains(&t) {
        return Err(BeRrError::TemperatureDomain);
    }
    Ok(())
}

fn check_nonnegative(v: f64) -> Result<(), BeRrError> {
    if !v.is_finite() || v < 0.0 { return Err(BeRrError::InvalidInput); }
    Ok(())
}

impl BeRrProvider {
    /// Parse exactly the three retained author rows once. No new fit is made.
    pub fn from_primary_rows() -> Result<Self, BeRrError> {
        let labels = ["BeII", "BeIII", "BeIV"];
        let mut records = Vec::with_capacity(3);
        for (i, line) in RAW_ROWS.lines().enumerate() {
            let v: Vec<_> = line.split_whitespace().collect();
            if i >= 3 || v.len() != 7 || v[0] != labels[i] || v[1] != "4" {
                return Err(BeRrError::SourceData);
            }
            let n = v[2].parse::<u8>().map_err(|_| BeRrError::SourceData)?;
            if n != 3 - i as u8 { return Err(BeRrError::SourceData); }
            let mut p = [0.0; 4];
            for (out, raw) in p.iter_mut().zip(&v[3..]) {
                *out = raw.parse::<f64>().map_err(|_| BeRrError::SourceData)?;
            }
            if p.iter().any(|v| !v.is_finite()) || p[0] <= 0.0
                || !(0.0..=1.0).contains(&p[1]) || p[2] <= 0.0 || p[3] <= 0.0 {
                return Err(BeRrError::SourceData);
            }
            records.push(BeRrRecord { formed_ion: labels[i], atomic_number: 4,
                formed_electron_count: n, initial_charge: 5 - n, final_charge: 4 - n,
                a_cm3_s: p[0], b: p[1], t0_k: p[2], t1_k: p[3],
                minimum_k: BE_RR_MIN_K, maximum_k: BE_RR_MAX_K });
        }
        Ok(Self { records: records.try_into().map_err(|_| BeRrError::SourceData)? })
    }

    pub fn records(&self) -> [BeRrRecord; 3] { self.records }

    pub fn record_forming_charge(&self, final_charge: u8) -> Result<BeRrRecord, BeRrError> {
        match final_charge {
            0 => Err(BeRrError::MissingSource), // Be I is absent, not zero.
            1..=3 => Ok(self.records[final_charge as usize - 1]),
            _ => Err(BeRrError::InvalidCharge),
        }
    }

    pub fn coefficient_cm3_s(&self, final_charge: u8, t: f64) -> Result<f64, BeRrError> {
        let p = self.record_forming_charge(final_charge)?;
        check_temperature(t)?;
        let x = (t / p.t0_k).sqrt();
        let y = (t / p.t1_k).sqrt();
        let value = p.a_cm3_s / (x * (1.0 + x).powf(1.0 - p.b) * (1.0 + y).powf(1.0 + p.b));
        if !value.is_finite() || value <= 0.0 { return Err(BeRrError::Arithmetic); }
        Ok(value)
    }

    pub fn rates(&self, t: f64) -> Result<BeRrRates, BeRrError> {
        check_temperature(t)?;
        Ok(BeRrRates { temperature_k: t, alpha_cm3_s: [
            self.coefficient_cm3_s(1, t)?, self.coefficient_cm3_s(2, t)?,
            self.coefficient_cm3_s(3, t)?,
        ] })
    }
}

/// The exact fixed99 interpolation mechanism, on a smooth positive source.
#[derive(Clone, Debug)]
pub struct BeRrTable { provider: BeRrProvider, grid: LogRateGrid<3> }

fn as_forward_error(_: BeRrError) -> ForwardError {
    ForwardError::InvalidInput("VF1996_BE_RR_DOMAIN_OR_ARITHMETIC")
}

impl BeRrTable {
    pub fn build(nodes: usize) -> Result<Self, BeRrError> {
        let provider = BeRrProvider::from_primary_rows()?;
        let grid = LogRateGrid::build(BE_RR_MIN_K, BE_RR_MAX_K, nodes,
            |t| provider.rates(t).map(|r| r.alpha_cm3_s).map_err(as_forward_error),
            |_, _| false, |_, _, _| false).map_err(|_| BeRrError::Table)?;
        Ok(Self { provider, grid })
    }
    pub fn nodes(&self) -> usize { self.grid.nodes() }
    pub fn storage_bytes(&self) -> usize { self.grid.storage_bytes() }
    pub fn blocked_cells(&self) -> usize { self.grid.blocked_cells() }

    pub fn rates(&self, t: f64) -> Result<BeRrRates, BeRrError> {
        check_temperature(t)?;
        let v = self.grid.evaluate(t,
            |x| self.provider.rates(x).map(|r| r.alpha_cm3_s).map_err(as_forward_error))
            .map_err(|_| BeRrError::Table)?;
        Ok(BeRrRates { temperature_k: t, alpha_cm3_s: v })
    }

    pub fn batch_soa(&self, ts: &[f64]) -> Result<[Vec<f64>; 3], BeRrError> {
        for &t in ts { check_temperature(t)?; }
        self.grid.evaluate_batch_soa(ts,
            |x| self.provider.rates(x).map(|r| r.alpha_cm3_s).map_err(as_forward_error))
            .map_err(|_| BeRrError::Table)
    }

    /// Preserves the shared grid's deterministic coefficient order (1..4 workers).
    pub fn batch_parallel(&self, ts: &[f64], workers: usize) -> Result<[Vec<f64>; 3], BeRrError> {
        for &t in ts { check_temperature(t)?; }
        self.grid.evaluate_batch_parallel(ts, workers,
            |x| self.provider.rates(x).map(|r| r.alpha_cm3_s).map_err(as_forward_error))
            .map_err(|_| BeRrError::Table)
    }
}

#[derive(Clone, Debug)]
enum Evaluator { Direct(Arc<BeRrProvider>), Table(Arc<BeRrTable>) }
#[derive(Clone, Debug)]
pub struct BeRrBackend { evaluator: Evaluator }
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct PreparedBeRrRates { rates: BeRrRates, binding: EvaluatorBinding }

impl PreparedBeRrRates {
    pub fn rates(&self) -> BeRrRates { self.rates }
    pub fn binding(&self) -> EvaluatorBinding { self.binding }
}

impl BeRrBackend {
    pub fn direct() -> Result<Self, BeRrError> {
        Ok(Self { evaluator: Evaluator::Direct(Arc::new(BeRrProvider::from_primary_rows()?)) })
    }
    pub fn tabulated(nodes: usize) -> Result<Self, BeRrError> {
        Ok(Self { evaluator: Evaluator::Table(Arc::new(BeRrTable::build(nodes)?)) })
    }
    pub fn binding(&self) -> EvaluatorBinding {
        let (evaluator_id, nodes) = match &self.evaluator {
            Evaluator::Direct(_) => ("VF1996_BE_RR_DIRECT_F64_V1", None),
            Evaluator::Table(t) => ("VF1996_BE_RR_FIXED99_LOGLINEAR_F64_V1", Some(t.nodes())),
        };
        EvaluatorBinding { source_id: BE_RR_SOURCE_ID, evaluator_id, nodes }
    }
    pub fn rates(&self, t: f64) -> Result<BeRrRates, BeRrError> {
        match &self.evaluator { Evaluator::Direct(p) => p.rates(t), Evaluator::Table(g) => g.rates(t) }
    }
    pub fn prepare(&self, t: f64) -> Result<PreparedBeRrRates, BeRrError> {
        Ok(PreparedBeRrRates { rates: self.rates(t)?, binding: self.binding() })
    }
    pub fn require_prepared(&self, t: f64, p: &PreparedBeRrRates) -> Result<BeRrRates, BeRrError> {
        if p.rates.temperature_k.to_bits() != t.to_bits() || p.binding != self.binding() {
            return Err(BeRrError::BindingMismatch);
        }
        Ok(p.rates)
    }
    pub fn number_contribution(&self, t: f64, prepared: &PreparedBeRrRates,
        state: &BerylliumIsotopeNumberState, electron_density_m3: f64,
        policy: IsotopeRatePolicy) -> Result<BeRrContribution, BeRrError>
    {
        be_rr_number_contribution(&self.require_prepared(t, prepared)?, state, electron_density_m3, policy)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum BerylliumIsotope { Be7, Be9 }
impl BerylliumIsotope {
    pub fn mass_number(self) -> u16 { match self { Self::Be7 => 7, Self::Be9 => 9 } }
    pub fn nuclear_charge(self) -> u16 { 4 }
    /// Isotope labels never silently activate decay or daughter models.
    pub fn nuclear_evolution_scope(self) -> &'static str { "NOT_MODELED_BY_ELECTRONIC_PROVIDER" }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct BerylliumIsotopeNumberState {
    /// [Be7(q=1..4), Be9(q=1..4)]; no Be I coordinate is defaulted.
    density_m3: [[f64; 4]; 2],
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct BerylliumNumberMoments {
    pub isotope_nuclei_m3: [f64; 2],
    pub baryon_number_m3: f64,
    pub nuclear_charge_number_m3: f64,
    pub ionic_charge_number_m3: f64,
}
impl BerylliumIsotopeNumberState {
    pub fn new(be7_m3: [f64; 4], be9_m3: [f64; 4]) -> Result<Self, BeRrError> {
        for v in be7_m3.into_iter().chain(be9_m3) { check_nonnegative(v)?; }
        let state = Self { density_m3: [be7_m3, be9_m3] };
        state.moments()?;
        Ok(state)
    }
    pub fn densities_m3(&self) -> [[f64; 4]; 2] { self.density_m3 }
    pub fn density_m3(&self, isotope: BerylliumIsotope, charge: u8) -> Result<f64, BeRrError> {
        if charge == 0 { return Err(BeRrError::MissingSource); }
        if charge > 4 { return Err(BeRrError::InvalidCharge); }
        let i = match isotope { BerylliumIsotope::Be7 => 0, BerylliumIsotope::Be9 => 1 };
        Ok(self.density_m3[i][charge as usize - 1])
    }
    pub fn moments(&self) -> Result<BerylliumNumberMoments, BeRrError> {
        let nuclei = self.density_m3.map(|r| r.iter().sum::<f64>());
        let baryons = 7.0 * nuclei[0] + 9.0 * nuclei[1];
        let nuclear_charge = 4.0 * (nuclei[0] + nuclei[1]);
        let ionic_charge = self.density_m3.iter().map(|r| r.iter().enumerate()
            .map(|(i, n)| (i + 1) as f64 * n).sum::<f64>()).sum::<f64>();
        if [nuclei[0], nuclei[1], baryons, nuclear_charge, ionic_charge].iter().any(|v| !v.is_finite()) {
            return Err(BeRrError::Arithmetic);
        }
        Ok(BerylliumNumberMoments { isotope_nuclei_m3: nuclei, baryon_number_m3: baryons,
            nuclear_charge_number_m3: nuclear_charge, ionic_charge_number_m3: ionic_charge })
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct BeRrContribution {
    /// [Be7(q=1..4), Be9(q=1..4)], proper number density per second.
    pub species_m3_s: [[f64; 4]; 2],
    /// Sum of both labels' free-electron consumption, to be added exactly once.
    pub electron_m3_s: f64,
    pub recombination_events_m3_s: [[f64; 3]; 2],
    pub policy: IsotopeRatePolicy,
    pub isotope_resolved_coefficients: bool,
    pub scope: &'static str,
}

/// Contribution from q2->q1, q3->q2 and q4->q3 only. All three events move
/// one nucleus between electronic states and consume one free electron.
/// The omitted Be II -> Be I channel is not asserted physically absent.
pub fn be_rr_number_contribution(rates: &BeRrRates, state: &BerylliumIsotopeNumberState,
    electron_density_m3: f64, policy: IsotopeRatePolicy) -> Result<BeRrContribution, BeRrError>
{
    if policy != IsotopeRatePolicy::ElementalElectronicEquality { return Err(BeRrError::MissingSource); }
    check_nonnegative(electron_density_m3)?;
    let mut species = [[0.0; 4]; 2];
    let mut events = [[0.0; 3]; 2];
    let mut electrons = 0.0;
    for i in 0..2 {
        for j in 0..3 {
            let density = state.density_m3[i][j + 1];
            let event = if electron_density_m3 == 0.0 || density == 0.0 { 0.0 } else {
                let value = electron_density_m3 * density * (rates.alpha_cm3_s[j] * 1e-6);
                if !value.is_finite() || value <= 0.0 { return Err(BeRrError::Arithmetic); }
                value
            };
            species[i][j] += event;
            species[i][j + 1] -= event;
            events[i][j] = event;
            electrons -= event;
        }
    }
    if !electrons.is_finite() || species.iter().flatten().any(|v| !v.is_finite()) {
        return Err(BeRrError::Arithmetic);
    }
    Ok(BeRrContribution { species_m3_s: species, electron_m3_s: electrons,
        recombination_events_m3_s: events, policy, isotope_resolved_coefficients: false,
        scope: BE_RR_SCOPE })
}

