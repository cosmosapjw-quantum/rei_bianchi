//! Sandbox ISO-COUPLE scope: exact PR150 owner modules, source-off reference,
//! H/He/D fixed-proper-volume CX composition, no production integration.
#![forbid(unsafe_code)]

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ForwardError {
    InvalidInput(&'static str),
}

// Only the two physical constants used by DAtomicProvider are reproduced.
// Values exactly equal owner hhe_events::HHeModel::controlled_fixture().
pub struct HHeModel {
    pub kb_erg_k: f64,
    pub ev_erg: f64,
}
impl HHeModel {
    pub fn controlled_fixture() -> Self {
        Self { kb_erg_k: 1.380_649e-16, ev_erg: 1.602_176_634e-12 }
    }
}

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
