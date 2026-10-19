//! Exact stored-polynomial arithmetic plus unchanged VigilODE interval source.
//!
//! This adapter does not integrate an ODE. Binary64 bit patterns are interpreted
//! as exact rationals. Point interval inclusion checks are concrete checks of
//! the imported arithmetic on these expressions, not a global solver proof.
use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, Signed, ToPrimitive, Zero};

pub type Q = BigRational;

/// The only error variants referenced by the unchanged imported module.
/// This shim changes no arithmetic or interval implementation statement.
#[derive(Debug, Clone)]
pub enum CoreError {
    InvalidInput(String),
    NonFinite(String),
}
pub type CoreResult<T> = Result<T, CoreError>;
#[path = "../provenance/vigilode_directed.rs"]
pub mod vigilode_directed;
use vigilode_directed::Interval;

pub fn rational_bits(bits: u64) -> Result<Q, String> {
    Q::from_float(f64::from_bits(bits)).ok_or_else(|| "finite binary64 required".into())
}

pub fn rational_hex(text: &str) -> Result<Q, String> {
    if text.len() != 16 || !text.bytes().all(|b| b.is_ascii_hexdigit()) {
        return Err("exactly 16 hexadecimal IEEE754 bits required".into());
    }
    rational_bits(u64::from_str_radix(text, 16).map_err(|e| e.to_string())?)
}

pub fn dense_value_derivative(t_old: &Q, h: &Q, t: &Q, y_old: &Q,
                              coefficients: &[Q; 7]) -> Result<(Q, Q, Q), String> {
    if h <= &Q::zero() {
        return Err("positive dense step required".into());
    }
    let x = (t-t_old)/h;
    let one_minus = Q::one()-&x;
    let mut value = Q::zero();
    let mut derivative_x = Q::zero();
    for (i, coefficient) in coefficients.iter().rev().enumerate() {
        let before = &value+coefficient;
        if i % 2 == 0 {
            derivative_x = &derivative_x*&x+&before;
            value = before*&x;
        } else {
            derivative_x = &derivative_x*&one_minus-&before;
            value = before*&one_minus;
        }
    }
    Ok((value+y_old, derivative_x/h, x))
}

fn choose(n: usize, k: usize) -> BigInt {
    if k > n { return BigInt::zero(); }
    let k = k.min(n-k);
    let mut result = BigInt::one();
    for j in 0..k {
        result = result*BigInt::from(n-j)/BigInt::from(j+1);
    }
    result
}

/// Independent ascending power expansion on the exact accepted interval.
pub fn dense_power(y_old: &Q, coefficients: &[Q; 7], x_end: &Q) -> Vec<Q> {
    let mut powers = vec![Q::zero(); 8];
    powers[0] = y_old.clone();
    for (k, f) in coefficients.iter().enumerate() {
        let p = 1+k/2;
        let q = (k+1)/2;
        for j in 0..=q {
            let sign = if j % 2 == 0 { 1 } else { -1 };
            powers[p+j] += f*Q::from_integer(choose(q,j)*sign)*x_end.pow((p+j) as i32);
        }
    }
    powers
}

pub fn bernstein(power: &[Q]) -> Result<Vec<Q>, String> {
    if power.is_empty() || power.len() > 65 {
        return Err("one to 65 power coefficients required".into());
    }
    let degree = power.len()-1;
    Ok((0..=degree).map(|j| (0..=j).map(|k|
        &power[k]*Q::new(choose(j,k),choose(degree,k))).sum()).collect())
}

fn point(bits: u64) -> CoreResult<Interval> {
    Interval::point(f64::from_bits(bits))
}

/// Actual VigilODE interval operations on the same degree-seven recurrence.
pub fn interval_dense(t_old: u64, h: u64, t: u64, y_old: u64,
                      coefficients: &[u64; 7]) -> CoreResult<(Interval, Interval)> {
    let h = point(h)?;
    if h.lo <= 0.0 {
        return Err(CoreError::InvalidInput("positive dense interval step required".into()));
    }
    let x = point(t)?.sub(point(t_old)?)?.div(h)?;
    let complement = Interval::point(1.0)?.sub(x)?;
    let mut value = Interval::point(0.0)?;
    let mut derivative_x = Interval::point(0.0)?;
    for (i, coefficient) in coefficients.iter().rev().enumerate() {
        let before = value.add(point(*coefficient)?)?;
        if i % 2 == 0 {
            derivative_x = derivative_x.mul(x)?.add(before)?;
            value = before.mul(x)?;
        } else {
            derivative_x = derivative_x.mul(complement)?.sub(before)?;
            value = before.mul(complement)?;
        }
    }
    Ok((value.add(point(y_old)?)?, derivative_x.div(h)?))
}

/// Compare rational truth to exact dyadic endpoints, never to a rounded f64 truth.
pub fn interval_contains_exact(interval: Interval, value: &Q) -> bool {
    match (rational_bits(interval.lo.to_bits()), rational_bits(interval.hi.to_bits())) {
        (Ok(lo), Ok(hi)) => lo <= *value && *value <= hi,
        _ => false,
    }
}

pub fn enclose_rational(value: &Q) -> Result<Interval, String> {
    let approximation = value.to_f64().ok_or("rational outside finite binary64")?;
    if !approximation.is_finite() { return Err("finite rational enclosure required".into()); }
    let rounded = rational_bits(approximation.to_bits())?;
    let lo = if rounded > *value { approximation.next_down() } else { approximation };
    let hi = if rounded < *value { approximation.next_up() } else { approximation };
    Interval::new(lo,hi).map_err(|e|format!("{e:?}"))
}

/// Repair-only bound exp(Gamma)-1 <= Gamma/(1-Gamma), 0 <= Gamma < 1.
pub fn beta_and_vigilode_enclosure(gamma: &Q) -> Result<(Q, Interval), String> {
    if gamma < &Q::zero() || gamma >= &Q::one() {
        return Err("repair radius must satisfy 0 <= Gamma < 1".into());
    }
    let beta = gamma/(Q::one()-gamma);
    let interval_gamma = enclose_rational(gamma)?;
    let interval = interval_gamma.div(Interval::point(1.0)
        .and_then(|one|one.sub(interval_gamma)).map_err(|e|format!("{e:?}"))?)
        .map_err(|e|format!("{e:?}"))?;
    if !interval_contains_exact(interval, &beta) {
        return Err("VigilODE beta interval misses exact rational".into());
    }
    Ok((beta,interval))
}

#[cfg(test)]
mod tests {
    use super::*;
    fn q(n:i64,d:i64)->Q { Q::new(n.into(),d.into()) }
    #[test]
    fn exact_bits_normal_subnormal_and_nonfinite() {
        assert_eq!(rational_bits(0.1_f64.to_bits()).unwrap(),
                   Q::new(BigInt::from(3602879701896397_i64),BigInt::one()<<55));
        assert_eq!(rational_bits(1).unwrap(),Q::new(BigInt::one(),BigInt::one()<<1074));
        assert_eq!(rational_bits((-0.0_f64).to_bits()).unwrap(),Q::zero());
        assert!(rational_bits(f64::NAN.to_bits()).is_err());
        assert!(rational_bits(f64::INFINITY.to_bits()).is_err());
    }
    #[test]
    fn dense_recurrence_matches_independent_power_at_nonunit_clock() {
        let coefficients = [q(1,3),q(-2,7),q(3,11),q(1,13),q(-1,17),q(2,19),q(1,23)];
        let (t0,h,t,y0)=(q(13,4),q(1,8),q(79,24),q(7,10));
        let (value,derivative,x)=dense_value_derivative(&t0,&h,&t,&y0,&coefficients).unwrap();
        let p=dense_power(&y0,&coefficients,&Q::one());
        let independently:Q=p.iter().enumerate().map(|(j,a)|a*x.pow(j as i32)).sum();
        let d:Q=p.iter().enumerate().skip(1).map(|(j,a)|a*Q::from_integer(j.into())*x.pow(j as i32-1)).sum();
        assert_eq!(value,independently);
        assert_eq!(derivative,d/h);
        assert_eq!(bernstein(&[q(5,4),q(-1,1),q(1,1)]).unwrap(),vec![q(5,4),q(3,4),q(5,4)]);
        assert!(bernstein(&[q(1,1),q(-8,1),q(8,1)]).unwrap()[1].is_negative());
    }
    #[test]
    fn vigilode_intervals_contain_exact_corner_operations_and_repair_beta() {
        for (a,b) in [(0.1,0.2),(-3.25,0.125),(f64::from_bits(1),0.5),(1e-250,1e-100)] {
            let ai=Interval::point(a).unwrap();let bi=Interval::point(b).unwrap();
            let aq=rational_bits(a.to_bits()).unwrap();let bq=rational_bits(b.to_bits()).unwrap();
            assert!(interval_contains_exact(ai.add(bi).unwrap(),&(&aq+&bq)));
            assert!(interval_contains_exact(ai.mul(bi).unwrap(),&(&aq*&bq)));
            assert!(interval_contains_exact(ai.div(bi).unwrap(),&(&aq/&bq)));
        }
        let gamma=q(9,288230376151711744);
        let (beta,interval)=beta_and_vigilode_enclosure(&gamma).unwrap();
        assert_eq!(beta,q(9,288230376151711735));
        assert!(interval_contains_exact(interval,&beta));
        assert!(beta_and_vigilode_enclosure(&q(1,1)).is_err());
    }
}
