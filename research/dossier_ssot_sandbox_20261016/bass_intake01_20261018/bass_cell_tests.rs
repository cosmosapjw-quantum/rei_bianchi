// Ten authored tests, NONE EXECUTED: sandbox ServerError before startup.
// rustc --edition=2021 --test bass_cell_tests.rs -o bass_cell_tests
// ./bass_cell_tests
#[path="bass_cell.rs"] mod bass_cell;
use bass_cell::*;
fn node(x:f64,b:f64,r:f64)->Node {Node{x,b,h_per_s:1.0,s_per_s:r,dh_dln_a_per_s:0.0}}
fn flat()->Cell {Cell::new(node(0.0,0.0,0.0),node(1.0,0.0,0.0)).unwrap()}
fn p(mu:f64)->Birth {Birth{x:0.0,b:0.0,energy_ev:20.0,mu}}
fn near(a:f64,b:f64,t:f64){assert!((a-b).abs()<=t,"{a} != {b}");}
fn root_mid(r:Crossing)->f64 {match r{Crossing::Point(x)=>x,Crossing::Bracket{left_x,right_x}=>(left_x+right_x)*0.5,_=>panic!("root expected")}}
#[test] fn flrw_geometry_and_energy(){
 let c=flat();let g=c.geometry(1.0,0.2).unwrap();
 for a in g.scale_factors {near(a,0.2_f64.exp(),1e-14);}
 for h in g.hubble_per_s {near(h,1.0,1e-14);}
 near(g.sigma_magnitude,0.0,1e-14);
 near(c.log_energy_ev(p(0.4),0.2).unwrap(),20.0_f64.ln()-0.2,1e-14);
}
#[test] fn linear_b_has_expected_directional_rates(){
 let c=Cell::new(node(0.0,0.0,0.1),node(1.0,0.1,0.1)).unwrap();
 let g=c.geometry(1.0,0.5).unwrap();near(g.signed_s_over_h,0.1,1e-14);
 near(g.hubble_per_s[0],0.9,1e-14);near(g.hubble_per_s[2],1.2,1e-14);
 let root=c.threshold_crossing(p(1.0),20.0*(-0.3_f64).exp(),1e-12).unwrap();
 near(root_mid(root),0.25,2e-12);
}
#[test] fn endpoint_and_absent_crossings(){
 let c=flat();assert_eq!(c.threshold_crossing(p(0.4),20.0,1e-12).unwrap(),Crossing::Point(0.0));
 assert_eq!(c.threshold_crossing(p(0.4),21.0,1e-12).unwrap(),Crossing::None);
 assert_eq!(c.threshold_crossing(p(0.4),1.0,1e-12).unwrap(),Crossing::None);
}
#[test] fn endpoint_expansion_does_not_admit_hidden_contraction(){
 let c=Cell::new(node(0.0,0.0,0.0),node(1.0,-2.0/3.0,0.0)).unwrap();
 assert!(c.geometry(1.0,0.0).unwrap().hubble_per_s[2]>0.0);
 assert!(c.geometry(1.0,1.0).unwrap().hubble_per_s[2]>0.0);
 assert!(c.geometry(1.0,0.5).unwrap().hubble_per_s[2]<0.0);
 assert_eq!(c.expansion().unwrap_err(),Error::UnsupportedCell);
 assert_eq!(c.threshold_crossing(p(1.0),20.0*(-0.02_f64).exp(),1e-12).unwrap_err(),Error::UnsupportedCell);
}
#[test] fn causal_range_and_input_rejections(){
 assert!(Cell::new(node(0.0,0.0,0.0),node(0.0,0.0,0.0)).is_err());
 let mut n=node(1.0,0.0,0.0);n.h_per_s=0.0;assert!(Cell::new(node(0.0,0.0,0.0),n).is_err());
 n=node(1.0,0.0,0.0);n.b=f64::NAN;assert!(Cell::new(node(0.0,0.0,0.0),n).is_err());
 assert!(flat().geometry(1.0,1.1).is_err());assert!(flat().geometry(-1.0,0.1).is_err());
 let mut b=p(0.4);b.x=0.5;assert!(flat().log_energy_ev(b,0.4).is_err());
 b=p(2.0);assert!(flat().log_energy_ev(b,0.4).is_err());
 assert!(flat().threshold_crossing(p(0.4),10.0,0.0).is_err());
}
fn donor()->Cell {Cell::new(
 Node{x:0.0,b:0.0,h_per_s:1.1835693720646417e-16,s_per_s:-1.183510198034054e-18,dh_dln_a_per_s:-1.7795494197516895e-16},
 Node{x:0.011959037710744356,b:-0.00011851083565535744,h_per_s:1.1624783532484068e-16,s_per_s:-1.1416116789266804e-18,dh_dln_a_per_s:-1.7477564709347456e-16}).unwrap()}
#[test] fn donor_cell_expansion_and_sigma_convention(){
 let c=donor();let e=c.expansion().unwrap();near(e.raw_margin,0.9800009999250062,3e-13);
 let g=c.geometry(1.0/21.0,0.011959037710744356/2.0).unwrap();
 near(g.mean_h_per_s/1.1729763363479359e-16,1.0,3e-13);
 near(g.sigma_magnitude,0.01716392289765967,3e-13);assert!(g.signed_s_per_s<0.0);
}
#[test] fn donor_cell_threshold_matches_cas_reference(){
 let c=donor();let b=Birth{x:0.0,b:0.0,energy_ev:13.605,mu:0.4};
 let x=root_mid(c.threshold_crossing(b,13.602134599702,1e-12).unwrap());
 near(x,0.00020954653923285161,2e-12);
 near(c.delta_proper_s(0.0,x).unwrap()/1.7707416039508226e12,1.0,2e-8);
}
#[test] fn donor_clock_not_silently_equal_to_raw_producer_time(){
 let t=donor().delta_proper_s(0.0,0.011959037710744356).unwrap();
 near(t/1.0195600729585139e14,1.0,2e-13);
 // The reference is the reconstructed log-H integral, not raw producer elapsed_s.
 assert!((t-101956007295789.6).abs()>1.0);
}
#[test] fn constant_h_clock_and_partition(){
 let c=flat();near(c.delta_proper_s(0.1,0.9).unwrap(),0.8,2e-14);
 near(c.delta_proper_s(0.1,0.4).unwrap()+c.delta_proper_s(0.4,0.9).unwrap(),0.8,3e-14);
 assert_eq!(c.delta_proper_s(0.3,0.3).unwrap(),0.0);assert!(c.delta_proper_s(0.5,0.2).is_err());
}
#[test] fn strict_boundary_and_reflection_scope(){
 let c=Cell::new(node(0.0,0.0,1.0),node(1.0,1.0,1.0)).unwrap();
 assert_eq!(c.expansion().unwrap_err(),Error::UnsupportedCell);
 near(donor().log_energy_ev(p(0.4),0.01).unwrap(),donor().log_energy_ev(p(-0.4),0.01).unwrap(),0.0);
}
