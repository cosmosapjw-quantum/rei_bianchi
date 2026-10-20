//! RUN19 opt-in coefficient-value cubic evaluator on log T, not a new atom model.
//! Derived from the tested rate_cubic examples/common field mapping. Actual source
//! bytes, algorithm implementation and wrapper policy are compile-bound to cache ID.
use rei_rate_cubic::{CubicRateGrid,Error,Sample,source_digest};
use crate::{ForwardError,igm_rates::{igm_rates,IgmRates,IgmRateDiagnostics},
    rate_table::{igm_flat,igm_branch_knots}};
use std::path::Path;

pub const DEFAULT_NODES:usize=32_769;
const POLICY:&[u8]=b"REI_NATIVE_HHE_CUBIC_V1;T=[1,1000000];units=cgs;channels=15+zeroPad;layout=nodeMajor16;grid=lnT;stencil=-1,0,1,2;order=nonFMA;tag=floors3-drLow1-ceCaps3;thresholdBranchStencilFallback;normalPositiveOrDirect;cacheDefaultNodes=32769";
pub fn source_id()->[u8;32]{
    let mut bytes=Vec::new();
    for part in [POLICY,include_bytes!("../owner_src/igm_rates.rs").as_slice(),
        include_bytes!("../owner_src/rate_table.rs").as_slice(),
        include_bytes!("../../rate_cubic/src/lib.rs").as_slice(),
        include_bytes!("cubic_igm.rs").as_slice()] {
        bytes.extend_from_slice(&(part.len()as u64).to_le_bytes());bytes.extend_from_slice(part);
    }
    source_digest(&bytes)
}
pub fn source_id_hex()->String{source_id().iter().map(|b|format!("{b:02x}")).collect()}

#[derive(Clone,Debug)]
pub struct CubicIgmTable{grid:CubicRateGrid<16>}
impl CubicIgmTable{
    pub fn build_default()->Result<Self,Error>{Self::new(DEFAULT_NODES)}
    pub fn new(nodes:usize)->Result<Self,Error>{
        let grid=CubicRateGrid::build(1.0,1e6,nodes,source_id(),|t|{
            let r=igm_rates(t).map_err(|_|Error::Invalid("IGM_TEMPERATURE_DOMAIN"))?;
            let flat=igm_flat(r);let mut values=[0.0;16];values[..15].copy_from_slice(&flat);
            let mut tag=if r.diagnostics.dr_low_branch{8}else{0};
            for j in 0..3{if r.diagnostics.ci_floor_cm3_s[j]!=0.0{tag|=1<<j;}
                if r.diagnostics.ce_cap_erg[j]!=0.0{tag|=1<<(4+j);}}
            Ok(Sample{values,tag})
        },|a,b|igm_branch_knots().iter().any(|&k|a<=k&&k<=b),
        |j,a,b|j==15||(j==6&&a/11605.0<=0.8&&b/11605.0<=0.8))?;
        Ok(Self{grid})
    }
    pub fn grid(&self)->&CubicRateGrid<16>{&self.grid}
    pub fn save_new(&self,path:impl AsRef<Path>)->Result<(),Error>{self.grid.save_new(path)}
    /// The server contract is the default grid. A differently sized valid cache
    /// is rejected rather than silently selecting a different accuracy budget.
    pub fn load_default(path:impl AsRef<Path>)->Result<Self,Error>{
        let grid=CubicRateGrid::load(path,source_id())?;
        if grid.domain().map(f64::to_bits)!=[1.0_f64.to_bits(),1e6_f64.to_bits()]
            ||grid.nodes()!=DEFAULT_NODES{return Err(Error::Invalid("IGM_CUBIC_CACHE_DOMAIN_OR_NODES"));}
        Ok(Self{grid})
    }
    pub fn rates(&self,t:f64)->Result<IgmRates,ForwardError>{
        let Some(s)=self.grid.sample(t)else{return igm_rates(t);};
        let mut v=s.values;let floor:[bool;3]=std::array::from_fn(|j|s.tag&(1<<j)!=0);
        for j in 0..3{if floor[j]{v[j]=1e-20;}}
        let low=t/11605.0<=0.8;let ce=[v[7],v[8],v[9]];
        Ok(IgmRates{ci_cm3_s:[v[0],v[1],v[2]],rr_cm3_s:[v[3],v[4],v[5]],dr_cm3_s:v[6],ce_erg:ce,
            rr_cooling_erg_cm3_s:[v[10],v[11],v[12]],dr_cooling_erg_cm3_s:if low{0.0}else{v[13]},
            dr_raw_cooling_erg_cm3_s:v[13],freefree_erg_cm3_s:v[14],
            diagnostics:IgmRateDiagnostics{ci_floor_cm3_s:std::array::from_fn(|j|if floor[j]{v[j]}else{0.0}),
                ce_cap_erg:std::array::from_fn(|j|if [118348.0,13179.0,473638.0][j]/t>69.07755278982137{ce[j]}else{0.0}),
                dr_excluded_erg_cm3_s:if low{v[13]}else{0.0},dr_low_branch:low}})
    }
}
