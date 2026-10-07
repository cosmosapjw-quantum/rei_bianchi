//! Positive spectral-panel restrictions. Additive research API, not a gas solver.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Family { Ordinary, RightFront }
#[derive(Clone, Copy, Debug)]
pub struct Panel { pub l:f64, pub r:f64, pub beta:f64, pub family:Family, pub ln_n:f64 }
#[derive(Clone, Copy, Debug)]
pub struct Restriction { pub lo:f64, pub hi:f64, pub ln_fraction:f64, pub ln_n:f64, pub normalized_mean:f64, pub mean_eta:f64, pub mean_exp_eta:f64, pub panels:usize, pub convergence_error:f64 }
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum PanelError { Domain, Unsupported, Quadrature, Arithmetic }
impl Panel {
 pub fn restrict(&self,_a:f64,_b:f64)->Result<Option<Restriction>,PanelError>{Err(PanelError::Unsupported)}
}
