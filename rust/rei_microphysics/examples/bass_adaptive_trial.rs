//! Fresh source009 BASS adaptive execution; launch authority is separate.
use rei_microphysics::axbi_bass_background::{BassBackground, BassSourceIdentity};
use rei_microphysics::axbi_driver::run_bass_fresh;
use std::{env, fs, path::Path};
pub fn execute_args(args: &[String]) -> Result<(), Box<dyn std::error::Error>> {
    if args.iter().any(|arg| arg == "--resume") {
        return Err("BASS_ADAPTIVE_FRESH_ONLY: resume/checkpoint adoption is unsupported".into());
    }
    if args.len() != 7 {
        return Err("usage: bass_adaptive_trial CSV PRODUCER_JSON CONFIG CASE OUTPUT_DIR EPOCH (fresh only)".into());
    }
    let identity = BassSourceIdentity {
        producer_commit: "3c39bbbf46b6663e7c40277e194fd0ef48118472".into(),
        source_csv_sha256: "5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133"
            .into(),
        source_manifest_sha256: "98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed"
            .into(),
        case: args[4].clone(),
        grid_points: 121,
    };
    let background =
        BassBackground::from_files(Path::new(&args[1]), Path::new(&args[2]), identity)?;
    let config = fs::read_to_string(&args[3])?;
    run_bass_fresh(&config, Path::new(&args[5]), &args[4], background, &args[6])?;
    Ok(())
}
#[allow(dead_code)]
fn main() {
    if let Err(error) = execute_args(&env::args().collect::<Vec<_>>()) {
        eprintln!("BASS_ADAPTIVE_ERROR: {error:?}");
        std::process::exit(2);
    }
}
