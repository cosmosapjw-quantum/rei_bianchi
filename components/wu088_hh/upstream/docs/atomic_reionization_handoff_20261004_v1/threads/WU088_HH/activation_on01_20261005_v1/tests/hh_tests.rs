use crate::*;
use crate::hh_optin::{self,events,HhProvider as P,HhSelection as S};
fn setup(t:f64,h:f64,he:[f64;2])->(Ft03Model,HHeState){
 let m=Ft03Model::controlled().unwrap(); let mut s=m.initial_state();s.fractions=[h,he[0],he[1]];
 let ne=m.gas.n_h_cm3*h+m.gas.n_he_cm3*(he[0]+2.0*he[1]);
 s.u_erg_cm3=1.5*m.gas.kb_erg_k*t*(m.gas.n_h_cm3+m.gas.n_he_cm3+ne); (m,s)
}
fn close(a:f64,b:f64){assert!((a-b).abs()<=3e-12*b.abs().max(1e-300),"{a:e} != {b:e}");}
fn same(a:Ft03Rhs,b:Ft03Rhs){
 for i in 0..7{assert_eq!(a.derivative[i].to_bits(),b.derivative[i].to_bits());}
 assert_eq!(a.escaped_energy_rate.to_bits(),b.escaped_energy_rate.to_bits());
 for i in 0..3 {assert_eq!(a.collision_per_cm3_s[i].to_bits(),b.collision_per_cm3_s[i].to_bits());assert_eq!(a.recombination_per_cm3_s[i].to_bits(),b.recombination_per_cm3_s[i].to_bits());
 for j in 0..3{assert_eq!(a.photo_per_cm3_s[i][j].to_bits(),b.photo_per_cm3_s[i][j].to_bits());}}
 for i in 0..2{assert_eq!(a.dr_per_cm3_s[i].to_bits(),b.dr_per_cm3_s[i].to_bits());}
}
#[test]fn lcs_value(){close(P::Lcs91.rate(50000.0).unwrap().k_cm3_s,2.224907020287297e-13);}
#[test]fn corrected_ks_value(){close(P::CorrectedKs.rate(50000.0).unwrap().k_cm3_s,2.214494339455798e-15);}
#[test]fn unit_conversion(){let k=P::Lcs91.rate(50000.0).unwrap();close(k.k_m3_s,k.k_cm3_s*1e-6);}
#[test]fn derivative_jet_positive(){let r=P::Lcs91.rate(50000.0).unwrap(); assert!(r.d1>0.0&&r.d2>0.0);close(r.d1/r.k_cm3_s,(1.2+157800.0/50000.0)/50000.0);}
#[test]fn exact_rate_window_endpoints(){assert!(P::Lcs91.rate(35000.0).unwrap().k_cm3_s>0.0);assert!(P::CorrectedKs.rate(60000.0).unwrap().k_cm3_s>0.0);}
#[test]fn cutoff_is_rejected_not_smoothed(){assert_eq!(P::Lcs91.rate(3000.0).unwrap_err().code(),"HH_TEMPERATURE_DOMAIN");}
#[test]fn outside_temperature(){for t in [34999.0,60001.0,0.0,-1.0,f64::NAN,f64::INFINITY]{assert_eq!(P::CorrectedKs.rate(t).unwrap_err().code(),"HH_TEMPERATURE_DOMAIN");}}
#[test]fn neutral_hh_is_not_electron_gated(){let r=events(P::Lcs91,50000.0,1e-4,0.0,2e-11).unwrap();assert!(r.events_cm3_s>0.0);}
#[test]fn fully_ionized_is_exact_zero(){let r=events(P::Lcs91,50000.0,1e-4,1.0,2e-11).unwrap();assert_eq!(r.events_cm3_s,0.0);assert_eq!(r.thermal_erg_cm3_s,0.0);}
#[test]fn zero_density_is_exact_zero(){let r=events(P::Lcs91,50000.0,0.0,0.3,2e-11).unwrap();assert_eq!(r.events_cm3_s,0.0);assert_eq!(r.per_h_s,0.0);}
#[test]fn no_extra_half(){let r=events(P::Lcs91,50000.0,2.0,0.5,2e-11).unwrap();close(r.events_cm3_s,r.rate.k_cm3_s);}
#[test]fn density_squared(){let a=events(P::Lcs91,50000.0,1e-4,0.4,2e-11).unwrap();let b=events(P::Lcs91,50000.0,2e-4,0.4,2e-11).unwrap();close(b.events_cm3_s,4.0*a.events_cm3_s);}
#[test]fn thermal_binding_and_not_activation_energy(){let chi=2.17e-11;let r=events(P::Lcs91,50000.0,1e-4,0.1,chi).unwrap();assert_eq!(r.thermal_erg_cm3_s+r.binding_erg_cm3_s,0.0);close(r.binding_erg_cm3_s/r.events_cm3_s,chi);}
#[test]fn product_underflow_is_error(){assert_eq!(events(P::Lcs91,50000.0,1e-200,0.5,2e-11).unwrap_err().code(),"HH_PRODUCT_UNDERFLOW");}
#[test]fn product_overflow_is_error(){assert_eq!(events(P::Lcs91,50000.0,1e300,0.5,2e-11).unwrap_err().code(),"HH_NONFINITE");}
#[test]fn invalid_event_domain(){for (n,h,c) in [(-1.0,0.0,1.0),(1.0,-0.1,1.0),(1.0,1.1,1.0),(1.0,0.0,0.0),(f64::NAN,0.0,1.0)]{assert_eq!(events(P::Lcs91,50000.0,n,h,c).unwrap_err().code(),"HH_EVENT_DOMAIN");}}
#[test]fn off_is_bitwise_baseline(){let(m,s)=setup(50000.0,0.9,[0.3,0.6]);let r=hh_optin::combined_ft03_rhs(&m,&s,S::default()).unwrap();same(r.combined,ft03_rhs(&m,&s).unwrap());assert!(r.hh.is_none());}
#[test]fn off_bypasses_hh_rate_domain(){let(m,s)=setup(31000.0,0.9,[0.3,0.6]);let r=hh_optin::combined_ft03_rhs(&m,&s,S::Disabled).unwrap();same(r.combined,ft03_rhs(&m,&s).unwrap());assert!(r.hh.is_none());assert_eq!(hh_optin::combined_ft03_rhs(&m,&s,S::Research(P::Lcs91)).unwrap_err().code(),"HH_TEMPERATURE_DOMAIN");}
#[test]fn on_uses_typed_ft03(){let(m,s)=setup(50000.0,0.9,[0.3,0.6]);let r=hh_optin::combined_ft03_rhs(&m,&s,S::Research(P::Lcs91)).unwrap();same(r.baseline,ft03_rhs(&m,&s).unwrap());assert!(r.baseline.collision_per_cm3_s[0]>0.0&&r.baseline.recombination_per_cm3_s[0]>0.0&&r.baseline.dr_per_cm3_s[0]>0.0);assert!(r.hh.unwrap().events_cm3_s>0.0);}
#[test]fn only_h_and_u_change(){let(m,s)=setup(50000.0,0.9,[0.3,0.6]);let r=hh_optin::combined_ft03_rhs(&m,&s,S::Research(P::Lcs91)).unwrap();for i in [1,2,4,5,6]{assert_eq!(r.baseline.derivative[i].to_bits(),r.combined.derivative[i].to_bits());}let q=r.hh.unwrap();assert_eq!(r.combined.derivative[0],r.baseline.derivative[0]+q.per_h_s);assert_eq!(r.combined.derivative[3],r.baseline.derivative[3]+q.thermal_erg_cm3_s);assert_eq!(r.combined.escaped_energy_rate,r.baseline.escaped_energy_rate);}
#[test]fn neutral_native_composition(){let(m,mut s)=setup(50000.0,0.0,[0.0,0.0]);s.photon_cm3=[0.0;3];let r=hh_optin::combined_ft03_rhs(&m,&s,S::Research(P::CorrectedKs)).unwrap();assert_eq!(m.gas.electron_density(&s).unwrap(),0.0);assert_eq!(r.baseline.derivative[0],0.0);assert!(r.combined.derivative[0]>0.0&&r.combined.derivative[3]<0.0);}
#[test]fn endpoint_uses_same_state_source(){let(m,s)=setup(50000.0,0.9,[0.3,0.6]);let dt=1e9;let e=hh_optin::endpoint(&m,&s,&s,dt,S::Research(P::Lcs91)).unwrap();let q=e.rhs.hh.unwrap();close(e.hh_events_cm3,dt*q.events_cm3_s);close(e.hh_per_h,dt*q.per_h_s);close(e.hh_heat_erg_cm3,dt*q.thermal_erg_cm3_s);for i in 0..7{assert_eq!(e.residual[i],-dt*e.rhs.combined.derivative[i]);}}
#[test]fn endpoint_zero_dt(){let(m,s)=setup(50000.0,0.9,[0.3,0.6]);let e=hh_optin::endpoint(&m,&s,&s,0.0,S::Research(P::Lcs91)).unwrap();assert!(e.residual.iter().all(|x|*x==0.0));assert_eq!(e.hh_events_cm3,0.0);}
#[test]fn endpoint_invalid_time(){let(m,s)=setup(50000.0,0.9,[0.3,0.6]);for dt in [-1.0,f64::INFINITY,f64::NAN]{assert_eq!(hh_optin::endpoint(&m,&s,&s,dt,S::Research(P::Lcs91)).unwrap_err().code(),"HH_STEP_DOMAIN");}}
#[test]fn error_does_not_mutate_state(){let(m,s)=setup(31000.0,0.9,[0.3,0.6]);let before=s;assert_eq!(hh_optin::combined_ft03_rhs(&m,&s,S::Research(P::Lcs91)).unwrap_err().code(),"HH_TEMPERATURE_DOMAIN");assert_eq!(s,before);}
