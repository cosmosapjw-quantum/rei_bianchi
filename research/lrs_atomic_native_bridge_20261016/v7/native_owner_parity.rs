//! Exact owner fixed_step parity control on a state constructible by both crates.
//! This control uses HII=.075, HeII=HeIII=0, T=15000 K; the main V7 study
//! uses the shared H/He seed through the isolated v7_seed identity update.
use rei_microphysics::axbi_driver::{Driver,DriverConfig};
fn main()->Result<(),Box<dyn std::error::Error>> {
    let mut cfg=DriverConfig::baseline();
    cfg.initial_x_hii=0.075;
    cfg.initial_temperature_k=15000.0;
    cfg.transport_cells=64; cfg.energy_subdivisions=16; cfg.n_mu=8; cfg.transport_threads=2;
    cfg.max_steps=256; cfg.max_attempts=512; cfg.max_rhs=200000; cfg.max_wall_s=3600.0;
    let (driver,mut state)=Driver::new(cfg)?;
    for _ in 0..16 {driver.fixed_step(&mut state,1e-5/16.0)?;}
    driver.validate(&state,1e-8)?;
    println!("{state:?}");
    Ok(())
}
