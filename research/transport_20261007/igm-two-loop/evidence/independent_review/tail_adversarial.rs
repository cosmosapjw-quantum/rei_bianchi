#[path = "../repo/research/transport_20261007/igm-two-loop/src/tail.rs"]
mod tail;
use tail::{LogPositive as P,characteristic,export};
fn main(){
 let mut n=P::from_log(-750.0).unwrap();
 let mut energy=1000.0;
 let h=0.00025;
 for step in 1..=4 {
  let o=characteristic(n,P::empty(),[1e6,0.0,0.0],h,energy).unwrap().owners;
  let (hi,lo)=o.n.log_parts();
  println!("survivor,{step},{hi:.17e},{lo:.17e}");
  n=o.n;energy*=(-h).exp();
 }
 let n=P::from_log_parts(-1e12,-2.0f64.ln()).unwrap();
 let r=characteristic(n,P::empty(),[3.0,0.0,0.0],0.1,100.0).unwrap();
 let (hi,lo)=r.owners.n.log_parts();
 println!("paired_parent,1,{hi:.17e},{lo:.17e}");
 let n=P::from_log(-750.0).unwrap();
 let o=characteristic(n,P::empty(),[0.0;3],0.0,13.6).unwrap().owners;
 let x=export(o).unwrap().owners;
 assert_eq!(x.outn,n);assert!(x.n.is_empty());assert!(!x.oute.is_empty());
 assert_eq!(x.oute,o.u);assert_eq!(x.oute.readout().unwrap().value,0.0);
 let x=characteristic(P::from_log(-1000.0).unwrap(),P::from_linear(1.0).unwrap(),[1e6,0.0,0.0],0.0001,14.0).unwrap();
 assert!(!x.omitted_addend_bounds.n.is_empty());
 let (hi,lo)=x.owners.n.log_parts();println!("restart,1,{hi:.17e},{lo:.17e}");
 assert!(characteristic(P::from_log(-750.0).unwrap(),P::empty(),[1.0,0.0,0.0],0.1,14.0).is_err());
}
