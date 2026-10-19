//! Targeted V15 native SSPRK transport specifications; no legacy suite reruns.
use rei_microphysics::{axbi_covariant_transport::{CovariantTransport,PhotonState},
    axbi_driver::{Driver,DriverConfig},axbi_sources::AxbiSource,
    Absorber,AtomicProvider,AxisymmetricPoint,GeometrySnapshot,HHeModel,ForwardError};
fn close(a:f64,b:f64,t:f64){assert!((a-b).abs()<=t*a.abs().max(b.abs()).max(1e-300),"{a:.17e} != {b:.17e}");}
fn geometry()->GeometrySnapshot{AxisymmetricPoint::new(0.05,0.,1e-16,0.).unwrap().snapshot().unwrap()}
fn core(cells:usize)->CovariantTransport{let s=AxbiSource::new(1.898198450714027e-7,0.2,16,8).unwrap();CovariantTransport::new(&s,geometry(),cells,13.6,512.).unwrap()}
fn broad(c:&CovariantTransport,mean:f64)->PhotonState{let mut s=c.empty_state();s.number[0]=1.;s.energy_ref[0]=mean;s.support_lo[0]=13.6;s.support_hi[0]=100.;c.validate_state(&s).unwrap();s}
#[test]
fn dt_zero_and_zero_opacity_preserve_exact_moments_and_support(){
 let c=core(1);let g=geometry();let s=broad(&c,40.);let p=c.prepare(&s,&g).unwrap();
 for (abs,dt) in [([1e-4,1e-5,3e-6],0.),([0.;3],1e12)]{
  let f=p.evaluate_forward_euler(abs,1e-3,dt).unwrap();assert_eq!(f.state,s);assert_eq!(f.absorbed_per_h,[0.;3]);
  let r=c.absorb_ssprk2(&s,&g,abs,1e-3,dt).unwrap();assert_eq!(r.absorption.state,s);assert_eq!(r.absorption.absorbed_per_h,[0.;3]);assert_eq!(r.absorption.binding_ev_per_h,0.);assert_eq!(r.absorption.heat_ev_per_h,0.);
 }
}
#[test]
fn empty_state_remains_empty(){let c=core(8);let s=c.empty_state();let r=c.absorb_ssprk2(&s,&geometry(),[1e-4;3],1e-3,1e12).unwrap();assert_eq!(r.absorption.state,s);assert_eq!(r.nodes_stage1,0);assert_eq!(r.nodes_stage2,0);assert_eq!(r.absorption.photo.gamma_s,[0.;3]);}
#[test]
fn near_endpoint_and_delta_stay_in_original_support_cone(){
 let c=core(1);let g=geometry();let abs=[1e-4,1e-5,3e-6];
 for mean in [f64::from_bits(13.6_f64.to_bits()+1),40.,f64::from_bits(100_f64.to_bits()-1)]{
  let s=broad(&c,mean);let rate=c.prepare(&s,&g).unwrap().max_node_rate(abs).unwrap();let r=c.absorb_ssprk2(&s,&g,abs,1e-3,0.1/rate).unwrap();c.validate_state(&r.absorption.state).unwrap();assert_eq!(r.absorption.state.support_lo,s.support_lo);assert_eq!(r.absorption.state.support_hi,s.support_hi);
 }
 let mut s=c.empty_state();c.add_delta(&mut s,0,60.,0.7).unwrap();let p=c.prepare(&s,&g).unwrap();let dt=0.3/p.max_node_rate(abs).unwrap();let r=c.absorb_ssprk2(&s,&g,abs,1e-3,dt).unwrap();for k in 0..s.number.len(){if s.number[k]>0.{assert_eq!(r.absorption.state.energy_ref[k],60.*r.absorption.state.number[k]);assert_eq!(r.absorption.state.support_lo[k],60.);assert_eq!(r.absorption.state.support_hi[k],60.);}}
}
#[test]
fn cfl_and_domain_failures_preserve_borrowed_input(){
 let c=core(1);let g=geometry();let s=broad(&c,40.);let before=s.clone();let abs=[1e-4,1e-5,3e-6];let p=c.prepare(&s,&g).unwrap();let dt=1.01/p.max_node_rate(abs).unwrap();
 assert!(matches!(p.evaluate_forward_euler(abs,1e-3,dt),Err(ForwardError::InvalidInput("AXBI_SSP_CFL"))));assert!(matches!(c.absorb_ssprk2(&s,&g,abs,1e-3,dt),Err(ForwardError::InvalidInput("AXBI_SSP_CFL"))));assert_eq!(s,before);
 for dt in [-1.,f64::NAN,f64::INFINITY]{assert!(c.absorb_ssprk2(&s,&g,abs,1e-3,dt).is_err());assert_eq!(s,before);}
}
#[test]
fn native_md14_number_energy_and_species_ledgers_share_owner(){
 let mut cfg=DriverConfig::baseline();cfg.transport_cells=16;cfg.transport_threads=1;cfg.background_panels=128;let(d,_)=Driver::new(cfg).unwrap();let a=1_f64/21.;let g=d.geometry_point(a).unwrap().geometry().unwrap();let nh=d.n_h0_cm3/a.powi(3);let nhe=d.n_he0_cm3/a.powi(3);let abs=[nh*0.925,nhe*0.85,nhe*0.12];let c=&d.transport;let mut s=c.empty_state();c.inject(&mut s,&g,20.,1e10).unwrap();let(n0,u0)=c.inventory(&s,&g).unwrap();let p=c.prepare(&s,&g).unwrap();let dt=0.2/p.max_node_rate(abs).unwrap();let r=c.absorb_ssprk2(&s,&g,abs,nh,dt).unwrap().absorption;let(n,u)=c.inventory(&r.state,&g).unwrap();close(n0-n,r.absorbed_per_h.iter().sum(),2e-12);close(u0-u,r.binding_ev_per_h+r.heat_ev_per_h,2e-12);for j in 0..3{close(r.absorbed_per_h[j],dt*abs[j]/nh*r.photo.gamma_s[j],2e-14);}c.validate_state(&r.state).unwrap();
}
#[test]
fn delta_scalar_ssp_polynomial_and_species_event_formula(){
 let c=core(8);let g=geometry();let mut s=c.empty_state();c.add_delta(&mut s,2,60.,0.7).unwrap();let abs=[1e-4,1e-5,3e-6];let nh=1e-3;let model=HHeModel::controlled_fixture();let ap=AtomicProvider::reference();let sig=[Absorber::HI,Absorber::HeI,Absorber::HeII].map(|a|ap.cross_section(a,60.).unwrap());let rates=sig.map(|v|model.c_cm_s*v);let rate=(0..3).map(|j|abs[j]*rates[j]).sum::<f64>();let tau=0.3;let dt=tau/rate;let r=c.absorb_ssprk2(&s,&g,abs,nh,dt).unwrap();let(n,u)=c.inventory(&r.absorption.state,&g).unwrap();let expected=0.7*(1.-tau+0.5*tau*tau);close(n,expected,3e-15);close(u,60.*expected,3e-15);close(r.max_tau_stage1,tau,3e-15);close(r.max_tau_stage2,tau,3e-15);
 for j in 0..3{let avg=0.7*(1.-0.5*tau);close(r.absorption.absorbed_per_h[j],dt*abs[j]*rates[j]*avg,5e-15);close(r.absorption.photo.gamma_s[j],nh*rates[j]*avg,5e-15);close(r.absorption.photo.heat_erg_per_absorber_s[j],nh*rates[j]*avg*(60.-model.threshold_ev[j])*model.ev_erg,5e-15);}
 close(0.7-n,r.absorption.absorbed_per_h.iter().sum(),4e-15);close(42.-u,r.absorption.binding_ev_per_h+r.absorption.heat_ev_per_h,8e-15);
}
#[test]
fn unabsorbed_cell_is_preserved_exactly_alongside_absorbed_cell(){let c=core(8);let g=geometry();let mut s=c.empty_state();c.add_delta(&mut s,0,20.,0.2).unwrap();c.add_delta(&mut s,0,60.,0.3).unwrap();let abs=[0.,0.,1e-5];let p=c.prepare(&s,&g).unwrap();let r=c.absorb_ssprk2(&s,&g,abs,1e-4,0.2/p.max_node_rate(abs).unwrap()).unwrap();for k in 0..s.number.len(){if s.number[k]>0.&&s.support_hi[k]<54.42{assert_eq!(r.absorption.state.number[k],s.number[k]);assert_eq!(r.absorption.state.energy_ref[k],s.energy_ref[k]);}}}
