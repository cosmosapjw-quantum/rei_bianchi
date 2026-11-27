//! Opaque native receipts cannot be replaced by caller arrays or JSON certificates.
use hh_phys04_candidate::{Interval,ForwardError};
pub struct CertifiedCorners { _private:() }
pub struct ContinuousTarget { _private:() }
#[derive(Debug,Clone)]pub struct Observable {pub definition:&'static str,pub value:Option<Vec<Interval>>,pub missing:&'static str}
pub fn actual_observables(_corners:Option<&CertifiedCorners>,_continuous:Option<&ContinuousTarget>)->Vec<Observable>{
 ["D_h_full(b)=Z_full(1,b)-Z_full(0,b)","D_h_twohalf(b)=Z_twohalf(1,b)-Z_twohalf(0,b)","I_h_full=D_h_full(1)-D_h_full(0)","I_h_twohalf=D_h_twohalf(1)-D_h_twohalf(0)","HH_scheme_defect(b)=D_h_twohalf(b)-D_h_full(b)","mixed_scheme_defect=I_h_twohalf-I_h_full","true_continuous_source_law_error_full=Z_full-Phi","true_continuous_source_law_error_twohalf=Z_twohalf-Phi"].map(|definition|Observable{definition,value:None,missing:"native corner/root/tube/continuous producer absent; authorization null"}).to_vec()
}
pub fn native_metrics_requested()->Result<(),ForwardError>{Err(ForwardError::InvalidInput("PHYS04_TRUSTED_NATIVE_CORNER_FAMILY_MISSING"))}
#[cfg(test)]mod tests{use super::*;#[test]fn distinct_uncomputed_observables_null(){let o=actual_observables(None,None);assert_eq!(o.len(),8);assert!(o.iter().all(|v|v.value.is_none()));assert!(native_metrics_requested().is_err());}}
