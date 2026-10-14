//! Read a frozen key=value config and run an explicitly bound local case.
use std::{fs, path::PathBuf};
fn main() {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    let mut config = None;
    let mut output = None;
    let mut case = None;
    let mut resume = false;
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--resume" => resume = true,
            "--config" | "--output" | "--case" => {
                let key = &args[i];
                i += 1;
                let value = args
                    .get(i)
                    .unwrap_or_else(|| {
                        eprintln!("missing {key} value");
                        std::process::exit(2)
                    })
                    .clone();
                match key.as_str() {
                    "--config" => config = Some(value),
                    "--output" => output = Some(value),
                    _ => case = Some(value),
                }
            }
            _ => {
                eprintln!("unknown argument {}", args[i]);
                std::process::exit(2)
            }
        }
        i += 1;
    }
    let (Some(config), Some(output), Some(case)) = (config, output, case) else {
        eprintln!("usage: axbi_reionization --config PATH --output NEW_DIR --case ID [--resume]");
        std::process::exit(2)
    };
    let result = fs::read_to_string(&config)
        .map_err(|e| format!("{e:?}"))
        .and_then(|text| {
            rei_microphysics::axbi_driver::run(&text, &PathBuf::from(output), &case, resume)
                .map_err(|e| format!("{e:?}"))
        });
    if let Err(e) = result {
        eprintln!("{e}");
        std::process::exit(1)
    }
}
