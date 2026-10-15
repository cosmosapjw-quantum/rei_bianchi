//! Scalar reference: pinned axbi_driver.rs evaluate lines 452..479 and f lines24..30.
use rei_microphysics::{igm_thermal::IgmPhotoInput,ForwardError,HHeModel};
#[derive(Clone,Debug)]
pub struct Input {pub energies:Vec<f64>, pub signatures:Vec<[f64;3]>,pub absorbers:[f64;3],pub nh:f64,pub dt:f64,pub stocks:Vec<f64>}
pub fn finite(x:f64)->Result<f64,ForwardError>{if x.is_finite(){Ok(x)}else{Err(ForwardError::InvalidInput("AXBI_DRIVER_NONFINITE"))}}
pub fn reference(a:&Input)->Result<(Vec<f64>,IgmPhotoInput),ForwardError>{
 let c=HHeModel::controlled_fixture();let ne=a.energies.len();let mut stocks=Vec::with_capacity(a.stocks.len());let mut photo=IgmPhotoInput::default();
 for (j,&nstar) in a.stocks.iter().enumerate(){let i=j%ne;let opacity=(0..3).map(|k|a.absorbers[k]*a.signatures[i][k]).sum::<f64>();let n=finite(nstar/(1.0+a.dt*c.c_cm_s*opacity))?;stocks.push(n);
 for k in 0..3 {let rate=c.c_cm_s*a.nh*a.signatures[i][k]*n;photo.gamma_s[k]+=rate;if rate!=0.0{if a.energies[i]<c.threshold_ev[k]{return Err(ForwardError::InvalidInput("AXBI_THRESHOLD_OWNERSHIP"));}photo.heat_erg_per_absorber_s[k]+=rate*(a.energies[i]-c.threshold_ev[k])*c.ev_erg;}}}
 Ok((stocks,photo))
}
pub fn hoisted(a:&Input)->Result<(Vec<f64>,IgmPhotoInput),ForwardError>{
 let c=HHeModel::controlled_fixture();let ne=a.energies.len();
 let factors:Vec<(f64,[f64;3],[f64;3])>=(0..ne).map(|i|{let opacity=(0..3).map(|k|a.absorbers[k]*a.signatures[i][k]).sum::<f64>();(1.0+a.dt*c.c_cm_s*opacity,std::array::from_fn(|k|c.c_cm_s*a.nh*a.signatures[i][k]),std::array::from_fn(|k|a.energies[i]-c.threshold_ev[k]))}).collect();
 let mut stocks=Vec::with_capacity(a.stocks.len());let mut photo=IgmPhotoInput::default();
 for (j,&nstar) in a.stocks.iter().enumerate(){let i=j%ne;let (den,pref,excess)=factors[i];let n=finite(nstar/den)?;stocks.push(n);for k in 0..3{let rate=pref[k]*n;photo.gamma_s[k]+=rate;if rate!=0.0{if a.energies[i]<c.threshold_ev[k]{return Err(ForwardError::InvalidInput("AXBI_THRESHOLD_OWNERSHIP"));}photo.heat_erg_per_absorber_s[k]+=rate*excess[k]*c.ev_erg;}}}Ok((stocks,photo))
}
