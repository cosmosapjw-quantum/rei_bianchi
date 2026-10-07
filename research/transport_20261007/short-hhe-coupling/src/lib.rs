#![allow(clippy::needless_range_loop)]
pub mod coupled;
pub mod material;
pub mod output;
pub mod radiation;
#[allow(dead_code)]
#[path = "../../continuous-boundary-prototype-v2/src/primitives.rs"]
pub mod v2;
pub use material::photo_delta;
pub type Fallible<T> = Result<T, String>;
pub fn err<E: std::fmt::Debug>(e: E) -> String {
    format!("{e:?}")
}
pub fn checked(x: f64) -> Fallible<f64> {
    if x == 0.0 || x.is_normal() {
        Ok(x)
    } else {
        Err(format!("unsupported nonnormal {x:e}"))
    }
}
pub fn nonnegative(x: f64) -> Fallible<f64> {
    checked(x)?;
    if x >= 0.0 {
        Ok(x)
    } else {
        Err(format!("negative {x:e}"))
    }
}
pub fn positive(x: f64) -> Fallible<f64> {
    if x > 0.0 && x.is_normal() {
        Ok(x)
    } else {
        Err(format!("nonpositive/nonnormal {x:e}"))
    }
}
pub fn product(a: f64, b: f64) -> Fallible<f64> {
    nonnegative(a)?;
    nonnegative(b)?;
    if a == 0.0 || b == 0.0 {
        Ok(0.0)
    } else {
        positive(a * b)
    }
}

pub mod event_anchor;
