//! Separate static constant-alpha kernel, not the FLRW/Grackle history.
use rei_microphysics::{adaptive_hhe_step,hhe_rhs,HHeModel,HHeState,StepControl};
pub struct ResultRow {pub error:f64,pub exact:f64,pub temp_relative:f64,pub energy_relative:f64,pub recombination_defect:f64}
pub fn run(n:usize)->ResultRow {
 let nh=1e-3;let alpha=2e-13;let x0=0.8;let temperature=1e4;let duration=1e16;
 let mut model=HHeModel::controlled_fixture();
 model.n_h_cm3=nh;model.n_he_cm3=0.;model.alpha_cm3_s=[alpha,0.,0.];model.beta_cm3_s=[0.;3];model.sigma_cm2=[[0.;3];3];
 let mut state=HHeState {fractions:[x0,0.,0.],u_erg_cm3:1.5*model.kb_erg_k*temperature*nh*(1.+x0),photon_cm3:[0.;3],escaped_erg_cm3:0.};
 let initial_energy=model.total_energy(&state).unwrap();let mut recombinations=0.;
 let rhs=hhe_rhs(&model,&state).unwrap();
 let expected=-alpha*nh*x0*x0;
 assert!((rhs.derivative[0]-expected).abs()<1e-14*expected.abs());
 let dt_defect=rhs.derivative[3]-1.5*model.kb_erg_k*temperature*nh*rhs.derivative[0];
 assert!(dt_defect.abs()<1e-14*rhs.derivative[3].abs());
 for _ in 0..n {
  let result=adaptive_hhe_step(&model,&state,duration/n as f64,StepControl::default()).unwrap();
  state=result.state;recombinations+=result.events.recombination_per_cm3[0]/nh;
  assert_eq!(state.photon_cm3,[0.;3]);assert_eq!([state.fractions[1],state.fractions[2]],[0.;2]);
  assert_eq!(model.electron_density(&state).unwrap(),nh*state.fractions[0]);
 }
 let exact=x0/(1.+alpha*nh*x0*duration);
 let result=ResultRow{error:(state.fractions[0]-exact).abs(),exact,temp_relative:(model.temperature(&state).unwrap()/temperature-1.).abs(),energy_relative:(model.total_energy(&state).unwrap()/initial_energy-1.).abs(),recombination_defect:(recombinations-(x0-state.fractions[0])).abs()};
 println!("{{\"steps\":{n},\"x\":{},\"exact\":{},\"error\":{},\"temp_relative\":{},\"energy_relative\":{},\"recombination_defect\":{}}}",state.fractions[0],result.exact,result.error,result.temp_relative,result.energy_relative,result.recombination_defect);
 result
}
