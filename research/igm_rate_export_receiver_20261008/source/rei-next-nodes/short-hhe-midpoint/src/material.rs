use crate::{checked, err, positive, product, Fallible};
use rei_microphysics::{
    igm_background::FlrwPoint,
    igm_state::IgmGasState,
    igm_thermal::{igm_point_rhs, IgmPointRhs},
    HHeModel,
};
pub fn photo_delta(a: [f64; 3], b: [f64; 3], fhe: f64) -> [f64; 4] {
    let c = HHeModel::controlled_fixture();
    [
        a[0],
        (a[1] - a[2]) / fhe,
        a[2] / fhe,
        (0..3)
            .map(|i| b[i] - c.ev_erg * c.threshold_ev[i] * a[i])
            .sum(),
    ]
}
pub fn gas(y: [f64; 4]) -> Fallible<IgmGasState> {
    IgmGasState::new([y[0], y[1], y[2]], y[3]).map_err(err)
}
pub fn values(g: &IgmGasState) -> [f64; 4] {
    [
        g.fractions[0],
        g.fractions[1],
        g.fractions[2],
        g.w_erg_per_h,
    ]
}
pub fn rhs(y: [f64; 4], p: FlrwPoint) -> Fallible<IgmPointRhs> {
    igm_point_rhs(
        &gas(y)?,
        p.n_h_cm3,
        p.n_he_cm3,
        p.hubble_per_s,
        p.tcmb_k,
        Default::default(),
    )
    .map_err(err)
}
pub fn binding(y: [f64; 4], fhe: f64) -> f64 {
    let c = HHeModel::controlled_fixture();
    c.ev_erg
        * (c.threshold_ev[0] * y[0]
            + fhe * (c.threshold_ev[1] * y[1] + (c.threshold_ev[1] + c.threshold_ev[2]) * y[2]))
}
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct MaterialOwners {
    pub ci: [f64; 3],
    pub rr: [f64; 3],
    pub dr: f64,
    pub escape: f64,
    pub work: f64,
    pub cmb: f64,
    pub floor: [f64; 3],
    pub cap: [f64; 3],
    pub excluded_dr: f64,
    pub nonphoto_binding: f64,
    pub nonphoto_thermal: f64,
}
impl MaterialOwners {
    pub fn stage(r: IgmPointRhs, p: FlrwPoint, ds: f64) -> Fallible<Self> {
        let dt = positive(ds / p.hubble_per_s)?;
        let vol = positive(dt / p.n_h_cm3)?;
        let mut z = Self::default();
        for i in 0..3 {
            z.ci[i] = product(vol, r.ci_events_cm3_s[i])?;
            z.rr[i] = product(vol, r.rr_events_cm3_s[i])?;
            z.floor[i] = product(vol, r.ci_floor_events_cm3_s[i])?;
            z.cap[i] = product(vol, r.ce_cap_cooling_erg_cm3_s[i])?;
        }
        z.dr = product(vol, r.dr_events_cm3_s)?;
        z.escape = product(vol, r.escape_erg_cm3_s)?;
        z.work = product(vol, r.expansion_work_erg_cm3_s)?;
        z.cmb = -product(vol, r.cmb_to_gas_erg_cm3_s.abs())? * r.cmb_to_gas_erg_cm3_s.signum();
        z.excluded_dr = product(vol, r.excluded_dr_cooling_erg_cm3_s)?;
        z.nonphoto_binding = checked(vol * r.binding_micro_erg_cm3_s)?;
        z.nonphoto_thermal = checked(dt * r.w_dt_erg_per_h_s)?;
        Ok(z)
    }
    pub fn plus(self, b: Self) -> Fallible<Self> {
        let mut a = self;
        for i in 0..3 {
            a.ci[i] = checked(a.ci[i] + b.ci[i])?;
            a.rr[i] = checked(a.rr[i] + b.rr[i])?;
            a.floor[i] = checked(a.floor[i] + b.floor[i])?;
            a.cap[i] = checked(a.cap[i] + b.cap[i])?;
        }
        a.dr = checked(a.dr + b.dr)?;
        a.escape = checked(a.escape + b.escape)?;
        a.work = checked(a.work + b.work)?;
        a.cmb = checked(a.cmb + b.cmb)?;
        a.excluded_dr = checked(a.excluded_dr + b.excluded_dr)?;
        a.nonphoto_binding = checked(a.nonphoto_binding + b.nonphoto_binding)?;
        a.nonphoto_thermal = checked(a.nonphoto_thermal + b.nonphoto_thermal)?;
        Ok(a)
    }
}
