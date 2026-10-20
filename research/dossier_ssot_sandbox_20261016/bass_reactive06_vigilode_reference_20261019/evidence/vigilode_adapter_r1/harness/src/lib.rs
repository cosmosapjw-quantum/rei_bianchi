//! Lightweight recovery harness with a separate exact-kernel dependency.
//! The full VigilODE workspace is outside this package's verification scope.
pub use rodas5p_core::{damped_moments, directed};

#[path = "../../vigilode_moments.rs"]
pub mod adapter;
