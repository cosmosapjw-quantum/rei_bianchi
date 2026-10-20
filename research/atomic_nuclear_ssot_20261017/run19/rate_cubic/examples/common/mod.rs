use rei_rate_cubic::{CubicRateGrid, Error, Sample, source_digest};
use rei_reference::{igm_rates::{igm_rates, IgmRates, IgmRateDiagnostics}, rate_table::{igm_flat, igm_branch_knots}};

pub fn source_id() -> [u8;32] {
    // The manifest binds the exact source bytes separately. This typed identity
    // includes algorithm, layout, known branch policy, units, and immutable owner.
    source_digest(b"RUN19_HHE_CUBIC_V1;baseline=99e07bcff126d0a73a03bafc4b71e0b735dbcc3e;owner=run13/recovered/code/rei_bass_coupled/owner_src/igm_rates.rs;units=cgs;nodes=logT;stencil=-1,0,1,2;tag=floors3-drLow1-ceCaps3;channels=15+zeroPad")
}
pub struct HheCubic { pub grid: CubicRateGrid<16> }
impl HheCubic {
    pub fn new(nodes:usize)->Result<Self,Error> {
        let grid=CubicRateGrid::build(1.0,1e6,nodes,source_id(),|t| {
            let r=igm_rates(t).map_err(|_|Error::Invalid("IGM_TEMPERATURE_DOMAIN"))?;
            let flat=igm_flat(r);let mut values=[0.0;16];values[..15].copy_from_slice(&flat);
            let mut tag=if r.diagnostics.dr_low_branch {8}else{0};
            for j in 0..3 {if r.diagnostics.ci_floor_cm3_s[j]!=0.0 {tag|=1<<j;}
                if r.diagnostics.ce_cap_erg[j]!=0.0 {tag|=1<<(4+j);}}
            Ok(Sample{values,tag})
        },|a,b| igm_branch_knots().iter().any(|&k|a<=k&&k<=b),
        |j,a,b|j==15||(j==6&&a/11605.0<=0.8&&b/11605.0<=0.8))?;
        Ok(Self{grid})
    }
    pub fn rates(&self,t:f64)->Result<IgmRates,Error> {
        let Some(s)=self.grid.sample(t) else{return igm_rates(t).map_err(|_|Error::Invalid("IGM_TEMPERATURE_DOMAIN"));};
        let mut v=s.values;let floor: [bool;3]=std::array::from_fn(|j|s.tag&(1<<j)!=0);
        for j in 0..3 {if floor[j]{v[j]=1e-20;}}
        let low=t/11605.0<=0.8;let ce=[v[7],v[8],v[9]];
        // Same field mapping and unit convention as the existing log-linear table.
        Ok(IgmRates {ci_cm3_s:[v[0],v[1],v[2]],rr_cm3_s:[v[3],v[4],v[5]],dr_cm3_s:v[6],ce_erg:ce,
            rr_cooling_erg_cm3_s:[v[10],v[11],v[12]],dr_cooling_erg_cm3_s:if low{0.0}else{v[13]},
            dr_raw_cooling_erg_cm3_s:v[13],freefree_erg_cm3_s:v[14],
            diagnostics:IgmRateDiagnostics {ci_floor_cm3_s:std::array::from_fn(|j|if floor[j]{v[j]}else{0.0}),
                ce_cap_erg:std::array::from_fn(|j|if [118348.0,13179.0,473638.0][j]/t>69.07755278982137{ce[j]}else{0.0}),
                dr_excluded_erg_cm3_s:if low{v[13]}else{0.0},dr_low_branch:low}})
    }
}
