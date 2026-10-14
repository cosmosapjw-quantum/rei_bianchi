use rei_microphysics::{hhe_rhs,implicit_hhe_step,try_hhe_step,HHeModel,HHeState,StepControl};
fn main() {
    let mut m=HHeModel::controlled_fixture();
    m.sigma_cm2=[[0.0;3];3]; m.alpha_cm3_s=[0.0;3]; m.beta_cm3_s=[0.0;3];
    let mut s=HHeState::controlled_fixture(&m); s.fractions=[0.01,0.0,0.1];
    println!("ZERO_RATES_RHS={:?}",hhe_rhs(&m,&s));
    println!("ZERO_RATES_STEP={:?}",implicit_hhe_step(&m,&s,1e9,StepControl::default()));
    let before=s; let result=try_hhe_step(&m,&mut s,1e9,StepControl::default());
    println!("ZERO_RATES_TRANSACTION={:?},UNCHANGED={}",result,s==before);
    let m=HHeModel::controlled_fixture(); let mut s=HHeState::controlled_fixture(&m);
    s.fractions=[0.01,0.9,0.1];
    let rhs=hhe_rhs(&m,&s).unwrap();
    println!("FULL_HE_SUM={:?},HeI_PHOTO={:?},HeI_COLLISION={:?}",s.fractions[1]+s.fractions[2],rhs.photo_per_cm3_s[1],rhs.collision_per_cm3_s[1]);
    let mut m=HHeModel::controlled_fixture(); m.n_h_cm3=1e308; m.n_he_cm3=0.0;
    let s=HHeState {fractions:[1.0,0.0,0.0],u_erg_cm3:1e300,photon_cm3:[0.0;3],escaped_erg_cm3:0.0};
    println!("DENSE_TEMPERATURE={:?},STABLE_FORM={:?}",m.temperature(&s),(s.u_erg_cm3/m.n_h_cm3)/(3.0*m.kb_erg_k));
    let mut m=HHeModel::controlled_fixture(); m.kb_erg_k=1e308;
    let s=HHeState {fractions:[0.0;3],u_erg_cm3:1e300,photon_cm3:[0.0;3],escaped_erg_cm3:0.0};
    println!("LARGE_KB_TEMPERATURE={:?},STABLE_FORM={:?}",m.temperature(&s),(s.u_erg_cm3/m.kb_erg_k)*(2.0/(3.0*(m.n_h_cm3+m.n_he_cm3))));
}
