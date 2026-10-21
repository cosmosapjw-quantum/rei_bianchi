//! RUN19 consumer binding around the unchanged PR150 Li provider/table.
use crate::EvaluatorBinding;
use crate::lithium_rates::{
    IsotopeRatePolicy, LithiumError, LithiumIsotopeNumberRhs,
    LithiumIsotopeNumberState, LithiumProvider, LithiumRateTable, LithiumRates,
    lithium_isotope_number_rhs,
};
use std::sync::Arc;

/// SHA256 of the compiled, unchanged donor module. Parameter row identities are
/// retained independently in provenance/ORIGINAL_SOURCE_MANIFEST.json.
pub const LI_SOURCE_ID: &str = "PR150_LI_SOURCE_10e4db3fa5bd9a4c2dca5c4bfd7fc7fa6a3fa4bbe83862c25b5c4e1a7ba4d629";

#[derive(Clone)]
enum Evaluator {
    Direct(Arc<LithiumProvider>),
    Table { table: Arc<LithiumRateTable>, nodes: usize },
}

/// Construction selects the preserved primary rows once, with no caller-driven
/// source substitution or implicit extension of the source temperature domain.
#[derive(Clone)]
pub struct LithiumBackend {
    evaluator: Evaluator,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct PreparedLithiumRates {
    temperature_k: f64,
    rates: LithiumRates,
    binding: EvaluatorBinding,
}

impl PreparedLithiumRates {
    pub fn temperature_k(&self) -> f64 { self.temperature_k }
    pub fn rates(&self) -> LithiumRates { self.rates }
    pub fn binding(&self) -> EvaluatorBinding { self.binding }
}

impl LithiumBackend {
    pub fn direct() -> Result<Self, LithiumError> {
        Ok(Self { evaluator: Evaluator::Direct(Arc::new(LithiumProvider::from_primary_rows()?)) })
    }

    pub fn tabulated(nodes: usize) -> Result<Self, LithiumError> {
        let table = LithiumRateTable::build(LithiumProvider::from_primary_rows()?, nodes)?;
        Ok(Self { evaluator: Evaluator::Table { table: Arc::new(table), nodes } })
    }

    pub fn binding(&self) -> EvaluatorBinding {
        let (evaluator_id, nodes) = match &self.evaluator {
            Evaluator::Direct(_) => ("PR150_LI_DIRECT_F64_V1", None),
            Evaluator::Table { nodes, .. } => ("PR150_LI_FIXED99_LOGLINEAR_F64_V1", Some(*nodes)),
        };
        EvaluatorBinding { source_id: LI_SOURCE_ID, evaluator_id, nodes }
    }

    pub fn rates(&self, t: f64) -> Result<LithiumRates, LithiumError> {
        match &self.evaluator {
            Evaluator::Direct(p) => p.rates(t),
            Evaluator::Table { table, .. } => table.rates(t),
        }
    }

    pub fn prepare(&self, t: f64) -> Result<PreparedLithiumRates, LithiumError> {
        Ok(PreparedLithiumRates { temperature_k: t, rates: self.rates(t)?, binding: self.binding() })
    }

    pub fn require_prepared(&self, t: f64, prepared: &PreparedLithiumRates)
        -> Result<LithiumRates, LithiumError>
    {
        if t.to_bits() != prepared.temperature_k.to_bits() || self.binding() != prepared.binding {
            return Err(LithiumError::InvalidInput);
        }
        Ok(prepared.rates)
    }

    /// The caller supplies proper density and adds the combined electron source
    /// once. No full gas or energy equation is assembled here.
    pub fn number_contribution(&self, t: f64, prepared: &PreparedLithiumRates,
        state: &LithiumIsotopeNumberState, electron_density_m3: f64,
        policy: IsotopeRatePolicy) -> Result<LithiumIsotopeNumberRhs, LithiumError>
    {
        let rates = self.require_prepared(t, prepared)?;
        lithium_isotope_number_rhs(&rates, state, electron_density_m3, policy)
    }
}

/// Public coefficient order for a later generic interpolation adapter:
/// CI(q=0..3), RR(q=0..3), DR(q=0..3), all in cm^3/s.
pub fn lithium_flat(r: LithiumRates) -> [f64; 12] {
    std::array::from_fn(|i| if i < 4 { r.ci_cm3_s[i] }
        else if i < 8 { r.rr_cm3_s[i - 4] } else { r.dr_cm3_s[i - 8] })
}

