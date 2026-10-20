//! Explicit recovery R1 wrappers around the byte-recovered BR06 V2 path core.
#![forbid(unsafe_code)]
pub mod fixture;
pub mod quadrature;
pub mod reference;
pub mod vigilode_moments;
pub mod vigilode_native;

use rei_iso_couple_reference::{
    ForwardError, full_network::NetworkError, mixture_coupling::CoupleError,
    mixture_eos::MixtureError,
};
use std::fmt;
use vigilode_moments::MomentRefusal;

#[derive(Debug)]
pub enum Error {
    InvalidInput(&'static str),
    WorkLimit(&'static str),
    NoForwardProgress(&'static str),
    Forward(ForwardError),
    Network(NetworkError),
    Moment(MomentRefusal),
    Io(std::io::Error),
}
pub type Result<T> = std::result::Result<T, Error>;
impl Error {
    pub fn class(&self) -> &'static str {
        match self {
            Self::InvalidInput(_) => "INPUT_REJECTED",
            Self::WorkLimit(_) => "REFERENCE_WORK_LIMIT",
            Self::NoForwardProgress(_) => "REPRESENTATION_LIMIT",
            Self::Forward(_) => "OWNER_GEOMETRY_REFUSAL",
            Self::Network(NetworkError::Cx(CoupleError::WorkLimit)) => "CX_WORK_LIMIT",
            Self::Network(_) => "OWNER_NETWORK_REFUSAL",
            Self::Moment(MomentRefusal::WidthExceeded { .. }) => "VIGILODE_WIDTH_REFUSAL",
            Self::Moment(_) => "VIGILODE_REFUSAL",
            Self::Io(_) => "ENVIRONMENT_IO_FAILURE",
        }
    }
}
impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: {self:?}", self.class())
    }
}
impl std::error::Error for Error {}
impl From<ForwardError> for Error {
    fn from(value: ForwardError) -> Self {
        Self::Forward(value)
    }
}
impl From<NetworkError> for Error {
    fn from(value: NetworkError) -> Self {
        Self::Network(value)
    }
}
impl From<MixtureError> for Error {
    fn from(value: MixtureError) -> Self {
        Self::Network(value.into())
    }
}
impl From<MomentRefusal> for Error {
    fn from(value: MomentRefusal) -> Self {
        Self::Moment(value)
    }
}
impl From<std::io::Error> for Error {
    fn from(value: std::io::Error) -> Self {
        Self::Io(value)
    }
}
