#![allow(dead_code)]
mod full_network {
    #[derive(Debug)]
    pub enum NetworkError { InvalidInput, NoForwardProgress, NonFinite }
}
// compare_rust_rule.py resolves the exact candidate path before compilation.
#[path = "__REI_FITTED_BIRTH_FILE__"]
mod fitted_birth;
fn main() {
    println!("tau,refinement,cohorts,phi,emission,emission_mean,survivor_age_mean,survivor_age_second,species_h,species_he0,species_he1,species_d,number_residual");
    for tau in [0.,1e-12,1e-8,1e-4,0.1,1.,10.,30.,93.,100.,1e3,1e6,1e12] {
        for r in [1,2,4,8,16] {
            let pairs=fitted_birth::rule(tau,r).expect("candidate rejected finite test point");
            let rates=[0.71*tau,0.19*tau,0.097*tau,0.003*tau];
            let inv=fitted_birth::frozen_inventory(0.,1.,rates,1.,r).expect("candidate transaction failed");
            let emission:f64=pairs.iter().map(|(_,w)|w).sum();
            let mean:f64=pairs.iter().map(|(a,w)|a*w).sum();
            let s1=inv.born_age_moments[1]/inv.born_age_moments[0];
            let s2=inv.born_age_moments[2]/inv.born_age_moments[0];
            println!("{tau:.17e},{r},{},{:.17e},{emission:.17e},{mean:.17e},{s1:.17e},{s2:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",pairs.len(),inv.born_survivor,inv.species_absorbed[0],inv.species_absorbed[1],inv.species_absorbed[2],inv.species_absorbed[3],inv.number_residual);
        }
    }
}
