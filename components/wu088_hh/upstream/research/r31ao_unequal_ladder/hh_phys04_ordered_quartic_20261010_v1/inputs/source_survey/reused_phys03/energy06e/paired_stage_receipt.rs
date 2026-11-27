// Candidate ABI only. No public receipt issuer and no science permit issuer.
// This object binds the ENTIRE native checkpoint, not a weights transcript.
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct ReceiptIdentity {
 pub member:usize, pub theta_bits:u64, pub lambda_bits:u64,
 pub source_binding_sha256:String, pub abi_sha256:String,
}
#[derive(Clone,Debug)]
pub struct PairedStageReceipt {
 identity:ReceiptIdentity, config:HhRunConfig,
 predecessor_bytes:Vec<u8>, accepted_bytes:Vec<u8>,
 root_preconditioner:[[f64;4];4], root_box:[Interval;4],
 root_image:[Interval;4], scales:[f64;4], contraction:f64,
}
const ENERGY06E_SOURCE_BINDING:&str="265c5cf32db1d6a4e795c0cb383e547bc33697b8827adf9f16fb036d20098cfe";
fn receipt_identity_valid(id:&ReceiptIdentity,c:&HhRunConfig)->bool {
 id.member<4 && id.theta_bits==0.0_f64.to_bits()
 && id.lambda_bits==(if id.member%2==0{0.0_f64}else{1.0_f64}).to_bits()
 && id.source_binding_sha256==ENERGY06E_SOURCE_BINDING
 && id.abi_sha256=="1ea3cbdfd8658ee0e758182b1cd65aca228adbfa979ed0a6c664f52366d4e147"
 && c.mode()==if id.member%2==0{HhMode::Off}else{HhMode::Lcs91}
 && c.hubble()==if id.member<2{[1e-14;3]}else{[1.01e-14,0.99e-14,1e-14]}
 && c.grid().spectral_subdivisions==8&&c.grid().n_mu==8&&c.grid().n_phi==16
}
// Called only by a future exact-authorized native accepted half1 producer.
// A point receipt does NOT issue a uniform theta/lambda family certificate.
fn accepted_half1_receipt(_permit:&ExactSciencePermit,id:ReceiptIdentity,c:&HhRunConfig,
 old:&HhPairedState,next:&HhPairedState,root:&crate::coupled_primary::HhRoot,
 stage:&crate::coupled_primary::PrimaryStage,prebe:&crate::coupled_primary::PrimaryState,
 parent:&crate::coupled_primary::PrimaryBox)->Result<PairedStageReceipt,ForwardError>{
 if !receipt_identity_valid(&id,c) || old.base.time_s.to_bits()!=1.6e11_f64.to_bits()
 || next.base.time_s.to_bits()!=1.60625e11_f64.to_bits(){return Err(fail("ENERGY06E_RECEIPT_IDENTITY_CLOCK"));}
 hh_check(c,old)?;hh_check(c,next)?;
 let (native_next,_,native_ledger,_)=actual_full(_permit,c,old,6.25e8)?;
 if native_ledger>1e-12 || hh_checkpoint_encode(c,&native_next)?!=hh_checkpoint_encode(c,next)? {return Err(fail("ENERGY06E_NATIVE_ACCEPTED_RETURN_MISMATCH"));}
 let control=StepControl{max_iterations:200,residual_tolerance:1e-15};
 if !crate::coupled_primary::hh_root_matches(root,stage,prebe,parent,6.25e8,control,c.mode())
 || !root.root.q.is_finite() || root.root.q>=1.0 || root.root.q<0.0
 || root.scales.iter().any(|x|!x.is_finite()||*x<=0.0)
 || !(0..4).all(|i|root.root.gas[i].lo<root.image[i].lo&&root.image[i].hi<root.root.gas[i].hi)
 || root.root.preconditioner.iter().flatten().any(|x|!x.is_finite()) {
 return Err(fail("ENERGY06E_NATIVE_ROOT_CERTIFICATE_MISSING_OR_INVALID"));}
 Ok(PairedStageReceipt{identity:id,config:c.clone(),predecessor_bytes:hh_checkpoint_encode(c,old)?,
 accepted_bytes:hh_checkpoint_encode(c,next)?,root_preconditioner:root.root.preconditioner,
 root_box:root.root.gas,root_image:root.image,scales:root.scales,contraction:root.root.q})
}
// There is no conversion from JSON/weights-only to PairedStageReceipt.
// Every native point, enclosure, guard, compensation and HH ledger byte is compared.
pub fn resolve_half2_predecessor(receipt:Option<&PairedStageReceipt>,id:&ReceiptIdentity,
 c:&HhRunConfig,seed:&HhPairedState,half1:&HhPairedState)->Result<HhPairedState,ForwardError>{
 let r=receipt.ok_or_else(||fail("ENERGY06E_ACCEPTED_HALF1_RECEIPT_MISSING"))?;
 if !receipt_identity_valid(id,c)||id!=&r.identity||r.config.identity!=c.identity
 || seed.base.time_s.to_bits()!=1.6e11_f64.to_bits()||half1.base.time_s.to_bits()!=1.60625e11_f64.to_bits()
 || hh_checkpoint_encode(c,seed)?!=r.predecessor_bytes
 || hh_checkpoint_encode(c,half1)?!=r.accepted_bytes {
 return Err(fail("ENERGY06E_EXACT_PREDECESSOR_MISMATCH"));}
 hh_checkpoint_decode(c,&r.accepted_bytes)
}
pub fn uniform_family_certificate_requested()->Result<(),ForwardError>{
 Err(fail("ENERGY06E_UNIFORM_THETA_LAMBDA_DERIVATIVE_ENCLOSURE_MISSING"))
}
#[cfg(test)]mod energy06e_tests {
 use super::*;
 fn fixture()->(ReceiptIdentity,HhRunConfig,HhPairedState,HhPairedState,PairedStageReceipt){
  let c=cfg(1).unwrap();let mut seed=hh_paired_initial(&c).unwrap();seed.base.time_s=1.6e11;let mut half=seed.clone();half.base.time_s=1.60625e11;
  let id=ReceiptIdentity{member:1,theta_bits:0.0_f64.to_bits(),lambda_bits:1.0_f64.to_bits(),source_binding_sha256:ENERGY06E_SOURCE_BINDING.into(),abi_sha256:"1ea3cbdfd8658ee0e758182b1cd65aca228adbfa979ed0a6c664f52366d4e147".into()};
  // Explicit SYNTHETIC fixture; test module cannot export an issuer.
  let r=PairedStageReceipt{identity:id.clone(),config:c.clone(),predecessor_bytes:hh_checkpoint_encode(&c,&seed).unwrap(),accepted_bytes:hh_checkpoint_encode(&c,&half).unwrap(),root_preconditioner:[[0.0;4];4],root_box:[p(0.0).unwrap();4],root_image:[p(0.0).unwrap();4],scales:[1.0;4],contraction:0.0};
  (id,c,seed,half,r)
 }
 #[test]fn missing_receipt_and_weights_only_fail(){let(id,c,s,h,_)=fixture();assert!(resolve_half2_predecessor(None,&id,&c,&s,&h).is_err());}
 #[test]fn exact_checkpoint_contract_roundtrip(){let(id,c,s,h,r)=fixture();assert_eq!(hh_checkpoint_encode(&c,&resolve_half2_predecessor(Some(&r),&id,&c,&s,&h).unwrap()).unwrap(),r.accepted_bytes);}
 #[test]fn changed_member_theta_lambda_source_abi_rejected(){let(id,c,s,h,r)=fixture();for k in 0..5{let mut x=id.clone();match k{0=>x.member=3,1=>x.theta_bits=1.0_f64.to_bits(),2=>x.lambda_bits=0.5_f64.to_bits(),3=>x.source_binding_sha256="b".repeat(64),_=>x.abi_sha256="b".repeat(64)}assert!(resolve_half2_predecessor(Some(&r),&x,&c,&s,&h).is_err());}}
 #[test]fn gas_photon_guard_compensation_and_hh_ledger_rejected(){let(id,c,s,h,r)=fixture();for k in 0..9{let mut x=h.clone();match k{0=>x.base.gas.fractions[0]+=1e-8,1=>x.base.photons[0]+=1e-8,2=>x.base.lower_guard_n[0]+=1e-8,3=>x.base.lower_guard_u[0]+=1e-8,4=>x.base.ledger_comp[0]+=1e-8,5=>x.base.energy_comp+=1e-8,6=>x.hh_events+=1e-8,7=>x.hh_heat-=1e-8,_=>x.hh_comp[0]+=1e-8}assert!(resolve_half2_predecessor(Some(&r),&id,&c,&s,&x).is_err());}}
 #[test]fn wrong_clock_and_seed_rejected(){let(id,c,s,h,r)=fixture();let mut x=h.clone();x.base.time_s+=1.0;assert!(resolve_half2_predecessor(Some(&r),&id,&c,&s,&x).is_err());let mut y=s.clone();y.base.energy_comp+=1e-8;assert!(resolve_half2_predecessor(Some(&r),&id,&c,&y,&h).is_err());}
 #[test]fn family_never_inferred_from_point(){assert!(uniform_family_certificate_requested().is_err());assert!(scientific_dispatch_requested().is_err());}
}
