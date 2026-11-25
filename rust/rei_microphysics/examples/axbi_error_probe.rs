use rei_microphysics::axbi_covariant_driver::{Driver, DriverConfig};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let a = std::env::args().skip(1).collect::<Vec<_>>();
    if a.len() != 2 {
        return Err("usage CONFIG CHECKPOINT".into());
    }
    let (d, mut s) = Driver::new(DriverConfig::read(&std::fs::read_to_string(&a[0])?)?)?;
    for label in ["initial", "cap"] {
        if label == "cap" {
            s = d.read_checkpoint(std::path::Path::new(&a[1]))?;
        }
        eprintln!(
            "{label}: z={} h={} last_error={}",
            1. / s.a - 1.,
            s.next_dln_a,
            s.last_error
        );
        for multiplier in [0.25, 0.5, 1., 2., 4., 16., 64., 256., 1024.] {
            let h = (s.next_dln_a * multiplier).min(0.005);
            match d.probe_step(&s, h) {
                Ok(r) => {
                    let x = r.components;
                    println!("{label}\t{h:.17e}\t{}",[x.legacy_metric(),x.rate_metric(),x.gas[0],x.gas[1],x.gas[2],x.gas[3],x.shape_n,x.shape_u,x.pool_n,x.pool_u,x.gamma[0],x.gamma[1],x.gamma[2],x.heat[0],x.heat[1],x.heat[2]].iter().map(|v|format!("{v:.17e}")).collect::<Vec<_>>().join("\t"));
                }
                Err(e) => println!("{label}\t{h:.17e}\tERROR:{e:?}"),
            }
        }
    }
    Ok(())
}
