//! Diagnostic source/parameter derivative export and opaque authority types.
use hh_phys04_candidate::{Interval,ForwardError};
use hh_phys04_candidate::coupled_primary::{Phys04MixedArithmetic,phys04_mixed_at_box};
use hh_phys04_candidate::paired_runtime::Phys04PreBE;
use crate::family::{CommonFamily,FamilyIdentity};
#[derive(Debug)]pub struct BoundDerivatives{pub incoming_identity:FamilyIdentity,pub endpoint_clock_bits:u64,pub density_bits:u64,pub rectangle:[Interval;2],pub arithmetic:Phys04MixedArithmetic}
// This export is full-chain source arithmetic. It is not a uniform root certificate.
pub fn export_derivatives(family:&CommonFamily,pre:&Phys04PreBE,gas:[Interval;4],rectangle:[Interval;2],candidates:[[Interval;4];3])->Result<BoundDerivatives,ForwardError>{
 let h=family.identity.theta_bits.map(f64::from_bits);let density=1e-4*(-h.iter().sum::<f64>()*pre.time_s).exp();
 if pre.time_s.to_bits()!=(family.physical.time_s+pre.dt).to_bits()||pre.stage.n_h_cm3.to_bits()!=density.to_bits()||rectangle[0].lo<0.0||rectangle[0].hi>1.0||rectangle[1].lo<0.0||rectangle[1].hi>1.0{return Err(ForwardError::InvalidInput("PHYS04_EXPORT_CLOCK_SOURCE_IDENTITY"));}
 pre.validate_family_input(h,family.physical.time_s,pre.dt,&family.gas,&family.photons,&family.guard_n,&family.guard_u,rectangle[1])?;
 let arithmetic=phys04_mixed_at_box(&pre.stage,&pre.gas,gas,&pre.groups,&pre.energies,rectangle[0],pre.dt,candidates)?;
 Ok(BoundDerivatives{incoming_identity:family.identity.clone(),endpoint_clock_bits:pre.time_s.to_bits(),density_bits:pre.stage.n_h_cm3.to_bits(),rectangle,arithmetic})
}
// No public constructors, serde deserialization or arbitrary C/JSON conversion.
pub struct NativePointCertificate{_private:()}
pub struct NativeFamilyTube{_private:()}
pub fn request_native_family_certificate(_point:Option<&NativePointCertificate>)->Result<NativeFamilyTube,ForwardError>{Err(ForwardError::InvalidInput("PHYS04_UNIFORM_ROOT_PRODUCER_AUTHORIZATION_MISSING"))}
#[cfg(test)]mod tests{use super::*;#[test]fn point_is_not_uniform_tube(){assert!(request_native_family_certificate(None).is_err());}}
