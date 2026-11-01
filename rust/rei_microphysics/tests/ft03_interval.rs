use rei_microphysics::{ft03_interval_rhs, Ft03Model, Interval};
fn initial(m: &Ft03Model) -> [Interval;7] {
    let s=m.initial_state();
    [s.fractions[0],s.fractions[1],s.fractions[2],s.u_erg_cm3/(m.gas.n_h_cm3*m.gas.ev_erg),s.photon_cm3[0]/m.gas.n_h_cm3,s.photon_cm3[1]/m.gas.n_h_cm3,s.photon_cm3[2]/m.gas.n_h_cm3].map(|v|Interval::point(v).unwrap())
}
#[test]
fn actual_scaled_rhs_contains_production_point() {
    let m=Ft03Model::controlled().unwrap();let s=m.initial_state();let r=rei_microphysics::ft03_rhs(&m,&s).unwrap();let j=ft03_interval_rhs(&m,&initial(&m)).unwrap();
    let scaled=[r.derivative[0],r.derivative[1],r.derivative[2],r.derivative[3]/(m.gas.n_h_cm3*m.gas.ev_erg),r.derivative[4]/m.gas.n_h_cm3,r.derivative[5]/m.gas.n_h_cm3,r.derivative[6]/m.gas.n_h_cm3];
    for k in 0..7 {assert!(j[k].value.lo<=scaled[k] && scaled[k]<=j[k].value.hi,"coordinate {k}: {:?} vs {}",j[k].value,scaled[k]);}
}
#[test]
fn malformed_or_outside_actual_ft03_domain_rejected() {
    let m=Ft03Model::controlled().unwrap();let mut y=initial(&m);y[3]=Interval::point(1e-6).unwrap();assert!(ft03_interval_rhs(&m,&y).is_err());
    let mut y=initial(&m);y[1]=Interval::point(0.5).unwrap();assert!(ft03_interval_rhs(&m,&y).is_err());
    let mut y=initial(&m);y[4]=Interval{lo:f64::NAN,hi:1.};assert!(ft03_interval_rhs(&m,&y).is_err());
}
#[test]
fn full_mixed_hessian_is_symmetric_enclosed() {
    let m=Ft03Model::controlled().unwrap();let j=ft03_interval_rhs(&m,&initial(&m)).unwrap();
    for v in j {for a in 0..7 {for b in 0..7 {assert!(v.hessian[a][b].lo<=v.hessian[b][a].hi && v.hessian[b][a].lo<=v.hessian[a][b].hi);}}}
}
