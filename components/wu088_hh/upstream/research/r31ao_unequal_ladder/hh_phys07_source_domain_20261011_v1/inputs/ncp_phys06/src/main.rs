//! Six bounded nonnative targets only. No old tests or native dispatcher entry.
use hh_phys06_local::*;use hh_phys06_local::energy::*;use hh_phys06_local::uniform::*;
use hh_phys04_candidate::coupled_primary::{Phys04DerivativeExport,PrimaryStage};
fn p(x:f64)->Interval{point(x).unwrap()}fn z()->Interval{p(0.)}fn iv(a:f64,b:f64)->Interval{Interval::new(a,b).unwrap()}
fn c(x:f64)->Jet{Jet::constant(p(x)).unwrap()}fn carry(value:f64,u:f64,v:f64,w:f64)->Jet{let mut j=c(value);j.gradient[4]=p(u);j.gradient[5]=p(v);j.hessian[4][5]=p(w);j.hessian[5][4]=p(w);j}
fn contains(x:Interval,v:f64){assert!(x.lo<=v&&v<=x.hi,"{:?} does not contain {}",x,v)}
fn zero_mat()->Mat{[[z();4];4]}fn idmat()->[[f64;4];4]{std::array::from_fn(|i|std::array::from_fn(|j|if i==j{1.}else{0.}))}
fn key()->Identity{Identity{source:family::bindings::SOURCE_SHA.into(),abi:family::bindings::ABI_SHA.into(),seed:"manufactured-parameter-independent-seed-not-archived".into(),family:"analytic-generic-family".into(),start:1.6e11_f64.to_bits(),terminal:1.6125e11_f64.to_bits(),density:1e-4_f64.to_bits(),leaf_graph:"synthetic exact leaf graph".into(),initial_carry:"full gas/photon/guard UVW fixture".into()}}
fn data()->UniformData{
 let center=[0.5,0.15,0.3,12.];let radius=[0.125,0.03125,0.03125,1.];let x=std::array::from_fn(|i|Interval{lo:sub(p(center[i]),p(radius[i])).unwrap().lo,hi:add(p(center[i]),p(radius[i])).unwrap().hi});let theta=[iv(0.,1.),iv(0.,1.)];let identity=key();
 let domain=Domain{identity:identity.clone(),theta,x,coverage:Coverage::Whole{state:x,theta},regularity:Regularity::ConditionalC2{open_domain_premise:"analytic manufactured polynomial family with open extension".into(),branch_premise:"constant synthetic chart and denominator".into()},denominator_min:p(1.),temperature:iv(45000.,50000.),no_hat_guard_crossing:true};
 let a=std::array::from_fn(|i|std::array::from_fn(|j|p(if i==j{1.}else{0.})));let mut ga=[z();4];let mut gb=ga;let mut gab=ga;ga[0]=iv(-0.01171875,-0.0078125);gb[0]=iv(-0.01953125,-0.015625);gab[0]=p(-0.00390625);
 UniformData{domain,center,radius,gc:[iv(-0.02734375,0.02734375),z(),z(),z()],a,c:CChoice::Fixed(FixedC::from_center(&identity,idmat()).unwrap()),partials:Partials{ga,gb,gab,gya:zero_mat(),gyb:zero_mat(),gyy:[zero_mat();4]}}
}
fn mixed_fixture()->(UniformData,RootBounds,MixedBounds){let d=data();let r=root_arithmetic(&d).unwrap();let mb=mixed(&r,[[iv(-0.125,0.125);4];3]).unwrap();(d,r,mb)}
fn energy_source_projection(){
 let residual=std::array::from_fn(|i|{let mut j=Jet::variable(p((i+1)as f64),i).unwrap();j.gradient[4]=p((i+1)as f64/8.);j.gradient[5]=p(-((i+1)as f64)/16.);j.hessian[4][5]=p((i+1)as f64/32.);j.hessian[5][4]=j.hessian[4][5];j});
 let nh=1e-4;let fhe=0.083;let mut export=Phys04DerivativeExport{residual,photons:vec![carry(1.,-3.,5.,7.)],denominators:vec![carry(2.,1.,2.,4.)],rhs:std::array::from_fn(|_|c(0.)),native_root_certified:false,nonphoto:[c(0.),carry(1e15,2e15,-3e15,4e15),carry(2e15,-1e15,2e15,-3e15),c(0.)],photo_rates:vec![[carry(2.,3.,5.,7.),c(0.),c(0.)]],source_stage:PrimaryStage{n_h_cm3:nh,f_he:fhe,h_mean_per_s:1e-14},energy_leaves:vec![100.],stored_n_he:nh*fhe,dt:1.};
 let e=hh_phys06_local::energy::export(&export).unwrap();assert!(!e.native_authority);assert_eq!(e.epsilon[0][0],-2_f64.powi(-48));contains(e.psi.value,-2.*2_f64.powi(-48));contains(e.psi.gradient[4],-3.*2_f64.powi(-48));contains(e.psi.hessian[4][5],-7.*2_f64.powi(-48));assert!(mag(e.j_norm.hessian[4][5])>0.);
 let ell=[CHI[0],fhe*CHI[1],fhe*(CHI[1]+CHI[2]),1.];let scalar=(0..4).map(|i|ell[i]*(i+1)as f64).sum::<f64>();contains(e.ell_g.value,scalar);contains(e.ell_g.gradient[4],scalar/8.);contains(e.ell_g.gradient[5],-scalar/16.);contains(e.ell_g.hessian[4][5],scalar/32.);
 for i in 0..4{for j in 0..4{contains(e.transformed[i].gradient[j],if i==j{1.}else{0.});}}let sq=matmul(&e.s,&e.q).unwrap();for i in 0..4{for j in 0..4{contains(sq[i][j],if i==j{1.}else{0.});}}
 let ci=transform_c(idmat(),&e.s,&e.q).unwrap();for i in 0..4{for j in 0..4{contains(ci[i][j],if i==j{1.}else{0.});}}
 // Quotient carries both incoming cross terms, including at zero stock.
 let n=carry(0.,-3.,5.,7.);let den=carry(2.,1.,2.,4.);let photon=n.div(&den).unwrap();contains(photon.gradient[4],-1.5);contains(photon.gradient[5],2.5);contains(photon.hessian[4][5],3.75);
 export.denominators[0].value=iv(-1.,1.);assert!(hh_phys06_local::energy::export(&export).is_err());assert!(heat_epsilon(f64::NAN,CHI[0]).is_err());
}
fn uniform_contract_binding(){
 let d=data();let r=root_arithmetic(&d).unwrap();assert!(!r.native_authority());assert!(request_native_certificate().is_err());assert!(actual_physical_values().iter().all(Option::is_none));
 let mut bad=d.clone();bad.domain.coverage=Coverage::Point;assert!(root_arithmetic(&bad).is_err());bad.domain.coverage=Coverage::BooleanClaim(true);assert!(root_arithmetic(&bad).is_err());bad=d.clone();bad.domain.regularity=Regularity::BooleanClaim(true);assert!(root_arithmetic(&bad).is_err());
 bad=d.clone();bad.domain.identity.source.push('x');assert!(root_arithmetic(&bad).is_err());bad=d.clone();bad.domain.identity.terminal+=1;assert!(root_arithmetic(&bad).is_err());bad=d.clone();if let Coverage::Whole{theta,..}=&mut bad.domain.coverage{theta[0]=iv(0.,0.5);}assert!(root_arithmetic(&bad).is_err());bad=d.clone();bad.domain.identity.initial_carry.push('x');assert!(root_arithmetic(&bad).is_err());
 let c=match d.c{CChoice::Fixed(c)=>c,_=>unreachable!()};assert_eq!(c.centre_bits(),idmat().map(|r|r.map(f64::to_bits)));
}
fn uniform_strict_margins(){
 let d=data();let r=root_arithmetic(&d).unwrap();assert!(r.q().hi<1.);assert!(r.margins().iter().all(|x|x.lo>0.));
 for k in 0..7{let mut b=d.clone();match k{0=>b.radius[0]=0.,1=>b.gc[0]=p(b.radius[0]),2=>b.a[0][0]=p(0.),3=>b.c=CChoice::VariableClaim,4=>b.domain.denominator_min=iv(-1.,1.),5=>b.domain.x[3]=iv(-1.,1.),_=>b.domain.temperature=iv(34000.,50000.)};assert!(root_arithmetic(&b).is_err());}
 assert!(linear(&r,[p(1.);4],[iv(-0.1,0.1);4]).is_err());
 // Non-diagonal interval matrix: strict Krawczyk linear inclusion, no scalar inverse assumption.
 let mut nd=d.clone();nd.a[0][1]=iv(0.124,0.126);let mut jc=idmat();jc[0][1]=0.125;nd.c=CChoice::Fixed(FixedC::from_center(&nd.domain.identity,jc).unwrap());let nr=root_arithmetic(&nd).unwrap();let l=linear(&nr,[p(0.01),p(0.02),z(),z()],[iv(-0.1,0.1);4]).unwrap();contains(l.enclosure()[0],0.0075);contains(l.image()[1],0.02);
}
fn mixed_incoming_chain(){
 // Independent prescribed mixed coefficients; no nonlinear solve or physical RHS.
 for n0 in [0.,1.]{let n=carry(n0,-3.,5.,7.);let d=carry(2.,1.,2.,4.);let photon=n.div(&d).unwrap();let p0=n0/2.;let pa=(-3.-p0)/2.;let pb=(5.-2.*p0)/2.;let pab=(7.-4.*p0-2.*pa-pb)/2.;contains(photon.value,p0);contains(photon.gradient[4],pa);contains(photon.gradient[5],pb);contains(photon.hessian[4][5],pab);
 let gas=carry(0.5,0.03125,-0.0625,0.125);let stock=photon.mul(&c(0.125)).unwrap();let old=gas.sub(&stock).unwrap();let residual=gas.sub(&old).unwrap().sub(&stock).unwrap();contains(residual.hessian[4][5],0.);let mut erased=old.clone();erased.hessian[4][5]=z();erased.hessian[5][4]=z();let wrong=gas.sub(&erased).unwrap().sub(&stock).unwrap();assert!(mag(wrong.hessian[4][5])>0.01);
 let gn=carry(2.,-3.,4.,-5.);let gu=gn.mul(&c(10.)).unwrap();let half2=gn.clone();assert_eq!(half2.gradient[4].lo,gn.gradient[4].lo);contains(gu.hessian[4][5],-50.);
 }
 let(d,_,m)=mixed_fixture();contains(m.w().enclosure()[0],0.00390625);contains(m.forcing()[0],0.00390625);assert!(!m.w().native_authority());
 // Every Hessian/cross forcing term discriminated by independent scalar sum.
 let mut p=d.partials.clone();p.gab[0]=pnt(2.);p.gya[0][0]=pnt(3.);p.gyb[0][0]=pnt(5.);p.gyy[0][0][0]=pnt(7.);let mut u=[z();4];let mut v=u;u[0]=pnt(-2.);v[0]=pnt(4.);contains(forcing(&p,u,v).unwrap()[0],52.);
}
fn pnt(x:f64)->Interval{p(x)}
fn finite_observable_coverage(){
 let(d,_,m)=mixed_fixture();let f=finite(&m,d.domain.theta).unwrap();contains(f.enclosure[0],0.00390625);assert!(!f.native_authority);assert!(finite(&m,[iv(0.,0.5),iv(0.,1.)]).is_err());
 // y_i=center_i+lambda+b on Theta=[0,1/128]^2,
 // O=(y_0-center_0)^2: W=0 but O_yy[U,V]=2.
 // Gc=-lambda-b in every component fits the unchanged physical state box.
 let mut dat=data();dat.domain.theta=[iv(0.,1./128.);2];dat.domain.coverage=Coverage::Whole{state:dat.domain.x,theta:dat.domain.theta};dat.gc=[iv(-1./64.,0.);4];dat.partials.ga=[p(-1.);4];dat.partials.gb=[p(-1.);4];dat.partials.gab=[z();4];let root=root_arithmetic(&dat).unwrap();let mb=mixed(&root,[[iv(0.99,1.01);4],[iv(0.99,1.01);4],[iv(-0.01,0.01);4]]).unwrap();let mut h=zero_mat();h[0][0]=p(2.);let mut gradient=[z();4];gradient[0]=iv(-0.5,0.5); // whole-X bound for 2*(y0-center0), not a center sample
 let o=ObservablePartials{gradient,hessian:h,explicit_ab:z(),gas_a:[z();4],gas_b:[z();4]};contains(observable(&mb,&o).unwrap(),2.);contains(finite_observable(&mb,&o,dat.domain.theta).unwrap(),2./16384.);
 let explicit=ObservablePartials{gradient:[z();4],hessian:zero_mat(),explicit_ab:p(3.),gas_a:[p(2.);4],gas_b:[p(-1.);4]};contains(observable(&mb,&explicit).unwrap(),7.);
}
fn paired_difference_binding(){
 let(d,r,m)=mixed_fixture();let mut da=zero_mat();da[0][0]=p(0.25);let mut df=[z();4];df[0]=p(0.001);let before=hh_phys04_candidate::paired_runtime::phys04_native_counts();let bound=paired(&r,&m,da,df,[iv(-0.1,0.1);4],"analytic shared-parameter delta witness; full mixed range retained").unwrap();assert!(!bound.native_authority);contains(bound.forcing[0],0.001-0.25*0.00390625);
 let mut changed=d.clone();changed.domain.identity.terminal+=1;changed.c=CChoice::Fixed(FixedC::from_center(&changed.domain.identity,idmat()).unwrap());let bad=root_arithmetic(&changed).unwrap();assert!(paired(&bad,&m,da,df,[iv(-1.,1.);4],"joint").is_err());assert!(paired(&r,&m,da,df,[iv(-1.,1.);4],"").is_err());assert_eq!(hh_phys04_candidate::paired_runtime::phys04_native_counts(),before);
 let mut changed=d.clone();changed.domain.identity.seed.push('x');changed.c=CChoice::Fixed(FixedC::from_center(&changed.domain.identity,idmat()).unwrap());let bad=root_arithmetic(&changed).unwrap();assert!(paired(&bad,&m,da,df,[iv(-1.,1.);4],"joint").is_err());
}
fn main(){let name=std::env::args().nth(1).expect("one explicit nonnative target required");let before=hh_phys04_candidate::paired_runtime::phys04_native_counts();assert_eq!(before,[0;4]);match name.as_str(){"energy_source_projection"=>energy_source_projection(),"uniform_contract_binding"=>uniform_contract_binding(),"uniform_strict_margins"=>uniform_strict_margins(),"mixed_incoming_chain"=>mixed_incoming_chain(),"finite_observable_coverage"=>finite_observable_coverage(),"paired_difference_binding"=>paired_difference_binding(),_=>panic!("unknown target; no native execution mode")};assert_eq!(hh_phys04_candidate::paired_runtime::phys04_native_counts(),before);assert_eq!(hh_phys04_candidate::coupled_primary::phys04_arithmetic_counts(),[0;3]);println!("{{\"target\":\"{}\",\"status\":\"PASS\",\"scope\":\"MANUFACTURED_NONNATIVE_CONDITIONAL_ARITHMETIC\",\"native_counts\":{:?},\"phys04_callback_counts\":{:?},\"energy_exports\":{},\"uniform_linear_counts\":{:?}}}",name,before,hh_phys04_candidate::coupled_primary::phys04_arithmetic_counts(),export_count(),counts());}
