//! Fixed-source, fixed-opacity research integration of VigilODE affine transport.
extern crate self as rodas5p_core;

#[derive(Debug)]
pub enum CoreError {
    InvalidInput(String),
    NonFinite(String),
    Dimension(String),
}
pub type CoreResult<T> = Result<T, CoreError>;
impl std::fmt::Display for CoreError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{self:?}")
    }
}
impl std::error::Error for CoreError {}
#[path = "vendor/directed.rs"]
pub mod directed;
#[path = "vendor/affine_transport.rs"]
pub mod affine_transport;
pub mod certified;
