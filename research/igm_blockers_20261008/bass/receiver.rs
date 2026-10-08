#[path="source/frame.rs"] mod frame;
#[path="source/visibility.rs"] mod visibility;
#[path="source/visibility_clock.rs"] mod visibility_clock;
use std::io::{self,Read};
fn vector(v:&[f64])->String {format!("[{}]",v.iter().map(|x|format!("{x:.17e}")).collect::<Vec<_>>().join(","))}
fn main(){let mut s=String::new();io::stdin().read_to_string(&mut s).unwrap();let v:Vec<f64>=s.split_whitespace().map(|x|x.parse().unwrap()).collect();assert_eq!(v.len(),14);let f=frame::MaterialFrame::new([0.;3]).unwrap();let mut rates=Vec::new();let mut ne=Vec::new();for i in 0..2{let a=&v[3+i*5..8+i*5];let e=visibility::ElectronState::new(a[0],a[1],a[2],a[3],a[4]).unwrap();ne.push(e.number_density_m3());rates.push(e.scattering_rate_per_normal_second(f,[1.,0.,0.]).unwrap());}let r=visibility_clock::integrate_clock_visibility(visibility_clock::RayClockGrid::NormalSeconds{edges_seconds:&v[..3]},&rates,v[13]).unwrap();println!("{{\"ne_m3\":{},\"rates\":{},\"tau\":{},\"survival\":{},\"mass\":{}}}",vector(&ne),vector(&rates),vector(&r.visibility.optical_depth),vector(&r.visibility.survival),vector(&r.visibility.interval_probability));}
