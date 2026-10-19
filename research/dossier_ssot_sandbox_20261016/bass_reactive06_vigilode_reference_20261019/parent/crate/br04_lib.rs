//! Additive age-distribution diagnostics over the unchanged BR03 target.
#![forbid(unsafe_code)]
#[path = "ap_lib.rs"]
pub mod br03;
pub use br03::*;

pub mod birth_age_certificate;
