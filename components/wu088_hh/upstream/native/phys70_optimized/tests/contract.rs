use std::sync::Arc;
use num_complex::Complex64 as C;
use rodas5p_core::{WorkCounters,rodas5p_coefficients};
use rodas5p_integrators::Rodas5pMfFastWorkspace;
use wu088_hh_phys69_vigilode::HhModel;
use wu088_hh_phys70_optimized::{*,block::FrozenJacobian,kernel::{HhKernel,Backend},integrate::StructuredWorkspace};

fn state(lmax:usize)->Vec<f64> {
    let n=lmax+1;let mut y=vec![0.0;2*(4*n+1)];
    for j in 0..n {put(&mut y,j,C::new(0.8+0.002*j as f64,0.2-0.001*j as f64));put(&mut y,n+j,C::new(0.1,-0.4));put(&mut y,2*n+j,C::new(0.03,0.004*j as f64));put(&mut y,3*n+j,C::new(-0.01,0.007*j as f64));}
    y
}
fn direction(n:usize)->Vec<f64>{(0..n).map(|i|((i*7%31) as f64-15.0)/30.0).collect()}
fn rel(a:&[f64],b:&[f64])->f64 {
    let e=a.iter().zip(b).map(|(a,b)|(a-b).abs()).fold(0.0_f64,f64::max);
    let m=a.iter().chain(b).map(|x|x.abs()).fold(0.0_f64,f64::max);if m==0.0{e}else{e/m}
}
#[test]
fn ordered_scalar_simd_callbacks_match_original_bits() {
    for l in [21,28,36,64] {
        let nq=if l<=36{96}else{128};let old=HhModel::new(l,nq).unwrap();let y=state(l);
        let mut a=HhKernel::new(l,nq,Backend::Scalar).unwrap();let mut b=HhKernel::new(l,nq,Backend::Simd).unwrap();
        let mut oo=vec![0.0;y.len()];let mut aa=oo.clone();let mut bb=oo.clone();
        for tau in [0.0,12.125,37.625,38.0] {
            old.rhs(tau,&y,&mut oo).unwrap();a.rhs(tau,&y,&mut aa).unwrap();b.rhs(tau,&y,&mut bb).unwrap();
            assert!(oo.iter().zip(&aa).zip(&bb).all(|((&o,&a),&b)|o.to_bits()==a.to_bits()&&o.to_bits()==b.to_bits()));
            old.partial_tau(tau,&y,&mut oo).unwrap();a.partial_tau(tau,&y,&mut aa).unwrap();b.partial_tau(tau,&y,&mut bb).unwrap();
            assert!(oo.iter().zip(&aa).zip(&bb).all(|((&o,&a),&b)|o.to_bits()==a.to_bits()&&o.to_bits()==b.to_bits()));
        }
    }
}
#[test]
fn full_structured_inverse_checked_by_unmodified_original_jvp() {
    for l in [21,28,64] {
        let nodes=if l==64{128}else{96};let old=HhModel::new(l,nodes).unwrap();let y=state(l);let v=direction(y.len());
        let mut k=HhKernel::new(l,nodes,Backend::Simd).unwrap();let mut j=FrozenJacobian::new(l+1);
        let mut a=vec![0.0;y.len()];let mut b=a.clone();let mut out=a.clone();let mut scratch=a.clone();
        for tau in [0.0,37.75] {
            k.freeze(tau,&y,&mut j).unwrap();old.jvp(tau,&y,&v,&mut a).unwrap();j.apply(&v,&mut b).unwrap();assert!(rel(&a,&b)<3e-14);
            for s in [0.0,0.01,0.1] {
                for i in 0..y.len(){b[i]=v[i]-s*a[i];}
                assert!(j.solve(s,&b,&mut out,&mut scratch).unwrap()<3e-14);
                assert!(rel(&v,&out)<3e-14);
                old.jvp(tau,&y,&out,&mut scratch).unwrap();
                let defect:Vec<f64>=out.iter().zip(&scratch).map(|(x,jx)|x-s*jx).collect();assert!(rel(&defect,&b)<3e-14);
            }
        }
    }
}
#[test]
fn all_raw_u_stages_satisfy_original_non_autonomous_equations() {
    let l=28;let y=state(l);let old=Arc::new(HhModel::new(l,96).unwrap());let mut k=HhKernel::new(l,96,Backend::Simd).unwrap();let mut w=StructuredWorkspace::new(y.len()).unwrap();
    let (t,h)=(37.25,0.002);w.attempt(&mut k,t,&y,h,true,3e-13,3e-11).unwrap();let c=rodas5p_coefficients().unwrap();let shift=h*c.gamma;
    let mut ft=vec![0.0;y.len()];old.partial_tau(t,&y,&mut ft).unwrap();
    for i in 0..8 {
        let mut stage=y.clone();for j in 0..i{let a=c.a[(i,j)];if a!=0.0{for (x,v) in stage.iter_mut().zip(w.stage(j)){*x+=a*v;}}}
        let mut rhs=vec![0.0;y.len()];old.rhs(t+c.c[i]*h,&stage,&mut rhs).unwrap();for x in &mut rhs{*x*=shift;}
        for j in 0..i{let c0=c.c_matrix[(i,j)];if c0!=0.0{let weight=c.gamma*c0;for (x,v) in rhs.iter_mut().zip(w.stage(j)){*x+=weight*v;}}}
        for (x,v) in rhs.iter_mut().zip(&ft){*x+=shift*h*c.gamma_rows[i]*v;}
        let mut jv=vec![0.0;y.len()];old.jvp(t,&y,w.stage(i),&mut jv).unwrap();
        let lhs:Vec<_>=w.stage(i).iter().zip(jv).map(|(x,jx)|x-shift*jx).collect();assert!(rel(&lhs,&rhs)<1e-13,"stage {i}");
    }
    let problem=old.ode().unwrap();let mut baseline=Rodas5pMfFastWorkspace::new(&problem,&benchmark::linear_config()).unwrap();baseline.set_gmres_into(true);baseline.set_ls_workspace(true);let mut count=WorkCounters::default();
    baseline.attempt(&problem,t,&y,h,true,None,3e-13,3e-11,&mut count).unwrap();
    assert!(rel(baseline.y_new(),w.y_new())<2e-12);
}
#[test]
fn shared_external_channel_has_both_derivative_terms() {
    let l=28;let y=state(l);let mut k=HhKernel::new(l,96,Backend::Scalar).unwrap();let mut jac=FrozenJacobian::new(l+1);k.freeze(38.0,&y,&mut jac).unwrap();
    let old=HhModel::new(l,96).unwrap();let mut v=vec![0.0;y.len()];put(&mut v,TARGET_A,C::new(1.0,0.25));let mut a=v.clone();let mut b=v.clone();
    jac.apply(&v,&mut a).unwrap();old.jvp(38.0,&y,&v,&mut b).unwrap();assert_eq!(get(&a,2*(l+1)+TARGET_A),get(&b,2*(l+1)+TARGET_A));
}
#[test]
fn failed_public_freeze_invalidates_previous_operator() {
    let mut y=state(28);let mut k=HhKernel::new(28,96,Backend::Simd).unwrap();let mut jac=FrozenJacobian::new(29);let mut out=y.clone();
    k.freeze(1.0,&y,&mut jac).unwrap();put(&mut y,3,C::default());assert!(k.freeze(1.0,&y,&mut jac).is_err());assert!(jac.apply(&y,&mut out).is_err());
}
#[test]
fn overflow_in_residual_normalizer_cannot_pass_as_zero() {
    let y=state(28);let mut k=HhKernel::new(28,96,Backend::Scalar).unwrap();let mut jac=FrozenJacobian::new(29);k.freeze(1.0,&y,&mut jac).unwrap();
    let mut rhs=vec![0.0;y.len()];let n=29;rhs[2*(4*n)]=f64::MAX;let mut out=rhs.clone();let mut scratch=rhs.clone();
    assert!(jac.solve(0.0,&rhs,&mut out,&mut scratch).is_err());
}
#[test]
fn cache_reuse_requires_actual_time_state_and_kernel_config() {
    let mut y=state(28);let mut k=HhKernel::new(28,96,Backend::Scalar).unwrap();let mut w=StructuredWorkspace::new(y.len()).unwrap();
    w.attempt(&mut k,1.0,&y,0.001,true,3e-13,3e-11).unwrap();let bytes=w.workspace_bytes();
    w.attempt(&mut k,1.0,&y,0.0005,false,3e-13,3e-11).unwrap();assert_eq!(w.state_reuses(),1);assert_eq!(k.counts.linearizations,1);
    y[4]+=0.01;w.attempt(&mut k,1.0,&y,0.001,false,3e-13,3e-11).unwrap();assert_eq!(k.counts.linearizations,2);
    w.attempt(&mut k,1.5,&y,0.001,false,3e-13,3e-11).unwrap();assert_eq!(k.counts.linearizations,3);
    let mut other=HhKernel::new(28,100,Backend::Simd).unwrap();w.attempt(&mut other,1.5,&y,0.001,false,3e-13,3e-11).unwrap();assert_eq!(other.counts.linearizations,1);assert_eq!(w.workspace_bytes(),bytes);
}
#[test]
fn failed_refresh_does_not_poison_later_valid_attempt() {
    let good=state(28);let mut bad=good.clone();put(&mut bad,0,C::default());let mut k=HhKernel::new(28,96,Backend::Simd).unwrap();let mut w=StructuredWorkspace::new(good.len()).unwrap();
    w.attempt(&mut k,1.0,&good,0.001,true,3e-13,3e-11).unwrap();assert!(w.attempt(&mut k,1.0,&bad,0.001,false,3e-13,3e-11).is_err());
    w.attempt(&mut k,1.0,&good,0.001,false,3e-13,3e-11).unwrap();let mut independent=StructuredWorkspace::new(good.len()).unwrap();independent.attempt(&mut k,1.0,&good,0.001,true,3e-13,3e-11).unwrap();assert_eq!(w.y_new(),independent.y_new());
}
#[test]
fn fixed_step_and_shape_limits_are_enforced() {
    let y=state(28);let mut k=HhKernel::new(28,96,Backend::Simd).unwrap();let mut w=StructuredWorkspace::new(y.len()).unwrap();
    for (t,h) in [(0.0,0.51),(38.0,0.01),(-1.0,0.1),(1.0,0.0),(1.0,f64::NAN)] {assert!(w.attempt(&mut k,t,&y,h,true,3e-13,3e-11).is_err());}
    assert_eq!(w.shifted_solves(),0);assert!(StructuredWorkspace::new(234+1).is_err());assert!(HhKernel::new(64,64,Backend::Simd).is_err());
}
