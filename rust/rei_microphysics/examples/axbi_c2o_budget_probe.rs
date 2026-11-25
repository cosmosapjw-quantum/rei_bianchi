use rei_microphysics::axbi_covariant_driver::{Driver,DriverConfig};
use std::{fs,path::Path};
fn main()->Result<(),Box<dyn std::error::Error>>{
    let a=std::env::args().skip(1).collect::<Vec<_>>();
    let c=DriverConfig::read(&fs::read_to_string(&a[0])?)?;
    for b in [c.energy_budget_ev_per_h,0.]{
        let mut cc=c.clone();cc.energy_budget_ev_per_h=b;
        let (d,_)=Driver::new(cc)?;let s=d.read_checkpoint(Path::new(&a[1]))?;
        for h in [2e-5,1e-5,5e-6,2.5e-6,1.25e-6,6.25e-7,1e-7,1e-8,1e-9,1e-10]{
            match d.probe_step(&s,h){
                Ok(p)=>println!("B={b:e} h={h:e} accepted_probe metric={:e} deltaE={:e} rhs={}",p.components.legacy_metric().max(p.components.rate_metric()),d.residuals(&p.half)?.1-d.residuals(&s)?.1,p.rhs),
                Err(e)=>println!("B={b:e} h={h:e} err={e:?}"),
            }
        }
    }Ok(())
}
