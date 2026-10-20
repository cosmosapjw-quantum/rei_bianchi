//! Original-data Li/C/N/O coefficient catalog, separate from the H/He/D owners.
//!
//! This is a coefficient library. It supplies neither isotope-specific atomic
//! structure, populations, nor a thermochemistry evolution or energy ledger.
//! PI fits stop at their published Emax; CI fits enforce the original per-ion
//! electron-temperature range. Sparse RR means capture TOWARD the named ion.
//! Original author coefficient files, hashes and descriptions are retained in
//! the sibling data directory. Rust formulas are an independent f64 expression.

mod generated;

/// The temperature conversion in the original cfit.f, deliberately retained.
pub const VORONOV_EV_PER_K: f64 = 8.617_385e-5;
pub const CM3_TO_M3: f64 = 1e-6;
pub const MB_TO_M2: f64 = 1e-22;
pub const VERIFICATION_SCOPE: &str = "COEFFICIENT_AND_T_TABLE_ONLY_NO_NETWORK_ADMISSION";
pub const MAX_TABLE_NODES: usize = 65_537;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AtomicError {
    UnsupportedIon,
    InvalidInput,
    InvalidSourceCoefficient,
    OutsideTemperatureDomain,
    OutsidePhotoFitDomain,
    MissingRecombination,
    TableBudget,
    ArithmeticFailure,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Ion {
    atomic_number: u8,
    electrons: u8,
}

impl Ion {
    pub fn new(atomic_number: u8, electrons: u8) -> Result<Self, AtomicError> {
        if ![3, 6, 7, 8].contains(&atomic_number) || electrons == 0 || electrons > atomic_number {
            return Err(AtomicError::UnsupportedIon);
        }
        Ok(Self {
            atomic_number,
            electrons,
        })
    }
    pub fn atomic_number(self) -> u8 {
        self.atomic_number
    }
    pub fn electrons(self) -> u8 {
        self.electrons
    }
    pub fn charge(self) -> u8 {
        self.atomic_number - self.electrons
    }
}

#[derive(Clone, Copy, Debug)]
pub struct PhotoFit {
    coeff: [f64; 9],
}

impl PhotoFit {
    /// [Eth/eV, Emax/eV, E0/eV, sigma0/Mb, ya, P, yw, y0, y1].
    pub fn checked(coeff: [f64; 9]) -> Result<Self, AtomicError> {
        if coeff.iter().any(|v| !v.is_finite() || *v < 0.0)
            || coeff[0] == 0.0
            || coeff[1] <= coeff[0]
            || [2, 3, 4, 5].iter().any(|&i| coeff[i] <= 0.0)
        {
            return Err(AtomicError::InvalidSourceCoefficient);
        }
        Ok(Self { coeff })
    }
    pub fn coefficients(self) -> [f64; 9] {
        self.coeff
    }
    pub fn energy_domain_ev(self) -> [f64; 2] {
        [self.coeff[0], self.coeff[1]]
    }
    pub fn cross_section_m2(self, energy_ev: f64) -> Result<f64, AtomicError> {
        if !energy_ev.is_finite() || energy_ev < 0.0 {
            return Err(AtomicError::InvalidInput);
        }
        let [eth, emax, e0, sigma0, ya, p, yw, y0, y1] = self.coeff;
        if energy_ev < eth {
            return Ok(0.0);
        }
        if energy_ev > emax {
            return Err(AtomicError::OutsidePhotoFitDomain);
        }
        let x = energy_ev / e0 - y0;
        let y = x.hypot(y1);
        let shape = (x - 1.0).powi(2) + yw * yw;
        if shape == 0.0 && y > 0.0 {
            return Ok(0.0);
        }
        if y <= 0.0 {
            return Err(AtomicError::ArithmeticFailure);
        }
        let log_sigma = sigma0.ln() + shape.ln() + (0.5 * p - 5.5) * y.ln()
            - p * (y / ya).sqrt().ln_1p()
            + MB_TO_M2.ln();
        positive_exp(log_sigma)
    }
}

#[derive(Clone, Copy, Debug)]
pub struct CiFit {
    coeff: [f64; 7],
}

impl CiFit {
    /// [dE/eV, P, A/(cm3/s), X, K, Tmin/eV, Tmax/keV].
    pub fn checked(coeff: [f64; 7]) -> Result<Self, AtomicError> {
        let [de, p, a, x, k, lo, hi] = coeff;
        if coeff.iter().any(|v| !v.is_finite())
            || de <= 0.0
            || ![0.0, 1.0].contains(&p)
            || a <= 0.0
            || x <= 0.0
            || k < 0.0
            || lo <= 0.0
            || hi * 1000.0 <= lo
        {
            return Err(AtomicError::InvalidSourceCoefficient);
        }
        Ok(Self { coeff })
    }
    pub fn coefficients(self) -> [f64; 7] {
        self.coeff
    }
    pub fn temperature_domain_k(self) -> [f64; 2] {
        [
            self.coeff[5] / VORONOV_EV_PER_K,
            self.coeff[6] * 1000.0 / VORONOV_EV_PER_K,
        ]
    }
    pub fn rate_m3_s(self, temperature_k: f64) -> Result<f64, AtomicError> {
        self.validate_temperature(temperature_k)?;
        positive_exp(self.log_rate(temperature_k))
    }
    fn validate_temperature(self, t: f64) -> Result<(), AtomicError> {
        validate_temperature(t, self.temperature_domain_k())
    }
    fn log_rate(self, t: f64) -> f64 {
        let [de, p, a, x, k, _, _] = self.coeff;
        let u = de / (t * VORONOV_EV_PER_K);
        a.ln() + (p * u.sqrt()).ln_1p() - (x + u).ln() + k * u.ln() - u + CM3_TO_M3.ln()
    }
    /// Exact-real-arithmetic bound: |d² log C/d(log T)²| <= Umax + 5/16.
    pub fn log_curvature_bound(self) -> f64 {
        self.coeff[0] / self.coeff[5] + 5.0 / 16.0
    }
}

#[derive(Clone, Copy, Debug)]
pub struct RrFit {
    coeff: [f64; 4],
}

impl RrFit {
    /// [A/(cm3/s), b, T0/K, T1/K]; recombination TOWARD the associated ion.
    pub fn checked(coeff: [f64; 4]) -> Result<Self, AtomicError> {
        let [a, b, t0, t1] = coeff;
        if coeff.iter().any(|v| !v.is_finite())
            || a <= 0.0
            || !(0.0..=1.0).contains(&b)
            || t0 <= 0.0
            || t1 <= 0.0
        {
            return Err(AtomicError::InvalidSourceCoefficient);
        }
        Ok(Self { coeff })
    }
    pub fn coefficients(self) -> [f64; 4] {
        self.coeff
    }
    pub fn temperature_domain_k(self) -> [f64; 2] {
        [3.0, 1e9]
    }
    pub fn rate_m3_s(self, temperature_k: f64) -> Result<f64, AtomicError> {
        validate_temperature(temperature_k, self.temperature_domain_k())?;
        positive_exp(self.log_rate(temperature_k))
    }
    fn log_rate(self, t: f64) -> f64 {
        let [a, b, t0, t1] = self.coeff;
        let s0 = (t / t0).sqrt();
        let s1 = (t / t1).sqrt();
        a.ln() - s0.ln() - (1.0 - b) * s0.ln_1p() - (1.0 + b) * s1.ln_1p() + CM3_TO_M3.ln()
    }
    /// |d² log alpha/d(log T)²| <= 1/8 for the admitted 0<=b<=1 fits.
    pub fn log_curvature_bound(self) -> f64 {
        1.0 / 8.0
    }
}

fn positive_exp(log_value: f64) -> Result<f64, AtomicError> {
    let value = log_value.exp();
    if value.is_normal() && value > 0.0 {
        Ok(value)
    } else {
        Err(AtomicError::ArithmeticFailure)
    }
}

fn validate_temperature(t: f64, [lo, hi]: [f64; 2]) -> Result<(), AtomicError> {
    if !t.is_finite() || t <= 0.0 {
        return Err(AtomicError::InvalidInput);
    }
    if t < lo || t > hi {
        return Err(AtomicError::OutsideTemperatureDomain);
    }
    Ok(())
}

#[derive(Clone, Copy, Debug)]
pub struct IonFit {
    ion: Ion,
    photo: PhotoFit,
    ci: CiFit,
    rr_toward: Option<RrFit>,
}

impl IonFit {
    pub fn ion(self) -> Ion {
        self.ion
    }
    pub fn photo(self) -> PhotoFit {
        self.photo
    }
    pub fn collisional_ionization(self) -> CiFit {
        self.ci
    }
    pub fn recombination_toward(self) -> Option<RrFit> {
        self.rr_toward
    }
}

pub fn catalog() -> &'static [IonFit] {
    &generated::IONS
}

pub fn lookup(ion: Ion) -> Result<IonFit, AtomicError> {
    catalog()
        .iter()
        .copied()
        .find(|fit| fit.ion == ion)
        .ok_or(AtomicError::UnsupportedIon)
}

/// Immutable positive log-linear rate table. Build once, reuse at runtime.
/// The stored bound addresses interpolation in exact arithmetic. Floating-point
/// implementation error is checked independently, not subsumed into that bound.
#[derive(Clone, Debug)]
pub struct TemperatureTable {
    domain: [f64; 2],
    log_lower: f64,
    inv_step: f64,
    logs: Vec<f64>,
    interpolation_relative_bound: f64,
}

/// One exact positive temperature and its reusable logarithm. Private fields
/// prevent a caller from attaching an unrelated logarithm to a temperature.
#[derive(Clone, Copy, Debug)]
pub struct PreparedTemperature {
    kelvin: f64,
    log_kelvin: f64,
}

impl PreparedTemperature {
    pub fn new(kelvin: f64) -> Result<Self, AtomicError> {
        if !kelvin.is_finite() || kelvin <= 0.0 {
            return Err(AtomicError::InvalidInput);
        }
        Ok(Self {
            kelvin,
            log_kelvin: kelvin.ln(),
        })
    }
    pub fn kelvin(self) -> f64 {
        self.kelvin
    }
}

impl TemperatureTable {
    pub fn from_ci(fit: CiFit, target_relative_error: f64) -> Result<Self, AtomicError> {
        Self::build(
            fit.temperature_domain_k(),
            fit.log_curvature_bound(),
            target_relative_error,
            |t| fit.log_rate(t),
        )
    }
    pub fn from_rr(fit: RrFit, target_relative_error: f64) -> Result<Self, AtomicError> {
        Self::build(
            fit.temperature_domain_k(),
            fit.log_curvature_bound(),
            target_relative_error,
            |t| fit.log_rate(t),
        )
    }
    fn build(
        domain: [f64; 2],
        curvature: f64,
        tolerance: f64,
        log_rate: impl Fn(f64) -> f64,
    ) -> Result<Self, AtomicError> {
        if !tolerance.is_finite() || tolerance <= 0.0 || tolerance > 0.1 {
            return Err(AtomicError::InvalidInput);
        }
        let span = (domain[1] / domain[0]).ln();
        let max_step = (8.0 * tolerance.ln_1p() / curvature).sqrt();
        let intervals = (span / max_step).ceil();
        if !intervals.is_finite() || intervals >= MAX_TABLE_NODES as f64 {
            return Err(AtomicError::TableBudget);
        }
        let intervals = (intervals as usize).max(1);
        let step = span / intervals as f64;
        let log_lower = domain[0].ln();
        let logs = (0..=intervals)
            .map(|i| {
                let t = if i == 0 {
                    domain[0]
                } else if i == intervals {
                    domain[1]
                } else {
                    (log_lower + i as f64 * step).exp()
                };
                log_rate(t)
            })
            .collect::<Vec<_>>();
        if logs.iter().any(|v| !v.is_finite()) {
            return Err(AtomicError::ArithmeticFailure);
        }
        Ok(Self {
            domain,
            log_lower,
            inv_step: 1.0 / step,
            logs,
            interpolation_relative_bound: (curvature * step * step / 8.0).exp_m1(),
        })
    }
    pub fn rate_m3_s(&self, t: f64) -> Result<f64, AtomicError> {
        self.rate_prepared(PreparedTemperature::new(t)?)
    }
    /// Reuse one logarithm across several independently valid ion tables.
    pub fn rate_prepared(&self, t: PreparedTemperature) -> Result<f64, AtomicError> {
        validate_temperature(t.kelvin, self.domain)?;
        let x = (t.log_kelvin - self.log_lower) * self.inv_step;
        let i = (x.floor() as usize).min(self.logs.len() - 2);
        let theta = (x - i as f64).clamp(0.0, 1.0);
        positive_exp(self.logs[i] + theta * (self.logs[i + 1] - self.logs[i]))
    }
    pub fn nodes(&self) -> usize {
        self.logs.len()
    }
    pub fn storage_bytes(&self) -> usize {
        self.logs.len() * std::mem::size_of::<f64>()
    }
    pub fn temperature_domain_k(&self) -> [f64; 2] {
        self.domain
    }
    pub fn interpolation_relative_bound(&self) -> f64 {
        self.interpolation_relative_bound
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pinned_catalog_coverage_and_coefficients_are_valid() {
        assert_eq!(catalog().len(), 24);
        assert_eq!(
            catalog().iter().filter(|r| r.rr_toward.is_some()).count(),
            12
        );
        for fit in catalog() {
            assert!(PhotoFit::checked(fit.photo.coeff).is_ok());
            assert!(CiFit::checked(fit.ci.coeff).is_ok());
            if let Some(rr) = fit.rr_toward {
                assert!(RrFit::checked(rr.coeff).is_ok());
            }
        }
        assert!(Ion::new(6, 0).is_err());
        assert!(Ion::new(2, 1).is_err());
        assert!(Ion::new(6, 7).is_err());
    }

    #[test]
    fn source_data_and_invalid_runtime_inputs_are_rejected() {
        let fit = catalog()[0];
        let mut c = fit.ci.coeff;
        c[2] = -1.0;
        assert_eq!(
            CiFit::checked(c).unwrap_err(),
            AtomicError::InvalidSourceCoefficient
        );
        let mut p = fit.photo.coeff;
        p[3] = f64::NAN;
        assert_eq!(
            PhotoFit::checked(p).unwrap_err(),
            AtomicError::InvalidSourceCoefficient
        );
        let mut r = fit.rr_toward.unwrap().coeff;
        r[1] = 1.1;
        assert_eq!(
            RrFit::checked(r).unwrap_err(),
            AtomicError::InvalidSourceCoefficient
        );
        for t in [f64::NAN, f64::INFINITY, 0.0, -1.0] {
            assert_eq!(fit.ci.rate_m3_s(t), Err(AtomicError::InvalidInput));
        }
        for e in [f64::NAN, f64::INFINITY, -1.0] {
            assert_eq!(
                fit.photo.cross_section_m2(e),
                Err(AtomicError::InvalidInput)
            );
        }
    }

    #[test]
    fn pi_thresholds_and_maximum_energy_are_explicit() {
        for fit in catalog() {
            let [lo, hi] = fit.photo.energy_domain_ev();
            assert_eq!(fit.photo.cross_section_m2(0.0), Ok(0.0));
            assert_eq!(fit.photo.cross_section_m2(lo.next_down()), Ok(0.0));
            assert!(fit.photo.cross_section_m2(lo).unwrap() >= 0.0);
            assert!(fit.photo.cross_section_m2(hi).unwrap() >= 0.0);
            assert_eq!(
                fit.photo.cross_section_m2(hi.next_up()),
                Err(AtomicError::OutsidePhotoFitDomain)
            );
        }
    }

    #[test]
    fn ci_domains_follow_ev_kev_columns_and_original_conversion() {
        for fit in catalog() {
            let [lo, hi] = fit.ci.temperature_domain_k();
            assert!(fit.ci.rate_m3_s(lo).unwrap() > 0.0);
            assert!(fit.ci.rate_m3_s(hi).unwrap() > 0.0);
            assert_eq!(
                fit.ci.rate_m3_s(lo.next_down()),
                Err(AtomicError::OutsideTemperatureDomain)
            );
            assert_eq!(
                fit.ci.rate_m3_s(hi.next_up()),
                Err(AtomicError::OutsideTemperatureDomain)
            );
            assert!(fit.ci.coeff[0] / fit.ci.coeff[5] < 80.0);
        }
    }

    #[test]
    fn all_ci_tables_respect_curvature_bound_on_offset_grid() {
        for fit in catalog() {
            let table = TemperatureTable::from_ci(fit.ci, 1e-4).unwrap();
            let [lo, hi] = fit.ci.temperature_domain_k();
            let log_span = (hi / lo).ln();
            for i in 0..1024 {
                let t = lo * (log_span * (i as f64 + 0.371) / 1024.0).exp();
                let direct = fit.ci.rate_m3_s(t).unwrap();
                let interp = table.rate_m3_s(t).unwrap();
                let error = (interp / direct - 1.0).abs();
                assert!(
                    error <= table.interpolation_relative_bound() + 2e-13,
                    "{error}"
                );
                assert!(interp > 0.0);
            }
        }
    }

    #[test]
    fn rr_sparse_labels_and_tables_are_explicit() {
        assert!(lookup(Ion::new(6, 6).unwrap()).unwrap().rr_toward.is_none());
        for fit in catalog() {
            if let Some(rr) = fit.rr_toward {
                assert!(fit.ion.electrons <= 3);
                let table = TemperatureTable::from_rr(rr, 1e-5).unwrap();
                for i in 0..257 {
                    let t = 3.0 * ((1e9_f64 / 3.0).ln() * (i as f64 + 0.123) / 258.0).exp();
                    assert!(
                        (table.rate_m3_s(t).unwrap() / rr.rate_m3_s(t).unwrap() - 1.0).abs()
                            <= table.interpolation_relative_bound() + 2e-13
                    );
                }
            }
        }
    }

    #[test]
    fn impossible_table_work_is_classified_as_budget() {
        let ci = catalog()[0].ci;
        assert_eq!(
            TemperatureTable::from_ci(ci, 1e-30).unwrap_err(),
            AtomicError::TableBudget
        );
        assert_eq!(
            TemperatureTable::from_ci(ci, -1.0).unwrap_err(),
            AtomicError::InvalidInput
        );
        let table = TemperatureTable::from_ci(ci, 1e-4).unwrap();
        assert_eq!(
            table.rate_m3_s(1.0),
            Err(AtomicError::OutsideTemperatureDomain)
        );
    }

    #[test]
    fn prepared_temperature_reuses_logarithm_without_changing_result() {
        for fit in catalog() {
            let table = TemperatureTable::from_ci(fit.ci, 1e-4).unwrap();
            let [lo, hi] = table.temperature_domain_k();
            for t in [lo, (lo * hi).sqrt(), hi] {
                assert_eq!(
                    table.rate_m3_s(t),
                    table.rate_prepared(PreparedTemperature::new(t).unwrap())
                );
            }
        }
        assert_eq!(
            PreparedTemperature::new(f64::NAN).unwrap_err(),
            AtomicError::InvalidInput
        );
    }
}
