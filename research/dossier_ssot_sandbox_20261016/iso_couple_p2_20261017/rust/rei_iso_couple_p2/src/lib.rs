//! Sandbox ISO-COUPLE scope: exact PR150 owner modules, source-off reference,
//! H/He/D fixed-proper-volume CX composition, no production integration.
#![forbid(unsafe_code)]

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ForwardError {
    InvalidInput(&'static str),
}

// Import exact original PR150 HHeModel thresholds and constants, no local approximation.
#[allow(dead_code)]
#[path = "../owner_src/hhe_events.rs"]
pub mod hhe_events;
pub use hhe_events::{HHeModel, HHeState};

#[path = "../owner_src/atomic_provider.rs"]
pub mod atomic_provider;
pub use atomic_provider::{Absorber, AtomicProvider};
#[path = "../owner_src/igm_rates.rs"]
pub mod igm_rates;
#[allow(clippy::nonminimal_bool, clippy::needless_range_loop)]
#[path = "../owner_src/rate_table.rs"]
pub mod rate_table;
#[path = "../owner_src/isotope_state.rs"]
pub mod isotope_state;
pub use isotope_state::{IsotopeNumberState, IsotopeSpecies};
#[path = "../owner_src/deuterium_charge_exchange.rs"]
pub mod deuterium_charge_exchange;
#[allow(clippy::needless_range_loop)]
#[path = "../owner_src/deuterium_thermal_charge_exchange.rs"]
pub mod deuterium_thermal_charge_exchange;
#[path = "../owner_src/deuterium_atomic.rs"]
pub mod deuterium_atomic;
#[path = "../owner_src/deuterium_thermal_coupling.rs"]
pub mod deuterium_thermal_coupling;

pub mod mixture_eos;
pub mod mixture_coupling;

pub mod full_network;

// Exact PR150 H/He source RHS is compiled unchanged, with a small audited
// HHe-only EOS adapter. It is for pure-HHe parity, not for mixed-state execution.
pub mod igm_state;
#[path = "../owner_src/igm_thermal.rs"]
pub mod igm_thermal;
