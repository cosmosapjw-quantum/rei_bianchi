use rei_microphysics::axbi_driver::{Driver, DriverConfig};
use std::{env, fs, path::Path};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = env::args().collect();
    if args.len() != 3 {
        return Err("usage: export_starting_state CONFIG CHECKPOINT".into());
    }
    let config = DriverConfig::read(&fs::read_to_string(&args[1])?)?;
    let (driver, _) = Driver::new(config)?;
    let state = driver.read_checkpoint(Path::new(&args[2]))?;
    println!("{state:?}");
    Ok(())
}
