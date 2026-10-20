//! BRPERF01 opt-in exact work reuse. No physical owner or solver is replaced.
#![forbid(unsafe_code)]

pub use rei_br06_reference::{Error, Result};
pub mod batch;
pub mod fingerprint;
pub mod kernel;

/// Explicitly opt in to the cached kernel. Default preserves the original call.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum Mode {
    #[default]
    Baseline,
    Cached,
}

pub fn fixture_root() -> std::path::PathBuf {
    std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../repo/research/dossier_ssot_sandbox_20261016/bass_reactive06_vigilode_reference_20261019")
}
