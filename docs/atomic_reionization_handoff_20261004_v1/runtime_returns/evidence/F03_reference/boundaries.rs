use rei_microphysics::{hhe_rhs,implicit_hhe_step,adaptive_hhe_step,try_hhe_step,HHeModel,HHeState,StepControl};
fn main(){
let mut m=HHeModel::controlled_fixture();m.sigma_cm2=[[0.0;3];3];m.alpha_cm3_s=[0.0;3];m.beta_cm3_s=[0.0;3];let mut s=HHeState::controlled_fixture(&m);s.fractions=[0.01,0.0,0.1];
let zero_rhs=hhe_rhs(&m,&s).unwrap().derivative==[0.0;7];let no_event=implicit_hhe_step(&m,&s,1e9,StepControl::default()).is_ok_and(|a|a.state==s);let adaptive_identity=adaptive_hhe_step(&m,&s,1e9,StepControl::default()).is_ok_and(|a|a.state==s&&a.local_error==0.0);
let before=s;let bad=StepControl{max_iterations:0,..StepControl::default()};let rejection=try_hhe_step(&m,&mut s,1e9,bad).is_err()&&s==before;
let m=HHeModel::controlled_fixture();let mut s=HHeState::controlled_fixture(&m);s.fractions=[0.01,0.9,0.1];let rhs=hhe_rhs(&m,&s).unwrap();let neutral_boundary=rhs.photo_per_cm3_s[1]==[0.0;3]&&rhs.collision_per_cm3_s[1]==0.0&&rhs.photo_per_cm3_s.iter().flatten().all(|v|*v>=0.0);
let mut m=HHeModel::controlled_fixture();m.n_h_cm3=1e308;m.n_he_cm3=0.0;let s=HHeState{fractions:[1.0,0.0,0.0],u_erg_cm3:1e300,photon_cm3:[0.0;3],escaped_erg_cm3:0.0};let density_overflow=m.temperature(&s).is_err();
let mut m=HHeModel::controlled_fixture();m.kb_erg_k=1e308;let s=HHeState{fractions:[0.0;3],u_erg_cm3:1e300,photon_cm3:[0.0;3],escaped_erg_cm3:0.0};let eos_overflow=m.temperature(&s).is_err();
println!("{{\"zero_rhs\":{zero_rhs},\"no_event_identity\":{no_event},\"adaptive_identity\":{adaptive_identity},\"rejection_unchanged\":{rejection},\"neutral_boundary\":{neutral_boundary},\"density_overflow_rejected\":{density_overflow},\"eos_overflow_rejected\":{eos_overflow}}}");
if !(zero_rhs&&no_event&&adaptive_identity&&rejection&&neutral_boundary&&density_overflow&&eos_overflow){std::process::exit(1);}
}
