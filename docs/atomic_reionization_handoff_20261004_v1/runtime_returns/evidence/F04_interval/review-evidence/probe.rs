use rei_microphysics::{Interval, Jet};
fn point(x:f64)->Interval { Interval::point(x).unwrap() }
fn contains(a:Interval,x:f64)->bool {a.lo.is_finite() && a.hi.is_finite() && a.lo<=x && x<=a.hi}
fn main(){
    for x in [2.0,1e-200,1e200,f64::from_bits(1),f64::MAX] {
        for p in [0.0,1.0] {
            let scalar=point(x).powf(p);
            let jet=Jet::variable(point(x),0).unwrap().powf(p);
            println!("pow x={x:.17e} p={p} scalar={scalar:?}");
            match jet {
                Ok(j)=>{
                    let value=if p==0.0 {1.0} else {x};
                    assert!(contains(j.value,value));
                    for i in 0..7 {
                        assert!(contains(j.gradient[i],if i==0 {p} else {0.0}));
                        for k in 0..7 {assert!(contains(j.hessian[i][k],0.0));}
                    }
                    println!("jet=OK value={:?} d0={:?} h00={:?}",j.value,j.gradient[0],j.hessian[0][0]);
                }
                Err(e)=>println!("jet=ERR {e:?}; exact value={}, d0={p}, Hessian=0",if p==0.0 {1.0} else {x}),
            }
        }
    }
    let x=Jet::variable(point(2.0),0).unwrap();
    let y=Jet::variable(point(2.0),1).unwrap();
    let q=x.div(&y).unwrap();
    assert!(contains(q.value,1.0));
    assert!(contains(q.gradient[0],0.5));
    assert!(contains(q.gradient[1],-0.5));
    assert!(contains(q.hessian[0][0],0.0));
    assert!(contains(q.hessian[0][1],-0.25));
    assert!(contains(q.hessian[1][0],-0.25));
    assert!(contains(q.hessian[1][1],0.5));
    println!("quotient_mixed_partials=PASS");
    let a=Jet::variable(point(0.0),0).unwrap();
    let b=Jet::variable(point(-0.0),1).unwrap();
    let e=a.mul(&b).unwrap().exp().unwrap();
    assert!(contains(e.value,1.0));
    assert!(contains(e.hessian[0][1],1.0));
    assert!(contains(e.hessian[1][0],1.0));
    println!("exp_product_mixed_partials_signed_zero=PASS");
    let mut bad=Jet::variable(point(1.0),0).unwrap();
    bad.hessian[6][6]=Interval {lo:f64::NAN,hi:0.0};
    assert!(bad.exp().is_err()); assert!(bad.ln().is_err());
    assert!(bad.powf(0.0).is_err()); assert!(bad.powf(1.0).is_err());
    assert!(bad.add(&x).is_err()); assert!(bad.mul(&x).is_err()); assert!(bad.div(&x).is_err());
    println!("malformed_public_hessian=PASS");
    for x in [-1000.0,-f64::MAX] {
        let e=point(x).exp().unwrap();
        assert_eq!(e.lo,0.0); assert_eq!(e.hi,f64::from_bits(1));
        println!("negative_exp x={x:.17e} value={e:?}");
    }
    let s=point(f64::from_bits(1)).mul(&point(0.5)).unwrap();
    assert!(s.lo<=0.0 && s.hi>=f64::from_bits(1));
    assert!(point(f64::MAX).mul(&point(2.0)).is_err());
    assert!(point(1.0).div(&Interval::new(-0.0,0.0).unwrap()).is_err());
    println!("subnormal_overflow_zero_division=PASS");
}
