// No public issuer. SameEndpointReturn is constructed at the endpoint return seam.
use std::sync::atomic::{AtomicUsize,Ordering};
pub(crate) static PHYS04_ENDPOINT:AtomicUsize=AtomicUsize::new(0);
pub(crate) static PHYS04_CONSERVATIVE:AtomicUsize=AtomicUsize::new(0);
pub(crate) static PHYS04_INTERNAL_POINT:AtomicUsize=AtomicUsize::new(0);
pub(crate) static PHYS04_ROOT:AtomicUsize=AtomicUsize::new(0);
pub fn phys04_native_counts()->[usize;4]{[&PHYS04_ENDPOINT,&PHYS04_CONSERVATIVE,&PHYS04_INTERNAL_POINT,&PHYS04_ROOT].map(|x|x.load(Ordering::SeqCst))}
#[derive(Clone,Debug,PartialEq,Eq)]
struct EndpointIdentity {config:Vec<u64>,old:Vec<u64>,clock:[u64;2],source:Vec<u8>}
fn physical_words(s:&PairedState)->Vec<u64>{
 let mut v=vec![s.time_s.to_bits(),s.gas.escape_ev_per_h.to_bits(),s.gas.w_ev_per_h.to_bits(),s.energy_comp.to_bits()];
 v.extend(s.gas.fractions.map(f64::to_bits));
 for x in s.photons.iter().chain(&s.lower_guard_n).chain(&s.lower_guard_u).chain(&s.ledger_comp){v.push(x.to_bits());}
 for b in s.gas_box.iter().chain(&s.photon_boxes).chain(&s.lower_guard_n_box).chain(&s.lower_guard_u_box){v.extend([b.lo.to_bits(),b.hi.to_bits()]);}
 v.extend([s.redshift_work_ev_per_h,s.thermal_work_ev_per_h,s.source_photons_per_h,s.source_energy_ev_per_h,s.absorbed_photons_per_h].map(f64::to_bits));
 for x in &s.gas.packets {v.extend([x.energy_ev.to_bits(),x.per_h.to_bits()]);}v
}
impl EndpointIdentity {
 fn new(c:&PairedConfig,h:[f64;3],old:&PairedState,dt:f64)->Self{Self::amplitude(c,h,old,dt,1.0,1.0)}
 fn amplitude(c:&PairedConfig,h:[f64;3],old:&PairedState,dt:f64,lambda:f64,b:f64)->Self{
  let mut config=vec![c.spectral_subdivisions as u64,c.n_mu as u64,c.n_phi as u64];config.extend(h.map(f64::to_bits));config.extend([lambda.to_bits(),b.to_bits()]);
  // Actual compiled source bytes; binary/loader identity is supplied separately at delivery.
  let source=[include_bytes!("paired_runtime.rs").as_slice(),include_bytes!("hh_paired_extension.rs").as_slice(),include_bytes!("phys04_receipt.rs").as_slice(),include_bytes!("phys04_mixed.rs").as_slice(),include_bytes!("interval_ad.rs").as_slice(),include_bytes!("interval_math.rs").as_slice(),include_bytes!("coupled_primary.rs").as_slice(),include_bytes!("hh_primary_extension.rs").as_slice(),include_bytes!("hh_return_enclosure.rs").as_slice(),include_bytes!("phys04_transport.rs").as_slice()].concat();
  Self{config,old:physical_words(old),clock:[old.time_s.to_bits(),dt.to_bits()],source}
 }
}
struct SameEndpointReturn {
 next:PairedState,audit:String,ledger:f64,events:[f64;2],
 point:crate::coupled_primary::HhStep,root:crate::coupled_primary::HhRoot,
 carry:PrimaryBox,stage:PrimaryStage,prebe:PrimaryState,parent:PrimaryBox,control:StepControl,
 identity:EndpointIdentity,history:Option<([f64;4],[f64;4])>,
}
// Accepted receipt consumes the returned object. No solver/callback is invoked here.
struct AcceptedHalf1 {returned:SameEndpointReturn,history:[f64;4]}
fn accepted_half1_receipt(returned:SameEndpointReturn,c:&PairedConfig,h:[f64;3],old:&PairedState,history:[f64;4])->Result<AcceptedHalf1,ForwardError>{
 accepted_half1_amplitude_receipt(returned,c,h,old,history,1.0,1.0)
}
fn accepted_half1_amplitude_receipt(returned:SameEndpointReturn,c:&PairedConfig,h:[f64;3],old:&PairedState,history:[f64;4],lambda:f64,b:f64)->Result<AcceptedHalf1,ForwardError>{
 use crate::coupled_primary::hh_amplitude_root_matches;
 if ![lambda,b].iter().all(|x|x.is_finite()&&(0.0..=1.0).contains(x)) || returned.identity!=EndpointIdentity::amplitude(c,h,old,6.25e8,lambda,b)
 || old.time_s.to_bits()!=1.6e11_f64.to_bits() || returned.next.time_s.to_bits()!=1.60625e11_f64.to_bits()
 || !returned.ledger.is_finite() || returned.ledger>1e-12
 || !hh_amplitude_root_matches(&returned.root,&returned.stage,&returned.prebe,&returned.parent,6.25e8,returned.control,lambda)
 || returned.root.root.q<0.0 || returned.root.root.q>=1.0 || !returned.root.root.q.is_finite()
 || !(0..4).all(|i|returned.root.root.gas[i].lo<returned.root.image[i].lo&&returned.root.image[i].hi<returned.root.root.gas[i].hi)
 || returned.history.as_ref().map(|v|v.0.map(f64::to_bits))!=Some(history.map(f64::to_bits))
 || history.iter().any(|x|!x.is_finite()) {return Err(fail("PHYS04_SAME_EXECUTION_IDENTITY"));}
 let point=gas4(&returned.point.base.state);
 if !(0..4).all(|i|contains(returned.carry.gas[i],point[i])&&returned.carry.gas[i].lo<=returned.root.root.gas[i].lo&&returned.root.root.gas[i].hi<=returned.carry.gas[i].hi)
 || returned.next.gas_box.iter().zip(returned.carry.gas).any(|(a,b)|a.lo.to_bits()!=b.lo.to_bits()||a.hi.to_bits()!=b.hi.to_bits()) {return Err(fail("PHYS04_CARRY_DISTINCT_FROM_ROOT"));}
 Ok(AcceptedHalf1{returned,history})
}
fn resolve_half2_predecessor(receipt:&AcceptedHalf1,c:&PairedConfig,h:[f64;3],old:&PairedState,history:[f64;4])->Result<PairedState,ForwardError>{
 let config=&receipt.returned.identity.config;let lambda=f64::from_bits(config[6]);let b=f64::from_bits(config[7]);
 if receipt.returned.identity!=EndpointIdentity::amplitude(c,h,old,6.25e8,lambda,b)||receipt.history.map(f64::to_bits)!=history.map(f64::to_bits){return Err(fail("PHYS04_PREDECESSOR_IDENTITY"));}
 Ok(receipt.returned.next.clone())
}
// Private future issuer: existing primal/root paths remain separate; one endpoint.
struct Phys04ExactPermit{_sealed:()}
fn accepted_half1_producer(_permit:&Phys04ExactPermit,c:&HhRunConfig,old:&HhPairedState)->Result<AcceptedHalf1,ForwardError>{
 hh_check(c,old)?;
 if c.mode()!=HhMode::Lcs91{return Err(fail("PHYS04_LEGACY_POINT_ONLY_LCS_SEAM"));}
 accepted_half1_amplitude_producer(_permit,c,old,1.0,1.0)
}
fn accepted_half1_amplitude_producer(_permit:&Phys04ExactPermit,c:&HhRunConfig,old:&HhPairedState,lambda:f64,b:f64)->Result<AcceptedHalf1,ForwardError>{
 hh_check(c,old)?;if c.mode()!=HhMode::Lcs91||![lambda,b].iter().all(|x|x.is_finite()&&(0.0..=1.0).contains(x)){return Err(fail("PHYS04_AMPLITUDE_IDENTITY"));}
 let nodes=energy_nodes(c.grid())?;let mut result=hh_source_endpoint_returned(c.grid(),c.hubble(),old.base(),6.25e8,&nodes,lambda,b)?;
 let before=[old.hh_events,old.hh_heat,old.hh_comp[0],old.hh_comp[1]];
 let e=accumulate(before[0],before[2],result.events[0]);let heat=accumulate(before[1],before[3],result.events[1]);
 result.history=Some((before,[e.0,heat.0,e.1,heat.1]));
 accepted_half1_amplitude_receipt(result,c.grid(),c.hubble(),old.base(),before,lambda,b)
}
fn resolve_half2_hh_predecessor(receipt:&AcceptedHalf1,c:&HhRunConfig,old:&HhPairedState)->Result<HhPairedState,ForwardError>{
 hh_check(c,old)?;let before=[old.hh_events,old.hh_heat,old.hh_comp[0],old.hh_comp[1]];
 let base=resolve_half2_predecessor(receipt,c.grid(),c.hubble(),old.base(),before)?;
 let after=receipt.returned.history.ok_or_else(||fail("PHYS04_HISTORY_RETURN_MISSING"))?.1;
 let next=HhPairedState{base,hh_events:after[0],hh_heat:after[1],hh_comp:[after[2],after[3]],identity:old.identity.clone()};hh_check(c,&next)?;Ok(next)
}
pub fn phys04_native_dispatch_requested()->Result<(),ForwardError>{Err(fail("PHYS04_AUTHORIZATION_NULL_BUDGET_ZERO"))}

#[cfg(test)] mod phys04_receipt_tests {
 use super::*;use crate::coupled_primary::*;
 static SYNTHETIC:AtomicUsize=AtomicUsize::new(0);
 fn fixture()->(PairedConfig,PairedState,SameEndpointReturn){
  SYNTHETIC.fetch_add(1,Ordering::SeqCst);
  let c=PairedConfig{spectral_subdivisions:8,n_mu:8,n_phi:16};let mut old=paired_initial(&c).unwrap();old.time_s=1.6e11;
  let stage=PrimaryStage{n_h_cm3:1e-4,f_he:0.083,h_mean_per_s:1e-14};let control=StepControl{max_iterations:200,residual_tolerance:1e-15};
  let prebe=old.gas.clone();let parent=PrimaryBox{gas:old.gas_box,photons:prebe.packets.iter().map(|p|super::p(p.per_h).unwrap()).collect()};
  let centre=gas4(&prebe);let root_box=centre.map(|x|Interval{lo:x-1e-8,hi:x+1e-8});
  let root=HhRoot{root:PrimaryRoot{centre,gas:root_box,photons:parent.photons.clone(),preconditioner:std::array::from_fn(|i|std::array::from_fn(|j|if i==j{1.0}else{0.0})),q:0.01},mode:HhMode::Lcs91,amplitude:1.0,image:centre.map(|x|Interval{lo:x-1e-9,hi:x+1e-9}),scales:[1.0,1.0,1.0,centre[3]],identity:HhIdentity::new(&stage,&prebe,&parent,6.25e8,control,HhMode::Lcs91)};
  let point=HhStep{base:PrimaryStep{state:prebe.clone(),events:PrimaryEvents{photo_per_h:vec![[0.0;3];prebe.packets.len()],collision_per_h:[0.0;3],recombination_per_h:[0.0;3],dr_per_h:[0.0;2],thermal_work_ev_per_h:0.0},iterations:0,residual:0.0},hh_events_per_h:0.0,hh_heat_ev_per_h:0.0,mode:HhMode::Lcs91};
  let carry=PrimaryBox{gas:root_box.map(|x|Interval{lo:x.lo-1e-7,hi:x.hi+1e-7}),photons:parent.photons.clone()};let mut next=old.clone();next.time_s=1.60625e11;next.gas_box=carry.gas;
  let returned=SameEndpointReturn{next,audit:"SYNTHETIC_NO_ROOT_EXECUTION".into(),ledger:0.0,events:[0.0;2],point,root,carry,stage,prebe,parent,control,identity:EndpointIdentity::new(&c,[1e-14;3],&old,6.25e8),history:Some(([0.3,-4.0,1e-17,2e-17],[0.3,-4.0,1e-17,2e-17]))};(c,old,returned)
 }
 #[test] fn ReceiptNoRedispatch(){
  let before=phys04_native_counts();let spy=SYNTHETIC.load(Ordering::SeqCst);let(c,old,result)=fixture();let proof=result.root.root.gas;let carry=result.carry.gas;
  let receipt=accepted_half1_receipt(result,&c,[1e-14;3],&old,[0.3,-4.0,1e-17,2e-17]).unwrap();let next=resolve_half2_predecessor(&receipt,&c,[1e-14;3],&old,[0.3,-4.0,1e-17,2e-17]).unwrap();
  assert_eq!(SYNTHETIC.load(Ordering::SeqCst),spy+1);assert_eq!(phys04_native_counts(),before);assert_eq!(physical_words(&next),physical_words(&receipt.returned.next));
  let hc=HhRunConfig::new(c.clone(),[1e-14;3],HhMode::Lcs91).unwrap();let hs=HhPairedState{base:old.clone(),hh_events:0.3,hh_heat:-4.0,hh_comp:[1e-17,2e-17],identity:hc.identity.clone()};let hn=resolve_half2_hh_predecessor(&receipt,&hc,&hs).unwrap();assert_eq!(hn.hh_comp,hs.hh_comp);assert_eq!(hn.hh_events,hs.hh_events);assert_eq!(phys04_native_counts(),before);
  assert_eq!(receipt.returned.root.root.gas[0].lo.to_bits(),proof[0].lo.to_bits());assert!(carry[0].lo<proof[0].lo);
  println!("RECEIPT_TRACE synthetic_endpoint=1 synthetic_point=1 synthetic_root=1 receipt=1 resolve=1 added_endpoint=0 added_point=0 added_root=0 native={:?}",phys04_native_counts());
 }
 #[test] fn RootTubeAuthority(){
  for k in 0..8 {let(c,old,mut r)=fixture();match k {0=>r.identity.clock[0]^=1,1=>r.identity.config[0]^=1,2=>r.identity.source.push(0),3=>r.prebe.w_ev_per_h+=1.0,4=>r.parent.gas[0].lo-=0.01,5=>r.control.max_iterations+=1,6=>r.stage.n_h_cm3*=2.0,_=>r.root.root.q=1.0};assert!(accepted_half1_receipt(r,&c,[1e-14;3],&old,[0.3,-4.0,1e-17,2e-17]).is_err());}
  let(c,old,r)=fixture();let receipt=accepted_half1_receipt(r,&c,[1e-14;3],&old,[0.3,-4.0,1e-17,2e-17]).unwrap();
  let mut changed=old.clone();changed.lower_guard_u[0]=1e-9;assert!(resolve_half2_predecessor(&receipt,&c,[1e-14;3],&changed,[0.3,-4.0,1e-17,2e-17]).is_err());assert!(resolve_half2_predecessor(&receipt,&c,[1e-14;3],&old,[0.0;4]).is_err());
 }
 #[test] fn AmplitudeReceiptFourCorners(){
 let before=phys04_native_counts();let history=[0.3,-4.0,1e-17,2e-17];
 for (lambda,b) in [(0.0,0.0),(0.0,1.0),(1.0,0.0),(1.0,1.0),(0.4,0.6)] {
 let(c,old,mut r)=fixture();r.root.amplitude=lambda;r.identity=EndpointIdentity::amplitude(&c,[1e-14;3],&old,6.25e8,lambda,b);
 let a=accepted_half1_amplitude_receipt(r,&c,[1e-14;3],&old,history,lambda,b).unwrap();let next=resolve_half2_predecessor(&a,&c,[1e-14;3],&old,history).unwrap();assert_eq!(physical_words(&next),physical_words(&a.returned.next));assert_eq!(a.history,history);
 let(c,old,mut r)=fixture();r.root.amplitude=lambda;r.identity=EndpointIdentity::amplitude(&c,[1e-14;3],&old,6.25e8,lambda,b);
 assert!(accepted_half1_amplitude_receipt(r,&c,[1e-14;3],&old,history,lambda,if b==0.0{1.0}else{0.0}).is_err());
 }assert_eq!(phys04_native_counts(),before);
 }
 #[test] fn NativeBudgetRefusal(){assert!(phys04_native_dispatch_requested().is_err());assert_eq!(phys04_native_counts(),[0;4]);}
}
