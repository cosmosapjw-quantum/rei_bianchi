//! Additive, source-frozen AX03-C8 stable local interval reference.
//! The current production AX08 point_at_scale uses accumulated timestamp values.
//! Keep this prospective callsite correction separate; DO NOT replace any binary
//! mid-run. Units: H and s in 1/second; time increment proper seconds, b dimensionless.
const X4: [f64; 4] = [
    -0.8611363115940526,
    -0.3399810435848563,
    0.3399810435848563,
    0.8611363115940526,
];
const W4: [f64; 4] = [
    0.34785484513745385,
    0.6521451548625461,
    0.6521451548625461,
    0.34785484513745385,
];
#[derive(Clone, Copy, Debug)]
pub struct Increment {
    pub proper_seconds: f64,
    pub delta_b: f64,
}
/// The original physical-density-fixed source, not SAME_H counterfactual.
pub fn integrate_clock(a0: f64, a1: f64, q_ref: f64) -> Result<Increment, &'static str> {
    const REF: f64 = 1.0 / 21.0;
    const END: f64 = 0.2;
    const H0: f64 = 67.4e3 / 3.0856775814913673e22;
    const OM: f64 = 0.315;
    const OR: f64 = 9.2e-5;
    const OL: f64 = 1.0 - 0.315 - 9.2e-5;
    if !(a0.is_finite()
        && a1.is_finite()
        && q_ref.is_finite()
        && REF <= a0
        && a0 < a1
        && a1 <= END
        && matches!(q_ref,x if x==0.0||x==0.005||x== -0.005||x==0.01||x== -0.01))
    {
        return Err("SOURCE_CASE_OR_ORDER_OR_RANGE");
    }
    let flrw = |a: f64| H0 * (OM / a.powi(3) + OR / a.powi(4) + OL).sqrt();
    let href = flrw(REF);
    let dx = ((a1 - a0) / a0).ln_1p(); // stable for adjacent binary64 endpoints
    if !dx.is_finite() || dx <= 0.0 {
        return Err("NONPOSITIVE_LOG_INTERVAL");
    }
    let mut dt = 0.0;
    let mut db = 0.0;
    for i in 0..4 {
        let u = 0.5 * (1.0 + X4[i]);
        let a = a0 * (u * dx).exp();
        let s = q_ref * href * (REF / a).powi(3);
        let h = flrw(a).hypot(s);
        let w = 0.5 * W4[i] * dx;
        dt += w / h;
        db += w * s / h;
    }
    if !dt.is_finite() || dt <= 0.0 || !db.is_finite() {
        return Err("UNPHYSICAL_SAVED_SOURCE_CLOCK");
    }
    Ok(Increment {
        proper_seconds: dt,
        delta_b: db,
    })
}
