// Compile the exact four donor tests against the new compatibility crate.
// The original test source and its MIT license remain unchanged.
extern crate rei_run19_metals as rei_microphysics;
include!("../upstream/rei_bianchi/rust/rei_microphysics/tests/lithium_rates.rs");
