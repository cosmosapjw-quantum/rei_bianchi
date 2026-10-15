//! Campaign binding of the existing cold-through-reheated H/He point model.
//!
//! Grackle 3.4.1 literals are owned by `igm_rates`; event/energy ownership is
//! owned by `igm_point_rhs`. This adapter adds no coefficients or admission to
//! the FT03 interval model. The numerical operational domain does not assert
//! empirical fit accuracy, a continuum certificate, or a cosmological history.
use rei_microphysics::{igm_state::IgmGasState, igm_thermal::IgmPhotoInput, axbi_rates::{AxbiPoint,AXBI_PROVIDER_ID}, ForwardError};
use crate::candidate_igm_thermal::igm_point_rhs_bundle;
pub fn point(gas:&IgmGasState, n_h_cm3:f64,n_he_cm3:f64,mean_h_per_s:f64,tcmb_k:f64,photo:IgmPhotoInput)->Result<AxbiPoint,ForwardError>{
 let temperature_k=gas.eos(n_h_cm3,n_he_cm3)?.temperature_k;
 let (rhs,rates)=igm_point_rhs_bundle(gas,n_h_cm3,n_he_cm3,mean_h_per_s,tcmb_k,photo)?;
 Ok(AxbiPoint{provider_id:AXBI_PROVIDER_ID,temperature_k,rates,rhs})
}
