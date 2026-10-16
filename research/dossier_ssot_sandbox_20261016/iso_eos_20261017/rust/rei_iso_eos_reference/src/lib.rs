//! ISO-EOS bounded reference, not native solver integration.
//! Owner snapshots are byte-identical to frozen PR #150 owner source.
#![forbid(unsafe_code)]

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ForwardError {
    InvalidInput(&'static str),
}

#[path = "../owner_src/deuterium_charge_exchange.rs"]
pub mod deuterium_charge_exchange;
// Frozen owner source is byte-identical and has one inherited rust1.94 lint.
#[allow(clippy::needless_range_loop)]
#[path = "../owner_src/deuterium_thermal_charge_exchange.rs"]
pub mod deuterium_thermal_charge_exchange;
#[path = "../owner_src/isotope_state.rs"]
pub mod isotope_state;

pub use isotope_state::{IsotopeNumberState, IsotopeSpecies};
pub mod mixture_eos;
