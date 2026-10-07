//! Sharp E^-3 bounds for positive spectra with fixed number and energy moments.
//! This is not a Verner cross-section enclosure or an interval-arithmetic proof.
use crate::panel::Panel;
use crate::tail::LogPositive;

#[derive(Clone, Copy, Debug)]
pub struct Bounds { pub lower: LogPositive, pub upper: LogPositive }
pub fn inverse_cubic(n: LogPositive, a: f64, b: f64, mean: f64) -> Result<Bounds, &'static str> {
    if ![a,b,mean].iter().all(|v|v.is_finite()) || a<=0.0 || b<=a || mean<a || mean>b {
        return Err("invalid positive measure moments/support");
    }
    let lower = n.scale(mean.powi(-3))?;
    let upper = n.scale(((b-mean)*a.powi(-3)+(mean-a)*b.powi(-3))/(b-a))?;
    Ok(Bounds{lower,upper})
}
/// Restriction supplies the actual two moments in each child, without refitting.
pub fn restricted_bounds(panel: &Panel, s: f64, parts: usize) -> Result<Bounds, String> {
    if !s.is_finite() || parts==0 || parts>1024 {return Err("invalid refinement".into());}
    let mut total=Bounds{lower:LogPositive::empty(),upper:LogPositive::empty()};
    for j in 0..parts {
        let a=panel.l+(panel.r-panel.l)*j as f64/parts as f64;
        let b=if j+1==parts {panel.r} else {panel.l+(panel.r-panel.l)*(j+1) as f64/parts as f64};
        let r=panel.restrict(a,b).map_err(|e|format!("restriction: {e:?}"))?.ok_or("empty child")?;
        let (hi,lo)=r.log_amplitude_parts();
        let bound=inverse_cubic(LogPositive::from_log_parts(hi,lo)?,(a-s).exp(),(b-s).exp(),(r.mean_eta-s).exp())?;
        total.lower=total.lower.add(bound.lower)?.value;
        total.upper=total.upper.add(bound.upper)?.value;
    }
    Ok(total)
}

#[cfg(test)]
mod tests {
 use super::*;
 fn v(x:LogPositive)->f64{x.readout().unwrap().value}
 #[test] fn same_moments_have_different_rates() {
    let b=inverse_cubic(LogPositive::from_linear(1.0).unwrap(),1.0,4.0,2.0).unwrap();
    assert!((v(b.lower)-0.125).abs()<1e-15);
    assert!((v(b.upper)-0.671875).abs()<1e-15);
    // Mean atom E=2 and endpoint mixture (2/3 at1,1/3 at4) share N=1,U/eps=2.
    assert!(v(b.upper)/v(b.lower)>5.0);
 }
 #[test] fn positive_mixtures_stay_between_jensen_and_secant() {
    for k in 1..40 {let t=k as f64/40.0;let mean=t*1.3+(1.0-t)*3.7;
      let b=inverse_cubic(LogPositive::from_linear(1.0).unwrap(),1.0,4.0,mean).unwrap();
      let actual=t*1.3_f64.powi(-3)+(1.0-t)*3.7_f64.powi(-3);
      assert!(v(b.lower)<=actual && actual<=v(b.upper));}
 }
 #[test] fn invalid_mean_and_zero_support_reject() {
    assert!(inverse_cubic(LogPositive::empty(),1.,2.,3.).is_err());
    assert!(inverse_cubic(LogPositive::empty(),1.,1.,1.).is_err());
 }
 #[test] fn positive_rate_tail_must_not_become_empty() {
    let b=inverse_cubic(LogPositive::from_linear(1.).unwrap(),1e200,4e200,2e200).unwrap();
    assert!(!b.lower.is_empty() && !b.upper.is_empty());
    assert!(b.lower.log_value().is_finite() && b.upper.log_value().is_finite());
 }
}
