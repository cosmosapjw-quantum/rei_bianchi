//! Exact upstream source slice at validated VigilODE pin a21d573.
//! Only the import boundary is new; the three source files are unchanged.
//! This is not the entire rodas5p-core package or workspace.
#![forbid(unsafe_code)]

#[path = "../../../../vigilode_exact_selected/crates/rodas5p-core/src/error.rs"]
mod error;
pub use error::{CoreError, CoreResult};

#[path = "../../../../vigilode_exact_selected/crates/rodas5p-core/src/damped_moments.rs"]
pub mod damped_moments;
#[path = "../../../../vigilode_exact_selected/crates/rodas5p-core/src/directed.rs"]
pub mod directed;
