//! Admissible synthetic candidate; evaluates callbacks only, not roots or trajectory.
use hh_phys04_candidate::{Interval,Jet};
use hh_phys04_candidate::coupled_primary::*;
pub fn derivative_probe(){
 let p=|x|Interval::point(x).unwrap();let c=|x|Jet::constant(p(x)).unwrap();
 let values=[0.8,0.2,0.4,12.0];let u=[0.02,-0.01,0.03,0.2];let v=[-0.01,0.02,-0.01,0.3];
 let old=values.map(c);let mut gas=std::array::from_fn(|i|Jet::variable(p(values[i]),i).unwrap());
 for i in 0..4 {gas[i].gradient[4]=p(u[i]);gas[i].gradient[5]=p(v[i]);}
 let energies=[13.7,35.0,70.0];let n=[0.05,0.005,0.001];let na=[-0.003,0.0002,-0.0001];let nb=[0.01,-0.0003,0.0002];let nab=[0.002,-0.0001,0.00004];
 let incoming=(0..3).map(|i|phys04_carry(p(n[i]),p(na[i]),p(nb[i]),p(nab[i])).unwrap()).collect::<Vec<_>>();
 let stage=PrimaryStage{n_h_cm3:1e-4,f_he:0.083,h_mean_per_s:1e-14};let lam=phys04_parameter(p(0.4),4).unwrap();
 let out=phys04_reduced_residual(&stage,&old,&gas,&incoming,&energies,&lam,1e7).unwrap();
 let box_=|x:Interval|format!("[{:.17e},{:.17e}]",x.lo,x.hi);
 let emit=|j:&Jet|format!("{{\"value\":{},\"gradient\":[{}],\"hessian\":[{}]}}",box_(j.value),j.gradient[..6].iter().map(|x|box_(*x)).collect::<Vec<_>>().join(","),j.hessian[..6].iter().map(|r|format!("[{}]",r[..6].iter().map(|x|box_(*x)).collect::<Vec<_>>().join(","))).collect::<Vec<_>>().join(","));
 let provider=hh_phys04_candidate::AtomicProvider::reference();let sig=energies.iter().map(|e|[hh_phys04_candidate::Absorber::HI,hh_phys04_candidate::Absorber::HeI,hh_phys04_candidate::Absorber::HeII].map(|a|provider.cross_section(a,*e).unwrap())).collect::<Vec<_>>();
 println!("{{\"scope\":\"SYNTHETIC_REAL_FT03_LCS_CALLBACK_NO_ROOT\",\"sigma\":{:?},\"rhs\":[{}],\"photons\":[{}],\"native_counts\":{:?},\"arithmetic_counts\":{:?}}}",sig,out.rhs.iter().map(emit).collect::<Vec<_>>().join(","),out.photons.iter().map(emit).collect::<Vec<_>>().join(","),hh_phys04_candidate::paired_runtime::phys04_native_counts(),phys04_arithmetic_counts());
}
