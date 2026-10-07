use rei_microphysics::{coupled_primary::PrimaryPacket,igm_state::IgmGasState,igm_step::*,verner_cutoff_ev,Absorber};
fn emit(n: &mut usize, r: Result<StepResult, rei_microphysics::ForwardError>) { println!("case_{} {:?}",*n,r); *n+=1; }
fn main() {
 let b=StepBackground{n_h:4e-4,n_he:3.16e-5,hubble:6e-17,tcmb:35.0};
 let g=IgmGasState::from_temperature([2e-4,0.0,0.0],b.n_h,b.n_he,30.0).unwrap();
 let mut n=0;
 let mut energies=vec![0.0,-1.0,f64::NAN,f64::INFINITY,f64::MIN_POSITIVE/2.0,10.0,20.0,80.0,50000.0,50001.0];
 for a in [Absorber::HI,Absorber::HeI,Absorber::HeII] { let e=verner_cutoff_ev(a); energies.extend([f64::from_bits(e.to_bits()-1),e,f64::from_bits(e.to_bits()+1)]); }
 for e in energies { for count in [0.0,0.01,f64::MIN_POSITIVE,f64::MIN_POSITIVE/2.0,-1.0,f64::NAN,1e308] {
  let p=[PrimaryPacket{energy_ev:e,per_h:count}];
  for mask in [[true;3],[false;3],[true,false,true],[false,true,false]] { for source in [0.0,1e-14] {
   emit(&mut n,implicit_step_with_source_masked(&g,&p,&[source],&[mask],b,1e5,StepControl::default()));
  }}
 }}
 for t in [1.0,30.0,1e4,1e6] {for dt in [1.0,1e5,1e11,1e15] {
  let q=IgmGasState::from_temperature([0.9,0.2,0.7],b.n_h,b.n_he,t).unwrap();let p=[PrimaryPacket{energy_ev:80.0,per_h:0.001},PrimaryPacket{energy_ev:20.0,per_h:0.002}];
  emit(&mut n,implicit_step(&q,&p,b,dt,StepControl::default()));
  emit(&mut n,implicit_step_with_source(&q,&p,&[1e-14,1e-15],b,dt,StepControl::default()));
 }}
 let bad=IgmGasState{fractions:[-1.0,0.0,0.0],w_erg_per_h:g.w_erg_per_h};
 for q in [g,bad] {for dt in [0.0,f64::NAN,1e5] {
  let p=[PrimaryPacket{energy_ev:50001.0,per_h:-1.0}];
  emit(&mut n,implicit_step(&q,&p,b,dt,StepControl::default()));
  emit(&mut n,implicit_step_with_source_masked(&q,&p,&[1e-14],&[],b,dt,StepControl::default()));
 }}
 eprintln!("cases={n}");
}
