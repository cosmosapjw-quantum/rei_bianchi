//! Per-driver rate selection. No process-global backend state.
use std::{cell::Cell, path::Path, rc::Rc};
use axbi_temperature_rate_table_benchmark::{thermal_adapter, Table};
use rei_microphysics::{
    axbi_rates::{AxbiPoint, AxbiProvider, AXBI_PROVIDER_ID},
    igm_rates::IgmRates, igm_state::IgmGasState,
    igm_thermal::IgmPhotoInput, ForwardError,
};

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Backend { Direct, Table }

#[derive(Clone)]
pub struct Provider {
    backend: Backend,
    table: Option<Rc<Table>>,
    coefficient_calls: Rc<Cell<u64>>,
}
impl Provider {
    pub fn direct() -> Self { Self { backend: Backend::Direct, table: None, coefficient_calls: Rc::new(Cell::new(0)) } }
    pub fn load(path: &Path) -> Result<Self, String> {
        let table = Table::load(path)?;
        Ok(Self { backend: Backend::Table, table: Some(Rc::new(table)), coefficient_calls: Rc::new(Cell::new(0)) })
    }
    pub fn backend(&self) -> Backend { self.backend }
    pub fn counts(&self) -> (u64,u64,u64) {
        let (lookup,fallback) = self.table.as_ref().map(|t|(t.lookup.get(),t.fallback.get())).unwrap_or((0,0));
        (self.coefficient_calls.get(),lookup,fallback)
    }
    pub fn rates(&self, t:f64)->Result<IgmRates,ForwardError> {
        let n=self.coefficient_calls.get();
        if n>=5_000_000 {return Err(ForwardError::InvalidInput("INTEGRATION_COEFFICIENT_CAP"));}
        self.coefficient_calls.set(n+1);
        match &self.table {Some(table)=>table.query(t),None=>AxbiProvider.rates(t)}
    }
    pub fn point(&self,gas:&IgmGasState,nh:f64,nhe:f64,h:f64,tcmb:f64,photo:IgmPhotoInput)->Result<AxbiPoint,ForwardError>{
        // Match the canonical outer EOS, inner RHS EOS, then second rate lookup.
        // The accepted adapter is the same scalar RHS with a selected rate callback.
        let temperature_k=gas.eos(nh,nhe)?.temperature_k;
        let rhs=thermal_adapter::igm_point_rhs(gas,nh,nhe,h,tcmb,photo,|t|self.rates(t))?;
        let rates=self.rates(temperature_k)?;
        Ok(AxbiPoint{provider_id:AXBI_PROVIDER_ID,temperature_k,rates,rhs})
    }

}
impl std::fmt::Debug for Provider {
    fn fmt(&self,f:&mut std::fmt::Formatter<'_>)->std::fmt::Result {
        f.debug_struct("Provider").field("backend",&self.backend).field("counts",&self.counts()).finish()
    }
}

#[cfg(test)]
mod accounting_tests {
    use super::*;
    #[test]
    fn synthetic_cap_last_attempt_and_rejection() {
        for provider in [Provider::direct(),Provider::load(Path::new("../temperature_rate_table_001/data/rates.bin")).unwrap()] {
            provider.coefficient_calls.set(4_999_999);
            assert!(provider.rates(0.5).is_err());
            assert_eq!(provider.counts().0,5_000_000);
            let previous=provider.counts();
            assert!(matches!(provider.rates(10.0),Err(ForwardError::InvalidInput("INTEGRATION_COEFFICIENT_CAP"))));
            assert_eq!(provider.counts(),previous);
            println!("cap backend={:?} count={} lookup={} fallback={}",provider.backend(),previous.0,previous.1,previous.2);
        }
    }
}
