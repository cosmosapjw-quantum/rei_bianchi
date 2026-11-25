use rei_microphysics::axbi_covariant_driver::{Driver, DriverConfig};
use std::{fs, path::Path};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let a = std::env::args().skip(1).collect::<Vec<_>>();
    let c = DriverConfig::read(&fs::read_to_string(&a[0])?)?;
    let (d, _) = Driver::new(c)?;
    let s = d.read_checkpoint(Path::new(&a[1]))?;
    println!(
        "z={:.17e} accepted={} h_next={:.17e}",
        1. / s.a - 1.,
        s.accepted,
        s.next_dln_a
    );
    for h in [
        1.28e-3, 3.2e-4, 8e-5, 4e-5, 2e-5, 1e-5, 5e-6, 2.5e-6, 1.25e-6,
    ] {
        match d.probe_step(&s, h) {
            Ok(p) => {
                let e = p.components;
                println!("h={h:e} metric={:e} gas={:?} gamma={:?} heat={:?} shape_n={:e} shape_u={:e} pool_n={:e} pool_u={:e} deltaE={:e} rhs={}",e.legacy_metric().max(e.rate_metric()),e.gas,e.gamma,e.heat,e.shape_n,e.shape_u,e.pool_n,e.pool_u,d.residuals(&p.half)?.1-d.residuals(&s)?.1,p.rhs);
            }
            Err(e) => println!("h={h:e} err={e:?}"),
        }
    }
    Ok(())
}
