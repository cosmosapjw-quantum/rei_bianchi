#[path="../src/family.rs"] mod family;
use family::*;use hh_phys04_candidate::{Interval,Jet};
use hh_phys04_candidate::coupled_primary::*;
use hh_phys04_candidate::paired_runtime::*;
fn p(x:f64)->Interval{Interval::point(x).unwrap()}
fn c(x:f64)->Jet{Jet::constant(p(x)).unwrap()}
fn carries(v:f64,u:f64,b:f64,w:f64)->Jet{phys04_carry(p(v),p(u),p(b),p(w)).unwrap()}
fn contains(v:Interval,x:f64)->bool{v.lo<=x&&x<=v.hi}
fn identity(lambda:f64,b:f64)->FamilyIdentity {FamilyIdentity{archive_sha256:"678f967f0d50ad1fff47a73e2e63193429b708246cd84ca8ffc72191c31b522b".into(),candidate_source_sha256:family::bindings::SOURCE_SHA.into(),abi_sha256:family::bindings::ABI_SHA.into(),theta_bits:[1e-14_f64.to_bits();3],clock_bits:1.6e11_f64.to_bits(),lambda_bits:lambda.to_bits(),b_bits:b.to_bits()}}
#[test] fn CommonStateHistory(){
 let bytes=include_bytes!("../inputs/COMMON_SEED_MEMBER1.bin");let config=rei_reference::paired_runtime::HhRunConfig::new(rei_reference::paired_runtime::PairedConfig{spectral_subdivisions:8,n_mu:8,n_phi:16},[1e-14;3],rei_reference::coupled_primary::HhMode::Lcs91).unwrap();
 let mut families=Vec::new();for (l,b) in [(1.,1.),(1.,0.),(0.,1.),(0.,0.)] {let f=CommonFamily::initialize(bytes,&config,identity(l,b)).unwrap();assert_eq!(f.archived_roundtrip().unwrap(),bytes);assert_eq!(f.original_bytes(),bytes);assert_eq!(f.photons.len(),4224);assert_eq!(f.guard_n.len(),128);assert!(f.photons.iter().flat_map(|j|j.gradient).all(|x|x.lo==0.0&&x.hi==0.0));assert_eq!(f.future_hh,[0.0;4]);families.push(f);}
 for f in &families[1..]{assert_eq!(format!("{:?}",f.physical),format!("{:?}",families[0].physical));assert_eq!(f.historical_hh.map(f64::to_bits),families[0].historical_hh.map(f64::to_bits));}
 assert!(families[0].historical_hh[0]>0.0);let old=families[2].total_hh();assert!(families[2].add_future_hh(0.001).is_err());assert_eq!(families[2].total_hh(),old);assert_eq!(families[1].future_birth_rate(),0.0);
 let old=families[0].historical_hh;families[0].add_future_hh(0.001).unwrap();assert_eq!(families[0].historical_hh,old);
 let mut corrupt=bytes.to_vec();corrupt[40]^=1;assert!(CommonFamily::initialize(&corrupt,&config,identity(1.,1.)).is_err());
 println!("COMMON_SEED_READ_ONLY time={} history={:?} photon_sum={:.17e} guard_n_sum={:.17e} energy_comp={:.17e}",families[0].physical.time_s,old,families[0].physical.photons.iter().sum::<f64>(),families[0].physical.lower_guard_n.iter().sum::<f64>(),families[0].physical.energy_comp);
}
#[test] fn PhotonZeroStockSignedMixed(){
 let stage=PrimaryStage{n_h_cm3:1e-4,f_he:0.083,h_mean_per_s:1e-14};let y=[c(0.8),c(0.2),c(0.4),c(12.)];let n=carries(0.,-0.003,0.01,-0.002);let lam=phys04_parameter(p(0.4),4).unwrap();
 let o=phys04_reduced_residual(&stage,&y,&y,&[n],&[13.7],&lam,1e7).unwrap();let d=o.denominators[0].value;let ph=&o.photons[0];assert!(ph.gradient[4].hi<0.0&&ph.gradient[5].lo>0.0&&ph.hessian[4][5].hi<0.0);
 assert!(contains(ph.gradient[4],-0.003/((d.lo+d.hi)/2.)));assert!(contains(ph.hessian[4][5],-0.002/((d.lo+d.hi)/2.)));
 let numerator=carries(2.,-1.,3.,-2.);let denominator=carries(4.,0.5,-0.25,0.75);let q=numerator.div(&denominator).unwrap();let qa=(-1.-0.5*0.5)/4.;let qb=(3.-0.5*(-0.25))/4.;let qab=(-2.-0.5*0.75-qa*(-0.25)-qb*0.5)/4.;assert!(contains(q.hessian[4][5],qab));
}
#[test] fn LinkedHalfMixedCarry(){
 let stage=PrimaryStage{n_h_cm3:1e-4,f_he:0.083,h_mean_per_s:1e-14};let values=[0.8,0.2,0.4,12.];let old=values.map(|v|carries(v,0.02,-0.01,0.003));let stock=[carries(0.05,-0.003,0.01,-0.002)];let boxes=[[Interval{lo:-1.,hi:1.};4];3];
 let first=phys04_mixed_at_box(&stage,&old,values.map(p),&stock,&[13.7],p(0.4),1e7,boxes).unwrap();assert!(first.contraction<1.0&&!first.native_root_certified);
 let linked=std::array::from_fn(|i|phys04_carry(p(values[i]),first.u[i],first.v[i],first.w[i]).unwrap());
 let second=phys04_mixed_at_box(&stage,&linked,values.map(p),&first.photons,&[13.7],p(0.4),1e7,boxes).unwrap();
 let reset=values.map(c);let reset_photons=first.photons.iter().map(|j|Jet::constant(j.value).unwrap()).collect::<Vec<_>>();let wrong=phys04_mixed_at_box(&stage,&reset,values.map(p),&reset_photons,&[13.7],p(0.4),1e7,boxes).unwrap();assert!(second.u[0].lo>wrong.u[0].hi);assert!(second.w[0].lo>wrong.w[0].hi);
 assert_eq!(phys04_native_counts(),[0;4]);println!("LINKED_SOURCE_ARITHMETIC_COUNTS {:?} native={:?}",phys04_arithmetic_counts(),phys04_native_counts());
}
#[test] fn OrderedRemapAndGuardChart(){
 let cfg=PairedConfig{spectral_subdivisions:8,n_mu:8,n_phi:16};let gas=[c(0.8),c(0.2),c(0.4),c(12.)];let mut photons=vec![c(0.);4224];photons[0]=carries(0.001,-0.002,0.003,-0.004);photons[24]=carries(0.01,0.02,-0.03,0.04);let guard=vec![c(0.);128];let b=phys04_parameter(p(0.),5).unwrap();
 let full=phys04_prepare_family(&cfg,[1e-14;3],1.6e11,1.25e9,&gas,&photons,&guard,&guard,&b).unwrap();assert_eq!(full.guard_exports,128);assert!(full.guard_n[0].gradient[4].hi<0.);assert!(full.guard_u[0].hessian[4][5].hi<0.);assert!(full.source_n.gradient[5].lo>0.&&full.source_n.gradient[4].lo<=0.&&full.source_n.gradient[4].hi>=0.);
 full.validate_family_input([1e-14;3],1.6e11,1.25e9,&gas,&photons,&guard,&guard,p(0.)).unwrap();
 assert!(full.validate_family_input([1e-14;3],1.6e11,1.25e9,&gas,&photons,&guard,&guard,Interval{lo:0.,hi:1.}).is_err());
 assert!(full.validate_family_input([1.01e-14,0.99e-14,1e-14],1.6e11,1.25e9,&gas,&photons,&guard,&guard,p(0.)).is_err());
 let mut forged=full.clone();forged.groups[24].value=p(1.0);assert!(forged.validate_family_input([1e-14;3],1.6e11,1.25e9,&gas,&photons,&guard,&guard,p(0.)).is_err());
 assert!(full.photons[24].value.lo>0.0);assert!(full.groups[24].hessian[4][5].lo>0.0);assert_eq!(full.energies[16].to_bits(),13.6_f64.to_bits());
 let half=phys04_prepare_family(&cfg,[1e-14;3],1.6e11,6.25e8,&gas,&photons,&guard,&guard,&b).unwrap();let after=phys04_distribute_after_be(&half,&gas).unwrap();let half2=phys04_prepare_family(&cfg,[1e-14;3],half.time_s,6.25e8,&gas,&after,&half.guard_n,&half.guard_u,&b).unwrap();assert!(half2.guard_n[0].gradient[4].hi<0.);assert!(half2.guard_u[0].hessian[4][5].hi<0.);assert_eq!(half2.gas[0].value.lo,gas[0].value.lo);
 let provider=hh_phys04_candidate::AtomicProvider::reference();for e in &full.energies[..16]{assert_eq!(provider.cross_section(hh_phys04_candidate::Absorber::HI,*e).unwrap(),0.0);}
 // Inactive cannot return to active for positive H; guard remains outside quotient.
 let h=1e-14_f64;let dt=1.25e9_f64;let sh=-(-h*dt/2.).exp_m1()/h;let sf=-(-h*dt).exp_m1()/h;assert!((2.*sh-h*sh*sh-sf).abs()<1e-6);
 let node=full.energies[24];let prev=full.energies[23];let alpha=h*node/(node-prev);let l=-alpha;let full_weight=1.+sf*l;let two_weight=(1.+sh*l).powi(2);let defect=sh*sh*(l*l+h*l);assert!((two_weight-full_weight-defect).abs()<3e-16);
}
