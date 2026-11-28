pub mod family;
pub mod certificate;
pub mod energy;
pub mod uniform;
pub mod adapter;
pub use hh_phys04_candidate::{Interval,Jet};
pub type R<T> = Result<T,&'static str>;
pub fn point(x:f64)->R<Interval>{Interval::point(x).map_err(|_|"invalid interval leaf")}
pub fn add(a:Interval,b:Interval)->R<Interval>{a.add(&b).map_err(|_|"interval add")}
pub fn sub(a:Interval,b:Interval)->R<Interval>{a.sub(&b).map_err(|_|"interval sub")}
pub fn mul(a:Interval,b:Interval)->R<Interval>{a.mul(&b).map_err(|_|"interval mul")}
pub fn div(a:Interval,b:Interval)->R<Interval>{a.div(&b).map_err(|_|"interval div")}
pub fn neg(a:Interval)->R<Interval>{a.neg().map_err(|_|"interval neg")}
pub fn valid(a:Interval)->R<()>{Interval::new(a.lo,a.hi).map(|_|()).map_err(|_|"invalid interval")}
pub fn same(a:Interval,b:Interval)->bool{a.lo.to_bits()==b.lo.to_bits()&&a.hi.to_bits()==b.hi.to_bits()}
pub fn mag(a:Interval)->f64{a.lo.abs().max(a.hi.abs())}
