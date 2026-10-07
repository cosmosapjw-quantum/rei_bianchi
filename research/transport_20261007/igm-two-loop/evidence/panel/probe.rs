#[allow(dead_code)]
#[path="../../repo/research/transport_20261007/igm-two-loop/src/panel.rs"] mod panel;
use panel::{Panel,Family};
fn main(){
 println!("family,l,r,beta,ln_n,a,b,ln_fraction,normalized_mean,mean_eta,mean_exp_eta,panels,error");
 for l in [-32.0,-8.0,0.0,2.6100697927420065,16.0] {
 for width in [1.0001e-7,0.01,1.0,16.0] {
 let r=l+width;if r>32.0 {continue;}
 for beta in [-128.0,-width,0.0,32.0,128.0] {
 for (family,id) in [(Family::Ordinary,0),(Family::RightFront,1)] {
 let p=Panel{l,r,beta,family,ln_n:-1000.0};
 for (a,b) in [(l,r),(l,l+(r-l)*0.375),(l+(r-l)*0.625,r)] {
 let x=p.restrict(a,b).unwrap().unwrap();
 println!("{id},{l:.17e},{r:.17e},{beta:.17e},{:.17e},{a:.17e},{b:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{},{:.17e}",p.ln_n,x.ln_fraction,x.normalized_mean,x.mean_eta,x.mean_exp_eta,x.panels,x.convergence_error);
 }
 }
 }
 }
 }
 let p=Panel{l:0.0,r:1.0,beta:128.0,family:Family::RightFront,ln_n:-1000.0};
 let a=f64::from_bits(1.0_f64.to_bits()-1);let x=p.restrict(a,1.0).unwrap().unwrap();
 println!("1,0,1,128,-1000,{a:.17e},1,{:.17e},{:.17e},{:.17e},{:.17e},{},{:.17e}",x.ln_fraction,x.normalized_mean,x.mean_eta,x.mean_exp_eta,x.panels,x.convergence_error);
}
