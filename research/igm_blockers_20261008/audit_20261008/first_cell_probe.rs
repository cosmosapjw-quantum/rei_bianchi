#![allow(dead_code)]
extern crate self as canonical;
#[path="/home/cosmosapjw/rei_worktrees/igm-rate-export01-20261008/research/igm_blockers_20261008/numeric/source/rei-next-nodes/canonical/src/primitives.rs"] mod core;
pub use core::{Tracked,Wide};
#[path="/home/cosmosapjw/rei_worktrees/igm-rate-export01-20261008/research/igm_blockers_20261008/numeric/source/rei-next-nodes/short-hhe-midpoint/src/canonical_owner.rs"] mod owner;
use rei_microphysics::{audit_counts,igm_background::{FlatFlrwConfig,FlatFlrwBackground},igm_state::IgmGasState,igm_photo::packet_opacity};
fn main(){
 let a:f64=-2.56445769079487;let b:f64=-2.5644493574615366;let eta:f64=0.05244705397124411;let f:f64=2.509215666667852e-296;let y=[0.006889756014935459,0.023189081258542812,7.706744884716575e-05];let thermal:f64=2.1177800545386836e-13;
 let background=FlatFlrwBackground::new(FlatFlrwConfig{h0_per_s:2.2e-18,omega_r:9e-5,omega_m:0.3,omega_b:0.048,omega_lambda:0.69991,helium_mass_fraction:0.24,tcmb0_k:2.7255,ln_a_min:-13f64.ln(),ln_a_max:-11f64.ln(),parameter_source:"existing igm_manufactured_z12_to10.cfg".to_string()}).unwrap();
 let p=background.at_ln_a((a+b)*0.5).unwrap();let gas=IgmGasState::new(y,thermal).unwrap();let stage_e=(eta-(a+b)*0.5).exp();let rates=packet_opacity(&gas,stage_e,p.n_h_cm3,p.n_he_cm3).unwrap().map(|x|x/p.hubble_per_s);
 let es=(eta-a).exp();let o=owner::kernel(f,0.,rates,b-a,es).unwrap();let heat=o.be[0]-owner::EPS*owner::CHI[0]*o.an[0];let expected=3.812277937532397e-309f64;
 println!("SOURCE HEAD=ddf125732854f4365e000b013c4bb78970ac6fcd CHECKPOINT coarse/k11 NODE=0 NEWTON_TRIAL=old.y");
 println!("inputs f={f:.17e} a={a:.17e} b={b:.17e} eta={eta:.17e} E={es:.17e} rates={rates:?}");
 println!("N_next={:.17e} U_next={:.17e} red={:.17e} A={:?} B={:?}",o.n,o.u,o.red,o.an,o.be);
 println!("HI_HEAT={heat:.17e} bits={:016x} MATCH_FAILURE={} INPUT_NORMAL={} NEXT_N_NORMAL={} NEXT_U_NORMAL={}",heat.to_bits(),heat.to_bits()==expected.to_bits(),f.is_normal(),o.n.is_normal(),o.u.is_normal());
 println!("OWNER_BEFORE_HEAT_VALID={:?}",owner::try_add_scaled(&mut owner::Owners::default(),o,1.));
 println!("COUNTS_RHS_SIGMA={:?} KERNEL_CALLS=1 COUPLED_ADVANCES=0 OBSERVERS=0 HISTORY_WRITES=0",audit_counts::read());
 assert_eq!(heat.to_bits(),expected.to_bits());assert_eq!(audit_counts::read(),(0,3));
}
