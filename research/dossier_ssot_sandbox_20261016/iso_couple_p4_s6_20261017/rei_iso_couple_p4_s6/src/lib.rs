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
#[path = "../owner_src/isotope_state.rs"]
pub mod isotope_state;
#[allow(clippy::nonminimal_bool, clippy::needless_range_loop)]
#[path = "../owner_src/rate_table.rs"]
pub mod rate_table;
pub use isotope_state::{IsotopeNumberState, IsotopeSpecies};
#[path = "../owner_src/deuterium_atomic.rs"]
pub mod deuterium_atomic;
#[path = "../owner_src/deuterium_charge_exchange.rs"]
pub mod deuterium_charge_exchange;
#[allow(clippy::needless_range_loop)]
#[path = "../owner_src/deuterium_thermal_charge_exchange.rs"]
pub mod deuterium_thermal_charge_exchange;
#[path = "../owner_src/deuterium_thermal_coupling.rs"]
pub mod deuterium_thermal_coupling;

pub mod mixture_coupling;
pub mod mixture_eos;

pub mod full_network;

// Exact PR150 H/He source RHS is compiled unchanged, with a small audited
// HHe-only EOS adapter. It is for pure-HHe parity, not for mixed-state execution.
pub mod igm_state;
#[path = "../owner_src/igm_thermal.rs"]
pub mod igm_thermal;

// Immutable PR150 providers. Existing owner_src files are never formatted/edited.
// Exact source constant from the PR150 owner crate (comoving Mpc in centimeters).
pub const MPC_CM: f64 = 3.085_677_581_491_367e24;
#[path = "../owner_src/axbi_sources.rs"]
pub mod axbi_sources;
#[path = "../owner_src/bianchi_i.rs"]
pub mod bianchi_i;
pub mod positive_age;
pub mod source_age;

// P4/S2 opt-in exact constant-slab newborn source exposure, P3 untouched.
pub mod positive_birth_clock;

// P4/S3 native positive retarded-age and threshold-split spectral comparator.
pub mod positive_spectral;
pub mod retarded_transport;

// P4/S4 additive exact threshold roots and cached geometry execution.
pub mod threshold_roots;
pub mod retarded_transport_threshold;

// P4/S5 additive, error-budgeted opt-in nonzero source-age remainder.
pub mod age_remainder;

// P4/S6 opt-in reflection-orbit computational reuse.
pub mod reflection_pool;
