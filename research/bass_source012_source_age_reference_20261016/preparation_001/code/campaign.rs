mod native_owner;
mod source_reference;
use native_owner::*;
use rei_microphysics::axbi_driver::{Driver, DriverConfig};
use rei_microphysics::igm_state::IgmGasState;
use std::{fs, io::Write, path::Path};
fn driver(
    q: f64,
    nmu: usize,
    cells: usize,
) -> Result<(Driver, Accepted), Box<dyn std::error::Error>> {
    let mut cfg = DriverConfig::baseline();
    cfg.q_ref = q;
    cfg.n_mu = nmu;
    cfg.energy_subdivisions = 2;
    cfg.transport_cells = cells;
    cfg.background_panels = 256;
    cfg.inactive_hi_split = false;
    cfg.max_rhs = 2_000_000;
    cfg.transport_threads = 1;
    cfg.parallel_jacobian_columns = false;
    let (d, mut s) = Driver::new(cfg)?;
    s.gas = IgmGasState::from_temperature(
        [0.01, 0.01, 0.001],
        d.n_h0_cm3 / s.a.powi(3),
        d.n_he0_cm3 / s.a.powi(3),
        8000.,
    )?;
    Ok((d, empty(s)))
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 4 || args[1] != "source_rhs" {
        return Err("RHS_ONLY: source_rhs -0.1 BIRTH_COUNT (8/16/32); no default campaign/native mode".into());
    }
    let q: f64 = args[2].parse()?;
    let births: usize = args[3].parse()?;
    if q != -0.1 || ![8,16,32].contains(&births) {
        return Err("pinned q=-0.1 and birth_count 8/16/32 only".into());
    }
    source_reference::server(q, births)
}
