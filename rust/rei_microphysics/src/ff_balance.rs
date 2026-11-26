//! Nonrelativistic free-free absorption on a prescribed Planck bath.
//! The van Hoof table supplies a spectral shape; the original integrated
//! Grackle emission remains the normalization. Not a new absolute emissivity.
use crate::ForwardError;
use std::sync::OnceLock;
const DATA: &str = include_str!("../../../research/r118c3b_ff_balance/gauntff.dat");
static TABLE: OnceLock<Vec<f64>> = OnceLock::new();
fn bad() -> ForwardError {
    ForwardError::InvalidInput("FF_BALANCE_DOMAIN")
}
pub fn gaunt(gamma2: f64, u: f64) -> Result<f64, ForwardError> {
    if !gamma2.is_finite() || !u.is_finite() || gamma2 <= 0. || u <= 0. {
        return Err(bad());
    }
    let x = (gamma2.log10() + 6.) / 0.2;
    let y = (u.log10() + 16.) / 0.2;
    if !(0. ..=80.).contains(&x) || !(0. ..=145.).contains(&y) {
        return Err(bad());
    }
    let t = TABLE.get_or_init(|| {
        DATA.lines()
            .filter_map(|l| {
                let l = l.split('#').next().unwrap().trim();
                let v = l.split_whitespace().collect::<Vec<_>>();
                if v.len() == 81 {
                    Some(
                        v.into_iter()
                            .map(|v| v.parse::<f64>().expect("Gaunt table"))
                            .collect::<Vec<_>>(),
                    )
                } else {
                    None
                }
            })
            .take(146)
            .flatten()
            .collect()
    });
    if t.len() != 81 * 146 {
        return Err(bad());
    }
    let i = (x.floor() as usize).min(79);
    let j = (y.floor() as usize).min(144);
    let a = x - i as f64;
    let b = y - j as f64;
    let at = |i, j| t[j * 81 + i];
    Ok((1. - b) * ((1. - a) * at(i, j) + a * at(i + 1, j))
        + b * ((1. - a) * at(i, j + 1) + a * at(i + 1, j + 1)))
}
pub fn absorption_ratio(t: f64, tc: f64, z2frac: f64, mode: u8) -> Result<f64, ForwardError> {
    absorption_ratio_n(t, tc, z2frac, mode, 256)
}
pub fn absorption_ratio_n(
    t: f64,
    tc: f64,
    z2frac: f64,
    mode: u8,
    n: usize,
) -> Result<f64, ForwardError> {
    if ![t, tc, z2frac].iter().all(|x| x.is_finite())
        || t <= 0.
        || tc <= 0.
        || !(0. ..=1.).contains(&z2frac)
        || ![1, 2].contains(&mode)
        || n < 16
        || n % 2 != 0
    {
        return Err(bad());
    }
    let r = tc / t;
    let g2 = 13.605693122994 / (8.617333262145e-5 * t);
    let g = |u: f64| -> Result<f64, ForwardError> {
        if mode == 1 {
            Ok(1.)
        } else {
            Ok((1. - z2frac) * gaunt(g2, u)? + z2frac * gaunt(4. * g2, u)?)
        }
    };
    let l0 = -23.025850929940457_f64;
    let dl = (60_f64.ln() - l0) / n as f64;
    let mut a = 0.;
    let mut e = 0.;
    for i in 0..=n {
        let x = (l0 + dl * i as f64).exp();
        let w = if i == 0 || i == n {
            1.
        } else if i % 2 == 0 {
            2.
        } else {
            4.
        };
        let u = r * x;
        e += w * x * (-x).exp() * g(x)?;
        a += w * x * r * (-(-u).exp_m1()) * (-x).exp() / (-(-x).exp_m1()) * g(u)?;
    }
    let v = a / e;
    if !v.is_finite() || v < 0. {
        return Err(bad());
    }
    Ok(v)
}
