#[path="bindings.rs"] pub mod bindings;
// Archived ON bytes stay ON. The future family has its own identity and ledger.
use hh_phys04_candidate::{Interval,Jet,ForwardError};
use rei_reference::paired_runtime::{HhRunConfig,HhPairedState,PairedState,hh_checkpoint_decode,hh_checkpoint_encode};
fn error()->ForwardError{ForwardError::InvalidInput("PHYS04_COMMON_FAMILY_IDENTITY")}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct FamilyIdentity {pub archive_sha256:String,pub candidate_source_sha256:String,pub abi_sha256:String,pub theta_bits:[u64;3],pub clock_bits:u64,pub lambda_bits:u64,pub b_bits:u64}
#[derive(Clone,Debug)]
pub struct CommonFamily {
 archive_bytes:Vec<u8>,archived:HhPairedState,config:HhRunConfig,
 pub identity:FamilyIdentity,pub physical:PairedState,
 pub historical_hh:[f64;4],pub future_hh:[f64;4],
 pub gas:[Jet;4],pub photons:Vec<Jet>,pub guard_n:Vec<Jet>,pub guard_u:Vec<Jet>,
 // Primal compensation remains in physical; derivative ledgers are separate real-family jets.
 pub ledger_derivatives:[Jet;5],pub energy_comp_derivative:Jet,pub hh_derivatives:[Jet;2],
}
fn jet(x:rei_reference::Interval)->Jet{Jet::constant(Interval{lo:x.lo,hi:x.hi}).expect("decoded valid interval")}
fn sha_format(s:&str)->bool{s.len()==64&&s.bytes().all(|b|b.is_ascii_hexdigit())}
impl CommonFamily {
 pub fn initialize(bytes:&[u8],config:&HhRunConfig,id:FamilyIdentity)->Result<Self,ForwardError>{
  if bytes!=include_bytes!("../inputs/COMMON_SEED_MEMBER1.bin") || id.archive_sha256!="678f967f0d50ad1fff47a73e2e63193429b708246cd84ca8ffc72191c31b522b" || !sha_format(&id.archive_sha256)||id.candidate_source_sha256!=bindings::SOURCE_SHA||id.abi_sha256!=bindings::ABI_SHA
   || ![id.lambda_bits,id.b_bits].iter().all(|x|{let v=f64::from_bits(*x);v.is_finite()&&(0.0..=1.0).contains(&v)})
   || id.theta_bits!=config.hubble().map(f64::to_bits) {return Err(error());}
  // SHA validated externally in intake; exact bytes are retained and roundtrip checked here.
  let archived=hh_checkpoint_decode(config,bytes).map_err(|_|error())?;
  if hh_checkpoint_encode(config,&archived).map_err(|_|error())?!=bytes||id.clock_bits!=archived.base().time_s.to_bits(){return Err(error());}
  let physical=archived.base().clone();
  if physical.photons.len()!=4224||physical.lower_guard_n.len()!=128||config.grid().spectral_subdivisions!=8||config.grid().n_mu!=8||config.grid().n_phi!=16{return Err(error());}
  let z=jet(rei_reference::Interval{lo:0.0,hi:0.0});let comp=archived.hh_compensation();
  Ok(Self{archive_bytes:bytes.to_vec(),historical_hh:[archived.hh_events_per_h(),archived.hh_heat_ev_per_h(),comp[0],comp[1]],future_hh:[0.0;4],gas:physical.gas_box.map(jet),photons:physical.photon_boxes.iter().copied().map(jet).collect(),guard_n:physical.lower_guard_n_box.iter().copied().map(jet).collect(),guard_u:physical.lower_guard_u_box.iter().copied().map(jet).collect(),ledger_derivatives:std::array::from_fn(|_|z.clone()),energy_comp_derivative:z.clone(),hh_derivatives:[z.clone(),z],physical,archived,config:config.clone(),identity:id})
 }
 pub fn original_bytes(&self)->&[u8]{&self.archive_bytes}
 pub fn archived_roundtrip(&self)->Result<Vec<u8>,ForwardError>{hh_checkpoint_encode(&self.config,&self.archived).map_err(|_|error())}
 pub fn total_hh(&self)->[f64;2]{[self.historical_hh[0]+self.future_hh[0],self.historical_hh[1]+self.future_hh[1]]}
 pub fn future_birth_rate(&self)->f64{5e-15*f64::from_bits(self.identity.b_bits)}
 // Candidate endpoint increments only: zero future lambda does not erase history.
 pub fn add_future_hh(&mut self,events:f64)->Result<(),ForwardError>{
  if !events.is_finite()||events<0.0||(self.identity.lambda_bits==0.0_f64.to_bits()&&events!=0.0){return Err(error());}
  for (i,x) in [events,-13.598434599702*events].iter().enumerate(){let y=x-self.future_hh[i+2];let t=self.future_hh[i]+y;self.future_hh[i+2]=(t-self.future_hh[i])-y;self.future_hh[i]=t;}Ok(())
 }
}
