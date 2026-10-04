use rei_microphysics::{ft03_coefficients, ft03_rhs, ft03_implicit_step, Ft03Model, StepControl};
fn main() {
    for (label, nh, nhe) in [("trace_H",1e-320,8.3e-6),("trace_He",1e-4,1e-320),("normal_input_trace_H",1e-300,8.3e-20)] {
        let mut m=Ft03Model::controlled().unwrap();m.gas.n_h_cm3=nh;m.gas.n_he_cm3=nhe;
        let mut s=m.initial_state();s.photon_cm3=[0.0;3];
        let t=m.gas.temperature(&s).unwrap();let c=ft03_coefficients(t).unwrap();let ne=m.gas.electron_density(&s).unwrap();
        let x=s.fractions;let q=[(1.0-x[0])*ne*c.beta_ci_cm3_s[0]-x[0]*ne*c.alpha_rr_cm3_s[0], (1.0-(x[1]+x[2]))*ne*c.beta_ci_cm3_s[1]-x[1]*ne*(c.alpha_rr_cm3_s[1]+c.alpha_dr_cm3_s.iter().sum::<f64>()), x[1]*ne*c.beta_ci_cm3_s[2]-x[2]*ne*c.alpha_rr_cm3_s[2]];
        let expected=[q[0],q[1]-q[2],q[2]];
        let got=ft03_rhs(&m,&s);
        println!("{label}: nH={nh:e} nHe={nhe:e} T={t:e} expected={expected:?} rhs={got:?}");
        println!("{label}: step={:?}",ft03_implicit_step(&m,&s,1e11,StepControl::default()));
    }
}
