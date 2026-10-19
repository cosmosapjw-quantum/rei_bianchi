//! Recovery R1 command wrapper. The previous wrapper bytes were not recovered.
use rei_br06_reference::{
    Error, Result,
    fixture::NativeFixture,
    reference::{self, BirthMethod, PathControls, RunControls},
    vigilode_native,
};
use std::{env, path::Path};

fn integer(text: &str) -> Result<usize> {
    text.parse().map_err(|_| Error::InvalidInput("cli_integer"))
}

fn execute(args: &[String]) -> Result<()> {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("..");
    match args.get(1).map(String::as_str) {
        Some("fixture" | "moments") if args.len() == 5 && args[3] == "export" => {
            let fixture = NativeFixture::load(&root, &args[2])?;
            let directory = Path::new(&args[4]);
            if args[1] == "fixture" {
                fixture.export(directory)?;
                println!("BR06_FIXTURE_COMPLETE case={}", fixture.case);
            } else {
                vigilode_native::export(&fixture, directory)?;
                println!("BR06_MOMENTS_COMPLETE case={} rules=48", fixture.case);
            }
            Ok(())
        }
        Some("run") if args.len() == 12 => {
            let birth = match args[3].as_str() {
                "fitted" => BirthMethod::Fitted,
                "gauss" => BirthMethod::Gauss,
                _ => return Err(Error::InvalidInput("cli_birth_method")),
            };
            let split_spectrum = match args[9].as_str() {
                "original" => false,
                "split" => true,
                _ => return Err(Error::InvalidInput("cli_spectrum")),
            };
            let controls = RunControls {
                birth,
                refinement: integer(&args[4])?,
                birth_degree: integer(&args[5])?,
                path: PathControls {
                    slabs: integer(&args[6])?,
                    opacity_degree: integer(&args[7])?,
                    event_degree: integer(&args[8])?,
                    ..PathControls::default()
                },
                split_spectrum,
                template_limit: integer(&args[10])?,
                source_scale: 1.0,
            };
            let fixture = NativeFixture::load(&root, &args[2])?;
            let totals = reference::run(&fixture, controls, Path::new(&args[11]))?;
            println!(
                "BR06_COMPLETE cohorts={} survivor={:.17e} number_residual={:.17e} energy_residual_j={:.17e}",
                totals.cohorts,
                totals.surviving,
                totals.number_residual(),
                totals.energy_residual(),
            );
            Ok(())
        }
        _ => Err(Error::InvalidInput(
            "usage: br06_reference fixture|moments CASE export OUT; or run CASE fitted|gauss refinement birth_degree path_slabs opacity_degree event_degree original|split template_limit OUT",
        )),
    }
}

fn main() {
    if let Err(error) = execute(&env::args().collect::<Vec<_>>()) {
        eprintln!("{error}");
        std::process::exit(2);
    }
}
