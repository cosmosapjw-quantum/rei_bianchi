#![forbid(unsafe_code)]
pub mod kernel;
pub mod block;
pub mod integrate;
pub mod benchmark;

use serde::{Deserialize,Serialize};
use rodas5p_core::{CoreError,CoreResult};
pub use wu088_hh_phys69_vigilode::{Request as PhysicsRequest,parse_seed,get,put,B,T,K,Q_SCALE,D2_SCALE,TARGET_A,TARGET_B,UPSTREAM_COMMIT,FROZEN_SOURCE_SHA256};

#[derive(Clone,Copy,Debug,PartialEq,Eq,Deserialize,Serialize)]
#[serde(rename_all="snake_case")]
pub enum Engine { LegacyGmres, BlockScalar, BlockSimd }

#[derive(Clone,Debug,Deserialize,Serialize)]
#[serde(deny_unknown_fields)]
pub struct Request {
    pub schema:String,
    pub engine:Engine,
    pub physics_request:PhysicsRequest,
    #[serde(rename="HH_R10")] pub hh_r10:String,
}
impl Request {
    pub fn validate(&self)->CoreResult<()> {
        self.physics_request.validate()?;
        if self.schema!="PHYS70_OPTIMIZED_REQUEST_V1" || self.hh_r10!="OFF" || self.physics_request.max_step>0.5 {
            return Err(CoreError::InvalidInput("PHYS70 identity or represented step cap".into()));
        } Ok(())
    }
}
