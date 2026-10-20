//! Optional trace electronic coefficients, independent of the original 13-state
//! gas registry. PR150 lithium is compiled byte-for-byte from its original path.
//! Beryllium supplies selected total radiative-recombination contributions only.
//! Density, abundance, photon fields, thermal power and nuclear evolution belong
//! to callers and are never inferred from these temperature-only providers.
#![forbid(unsafe_code)]

pub use rei_iso_couple_reference::ForwardError;

/// Exact fixed99 grid implementation, shared rather than reimplemented.
pub mod rate_table {
    pub use rei_iso_couple_reference::rate_table::LogRateGrid;
}

#[path = "../upstream/rei_bianchi/rust/rei_microphysics/src/lithium_rates.rs"]
pub mod lithium_rates;

pub mod beryllium_rr;
pub mod lithium_backend;

/// A prepared coefficient bundle retains the selected source and evaluator.
/// Table size belongs to its evaluator identity; the source is fixed at build.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct EvaluatorBinding {
    pub source_id: &'static str,
    pub evaluator_id: &'static str,
    pub nodes: Option<usize>,
}

