use crate::Fallible;
/// Red scaffold: ordinary exponential currently ignores exact event identity.
pub fn start_energy(eta:f64,a:f64,_b:f64)->Fallible<(f64,bool)>{Ok(((eta-a).exp(),false))}
