//! Actual source linkage with typed unresolved whole-domain premises. This does
//! not call the callback, solve a root or claim coverage from a hash/domain label.
use crate::*;
use crate::family::{CommonFamily,FamilyIdentity};
use crate::certificate::BoundDerivatives;
use hh_phys04_candidate::paired_runtime::Phys04PreBE;
#[derive(Debug)]pub enum WholeSourceEnclosure{Unresolved{missing:Vec<&'static str>}}
#[derive(Debug)]pub struct SourceAdapter{
 pub family:FamilyIdentity,pub requested_x:[Interval;4],pub theta:[Interval;2],pub clock:u64,pub density:u64,
 pub incoming_gas:[Jet;4],pub incoming_photons:Vec<Jet>,pub guards_n:Vec<Jet>,pub guards_u:Vec<Jet>,
 pub inherited_physical_compensation:[f64;5],pub inherited_energy_compensation:f64,
 pub source_carry_word_receipt:String,pub supplied_fixed_c:[[f64;4];4],pub whole_source:WholeSourceEnclosure,
 pub native_authority:bool,
}
pub fn bind(family:&CommonFamily,pre:&Phys04PreBE,derivatives:&BoundDerivatives,requested_x:[Interval;4],theta:[Interval;2])->R<SourceAdapter>{
 if family.identity!=derivatives.incoming_identity||derivatives.endpoint_clock_bits!=pre.time_s.to_bits()||derivatives.density_bits!=pre.stage.n_h_cm3.to_bits()||!theta.iter().zip(derivatives.rectangle).all(|(a,b)|same(*a,b)){return Err("actual adapter family/clock/density/rectangle mismatch");}
 if family.identity.candidate_source_sha256!=crate::family::bindings::SOURCE_SHA||family.identity.abi_sha256!=crate::family::bindings::ABI_SHA{return Err("compiled source ABI mismatch");}
 for x in requested_x.iter().chain(theta.iter()){valid(*x)?;}
 pre.validate_family_input(family.identity.theta_bits.map(f64::from_bits),family.physical.time_s,pre.dt,&family.gas,&family.photons,&family.guard_n,&family.guard_u,theta[1]).map_err(|_|"exact incoming Jet/clock/geometry/b seal mismatch")?;
 Ok(SourceAdapter{family:family.identity.clone(),requested_x,theta,clock:pre.time_s.to_bits(),density:pre.stage.n_h_cm3.to_bits(),incoming_gas:pre.gas.clone(),incoming_photons:pre.photons.clone(),guards_n:pre.guard_n.clone(),guards_u:pre.guard_u.clone(),inherited_physical_compensation:family.physical.ledger_comp,inherited_energy_compensation:family.physical.energy_comp,source_carry_word_receipt:format!("{:?}",(&family.identity,&pre.gas,&pre.photons,&pre.guard_n,&pre.guard_u)),supplied_fixed_c:derivatives.arithmetic.fixed_c,whole_source:WholeSourceEnclosure::Unresolved{missing:vec!["G(center,whole Theta) enclosure","whole X times Theta source A/partials and physical C2 open-domain evidence","trusted uniform root/tube producer and exact authorization"]},native_authority:false})
}
