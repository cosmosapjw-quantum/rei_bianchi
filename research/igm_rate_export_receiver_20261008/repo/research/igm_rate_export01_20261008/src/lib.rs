//! Instantaneous finite-grid observation. No RHS, history, target density or enclosure.
use rei_microphysics::{igm_background::FlrwPoint, AtomicProvider, HHeModel};
use short_hhe_control::{radiation::{Grid,SPECIES}, product, Fallible};

#[derive(Clone,Debug)]
pub struct Observation { pub gamma:[f64;3], pub incident_ev:[f64;3], pub samples:Vec<[f64;11]> }

pub fn validate(grid:&Grid,s:f64,density:&[f64],p:FlrwPoint)->Fallible<()> {
    if grid.nodes.len()!=density.len() || !s.is_finite() || !p.n_h_cm3.is_normal() || p.n_h_cm3<=0. {return Err("EXACT_GRID_CLOCK_DENSITY_CONTEXT".into())}
    if grid.nodes.iter().any(|&(e,w)| !e.is_finite() || !w.is_normal() || w<=0.) || density.iter().any(|&f| !f.is_finite() || f<0.) {return Err("SPECTRAL_DOMAIN".into())}
    Ok(())
}

pub fn observe(grid:&Grid,s:f64,density:&[f64],p:FlrwPoint)->Fallible<Observation> {
    validate(grid,s,density,p)?;
    let c=HHeModel::controlled_fixture();
    let mut out=Observation{gamma:[0.;3],incident_ev:[0.;3],samples:Vec::new()};
    // Preserve radiation::gamma's exact node/species/reduction and product order.
    // Each provider sample supplies BOTH moments. No re-evaluation for Ecal.
    for (&(eta,w),&f) in grid.nodes.iter().zip(density) {
        let e=(eta-s).exp(); let mut sig=[0.;3]; let mut term=[0.;3];
        for i in 0..3 {
            sig[i]=AtomicProvider::reference().cross_section(SPECIES[i],e).map_err(short_hhe_control::err)?;
            term[i]=product(product(product(product(c.c_cm_s,p.n_h_cm3)?,sig[i])?,f)?,w)?;
            out.gamma[i]+=term[i];out.incident_ev[i]+=product(term[i],e)?;
        }
        out.samples.push([eta,w,f,e,sig[0],sig[1],sig[2],term[0],term[1],term[2],c.c_cm_s]);
    }
    if out.gamma.iter().chain(out.incident_ev.iter()).any(|x|!x.is_finite()||*x<0.) {return Err("MOMENT_DOMAIN".into())}
    Ok(out)
}
