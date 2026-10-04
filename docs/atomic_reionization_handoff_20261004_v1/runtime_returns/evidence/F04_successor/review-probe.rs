use rei_microphysics::{ft03_rhs,ft03_try_step,Ft03Model,StepControl,ForwardError};
fn main() {
 let cases=[("subnormal_trace_H",1e-320,8.3e-6),("normal_trace_H",1e-300,8.3e-20),("trace_He",1e-4,1e-320),("dilute",1e-200,8.3e-202)];
 for (label,nh,nhe) in cases {
  let mut model=Ft03Model::controlled().unwrap();model.gas.n_h_cm3=nh;model.gas.n_he_cm3=nhe;
  let mut state=model.initial_state();state.photon_cm3=[0.0;3];let before=state;
  let rhs=ft03_rhs(&model,&state);println!("{label}: rhs={rhs:?}");
  assert!(matches!(rhs,Err(ForwardError::InvalidInput("FT03_PRODUCT_UNDERFLOW"))),"silent loss of positive source product: {label}");
  assert!(ft03_try_step(&model,&mut state,1e11,StepControl::default()).is_err());
  assert_eq!(state,before,"rejected candidate wrote state: {label}");
 }
 let model=Ft03Model::controlled().unwrap();let mut state=model.initial_state();state.fractions=[0.5,0.25,0.75];state.photon_cm3=[0.0;3];let rhs=ft03_rhs(&model,&state).unwrap();assert_eq!(rhs.collision_per_cm3_s[1],0.0);assert!(rhs.recombination_per_cm3_s.iter().all(|x| *x>0.0));
 println!("PASS: 4 underflow rejections with transactional state preservation; exact zero channel accepted");
}
