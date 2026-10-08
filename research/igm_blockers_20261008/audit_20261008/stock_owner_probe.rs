#![allow(dead_code)]
extern crate self as canonical;
#[path="/home/cosmosapjw/rei_worktrees/igm-rate-export01-20261008/research/igm_blockers_20261008/numeric/source/rei-next-nodes/canonical/src/primitives.rs"] mod core;
pub use core::{Tracked,Wide};
#[path="/home/cosmosapjw/rei_worktrees/igm-rate-export01-20261008/research/igm_blockers_20261008/numeric/source/rei-next-nodes/short-hhe-midpoint/src/canonical_owner.rs"] mod owner;
fn main(){
 let mut x=owner::Owners::default();
 owner::try_add_scaled(&mut x,owner::Owners{red:1.,..Default::default()},1.).unwrap();
 x.n=1.;x.u=2.;
 let mut total=owner::Owners::default();
 println!("REPLAY_DIRECT_STOCK_ASSIGNMENT={:?}",owner::try_add_scaled(&mut total,x,1.));
 let a=Tracked::from_f64(0.1).unwrap();let b=Tracked::from_f64(0.3).unwrap();let c=a.mul(b).unwrap();
 println!("BARE_TRACKED_PRODUCT_BITS={} LOSS_EMPTY={}",c.readout().unwrap().0.to_bits(),c.loss.is_empty());
 let mut o=owner::Owners::default();owner::try_add_scaled(&mut o,owner::Owners{red:0.3,..Default::default()},0.1).unwrap();let original=owner::owner_bounds(o).unwrap()[2];owner::replace_owner_components(&mut o,&[2]).unwrap();let replaced=owner::owner_bounds(o).unwrap()[2];
 println!("REPLACEMENT_LOSS old={:?} new={:?}",original,replaced);
}
