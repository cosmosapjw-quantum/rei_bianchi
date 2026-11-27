use crate::*;
use crate::hh_optin::{HhSelection as S,HhProvider as P};
use crate::hh_stepper as hh;
fn ctl()->StepControl {StepControl{max_iterations:80,residual_tolerance:1e-14}}
fn state(m:&Ft03Model,f:[f64;3],t:f64,ph:[f64;3])->HHeState{
 let mut s=m.initial_state();s.fractions=f;s.photon_cm3=ph.map(|v|v*m.gas.n_h_cm3);
 let ne=m.gas.electron_density(&s).unwrap();s.u_erg_cm3=1.5*m.gas.kb_erg_k*t*(m.gas.n_h_cm3+m.gas.n_he_cm3+ne);s
}
fn bits(a:&HHeState,b:&HHeState){assert_eq!(a.coordinates().map(f64::to_bits),b.coordinates().map(f64::to_bits));assert_eq!(a.escaped_erg_cm3.to_bits(),b.escaped_erg_cm3.to_bits());}
fn ebits(a:Ft03Events,b:Ft03Events){for k in 0..3{assert_eq!(a.photo_per_cm3[k].map(f64::to_bits),b.photo_per_cm3[k].map(f64::to_bits));}assert_eq!(a.collision_per_cm3.map(f64::to_bits),b.collision_per_cm3.map(f64::to_bits));assert_eq!(a.recombination_per_cm3.map(f64::to_bits),b.recombination_per_cm3.map(f64::to_bits));assert_eq!(a.dr_per_cm3.map(f64::to_bits),b.dr_per_cm3.map(f64::to_bits));}
#[test] fn off_implicit_exact_baseline_even_outside_hh_window(){let m=Ft03Model::controlled().unwrap();for t in [34000.,50000.,70000.]{let s=state(&m,[0.9,0.3,0.6],t,[0.05,0.005,0.001]);let a=ft03_implicit_step(&m,&s,1e8,ctl()).unwrap();let b=hh::implicit(&m,&s,1e8,ctl(),S::Disabled).unwrap();bits(&a.state,&b.state);ebits(a.events,b.events);assert_eq!(a.iterations,b.iterations);assert_eq!(a.residual_norm.to_bits(),b.residual_norm.to_bits());assert_eq!(b.hh.events_cm3,0.);}}
#[test] fn off_adaptive_exact_baseline(){let m=Ft03Model::controlled().unwrap();let s=m.initial_state();let a=ft03_adaptive_step(&m,&s,1e9,ctl()).unwrap();let b=hh::adaptive(&m,&s,1e9,ctl(),S::Disabled).unwrap();bits(&a.state,&b.state);ebits(a.events,b.events);assert_eq!(a.local_error.to_bits(),b.local_error.to_bits());assert_eq!(a.iterations,b.iterations);}
#[test] fn neutral_seed_produces_electrons_without_dividing_by_ne(){let m=Ft03Model::controlled().unwrap();let s=state(&m,[0.,0.,0.],50000.,[0.;3]);for p in [P::Lcs91,P::CorrectedKs]{let b=hh::implicit(&m,&s,1e9,ctl(),S::Research(p)).unwrap();assert!(b.state.fractions[0]>0.);assert!(b.hh.events_cm3>0.);assert!(b.hh.heat_erg_cm3<0.);}}
#[test] fn hh_source_is_present_in_final_be_equation(){let m=Ft03Model::controlled().unwrap();let s=state(&m,[0.,0.,0.],50000.,[0.;3]);let b=hh::implicit(&m,&s,1e9,ctl(),S::Research(P::Lcs91)).unwrap();let ep=hh_optin::endpoint(&m,&s,&b.state,1e9,S::Research(P::Lcs91)).unwrap();assert!(ep.residual[0].abs()<1e-14,"{:?}",ep.residual);assert!(ep.residual[3].abs()/s.u_erg_cm3<1e-14);}
#[test] fn returned_hh_events_belong_to_actual_endpoint(){let m=Ft03Model::controlled().unwrap();let s=m.initial_state();let dt=1e9;let b=hh::implicit(&m,&s,dt,ctl(),S::Research(P::Lcs91)).unwrap();let ep=hh_optin::endpoint(&m,&s,&b.state,dt,S::Research(P::Lcs91)).unwrap();assert!(b.hh.events_cm3>0.);assert_eq!(b.hh.events_cm3.to_bits(),ep.hh_events_cm3.to_bits());assert_eq!(b.hh.heat_erg_cm3.to_bits(),ep.hh_heat_erg_cm3.to_bits());}
#[test] fn lcs_and_ks_are_distinct_time_evolutions(){let m=Ft03Model::controlled().unwrap();let s=state(&m,[0.,0.,0.],50000.,[0.;3]);let a=hh::implicit(&m,&s,1e10,ctl(),S::Research(P::Lcs91)).unwrap();let b=hh::implicit(&m,&s,1e10,ctl(),S::Research(P::CorrectedKs)).unwrap();assert!(a.state.fractions[0]>50.*b.state.fractions[0]);}
#[test] fn on_start_outside_research_window_rejected(){let m=Ft03Model::controlled().unwrap();let s=state(&m,[0.,0.,0.],34000.,[0.;3]);let e=hh::implicit(&m,&s,1e9,ctl(),S::Research(P::Lcs91)).unwrap_err();assert_eq!(e.code(),"HH_TEMPERATURE_DOMAIN");}
#[test] fn on_dtzero_validates_domain(){let m=Ft03Model::controlled().unwrap();let s=state(&m,[0.,0.,0.],70000.,[0.;3]);assert_eq!(hh::implicit(&m,&s,0.,ctl(),S::Research(P::Lcs91)).unwrap_err().code(),"HH_TEMPERATURE_DOMAIN");}
#[test] fn dtzero_in_domain_identity(){let m=Ft03Model::controlled().unwrap();let s=m.initial_state();for p in [P::Lcs91,P::CorrectedKs]{let b=hh::adaptive(&m,&s,0.,ctl(),S::Research(p)).unwrap();bits(&s,&b.state);assert_eq!(b.hh.events_cm3,0.);assert_eq!(b.iterations,0);}}
#[test] fn accepted_half_counters_are_summed_not_endpoint_times_full_dt(){let m=Ft03Model::controlled().unwrap();let s=state(&m,[0.,0.,0.],50000.,[0.;3]);let dt=1e10;let sel=S::Research(P::Lcs91);let b=hh::adaptive(&m,&s,dt,ctl(),sel).unwrap();let h1=hh::implicit(&m,&s,dt/2.,ctl(),sel).unwrap();let h2=hh::implicit(&m,&h1.state,dt/2.,ctl(),sel).unwrap();bits(&b.state,&h2.state);assert!(b.hh.events_cm3>0.);assert_eq!(b.hh.events_cm3.to_bits(),(h1.hh.events_cm3+h2.hh.events_cm3).to_bits());assert_eq!(b.hh.heat_erg_cm3.to_bits(),(h1.hh.heat_erg_cm3+h2.hh.heat_erg_cm3).to_bits());let wrong=hh_optin::endpoint(&m,&s,&b.state,dt,sel).unwrap();assert!((wrong.hh_events_cm3-b.hh.events_cm3).abs()>1e-10*b.hh.events_cm3);}
#[test] fn thermal_binding_and_material_event_ledger_agree(){let m=Ft03Model::controlled().unwrap();let s=state(&m,[1e-5,0.,0.],50000.,[0.;3]);let b=hh::adaptive(&m,&s,1e10,ctl(),S::Research(P::Lcs91)).unwrap();assert!(b.hh.events_cm3>0.);let e0=m.gas.total_energy(&s).unwrap();assert!((m.gas.total_energy(&b.state).unwrap()-e0).abs()/e0<1e-12);let j=b.events.photo_per_cm3[0].iter().sum::<f64>()+b.events.collision_per_cm3[0]-b.events.recombination_per_cm3[0]+b.hh.events_cm3;assert!((m.gas.n_h_cm3*(b.state.fractions[0]-s.fractions[0])-j).abs()/m.gas.n_h_cm3<1e-13);assert!((b.hh.heat_erg_cm3+m.gas.threshold_ev[0]*m.gas.ev_erg*b.hh.events_cm3).abs()<1e-12*(-b.hh.heat_erg_cm3));}
#[test] fn rejected_domain_update_is_transactional(){let m=Ft03Model::controlled().unwrap();let old=state(&m,[0.,0.,0.],34000.,[0.;3]);let mut s=old;assert!(hh::try_adaptive(&m,&mut s,1e9,ctl(),S::Research(P::Lcs91)).is_err());bits(&s,&old);}
#[test] fn iteration_failure_leaves_caller_unchanged(){let m=Ft03Model::controlled().unwrap();let old=m.initial_state();let mut s=old;let c=StepControl{max_iterations:1,residual_tolerance:1e-14};assert!(hh::try_adaptive(&m,&mut s,1e10,c,S::Research(P::Lcs91)).is_err());bits(&s,&old);}
#[test] fn invalid_dt_rejected_without_mutation(){let m=Ft03Model::controlled().unwrap();for dt in [-1.,f64::NAN,f64::INFINITY]{let old=m.initial_state();let mut s=old;assert!(hh::try_adaptive(&m,&mut s,dt,ctl(),S::Research(P::Lcs91)).is_err());bits(&s,&old);}}
// Coverage added after the first green run: this checks an INTERMEDIATE
// temperature rejection from a valid starting state, not an invalid input.
#[test]
fn candidate_temperature_exit_rejects_without_committing() {
    let m=Ft03Model::controlled().unwrap();
    let old=state(&m,[0.,0.,0.],35000.01,[0.;3]);
    assert!(m.gas.temperature(&old).unwrap()>35000.);
    let mut s=old;
    let e=hh::try_adaptive(&m,&mut s,1e11,ctl(),S::Research(P::Lcs91)).unwrap_err();
    assert_eq!(e.code(),"HH_TEMPERATURE_DOMAIN");
    bits(&s,&old);
}
