//! Source-backed, elemental ground-parent carbon CI/RR/DR coefficients.
//!
//! Voronov (1997) and Badnell RR/DR parameter rows are retained verbatim in
//! the research unit. This module supplies number kinetics only. It supplies
//! no isotope-native rates, photo donor, thermal closure, or abundances.

use crate::rate_table::LogRateGrid;
use crate::ForwardError;

pub const MODEL_ID: &str = "ELEMENTAL_C_GROUND_CI_RR_DR_V1";
/// Literal used by the official Voronov cfit.f implementation, eV/K.
pub const VORONOV_KB_EV_K: f64 = 8.617385e-5;
pub const COMMON_MIN_K: f64 = 20.0 / VORONOV_KB_EV_K;
pub const COMMON_MAX_K: f64 = 1e7;
const RR_ROWS: &str = include_str!("../../../research/flrw_rate_table_acceleration_20261016/data/badnell_carbon_rr_rows.txt");
const DR_ROWS: &str = include_str!("../../../research/flrw_rate_table_acceleration_20261016/data/badnell_carbon_dr_rows.txt");
const CI_ROWS: &str = include_str!("../../../research/flrw_rate_table_acceleration_20261016/data/voronov_carbon_ci_rows.txt");

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CarbonIdentity {
    ElementalGroundParent,
    /// No mass-number-specific coefficient authority is supplied by these tables.
    Isotope { mass_number: u16 },
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CarbonError {
    MissingIsotopeNative,
    InvalidCharge,
    InvalidInput,
    TemperatureDomain,
    SourceData,
    Arithmetic,
    Table,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CarbonProcess { CollisionalIonization, RadiativeRecombination, DielectronicRecombination }
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct CarbonChannelRecord {
    pub initial_charge: usize,
    pub final_charge: usize,
    pub process: CarbonProcess,
    pub minimum_k: f64,
    pub maximum_k: f64,
    pub structural_zero: bool,
    pub source: &'static str,
    pub units: &'static str,
    pub domain_description: &'static str,
}
#[derive(Clone, Debug)]
struct RrFit { a: f64, b: f64, t0: f64, t1: f64, c: f64, t2: f64 }
#[derive(Clone, Debug)]
struct DrFit { c: Vec<f64>, e: Vec<f64> }
#[derive(Clone, Debug)]
struct CiFit { energy: f64, p: f64, a: f64, x: f64, k: f64, minimum_ev: f64, maximum_kev: f64 }
#[derive(Clone, Debug)]
pub struct CarbonProvider {
    rr: [Option<RrFit>; 7],
    dr: [Option<DrFit>; 7],
    ci: [Option<CiFit>; 7],
}
fn numbers(line: &str) -> Vec<f64> {
    line.split_whitespace().filter_map(|x| x.parse::<f64>().ok()).collect()
}
fn valid_rate(value: f64) -> Result<f64, CarbonError> {
    if value.is_finite() && value >= 0.0 { Ok(value) } else { Err(CarbonError::Arithmetic) }
}
fn nonnegative(value: f64) -> Result<f64, CarbonError> {
    if value.is_finite() && value >= 0.0 { Ok(value) } else { Err(CarbonError::InvalidInput) }
}
fn checked_product(a: f64, b: f64, c: f64) -> Result<f64, CarbonError> {
    nonnegative(a)?; nonnegative(b)?; nonnegative(c)?;
    if a == 0.0 || b == 0.0 || c == 0.0 { return Ok(0.0); }
    let v = a * b * c;
    if v.is_finite() && v > 0.0 { Ok(v) } else { Err(CarbonError::Arithmetic) }
}
impl CarbonProvider {
    /// Parse the preserved primary parameter rows once; no coefficient is fit here.
    pub fn from_primary_rows(identity: CarbonIdentity) -> Result<Self, CarbonError> {
        if identity != CarbonIdentity::ElementalGroundParent { return Err(CarbonError::MissingIsotopeNative); }
        let mut provider = Self { rr: std::array::from_fn(|_| None), dr: std::array::from_fn(|_| None), ci: std::array::from_fn(|_| None) };
        for line in RR_ROWS.lines() {
            let v = numbers(line);
            if !(v.len() == 8 || v.len() == 10) || v[0] != 6.0 || v[2] != 1.0 { return Err(CarbonError::SourceData); }
            let n = v[1] as usize;
            if n > 5 || v[1] != n as f64 { return Err(CarbonError::SourceData); }
            let q = 6 - n;
            if provider.rr[q].is_some() { return Err(CarbonError::SourceData); }
            provider.rr[q] = Some(RrFit { a:v[4], b:v[5], t0:v[6], t1:v[7], c:if v.len()==10 {v[8]} else {0.0}, t2:if v.len()==10 {v[9]} else {0.0} });
        }
        let rows: Vec<Vec<f64>> = DR_ROWS.lines().map(numbers).collect();
        if rows.len() != 10 { return Err(CarbonError::SourceData); }
        for i in 0..5 {
            let (c,e) = (&rows[i], &rows[i+5]);
            if c.len() < 5 || c.len()!=e.len() || c[..4]!=e[..4] || c[0]!=6.0 || c[2]!=1.0 { return Err(CarbonError::SourceData); }
            let n=c[1] as usize;
            if !(1..=5).contains(&n) || c[1]!=n as f64 { return Err(CarbonError::SourceData); }
            let q=6-n;
            if provider.dr[q].is_some() { return Err(CarbonError::SourceData); }
            // Individual DR amplitudes are signed source parameters, not rates.
            provider.dr[q]=Some(DrFit { c:c[4..].to_vec(), e:e[4..].to_vec() });
        }
        for line in CI_ROWS.lines() {
            let v=numbers(line);
            if v.len()!=9 || v[0]!=6.0 { return Err(CarbonError::SourceData); }
            let n=v[1] as usize;
            if !(1..=6).contains(&n) || v[1]!=n as f64 { return Err(CarbonError::SourceData); }
            let q=6-n;
            if provider.ci[q].is_some() { return Err(CarbonError::SourceData); }
            provider.ci[q]=Some(CiFit { energy:v[2], p:v[3], a:v[4], x:v[5], k:v[6], minimum_ev:v[7], maximum_kev:v[8] });
        }
        if provider.rr[1..].iter().any(Option::is_none) || provider.dr[1..6].iter().any(Option::is_none) || provider.ci[..6].iter().any(Option::is_none) { return Err(CarbonError::SourceData); }
        Ok(provider)
    }
    pub fn record(&self, process: CarbonProcess, q: usize) -> Result<CarbonChannelRecord, CarbonError> {
        use CarbonProcess::*;
        if q>6 { return Err(CarbonError::InvalidCharge); }
        let structural_zero = matches!((process,q),(CollisionalIonization,6)|(RadiativeRecombination,0)|(DielectronicRecombination,0|6));
        let (minimum_k,maximum_k,source,domain_description)=if structural_zero {
            (0.0,f64::INFINITY,"adjacent-chain structural boundary / bare-ion DR absence","structural absence for all finite T>0")
        } else if process==CollisionalIonization {
            let p=self.ci[q].as_ref().ok_or(CarbonError::SourceData)?;
            (p.minimum_ev/VORONOV_KB_EV_K,1000.0*p.maximum_kev/VORONOV_KB_EV_K,"Voronov 1997 official cfit.dat/cfit.f","per-row source Tmin(eV)..Tmax(keV)")
        } else {
            (10.0*(q*q) as f64,1e7*(q*q) as f64,if process==RadiativeRecombination {"Badnell RR 20230511 ground M=1"} else {"Badnell DR 20230512 ground M=1"},"conservative standard ADAS tabulation range; not universal fit-accuracy bound")
        };
        Ok(CarbonChannelRecord { initial_charge:q, final_charge:if process==CollisionalIonization { (q+1).min(6) } else { q.saturating_sub(1) }, process, minimum_k, maximum_k, structural_zero, source, units:"cm^3 s^-1", domain_description })
    }
    /// Each channel retains its own source domain, including cold-valid RR.
    pub fn coefficient_cm3_s(&self, process: CarbonProcess, q: usize, t: f64) -> Result<f64, CarbonError> {
        if !t.is_finite() || t<=0.0 { return Err(CarbonError::InvalidInput); }
        let record=self.record(process,q)?;
        if record.structural_zero { return Ok(0.0); }
        if t<record.minimum_k || t>record.maximum_k { return Err(CarbonError::TemperatureDomain); }
        use CarbonProcess::*;
        let rate=match process {
            CollisionalIonization => { let p=self.ci[q].as_ref().ok_or(CarbonError::SourceData)?; let u=p.energy/(VORONOV_KB_EV_K*t); p.a*(1.0+p.p*u.sqrt())/(p.x+u)*u.powf(p.k)*(-u).exp() },
            RadiativeRecombination => { let p=self.rr[q].as_ref().ok_or(CarbonError::SourceData)?; let b=p.b+p.c*(-p.t2/t).exp(); let x=(t/p.t0).sqrt(); let y=(t/p.t1).sqrt(); p.a/(x*(1.0+x).powf(1.0-b)*(1.0+y).powf(1.0+b)) },
            DielectronicRecombination => { let p=self.dr[q].as_ref().ok_or(CarbonError::SourceData)?; p.c.iter().zip(&p.e).map(|(c,e)|c*(-e/t).exp()).sum::<f64>()/t.powf(1.5) },
        };
        valid_rate(rate)
    }
    /// Complete bundle uses the intersection, without broadening any source.
    pub fn rates(&self,t:f64)->Result<CarbonRates,CarbonError> {
        if !t.is_finite() || !(COMMON_MIN_K..=COMMON_MAX_K).contains(&t) { return Err(CarbonError::TemperatureDomain); }
        let mut flat=[0.0;21];
        for (i,p) in [CarbonProcess::CollisionalIonization,CarbonProcess::RadiativeRecombination,CarbonProcess::DielectronicRecombination].iter().enumerate() {
            for q in 0..7 { flat[7*i+q]=self.coefficient_cm3_s(*p,q,t)?; }
        }
        Ok(CarbonRates::from_flat(t,flat))
    }
}
#[derive(Clone,Copy,Debug,PartialEq)]
pub struct CarbonRates {
    pub temperature_k:f64,
    pub ci_cm3_s:[f64;7],
    pub rr_cm3_s:[f64;7],
    pub dr_cm3_s:[f64;7],
}
impl CarbonRates {
    fn from_flat(t:f64,v:[f64;21])->Self { Self {temperature_k:t,ci_cm3_s:std::array::from_fn(|q|v[q]),rr_cm3_s:std::array::from_fn(|q|v[q+7]),dr_cm3_s:std::array::from_fn(|q|v[q+14])} }
    fn flat(self)->[f64;21] { std::array::from_fn(|i|if i<7 {self.ci_cm3_s[i]} else if i<14 {self.rr_cm3_s[i-7]} else {self.dr_cm3_s[i-14]}) }
}
/// Same immutable, shared-log-temperature mechanism as the H/He provider.
pub struct CarbonRateTable { provider:CarbonProvider, grid:LogRateGrid<21> }
impl CarbonRateTable {
    pub fn build(provider:CarbonProvider,nodes:usize)->Result<Self,CarbonError> {
        let grid=LogRateGrid::build(COMMON_MIN_K,COMMON_MAX_K,nodes,|t|provider.rates(t).map(CarbonRates::flat).map_err(|_|ForwardError::InvalidInput("CARBON_RATE_DOMAIN")),|_,_|false,|i,_,_|matches!(i,6|7|14|20)).map_err(|_|CarbonError::Table)?;
        Ok(Self {provider,grid})
    }
    pub fn rates(&self,t:f64)->Result<CarbonRates,CarbonError> {
        if !t.is_finite() || !(COMMON_MIN_K..=COMMON_MAX_K).contains(&t) { return Err(CarbonError::TemperatureDomain); }
        let v=self.grid.evaluate(t,|t|self.provider.rates(t).map(CarbonRates::flat).map_err(|_|ForwardError::InvalidInput("CARBON_RATE_DOMAIN"))).map_err(|_|CarbonError::Table)?;
        Ok(CarbonRates::from_flat(t,v))
    }
    pub fn batch(&self,temperatures:&[f64])->Result<Vec<CarbonRates>,CarbonError> { temperatures.iter().map(|&t|self.rates(t)).collect() }
}
#[derive(Clone,Copy,Debug,PartialEq)]
pub struct CarbonNumberRhs {
    pub species_m3_s:[f64;7],
    /// Supply this contribution once to the caller's global electron equation.
    pub electron_m3_s:f64,
    pub ionization_events_m3_s:[f64;7],
    pub recombination_events_m3_s:[f64;7],
}
/// Proper densities, prescribed free-electron density, and one rate bundle.
/// CI/RR/DR events own only number changes here; energy closure is absent.
pub fn carbon_number_rhs(rates:&CarbonRates,density_m3:[f64;7],electron_density_m3:f64)->Result<CarbonNumberRhs,CarbonError> {
    nonnegative(electron_density_m3)?;
    let mut ci=[0.0;7]; let mut re=[0.0;7];
    for q in 0..7 {
        nonnegative(density_m3[q])?;
        ci[q]=checked_product(electron_density_m3,density_m3[q],rates.ci_cm3_s[q]*1e-6)?;
        re[q]=checked_product(electron_density_m3,density_m3[q],(rates.rr_cm3_s[q]+rates.dr_cm3_s[q])*1e-6)?;
    }
    if ci[6]!=0.0 || re[0]!=0.0 {return Err(CarbonError::InvalidInput);}
    let mut species=[0.0;7]; let mut electrons=0.0;
    for q in 0..6 {
        let net=ci[q]-re[q+1];
        species[q]-=net; species[q+1]+=net; electrons+=net;
    }
    if !electrons.is_finite() || species.iter().any(|x|!x.is_finite()) {return Err(CarbonError::Arithmetic);}
    Ok(CarbonNumberRhs {species_m3_s:species,electron_m3_s:electrons,ionization_events_m3_s:ci,recombination_events_m3_s:re})
}
